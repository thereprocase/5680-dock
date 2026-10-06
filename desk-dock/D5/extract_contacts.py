"""Contact curves and rubber-foot keepouts from Dell-linked visualization mesh."""
from pathlib import Path
import json,hashlib,sys
import numpy as np,trimesh
R=Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit('Usage: python extract_contacts.py /path/to/decompressed/laptop.glb')
source=Path(sys.argv[1])
s=trimesh.load(source)
def node(n):
 t,gn=s.graph[n];g=s.geometry[gn].copy();g.apply_transform(t);g.apply_scale(1000);return g
case=node('Dell4649');foot=node('Dell4604');rear=case.bounds[0,2]
# Outer rear-case boundary: smallest rear coordinate at each thickness station.
curves=[]
for x in [155,160,166.84,170,174]:
 seg=trimesh.intersections.mesh_plane(case,[1,0,0],[x,0,0]);values=[]
 for y in np.linspace(8.5,17.5,46):
  hits=[]
  for a,b in seg:
   if abs(b[1]-a[1])<1e-8:continue
   t=(y-a[1])/(b[1]-a[1])
   if 0<=t<=1:hits.append(float(a[2]+t*(b[2]-a[2])))
  if hits:values.append([float(y-22.17/2),float(min(hits)-rear)])
 curves.append({'case_x_from_center_mm':x,'rear_curve_local_yz_mm':values})
footboxes=[]
for tag,mask in [('rear_strip',foot.vertices[:,2]<0),('front_left',(foot.vertices[:,2]>0)&(foot.vertices[:,0]<0)),('front_right',(foot.vertices[:,2]>0)&(foot.vertices[:,0]>0))]:
 v=foot.vertices[mask];b=np.array([v.min(0),v.max(0)]);b[:,0]+=353.68/2;b[:,1]-=22.17/2;b[:,2]-=rear
 footboxes.append({'name':tag,'untilted_case_relative_bounds_mm':b.tolist()})
data={'source_url':'https://content.hmxmedia.com/precision-16-5680-laptop-AR/gltf/precision-16-5680-laptop-AR.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'case_node':'Dell4649','feet_node':'Dell4604','datum':'X before D3 reflection; Y about closed-envelope midplane; Z from rear-case datum. Build adds seat height, reflects X and applies lean.','curves':curves,'rubber_feet':footboxes,'keepout_expansion_mm':2,'limits':'Visualization mesh, not manufacturing tolerances. Five side sections establish the sculpted seat envelope; replaceable liners absorb residual fit. Lid envelope retains published thickness.'}
vent=node('Dell4607').bounds.copy();vent[:,0]+=353.68/2;vent[:,1]-=22.17/2;vent[:,2]-=rear
data['intake_window_case_relative_bounds_mm']=vent.tolist()
(R/'contact-profiles.json').write_text(json.dumps(data,indent=2)+'\n')
print('Foot bounds:',footboxes)
