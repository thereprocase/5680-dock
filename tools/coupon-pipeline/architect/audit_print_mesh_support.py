"""Geometry-only proof check of nominated print poses; never invokes a slicer."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
import trimesh

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--stl',type=Path,action='append',required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args()
records=[]
for path in a.stl:
    m=trimesh.load_mesh(path,process=True)
    assert m.is_watertight and m.is_winding_consistent and m.volume>0
    zmin=float(m.bounds[0,2]); zmax=float(m.bounds[1,2])
    flat_bed=np.all(np.abs(m.triangles[:,:,2]-zmin)<1e-4,axis=1)
    downward=m.face_normals[:,2]<-1e-6
    suspended=downward & ~flat_bed
    angles=np.degrees(np.arctan2(-m.face_normals[suspended,2],np.linalg.norm(m.face_normals[suspended,:2],axis=1)))
    maximum=float(np.max(angles)) if len(angles) else 0.0
    area=float(np.sum(m.area_faces[suspended]))
    # Triangle normals are geometry evidence, not extrusion/strength evidence.
    # In a valid outward-wound closed mesh, any non-bed down-facing surface
    # records an outward-growing underside in the nominated print frame.
    record={'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),
      'components':len(m.split()),'bounds_mm':m.bounds.tolist(),
      'bed_contact_area_mm2':float(np.sum(m.area_faces[flat_bed & downward])),
      'nonbed_downfacing_area_mm2':area,'maximum_underside_angle_from_vertical_deg':maximum,
      'zero_outward_growth_mesh_check':area<1e-5,
      'scope':'Nominated-pose geometric mesh verification only. Non-bed undersides require slope/landing analysis; not a slicer or structural result.'}
    records.append(record)
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps({'parts':records},indent=2)+'\n')
print(json.dumps(records,indent=2))
