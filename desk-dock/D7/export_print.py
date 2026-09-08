"""Separate PETG parts in explicit print poses; never slice the assembly."""
import json
from pathlib import Path
import cadquery as cq
import build

R=Path(__file__).resolve().parent
OUT=R/'print'
OUT.mkdir(exist_ok=True)
records=[]
for a in build.parts:
    n=a['name']
    if a['reference'] or any(k in n for k in ['foot_', 'pad_', 'liner_', 'seal_']):
        continue
    s=a['shape']
    if n=='01_manifold_with_cradle':
        s=s.rotate((0,0,0),(0,1,0),90)
        pose='Flat center-seam end wall on bed; fixed hinge support builds upward. Inspect duct roofs and accessible internal supports.'
    elif 'manifold' in n:
        s=s.rotate((0,0,0),(1,0,0),-build.ANGLE)
        pose='Fan pocket front rim on bed; open sole accessible for support removal.'
    elif 'fan_guard' in n or 'fan_thumb_lock' in n:
        s=s.rotate((0,0,0),(1,0,0),-build.ANGLE)
        pose='Flat grille front face on bed; integral top return upward.'
    elif n.startswith(('01_', '02_')) or 'bridge_key' in n:
        pose='Flat underside on bed.'
        if 'bridge_thumb_lock' in n:
            s=s.rotate((0,0,0),(1,0,0),180)
            pose='Large hand face on bed; 8 mm custom thread shaft upright.'
    else:
        s=s.rotate((0,0,build.H),(1,0,build.H),build.LEAN)
        pose='Laptop lean removed; flat underside on bed.'
        if n=='sliding_plug_cap':
            s=s.rotate((0,0,0),(1,0,0),180)
            pose='Inverted cap on its rear clevis; broad face has a 2.5 mm ledge requiring accessible support review.'
        elif n=='height_shim_pack':
            pose='Underside key on bed; broad peripheral ledge starts 4.3 mm above bed and requires accessible support review.'
        if n=='plug_cap_quarter_turn_keeper':
            s=s.rotate((0,0,0),(1,0,0),180)
            pose='Thumb paddle face on bed; stem and T lug upward; inspect lug support.'
        if n=='stop_thumb_knob':
            s=s.rotate((0,0,0),(0,1,0),-90)
            pose='Outer hand face on bed; hex head well upward.'
        if n=='breakaway_spring_cartridge':
            from breakaway_geometry import make_spring
            s=make_spring(build.p,delta=0).val().rotate((0,0,0),(1,0,0),-90)
            pose='UNLOADED spring: common flat outside face on bed; leaf lengths and bending stress in the bed plane.'
        elif n in ['breakaway_pivot_pin_10mm','cassette_cap_push_pin_6p5']:
            s=s.rotate((0,0,0),(1,0,0),90)
            pose='Large pin head on bed, shaft upright. Qualify layer strength and fit.'
        elif n=='breakaway_preload_hand_nut' or n.startswith('breakaway_spring_hand_screw'):
            s=s.rotate((0,0,0),(1,0,0),-90)
            pose='Large hand face on bed; custom thread axis vertical.'
        elif n=='independent_printed_chassis_stop_screw':
            s=s.rotate((0,0,0),(0,1,0),-90)
            pose='Large hand face on bed; 10 mm custom threaded shaft upright.'
        elif n=='stop_soft_tip':
            s=s.rotate((0,0,0),(0,1,0),90)
            pose='Closed contact face on bed; socket upward. Use a flexible bumper, or PETG with an added soft face pad and recalibrate the stop.'
    b=s.BoundingBox()
    s=s.translate((-b.xmin,-b.ymin,-b.zmin))
    b=s.BoundingBox()
    cq.exporters.export(s,str(OUT/(n+'.stl')),tolerance=.08,angularTolerance=.12)
    slab=cq.Workplane('XY').box(b.xlen+2,b.ylen+2,.2,centered=False).translate((-1,-1,0)).val()
    records.append(dict(part=n,file=n+'.stl',orientation=pose,
        dimensions_mm=[b.xlen,b.ylen,b.zlen],first_0p2mm_mean_contact_area_mm2=s.intersect(slab).Volume()/.2,
        support_review='Required: inspect unsupported ledges, bridges and support removal in a working slicer.',
        material='PETG',printer='Bambu P1S, 0.4 mm nozzle',
        infill='100% for initial structural/fastener/spring qualification; hollow CAD ducts remain hollow.'))
(R/'print-manifest.json').write_text(json.dumps(dict(parts=records,scope='Print poses and geometric outputs only. No toolpaths or physical print qualification.'),indent=2)+'\n')
print('Print-oriented parts:',len(records),flush=True)
