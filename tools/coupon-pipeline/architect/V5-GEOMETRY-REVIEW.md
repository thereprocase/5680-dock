# V5 geometry review before one fixed-pose Orca verification

Claude Fable 5.1, 2026-09-17. Reviewed candidate: V4 full-rail A/B/C with the
whole rail side moved 3.5 mm outward, normal to the lid-rail face.

Trigger: the printed V4 plate. The user reported all three coupons wrong in the
same way and C (three openings) still not enough, and asked for the tall
lid-stop wall to sit 3.5 mm further from the seat/hinge/bearing surface and the
short fence, with the whole coupon growing by 3.5 mm normal to that wall.

Builder receipts checked in `generated/manifest.json`:

- Split plane at unleaned y = 8.75 mm, strictly between the R2 seat-curve end (6.415 mm) and the rail inner face (11.085 mm). Exactly one section face crosses it: the flat deck, unleaned z 46..51 mm, area 120 mm2, for both A and B.
- Rail-side piece translated by [0.0, 3.4867, -0.305] mm (3.5 mm along the leaned rail normal). Deck filler volume 420 mm3 per variant; result volume equals source plus filler.
- Seat/fence side of the split plane is byte-for-byte the V4 crop (symmetric difference below 1e-6 mm3) for A and B.
- The full 8256 mm3 source rail is retained at its moved position in A, B and C; the 3.5-mm channel above the deck between the old and new rail faces is empty.
- Fence inner face to rail inner face: A 22.42 -> 25.92 mm; B and C 24.42 -> 27.92 mm.
- C relief cut removes 240.000 mm3, identical to V4; identifier holes keep V4 positions, volumes, halos and rail/relief separation.
- Valid single-solid STEP and watertight single-component STL for all three; every feature remains a constant YZ profile along original X, so the print pose (original X to print Z) keeps zero lateral layer advance and no designed overhangs.

Print bounds grow from about 40.1 x 89.2 x 24 mm to about 43.6 x 89.2 x 24 mm per coupon; the three-column plate layout still fits the P1S bed.

This permits one fixed-placement verification slice, not a physical fit, load,
airflow or acoustic conclusion. The 3.5 mm is a requested trial increment, not a
measured lid thickness.

Frozen geometry manifest SHA-256: 4bb83bb4528b0ab31d9a53354693d36195cc6352de013282be689a4e5db225c8

{
  "A_R1_full_rail_plus_3p5mm.step": "f62f9f7632442ad9234b15f220c858d52fd517e0c0426bc6795fe9fc8bfe9b68",
  "A_R1_full_rail_plus_3p5mm_X_to_print_Z.stl": "c3fbe9c04abdcae53b7d8b8c9dc9c354e66eaeab9bd450bc954ad4e98a2fee59",
  "B_R2_full_rail_plus_3p5mm.step": "f0451c579822bee36bfb53216e1cffb210589b63e01f58f682167f75adefd0fa",
  "B_R2_full_rail_plus_3p5mm_X_to_print_Z.stl": "dad7d63de9b792c9042661b8d1eeac6ef3c51e9d3ee6f6b9d109d8bfd959984f",
  "C_R2_full_rail_plus_3p5mm_plus_1mm_seat_relief.step": "2905e0803b4c45a90423fa56d6f0bc6def83bc696091763f1323c53abadf1dad",
  "C_R2_full_rail_plus_3p5mm_plus_1mm_seat_relief_X_to_print_Z.stl": "0e5512bfb011cd286049b1590bf67a0d87526eafecc07840bdc01b84a30e4a08",
  "ABC_full_rail_plus_3p5mm_comparison.png": "4d924530688bab68e523f3577ce42c8f1da1142fd66dc7c3f493e68c9424357c",
  "B_V4_vs_V5_X_section.png": "aa5f75138e01b8d3d5db4d38a17e684c96fe1082fd90f98a53a618b80c77f34f"
}
