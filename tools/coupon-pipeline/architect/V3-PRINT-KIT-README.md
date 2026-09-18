# Precision 5680: full-height A/B/C contact coupons

Open **OPEN-ME.3mf** in OrcaSlicer. The named, locked plate contains one of
each coupon in its verified print pose. The matching standalone G-code is
for the frozen **P1S, 0.4-mm nozzle, Generic PETG, textured PEI** profile.
Estimated whole plate: **1 hour 52 minutes, 46.50 g**. No print was sent.

These are handheld fit specimens. They include the original full lid-side
rail so the reported gentle lid curve can participate in the contact check.
They are not freestanding supports and are not load, cooling or noise tests.

| Coupon | Identification | What changes |
| --- | --- | --- |
| A | One small through-hole | Original R1 contact geometry, including the full rail |
| B | Two small through-holes | Original R2 geometry: its documented capture changes and actual extended seat curve |
| C | Three small through-holes | B with a 1-mm local seat-relief cut in the original leaned frame |

The identification openings are only 0.48 x 0.70 mm in CAD. Use the included
close-up toolpath receipt and keep the plate positions identified as you
remove parts. Physical hole size/readability remains dependent on the print.
In the included top-down plate view, A is lower left, B lower right, and C
upper left. The individual STEP/STL filenames also identify each variant.

## Contact check

Support the laptop independently and present one coupon gently at the same
local section where the original leg engages. Keep fingers clear of the
contact gap. Observe which surface touches first: the intended curved seat,
the short backup fence, or the tall lid-side rail. Do not bend the rail to
make it fit or use the coupon to carry the laptop's weight.

Compare A, B and C at the same section and orientation. Record the variant,
first-contact location and whether the curved seat actually engages. A scaled
perpendicular view of a new trial can document the result; the original four
V1 photographs remain preserved and do not need resending.

- If all three hit the rail/fence before the seat, the real local profile is
  still unresolved. Do not promote a coupon to a final contact design.
- If B engages where A does not, the R2 combination improves this local test;
  it does not identify which of its several changes was responsible.
- If C improves on B, local seat clearance matters. The 1-mm trial does not
  establish a measured increase in lid thickness.
- A successful handheld contact check does not establish loaded stability,
  retention, full-dock alignment or connector protection.

## Manufacturing evidence

The broad profile is the designed bed face. Original X becomes print Z, and
the source geometry and all cuts have a constant section through that axis.
The analytical lateral layer advance is zero, with no designed unsupported
roofs. Orca 2.4.2 then verified the selected orientation: automatic supports
enabled, **zero emitted support paths and zero external bridges**. Internal
infill closure occurs near the top skin at print Z=23.2 mm.

The actual native object transforms retain the prepared orientations and
16-mm minimum model spacing. Model and brim paths stay inside the P1S bed and
away from its front-left excluded area. The native project's embedded G-code
matches the standalone file byte for byte. The package manifest and ZIP were
checked against all included file hashes. Separate actual-toolpath and CAD
previews are included because the headless Orca run could not make an OpenGL
thumbnail; this did not prevent slicing/export.

The frozen process uses 0.20-mm layers, four walls, five top/bottom layers,
20% gyroid infill and a 5-mm outer brim. It is a diagnostic-coupon process,
not a structural qualification profile for the major dock revision.

## Contents and reproducibility

`fallback-CAD/` holds individual print-oriented STLs and original-frame STEPs.
`frozen-profiles/` contains the exact printer/process/filament snapshots.
`verification/` and `previews/` preserve the checks and visible evidence.
`source/` includes the editable builders and their local STEP/JSON inputs.
With compatible CadQuery, trimesh and Pillow installed, the source can be
rebuilt by running `source/profile-v3/build_full_rail_coupon_v3.py` with
`--d8 source/D8 --out <new-output-directory>` from this package directory.

R1 remains the plausible source of the original V1 print, not a proven exact
export identity. Its contact data came from a visualization reference, not
manufacturing metrology. The package provides the next physical fit question;
it does not claim a measured lid curve, acoustic benefit or installed airflow.
