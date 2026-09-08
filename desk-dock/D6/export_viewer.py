"""Export the actual CAD tessellation to the dependency-free showcase mesh format."""
from pathlib import Path
import json,struct
import build
R=Path(__file__).resolve().parents[2]/'docs/models/desk-dock-d6'
R.mkdir(parents=True,exist_ok=True)
data=bytearray(); entries=[]
for p in build.parts:
 v,f=p['shape'].tessellate(.35,.2)
 off=len(data)
 for a in v:data.extend(struct.pack('<fff',a.x,a.y,a.z))
 io=len(data)
 for a in f:data.extend(struct.pack('<III',*a))
 b=p['shape'].BoundingBox()
 entries.append(dict(name=p['name'],color=p['color'],reference=p['reference'],positionOffset=off,vertexCount=len(v),indexOffset=io,indexCount=len(f)*3,center=[(b.xmin+b.xmax)/2,(b.ymin+b.ymax)/2,(b.zmin+b.zmax)/2]))
(R/'model.bin').write_bytes(data)
(R/'model.json').write_text(json.dumps(dict(revision='D6',units='mm',coordinate_frame=build.p['coordinate_frame'],undocked_x_offset_mm=18,laptop_lean_deg=build.LEAN,parts=entries),indent=2)+'\n')
print('Viewer mesh:',len(entries),'parts,',len(data),'bytes')
