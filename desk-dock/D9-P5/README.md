# Precision 5680 D9 P5: 8-degree lean, drop-in contact pegs, finished edges

P5 is the D9 P2 no-metal-hardware dock with these changes and nothing else:

1. **8-degree lean and modular contact on the R7 frame.** Each cradle end is
   the R7 frame profile: base, brace, a tower whose top is the deck with two
   22-mm channels along the docking axis, the 8-degree lid rail (the only
   laptop-touching surface on the frame) and a 6-mm outer wall. Everything
   else the laptop touches is a drop-in peg on plate 08: a seat peg per
   machine (R2 seat with the V5 C relief) and a fence peg per end (64-mm
   underside wall at the plug end, 15-mm fence at the far end where the rear
   rubber-foot strip slides past during docking). One 36-mm fan pin pushed in
   from the outer face passes through the outer wall and both feet; the peg
   bores sit 0.15 mm lower than the frame bore so the pin cams both pegs onto
   the deck. Pull the pin and lift to swap pegs; push-out holes under the
   channels take a rod. Other machines: re-head the pegs, keep the frame. The
   plenum front wall moved from 24 to 26.5 mm so the 8-degree lid keeps 2 mm
   clearance at the top. The cradle base
   stays 4 mm so every foot remains coplanar with the ties.
3. **Fit corrections from the printed P2 fit plate.** Pin bores 8.8 -> 8.4 mm
   (0.2-mm diametral clearance on the 8.2-mm octagonal pins); key barbs 6.2 ->
   7.2 mm wide through the 5.4-mm slot (total interference 0.8 -> 1.8 mm). The T
   tongue stays 12.7 mm tall: the P4 trim to 12.1 mm chased stuck support
   debris; the cleaned printed pair nests flush. Round-shaft trial (18 September):
   the four frame-end pins have a round 8.2-mm shaft with one chord flat on the
   bed, so they match the 8.4-mm round bores everywhere instead of only at the
   octagon's corners (the printed P2 octagons rattled). The other 18 pins stay
   octagonal until the trial is judged. Bonus fan-screw path (optional): the
   guards carry 4.5-mm clearance holes through plate and standoffs and every
   flange carries 3.5-mm blind pilots 6 mm deep on the fan's 105-mm pattern, so
   four M4 x 45 screws can hold guard and fan instead of (or as well as) the
   pins. The pilots are blind, so the air wall stays closed; plug or ignore
   them if unused. Shells printed before 18 September 17:00 lack the pilots:
   use the guard as a drill jig. Support-reducing gussets (18 September, no mating
   change; `check_no_removed_material.py` proves nothing was removed from any shell
   or guard): every external socket boss now carries a rib or a 34-degree wedge to
   the flange, and each seam tab carries a 34-degree wedge on its pin-tip end,
   which is the bed-facing end on the M1 inner shell and the M2 outer cradle. Those
   two parts lose 80 % and 64 % of their support road; the M1 outer cradle and
   M2 inner shell keep their tab towers because the pin head sits under those tab
   ends. The wedges add about 15 cm3 per plenum and 30 to 35 minutes of print time
   per gusseted shell, so the trade is cleanup for time. `overhang-threshold-test/`
   is the calibration: this Orca profile supports faces at 45 degrees from
   vertical and leaves 35 degrees alone.
4. **Centre frame (19 September).** The two inner halves stop 2.3 mm apart at
   the middle with nothing joining them above the ties and no laptop contact
   between the frame ends. Plate 08 now carries a third cradle-end frame: the
   same R7 profile and peg sockets as the ends, so it takes the same seat peg
   and a 15-mm fence peg (both on the plate, the seat peg cropped to sit on the
   plenum roof), trimmed to wrap the printed halves with 0.15 mm clearance, a
   2-mm fin that fills the gap and registers it, a foot that follows the plenum
   floor under the splice, and a base that stops 0.5 mm above the four corner
   feet so the dock never rocks on the middle. The front T-joint's lap pin and
   key pass through it. It is epoxied to both halves; there is no lock pin.
   Proven additive: nothing was removed from any printed part. Plate 00 is regenerated: print it first and check insertion,
   retention and deliberate removal before the large parts.
2. **Printable edge treatment.** Profile corners that run along each part's
   print Z are filleted (3 mm concave for stress relief, 1.5 mm convex for
   looks); the ties' top edges carry a 0.8-mm chamfer; bed edges are untouched.
   Every mating zone is protected and unchanged: air cavities, fan seats,
   blind sockets, pin bores, key slots, T joints, guard bars and standoffs,
   and the laptop contact band. Pins, keys and fit fixtures carry the P4
   fit corrections below.

