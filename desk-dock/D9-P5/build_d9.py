"""D9 P5 cleanup: 8-degree lean and drop-in contact pegs on the R7 frame.

Each cradle end is the R7 frame profile (base, brace, tower with deck top and two 22-mm channels, 8-degree lid rail,
6-mm outer wall). The seat and fence at each end form one H-shaped contact cassette
locked by one horizontal 36-mm printed pin through the outer wall and both feet
with a 0.15-mm cam offset. The socket void is subtracted from the fused cradle.

Fit corrections (user, 2026-09-18): pin bores 8.8 -> 8.4 mm so the 8.2-mm octagonal pins ride with 0.2 mm
clearance; key barbs 1 mm more total interference through the 5.4-mm slot (0.8 -> 1.8 mm). The T tongue keeps its
P2/P3 12.7-mm height: the P4 0.6-mm trim was withdrawn once the printed pair proved to nest flush after cleaning support debris.

Derived from the frozen D9 P2 builder. P6 replaces the three internal pin-and-key
connections in each plenum with a continuous bonded shiplap at the shell split.
Printed fan grilles and their pin/socket hardware are replaced by standard
120-mm steel wire guards retained with four M4 x 35 screws per fan.
"""
from pathlib import Path
import json,math,hashlib,sys
import cadquery as cq
import trimesh
from shapely.geometry import Polygon
HERE=Path(__file__).resolve().parent;OUT=HERE/'generated';OUT.mkdir(exist_ok=True)
D8=HERE/'source-inputs';sys.path.insert(0,str(D8));from raster import render
sys.path.insert(0,str(HERE.parent/'D8'));from printed_fasteners import make_screw,make_nut,make_threaded_hole,make_threaded_shaft,_hand_grip
P=json.loads((D8/'parameters.json').read_text());FLOW=json.loads((D8/'flow-geometry.json').read_text())
ANGLE=math.radians(108);FY=70.;FZ=72.;WALL=3.
PARTS={};POSES={};NOTES={};RECORDS=[];JOINTS=[];MODULES=[];FANS=[];MOTIONS=[];COUPONS={}
ORIENT={};PROTECT={};MODULE_AIR={};LAP_RELIEF={};DRESS={};AIR_DELTA={};FRAME_X={}
ACCESSORY={}
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
def selfsupport(sh,down,keepout=None,maxdrop=4.5,passes=3):
    """Fuse a straight-down fill under every face flatter than 45 degrees, so the part needs no support.
    `down` is the print-down direction in assembly coords; `keepout` is a solid the fill must not enter."""
    d=cq.Vector(*down);up=(-down[0],-down[1],-down[2])
    hgt=lambda p:p.toTuple()[0]*up[0]+p.toTuple()[1]*up[1]+p.toTuple()[2]*up[2]
    for _ in range(passes):
        bed=min(hgt(f.Center()) for f in sh.Faces())
        b=sh.BoundingBox();S=(b.xlen+b.ylen+b.zlen)*2+100
        ctr=cq.Vector((b.xmin+b.xmax)/2,(b.ymin+b.ymax)/2,(b.zmin+b.zmax)/2)
        bedcut=cq.Solid.makeBox(S,S,S,cq.Vector(ctr.x-S/2,ctr.y-S/2,ctr.z-S/2))
        bedcut=bedcut.translate(cq.Vector(*up).multiply(bed-(hgt(ctr)+S/2)))   # a half-space strictly below the bed plane
        add=[]
        for f in sh.Faces():
            if f.Area()<0.3:continue
            try:n=f.normalAt(f.Center())
            except Exception:continue
            nv=cq.Vector(n.x,n.y,n.z)
            if nv.dot(d)/nv.Length<=0.7071:continue
            h=hgt(f.Center())-bed
            if h<0.4 or h>maxdrop:continue
            try:
                from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
                from OCP.gp import gp_Vec
                v=d.multiply(h+1.0)
                fill=cq.Shape.cast(BRepPrimAPI_MakePrism(f.wrapped,gp_Vec(v.x,v.y,v.z)).Shape())   # prisms curved faces too
                fill=fill.cut(bedcut)                                                              # square it off at the bed, no tangency sliver
            except Exception:continue
            if fill.Volume()<0.05:continue
            if keepout is not None:
                try:
                    fill=fill.cut(keepout)
                except Exception:continue
                if fill.Volume()<0.05:continue
            add.append(fill)
        if not add:break
        merged=sh
        for a in add:merged=merged.fuse(a)
        merged=merged.clean()
        if not merged.isValid():
            try:merged=cq.Shape.cast(merged.wrapped);merged=merged.clean()
            except Exception:pass
        if not merged.isValid():break
        sh=merged
    return sh
def bore_td(origin,axis,r,length,up):
    """Pin bore with a 45-degree teardrop crest along `up`. A round hole whose axis lies in the bed plane prints its own
    roof as an unsupported arc and fills with support; the crest makes it self-supporting and still beds the pin on the
    bottom and sides, where it bears."""
    a=cq.Vector(*axis);a=a.multiply(1.0/a.Length);u=cq.Vector(*up);u=u.multiply(1.0/u.Length);w=a.cross(u);o=cq.Vector(*origin)
    cyl=cq.Solid.makeCylinder(r,length,o,a)
    th=math.radians(40.0)                      # crest sides 40 deg from vertical, clear of the slicer's 45 deg threshold
    tp=o.add(u.multiply(r*math.cos(th)))       # the crest must be TANGENT to the bore, or a band of the arc stays shallow
    p0=tp.add(w.multiply(r*math.sin(th)));p1=tp.add(w.multiply(-r*math.sin(th)));p2=o.add(u.multiply(r/math.cos(th)))
    face=cq.Face.makeFromWires(cq.Wire.makePolygon([p0,p1,p2,p0]))
    return cyl.fuse(cq.Solid.extrudeLinear(face,a.multiply(length))).clean()
def wedge_xz(points,y0,width):return cq.Workplane('XZ',origin=(0,y0,0)).polyline(points).close().extrude(-width).val()  # triangle in (x,z) at y0, extruded +Y
GUSSET_RUN=15.5;GUSSET_SLOPE=1.5  # gussets: print-Z extent = 1.5 x overhang depth (34 degrees from vertical). overhang-threshold-test/ showed this Orca profile supports 45 degrees from vertical and leaves 35 alone
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
PIN_R_ROUND=3.95  # round-shaft pins: 7.9 mm in the 8.4-mm bores (0.5 mm diametral). The 8.2-mm round trial was too tight (user, 2026-09-19).
SCREW_PILOT_R=1.75  # M4 x 35 screws through a standard wire guard and 25-mm fan into 3.5-mm x 6-mm blind pilots
BORE_R=4.2   # 8.4-mm bores for the 8.2-mm across-corners pins: 0.2-mm diametral clearance (P2/P3 used 4.4)
KEY_BARB=3.6 # barb half-width: 7.2 mm through the 5.4-mm slot = 1.8 mm total interference (P2/P3: 3.1 = 0.8 mm)
TONGUE_H=12.7 # T tongue height in print Z; P2/P3 value restored 2026-09-18 (the P4 0.6-mm trim chased support debris, not geometry)
PLENUM_LAP=10.0       # overlap each side of the nominal split: 20 mm total bonded length
PLENUM_LAP_INNER=1.4  # inner tongue thickness, measured out from the air surface
PLENUM_LAP_OUTER=1.4  # outer tongue thickness, measured in from the shell exterior
PLENUM_LAP_CLEAR=.20  # epoxy/print clearance between the complementary tongue faces
PLENUM_AIR_RECESS=.15 # shallow epoxy land keeps the dry-fit tongue from protruding into/splitting the airway
PLENUM_SCALLOP_R=8.0  # broad, shallow round keys in the lap ends; wall-only, never in the airway
PLENUM_SCALLOP_D=1.5  # axial engagement of each scallop
OCT=[(PIN_R*math.cos(math.pi/8+i*math.pi/4),PIN_R*math.sin(math.pi/8+i*math.pi/4)) for i in range(8)]
def pin(length,marks,profile='round'):
    if profile=='round':
        # Round 7.9-mm shaft with one chord flat at the octagon's flat height: same bed contact, 0.5 mm diametral in the
        # 8.4-mm bore (8.2 was too tight in print), matching everywhere except that chord instead of only at eight corners.
        sh=cq.Solid.makeCylinder(PIN_R_ROUND,length,cq.Vector(0,0,0),cq.Vector(0,0,1)).cut(box(-6,-6,-1,12,6-FLAT,length+2))
    else:
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

