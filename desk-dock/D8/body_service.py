"""D8 shell-supported feet and light downward-removable duct lids."""
import cadquery as cq
from cable_service import add_cable_routing
from body_print_geometry import lower_perimeter
from printed_fasteners import make_screw,make_threaded_hole,THREAD_SPEC

def body_service(bodies,W,front_y,box,rb,hole,add):
    metadata=[];hand=(86,115,108)
    def down(shape,x,y,z):
        return shape.rotate((0,0,0),(1,0,0),180).translate((x,y,z))
    for i,(x0,x1,body) in enumerate(bodies,1):
        front=front_y(5.4)-6
        opening=rb(x0+6,-18,2.9,x1-x0-12,front+18,3.2,3)
        body=body.cut(opening.val()).clean()
        # Broad flat 2 mm skin. A perimeter ring replaces the full-area tongue.
        plate=rb(x0+2.6,-21.4,.5,x1-x0-5.2,front_y(3)+18.8,2.0,3)
        tongue=rb(x0+6.35,-17.65,2.5,x1-x0-12.7,front+17.3,2.2,2.65)
        inner=rb(x0+8.75,-15.25,2.4,x1-x0-17.5,front+12.5,2.5,1)
        plate=plate.union(tongue.cut(inner))
        for fraction in [.25,.5,.75]:
            x=x0+(x1-x0)*fraction
            plate=plate.union(box(x-1.2,-17.65,2.4,2.4,front+17.3,2.3))
        # Annular threaded bosses and endwall webs replace 40x40x20 blocks.
        for j,x in enumerate([x0+16,x1-16],1):
            boss=cq.Workplane('XY',origin=(x,0,2.8)).circle(9).extrude(12)
            web=box(x0+1,-2.4,3,x-x0,4.8,11.8) if j==1 else box(x,-2.4,3,x1-x,4.8,11.8)
            boss=boss.union(web)
            cutter=make_threaded_hole(12.2,phase_z=.5-2.7).translate((x,0,2.7))
            boss=boss.cut(cutter)
            body=body.fuse(boss.val()).cut(cutter.val()).clean()
            plate=plate.cut(hole((0,0,1),(x,0,.3),4.5,5))
            plate=plate.cut(hole((0,0,1),(x,0,2.51),9.35,3))
            # Small breaks in the seating ring clear the endwall gussets.
            relief=box(x0-.1,-2.75,2.51,x-x0+.45,5.5,3) if j==1 else box(x-.35,-2.75,2.51,x1-x+.45,5.5,3)
            plate=plate.cut(relief)
            add(f'{i:02}_bottom_thumb_lock_{j}',make_screw(14,head_diameter=18,head_height=4).translate((x,0,.5)),hand,False)
        foot_positions=[]
        for j,x in enumerate([x0,x1-12],1):
            for k,y in enumerate([-24,front_y(3)-12],1):
                stem=rb(x,y,-2,12,12,10,2)
                body=body.fuse(stem.val()).clean()
                plate=plate.cut(rb(x-.35,y-.35,.3,12.7,12.7,5,2.35))
                add(f'{i:02}_desk_pad_{j}_{k}',rb(x,y,-5,12,12,3,2),(31,34,37),False)
                foot_positions.append([x+6,y+6,-5])
        body=lower_perimeter(body,i,x0,x1,front_y)
        body,plate,cable=add_cable_routing(i,x0,x1,body,plate,box,rb,hole)
        add(f'{i:02}_bottom_panel',plate,(56,65,69),False)
        bodies[i-1]=(x0,x1,body)
        metadata.append(dict(module=i,cover_skin_mm=2.0,flat_print_perimeter_bottom_z_mm=-2,perimeter_rib_mm=2.4,rib_height_mm=2.2,
            panel_clearance_per_side_mm=.35,panel_removal_direction=[0,0,-1],fastener=dict(THREAD_SPEC),
            bottom_screw_under_head_length_mm=14,nominal_thread_engagement_mm=11.7,feet=foot_positions,
            load_path='Laptop seat to shell walls to integral corner stems to desk pads; covers are bypassed.',
            minimum_lock_head_desk_clearance_mm=1.5,
            sealing='No required gasket. Perimeter tongue limits gross bypass; optional tape only if testing warrants it.',
            cable_routing=cable))
    mid=W/2+.15
    for j,y in enumerate([23,45],1):
        bridge=rb(mid-20,y-9,50,40,18,4,2)
        for k,x in enumerate([mid-10,mid+10]):
            x0,x1,body=bodies[k]
            body=body.fuse(rb(x-9,y-9,36,18,18,14,2).val()).clean()
            cutter=make_threaded_hole(14.3,phase_z=50.1-54)
            body=body.cut(down(cutter,x,y,50.1).val()).clean()
            bridge=bridge.cut(hole((0,0,1),(x,y,49.9),4.5,4.2))
            bodies[k]=(x0,x1,body)
            add(f'{k+1:02}_bridge_thumb_lock_{j}',down(make_screw(14,head_diameter=18,head_height=5),x,y,54),hand,False)
        add(f'bridge_key_{j}',bridge,(70,83,86),False)
    for i,(x0,x1,body) in enumerate(bodies,1):add(f'{i:02}_manifold_with_cradle',body)
    return metadata
