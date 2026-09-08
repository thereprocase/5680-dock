"""D6 review CAD. Exported +X runs away from keyboard-left/plug end; +Y lid/fans; -Y underside/intakes; +Z up.
Builds physical duct passages, fan mounts, three adjustment stages and guards.
Separate production detailing and slicer/physical qualification remain required.
"""
from pathlib import Path
import json, math
import cadquery as cq
from cadquery import exporters
R=Path(__file__).resolve().parent
p=json.loads((R/'parameters.json').read_text())
W=p['laptop_width'];T=p['laptop_thickness'];H=p['rear_case_seat_z']
P=H+p['port_from_rear_case'];Y=p['port_y'];parts=[]
contacts=json.loads((R/'contact-profiles.json').read_text())
port_study=json.loads((R/'port-study.json').read_text())
LEAN=p['laptop_lean_deg']
def leaned(shape):return shape.rotate((0,0,H),(1,0,H),-LEAN)
def box(x,y,z,a,b,c):return cq.Workplane('XY').box(a,b,c,centered=False).translate((x,y,z))
def rb(x,y,z,a,b,c,r=2):
    s=box(x,y,z,a,b,c)
    return s.edges('|Z').fillet(r)
def hole(axis,pos,r,l):
    return cq.Solid.makeCylinder(r,l,cq.Vector(*pos),cq.Vector(*axis))
def add(n,s,col=(54,62,68),ref=False):
    if isinstance(s,cq.Workplane):s=s.val()
    assert s.isValid() and len(s.Solids())==1 and s.Volume()>0,n
    parts.append(dict(name=n,shape=s,color=col,reference=ref));return s
def slotx(y,z,length,diam=3.4,x=-60,depth=60):
    return cq.Workplane('YZ',origin=(x,0,0)).center(y,z).slot2D(length,diam,90).extrude(depth)
def screw(n,axis,start,length,r=1.5):
    v=cq.Vector(*axis);a=cq.Vector(*start)
    s=hole(axis,start,r,length).fuse(cq.Solid.makeCylinder(2.8,2.7,a-v*2.7,v))
    add(n,s,(175,181,185),True)

# Fan tops tilt toward the lid; discharge follows the configured elevation.
# Parametric fan seating plane keeps the duct behind the actual suction face.
ELEV=math.radians(p['fan_exhaust_elevation_deg']);ANGLE=90+p['fan_exhaust_elevation_deg']
FAN_Y=p['fan_center_y'];FAN_Z=p['fan_center_z']
FACE_C=FAN_Y+FAN_Z*math.tan(ELEV)-7.5/math.cos(ELEV)-.10
INNER_C=FACE_C-2.4/math.cos(ELEV)
def front_y(z,inner=False):return (INNER_C if inner else FACE_C)-math.tan(ELEV)*z

