# D8 direct printed contacts — 16 September 2026

The six quarter-interval hinge bridges, profiled end seats and lid contact
lands are now integral printed shell surfaces. The 0.3 mm hinge/end liners,
0.6 mm lid liners and four hinge seal strips have been removed: 14 fewer
separate pieces. Contact surfaces occupy their former contact datums rather
than leaving gaps where the liners used to be. Hinge bearings retain their
1 mm chamfers in both sliding directions.

The printed feet and continuous lower perimeter now finish at Z=-5 mm.
This leaves 1.5 mm beneath the cover-screw heads with no pads fitted. The
existing flat foot faces can accept optional 12 x 12 x 3 mm grip pads, shown
as reference parts below Z=-5 mm. Bare printed feet are the default render
and viewer configuration; the viewer can show the optional pads separately.
Pads are not needed to support the dock or clear the screws.

Printed screws, joining keys, grilles and replaceable fan clips remain.
The existing fan mounting holes are retained as optional mounting geometry,
including for a later isolation-mount experiment. No bought fan fasteners or
rubber mounts are required by the pocket/clip arrangement; fit an actual
pull-through mount before assuming its head and tail clear the duct.

The connector mechanism and its soft stop are unchanged.

## Checks and printing

The assembly contains 75 solids, including eight optional desk-pad references,
and still exports 43 manufacturing meshes. Fresh exact-solid checks cover
all 12 sampled laptop positions, expanded rubber-foot keepouts and service
removal. Direct hinge/lid contact probes and bare-foot screw clearance are
recorded in [bearing-check.json](bearing-check.json). All manufacturing
meshes receive fresh topology and printer-envelope checks.

The shell changes need a new OrcaSlicer support and material review. Earlier
deposited-path and 1.659 kg figures describe the previous shell geometry.
Cooling, noise, surface wear and desk grip remain physical checks; removing
seals is a design simplification, not a new measured airflow claim.

![Direct printed hinge bearings](D8-hinge-bearings.png)
