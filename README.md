# A wall mount that became an airflow problem

A closed Dell Precision 5560, two 120 mm fans, four wall bolts, and a requirement to lift the laptop out whenever the server needs a keyboard. The final design uses side-printed ASA cradles, a shrouded rear plenum, 45° fan modules and a restricted upper outlet. Fourteen printed pieces assemble with keyed CA joints and removable split pins.

![Revision F, installed and empty, rendered from the actual CAD](Precision_5560_Wall_Mount_Preview.png)

**Revision F is a prototype checkpoint.** Geometry checks, a limited structural screen and eight OpenFOAM cases are complete. Physical printing, joint qualification and cooling measurements are not.

[Download the STEP assembly](Precision_5560_Wall_Mount.step) · [Print files](print_ready/) · [Print and assembly guide](P1S_ASA_Print_Guide.md) · [Engineering report](ENGINEERING_REPORT.md) · [Reproduce the work](PROCESS.md)

## 1. Establish the interfaces before shaping the bracket

> “The hinge will go down— no, wait. The hinge will go up so that the hot air escapes up and the fans can go on the bottom…”

The initial brief established the load, removal direction and air path together. We kept the laptop vertical, underside toward the wall, with a nominal 40 mm rear gap. A 344.4 × 230.3 × 20 mm envelope controls fit; a 26 mm bare slot leaves room for pads and the actual case profile.

> “…make the tines on the front a little bit taller… make sure that all of the fasteners are easy to install and oriented perpendicular to the wall”

The front tines reached 94 mm. The four wall holes remain at X = ±162 mm and Z = −36/+174 mm, with Ø7 mm bores and clear Ø16 mm driver corridors. We checked the laptop's lift-then-forward path and the assembled tool paths, rather than checking only whether the stationary solids intersect. Removal requires about 105 mm of lift; allow 110 mm overhead.

## 2. Treat the gap as a plenum

> “…should we tilt the laptop towards the wall to create a restriction (or make an additional part - a back rail)…?”

> “…doesn't have to seal, just has to be high pressure at vent high velocity beyond. check vent layout dims to align the restriction / outlet properly”

That changed the task. Passing air over the underside was insufficient as a design objective: the intake needed available static pressure, and the bypass needed a controlled exit. We kept the laptop vertical and put the contraction in a separate upper rail. That preserved removal and made outlet width an interchangeable parameter.

The important distinction is between pressure and flow. Restricting the exit can retain upstream pressure while reducing flow. A smaller slot does not necessarily produce a faster jet when the supply pressure is limited. The simulation later made that tradeoff explicit.

## 3. Find the intake behind the visible grille

> “…download and scale images and cross sections of the machine to estimate its profile geometry?”

We downloaded Dell side views and the inside-base-cover image, scaled them against the published width and depth, and retained the pixel picks. The inside view changed the interpretation: the broad exterior grille has a covered center. Two approximately 70 × 40 mm regions near X = ±111 mm represent the inferred active windows.

![Scaled manufacturer images and inferred geometry](Laptop_Profile_References.png)

Their estimated upper boundary is near Z = 191 mm, with ±4 mm location uncertainty. The contraction starts at Z = 198 mm, reaches its throat at 226 mm and exits at 232 mm, close to the hinge. We found no dimensioned factory cross-section. The reconstructed silhouette carries an estimated ±2 mm uncertainty; the 20 mm fit envelope remains authoritative until measured.

## 4. Design the print orientation into the solid

> “I would like to print the brackets on their side for strength, and not on their back.”

> “Also bridges are just fine, they're usually printable. Unsupported overhangs are bad.”

We treated these as different geometric problems. The cradles print on their outer sides; ducts grow from the fan-inlet face; outlet rails print lip down. Sloped roofs replace unsupported ledges. Short bridges close box sections and dovetail grooves without filling the air path with support.

![Part families in their supplied print orientations](FDM_Print_Orientations.png)

A geometric audit at 0.20 mm layers found no floating starts. The longest intentional bridge spans 18 mm in the cradle spine. Every individual part and its 8 mm brim fits the P1S bed and avoids the stock cutter exclusion. Those checks establish geometric feasibility. Bambu Studio could not execute in the environment, so extrusion paths and ASA bridge quality still need a slicer preview and a print.

## 5. Remove material where the load path allows it

> “Fluid dynamics? Airflow sim? Topological optimization? Generative structures? What would help and what can you do well, quickly?”

> “I feel like we could get really creative and save a ton of plastic here.”

> “yes, do it.”

We used hollow box sections, thin duct skins, framed trays and pocketed caps. The geometry remained interpretable: material stayed at bearing shoulders, bracket roots and wall holes. No topology optimizer or generative-structure solver was run.

Net section properties were extracted from the actual cradle every 0.5 mm, including voids and unsymmetric bending. The screen used a 2.5 kg laptop, 6 kg installation, 3g acceleration and a 50 N outward hinge pull. Its minimum assumed-stress-limit-to-demand ratio is 1.19. That is a limited calculation with chosen ASA properties, not a tested assembly safety factor.

Revision F contains **1,177.3 cm³ of solid CAD, 35.0% below Revision D** at equal fill policy. The latest containment and assembly changes cost 13.1 cm³ relative to the lightweight Revision E. The remaining questions are joints, local behavior and warm creep—not whether an organic-looking surface can remove another few percent.

## 6. Separate fixed joints from service joints

