# V2 contact coupon geometry review

2026-09-17. **PASS to one Orca toolpath-verification pass.** Geometry is frozen.
This is a handheld diagnostic coupon set, not a stand or airflow prototype.

Source: `work/quartet-team/geometry/profile-v2/`.
Builder SHA-256: `ca5dcf24cba2026c2443e146f7afff4656155d59aa260b9bb1a40530dad08333`.
Manifest SHA-256: `1fd8b22c3a5638194ff621ce9e1ca42dccd10269013abe9475893ebbdf1ce433`.

Sonnet-GeometryReview approved the source-datum and Boolean review in Quartet
message 4629, after the owner froze geometry in 4627. Architect independently
imported the exported STEP files and rebuilt the expected source crops and
cuts without importing the coupon builder. All three symmetric differences
were zero; three aligned 0.25-mm slabs through each coupon also differed by
zero volume. The independent receipt SHA-256 is
`83fe5ddfd94c8e851e7b3b60246f892adade401fbf4c22beeea4ad40b5aad8cd`.

| Variant | Contact geometry | STEP SHA-256 |
| --- | --- | --- |
| A | Original R1 crop; one identification hole | `9b68e26046ff96c317cbcb04233e06b5017c859021a621e69d08e6fdc4cc7d8c` |
| B | Original R2 crop; two identification holes | `2e013167a08c8f457a7234eff4344e7d145ca450ac5ed6007fb2ffdc323a1f45` |
| C | B with a 1-mm local seat-relief band; three identification holes | `b943326b7e4f3028576deaa1a1a13075e91e4f76ba977a7bf428803b3f215305` |

C's cut is rotated into the exact source lean frame before subtraction. It
removes 240 mm3. No common base was added. Identification-hole tops at native
Z=49.7 mm are below the relief minimum Z=52.8073 mm and both source bearing
minima Z=53.8035 mm. Contact faces and backup stops retain their source datums.

Print on the broad YZ face, with original X becoming print Z. Every retained
feature and new cut is constant through X. Analytical layer-to-layer lateral
advance is zero, with no designed unsupported roofs. The identification holes
run vertically through the print; they do not require bridging. The broad
profile provides bed contact. These specimens are hand-positioned, with no
stand-load or retention qualification. The contact profiles lie in the print
plane, avoiding layer steps along their curved section.

Use the frozen P1S 0.4-mm / Generic PETG / 0.20-mm baseline. Enable automatic
supports for verification and require zero emitted support paths. Check model
and brim bounds, all contact profiles and each identification opening. The
0.48 x 0.70-mm identification holes are small; their survival in the actual
toolpath is mandatory, and physical readability is not established by CAD.

R1 is a plausible source for the user's original V1 print, not a proven exact
export identity. The source laptop reference is simplified. No physical fit,
strength, acoustic, thermal or installed-airflow performance is established.
