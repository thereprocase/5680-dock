"""Export the actual CAD tessellation to the dependency-free showcase mesh format."""
from pathlib import Path
import json,struct,math
import build
from breakaway_geometry import datum,cam_lift,make_spring,moving_names
R=Path(__file__).resolve().parents[2]/'docs/models/desk-dock-d7'
R.mkdir(parents=True,exist_ok=True)
data=bytearray(); entries=[]
def append_mesh(shape):
 v,f=shape.tessellate(.35,.2)
 off=len(data)
 for a in v:data.extend(struct.pack('<fff',a.x,a.y,a.z))
 io=len(data)
 for a in f:data.extend(struct.pack('<III',*a))
 return dict(positionOffset=off,vertexCount=len(v),indexOffset=io,indexCount=len(f)*3)

for p in build.parts:
 entry=dict(name=p['name'],color=p['color'],reference=p['reference'],**append_mesh(p['shape']))
 b=p['shape'].BoundingBox()
 entry['center']=[(b.xmin+b.xmax)/2,(b.ymin+b.ymax)/2,(b.zmin+b.zmax)/2]
 n=p['name']; angle=45; lift=cam_lift(build.p,angle); px,pz=datum(build.p)
 folded=None
 if n=='breakaway_spring_cartridge':
  entry['motion']='spring'
  # Match the actual piecewise cubic leaf profile used by make_spring.
  # Tessellation topology is retained throughout motion; only its displacement
  # changes. Fixed frame vertices have zero weight and the island has one.
  vertices,_=p['shape'].tessellate(.35,.2)
  entry['springWeightOffset']=len(data)
  for v in vertices:
   dy=v.y; dz=v.z-build.H; a=math.radians(build.LEAN)
   local_z=dy*math.sin(a)+dz*math.cos(a)+build.H
   u=max(0,min(1,(38-abs(v.x-px))/build.p['breakaway']['spring_leaf_length_mm']))
   step=min(19,math.floor(u*20)); q=u*20-step
   f=lambda x:3*x*x-2*x*x*x
   weight=(f(step/20)*(1-q)+f((step+1)/20)*q) if abs(local_z-pz)<=12.0001 else 0
   data.extend(struct.pack('<f',weight))
  folded=build.leaned(make_spring(build.p,build.p['breakaway']['spring_preload_deflection_mm']+lift).val())
 elif moving_names(n) or n in ['breakaway_pivot_pin_10mm','breakaway_preload_hand_nut']:
  entry['motion']='rotate' if moving_names(n) else 'axial'
  folded=p['shape'].rotate((0,0,build.H),(1,0,build.H),build.LEAN)
  if moving_names(n):folded=folded.rotate((px,0,pz),(px,1,pz),angle)
  folded=build.leaned(folded.translate((0,-lift,0)))
 if folded is not None:entry['folded']=append_mesh(folded)
 entries.append(entry)
(R/'model.bin').write_bytes(data)
px,pz=datum(build.p); a=math.radians(build.LEAN); hinge=build.p['breakaway']
animation=dict(pivot=[px,(pz-build.H)*math.sin(a),build.H+(pz-build.H)*math.cos(a)],
 axis=[0,math.cos(a),-math.sin(a)],maxAngleDeg=45,
 springRate=2*hinge['nominal_E_MPa']*hinge['spring_width_mm']*hinge['spring_thickness_mm']**3/hinge['spring_leaf_length_mm']**3,
 preload=hinge['spring_preload_deflection_mm'],rise=hinge['cam_rise_mm'],torque=hinge['nominal_release_N']*27.15)
(R/'model.json').write_text(json.dumps(dict(revision='D7',units='mm',coordinate_frame=build.p['coordinate_frame'],undocked_x_offset_mm=18,laptop_lean_deg=build.LEAN,breakawayAnimation=animation,parts=entries),indent=2)+'\n')
print('Viewer mesh:',len(entries),'parts,',len(data),'bytes')
