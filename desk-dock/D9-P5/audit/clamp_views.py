"""Deliverable views of the large-shaft clamp pivot, rendered from generated/*.step:
assembled (arm swung to port 1 with a plug in place), exploded clamp stack, axial
section through the pivot axis, and a close-up of the real thread geometry."""
import json,math,sys
from pathlib import Path
import cadquery as cq
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'generated';DOC=HERE.parent/'clamp-pivot-views';DOC.mkdir(exist_ok=True)
sys.path.insert(0,str(HERE.parent/'source-inputs'));from raster import render,font
P=json.loads((HERE.parent/'source-inputs/parameters.json').read_text());LEAN=P['laptop_lean_deg']
man=json.loads((OUT/'manifest.json').read_text());ACC=man['accessory_socket'];CL=ACC['base_clamp'];RE=ACC['reach']
BY,BZ=CL['pivot_axis_yz_mm'];tip_y,tip_z=RE.get('tip_pivot_yz_mm',[BY,BZ+115.5])   # modelled mid-travel tip pivot, from the builder
def box(x,y,z,a,b,c):return cq.Solid.makeBox(a,b,c,cq.Vector(x,y,z))
def L(n):return cq.importers.importStep(str(OUT/(n+'.step'))).val()
COL={'plug-holder-clamp-cam-spatula':(232,190,90),'plug-holder-clamp-shoulder':(150,110,60),'plug-holder-polar-inner-arm':(60,130,150),'plug-holder-polar-outer-arm':(80,160,180),
     'plug-holder-polar-plug-rotor':(210,90,70),'plug-holder-clamp-nut':(190,150,80),'plug-holder-clamp-pressure-washer':(230,200,120),
     'accessory-socket-body':(110,120,130),'plug-holder-tip-annular-screw':(200,170,90),'plug-holder-tip-annular-nut':(200,170,90),
     'plug-holder-tip-head-thrust-washer':(230,200,120),'plug-holder-tip-nut-thrust-washer':(230,200,120),
     'plug-holder-length-clamp-1-screw':(200,170,90),'plug-holder-length-clamp-1-nut':(200,170,90),
     'plug-holder-length-clamp-2-screw':(200,170,90),'plug-holder-length-clamp-2-nut':(200,170,90),
     'plug-holder-rotor-pinch-screw':(200,170,90),'plug-holder-rotor-pinch-nut':(200,170,90),'plug-holder-rotor-pinch-shim':(240,210,140),
     'laptop-slide-endstop-screw':(120,120,120),'laptop-slide-endstop-soft-tip':(90,90,90),
     'M1-outer-cradle-shell':(205,205,210),'M1-inner-shell':(175,185,195),'M1-contact-cassette':(120,140,120),'accessory-socket-clamp-bolt':(120,120,120)}
S={n:L(n) for n in COL}
ARM=['plug-holder-polar-inner-arm'];OUTER=[n for n in COL if n.startswith('plug-holder-polar-') and n not in ARM]+[n for n in COL if n.startswith(('plug-holder-tip','plug-holder-length','plug-holder-rotor-'))]
laptop=box(0,-P['laptop_thickness']/2,62,P['laptop_width'],P['laptop_thickness'],232.33).rotate((0,0,54),(1,0,54),-LEAN)
CAM='plug-holder-clamp-cam-spatula';CAM_ROT0=CL['cam_plate']['modelled_rotation_deg']
def posed(tag):
    rec=RE['ports'][tag];phi=rec['arm_angle_deg'];dR=(BZ+rec['tip_radius_mm'])-tip_z
    out=dict(S)
    for n in ARM:out[n]=S[n].rotate((0,BY,BZ),(1,BY,BZ),phi)
    psi=rec.get('rotor_trim_deg',0.0);ROTG=('plug-holder-polar-plug-rotor','plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut','plug-holder-rotor-pinch-shim')
    for n in OUTER:
        s=S[n].rotate((0,tip_y,tip_z),(1,tip_y,tip_z),psi) if n in ROTG else S[n]
        out[n]=s.translate((0,0,dR)).rotate((0,BY,BZ),(1,BY,BZ),phi)
    out[CAM]=S[CAM].rotate((0,BY,BZ),(1,BY,BZ),rec['cam_rotation_deg']-CAM_ROT0)
    return out
