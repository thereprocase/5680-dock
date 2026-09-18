# Coupon and plate pipeline (snapshot)

Source snapshot of the fit-coupon and mixed-plate pipeline used for V2–V5
coupons, the R4-C bracket plate and the D9 P3–P5 verification passes. The live
working copy, with generated geometry, slice folders and Orca data dirs, is
the Codex work tree `C:\Users\repro\Documents\Codex\2026-09-17\for-x20\work\quartet-team\`
(see CLAUDE.md). Nothing here is required to print the kits in `docs/printables`.

- `geometry/profile-v2,v4,v5/` — CadQuery coupon builders (V5 = V4 with the
  lid rail moved 3.5 mm) and their frozen output manifests.
- `architect/` — `run_coupon_pipeline.py` (place → Orca → verify → ID audit →
  package), `prepare_coupon_plate.py`, `prepare_mixed_plate.py` (footprint-aware
  placement), `verify_coupon_plate.py`, `verify_mixed_plate.py` (per-object
  support/bridge counts, shrink-aware placement), `run_coupon_orca.py`,
  `package_coupon_plate*.py`, `package_plate.py`, review receipts and READMEs,
  and `profiles/` (frozen-normal, structural-8h, coupon-fast, asa-structural,
  asa-polylite-calibrated).
- `verification/` — identifier-hole toolpath audits and independent geometry
  comparisons.

Run everything with the Windows CadQuery environment (`cadpy`, see CLAUDE.md).
Paths inside the scripts assume the Codex work-tree layout.
