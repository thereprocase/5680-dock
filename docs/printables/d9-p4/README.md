# Precision 5680 D9 P4: R5-C cradles, fit corrections, finished edges

P4 is the D9 P2 no-metal-hardware dock with these changes and nothing else:

1. **Cradle contact from the R5-C profile.** The printed V5 coupon C seated
   (R2 seat with the 1-mm local relief) once the lid rail was moved 3.5 mm
   outward, so both outer cradles carry that seat and rail position with a
   6-mm rail. On the plug-end cradle (M1) the short underside fence is raised
   into a 6-mm underside rail 64 mm above the seat datum, same 2.25-mm running
   clearance, 4 x 2 mm lead-in, after the printed R4-C pair tipped toward the
   underside side when nudged. The far-end cradle (M2) keeps the R4-C profile
   without the wall: the rear rubber-foot strip slides through that end during
   the 18-mm docking travel and would catch on it. One wall is enough to stop
   the laptop rotating. The cradle base
   stays 4 mm so every foot remains coplanar with the ties.
3. **Fit corrections from the printed P2 fit plate.** Pin bores 8.8 -> 8.4 mm
   (0.2-mm diametral clearance on the 8.2-mm octagonal pins); key barbs 6.2 ->
   7.2 mm wide through the 5.4-mm slot (total interference 0.8 -> 1.8 mm); T
   tongue 12.7 -> 12.1 mm tall so it no longer stands 0.6 mm proud of the
   female tie. Plate 00 is regenerated: print it first and check insertion,
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

Open **OPEN-ME.3mf** in OrcaSlicer; it is an identical copy of
**00-START-HERE-fastener-fit.3mf**, print only one of the two. Then print
plates **01 through 07 once each** for one dock: ten major parts, 20 pins and
20 locking keys. Each numbered 3MF contains
one frozen, named plate with matching embedded G-code; matching standalone
G-code, oriented STL and assembly-coordinate STEP bodies are included. The
STL poses are intentional; do not auto-orient them. Print the two outer
cradle plates (01 and 04) only after the R5-C bracket pair has been handled;
the other five plates do not depend on the contact geometry.

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
(`source-inputs/quick-fit/R5`, built from the R2 bracket by the R5 builder with
`--variant C --base-thickness 4 --tag d9-source`), the R2 inputs and the
geometry JSON are included. STEP files preserve assembled coordinates; STL
files preserve print poses. Preparation helpers and frozen profiles are
included. SHA256.json and the ZIP payload are verified against the standalone
print directory.

## Orca estimates

- fit plate 00: 40.39 g; 1h 52m 51s.
- assembly plates 01 to 07: 1104.97 g; 46h 31m 5s.
- outer cradle plates 01 and 04: 435.94 g; 19h 57m 19s.
- contact independent plates 02 03 05 06 07: 669.03 g; 26h 33m 46s.
