# D8 hinge support update

## Chamfered hinge bearings — 16 September 2026

Six integral 6 mm-wide bridges now support the straight hinge edge, at 25%,
50% and 75% of each inlet opening. Both sliding ends of each printed bearing
have a 1 mm chamfer. Each replaceable 4 x 8 x 0.3 mm liner has 0.15 mm bevels
on its two sliding edges; total thickness includes adhesive. Original end
seats remain. The bearings follow the 5-degree laptop lean and the existing
reference model's straight-edge datum (local Z=58 mm). Confirm this height
on the physical laptop before loading it.

The bridge widths occupy 36 mm of the combined 279.38 mm opening length:
87.1% remains between them. This is a geometric length measure, not a cooling
or flow-rate prediction. The mouth areas in flow-geometry.json are gross;
the final cavity volume subtracts the actual added structures.

Fresh checks cover 89 valid assembly solids, 43 manufacturing meshes, all 12
sampled laptop poses, expanded rubber-foot keepouts, service-removal motions,
and exact contact/seal-clearance checks for all six bearings. There are no
unintended rigid collisions. The STEP, viewer, print meshes and renders were
regenerated together. See [bearing checks](bearing-check.json) and
[layout](hinge-bearing-layout.json).

The changed shells need a new OrcaSlicer review with the intended P1S/material
profile, especially support placement and removal below the cross-slot
bridges. Previous deposited-path and 1.659 kg estimates describe the earlier
shells; they do not qualify this update. Physical fit, sliding friction,
strength, warm creep and cooling remain unmeasured.

![Chamfered quarter-interval hinge bearings](D8-hinge-bearings.png)
