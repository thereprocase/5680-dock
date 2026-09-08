"""Sampled D7 assembly/service clearances; no claim of physical qualification.

Run from any working directory. Importing build regenerates the final assembly
once; every service sample then reuses those shapes. Adjustment corner checks
regenerate only the small isolated connector cassette, never the entire dock.
"""
import itertools
import json
import math
from pathlib import Path

import cadquery as cq
import build
from cassette import build_cassette

R=Path(__file__).resolve().parent
LIMIT=.01


def overlap(a,b):
    A=a.BoundingBox(); B=b.BoundingBox()
    if (A.xmax<=B.xmin+1e-6 or B.xmax<=A.xmin+1e-6 or
        A.ymax<=B.ymin+1e-6 or B.ymax<=A.ymin+1e-6 or
        A.zmax<=B.zmin+1e-6 or B.zmax<=A.zmin+1e-6):
        return 0.0
    return a.intersect(b).Volume()


def cassette_corner(dx,dy,dz):
    parts=[]
    def add(name,shape,color=None,ref=False):
        if isinstance(shape,cq.Workplane): shape=shape.val()
        assert shape.isValid() and len(shape.Solids())==1 and shape.Volume()>0,name
        parts.append(dict(name=name,shape=shape,reference=ref))
    p=dict(build.p,depth_adjustment=dx,lateral_adjustment=dy,height_adjustment=dz)
    build_cassette(p,build.box,build.rb,build.hole,add)
    hits=[]
    for a,b in itertools.combinations(parts,2):
        # Metal thread envelopes intentionally overlap their metal nuts.
        if a['reference'] and b['reference']: continue
        v=overlap(a['shape'],b['shape'])
        if v>LIMIT: hits.append([a['name'],b['name'],round(v,6)])
    return dict(adjustment_depth_lateral_height_mm=[dx,dy,dz],
                valid_single_solids=len(parts),collisions=hits,
                scope='Isolated cassette only; not a laptop/plenum adjustment qualification.')


