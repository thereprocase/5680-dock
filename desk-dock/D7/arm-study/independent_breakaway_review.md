# Independent review of the printed face-cam breakaway

The proposed hinge is a workable calibration-prototype topology for an
**unmated, misaligned docking impact**. Its nominal spring and cam equations
are consistent. Neither those equations nor a clear CAD sweep establish a
50 N impact ceiling, reliable printed alignment at 20 N, or protection of a
partially engaged USB-C connection.

This review is read-only. Production geometry was being revised in parallel;
`independent_cam_results.json` records the source hash used for the final
height-profile calculation. The root agent separately checks complete CAD
clearances, including the subsequently added 45 degree stop and conical pilot.

## Cam geometry versus its analytic lift

The original 20 degree crown was one ruled loft. Its radial walls were long
straight chords, and rotating an identical male tooth inside its negative
could bind radially despite the correct axial lift. The revised eight-part
crown reduces the maximum r24 chord error to 0.00571 mm. The 0.15 mm female
radial relief addresses that source of nominal interference.

For each ramp facet, intersecting a polar ray with the chord between adjacent
radial loft wires gives interpolation fraction:

`t = sin(theta-theta0) / [sin(theta-theta0) + sin(theta1-theta)]`

The actual ruled height is the linear interpolation using t. Across the
3.111826 degree ramp, the smooth requested lift is conservative by at most
0.000741 mm relative to this height. This does not itself prove the remaining
radial, pilot, stop or assembled CAD clearance.

The 12 ramp facets do not give mathematically constant torque. Their slope
is nearly constant within each facet while spring force increases. With
the nominal ideal spring, the calculated frictionless torque ranges from
1310.64 to 1404.37 N mm, versus the intended 1357.5 N mm. Increasing the
number of ramp facets would reduce this small sawtooth; friction and printed
fit are likely larger uncertainties and must still be measured.

## Spring calculation and calibration

Two ideal fixed-guided leaves with L30, b24 and t3 mm give:

- Combined stiffness: `2 E b t^3 / L^3` = 57.6 N/mm for assumed E1200 MPa.
- Preload at 1.2 mm deflection: 69.12 N.
- Force after the additional 0.8 mm cam rise: 115.2 N.
- Energy stored over that rise: 73.728 N mm = 0.073728 J.
- Maximum ideal surface strain: `3 t delta / L^2`, or 1.2% initially and
  **2.0%** at full lift. The earlier 1.57% estimate does not apply to these
  shorter leaves.

These values assume rigid leaf roots and a rigid central island. The outer
cartridge frame is attached by two screws near its center, so its outer
leaf roots can also move. A rough four-rail cantilever sensitivity gives
about 407.5 N/mm frame stiffness and 50.5 N/mm combined stiffness in series
with the leaves, approximately 12% below the leaf-only value. This is an
illustration of omitted compliance, not a validated frame correction.

Actual modulus scales the release torque of an already-printed cam. At
E800/E1200/E1800 MPa and otherwise unchanged assumptions, the smooth nominal
release equivalent scales approximately 33.3/50/75 N. The geometry is a
calibration cartridge, not a material-independent force limiter. Raising
preload alone to compensate for a low-modulus print increases peak strain:
ideal E800 would need about 1.8 mm preload, followed by 0.8 mm lift, reaching
2.6% ideal strain. Prefer calibrated cartridge dimensions and a controlled
preload range rather than unrestricted nut tightening.

The present nut needs a clear preload datum, limited spacer selection or
equivalent adjustment constraint. A deflection stop must still leave the full
0.8 mm release travel at the largest permitted preload. Otherwise a user can
protect the spring while unintentionally preventing the breakaway from
releasing. PETG stress relaxation, temperature and repeated cycles must be
checked after setting the preload.

## Force direction and retreat

At the nominal metal-tip center, the pivot has equal 27.15 mm X and Z lever
arms. Opening torque at zero rotation is:

`M_y = -27.15 × (F_x + F_z)`

Thus a pure -X load and a pure -Z load each correspond nominally to 50 N.
An equal diagonal -X/-Z load corresponds to only 35.36 N resultant. A pure
Y-directed load does not actuate this hinge through the same torque. Opposed
X/Z components can cancel. Impact contact elsewhere on the tip, and the
available cassette height/depth adjustments, change these levers.

During positive-Y folding, the -X moment arm increases and the -Z moment
arm decreases. Including both changing lever and ramp facets, the idealized
force equivalent across the ramp ranges approximately 47.03–51.49 N for
-X, and 48.27–53.68 N for -Z. These numbers omit friction, cone seating,
moving inertia, cable forces, frame compliance and material variation.

| Fold angle | Tip outward movement (-X) | Tip downward movement (-Z) | Carrier movement (-Y) |
|---|---:|---:|---:|
| End of ramp, 3.112 degrees | 1.514 mm | 1.434 mm | 0.800 mm |
| 10 degrees | 5.127 mm | 4.302 mm | 0.800 mm |
| 30 degrees | 17.212 mm | 9.938 mm | 0.800 mm |
| 45 degrees | 27.150 mm | 11.246 mm | 0.800 mm |

