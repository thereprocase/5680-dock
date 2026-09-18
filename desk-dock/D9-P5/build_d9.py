"""D9 P5: 8-degree lean and drop-in contact pegs on the R7 frame (P4 connections, plenums, guards, ties unchanged).

Each cradle end is the R7 frame profile (base, brace, tower with deck top and two 22-mm channels, 8-degree lid rail,
6-mm outer wall). Everything the laptop touches except that rail is a drop-in peg: a seat peg (per machine) and a
fence peg (64-mm wall at the plug end, 15-mm at the far end), locked by one horizontal 36-mm fan pin through the
outer wall and both feet with a 0.15-mm cam offset. The socket void is subtracted from the fused cradle. P4 fit corrections kept.

Fit corrections (user, 2026-09-18): pin bores 8.8 -> 8.4 mm so the 8.2-mm octagonal pins ride with 0.2 mm
clearance; key barbs 1 mm more total interference through the 5.4-mm slot (0.8 -> 1.8 mm). The T tongue keeps its
P2/P3 12.7-mm height: the P4 0.6-mm trim was withdrawn once the printed pair proved to nest flush after cleaning support debris.

Derived from the frozen D9 P2 builder; connections, plenums, guards and ties are unchanged in function.
"""
from pathlib import Path
import json,math,hashlib,sys
import cadquery as cq
import trimesh
from shapely.geometry import Polygon
HERE=Path(__file__).resolve().parent;OUT=HERE/'generated';OUT.mkdir(exist_ok=True)
D8=HERE/'source-inputs';sys.path.insert(0,str(D8));from raster import render
P=json.loads((D8/'parameters.json').read_text());FLOW=json.loads((D8/'flow-geometry.json').read_text())
ANGLE=math.radians(108);FY=70.;FZ=72.;WALL=3.
PARTS={};POSES={};NOTES={};RECORDS=[];JOINTS=[];MODULES=[];FANS=[];MOTIONS=[];COUPONS={}
ORIENT={};PROTECT={};MODULE_AIR={};DRESS={};AIR_DELTA={};FRAME_X={}
from dress import dress
EDGE=dict(inside=3.0,outside=1.5,top_chamfer=0.8)
T_LAPTOP=P['laptop_thickness'];CONTACT_BAND_Y=(-T_LAPTOP/2-.25-2-.5,T_LAPTOP/2+3.5+1)  # R2 fence inner face to the moved rail inner face
def box(x,y,z,dx,dy,dz):return cq.Workplane('XY').box(dx,dy,dz,centered=False).translate((x,y,z)).val()
def prism(points,x,width):return cq.Workplane('YZ',origin=(x,0,0)).polyline(points).close().extrude(width).val()
def cx(x,y,z,r,length):return cq.Solid.makeCylinder(r,length,cq.Vector(x,y,z),cq.Vector(1,0,0))
def cy(x,y,z,r,length):return cq.Solid.makeCylinder(r,length,cq.Vector(x,y,z),cq.Vector(0,1,0))
def cz(x,y,z,r,length):return cq.Solid.makeCylinder(r,length,cq.Vector(x,y,z),cq.Vector(0,0,1))
def norm(s):
    b=s.BoundingBox();return s.translate((-b.xmin,-b.ymin,-b.zmin))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def posed(s,fx):return s.rotate((0,0,0),(1,0,0),108).translate((fx,FY,FZ))
def fp(y,w):return (FY+math.cos(ANGLE)*y-math.sin(ANGLE)*w,FZ+math.sin(ANGLE)*y+math.cos(ANGLE)*w)
def locate(s,origin,normal=(1,0,0),xdir=(0,0,-1)):
    return s.moved(cq.Plane(origin=origin,xDir=xdir,normal=normal).location)
def pose(s,orientation):
    if orientation=='left':return s.rotate((0,0,0),(0,1,0),-90)
    if orientation=='right':return s.rotate((0,0,0),(0,1,0),90)
    if orientation=='fan':return s.rotate((0,0,0),(1,0,0),-108)
    if orientation=='flip':return s.rotate((0,0,0),(1,0,0),180)
    return s
PRINT_Z={'left':(1,0,0),'right':(-1,0,0),'fan':(0,-math.sin(ANGLE),math.cos(ANGLE)),'flip':(0,0,-1),'base':(0,0,1)}
def add(name,s,orientation,note,print_shape=None):
    s=s.clean();assert s.isValid() and len(s.Solids())==1,(name,'invalid',len(s.Solids()))
    PARTS[name]=s;ORIENT[name]=orientation if print_shape is None else None
    q=print_shape if print_shape is not None else pose(s,orientation)
    POSES[name]=norm(q);NOTES[name]=note
    print('Built',name,round(s.Volume(),1),flush=True)

