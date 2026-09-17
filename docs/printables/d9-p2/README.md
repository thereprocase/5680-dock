# Precision 5680 D9 P2: no added metal hardware

The cradle, plenum, fan-guard and brace assembly uses printed connections throughout: no added screws, nuts, washers or threaded inserts. Two purchased 120 x 120 x 25 mm fans are still required. The plug mechanism is excluded.

## Start with the fit plate

Open **OPEN-ME.3mf** in OrcaSlicer. It is an identical copy of **00-START-HERE-fastener-fit.3mf**: print only one of those two files. This small plate has both fan-socket arrangements, two exact T-joint ends, and three production pin/key pairs. Confirm easy insertion, positive retention and deliberate removal before printing the large parts. Press the two key tips together to release them; do not force a tight fit. These clearances have not been calibrated on a physical print.

Then print plates **01 through 07 once each** for one dock: ten major parts, 20 pins and 20 locking keys, 50 printed assembly parts total. Plate 00 is a separate fit trial; its three pin/key pairs duplicate production parts on plate 07. Each numbered 3MF contains one frozen, named plate with matching embedded G-code. Matching standalone G-code and oriented STL plus assembly-coordinate STEP bodies are included. The STL poses are intentional; do not auto-orient them.

Printer/profile: Repro Bambu P1S, 0.4 mm nozzle, Generic PETG Starter, textured PEI, 0.2 mm nominal layers, five walls, six top/bottom layers, 5 mm brim. Main plates use 40% gyroid; fit fixtures and fasteners use 100% infill. Supports are enabled for accessible hidden surfaces. Confirm the actual printer and filament before using the saved G-code. No job was sent.

## Parts and identification

| Pin use | Quantity | Head-edge notches | Shaft length | Matching key |
| --- | ---: | ---: | ---: | --- |
| Fan guards | 8 | 1 | 36 mm | Six long; two short at the outboard lower sockets |
| Frame ends | 4 | 2 | 32.8 mm | Long |
| Plenum seams | 6 | 3 | 26 mm | Long |
| Brace T joints | 2 | 4 | 29.4 mm | Short |

There are 16 long keys (22.5 mm overall, 16 mm grip) and four short keys (15.5 mm overall, 8 mm grip). Each pin has an additional 4 mm head. Part names are retained in the Orca projects and CAD files. Gray pins and gold keys in the assembly render are printed plastic; color only distinguishes parts.

## Assembly

1. Remove supports and brim while the shell halves are open. Clean pin bores and key windows without enlarging their bearing surfaces. Use the fit plate to check the intended clearance first.
2. Join each front/rear brace on the bench: lower the male T tongue into the floor-backed female pocket, insert a four-notch pin, then its short key. The T shoulders transfer brace loads; the pin prevents lifting. The complete brace attaches to the cradle feet with two-notch pins and long keys. Front feet are 20 mm farther forward than P1 for retainer access.
3. Dry-fit each matching M1/M2 shell pair. Join its three internal tabs with three-notch pins and long keys before fitting the fans. The rear-wall seam key inserts downward through the open mouth. Optional thin seam sealant addresses physical leakage; it is not the structural connection.
4. Place each fan against its flange and add the guard. Guard standoffs bear on the fan corners. Four one-notch pins run outside the fan frame into blind sockets; factory screw holes are unused. Install their keys. The lower outboard sockets (M1-fan-1 and M2-fan-3) take short keys from the outer cradle side; rotate those pins one quarter-turn so the cross-slot faces that side. The other lower fan keys insert from above; upper keys use their exposed transverse windows.
5. To service a rear brace T joint, first remove the complete brace from the cradle feet. Do not try to withdraw its center pin through an installed fan housing. Remove fans before servicing the internal plenum retainers.

The lower laptop-contact shape remains R2. It has not been adjusted from newly measured laptop thickness. Use the separate V4 contact coupons before committing to large cradle prints. Check initial seating with the laptop independently supported.

## Why these poses

Shells print on their broad exterior X faces, cavities upward. This keeps supported internal tab/socket undersides accessible before closure; the broad finished sides receive bed texture. Guards print exterior-face down, standoffs vertical. Male ties print broad top down; female ties print floor down. Pins print on an octagonal longitudinal flat, with their long load direction in the layers. Keys print flat so their leaves bend within the layer plane. Transverse bores bridge between two landings. Orientations and geometry were selected before Orca verification.

## Verification and limits

All 50 assembly solids and four fit fixtures are valid, single-component watertight meshes. No nominal volume interference was found between assembly parts, purchased fan envelopes or the upper laptop envelope. Pin/key insertion was checked at five positions along each selected path, using compressed key-barb geometry and the assembly sequence above. This is sampled clearance evidence, not a continuous swept-volume proof or a measured insertion-force result.

Both plenums pass nominal enclosure checks using the two actual shell halves, with each named port capped in turn. No idealized fastener-seal patches were needed: fan sockets are blind and outside the air wall. Printed seam leakage remains unmeasured.

All eight plates must pass the included native Orca verification before this kit is packaged: unchanged poses and placement; actual model/support/brim extrusion inside the usable bed and outside the exclusion zone; expected heights; zero reported mesh repair; matching embedded and standalone G-code. The overview and detailed production-key road preview are included.

This is a prototype print kit. Physical seating, pin/key fit, support removal, loaded stability, creep, retention durability, cooling and acoustics remain untested. No 800 RPM performance claim is made.

## Editable source and provenance

`source/build_d9.py` runs with CadQuery 2.8, trimesh, Shapely and Pillow. Its frozen R2 STEP and geometry inputs are included in `source/source-inputs`; it exports to an adjacent `generated` directory. STEP files preserve assembled coordinates; STL files preserve print poses. Preparation helpers and frozen profiles are included. The local Orca executable path in the preparation script may need adjustment on another machine. Existing plate directories are preserved; use a fresh source copy for another slicing run. SHA256.json and the ZIP payload are verified against the standalone print directory.

## Orca estimates

- fit plate 00: 40.26 g; 1h 52m 26s.
- assembly plates 01 to 07: 1098.99 g; 44h 54m 4s.
