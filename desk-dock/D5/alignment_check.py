"""Quantify rib free area and screen representative funnel-entry corrections."""
from pathlib import Path
import json,math
import build
R=Path(__file__).resolve().parent
lap=next(a['shape'] for a in build.parts if a['name']=='Precision_5680_REFERENCE')
static=[a for a in build.parts if a['name']!='Precision_5680_REFERENCE' and not a['name'].startswith('RUBBER_FOOT_') and not 'seal' in a['name']]
def overlap(a,b):
 A=a.BoundingBox();B=b.BoundingBox()
 if A.xmax<=B.xmin+1e-5 or B.xmax<=A.xmin+1e-5 or A.ymax<=B.ymin+1e-5 or B.ymax<=A.ymin+1e-5 or A.zmax<=B.zmin+1e-5 or B.zmax<=A.zmin+1e-5:return 0
 return a.intersect(b).Volume()
lo,hi=build.contacts['intake_window_case_relative_bounds_mm'];area=(hi[0]-lo[0])*(hi[2]-lo[2])
frame=build.rib_frame.rotate((0,0,build.H),(1,0,build.H),build.LEAN)
slab=build.box(lo[0],-17.01,build.H+lo[2],hi[0]-lo[0],.02,hi[2]-lo[2]).val()
blocked=frame.intersect(slab).Volume()/.02
free=1-blocked/area
assert free>=.8
entry=[]
for err in [-3,0,3]:
 for h in [85,80,75,70,65,62,50,0]:
  correction=err*max(0,min(1,(h-68)/17))
  shift=(-18,math.sin(math.radians(build.LEAN))*h+correction,math.cos(math.radians(build.LEAN))*h)
  hits=[];feet=[]
  for a in static:
   v=overlap(lap.translate(shift),a['shape'])
   if v>.02:hits.append([a['name'],round(v,3)])
   for keep in build.foot_keepouts:
    v=overlap(keep.translate(shift),a['shape'])
    if v>.02:feet.append([a['name'],round(v,3)])
  entry.append({'initial_cross_slot_error_mm':err,'lift_mm':h,'remaining_error_mm':correction,'collisions':hits,'foot_keepout_collisions':feet})
data={'laptop_lean_deg':build.LEAN,'intake_window_mm2':area,'rib_projected_blockage_mm2':blocked,'rib_net_free_fraction':free,'funnel_entry_samples':entry,'scope':'Geometric prescribed paths, not a gravity/friction/dynamic self-centering simulation. Net free area is the added stand structure over the OEM intake window; excludes OEM grille solidity. Foot keepouts expand the visualization-mesh bounds by 2 mm.'}
(R/'alignment-validation.json').write_text(json.dumps(data,indent=2)+'\n')
print('Net free area',free,'entry collision poses',sum(bool(a['collisions']) for a in entry),'foot keepout poses',sum(bool(a['foot_keepout_collisions']) for a in entry))
for a in entry:
 if a['collisions'] or a['foot_keepout_collisions']:print(a)
