"""Check exact cached D8 assembly BReps without importing or rerunning build.

Usage: python validate.py --cache /path/to/d8-review-cache
The cache contains parts.json and one <name>.brep for every part. Static checks
include physical fan/plug references; the nominal laptop and expanded rubber
foot envelopes receive separately reported, finite docking-path samples.
Module and bottom-panel removal have additional finite, unloaded samples.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import math
import re
import tempfile
import cadquery as cq

R=Path(__file__).resolve().parent
VOLUME_TOLERANCE_MM3=.01
BOUND_TOLERANCE_MM=1e-6
SOFT_NAMES=('corner_pad_','lid_bearing_liner_','hinge_seal_')


def box(x,y,z,a,b,c):
    return cq.Workplane('XY').box(a,b,c,centered=False).translate((x,y,z)).val()


def bounds(shape):
    b=shape.BoundingBox()
    return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]


def boxes_overlap(a,b):
    return all(a[k+3]>b[k]+BOUND_TOLERANCE_MM and
               b[k+3]>a[k]+BOUND_TOLERANCE_MM for k in range(3))


def is_soft(name):
    return name.startswith(SOFT_NAMES) or '_desk_pad_' in name or name=='stop_soft_tip'


def is_physical_reference(name):
    return name in ('Dell_plug_overmold_REFERENCE','USB_C_shell_REFERENCE') or any(
        token in name for token in ('fan_frame','fan_hub_struts','_blade_'))


def contact_regions(a,b,p):
    """Return only narrowly bounded, named elastic contact regions.

    No shell/module, screw/thread, or fan-clip/shell intersection is waived.
    """
    names={a['name'],b['name']}
    H=p['rear_case_seat_z'];lean=p['laptop_lean_deg']
    def leaned(s):return s.rotate((0,0,H),(1,0,H),-lean)
    dy=float(p.get('lateral_adjustment',0));dz=float(p.get('height_adjustment',0))
    # D8 keeps plug X fixed. The separate chassis stop supplies X adjustment.
    cx=-26.5;cy=p['port_y']+dy;cz=H+p['port_from_rear_case']+dz
    if names=={'sliding_plug_cap','Dell_plug_overmold_REFERENCE'}:
        squeeze=float(p.get('overmold_grip_squeeze_mm',.3))
        region=box(cx+5.98,cy-2.92,cz+6.25-squeeze-.02,18.04,5.84,squeeze+.04)
        return [leaned(region)],'calibratable cap/overmold squeeze strip'
    if 'cassette_cap_push_pin_6p5' in names and names.intersection(
            {'X_depth_overmold_clamp','sliding_plug_cap'}):
        top_y=8.5+dy
        regions=[]
        # Current ribs are measured from the moving pin's TOP end. Restrict
        # acceptance to the small annulus protruding through the 6.8 mm bore.
        for centre_y in (top_y-1.3,top_y-2.5):
            origin=cq.Vector(cx-1,centre_y-.43,cz+9)
            outer=cq.Solid.makeCylinder(3.48,.86,origin,cq.Vector(0,1,0))
            inner=cq.Solid.makeCylinder(3.38,.86,origin,cq.Vector(0,1,0))
            regions.append(leaned(outer.cut(inner)))
        return regions,'two near-end cap-pin retention-rib annuli'
    clip=next((re.fullmatch(r'(0[12])_fan_top_clip_([12])',n) for n in names
               if re.fullmatch(r'(0[12])_fan_top_clip_([12])',n)),None)
    if clip:
        module=int(clip.group(1));side=int(clip.group(2))
        other=next(n for n in names if n!=clip.group(0))
        if other.startswith(f'{module:02}_') and 'fan_frame' in other:
            fx=p['fan_centers_x'][module-1]
            x=fx+(-52.5 if side==1 else 52.5)
            fit=p.get('fan_fit',{})
            front=30-p['fan_thickness']-2*float(fit.get('pad_thickness_mm',0))
            def fanpose(s):
                return (s.translate((-fx,-91,-22.5))
                    .rotate((0,0,0),(1,0,0),90+p['fan_exhaust_elevation_deg'])
                    .translate((fx,p['fan_center_y'],p['fan_center_z'])))
            axial=box(x-4.2,139.8,front-.2,8.4,4.8,1.0)
            top=box(x-4.2,150.0,7,8.4,2.2,5)
            return [fanpose(axial),fanpose(top)],'fan top/axial leaf contact tips'
    return [],''


def run(cache,output):
    cache=cache.resolve()
    manifest_path=cache/'parts.json'
    manifest_bytes=manifest_path.read_bytes()
    metadata=json.loads(manifest_bytes)
    cache_hashes={'parts.json':hashlib.sha256(manifest_bytes).hexdigest()}
    if isinstance(metadata,dict):metadata=metadata['parts']
    params_path=R/'parameters.json';contact_path=R/'contact-profiles.json';ports_path=R/'port-study.json'
    input_bytes={path.name:path.read_bytes() for path in [params_path,contact_path,ports_path,Path(__file__)]}
    source_hashes={name:hashlib.sha256(raw).hexdigest() for name,raw in input_bytes.items()}
    p=json.loads(input_bytes[params_path.name]);contacts=json.loads(input_bytes[contact_path.name])
    port_study=json.loads(input_bytes[ports_path.name])
    snapshot=tempfile.TemporaryDirectory(prefix='d8-validation-')
    snapshot_root=Path(snapshot.name)
    parts=[];part_results=[]
    seen=set()
    for row in metadata:
        name=row['name']
        if name in seen:raise ValueError(f'Duplicate cached part: {name}')
        seen.add(name)
        path=cache/(row.get('brep') or name+'.brep')
        raw=path.read_bytes()
        cache_hashes[path.name]=hashlib.sha256(raw).hexdigest()
        snapshot_path=snapshot_root/path.name
        snapshot_path.write_bytes(raw)
        shape=cq.importers.importBrep(str(snapshot_path)).val()
        bb=bounds(shape)
        parts.append(dict(row,shape=shape,bounds=bb))
        part_results.append(dict(name=name,reference=bool(row['reference']),
            valid=bool(shape.isValid()),solids=len(shape.Solids()),volume_mm3=shape.Volume()))
    snapshot.cleanup()
    print(f'Loaded {len(parts)} exact cached D8 parts',flush=True)
    errors=[];hits=[];intended=[]
    rigid=[a for a in parts if (not a['reference'] or is_physical_reference(a['name']))
           and not is_soft(a['name']) and a['name']!='Precision_5680_REFERENCE'
           and not a['name'].startswith('RUBBER_FOOT_')]
    def intersection(a,b,abb=None,bbb=None,label=None):
        abb=bounds(a) if abb is None else abb
        bbb=bounds(b) if bbb is None else bbb
        if not boxes_overlap(abb,bbb):return None,0.
        try:
            inter=a.intersect(b)
            return inter,float(inter.Volume())
        except Exception as exc:
            row=dict(check=label,error=repr(exc))
            errors.append(row);print('BOOLEAN ERROR',json.dumps(row),flush=True)
            return None,0.
    pair_count=0;ref_ref_omitted=0
    for a,b in itertools.combinations(rigid,2):
        if a['reference'] and b['reference']:
            ref_ref_omitted+=1;continue
        pair_count+=1
        inter,v=intersection(a['shape'],b['shape'],a['bounds'],b['bounds'],[a['name'],b['name']])
        if v<=VOLUME_TOLERANCE_MM3:continue
        regions,reason=contact_regions(a,b,p)
        outside=v
        if regions:
            # Complete subtraction can return a null OCC shape. Common volume
            # gives the same containment check without treating empty material
            # as a kernel error. These named contact regions are disjoint.
            try:
                allowed=cq.Compound.makeCompound(regions)
                covered=float(inter.intersect(allowed).Volume())
                outside=max(0.,v-covered)
            except Exception as exc:
                errors.append(dict(check=['contact containment',a['name'],b['name']],error=repr(exc)))
        row=dict(a=a['name'],b=b['name'],volume_mm3=v,bounds_mm=bounds(inter))
        if regions and outside<=VOLUME_TOLERANCE_MM3:
            row.update(reason=reason,outside_allowed_regions_mm3=outside)
            intended.append(row)
        else:
            if regions:row.update(candidate_contact=reason,outside_allowed_regions_mm3=outside)
            hits.append(row);print('COLLISION',json.dumps(row),flush=True)
    H=p['rear_case_seat_z'];lean=math.radians(p['laptop_lean_deg'])
    def leaned(s):return s.rotate((0,0,H),(1,0,H),-p['laptop_lean_deg'])
    laptop=next(a for a in parts if a['name']=='Precision_5680_REFERENCE')
    # Include the compliant stop tip in laptop/foot clearance checks; other
    # compliant contact liners and seals remain outside this rigid path screen.
    static=rigid+[a for a in parts if a['name']=='stop_soft_tip']
    feet=[]
    expansion=float(contacts.get('keepout_expansion_mm',2.0))
    for foot in contacts['rubber_feet']:
        lo,hi=foot['untilted_case_relative_bounds_mm'];e=expansion
        s=leaned(box(lo[0]-e,lo[1]-e,H+lo[2]-e,
                     hi[0]-lo[0]+2*e,hi[1]-lo[1]+2*e,hi[2]-lo[2]+2*e))
        feet.append(dict(name=foot['name'],shape=s,bounds=bounds(s)))
    withdrawal=float(p.get('docking_withdrawal_mm',18))
    lift=float(p.get('animation_lift_mm',135))
    poses=[(withdrawal,z) for z in [lift,80,30,24,10,0]]+[(x,0) for x in [15,10,6,4,2,0]]
    motion=[]
    for x,z in poses:
        shift=(x,math.sin(lean)*z,math.cos(lean)*z)
        moved=laptop['shape'].translate(shift);mb=bounds(moved)
        collisions=[];foot_hits=[]
        for a in static:
            inter,v=intersection(moved,a['shape'],mb,a['bounds'],['laptop',x,z,a['name']])
            if v>VOLUME_TOLERANCE_MM3:
                row=dict(part=a['name'],volume_mm3=v,bounds_mm=bounds(inter))
                collisions.append(row);print('DOCKING COLLISION',json.dumps(dict(offset_xz_mm=[x,z],**row)),flush=True)
        for foot in feet:
            moved_foot=foot['shape'].translate(shift);fb=bounds(moved_foot)
            for a in static:
                inter,v=intersection(moved_foot,a['shape'],fb,a['bounds'],['expanded foot',foot['name'],x,z,a['name']])
                if v>VOLUME_TOLERANCE_MM3:
                    row=dict(foot=foot['name'],part=a['name'],volume_mm3=v,bounds_mm=bounds(inter))
                    foot_hits.append(row);print('FOOT KEEPOUT COLLISION',json.dumps(dict(offset_xz_mm=[x,z],**row)),flush=True)
        motion.append(dict(offset_xz_mm=[x,z],assembly_translation_mm=list(shift),
                           collisions=collisions,expanded_foot_keepout_collisions=foot_hits))

    def sample_service_motion(moving, fixed, poses, label):
        samples=[]
        for position, shift in poses:
            collisions=[]
            for a in moving:
                moved=a['shape'].translate(shift);mb=bounds(moved)
                for b in fixed:
                    inter,v=intersection(moved,b['shape'],mb,b['bounds'],
                                         [label,position,a['name'],b['name']])
                    if v>VOLUME_TOLERANCE_MM3:
                        row=dict(moving_part=a['name'],fixed_part=b['name'],
                                 volume_mm3=v,bounds_mm=bounds(inter))
                        collisions.append(row)
                        print('SERVICE COLLISION',json.dumps(dict(
                            service=label,position_mm=position,**row)),flush=True)
            samples.append(dict(position_mm=position,assembly_translation_mm=list(shift),
                                collisions=collisions))
        return samples

    # The complete plug module leaves together, with the laptop unloaded and
    # only its two shell-mount locks removed. Its internal locks, spring, cap,
    # stop, reference overmold and USB shell all move with it.
    def on_module(name):
        return name.startswith(('breakaway_','cassette_','chassis_stop_')) or name in {
            'connector_module_body','X_depth_overmold_clamp','sliding_plug_cap',
            'Dell_plug_overmold_REFERENCE','USB_C_shell_REFERENCE',
            'independent_printed_chassis_stop_screw','stop_soft_tip'}
    module=[a for a in static if on_module(a['name'])]
    module_names={a['name'] for a in module}
    removed_locks=[a['name'] for a in static if a['name'].startswith('connector_mount_lock_')]
    fixed=[a for a in static if a['name'] not in module_names and a['name'] not in removed_locks]
    module_positions=[(0,0),(0,1),(0,4.3),(-5,4.3),(-15,4.3),(-35,4.3),(-70,4.3)]
    module_poses=[(dict(local_x=x,local_y=-y),(x,-math.cos(lean)*y,math.sin(lean)*y))
                  for x,y in module_positions]
    module_samples=sample_service_motion(module,fixed,module_poses,'connector_module_removal')
    panel_checks=[]
    for panel in [a for a in static if a['name'].endswith('_bottom_panel')]:
        prefix=panel['name'][:2]
        removed=[a['name'] for a in static if a['name'].startswith(prefix+'_bottom_thumb_lock_')]
        fixed=[a for a in static if a['name']!=panel['name'] and a['name'] not in removed]
        poses=[(dict(global_z=-z),(0,0,-z)) for z in [0,1,4,10,35]]
        samples=sample_service_motion([panel],fixed,poses,panel['name']+'_removal')
        panel_checks.append(dict(panel=panel['name'],removed_locks=removed,samples=samples))
    service_passed=all(not r['collisions'] for r in module_samples) and all(
        not r['collisions'] for panel in panel_checks for r in panel['samples'])
    probes=[]
    for port in port_study['ports']:
        left=port['side']=='keyboard-left';z=H+port['case_offset_from_rear_mm'];y=port['case_y_mm']
        x=.2 if left else p['laptop_width']-1
        other=p['laptop_width']-1 if left else .2
        probe=leaned(box(x,y-.5,z-.5,.8,1,1));opposite=leaned(box(other,y-.5,z-.5,.8,1,1))
        _,v=intersection(laptop['shape'],probe,label=['port opening',port['name']])
        _,ov=intersection(laptop['shape'],opposite,label=['opposite port edge',port['name']])
        source_handed=(port['source_center_mm'][0]<0)==left
        probes.append(dict(name=port['name'],side=port['side'],source_handedness_preserved=source_handed,
                           opening_material_mm3=v,opposite_edge_material_mm3=ov,
                           passed=bool(source_handed and v<1e-6 and ov>.79)))
    plug=next(a for a in parts if a['name']=='USB_C_shell_REFERENCE')
    plug_side=plug['bounds'][0]<0 and 0<plug['bounds'][3]<7
    fan_side=all(a['shape'].Center().y>p['laptop_thickness']/2 for a in parts if 'fan_frame' in a['name'])
    passed=not (hits or errors) and all(r['valid'] and r['solids']==1 and r['volume_mm3']>0 for r in part_results)
    passed=bool(passed and all(not r['collisions'] and not r['expanded_foot_keepout_collisions'] for r in motion)
                and service_passed and all(r['passed'] for r in probes) and plug_side and fan_side)
    data=dict(passed=passed,scope='Exact cached nominal CAD and the finite listed docking/withdrawal and unloaded service-removal poses. No continuous sweep, complete adjustment envelope, manufacturing fit, loading, physical fan/plug qualification, cable flex, cooling or toolpath claim. STEP is not reopened by this check.',
        parameters_tested=dict(height_adjustment_mm=p.get('height_adjustment',0),
             lateral_adjustment_mm=p.get('lateral_adjustment',0),stop_adjustment_x_mm=p.get('stop_adjustment_x_mm',0),
             fan_thickness_mm=p['fan_thickness'],fan_fit=p.get('fan_fit',{})),
        cache_part_count=len(parts),cache_part_validity=part_results,rigid_pair_count=pair_count,
        omitted_reference_reference_pair_count=ref_ref_omitted,
        excluded_soft_parts=[a['name'] for a in parts if is_soft(a['name'])],
        nominal_rigid_collisions=hits,intentional_compliant_contacts=intended,
        docking_path_samples=motion,foot_keepout_expansion_mm=expansion,
        service_removal=dict(laptop='unloaded/removed',
            scope='Finite listed translations only; attached cable flex and extraction of the threaded locks are not modeled.',
            connector_module=dict(moving_parts=sorted(module_names),removed_locks=removed_locks,
                path='Local -Y by 4.3 mm, then local -X',samples=module_samples),
            bottom_panels=panel_checks,passed=service_passed),
        orientation=dict(docking_direction='-X',plug_x_bounds_mm=[plug['bounds'][0],plug['bounds'][3]],
                         plug_at_source_keyboard_left=plug_side,fans_on_lid_side=fan_side,port_probes=probes),
        geometry_errors=errors,numerical_intersection_threshold_mm3=VOLUME_TOLERANCE_MM3,
        provenance=dict(cache_directory=str(cache),input_sha256=source_hashes,cache_sha256=cache_hashes,
             note='Hashes identify the exact BReps and parameter/source-reference bytes checked. This cache does not itself certify that current CAD source regenerated those BReps.'))
    output.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(passed=passed,parts=len(parts),rigid_collisions=len(hits),
                         intentional_contacts=len(intended),docking_samples=len(motion),
                         service_removal_passed=service_passed,
                         boolean_errors=len(errors),report=str(output))),flush=True)
    return 0 if passed else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=R/'validation.json')
    args=parser.parse_args()
    raise SystemExit(run(args.cache,args.output))
