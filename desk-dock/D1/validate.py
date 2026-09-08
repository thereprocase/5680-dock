"""Geometric screen: separate rigid parts, 27 adjustment combinations, STEP.
Soft pads, references and schematic fasteners are not certified by this test.
"""
import json,itertools
from pathlib import Path
import cadquery as cq
import build
R=Path(__file__).resolve().parent
parts=build.parts
def overlap(a,b):
 A=a.BoundingBox();B=b.BoundingBox()
 if A.xmax<=B.xmin+1e-6 or B.xmax<=A.xmin+1e-6 or A.ymax<=B.ymin+1e-6 or B.ymax<=A.ymin+1e-6 or A.zmax<=B.zmin+1e-6 or B.zmax<=A.zmin+1e-6:return 0
 return a.intersect(b).Volume()
rigid=[a for a in parts if not a['reference'] and not any(k in a['name'] for k in ['pad','seal','foot','soft'])]
collisions=[]
for a,b in itertools.combinations(rigid,2):
 v=overlap(a['shape'],b['shape'])
 if v>.01:collisions.append([a['name'],b['name'],round(v,3)])
names=['Z_height_carrier','Y_lateral_carrier','X_depth_overmold_clamp','removable_plug_cap','01_fan_deck_with_plug_support']
shapes={a['name']:a['shape'] for a in parts if a['name'] in names}
travel=[]
for dx,dy,dz in itertools.product([-5,0,5],[-3,0,3],[-5,0,5]):
 moved={}
 for n,s in shapes.items():
  shift=(0,0,0)
  if n.startswith('Z_'):shift=(0,0,dz)
  elif n.startswith('Y_'):shift=(0,dy,dz)
  elif n.startswith('X_') or n=='removable_plug_cap':shift=(dx,dy,dz)
  moved[n]=s.translate(shift)
 hits=[]
 for na,nb in itertools.combinations(moved,2):
  v=overlap(moved[na],moved[nb])
  if v>.01:hits.append([na,nb,round(v,3)])
 travel.append({'xyz_mm':[dx,dy,dz],'collisions':hits})
back=cq.importers.importStep(str(R/'Precision_5680_D1.step'))
data={'nominal_rigid_collisions':collisions,'adjustment_positions':travel,
 'step_roundtrip_solids':len(back.solids().vals()),'step_all_valid':all(s.isValid() for s in back.solids().vals()),
 'limits':'Solid/clearance screen only. Excludes hardware thread/nut engagement, lock-screw access, pad compression, mesh-to-hardware accuracy, movement of the laptop, strength, airflow and printing.'}
(R/'validation.json').write_text(json.dumps(data,indent=2)+'\n')
print('Nominal rigid collisions:',collisions)
print('Adjustment positions with collisions:',sum(bool(t['collisions']) for t in travel),'/',len(travel))
for t in travel:
 if t['collisions']:print(t)
print('STEP:',data['step_roundtrip_solids'],data['step_all_valid'])
