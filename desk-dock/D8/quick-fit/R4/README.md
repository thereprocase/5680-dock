# D8 R4: R2 contact + the V5 lid-rail move + thicker members

**Loaded fit pair, 17 September 2026. Print two identical brackets.**

## Decision record

- V4 A/B/C coupons printed: all three contacted the tall lid-side rail before
  the seat; C (three openings) was still not enough.
- V5 = V4 with the whole rail side moved 3.5 mm outward, normal to the rail
  face. Printed the same evening. **C seated** (R2 seat with the 1-mm local
  seat relief). Decision by the user: "3 dots wins", go for the loaded pair.
- R4 therefore carries the R2 seat, lip shift, lip rise and heel extension,
  the C relief band, and the 3.5-mm rail move. The 3.5 mm is the requested
  trial increment from handling the coupons, not a measured lid thickness.

## Geometry versus R2

| Feature | R2 | R4 | Direction of change |
| --- | --- | --- | --- |
| Rail inner face (unleaned y) | 11.085 mm | 14.585 mm | outward, +3.5 mm |
| Rail thickness | 4 mm | 6 mm | outward |
| Short fence outer face | −16.085 − 2 mm | 2 mm further out | outward |
| Base plate thickness | 4 mm | 6 mm | downward (height above desk 152.9 mm) |
| Diagonal brace width | 4 mm | 6 mm | into the brace |
| Fence inner face to rail inner face | 24.42 mm | 27.92 mm | |
| Seat, fence inner face, column, inside gap 318.48 mm | unchanged | unchanged | |

`build_quick_fit.py --variant A|B|C` selects the seat side to match the V5
coupon letters; C is the printed one. Outputs: `D8-R4-<variant>-quick-fit-
bracket.step`, `...-print-TWO.stl`, `checks-<variant>.json`, previews. The
builder re-extracts the R2 heel from the reference GLB, asserts the R2 seat
profile is reproduced, probes the new rail face and the empty 3.5-mm channel,
and reruns R2's laptop, rubber-foot, keepout, lift and lid-side checks.

## Print

Printed once as one plate with the D9 P2 fastener fit parts: kit
`PRINT-ME-R4-C-BRACKET-PAIR-PLUS-P2-FIT` (Codex outputs and
`docs/printables/r4-fit-pair/`), Repro Normal at 15 % grid infill, about
7 h 05 m and 217 g, sent to the P1S on 17 September (dark-grey PETG, physical
AMS slot 2).

## What the pair answers

Stand the pair at the R2 spacing, lower the closed laptop on with the lid
toward the tall rails, and check seat engagement, rocking onto the fence, lid
contact with the rail, stability under a nudge and docking along the long
axis. If it passes, the same rail move and C seat go into the D9 P2 outer
cradles (plates 01 and 04) before those print. Load capacity, creep and
retention durability are untested.

## Edge treatment (added after the first R4-C plate)

`fit-parameters.json` now carries `inside_corner_fillet_mm` 3.0,
`outside_corner_fillet_mm` 1.5, `contact_edge_break_mm` 0.5 and
`top_face_chamfer_mm` 0.8. Profile corners (edges along print Z) are filleted:
concave for stress relief, convex for looks; the laptop contact band is left
alone except a 0.5-mm break on the rail's top inner edge; the top face gets a
0.8-mm chamfer built as four 0.2-mm steps from inward 2-D offsets (exactly
what the slicer would make of a 45-degree chamfer); the bed face stays sharp.
Two 1-mm slivers were removed so the fillets close: the deck is now flush with
the fence outer face and the brace foot flush with the base end. Re-sliced with
the fit parts: 7 h 06 m, 215 g, still zero support and bridge roads on the
brackets. `--base-thickness 4 --tag d9-source` exports the profile the D9 P3
cradles are built from.