def pin_and_key(name,length,marks,transform,grip=16,key_reverse=False,key_angle=0,profile='round'):
    canonical_pin=pin(length,marks,profile)
    p=canonical_pin.rotate((0,0,0),(0,0,1),key_angle)
    k=key(grip).translate((0,0,length-7.5))
    compressed=k.cut(box(2.4,grip/2,-3+length-7.5,2,5,6)).cut(box(-4.4,grip/2,-3+length-7.5,2,5,6))
    angle=key_angle+(180 if key_reverse else 0)
    k=k.rotate((0,0,0),(0,0,1),angle);compressed=compressed.rotate((0,0,0),(0,0,1),angle)
    add(name+'-pin',transform(p),'base',('Round pin with one longitudinal chord flat on the bed' if profile=='round' else 'Octagonal pin on its longitudinal flat')+'; axis and tension path lie in the layers. Head edge notch count identifies the length.',canonical_pin.rotate((0,0,0),(1,0,0),90))
    add(name+'-key',transform(k),'base',f'Flat XY print; two {1.0 if grip==8 else 1.2}-mm locking leaves flex in the layer plane. Pin carries the load; barbs retain the removable key.',key(grip))
    JOINTS.append({'name':name,'pin_length_mm':length,'head_notches':marks,'key_grip_mm':grip,'shaft_profile':profile,'radial_pin_clearance_mm':round(BORE_R-(PIN_R_ROUND if profile=='round' else PIN_R),2),'key_barb_total_interference_mm':round(2*KEY_BARB-5.4,2),'key_slot_clearance_per_side_mm':.3})
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
    # Primary fan mounting: four M4 x 35 screws pass through a standard 120-mm
    # wire finger guard and the 25-mm fan into 3.5-mm x 6-mm blind pilots on the
    # 105-mm pattern. The pilots remain outside the air wall.
    screw_pilots=[posed(cz(sx,sy,7.4,SCREW_PILOT_R,6.1),fx) for sx in (-52.5,52.5) for sy in (-52.5,52.5)]
    for hole in screw_pilots:housing=housing.cut(hole)
    # Bonded plenum split. The old design projected three pin bosses, bores,
    # locking-key slots and support wedges into each air chamber. Instead, split
    # the existing 3-mm shell wall into complementary inner/outer tongues over a
    # 20-mm axial overlap. Nothing is added inside `poly`, so the nominal airway
    # remains smooth. The 0.20-mm radial gap accepts epoxy and print variation.
    # The long wall-following lap registers the halves in Y/Z and provides a
    # generous bond line without separate fasteners.
    inner_edge=poly.buffer(PLENUM_LAP_INNER,join_style='mitre')
    outer_edge=poly.buffer(WALL-PLENUM_LAP_OUTER,join_style='mitre')
    air_land=poly.buffer(PLENUM_AIR_RECESS,join_style='mitre')
    layer_x0=fx-PLENUM_LAP-PLENUM_SCALLOP_D-2
    layer_w=2*(PLENUM_LAP+PLENUM_SCALLOP_D+2)
    inner_layer=prism(list(inner_edge.exterior.coords)[:-1],layer_x0,layer_w).cut(
        prism(list(air_land.exterior.coords)[:-1],layer_x0-1,layer_w+2))
    outer_layer=prism(list(outer.exterior.coords)[:-1],layer_x0,layer_w).cut(
        prism(list(outer_edge.exterior.coords)[:-1],layer_x0-1,layer_w+2))
    inner_band=prism(list(inner_edge.exterior.coords)[:-1],fx-PLENUM_LAP,2*PLENUM_LAP).cut(
        prism(list(air_land.exterior.coords)[:-1],fx-PLENUM_LAP,2*PLENUM_LAP))
    outer_band=prism(list(outer.exterior.coords)[:-1],fx-PLENUM_LAP,2*PLENUM_LAP).cut(
        prism(list(outer_edge.exterior.coords)[:-1],fx-PLENUM_LAP,2*PLENUM_LAP))
    left_far=housing.intersect(box(ox0-30,-100,-30,fx-PLENUM_LAP-(ox0-30),350,230))
    right_far=housing.intersect(box(fx+PLENUM_LAP,-100,-30,ox1-fx+30-PLENUM_LAP,350,230))
    left=left_far.fuse(housing.intersect(outer_band)).clean()
    right=right_far.fuse(housing.intersect(inner_band)).clean()
    # Give the outer tongue's axial end three broad, shallow scallops. These are
    # spherical caps clipped to the outer half of the existing shell wall—not
    # posts or bosses—so they supply an unambiguous seated position and epoxy
    # keying without disturbing flow.
    coords=list(poly.exterior.coords)[:-1]
    scallops=[]
    for n,edge in enumerate((3,6,7)):
        a=coords[edge];b=coords[(edge+1)%len(coords)]
        fraction=(19.5-5)/42 if edge==7 else .5
        yy=a[0]+fraction*(b[0]-a[0]);zz=a[1]+fraction*(b[1]-a[1])
        dy,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dy,dz);ty,tz=dy/length,dz/length
        yy-=1.5*tz;zz+=1.5*ty  # wall mid-thickness, outward from the air polygon
        boundary=fx+PLENUM_LAP
        centre=boundary+PLENUM_SCALLOP_R-PLENUM_SCALLOP_D
        male=cq.Solid.makeSphere(PLENUM_SCALLOP_R,cq.Vector(centre,yy,zz)).intersect(housing).intersect(outer_layer)
        clearance=cq.Solid.makeSphere(PLENUM_SCALLOP_R+PLENUM_LAP_CLEAR,cq.Vector(centre,yy,zz)).intersect(outer_layer)
        left=left.fuse(male);right=right.cut(clearance)
        scallops.append({'edge':edge,'male':'outer tongue','x_mm':boundary})
    # Keep every scallop the same shallow distance off the finished air surface;
    # epoxy can be wiped flush here after assembly.
    air_relief=prism(list(air_land.exterior.coords)[:-1],fx-PLENUM_LAP-PLENUM_SCALLOP_D-1,2*(PLENUM_LAP+PLENUM_SCALLOP_D+1))
    left=left.cut(air).cut(air_relief).clean();right=right.cut(air).cut(air_relief).clean()
    LAP_RELIEF[index]=air_relief
    # The wall-derived lap bands do not include the fan flange beyond the raw
    # plenum outline. That previously left two 20-mm-wide slots through the fan
    # seat at the top and bottom edges of the 120-mm footprint. Restore only the
    # flange material missing from the assembled pair, split at X=fx so the two
    # halves meet on one plane without overlapping. `housing` already contains
    # the circular opening and blind screw pilots, so neither is filled here.
    # Only two rectangular lands are absent: local Y=-60..-56.5 and
    # Y=56.5..60 over local X=-10..10. Build them explicitly instead of
    # re-booleaning the complete annulus, which can create coincident circular
    # faces at the air opening in OCCT.
    fan_patch=posed(box(-PLENUM_LAP-.2,-60.2,7.5,2*PLENUM_LAP+.4,120.4,8).cut(
                     cz(0,0,7.4,56.6,8.2)),fx)
    left_fill=fan_patch.intersect(box(fx-PLENUM_LAP-.2,-100,-30,PLENUM_LAP+.2,350,230))
    right_fill=fan_patch.intersect(box(fx,-100,-30,PLENUM_LAP+.2,350,230))
    existing=left.fuse(right)
    left_fill=left_fill.cut(air).cut(existing)
    right_fill=right_fill.cut(air).cut(existing).cut(left_fill)
    left=left.fuse(left_fill).clean();right=right.fuse(right_fill).clean()
    fan_face=housing.intersect(posed(box(-60,-60,7.5,120,120,.25).cut(cz(0,0,7.4,56.6,.5)),fx))
    fan_face_missing=fan_face.cut(left.fuse(right));fan_face_gap=fan_face_missing.Volume()
    if fan_face_gap>=.001:print('Fan seat gap',index,fan_face_gap,[(s.Volume(),(s.BoundingBox().xmin,s.BoundingBox().xmax,s.BoundingBox().ymin,s.BoundingBox().ymax,s.BoundingBox().zmin,s.BoundingBox().zmax)) for s in fan_face_missing.Solids()],flush=True)
    assert fan_face_gap<.001,(index,'fan seat face gap',fan_face_gap)
    seam=[];seam_cuts=[]
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
    if index==1:
        left=left.fuse(frame).fuse(cap).cut(fan_keepout).cut(socket_cut).clean()
        # Universal plug-end accessory receiver. Its 30 x 40 mm cavity opens
        # outboard along -X and remains wholly outside the nominal air volume.
        # The broad socket walls carry accessory loads; the transverse printed
        # bolt only clamps a male cartridge against the internal stop face.
        rx0=frame_x-42;ry0=26;rz0=46
        receiver_outer=box(rx0,ry0,rz0,42,38,48)
        receiver_void=box(rx0-1,ry0+4,rz0+4,39,30,40)
        clamp_axis_x=frame_x-15;clamp_axis_z=70
        clamp_bore=cy(clamp_axis_x,ry0-1,clamp_axis_z,6.6,58)
        receiver=receiver_outer.cut(receiver_void).cut(clamp_bore).clean()
        # Keep the socket separately printable. A broad closed-end flange and
        # shallow perimeter tongue bond into a matching cradle recess, so the
        # proven cradle bed face is not displaced 42 mm by an integral tube.
        mount_flange=box(frame_x-4,ry0-4,rz0-4,4,46,56)
        tongue_outer=box(frame_x,ry0-2,rz0-2,1.2,42,52)
        tongue_inner=box(frame_x-.1,ry0+1,rz0+1,1.4,36,46)
        tongue=tongue_outer.cut(tongue_inner)
        recess_outer=box(frame_x-.1,ry0-2.2,rz0-2.2,1.5,42.4,52.4)
        recess_inner=box(frame_x-.2,ry0+1.2,rz0+1.2,1.7,35.6,45.6)
        registration_recess=recess_outer.cut(recess_inner)
        ACCESSORY_RECESS=registration_recess
        receiver=receiver.fuse(mount_flange).fuse(tongue).cut(clamp_bore).clean()
        # Restore the independent laptop slide stop. It is fixed to the bonded
        # receiver, not the USB-C linkage, so docking thrust never loads the
        # connector. The M10 printed screw gives +/-4 mm useful adjustment and
        # ends in a replaceable soft printed bumper at the nominal X=0 case edge.
        stop_x0=rx0+15.5;stop_y=0;stop_z=SOCK['deck_top_z_mm']+14
        stop_block=box(stop_x0,-9,stop_z-10,12,39,20)
        stop_thread=make_threaded_hole(12,diameter=10,pitch=2,phase_z=-5).val().rotate((0,0,0),(0,1,0),90).translate((stop_x0,stop_y,stop_z))
        clamp_head_clear=cy(clamp_axis_x,ry0-5,clamp_axis_z,11.3,5.2)
        receiver=receiver.fuse(stop_block).cut(stop_thread).cut(clamp_bore).cut(clamp_head_clear).clean()
        ACCESSORY_BODY=receiver
        left=left.cut(registration_recess).clean()
        ACCESSORY.update({'socket_origin':[rx0,ry0,rz0],'internal_section_yz_mm':[30,40],
                          'engagement_mm':39,'wall_mm':4,'stop_x_mm':rx0+39,
                          'clamp_axis':[clamp_axis_x,ry0-1,clamp_axis_z],
                          'mount':'bonded broad flange with 1.2-mm perimeter registration tongue',
                          'slide_stop':{'axis':[stop_x0,stop_y,stop_z],'adjustment_mm':[-4,4],'nominal_contact_x_mm':0,'thread':'printed M10 coarse with replaceable soft tip'}})
    else:right=right.fuse(frame).fuse(cap).cut(fan_keepout).cut(socket_cut).clean()
    cutters=[]
    names=[f'M{index}-outer-cradle-shell',f'M{index}-inner-shell'] if index==1 else [f'M{index}-inner-shell',f'M{index}-outer-cradle-shell']
    add(names[0],left,'left','Broad outside X face on bed, cavity open upward. Continuous outer shiplap tongue bonds the plenum halves without airway bosses.')
    add(names[1],right,'right','Broad outside X face on bed, cavity open upward. Fan screws terminate in blind flange pilots outside the air wall.')
    socket_zone=box(frame_x-1,Y_OUT-1,26,18,RAIL_OUT-Y_OUT+2,28).rotate((0,0,54),(1,0,54),-LEAN)
    lap_guard=PLENUM_LAP+PLENUM_SCALLOP_D+1
    lap_zone=box(fx-lap_guard,-100,-30,2*lap_guard,350,230)
    for nm in names:PROTECT[nm]=[air,fan_keepout,socket_zone,lap_zone]+cutters+seam_cuts+foot_bores+([registration_recess] if index==1 and nm==names[0] else [])+[posed(cz(sx,sy,6.5,SCREW_PILOT_R+1,8),fx) for sx in (-52.5,52.5) for sy in (-52.5,52.5)]
    # Modular contact cassette for this end. The seat and fence gain 2 mm in
    # the leaned-up direction and are joined by a 4-mm deck bridge, producing
    # one H-section in side view: two deep channel legs connected above the
    # frame web. The laptop consequently sits 2 mm higher against the tall rail.
    # Original 16-mm width, channel feet and the transverse lock pin are kept.
    liner_kind='plug' if index==1 else 'far'
    dx=(frame_x-8,0,0)
    seat=insert_profiles['seat'].translate(dx)
    fence=insert_profiles[liner_kind].translate(dx)
    lift=(0,-2*math.sin(math.radians(LEAN)),2*math.cos(math.radians(LEAN)))
    fence_ch=SOCK['fence_channel_y_mm'];seat_ch=SOCK['seat_channel_y_mm'];deck_z=SOCK['deck_top_z_mm']
    # Raise only the laptop-contact region. Copying the complete finished pegs
    # also copied their negative pin bores, leaving two overlapping holes in
    # each fork. The feet stay in their original channels; explicit solid foot
    # cores heal the inherited source bores before one production bore is cut.
    contact_zone=box(frame_x,-100,deck_z,16,200,200).rotate((0,0,54),(1,0,54),-LEAN)
    seat=seat.fuse(seat.translate(lift).intersect(contact_zone))
    fence=fence.fuse(fence.translate(lift).intersect(contact_zone))
    foot_z=deck_z-SOCK['channel_depth_mm']
    seat_foot=box(frame_x,seat_ch[0]+.3,foot_z,16,seat_ch[1]-seat_ch[0]-.6,SOCK['channel_depth_mm']).rotate((0,0,54),(1,0,54),-LEAN)
    fence_foot=box(frame_x,fence_ch[0]+.3,foot_z,16,fence_ch[1]-fence_ch[0]-.6,SOCK['channel_depth_mm']).rotate((0,0,54),(1,0,54),-LEAN)
    bridge=box(frame_x,fence_ch[0]+.3,deck_z,16,seat_ch[1]-fence_ch[0]-.6,4).rotate((0,0,54),(1,0,54),-LEAN)
    cassette=seat.fuse(fence).fuse(seat_foot).fuse(fence_foot).fuse(bridge).clean()
    loy,loz=Y_OUT-1,PIN_Z-.15
    lock_origin=cq.Vertex.makeVertex(frame_x+8,loy,loz).rotate((0,0,54),(1,0,54),-LEAN).Center()
    lock_axis=cq.Vertex.makeVertex(0,1,0).rotate((0,0,0),(1,0,0),-LEAN).Center()
    lock_bore=bore_td(lock_origin.toTuple(),lock_axis.toTuple(),BORE_R,40,(1,0,0))
    cassette=cassette.cut(lock_bore).clean()
    outer_shell=PARTS[names[0] if index==1 else names[1]]
    cassette=cassette.cut(outer_shell).clean()
    assert cassette.isValid() and len(cassette.Solids())==1,(index,'contact cassette invalid',len(cassette.Solids()))
    cassette_name=f'M{index}-contact-cassette'
    add(cassette_name,cassette,'left',f'One-piece 16-mm-wide H contact cassette, {liner_kind} end: R2/V5-C seat and {"64-mm underside wall" if liner_kind=="plug" else "15-mm fence"}, both built 2 mm upward and joined by a 4-mm deck bridge; one transverse lock pin.')
    PROTECT[cassette_name]=[lock_bore]
    lock_pin=pin(36,1)
    pin_pose=lock_pin.rotate((0,0,0),(1,0,0),-90).translate((frame_x+8,Y_OUT,PIN_Z)).rotate((0,0,54),(1,0,54),-LEAN)
    add(f'M{index}-insert-pin',pin_pose,'base','36-mm one-notch fan pin as the peg lock: through the outer wall, fence foot, web and seat foot; 0.15-mm cam offset seats both pegs.',lock_pin.rotate((0,0,0),(1,0,0),90))
    axis=cq.Vertex.makeVertex(0,1,0).rotate((0,0,0),(1,0,0),-LEAN).Center()
    # Keep the mating cassette in the insertion sweep. Excluding it previously
    # allowed a misaligned/duplicated lock bore to pass the motion audit.
    MOTIONS.append((f'M{index}-insert-pin',pin_pose,axis,40,[f'M{index}-insert-pin']))
    housing_names+=names
    material=left.Solids()[0].fuse(right.Solids()[0]).clean()
    assert abs(material.Volume()-left.Volume()-right.Volume())<.01,(index,'half overlap',left.intersect(right).Volume())
    void=air.cut(material).clean()
    assert void.isValid() and len(void.Solids())==1,(index,'air void invalid',void.isValid(),len(void.Solids()),void.Volume())
    MODULE_AIR[index]=(air,names,void.Volume(),void)
    fan_cap=posed(cz(0,0,7.3,56.5,.4),fx)
    mouth_cap=(cq.Workplane('XY',origin=((mx0+mx1)/2,0,49.8)).sketch().rect(mx1-mx0,21).vertices().fillet(4).finalize().extrude(.4).val())
    cq.exporters.export(cq.Compound.makeCompound([left.Solids()[0],right.Solids()[0]]),str(OUT/f'M{index}-audit-material.step'))
    cq.exporters.export(void,str(OUT/f'M{index}-air.step'))
    cq.exporters.export(cq.Compound.makeCompound([fan_cap,mouth_cap]),str(OUT/f'M{index}-port-caps.step'))
    fan=posed(box(-60,-60,-17.5,120,120,25).cut(cz(0,0,-17.6,56.5,25.2)),fx);FANS.append(fan)
    assert fan.intersect(material).Volume()<1e-3
    MODULES.append({'module':index,'fan_center':[fx,FY,FZ],'mouth_area_mm2':mouth['area_mm2'],'plenum_joint':{'type':'continuous bonded scalloped shiplap','total_overlap_mm':2*PLENUM_LAP,'inner_tongue_mm':PLENUM_LAP_INNER-PLENUM_AIR_RECESS,'outer_tongue_mm':PLENUM_LAP_OUTER,'epoxy_clearance_mm':PLENUM_LAP_CLEAR,'air_surface_epoxy_land_mm':PLENUM_AIR_RECESS,'scallop_radius_mm':PLENUM_SCALLOP_R,'scallop_depth_mm':PLENUM_SCALLOP_D,'scallops':scallops},'air_volume_mm3':void.Volume(),'seam_tabs':seam,'fan_mount':'Standard 120-mm steel wire finger guard and four M4 x 35 screws through the 25-mm fan into 3.5-mm x 6-mm blind flange pilots on the 105-mm pattern','fan_seat_face_gap_mm3':fan_face_gap,'ideal_fastener_seal_helpers':0})

