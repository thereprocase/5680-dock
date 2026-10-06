"""Changed-geometry screen: stationary solids, nominal docking path, STEP."""
import itertools,json
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
static=[a for a in parts if a['name']!='Precision_5680_REFERENCE' and not any(k in a['name'] for k in ['seal','pad'])]
motion=[]
for x,z in [(18,z) for z in [135,80,30,24,10,0]]+[(x,0) for x in [15,10,6,4,2,0]]:
 s=laptop.translate((x,0,z));coll=[]
 for a in static:
  v=overlap(s,a['shape'])
  if v>.01:coll.append([a['name'],round(v,3)])
 motion.append({'offset_xz_mm':[x,z],'collisions':coll})
back=cq.importers.importStep(str(R/'Precision_5680_D2.step'))
data={'nominal_rigid_collisions':hits,'docking_path_samples':motion,'step_solids':len(back.solids().vals()),'step_all_valid':all(s.isValid() for s in back.solids().vals()),'scope':'Simplified nominal envelope and sampled path only; does not qualify real hardware, all adjustment positions, manufacturing, loads or airflow.'}
(R/'validation.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data,indent=2))