Connections, plenum geometry, fan pose, guards and braces are P2. Two purchased
120 x 120 x 25 mm fans are still required. The plug mechanism is excluded.

## What to print

**Plate 09, the cradle-end trial**, is the M1 outer cradle sliced to its
16-mm frame width with a seat peg, the tall fence peg and a pin: print it
before the cradles to feel the 8-degree seat and the peg fit. Plates 02, 03,
05, 06 and 07 do not depend on the contact geometry.

Open **OPEN-ME.3mf** in OrcaSlicer; it is an identical copy of
**00-START-HERE-fastener-fit.3mf**, print only one of the two. Then print
plates **01 through 08 once each** for one dock: eleven major parts, six pegs,
22 pins and 20 locking keys. Each numbered 3MF contains
one frozen, named plate with matching embedded G-code; matching standalone
G-code, oriented STL and assembly-coordinate STEP bodies are included. The
STL poses are intentional; do not auto-orient them. Print the two outer
cradle plates (01 and 04) after the plate 09 trial; the other five plates do
not depend on the contact geometry.

Printer/profile: Repro Bambu P1S, 0.4 mm nozzle, Generic PETG Starter,
textured PEI, 0.2 mm layers, five walls, six top/bottom layers, 5 mm brim,
40 % gyroid on the main plates and 100 % on the fasteners. Supports are
enabled for accessible hidden surfaces. Confirm the actual printer and
filament before using the saved G-code.

## Parts and identification

| Pin use | Quantity | Head-edge notches | Shaft length | Matching key |
| --- | ---: | ---: | ---: | --- |
| Fan guards | 8 | 1 | 36 mm | Six long; two short at the outboard lower sockets |
| Frame ends | 4 | 2 | 32.8 mm | Long |
| Plenum seams | 6 | 3 | 26 mm | Long |
| Brace T joints | 2 | 4 | 29.4 mm | Short |

There are 16 long keys (22.5 mm overall, 16 mm grip) and four short keys
(15.5 mm overall, 8 mm grip). Each pin has an additional 4 mm head. Part
names are retained in the Orca projects and CAD files.

## Assembly

1. Remove supports and brim while the shell halves are open. Clean pin bores
   and key windows without enlarging their bearing surfaces.
2. Join each front/rear brace on the bench: lower the male T tongue into the
   floor-backed female pocket, insert a four-notch pin, then its short key.
   The complete brace attaches to the cradle feet with two-notch pins and
   long keys.
3. Dry-fit each matching M1/M2 shell pair. Join its three internal tabs with
   three-notch pins and long keys before fitting the fans. The rear-wall seam
   key inserts downward through the open mouth. Optional thin seam sealant
   addresses physical leakage; it is not the structural connection.
4. Place each fan against its flange and add the guard. Four one-notch pins
   run outside the fan frame into blind sockets; factory screw holes are
   unused. The lower outboard sockets take short keys from the outer cradle
   side; rotate those pins a quarter-turn so the cross-slot faces that side.
5. To service a rear brace T joint, remove the complete brace from the cradle
   feet first. Remove fans before servicing the internal plenum retainers.

## Verification and limits

All 50 assembly solids are valid, single-component watertight meshes. No
nominal volume interference exists between assembly parts, purchased fan
envelopes or the upper laptop envelope. Pin/key insertion was re-checked at
five positions along each path with compressed key-barb geometry. Both
plenums pass the nominal enclosure checks with the two actual shell halves
and each named port capped in turn, and the edge treatment changed the
intended air volume of each module by exactly zero. Every plate passed the
native Orca verification: unchanged poses and placement, all roads inside the
usable bed and outside the exclusion zone, expected heights, matching
embedded and standalone G-code, and per-object support and bridge counts
recorded (hidden supports on shells, guards and ties are intended).

This is a prototype print kit. Physical seating of the R4-C cradles, pin/key
fit, support removal, loaded stability, creep, retention durability, cooling
and acoustics remain untested. No 800 RPM performance claim is made.

## Editable source and provenance

`source/build_d9.py` runs with CadQuery 2.8, trimesh, Shapely and Pillow, with
`source/dress.py` for the edge treatment. The frozen R4-C cradle source
(`source-inputs/quick-fit/R7`, built from the R2 bracket by the R7 builder with
`--variant C --base-thickness 4 --tag d9-source`), the R2 inputs and the
geometry JSON are included. STEP files preserve assembled coordinates; STL
files preserve print poses. Preparation helpers and frozen profiles are
included. SHA256.json and the ZIP payload are verified against the standalone
print directory.