# Pin axis is canonical Z; the key inserts along canonical Y. Pins print along
# the bed, on their longitudinal octagonal flat. The key's two leaves flex in XY.
PIN_R=4.1;FLAT=PIN_R*math.cos(math.pi/8)
BORE_R=4.2   # 8.4-mm bores for the 8.2-mm across-corners pins: 0.2-mm diametral clearance (P2/P3 used 4.4)
KEY_BARB=3.6 # barb half-width: 7.2 mm through the 5.4-mm slot = 1.8 mm total interference (P2/P3: 3.1 = 0.8 mm)
TONGUE_H=12.7 # T tongue height in print Z; P2/P3 value restored 2026-09-18 (the P4 0.6-mm trim chased support debris, not geometry)
OCT=[(PIN_R*math.cos(math.pi/8+i*math.pi/4),PIN_R*math.sin(math.pi/8+i*math.pi/4)) for i in range(8)]
def pin(length,marks):
    sh=cq.Workplane('XY').polyline(OCT).close().extrude(length).val()
    head=[(-5.5,-FLAT),(5.5,-FLAT),(7.5,2-FLAT),(7.5,4.2),(5.5,6.2),(-5.5,6.2),(-7.5,4.2),(-7.5,2-FLAT)]
    sh=sh.fuse(cq.Workplane('XY',origin=(0,0,-4)).polyline(head).close().extrude(4).val())
    sh=sh.cut(box(-2.7,-5,length-7.5-1.7,5.4,10,3.4))
    for i in range(marks):sh=sh.cut(box((i-(marks-1)/2)*3-0.6,4.8,-4.1,1.2,1.5,4.2))
    return sh.clean()
def key(grip):
    a=grip/2
    head_length=5 if grip==8 else 3
    sh=box(-4.5,-a-head_length,-1.4,9,head_length,2.8)
    # 1.2-mm leaves; 0.4-mm inward travel per barb through the 5.4-mm slot.
    # Slot terminates in a round root to avoid a sharp re-entrant corner.
    tip=a+(2.5 if grip==8 else 3.5)
    outline=[(-2.4,-a),(-2.4,a+.2),(-KEY_BARB,a+.2),(-2.4,tip),(2.4,tip),(KEY_BARB,a+.2),(2.4,a+.2),(2.4,-a)]
    sh=sh.fuse(cq.Workplane('XY',origin=(0,0,-1.4)).polyline(outline).close().extrude(2.8).val())
    half_gap=1.4 if grip==8 else 1.2
    root=-a-1 if grip==8 else -a+3
    gap=box(-half_gap,root,-1.6,2*half_gap,grip+8,3.2).fuse(cz(0,root,-1.6,half_gap,3.2))
    return sh.cut(gap).clean()
def pin_and_key(name,length,marks,transform,grip=16,key_reverse=False,key_angle=0):
    canonical_pin=pin(length,marks)
    p=canonical_pin.rotate((0,0,0),(0,0,1),key_angle)
    k=key(grip).translate((0,0,length-7.5))
    compressed=k.cut(box(2.4,grip/2,-3+length-7.5,2,5,6)).cut(box(-4.4,grip/2,-3+length-7.5,2,5,6))
    angle=key_angle+(180 if key_reverse else 0)
    k=k.rotate((0,0,0),(0,0,1),angle);compressed=compressed.rotate((0,0,0),(0,0,1),angle)
    add(name+'-pin',transform(p),'base','Octagonal pin on its longitudinal flat; axis and tension path lie in the layers. Head edge notch count identifies the length.',canonical_pin.rotate((0,0,0),(1,0,0),90))
    add(name+'-key',transform(k),'base',f'Flat XY print; two {1.0 if grip==8 else 1.2}-mm locking leaves flex in the layer plane. Pin carries the load; barbs retain the removable key.',key(grip))
    JOINTS.append({'name':name,'pin_length_mm':length,'head_notches':marks,'key_grip_mm':grip,'radial_pin_clearance_mm':round(BORE_R-PIN_R,2),'key_barb_total_interference_mm':round(2*KEY_BARB-5.4,2),'key_slot_clearance_per_side_mm':.3})
    origin=transform(cq.Vertex.makeVertex(0,0,0)).Center()
    key_axis=transform(cq.Vertex.makeVertex(-math.sin(math.radians(angle)),math.cos(math.radians(angle)),0)).Center()-origin
    pin_axis=transform(cq.Vertex.makeVertex(0,0,1)).Center()-origin
    MOTIONS.append((name+'-key',transform(compressed),key_axis,grip+7,[name+'-key']))
    MOTIONS.append((name+'-pin',transform(p),pin_axis,length+4,[name+'-key',name+'-pin']))