def main():
    from contact_check import intended_contact
    from breakaway_geometry import datum,cam_lift,make_spring,moving_names
    from cassette import make_rear_cable_keepout,rear_cable_spec
    byname={a['name']:a for a in build.parts}
    unloaded={n for n in byname if n=='Precision_5680_REFERENCE' or n.startswith('RUBBER_FOOT_')}
    lean=math.radians(build.LEAN)
    up=(0,math.sin(lean),math.cos(lean));negative_y=(0,-math.cos(lean),math.sin(lean))
    stages=[]
    def stage(label,moving,removed,samples,transform,instruction,pin=False):
        moving=set(moving);removed=set(removed)|unloaded
        fixed=[a for n,a in byname.items() if n not in moving|removed]
        rows=[]
        for sample in samples:
            hits=[];fits=[]
            for name in sorted(moving):
                moved=transform(byname[name]['shape'],sample)
                for a in fixed:
                    v=overlap(moved,a['shape'])
                    if v<=LIMIT:continue
                    shift=tuple(sample*x for x in negative_y) if pin else (0,0,0)
                    ok,why=intended_contact(byname[name],a,build.p,build.leaned,moved.intersect(a['shape']),shift)
                    (fits if ok else hits).append([name,a['name'],round(v,6),why])
            rows.append(dict(sample=sample,collisions=hits,intentional_contacts=fits))
        row=dict(operation=label,instruction=instruction,moving_parts=sorted(moving),removed_before_operation=sorted(removed),samples=rows,passed=all(not s['collisions'] for s in rows))
        stages.append(row);print(label+': '+('PASS' if row['passed'] else 'COLLISION'),flush=True)
    pin='cassette_cap_push_pin_6p5';cap='sliding_plug_cap'
    stage('Printed cap pin withdrawal',[pin],[],[0,.5,2,5,10,20,35],lambda s,d:s.translate(tuple(d*x for x in negative_y)),
          'Pull the large cap pin toward the underside side; small retention ribs flex during withdrawal.',True)
    stage('Plug cap lift',[cap],[pin],[0,.3,1,3,8,16,30],lambda s,d:s.translate(tuple(d*x for x in up)),
          'Remove pin, then lift cap. The initial overmold squeeze is a deliberate fit allowance.')
    fan_up=(0,-math.sin(build.ELEV),math.cos(build.ELEV))
    for prefix in ['01_','02_']:
        panel=prefix+'bottom_panel';feet={n for n in byname if n.startswith(prefix+'foot_')}
        locks={n for n in byname if n.startswith(prefix+'bottom_thumb_lock_')}
        stage(prefix+'bottom cover withdrawal',{panel}|feet,locks,[0,.5,2,5,10,20],lambda s,d:s.translate((0,0,-d)),
              'Lift unloaded stand from desk, remove its printed floor locks, lower cover with feet and lay-in cable saddle.')
        guard=prefix+'fan_guard_retainer'
        stage(prefix+'grille lift',[guard],[],[0,.5,2,4,6,10,25,60,100,140],lambda s,d:s.translate(tuple(d*x for x in fan_up)),
              'Laptop removed: slide grille upward along the inclined pocket; friction lands release in the first few millimetres.')
        fan={n for n in byname if n.startswith(prefix) and ('_fan_frame' in n or 'fan_hub_struts' in n or 'blade_' in n)}
        stage(prefix+'fan lift',fan,[guard],[0,1,3,6,15,35,70,110,140],lambda s,d:s.translate(tuple(d*x for x in fan_up)),
              'After grille removal and cable disconnection, lift fan from the open-top pocket.')
    spring='breakaway_spring_cartridge'
    remove={n for n in byname if n.startswith('breakaway_spring_hand_screw')}|{'breakaway_preload_hand_nut'}
    free_spring=build.leaned(make_spring(build.p,delta=0).val())
    stage('Unloaded spring cartridge withdrawal',[spring],remove,[0,1,3,8,16,30],lambda s,d:free_spring.translate(tuple(-d*x for x in negative_y)),
          'Support the unloaded cassette, remove preload nut and both cartridge screws; withdraw the relaxed cartridge off the axle.')
    # Full mechanism samples include movement of axle/nut and elastic spring
    # shapes. Static laptop is excluded: this is unmated docking retreat.
    px,pz=datum(build.p);samples=[]
    # Clip distant fan/body detail once for the hinge-only stage. Every moving
    # part and the entire cable allowance must lie inside this box, so the
    # excluded material cannot intersect them. Keep the full bodies for the
    # fan, grille and cover service checks above.
    clip_limits=(-160,-60,20,32,140,230)
    clip_box=build.box(-160,-60,20,192,200,210).val()
    hinge_body=byname['01_manifold_with_cradle']['shape'].intersect(clip_box)
    def inside_clip(s):
        b=s.BoundingBox()
        return b.xmin>=-160 and b.xmax<=32 and b.ymin>=-60 and b.ymax<=140 and b.zmin>=20 and b.zmax<=230
    cable_allowance=make_rear_cable_keepout(build.p).val()
    for angle in [0,.1,.5,1,2,3,4,10,20,30,45]:
        lift=cam_lift(build.p,angle);posed=[]
        for name,a in byname.items():
            if name in unloaded:continue
            s=a['shape']
            dynamic=moving_names(name) or name in [spring,'breakaway_pivot_pin_10mm','breakaway_preload_hand_nut']
            if name==spring:s=build.leaned(make_spring(build.p,build.p['breakaway']['spring_preload_deflection_mm']+lift).val())
            elif dynamic:
                s=s.rotate((0,0,build.H),(1,0,build.H),build.LEAN)
                if moving_names(name):s=s.rotate((px,0,pz),(px,1,pz),angle)
                s=build.leaned(s.translate((0,-lift,0)))
            if dynamic:assert inside_clip(s),(name,angle,'hinge collision clip too small')
            if name=='01_manifold_with_cradle':s=hinge_body
            posed.append(dict(a,shape=s,dynamic=dynamic))
        hits=[]
        # Internal cassette fits move as a unit; the separate nominal and
        # isolated checks qualify them. Screen every changing interface here.
        for a,b in itertools.combinations(posed,2):
            if not(a['dynamic'] or b['dynamic']):continue
            if moving_names(a['name']) and moving_names(b['name']):continue
            v=overlap(a['shape'],b['shape'])
            if v>LIMIT:hits.append([a['name'],b['name'],round(v,6)])
        cable=build.leaned(cable_allowance.rotate((px,0,pz),(px,1,pz),angle).translate((0,-lift,0)))
        assert inside_clip(cable),('cable',angle,'hinge collision clip too small')
        cable_hits=[]
        for a in posed:
            if a['dynamic']:continue
            v=overlap(cable,a['shape'])
            if v>LIMIT:cable_hits.append(['provisional_rear_cable_loop',a['name'],round(v,6)])
        hits+=cable_hits
        samples.append(dict(angle_deg=angle,cam_lift_mm=lift,collisions=hits,cable_fixed_hardware_collisions=cable_hits))
        print('Breakaway '+str(angle)+': '+('PASS' if not hits else 'COLLISION '+str(hits)),flush=True)
    data=dict(service_stages=stages,breakaway_samples=samples,rear_cable_allowance=rear_cable_spec(build.p),hinge_collision_clip_bounds_mm=clip_limits,
        scope='Sampled actual CAD, spring shape, compliant fit regions and a provisional free cable loop against fixed hardware. Not a continuous sweep, actual cable bend/slack or remote-anchor model, measured force, fatigue or impact validation.',
        passed=all(s['passed'] for s in stages) and all(not s['collisions'] for s in samples))
    (R/'service-validation.json').write_text(json.dumps(data,indent=2)+'\n')
    assert data['passed'],'See service-validation.json for colliding parts and samples.'
    print('D7 service and breakaway geometry checks passed.',flush=True)

if __name__=='__main__':main()
