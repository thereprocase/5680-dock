"""Check D8 browser mesh integrity and kinematics without rebuilding CAD.

Rigid motion compares the browser's world-axis formula with independent
construction-frame matrix composition. Spring checks establish fixed-frame
and translating-island endpoint behavior for the rotated cartridge; they do
not compare to a newly regenerated CAD spring or simulate material behavior.
"""
from pathlib import Path
import hashlib
import json
import math
import numpy as np

ROOT=Path(__file__).resolve().parent
MODEL=ROOT.parents[1]/'docs/models/desk-dock-d8'
manifest=json.loads((MODEL/'model.json').read_text())
blob=(MODEL/'model.bin').read_bytes()
params=json.loads((ROOT/'parameters.json').read_text())
validation=json.loads((ROOT/'validation.json').read_text())
hinge=manifest['breakawayAnimation']
axis=np.array(hinge['axis']);pivot=np.array(hinge['pivot'])
H=params['rear_case_seat_z'];angle=math.radians(params['laptop_lean_deg'])
lean=np.array([[1,0,0],[0,math.cos(angle),math.sin(angle)],[0,-math.sin(angle),math.cos(angle)]])
origin=np.array([0,0,H]);pivot_local=(pivot-origin)@lean+origin

def vertices(part):
    return np.frombuffer(blob,dtype='<f4',count=part['vertexCount']*3,offset=part['positionOffset']).reshape(-1,3).astype(float)

def lift_at(degrees):
    return min(hinge['rise'],math.sqrt(hinge['preload']**2+2*hinge['torque']*abs(math.radians(degrees))/hinge['springRate'])-hinge['preload'])

rows=[];motion=[];spring_check={}
for part in manifest['parts']:
    ready=vertices(part)
    indices=np.frombuffer(blob,dtype='<u4',count=part['indexCount'],offset=part['indexOffset'])
    okay=bool(np.isfinite(ready).all() and len(indices)%3==0 and indices.max()<len(ready))
    assert okay,part['name']
    rows.append(dict(name=part['name'],vertices=len(ready),triangles=len(indices)//3,passed=okay))
    if part.get('motion') in ['rotate','axial']:
        errors=[]
        for degrees in [0,.5,1,5,15,45]:
            theta=math.radians(degrees);lift=lift_at(degrees)
            local=(ready-origin)@lean+origin
            if part['motion']=='rotate':
                rotation=np.array([[math.cos(theta),0,math.sin(theta)],[0,1,0],[-math.sin(theta),0,math.cos(theta)]])
                local=(local-pivot_local)@rotation.T+pivot_local
                rel=ready-pivot
                actual=rel*math.cos(theta)+np.cross(axis,rel)*math.sin(theta)+np.outer(rel@axis,axis)*(1-math.cos(theta))+pivot-lift*axis
            else:
                actual=ready-lift*axis
            expected=(local+np.array([0,-lift,0])-origin)@lean.T+origin
            errors.append(float(np.max(np.abs(actual-expected))))
        motion.append(dict(name=part['name'],motion=part['motion'],max_error_mm=max(errors),passed=max(errors)<1e-9))
    if part.get('motion')=='spring':
        weights=np.frombuffer(blob,dtype='<f4',count=part['vertexCount'],offset=part['springWeightOffset']).astype(float)
        local=(ready-origin)@lean+origin
        # D8's +90-degree Y rotation places the leaves along local Z. The
        # central island fits X ±12, Z ±8; the outer frame starts at X ±16
        # or Z ±38. Exclude tessellation points on shared boundaries.
        xdist=np.abs(local[:,0]-pivot_local[0]);zdist=np.abs(local[:,2]-pivot_local[2])
        fixed=(xdist>16.001)|(zdist>38.001)
        island=(xdist<11.999)&(zdist<7.999)
        assert fixed.any() and island.any()
        deflection=-np.outer(weights*lift_at(45),axis)
        fixed_error=float(np.max(np.abs(deflection[fixed])))
        island_error=float(np.max(np.abs(deflection[island]+.8*axis)))
        spring_check=dict(fixed_frame_vertices=int(fixed.sum()),island_vertices=int(island.sum()),
            fixed_frame_displacement_mm=fixed_error,island_translation_error_mm=island_error,
            weight_range=[float(weights.min()),float(weights.max())],
            passed=bool(fixed_error<1e-9 and island_error<1e-9 and weights.min()>=0 and weights.max()<=1))
        assert spring_check['passed']

service=manifest['moduleService'];expected_service=validation['service_removal']['connector_module']
assert set(service['movingParts'])==set(expected_service['moving_parts'])
assert set(service['removedLocks'])==set(expected_service['removed_locks'])
service_checks=[]
for sample in expected_service['samples']:
    x=sample['position_mm']['local_x'];y=sample['position_mm']['local_y']
    actual=np.array([x,math.cos(angle)*y,-math.sin(angle)*y])
    error=float(np.max(np.abs(actual-sample['assembly_translation_mm'])))
    service_checks.append(dict(position_mm=sample['position_mm'],max_error_mm=error,passed=error<1e-9))
result=dict(revision='D8',passed=all(r['passed'] for r in rows+motion+service_checks) and spring_check['passed'],
    model_sha256=hashlib.sha256(blob).hexdigest(),manifest_sha256=hashlib.sha256((MODEL/'model.json').read_bytes()).hexdigest(),
    checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    binary_parts=rows,rigid_motion_angles_deg=[0,.5,1,5,15,45],rigid_motion=motion,
    spring_endpoints=spring_check,module_service_samples=service_checks,
    module_part_count=len(service['movingParts']),removed_lock_count=len(service['removedLocks']),
    scope=__doc__.strip())
(ROOT/'viewer-motion-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(passed=result['passed'],parts=len(rows),rigid_motion_parts=len(motion),spring=spring_check,module_samples=len(service_checks))))
assert result['passed']