# Installed polar plug-positioner at the plug end. The bonded receiver remains
# the standardized dock interface, but the inserted cartridge now ends in a
# large X-axis clevis. A radial telescoping arm swings in the Y/Z plane and a
# second, smaller X-axis pivot aligns the plug axis with the laptop port. This
# replaces the old Cartesian mounting frame with three independent clamps:
# base angle, arm radius (two separated screws), and plug angle.
rx0,ry0,rz0=ACCESSORY['socket_origin'];clamp_x,_,clamp_z=ACCESSORY['clamp_axis']
add('accessory-socket-body',ACCESSORY_BODY,'right','Replaceable external 30 x 40 mm accessory receiver. Print on its broad closed mounting flange with the cavity upward, then epoxy its shallow perimeter tongue into the plug-end cradle recess.')
PROTECT['accessory-socket-body']=[box(FRAME_X[1]-4.2,ry0-4.2,rz0-4.2,5.6,46.4,56.4),cy(clamp_x,ry0-1,clamp_z,6.6,58)]
stem=box(rx0,ry0+4.3,rz0+4.3,37.7,29.4,39.4)
stem=stem.cut(cy(clamp_x,ry0+3.5,clamp_z,6.6,40))
flange=box(rx0-6,ry0+1,rz0+1,6,36,46)
# Large face-clamp base pivot (todo.md, PR #15). The 48-mm clevis is replaced by a
# broad stationary shoulder carrying a hollow 75-mm shaft. The arm's circular base
# turns on a SMOOTH journal; a printed thread lives entirely outboard of it, and a
# knurled nut squeezes the stack against the shoulder. Face friction locks the angle.
#
# The shaft is deliberately NOT coaxial with the socket. The laptop's USB-C port is
# only 59 mm from the socket centre, inside the radius any 75-100-mm shoulder and
# its skirt occupy, so the pivot is carried 45 mm lidward. Port 1 is then 92.6 mm
# from the axis. The port-reach audit below fails the build if the plug pocket
# cannot be placed on both ports.
#
# A separate cam-lobe "spatula" plate rides the same journal, outboard of the arm
# disc, and is pinched by the same nut. Its steep spiral edge is rotated until it
# tucks under the rotor's pocket block, so the docking push on the plug goes face to
# face into a clamped plate instead of down the arm; the edge stops 2 mm short of the
# pocket so the plug and boot still pass through.
#
# Axial stack, outboard is -X:
#   cradle face 9.5 | ring | ribbed skirt | shoulder -52.5 | arm disc -65.5..-52.5 |
#   cam plate -79.5..-65.5 | keyed washer -82..-79.5 | nut -94..-82 | thread to -101
BX=rx0-37                                           # X datum for the arm hardware
SY=ry0+19;SZ=rz0+24                                 # socket centre
PIV_OFF_Y=25.0                                      # port 1 then sits 76 mm from the axis, port 2 86; enough for a 70-mm disc and its skirt
BY=SY+PIV_OFF_Y;BZ=SZ                               # pivot axis, along X
PIV=(BY,BZ)
SHAFT_D=50.0;SHAFT_BORE=30.0                        # hollow, for material; nothing routes through it
TH_D=47.0;TH_P=3.0;TH_CORE=44.7                     # shallow flat-crested trapezoid, 1.15-mm depth
TH_CLR_R=.35;TH_CLR_A=.15
SH_FACE=-40.0;SH_T=10.0;SH_OD=70.0                   # stationary shoulder: the clamping face, just outboard of the socket flange
ARM_T=10.0;ARM_OD=70.0;ARM_BORE=50.5                # 0.25-mm radial running fit on the journal
ARM_X0=SH_FACE-ARM_T
CAM_T=10.0;CAM_X0=ARM_X0-CAM_T;CAM_BORE=50.5;CAM_HUB_R=35.0   # hub inside the retracted sleeve
WSH_T=2.5;WSH_OD=75.0;WSH_ID=50.6;WSH_X0=CAM_X0-WSH_T
NUT_T=9.0;NUT_OD=72.0;NUT_X=WSH_X0-NUT_T;NUT_FLUTES=16
JRN_X0=WSH_X0-0.5;THR_X0=NUT_X-4.0                  # journal covers disc, cam and washer; 4 mm of thread spare outboard of the nut
KEY_W=6.0;KEY_D=3.0                                 # two journal keyways hold the washer still
RING_X=9.5;RING_T=6.0;RING_OD=80.0;RING_ID=56.0    # bears on the cradle plug-end face; 100 keeps the skirt under the retracted sleeve and clear of the rear-frame-L pin
SKIRT_T=3.0
CLAMP={'shaft_diameter_mm':SHAFT_D,'shaft_bore_mm':SHAFT_BORE,'journal_length_mm':SH_FACE-JRN_X0,
       'pivot_axis_yz_mm':[BY,BZ],'pivot_offset_from_socket_centre_mm':[PIV_OFF_Y,0.0],
       'arm_base_outside_diameter_mm':ARM_OD,'arm_bore_mm':ARM_BORE,
       'journal_diametral_clearance_mm':round(ARM_BORE-SHAFT_D,2),
       'cam_plate':{'thickness_mm':CAM_T,'bore_mm':CAM_BORE,'hub_diameter_mm':2*CAM_HUB_R,'position':'outboard of the arm disc, pinched by the same nut through the keyed washer'},
       'thread':{'form':'D8 custom trapezoidal, 45-degree flanks, flat crest','major_diameter_mm':TH_D,
                 'core_diameter_mm':TH_CORE,'pitch_mm':TH_P,'depth_mm':round((TH_D-TH_CORE)/2,3),
                 'crest_width_mm':0.45,'radial_clearance_mm':TH_CLR_R,'axial_clearance_per_flank_mm':TH_CLR_A,
                 'thread_length_mm':JRN_X0-THR_X0,'nut_engagement_mm':NUT_T,'turns_engaged':round(NUT_T/TH_P,2),
                 'spare_thread_outboard_of_nut_mm':round(abs(THR_X0-NUT_X),2)},
       'nut_outside_diameter_mm':NUT_OD,'washer':'keyed to the shaft by two journal keyways',
       'clamped_annulus_mm':[SHAFT_D,SH_OD],'shoulder':'bridge from the socket stem, 50-degree ribbed skirt to a backing ring on the cradle plug-end face'}

def _ring(x0,x1,ro,ri):
    return cx(x0,BY,BZ,ro,x1-x0).cut(cx(x0-1,BY,BZ,ri,(x1-x0)+2))
# two opposed axial keyways, cut as slabs through the journal wall
key_slabs=[box(THR_X0-1,BY-KEY_W/2,BZ+SHAFT_D/2-KEY_D,(SH_FACE-THR_X0)+2,KEY_W,KEY_D+6),
           box(THR_X0-1,BY-KEY_W/2,BZ-SHAFT_D/2-6,(SH_FACE-THR_X0)+2,KEY_W,KEY_D+6)]

# --- stationary shoulder: socket stem, bridge, ribbed skirt, backing ring, shaft
# Narrow (SH_OD) at the shoulder face, wide (RING_OD) at the ring: with the ring on the
# bed the skirt narrows upward.
skirt=cq.Solid.makeCone(SH_OD/2,RING_OD/2,RING_X-RING_T-SH_FACE,cq.Vector(SH_FACE,0,0),cq.Vector(1,0,0))
skirt=skirt.translate((0,BY,BZ))
skirt=skirt.cut(cq.Solid.makeCone(SH_OD/2-SKIRT_T,RING_OD/2-SKIRT_T,RING_X-RING_T-SH_FACE+2,
                                  cq.Vector(SH_FACE-1,BY,BZ),cq.Vector(1,0,0)))
ring=_ring(RING_X-RING_T,RING_X,RING_OD/2,RING_ID/2)
shoulder_plate=_ring(SH_FACE,SH_FACE+SH_T,SH_OD/2,SHAFT_BORE/2)
journal=cx(JRN_X0,BY,BZ,SHAFT_D/2,SH_FACE-JRN_X0)
thread=make_threaded_shaft(JRN_X0-THR_X0,diameter=TH_D,pitch=TH_P,core_diameter=TH_CORE).val()
thread=thread.rotate((0,0,0),(0,1,0),90).translate((THR_X0,BY,BZ))
shaft=journal.fuse(thread).cut(cx(THR_X0-1,BY,BZ,SHAFT_BORE/2,(SH_FACE-THR_X0)+2))
for sl in key_slabs:shaft=shaft.cut(sl)
# Bridge: the socket flange footprint carried out to the shoulder plate. It rests on
# the flange, which rests on the stem, so nothing here overhangs when the ring is on
# the bed and the shaft prints upward.
bridge=box(SH_FACE+1.0,ry0+1,rz0+1,(rx0)-(SH_FACE+1.0),36,46)
# The shoulder plate would otherwise be a flat ceiling over the hollow skirt. Twelve
# 50-degree ribs from the skirt wall to the bore turn it into short bridges.
_ri=lambda x:(SH_OD/2-SKIRT_T)+((RING_OD/2-SKIRT_T)-(SH_OD/2-SKIRT_T))*(x-SH_FACE)/(RING_X-RING_T-SH_FACE)   # skirt inner-wall radius
_ro=lambda x:(SH_OD/2)+((RING_OD/2)-(SH_OD/2))*(x-SH_FACE)/(RING_X-RING_T-SH_FACE)                         # skirt outer radius
_t50=math.tan(math.radians(50.0));_xc=SH_FACE+SH_T
while SHAFT_BORE/2+(_xc-(SH_FACE+SH_T))/_t50<_ri(_xc)+1.3:_xc+=.1        # where a 50-degree edge from the bore meets the wall
_rib=cq.Workplane('XZ').polyline([(SH_FACE+SH_T,SHAFT_BORE/2),(SH_FACE+SH_T,_ri(SH_FACE+SH_T)+1.6),(_xc,_ri(_xc)+1.3)]).close().extrude(1.5,both=True).val()
_rib=_rib.translate((0,BY,BZ))
_ribs=None
for _k in range(12):
    _w=_rib.rotate((0,BY,BZ),(1,BY,BZ),_k*30.0)
    _ribs=_w if _ribs is None else _ribs.fuse(_w)
# The receiver (accessory-socket-body) is bonded into the cradle and the stem lives
# inside it, so the skirt, ring and ribs are cut clear of its envelope.
_recv=PARTS['accessory-socket-body'].BoundingBox()
_recv_env=box(_recv.xmin-.6,_recv.ymin-.6,_recv.zmin-.6,(_recv.xmax-_recv.xmin)+1.2,(_recv.ymax-_recv.ymin)+1.2,(_recv.zmax-_recv.zmin)+1.2)
skirt=skirt.cut(_recv_env);ring=ring.cut(_recv_env);shoulder_plate=shoulder_plate.cut(_recv_env)
# The 60- and 120-degree ribs meet the skirt wall exactly on the envelope's z faces and
# would leave two 41-mm3 slivers there, so the ribs are trimmed 4 mm taller.
_ribs=_ribs.cut(box(_recv.xmin-.6,_recv.ymin-.6,_recv.zmin-4.6,(_recv.xmax-_recv.xmin)+1.2,(_recv.ymax-_recv.ymin)+1.2,(_recv.zmax-_recv.zmin)+9.2))
shoulder=stem.fuse(flange).fuse(bridge).fuse(shoulder_plate).fuse(skirt).fuse(_ribs).fuse(ring).fuse(shaft)
# Clamp-bolt column through anything the skirt or ribs put in its way.
shoulder=shoulder.cut(cy(clamp_x,12.0,clamp_z,6.8,50.0)).cut(cy(clamp_x,12.0,clamp_z,11.5,15.0))
_lap_clear=box(-2,-P['laptop_thickness']/2-2,60,P['laptop_width']+6,P['laptop_thickness']+4,236).rotate((0,0,54),(1,0,54),-LEAN)
shoulder=shoulder.cut(_lap_clear).clean()
add('plug-holder-clamp-shoulder',shoulder,'right',
    'Stationary large-shaft clamp shoulder: socket stem and bridge, twelve-rib skirt to a backing ring on the cradle plug-end face, and a hollow 75-mm shaft offset 45 mm lidward of the socket with a smooth journal and an outboard flat-crested 72-mm x 3-mm thread. Print shaft axis vertical, ring on the bed: the skirt narrows upward, the ribs rise at 50 degrees and the thread prints vertically.')
PROTECT['plug-holder-clamp-shoulder']=[cy(clamp_x,ry0+3.5,clamp_z,6.6,40),
                                       cx(THR_X0-2,BY,BZ,SHAFT_BORE/2,(SH_FACE-THR_X0)+4)]

# Inner radial arm: 90-mm clamped disc on the journal, tongue springing from just
# outside the shaft. The docking push goes into the cam plate; the withdrawal pull
# comes down this arm, hence the 20-mm X depth outside the disc.
TONGUE_X0=ARM_X0;TONGUE_T=20.0;TONGUE_STEP=BZ+37.5  # 10 mm (the disc) at the root, 20 mm deep in X from r 40, clear of the skirt: the withdrawal pull comes down this arm
base_eye=_ring(ARM_X0,SH_FACE,ARM_OD/2,ARM_BORE/2)
ARM_CLEAR=BZ+ARM_BORE/2+1.75                        # tongue root, r 27
TONGUE_END=BZ+87.5
inner_tongue=box(TONGUE_X0,BY-7,ARM_CLEAR,ARM_T,14,TONGUE_STEP-ARM_CLEAR).fuse(box(TONGUE_X0,BY-7,TONGUE_STEP,TONGUE_T,14,TONGUE_END-TONGUE_STEP))
_sl0=BZ+46.5;_sl1=TONGUE_END-4.0                    # slot floor sets full retraction, roof sets full reach
length_slot=box(TONGUE_X0-1,BY-4.4,_sl0,TONGUE_T+2,8.8,_sl1-_sl0).fuse(cx(TONGUE_X0-1,BY,_sl0,4.4,TONGUE_T+2)).fuse(cx(TONGUE_X0-1,BY,_sl1,4.4,TONGUE_T+2))
inner_arm=base_eye.fuse(inner_tongue).cut(length_slot).clean()
add('plug-holder-polar-inner-arm',inner_arm,'left','Radial arm on a 70-mm clamped base disc with a 50.5-mm bore running on the smooth journal; the telescoping tongue springs from outside the 50-mm shaft, 20 mm deep in X from r 40. The knurled nut locks the angle by face friction, not by the thread. Prints flat, disc on the bed, tongue standing 20 mm.')
PROTECT['plug-holder-polar-inner-arm']=[cx(ARM_X0-1,BY,BZ,ARM_BORE/2,ARM_T+2)]

