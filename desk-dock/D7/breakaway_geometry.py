"""Printed, preloaded face-cam hinge. Construction frame follows the laptop.

This is a calibration prototype: CAD does not establish its release force.
The spring's assembled deflection is displayed; export its unloaded shape.
"""
import math
import cadquery as cq

def spring_offset(p):
    return float(p['breakaway'].get('spring_offset_y_mm',26.0))

def datum(p):
    P=p['rear_case_seat_z']+p['port_from_rear_case']
    return -22.0,P+27.15

def box(x,y,z,a,b,c):
    return cq.Workplane('XY').box(a,b,c,centered=False).translate((x,y,z))

def cyl(x,y,z,r,h):
    return cq.Workplane(obj=cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z),cq.Vector(0,1,0)))

def along_y(shape,x,y,z):
    return shape.rotate((0,0,0),(1,0,0),-90).translate((x,y,z))

def cam_angle(p):
    a=p['breakaway'];k=2*a['nominal_E_MPa']*a['spring_width_mm']*a['spring_thickness_mm']**3/a['spring_leaf_length_mm']**3
    d=a['spring_preload_deflection_mm'];h=a['cam_rise_mm'];T=a['nominal_release_N']*27.15
    return (k*d*h+.5*k*h*h)/T

def cam_lift(p,angle):
    a=p['breakaway'];k=2*a['nominal_E_MPa']*a['spring_width_mm']*a['spring_thickness_mm']**3/a['spring_leaf_length_mm']**3
    d=a['spring_preload_deflection_mm'];T=a['nominal_release_N']*27.15
    return min(a['cam_rise_mm'],math.sqrt(d*d+2*T*abs(math.radians(angle))/k)-d)

def cam_teeth(p,radial_clearance=0):
    """Three broad sector teeth, with an energy-shaped rising release ramp."""
    px,pz=datum(p);half=math.radians(10);ramp=cam_angle(p);rise=p['breakaway']['cam_rise_mm']
    solids=[]
    # Tooth starts at y25.8; a 0.2 mm shoulder spans the face clearance.
    for centre in [0,2*math.pi/3,4*math.pi/3]:
        samples=[(-half-ramp-.00001,.001)]
        for j in range(12,0,-1):
            q=ramp*j/12
            samples.append((-half-q,.2+rise-cam_lift(p,math.degrees(q))))
        samples += [(-half+2*half*j/8,.2+rise) for j in range(9)]
        for j in range(1,13):
            q=ramp*j/12
            samples.append((half+q,.2+rise-cam_lift(p,math.degrees(q))))
        samples.append((half+ramp+.00001,.001))
        # Piecewise ruled lofts keep planar radial walls and valid broad teeth.
        wires=[]
        for theta,h in samples:
            theta+=centre
            pts=[cq.Vector(px+r*math.cos(theta),y,pz+r*math.sin(theta))
                 for r,y in [(16-radial_clearance,25.8),(24+radial_clearance,25.8),(24+radial_clearance,25.8+h),(16-radial_clearance,25.8+h)]]
            wires.append(cq.Wire.makePolygon(pts+[pts[0]]))
        for u,v in zip(wires,wires[1:]):solids.append(cq.Solid.makeLoft([u,v],True))
    return cq.Workplane(obj=cq.Compound.makeCompound(solids))

def centering_pilot(p):
    px,pz=datum(p)
    pilot=cq.Workplane(obj=cq.Solid.makeCone(12,11,1,cq.Vector(px,25.8,pz),cq.Vector(0,1,0)))
    return pilot.cut(cyl(px,25.7,pz,6.2,1.2))

def make_spring(p,delta=None):
    a=p['breakaway'];px,pz=datum(p)
    if delta is None:delta=a['spring_preload_deflection_mm']
    L=a['spring_leaf_length_mm'];t=a['spring_thickness_mm'];b=a['spring_width_mm']
    # Two fixed-guided leaves, a rigid central island and a removable outer frame.
    frame=box(px-44,50,pz-30,88,11,60).cut(box(px-38,49,pz-16,76,14,32))
    for sign in [-1,1]:
        pts=[]
        for i in range(21):
            u=i/20;x=px+sign*(38-L*u);w=delta*(3*u*u-2*u*u*u)
            pts.append((x,58-w))
        polygon=pts+[(x,y+t) for x,y in reversed(pts)]
        leaf=cq.Workplane('XY',origin=(0,0,pz-b/2)).polyline(polygon).close().extrude(b)
        frame=frame.union(leaf)
    # Reinforcement projects toward the support. In the unloaded print pose
    # frame, leaves and island share one flat outer face at y=61.
    island=box(px-8,55-delta,pz-12,16,6,24)
    frame=frame.union(island).cut(cyl(px,49,pz,5.35,20))
    for zz in [pz-22,pz+22]:frame=frame.cut(cyl(px,49,zz,4.35,20))
    # Put the spring behind the slide-in fan rails, inside the existing fan
    # depth envelope. Two short spacers carry it back to the fixed support.
    return frame.translate((0,spring_offset(p),0))

