"""Local shell clearances for the removable connector assembly.

Call after the cradle/lip fusion and BEFORE connector_shell_shoe is fused.
The keyed shoe is the structural mating interface and must retain its full
geometry. All pockets below are specified in the unleaned laptop frame.
"""
import cadquery as cq


CLEARANCE_MM = .35
MODULE_RELEASE_Y_MM = 4.3


def clear_grille_for_module(grille, p):
    """Relieve the outboard spring corner's short crossing of the grille.

    Accept an assembled, fan-posed grille after the part lean pass. Apply to
    both fan grilles for interchangeable geometry. The pocket is the bounded
    lower spring corner envelope during -Y release, with 0.35 mm allowance.
    It recesses the discharge-side edge locally while retaining the rear
    thickness and the remainder of the flat perimeter.
    """
    shape = grille.val() if isinstance(grille, cq.Workplane) else grille
    H = p['rear_case_seat_z']
    P = H + p['port_from_rear_case']
    offset = float(p['breakaway'].get('spring_offset_y_mm', 26))
    c = CLEARANCE_MM
    b = shape.BoundingBox()
    center_x = (b.xmin+b.xmax)/2
    fan_x = min(p['fan_centers_x'], key=lambda x: abs(x-center_x))
    dx = fan_x-p['fan_centers_x'][0]
    lo = (17+dx, 50+offset-MODULE_RELEASE_Y_MM, P+27.15-30)
    hi = (22+dx, 61+offset, P+27.15-24)
    cutter = (cq.Workplane('XY')
        .box(*(hi[k]-lo[k]+2*c for k in range(3)), centered=False)
        .translate(tuple(v-c for v in lo)).val()
        .rotate((0, 0, H), (1, 0, H), -p['laptop_lean_deg']))
    shape = shape.cut(cutter).clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise ValueError('Connector relief must preserve one valid flat grille')
    return shape


def clear_shell_for_module(roof, p):
    """Remove four bounded fit/service pockets from the baseline shell.

    This reserves the old rectangular beam envelope, its remaining lower root,
    and the stop/spring corners during the 4.3 mm -Y then -X removal path.
    It does not subtract an entire
    module bounding box or enlarge the pocket through the fan aperture.
    The fitted module and fixed shoe cover most of the beam opening; the
    running clearance is a local air bypass, not a claimed airtight joint.
    """
    H = p['rear_case_seat_z']
    P = H + p['port_from_rear_case']
    offset = float(p['breakaway'].get('spring_offset_y_mm', 26))
    c = CLEARANCE_MM
    release = MODULE_RELEASE_Y_MM

    # Minima and maxima before the 0.35 mm fit allowance. The beam's lower
    # root descends to Z=46 below the beam floor at P-66.7; leaving it out
    # would preserve part of the measured 762 mm3 nominal interference.
    pockets = [
        ((-40, 26-release, P-66.7), (18, 50, P-18.7)),
        # The lower root starts at X=10, but passes across the left endwall
        # during -X extraction. Continue this pocket all the way outboard.
        ((-40, 26-release, 46), (18, 50, P-66.7)),
        # Only the low outboard stop corner intersects the shell. Stay outside
        # the X=6..25 laptop seat and leave the higher stop bracket untouched.
        ((-7, 18-release, H-4), (-5, 26, H)),
        # Lower/outboard spring frame corner beside the rail transition. This
        # local notch follows its approach to the sloped rail during -Y
        # release, leaving the rest of the fan rail/rear seat intact.
        ((17, 50+offset-release, P+27.15-30),
         (22, 61+offset, P+27.15-18)),
    ]
    shape = roof.val() if isinstance(roof, cq.Workplane) else roof
    for lo, hi in pockets:
        cutter = (cq.Workplane('XY')
            .box(*(hi[k]-lo[k]+2*c for k in range(3)), centered=False)
            .translate(tuple(v-c for v in lo)).val()
            .rotate((0, 0, H), (1, 0, H), -p['laptop_lean_deg']))
        shape = shape.cut(cutter)
    shape = shape.clean()
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise ValueError('Connector clearance must preserve one valid shell solid')
    return shape