# Outer radial sleeve and tip clevis. Two cross-clamp bores 18 mm apart resist
# slip and yaw. The sleeve is 19 mm deep in X around the 13-mm tongue.
SLV_X0=TONGUE_X0-2.8;SLV_W=TONGUE_T+0.8+2.8+2.0
tip_z=BZ+115.5;tip_y=BY                             # modelled mid-travel pose
sleeve_z=tip_z-66.0
_sleeve_len=(tip_z+5.0)-sleeve_z
sleeve_outer=box(SLV_X0,BY-11,sleeve_z,SLV_W,22,_sleeve_len)
sleeve_void=box(TONGUE_X0-.4,BY-7.3,sleeve_z-1,TONGUE_T+.8,14.6,_sleeve_len-10.0)
sleeve=sleeve_outer.cut(sleeve_void)
length_axes=[]
for zz in (tip_z-58.0,tip_z-43.0):
    bore=cx(SLV_X0-1,BY,zz,4.4,SLV_W+2);sleeve=sleeve.cut(bore);length_axes.append([SLV_X0-1,BY,zz])
CHEEK_R=14.0;CHEEK_T=3.0;EYE_R=13.0;TIP_BORE_R=6.4  # 12-mm hollow tip screw
CHEEK_SHIFT=SLV_X0+CHEEK_T+0.4-(CAM_X0+CAM_T+0.1)   # cheeks sit this far outboard of the sleeve walls so the rotor's eye, neck and block start exactly 0.1 mm off the cam face
tip_bore=cx(SLV_X0-CHEEK_SHIFT-1,tip_y,tip_z,TIP_BORE_R,SLV_W+CHEEK_SHIFT+2)
tip_l=cx(SLV_X0-CHEEK_SHIFT,tip_y,tip_z,CHEEK_R,CHEEK_T).cut(tip_bore)
tip_r=cx(SLV_X0+SLV_W-CHEEK_T-CHEEK_SHIFT,tip_y,tip_z,CHEEK_R,CHEEK_T).cut(tip_bore)
sleeve=sleeve.fuse(tip_l).fuse(tip_r).clean()
sleeve=sleeve.cut(tip_bore).cut(box(SLV_X0+CHEEK_T-CHEEK_SHIFT,tip_y-17,tip_z-(EYE_R+2.0),SLV_W-2*CHEEK_T,34,EYE_R+2.0+6.5)).cut(box(SLV_X0+SLV_W-CHEEK_SHIFT,tip_y-17,tip_z-(EYE_R+2.0),CHEEK_SHIFT+1,34,EYE_R+2.0+6.5)).clean()
add('plug-holder-polar-outer-arm',sleeve,'left','Telescoping outer arm with two spaced captive-head length clamps and a 36-mm tip clevis. The paired clamps prevent yaw; the docking push itself is taken by the cam plate.')
PROTECT['plug-holder-polar-outer-arm']=[tip_bore]+[cx(a[0],a[1],a[2],4.4,SLV_W+2) for a in length_axes]

ROT_X0=SLV_X0-CHEEK_SHIFT+CHEEK_T+0.4;ROT_T=SLV_W-2*CHEEK_T-0.8   # rotor eye between the cheeks, 0.4 mm each side
PAD_LAT=34.0;PAD_RAD=41.0                           # rotor pocket centre: 34 mm lateral (-Y at the modelled pose), 41 mm inboard of the tip
# --- Telescoping travel, from the slot and the sleeve bores (all in modelled-pose Z).
_bore_lo,_bore_hi=length_axes[0][2],length_axes[1][2]
_retract=_bore_lo-_sl0;_extend=_sl1-_bore_hi
TIP_MIN=tip_z-_retract;TIP_MAX=tip_z+_extend
assert (sleeve_z-_retract)-BZ>=_ro(SLV_X0+SLV_W)+2.0,'sleeve must clear the skirt at full retraction'
assert TONGUE_END<=TIP_MIN-(EYE_R+2.0)-2.0,'tongue must stay clear of the rotor slot at full retraction'
REACH={'tip_radius_mm':[TIP_MIN-BZ,TIP_MAX-BZ],'travel_mm':TIP_MAX-TIP_MIN,
       'pocket_offset_mm':{'lateral':PAD_LAT,'inboard_of_tip':PAD_RAD},
       'pocket_radius_mm':[round(math.hypot(TIP_MIN-BZ-PAD_RAD,PAD_LAT),2),round(math.hypot(TIP_MAX-BZ-PAD_RAD,PAD_LAT),2)]}

# --- Port reach. This is the check the polar arm never had: the datum every earlier
# revision (D1-D7) uses is P = rear_case_seat_z + port_from_rear_case at port_y in the
# unleaned laptop frame. Carry it through the builder's own lean and solve the arm
# angle and reach that put the pocket centre on each port with the rotor at neutral.
def _lean_pt(y,z):
    t=math.radians(-LEAN);dy,dz=y-0.0,z-54.0
    return (dy*math.cos(t)-dz*math.sin(t),54.0+dy*math.sin(t)+dz*math.cos(t))
PORTS={'port-1':_lean_pt(P['port_y'],P['rear_case_seat_z']+P['port_from_rear_case']),
       'port-2':_lean_pt(P['port_y'],P['rear_case_seat_z']+P['second_port_from_rear_case'])}
def _rot(v,deg):
    a=math.radians(deg);return (v[0]*math.cos(a)-v[1]*math.sin(a),v[0]*math.sin(a)+v[1]*math.cos(a))
def _solve_pose(py,pz,roll):
    """Arm angle (deg, +toward -Y) and tip radius that put the clamped plug axis on (py,pz).
    The rotor is trimmed about the tip by psi = -(phi+LEAN)-roll so the carrier window is
    square to the port; the pocket offset from the tip therefore rotates with phi. With
    roll=None the rotor is left at neutral."""
    d=(py-BY,pz-BZ)
    def resid(phi):
        psi=0.0 if roll is None else -(phi+LEAN)-roll
        v=_rot((-PAD_LAT,-PAD_RAD),psi);w=_rot(d,-phi)          # (lateral, radial) the tip-relative axis must equal, in the arm frame
        return w[0]-v[0],w[1]-v[1]
    lo,hi=-30.0,90.0;flo=resid(lo)[0]
    for _ in range(80):
        mid=(lo+hi)/2;fm=resid(mid)[0]
        if (fm>0)==(flo>0):lo,flo=mid,fm
        else:hi=mid
    phi=(lo+hi)/2;R=resid(phi)[1]
    psi=0.0 if roll is None else -(phi+LEAN)-roll
    v=_rot((-PAD_LAT,-PAD_RAD),psi);chk=_rot((v[0],R+v[1]),phi)
    assert abs(chk[0]-d[0])<1e-6 and abs(chk[1]-d[1])<1e-6,(chk,d)
    return phi,R,psi
# pre-roll the window to the mean working arm angle plus the lean, iterating because the
# working angles themselves move slightly with the trim
POCKET_ROLL=None
for _it in range(3):
    _sol={tag:_solve_pose(py,pz,POCKET_ROLL) for tag,(py,pz) in PORTS.items()}
    POCKET_ROLL=-(sum(s[0] for s in _sol.values())/len(_sol)+LEAN)
REACH['ports']={}
for _tag,(_py,_pz) in PORTS.items():
    _phi,_R,_psi=_sol[_tag]
    _ok=TIP_MIN<=BZ+_R<=TIP_MAX
    REACH['ports'][_tag]={'leaned_yz_mm':[round(_py,3),round(_pz,3)],'radius_from_pivot_mm':round(math.hypot(_py-BY,_pz-BZ),2),
                          'arm_angle_deg':round(_phi,2),'tip_radius_mm':round(_R,2),'rotor_trim_deg':round(_psi,2),
                          'within_travel':_ok,'margin_to_travel_limits_mm':[round(BZ+_R-TIP_MIN,2),round(TIP_MAX-(BZ+_R),2)]}
    print('Port reach',_tag,json.dumps(REACH['ports'][_tag]),flush=True)
assert all(v['within_travel'] for v in REACH['ports'].values()),'Plug pocket cannot be placed on every USB-C port'

# Plug carrier. The USB-C port face is at x=0 and the plug is 25 mm long, so the boot
# pocket sits inboard of the arm plane and, because the tip clevis can never get closer
# than about 120 mm to the pivot, inboard of the tip as well: an eye on the tip pivot, a
# bar and plate beside the sleeve, and a carrier block built in the PLUG's frame (faces
# parallel to the plug's major and minor axes, rolled to the mean working arm angle plus
# the lean) with a 14 x 16 mm window and a printed M8 pinch screw through the thick wall
# into a captured hex nut. The block's back face lies on the cam plate's face.
PAD_X1=-5.0                                         # block runs to 5 mm short of the docked laptop face so the window clamps the overmold
BLK_X0=ROT_X0
assert BLK_X0>=CAM_X0+CAM_T+0.1-1e-9,'rotor must clear the cam face'
POCKET_W,POCKET_H=14.0,13.0                         # W along the plug's minor axis, H along its major axis (12.35 max, 0.3 per side)
WALL_N,WALL_S=12.0,10.0                             # thin (pivot-side) wall, screw-side wall
WALL_HB,WALL_HT=18.0,5.0                            # walls along H: the bottom one faces the pivot and is the lobe bearing land (5 mm gave a 46-75 mm2 patch; 18 mm gives ~380-410 mm2)
tip_eye=cx(ROT_X0,tip_y,tip_z,EYE_R,ROT_T)
rot_bar=box(ROT_X0,tip_y-20,tip_z-13,ROT_T,8,26)                    # eye to plate, inside the sleeve's rotor slot
rot_plate=box(ROT_X0,tip_y-48,tip_z-36,ROT_T,28,42)                 # 9 mm clear of the sleeve side wall
BOOT_R=4.5                                          # largest common USB-C strain-relief boot, relieved behind the clamp zone
CLAMP_OFF=POCKET_W/2-P['plug_minor']/2-0.25          # clamped, the overmold's flat sits 0.25 mm off the thin wall: its axis is this far from the window centre along +W
CLAMP_X0=-17.5                                      # the overmold (x -18.35..0) is clamped from here to the block end; behind it the window is relieved for the boot
_ax=(tip_y-PAD_LAT,tip_z-PAD_RAD)                   # clamped plug axis = the reach target
_pc=(_ax[0]-CLAMP_OFF*math.cos(math.radians(POCKET_ROLL)),_ax[1]-CLAMP_OFF*math.sin(math.radians(POCKET_ROLL)))   # window centre
def _plugframe(s):
    """Rotate a solid built with W along +Y and H along +Z about the pocket centre into the plug frame."""
    return s.rotate((0,_pc[0],_pc[1]),(1,_pc[0],_pc[1]),POCKET_ROLL)