def lean_pt(y,z):
    t=math.radians(-LEAN);dy,dz=y,z-54.0
    return (dy*math.cos(t)-dz*math.sin(t),54.0+dy*math.sin(t)+dz*math.cos(t))
def plug_at(tag):
    py,pz=RE['ports'][tag]['leaned_yz_mm']
    body=box(-P['plug_length']+P['plug_tip_length'],-P['plug_minor']/2,-P['plug_major']/2,P['plug_length'],P['plug_minor'],P['plug_major'])
    boot=cq.Solid.makeCylinder(4.5,45.0-(P['plug_length']-P['plug_tip_length'])+0.1,cq.Vector(-45.0,0,0),cq.Vector(1,0,0))
    cable=cq.Solid.makeCylinder(2.5,65.1,cq.Vector(-110.0,0,0),cq.Vector(1,0,0))
    return body.fuse(boot).fuse(cable).rotate((0,0,0),(1,0,0),-LEAN).translate((0,py,pz))
def page(im,title,sub,name):
    pg=Image.new('RGB',(im.width,im.height+110),'#f8f8f8');pg.paste(im,(0,100));d=ImageDraw.Draw(pg)
    d.text((28,18),title,font=font(34,True),fill='#101010');d.text((28,62),sub,font=font(22),fill='#404040')
    pg.save(DOC/name);print('wrote',name,flush=True)

crop=box(-120,-40,-10,240,220,280)
# 1. assembled, arm at port 1, plug in the port
objs=[(laptop.intersect(crop),(46,52,58))]
pp=posed('port-1')
for n,s in pp.items():
    c=s.intersect(crop)
    if c.Volume()>1:objs.append((c,COL[n]))
objs.append((plug_at('port-1'),(40,200,90)))
im,_=render(objs,(1700,1300),(-1.0,-0.85,0.6),pad=40)
page(im,'Assembled: arm swung to USB-C port 1',f"arm {RE['ports']['port-1']['arm_angle_deg']} deg, tip radius {RE['ports']['port-1']['tip_radius_mm']} mm; green = 25-mm plug and boot at the port datum",'01-assembled-port-1.png')
im,_=render(objs,(1700,1300),(-1.0,0.0,0.0),pad=40)
page(im,'Assembled, looking down -X from the plug end','pocket centred on port 1; the shoulder skirt is now 36 mm clear of the port axis','02-assembled-end-view.png')

# 2. exploded clamp stack along X (outboard is -X)
EXP={'plug-holder-clamp-nut':-95,'plug-holder-clamp-pressure-washer':-70,'plug-holder-clamp-cam-spatula':-50,'plug-holder-polar-inner-arm':-25,'plug-holder-clamp-shoulder':0,
     'plug-holder-polar-outer-arm':-25,'plug-holder-polar-plug-rotor':-25,'accessory-socket-body':35,'accessory-socket-clamp-bolt':35,
     'plug-holder-tip-annular-screw':-25,'plug-holder-tip-annular-nut':-25,'plug-holder-tip-head-thrust-washer':-25,'plug-holder-tip-nut-thrust-washer':-25,
     'plug-holder-length-clamp-1-screw':-25,'plug-holder-length-clamp-1-nut':-25,'plug-holder-length-clamp-2-screw':-25,'plug-holder-length-clamp-2-nut':-25,'plug-holder-rotor-pinch-screw':-25,'plug-holder-rotor-pinch-nut':-25,'plug-holder-rotor-pinch-shim':-25}
objs=[(S[n].translate((dx,0,0)),COL[n]) for n,dx in EXP.items()]
im,_=render(objs,(1700,1300),(-1.0,-0.9,0.55),pad=40)
page(im,'Exploded clamp stack (outboard is -X)','nut, keyed pressure washer, cam-lobe spatula, arm base disc, shoulder with 50-mm shaft; socket body and clamp bolt behind','03-exploded-clamp-stack.png')

# 3. axial section through the pivot axis (plane y = BY), viewed from -Y
half=box(-200,BY,-100,400,300,400)
sec=[]
for n in ('plug-holder-clamp-shoulder','plug-holder-polar-inner-arm','plug-holder-clamp-cam-spatula','plug-holder-clamp-pressure-washer','plug-holder-clamp-nut','plug-holder-polar-outer-arm','accessory-socket-body','plug-holder-polar-plug-rotor'):
    c=S[n].intersect(half)
    if c.Volume()>1:sec.append((c,COL[n]))
