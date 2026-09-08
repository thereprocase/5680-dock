"""Render exact regenerated D8 CAD from the optional BREP review cache."""
from pathlib import Path
import argparse,json
import cadquery as cq
from raster import render,font
from PIL import Image,ImageDraw
parser=argparse.ArgumentParser();parser.add_argument('cache',type=Path);args=parser.parse_args()
root=Path(__file__).resolve().parent
parts=[dict(a,shape=cq.Shape.importBrep(str(args.cache/(a['name']+'.brep')))) for a in json.loads((args.cache/'parts.json').read_text())]
for a in parts:
 if 'manifold_with_cradle' in a['name']:a['color']=(136,149,152)
 elif a['name']=='connector_module_body':a['color']=(87,137,157)
objects=[(a['shape'],a['color']) for a in parts]
im,_=render(objects,(1400,1000),(-.55,1,.55),pad=45);im.save(root/'D8-assembled.png')
objects=[]
for a in parts:
 n=a['name'];s=a['shape'];color=a['color']
 if a['reference'] or any(k in n for k in ['hinge_seal','lid_bearing','corner_pad']):continue
 if 'bottom_panel' in n:s=s.translate((0,0,-35));color=(86,142,159)
 if 'bottom_thumb_lock' in n:s=s.translate((0,0,-42))
 objects.append((s,color))
im,_=render(objects,(1400,850),(-.4,-1,-.55),pad=45);im.save(root/'D8-service-covers.png')
objects=[]
for a in parts:
 n=a['name'];s=a['shape'];color=a['color']
 if n=='01_manifold_with_cradle':
  s=s.intersect(cq.Workplane('XY').box(145,200,240,centered=False).translate((-100,-60,-8)).val())
  color=(176,184,180)
 elif n=='connector_module_body':color=(78,129,152)
 elif not (n.startswith(('cassette_','breakaway_','connector_mount_','chassis_stop_')) or n in ['X_depth_overmold_clamp','sliding_plug_cap','Dell_plug_overmold_REFERENCE','USB_C_shell_REFERENCE','independent_printed_chassis_stop_screw','stop_soft_tip']):continue
 objects.append((s,color))
im,_=render(objects,(1200,1000),(-.75,-1,.45),pad=55);im.save(root/'D8-connector.png')
canvas=Image.new('RGB',(1800,840),(248,248,248));draw=ImageDraw.Draw(canvas)
for label,name,x in [('Shell feet and removable covers','D8-service-covers.png',0),('Removable connector and live Y/Z slides','D8-connector.png',900)]:
 im=Image.open(root/name);im.thumbnail((875,770));canvas.paste(im,(x+(900-im.width)//2,65+(770-im.height)//2))
 draw.text((x+22,22),label,font=font(24,True),fill=(35,57,60))
canvas.save(root/'D8-changes.png')
print('Exact CAD review images saved',flush=True)