def rest_y(z):return (T/2+.6)/math.cos(math.radians(LEAN))+(z-H)*math.tan(math.radians(LEAN))
flow_voids=[];mouth_records=[]
for i,(x0,x1,fx) in enumerate([(-7,W/2,84),(W/2+.30,W+25,269.68)],1):
    length=x1-x0
    def profile(x,length,inner=False):
        if not inner:
            return (cq.Workplane('YZ',origin=(x,0,0)).moveTo(-24,3)
              .lineTo(-24,41).threePointArc((-21,48),(-13,50)).lineTo(13,50)
              .lineTo(rest_y(66),66).lineTo(rest_y(129),129)
              .lineTo(rest_y(134)+2,134).lineTo(front_y(134),134)
              .lineTo(front_y(3),3).close().extrude(length))
        return (cq.Workplane('YZ',origin=(x,0,0)).moveTo(-21.6,5.4)
              .lineTo(-21.6,40).threePointArc((-18,46),(-12,47.6)).lineTo(13,47.6)
              .lineTo(rest_y(66)+2.4,66).lineTo(rest_y(129)+2.4,129)
              .lineTo(rest_y(131.6)+3,131.6).lineTo(front_y(131.6,True),131.6)
              .lineTo(front_y(5.4,True),5.4).close().extrude(length))
    def low(x,l,rear,bottom,top,inner=False):
        return (cq.Workplane('YZ',origin=(x,0,0)).moveTo(rear,bottom).lineTo(rear,top)
          .lineTo(front_y(top,inner),top).lineTo(front_y(bottom,inner),bottom).close().extrude(l))
    outer=low(x0,length,-24,3,50).union(profile(fx-62,124))
    inner=low(x0+2.4,length-4.8,-21.6,5.4,47.6,True).union(profile(fx-59.6,119.2,True))
    edge_list=[e for e in outer.val().Edges() if abs(e.BoundingBox().ymin+24)<1e-5 and abs(e.BoundingBox().ymax+24)<1e-5 and e.BoundingBox().xlen<1e-5 and e.BoundingBox().zlen>20]
    outer=cq.Workplane(obj=outer.val().fillet(2.0,edge_list))
    roof=outer.cut(inner)
    # Keep the mouths outside bearing pads and the split joint. Full-width
    # rounded rectangles avoid a row of narrow, sharp-edged whistle slots.
    ma=max(42,x0+4);mb=min(W-24,x1-4)
    mouth=rb(ma,-10.5,43,mb-ma,21,16,4)
    roof=roof.cut(mouth)
    edges=[]
    for e in roof.val().Edges():
        bb=e.BoundingBox()
        if abs(bb.zmin-50)<1e-5 and abs(bb.zmax-50)<1e-5 and bb.xmin>=ma-.01 and bb.xmax<=mb+.01 and bb.ymin>=-10.51 and bb.ymax<=10.51:edges.append(e)
    if edges:roof=cq.Workplane(obj=roof.val().fillet(1.0,edges))
    mouth_records.append({'module':i,'construction_x_bounds':[ma,mb],'width_mm':21,'corner_radius_mm':4,'edge_radius_mm':1,'area_mm2':(mb-ma)*21-(4-math.pi)*4**2})
    def fanpose(shape):
        return shape.translate((-fx,-91,-22.5)).rotate((0,0,0),(1,0,0),ANGLE).translate((fx,FAN_Y,FAN_Z))
    aperture=fanpose(hole((0,0,1),(fx,91,10),56.5,30))
    roof=roof.cut(aperture)
    # Rounded entrance at the plenum-side fan aperture, R1 on the thin wall.
    ring_edges=[]
    for e in roof.val().Edges():
        if e.geomType()=='CIRCLE':
            try:
                if abs(e.radius()-56.5)<1e-4:ring_edges.append(e)
            except Exception:pass
    if ring_edges:roof=cq.Workplane(obj=roof.val().fillet(1.0,ring_edges))
    for xx in [fx-52.5,fx+52.5]:
      for yy in [38.5,143.5]:roof=roof.cut(fanpose(hole((0,0,1),(xx,yy,10),2.2,35)))
    add(f'{i:02}_suction_roof',roof)
    # Retain the exact connected cavity for geometric area/volume screening.
    flow_voids.append(inner.val())
    for xx in [x0+8,x1-20]:
      for yy in [-20,front_y(3)-20]:add(f'{i:02}_foot_{xx:.1f}_{yy}',rb(xx,yy,0,12,16,3,3),(31,34,37))
    fan_start=len(parts)
    # Fan envelope with realistic opening, hub, seven schematic blades and struts.
    fan=rb(fx-60,31,15,120,120,15,6).cut(hole((0,0,1),(fx,91,14),56.5,18))
    for xx in [fx-52.5,fx+52.5]:
      for yy in [38.5,143.5]:fan=fan.cut(hole((0,0,1),(xx,yy,14),2.2,18))
    add(f'{i:02}_120x15_fan_frame',fan,(28,31,33),True)
    hub=cq.Workplane('XY').center(fx,91).circle(17).extrude(12).translate((0,0,16))
    for a in range(0,360,90):
        arm=box(fx+10,88.8,16,48,4.4,2).rotate((fx,91,0),(fx,91,1),a)
        hub=hub.union(arm)
    add(f'{i:02}_fan_hub_struts',hub,(61,65,68),True)
    for j in range(7):
        blade=(cq.Workplane('XY').moveTo(15,-6).threePointArc((35,-18),(51,-9))
          .threePointArc((52,4),(47,11)).threePointArc((30,9),(15,1)).close()
          .extrude(1.3).rotate((0,0,0),(0,0,1),j*360/7).translate((fx,91,23)))
        add(f'{i:02}_blade_{j}',blade,(72,76,78),True)
    # Fabricated/bought wire guard: 1 mm round bars on 9 mm pitch, 7.5 mm
    # ahead of the fan discharge. Its attachment remains production detailing.
    guard=cq.Solid.makeTorus(58.5,.8,cq.Vector(fx,91,7.5),cq.Vector(0,0,1))
    for off in range(-54,55,9):
        span=2*math.sqrt(58.5**2-off**2)
        guard=guard.fuse(hole((1,0,0),(fx-span/2,91+off,7.5),.5,span))
    add(f'{i:02}_outlet_guard',guard,(129,139,144))

    bezel=rb(fx-63,28,10.5,126,126,3.5,12)
    bezel=bezel.cut(hole((0,0,1),(fx,91,9),56.8,7))
    for xx in [fx-52.5,fx+52.5]:
      for yy in [38.5,143.5]:
        bezel=bezel.cut(hole((0,0,1),(xx,yy,9),2.2,7))
        bezel=bezel.cut(cq.Solid.makeCone(3.8,2.2,1.6,cq.Vector(xx,yy,10.49),cq.Vector(0,0,1)))
    add(f'{i:02}_rounded_fan_bezel',bezel,(47,55,59))
    for item in parts[fan_start:]:
        item['shape']=fanpose(item['shape'])

