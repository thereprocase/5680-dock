"""Export D8's verified BREP cache to the browser's indexed mesh format.

No build import or geometry regeneration. The exporter refuses a cache that
fails to match final validation. Dynamic spring weights follow the actual
piecewise cubic leaf shape after D8's 90-degree cartridge rotation; motion is
illustrative and does not establish release force or a continuous clear sweep.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import struct
import cadquery as cq
from breakaway_geometry import datum, moving_names

ROOT = Path(__file__).resolve().parent

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def export(cache, output):
    validation_raw = (ROOT/'validation.json').read_bytes()
    validation = json.loads(validation_raw)
    assert validation['passed'], 'Final CAD validation must pass first'
    expected = validation['provenance']['cache_sha256']
    cache_hashes = {}
    for name, expected_hash in expected.items():
        cache_hashes[name] = sha((cache/name).read_bytes())
        assert cache_hashes[name] == expected_hash, f'Cache changed: {name}'
    parameter_raw = (ROOT/'parameters.json').read_bytes()
    assert sha(parameter_raw) == validation['provenance']['input_sha256']['parameters.json']
    p = json.loads(parameter_raw)
    H = p['rear_case_seat_z']
    a = math.radians(p['laptop_lean_deg'])
    px, pz = datum(p)
    spring = p['breakaway']
    data = bytearray()
    entries = []
    spring_check = None
    for part in json.loads((cache/'parts.json').read_text()):
        n = part['name']
        shape = cq.Shape.importBrep(str(cache/(n+'.brep')))
        vertices, faces = shape.tessellate(.35, .2)
        offset = len(data)
        for v in vertices:
            data.extend(struct.pack('<fff', v.x, v.y, v.z))
        index_offset = len(data)
        for face in faces:
            data.extend(struct.pack('<III', *face))
        b = shape.BoundingBox()
        entry = dict(part, positionOffset=offset, vertexCount=len(vertices),
                     indexOffset=index_offset, indexCount=3*len(faces),
                     center=[(b.xmin+b.xmax)/2, (b.ymin+b.ymax)/2, (b.zmin+b.zmax)/2])
        if n == 'breakaway_spring_cartridge':
            entry['motion'] = 'spring'
            entry['springWeightOffset'] = len(data)
            weights = []
            for v in vertices:
                # Undo laptop lean, then undo the cartridge's +90-degree Y
                # rotation. Original leaf X offset becomes negative local Z.
                local_z = v.y*math.sin(a)+(v.z-H)*math.cos(a)+H
                u = max(0, min(1, (38-abs(local_z-pz))/spring['spring_leaf_length_mm']))
                step = min(19, math.floor(u*20))
                q = u*20-step
                smooth = lambda x: 3*x*x-2*x*x*x
                weight = (smooth(step/20)*(1-q)+smooth((step+1)/20)*q) if abs(v.x-px)<=12.0001 else 0
                weights.append(weight)
                data.extend(struct.pack('<f', weight))
            spring_check = dict(vertex_count=len(weights), fixed_vertices=sum(w==0 for w in weights),
                                island_vertices=sum(w==1 for w in weights),
                                leaf_vertices=sum(0<w<1 for w in weights),
                                min_weight=min(weights), max_weight=max(weights),
                                maximum_added_deflection_mm=spring['cam_rise_mm'])
            assert all(spring_check[k]>0 for k in ['fixed_vertices','island_vertices','leaf_vertices'])
        elif moving_names(n):
            entry['motion'] = 'rotate'
        elif n in ['breakaway_pivot_pin_10mm','breakaway_preload_hand_nut']:
            entry['motion'] = 'axial'
        entries.append(entry)
        print(n, len(vertices), 'vertices', flush=True)
    service = validation['service_removal']['connector_module']
    animation = dict(pivot=[px,(pz-H)*math.sin(a),H+(pz-H)*math.cos(a)],
                     axis=[0,math.cos(a),-math.sin(a)], maxAngleDeg=45,
                     springRate=2*spring['nominal_E_MPa']*spring['spring_width_mm']*spring['spring_thickness_mm']**3/spring['spring_leaf_length_mm']**3,
                     preload=spring['spring_preload_deflection_mm'],rise=spring['cam_rise_mm'],
                     torque=spring['nominal_release_N']*27.15,
                     scope='Illustrative cam kinematics. Release force, creep and cable flex require physical qualification.')
    manifest = dict(revision='D8', units='mm', coordinate_frame=p['coordinate_frame'],
                    undocked_x_offset_mm=18, laptop_lean_deg=p['laptop_lean_deg'],
                    breakawayAnimation=animation,
                    moduleService=dict(movingParts=service['moving_parts'],removedLocks=service['removed_locks'],
                        keyReleaseMm=4.3,outboardTravelMm=70,scope='Unloaded laptop, two mount locks removed; local -Y then -X. Finite CAD positions checked, not a continuous collision simulation.'),
                    parts=entries)
    output.mkdir(parents=True, exist_ok=True)
    model_json = (json.dumps(manifest, indent=2)+'\n').encode()
    (output/'model.bin').write_bytes(data)
    (output/'model.json').write_bytes(model_json)
    evidence = dict(revision='D8', cache_matches_final_validation=True, part_count=len(entries),
                    vertex_count=sum(e['vertexCount'] for e in entries), triangle_count=sum(e['indexCount']//3 for e in entries),
                    bytes=len(data), tessellation=dict(linear_tolerance_mm=.35,angular_tolerance_rad=.2),
                    spring_weight_check=spring_check,
                    input_sha256={'export_viewer.py':sha(Path(__file__).read_bytes()),
                        'breakaway_geometry.py':sha((ROOT/'breakaway_geometry.py').read_bytes()),
                        'parameters.json':sha(parameter_raw),'validation.json':sha(validation_raw)},
                    cache_sha256=cache_hashes,
                    output_sha256={'model.json':sha(model_json),'model.bin':sha(data)},
                    limits='Visual mesh and illustrative motion. No new physical fit, strength, continuous swept-volume, release-force or printer qualification.')
    (output/'provenance.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print('Viewer mesh:',len(entries),'parts,',len(data),'bytes',flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('cache',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT.parents[1]/'docs/models/desk-dock-d8')
    args = parser.parse_args()
    export(args.cache,args.output)