def socket_cutter(sx,sy,side_access=False):
    grip=8 if side_access else 16;a=grip/2
    angle=(-90 if sx<0 else 90) if side_access else 0
    slot=box(-2.7,-a-.2,-2.4,5.4,grip+.4,3.4)
    access=box(-4.8,-20 if side_access else -11.8,-2.4,9.6,26.8 if side_access else 23.6,3.4)
    collar=box(-50,-a,-8,100,grip,15.5)
    lateral=slot.fuse(access.cut(collar)).rotate((0,0,0),(0,0,1),angle).translate((sx,sy,0))
    return cz(sx,sy,-29.4,BORE_R,36.4).fuse(lateral)

# Plug end (module 1, x=0 side): R5-C with the 64-mm underside rail; the rear foot strip (x 30..323, +18 mm undocked) never reaches it.
# Far end (module 2): R4-C without the wall, because that foot strip slides through the far cradle's x range during docking.
R7=D8/'quick-fit/R7'
SOURCE_STEP={1:R7/'D8-R7-frame-d9-source.step',2:R7/'D8-R7-frame-d9-source.step'}
sources={i:cq.importers.importStep(str(path)).val() for i,path in SOURCE_STEP.items()}
R7C=json.loads((R7/'checks-d9-source.json').read_text())
INSERT_STEP={'seat':R7/'D8-R7-seat-peg-d9-source.step','plug':R7/'D8-R7-fence-peg-plug-d9-source.step','far':R7/'D8-R7-fence-peg-far-d9-source.step'}
insert_solids={k:cq.importers.importStep(str(v)).val() for k,v in INSERT_STEP.items()}
SOCKET_VOID=cq.importers.importStep(str(R7/'D8-R7-socket-void-d9-source.step')).val()
LEAN=P['laptop_lean_deg'];SOCK=R7C['socket'];Y_OUT=SOCK['outer_face_y_mm'];PIN_Z=SOCK['pin']['z_mm'];RAIL_OUT=R7C['rail_inner_face_unleaned_y_mm']+6
CROP=box(8,-200,-20,16,450,240)
frame_profiles={i:src.intersect(CROP).clean() for i,src in sources.items()}
insert_profiles={k:v.intersect(CROP).clean() for k,v in insert_solids.items()}
void_profile=SOCKET_VOID.intersect(CROP).clean()
frames=[];housing_names=[]
for index,fx in enumerate(P['fan_centers_x'],1):
    mounts=[]
    for sx in (-67,67):
        for sy in (-52.5,52.5):
            side=sy<0 and ((index==1 and sx<0) or (index==2 and sx>0))
            mounts.append((sx+(-1 if sx<0 else 1) if side else sx,sy,side))
    mouth=FLOW['mouths'][index-1];mx0,mx1=mouth['construction_x_bounds']
    ix0=min(fx-56.5,mx0);ix1=max(fx+56.5,mx1);ox0,ox1=ix0-3,ix1+3
    low=fp(-62,15.5);high=fp(62,15.5)
    FW=P.get('plenum_front_wall_y_mm',24)
    poly=Polygon([(-10.5,47),(10.5,47),(10.5,30),(FW,30),(FW,high[1]),high,low,(-10.5,5)])
    outer=poly.buffer(WALL,join_style='mitre')
    air=prism(list(poly.exterior.coords)[:-1],ix0,ix1-ix0)
    stock=prism(list(outer.exterior.coords)[:-1],ox0,ox1-ox0)
    flange=posed(box(ox0-fx,-66,7.5,ox1-ox0,132,8),fx)
    fan_column=posed(cz(0,0,7.5,56.5,8.5),fx)
    slot=(cq.Workplane('XY',origin=((mx0+mx1)/2,0,46.5)).sketch().rect(mx1-mx0,21).vertices().fillet(4).finalize().extrude(3.5).val())
    air=air.fuse(fan_column).fuse(slot).clean();housing=stock.fuse(flange).cut(air).clean()
    # Four blind external sockets. No fan screw hole penetrates the air wall.
    for sx,sy,side_access in mounts:
        boss=box(sx-6,sy-8,-8,12,16,15.5).cut(socket_cutter(sx,sy,side_access))
        housing=housing.fuse(posed(boss,fx))
    # Three internal pin tabs. Avoid the narrow inlet neck; orient key insertion
    # tangentially to each wall, with the head and flexing leaves inside the cavity.
    coords=list(poly.exterior.coords)[:-1];seam=[];seam_cuts=[]
    for edge in (3,6,7):
        a=coords[edge];b=coords[(edge+1)%len(coords)];fraction=(19.5-5)/42 if edge==7 else .5
        yy=a[0]+fraction*(b[0]-a[0]);zz=a[1]+fraction*(b[1]-a[1])
        dy,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dy,dz);ty,tz=dy/length,dz/length
        sign=-1 if poly.exterior.is_ccw else 1
        yy+=sign*9*tz;zz-=sign*9*ty
        if edge==7:ty,tz=-ty,-tz  # Rear-wall key inserts downward through the open mouth.
        # Canonical Z is axial X; canonical Y is the wall tangent.
        place=lambda s,yy=yy,zz=zz,ty=ty,tz=tz:locate(s,(fx-13.2,yy,zz),xdir=(0,tz,-ty))
        tab=place(box(-12,-8,.2,24,16,26)).intersect(stock)
        housing=housing.fuse(tab).cut(cx(fx-13.3,yy,zz,BORE_R,26.6))
        housing=housing.cut(place(box(-2.7,-8.2,18.5-1.7,5.4,16.4,3.4)))
        seam_cuts.append(cx(fx-13.3,yy,zz,BORE_R,26.6));seam_cuts.append(place(box(-2.7,-8.2,18.5-1.7,5.4,16.4,3.4)))
        seam.append({'y':yy,'z':zz,'tangent':[ty,tz]})
        pin_and_key(f'M{index}-seam-{len(seam)}',26,3,place)
    left=housing.intersect(box(ox0-30,-100,-30,fx-(ox0-30),350,230)).clean()
    right=housing.intersect(box(fx,-100,-30,ox1-fx+30,350,230)).clean()
    frame_x=ox0-15 if index==1 else ox1-1;frame=frame_profiles[index].translate((frame_x-8,0,0));FRAME_X[index]=frame_x
    # Continuous 9-mm sole connects the wider front pin/key clearance foot
    # back to the original cradle base. It shares the same exterior bed face.
    frame=frame.fuse(box(frame_x,-48,-4,16,36,9))
    foot_bores=[]
    for yy in (-40,100):
        frame=frame.fuse(prism([(yy-8,-4),(yy+8,-4),(yy+8,19),(yy-8,19)],frame_x,16))
        frame=frame.cut(cx(frame_x-.1,yy,8,BORE_R,16.2));foot_bores.append(cx(frame_x-.1,yy,8,BORE_R,16.2))
    frames.append((frame_x,frame_x+16))
    cap_x=frame_x if index==1 else ix1;cap_width=ix0-frame_x if index==1 else frame_x+16-ix1
    cap=prism(list(outer.exterior.coords)[:-1],cap_x,cap_width)
    cap=cap.fuse(posed(box(cap_x-fx,-66,7.5,cap_width,132,8),fx))
    fan_keepout=posed(box(-60.75,-60.75,-18,121.5,121.5,25.5),fx)
    socket_cut=void_profile.translate((frame_x-8,0,0))   # channels, pin bore and push-outs: the cap is solid here, so subtract after fusing
    if index==1:left=left.fuse(frame).fuse(cap).cut(fan_keepout).cut(socket_cut).clean()
    else:right=right.fuse(frame).fuse(cap).cut(fan_keepout).cut(socket_cut).clean()
    # The old solid cradle ribs cross the lower external socket. Form the pin
    # channel and accessible key relief after joining those ribs, while retaining
    # the socket's 16-mm grip faces and the closed air-wall floor behind W=7.
    cutters=[]
    for sx,sy,side_access in mounts:
        cutter=posed(socket_cutter(sx,sy,side_access),fx)
        left=left.cut(cutter).clean();right=right.cut(cutter).clean();cutters.append(cutter)
    names=[f'M{index}-outer-cradle-shell',f'M{index}-inner-shell'] if index==1 else [f'M{index}-inner-shell',f'M{index}-outer-cradle-shell']
    add(names[0],left,'left','Broad outside X face on bed, cavity open upward. Internal pin-tab supports accessible before assembly.')
    add(names[1],right,'right','Broad outside X face on bed, cavity open upward. Blind fan sockets do not pierce the air wall.')
    socket_zone=box(frame_x-1,Y_OUT-1,26,18,RAIL_OUT-Y_OUT+2,28).rotate((0,0,54),(1,0,54),-LEAN)
    for nm in names:PROTECT[nm]=[air,fan_keepout,socket_zone]+cutters+seam_cuts+foot_bores
    # Modular contact pieces for this end: seat block + fence liner, dropped into the frame socket, one horizontal pin.
    liner_kind='plug' if index==1 else 'far'
    dx=(frame_x-8,0,0)
    add(f'M{index}-seat-peg',insert_profiles['seat'].translate(dx),'left','Drop-in seat peg: 12.4-mm foot in the 13-mm seat channel, R2 seat with the V5 C relief above; profile on bed.')
    add(f'M{index}-fence-peg',insert_profiles[liner_kind].translate(dx),'left',f'Drop-in fence peg, {liner_kind} end ({"64-mm underside wall" if liner_kind=="plug" else "15-mm fence"}): 5.4-mm foot in the 6-mm channel; profile on bed.')
    lock_pin=pin(36,1)
    pin_pose=lock_pin.rotate((0,0,0),(1,0,0),-90).translate((frame_x+8,Y_OUT,PIN_Z)).rotate((0,0,54),(1,0,54),-LEAN)
    add(f'M{index}-insert-pin',pin_pose,'base','36-mm one-notch fan pin as the peg lock: through the outer wall, fence foot, web and seat foot; 0.15-mm cam offset seats both pegs.',lock_pin.rotate((0,0,0),(1,0,0),90))
    axis=cq.Vertex.makeVertex(0,1,0).rotate((0,0,0),(1,0,0),-LEAN).Center()
    MOTIONS.append((f'M{index}-insert-pin',pin_pose,axis,40,[f'M{index}-insert-pin',f'M{index}-seat-peg',f'M{index}-fence-peg']))
    housing_names+=names
    material=left.Solids()[0].fuse(right.Solids()[0]).clean()
    assert abs(material.Volume()-left.Volume()-right.Volume())<.01
    void=air.cut(material).clean();assert void.isValid() and len(void.Solids())==1
    MODULE_AIR[index]=(air,names,void.Volume(),void)
    fan_cap=posed(cz(0,0,7.3,56.5,.4),fx)
    mouth_cap=(cq.Workplane('XY',origin=((mx0+mx1)/2,0,49.8)).sketch().rect(mx1-mx0,21).vertices().fillet(4).finalize().extrude(.4).val())
    cq.exporters.export(cq.Compound.makeCompound([left.Solids()[0],right.Solids()[0]]),str(OUT/f'M{index}-audit-material.step'))
    cq.exporters.export(void,str(OUT/f'M{index}-air.step'))
    cq.exporters.export(cq.Compound.makeCompound([fan_cap,mouth_cap]),str(OUT/f'M{index}-port-caps.step'))
    guard=box(-77,-66,-29,154,132,4).cut(cz(0,0,-29.1,56.5,4.2))
    for yy in range(-45,46,9):
        half=math.sqrt(56.5**2-yy**2)+1;guard=guard.fuse(box(-half,yy-1,-29,2*half,2,4))
    for sx in (-52.5,52.5):
        for sy in (-52.5,52.5):guard=guard.fuse(cz(sx,sy,-25,5,7.5))
    for sx,sy,side_access in mounts:
        guard=guard.cut(cz(sx,sy,-29.1,BORE_R,4.2))
        place=lambda s,sx=sx,sy=sy:posed(s.translate((sx,sy,-29.2)),fx)
        pin_and_key(f'M{index}-fan-{1+(sx>0)*2+(sy>0)}',36,1,place,grip=8 if side_access else 16,key_reverse=sy<0 and not side_access,key_angle=(-90 if sx<0 else 90) if side_access else 0)
    add(f'M{index}-fan-guard',posed(guard,fx),'fan','Exterior guard face on bed, 7.5-mm standoffs vertical. Fan pins run outside the purchased fan body.')
    PROTECT[f'M{index}-fan-guard']=[posed(cz(0,0,-29.5,58.5,8),fx)]+[posed(cz(sx,sy,-30,6,10),fx) for sx in (-52.5,52.5) for sy in (-52.5,52.5)]+[posed(cz(sx,sy,-30,5.5,6),fx) for sx,sy,_ in mounts]
    fan=posed(box(-60,-60,-17.5,120,120,25).cut(cz(0,0,-17.6,56.5,25.2)),fx);FANS.append(fan)
    assert fan.intersect(material).Volume()<1e-3
    MODULES.append({'module':index,'fan_center':[fx,FY,FZ],'mouth_area_mm2':mouth['area_mm2'],'air_volume_mm3':void.Volume(),'seam_tabs':seam,'fan_mount':'Four external blind sockets, printed octagonal pins and flat locking keys','ideal_fastener_seal_helpers':0})

