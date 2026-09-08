"""D8 print-first development CAD. Exported +X runs away from keyboard-left/plug end; +Y lid/fans; -Y underside/intakes; +Z up.
Builds physical duct passages, fan mounts, three adjustment stages and guards.
Separate production detailing and slicer/physical qualification remain required.
"""
from pathlib import Path
import json, math
import cadquery as cq
from cadquery import exporters
R=Path(__file__).resolve().parent
p=json.loads((R/'parameters.json').read_text())
W=p['laptop_width'];T=p['laptop_thickness'];H=p['rear_case_seat_z'];WALL=float(p['wall'])
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
from fan_service import fan_dimensions,POSE_ANCHOR_Z
FAN_D=fan_dimensions(p['fan_thickness'],p.get('fan_fit',{}).get('pad_thickness_mm',0.0))
FACE_C=FAN_Y+FAN_Z*math.tan(ELEV)-7.5/math.cos(ELEV)-.10
INNER_C=FACE_C-WALL/math.cos(ELEV)
def front_y(z,inner=False):return (INNER_C if inner else FACE_C)-math.tan(ELEV)*z

def rest_y(z):return (T/2+.6)/math.cos(math.radians(LEAN))+(z-H)*math.tan(math.radians(LEAN))
flow_voids=[];mouth_records=[]
for i,((x0,x1),fx) in enumerate(zip([(-7,W/2),(W/2+.30,W+25)],p['fan_centers_x']),1):
    print('Building D8 shell',i,flush=True)
    length=x1-x0
    def profile(x,length,inner=False):
        if not inner:
            return (cq.Workplane('YZ',origin=(x,0,0)).moveTo(-24,3)
              .lineTo(-24,41).threePointArc((-21,48),(-13,50)).lineTo(13,50)
              .lineTo(rest_y(66),66).lineTo(rest_y(129),129)
              .lineTo(rest_y(134)+2,134).lineTo(front_y(134),134)
              .lineTo(front_y(3),3).close().extrude(length))
        return (cq.Workplane('YZ',origin=(x,0,0)).moveTo(-24+WALL,3+WALL)
              .lineTo(-24+WALL,40).threePointArc((-18,46),(-12,50-WALL)).lineTo(13,50-WALL)
              .lineTo(rest_y(66)+WALL,66).lineTo(rest_y(129)+WALL,129)
              .lineTo(rest_y(134-WALL)+3,134-WALL).lineTo(front_y(134-WALL,True),134-WALL)
              .lineTo(front_y(3+WALL,True),3+WALL).close().extrude(length))
    def low(x,l,rear,bottom,top,inner=False):
        return (cq.Workplane('YZ',origin=(x,0,0)).moveTo(rear,bottom).lineTo(rear,top)
          .lineTo(front_y(top,inner),top).lineTo(front_y(bottom,inner),bottom).close().extrude(l))
    outer=low(x0,length,-24,3,50).union(profile(fx-62,124))
    inner=low(x0+WALL,length-2*WALL,-24+WALL,3+WALL,50-WALL,True).union(profile(fx-62+WALL,124-2*WALL,True))
    edge_list=[e for e in outer.val().Edges() if abs(e.BoundingBox().ymin+24)<1e-5 and abs(e.BoundingBox().ymax+24)<1e-5 and e.BoundingBox().xlen<1e-5 and e.BoundingBox().zlen>20]
    outer=cq.Workplane(obj=outer.val().fillet(2.0,edge_list))
    roof=outer.cut(inner)
    # Keep the mouths outside bearing pads and the split joint. Full-width
    # rounded rectangles avoid a row of narrow, sharp-edged whistle slots.
    ma=max(42,x0+4);mb=min(W-24,x1-4)
    mw=float(p['mouth_width_mm']);mr=float(p['mouth_corner_radius_mm']);me=float(p['mouth_edge_radius_mm'])
    mouth=rb(ma,-mw/2,43,mb-ma,mw,16,mr)
    roof=roof.cut(mouth)
    edges=[]
    for e in roof.val().Edges():
        bb=e.BoundingBox()
        if abs(bb.zmin-50)<1e-5 and abs(bb.zmax-50)<1e-5 and bb.xmin>=ma-.01 and bb.xmax<=mb+.01 and bb.ymin>=-mw/2-.01 and bb.ymax<=mw/2+.01:edges.append(e)
    if edges and me>0:roof=cq.Workplane(obj=roof.val().fillet(me,edges))
    mouth_records.append({'module':i,'construction_x_bounds':[ma,mb],'width_mm':mw,'corner_radius_mm':mr,'edge_radius_mm':me,'area_mm2':(mb-ma)*mw-(4-math.pi)*mr**2})
    def fanpose(shape):
        return shape.translate((-fx,-91,-POSE_ANCHOR_Z)).rotate((0,0,0),(1,0,0),ANGLE).translate((fx,FAN_Y,FAN_Z))
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
    from fan_service import build_fan_service
    roof=build_fan_service(i,fx,roof,fanpose,box,rb,hole,add,thickness=p['fan_thickness'],fit=p.get('fan_fit'))
    add(f'{i:02}_suction_roof',roof)
    # Retain the exact connected cavity for geometric area/volume screening.
    flow_voids.append(inner.val())
    fan_start=len(parts)
    # Fan envelope with realistic opening, hub, seven schematic blades and struts.
    fan=rb(fx-60,31,FAN_D['front'],120,120,p['fan_thickness'],6).cut(hole((0,0,1),(fx,91,FAN_D['front']-1),56.5,p['fan_thickness']+2))
    for xx in [fx-52.5,fx+52.5]:
      for yy in [38.5,143.5]:fan=fan.cut(hole((0,0,1),(xx,yy,FAN_D['front']-1),2.2,p['fan_thickness']+2))
    add(f"{i:02}_120x{p['fan_thickness']:g}_fan_frame",fan,(28,31,33),True)
    hub=cq.Workplane('XY').center(fx,91).circle(17).extrude(p['fan_thickness']-3).translate((0,0,FAN_D['front']+1))
    for a in range(0,360,90):
        arm=box(fx+10,88.8,FAN_D['front']+1,48,4.4,2).rotate((fx,91,0),(fx,91,1),a)
        hub=hub.union(arm)
    add(f'{i:02}_fan_hub_struts',hub,(61,65,68),True)
    for j in range(7):
        blade=(cq.Workplane('XY').moveTo(15,-6).threePointArc((35,-18),(51,-9))
          .threePointArc((52,4),(47,11)).threePointArc((30,9),(15,1)).close()
          .extrude(1.3).rotate((0,0,0),(0,0,1),j*360/7).translate((fx,91,FAN_D['center']+.5)))
        add(f'{i:02}_blade_{j}',blade,(72,76,78),True)
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
    add('corner_cradle_'+tag,cradle)
