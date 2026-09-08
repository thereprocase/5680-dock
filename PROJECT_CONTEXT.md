# Project context and maintainer handoff

This is the durable engineering context for the Precision 5680 desk dock as
of 2026-09-08. **D7 is the active design.** Its new home is
[`thereprocase/5680-dock`](https://github.com/thereprocase/5680-dock), with the
[project site](https://thereprocase.github.io/5680-dock/) and
[interactive model](https://thereprocase.github.io/5680-dock/desk-dock.html).
Earlier repository history and studies are retained so decisions and source
geometry can be traced. This handoff records project decisions and evidence;
it is not a transcript or a substitute for current CAD and manifests.

## Intent and everyday use

Make an elegant, compact stand for a closed Precision 5680 at the edge of a
desk. The hinge points down, the lid faces the user and fans, and the underside
intake remains exposed. The plenum serves as the laptop support, avoiding
separate tall guides that duplicate its function. Two shaped end seats carry
the laptop's weight; soft plenum contacts take its lean. Seals guide airflow
and are not structural bearings.

Lower the laptop onto the seats at the withdrawal offset, then slide it
sideways into the captured original host-cable plug. Withdraw sideways before
lifting. The modeled withdrawal is 18 mm. The viewer's 135 mm lift is a
presentation distance, not a required stroke or an automatic sequencing
mechanism. This is a mechanical cable holder and extraction stand; the dock
electronics remain external.

The accepted direction is fewer useful parts, open access, smooth loading
and compact desk depth. A troublesome loading-end tab was removed. Two small
thrust tabs became one **continuous low lip**, split only at the plenum seam;
the requested change was continuity, not taller retention walls. The 12 mm
lip stays below the modeled rubber-foot keepout. Do not restore separate lid
guides or a tall loading-end obstacle without addressing why they were removed.

## Revision history and superseded assumptions

| Stage | Main contribution | How to use it now |
|---|---|---|
| Earlier 5560 wall mount | Wall-mount geometry, materials, print packages and CFD studies | Historical project branch; not a 5680 desk-dock qualification |
| D1 | Dell source extraction, hinge-down concept, adjustable original-plug cassette and separate stop; flat slim fans | Source provenance and initial concept; wrong-end orientation and incomplete assembly details were superseded |
| D2 | Nearly upright fans and lower/slide/withdraw/lift animation | Historical motion study; orientation and fan discharge changed later |
| D3 | Attempt to match the photographed far docking end | Its stated correction did not resolve the later-discovered CAD/raster reflection problem |
| D4 | Upward 15° discharge, rounded mouths, curved passages and conditional airflow sizing | Useful airflow reasoning; larger, older geometry and fabricated guard concept |
| D5 | Profiled guides, 2° laptop lean, open ribs and expanded rubber-foot keepouts | Contact-source evidence; guides, lean, fan geometry and mirrored CAD were superseded |
| D6 | Independent port study; removal of reflection; 5° lean, direct plenum bearing, 18° discharge and compact plenum | Orientation/contact and airflow baseline inherited by D7 |
| D7 | Recessed fan pockets, slide-in printed grilles, service covers, printed hardware, continuous low lip, reinforced/resettable cassette and cable passages; final 25 mm fans | Active development prototype; use regenerated geometry, manifests and checks |

Older reports may call their revision “current,” use ASA, specify 15 mm fans,
or claim an orientation correction that predates D6's independent audit.
Keep those statements attached to their original revisions. The original
root overview is at [docs/history/5560-README.md](docs/history/5560-README.md).
Root-level wall-mount scripts and reports are retained history; start current
work in [desk-dock/D7](desk-dock/D7/).

## Handedness and coordinate contract

**Both Thunderbolt 4 ports are on the keyboard-left edge.** With the closed
laptop hinge-down and viewed from the lid side, this is image-right, at the
far plug station. The opposite keyboard-right USB-C port supports USB 3.2
Gen 2 / DisplayPort. Do not label it Thunderbolt.

D5 reflected the CAD about the laptop midpoint. A reversed camera basis in
its still-image renderer concealed the reflection; a browser camera exposed
it. D6 removed the mirror and checked port voids, solid opposite edges, plug
side and projection separately. A screenshot that looks right is insufficient
evidence of a correctly handed solid.

In the unleaned construction frame:

- X=0 is keyboard-left and the plug station; X increases toward keyboard-right.
- +Y is toward the lid, user and fans; -Y is toward the underside intake.
- +Z is upward. The rear-case seat datum is Z=54 mm.
- The plug enters along +X. The laptop docks along -X and withdraws +18 mm.
- Apply the 5° rigid lean about X after construction. Use proper rigid
  transforms; no reflection is permitted.

The selected rear Thunderbolt center is 65.979 mm from the rear-case datum,
at thickness coordinate +2.231 mm; the second is 82.192 mm from that datum,
with its own +1.915 mm thickness coordinate. Nominal laptop dimensions are
353.68 × 240.33 × 22.17 mm. These come from Dell-linked visualization geometry,
not toleranced factory connector drawings. Physical calibration is necessary.
Read [D6 PORT_STUDY](desk-dock/D6/PORT_STUDY.md) and its extraction record
before changing reference transforms.

## Current geometry and service decisions

The laptop leans **5°**. Fans discharge **18° upward in the desk/world frame**;
their planes are 18° from vertical. The fan angle is independently posed,
not 18° added to the laptop lean. The compactness request suggested a few
extra degrees of fan kick; the existing 15° baseline plus the selected
additional 3° produced the retained 18° world angle.

The compact plenum keeps a fan pose anchor at Y=58, Z=72 mm. Final fans are
**120 × 120 × 25 mm**. Their thicker frames grow outward while keeping the
suction face at the prior location, preserving the inlet passage. Historical
`fan_center_y/z` fields are pose anchors; with 25 mm fans they are not the
actual frame centers. Read `fan_depth_datum` in the parameters. Do not simply
center a thicker fan on the old 15 mm frame center.

D6 selected this depth using an assumed 30 CFM total flow, a chosen inlet
allowance and sampled cavity rays. It did not find a measured airflow optimum.
Its slim-fan example does not specify the final 25 mm fan model. Check the
actual fan, vibration pads, connector and lead exit. See
[AIRFLOW_STUDY](desk-dock/D6/AIRFLOW_STUDY.md) and regenerated D7 airflow
records for the geometry and calculation scope.

Fans lower into open-top pockets. Printed grilles slide in rails and close
the top; small friction lands replace loose fan-retaining screws. Remove
the laptop before service and allow the documented inclined removal travel.
Bottom panels expose the ducts and close around fan wires laid into open
edge saddles. Shell tie lugs retain fan wiring when covers are off. Use
accessible loops or disconnects; do not attach the moving USB lead to fixed
fan-wire tie points. Cable ties are service accessories, not precision
locators or substitutes for the printed body fasteners.

## Printed hardware and plug calibration

The user selected **Bambu Lab P1S, PETG and a 0.4 mm nozzle**, with hand
assembly and printable screws, nuts and pins. Small metal fasteners and the
earlier metal front-clip approach were superseded. Examples include 8 mm
coarse clamp threads, 10 mm stop/preload threads, a 10 mm hinge axle and a
6.5 mm cap pin. These follow the direction to avoid tiny printed hardware:
pins at least 6 mm and threads at least 8 mm.

The thread pairs have actual matched custom helical profiles; their nominal
diameters are not claims of ISO metric interchangeability. Check coupons
and actual horizontal bores with the chosen process. Fans, the original
cable, electronics and compliant contacts remain external components;
this is not an all-PETG electronic dock.

The cassette uses a broad keyed replaceable shim, one printed lock and a
lower keeper. Height, lateral position and insertion depth are encoded in
the fitted parts, rather than left sliding on friction-locked slots. Ranges
are Z=-4..+5, Y=-3..+3 and X=-5..+5 mm. Regenerate affected parts for the chosen
calibration; these ranges do not reach the other Thunderbolt port. A lift-off
cap and transverse pin retain the overmold. Nominal squeeze is a fit assumption;
extraction retention requires a pull test. The USB shell must not act as a
guide, bearing or chassis stop. See
[CASSETTE_ASSEMBLY](desk-dock/D7/CASSETTE_ASSEMBLY.md).

## Alignment and resettable breakaway

Targets are **no more than 0.20 mm complete-holder axial movement at 20 N**
and a **50 N-class resettable release for a misaligned, unmated docking
strike**. These are acceptance targets. The independent fixed chassis stop
already limits seated travel; the breakaway is not a 50 N protection rating
for a mated USB-C port.

A printed face-cam hinge turns about Y, with its pivot 27.15 mm above and
27.15 mm behind the nominal metal tip. Three cam teeth and a shallow conical
pilot locate the ready position. The clearance-fit axle guides motion; it
is not the sole precision seat. Two replaceable PETG leaves preload the cam
through a hand nut. A shoulder limits nominal preload while allowing extra
cam travel. The spring moved rearward to clear the final 25 mm fan rails;
read its current offset from parameters, not old images.

Each nominal leaf is 30 × 24 × 3 mm, initial deflection is 1.2 mm and extra
cam lift is 0.8 mm. The ideal combined rate is 57.6 N/mm at assumed E=1.2 GPa.
The energy-shaped ramp aims for 1.3575 N m, reaches full lift near 3.112°,
then permits manual folding to the 45° stop. The tip retreats outward and
down. Return it by hand to seat and reset. Print the spring's **unloaded
export**, not its deflected assembly appearance.

Friction, conical contact, finite cam geometry, spring-frame compliance,
anisotropy, temperature, creep and cable reaction affect release. The nominal
50 N interpretation applies separately to axial or downward force at the tip.
An equal diagonal load gives the same moment at roughly 35 N resultant;
lateral Y loading does not trigger this hinge. Adjustment changes lever arms.
Static release is not an impact-force ceiling, and partially engaged contact
needs separate assessment.

The member calculation and local carrier screen are distinct. At assumed
E=0.8 GPa and 20 N, the brace's worst calculated axial contribution is about
0.07945 mm. The cable notch raises the local carrier torsion proxy to about
0.049-0.055 mm nominal and 0.082-0.090 mm at the adverse low/lateral setting.
These do not solve every joint or prove the complete 0.20 mm target. Do not
reuse the smaller pre-notch estimate or treat removed volume fraction as a
stiffness result. The [holder study](desk-dock/D7/arm-study/HOLDER_AND_BREAKAWAY.md)
and independent calculations retain the derivations and boundaries.

## Rear USB cable and animation

The rear lead exits along -X through an **8.5 mm open-top rounded trough**.
Its mouth flares to 12.5 mm over the outer 2 mm of the carrier wall. Removing
the cap and pin permits lay-in without passing either connector through a
closed hole. The source stub is 6.5 mm diameter; this does not establish the
actual cable diameter farther along the lead.

Reserve loose cable outside the carrier. The illustrative clearance path has
30 mm of straight lead beyond the wall, an **assumed R30** downward bend and
a short tail. Actual minimum bend radius and needed slack are unmeasured.
The rear outlet rises about 25.63 mm during a 45° fold even while the tip
drops, so a tight downward elbow or immediate fixed clamp would oppose the
release. The actual far cable endpoint stays fixed and the loop must deform.
A transported rigid keepout is a geometric screen, not a flexible-cable or
tension model. See the
[independent route audit](desk-dock/D7/arm-study/independent_cable_route.md).

The viewer moves carrier parts with a rigid pivot rotation plus axial cam
lift. The axle/nut translate; spring leaves deform while their frame stays
fixed. Reset reverses the path. Exploded offsets are explanatory, and the
slow fold is kinematic; neither simulates force nor establishes a physical
assembly/removal sequence. Describe endpoint and intermediate checks according
to the current validation report, not as physical qualification.

## Evidence, reproduction and publication

Start with the [D7 review](desk-dock/D7/REVIEW.md),
[print preparation](desk-dock/D7/PRINT_PREPARATION.md), `parameters.json`,
`geometry.json`, `print-manifest.json` and `package-manifest.json`.
Validation records cover solid/mesh validity, selected intersections,
sampled docking/service motion, source hashes and stated exclusions.
Intentional soft-contact squeeze, grille friction lands and matched seats
must be distinguished from accidental interference. A passing check applies
only to its geometry and sample set; compare source hashes after edits.

Editable generation is in `desk-dock/D7/build.py` and the body, fan, cassette,
printed-fastener and breakaway modules. Importing `build.py` can regenerate
outputs. Use isolated checks for one interface; then regenerate the complete
STEP, meshes, viewer and package together. Repository Python requirements
include CadQuery and analysis/rendering libraries; review the relevant script's
imports and documented working directory. Serve the viewer over local HTTP
from `docs` or the repository, rather than opening HTML directly from disk.
The viewer uses vendored JavaScript dependencies.

The current package is
[desk-dock/D7/Precision_5680_D7_Review.zip](desk-dock/D7/Precision_5680_D7_Review.zip),
mirrored under [docs/downloads](docs/downloads/Precision_5680_D7_Review.zip)
for Pages. Keep both copies consistent with the manifest. Publishing a
review archive does not make it a qualified print release. The old repository's
Git ancestry, source and evidence are preserved in this home; do not assume
old wall-mount scripts generate the active desk dock.

## Research worth retaining

The [material/load audit](desk-dock/D7/arm-study/material-load-sources.md)
was checked on 2026-09-08. It distinguishes standards, measurements and
assumptions; preserve those distinctions when updating it.

- [Dell 5680 left view](https://www.dell.com/support/manuals/en-us/precision-16-5680-laptop/precision-5680-owners-manual/left?guid=guid-12cd14bb-8db3-47d7-a090-15d75787517a&lang=en-us)
  and [right view](https://www.dell.com/support/manuals/en-us/precision-16-5680-laptop/precision-5680-owners-manual/right?guid=guid-f0efa586-1b43-447c-a299-f188f5e5c5a5&lang=en-us)
  establish port types. The [Dell-linked visualization asset](https://content.hmxmedia.com/precision-16-5680-laptop-AR/gltf/precision-16-5680-laptop-AR.glb)
  supplies geometric evidence, with extraction provenance retained in D1/D6.
- [USB-IF Type-C Release 2.5](https://www.usb.org/document-library/usb-type-cr-cable-and-connector-specification-release-25)
  informs ordinary mating-force scenarios. Its cited force clauses exclude
  docking; cable pull-out and connector extraction are different tests.
- [Molex 218847 measured test report](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/218/218847/2188470001TS-000.pdf?inline=)
  gives specimen results for one connector family, not Dell force data. No
  public Dell 5680 force-displacement curve was located in the recorded search.
- [Dell connector handling guidance](https://www.dell.com/support/kbdoc/en-us/000198334/how-to-correctly-plug-and-unplug-the-usb-type-c-connector-on-a-dell-dock)
  supports straight aligned insertion/removal and avoiding twist or taut leads.
- [Prusament printed PETG data](https://prusament.com/wp-content/uploads/2022/10/PETG_Prusament_TDS_2021_10_EN.pdf),
  [Polymaker printed PETG data](https://polymaker.com/wp-content/uploads/lana-downloads/TDS_Polymaker_PETG_V2.0_2025-11-17.pdf)
  and [Redutko et al.'s original experiment](https://doi.org/10.24425/amm.2022.137763)
  show material variability. Static tensile, flexural and dynamic storage
  moduli differ. E=0.8/1.2/1.8 GPa are sensitivity inputs, not a measured
  temperature curve for this spool; HDT/Tg are not service ratings.
- [Fantech installation guidance](https://www.fantech.com.au/Content.aspx?ContentID=L5&category=dos-and-donts)
  explains inlet system effects. It does not establish a safe minimum gap,
  operating flow or acoustic result for this compact enclosure.

## Next physical work

1. **Measure and fit.** Confirm the real laptop, chosen port, cable overmold,
   fan thickness/pads, lead exit and cable diameter. Print thread, pin,
   cam/pilot, grille and panel samples before large bodies.
2. **Complete slicing.** Use OrcaSlicer, the project default, with the selected
   P1S/PETG/0.4 mm setup. Review deposited paths, support access, bearing faces,
   thread roots, spring orientation and brim/excluded-bed clearance. The
   package is unsliced; geometric preflight is not toolpath review.
3. **Test the detached holder.** Use a dummy plug and measured load to assess
   complete movement relative to the laptop-bearing datum at 20 N, directional
   release, peak force, repeatable reseating, overmold retention and warm dwell.
   Calibrate within the nut's shoulder limit; do not overtighten a relaxed
   spring to recover force. Keep the laptop out of these load tests.
4. **Calibrate docking.** With the laptop supported, set the fitted cassette
   and independent stop. Check straight engagement/withdrawal, feet/intake
   clearance, cable slack and manual removal without a slam.
5. **Check the stand in use.** Measure sliding and tip stability under actual
   laptop/cable loads, service access, fastener/grille retention, seals and
   PETG creep. Repeat with the actual cable through the full fold.
6. **Measure cooling and sound.** At fixed workload and fan settings, compare
   temperatures, power, branch flow/pressure and sound with external fans off
   and running. Test leakage and fans-off restriction. Establish the fan/system
   operating point before claiming benefit.

No successful slice, printer job, physical force/impact test or measured
thermal/acoustic qualification is recorded for D7. Keep that status explicit
until corresponding evidence is added.
