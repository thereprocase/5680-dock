"""Changed-geometry screen: stationary solids, nominal docking path, STEP."""
import itertools,json,math
from pathlib import Path
import cadquery as cq
import build
R=Path(__file__).resolve().parent
parts=build.parts

def overlap(a,b):
 A=a.BoundingBox();B=b.BoundingBox()
 if A.xmax<=B.xmin+1e-6 or B.xmax<=A.xmin+1e-6 or A.ymax<=B.ymin+1e-6 or B.ymax<=A.ymin+1e-6 or A.zmax<=B.zmin+1e-6 or B.zmax<=A.zmin+1e-6:return 0
 return a.intersect(b).Volume()
rigid=[a for a in parts if (not a['reference'] or 'fan_frame' in a['name'] or 'fan_hub' in a['name'] or 'blade_' in a['name']) and not any(k in a['name'] for k in ['pad','seal','foot','soft'])]
hits=[]
for a,b in itertools.combinations(rigid,2):
 if a['reference'] and b['reference']:continue
 v=overlap(a['shape'],b['shape'])
 if v>.01:hits.append([a['name'],b['name'],round(v,3)])
laptop=next(a['shape'] for a in parts if a['name']=='Precision_5680_REFERENCE')
static=[a for a in parts if a['name']!='Precision_5680_REFERENCE' and not a['name'].startswith('RUBBER_FOOT_') and not any(k in a['name'] for k in ['seal','pad'])]
motion=[]
for x,z in [(18,z) for z in [135,80,30,24,10,0]]+[(x,0) for x in [15,10,6,4,2,0]]:
 shift=(x,math.sin(math.radians(build.LEAN))*z,math.cos(math.radians(build.LEAN))*z)
 s=laptop.translate(shift);coll=[]
 for a in static:
  v=overlap(s,a['shape'])
  if v>.01:coll.append([a['name'],round(v,3)])
 foot_hits=[]
 for keep in build.foot_keepouts:
  for a in static:
   v=overlap(keep.translate(shift),a['shape'])
   if v>.01:foot_hits.append([a['name'],round(v,3)])
 motion.append({'offset_xz_mm':[x,z],'collisions':coll,'expanded_foot_keepout_collisions':foot_hits})
# Cross-check against source coordinates, not a reflected CAD expectation.
import numpy as np
from raster import render
plug=next(a['shape'] for a in parts if a['name']=='USB_C_shell_REFERENCE')
assert plug.BoundingBox().xmin<0 and 0<plug.BoundingBox().xmax<7
assert all(a['shape'].Center().y>build.T/2 for a in parts if 'fan_frame' in a['name'])
port_probes=[]
for port in build.port_study['ports']:
    left=port['side']=='keyboard-left'
    assert (port['source_center_mm'][0]<0)==left
    z=build.H+port['case_offset_from_rear_mm']; y=port['case_y_mm']
    x=.2 if left else build.W-1
    other=build.W-1 if left else .2
    probe=build.leaned(build.box(x,y-.5,z-.5,.8,1,1).val())
    opposite=build.leaned(build.box(other,y-.5,z-.5,.8,1,1).val())
    v=overlap(laptop,probe); ov=overlap(laptop,opposite)
    assert v<1e-6 and ov>.79,(port['name'],v,ov)
    port_probes.append(dict(name=port['name'],side=port['side'],opening_material_mm3=v,opposite_edge_material_mm3=ov))
# Standard +Y lid camera sees the source -X (keyboard-left) end at screen-right.
_,project=render([(laptop,(180,180,180))],(300,250),(0,1,0))
screen=project([[0,0,build.P],[build.W,0,build.P]])
assert screen[0,0]>screen[1,0]
assert all(not row['collisions'] and not row['expanded_foot_keepout_collisions'] for row in motion),motion
assert not hits,hits
back=cq.importers.importStep(str(R/'Precision_5680_D6.step'))
data={'orientation':{'plug_edge':'far, keyboard-left; photo right','docking_direction':'-X','port_probes':port_probes,'lid_camera_keyboard_left_screen_right':True,'source_handedness_preserved':True},'nominal_rigid_collisions':hits,'docking_path_samples':motion,'step_solids':len(back.solids().vals()),'step_all_valid':all(s.isValid() for s in back.solids().vals()),'scope':'Simplified nominal envelope and sampled path only; does not qualify real hardware, all adjustment positions, manufacturing, loads or airflow.'}
(R/'validation.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data,indent=2))