_bw0=_pc[0]-POCKET_W/2-WALL_S;_bw=POCKET_W+WALL_S+WALL_N;_bh0=_pc[1]-POCKET_H/2-WALL_HB;_bh=POCKET_H+WALL_HB+WALL_HT
BLK_FILLET,BLK_CHAMFER,MOUTH_FLARE=3.5,1.5,1.5             # long (print-Z) edges rounded, front face chamfered, window mouth flared 45 deg where the plug tip enters; the back face is the bed face and the lobe bearing land, so it stays square
_blk=cq.Workplane('XY').add(box(BLK_X0,_bw0,_bh0,PAD_X1-BLK_X0,_bw,_bh)).edges('|X').fillet(BLK_FILLET).faces('>X').chamfer(BLK_CHAMFER).val()
carrier=_plugframe(_blk)
pocket=_plugframe(box(BLK_X0-1,_pc[0]-POCKET_W/2,_pc[1]-POCKET_H/2,(PAD_X1-BLK_X0)+2,POCKET_W,POCKET_H))
_mouth=_plugframe(cq.Workplane('YZ',origin=(PAD_X1-MOUTH_FLARE,_pc[0],_pc[1])).rect(POCKET_W,POCKET_H).workplane(offset=MOUTH_FLARE+0.01).rect(POCKET_W+2*MOUTH_FLARE,POCKET_H+2*MOUTH_FLARE).loft().val())
_boot_relief=_plugframe(cx(BLK_X0-1,_pc[0]+CLAMP_OFF,_pc[1],BOOT_R+0.2,CLAMP_X0-BLK_X0+1))   # round boots up to 9 mm clear the thin wall behind the clamp zone
PINCH_X=(CLAMP_X0+PAD_X1)/2                         # screw axis: through the thick wall along -W, mid overmold clamp zone
PINCH_D=8.0;PINCH_P=3.0;PINCH_HEAD=14.0;PINCH_NUT_T=6.0   # same 8 x 3 form as the length clamps; the helper needs pitch >= 2.35 at this depth
_pin_hole=_plugframe(cy(PINCH_X,_bw0-1,_pc[1],PINCH_D/2+0.3,WALL_S+2))                       # clearance hole through the thick wall
_nut_pocket=_plugframe(_hand_grip(PINCH_HEAD+0.6,PINCH_NUT_T+1.6,-1.0).val().rotate((0,0,0),(1,0,0),-90).translate((PINCH_X,_bw0,_pc[1])))   # scalloped pocket, open at the outer face; its six lobes key the nut's scallops
plug_rotor=tip_eye.fuse(rot_bar).fuse(rot_plate).fuse(carrier).cut(pocket).cut(_mouth).cut(_boot_relief).cut(_pin_hole).cut(_nut_pocket)
plug_rotor=plug_rotor.cut(cx(ROT_X0-1,tip_y,tip_z,TIP_BORE_R,ROT_T+2)).clean()
add('plug-holder-polar-plug-rotor',plug_rotor,'left','Plug carrier, %.1f mm wide: eye on the tip pivot, bar and plate beside the sleeve, and a carrier block in the plug frame (rolled %.1f deg) with a 14 x 13 mm window that clamps the overmold on its flats, a 10-mm wall carrying a captured scalloped nut and an M8 x 3 printed pinch screw, and an 18-mm bearing land under the window on the pivot side so its back face bears on the cam lobe over several hundred square millimetres; long edges rounded r 3.5, front face chamfered 1.5, window mouth flared 1.5 mm. Prints eye, plate and block face down, window vertical.'%(ROT_T,POCKET_ROLL))
PROTECT['plug-holder-polar-plug-rotor']=[cx(ROT_X0-1,tip_y,tip_z,TIP_BORE_R,ROT_T+2),_pin_hole,_nut_pocket]
REACH['tip_pivot_yz_mm']=[tip_y,tip_z];REACH['carrier_walls_mm']={'thin':WALL_N,'screw':WALL_S,'bottom_bearing':WALL_HB,'top':WALL_HT};REACH['pocket_window_mm']=[POCKET_W,POCKET_H];REACH['pocket_pre_roll_deg']=round(POCKET_ROLL,2);REACH['pocket_block_x_mm']=[BLK_X0,PAD_X1]
# Pinch screw, nut and bearing shim. The screw is built along +Z (head at -Z) and
# printed thread-axis vertical, then laid along +W in the plug frame. Its flat tip seats
# in a shallow round recess on the back of a loose flat shim; the shim's front and the
# thin wall are the two jaws on the overmold's 6.5-mm FLATS, so the plug cannot roll in
# the carrier. Clamped, the overmold sits 0.25 mm off the thin wall (that clamped axis is
# the reach target, so the window centre is offset by CLAMP_OFF). A thinner overmold just
# lets the shim and screw travel further. The tip sits 0.2 mm off the recess floor.
SHIM_T=POCKET_W-P['plug_minor']-0.5;SHIM_L=(PAD_X1-CLAMP_X0)-1.0;SHIM_RECESS=1.5   # 7.0 x 11.5: fills the window beside the 6.5-mm overmold with 0.5 mm to spare
_shim_w0=_pc[0]-POCKET_W/2                         # against the thick wall side of the window
_pinch_len=16.0
_pinch_tip_w=_shim_w0+SHIM_RECESS-0.2
pinch_screw0=make_screw(_pinch_len,diameter=PINCH_D,pitch=PINCH_P,core_diameter=6.2,head_diameter=PINCH_HEAD,thread_length=_pinch_len-2,tip_chamfer=0).val()
pinch_nut0=make_nut(PINCH_NUT_T,diameter=PINCH_D,pitch=PINCH_P,core_diameter=6.2,outer_diameter=PINCH_HEAD,radial_clearance=.30,phase_z=-(PINCH_NUT_T+0.3)).val()
pinch_screw=_plugframe(pinch_screw0.rotate((0,0,0),(1,0,0),-90).translate((PINCH_X,_pinch_tip_w-_pinch_len,_pc[1])))
pinch_nut=_plugframe(pinch_nut0.rotate((0,0,0),(1,0,0),-90).translate((PINCH_X,_bw0+0.3,_pc[1])))
_shim=box(PINCH_X-SHIM_L/2,_shim_w0,_pc[1]-(POCKET_H/2-0.2),SHIM_L,SHIM_T,POCKET_H-0.4)
_shim=_shim.cut(cy(PINCH_X,_shim_w0-1,_pc[1],PINCH_D/2+0.3,SHIM_RECESS+1))                                   # tip recess on the back
pinch_shim0=_shim.clean()
pinch_shim=_plugframe(pinch_shim0)
add('plug-holder-rotor-pinch-shim',pinch_shim,'left','Loose 7-mm flat bearing shim in the carrier window: the pinch screw tip seats in the round recess on its back and its flat front bears on the overmold flat, so the plug is held on its flats and cannot roll. Print recess face down.',
    pinch_shim0.translate((-PINCH_X,-_shim_w0,-_pc[1])).rotate((0,0,0),(1,0,0),90))
REACH['pinch_screw']={'thread':'printed M%.0f x %.0f, %.0f mm shank'%(PINCH_D,PINCH_P,_pinch_len),'axis':'along the plug minor axis through the 10-mm wall, captured scalloped nut on the outer face','bearing_shim_mm':[SHIM_L,POCKET_H-0.4,SHIM_T],'clamps':'overmold flats (6.5 mm) between the shim and the thin wall, x %.1f..%.1f; boot relief r %.1f behind'%(CLAMP_X0,PAD_X1,BOOT_R+0.2),'tip_to_recess_floor_mm':0.2,'boot_diameter_design_mm':[6.0,2*BOOT_R],'clamped_axis_offset_from_window_centre_mm':CLAMP_OFF,'overmold_envelope_mm':'USB-IF Type-C max 12.35 x 6.5 (parameters.json 12.5 x 6.5)'}
add('plug-holder-rotor-pinch-screw',pinch_screw,'base','Printed M8 x 3 pinch screw for the plug carrier, 16-mm shank with a flat tip that seats in the bearing shim. Print thread axis vertical.',pinch_screw0)
add('plug-holder-rotor-pinch-nut',pinch_nut,'base','Captured printed scalloped nut for the carrier pinch screw; drops into the matching pocket on the carrier wall, which keys its scallops. Print thread axis vertical.',pinch_nut0)

# Cam-lobe spatula. Hub on the journal; lobe bounded by two radial cuts and a steep
# log spiral r = CAM_R0 * exp(CAM_B * theta). For a given arm angle and reach the cam is
# rotated so the spiral passes CAM_GAP inside the pocket's nearest corner, i.e. right
# at the boot; the lobe then lies under the block's outboard face, runs past the block
# on the far side, and its arm-side cut stays outside the sleeve.
CAM_R0=58.0;CAM_B=1.2;CAM_ARC=24.0;CAM_CUT=3.0;CAM_GAP=0.5   # spiral r = 72 e^(1.1 theta) over 24 deg (r 72 -> 114); the near edge is cut 3 deg along it so it sits clear of the sleeve at full reach
CAM_RMAX=CAM_R0*math.exp(CAM_B*math.radians(CAM_ARC))
def _pocket_corners(R,psi=0.0):
    """Window corners in the arm frame (lateral, radial from the pivot) for tip radius R and rotor trim psi."""
    cw=_rot((_pc[0]-tip_y,_pc[1]-tip_z),psi);c=(cw[0],R+cw[1]);a=math.radians(POCKET_ROLL+psi);out=[]
    for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1)):
        u,v=sx*POCKET_W/2,sy*POCKET_H/2
        out.append((c[0]+u*math.cos(a)-v*math.sin(a),c[1]+u*math.sin(a)+v*math.cos(a)))
    return out
def _cam_target(R,psi=0.0):
    """Radius the spiral must have under the window, and the window's angle from the arm line."""
    lo=min(_pocket_corners(R,psi),key=lambda p:math.hypot(*p))
    return math.hypot(*lo)-CAM_GAP,math.degrees(math.atan2(-lo[0],lo[1]))
def _cam_rotation(phi,R,psi=0.0):
    """Cam rotation (deg, same sense as the arm) placing the spiral point of the needed radius at the window angle."""
    r_need,alpha=_cam_target(R,psi)
    assert CAM_R0*math.exp(CAM_B*math.radians(CAM_CUT))<=r_need<=CAM_RMAX,('cam spiral cannot reach',r_need)
    psi=math.degrees(math.log(r_need/CAM_R0)/CAM_B)   # angle along the lobe, from its near edge
    return phi+alpha-psi
# Leaf outline in the cam frame: a radial near edge from inside the hub up to the spiral
# start, the spiral, then a spline tip and back edge returning into the hub about 53 deg
# from the near edge. +theta is toward -Y, like the arm angle.
_pt=lambda r,deg:(-r*math.sin(math.radians(deg)),r*math.cos(math.radians(deg)))
_lead=[_pt(CAM_HUB_R-2.0,CAM_CUT),_pt(CAM_R0*math.exp(CAM_B*math.radians(CAM_CUT)),CAM_CUT)]
_spiral=[_pt(CAM_R0*math.exp(CAM_B*math.radians(_a)),_a) for _a in [CAM_CUT+(CAM_ARC-CAM_CUT)*_k/40.0 for _k in range(1,41)]]
_back=[_pt(CAM_RMAX+1.0,CAM_ARC+4.0),_pt(CAM_RMAX-4.0,CAM_ARC+10.0),_pt(CAM_RMAX-16.0,CAM_ARC+17.0),_pt(CAM_RMAX-34.0,CAM_ARC+23.0),_pt(CAM_RMAX-52.0,CAM_ARC+27.0),_pt(CAM_HUB_R-2.0,CAM_ARC+29.0)]
_lobe=cq.Workplane('YZ').polyline(_lead+_spiral).spline(_back,includeCurrent=True).close().extrude(CAM_T).val()
_lobe=_lobe.translate((CAM_X0,BY,BZ))
cam=cx(CAM_X0,BY,BZ,CAM_HUB_R,CAM_T).fuse(_lobe).cut(cx(CAM_X0-1,BY,BZ,CAM_BORE/2,CAM_T+2))
CAM_ROT0=_cam_rotation(0.0,tip_z-BZ)
cam=cam.rotate((0,BY,BZ),(1,BY,BZ),CAM_ROT0).clean()
add('plug-holder-clamp-cam-spatula',cam,'left','Leaf-lobe spatula: 14-mm plate on the journal outboard of the arm disc, pinched by the same nut. Rotate it until its spiral edge runs up to the plug boot; the rotor block then bears face to face on it, back face to lobe face, when the laptop pushes the plug. Prints flat.')
PROTECT['plug-holder-clamp-cam-spatula']=[cx(CAM_X0-1,BY,BZ,CAM_BORE/2,CAM_T+2)]
CLAMP['cam_plate'].update({'lobe':'leaf: radial near edge at %.0f deg, log spiral r = %.0f*exp(%.1f*theta) to %.0f deg (r %.0f), spline tip and back edge closing at %.0f deg'%(CAM_CUT,CAM_R0,CAM_B,CAM_ARC,CAM_RMAX,CAM_ARC+29.0),
                           'edge_gap_below_pocket_mm':CAM_GAP,'modelled_rotation_deg':round(CAM_ROT0,2)})
for _tag,_rec in REACH['ports'].items():
    _rec['cam_rotation_deg']=round(_cam_rotation(_rec['arm_angle_deg'],_rec['tip_radius_mm'],_rec['rotor_trim_deg']),2)
    _rec['cam_edge_radius_mm']=round(_cam_target(_rec['tip_radius_mm'],_rec['rotor_trim_deg'])[0],2)

# First-order angular compliance of the plug axis under a 20-N load at the pocket:
# Euler-Bernoulli beams, printed-PETG moduli as stated. Reported for design steering
# only; it ignores joint slip, layer anisotropy and the socket cartridge's clearance,
# so it is not a substitute for a dial-indicator test at 20 N. Two directions: the
# docking push (-X) goes face to face into the cam lobe; the withdrawal pull (+X)
# lifts the block off the cam and goes down the arm.
def _stiffness(E,F=20.0):
    I=lambda b,h:b*h**3/12.0
    R_tip=tip_z-BZ
    # -X: cam lobe as a cantilever from the hub edge to the contact, width taken at the lobe root
    # shoulder: plate plus bridge as a cantilever from the socket flange out to the shaft axis, both directions
    th_sh=F*(R_tip+PAD_LAT)*PIV_OFF_Y/(E*I(36.0,SH_T+(rx0-(SH_FACE+1.0))))
    r_c,_=_cam_target(R_tip);th_cam=F*(r_c-CAM_HUB_R)**2/(2*E*I(60.0,CAM_T))+th_sh
    # +X: arm chain
    seg=[(ARM_OD/2,TONGUE_STEP-BZ,I(14,ARM_T)),(TONGUE_STEP-BZ,sleeve_z-BZ,I(14,TONGUE_T)),
         (sleeve_z-BZ,R_tip,(22*SLV_W**3-14.6*(TONGUE_T+.8)**3)/12.0+I(14,TONGUE_T))]
    th=sum(F*((R_tip-r0)**2-(R_tip-r1)**2)/(2*E*Ii) for r0,r1,Ii in seg)
    M=F*PAD_LAT
    th+=M*6.0/(E*I(30,ROT_T))+M*25.0/(E*I(28,ROT_T))
    th+=th_sh
    return math.degrees(th_cam),math.degrees(th)
_s20=_stiffness(2000.0);_s15=_stiffness(1500.0)
REACH['plug_axis_compliance_estimate']={'load_N':20.0,'method':'Euler-Bernoulli beams; clamp faces, socket and thread treated as rigid',
    'docking_push_minus_x_deg':{'E_2000MPa':round(_s20[0],3),'E_1500MPa':round(_s15[0],3),'path':'block face on the cam lobe, lobe bending from the clamped hub, shoulder plate and bridge'},
    'withdrawal_pull_plus_x_deg':{'E_2000MPa':round(_s20[1],3),'E_1500MPa':round(_s15[1],3),'path':'tongue, sleeve, rotor bar and plate, shoulder bridge'},
    'target_deg':0.5,
    'not_included':'socket cartridge clearance (0.3 mm per side over 39 mm engagement, up to %.2f deg unless preloaded), clamp-face slip, layer anisotropy'%math.degrees(math.atan(0.6/39.0))}
print('Plug-axis compliance estimate',json.dumps(REACH['plug_axis_compliance_estimate']),flush=True)

clamp_bolt=make_screw(58,diameter=12,pitch=3,core_diameter=10,head_diameter=22,thread_length=20).val().rotate((0,0,0),(1,0,0),-90).translate((clamp_x,ry0,clamp_z))
clamp_nut=make_nut(9,diameter=12,pitch=3,core_diameter=10,outer_diameter=22,radial_clearance=.30,phase_z=-39).val().rotate((0,0,0),(1,0,0),-90).translate((clamp_x,ry0+39,clamp_z))
add('accessory-socket-clamp-bolt',clamp_bolt,'base','M12-class printed clamp bolt with 3-mm-pitch trapezoidal thread; print thread axis vertical. Broad socket faces carry the accessory load, while this bolt removes play.',clamp_bolt.rotate((0,0,0),(1,0,0),90))
add('accessory-socket-clamp-nut',clamp_nut,'base','Replaceable printed coarse-thread hex nut for the plug-end accessory socket; print thread axis vertical.',clamp_nut.rotate((0,0,0),(1,0,0),90))