# Continuous low retention lip: the original 12 mm profile spans the laptop,
# with only the 0.3 mm joint between the two printable shells. Extending its
# root below the deck makes the lip integral with the plenum along its length.
# The rear rubber-foot keepout starts 3.057 mm above its top in this frame.
lip_root=p['retention_lip_root_z_mm']
lip_top=H+p['retention_lip_height_mm']
lip_pts=[(-G-3,lip_root),(-G-3,lip_top),(-G-1,lip_top),(-G,H+8),(-G,lip_root)]
for side,a,b in [('left',6,W/2),('right',W/2+.3,W+20)]:
    lip=cq.Workplane('YZ',origin=(a,0,0)).polyline(lip_pts).close().extrude(b-a)
    add('retention_lip_'+side,lip)
# Thin replaceable liners on the plenum wall carry the lid-side lean load.
# Two broad, separated contacts use the duct itself as the stand structure.
for i,fx in enumerate(p['fan_centers_x'],1):
    add(f'lid_bearing_liner_{i}',box(fx-43,T/2,H+20,86,.6,52),(119,131,124))
for yy,seal_width in [(-G,.6),(11.0,1.3)]:
    # Replaceable compliant seal; bearing loads use end pads, not this lip.
    # The thin rear strip fits inside the new continuous rail and stays clear
    # of the mouth. It uses the same 0.6 mm stock as the lid contact liners.
    for a,b in [(42,W/2-.2),(W/2+.5,W-24)]:
        seal=box(a,yy,50,b-a,seal_width,3.6).val()
        # Adhere the rear strip directly to the lip's leaned inside face.
        if yy<0:seal=leaned(seal)
        add(f'hinge_seal_{a:.1f}_{yy}',seal,(56,80,75))

