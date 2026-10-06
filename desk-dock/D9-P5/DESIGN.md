# D9 P2 — no added metal hardware

Preserve the R2 contact profile and D9 P1 mouth geometry/fan pose. Replace every
added screw, nut and washer with printable mechanical connections. Purchased
fans still contain their normal motor and frame components; the plug mechanism
remains outside this revision.

The ten major parts now use 20 large printed pins and 20 flat locking keys:
eight fan pins, six internal plenum pins, four frame-end pins and two tie pins.
Sixteen keys have a 16-mm grip; four short keys have an 8-mm grip. The short
keys serve the two T-joint pins and two outboard lower fan sockets. Those two
fan sockets use side access through the cradle face; their neighboring inboard
lower fan keys insert from above, clear of the rear tie.
Floor-backed T joints transfer tie loads through shoulders; their pins prevent
uplift. The front tie/foot moved 20 mm forward from P1 to clear its accessible
printed retainers. Rear tie height remains 16 mm to clear the fans.

Pin sections: P2/P3 octagonal 8.2 mm across corners in 8.8 mm holes; P4 8.4 mm holes; from 19 September every pin is a round 7.9 mm shaft with a chord flat on the bed (0.5 mm diametral), after the octagons rattled and a round 8.2 mm trial would not enter the printed bores; the 7.9 mm pins were printed and confirmed to fit on 19 September.
Pin axes print parallel to the bed, on a longitudinal flat. Head notches identify
fan (1), frame (2), seam (3) and T-joint (4) pins. The keys print flat and bend in
their layer plane. Long keys use 1.2 mm leaves; short keys use 1 mm leaves and a
longer rounded root. Barbs must compress inward by approximately 0.4 mm each
to pass a nominal 5.4 mm slot. These are design dimensions, not calibrated fits
or measured insertion force/fatigue limits.

Fan sockets are external and blind. No fan fastener enters the air wall, so the
nominal enclosure audit needs no idealized bolt seals. (P5, 18 September: optional
M4 screw path added as bonus holes: 4.5-mm guard clearance, 3.5-mm blind pilots 6 mm
deep in the flange on the 105-mm pattern. Still blind, so the audit is unchanged.) Thin seam sealant remains
optional for physical airtightness, not structural attachment.

Manufacturing: broad shell exterior X faces down, cavities up; guard faces down;
male T ties broad top down, female ties broad base down. Hidden accessible support
is acceptable. No slicer search for orientations; Orca verifies the selected poses.
The fastener and fit-test plates use 100% infill; the six main plates retain five
walls, six top/bottom layers and 40% gyroid PETG.

The small fit-test plate includes both blind socket arrangements and guard spacing,
exact cropped T-joint ends, three production pins and their keys. Test insertion, positive
retention and deliberate removal before committing to the full shell print.
Physical laptop fit, loaded stability, clip durability, creep, airflow and noise
remain separate qualification steps.


# D9 P3 delta (17 September 2026)

Cradle contact from the R4-C bracket profile: R2 seat plus the 1-mm local
relief that seated on the printed V5 C coupon, lid rail moved 3.5 mm outward,
rail 6 mm thick, fence outer face +2 mm, base kept at 4 mm so all feet stay
coplanar. Cosmetic edge treatment on shells, guards and ties (3-mm concave and
1.5-mm convex fillets on print-Z profile corners, 0.8-mm chamfer on tie top
edges, bed edges untouched) with every mating zone protected; air volume of
each module unchanged to the mm3. Pins, keys and fit fixtures identical to P2.


# D9 P4 delta (18 September 2026)

