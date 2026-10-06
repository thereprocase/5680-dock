# V3 full-height contact coupon geometry review

2026-09-17. **PASS to Orca toolpath verification.** This supersedes the short V2
coupon for the next print candidate, following the reported gentle lid curve.
It is a handheld, light-contact diagnostic set, not a freestanding stand.

Geometry: `work/quartet-team/geometry/profile-v3/`.
Builder SHA-256: `ca8ae8acd24ed6a89f1ee5440134d2c5ba35894e303980cf8f4d4d6c2ca62490`.
Manifest SHA-256: `a7c9dd78186a555930d1d4c39265b8400f5ef8c6ba4760d1f497bb43f0bd3c43`.

Sonnet-GeometryReview approved source/crop/rail/Boolean checks in Quartet
message 4670. Terra-Verification independently reconstructed the actual
exports and reported zero symmetric difference for A/B/C in message 4684.
The full source rail volume is retained in all three: 8256 mm3 within numerical
tolerance. C's isolated lean-transformed seat-relief cut removes 240 mm3.
Identification holes remove only native support material below the contacts.

| Variant | Test | STEP SHA-256 |
| --- | --- | --- |
| A | Full R1 contact-height control, one ID hole | `57ff9d05e2d9dbe5e4a7a7f2b3d8be4cc43527909f1a90e3eb66dea4c01a9dca` |
| B | Full R2 contact-height trial, two ID holes | `1eb7c59e31bc51ab743ffe6827ffaac47248336658994bcd247cf33aede7d335` |
| C | B plus local 1-mm seat relief, three ID holes | `4d4471b2f69a32fc91cb3c5dd2a7edb3b8b08b414d073c3f8d9cbea73945dafc` |

The original rail spans unleaned Z=48..134 mm, 86 mm total and 80 mm above the
rear-seat datum. Crop bounds derive from its leaned corners and retain its
full geometry; the reported physical lid curve is not fabricated in CAD.
No added base or brace changes the source contacts. Cropped brace remnants
are not credited as structural reinforcement. Avoid flexing the tall rail
while reading contact; force, retention and stiffness are unqualified.

All source features and new cuts remain constant YZ profiles through the
24-mm X width. Broad-face printing maps original X to print Z. Lateral layer
advance is zero, and there are no designed unsupported roofs. The ID holes
run vertically through the print and need no bridges. Contact-curve bending
and printed rails lie in the layer plane; this does not establish strength.

Orca must verify the preserved bed face/rotation, 16-mm object spacing,
zero emitted supports or external bridges, bed clearance, native/standalone
G-code identity, and survival of all 1/2/3 small identification openings.
Use the frozen P1S 0.4-mm / Generic PETG / 0.20-mm baseline. This review is
geometry evidence only; physical fit, cooling and acoustic benefit are unknown.
