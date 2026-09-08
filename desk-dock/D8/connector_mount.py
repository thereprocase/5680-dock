"""Removable connector-module interface, in the unleaned laptop frame.

The shell receives only connector_shell_shoe. Two accessible transverse hand
locks clamp the module against its broad side face; keys bear docking thrust.
Print fits and the complete loaded alignment budget remain unqualified.
"""
import cadquery as cq
from printed_fasteners import make_screw, make_threaded_hole


def detachable_support(p, support, box, hole, add):
    from breakaway_geometry import spring_mounts
    P = p['rear_case_seat_z'] + p['port_from_rear_case']
    # With Y=50 on the bed, two 45-degree haunches reduce the original
    # 40 mm cavity roof bridge to 8 mm. The brace remains open at X=-40 for
    # inspection and support access; its external load-path envelope is unchanged.
    zlo,zhi=P-62.7,P-22.7
    for section in [[(30,zlo),(46,zlo),(30,zlo+16)],
                    [(30,zhi),(30,zhi-16),(46,zhi)]]:
        haunch=(cq.Workplane('YZ',origin=(-40,0,0)).polyline(section)
                .close().extrude(54.2))
        support=support.union(haunch)
    # Separate the existing spring stand-offs at their flat datum. They retain
    # their external dimensions and the original long spring screws, but their
    # bores are clearance fits. The main support can now print on its XZ face.
    support = support.cut(box(-100, 50, P-10, 200, 100, 120))
    for j, (xx,zz) in enumerate(spring_mounts(p)):
        offset = float(p['breakaway'].get('spring_offset_y_mm', 26))
        spacer = cq.Workplane(obj=hole((0, 1, 0), (xx, 50, zz), 8, offset))
        spacer = spacer.cut(hole((0, 1, 0), (xx, 49.9, zz), 4.35, offset+.2))
        add(f'breakaway_spring_spacer_{j}', spacer, (74, 82, 86))
    split = box(18, -60, 0, 80, 200, P-18.7)
    shoe = support.intersect(split)
    module = support.cut(split)
    # This old under-root projection served the formerly fused shell joint.
    # The removable module instead seats against the keyed side flange.
    module = module.cut(box(0, -60, 0, 18.1, 86, P-18.7))
    module = module.cut(box(0, 26, 0, 18.1, 24.1, P-66.7))
    # Stop at X=23: the actual left fan frame begins at X=24, with its
    # half-millimetre pocket clearance beginning at X=23.5.
    shoe = shoe.union(box(-16, 50, P-66.7, 39, 8, 48))
    keys = []
    for j, zz in enumerate([P-54, P-31]):
        # Thickened local female bosses leave the hollow brace predominantly open.
        boss = cq.Workplane(obj=hole((0, 1, 0), (4, 40, zz), 8, 10))
        module = module.union(boss)
        threaded = make_threaded_hole(10, phase_z=-8).rotate(
            (0, 0, 0), (1, 0, 0), 90).translate((4, 50, zz))
        module = module.cut(threaded)
        shoe = shoe.cut(hole((0, 1, 0), (4, 49.9, zz), 4.35, 8.2))
        key = box(-14, 46, zz-5, 8, 4, 10)
        socket = box(-14.15, 45.8, zz-5.15, 8.3, 4.3, 10.3)
        module = module.cut(socket)
        shoe = shoe.union(key)
        screw = make_screw(17.5, head_diameter=14, head_height=4).rotate(
            (0, 0, 0), (1, 0, 0), 90).translate((4, 58, zz))
        add(f'connector_mount_lock_{j}', screw, (109, 143, 130))
        keys.append({'center_xz_mm': [-10, zz], 'size_xyz_mm': [8, 4, 10]})
    add('connector_shell_shoe', shoe, (74, 82, 86))
    return module, {
        'fixed_shell_part': 'connector_shell_shoe',
        'removable_body': 'connector_module_body',
        'seat_plane_laptop_y_mm': 50,
        'locks': 'Two accessible printed 8x2 screws, axes -Y, 9.5 mm nominal engagement',
        'positive_keys': keys,
        'key_clearance_per_face_mm': .15,
        'main_body_print_face': 'Y=50 on bed; X and Z load directions in bed plane. Internal 45 degree haunches leave an 8 mm roof bridge.',
        'removal': 'Unload laptop; remove two shell-mount locks; pull module local -Y 4.3 mm to clear keys, then withdraw outboard along -X. Cable remains installed in module; reserve a loose exterior loop. Do not lift the module before its right edge has cleared the rail.',
        'spring_cartridge_orientation': 'Original 88 x 60 mm leaf frame rotated 90 degrees about the unchanged Y preload axis, giving 60 mm X width and 88 mm Z height. Lateral spacer/screw mounts are X=-44 and 0 at the pivot height.',
        'qualification': 'Nominal keys and broad clamp seat only; printed repeatability, extraction restraint and <=0.20 mm whole-holder movement require measurement.'}


def attach_stop(p, module, stop, box, hole, add):
    """An independently adjustable stop bracket, removable with the module.

    Both large parts have a common broad XZ print face. The stop's horizontal
    adjustment thread still needs its own print-fit/support check.
    """
    H=p['rear_case_seat_z']
    stop=stop.cut(box(-60,26,0,100,80,H+50))
    stop=stop.union(box(-31,18,H-4,26,8,30))
    for j,zz in enumerate([H+3,H+19]):
        module=module.union(cq.Workplane(obj=hole((0,1,0),(-24.5,26,zz),8,10)))
        female=make_threaded_hole(10,phase_z=-8).rotate(
            (0,0,0),(1,0,0),-90).translate((-24.5,26,zz))
        module=module.cut(female)
        stop=stop.cut(hole((0,1,0),(-24.5,17.9,zz),4.35,8.2))
        lock=make_screw(17.5,head_diameter=14,head_height=4).rotate(
            (0,0,0),(1,0,0),-90).translate((-24.5,18,zz))
        add(f'chassis_stop_mount_lock_{j}',lock,(109,143,130))
    module=module.union(box(-27,22,H+8,8,4,6))
    stop=stop.cut(box(-27.15,21.8,H+7.85,8.3,4.3,6.3))
    add('chassis_stop_bracket',stop,(74,82,86))
    return module
