# Saved handoff — 8 September 2026

The project is saved for shutdown. Current source includes the final fan-pocket overlap-rib correction and the viewer camera fix.

**This is an engineering review package, not a print release.**

- Final 25 mm fans, rear cable trough, and 26 mm spring standoff are in the source.
- Full nominal docking, bearing, fan-service and 0–45 degree breakaway checks passed before the final small fan-pocket rib addition.
- The rib addition passes both isolated shell watertightness and service checks.
- 44 production/coupon meshes pass the P1S geometric preflight.
- Both complete production shell STLs must be regenerated from the corrected source and preflighted. Their earlier nonmanifold exports are quarantined in `print-review/superseded-shells-DO-NOT-PRINT/`.
- The full STEP assembly and viewer mesh still precede that small rib addition and need regeneration together with the shell exports. All other final geometry is represented.
- The final airflow report refresh and complete package hash manifest should be regenerated after those exports.
- No successful slicing or physical print qualification is claimed. Do not resume Orca CLI discovery; it crashed previously.

## Resume

Run the current D7 build and export scripts, preflight the two corrected shell STLs, and combine their results with the 44 unchanged validated meshes. Check hashes against the current manifests. Refresh the STEP, viewer assets, review package and Pages download. The successful isolated rib check is in `service_isolated_validation.json`; the shell correction is in `fan_service.py`. Keep the current 20 N/.20 mm and 50 N-class breakaway values as physical calibration targets.
