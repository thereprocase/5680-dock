# Precision 5680 D9 P1 prototype print kit

Ten new printable parts on six frozen, named Orca plates. Plug mechanism excluded.
Open each numbered .3mf in OrcaSlicer. Each contains ONE plate and matching embedded G-code. Print each plate once for one dock. Standalone matching .gcode and oriented STL/STEP fallback bodies are included.

Printer/profile: Repro Bambu P1S, 0.4 mm nozzle, Generic PETG Starter, textured PEI, 0.2 mm nominal layer, five walls, six top/bottom layers, 40% gyroid, 5 mm brim. These are saved prototype settings; confirm the actual machine and material before printing. No job was sent.

## What changed

Two split plenums with full-height R2 end cradles; two fan guards with 7.5 mm standoffs; four bracing tie halves. Fan centers moved 12 mm outward for lid clearance. The original source mouth-port areas and nominal 120 mm fan / 105 mm mounting pattern remain. The lower contact profile is R2; it has NOT been corrected from new measurements. Use the separate V4 fit coupons before committing to the large cradle prints.

## Manufacturing and assembly

Keep the supplied poses. Shells print on their broad exterior X faces, open cavities upward. The broad finished outer sides face the bed. Hidden seam-tab and nut-pocket undersides receive removable support through the open halves. Guards print exterior-face down with vertical standoffs. Ties print long-axis horizontal; small transverse holes bridge between two landings. Supports are acceptable on these internal surfaces; remove before closing the plenums.

Dry-fit matching M1/M2 halves and four seam tabs per module. Insert captive nuts while the halves are open. Use thin sealant at the mating seam and seal the fan-flange screw interfaces; the enclosure check explicitly assumes these fastener seals. Fit each 120 x 120 x 25 mm fan and its guard to the 105 mm hole pattern. Join L/R front and rear ties at their 24 mm half-laps, then bolt their ends through the two cradle feet. Do not force misaligned or tight joints.

Nominal hardware: two 120 x 120 x 25 mm fans; 8 M4 x 50 fan/guard bolts; 8 M4 x 25 shell-seam bolts; 4 M4 x 30 tie-end bolts; 4 M4 x 16 tie-lap bolts; 24 M4 hex nuts, suitable washers and fan/seam sealing material. Confirm thread engagement and clearance during dry assembly. Nut pockets are nominal 8.3 mm across corners; printer and nut tolerances are uncalibrated.

## Verification and limits

All ten CAD solids valid; ten STL meshes watertight, consistently wound and single-component. No volume interference across the 45 printed-part pairs, fan bodies or nominal upper laptop envelope. Each plenum's intended air region is enclosed with both named ports capped and the explicitly modeled fastener seals installed; uncapping either port reconnects it to exterior. This is nominal geometric closure, not measured airtightness.

All six plates sliced successfully in native OrcaSlicer 2.4.2 after geometric design. Verified unchanged poses/placement, bed and exclusion-zone clearance of actual model/support/brim extrusion, intended height, zero reported mesh repair, and matching embedded/standalone G-code. The support/bridge overview is included for inspection. Actual support removal and cosmetic print quality require a physical trial.

This is a completed prototype CAD/print package, not a physically qualified dock. Laptop seating, loaded stability, screw fit, fan fit, cooling, airflow and acoustics remain untested. Support the laptop independently during initial fit checks. No 800 RPM performance claim is made.

Source builder and frozen input hashes are included for provenance. The original builder records local dependency paths; CadQuery 2.8, trimesh, Shapely and Pillow were used. Exported STEP/STL and frozen Orca projects are standalone.

## Slicer estimates

| Plate | Estimated total time | PETG |
|---|---|---|
| 01-M1-outer-cradle | 8h 38m 22s | 195.08 g |
| 02-M1-inner | 5h 41m 28s | 170.40 g |
| 03-M2-inner | 5h 39m 1s | 169.88 g |
| 04-M2-outer-cradle | 8h 54m 15s | 201.75 g |
| 05-M1-guard-front-ties | 3h 51m 51s | 91.86 g |
| 06-M2-guard-rear-ties | 3h 51m 52s | 91.86 g |

Total: 36 h 36 m 49 s and 920.83 g, including the selected supports and brims. Estimates exclude manual handling and assembly.
