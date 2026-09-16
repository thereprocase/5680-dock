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

## Historical review records

# D8 current CAD review — physical qualification pending

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

## Previous D8 review record (before intermediate bearings)

# D8 completed CAD review — physical qualification pending

D8 includes a removable live Y/Z connector module, independent X stop, dedicated shell feet, light covers, researched fan clearances and separate flat-printing fan clips.

## Connector service and adjustment

The spring cartridge is rotated 90 degrees while retaining its leaf dimensions, preload axis and cam. Both spacer/screw/thread mounts move consistently. The obsolete lower root is removed.

**The complete module now clears all 19 sampled service positions:** unload the laptop, remove two mounting locks, move local −Y by 4.3 mm, then withdraw along −X. No initial lift is required. The check found zero nominal connector collisions and 79 valid single CAD solids. See [the hashed service evidence](review-evidence/module-service-check.json).

Live Y/Z travel also passed nominal and four corner positions with invariant part volumes and no unintended housing collisions using cylindrical thread envelopes. Exact matched thread geometry was checked separately.

## Final regenerated package

The STEP, 43 manufacturing STLs, manifests and four CAD renders have been regenerated from the corrected source. The complete STEP is distributed in a [lossless ZIP](Precision_5680_D8_STEP.zip); extraction was verified byte-for-byte against the generated file. [Generation provenance](generation-provenance.json) records the unchanged build inputs and exact output hashes. Final checks use those exports; older bounded development experiments retain their own hashes and scope.

| Check | Final result |
|---|---|
| Exact full assembly | 83 valid single solids; zero unintended rigid collisions or Boolean errors; two documented intentional compliant contacts |
| Laptop approach and withdrawal | All 12 sampled positions pass, including expanded OEM-foot keepouts and source port handedness |
| Service motions | Connector removal and both downward cover-removal paths pass at the listed finite samples |
| Manufacturing meshes | All 43 watertight, consistently wound, single connected boundaries with positive volume |
| P1S envelope | All 43 meshes fit the recorded bed/exclusion envelope with an 8 mm brim |
| Generic deposited-path envelope | All 42 PETG parts pass; eight freshly sliced and 34 reused only with matching STL, slicer, profile and material hashes |

See [assembly validation](validation.json), [mesh preflight](print-review/mesh-preflight-summary.json) and [material/path screen](print-review/path-screen-summary.json). Finite collision samples are not a continuous-motion proof. The generic Cura screen is not an approved P1S machine job.

## Plastic estimate

At 1.27 g/cm³ PETG, the finished CAD solids contain **1,243 g**. The conservative generic slicing screen estimates **1,659 g deposited PETG**: 1,255 g model, 380 g normal automatic support and 25 g individual part brims. Budget **1.8–2.0 kg** for initial qualification and some reprints. Flexible pads/liners, the soft stop and startup waste are additional.

The two covers now contain about **94 g**, versus about 180 g in D7: approximately **48% less cover plastic**. Total CAD PETG falls about 8.4% from D7's 1,356.5 g; the complete dock remains a substantial print.

Automatic shell support is still the largest manufacturing loose end. The reduced-support experiment was rejected after finding approximately 93 mm hood skin roads in the wrong bridge direction. Its smaller estimate is excluded. Inspect bridge direction and support removal in the actual P1S profile before printing; short CAD rib gaps alone do not control deposited paths. [PRINT_DESIGN.md](PRINT_DESIGN.md) records every orientation and its layer-strength tradeoffs.

## Remaining qualification

Actual P1S slicing, physical thread/slider/fan fit, whole-holder stiffness, warm spring creep, measured release force, tip stability and cooling/noise remain unqualified. Five walls and dense loaded parts are a starting process choice, not a demonstrated strength rating. The complete-holder target of at most 0.20 mm deflection at 20 N and nominal 50 N release require measurement. The current printed face-cam and spring remain; a steel-preloaded detent redesign has not been implemented.

The public showcase and viewer now use D8; the archived D7 viewer and archive retain D7. This package completes the documented CAD and manufacturing review, not a production print release.