# Independent laptop insertion-depth stop, restored from the earlier cassette.
# At nominal adjustment its soft face terminates at X=0, ahead of the plug; the
# laptop therefore bottoms on the stop before connector insertion force rises.
stop_x0,stop_y,stop_z=ACCESSORY['slide_stop']['axis']
stop_screw=make_screw(18,diameter=10,pitch=2,head_diameter=24,head_height=6,tip_chamfer=0).val()
stop_screw=stop_screw.fuse(cz(0,0,17.8,4,3.2)).rotate((0,0,0),(0,1,0),90).translate((stop_x0-5,stop_y,stop_z))
add('laptop-slide-endstop-screw',stop_screw,'left','Independent printed M10 laptop slide endstop, adjustable +/-4 mm; prints thread axis vertical and sets docked depth without using the USB-C plug as the hard stop.')
stop_tip=cz(0,0,0,6,4).cut(cz(0,0,-.1,4.1,3.1)).rotate((0,0,0),(0,1,0),90).translate((-4,stop_y,stop_z)).clean()
add('laptop-slide-endstop-soft-tip',stop_tip,'left','Replaceable flexible printed bumper for the laptop slide stop; 8.2-mm socket over the screw stem, nominal contact face at X=0.')

# Knurled clamp nut. The helper's six 2.3-mm scallops are meaningless on a 100-mm
# nut, so the grip is twenty scalloped flutes cut around the rim instead.
def _knurled_blank(x0,yc,zc):
    b=cx(x0,yc,zc,NUT_OD/2,NUT_T)
    for _k in range(NUT_FLUTES):
        _a=math.radians(_k*360/NUT_FLUTES)
        b=b.cut(cx(x0-1,yc+math.cos(_a)*(NUT_OD/2+2.0),zc+math.sin(_a)*(NUT_OD/2+2.0),4.2,NUT_T+2))
    return b
_nut_body=_knurled_blank(NUT_X,BY,BZ)
_nut_hole=make_threaded_hole(NUT_T,diameter=TH_D,pitch=TH_P,radial_clearance=TH_CLR_R,
                             axial_clearance=TH_CLR_A,core_diameter=TH_CORE,
                             phase_z=-(NUT_X-THR_X0)).val().rotate((0,0,0),(0,1,0),90).translate((NUT_X,BY,BZ))
clamp_nut_big=_nut_body.cut(_nut_hole).clean()
add('plug-holder-clamp-nut',clamp_nut_big,'left',
    'Knurled 100-mm clamp nut on the outboard 72-mm x 3-mm flat-crested thread. Tightening squeezes the cam plate and the arm base against the stationary shoulder; the angle is held by face friction over the 75-90-mm annulus, not by the thread. Print thread axis vertical.')
# Tip pivot hardware. Hollow printable pivot screw keeps the cable path available;
# its broad annular head is captive outboard of the clevis, the coarse nut is replaceable.
tip_screw=make_screw(SLV_W+11,diameter=12,pitch=3,core_diameter=10,head_diameter=22,thread_length=12).val().cut(cz(0,0,-2,3,SLV_W+18)).rotate((0,0,0),(0,1,0),90).translate((SLV_X0-CHEEK_SHIFT-3.5,tip_y,tip_z))
tip_nut=make_nut(6,diameter=12,pitch=3,core_diameter=10,outer_diameter=22,radial_clearance=.30,phase_z=-(SLV_W+5.1)).val().rotate((0,0,0),(0,1,0),90).translate((SLV_X0-CHEEK_SHIFT+SLV_W+1.6,tip_y,tip_z))
add('plug-holder-tip-annular-screw',tip_screw,'left','Small hollow printed pivot screw with captive annular head; prints thread axis vertical and clamps plug-axis alignment at the arm tip.')
add('plug-holder-tip-annular-nut',tip_nut,'left','Replaceable coarse-thread annular nut captured at the plug-end clevis; print thread axis vertical.')

# Printable thrust washers isolate tightening torque from the hinge members.
# Keyed pressure washer. Two tabs sit in the journal keyways, so the washer cannot
# turn with the nut and the nut's torque never reaches the cam or the arm.
_wsh=_ring(WSH_X0,WSH_X0+WSH_T,WSH_OD/2,WSH_ID/2)
for _sgn in (1,-1):
    _z0=BZ+SHAFT_D/2-KEY_D+.2 if _sgn>0 else BZ-SHAFT_D/2-.3
    _wsh=_wsh.fuse(box(WSH_X0,BY-2.9,_z0,WSH_T,5.8,3.2))
add('plug-holder-clamp-pressure-washer',_wsh.clean(),'left',
    'Keyed pressure washer between the nut and the cam plate. Two tabs ride in the journal keyways so it stays with the shaft while the nut turns against it; replace when worn.')
for label,x,y,z,ro,ri in [('tip-head',SLV_X0-CHEEK_SHIFT-1.6,tip_y,tip_z,11,6.35),('tip-nut',SLV_X0-CHEEK_SHIFT+SLV_W,tip_y,tip_z,11,6.35)]:
    washer=cx(x,y,z,ro,1.6).cut(cx(x-.1,y,z,ri,1.8)).clean()
    add(f'plug-holder-{label}-thrust-washer',washer,'left','Printable annular thrust washer: lets the fastener turn without twisting or galling the pivot cheek; replace when worn.')

# Full-diameter shaft/nut fit coupon. Nothing about the 72-mm thread should be
# trusted until this pair has been printed and turned by hand.
_cpz=19.0
_cp=make_threaded_shaft(_cpz,diameter=TH_D,pitch=TH_P,core_diameter=TH_CORE).val()
_cp=_cp.fuse(cz(0,0,_cpz,SHAFT_D/2,10.0))
_cp=_cp.cut(cz(0,0,-1,SHAFT_BORE/2,_cpz+12))
for _sgn in (1,-1):                                   # the journal keyways, so the washer tab fit is proved too
    _cp=_cp.cut(cq.Solid.makeBox(KEY_W,KEY_D+6,_cpz+12,cq.Vector(-KEY_W/2,_sgn*(SHAFT_D/2-KEY_D) if _sgn>0 else -SHAFT_D/2-6,-1)))
COUPONS['clamp-shaft-fit-coupon']=(_cp.clean(),_cp.clean())
_cpn=_knurled_blank(0,0,0).rotate((0,0,0),(0,1,0),-90)   # knurled blank about +Z
_cpn=_cpn.cut(make_threaded_hole(NUT_T,diameter=TH_D,pitch=TH_P,radial_clearance=TH_CLR_R,
                                 axial_clearance=TH_CLR_A,core_diameter=TH_CORE,phase_z=0).val())
COUPONS['clamp-nut-fit-coupon']=(_cpn.clean(),_cpn.clean())
CLAMP['fit_coupon']='clamp-shaft-fit-coupon plus clamp-nut-fit-coupon: full 72-mm thread, 19-mm stub with both keyways, and the real nut'
CLAMP['axial_stack_mm']={'shoulder_face_x':SH_FACE,'arm_base':[ARM_X0,SH_FACE],'cam_plate':[CAM_X0,ARM_X0],
                         'pressure_washer':[WSH_X0,WSH_X0+WSH_T],
                         'nut':[NUT_X,NUT_X+NUT_T],'journal':[JRN_X0,SH_FACE],'thread':[THR_X0,JRN_X0],
                         'nut_lands_inboard_of_thread_start_mm':round(abs((NUT_X+NUT_T)-JRN_X0),2),
                         'journal_longer_than_stack_mm':round((SH_FACE-JRN_X0)-(ARM_T+CAM_T+WSH_T),2)}

for i,(_,_,zz) in enumerate(length_axes,1):
    screw=make_screw(SLV_W+8,diameter=8,pitch=3,core_diameter=6.2,head_diameter=15,thread_length=12).val().rotate((0,0,0),(0,1,0),90).translate((SLV_X0-2,BY,zz))
    nut=make_nut(6,diameter=8,pitch=3,core_diameter=6.2,outer_diameter=15,radial_clearance=.30,phase_z=-(SLV_W+2)).val().rotate((0,0,0),(0,1,0),90).translate((SLV_X0+SLV_W,BY,zz))
    add(f'plug-holder-length-clamp-{i}-screw',screw,'left',f'Printable arm-length clamp screw {i}; print thread axis vertical. Captive head cannot fall out when reach is adjusted.')
    add(f'plug-holder-length-clamp-{i}-nut',nut,'left',f'Replaceable captive nut for arm-length clamp {i}; print thread axis vertical.')

blank=box(rx0,ry0+4.3,rz0+4.3,37.7,29.4,39.4).fuse(box(rx0-4,ry0+1,rz0+1,4,36,46))
blank=blank.cut(cy(clamp_x,ry0+3.5,clamp_z,6.6,40)).clean()
COUPONS['fan-stand-socket-blank']=(blank,pose(blank,'left'))
ACCESSORY.update({'installed_parts':['plug-holder-clamp-shoulder','plug-holder-polar-inner-arm','plug-holder-polar-outer-arm','plug-holder-polar-plug-rotor','plug-holder-clamp-cam-spatula'],
                  'adjustment':'polar: base angle by large face clamp + telescoping radius + independent plug-roll rotor, braced by a cam-lobe spatula pinched by the same nut','base_pivot_diameter_mm':SHAFT_D,'tip_pivot_diameter_mm':2*CHEEK_R,
                  'base_clamp':CLAMP,'reach':REACH,
                  'radial_adjustment_mm':round(TIP_MAX-TIP_MIN,2),'clamps':['large-shaft face clamp: knurled nut squeezing the cam plate and the arm base against a stationary shoulder through a keyed pressure washer','two captive-head arm-length screws','small captive annular plug-pivot screw with two printable thrust washers'],
                  'fan_stand_alternative':'fan-stand-socket-blank','receiver_clamp':'printed M12-class bolt and replaceable nut, 3-mm trapezoidal thread'})

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
    # Teardrop the transverse bore: the ties print with Z up, so this bore lies in the bed plane (L prints flipped).
    left=left.cut(bore_td((hx,yy-10.2,8),(0,1,0),BORE_R,20.4,(0,0,-1)))
    right=right.cut(bore_td((hx,yy-10.2,8),(0,1,0),BORE_R,20.4,(0,0,1)))
    for side,shape,xx,sgn in [('L',left,start,1),('R',right,end,-1)]:
        origin=(xx-16.2 if sgn>0 else xx+16.2,yy,8)
        place=lambda s,origin=origin,sgn=sgn:locate(s,origin,normal=(sgn,0,0),xdir=(0,0,-sgn))
        shape=shape.cut(bore_td((xx-.1 if sgn>0 else xx-17,yy,8),(1,0,0),BORE_R,17.1,(0,0,-1 if side=='L' else 1)))
        shape=shape.cut(place(box(-2.7,-8.2,32.8-7.5-1.7,5.4,16.4,3.4)))
        add(f'{label}-tie-{side}',shape,'flip' if side=='L' else 'base','Male T tongue prints broad top down; female socket floor prints base down. Shoulder bearing carries longitudinal load; 0.3-mm mating clearance.')
        PROTECT[f'{label}-tie-{side}']=[box(mid-13,yy-11,-1.5,31,22,18),box(start-1,yy-9,-2,19,18,19),box(end-18,yy-9,-2,19,18,19)]
        pin_and_key(f'{label}-frame-{side}',32.8,2,place,key_reverse=label=='rear',profile='round')  # 2026-09-18 trial: round shaft on the four frame-end pins first
    sgn=1
    place=lambda s,yy=yy,sgn=sgn:locate(s,(hx,yy-sgn*10.2,8),normal=(0,sgn,0),xdir=(1,0,0))
    pin_and_key(f'{label}-lap',29.4,4,place,grip=8)

# Optional physical fit plate: exact cropped T-joint ends. Coupons are not dock parts.
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
    if orientation is None or name.endswith(('-pin','-key')) or name.startswith('accessory-') or name.startswith('plug-holder-') or name=='laptop-slide-endstop-screw' or name=='centre-fence' or name.startswith('splice-clip') or name.startswith('align-aid'):continue  # fitted/threaded and centre parts stay exact
    is_tie='-tie-' in name
    shape,report=dress(PARTS[name],PRINT_Z[orientation],PROTECT.get(name,[]),inside=EDGE['inside'],outside=EDGE['outside'],top_chamfer=EDGE['top_chamfer'] if is_tie else 0.0)
    DRESS[name]=report;PARTS[name]=shape;POSES[name]=norm(pose(shape,orientation))
    print('Dressed',name,json.dumps(report),flush=True)
# The edge treatment adds concave fillet material to the halves, so cut the centre frame against the dressed halves too.
# Two-piece centre splice ring. The original four functional arcs are retained
# because their alternating M1/M2 flanges grip both plenum halves, but the back
# and front arcs are fused into one upper piece and the fan and floor arcs into
# one lower closure. Only the two opposite junctions remain as assembly joints.
# The upper piece also carries the required centre foot and sliding fence.
from shapely.ops import substring
from shapely.geometry import Point as ShpPoint, LineString
CF_CLR=0.15;_gap_lo=175.84;_gap_hi=178.14          # M1 inner shell end, M2 inner shell start
_gx0=_gap_lo+CF_CLR;_gx1=_gap_hi-CF_CLR;HALF=(_gx1-_gx0)/2.0
TRIM_OVER,TRIM_DEPTH,TRIM_PROUD=4.0,6.0,1.2
# The ring follows the plenum's structural outline, not the raw cross-section of the shell: the shell's section at the
# splice also contains the fan mounting flange, and tracing that put flange-shaped lobes on the parts that had nothing
# to sit against. Anything the clips would foul is removed by the shell cuts below instead.
_ringOut=outer.buffer(TRIM_PROUD,join_style='mitre');_ringIn=outer.buffer(-TRIM_DEPTH,join_style='mitre')
def _p(poly,x0,w):
    parts=list(poly.geoms) if poly.geom_type=='MultiPolygon' else [poly]
    out=None
    for g in parts:
        q=prism(list(g.exterior.coords)[:-1],x0,w)
        for h in g.interiors:q=q.cut(prism(list(h.coords)[:-1],x0-1,w+2))
        out=q if out is None else out.fuse(q)
    return out