def make_fixed_support(p):
    from printed_fasteners import make_threaded_hole
    P=p['rear_case_seat_z']+p['port_from_rear_case'];px,pz=datum(p)
    # Tube is outside the carrier's swept Y envelope. The closed root shoe
    # joins the tower ahead of the fan frame and does not open an air bypass.
    beam=box(-40,26,P-66.7,58,24,48).cut(box(-40.1,30,P-62.7,54.1,16,40))
    shoe=box(10,18,46,12,32,P-18.7-46).union(box(18,12,46,8,16,P-18.7-46))
    post=box(px-18,26,P-18.7,36,24,pz-(P-18.7))
    disc=cyl(px,26,pz,34,24)
    fixed=beam.union(shoe).union(post).union(disc)
    fixed=fixed.cut(cyl(px,25,pz,5.35,27)).cut(cam_teeth(p,.15)).cut(centering_pilot(p))
    # An 8 mm integral rotor peg travels in a relieved arc and arrests the
    # fold at about 45 degrees. It does not set the calibrated release load.
    r=29;inner=r-4.25;outer=r+4.25;a=math.pi/4
    track=(cq.Workplane('XZ',origin=(px,25.9,pz)).moveTo(inner,0)
        .threePointArc((inner*math.cos(a/2),-inner*math.sin(a/2)),(inner*math.cos(a),-inner*math.sin(a)))
        .lineTo(outer*math.cos(a),-outer*math.sin(a))
        .threePointArc((outer*math.cos(a/2),-outer*math.sin(a/2)),(outer,0)).close().extrude(-6))
    for theta in [0,-a]:track=track.union(cyl(px+r*math.cos(theta),25.9,pz+r*math.sin(theta),4.25,6))
    fixed=fixed.cut(track)
    for zz in [pz-22,pz+22]:
        offset=spring_offset(p)
        fixed=fixed.union(cyl(px,49.9,zz,8,offset+.1))
        fixed=fixed.cut(make_threaded_hole(23+offset,diameter=8).rotate((0,0,0),(1,0,0),90).translate((px,61+offset,zz)))
    return fixed

def make_carrier(p):
    P=p['rear_case_seat_z']+p['port_from_rear_case'];px,pz=datum(p)
    shelf=box(-47,-28,P-26,47,51,7.3)
    # Wide side web remains outside the laptop, and beside the fixed arm.
    web=box(-47,18,P-26,39,7.8,pz-(P-26))
    # A broad return around the rear and underside edge carries cassette
    # torsion. It clears the shim, cap-pin head and vertical cap removal path.
    web=web.union(box(-47,-28,P-26,7,53.8,39))
    web=web.union(box(-47,-28,P-26,39,7.6,27))
    hub=cyl(px,18,pz,27,7.8)
    carrier=shelf.union(web).union(hub).union(cam_teeth(p)).union(centering_pilot(p))
    carrier=carrier.union(cyl(px+29,24,pz,4,6.5))
    carrier=carrier.cut(cyl(px,16,pz,5.2,12))
    return carrier

def add_hinge_hardware(p,add):
    from printed_fasteners import make_screw,make_nut,make_threaded_hole
    px,pz=datum(p);delta=p['breakaway']['spring_preload_deflection_mm'];offset=spring_offset(p)
    thread_start=58+offset;spring_face=61+offset
    # One 10 mm printed axle; only the far end is threaded. The shoulder sets
    # bearing diameter, while the separate nut sets spring compression.
    threaded=along_y(make_screw(16,diameter=10,head_diameter=22,head_height=6),px,thread_start,pz).intersect(cyl(px,thread_start,pz,5.01,16))
    axle=cyl(px,18,pz,5,thread_start-18).union(threaded)
    axle=axle.union(cyl(px,12,pz,11,6))
    # This collar limits nut advance to the 1.2 mm nominal maximum preload.
    # It moves with the axle during release, so the extra .8 mm cam travel
    # remains available. Its diameter clears the spring island's 10.7 bore.
    axle=axle.union(cyl(px,55+offset,pz,5.25,4.8))
    add('breakaway_pivot_pin_10mm',axle,(109,143,130))
    add('breakaway_spring_cartridge',make_spring(p),(154,157,116))
    # A narrow bearing nose loads only the rigid island. The wide hand grip
    # stands clear of both flexible leaves throughout the compression stroke.
    base=spring_face-delta
    nut=make_nut(8,diameter=10,outer_diameter=24,phase_z=thread_start-(base+2)).translate((0,0,2))
    nose=cq.Workplane('XY').circle(7.5).extrude(2).cut(make_threaded_hole(2,diameter=10,phase_z=thread_start-base,lead_in=0))
    nut=nut.union(nose)
    add('breakaway_preload_hand_nut',along_y(nut,px,base,pz),(109,143,130))
    for j,zz in enumerate([pz-22,pz+22]):
        screw=make_screw(22+offset,diameter=8,head_diameter=17,head_height=5)
        # Screw points toward -Y. Thread phase follows its own reverse axis.
        posed=screw.rotate((0,0,0),(1,0,0),90).translate((px,spring_face,zz))
        add(f'breakaway_spring_hand_screw_{j}',posed,(109,143,130))

def moving_names(name):
    return name.startswith(('cassette_','breakaway_carrier','plug_')) or name in ['height_shim_pack','X_depth_overmold_clamp','sliding_plug_cap','Dell_plug_overmold_REFERENCE','USB_C_shell_REFERENCE']