im,_=render(sec,(1700,1300),(0,-1,0),pad=40)
d=ImageDraw.Draw(im)
page(im,'Axial section through the pivot axis (plane through y = %.0f, seen from -Y)'%BY,'journal, arm bore, clamping faces (shoulder plate | arm disc | washer | nut), outboard thread and hollow bore','04-axial-section.png')

# 4. thread close-up: the top of the thread/nut engagement in the same section
th=CL['thread']
zoom=box(-82,BY-1,BZ+15,52,60,20)
close=[]
for n in ('plug-holder-clamp-shoulder','plug-holder-clamp-nut','plug-holder-clamp-pressure-washer','plug-holder-clamp-cam-spatula','plug-holder-polar-inner-arm'):
    c=S[n].intersect(half).intersect(zoom)
    if c.Volume()>.5:close.append((c,COL[n]))
im,_=render(close,(1700,1100),(0,-1,0),pad=30)
page(im,'Thread close-up, real mating geometry in section','%s: major %.1f, core %.1f, pitch %.1f, depth %.2f, crest %.2f mm; radial clearance %.2f, axial %.2f per flank; %.0f turns engaged'%(th['form'],th['major_diameter_mm'],th['core_diameter_mm'],th['pitch_mm'],th['depth_mm'],th['crest_width_mm'],th['radial_clearance_mm'],th['axial_clearance_per_flank_mm'],th['turns_engaged']),'05-thread-closeup.png')

# 5. rotor and pocket at port 1, close, from the plug end
pp=posed('port-1');zoom=box(-115,-30,60,135,140,110)
objs=[(laptop.intersect(zoom),(46,52,58)),(plug_at('port-1'),(40,200,90))]
for n in ('plug-holder-polar-plug-rotor','plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut','plug-holder-rotor-pinch-shim','plug-holder-clamp-cam-spatula','plug-holder-polar-outer-arm','plug-holder-clamp-shoulder','plug-holder-tip-annular-nut','plug-holder-tip-nut-thrust-washer','laptop-slide-endstop-soft-tip','laptop-slide-endstop-screw'):
    c=pp[n].intersect(zoom)
    if c.Volume()>1:objs.append((c,COL[n]))
im,_=render(objs,(1700,1300),(-1.0,-0.6,0.45),pad=30)
page(im,'Plug carrier on the leaf lobe at port 1','green = plug, boot and cable. Carrier rolled %.1f deg to the plug, pinch screw through the thick wall; the lobe edge runs to the boot and the carrier back face bears on the lobe'%RE['pocket_pre_roll_deg'],'06-rotor-at-port.png')

# 7. plug end view of the carrier on the lobe: is the tunnel open, where does the edge stop
objs=[(plug_at('port-1'),(40,200,90))]
for n in ('plug-holder-polar-plug-rotor','plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut','plug-holder-rotor-pinch-shim','plug-holder-clamp-cam-spatula','plug-holder-polar-outer-arm','plug-holder-polar-inner-arm','plug-holder-clamp-nut'):
    c=pp[n].intersect(box(-115,-40,40,135,150,140))
    if c.Volume()>1:objs.append((c,COL[n]))
im,_=render(objs,(1500,1500),(-1.0,0.0,0.0),pad=30)
page(im,'Carrier, lobe and plug from the plug end (port 1)','looking down -X: the spiral edge stops at the boot; the plug tunnel through the pocket is open','07-lobe-and-tunnel-end-view.png')

# 8. section through the carrier window across the plug: shim cradle, screw tip in the recess, boot
_py,_pz=RE['ports']['port-1']['leaned_yz_mm'];pp=posed('port-1')
cutx=box(-13.25,-100,-100,4.0,400,400)   # a 4-mm slab about the pinch axis, x -13.25..-9.25
objs=[(plug_at('port-1').intersect(cutx),(40,200,90))]
for n in ('plug-holder-polar-plug-rotor','plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut','plug-holder-rotor-pinch-shim','plug-holder-clamp-cam-spatula'):
    c=pp[n].intersect(cutx)
    if c.Volume()>.5:objs.append((c,COL[n]))
im,_=render(objs,(1500,1300),(-1.0,0.0,0.0),pad=30)
page(im,'Carrier window in section at the pinch axis (port 1)','4-mm slab at x -13..-9 seen from the plug end: screw through the thick wall and nut, flat tip in the shim recess, flat shim on the overmold flat, overmold against the thin wall','08-window-section.png')
