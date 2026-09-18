# Precision 5680: R4-C bracket pair plus the D9 P2 fastener fit parts

Open **OPEN-ME.3mf** in OrcaSlicer. One locked plate, twelve objects, frozen
**P1S, 0.4-mm nozzle, Generic PETG, textured PEI**, 0.20-mm layers, four
walls, 15 % grid infill, 5-mm brim, automatic supports on. Estimated
**7 h 05 m total (6 h 59 m model time), 217 g.**

## What is on the plate

| Object | Count | Purpose |
| --- | --- | --- |
| D8-R4-C quick-fit bracket | 2 (one rotated 180°) | A freestanding laptop stand pair: the loaded test of the contact geometry that the V5 C coupon confirmed |
| fan-socket-fit-fixture, side-socket-fit-fixture | 1 each | D9 P2 pin/key socket trials |
| T-joint-fit-L, T-joint-fit-R | 1 each | D9 P2 floor-backed T joint trial |
| M1-fan-1-pin, M1-fan-3-pin, front-lap-pin | 1 each | D9 P2 printed pins |
| M1-fan-1-key, M1-fan-3-key, front-lap-key | 1 each | D9 P2 locking keys |

The two pins that sit inside the hollow bracket frames are deliberate; every
object keeps at least 16 mm of clearance to its neighbours, brims included.

## R4-C

R4 is the R2 quick-fit bracket with two changes:

1. **The V5 lid-rail move.** The whole rail side sits 3.5 mm further from the
   seat and the short fence, measured normal to the rail face. The printed V5
   C coupon (three openings: R2 seat plus the 1-mm local seat relief) was the
   one that seated, so R4-C carries that seat, and the relief band is cut in
   the bracket too.
2. **Thicker members, outward and downward only.** Rail 4 → 6 mm, short fence
   +2 mm on its outer face, base plate 4 → 6 mm, diagonal brace 4 → 6 mm. The
   laptop-facing surfaces are unchanged from V5 C, so the fit reading carries
   over. Height above the desk grows by 2 mm (152.9 mm).

Fence inner face to rail inner face: 27.92 mm (R2 was 24.42 mm). Inside clear
gap between the pair: 318.48 mm, unchanged. Each bracket is 127 cm³ solid.

## Fit trial

Stand the pair on the desk at the R2 spacing (a printed label on each base
gives the gap). Lower the closed laptop onto the seats with the lid toward
the tall rails. Check: does the curved seat carry it, does it rock onto the
short fence, does the lid touch the rail, does it stay put when nudged and
when docking along the laptop's long axis. Do not lever the rails.

Then trial the P2 connections: press each pin into its socket fixture, add
the key, confirm positive retention and deliberate removal, and assemble the
T joint the same way. Remove the hidden supports first.

## Manufacturing evidence

Brackets lie on their sides with the profile on the bed, so every bracket
layer is the same outline; Orca emitted **zero support and zero external
bridge roads for both brackets**. The fit parts carry their intended hidden
supports and bridges from the P2 kit (counts per object in
`verification/toolpath-verification.json`). Prepared positions were retained
by Orca, all roads sit inside the bed and outside the front-left exclusion,
and the embedded G-code matches the standalone file.

The process differs from the P2 kit only in sparse infill (15 % grid instead
of 20 % gyroid) to bring the plate under eight hours; walls, layer height,
shells and supports are the same, so pin and key clearances match the kit.

## Contents

`fallback-CAD/` bracket STEP/STL for A, B and C variants and the fit-part
STLs; `frozen-profiles/` the exact profile snapshot; `verification/` the
plate preparation, toolpath audit and geometry review; `previews/` layout
and toolpath images; `source/` the R4 builder, its parameters and the plate
scripts. Physical fit, load capacity and retention durability are untested.
