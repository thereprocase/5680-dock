"""Build only the cassette/hinge; check critical interfaces and export local poses."""
import hashlib
import json
from pathlib import Path
import cadquery as cq
from cassette import build_cassette, make_rear_cable_keepout, rear_cable_spec

R=Path(__file__).resolve().parent
OUT=R/'cassette-review'
OUT.mkdir(exist_ok=True)
p=json.loads((R/'parameters.json').read_text())
source_hashes={name:hashlib.sha256((R/name).read_bytes()).hexdigest()
               for name in ('cassette.py','breakaway_geometry.py','printed_fasteners.py','parameters.json')}

def box(x,y,z,a,b,c):
    return cq.Workplane('XY').box(a,b,c,centered=False).translate((x,y,z))

def rb(x,y,z,a,b,c,r=2):
    return box(x,y,z,a,b,c).edges('|Z').fillet(r)

def hole(axis,pos,r,h):
    return cq.Solid.makeCylinder(r,h,cq.Vector(*pos),cq.Vector(*axis))

parts={}
def add(name,shape,col=None,ref=False):
    s=shape.val() if isinstance(shape,cq.Workplane) else shape
    assert s.isValid() and len(s.Solids())==1 and s.Volume()>0,name
    parts[name]={'shape':s,'reference':ref}
    print('VALID',name,flush=True)

details=build_cassette(p,box,rb,hole,add)
checks=[]
def overlap(a,b,allow=False,note=''):
    v=parts[a]['shape'].intersect(parts[b]['shape']).Volume()
    checks.append({'a':a,'b':b,'overlap_mm3':v,'intentional':allow,'note':note})
    if not allow:assert v<1e-3,(a,b,v)
    print('PAIR',a,b,round(v,5),flush=True)

overlap('X_depth_overmold_clamp','height_shim_pack')
overlap('X_depth_overmold_clamp','Dell_plug_overmold_REFERENCE')
overlap('breakaway_pivot_pin_10mm','breakaway_preload_hand_nut')
overlap('breakaway_pivot_pin_10mm','breakaway_spring_cartridge')
overlap('breakaway_pivot_pin_10mm','plug_support')
overlap('breakaway_preload_hand_nut','breakaway_spring_cartridge')
for j in (0,1):
    overlap(f'breakaway_spring_hand_screw_{j}','plug_support')
    overlap(f'breakaway_spring_hand_screw_{j}','breakaway_spring_cartridge')
overlap('height_shim_pack','breakaway_carrier')
overlap('cassette_calibration_keeper_plate','breakaway_carrier')
for name in ['X_depth_overmold_clamp','height_shim_pack','cassette_calibration_keeper_plate','breakaway_carrier']:
    overlap('cassette_calibration_hand_screw',name)
overlap('sliding_plug_cap','X_depth_overmold_clamp')
overlap('sliding_plug_cap','Dell_plug_overmold_REFERENCE',True,'Provisional .30mm overmold squeeze')
overlap('cassette_cap_push_pin_6p5','sliding_plug_cap')
overlap('cassette_cap_push_pin_6p5','X_depth_overmold_clamp',True,'Two .05mm radial pin retention lands')
for name in ['sliding_plug_cap','X_depth_overmold_clamp','cassette_cap_push_pin_6p5']:
    overlap(name,'breakaway_pivot_pin_10mm')
    overlap(name,'breakaway_carrier')
corner_checks=[]
# These three upper pieces translate with the measured cable position.  The
# independently regenerated shim/base and the complete duct are not covered.
for dx in p['depth_range']:
    for dy in p['lateral_range']:
        for dz in p['height_range']:
            for name in ['sliding_plug_cap','cassette_cap_push_pin_6p5']:
                moved=parts[name]['shape'].translate((dx,dy,dz))
                v=moved.intersect(parts['breakaway_carrier']['shape']).Volume()
                assert v<1e-3,(name,dx,dy,dz,v)
                corner_checks.append({'part':name,'translation_mm':[dx,dy,dz],
                                      'carrier_overlap_mm3':v})
overlap('independent_printed_chassis_stop_screw','chassis_stop_block')
overlap('stop_soft_tip','independent_printed_chassis_stop_screw')
overlap('stop_soft_tip','chassis_stop_block')
overlap('chassis_stop_block','plug_support',True,'Intentional fused fixed load path')
assert checks[-1]['overlap_mm3']>1