_flanM2=_p(_ringOut,_gx0,(_gx1-_gx0)+TRIM_OVER).cut(_p(outer,_gx0-1,(_gx1-_gx0)+TRIM_OVER+2))
_flanM1=_p(_ringOut,_gx0-TRIM_OVER,(_gx1-_gx0)+TRIM_OVER).cut(_p(outer,_gx0-TRIM_OVER-1,(_gx1-_gx0)+TRIM_OVER+2))
_tongFull=_p(outer,_gx0,_gx1-_gx0).cut(_p(_ringIn,_gx0-1,(_gx1-_gx0)+2))   # the gap is filled to full thickness everywhere but the shiplaps
_tongM2=_p(outer,_gx0,HALF).cut(_p(_ringIn,_gx0-1,HALF+2))
_tongM1=_p(outer,_gx0+HALF,HALF).cut(_p(_ringIn,_gx0+HALF-1,HALF+2))
_exl=outer.exterior;_L=_exl.length;OVL=9.0
def _arcline(s0,s1,ovl=None):
    ov=OVL if ovl is None else ovl
    a=(s0-ov)%_L;b=(s1+ov)%_L
    if a<b:return substring(_exl,a,b)
    return LineString(list(substring(_exl,a,_L).coords)+list(substring(_exl,0,b).coords))
def _mask(s0,s1,ovl=None):
    band=_arcline(s0,s1,OVL if ovl is None else ovl).buffer(TRIM_DEPTH+TRIM_PROUD+1.0,cap_style=2,join_style=2)
    parts=list(band.geoms) if band.geom_type=='MultiPolygon' else [band]
    out=None
    for g in parts:
        q=prism(list(g.exterior.coords)[:-1],_gx0-TRIM_OVER-2,(_gx1-_gx0)+2*TRIM_OVER+4)
        out=q if out is None else out.fuse(q)
    return out
def _inward(sv,d):
    p=_exl.interpolate(sv);q=_exl.interpolate((sv+0.5)%_L)
    tx,tz=q.x-p.x,q.y-p.y;n=math.hypot(tx,tz) or 1.0;tx,tz=tx/n,tz/n
    for sgn in (1,-1):
        if outer.contains(ShpPoint(p.x-sgn*tz*1.0,p.y+sgn*tx*1.0)):return (p.x-sgn*tz*d,p.y+sgn*tx*d)
    return (p.x,p.y)
def _key(sv,r,x0,length):
    y,z=_inward(sv,TRIM_DEPTH/2.0)
    return cq.Solid.makeCylinder(r,length,cq.Vector(x0,y,z),cq.Vector(1,0,0))
JUNC=[100.0,200.0,280.0,341.0]
ARCS=[('back',341.0,100.0,'M1'),('front',100.0,200.0,'M2'),('fan',200.0,280.0,'M1'),('floor',280.0,341.0,'M2')]
DESK_Z=-4.0;SAD_GAP=0.5;SEAT_Z=54.0;ROOF_Z=50.0
FENCE_OUT,FENCE_IN,STAND_OUT=-19.335,-13.5,-25.335
BX0=_gx0-TRIM_OVER;BW=(_gx1-_gx0)+TRIM_OVER
_wall=prism([(STAND_OUT,DESK_Z+SAD_GAP),(FENCE_IN,DESK_Z+SAD_GAP),(FENCE_IN,29.0),(FENCE_OUT,29.0),(FENCE_OUT,ROOF_Z),(STAND_OUT,ROOF_Z)],BX0,BW)   # solid below the channel so the holder's outer wall ties back to the skin, then the channel's outer wall above
_pad=prism([(FENCE_IN+0.5,ROOF_Z),(8.0,ROOF_Z),(8.0,SEAT_Z),(FENCE_IN+0.5,SEAT_Z)],BX0,BW)
_chan=prism([(FENCE_OUT,29.0),(FENCE_IN,29.0),(FENCE_IN,SEAT_Z+1),(FENCE_OUT,SEAT_Z+1)],BX0-1,BW+2)
# Consistent thickness in the joint: the tongue fills the whole 2-mm gap along the core of each arc, and only steps
# down to half over the shiplap that straddles each junction, where the neighbour's opposite half makes it up again.
# The flange has to pass through the gap to reach its lap, so it is confined to the same core arc.
# The band masks are flat-capped buffers round a polyline, so two neighbours' caps cross where the outline turns a
# corner at a junction. Every shiplap is therefore trimmed against all four core bands: it ends exactly where the
# neighbour's full-thickness core begins, with no overlap and no gap.
_CORE={_nm:_mask(_s0,_s1,-OVL) for _nm,_s0,_s1,_side in ARCS}
_SPLICE={}
_SPLICE_LAPS={}
for _nm,_s0,_s1,_side in ARCS:
    _mc=_CORE[_nm];_me=_mask(_s0,_s1,OVL)
    _fl=(_flanM2 if _side=='M2' else _flanM1).intersect(_mc)
    _tf=_tongFull.intersect(_mc)
    _th=(_tongM2 if _side=='M2' else _tongM1).intersect(_me)
    for _on,_oc in _CORE.items():
        _th=_th.cut(_oc)
    # The fan-seat plate envelopes the normal outside M1 flange profile. Pocket
    # that exact lap into M1 and replace the removed material flush with the
    # ring, preserving the fan face and airway while restoring positive capture.
    if _nm=='fan':
        _fan_lap_recess=_fl.intersect(PARTS['M1-inner-shell']).clean()
        assert _fan_lap_recess.Volume()>10,('fan arc M1 lap recess missing',_fan_lap_recess.Volume())
        PARTS['M1-inner-shell']=PARTS['M1-inner-shell'].cut(_fan_lap_recess).clean()
    body=_fl.fuse(_tf).fuse(_th)
    if _nm=='back':body=body.fuse(_wall).fuse(_pad).cut(_chan).cut(PARTS['front-lap-pin']).cut(PARTS['rear-lap-pin']).cut(PARTS['front-lap-key']).cut(PARTS['rear-lap-key'])
    for _j in (_s0,_s1):
        body=body.fuse(_key(_j,1.5,_gx0,2*HALF)) if _side=='M2' else body.cut(_key(_j,1.65,_gx0+HALF-0.1,HALF+0.2))
    body=body.cut(PARTS['M1-inner-shell']).cut(PARTS['M2-inner-shell']).clean()
    _bits=sorted(body.Solids(),key=lambda q:-q.Volume())
    _bb=_bits[0].BoundingBox();_lapped=_bb.xmin<_gap_lo-0.01 or _bb.xmax>_gap_hi+0.01
    _lap_volume=_bits[0].intersect(box(_gx0-TRIM_OVER-1,-300,-300,TRIM_OVER+1,600,600)).Volume() if _side=='M1' else _bits[0].intersect(box(_gx1,-300,-300,TRIM_OVER+1,600,600)).Volume()
    assert _lapped and _lap_volume>1.0,(_nm,_side,'splice arc has no positive shell lap',_lap_volume)
    _SPLICE_LAPS[_nm]={'shell':_side,'engagement_mm3':_lap_volume}
    _SPLICE[_nm]=_bits[0]
    print('clip',_nm,_side,'lap',_lapped,'engagement',round(_lap_volume,1),'bodies',[round(q.Volume(),1) for q in _bits[:3]],flush=True)
# Joint-thickness audit: the four clips together must fill the whole 2-mm gap, full depth, all the way round.
_ideal=_tongFull.cut(PARTS['M1-inner-shell']).cut(PARTS['M2-inner-shell'])
_ring=_SPLICE['back']
for _nm in ('front','fan','floor'):_ring=_ring.fuse(_SPLICE[_nm])
_ring=_ring.intersect(_p(outer,_gx0,_gx1-_gx0))
_miss=_ideal.cut(_ring)
_mv=sum(q.Volume() for q in _miss.Solids())
print('joint fill: ideal %.1f mm3, filled %.1f mm3, unfilled %.1f mm3 (%.2f%%)'%(_ideal.Volume(),_ring.Volume(),_mv,100.0*_mv/_ideal.Volume()),flush=True)
for _q in sorted(_miss.Solids(),key=lambda q:-q.Volume())[:5]:
    _b=_q.BoundingBox()
    if _q.Volume()>1.0:print('  unfilled %7.2f mm3  x %.2f..%.2f  y %.1f..%.1f  z %.1f..%.1f'%(_q.Volume(),_b.xmin,_b.xmax,_b.ymin,_b.ymax,_b.zmin,_b.zmax),flush=True)
# Matching removable H contact at the centre: the same 2-mm raised seat and
# short-fence relationship as the exit-side cassette, narrowed to the ring's
# existing fork. The fork remains integral with the anti-sag foot.
_cx=BX0+0.3;_cw=BW-0.6
_crop=box(_cx,-60,-300,_cw,400,500)
_seat=insert_profiles['seat'].translate((_cx-8,0,0))
_fence=insert_profiles['far'].translate((_cx-8,0,0))
_lift=(0,-2*math.sin(math.radians(LEAN)),2*math.cos(math.radians(LEAN)))
_contact_zone=box(_cx,-100,SOCK['deck_top_z_mm'],_cw,200,200).rotate((0,0,54),(1,0,54),-LEAN)
_seat=_seat.fuse(_seat.translate(_lift).intersect(_contact_zone));_fence=_fence.fuse(_fence.translate(_lift).intersect(_contact_zone))
_foot_z=SOCK['deck_top_z_mm']-SOCK['channel_depth_mm']
_seat_ch=SOCK['seat_channel_y_mm'];_fence_ch=SOCK['fence_channel_y_mm']
_seat_foot=box(_cx,_seat_ch[0]+.3,_foot_z,_cw,_seat_ch[1]-_seat_ch[0]-.6,SOCK['channel_depth_mm']).rotate((0,0,54),(1,0,54),-LEAN)
_fence_foot=box(_cx,_fence_ch[0]+.3,_foot_z,_cw,_fence_ch[1]-_fence_ch[0]-.6,SOCK['channel_depth_mm']).rotate((0,0,54),(1,0,54),-LEAN)
_bridge=box(_cx,SOCK['fence_channel_y_mm'][0]+.3,SOCK['deck_top_z_mm'],_cw,SOCK['seat_channel_y_mm'][1]-SOCK['fence_channel_y_mm'][0]-.6,4).rotate((0,0,54),(1,0,54),-LEAN)
_centre_contact=_seat.fuse(_fence).fuse(_seat_foot).fuse(_fence_foot).fuse(_bridge).intersect(_crop).clean()
# Fill the two now-internal arc junctions with the normal full-thickness tongue;
# their former peg/socket details become buried material, not assembly features.
upper_bridge=_tongFull.intersect(_mask(96.0,104.0,0)).cut(PARTS['M1-inner-shell']).cut(PARTS['M2-inner-shell'])
lower_bridge=_tongFull.intersect(_mask(276.0,284.0,0)).cut(PARTS['M1-inner-shell']).cut(PARTS['M2-inner-shell'])
upper=_SPLICE['back'].fuse(_SPLICE['front']).fuse(upper_bridge).clean()
lower=_SPLICE['fan'].fuse(_SPLICE['floor']).fuse(lower_bridge).clean()
assert upper.isValid() and len(upper.Solids())==1,('upper splice ring invalid',len(upper.Solids()))
assert lower.isValid() and len(lower.Solids())==1,('lower splice ring invalid',len(lower.Solids()))
# Dress the stock exit-side profile to the centre receiver. This preserves the
# fork and its anti-sag foot as ring structure while giving the removable
# cassette a real clearance boundary against both the ring and M1 shell.
_centre_contact=_centre_contact.cut(PARTS['M1-inner-shell']).cut(upper).clean()
_centre_bits=sorted(_centre_contact.Solids(),key=lambda q:-q.Volume())
_centre_scrap=sum(q.Volume() for q in _centre_bits[1:])
if len(_centre_bits)>1:
    print('centre H fragments',[(q.Volume(),(q.BoundingBox().xmin,q.BoundingBox().xmax,q.BoundingBox().ymin,q.BoundingBox().ymax,q.BoundingBox().zmin,q.BoundingBox().zmax)) for q in _centre_bits],flush=True)
# Subtracting the fork deliberately trims narrow side slivers from the stock
# end profile. Accept only edge-localized trim (<=2 mm in X) or tiny boolean
# crumbs; reject loss of another cassette-scale body instead of silently taking
# the largest solid as the old code did.
_centre_bad_scrap=[q for q in _centre_bits[1:] if q.BoundingBox().xlen>2.0 and q.Volume()>=10.0]
assert _centre_bits and _centre_bits[0].isValid() and not _centre_bad_scrap,('centre H contact lost substantive body',[(q.Volume(),q.BoundingBox().xlen) for q in _centre_bad_scrap])
_centre_contact=_centre_bits[0]
add('centre-contact-cassette',_centre_contact,'left','Removable narrow H cassette dressed to the centre fork: 2-mm-raised seat plus the short exit-side fence profile, joined by a 4-mm deck bridge. The upper ring retains the support foot and fork.')
PROTECT['centre-contact-cassette']=[box(BX0-2,-300,-300,BW+4,700,700)]
add('splice-ring-upper',upper,'left','Primary centre splice: alternating M1/M2 shell laps plus the fork, hinge pad and centre desk foot for the removable short H contact cassette. Bonds to both plenum halves; print on the larger flange face with localized supports under the opposing flange and fork.')
add('splice-ring-lower',lower,'left','Lower closure for the centre splice: fan-side and floor arcs fused as one piece, with the two retained half-lap peg/socket junctions registering it to the upper ring.')
for _nm in ('splice-ring-upper','splice-ring-lower'):
    PROTECT[_nm]=[box(BX0-2,-300,-300,BW+TRIM_OVER+6,700,700)]
