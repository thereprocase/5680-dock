# D7 connector cassette: printed hardware and service

The connector position, 25 mm cable envelope, USB-C shell and nominal calibration
ranges preserve the D6 source. The cassette remains at the keyboard-left end;
the whole station receives the same 5 degree lean as the laptop.

The cassette has a moving carrier and a separate fixed chassis stop. A broad
keyed shim locates the cassette in the carrier. Its rear shoulder carries the
plug insertion reaction. One printed 8 mm coarse screw and a 5 mm keeper plate
clamp the stack. The removable cap uses a 6.5 mm printed transverse push pin.
The chassis stop uses a printed 10 mm adjustment screw and removable soft bumper.

## Assembly

1. Print the current 8 mm/10 mm screw-and-nut coupons and 6.5 mm cap-pin fit first.
   Select the clearance that works with the actual PETG profile.
2. Fit the keyed shim from above into the carrier's 24 x 20 mm window. Place the
   cassette against its rear and side abutments. Hold the keeper plate below
   the shelf and install the 8 mm hand screw upward through it.
3. Lay the original cable into the open holder from above, with its lead pointing
   out the back along -X. The rear overmold face meets the lower insertion
   shoulder; the cable drops into the open rounded trough and rear-wall notch.
   Neither connector needs to be threaded through a printed hole.
4. Lower the cap, place its rear tongue between the two housing ears, and push
   the 6.5 mm pin toward +Y. The pin head remains on the accessible -Y side.
   The cap completes the upper insertion shoulder and rounded cable clearance.
5. Calibrate height, depth and lateral position using a replaceable keyed shim.
   The parameters encode its thickness, abutment positions and screw-bore
   position. Reprint the corrected shim and holder where their dimensions
   depend on that correction. These are discrete fitted settings, not unlocked
   slots that locate the plug by clamp friction.
6. Screw the independent 10 mm stop into its fixed block and fit the soft tip.
   Set its contact against the actual chassis after correct USB engagement.
   The fixed stop carries seated docking load independently of the moving
   connector holder. Hand-fit with the laptop supported and no docking slam.

To service the cable, unload the laptop, pull the cap pin toward -Y and lift the
cap. The upper cassette geometry stays at Y<=11.5 mm around the pivot head; the
shim extends to Y=17.5 mm below it. The hinge/breakaway calibration is documented
separately by the main D7 assembly.

## Rear cable path and folding

The source model's cylindrical rear stub is 6.5 mm in diameter and leaves the
overmold along -X. The continuation diameter is not measured Dell cable data.
The printed holder now has an 8.5 mm round-bottom trough, open upward when the
cap is removed. Its rear-wall mouth flares to 12.5 mm over the outer 2 mm of
wall thickness. The cap's rounded underside closes above the lead without
requiring the lead to pass through a closed loop during assembly.

Reserve a loose loop outside the back of the moving carrier. The screening
example continues straight for 30 mm past the rear wall, then bends downward
at a provisional 30 mm centerline radius. The 8 mm clearance envelope is
larger than the modeled 6.5 mm continuation. Neither the assumed diameter nor
the bend radius establishes the real cable's flexibility or required slack.
At release the rear outlet rises and its outward tangent turns upward; the
first part of the lead must be free to follow that movement. Keep a fixed
clamp or rigid elbow away from the outlet and check actual cable resistance.

The isolated check transports this illustrative loop with the carrier through
0..45 degrees and checks it against the fixed local hardware. This is geometric
clearance for that loop, not a cable-tension model or a guarantee for a fixed
remote cable endpoint. Main-shell, fan and real cable checks remain separate.
The exported `rear_cable_clearance_keepout_NONPRINT.step` is a clearance volume,
not a printable component or a measured cable model.

The notch interrupts the carrier's rear torsion wall. At nominal height its
round-bottom opening leaves 21.75 mm of continuous lower wall; at the minimum
height setting this falls to 17.75 mm. The exterior flare interrupts the outer
2 mm of wall thickness a further 2 mm lower. Stiffness estimates made before
the notch require revision; removal volume alone does not establish stiffness.

