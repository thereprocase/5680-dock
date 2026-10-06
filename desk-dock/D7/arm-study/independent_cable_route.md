# Rear cable route and fold-animation audit

This is a source-based kinematic review, without rebuilding production CAD.
The original reference cable stub is 6.5 mm diameter and leaves the connector
along -X. The actual cable jacket diameter, bend stiffness and permitted bend
radius beyond that stub remain unmeasured.

## Rear opening and service loop

The carrier's rear return wall at x=-47..-40 blocks a straight continuation
from the stub. The agreed relief is an open-top U-trough centered on
`Y=port_y+dy`, `Z=P+dz`, with R4.25 bottom and a flared exterior mouth.
This gives 1 mm nominal clearance per side around the 6.5 mm reference stub.
An open top permits cable lay-in after removing the cap and its pin; a small
closed hole would require threading a potentially larger connector through it.
The independent cassette review reports 84 zero-intersection sampled checks
covering nominal fit, cap removal/reclosure, cable lay-in and fixed hardware
through the 45 degree fold. See `../cassette-review/cassette-check.json`.
Those are geometric checks against the provisional cable envelope, not
physical cable-flexibility or assembled-load qualification.

The rear outlet rises during folding, even though the metal tip drops. At
the nominal calibration, outlet (-47,port_y,P) reaches approximately:

`(-58.876, port_y-0.8, P+25.630)` at 45 degrees.

Its outward tangent changes from (-1,0,0) to approximately
(-0.707,0,+0.707). A tight fixed downward elbow immediately behind the
holder would oppose the intended release. Leave the near cable free to move
upward/outward and keep the first fixed restraint beyond a loose service loop.

For illustration, print review proposed 30 mm straight behind the wall,
followed by an R30 downward quarter-bend. If this near portion follows the
carrier, its folded centerline reaches x approximately -122.5 and a maximum
height P+55.6. The current keepout adds a 30 mm straight tail below that
quarter-bend, extending the folded centerline to x=-143.73. The full folded
nominal centerline spans x=-143.73..-44.38 and z=P+11.13..P+55.63, before
adding its cable radius. These coordinates are in the unleaned construction
frame. The free loop therefore needs space above the rear outlet as
well as below it. These values describe a provisional visual route, not a
required cable bend radius or a qualified cable sweep. The cable stays well
to negative X, so the fan thickness change does not directly move it into
the fan pockets.

A remote fixed endpoint must remain fixed in an animation. Rigidly rotating
an entire drawn cable falsely moves its far endpoint. Use a visibly loose,
deforming loop and identify its shape as illustrative; do not imply a cable
stretch/force simulation. A rigid near tangent may follow the holder while
the remaining slack changes shape.

## Correct intermediate motion

Use the actual cam lift for every angle:

`lift(theta) = min(0.8, sqrt(1.2^2 + 2*T*abs(theta)/k) - 1.2)`

Here theta is radians, T=1357.5 N mm and k=57.6 N/mm for the current nominal
prototype. The lift saturates at about 3.112 degrees, not at 45 degrees.

The ready viewer meshes already include the 5 degree laptop lean. For the
carrier and every attached cassette, cap, pin, keeper, screw, plug and shim:

1. Undo that lean about (0,0,H).
2. Rotate by theta about Y through (-22,0,P+27.15).
3. Translate by (0,-lift,0).
4. Reapply the lean.

The axle and preload nut perform only step 3 in the unleaned frame. They do
not turn with the carrier, and their thread relationship remains unchanged.
The fixed support, independent chassis stop, two spring mounting screws and
outer spring frame remain stationary.

An equivalent viewer transform uses the world hinge axis
`(0, cos(5deg), -sin(5deg))` through the leaned pivot. Apply its quaternion
with a pivot-compensating translation, then add
`(0, -lift*cos(5deg), +lift*sin(5deg))`.

Do not linearly interpolate ready/folded carrier vertices: that produces
chord motion and can shrink/deform a rigid carrier. Endpoint folded meshes
are useful checks, but intermediate frames need the rigid transform.

## Spring deformation and reset

The spring island translates by the full cam lift. Each ideal fixed-guided
leaf's additional displacement is:

`-lift * (3*u^2 - 2*u^3)` along unleaned Y,

where `u=(38-abs(x-pivot_x))/30` spans 0 at the fixed root to 1 at the island.
The outer frame does not move. The spring's rearward relocation to clear
the thicker fan changes its position, not this displacement law. The
exporter recovers unleaned Z before assigning weights, so its X/Z-based
weight classification is unchanged by the Y offset.

For a mesh-based animation, derive weights from the ready mesh in unleaned
coordinates. Island vertices have weight 1; leaf vertices within its
24 mm Z width have the cubic weight; frame vertices have weight 0. Apply
the leaned -Y displacement vector times each weight. This preserves the
nominal mesh topology. Independently tessellated ready and folded spring
solids may have different vertex order/count and must not be blindly morphed.

Reset reverses the same path. From 45 degrees down to approximately
3.112 degrees, the spring remains at full extra compression. It unloads in
the final part of the rotation and clicks back into its seat. This is a
kinematic illustration of manual reset, not a solved dynamic response.

The current viewer animates direct scene meshes. The software renderer's
redraw signature includes their world matrices, geometry identity and
position versions; its shading cache also includes local quaternion changes.
This covers the present rigid motion and spring deformation. If parent
groups are introduced later, review both cache keys for inherited transforms.
Keep a docking-impact demonstration visibly unmated. The ordinary nominal
docking animation should reset the holder to its ready position.

The static control review found the default fold, docking, inspection and
reset paths mutually reset their conflicting motions. The laptop visibility
checkbox can nevertheless re-show a seated laptop during a fold; prevent or
explicitly explain that combination if the demonstration must stay unmated.
The endpoint checker compares exported CAD and a Python transform at the
fold endpoint. It does not execute the viewer JavaScript or validate its
control state, intermediate timing, impact dynamics or forces.

## Effect of the rear notch on the carrier screen

The earlier reinforced-channel estimate preceded this cable relief. The
plain R4.25 U-notch interrupts the rear tie over the top 4.4 mm of the
18.85 mm bare span at nominal height. At dz=-4, that becomes 8.4 mm. The
larger flared mouth affects the outer part of the rear wall another 2 mm
lower. Removing a small volume does not establish a small stiffness change.

A deliberately pessimistic comparison retains the lower intact channel
(J approximately 14,099 mm^4) and represents the affected upper band using
only the 39 by 7.8 mm positive web (J approximately 5,392 mm^4). With the
same force/eccentricity convention as the previous study:

| Assumed E800 MPa, 20 N | Local torsion proxy |
|---|---:|
| Nominal calibration | 0.049–0.055 mm |
| dz=-4, dy=-3 | 0.082–0.090 mm |

The range treats either the plain notch band or the whole flare-affected
band as the weak segment. This is not a rigorous upper bound: load sharing,
warping and the interrupted-wall transition are not resolved. It remains
a local comparison and does not qualify total holder movement, cam seating
or notch-root fatigue. The full assembled clearance check and a loaded
physical prototype remain necessary. `independent_cable_calculation.py`
reproduces this local screen, the route bounds and nominal fold samples in
`independent_cable_results.json`, using only the standard Python library
and current parameter file. It does not import or rebuild production CAD.