# The actual cable outside the source stub is unmeasured. This 8 mm envelope
# screens a deliberately loose illustrative loop against the modeled parts.
from breakaway_geometry import datum,cam_lift,make_carrier
cable=make_rear_cable_keepout(p).val()
assert cable.isValid() and len(cable.Solids())==1
cable_checks=[]
for name in parts:
    v=cable.intersect(parts[name]['shape']).Volume()
    assert v<1e-3,('rear cable',name,v)
    cable_checks.append({'part':name,'angle_deg':0,'overlap_mm3':v})
for lift in (5,10,20,35):
    v=cable.intersect(parts['sliding_plug_cap']['shape'].translate((0,0,lift))).Volume()
    assert v<1e-3,('cap reclosure',lift,v)
    cable_checks.append({'part':'sliding_plug_cap','cap_lift_mm':lift,'overlap_mm3':v})
    raised=cable.translate((0,0,lift))
    for name in ('X_depth_overmold_clamp','breakaway_carrier'):
        v=raised.intersect(parts[name]['shape']).Volume()
        assert v<1e-3,('cable lay-in',name,lift,v)
        cable_checks.append({'part':name,'cable_lay_in_lift_mm':lift,'overlap_mm3':v})
px,pz=datum(p)
fixed=['plug_support','breakaway_pivot_pin_10mm','breakaway_spring_cartridge',
       'breakaway_preload_hand_nut','breakaway_spring_hand_screw_0',
       'breakaway_spring_hand_screw_1','chassis_stop_block',
       'independent_printed_chassis_stop_screw','stop_soft_tip']
for angle in (5,10,15,20,30,45):
    moved=cable.rotate((px,0,pz),(px,1,pz),angle).translate((0,-cam_lift(p,angle),0))
    for name in fixed:
        v=moved.intersect(parts[name]['shape']).Volume()
        assert v<1e-3,('folded rear cable',angle,name,v)
        cable_checks.append({'part':name,'angle_deg':angle,'overlap_mm3':v})
before=make_carrier(p).cut(rb(-28,-11,p['rear_case_seat_z']+p['port_from_rear_case']-26.1,24,20,7.6,2)).val()
notch_removed=before.Volume()-parts['breakaway_carrier']['shape'].Volume()
cq.exporters.export(cable,str(OUT/'rear_cable_clearance_keepout_NONPRINT.step'))

records=[]
for name,item in parts.items():
    if item['reference'] or name.startswith('breakaway_') or name=='plug_support':continue
    s=item['shape']
    pose='Base down; review underside roofs after slicing'
    if name=='cassette_calibration_hand_screw':pose='Knob on bed; threaded shaft upright'
    elif name=='cassette_cap_push_pin_6p5':
        s=s.rotate((0,0,0),(1,0,0),90);pose='Pin head on bed; shaft upright'
    elif name in ['stop_soft_tip','independent_printed_chassis_stop_screw']:
        s=s.rotate((0,0,0),(0,1,0),-90)
        pose='Axis upright; knob down for screw, open socket up for bumper'
        if name=='stop_soft_tip':s=s.rotate((0,0,0),(1,0,0),180)
    elif name=='sliding_plug_cap':
        s=s.rotate((0,0,0),(1,0,0),180);pose='Rear clevis on bed; broad cap ledge starts 2.5 mm above bed. Cable relief opens upward; horizontal pin bore needs support/fit review.'
    b=s.BoundingBox();s=s.translate((-b.xmin,-b.ymin,-b.zmin))
    path=OUT/(name+'.stl')
    cq.exporters.export(s,str(path),tolerance=.04,angularTolerance=.1)
    b=s.BoundingBox()
    records.append({'name':name,'file':path.name,'size_mm':[b.xlen,b.ylen,b.zlen],
                    'pose':pose,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
report={'details':details,'part_count_with_hinge':len(parts),'cassette_stl_count':len(records),
        'critical_pairs':checks,'upper_cap_carrier_corner_checks':corner_checks,'parts':records,
        'rear_cable_spec':rear_cable_spec(p),'rear_cable_checks':cable_checks,
        'rear_wall_notch_removed_mm3':notch_removed,
        'source_modules_sha256':source_hashes,
        'limits':'Nominal isolated geometry, cap/pin-to-carrier translations at adjustment corners and the selected provisional cable-loop/lift samples only; regenerated calibration shapes, full-body sweep, slicing, actual cable flexibility and physical fit remain separate.',
        'cassette_source_sha256':hashlib.sha256((R/'cassette.py').read_bytes()).hexdigest()}
(OUT/'cassette-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('EXPORTED',len(records),'cassette STLs; valid total parts',len(parts),flush=True)
