"""Open-top fan pockets and slide-down grilles; no loose fan fasteners.

The suction face stays at the established local Z=30 datum. Changing thickness
grows the frame and retention features outward, preserving the intake cavity.
"""
import math

BACK_Z=30.0
POSE_ANCHOR_Z=22.5
DEFAULT_THICKNESS=25.0

def fan_dimensions(thickness=DEFAULT_THICKNESS):
    """Axial datums in the existing fan-local coordinate frame."""
    if thickness<=0:
        raise ValueError('Fan thickness must be positive')
    front=BACK_Z-thickness
    guard_back=front-7.5
    return dict(thickness=float(thickness),back=BACK_Z,front=front,
                center=(front+BACK_Z)/2,guard_back=guard_back,
                guard_front=guard_back-4,pocket_front=guard_back+.3,
                pocket_back=BACK_Z+.3,rail_front=guard_back-6.5)

D=fan_dimensions()
SPEC = {
    'pocket_inner_size_mm':121.0,
    'fan_reference_size_mm':[120,120,DEFAULT_THICKNESS],
    'fan_suction_face_local_z_mm':BACK_Z,
    'fan_pose_anchor_local_z_mm':POSE_ANCHOR_Z,
    'fan_discharge_face_local_z_mm':D['front'],
    'grille_frame_local_z_mm':[D['guard_front'],D['guard_back']],
    'fan_factory_holes_used':False,
    'fan_locating_pins_used':False,
    'fan_fasteners_used':False,
    'grille_bar_width_mm':1.6,
    'grille_bar_pitch_mm':9.0,
    'guard_back_to_fan_discharge_mm':7.5,
    'slide_axis_fan_local':[0,1,0],
    'full_service_lift_mm':140.0,
    'service_requires_laptop_removed':True,
    'fan_front_guide_clearance_mm':.2,
    'rail_side_running_clearance_mm':.6,
    'friction_land_interference_per_side_mm':.05,
    'friction_note':'Two small lands engage over the final 6 mm. Intentional 0.05 mm interference is a PETG coupon starting point, not a measured holding force.',
    'cable_bundle_envelope_mm':[6.0,4.0],
    'cable_notch_width_mm':7.0,
    'cable_notch_note':'Lower +X corner relief spans fan depth and opens to the suction cavity; actual lead exit and fan clocking remain provisional.',
}
FRICTION_REGIONS={}
ACTIVE_SPECS={}


def build_fan_service(i,fx,roof,fanpose,box,rb,hole,add,thickness=DEFAULT_THICKNESS):
    """Return the modified roof; add one already-posed slide-down grille."""
    d=fan_dimensions(thickness)
    back,front=d['back'],d['front']
    gf,gb,pf,pb,rf=(d[k] for k in ['guard_front','guard_back','pocket_front','pocket_back','rail_front'])
    ACTIVE_SPECS[i]=dict(SPEC,fan_reference_size_mm=[120,120,thickness],
                         fan_discharge_face_local_z_mm=front,
                         grille_frame_local_z_mm=[gf,gb])
    prefix=f'{i:02}_';graphite=(61,69,72)
    pocket=rb(fx-64,27,pf,128,128,pb-pf,8)
    pocket=pocket.cut(rb(fx-60.5,30.5,pf-.1,121,121,pb-pf+.3,6.5))
    roof=roof.union(fanpose(pocket))
    for xx in [fx-52.5,fx+52.5]:
        for yy in [38.5,143.5]:
            roof=roof.union(fanpose(hole((0,0,1),(xx,yy,back+.1),2.5,2.4)))
    # Front guide lips follow the thicker frame's discharge face.
    for side in [-1,1]:
        xx=fx-60.8 if side<0 else fx+58.2
        roof=roof.union(fanpose(box(xx,31,front-3.2,2.6,120,3)))
    # Open below the rounded shoulders so the frame clears during its lift.
    roof=roof.cut(fanpose(box(fx-60.5,144.9,pf-.1,121,156.1,back+.1-(pf-.1))))
    roof=roof.union(fanpose(box(fx-54,30.5,front,108,.5,pb-front)))

    # C rails are rooted into the pocket along their height, behind the grille.
    for side in [-1,1]:
        wall_x=fx-67 if side<0 else fx+64.6
        front_x=fx-67 if side<0 else fx+60.8
        rail=box(wall_x,25,rf,2.4,130,pb-rf)
        rail=rail.union(box(front_x,25,rf,6.2,130,2.25))
        rail=rail.union(box(fx-67 if side<0 else fx+63.8,25,pf,3.2,130,pb-pf))
        roof=roof.union(fanpose(rail))
    roof=roof.union(fanpose(box(fx-67,25,rf,134,2,pf-rf)))
    # Give the stop and pocket a real shared volume. Their former Y27/Zpf
    # edge-only junction produced a nonmanifold STL edge on the deeper pocket.
    # The rib starts 0.2 mm behind the grille back, clear of its sliding plane.
    roof=roof.union(fanpose(box(fx-67,26.7,pf-.1,134,.8,1.1)))

    guard=rb(fx-64,27,gf,128,128,4,8)
    guard=guard.cut(hole((0,0,1),(fx,91,gf-.1),56.5,4.2))
    for off in range(-54,55,9):
        half=math.sqrt(56.5**2-off**2)+1.2
        guard=guard.union(box(fx-half,91+off-.8,gf,2*half,1.6,4))
    # Integral top return reaches behind the complete 25 mm frame.
    guard=guard.union(rb(fx-56,153.5,gb-.1,112,3,back+.1-(gb-.1),1))

    regions=[]
    for side in [-1,1]:
        seat_x=fx-65 if side<0 else fx+64.3
        land_x=fx-64.35 if side<0 else fx+63.7
        seat=rb(seat_x,37,gf-.5,.7,6,4.8,.2)
        land=rb(land_x,37,gf+.5,.65,6,3,.2)
        roof=roof.union(fanpose(seat))
        guard=guard.union(land)
        region=box(fx-64.5 if side<0 else fx+64.2,36.8,gf-.6,.3,6.4,5.1)
        regions.append(fanpose(region).val())
    FRICTION_REGIONS[i]=regions

    # The relief follows the full frame depth, not just the old 15 mm frame.
    # Its rear branch opens into the duct; actual lead position remains a fit check.
    mouth=box(fx+59.8,43.5,front-.2,5.4,7,thickness+1).edges('|X').fillet(.6)
    rear=box(fx+59.8,43.5,back-2,5.4,7,8.5).edges('|Z').fillet(.5)
    roof=roof.cut(fanpose(mouth.union(rear)))
    add(prefix+'fan_guard_retainer',fanpose(guard),graphite,False)
    return roof