# Floor-backed T joints carry cross-tie loads through shoulders. The single
# transverse pin prevents lifting the tongue; its short key is externally accessible.
start=frames[0][1];end=frames[1][0];mid=(start+end)/2
for label,yy in [('front',-40),('rear',100)]:
    left=box(start,yy-8,-1,mid-12-start,16,16)
    tongue_pts=[(mid-12,yy-4),(mid,yy-4),(mid,yy-7),(mid+12,yy-7),(mid+12,yy+7),(mid,yy+7),(mid,yy+4),(mid-12,yy+4)]
    tongue=cq.Workplane('XY',origin=(0,0,2.3)).polyline(tongue_pts).close().extrude(TONGUE_H).val()
    left=left.fuse(tongue)
    right=box(mid-11.7,yy-10,-1,29.7,20,16).fuse(box(mid+17,yy-8,-1,end-(mid+17),16,16))
    cavity=Polygon(tongue_pts).buffer(.3,join_style='mitre')
    pocket=cq.Workplane('XY',origin=(0,0,2)).polyline(list(cavity.exterior.coords)[:-1]).close().extrude(13.2).val()
    right=right.cut(pocket)
    hx=mid+6
    left=left.cut(cy(hx,yy-10.2,8,BORE_R,20.4));right=right.cut(cy(hx,yy-10.2,8,BORE_R,20.4))
    for side,shape,xx,sgn in [('L',left,start,1),('R',right,end,-1)]:
        origin=(xx-16.2 if sgn>0 else xx+16.2,yy,8)
        place=lambda s,origin=origin,sgn=sgn:locate(s,origin,normal=(sgn,0,0),xdir=(0,0,-sgn))
        shape=shape.cut(cx(xx-.1 if sgn>0 else xx-17,yy,8,BORE_R,17.1))
        shape=shape.cut(place(box(-2.7,-8.2,32.8-7.5-1.7,5.4,16.4,3.4)))
        add(f'{label}-tie-{side}',shape,'flip' if side=='L' else 'base','Male T tongue prints broad top down; female socket floor prints base down. Shoulder bearing carries longitudinal load; 0.3-mm mating clearance.')
        PROTECT[f'{label}-tie-{side}']=[box(mid-13,yy-11,-1.5,31,22,18),box(start-1,yy-9,-2,19,18,19),box(end-18,yy-9,-2,19,18,19)]
        pin_and_key(f'{label}-frame-{side}',32.8,2,place,key_reverse=label=='rear')
    sgn=1
    place=lambda s,yy=yy,sgn=sgn:locate(s,(hx,yy-sgn*10.2,8),normal=(0,sgn,0),xdir=(1,0,0))
    pin_and_key(f'{label}-lap',29.4,4,place,grip=8)