The 45 degree stop matters: beyond that point the tip starts rising again.
The spring stores only about 0.074 J over its release rise; remaining impact
energy can reach the folded stop. Dynamic peak force is therefore not bounded
by the quasistatic setting. The first 3 degrees also introduce downward and
sideways motion before much axial retreat, so a partially engaged connector
is a distinct test case, not automatically protected by the unmated sweep.

## Alignment and reset

The original 10.4 mm rotor bore over the 10 mm pin has 0.2 mm radial clearance.
It should guide folding rather than establish precise seated alignment. The
added shallow conical pilot is a reasonable centering feature if it clears
fully within the cam's available lift. Its friction and wedging contribute
to the measured release force.

An exact conical pilot and three exact cam teeth are redundant mating
surfaces for a printed fit. If the pilot is proud, the angular seats may not
fully engage; if the cam seats are proud, the pilot may not center. The
coupon should include their relationship and verify radial/rotational
repeatability together. A 0.2 mm whole-holder movement budget corresponds
to only about 0.42 degrees at a 27.15 mm lever, before beam, carrier and
fastener deformation consume any of that budget.

After the ramp, the faces are on a dwell and there is no restoring cam torque
until the user rotates the carrier back near the seated region. That is
compatible with a manual click-back reset. Preload and friction determine
the feel and repeatability; the rigid chassis stop should remain attached
to the fixed body.

The earlier `arm_stiffness.py` study describes an 18×48×4 mm tube at a
66 mm span and y18 datum. The new fixed support is 24×48×4 mm at y26,
with a post, hinge, spring cartridge and moving carrier. The earlier beam
result must not be presented as qualification of this complete holder.

The earlier moving carrier had a 7.8 mm-thick, one-sided vertical web. Its
approximately 19.7 mm Y offset from the plug introduces torsion. A simple
rectangular-section screen of only the roughly 19 mm bare web below the hub
gives about 0.14 mm tip movement at E800 MPa and 20 N, before other compliance.
This is not a complete carrier model, but it makes a rigid-cassette transfer
assumption questionable. Thickening the web toward -Y or adding a shallow
return rib should be checked against the final cassette adjustment envelope.

## Follow-up: reinforced three-sided carrier

This subsection records the reinforcement before the later cable notch.
The notch consequence and animation review are recorded separately in
`independent_cable_route.md`; the values below should not be used unchanged
for the notched carrier.

The revised carrier adds a rear wall at x=-47..-40, y=-28..25.8 up to P+13,
and a negative-Y cheek at x=-47..-8, y=-28..-20.4 up to P+1. The positive
web is x=-47..-8, y=18..25.8. These create an open three-sided channel
through the previously identified bare torsion span.

The shelf top is P-18.7 and the round hub begins at P+0.15, giving an
18.85 mm bare span. All three walls cover this span; the negative cheek
overlaps the hub's bottom elevation by 0.85 mm. Its termination and the
transition through the rear wall into the hub still need the complete
geometry/loaded-part assessment. Merely overlapping elevations is not a
claim that the entire hub behaves as a rigid end restraint.

The proposed open-section estimate using full plate lengths is approximately
17,364 mm^4. Using wall centerlines to avoid double counting corners gives:

`J ≈ [46.1×7^3 + 35.5×7.8^3 + 35.5×7.6^3] / 3 = 16,081 mm^4`

Applying finite-rectangle aspect-ratio corrections separately to those walls
gives a sensitivity estimate of approximately 14,099 mm^4. Neither is an
exact torsion solution for the thick, joined, finite-length channel. It is
an open section; a closed-box torsion formula would be inappropriate.

Keeping the same conservative 19.669 mm force eccentricity as the previous
one-sided-web comparison gives the following local contribution at 20 N:

| Assumed modulus | Earlier single web | Revised three-sided span |
|---|---:|---:|
| E800 MPa | 0.144 mm | 0.031–0.036 mm |
| E1200 MPa | 0.096 mm | 0.021–0.024 mm |
| E1800 MPa | 0.064 mm | 0.014–0.016 mm |

The reinforcement therefore supports an approximately fourfold reduction
of the previously flagged **local** torsional contribution. This comparison
does not calculate the revised shear-center position, constrained warping,
upper section transition, slot/cassette compliance, cam/pilot contact,
fixed support or whole-holder alignment. It must not be substituted for
the complete 0.2 mm deflection budget or a loaded repeatability test.

The new moving axle collar is also consistent with the intended preload
limit: its upper face and the nut bearing face both lie at
`Y=61+spring_offset-1.2` (85.8 mm for the current 26 mm spring offset).
Because collar and nut translate with the axle during release, this limit
does not intrinsically consume the additional 0.8 mm spring stroke. The
10.5 mm collar clears the 10.7 mm island bore nominally. Its threaded-nut
contact, printed clearance and resistance to forced over-tightening remain
fit/load checks; it is an adjustment limit, not a measured spring preload.

## Recommended prototype checks

Use the finished calibration position and actual cable. Check retained
alignment at 20 N, directional quasistatic release, repeatable reseating,
preload relaxation and cable reaction. Include downward, axial and diagonal
misaligned contacts, and distinguish fully unmated from partial engagement.
Check after repeated resets and representative warm dwell. Keep the result
as a calibrated prototype until those measurements exist.