> “Can we also make it tool free / ca glue assembly, except for the four wall bolts? And shroud the cheeks to keep air contained? And have the fans angle down so they're blowing at a 45 to the gap instead of straight in?”

The fixed ducts and outlet rails now use keyed lap joints. Their shoulders carry vertical reactions; CA retains withdrawal. Fan trays slide in dry, and two split pins retain each removable cap. The fan intakes face down and outward; their flow points upward and wallward at 45°. Cheeks close the gross side openings while leaving the laptop's ports accessible.

![Fixed keyed joints and removable fan assemblies](Tool_Free_Assembly.png)

This removes all M3/M4 hardware and inserts, but creates explicit qualification work. Each duct has a calculated 47.8 N outward retention demand in the screened load case. Each pin has a 7.4 N retention demand. A bearing or shear calculation does not prove adhesive peel resistance or split-pin pullout.

## 7. Run a model that answers the slot question

> “And do some cfd to design the plenum and slot?”

We ran eight OpenFOAM v1912 `simpleFoam` cases: 8/12/16 mm slots, straight/curved lower turns, three mesh sizes, and supply-pressure and intake-demand sensitivities. The model uses steady incompressible RANS with k–omega SST in a representative sealed 2D section.

![Actual OpenFOAM fields and slot comparison](CFD_Plenum_Study.png)

At 20 Pa assumed inlet total pressure and 0.4 m/s prescribed laptop intake demand:

| Outlet | Mean intake pressure | Mean exit speed |
|---|---:|---:|
| 8 mm | 18.80 Pa | 4.01 m/s |
| **12 mm** | **17.67 Pa** | **4.42 m/s** |
| 16 mm | 15.43 Pa | 5.16 m/s |

The narrower slot retained more pressure; the wider slot produced the faster exit in this model. We kept 12 mm as the prototype compromise. The curved lower turn improved mean intake pressure by only about 0.11 Pa on the common mesh—too little evidence to call the bend optimized.

All meshes passed `checkMesh`; flow imbalance remained below 0.001%. Mesh refinement changed mean intake pressure by about 0.3% and exit speed by 2.9%. Four cases missed the strict residual target despite stabilized mean-pressure monitors. Raw cases and logs preserve that result.

The laptop intake flow is **prescribed**, not predicted. The model omits real fan curves, laptop internal resistance, side leakage, heat transfer and the room plume. It supports comparison of the proposed arrangements; it cannot establish cooling improvement, total CFM or hot-air carry distance.

## 8. State the fits precisely

> “what tolerances did you assume for slide to fit parts?”

The tray dovetail has 0.30 mm horizontal allowance per side, 0.30 mm above the crown and 0.20 mm below the root. The sloping flank's normal clearance is smaller than its horizontal allowance. Fixed-key pockets use 0.30 mm nominal offsets plus roof relief. Pins use a Ø4.0 mm shaft, Ø4.1 mm socket and Ø4.2 mm split crown.

No global ASA shrink correction is built in. Print the supplied coupons, inspect elephant foot, and adjust the specific interface rather than scaling the assembly. A short coupon checks local fit; full-length tray engagement also checks warping. [TOLERANCES.md](TOLERANCES.md) records the exact distinctions.

## 9. Preserve the process and identify the next useful experiment

> “Enumerate your workflow and thinking, list my prompts as part of the dialogue… what software and packages you used and how you approached the problem solving.”

The workflow was: establish interfaces → reconstruct uncertain geometry → build parametric solids → check load paths and service motions → audit print orientation → compare airflow variants → export the evidence. The quoted prompts above are selected excerpts; [DIALOGUE.md](DIALOGUE.md) preserves the available project prompts in order. The design rationale here summarizes decisions and evidence.

| Software / packages | Role |
|---|---|
| Python 3.12; CadQuery 2.8.0 / Open CASCADE | Parametric B-reps, booleans, sections, STEP export and assembly checks |
| NumPy; trimesh 5.1.0; Shapely 2.1.2; rtree; NetworkX | Mesh checks, planar sections, layer support and connectivity |
| Pillow | CAD raster rendering, scaled reference images and annotated figures |
| Matplotlib; SciPy; VTK | Postprocess actual CFD fields and draw pressure/velocity comparisons |
| OpenFOAM v1912 | `blockMesh`, `checkMesh`, `simpleFoam`, `foamToVTK` |
| Bambu Studio 2.8.2.61 profile sources | Starting P1S/ASA settings; runtime unavailable, no slicing claimed |
| Git / GitHub | Publish the current design, reports, source and numerical evidence |

[PROCESS.md](PROCESS.md) gives ordered commands and the repository map. [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md) consolidates dimensions, loads, assumptions and verification. [requirements.txt](requirements.txt) records the Python environment constraints.

The next experiment is a physical prototype: measure the actual laptop; print fit coupons; qualify the joints and warm structural behavior; then compare intake pressure and workload temperatures with the selected fans and outlet rails. Those measurements determine whether a coupled 3D or thermal model would answer a remaining design question.

---

**Print:** use the [P1S ASA guide](P1S_ASA_Print_Guide.md), start with fit coupons, retain the supplied orientations, and inspect the slice. Models are standard 3MF/STL, not sliced G-code. Reference STEP assemblies are not printable parts.

**License and sources:** the repository retains its [MIT license](LICENSE). Dell reference material remains attributed third-party content; see [SOURCES.md](SOURCES.md). The estimated laptop profile is not factory CAD. This project is not affiliated with Dell or Bambu Lab.
