# Precision 5680: V5 contact coupons, lid rail moved 3.5 mm outward

Open **OPEN-ME.3mf** in OrcaSlicer. The named, locked plate contains one of
each coupon in its verified print pose. The matching standalone G-code is
for the frozen **P1S, 0.4-mm nozzle, Generic PETG, textured PEI** profile.
Estimated whole plate: **1 hour 52 minutes model time (1 h 59 m with
start-up), 48.18 g.**

## What changed from V4

The printed V4 plate was handled against the real laptop: all three coupons
were wrong in the same way, and C (three openings) was still not enough. The
tall lid-side rail (the lid stop) sat too close to the seat / hinge-bearing
surface and the short fence.

V5 is V4 with the **entire rail side moved 3.5 mm further away**, measured
normal to the rail face. The flat deck between the seat and the rail is
3.5 mm longer, so each coupon grows by 3.5 mm in that direction. Nothing on
the seat/fence side moved: the short fence, the curved seat, the C relief band
and the identifier openings keep their V4 coordinates.

| Coupon | Identification | What it is |
| --- | --- | --- |
| A | One 2-mm square through-hole | V4 A (original R1 contact geometry, full rail) with the rail side moved 3.5 mm out |
| B | Two 2-mm square through-holes | V4 B (R2 capture changes and extended seat curve) with the rail side moved 3.5 mm out |
| C | Three 2-mm square through-holes | V4 C (B plus the 1-mm local seat relief) with the rail side moved 3.5 mm out |

Fence inner face to rail inner face: A 22.42 mm in V4, 25.92 mm in V5;
B and C 24.42 mm in V4, 27.92 mm in V5.

**V5 prints look like V4 prints.** Tell them apart by the flat deck between
the seat and the tall rail, which is 3.5 mm longer on V5. Label or discard
the V4 prints before comparing.

## Contact check

Support the laptop independently and present one coupon gently at the same
local section where the original leg engages. Keep fingers clear of the
contact gap. Observe which surface touches first: the intended curved seat,
the short backup fence, or the tall lid-side rail. Do not bend the rail to
make it fit or use the coupon to carry the laptop's weight.

Compare A, B and C at the same section and orientation. Record the variant,
first-contact location and whether the curved seat actually engages. If the
seat now engages with the rail clear of the lid, 3.5 mm is enough for this
local check; if the lid still reaches the rail first, the remaining gap is
the next measurement to take. A successful handheld contact check does not
establish loaded stability, retention, full-dock alignment or connector
protection.

## Manufacturing evidence

The broad profile is the designed bed face. Original X becomes print Z, and
the source geometry, the deck filler and all cuts have a constant section
through that axis. Orca 2.4.2 verified the selected orientation: automatic
supports enabled, **zero emitted support paths and zero external bridges**.
Internal infill closure occurs near the top skin at print Z=23.2 mm.

The prepared objects keep their orientations and 16-mm minimum spacing.
Model and brim paths stay inside the P1S bed and away from its front-left
excluded area. The native project's embedded G-code matches the standalone
file byte for byte. All six identifiers retain a 1-mm road-clear core and
surrounding walls on all 120 layers, checked in the frozen (0,+2)-mm nozzle
offset frame. An independent comparison rebuilt each V5 solid from the frozen
V4 STEP with explicit boxes and found zero symmetric difference.

The frozen process uses 0.20-mm layers, four walls, five top/bottom layers,
20% gyroid infill and a 5-mm outer brim. It is a diagnostic-coupon process,
not a structural qualification profile for the major dock revision.

## Contents and reproducibility

`fallback-CAD/` holds individual print-oriented STLs and original-frame STEPs.
`frozen-profiles/` contains the exact printer/process/filament snapshots.
`verification/` and `previews/` preserve the checks and visible evidence.
`source/` includes the editable builders and their local STEP/JSON inputs.
With compatible CadQuery, trimesh and Pillow installed, the source can be
rebuilt by running `source/profile-v5/build_full_rail_coupon_v5.py` with
`--d8 source/D8 --out <new-output-directory>` from this package directory;
it imports the V4 and V2 builders beside it.

The 3.5 mm is the requested trial increment from handling the printed V4
plate, not a measured lid thickness or curvature. R1/R2 contact data came
from a visualization reference, not manufacturing metrology.
