"""Localize exposed air-boundary samples and underside faces; no CAD edits."""
from pathlib import Path
import json, math
import cadquery as cq
import numpy as np
import trimesh

here=Path(__file__).resolve().parent
src=here.parent/'geometry/d9-fan-pod/closed-v3/generated'
out=here/'closed-v3-review'
assembly=cq.importers.importStep(str(src/'D9_closed_v3_physical_assembly.step')).val()
void=cq.importers.importStep(str(src/'D9_closed_v3_intended_air_volume.step')).val()
caps=cq.importers.importStep(str(out/'TEMPORARY_combined_port_caps.step')).val()
solids=assembly.Solids()+caps.Solids()
sealed=solids[0].fuse(*solids[1:]).clean()
sealed_solids=sealed.Solids()
def local(p):
 x,y,z=p; y-=58; z-=72
 a=math.radians(-108)
 return [x-84, math.cos(a)*y-math.sin(a)*z, math.sin(a)*y+math.cos(a)*z]
exposed=[]
for fi,face in enumerate(void.Faces()):
 vs,ts=face.tessellate(.15,.2)
 vertices=np.array([v.toTuple() for v in vs]); triangles=vertices[np.array(ts)]
 areas=np.linalg.norm(np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]),axis=1)/2
 hits=[]
 for ti in np.argsort(areas)[-12:]:
  c=triangles[ti].mean(axis=0)
  normal=np.array(face.normalAt(cq.Vector(*c)).toTuple())
  # Centroids lie on tessellation chords, not exactly on curved BREP faces.
  # Require a probe beyond the tessellation tolerance to be outside the void
  # as well as outside every physical solid; otherwise interior air would be
  # mislabeled as exposed wall.
  inside=c-.3*normal; outside=c+.3*normal
  if void.isInside(tuple(inside),1e-6) and not void.isInside(tuple(outside),1e-6) and not any(s.isInside(tuple(outside),1e-6) for s in sealed_solids):
   hits.append({'world_mm':c.tolist(),'fan_local_mm':local(c),'normal_world':normal.tolist()})
 if hits:exposed.append({'void_face':fi,'face_type':face.geomType(),'face_area_mm2':face.Area(),'exposed_samples':hits})
undersides={}
for name in ('intake_tray','solid_lid'):
 mesh=trimesh.load_mesh(src/f'D9_closed_v3_{name}_print_pose.stl')
 zmin=mesh.bounds[0,2]
 bad=np.flatnonzero((mesh.face_normals[:,2]<-1e-6)&~np.all(np.abs(mesh.triangles[:,:,2]-zmin)<1e-4,axis=1))
 regions=[]
 for sub in mesh.submesh([bad],append=True).split(only_watertight=False):
  regions.append({'area_mm2':float(sub.area),'bounds_print_mm':sub.bounds.tolist(),'normal_area_sum':(sub.face_normals*sub.area_faces[:,None]).sum(axis=0).tolist()})
 undersides[name]=sorted(regions,key=lambda x:x['area_mm2'],reverse=True)
report={'scope':'Diagnostic surface samples, not a proof of leak area or a manufacturing qualification. Frozen V3 only.', 'exposed_intended_void_faces':exposed,'underside_regions':undersides}
(out/'defect-localization.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
