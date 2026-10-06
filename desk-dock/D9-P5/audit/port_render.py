"""Side elevation looking down -X: laptop, port marker, base pivot, arm."""
import json,math,sys
from pathlib import Path
import cadquery as cq
from PIL import ImageDraw
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'generated'
sys.path.insert(0,str(HERE.parent/'source-inputs'));from raster import render,font
P=json.loads((HERE.parent/'source-inputs/parameters.json').read_text());LEAN=P['laptop_lean_deg']
def box(x,y,z,a,b,c):return cq.Solid.makeBox(a,b,c,cq.Vector(x,y,z))
def lean(y,z):
    t=math.radians(-LEAN);dy,dz=y,z-54.0
    return (dy*math.cos(t)-dz*math.sin(t),54.0+dy*math.sin(t)+dz*math.cos(t))
laptop=box(0,-P['laptop_thickness']/2,62,P['laptop_width'],P['laptop_thickness'],232.33).rotate((0,0,54),(1,0,54),-LEAN)
man=json.loads((OUT/'manifest.json').read_text())
rx0,ry0,rz0=man['accessory_socket']['socket_origin'];BY,BZ=ry0+19,rz0+24
objs=[(laptop.intersect(box(-90,-60,0,180,140,300)),(46,52,58))]
NEAR={'plug-holder-clamp-shoulder':(150,110,60),'plug-holder-polar-inner-arm':(60,130,150),
      'plug-holder-polar-outer-arm':(80,160,180),'plug-holder-polar-plug-rotor':(210,90,70),
      'plug-holder-clamp-nut':(190,150,80),'accessory-socket-body':(110,120,130)}
for n,c in NEAR.items():
    objs.append((cq.importers.importStep(str(OUT/(n+'.step'))).val(),c))
# port markers: 10-mm balls on the two port axes, x at the plug-end face
for tag,off,col in (('port1',P['port_from_rear_case'],(255,60,60)),('port2',P['second_port_from_rear_case'],(255,150,40))):
    py,pz=lean(P['port_y'],P['rear_case_seat_z']+off)
    objs.append((cq.Solid.makeSphere(6,cq.Vector(0,py,pz),angleDegrees1=-90),col))
    print(tag,'leaned y=%.2f z=%.2f  radius_from_pivot=%.2f'%(py,pz,math.hypot(py-BY,pz-BZ)))
# pivot marker
objs.append((cq.Solid.makeSphere(5,cq.Vector(-60,BY,BZ),angleDegrees1=-90),(60,220,120)))
im,_=render(objs,(1500,1250),(-1,0,0),pad=60)
d=ImageDraw.Draw(im)
d.text((30,20),'D9-P5 looking down -X: red/orange = laptop USB-C ports, green = clamp pivot axis',font=font(26,True),fill='#101010')
im.save(HERE/'port-reach.png');print('wrote',HERE/'port-reach.png')
