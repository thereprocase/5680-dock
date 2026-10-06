"""Serviceable plenum floors and joining keys with fully printed coarse locks.

All screw/nut interfaces use custom diameter8, 2 mm pitch threads and >=6 mm
cores. Female threads are integral with substantial shell bosses; no metal
hardware or undersized printed pin is present in this module.
"""
import cadquery as cq
from cable_service import add_cable_routing
from printed_fasteners import make_screw,make_threaded_hole,THREAD_SPEC


def body_service(bodies,W,front_y,box,rb,hole,add):
    metadata=[];hand=(86,115,108)
    def down(shape,x,y,z):
        return shape.rotate((0,0,0),(1,0,0),180).translate((x,y,z))
    for i,(x0,x1,body) in enumerate(bodies,1):
        front=front_y(5.4)-6
        opening=rb(x0+6,-18,2.9,x1-x0-12,front+18,3.2,3)
        body=body.cut(opening.val())
        plate=rb(x0+2.6,-21.4,.5,x1-x0-5.2,front_y(3)-2.6+21.4,2.3,3)
        tongue=rb(x0+6.35,-17.65,2.8,x1-x0-12.7,front+17.3,2.2,2.65)
        plate=plate.union(tongue)
        # Diameter31 access recesses give the diameter18 hand heads room to turn.
        # The head bears on the cover at z8.8; the female boss starts at z11.2.
        # A 14 mm screw therefore has 11.6 mm nominal engagement.
        for j,x in enumerate([x0+22,x1-22],1):
            y=0
            boss=rb(x-20,y-20,3,40,40,20,3)
            body=body.fuse(boss.val()).clean()
            body=body.cut(hole((0,0,1),(x,y,2.9),17.4,8.3)).clean()
            cutter=make_threaded_hole(12.1,phase_z=8.8-11.1).translate((x,y,11.1))
            body=body.cut(cutter.val()).clean()
            plate=plate.cut(hole((0,0,1),(x,y,.3),15.5,5))
            flange=cq.Workplane('XY',origin=(x,y,8.8)).circle(17.1).circle(4.5).extrude(2.4)
            neck=cq.Workplane('XY',origin=(x,y,2.7)).circle(17.1).circle(15.5).extrude(6.2)
            plate=plate.union(neck).union(flange)
            screw=make_screw(14,head_diameter=18,head_height=5).translate((x,y,8.8))
            add(f'{i:02}_bottom_thumb_lock_{j}',screw,hand,False)
        body=body.cut(opening.val()).clean()
        body,plate,cable=add_cable_routing(i,x0,x1,body,plate,box,rb,hole)
        add(f'{i:02}_bottom_panel',plate,(56,65,69),False)
        bodies[i-1]=(x0,x1,body)
        metadata.append(dict(module=i,panel_clearance_per_side_mm=.35,panel_removal_direction=[0,0,-1],
            fastener=dict(THREAD_SPEC),bottom_screw_under_head_length_mm=14,
            bottom_nominal_thread_engagement_mm=11.6,hand_access_diameter_mm=31,
            female_threads='Integral shell bosses; fully printed',
            gasket='0.2 mm self-adhesive closed-cell perimeter tape, compressed at the flange; terminate beside the cable saddle',cable_routing=cable))
    # Two low bridge keys join the independently sealed shells. Wide printed
    # locks engage integral bosses from above; no trapped nuts remain.
    mid=W/2+.15
    for j,y in enumerate([23,45],1):
        bridge=rb(mid-20,y-9,50,40,18,4,2)
        for k,x in enumerate([mid-10,mid+10]):
            x0,x1,body=bodies[k]
            boss=rb(x-9,y-9,36,18,18,14,2)
            body=body.fuse(boss.val()).clean()
            cutter=make_threaded_hole(14.3,phase_z=50.1-54)
            body=body.cut(down(cutter,x,y,50.1).val()).clean()
            bridge=bridge.cut(hole((0,0,1),(x,y,49.9),4.5,4.2))
            bodies[k]=(x0,x1,body)
            screw=down(make_screw(14,head_diameter=18,head_height=5),x,y,54)
            add(f'{k+1:02}_bridge_thumb_lock_{j}',screw,hand,False)
        add(f'bridge_key_{j}',bridge,(70,83,86),False)
    for i,(x0,x1,body) in enumerate(bodies,1):
        add(f'{i:02}_manifold_with_cradle',body)
    return metadata
