# R4 quick-fit bracket pair + P2 fastener fit parts — geometry review

Claude Fable 5.1, 2026-09-17. One plate: two identical R4 brackets (a loaded
laptop stand pair) plus the ten D9 P2 fastener fit-trial parts, printed on the
frozen structural profile so the pin/key clearances match the P2 kit.

R4 = the R2 quick-fit bracket with the V5 lid-rail move (rail side +3.5 mm,
unleaned +Y) and thicker members: rail 4 -> 6 mm (outward), short fence +2 mm
on its outer face, base plate 4 -> 6 mm (downward), diagonal brace 4 -> 6 mm.
Laptop-facing surfaces are unchanged from R2 / V5. Variant letter = the V5
coupon seat that fit: A original R1 seat, B R2 seat, C R2 seat + 1-mm relief.

Builder receipts (`checks-<variant>.json`): R2 seat profile reproduced exactly
from the GLB; new rail inner face at unleaned y = 14.585 mm; the 3.5-mm channel
above the deck is empty; nominal laptop, rubber-foot and expanded-keepout
overlaps are zero at rest and through 0.25..40 mm lifts; a lid-side probe
between y = T/2 and the new rail face is clear; seat contact probe engages
(A and B); watertight single-solid STL and STEP round trip.

- R4-A: solid 126.1 cm3 each, print bounds [152.9, 135.0, 38.1] mm, fence-to-rail 25.92 mm, STL sha256 d84348d03969ceb7ed7b395abcf5c2cb27aff49942856390a446df235b9e4092
- R4-B: solid 127.2 cm3 each, print bounds [152.9, 135.0, 38.1] mm, fence-to-rail 27.92 mm, STL sha256 340f1c8b2b681672c7d1e7455b660ad5c5ea58e103fd5e252765b412e483e7b9
- R4-C: solid 126.8 cm3 each, print bounds [152.9, 135.0, 38.1] mm, fence-to-rail 27.92 mm, STL sha256 76cd2acca0a54ecc02512d8b90cbe93551cd2c05d29e86c1dd79044041a817c8

Print pose: the bracket lies on its side (original X to print Z, 38.1 mm
tall), every feature a constant profile through print Z, so zero designed
overhangs; the pair nests hypotenuse to hypotenuse rotated 180 degrees. The
fit parts keep their P2-pass print poses (translation only). Brackets are
strict (no support, no external bridge roads); fit parts may carry the P2
kit's intended hidden supports and bridges.

Limits: source contact data is an AR visualization, not metrology; the
3.5 mm is the requested trial increment; no load, creep or physical fit
result exists yet.
