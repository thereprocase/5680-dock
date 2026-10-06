"""D4 review CAD. Exported +X runs toward the far/plug end in the lid-facing view; +Y lid/fans; -Y underside/intakes; +Z up.
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

# Upright fans exhaust 15 degrees above the desk, toward the lid/user side.
# Parametric fan seating plane keeps the duct behind the actual suction face.
ELEV=math.radians(p['fan_exhaust_elevation_deg']);ANGLE=90+p['fan_exhaust_elevation_deg']
FAN_Y=p['fan_center_y'];FAN_Z=p['fan_center_z']
FACE_C=FAN_Y+FAN_Z*math.tan(ELEV)-7.5/math.cos(ELEV)-.10
INNER_C=FACE_C-2.4/math.cos(ELEV)
def front_y(z,inner=False):return (INNER_C if inner else FACE_C)-math.tan(ELEV)*z
flow_voids=[];mouth_records=[]
for i,(x0,x1,fx) in enumerate([(-7,W/2,84),(W/2+.30,W+25,269.68)],1):
    length=x1-x0
    def profile(x,length,inner=False):
        if not inner:
            return (cq.Workplane('YZ',origin=(x,0,0)).moveTo(-24,3)
              .lineTo(-24,41).threePointArc((-21,48),(-13,50)).lineTo(13,50)
              .threePointArc((28.55635,56.44365),(35,72)).lineTo(35,123)
              .threePointArc((38.2218,130.7782),(46,134))
              .lineTo(front_y(134),134).lineTo(front_y(3),3).close().extrude(length))
        return (cq.Workplane('YZ',origin=(x,0,0)).moveTo(-21.6,5.4)
              .lineTo(-21.6,40).threePointArc((-18,46),(-12,47.6)).lineTo(13,47.6)
              .threePointArc((30.2534,54.7466),(37.4,72)).lineTo(37.4,123)
              .threePointArc((39.9189,129.0811),(46,131.6))
              .lineTo(front_y(131.6,True),131.6).lineTo(front_y(5.4,True),5.4).close().extrude(length))
    def low(x,l,rear,bottom,top,inner=False):
        return (cq.Workplane('YZ',origin=(x,0,0)).moveTo(rear,bottom).lineTo(rear,top)
          .lineTo(front_y(top,inner),top).lineTo(front_y(bottom,inner),bottom).close().extrude(l))
    outer=low(x0,length,-24,3,50).union(profile(fx-62,124))
    inner=low(x0+2.4,length-4.8,-21.6,5.4,47.6,True).union(profile(fx-59.6,119.2,True))
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
    flow_voids.append(inner.val().mirror('YZ',(W/2,0,0)))
    for xx in [x0+8,x1-20]:
      for yy in [-20,84]:add(f'{i:02}_foot_{xx:.1f}_{yy}',rb(xx,yy,0,12,16,3,3),(31,34,37))
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

    for item in parts[fan_start:]:
        item['shape']=fanpose(item['shape'])

# Hinge-end bearings touch the robust corner regions outside the exhaust span.
# Small cheeks flank only the end strips, never the broad base intake grille.
G=T/2+.35
for tag,xx in [('left',0),('right',W-19)]:
    span=39 if tag=='left' else 37
    cradle=rb(xx,-G-4,48,span,2*G+8,4,3)
    for yy in [-G-4,G]:
        cheek=box(xx,yy,52,span,4,26).edges('|X').fillet(1.2)
        cradle=cradle.union(cheek)
    add('corner_cradle_'+tag,cradle)
    add('corner_pad_'+tag,rb(xx+1,-T/2,52,span-2,T,2,2),(174,143,98))
for yy in [-12.3,11.0]:
    # Replaceable compliant seal; bearing loads use end pads, not this lip.
    for a,b in [(42,W/2-.2),(W/2+.5,W-24)]:
        add(f'hinge_seal_{a:.1f}_{yy}',box(a,yy,50,b-a,1.3,3.6),(56,80,75))

# A single sculpted end cheek carries all adjustment stages; no tall gantry.
tower=(cq.Workplane('XZ',origin=(0,37,0)).moveTo(-45,30).lineTo(-8,30)
 .lineTo(-8,64).threePointArc((-12,87),(-13,P+7))
 .threePointArc((-18,P+15),(-29,P+15)).lineTo(-39,P+15)
 .threePointArc((-45,P+12),(-45,P+6)).close().extrude(7))
# XZ workplane extrudes toward -Y: tower lives y=30..37 on the lid side.
# Transverse head plate offers two Z slots and an accessible jack-screw shelf.
head=box(-44,-30,P-18,6,67,33)
for yy in [-24,24]:head=head.cut(slotx(yy,P+7,13.4))
tower=tower.union(head).union(box(-44,-12,P-30,11,24,6)).union(box(-44,-12,P-30,6,49,18))
tower=tower.union(box(-45,30,26.7,60,7,6.3))
tower=tower.cut(hole((0,0,1),(-34,0,P-35),1.7,18))
add('plug_support',tower)

# Z carrier locks through the head slots. Y stage slides in two transverse slots.
dz=p['height_adjustment'];dy=p['lateral_adjustment'];dx=p['depth_adjustment']
zcar=box(-37.7,-28,P-14+dz,5,56,28)
for yy in [-24,24]:zcar=zcar.cut(hole((1,0,0),(-39,yy,P+7+dz),1.7,10))
for yy in [-21,21]:
    slot=cq.Workplane('YZ',origin=(-40,0,0)).center(yy,P-7+dz).slot2D(9.4,3.4).extrude(15)
    zcar=zcar.cut(slot)
zcar=zcar.cut(box(-39,-14,P-13.8+dz,10,29.7,26))
# The bottom crossbar receives the jack screw even with the central cable relief.
zcar=zcar.union(box(-37.7,-28,P-18+dz,5,56,4.2))
add('Z_height_carrier',zcar,(146,153,157))
ycar=box(-32.4,-25+dy,P-14+dz,5,50,28)
for yy in [-21+dy,21+dy]:ycar=ycar.cut(hole((1,0,0),(-34,yy,P-7+dz),1.7,10))
ycar=ycar.cut(box(-34,-12.5+dy,P-14+dz,10,26.5,26.5))
# Bottom shelf accepts the separate plug clamp and longitudinal depth slots.
ycar=ycar.union(box(-32.4,-25+dy,P-19+dz,31.4,50,5.3))
for yy in [-8+dy,8+dy]:
    sl=cq.Workplane('XY').center(-14,yy).slot2D(13.4,3.4).extrude(7).translate((0,0,P-20+dz))
    ycar=ycar.cut(sl)
add('Y_lateral_carrier',ycar,(146,153,157))

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
# Jack screw pushes Z carrier from below. A locknut and the two face clamps
# establish the load path after adjustment; threads are schematic cylinders.
screw('Z_M3x0p5_jack',(0,0,1),(-34,0,P-34),16+dz)
for yy in [-24,24]:screw('Z_lock_'+str(yy),(1,0,0),(-47,yy,P+7+dz),16)
for yy in [-21+dy,21+dy]:screw('Y_lock_'+str(yy),(1,0,0),(-40,yy,P-7+dz),16)
for yy in [-8+dy,8+dy]:screw('X_lock_'+str(yy),(0,0,1),(-14+dx,yy,cz-22),12)
# Separate stop stays below the audio/HDMI region and is reachable from outside.
stop=box(-8,-7,H+6,7,14,10).union(box(-13,-7,H+6,5,44,10))
stop=stop.cut(hole((1,0,0),(-23,0,H+11),2.1,24))
add('chassis_stop_block',stop,(169,144,105))
screw('independent_M4_stop',(1,0,0),(-22,0,H+11),19,2)
add('stop_soft_tip',hole((1,0,0),(-1,0,H+11),3,1),(56,80,75))

# Simplified closed laptop derived from the published envelope; vent regions
# and port centers follow the reference extraction, not a factory B-rep.
laptop=box(0,-T/2,H,W,T,p['laptop_depth']).edges('|Y').fillet(4)
laptop=laptop.cut(box(30,-7,H-1,W-60,17,5))
for zport in [H+p['port_from_rear_case'],H+p['second_port_from_rear_case']]:
    laptop=laptop.cut(box(-1,Y-1.65,zport-4.5,8,3.3,9))
add('Precision_5680_REFERENCE',laptop,(188,192,195),True)

# Fuse intentional structural overlaps and reserve a removable roof clearance
# around the integrated connector support. Distinct part intersections are
# checked by validate.py, separately from individual solid validity.
def take(name):
    a=next(a for a in parts if a['name']==name);parts.remove(a);return a['shape']
for side,i in [('left','01'),('right','02')]:
    roof=take(i+'_suction_roof').fuse(take('corner_cradle_'+side)).clean()
    if side=='left':
        roof=roof.fuse(take('plug_support')).fuse(take('chassis_stop_block')).clean()
    add(i+'_manifold_with_cradle',roof)

# D4 corrects the handedness established by the user's lid-facing photograph.
# Construction above retains D2 local coordinates. Mirror the actual solids,
# including port cutouts and plug stages, about the laptop's mid-width plane.
# Exported coordinates: x=0 near end; x=W far, keyboard-left port edge;
# +Y lid/user/fans; -Y underside/intake; +Z up. Docking travel is +X.
for item in parts:
    item['shape']=item['shape'].mirror('YZ',(W/2,0,0))
    assert item['shape'].isValid() and len(item['shape'].Solids())==1,item['name']
# Replace ambiguous viewer-left/right names with the actual desk relation.
for item in parts:
    item['name']=item['name'].replace('corner_pad_left','corner_pad_far').replace('corner_pad_right','corner_pad_near')

ass=cq.Assembly(name='Precision_5680_D4')
for a in parts:ass.add(a['shape'],name=a['name'],color=cq.Color(*[v/255 for v in a['color']]))
ass.save(str(R/'Precision_5680_D4.step'))
manifest=[]
for a in parts:
    b=a['shape'].BoundingBox()
    manifest.append({k:a[k] for k in ['name','reference']}|{'volume_mm3':a['shape'].Volume(),'bounds_mm':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]})
(R/'flow-geometry.json').write_text(json.dumps({'mouths':mouth_records,'plenum_volumes_mm3':[v.Volume() for v in flow_voids],'exhaust_axis':[0,math.cos(ELEV),math.sin(ELEV)]},indent=2)+'\n')
(R/'geometry.json').write_text(json.dumps({'coordinate_frame':p['coordinate_frame'],'scope':'Every component is one valid solid. References are simplified; this is not full physical qualification.','parts':manifest},indent=2)+'\n')
print('D4 exported:',len(parts),'valid solids',flush=True)

