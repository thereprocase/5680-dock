"""Printed D7 cassette; only original Dell plug and USB shell are references."""
import cadquery as cq
from printed_fasteners import make_screw, make_threaded_hole


def rear_cable_spec(p):
    """Provisional free cable continuation; only the source stub is dimensioned."""
    return {
        'source_stub_diameter_mm':6.5,
        'provisional_continuation_diameter_mm':6.5,
        'clearance_check_diameter_mm':8.0,
        'trough_diameter_mm':8.5,
        'fixed_carrier_window_width_mm':14.5,
        'fixed_carrier_window_lowest_relative_to_nominal_port_mm':-8.25,
        'window_basis':'Full Y/Z adjustment envelope; moving cradle retains the 8.5 mm rounded cable trough. Inspect real cable contact at the fixed window edge.',
        'exit_axis':[-1,0,0],
        'lay_in_direction':[0,0,-1],
        'rear_wall_outer_x_mm':-47,
        'free_straight_after_wall_mm':30,
        'illustrative_bend_radius_mm':30,
        'qualification':'Continuation diameter and bend radius are assumptions, not measured Dell cable properties. Reserve a loose exterior loop; no fixed clamp or rigid elbow near the moving outlet.'}


def make_rear_cable_keepout(p,radius=4.0):
    """Moving free-loop screening volume; not a manufactured cable model."""
    P=p['rear_case_seat_z']+p['port_from_rear_case']
    cx=-26.5+p['depth_adjustment']
    cy=p['port_y']+p['lateral_adjustment'];cz=P+p['height_adjustment']
    path=(cq.Workplane('XZ',origin=(0,cy,0)).moveTo(cx,cz)
          .lineTo(-77,cz).threePointArc((-98.2132034356,cz-8.7867965644),(-107,cz-30))
          .lineTo(-107,cz-60).wire())
    return cq.Workplane('YZ',origin=(cx,cy,cz)).circle(radius).sweep(path,isFrenet=True)