# Hand-adjusted cassette, captured nuts and tool-free removable cap.
from cassette import build_cassette
cassette_metadata=build_cassette(p,box,rb,hole,add)

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

bodies=[];roof_print_metadata=[]
from body_print_geometry import roof_gussets
from connector_clearance import clear_shell_for_module
for side,i,x0,x1 in [('left','01',-7,W/2),('right','02',W/2+.30,W+25)]:
    roof=take(i+'_suction_roof').fuse(take('corner_cradle_'+side)).fuse(take('retention_lip_'+side)).clean()
    roof,print_meta=roof_gussets(roof,x0,x1,p['fan_centers_x'][int(i)-1],front_y,W,WALL,p['mouth_width_mm'])
    roof_print_metadata.append(print_meta)
    if side=='left':
        roof=clear_shell_for_module(roof,p)
        roof=roof.fuse(take('connector_shell_shoe')).clean()
    bodies.append((x0,x1,roof))
from body_service import body_service
body_service_metadata=body_service(bodies,W,front_y,box,rb,hole,add)
# Subtract the final retainer bosses and panel flanges from the baseline cavity.
# This conservative cavity omits the small extra volume below the original floor.
for i in range(2):
    for item in parts:
        if item['name'] in [f'{i+1:02}_manifold_with_cradle',f'{i+1:02}_bottom_panel']:
            flow_voids[i]=flow_voids[i].cut(item['shape']).clean()

# Preserve source handedness. Dell keyboard-left is source -X, hence x=0.
# With a right-handed camera at +Y and +Z up, x=0 appears screen-right.
# Laptop withdrawal is +X; insertion is -X. No final reflection is permitted.
# Replace ambiguous viewer-left/right names with the actual desk relation.
for item in parts:
    item['name']=item['name'].replace('corner_pad_left','corner_pad_far').replace('corner_pad_right','corner_pad_near')

print('Exporting D8 assembly',flush=True)
ass=cq.Assembly(name='Precision_5680_D8')
for a in parts:ass.add(a['shape'],name=a['name'],color=cq.Color(*[v/255 for v in a['color']]))
ass.save(str(R/'Precision_5680_D8.step'))
manifest=[]
for a in parts:
    b=a['shape'].BoundingBox()
    manifest.append({k:a[k] for k in ['name','reference']}|{'volume_mm3':a['shape'].Volume(),'bounds_mm':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]})
(R/'flow-geometry.json').write_text(json.dumps({'mouths':mouth_records,'plenum_volumes_mm3':[v.Volume() for v in flow_voids],'cavity_basis':'Baseline void minus final body bosses and bottom panels; conservative omission of new floor clearance.','exhaust_axis':[0,math.cos(ELEV),math.sin(ELEV)]},indent=2)+'\n')
(R/'assembly-details.json').write_text(json.dumps({'cassette':cassette_metadata,'body_service':body_service_metadata,'roof_print_geometry':roof_print_metadata,'fan_fit':__import__('fan_service').ACTIVE_SPECS,'fan_retention':__import__('fan_service').TOP_CLIP_SPECS},indent=2)+'\n')
(R/'geometry.json').write_text(json.dumps({'coordinate_frame':p['coordinate_frame'],'scope':'D8 removable adjustable connector and direct-foot plenum study. End seats and lid liners support the laptop; no tall cheeks or underside frame. Source-handed USB-C ports. Physical qualification remains outstanding.','parts':manifest},indent=2)+'\n')
print('D8 exported:',len(parts),'valid solids',flush=True)

