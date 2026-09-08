# Laptop wall mount — Minimalist M1 and ducted Rev H

Two independent prototypes: **Minimalist M1** uses lighter open arms and fan
cradles with an optional indexed airflow dam; **Rev H** preserves the ducted
prototype and its already-printed arms. Future ducted revisions can change the
arms, size range and airflow adjustment too.

[Explore both designs](https://thereprocase.github.io/dell-5560-wall-mount/) ·
[Print and assembly guide](https://thereprocase.github.io/dell-5560-wall-mount/minimalist-guide.html)

## Minimalist M1

[5560 native + print package](docs/downloads/Minimalist_M1_5560.zip) ·
[Fit coupon package](docs/downloads/Minimalist_M1_Fit_Coupons.zip) ·
[Editable nominal FreeCAD](minimalist/Laptop_Wall_Mount_Minimalist.FCStd) ·
[Six native size presets](minimalist/presets/) ·
[Construction and validation](minimalist/README.md)

The nominal complete set is **388.05 g / 15 h 24 m 54 s** in OrcaSlicer 2.4.2,
using P1S / ASA / 0.4 mm / 0.20 mm / 6 walls / 100% fill / 8 mm brim. That is
67.2% less estimated filament than the full Rev H set under the same process.
Times include each layout's plate overhead. These are slicer estimates, not
measured printing or cooling results.

Print one each of **01–08 plus 21_all_hardware**: nine plates. The twelve
individual files 09–20 are alternatives for replacement hardware, already
included on plate 21. STEP, STL and geometry-only 3MF are alternative formats.
The assembled STEP is for inspection. Keep the supplied print orientations.

All six dimensioned width/depth/thickness examples were recomputed at all nine
dam indices. Native geometry, intended 0.30 mm gaps, saved/reopened models,
STEP roundtrips, closed meshes and bed/brim/cutter clearance passed. Nominal
Orca paths have no disconnected floating components. The expanded screen
finds up to 8.99 mm of overhang-wall path without prior-layer support; the
bridge-tagged maximum is 3.02 mm. The coupon includes the fan-hanger and dam
slot interfaces in their full-part build directions. Physical fit, printed
retention, long-term ASA creep, anchors and cooling remain to be qualified.

## Ducted Rev H prototype

[All 14 print-oriented STEP files + corrected Orca previews](docs/downloads/Precision_5560_RevH_Prototype_STEP.zip) ·
[Orca bridge instructions](print_release_step/ORCA_BRIDGE_REVIEW.txt) ·
[STL/3MF print set](print_release/) ·
[Native FreeCAD](freecad/Precision_5560_Native.FCStd) ·
[Assembled STEP](freecad/Precision_5560_Native.step)

For ducts 03 and 04, keep the baked inlet-down orientation and set both
**Bridge direction and Internal bridge direction to 180°**, with Relative
bridge angle and Align infill direction to model off. Automatic direction
runs lengthwise along the slots. The corrected paths cross them, with a
maximum unsupported span of 5.19 mm and no disconnected floating components.
This is a toolpath screen, not an ASA bridge test. Re-slice for your spool.

The original `print_ready/`, root STEP, CadQuery source and Fusion/Onshape
ports remain **Revision F history/baselines**. Rev H's arm geometry is preserved
as prototype history; it is not a permanent constraint on later designs.

## Rev H engineering history

Revision H adds three R12 internal tangent blends per duct and two R14 exterior
support blends. Inlet/outlet profiles, printed arms, and 0.30 mm interfaces
remain unchanged. The other twelve parts retain the prior release geometry.
See [flow validation](freecad/flow_validation.json) for sampled wall thickness
and inlet-down overhang checks. Cooling performance has not been measured.


- Closed rail roofs and end windows while retaining the exhaust slot and open back.
- Contoured the rail shoulder with 0.30 mm clearance to the frozen printed arm.
- Rounded exposed tips, matched cover outlines, and used print-aware corner bevels.
- Set the cap/duct/tray interfaces to measured 0.30 mm gaps on both sides.
- Corrected dovetail clearance normal to the sloping flank.
- Added separate editable native loft-skin patches to close the unintended duct-wall notches.
- Preserved pin retention, fixed mounting shoulders, screw access and service motions.

Final CAD checks: **14 valid solids, 176 fully constrained sketches**, zero
additional wall loss, unchanged frozen arms, and passing sampled service paths.
All 14 print meshes are closed and their oriented bounds plus brims fit the P1S.
Physical fit, retention and ASA bridging remain to be checked. Both duct
toolpaths have now been screened with the corrected Orca bridge direction.

[Fit-and-finish review](freecad/ADJACENT_FIT_REVIEW.md) ·
[Native model guide](freecad/README.md) ·
[Final acceptance JSON](freecad/complete_fit_review.json) ·
[Print manifest](print_release/manifest.json)

## Airflow research and technical drawings

Two 120 mm fans feed the rear plenum; the upper contraction directs bypass flow
past the hinge exhaust. The project includes the original 2D slot study and a
later exploratory 3D installed-flow case with traced laptop intake assumptions.

[Seven-sheet A3 technical review](docs/simulation/installed-airflow-2026-09-07/Precision_5560_CFD_Technical_Review.pdf) ·
[Drawing package](docs/simulation/installed-airflow-2026-09-07/) ·
[3D CFD run notes](fusion/cfd/TRACED_RUN_NOTES.md) ·
[2D CFD report](CFD_Design_Report.md)

The gallery is Revision F exploratory evidence. The separate Revision H transient study is being commissioned and has no accepted validation result here. The 3D
case uses uncalibrated constant-force fan assumptions, no thermal solution,
and did not meet its strict convergence target. It is not a measured hardware
performance claim.

## Project history

- [Minimalist workflow and reproduction](minimalist/README.md)
- [Original design narrative](docs/REVISION_F_DESIGN_STORY.md)
- [FreeCAD workflow notebook](freecad/RESEARCH_NOTES.md)
- [Fusion native port and CFD work](fusion/README.md)
- [Onshape pilot and API research](onshape/README.md)
- [Engineering report](ENGINEERING_REPORT.md) and [source attribution](SOURCES.md)

MIT licensed project. Third-party viewer code retains its own MIT notice.
This project is independent of Dell, Bambu Lab and Autodesk.