# Optional physical fit plate: an open-sided socket fixture plus exact cropped
# T-joint ends. It duplicates two real pins/keys; coupons are not dock parts.
fixture=box(-7.5,-8,-29,15,16,36.5).cut(cz(0,0,-29.1,BORE_R,36.1))
fixture=fixture.cut(box(-5,-6,-25,12.6,12,17)).cut(box(-2.7,-8.2,-2.4,5.4,16.4,3.4)).clean()
COUPONS['fan-socket-fit-fixture']=(fixture,fixture.rotate((0,0,0),(0,1,0),-90))
side_fixture=box(-7.5,-8,-29,15,16,36.5).cut(box(-5,-6,-25,12.6,12,17))
side_fixture=side_fixture.cut(socket_cutter(-68,0,True).translate((68,0,0))).clean()
COUPONS['side-socket-fit-fixture']=(side_fixture,side_fixture.rotate((0,0,0),(0,1,0),-90))
for side in ('L','R'):
    sample=PARTS['front-tie-'+side].intersect(box(mid-28,-55,-2,58,30,25)).clean()
    COUPONS['T-joint-fit-'+side]=(sample,sample.rotate((0,0,0),(1,0,0),180) if side=='L' else sample)
# Cradle-end trial: the dressed M1 outer cradle sliced to its 16-mm frame width (socket, sole, foot bores, full
# 8-degree lid rail), printed in the cradle's own pose. With the M1 pegs and pin it is the cheap 8-degree seat test.
trial=PARTS['M1-outer-cradle-shell'].intersect(box(FRAME_X[1]-1,-100,-30,18,350,230)).clean()
assert trial.isValid() and len(trial.Solids())==1
COUPONS['cradle-end-trial']=(trial,pose(trial,'left'))

