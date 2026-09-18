# D9 P5 builder snapshot

Source of the D9 P5 print kit in `docs/printables/d9-p5`: the builder
(`build_d9.py` + `dress.py`), plate preparation, enclosure and toolpath
verification, packaging, the ASA slicing helper, frozen profiles and the
`source-inputs` the builder reads (parameters at 8° lean, flow geometry, R2
inputs, R4–R7 cradle sources). `asa-01-receipts/` holds the verified receipts
of plate 01 sliced in calibrated Polymaker PolyLite ASA (18 September 2026);
`asa-10-receipts/` the overnight combined plate from `prepare_asa_combo.py` (both
inner halves, four contact pegs, two insert pins, four round-shaft frame-end pins
and keys; snug supports, calibrated ASA).
Generated geometry, plate folders and G-code are not stored here; the live
working copy is `C:\Users\repro\Documents\Codex\2026-09-17\for-x20\work\d9-p5-print-pass\`.
Chain: `cadpy build_d9.py` → `verify_enclosure.py` → `audit_closed_intake.py` (in
tools/coupon-pipeline/architect) per module → `prepare_and_slice.py` →
`verify_plates.py` → `verify_and_package.py`.