Cradle source R5-C: R4-C plus the 64-mm underside rail (6 mm, 2.25-mm running
clearance, 4 x 2 mm lead-in) at the cradle ends. Fit corrections from the
printed P2 fit plate: pin bores 8.4 mm (BORE_R 4.2), key barbs 7.2 mm wide
(KEY_BARB 3.6, 1.8 mm total interference), T tongue 12.7 mm (TONGUE_H; P4's 12.1 withdrawn). Plate 00
regenerated. Edge treatment and everything else as P3.

Revised the same day: the underside rail is on the plug-end cradle (module 1) only. The far-end cradle keeps the R4-C profile because the rear rubber-foot strip (x 30..323, starting 18 mm further out when undocked) slides through that cradle's x range during docking and would catch on a wall there.

# D9 P5 delta (18 September 2026)

Lean 8 degrees. R7 frame on both cradle ends with the socket void subtracted from the fused cradle; drop-in seat peg and fence peg per end locked by one horizontal fan pin (0.15-mm cam offset, push-out holes); plenum front wall 24 -> 26.5 for the 8-degree lid; plate 08 pegs, plate 09 cradle-end trial. P4 fit corrections kept.

Support-reducing gussets (18 September): ribs or 34-degree wedges under every external socket boss (clipped 0.5 mm clear of the tie envelopes) and a 34-degree wedge on the pin-tip end of each seam tab (bore extended through it). Proven additive-only against the previous geometry; air volume follows the material, audits unchanged.

Splice ring (20 September): two fused arc pairs close the plenum splice. The assembled ring fills 99.9 % of the joint; the only voids are four intentional key clearances. Flanges alternate: back and fan lap M1; front and floor lap M2. The fan-seat plate receives an exact 1.2-mm-deep, 3.85-mm-long pocket and the fan arc replaces that material flush, providing 297.6 mm3 of positive M1 engagement without changing the fan face or airway. The builder now rejects any arc without a positive shell lap and records each engagement volume in the manifest. The upper ring carries the centre foot and cassette fork and needs localized support beneath its opposing flange and fork.

# Codex cleanup: bonded plenum-half joints (20 September 2026)

The three internal pin tabs, pin bores, key slots and support wedges in each
plenum are replaced by a continuous bonded shiplap around the existing shell
wall. The overlap is 20 mm long. Its complementary inner and outer tongues are
1.25 and 1.4 mm thick, with 0.20 mm between their mating faces for epoxy and
print variation. A 0.15 mm recessed land at the air surface receives the final
epoxy wipe without projecting into the nominal airway.

Three broad scallops register each joint: 8 mm radius and 1.5 mm axial depth,
alternating between the two lap ends so the dry joint cannot rock. The scallops
are clipped to the existing wall and never form posts inside the plenum.

This removes six pins, six keys and all six internal boss assemblies. The CAD
build at that revision contained 52 printed parts (46 after the large-shaft clamp
pivot), preserves both nominal air volumes, reports no
part or fan interference, and exports watertight single-component meshes. The
published P5 print kit has not yet been regenerated or superseded.

## Fan-guard cleanup

The two 154 x 132 x 4 mm printed grilles, their eight 7.5-mm standoffs, eight
40-mm printed pins, eight locking keys and eight external socket/gusset
assemblies are deleted. Each fan instead uses a standard 120-mm steel wire
finger guard and four M4 x 35 screws on the normal 105-mm pattern. The screws
pass through the guard and 25-mm fan frame into 3.5-mm diameter, 6-mm-deep
blind pilots in the existing 8-mm flange; they do not penetrate the air wall.

Together with the bonded plenum joints, this reduces the CAD assembly to 34
printed parts. The fan guards and eight screws are now ordinary purchased
hardware. The printed mass and flow obstruction of the old grille system are
removed, while each fan remains independently serviceable.

## Two-piece centre splice

The four functional ring arcs remain because their alternating M1/M2 flanges
capture both plenum halves, but they are no longer four loose puzzle pieces.
The back and front arcs are fused into one upper ring; the fan and floor arcs
are fused into one lower closure. Full-thickness tongue bridges replace the two
internal clip junctions. The remaining two opposite junctions retain the
existing half-lap and peg/socket registration.

The required centre support foot and fork are integral with the upper ring. A
removable narrow contact cassette fits that fork; the three temporary alignment
aids are deleted. Nominal centre-ring fill, plenum air volumes and laptop
clearance remain verified; the revised ring has not yet been physically printed
or Orca-verified.

## One-piece contact cassettes

At each cradle end, the seat peg and fence peg are now one H-shaped cassette.
The two deep channel legs retain the established R2/V5-C seat and the plug- or
far-end fence geometry; a 4-mm deck bridge joins them above the frame web. The
seat and fence are built 2 mm farther in the leaned-up direction, so the laptop
sits 2 mm higher against the tall lid rail. Width remains 16 mm and the existing
single transverse cam pin still locks the complete cassette.

The centre fork takes a third, narrow H cassette built with the same 2-mm lift,
4-mm bridge and short fence profile as the exit side. It is dressed to the M1
shell and upper splice ring so the ring-integral foot and fork remain intact.

The cleanup assembly before the accessory socket is 27 printed parts. The CAD build reports no rigid
interference with the frame, laptop or fans. Physical contact and sliding still
require a printed trial.

### Cassette bore correction and print poses

The first H-cassette implementation raised the contact by fusing each complete
finished peg with a copy translated 2 mm up the lean. That also duplicated each
peg's negative pin bore, producing two overlapping holes in both forks. The
bore cutter was additionally transformed at +8 degrees while the actual pin is
transformed at -8 degrees.

The corrected construction keeps each original contact body, adds translated
material only above the deck split, and explicitly rebuilds the two channel
feet as solid nominal foot volumes. Each end cassette then receives one 8.4 mm
self-supporting teardrop bore using exactly the same -8-degree transform as its
lock pin. The centre cassette has solid feet and no bore because its ring fork
does not use a lock pin.

## Universal plug-end accessory socket

A separate external receiver bonds to a shallow registered recess on the
plug-end cradle. Separating it preserves the cradle's proven broad-face print
orientation: the receiver prints on its closed mounting flange with its cavity
open upward. The joint uses a 1.2-mm perimeter tongue with 0.2-mm clearance for
epoxy and registration; no part of the receiver enters the plenum.

The receiver has a 30 x 40 mm internal section, 39 mm nominal engagement,
4-mm walls and 0.3-mm clearance per side around the cartridge. A broad blind
stop carries axial load. A custom printed 12-mm trapezoidal clamp bolt and
replaceable nut remove play but do not serve as the primary bearing surface.
The installed cartridge carries a polar plug-positioning linkage instead of a
Cartesian mounting frame. A large base pivot sets direction in the Y-Z plane,
a telescoping arm sets radius, and a smaller tip pivot independently aligns the
plug axis with the laptop port. Setup is self-jigging: loosen all three clamp
stages, dock the laptop and insert the plug, let the linkage settle without side
load, then tighten the base pivot, the paired arm-length screws and the tip
pivot. No coordinate measurement is required.

The tip pivot uses a hollow coarse-thread printed screw with a captive annular
head, a replaceable captive nut and two printable thrust washers. The radius
clamp uses two separated printable screws with captive heads to prevent yaw. A
short blind insert remains the fan-stand-only alternative.

Large-shaft face-clamp base pivot (20-21 September, PR #15 concept, PR #16 at
O75, then compacted): the 48-mm base clevis and its annular screw are replaced by
a stationary shoulder carrying a hollow 50-mm shaft. Outward from the dock: an
80-mm backing ring on the cradle plug-end face, a 3-mm skirt narrowing to a 70-mm,
10-mm-thick shoulder plate with twelve 50-degree internal ribs, the smooth journal,
the arm's 70-mm base disc with a 50.5-mm bore, the 10-mm cam spatula, a keyed
2.5-mm pressure washer riding in two journal keyways, and a knurled 72-mm nut on a
47 x 3 mm flat-crested trapezoidal thread (depth 1.15, crest 0.45, 0.35 radial /
0.15 axial clearance, 3 turns engaged, 4 mm spare thread outboard). The nut face
is 71.5 mm outboard of the shoulder-side cradle face. The size floor was set by
face-friction torque (20 N at about 80 mm needs 1.6 N.m; a hand-tight printed nut on
this annulus gives roughly 2.5-4.5 N.m), three turns of 3-mm thread, and finger room
on the nut. The nut lands 0.5 mm inboard of the thread start and the
journal is 3 mm longer than the disc, so the arm never rides thread crests and
the nut clamps before any runout. The angle is held by face friction over the
50-70-mm annulus; the thread only sets preload, and the large diameter does not
by itself remove backlash. The shoulder is bridged from the socket stem and its
skirt and ring are cut clear of the bonded receiver and of the rear-frame-L pin's
extraction path.

The shaft is offset 25 mm lidward of the socket centre. The port datum used by
D1-D7 (`rear_case_seat_z + port_from_rear_case`, `port_y`) puts port 1 only 59 mm
from the socket centre, inside the radius any 75-100-mm shoulder occupies, and the
previous polar arm (tip 108-148 mm from a pivot 59 mm from the port) could not
reach either port at all. From (y 70, z 70) port 1 is 76.4 mm and port 2 86.1 mm
away. The telescoping tip runs 103.5-125.5 mm; the plug carrier is cranked so its
14 x 13 mm window sits 34 mm lateral and 41 mm inboard of the tip. The carrier
block is built in the plug's own frame, rolled to the mean working arm angle plus
the lean (-41.1 degrees) so its faces are square to the plug's major and minor
axes and the rotor only trims roll; it reaches from the cam plate's face (x -49.9) to x -5
and carries an M8 x 3 printed pinch screw (16-mm shank, flat tip) through its 10-mm
wall into a captured scalloped nut. Its other walls are 12 mm on the thin (pivot-side)
face, 5 mm above the window and 18 mm below it: the 18-mm land under the window is
what the cam lobe's face bears on. With 5-mm walls the lobe only caught a 46-75 mm2
sliver of the back face; the land raises that to 375-404 mm2
(the exact figure per pose is `lobe_bearing_area_mm2` in `generated/port-reach.json`).
The block's four long edges (parallel to the plug, i.e. print Z) are rounded r 3.5, its
front face is chamfered 1.5 and the window mouth on that face is flared 1.5 mm at 45
degrees so the plug tip finds the tunnel; the back face is the bed face and the bearing
land, so it is left square. The plug is clamped on the FLATS of its overmold
(USB-IF caps it at 12.35 x 6.5 mm, the 12.5 x 6.5 envelope parameters.json already
carries) between the thin wall and a loose flat 7-mm bearing shim, over the 12.5 mm
of overmold behind the port face, so it cannot roll in the carrier; the screw tip
seats in a round recess on the shim's back. Behind the clamp zone the window is
relieved to r 4.7 so boots up to 9 mm pass. Clamped, the overmold sits 0.25 mm off
the thin wall, so that clamped axis, not the window centre, is the reach target; and
because the rotor trim that squares the window to the port rotates the window about
the tip, the trim is part of the reach solve rather than a free adjustment. The builder solves the arm angle and reach for both
ports, swings the arm there, passes a plug-and-boot envelope through the port and
fails the build on any contact with the dock, laptop or desk.

Stiffness target: no more than 0.5 degrees of plug-axis tilt under 20 N along the
plug axis. The docking push is taken off the arm entirely by a separate cam-lobe
"spatula" plate (10 mm) that rides the same journal outboard of the arm disc and is
pinched by the same nut. Its lobe is a leaf covering about 50 degrees of arc: a
radial near edge 3 degrees along the spiral, a log spiral r = 58 e^(1.2 theta) to
24 degrees (r 96) and a spline tip and back edge. It is rotated until the spiral
runs up to the plug boot; the carrier's back face then bears face to face on the
lobe, so the laptop pushing the plug loads a clamped plate rather than a
cantilever, the edge stops at the boot so the plug and cable still pass, and the
lobe running past the carrier is what keeps higher arm positions viable. The builder solves the cam rotation for each port
and reach, checks the lobe against the sleeve, rotor and a plug-boot-cable
envelope, and records a first-order beam estimate for both directions (docking push
through the lobe and shoulder; withdrawal pull through the 20-mm tongue, 25.6-mm
sleeve and shoulder). Those
numbers are estimates only and exclude the socket cartridge's 0.3-mm-per-side
clearance, clamp-face slip and layer anisotropy; the acceptance test is a dial
indicator on the plug boot at 20 N.

Fan-seat continuity correction: the wall-derived 20-mm plenum shiplap does not
describe the wider fan flange. Applying it to the complete housing had left two
slots across each fan seat at the top and bottom of the 120-mm footprint. Those
missing flange volumes are now restored and divided at the nominal module split
between the two halves. A dedicated thin-face audit requires zero missing seat
volume while preserving the circular opening and four blind screw pilots.

Laptop insertion depth remains independent of connector alignment. The fixed
receiver carries the restored printed M10 chassis-stop screw with +/-4 mm
travel and a replaceable flexible tip. Set it so the laptop closes against the
soft stop immediately before the USB-C plug reaches full insertion; docking
thrust must not bottom out through the plug or either polar-link pivot.

The broad-side poses remain preferred for the two shells and three cassettes.
The laptop-side splice ring is flipped to put its larger flange area on the bed:
the mesh audit reduces non-bed downward-facing area from 2,523 to 1,870 mm2 and
increases bed contact from 65 to 718 mm2. Its alternating M1/M2 flanges lie on
opposite faces, so no flat orientation can place both on the bed; support remains
required below the smaller opposite-side flange. A vertical pose reduces that
support but leaves only about 89 mm2 of bed contact and puts the foot/fork load
across weaker layers, so it is rejected. The fan-side ring remains flat in its
existing pose. Recheck these poses and support interfaces in OrcaSlicer before
printing.
