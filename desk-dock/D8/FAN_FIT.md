# Fan fit and simple retention

D8 separates clearance, retention and sealing. An oversized pocket accepts the fan; two small removable printed top clips take up play and retain both fan and grille. The grille prints flat without D7's tall upper return. No full perimeter fan gasket is required.

## Published dimensions and tolerances

“120 × 120 × 25 mm” names a size class. It does not establish one universal maximum envelope or corner profile.

| Manufacturer / model | Frame width and height | Axial thickness | Hole pitch | Evidence |
|---|---:|---:|---:|---|
| Mechatronics MS1225-H | 120 ± 0.5 mm | 25.0 ± 0.5 mm | 105 ± 0.3 mm | [Manufacturer drawing, p. 1](https://www.mechatronics.com/pdf/MS1225-H.pdf) |
| Mechatronics G1225 | 120 ± 0.5 mm | 25 ± 0.5 mm | 105 ± 0.5 mm | [Manufacturer drawing, p. 1](https://www.mechatronics.com/pdf/G1225.pdf) |
| Noctua NF-A12x25 PWM, without pads | 120 × 120 mm nominal | 25 mm nominal | 105 × 105 mm nominal | [Manufacturer mechanical specifications](https://www.noctua.at/en/products/nf-a12x25-pwm/specifications) |
| Noctua NF-A12x25 PWM, with pads | 120 × 120 mm nominal | **27 mm nominal** | 105 × 105 mm nominal | Same manufacturer specifications |
| Delta AFB1212SH | 120 × 120 mm nominal | **25.4 mm nominal** | Check selected drawing | [Manufacturer product page](https://www.delta-fan.com/products/AFB1212SH.html) |

The two toleranced drawings allow a 120.5 × 120.5 × 25.5 mm bare frame. This is evidence from those products, not an upper bound on every fan. Noctua's cited page does not publish a dimensional tolerance. The 27 mm padded size is a nominal envelope, not a guaranteed maximum. Delta's product page establishes 25.4 mm nominal depth; this note does not assign it an unverified ± tolerance. Hole pitch does not control this pocket because D8 does not use the factory holes for retention.

## D8 allowances

The starting pocket is **121.5 mm inside**: 0.75 mm nominal clearance per side around a 120 mm frame, or 0.50 mm per side around a centered 120.5 mm frame, before print error. Its small internal corner radius avoids assuming every fan shares D7's generous molded corner radius. Long-part warping remains a fit check.

The axial envelope is **27.8 mm**. This accommodates the cited bare-frame range and leaves 0.8 mm total allowance around Noctua's nominal 27 mm padded stack before print error. This is an engineering starting allowance, not a guarantee for unspecified pads. Fit the actual fan before printing the complete shell.

The suction-envelope datum stays at fan-local Z = 30 mm. For a bare fan its suction frame face sits there. With a 1 mm rear pad, the rear pad's outside face stays at that datum and the bare frame moves 1 mm outward. Added depth grows toward the discharge side. Set `fan_fit.pad_thickness_mm` to the selected pad thickness and use the same value in `fan_dimensions()` when creating the reference fan. A nominal 25 mm frame plus two 1 mm pads gives the 27 mm stack. Printed contact shoes follow the selected stack; they are small replaceable parts if the fan changes.

## Clips and print orientation

Each fan uses two top clips at its upper mounting-frame corners. A rear snap hook enters an open notch in a shell ear. The clip spans the fan and grille top; its front leg blocks grille lift. Pull the accessible rear leg outward to release the hook, then lift the clip before withdrawing the grille and fan. The grille rails have running clearance and no intentional friction lands. Long front guide lips have been removed; the frame rests against the rear seat and the top clips provide axial retention.

Each clip contains a long top leaf to take up fan-height play and an axial leaf to take up frame-depth play. The nominal assembly represents 0.8 mm top-leaf movement and 0.45 mm axial-leaf movement. These are small contact preloads, not a calibrated force or a fan-frame compression specification. The short rear snap leg flexes only during installation and removal. Root concentrations, printed variation, warm creep and retention force remain prototype checks.

**Print the unloaded clip from `fan_service.PRINT_OVERRIDES`.** Put its broad fan-local YZ side on the bed; its 8 mm extrusion along X becomes build height. This places both leaf bending directions in the layer plane, prints the hooks without supports and keeps the large grille fully flat. The displayed assembly clip is not the production shape. The free clip geometry includes the small preload offsets.

The grille rear perimeter has a 2.8 mm chamfer that matches 45-degree ramps below the pocket and rail channel roof. At the default 4 mm grille depth, its outer front edge retains 1.2 mm full-width thickness. The mating faces keep a 0.30 mm coordinate clearance, approximately 0.21 mm perpendicular to the 45-degree faces; confirm the sliding fit with a short rail sample. The remaining pocket-rim shelf projects about 0.45 mm, roughly one extrusion width. The 0.5 mm lower fan-seat projection also remains. These small edges need ordinary deposited-path inspection.

**The final shell print pose is upright, with the lower perimeter skirt and foot stems on the bed.** The earlier fan-rim orientation study found 221 mm² of steep downward-facing area in its first 20 mm, down from 2,001 mm² before the rail changes (89% less). That was a local geometry screen, excluding the deliberate 45-degree ramps; it did not measure whole-shell support demand and does not prescribe the final print orientation. Nominal grille lifting at 0, 0.3, 1, 3, 8, 20, 75 and 140 mm produced no shell intersections in that earlier rail study. Use the final production mesh and upright slicer review for shell print decisions.

Use a short pocket-corner sample and one clip before printing complete shells. Confirm:

- The actual frame and pads drop into the pocket without force, with the lead clear of the corner notch.
- The installed clip positively catches its rear notch and prevents fan and grille lift.
- The leaves remove perceptible rattle without distorting the fan frame or rubbing the impeller.
- Clips release by hand and remain useful after repeated removal, warm dwell and operation across the intended speed range.

If a new fan has a different depth, regenerate the small clip contact shoe or use a measured local shim. Do not shrink the whole pocket or rely on permanent crush ribs in the expensive shell.

## Sealing

The fan frame overlaps the duct aperture. Use that rigid overlap first and inspect bypass during the prototype flow test. A little leakage is acceptable for this cooling aid; airtight construction is not a design target. A few small compliant patches at contact points may damp vibration if needed. They do not require a continuous fan gasket. Keep the lower duct-panel overlap and cable exits sensible, but add sealing material only where a measured leak affects cooling or noise.

Sources checked 8 September 2026. Dimensions above support fit decisions; they do not qualify the dock's airflow or structural performance.
