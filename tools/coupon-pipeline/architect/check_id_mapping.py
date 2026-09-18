import cadquery as cq,trimesh,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[3]
for rev in ('profile-v3','profile-v4'):
 for p in sorted((root/'work/quartet-team/geometry'/rev/'generated').glob('*.step')):
  s=cq.importers.importStep(str(p)).val(); b=s.BoundingBox()
  mesh=trimesh.load_mesh(p.with_name(p.stem+'_X_to_print_Z.stl'))
  section=mesh.section(plane_origin=[0,0,12],plane_normal=[0,0,1])
  print(rev,p.stem, 'source_bbox',b.ymin,b.ymax,b.zmin,b.zmax,'stl',mesh.bounds.tolist())
  for ring in section.discrete:
   if len(ring)>0 and max(ring[:,0])-min(ring[:,0])<4 and max(ring[:,1])-min(ring[:,1])<4:
    print('ID ring',ring.min(axis=0).tolist(),ring.max(axis=0).tolist())