# Cosmetic edge treatment on shells, guards and ties; pins, keys and coupons stay exact.
for name in list(PARTS):
    orientation=ORIENT.get(name)
    if orientation is None or name.endswith(('-pin','-key')):continue
    is_tie='-tie-' in name
    shape,report=dress(PARTS[name],PRINT_Z[orientation],PROTECT.get(name,[]),inside=EDGE['inside'],outside=EDGE['outside'],top_chamfer=EDGE['top_chamfer'] if is_tie else 0.0)
    DRESS[name]=report;PARTS[name]=shape;POSES[name]=norm(pose(shape,orientation))
    print('Dressed',name,json.dumps(report),flush=True)
for index,(air,names,void_volume,_) in MODULE_AIR.items():
    material=PARTS[names[0]].Solids()[0].fuse(PARTS[names[1]].Solids()[0]).clean()
    void=air.cut(material).clean()
    assert void.isValid() and len(void.Solids())==1,('air path split by edge treatment',index)
    delta=void.cut(MODULE_AIR[index][3]).clean();missing=MODULE_AIR[index][3].cut(void).clean()
    db=delta.BoundingBox() if delta.Volume()>1e-6 else None
    AIR_DELTA[index]={'void_before_mm3':void_volume,'void_after_mm3':void.Volume(),'added_void_mm3':delta.Volume(),'removed_void_mm3':missing.Volume(),'added_void_bounds':[[db.xmin,db.ymin,db.zmin],[db.xmax,db.ymax,db.zmax]] if db else None}
    if delta.Volume()>1e-6:cq.exporters.export(delta,str(OUT/f'M{index}-air-delta.step'))
    assert abs(void.Volume()-void_volume)/void_volume<2e-4,('air path changed by edge treatment beyond 0.02 %',index,AIR_DELTA[index])
    print('Air recheck',index,json.dumps(AIR_DELTA[index]),flush=True)
    cq.exporters.export(cq.Compound.makeCompound([PARTS[names[0]].Solids()[0],PARTS[names[1]].Solids()[0]]),str(OUT/f'M{index}-audit-material.step'))
    cq.exporters.export(void,str(OUT/f'M{index}-air.step'))