def build_cassette(p, box, rb, hole, add):
    from breakaway_geometry import make_fixed_support, make_carrier, add_hinge_hardware
    H=p['rear_case_seat_z']; P=H+p['port_from_rear_case']; Y=p['port_y']
    dz=p['height_adjustment']; dy=p['lateral_adjustment']; dx=0.0
    if not -4 <= dz <= 5 or not -3 <= dy <= 3:
        raise ValueError('Live connector travel is Z=-4..5 and Y=-3..3 mm')
    cx=-26.5+dx; cy=Y+dy; cz=P+dz
    polymer=(74,82,86); hand=(123,150,132); soft=(56,80,75)
    bx=-16+dx; by=-1+dy
    top_y=8.5+dy

    def positive_y(shape,x,y,z):
        return shape.rotate((0,0,0),(1,0,0),-90).translate((x,y,z))

    def positive_x(shape,x,y,z):
        return shape.rotate((0,0,0),(0,1,0),90).translate((x,y,z))

    # A fixed rear thrust wall guides a real Z saddle. The opening clears that
    # saddle, its underside gussets and hand controls throughout the live travel.
    carrier=make_carrier(p).union(box(-47,-28,P-34,7,53.8,8.1))
    carrier=carrier.cut(box(-40,-20.3,P-34.1,40.2,38.1,15.5))
    carrier=carrier.union(box(-40,-23,P-34,6,2.7,38))
    carrier=carrier.union(box(-40,17.8,P-34,6,3.2,38))
    cable_radius=4.25
    # Open upward so the cable is laid in, never threaded through the wall.
    cable_bottom=hole((1,0,0),(-49,cy,cz),cable_radius,cx+4.95+49)
    cable_open=box(-49,cy-cable_radius,cz,cx+4.95+49,2*cable_radius,35)
    cable_trough=cq.Workplane(obj=cable_bottom).union(cable_open)
    # Flare the outer 2 mm of the rear wall; the cable sees a broad mouth.
    flare=cq.Solid.makeCone(6.25,4.25,2,cq.Vector(-47,cy,cz),cq.Vector(1,0,0))
    flare_open=(cq.Workplane('XY',origin=(0,0,cz))
        .polyline([(-47.1,cy-6.25),(-45,cy-4.25),(-45,cy+4.25),(-47.1,cy+6.25)])
        .close().extrude(35))
    # Fixed parts clear the ENTIRE Y/Z adjustment rectangle, without reprinting.
    all_cable=box(-49,Y-7.25,P-8.25,28,14.5,44)
    carrier=carrier.cut(all_cable)
    for yy in [-13,9.5]:
        cutter=(cq.Workplane('YZ',origin=(-47.1,0,0)).center(yy,P-14.5)
            .slot2D(17.7,8.7,90).extrude(7.2))
        carrier=carrier.cut(cutter)
    add('breakaway_carrier',carrier,polymer)
    add_hinge_hardware(p,add)
    # Parallel Z guides and two vertical slots prevent rotation. Thrust acts
    # normal to the broad rear land, instead of relying on slot-clamp friction.
    # The rear clevis reinforcement reaches cz-3.4; leave 0.2 mm below it.
    saddle=box(-40,-20,P-29+dz,8,37.5,25.4)
    saddle=saddle.union(box(-34,-20,cz-17.6,33.6,37.5,4))
    saddle=saddle.union(box(-34,-20,cz-13.6,5,37.5,7.2))
    saddle=saddle.union(box(-2.8,-20,cz-13.6,2.4,37.5,7.2))
    for yy in [-20,13.5]:
        gusset=(cq.Workplane('XZ',origin=(0,yy,0))
            .polyline([(-34,cz-27.6),(-34,cz-17.5),(-.4,cz-17.5)])
            .close().extrude(-4))
        saddle=saddle.union(gusset)
    for j,yy in enumerate([-13,9.5]):
        threaded=make_threaded_hole(8,phase_z=-7).rotate(
            (0,0,0),(0,1,0),90).translate((-40,yy,cz-15))
        saddle=saddle.cut(threaded)
        lock=make_screw(14.5,head_diameter=14,head_height=4).rotate(
            (0,0,0),(0,1,0),90).translate((-47,yy,cz-15))
        add(f'cassette_Z_lock_{j}',lock,hand)
    saddle=saddle.cut(box(-41,Y-7.25,cz-4.25,13,14.5,30))
    # A Y slot lets the cable cradle translate across the laptop thickness.
    # Front and rear shoulders positively retain X position in both directions.
    for j,xx in enumerate([-15.25]):
        slot=(cq.Workplane('XY',origin=(0,0,cz-17.7)).center(xx,-1)
            .slot2D(14.7,8.7,90).extrude(4.2))
        saddle=saddle.cut(slot)
        lock=make_screw(10.5,head_diameter=18,head_height=4).translate((xx,-1+dy,cz-17.6))
        add(f'cassette_Y_lock_{j}',lock,hand)
    add('cassette_Z_saddle',saddle,hand)

    rear_x=-29
    clamp=rb(rear_x,-15+dy,cz-13.6,-2.8-rear_x,29,7.2,1.5)
    # Rear shoulder opposes insertion and leaves the cable stub clear.
    clamp=clamp.union(box(cx+1.1,cy-3.6,cz-6.4,3.8,7.2,13.0).cut(
        hole((1,0,0),(cx+.9,cy,cz),3.45,4.2)))
    for yy,ww in [(cy-15,11.55),(cy+3.45,top_y-(cy+3.45))]:
        clamp=clamp.union(box(cx-2,yy,cz-6.4,28.1,ww,13.0))
    # Cap clevis remains at Y<=11.5, clear of the fixed pivot head at Y=12.
    pin_x=cx-1; pin_z=cz+9
    for yy,ww in [(cy-15,7.9),(cy+1.8,top_y-(cy+1.8))]:
        lug=box(cx-6.5,yy,cz+3.6,11,ww,11)
        lug=lug.union(box(cx-6.5,yy,cz-3.4,7.6,ww,8))
        clamp=clamp.union(lug)
    clamp=clamp.cut(box(cx-6.6,cy-7.1,cz+3.6,11.2,8.9,12))
    pin_bore=hole((0,1,0),(pin_x,cy-15.2,pin_z),3.4,top_y-cy+15.5)
    clamp=clamp.cut(pin_bore)
    clamp=clamp.cut(cable_trough)
    threaded=make_threaded_hole(7.2,phase_z=-4,lead_in=.4)
    for xx in [-15.25]:
        clamp=clamp.cut(threaded.translate((xx,-1+dy,cz-13.6)))

    # Bring the broad outer cap face level with the clevis top. Inverting the
    # cap now gives a broad bed contact, eliminating the former 2.5 mm ledge.
    cap=rb(cx+4.8,cy-15,cz+8.4,21.3,top_y-(cy-15),5.5,1.5)
    cap=cap.union(box(cx-6.5,cy-6.75,cz+3.8,11,8.2,10.1))
    cap=cap.union(box(cx+4.3,cy-6.75,cz+8.4,2,8.2,5.5)).cut(pin_bore)
    # The upper half of the insertion shoulder travels with the removable cap.
    cap=cap.union(box(cx+1.1,cy-3.6,cz+3.8,3.8,7.2,2.8))
    cap=cap.cut(cable_bottom).cut(pin_bore)
    squeeze=float(p.get('overmold_grip_squeeze_mm',.30))
    if not 0 <= squeeze <= .6:
        raise ValueError('Overmold squeeze must be calibrated within0..0.6 mm')
    # Deliberate squeeze allowance against the actual elastomer overmold.
    # It is a fit parameter, not a claimed extraction-retention force.
    cap=cap.union(box(cx+6,cy-2.9,cz+6.25-squeeze,18,5.8,2.4+squeeze))
    nose=box(-.4,-50,cz-30,30,100,70)
    clamp=clamp.cut(nose);cap=cap.cut(nose)
    add('X_depth_overmold_clamp',clamp,polymer)
    add('sliding_plug_cap',cap,polymer)

    pin_start=cy-15; pin_length=top_y-pin_start
    pin=cq.Workplane('XY').circle(3.25).extrude(pin_length)
    pin=pin.union(cq.Workplane('XY',origin=(0,0,-4)).circle(7).extrude(4))
    for zz in [pin_length-1.3,pin_length-2.5]:
        rib=cq.Workplane('XZ').moveTo(3.15,zz-.4).threePointArc((3.45,zz),(3.15,zz+.4)).close().revolve(360,(0,0),(0,1))
        pin=pin.union(rib)
    add('cassette_cap_push_pin_6p5',positive_y(pin,pin_x,pin_start,pin_z),hand)

    # Original reference dimensions and transformations are unchanged.
    overmold=box(cx+5,cy-3.25,cz-6.25,20,6.5,12.5).edges('|X').fillet(1.5)
    overmold=overmold.union(hole((1,0,0),(cx,cy,cz),3.25,5.1))
    add('Dell_plug_overmold_REFERENCE',overmold,(36,38,40),True)
    tip=box(cx+25,cy-1.2,cz-4.125,6.65,2.4,8.25).edges('|X').fillet(1.15)
    add('USB_C_shell_REFERENCE',tip,(191,197,200),True)

    # Independent fixed case stop bridges directly to support at Y=26..35.
    stop=rb(-17,-9,H+1,12,44,20,2)
    stop_hole=make_threaded_hole(12,diameter=10,phase_z=-5)
    stop=stop.cut(positive_x(stop_hole,-17,0,H+11))
    from connector_mount import detachable_support,attach_stop
    support,mount_metadata=detachable_support(p,make_fixed_support(p),box,hole,add)
    support=attach_stop(p,support,stop,box,hole,add)
    add('connector_module_body',support,polymer)
    stop_screw=make_screw(18,diameter=10,head_diameter=24,head_height=6,tip_chamfer=0)
    stop_screw=stop_screw.union(cq.Workplane('XY',origin=(0,0,17.8)).circle(4).extrude(3.2))
    stop_dx=float(p.get('stop_adjustment_x_mm',0))
    if not -4 <= stop_dx <= 4:
        raise ValueError('Independent chassis stop travel is -4..+4 mm')
    stop_screw=stop_screw.rotate((0,0,0),(0,0,1),180*stop_dx)
    add('independent_printed_chassis_stop_screw',positive_x(stop_screw,-22+stop_dx,0,H+11),hand)
    bumper=cq.Workplane('XY').circle(6).extrude(4)
    bumper=bumper.cut(cq.Workplane('XY',origin=(0,0,-.1)).circle(4.1).extrude(3.1))
    add('stop_soft_tip',positive_x(bumper,-4+stop_dx,0,H+11),soft)
    return {
        'threads':'Custom printed8x2 calibration lock and10x2 chassis stop; real matched trapezoids, not ISO',
        'fasteners':'Three8mm live adjustment locks, two8mm module locks,6.5mm cap pin and existing printed hinge hardware',
        'cap_release_direction':'Pull6.5mm pin toward -Y then lift cap; no front clip',
        'height_adjustment':'Loosen two Z locks; slide saddle continuously -4..+5 mm; tighten. No replacement shim.',
        'depth_adjustment':'Plug X is fixed by front/rear saddle shoulders; independent chassis stop adjusts along X.',
        'lateral_adjustment':'Loosen Y lock beneath cradle; slide continuously -3..+3 mm; tighten.',
        'axis_frame':'Y and Z follow laptop thickness/height and rotate together through the5degree lean. X remains insertion axis.',
        'module_mount':mount_metadata,
        'stop_adjustment_x_mm':stop_dx,
        'stop_adjustment_range_mm':[-4,4],
        'overmold_grip_squeeze_mm':squeeze,
        'extraction_retention':'Overmold friction requires physical pull testing; squeeze is provisional',
        'moving_top_positive_y_limit_mm':top_y,
        'soft_stop':'Removable flexible printed bumper,8.2mm socket over8mm stem; fit test required',
        'material_target':'PETG,0.4mm nozzle,P1S; pin/thread/grip coupons required',
        'rear_cable':rear_cable_spec(p),
    }
