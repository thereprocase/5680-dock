"""Unleaned, serviceable D7 connector cassette; metal threads are envelopes.

The caller applies the laptop lean and fuses plug_support/chassis_stop_block
into its plenum. No dependency on build.py, so this module can be checked alone.
"""
import math
import cadquery as cq


def build_cassette(p, box, rb, hole, add):
    H=p['rear_case_seat_z']; P=H+p['port_from_rear_case']; Y=p['port_y']
    dz=p['height_adjustment']; dy=p['lateral_adjustment']; dx=p['depth_adjustment']
    cx=-26.5+dx; cy=Y+dy; cz=P+dz
    metal=(175,181,185); polymer=(74,82,86); soft=(56,80,75)

    def hexz(x,y,z,af,height):
        return cq.Workplane('XY',origin=(x,y,z)).polygon(6,af/math.cos(math.pi/6)).extrude(height)

    def hexx(x,y,z,af,length):
        # Vertices at 30 degrees: 7 mm flats lie parallel to the drop-in slot.
        r=af/math.sqrt(3)
        pts=[(y+r*math.cos(math.radians(30+60*i)),z+r*math.sin(math.radians(30+60*i))) for i in range(6)]
        return cq.Workplane('YZ',origin=(x,0,0)).polyline(pts).close().extrude(length)

    shelf=rb(-40,-18,P-24,39.4,43,5.3,3)
    for yy in [-8,8]:
        shelf=shelf.cut(rb(-20.7,yy-4.7,P-25,13.4,9.4,8,1.7))
    spine=box(-40,18,30,6,7,P-49).union(box(-40,18,26.7,55,7,6.3))
    add('plug_support',shelf.union(spine))

    shim=box(-28.3+dx,-9.8+dy,P-18.7,27.7,19.6,5+dz)
    for yy in [-8+dy,8+dy]:
        shim=shim.cut(hole((0,0,1),(-14+dx,yy,P-20),1.7,24))
    add('height_shim_pack',shim,(123,137,127))

    clamp=rb(cx-2,cy-10,cz-13.4,29,20,5,2)
    clamp=clamp.union(box(cx-2,-12.2+dy,cz-13.7,29,24.4,5.3))
    for yy in [cy-10,cy+5.1]:
        clamp=clamp.union(box(cx-2,yy,cz-8.4,29,4.9,16.8))
    back=box(cx+3.5,cy-5.1,cz-8.4,1.5,10.2,16.8).cut(hole((1,0,0),(cx+3,cy,cz),3.7,3))
    clamp=clamp.union(back)
    # Original thin metal clip stays outside the measured overmold envelope.
    # Its lower toe and side edges enter a downward seating slot in the base.
    front=box(cx+25.3,cy-5.1,cz-8.4,.8,10.2,16.8).cut(box(cx+25,cy-1.8,cz-4.8,4,3.6,9.6))
    clip_toe=box(cx+25.3,cy-4.5,cz-10.3,.8,9,1.9)
    front=front.union(clip_toe)
    clamp=clamp.cut(box(cx+25.15,cy-4.65,cz-10.5,1.1,9.3,2.2))

    # A cap moves along -X to release; T rails provide positive lift retention.
    cap=rb(cx-2,cy-10,cz+8.7,29,20,3,2)
    for yy in [cy-7.5,cy+7.5]:
        clamp=clamp.cut(box(cx-2.1,yy-1.7,cz+5.5,29.3,3.4,1.9))
        clamp=clamp.cut(box(cx-2.1,yy-.9,cz+7.3,29.3,1.8,1.3))
        tongue=box(cx-1.6,yy-1.35,cz+5.8,28.0,2.7,1.2)
        tongue=tongue.union(box(cx-1.6,yy-.55,cz+6.9,28.0,1.1,2.0))
        cap=cap.union(tongue)
    # Recessed rear finger scoop, not a projecting catch near the laptop.
    cap=cap.cut(hole((0,0,1),(cx-2.3,cy,cz+8.5),4,3.5))

    # Rigid quarter-turn T keeper. The lug sits in an undercut circular pocket;
    # rotate the thumb paddle 90 degrees to align with the withdrawal keyway.
    # It is retained while locked, removable when unlocked (not a captive pin).
    kx=cx+1.8; ky=cy+7.5
    boss=box(kx-3.6,ky-3.1,cz-.2,7.2,6.2,5.7)
    clamp=clamp.union(boss)
    clamp=clamp.cut(hole((0,0,1),(kx,ky,cz+1.9),2.6,2.3))
    keyway=box(kx-2.5,ky-.95,cz+2.0,5,1.9,11.0)
    bore=hole((0,0,1),(kx,ky,cz+3.8),1.7,10)
    clamp=clamp.cut(keyway).cut(bore)
    cap=cap.cut(keyway).cut(bore)
    keeper=cq.Workplane(obj=hole((0,0,1),(kx,ky,cz+3.2),1.4,8.8))
    keeper=keeper.union(box(kx-.6,ky-2.2,cz+2.4,1.2,4.4,1.1))
    keeper=keeper.union(rb(kx-4,ky-1.8,cz+12,8,3.6,2,1))
    # Small locating underside bridge traps the top of the metal clip.
    cap=cap.union(box(cx+25.15,cy-4.5,cz+8.4,1.15,9,.4))

    # Two captured M3 nuts remain replaceable from the open cassette before
    # installing the plug. Clearance above them accepts the screw protrusion.
    for yy in [-8+dy,8+dy]:
        xx=-14+dx
        clamp=clamp.cut(hexz(xx,yy,cz-11.2,5.9,2.9))
        # Rear-facing entry tunnels allow the nuts to be inserted before the
        # thumb screws, even where a cassette sidewall covers the pocket.
        clamp=clamp.cut(box(cx-2.1,yy-3.0,cz-11.2,xx-(cx-2.1)+.2,6,2.9))
        clamp=clamp.cut(hole((0,0,1),(xx,yy,cz-15),1.7,12))
        nut=hexz(xx,yy,cz-11.0,5.5,2.4).cut(hole((0,0,1),(xx,yy,cz-11.1),1.3,2.6))
        add('cassette_M3_captive_nut_'+str(yy),nut,metal,True)
        washer=cq.Workplane(obj=hole((0,0,1),(xx,yy,P-25),7,1)).cut(hole((0,0,1),(xx,yy,P-25.1),1.7,1.2))
        add('cassette_washer_'+str(yy),washer,metal,True)
        # 18 mm nominal under-head length, changing with shim calibration;
        # choose stock length plus spacing washers after the physical fitting.
        screw=hexz(xx,yy,P-27,5.5,2).union(hole((0,0,1),(xx,yy,P-25),1.45,18+dz))
        add('cassette_M3_screw_envelope_'+str(yy),screw,metal,True)
        knob=cq.Workplane('XY',origin=(xx,yy,P-30)).circle(6.5).extrude(5)
        for a in range(0,360,60):
            knob=knob.cut(hole((0,0,1),(xx+7.6*math.cos(math.radians(a)),yy+7.6*math.sin(math.radians(a)),P-31),1.6,7))
        knob=knob.cut(hexz(xx,yy,P-27.15,5.9,2.4))
        add('cassette_thumb_knob_'+str(yy),knob,polymer)

    # Preserve x=-0.4 clearance to the laptop regardless of calibration.
    nose=box(-.4+dx,-40,cz-30,6,80,60)
    clamp=clamp.cut(nose); cap=cap.cut(nose)
    add('X_depth_overmold_clamp',clamp,polymer)
    add('front_capture_clip_0p8mm_metal',front,metal,True)
    add('sliding_plug_cap',cap,polymer)
    add('plug_cap_quarter_turn_keeper',keeper,(123,137,127))

    overmold=box(cx+5,cy-3.25,cz-6.25,20,6.5,12.5).edges('|X').fillet(1.5)
    overmold=overmold.union(hole((1,0,0),(cx,cy,cz),3.25,5.1))
    add('Dell_plug_overmold_REFERENCE',overmold,(36,38,40),True)
    tip=box(cx+25,cy-1.2,cz-4.125,6.65,2.4,8.25).edges('|X').fillet(1.15)
    add('USB_C_shell_REFERENCE',tip,(191,197,200),True)

    stop=box(-8,-7,H+6,7,14,10).union(box(-13,-7,H+6,5,44,10))
    stop=stop.union(box(-13,18,46,8,6,H+10-46))
    stop=stop.cut(hole((1,0,0),(-28,0,H+11),2.2,29))
    stop=stop.cut(hexx(-7.2,0,H+11,7.4,3.8))
    stop=stop.cut(box(-7.2,-3.7,H+11,3.8,7.4,6))
    add('chassis_stop_block',stop,polymer)
    nut=hexx(-7,0,H+11,7,3.2).cut(hole((1,0,0),(-7.1,0,H+11),1.7,3.4))
    add('stop_M4_captive_nut',nut,metal,True)
    screw=hexx(-25,0,H+11,7,3).union(hole((1,0,0),(-22,0,H+11),1.9,21))
    add('independent_M4_stop_screw_envelope',screw,metal,True)
    knob=cq.Workplane(obj=hole((1,0,0),(-28,0,H+11),8.5,6))
    knob=knob.cut(hexx(-25.15,0,H+11,7.4,3.4))
    for a in range(0,360,60):
        knob=knob.cut(hole((1,0,0),(-28.1,10*math.cos(math.radians(a)),H+11+10*math.sin(math.radians(a))),2,6.3))
    add('stop_thumb_knob',knob,polymer)
    add('stop_soft_tip',hole((1,0,0),(-1,0,H+11),3,1),soft)
    return {'nominal_M3_under_head_length_mm':18,'M3_length_changes_with_shim_mm':dz,
            'cap_release_direction':'-X after 90 degree keeper rotation',
            'keeper':'retained when locked; removable when unlocked',
            'threads':'purchased metal; smooth reference envelopes only',
            'material_target':'PETG, 0.4 mm nozzle, P1S; coupon qualification required'}