for index,(air,names,void_volume,_) in MODULE_AIR.items():
    # Boolean filleting can reconstruct coincident faces at the lap. Reapply the
    # shallow air-surface land after dressing so no tolerance membrane can span
    # the airway, and refresh the manufacturing pose from the corrected solid.
    for nm in names:
        corrected=PARTS[nm].cut(air).cut(LAP_RELIEF[index])
        if nm=='M1-outer-cradle-shell':corrected=corrected.cut(ACCESSORY_RECESS)
        corrected=corrected.clean()
        solids=sorted(corrected.Solids(),key=lambda q:-q.Volume())
        assert solids and (len(solids)==1 or sum(q.Volume() for q in solids[1:])<1.0),(nm,'material fragments after airway recut',[q.Volume() for q in solids])
        PARTS[nm]=solids[0]
        POSES[nm]=norm(pose(PARTS[nm],ORIENT[nm]))
    cassette_name=f'M{index}-contact-cassette'
    outer_name=names[0] if index==1 else names[1]
    PARTS[cassette_name]=PARTS[cassette_name].cut(PARTS[outer_name]).clean()
    POSES[cassette_name]=norm(pose(PARTS[cassette_name],ORIENT[cassette_name]))
    material=PARTS[names[0]].Solids()[0].fuse(PARTS[names[1]].Solids()[0]).clean()
    intrusion=air.intersect(material).Volume()
    assert intrusion<1e-3,('shell intrudes into nominal air path after edge treatment',index,intrusion)
    # The shell is explicitly re-cut by `air` above. Reuse that authoritative
    # continuous volume; OCC can otherwise report two solids at coincident
    # zero-thickness faces on the scalloped lap even though overlap is zero.
    void=air
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
threaded_mates={frozenset(p) for p in [
    ('plug-holder-clamp-shoulder','plug-holder-clamp-nut'),
    ('plug-holder-tip-annular-screw','plug-holder-tip-annular-nut'),
    ('plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut'),
    ('plug-holder-length-clamp-1-screw','plug-holder-length-clamp-1-nut'),
    ('plug-holder-length-clamp-2-screw','plug-holder-length-clamp-2-nut')]}
laptop=box(0,-P['laptop_thickness']/2,62,P['laptop_width'],P['laptop_thickness'],232.33).rotate((0,0,54),(1,0,54),-LEAN)
upper={n:PARTS[n].intersect(laptop).Volume() for n in names if boxes_overlap(bounds[n],laptop.BoundingBox()) and not n.startswith('align-aid')}   # glue-up keys are never in place with the laptop
fans={n:sum(PARTS[n].intersect(f).Volume() for f in FANS if boxes_overlap(bounds[n],f.BoundingBox())) for n in names}
for i,n in enumerate(names):
    for m in names[i+1:]:
        if not boxes_overlap(bounds[n],bounds[m]):continue
        overlap=PARTS[n].intersect(PARTS[m]).Volume()
        if ('align-aid' in n or 'align-aid' in m) and ('splice-clip' in (n+m) or ('align-aid' in n and 'align-aid' in m)):continue   # aids and trim occupy the gap in turn, never together
        if frozenset((n,m)) in threaded_mates:continue  # modeled male/female thread envelopes engage by design
        if overlap>1e-3:checks.append({'a':n,'b':m,'overlap_mm3':overlap})
motion_hits=[]
motion_fractions=[i/20 for i in range(21)]
for name,shape,axis,distance,exclude in MOTIONS:
    for fraction in motion_fractions:
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
# --- Port-pose clearance. Swing the arm to each solved port pose and confirm nothing
# touches the dock, laptop or desk, and that a plug plus boot at the port passes
# through the rotor pocket and clears every stationary part (before the pivot moved,
# the skirt sat across port 1 and the laptop keep-out could not see it).
ARM_GROUP=['plug-holder-polar-inner-arm']
OUTER_GROUP=['plug-holder-polar-outer-arm','plug-holder-polar-plug-rotor','plug-holder-tip-annular-screw','plug-holder-tip-annular-nut',
             'plug-holder-tip-head-thrust-washer','plug-holder-tip-nut-thrust-washer','plug-holder-length-clamp-1-screw','plug-holder-length-clamp-1-nut',
             'plug-holder-length-clamp-2-screw','plug-holder-length-clamp-2-nut','plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut','plug-holder-rotor-pinch-shim']
CAM_PART='plug-holder-clamp-cam-spatula'
_fixed=[n for n in names if n not in ARM_GROUP+OUTER_GROUP+[CAM_PART]]
desk=box(-200,-300,-24.0,700,700,20.0)
pose_hits=[]
for _tag,_rec in REACH['ports'].items():
    _phi=_rec['arm_angle_deg'];_dR=(BZ+_rec['tip_radius_mm'])-tip_z
    _psi=_rec['rotor_trim_deg']                        # rotor trim that squares the window to the port at this arm angle
    ROTOR_GROUP=['plug-holder-polar-plug-rotor','plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut','plug-holder-rotor-pinch-shim']
    moved={n:PARTS[n].rotate((0,BY,BZ),(1,BY,BZ),_phi) for n in ARM_GROUP}
    moved.update({n:PARTS[n].translate((0,0,_dR)).rotate((0,BY,BZ),(1,BY,BZ),_phi) for n in OUTER_GROUP if n not in ROTOR_GROUP})
    moved.update({n:PARTS[n].rotate((0,tip_y,tip_z),(1,tip_y,tip_z),_psi).translate((0,0,_dR)).rotate((0,BY,BZ),(1,BY,BZ),_phi) for n in ROTOR_GROUP})
    moved[CAM_PART]=PARTS[CAM_PART].rotate((0,BY,BZ),(1,BY,BZ),_rec['cam_rotation_deg']-CAM_ROT0)
    # lobe bearing land: push the cam 0.3 mm into the carrier along +X; overlap volume / 0.3 is the face-to-face bearing area
    _rec['lobe_bearing_area_mm2']=round(moved[CAM_PART].translate((0.3,0,0)).intersect(moved['plug-holder-polar-plug-rotor']).Volume()/0.3,1)
    # the moved parts must also clear each other (cam vs arm, sleeve, rotor)
    _mv=list(moved.items())
    for _i,(n,s) in enumerate(_mv):
        for m,o in _mv[_i+1:]:
            if frozenset((n,m)) in threaded_mates or not boxes_overlap(s.BoundingBox(),o.BoundingBox()):continue
            v=s.intersect(o).Volume()
            if v>.01:pose_hits.append({'pose':_tag,'moving':n,'fixed':m,'overlap_mm3':v})
    for n,s in moved.items():
        bb=s.BoundingBox()
        for o in _fixed:
            if not boxes_overlap(bb,bounds[o]):continue
            v=s.intersect(PARTS[o]).Volume()
            if v>.01:pose_hits.append({'pose':_tag,'moving':n,'fixed':o,'overlap_mm3':v})
        for lab,o in (('laptop',laptop),('desk',desk)):
            if not boxes_overlap(bb,o.BoundingBox()):continue
            v=s.intersect(o).Volume()
            if v>.01:pose_hits.append({'pose':_tag,'moving':n,'fixed':lab,'overlap_mm3':v})
    _py,_pz=PORTS[_tag]
    # plug body, then a 9-mm boot and a 5-mm cable running outboard through the cam plate's band
    plug=box(-P['plug_length']+P['plug_tip_length'],-P['plug_minor']/2,-P['plug_major']/2,P['plug_length'],P['plug_minor'],P['plug_major'])
    plug=plug.fuse(cx(-45.0,0,0,4.5,45.0-(P['plug_length']-P['plug_tip_length'])+0.1)).fuse(cx(-110.0,0,0,2.5,65.1))
    plug=plug.rotate((0,0,0),(1,0,0),-LEAN).translate((0,_py,_pz))
    for o in _fixed+list(moved):
        s=moved.get(o,PARTS[o])
        if not boxes_overlap(plug.BoundingBox(),s.BoundingBox()):continue
        v=plug.intersect(s).Volume()
        if v>.01:pose_hits.append({'pose':_tag,'moving':'usb-c-plug-and-boot','fixed':o,'overlap_mm3':v})
    REACH['ports'][_tag]['pose_clear']=not any(h['pose']==_tag for h in pose_hits)
print('Port-pose conflicts',json.dumps(pose_hits),flush=True)
(OUT/'port-reach.json').write_text(json.dumps(REACH,indent=2)+'\n')
(OUT/'insertion-motion.json').write_text(json.dumps({'sampled_motion_clear':not motion_hits,'sampling_fractions':motion_fractions,'assembly_sequence':'T ties joined on bench before attaching them to the cradles; plenum keys installed before fans; frame and fan fasteners checked with purchased fans present. Remove a brace as a unit before disassembling its T joint.','key_model':'Barbs compressed flush to 4.8-mm stem width during insertion; head remains full width. No elastic force or fatigue result.','conflicts':motion_hits},indent=2)+'\n')
coupon_records=[]
for name,(shape,pose) in COUPONS.items():
    assert shape.isValid() and len(shape.Solids())==1,name
    cq.exporters.export(shape,str(OUT/(name+'.step')));cq.exporters.export(norm(pose),str(OUT/(name+'.stl')),tolerance=.055,angularTolerance=.12)
    mesh=trimesh.load_mesh(OUT/(name+'.stl'));assert mesh.is_watertight and len(mesh.split())==1
    coupon_records.append({'part':name,'step':name+'.step','stl':name+'.stl','stl_sha256':sha(OUT/(name+'.stl')),'dimensions_mm':mesh.extents.tolist()})
cq.exporters.export(cq.Compound.makeCompound(list(PARTS.values())),str(OUT/'D9-P5-assembly.step'))
colors=[(44,105,123),(183,127,57),(60,78,94),(83,130,143)]
image,_=render([(s,(198,153,65) if n.endswith('-key') else (115,132,141) if n.endswith('-pin') else colors[i%4]) for i,(n,s) in enumerate(PARTS.items())],(1500,1000),(.8,1,.55),pad=45);image.save(OUT/'D9-P5-assembly.png')
manifest={'revision':'D9-P5-codex-cleanup','lean_deg':LEAN,'modular_contact':{'frame':'R7 d9-source (base, brace, tower with deck top and two 22-mm channels, 8-degree lid rail, 6-mm outer wall)','pieces_per_end':['one-piece H contact cassette: seat + fence + 4-mm deck bridge'],'contact_lift_mm':2,'lock':'one 36-mm printed pin through the outer wall and both cassette feet, 0.15-mm cam offset, no key','socket':SOCK},'fit_corrections':{'pin_bore_diameter_mm':2*BORE_R,'pin_shaft_diameter_mm':2*PIN_R_ROUND,'pin_profile':'round with one chord flat (six frame/tie pins and two cassette locks)','pin_across_corners_mm_octagon_retired':2*PIN_R,'key_barb_width_mm':2*KEY_BARB,'key_slot_mm':5.4,'key_barb_total_interference_mm':round(2*KEY_BARB-5.4,2),'t_tongue_height_mm':TONGUE_H,'source':'printed P2 fit plate, user feedback 2026-09-18'},'edge_treatment':{'parameters_mm':EDGE,'reports':DRESS,'air_recheck':AIR_DELTA,'protected':'air cavity, fan seats and screw pilots, remaining pin bores and key slots, T joints, bonded shiplaps and laptop contact band'},'cradle_source':{'both_ends':'R7 d9-source','module_1_contact':'H cassette with tall plug-end fence','module_2_contact':'H cassette with short far-end fence: rear foot strip slides through during docking'},'scope':'Cradles, bonded split plenums, standard wire fan guards, frame ties, three H contact cassettes, two-piece centre splice ring, and a universal plug-end accessory socket with cartridge and printed clamp','accessory_socket':ACCESSORY,'centre':{'parts':['upper ring: back + front arcs, hinge pad, centre foot and cassette fork','removable narrow H cassette: raised seat + short exit-side fence + deck bridge','lower closure: fan + floor arcs'],'shell_capture':'alternating M1/M2 flanges retained','splice_lap_engagement':_SPLICE_LAPS,'interlock':'two opposite half-lap junctions with 3-mm boss/socket registration; the other two former junctions are fused with full-thickness tongue bridges','x_window_mm':[BX0,BX0+BW],'fence_channel_y_mm':[FENCE_OUT,FENCE_IN],'seat_plane_z_mm':SEAT_Z,'contact_lift_mm':2,'foot_gap_above_corner_feet_mm':SAD_GAP,'joining':'epoxy','upper_print_support':'localized supports required under opposing flange and fork'},'purchased_fan_guards':2,'m4_x_35_fan_screws':8,'metal_hardware_count':10,'parts':RECORDS,'fit_coupons':coupon_records,'modules':MODULES,'joints':JOINTS,'printed_parts':len(PARTS),'part_interferences':checks,'upper_laptop_overlap_mm3':upper,'fan_overlap_mm3':fans,'qualification':'Prototype; CAD verification is separate from physical fit, accessory-socket load, printed-thread strength, screw retention, structural load and cooling tests. Rebuild Orca plates before printing this branch.','builder_sha256':sha(Path(__file__)),'source_sha256':{'R7_frame_step':sha(SOURCE_STEP[1]),'R7_socket_void_step':sha(R7/'D8-R7-socket-void-d9-source.step'),**{f'R7_{k}_step':sha(v) for k,v in INSERT_STEP.items()},'R2_step':sha(D8/'quick-fit/R2/D8-R2-quick-fit-bracket.step'),'parameters':sha(D8/'parameters.json'),'flow_geometry':sha(D8/'flow-geometry.json')}}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Keep the disposable build directory to a strict inventory so retired parts
# and old P2-named assemblies cannot be mistaken for current print geometry.
generated_keep={r['step'] for r in RECORDS}|{r['stl'] for r in RECORDS}
generated_keep|={r['step'] for r in coupon_records}|{r['stl'] for r in coupon_records}
generated_keep|={'manifest.json','insertion-motion.json','port-reach.json','D9-P5-assembly.step','D9-P5-assembly.png'}
generated_keep|={f'M{i}-{suffix}.step' for i in (1,2) for suffix in ('air','audit-material','port-caps')}
generated_keep|={f'M{i}-air-delta.step' for i,v in AIR_DELTA.items() if v['added_void_mm3']>1e-6}
removed_generated=[]
for stale in OUT.iterdir():
    if stale.is_file() and stale.name not in generated_keep:
        stale.unlink();removed_generated.append(stale.name)
if removed_generated:print('Removed stale generated files',json.dumps(sorted(removed_generated)),flush=True)
print(json.dumps({'parts':len(PARTS),'interferences':checks,'upper':upper,'fan_interference':{k:v for k,v in fans.items() if v>.001}},indent=2),flush=True)
assert not checks and max(upper.values(),default=0)<.001 and max(fans.values())<.001,'Resolve geometric interference before slicing'
assert not motion_hits,'Resolve insertion access before slicing'
assert not pose_hits,'Resolve port-pose clearance before slicing'
