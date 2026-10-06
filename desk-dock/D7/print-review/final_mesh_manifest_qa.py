"""Read only the current manifest union; mesh QA, never a slicer launch."""
import hashlib
import json
from pathlib import Path
import trimesh
import numpy as np

ROOT=Path(__file__).resolve().parent.parent
PRINT=ROOT/'print'
REPORT=ROOT/'print-review'
main=json.loads((ROOT/'print-manifest.json').read_text())
coupons=json.loads((PRINT/'coupon-manifest.json').read_text())
files=[r['file'] for r in main['parts']]+[r['file'] for r in coupons['parts']]
assert len(files)==len(set(files))==46
rows=[]
for filename in files:
    path=PRINT/filename
    mesh=trimesh.load_mesh(path,process=False)
    mesh.merge_vertices()
    components=mesh.split(only_watertight=False)
    row={'file':filename,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
         'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),
         'mesh_components':len(components),'positive_volume_mm3':float(mesh.volume),
         'size_mm':mesh.extents.tolist()}
    row['pass']=bool(row['watertight'] and row['winding_consistent'] and len(components)==1 and mesh.volume>0)
    if not row['watertight']:
        counts=np.bincount(mesh.edges_unique_inverse)
        bad=mesh.edges_unique[counts!=2]
        points=mesh.vertices[bad]
        lengths=np.linalg.norm(points[:,1]-points[:,0],axis=1)
        row['bad_edge_count']=len(bad)
        row['bad_edge_counts']=counts[counts!=2].tolist()
        row['bad_edges_xyz_mm']=points.tolist()
        row['bad_edge_length_range_mm']=[float(lengths.min()),float(lengths.max())]
    rows.append(row)
report={'production_parts':len(main['parts']),'coupon_parts':len(coupons['parts']),
        'files_checked':len(rows),'all_pass':all(r['pass'] for r in rows),'parts':rows,
        'input_manifest_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (ROOT/'print-manifest.json',PRINT/'coupon-manifest.json')},
        'limits':'Geometric mesh/topology check only; no toolpaths, support qualification, or physical print.'}
(REPORT/'final-manifest-mesh-qa.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('CHECKED',len(rows),'manifest meshes; failures:',[r for r in rows if not r['pass']])
raise SystemExit(0 if report['all_pass'] else 1)