for name,shape in PARTS.items():
    step=OUT/(name+'.step');stl=OUT/(name+'.stl');cq.exporters.export(shape,str(step))
    cq.exporters.export(POSES[name],str(stl),tolerance=.055,angularTolerance=.12)
    mesh=trimesh.load_mesh(stl)
    assert mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split())==1,name
    assert max(mesh.extents[:2])<240 and mesh.extents[2]<250,(name,mesh.extents)
    down=(mesh.face_normals[:,2]<-1e-4)&(mesh.triangles_center[:,2]>.21)
    RECORDS.append({'part':name,'step':step.name,'stl':stl.name,'stl_sha256':sha(stl),'dimensions_mm':mesh.extents.tolist(),'volume_mm3':shape.Volume(),'mesh_valid':True,'downward_area_nonbed_mm2':float(mesh.area_faces[down].sum()),'manufacturing':NOTES[name]})
    print('Exported',name,mesh.extents.tolist(),flush=True)

def boxes_overlap(a,b):return all(min(getattr(a,k+'max'),getattr(b,k+'max'))-max(getattr(a,k+'min'),getattr(b,k+'min'))>1e-5 for k in ('x','y','z'))
checks=[];names=list(PARTS);bounds={n:PARTS[n].BoundingBox() for n in names}
laptop=box(0,-P['laptop_thickness']/2,62,P['laptop_width'],P['laptop_thickness'],232.33).rotate((0,0,54),(1,0,54),-LEAN)
upper={n:PARTS[n].intersect(laptop).Volume() for n in names if boxes_overlap(bounds[n],laptop.BoundingBox())}
fans={n:sum(PARTS[n].intersect(f).Volume() for f in FANS if boxes_overlap(bounds[n],f.BoundingBox())) for n in names}
for i,n in enumerate(names):
    for m in names[i+1:]:
        if not boxes_overlap(bounds[n],bounds[m]):continue
        overlap=PARTS[n].intersect(PARTS[m]).Volume()
        cam_pair='-insert-pin' in (n+m) and ('-peg' in n or '-peg' in m)
        if overlap>(1.0 if cam_pair else 1e-3):checks.append({'a':n,'b':m,'overlap_mm3':overlap})
motion_hits=[]
for name,shape,axis,distance,exclude in MOTIONS:
    for fraction in (0,.15,.35,.65,1):
        moved=shape.translate(tuple(-distance*fraction*v for v in axis.toTuple()));bb=moved.BoundingBox()
        for other in names:
            # Join the T ties on the bench before attaching them to the cradles.
            if '-lap-' in name and not (other.startswith(name.split('-')[0]+'-tie-') or other.startswith(name.split('-')[0]+'-lap-')):continue
            if other in exclude or not boxes_overlap(bb,bounds[other]):continue
            overlap=moved.intersect(PARTS[other]).Volume()
            if overlap>.01:motion_hits.append({'moving':name,'fixed':other,'fraction':fraction,'overlap_mm3':overlap})
        if '-seam-' not in name and '-lap-' not in name:
            for fi,fan in enumerate(FANS,1):
                if not boxes_overlap(bb,fan.BoundingBox()):continue
                overlap=moved.intersect(fan).Volume()
                if overlap>.01:motion_hits.append({'moving':name,'fixed':f'purchased-fan-{fi}','fraction':fraction,'overlap_mm3':overlap})
