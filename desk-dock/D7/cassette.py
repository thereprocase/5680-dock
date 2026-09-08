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
        'mouth_flare_diameter_mm':12.5,
        'mouth_flare_length_mm':2.0,
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
    dz=p['height_adjustment']; dy=p['lateral_adjustment']; dx=p['depth_adjustment']
    cx=-26.5+dx; cy=Y+dy; cz=P+dz
    polymer=(74,82,86); hand=(123,150,132); soft=(56,80,75)
    bx=-16+dx; by=-1+dy

    def positive_y(shape,x,y,z):
        return shape.rotate((0,0,0),(1,0,0),-90).translate((x,y,z))

    def positive_x(shape,x,y,z):
        return shape.rotate((0,0,0),(0,1,0),90).translate((x,y,z))

    # Broad keyed window carries insertion shear, clear of the Y=18 side web.
    # A large lower keeper plate prevents the screw pulling through the window.
    carrier=make_carrier(p).cut(rb(-28,-11,P-26.1,24,20,7.6,2))
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
    carrier=carrier.cut(cable_trough).cut(flare).cut(flare_open)
    add('plug_support',make_fixed_support(p))
    add('breakaway_carrier',carrier,polymer)
    add_hinge_hardware(p,add)

    shim_height=5.1+dz
    if shim_height < 1:
        raise ValueError('Height calibration leaves less than1 mm of printable shim')
    shim=rb(-39,-20,P-18.7,38.4,37.5,shim_height,2)
    shim=shim.union(rb(-27.65,-10.65,P-23,23.3,19.3,4.4,1.65))
    # Replaceable shim encodes measured depth, height and lateral correction.
    rear_x=-29+dx
    shim=shim.union(box(-39,-20,P-18.7,rear_x+39,37.5,12.3+dz))
    shim=shim.union(box(rear_x,-20,P-18.7,-.6-rear_x,5+dy,12.3+dz))
    shim=shim.cut(hole((0,0,1),(bx,by,P-24),4.35,24))
    add('height_shim_pack',shim,hand)

    keeper=rb(-34.5,-17,P-31,34,32,5,2)
    keeper=keeper.cut(hole((0,0,1),(bx,by,P-31.1),4.35,5.3))
    add('cassette_calibration_keeper_plate',keeper,polymer)

    clamp=rb(rear_x,-15+dy,cz-13.6,-.4-rear_x,29,7.2,1.5)
    # Rear shoulder opposes insertion and leaves the cable stub clear.
    clamp=clamp.union(box(cx+1.1,cy-3.6,cz-6.4,3.8,7.2,13.0).cut(
        hole((1,0,0),(cx+.9,cy,cz),3.45,4.2)))
    for yy,ww in [(cy-15,11.55),(cy+3.45,11.5-(cy+3.45))]:
        clamp=clamp.union(box(cx-2,yy,cz-6.4,28.1,ww,13.0))
    # Cap clevis remains at Y<=11.5, clear of the fixed pivot head at Y=12.
    pin_x=cx-1; pin_z=cz+9
    for yy,ww in [(cy-15,7.9),(cy+1.8,11.5-(cy+1.8))]:
        lug=box(cx-6.5,yy,cz+3.6,11,ww,11)
        lug=lug.union(box(cx-6.5,yy,cz-3.4,7.6,ww,8))
        clamp=clamp.union(lug)
    clamp=clamp.cut(box(cx-6.6,cy-7.1,cz+3.6,11.2,8.9,12))
    pin_bore=hole((0,1,0),(pin_x,cy-15.2,pin_z),3.4,27-cy)
    clamp=clamp.cut(pin_bore)
    clamp=clamp.cut(cable_trough)
    threaded=make_threaded_hole(7.2,phase_z=(P-31)-(cz-13.6),lead_in=.4)
    clamp=clamp.cut(threaded.translate((bx,by,cz-13.6)))
    screw=make_screw(23.9+dz,head_diameter=20,head_height=5)
    add('cassette_calibration_hand_screw',screw.translate((bx,by,P-31)),hand)

    cap=rb(cx+4.8,cy-15,cz+8.4,21.3,11.5-(cy-15),3,1.5)
    cap=cap.union(box(cx-6.5,cy-6.75,cz+3.8,11,8.2,10.1))
    cap=cap.union(box(cx+4.3,cy-6.75,cz+8.4,2,8.2,3)).cut(pin_bore)
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

    pin_start=cy-15; pin_length=11.5-pin_start
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
    add('chassis_stop_block',stop,polymer)
    stop_screw=make_screw(18,diameter=10,head_diameter=24,head_height=6,tip_chamfer=0)
    stop_screw=stop_screw.union(cq.Workplane('XY',origin=(0,0,17.8)).circle(4).extrude(3.2))
    add('independent_printed_chassis_stop_screw',positive_x(stop_screw,-22,0,H+11),hand)
    bumper=cq.Workplane('XY').circle(6).extrude(4)
    bumper=bumper.cut(cq.Workplane('XY',origin=(0,0,-.1)).circle(4.1).extrude(3.1))
    add('stop_soft_tip',positive_x(bumper,-4,0,H+11),soft)
    return {
        'threads':'Custom printed8x2 calibration lock and10x2 chassis stop; real matched trapezoids, not ISO',
        'fasteners':'One8mm calibration screw, keeper plate,6.5mm cap push pin, printed hinge hardware',
        'cap_release_direction':'Pull6.5mm pin toward -Y then lift cap; no front clip',
        'height_adjustment':'Replace keyed shim; thickness5.1+dz, minimum1.1mm',
        'depth_adjustment':'Rear abutment encoded in replaceable keyed shim',
        'lateral_adjustment':'Side abutment and bolt bore encoded in replaceable keyed shim',
        'overmold_grip_squeeze_mm':squeeze,
        'extraction_retention':'Overmold friction requires physical pull testing; squeeze is provisional',
        'moving_top_positive_y_limit_mm':11.5,
        'soft_stop':'Removable flexible printed bumper,8.2mm socket over8mm stem; fit test required',
        'material_target':'PETG,0.4mm nozzle,P1S; pin/thread/grip coupons required',
        'rear_cable':rear_cable_spec(p),
    }