# Profiled fixed seats and flared case-margin guides. No sliding carriage.
# The rear rubber strip sweeps across the center of the underside on lowering;
# only the bare end margins receive bearing contact.
G=T/2+.25
curve=[]
for j,pair in enumerate(contacts['curves'][0]['rear_curve_local_yz_mm']):
    y=pair[0];z=min(c['rear_curve_local_yz_mm'][j][1] for c in contacts['curves'])
    curve.append((y,H+z))
for tag,xx,span,top in [('left',6,19,P+12),('right',W-8,28,H+36)]:
    cradle=rb(xx,-16,48,span,32,4,3)
    # Seat top follows the extracted rear-case envelope; a 0.3 mm replaceable
    # liner sits between its printed substrate and the actual case.
    ys0=curve[0][0];ys1=curve[-1][0]
    seatpts=[(ys0,51),(ys1,51)]+[(y,z-.3) for y,z in reversed(curve)]
    seat=cq.Workplane('YZ',origin=(xx,0,0)).polyline(seatpts).close().extrude(span)
    cradle=cradle.union(seat)
    linerpts=[(y,z-.3) for y,z in curve]+list(reversed(curve))
    liner=cq.Workplane('YZ',origin=(xx,0,0)).polyline(linerpts).close().extrude(span)
    add('corner_pad_'+tag,liner,(133,140,135))
    # A low underside lip catches the bare case end margin during lowering.
    # The lid rests directly on the plenum. No separate tall cheeks.
    pts=[(-G-3,52),(-G-3,H+12),(-G-1,H+12),(-G,H+8),(-G,52)]
    lip=cq.Workplane('YZ',origin=(xx,0,0)).polyline(pts).close().extrude(span)
    cradle=cradle.union(lip)
    add('corner_cradle_'+tag,cradle)
# Thin replaceable liners on the plenum wall carry the lid-side lean load.
# Two broad, separated contacts use the duct itself as the stand structure.
for i,fx in enumerate([84,269.68],1):
    add(f'lid_bearing_liner_{i}',box(fx-43,T/2,H+20,86,.6,52),(119,131,124))
for yy in [-12.3,11.0]:
    # Replaceable compliant seal; bearing loads use end pads, not this lip.
    for a,b in [(42,W/2-.2),(W/2+.5,W-24)]:
        add(f'hinge_seal_{a:.1f}_{yy}',box(a,yy,50,b-a,1.3,3.6),(56,80,75))

# One integrated shelf supports a two-piece plug cassette. Shims set height;
# two broad slots allow in-plane calibration before locking. No stacked stages.
dz=p['height_adjustment'];dy=p['lateral_adjustment'];dx=p['depth_adjustment']
shelf=rb(-40,-18,P-24,39.4,43,5.3,3)
for yy in [-8,8]:
    slot=rb(-20.7,yy-4.7,P-25,13.4,9.4,8,1.7)
    shelf=shelf.cut(slot)
