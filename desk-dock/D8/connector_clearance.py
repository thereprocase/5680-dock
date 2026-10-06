"""Local shell clearances for the removable connector assembly.

Call after the cradle/lip fusion and BEFORE connector_shell_shoe is fused.
The keyed shoe is the structural mating interface and must retain its full
geometry. All pockets below are specified in the unleaned laptop frame.
"""
import cadquery as cq


CLEARANCE_MM = .35
MODULE_RELEASE_Y_MM = 4.3


def clear_grille_for_module(grille, p):
    """The narrower vertical spring leaves both complete grilles unchanged."""
    return grille.val() if isinstance(grille, cq.Workplane) else grille


def clear_shell_for_module(roof, p):
    """Remove two bounded fit/service pockets from the baseline shell.

    Reserve the rectangular beam and low stop corner during the initial
    4.3 mm local -Y release and subsequent -X withdrawal. The obsolete lower
    root is removed from the module;
    its former clearance and the narrower spring require no shell notches.
    It does not subtract an entire
    module bounding box or enlarge the pocket through the fan aperture.
    The fitted module and fixed shoe cover most of the beam opening; the
    running clearance is a local air bypass, not a claimed airtight joint.
    """
    H = p['rear_case_seat_z']
    P = H + p['port_from_rear_case']
    c = CLEARANCE_MM
    release = MODULE_RELEASE_Y_MM

    # Minima and maxima before the 0.35 mm fit allowance.
    pockets = [
        ((-40, 26-release, P-66.7), (18, 50, P-18.7)),
        # Only the low outboard stop corner intersects the shell. Stay outside
        # the X=6..25 laptop seat and leave the higher stop bracket untouched.
        ((-7, 18-release, H-4), (-5, 26, H)),
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
