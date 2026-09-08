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
for x,z in [(-18,z) for z in [135,80,30,24,10,0]]+[(-x,0) for x in [15,10,6,4,2,0]]:
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
# Check orientation independently of the collision screen. Reflected geometry
# preserves old clearances; these assertions catch the specific handedness bug.
plug=next(a['shape'] for a in parts if a['name']=='USB_C_shell_REFERENCE')
assert plug.BoundingBox().xmax>build.W
assert plug.BoundingBox().xmin>build.W-7
assert all(a['shape'].Center().y>build.T/2 for a in parts if 'fan_frame' in a['name'])
# Probe voids for both keyboard-left ports on the far edge and confirm the
# corresponding near-edge locations contain laptop material.
port_probes=[]
for offset in [build.p['port_from_rear_case'],build.p['second_port_from_rear_case']]:
    z=build.H+offset
    far=build.box(build.W-1,build.Y-.5,z-.5,.8,1,1).val()
    near=build.box(.2,build.Y-.5,z-.5,.8,1,1).val()
    fv=overlap(laptop,build.leaned(far));nv=overlap(laptop,build.leaned(near))
    assert fv<1e-6 and nv>.79,(fv,nv)
    port_probes.append({'z_mm':z,'far_edge_material_mm3':fv,'near_edge_material_mm3':nv})
back=cq.importers.importStep(str(R/'Precision_5680_D5.step'))
data={'orientation':{'plug_edge':'far, keyboard-left; photo right','docking_direction':'+X','port_probes':port_probes},'nominal_rigid_collisions':hits,'docking_path_samples':motion,'step_solids':len(back.solids().vals()),'step_all_valid':all(s.isValid() for s in back.solids().vals()),'scope':'Simplified nominal envelope and sampled path only; does not qualify real hardware, all adjustment positions, manufacturing, loads or airflow.'}
(R/'validation.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data,indent=2))