spine=box(-40,18,30,6,7,P-49)
spine=spine.union(box(-40,18,26.7,55,7,6.3))
add('plug_support',shelf.union(spine))
shim=box(-28.3+dx,-9.8+dy,P-18.7,27.7,19.6,5+dz)
for yy in [-8+dy,8+dy]:shim=shim.cut(hole((0,0,1),(-14+dx,yy,P-20),1.7,20))
add('height_shim_pack',shim,(123,137,127))
# Overmold is 25 x 12.5 x 6.5 mm in the Dell-linked mesh; cap uses flat
# replaceable liner stock so unknown local taper does not require recutting.
cx=-26.5+dx;cy=Y+dy;cz=P+dz
clamp=rb(cx-2,cy-10,cz-13.4,29,20,5,2)
clamp=clamp.union(box(cx-2,-10+dy,cz-13.7,29,20,3))
for yy in [cy-10,cy+5.1]:clamp=clamp.union(box(cx-2,yy,cz-8.4,29,4.9,16.8))
# End shoulders capture the overmold axially; front opening passes metal shell.
back=box(cx+3.5,cy-5.1,cz-8.4,1.5,10.2,16.8).cut(hole((1,0,0),(cx+3,cy,cz),3.7,3))
front=box(cx+25.3,cy-5.1,cz-8.4,.8,10.2,16.8).cut(box(cx+25,cy-1.8,cz-4.8,4,3.6,9.6))
clamp=clamp.union(back)
for xx in [cx+3,cx+21]:
 for yy in [cy-7.5,cy+7.5]:clamp=clamp.cut(hole((0,0,1),(xx,yy,cz-14),1.25,28))
for yy in [-8+dy,8+dy]:clamp=clamp.cut(hole((0,0,1),(-14+dx,yy,cz-15),1.25,7))
clamp=clamp.cut(box(-.4+dx,-40,cz-30,6,80,60))
add('X_depth_overmold_clamp',clamp,(169,144,105))
# Thin metal face clip is a separate bought/fabricated part, not a thin FDM wall.
add('front_capture_clip_0p8mm_metal',front,(175,181,185),True)
cap=rb(cx-2,cy-10,cz+8.7,29,20,3,2)
for xx in [cx+3,cx+21]:
 for yy in [cy-7.5,cy+7.5]:cap=cap.cut(hole((0,0,1),(xx,yy,cz+8),1.7,6))
cap=cap.cut(box(-.4+dx,-40,cz-30,6,80,60))
add('removable_plug_cap',cap,(169,144,105))
overmold=box(cx+5,cy-3.25,cz-6.25,20,6.5,12.5).edges('|X').fillet(1.5)
overmold=overmold.union(hole((1,0,0),(cx,cy,cz),3.25,5.1))
add('Dell_plug_overmold_REFERENCE',overmold,(36,38,40),True)
tip=box(cx+25,cy-1.2,cz-4.125,6.65,2.4,8.25).edges('|X').fillet(1.15)
add('USB_C_shell_REFERENCE',tip,(191,197,200),True)
# Two M3 screws and broad washers lock the calibrated cassette through shelf slots.
for yy in [-8+dy,8+dy]:
    screw('cassette_lock_'+str(yy),(0,0,1),(-14+dx,yy,P-25),22)
    washer=hole((0,0,1),(-14+dx,yy,P-25),7,1).cut(hole((0,0,1),(-14+dx,yy,P-25.1),1.7,1.2))
    add('cassette_washer_'+str(yy),washer,(175,181,185),True)
# Separate stop stays below the audio/HDMI region and is reachable from outside.
stop=box(-8,-7,H+6,7,14,10).union(box(-13,-7,H+6,5,44,10))
stop=stop.union(box(-13,18,46,8,6,H+10-46))
stop=stop.cut(hole((1,0,0),(-23,0,H+11),2.1,24))
add('chassis_stop_block',stop,(169,144,105))
screw('independent_M4_stop',(1,0,0),(-22,0,H+11),19,2)
add('stop_soft_tip',hole((1,0,0),(-1,0,H+11),3,1),(56,80,75))

# Cassette remains exposed for calibration; its rounded cap is the finished surface.

