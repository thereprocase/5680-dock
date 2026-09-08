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
