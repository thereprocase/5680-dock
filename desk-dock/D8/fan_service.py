"""Open-top fan pockets and slide-down grilles; no loose fan fasteners.

The suction face stays at the established local Z=30 datum. Changing thickness
grows the frame and retention features outward, preserving the intake cavity.
"""
import math

BACK_Z=30.0
POSE_ANCHOR_Z=22.5
DEFAULT_THICKNESS=25.0

def fan_dimensions(thickness=DEFAULT_THICKNESS, pad_thickness=0.0):
    """Axial datums in the existing fan-local coordinate frame."""
    if thickness<=0:
        raise ValueError('Fan thickness must be positive')
    if pad_thickness < 0:
        raise ValueError('Pad thickness must be nonnegative')
    back=BACK_Z-pad_thickness
    front=back-thickness
    envelope_front=front-pad_thickness
    guard_back=envelope_front-7.5
    return dict(thickness=float(thickness),back=back,front=front,
                pad_thickness=pad_thickness,envelope_back=BACK_Z,envelope_front=envelope_front,
                center=(front+back)/2,guard_back=guard_back,
                guard_front=guard_back-4,pocket_front=guard_back+.3,
                pocket_back=BACK_Z+.3,rail_front=guard_back-6.5)

D=fan_dimensions()
SPEC = {
    'pocket_inner_size_mm':121.5,
    'pocket_axial_envelope_mm':27.8,
    'retention':'Two replaceable flat-print top clips per fan; low-strain leaves and local contact shoes. No full perimeter gasket.',
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
    'fan_front_guide_clearance_mm':None,
    'long_front_guide_lips_used':False,
    'grille_back_edge_chamfer_mm':2.8,
    'rail_roof_transition':'45-degree support ramp with 0.30 mm normal-coordinate mating allowance; <=0.45 mm residual shelf at pocket rim.',
    'rail_side_running_clearance_mm':.6,
    'friction_land_interference_per_side_mm':0.0,
    'friction_note':'Grille uses running clearance. Separate positive top clips provide retention; no precise interference land is required.',
    'cable_bundle_envelope_mm':[6.0,4.0],
    'cable_notch_width_mm':7.0,
    'cable_notch_note':'Lower +X corner relief spans fan depth and opens to the suction cavity; actual lead exit and fan clocking remain provisional.',
}
FRICTION_REGIONS={}
ACTIVE_SPECS={}
RETENTION_CONTACT_REGIONS={}
PRINT_OVERRIDES={}
TOP_CLIP_SPECS={}