# Simplified closed laptop derived from the published envelope; vent regions
# and port centers follow the reference extraction, not a factory B-rep.
laptop=box(0,-T/2,H,W,T,p['laptop_depth']).edges('|Y').fillet(4)
laptop=laptop.cut(box(30,-7,H-1,W-60,17,5))
# Each opening retains its own source center and rounded USB-C envelope.
for port in port_study['ports']:
    x=-1 if port['side']=='keyboard-left' else W-7
    z=H+port['case_offset_from_rear_mm']; y=port['case_y_mm']
    h=port['opening_height_mm']; w=port['opening_thickness_mm']
    opening=box(x,y-w/2,z-h/2,8,w,h).edges('|X').fillet(w/2-.05)
    laptop=laptop.cut(opening)
# Replace the generic heel at the contact margins with the extracted profile.
heelpts=[(curve[0][0],H-6),(curve[-1][0],H-6)]+list(reversed(curve))
for xx,width in [(0,30),(W-30,30)]:
    cut=cq.Workplane('YZ',origin=(xx,0,0)).polyline(heelpts).close().extrude(width)
    laptop=laptop.cut(cut)
add('Precision_5680_REFERENCE',laptop,(188,192,195),True)

# Add the actual foot envelopes as moving references, and separate 2 mm
# expanded keepouts for validation. These never form intended bearing faces.
foot_keepouts=[]
for f in contacts['rubber_feet']:
    lo,hi=f['untilted_case_relative_bounds_mm'];x,y,z=lo
    ref=box(x,y,H+z,hi[0]-x,hi[1]-y,hi[2]-z)
    add('RUBBER_FOOT_'+f['name'],ref,(45,48,50),True)
    keep=box(x-2,y-2,H+z-2,hi[0]-x+4,hi[1]-y+4,hi[2]-z+4).val()
    foot_keepouts.append(leaned(keep))
# Lean only the laptop, guide/contact parts and plug station; fans retain the
# independently configured upward discharge angle. Contacts follow the laptop lean.
for item in parts:
    if not item['name'].startswith(('01_','02_','hinge_seal_')):
        item['shape']=leaned(item['shape'])

# Fuse intentional structural overlaps and reserve a removable roof clearance
# around the integrated connector support. Distinct part intersections are
# checked by validate.py, separately from individual solid validity.
def take(name):
    a=next(a for a in parts if a['name']==name);parts.remove(a);return a['shape']

for side,i in [('left','01'),('right','02')]:
    roof=take(i+'_suction_roof').fuse(take('corner_cradle_'+side)).clean()
    if side=='left':
        roof=roof.fuse(take('plug_support')).clean()
        roof=roof.fuse(take('chassis_stop_block')).clean()
    add(i+'_manifold_with_cradle',roof)

# Preserve source handedness. Dell keyboard-left is source -X, hence x=0.
# With a right-handed camera at +Y and +Z up, x=0 appears screen-right.
# Laptop withdrawal is +X; insertion is -X. No final reflection is permitted.
# Replace ambiguous viewer-left/right names with the actual desk relation.
for item in parts:
    item['name']=item['name'].replace('corner_pad_left','corner_pad_far').replace('corner_pad_right','corner_pad_near')

ass=cq.Assembly(name='Precision_5680_D6')
for a in parts:ass.add(a['shape'],name=a['name'],color=cq.Color(*[v/255 for v in a['color']]))
ass.save(str(R/'Precision_5680_D6.step'))
manifest=[]
for a in parts:
    b=a['shape'].BoundingBox()
    manifest.append({k:a[k] for k in ['name','reference']}|{'volume_mm3':a['shape'].Volume(),'bounds_mm':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]})
(R/'flow-geometry.json').write_text(json.dumps({'mouths':mouth_records,'plenum_volumes_mm3':[v.Volume() for v in flow_voids],'exhaust_axis':[0,math.cos(ELEV),math.sin(ELEV)]},indent=2)+'\n')
(R/'geometry.json').write_text(json.dumps({'coordinate_frame':p['coordinate_frame'],'scope':'D6 simplified plenum bearing study. End seats and lid liners support the laptop; no tall cheeks or underside frame. Source-handed USB-C ports. Physical qualification remains outstanding.','parts':manifest},indent=2)+'\n')
print('D6 exported:',len(parts),'valid solids',flush=True)

