"""Two views of the plug end: down -X (Y-Z plane) and down +Y (X-Z plane) with
laptop, both ports, base pivot and every part near the plug end."""
import json,math,sys
from pathlib import Path
import cadquery as cq
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'generated'
sys.path.insert(0,str(HERE.parent/'source-inputs'));from raster import render,font
P=json.loads((HERE.parent/'source-inputs/parameters.json').read_text());LEAN=P['laptop_lean_deg']
def box(x,y,z,a,b,c):return cq.Solid.makeBox(a,b,c,cq.Vector(x,y,z))
def lean(y,z):
    t=math.radians(-LEAN);dy,dz=y,z-54.0
    return (dy*math.cos(t)-dz*math.sin(t),54.0+dy*math.sin(t)+dz*math.cos(t))
man=json.loads((OUT/'manifest.json').read_text())
rx0,ry0,rz0=man['accessory_socket']['socket_origin'];BY,BZ=ry0+19,rz0+24
laptop=box(0,-P['laptop_thickness']/2,62,P['laptop_width'],P['laptop_thickness'],232.33).rotate((0,0,54),(1,0,54),-LEAN)
crop=box(-100,-70,-10,200,200,280)
objs=[(laptop.intersect(crop),(46,52,58))]
COL={'plug-holder-clamp-shoulder':(150,110,60),'plug-holder-polar-inner-arm':(60,130,150),
     'plug-holder-polar-outer-arm':(80,160,180),'plug-holder-polar-plug-rotor':(210,90,70),
     'plug-holder-clamp-nut':(190,150,80),'accessory-socket-body':(110,120,130),
     'M1-outer-cradle-shell':(200,200,205),'M1-inner-shell':(170,180,190),'M1-contact-cassette':(120,140,120)}
for n,c in COL.items():
    s=cq.importers.importStep(str(OUT/(n+'.step'))).val().intersect(crop)
    if s.Volume()>1:objs.append((s,c))
for off,col in ((P['port_from_rear_case'],(255,60,60)),(P['second_port_from_rear_case'],(255,150,40))):
    py,pz=lean(P['port_y'],P['rear_case_seat_z']+off)
    # port marker drawn as a short X-axis rod sticking out of the laptop face, so it shows in both views
    objs.append((cq.Solid.makeCylinder(4,40,cq.Vector(-40,py,pz),cq.Vector(1,0,0)),col))
objs.append((cq.Solid.makeCylinder(3,60,cq.Vector(-95,BY,BZ),cq.Vector(1,0,0)),(60,220,120)))
a,_=render(objs,(1400,1400),(-1,0,0),pad=40)
b,_=render(objs,(1400,1400),(0,-1,0),pad=40)
page=Image.new('RGB',(2800,1460),'#f8f8f8');page.paste(a,(0,60));page.paste(b,(1400,60))
d=ImageDraw.Draw(page)
d.text((20,12),'Looking down -X (Y-Z plane).  +Y (lid/fans) is LEFT, +Z up.',font=font(28,True),fill='#101010')
d.text((1420,12),'Looking down +Y (X-Z plane).  +X (into laptop) is LEFT, +Z up.',font=font(28,True),fill='#101010')
d.text((20,1425),'red/orange rods = USB-C port axes (40 mm long, from x=-40 to the laptop face at x=0).  green rod = base pivot axis.',font=font(24),fill='#303030')
page.save(HERE/'plug-end-views.png');print('wrote plug-end-views.png')