def build_fan_service(i,fx,roof,fanpose,box,rb,hole,add,thickness=DEFAULT_THICKNESS,fit=None):
    """Return the modified roof; add one already-posed slide-down grille."""
    fit=fit or {}
    pad=float(fit.get('pad_thickness_mm',0.0))
    d=fan_dimensions(thickness,pad)
    back=BACK_Z
    inner=float(fit.get('pocket_inner_size_mm',121.5))
    axial=float(fit.get('pocket_axial_envelope_mm',27.8))
    assert inner>=120.8 and axial>=thickness+2*pad+.3
    # The housing fits the full stack; the bare frame reference may sit farther
    # outward when its rear pad contacts the unchanged suction-envelope datum.
    front=back-axial
    gap=float(fit.get('guard_gap_mm',7.5))
    depth=float(fit.get('guard_bar_depth_mm',4.0))
    bar=float(fit.get('guard_bar_width_mm',1.6))
    pitch=float(fit.get('guard_pitch_mm',9.0))
    chamfer=min(2.8,depth-1.0)
    if chamfer<=0:raise ValueError('Grille depth must exceed 1 mm')
    gb=front-gap;gf=gb-depth;pf=gb+.3;pb=back+.3;rf=gf-2.5
    half_inner=inner/2
    low_y=91-half_inner
    ACTIVE_SPECS[i]=dict(SPEC,fan_reference_size_mm=[120,120,thickness],
                         fan_pad_thickness_mm=pad,pocket_inner_size_mm=inner,
                         pocket_axial_envelope_mm=axial,
                         fan_suction_face_local_z_mm=d['back'],
                         fan_discharge_face_local_z_mm=d['front'],
                         grille_frame_local_z_mm=[gf,gb],
                         grille_bar_width_mm=bar,grille_bar_pitch_mm=pitch,
                         grille_back_edge_chamfer_mm=chamfer,
                         guard_back_to_fan_discharge_mm=d['envelope_front']-gb)
    prefix=f'{i:02}_';graphite=(61,69,72)
    pocket=rb(fx-64,27,pf,128,128,pb-pf,5)
    pocket=pocket.cut(rb(fx-half_inner,low_y,pf-.1,inner,inner,pb-pf+.3,1.0))
    roof=roof.union(fanpose(pocket))
    for xx in [fx-52.5,fx+52.5]:
        for yy in [38.5,143.5]:
            roof=roof.union(fanpose(hole((0,0,1),(xx,yy,back+.1),2.5,2.4)))
    # The replaceable top clips control axial retention. Long front guide
    # lips would form unsupported ledges in the fan-rim print pose.
    # Open below the rounded shoulders so the frame clears during its lift.
    roof=roof.cut(fanpose(box(fx-half_inner,144.9,pf-.1,inner,156.1,back+.1-(pf-.1))))
    roof=roof.union(fanpose(box(fx-54,low_y,front,108,.5,pb-front)))

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
    # Support the channel roof with 45-degree ramps. The grille's matching
    # rear-edge chamfer preserves the sliding path. A 0.30 mm allowance at
    # its back face leaves at most a 0.45 mm shelf at the final pocket rim
    # with the default 121.5 mm pocket and 2.8 mm chamfer.
    import cadquery as cq
    side_run=chamfer+.6
    for side in [-1,1]:
        pts=[(fx+side*64.8,pf-side_run-.2),
             (fx+side*64.8,pf+.2),
             (fx+side*(64.6-side_run-.2),pf+.2)]
        ramp=cq.Workplane('XZ',origin=(0,25,0)).polyline(pts).close().extrude(-130)
        roof=roof.union(fanpose(ramp))
    pts=[(26.8,pf-chamfer-.2),(26.8,pf+.2),(27+chamfer+.2,pf+.2)]
    ramp=cq.Workplane('YZ',origin=(fx-67,0,0)).polyline(pts).close().extrude(134)
    roof=roof.union(fanpose(ramp))

    guard=rb(fx-64,27,gf,128,128,depth,8)
    guard=guard.faces('>Z').edges().chamfer(chamfer)
    guard=guard.cut(hole((0,0,1),(fx,91,gf-.1),56.5,depth+.2))
    for off in [k*pitch for k in range(-int(54/pitch),int(54/pitch)+1)]:
        half=math.sqrt(56.5**2-off**2)+1.2
        guard=guard.union(box(fx-half,91+off-bar/2,gf,2*half,bar,depth))
    # No upper return: the entire grille now prints on one broad face.
    # Two separate side-print clips close the pocket and retain the grille.

    FRICTION_REGIONS[i]=[]

    # The relief follows the full frame depth, not just the old 15 mm frame.
    # Its rear branch opens into the duct; actual lead position remains a fit check.
    mouth=box(fx+59.8,43.5,front-.2,5.4,7,axial+1).edges('|X').fillet(.6)
    rear=box(fx+59.8,43.5,back-2,5.4,7,8.5).edges('|Z').fillet(.5)
    roof=roof.cut(fanpose(mouth.union(rear)))
    add(prefix+'fan_guard_retainer',fanpose(guard),graphite,False)
    from fan_retention import add_top_clips
    roof,clip_spec,contacts,free_shapes=add_top_clips(i,fx,roof,fanpose,box,add,gf,
                                                   d['envelope_front'],back)
    TOP_CLIP_SPECS[i]=clip_spec
    RETENTION_CONTACT_REGIONS[i]=contacts
    PRINT_OVERRIDES.update(free_shapes)
    return roof