## Printable interfaces

- Calibration lock: custom 8 x 2 mm trapezoidal thread, 6.7 mm solid core, 20 mm hand
  knob and 7.2 mm threaded base. Under-head length is 23.9 mm plus the selected
  height correction. Its tip remains 0.85 mm below the nominal overmold bottom.
- Keyed shim: 0.35 mm clearance per face; height 5.1 mm plus correction, which is
  1.1..10.1 mm over the requested height range. The downward key is 4.3 mm deep.
- Cap pin: 6.5 mm shaft, 6.8 mm bores, 14 x 4 mm head. Two rounded 6.9 mm retention
  lands create 0.05 mm nominal radial interference in the receiving housing.
- Stop: custom 10 x 2 mm thread, 8.7 mm solid core, 24 x 6 mm hand knob, 18 mm threaded
  length plus a 3 mm smooth 8 mm stem. The fixed threaded block engages 12 mm.
- Bumper: 12 mm outside diameter, 4 mm long, 8.2 mm socket over the 8 mm stem.
  Print in a flexible material or use an equivalent removable soft contact.
  Socket retention must be fitted on a coupon; the current clearance is a
  starting point and does not establish retention.

The custom screw pairs are generated with real helical profiles and are not
ISO metric threads. Default female clearance is 0.25 mm radial and 0.15 mm axial
per flank. Screw/nut phase follows the assembled datum, including fractional
pitch offsets. Do not replace the custom mates with off-the-shelf metric nuts.

The cap has a broad pressure land over the cable body. Its default 0.30 mm
squeeze allowance is provisional. It intentionally overlaps the nominal soft
overmold reference in CAD; it does not establish actual contact pressure.
Calibrate against the real cable. Rear shoulder contact supports insertion;
extraction retention depends on overmold friction and requires a measured pull
test before docking use. The USB shell and actual overmold references retain
their source dimensions.

## Printing and verification

Print hand screws with their knobs flat on the bed and thread axis upright;
print nuts with thread axis upright. Print the cap pin on its head. The cap,
keyed shim, keeper plate and holder need orientation/support review around the
rear clevis, upper pressure land and underside key. These features are not
claimed support-free. Keep material out of the bores and thread roots when
removing supports.

`printed_fasteners.py` exports six 8 mm/10 mm nut coupons at 0.20, 0.25 and
0.30 mm radial clearance, matching 8 mm/10 mm screws, and an optional 12 mm
example (nine STLs total). `cassette_fit_coupons.py` exports three 14 x 8 mm
receiver rings with 6.8, 6.9 and 7.0 mm bores. Use the actual exported cap pin
as their male sample. These rings screen diameter and friction; their short
round walls do not reproduce the complete housing's compliance or retention.
They also print their bores vertically, whereas the assembled cap's 6.8 mm
pin bore prints horizontally in the supplied cap pose. Confirm that bore on
the actual cap; a good upright-ring fit does not establish a horizontal fit.

The revised cap remains inverted on its rear clevis. The current mesh is
32.60 x 24.27 x 10.10 mm and its section 0.1 mm above the bed is 90.2 mm².
The broad cap face starts 2.5 mm above the bed and needs accessible support.
The new cable trough opens upward in this pose; it adds no enclosed cable
tunnel. Review the horizontal pin-hole roof and remove support from the
gripping faces before fit testing. `cassette-review/cap-print-pose-review.json`
records this mesh-only orientation check.

`cassette_isolated_check.py` exports the nominal local parts and records critical
mating intersections in `cassette-review/cassette-check.json`. Intentional
exceptions are the cap's overmold squeeze, the pin's small retention lands and
the fixed stop joining the fixed support. This is an isolated nominal check;
the translated upper cap and pin are also checked against the reinforced
carrier at the eight requested adjustment corners. This does not qualify
the regenerated shim/base, full laptop/duct sweep or all combined adjustment
extremes. The actual print must establish thread fit, pin pull force, overmold
retention, warm creep and the breakaway response before load-bearing use.