print('Motion conflicts',json.dumps(motion_hits),flush=True)
(OUT/'insertion-motion.json').write_text(json.dumps({'sampled_motion_clear':not motion_hits,'sampling_fractions':[0,.15,.35,.65,1],'assembly_sequence':'T ties joined on bench before installation; plenum keys installed before fans; frame and fan fasteners checked with purchased fans present. Remove a brace as a unit before disassembling its T joint.','key_model':'Barbs compressed flush to 4.8-mm stem width during insertion; head remains full width. No elastic force or fatigue result.','conflicts':motion_hits},indent=2)+'\n')
coupon_records=[]
for name,(shape,pose) in COUPONS.items():
    assert shape.isValid() and len(shape.Solids())==1,name
    cq.exporters.export(shape,str(OUT/(name+'.step')));cq.exporters.export(norm(pose),str(OUT/(name+'.stl')),tolerance=.055,angularTolerance=.12)
    mesh=trimesh.load_mesh(OUT/(name+'.stl'));assert mesh.is_watertight and len(mesh.split())==1
    coupon_records.append({'part':name,'step':name+'.step','stl':name+'.stl','stl_sha256':sha(OUT/(name+'.stl')),'dimensions_mm':mesh.extents.tolist()})
cq.exporters.export(cq.Compound.makeCompound(list(PARTS.values())),str(OUT/'D9-P2-assembly.step'))
colors=[(44,105,123),(183,127,57),(60,78,94),(83,130,143)]
image,_=render([(s,(198,153,65) if n.endswith('-key') else (115,132,141) if n.endswith('-pin') else colors[i%4]) for i,(n,s) in enumerate(PARTS.items())],(1500,1000),(.8,1,.55),pad=45);image.save(OUT/'D9-P2-assembly.png')
manifest={'revision':'D9-P5','lean_deg':LEAN,'modular_contact':{'frame':'R7 d9-source (base, brace, tower with deck top and two 22-mm channels, 8-degree lid rail, 6-mm outer wall)','pieces_per_end':['seat peg','fence peg'],'lock':'one 36-mm fan pin through the outer wall and both feet, 0.15-mm cam offset, no key','socket':SOCK},'fit_corrections':{'pin_bore_diameter_mm':2*BORE_R,'pin_across_corners_mm':2*PIN_R,'key_barb_width_mm':2*KEY_BARB,'key_slot_mm':5.4,'key_barb_total_interference_mm':round(2*KEY_BARB-5.4,2),'t_tongue_height_mm':TONGUE_H,'source':'printed P2 fit plate, user feedback 2026-09-18'},'edge_treatment':{'parameters_mm':EDGE,'reports':DRESS,'air_recheck':AIR_DELTA,'protected':'air cavity, fan seats, sockets, pin bores, key slots, T joints, guard aperture and standoffs, laptop contact band'},'cradle_source':{'both_ends':'R7 frame d9-source','module_1_plug_end_fence_peg':'tall (64 mm)','module_2_far_end_fence_peg':'short (15 mm): the rear foot strip slides through this end during docking'},'scope':'Cradles, split plenums, fan guards and frame ties; no added metal fasteners; plug mechanism excluded','parts':RECORDS,'fit_coupons':coupon_records,'modules':MODULES,'joints':JOINTS,'metal_hardware_count':0,'printed_parts':len(PARTS),'part_interferences':checks,'upper_laptop_overlap_mm3':upper,'fan_overlap_mm3':fans,'qualification':'Prototype; CAD and Orca verification are separate from physical fit, support removal, printed-key durability, structural load and cooling tests.','builder_sha256':sha(Path(__file__)),'source_sha256':{'R7_frame_step':sha(SOURCE_STEP[1]),'R7_socket_void_step':sha(R7/'D8-R7-socket-void-d9-source.step'),**{f'R7_{k}_step':sha(v) for k,v in INSERT_STEP.items()},'R2_step':sha(D8/'quick-fit/R2/D8-R2-quick-fit-bracket.step'),'parameters':sha(D8/'parameters.json'),'flow_geometry':sha(D8/'flow-geometry.json')}}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'parts':len(PARTS),'interferences':checks,'upper':upper,'fan_interference':{k:v for k,v in fans.items() if v>.001}},indent=2),flush=True)
assert not checks and max(upper.values(),default=0)<.001 and max(fans.values())<.001,'Resolve geometric interference before slicing'
assert not motion_hits,'Resolve insertion access before slicing'
