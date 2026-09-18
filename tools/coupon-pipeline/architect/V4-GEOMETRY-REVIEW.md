# V4 geometry review before one fixed-pose Orca verification

Dock-Architect-Astra, 2026-09-17. Reviewed candidate: full original rail A/B/C, enlarged noncontact identifiers only.

GeometryReview approved in Quartet message 4735 after source diff and manifest re-hash. Terra-Verification independently rebuilt the source comparison in 4747: restoring V3 and V4 identifiers yields exactly zero symmetric difference for all three; new IDs remove 96/192/288 mm3; all 1-mm solid halos and rail/relief separation checks pass; valid one-solid STEP exports; print-axis sections at Z=0.2/12/23.8 are invariant with one/two/three 4-mm2 void rings.

The original 86-mm native rail is retained in each 24-mm-wide specimen. Bed face is the broad original YZ profile, original X mapped to print Z. Constant section gives zero lateral layer growth; identifier voids remain open through every layer. This permits one fixed-placement verification slice, not a physical fit, load, airflow or acoustic conclusion.

V3's earlier actual plate remains HOLD because its sub-nozzle identifiers were filled. Its files remain untouched. V4's 2-mm square identifiers were chosen geometrically with 2-mm ligaments and checked before this slice.

Frozen geometry manifest SHA-256: 52e49c292a3b167c99ee4a52745264b46d855a7d3317c11a0c61594d4b7add35

{
  "A_R1_full_native_rail.step": "042cfa99aab2418b64364d7bfdb60713a74dd35a25163ecbe49f03054e932fad",
  "A_R1_full_native_rail_X_to_print_Z.stl": "11bb78ab79a1e333f708042e76edf4bdb381a64b108034260dad0cbdc1e2b401",
  "B_R2_full_native_rail.step": "44f7dfecd792a2d05db909a7cb92bae7baf6b58dac3a03712c3255d08f1c0359",
  "B_R2_full_native_rail_X_to_print_Z.stl": "a2ec03ec6196f0214d7c75bfa340b6a6154b4393d1eb2a2693a6aceed91a0238",
  "C_R2_full_rail_plus_1mm_seat_relief.step": "0044238c554ab79ae0034bda225d472991e5129d50adcc7b3ff1379a2a836d17",
  "C_R2_full_rail_plus_1mm_seat_relief_X_to_print_Z.stl": "eb23e9dbe01ae39c80321c3095786bf2f3c1192c2dfdc12897d5597560e3022b",
  "ABC_full_native_rail_comparison.png": "a041c6e7f4b07f8137c7ec72a959d2c79e2fdceaa2cf78bdb4098c283335b584",
  "C_full_rail_boolean_X_section.png": "6a8f66cc0cad59d0fef148d5a9381180ee6b4d14dbcd53a13e16be88e751201a"
}
