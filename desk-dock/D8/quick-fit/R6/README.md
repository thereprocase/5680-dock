# D8 R6: modular bracket with backing wall (superseded by R7 the same day)

**18 September 2026.** Decisions: lean 8 degrees (was 5); everything the laptop
touches except the 8-degree lid-bearing wall is modular, so the plenum and fan
prints can start while capture and bearing are tuned later by reprinting only
the small pieces.

## Pieces

| Piece | Per | What it carries |
| --- | --- | --- |
| Frame | dock end (identical both ends) | base, brace, solid tower, 8-degree lid rail extended down to form one socket wall, 6-mm backing wall on the other side |
| Seat block | machine | deck, R2 seat curve with the V5 C 1-mm relief (hinge geometry lives here) |
| Fence liner | machine and end | an L whose foot fills the socket outboard of the seat block and whose wall is the underside stop: 64 mm tall at the plug end, 15 mm at the far end (laptop-thickness differences live here) |
| Pin | end | one 36-mm D9 fan pin, pushed in from the outer face through backing wall and liner foot into the seat block |

## Retention: drop in, one pin, no key

Considered and rejected: a long dovetail (needs sliding room the cradle end
does not have under a docked laptop; a crept PETG dovetail cannot be levered
apart), a wedge taper (self-locks with creep), snap detents (PETG fatigue),
a tilt-in hook (needs a second lock under the laptop). Chosen: the pieces
drop straight into the socket between the rail and the backing wall with
0.3 mm side clearance; the pin locates X, stops lift and carries the tipping
moment in shear. The bores in the two pieces sit 0.15 mm lower than the bore
in the frame, so driving the pin cams both pieces onto the floor: no rattle in
use. Disassembly: pull the pin by its lugged head and lift the pieces; a 6-mm
knock-out hole up through the base takes a rod if the seat block ever sticks.

Receipts in `checks.json`: every piece is blocked within 2 mm in all six
directions by frame plus pin; cam interference 0.1 mm3; laptop, rubber-foot,
keepout and lift checks clean at 8 degrees; plug-end liner catches a tipping
laptop from 4 degrees; docking sweep clear at the plug end (8.5 mm) and
through the far end (0.47 mm), which is why the far liner is short.

`--d9-source --base-thickness 4 --tag d9-source --lock-x 16` writes the frame
and pieces the D9 P5 cradles crop to their 16-mm width; the pin bore and the
knock-out sit at the centre of that crop. Nominal CAD only; the pieces are
not yet dressed with fillets (the D9 frame is, by the P3 dressing pass).
