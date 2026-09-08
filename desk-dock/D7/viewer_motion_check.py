"""Compare viewer motion against independently posed CAD endpoint meshes."""
from pathlib import Path
import hashlib,json,math
import numpy as np
import trimesh
from scipy.spatial import cKDTree

R=Path(__file__).resolve().parent
M=R.parents[1]/'docs/models/desk-dock-d7'
manifest=json.loads((M/'model.json').read_text())
blob=(M/'model.bin').read_bytes()
hinge=manifest['breakawayAnimation']
required={
    'breakaway_carrier':'rotate','breakaway_pivot_pin_10mm':'axial',
    'breakaway_spring_cartridge':'spring','breakaway_preload_hand_nut':'axial',
    'height_shim_pack':'rotate','cassette_calibration_keeper_plate':'rotate',
    'cassette_calibration_hand_screw':'rotate','X_depth_overmold_clamp':'rotate',
    'sliding_plug_cap':'rotate','cassette_cap_push_pin_6p5':'rotate',
    'Dell_plug_overmold_REFERENCE':'rotate','USB_C_shell_REFERENCE':'rotate'}
assert {p['name']:p['motion'] for p in manifest['parts'] if p.get('motion')}==required
assert hinge['maxAngleDeg']==45 and abs(np.linalg.norm(hinge['axis'])-1)<1e-8
axis=np.array(hinge['axis']);pivot=np.array(hinge['pivot'])
angle=math.radians(hinge['maxAngleDeg'])
lift=min(hinge['rise'],math.sqrt(hinge['preload']**2+2*hinge['torque']*angle/hinge['springRate'])-hinge['preload'])
def vertices(p):return np.frombuffer(blob,dtype='<f4',count=p['vertexCount']*3,offset=p['positionOffset']).reshape(-1,3).astype(float)
def mesh(p,verts):
    faces=np.frombuffer(blob,dtype='<u4',count=p['indexCount'],offset=p['indexOffset']).reshape(-1,3)
    return trimesh.Trimesh(vertices=verts,faces=faces,process=False)
rows=[]
for part in manifest['parts']:
    if not part.get('motion'):continue
    ready=vertices(part);expected=vertices(part['folded'])
    if part['motion']=='rotate':
        v=ready-pivot
        moved=v*math.cos(angle)+np.cross(axis,v)*math.sin(angle)+np.outer(v@axis,axis)*(1-math.cos(angle))+pivot-lift*axis
    elif part['motion']=='axial':moved=ready-lift*axis
    else:
        weights=np.frombuffer(blob,dtype='<f4',count=part['vertexCount'],offset=part['springWeightOffset'])
        assert weights.min()>=0 and weights.max()<=1
        moved=ready-np.outer(weights*lift,axis)
    # OCC tessellation may choose different vertices on a planar polygon.
    # Compare surfaces if available; nearest-vertex distance is retained too.
    de=cKDTree(expected).query(moved)[0];dm=cKDTree(moved).query(expected)[0]
    distance=max(de.max(),dm.max());surface_error=distance
    if distance>=.02:
        # Remeshed thread surfaces may use different points. Compare each
        # unmatched vertex to the other complete triangle surface instead.
        errors=[]
        for target,source,d in [(mesh(part['folded'],expected),moved,de),(mesh(part,moved),expected,dm)]:
            errors.extend(d[d<.02].tolist())
            if (d>=.02).any():errors.extend(trimesh.proximity.closest_point(target,source[d>=.02])[1].tolist())
        surface_error=max(errors)
    bounds_error=float(np.abs(np.vstack([moved.min(0),moved.max(0)])-np.vstack([expected.min(0),expected.max(0)])).max())
    rows.append(dict(part=part['name'],motion=part['motion'],symmetric_vertex_error_mm=float(distance),surface_error_mm=float(surface_error),bounds_error_mm=bounds_error,passed=bool(surface_error<.02 and bounds_error<.02)))
data=dict(model_sha256=hashlib.sha256(blob).hexdigest(),angle_deg=45,cam_lift_mm=lift,parts=rows,passed=all(r['passed'] for r in rows),scope='Exported viewer transforms and spring displacement compared with actual independently posed CAD at 45 degrees. This script does not execute the browser controls or validate intermediate frames; not a dynamics or force simulation.')
(R/'viewer-motion-validation.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data,indent=2))
assert data['passed'],'Viewer endpoint differs from actual CAD; inspect viewer-motion-validation.json.'
