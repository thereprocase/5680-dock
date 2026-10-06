# Independent D7 plug-arm stiffness screening

The current narrow C bracket should be redesigned before a 20 N engagement
load is treated as qualified. Both its vertical spine and bottom return are
flexible bending members. Increasing only the spine thickness leaves the
bottom return and the shell attachment as major sources of compliance.

This is an independent read-only CAD analysis. It does not establish a material
allowable, printed strength or a safe working load. The modulus values below
are requested sensitivity assumptions, not measurements of the user's PETG.

## Actual load path in the source

In `cassette.py`, the shelf is x=-40..-0.6, y=-18..25 and
z=P-24..P-18.7, with two broad adjustment slots. Its thickness is 5.3 mm.
The vertical spine is only 6 mm in X by 7 mm in Y, at x=-40..-34,
y=18..25. A 7 by 6.3 mm bottom return runs to x=15 at z=26.7..33.

The shelf joins the top of that spine. The return appears to meet the main
plenum primarily through its 2.4 mm end wall at x=-7..-4.6. Above z50, the
large plenum tower begins near x22, so the shelf is not backed by a tall solid
body immediately beneath it. The continuing part of the return inside the
duct is not automatically a second fixed support.

The reference port force is along X. Its Y coordinate is 2.231 mm, while the
spine center is y21.5: this creates a 19.269 mm sideways lever. The port is
21.35 mm above the shelf midplane. A 20 N axial force therefore applies
427 N mm bending moment and 385 N mm twisting moment at the spine top.
The 5 degree lean is a common rigid rotation around X; it does not remove
these lever arms for an X-directed force.

## Screening model and results

A two-member Euler–Bernoulli frame represents the bottom return and spine.
The return centerline is 31.2 mm from the wall center to the elbow. The spine
centerline is 68.779 mm long. The shell connection is provisionally fixed for
this calculation: this is an optimistic member-only boundary, not a claim
that the thin shell or whole stand supplies perfect fixity.

The in-plane frame solution independently reproduces the hand strain-energy
calculation to within numerical precision. A Saint-Venant rectangular-section
torsion approximation adds the off-center effect using assumed Poisson ratio
0.38. Shear deformation, fillets, section warping, printed anisotropy, local
stress concentration and material nonlinearity are omitted.

| Assumed E | Current spine bending | Spine eccentric torsion | Bottom-return bending and axial terms | Linearized member sum |
|---|---:|---:|---:|---:|
| 0.8 GPa | 47.78 mm | 7.22 mm | 45.07 mm | 100.06 mm |
| 1.2 GPa | 31.85 mm | 4.81 mm | 30.04 mm | 66.71 mm |
| 1.8 GPa | 21.24 mm | 3.21 mm | 20.03 mm | 44.47 mm |

These enormous values violate small-displacement assumptions. They are an
alarm that this open-bracket geometry is inadequate, **not predictions that
the real dock will elastically move by those distances**. Contact, yielding,
large rotation, slipping or failure can intervene much earlier. The linear
base bending stresses are approximately 42.9 MPa in the spine and 38.9 MPa in
the return, before concentration factors; no pass/fail strength judgment is
made from those figures.

For reference, the spine bending displacement contribution is:

`F / (E Iy) × (L³/3 + hL² + h²L)`

Here `Iy = 7×6³/12 = 126 mm⁴`, `L=68.779 mm`, and `h=21.35 mm`.
Ignoring h would miss more than half of this member's port displacement.

## Practical design directions within the station envelope

**Preferred load path to study:** connect the shelf's lid-side edge directly
to the nearby plenum tower at x approximately 22..25 and z approximately
80..100. A 20–30 mm-deep beam or web at y18..25 would transmit much of the
engagement force axially along X, removing the long spine/return bending
chain. This lies outside the modeled laptop lid at unleaned y11.085 and
within the current station's y25 extent. It needs a broad landing into the
tower side wall and adjacent roof; merely touching the 2.4 mm shell wall
does not make that wall rigid. Root must check its actual intersections,
air-path effect and docking clearance before adopting it.

**If retaining the lower bracket:** use two triangular cheeks, initially
4 mm thick, at approximately y=-18..-14 and y21..25. Join them with a
full-width back spine and bottom tie. Their diagonals should run from the
high shelf/spine region near x=-37,z99 to a broad shell landing near
x=-7,z48. Preserve the existing total envelope and add root fillets, rather
than a detached brace or extra assembly part. The second cheek brings the
section center toward the port and reduces the large one-sided twist.

An idealized in-plane frame with two 4 mm cheeks, represented by 16 mm-wide
diagonal load bands, gives 0.664/0.442/0.295 mm at the three E values.
An 8 mm-wide band assumption instead gives 1.257/0.838/0.559 mm. These
figures only compare bracing topology: they assume two fixed shell
attachment elevations and omit plate/shelf, root and bolt compliance.
They do not qualify a finished gusset design.

The two M3 hand controls and washers need clear access through the complete
adjustment range. Their nominal screw centers are x=-14,y=±8; adjustment
adds ±5 mm X and ±3 mm Y. The 14 mm washers can reach y18. Keep the high
lid-side tie at y>=18 with clearance, or deliberately relieve its underside
around the complete washer and finger-access envelope. Place diagonal
cheeks below the knob region rather than erecting vertical obstructions
alongside the knobs. No production geometry was changed in this study.

## Shelf, fasteners and root remain part of the stiffness budget

At E=1.2 GPa, a full-width idealized shelf gives roughly 0.23 mm displacement
from its off-center torsion, or roughly 0.33 mm for a 23 mm cantilever with
the port's overturning couple. These are separate simplified plate models,
not independent effects to add blindly. The actual one-corner root and
large adjustment slots make a rigid-shelf assumption inappropriate. A
5.3 mm plate can still dominate after the arm is braced. A deeper shelf
section or integral ribs should be checked with the hand-control clearance;
uniform downward thickening would require relocating the knobs and choosing
longer screws.

The two M3 locks lie on the same X coordinate. They can clamp the cassette,
but they do not form a bolt pair separated along X to resist the port-height
overturning moment directly. That moment is about 274 N mm at the cassette
base and 374 N mm at the shelf surface. The joint relies on preload and
distributed contact over the shim footprint.

The purely axial friction condition is `total preload >= 20 / mu`.
For assumed friction coefficients 0.15/0.20/0.30, this is 133/100/67 N
total, before allowance for eccentric traction, vibration or creep. These
friction values and preloads are not verified. The small Y offset from the
bolt-group center changes the two nominal axial shares to about 12.79 and
7.21 N. The long adjustment slots provide no positive restraint until a
shank reaches a slot end. A fitted calibration stop/shim or other positive
axial registration would make retention less dependent on unknown hand
torque, while remaining removable by hand.

Finally, a root rotation budget of just 0.1 mm at the port would require
about 1.62 million N mm/rad rotational stiffness for the present 90.13 mm
height above the return root; a 0.1 mm translational budget requires
200 N/mm. These are required stiffnesses, not asserted shell properties.
The thin wall, its attachment to the roof/floor, removable panels, bridge
keys and desk restraint must all be included in a complete test or model.

## Reproduction

Run `independent_arm_study.py` in this directory using the existing local
Python/NumPy environment. It writes `independent_arm_results.json` and
cross-checks the hand in-plane result against a separate frame stiffness
matrix. No production CAD is imported, rebuilt or edited.
