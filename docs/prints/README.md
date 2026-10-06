# Print log

Every job sent to the P1S, newest first, with the exact geometry (source-STL SHA-256 per part), profiles, estimate,
outcome and what we learned. Source of truth is `print-log.json`; append with `tools/print-log.py add`, close out with
`tools/print-log.py update`. Printer: Bambu P1S 01P00A3C1300643 via bambu-bridge on pve.

| Id | When | What | Status | Job | Slot | Estimate | Commit |
| --- | --- | --- | --- | --- | --- | ---: | --- |
| P-0015 | 2026-09-20 07:34 | D9 P5 plate 16: M2 fan guard (calibrated PolyLite ASA), last plate for a complete dock | printed | 0ce41b8d | 3 | 1h 54m 17s / 41.28 g | 830be64 |
| P-0014 | 2026-09-20 06:33 | D9 P5 plate 18: splice ring (four clips), centre fence and three glue-up alignment keys (calibrated PolyLite ASA) | printed | 01a7a8be | 3 |  | 4af3e3b |
| P-0013 | 2026-09-19 16:08 | D9 P5 plate 14: M2 outer cradle + all 16 seam/fan/lap pins and keys, round 7.9 mm (calibrated PolyLite ASA) | printed | 954998f5 | 3 | 12h 37m 47s / 212.6 g | 302606f |
| P-0012 | 2026-09-19 13:25 | D9 P5 plate 17 (second restart): splice plate, centre contact, gap trim, four 7.9 mm frame-end pins, three alignment keys | printed | 339d6f44 | 3 | 2h 40m 17s / 43.88 g | 302606f |
| P-0011 | 2026-09-19 13:20 | D9 P5 plate 17 (restart): splice plate, centre contact, gap trim, four 7.9 mm frame-end pins, three alignment keys | failed | 3b5c27d0 | 3 | 2h 40m 17s / 43.88 g | 302606f |
| P-0010 | 2026-09-19 13:12 | D9 P5 plate 17: splice plate, centre contact, gap trim, four 7.9 mm frame-end pins, three alignment keys (calibrated PolyLite ASA) | failed | 61d8ebc2 | 3 | 2h 40m 17s / 43.88 g | 302606f |
| P-0009 | 2026-09-19 06:41 | D9 P5 plate 15: M1 fan guard + front/rear ties L/R (calibrated PolyLite ASA) | printed | 1556c722 | 3 | 7h 52m 29s / 141.52 g | 9a8410f |
| P-0008 | 2026-09-18 16:58 | D9 P5 overnight plate: M1 + M2 inner plenums, 4 contact pegs, 2 insert pins, 4 round-shaft frame-end pins + keys (calibrated PolyLite ASA) | printed | 1cb99fd5 | 3 | 14h 33m 48s / 326.58 g | 6cc690c |
| P-0007 | 2026-09-18 08:08 | D9 P5 plate 01, M1 outer cradle (calibrated PolyLite ASA) | printed | 059ef858 | 3 | 9h 36m 19s / 170.35 g | 4834be6 |
| P-0006 | 2026-09-18 07:50 | D9 P5 plate 01, M1 outer cradle (calibrated PolyLite ASA), first attempt | failed | 405f9ec4 | 3 | 9h 36m 19s / 170.35 g | 4834be6 |
| P-0005 | 2026-09-18 07:22 | D9 P5 plate 02, M1 inner plenum (PETG grey) | not-started | ede6ad47 | 2 | 6h 35m 37s / 188.94 g | 4834be6 |
| P-0004 | 2026-09-17 22:11 | R4-C bracket pair + D9 P2 fastener fit parts (PETG grey, 8 h plate) | printed | 9c88a11e | 2 | 6h 59m 10s / 217.3 g | 30998a6 |
| P-0003 | 2026-09-17 20:06 | V5 rail +3.5 mm fit coupons A/B/C (PETG grey) | printed | 0eec266d | 2 | 1h 52m 33s / 48.18 g | f442cc2 |
| P-0002 | 2026-09-17 18:41 | V4 full-rail fit coupons A/B/C (PETG grey) | printed | 0d353e74 | 2 | 1h 50m 46s / 47.02 g | 3e8792b |
| P-0001 | 2026-09-16 18:44 | D8 quick-fit bracket pair, pre-R4 revision (PETG) | printed | b8c11d5e | None |  | 502a85e |

## P-0015 - D9 P5 plate 16: M2 fan guard (calibrated PolyLite ASA), last plate for a complete dock

- When: 2026-09-20 07:34; status: **printed**; job `0ce41b8d13914295bb573a572e7ca243`; file `n/a`; AMS physical slot 3; repo commit `830be64`.
- Profiles: Repro - ASA - Polymaker PolyLite - Calibrated; process Repro Normal - 0.4 nozzle; Polymaker PolyLite ASA, calibrated (flow 0.93, shrink 99.46 %, PA 0.034), AMS slot 3
- Process: layer_height 0.2, wall_loops 5, top_shell_layers 6, sparse_infill_density 40%, sparse_infill_pattern gyroid, support_type normal(auto), support_style snug, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.93, filament_shrink 99.46%, pressure_advance 0.034, nozzle_temperature 260, hot_plate_temp 100
- Estimate: 1h 54m 17s; 41.28 g; 58 layers; 11.6 mm tall; toolpath audit passed.
- Parts: `M2-fan-guard` (4fcbd471da01)
- Slice folder: `/mnt/c/Users/user/Documents/Codex/2026-09-17/for-x20/work/d9-p5-print-pass/asa/16-M2-guard`
- Lessons: M2 fan guard, last plate of the D9 P5 dock. All 64 printed parts now exist in ASA.

## P-0014 - D9 P5 plate 18: splice ring (four clips), centre fence and three glue-up alignment keys (calibrated PolyLite ASA)

- When: 2026-09-20 06:33; status: **printed**; job `01a7a8be885c4102894b3cb979b4f579`; file `n/a`; AMS physical slot 3; repo commit `4af3e3b`.
- Profiles: Repro - ASA - Polymaker PolyLite - Calibrated; process Repro Normal - 0.4 nozzle; Polymaker PolyLite ASA, calibrated (flow 0.93, shrink 99.46 %, PA 0.034), AMS slot 3
- Process: layer_height 0.2, wall_loops 5, top_shell_layers 6, sparse_infill_density 40%, sparse_infill_pattern gyroid, support_type normal(auto), support_style snug, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.93, filament_shrink 99.46%, pressure_advance 0.034, nozzle_temperature 260, hot_plate_temp 100
- Parts: `splice-clip-back` (000fe166a2c4), `splice-clip-fan` (f58c36cc50a4), `splice-clip-front` (7987baa8c60f), `splice-clip-floor` (da7f6fdbf4c7), `centre-fence` (7d44088b1e52), `align-aid-front` (63200440c7ea), `align-aid-top` (550617199a98), `align-aid-fan` (83ea687b0b0e)
- Slice folder: `/mnt/c/Users/user/Documents/Codex/2026-09-17/for-x20/work/d9-p5-print-pass/asa/18-splice-ring`
- Lessons: Splice ring, centre fence and three glue-up keys in ASA, zero support as sliced. 40 layers, ran clean.

## P-0013 - D9 P5 plate 14: M2 outer cradle + all 16 seam/fan/lap pins and keys, round 7.9 mm (calibrated PolyLite ASA)

- When: 2026-09-19 16:08; status: **printed**; job `954998f5e56547f0a389ad0a2a0a04a5`; file `D9-P5-14-M2-cradle-fasteners-ASA.gcode.3mf`; AMS physical slot 3; repo commit `302606f`.
- Profiles: Repro - ASA - Polymaker PolyLite - Calibrated; process Repro Normal - 0.4 nozzle; Polymaker PolyLite ASA, calibrated (flow 0.93, shrink 99.46 %, PA 0.034), AMS slot 3
- Process: layer_height 0.2, wall_loops 5, top_shell_layers 6, sparse_infill_density 40%, sparse_infill_pattern gyroid, support_type normal(auto), support_style snug, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.93, filament_shrink 99.46%, pressure_advance 0.034, nozzle_temperature 260, hot_plate_temp 100
- Estimate: 12h 37m 47s; 212.6 g; 538 layers; 78.0 mm tall; toolpath audit passed.
- Parts: `M2-outer-cradle-shell` (16a1ed436d3a), `M1-fan-1-pin` (62b079d87560), `M1-fan-2-pin` (62b079d87560), `M1-fan-3-pin` (62b079d87560), `M1-fan-4-pin` (62b079d87560), `M2-fan-1-pin` (62b079d87560), `M2-fan-2-pin` (62b079d87560), `M2-fan-3-pin` (62b079d87560), `M2-fan-4-pin` (62b079d87560), `M1-seam-1-pin` (2d8b004b160d), `M1-seam-2-pin` (2d8b004b160d), `M1-seam-3-pin` (2d8b004b160d), `M2-seam-1-pin` (2d8b004b160d), `M2-seam-2-pin` (2d8b004b160d), `M2-seam-3-pin` (2d8b004b160d), `front-lap-pin` (5e2050446ce0), `rear-lap-pin` (5e2050446ce0), `M1-fan-1-key` (0b621d0e7579), `M1-fan-2-key` (3905db7246ec), `M1-fan-3-key` (3905db7246ec), `M1-fan-4-key` (3905db7246ec), `M2-fan-1-key` (3905db7246ec), `M2-fan-2-key` (3905db7246ec), `M2-fan-3-key` (0b621d0e7579), `M2-fan-4-key` (3905db7246ec), `M1-seam-1-key` (3905db7246ec), `M1-seam-2-key` (3905db7246ec), `M1-seam-3-key` (3905db7246ec), `M2-seam-1-key` (3905db7246ec), `M2-seam-2-key` (3905db7246ec), `M2-seam-3-key` (3905db7246ec), `front-lap-key` (0b621d0e7579), `rear-lap-key` (0b621d0e7579)
- Slice folder: `/mnt/c/Users/user/Documents/Codex/2026-09-17/for-x20/work/d9-p5-print-pass/asa/14-M2-cradle-fasteners`
- Notes: Overnight. Bed clear confirmed by the user. Carries the first production set of round 7.9 mm pins after the fit was confirmed on plate 17. Identical ASA in slots 3 and 4.
- Lessons: Ran clean overnight, 538 layers. Completes the M2 outer cradle and all 16 seam/fan/lap pins and keys in ASA.

## P-0012 - D9 P5 plate 17 (second restart): splice plate, centre contact, gap trim, four 7.9 mm frame-end pins, three alignment keys

- When: 2026-09-19 13:25; status: **printed**; job `339d6f44684c431a9be1e180f212cd72`; file `D9-P5-17-splice-plate-contact-ASA.gcode.3mf`; AMS physical slot 3; repo commit `302606f`.
- Profiles: Repro - ASA - Polymaker PolyLite - Calibrated; process Repro Normal - 0.4 nozzle; Polymaker PolyLite ASA, calibrated (flow 0.93, shrink 99.46 %, PA 0.034), AMS slot 3
- Process: layer_height 0.2, wall_loops 5, top_shell_layers 6, sparse_infill_density 40%, sparse_infill_pattern gyroid, support_type normal(auto), support_style snug, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.93, filament_shrink 99.46%, pressure_advance 0.034, nozzle_temperature 260, hot_plate_temp 100
- Estimate: 2h 40m 17s; 43.88 g; 504 layers; 76.4 mm tall; toolpath audit passed.
- Parts: `splice-plate` (4b78d2bde9d6), `center-contact` (dab7afcac663), `gap-trim` (fa7e352fa99a), `front-frame-L-pin` (fc529f9df46d), `front-frame-R-pin` (fc529f9df46d), `rear-frame-L-pin` (fc529f9df46d), `rear-frame-R-pin` (fc529f9df46d), `align-aid-front` (f4d05babd297), `align-aid-top` (f99404108ae4), `align-aid-fan` (8cf8430e70b6)
- Slice folder: `/mnt/c/Users/user/Documents/Codex/2026-09-17/for-x20/work/d9-p5-print-pass/asa/17-splice-plate-contact`
- Notes: Restarted after a silicone sock change. Printer was IDLE with the bed still at 87 C, so the start was quick. Same file and slot.
- Lessons: CONFIRMED 19 Sept: the round 7.9 mm pins (0.5 mm diametral in the 8.4 mm bores) fit the printed plenum bores. The 8.2 mm round trial would not enter and the P2 octagons rattled, so 7.9 mm round is the production size; no further pin change needed. First articles of the splice plate, centre contact, gap trim and glue-up keys also came off this plate.
- Follow-up: The splice plate on this plate printed badly: it was oriented standing on its end, which the slicer filled with 16931 support segments. Reverted to flat (profile on the bed) on 19 September: 5332 segments, plate 08 down from 3 h 22 m to 2 h 36 m. Reprint the splice plate from the corrected plate 08 or ASA plate 17.
- Follow-up: Root cause of the bad splice plate: the part straddled the gap, so its 2 mm tongue floated mid-height and the slicer supported the tongue's mating face. Fixed by making the plate one-sided (wholly on the M2 side, 9 mm wide) so the tongue's mating face is the bed face. Support: 16931 standing, 5332 flat straddling, 1113 flat one-sided, and now only in the bottom 3.5 mm on outboard faces.

## P-0011 - D9 P5 plate 17 (restart): splice plate, centre contact, gap trim, four 7.9 mm frame-end pins, three alignment keys

- When: 2026-09-19 13:20; status: **failed**; job `3b5c27d0dd9c413a8bc929d68ea198fd`; file `D9-P5-17-splice-plate-contact-ASA.gcode.3mf`; AMS physical slot 3; repo commit `302606f`.
- Profiles: Repro - ASA - Polymaker PolyLite - Calibrated; process Repro Normal - 0.4 nozzle; Polymaker PolyLite ASA, calibrated (flow 0.93, shrink 99.46 %, PA 0.034), AMS slot 3
- Process: layer_height 0.2, wall_loops 5, top_shell_layers 6, sparse_infill_density 40%, sparse_infill_pattern gyroid, support_type normal(auto), support_style snug, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.93, filament_shrink 99.46%, pressure_advance 0.034, nozzle_temperature 260, hot_plate_temp 100
- Estimate: 2h 40m 17s; 43.88 g; 504 layers; 76.4 mm tall; toolpath audit passed.
- Parts: `splice-plate` (4b78d2bde9d6), `center-contact` (dab7afcac663), `gap-trim` (fa7e352fa99a), `front-frame-L-pin` (fc529f9df46d), `front-frame-R-pin` (fc529f9df46d), `rear-frame-L-pin` (fc529f9df46d), `rear-frame-R-pin` (fc529f9df46d), `align-aid-front` (f4d05babd297), `align-aid-top` (f99404108ae4), `align-aid-fan` (8cf8430e70b6)
- Slice folder: `/mnt/c/Users/user/Documents/Codex/2026-09-17/for-x20/work/d9-p5-print-pass/asa/17-splice-plate-contact`
- Notes: Restart after the user cancelled the first attempt at layer 1. Same file and slot. Stopped by the user at the start to change a silicone sock. Resubmitted as P-0012.

## P-0010 - D9 P5 plate 17: splice plate, centre contact, gap trim, four 7.9 mm frame-end pins, three alignment keys (calibrated PolyLite ASA)

- When: 2026-09-19 13:12; status: **failed**; job `61d8ebc286b44a16a6eb10a40b109111`; file `D9-P5-17-splice-plate-contact-ASA.gcode.3mf`; AMS physical slot 3; repo commit `302606f`.
- Profiles: Repro - ASA - Polymaker PolyLite - Calibrated; process Repro Normal - 0.4 nozzle; Polymaker PolyLite ASA, calibrated (flow 0.93, shrink 99.46 %, PA 0.034), AMS slot 3
- Process: layer_height 0.2, wall_loops 5, top_shell_layers 6, sparse_infill_density 40%, sparse_infill_pattern gyroid, support_type normal(auto), support_style snug, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.93, filament_shrink 99.46%, pressure_advance 0.034, nozzle_temperature 260, hot_plate_temp 100
- Estimate: 2h 40m 17s; 43.88 g; 504 layers; 76.4 mm tall; toolpath audit passed.
- Parts: `splice-plate` (4b78d2bde9d6), `center-contact` (dab7afcac663), `gap-trim` (fa7e352fa99a), `front-frame-L-pin` (fc529f9df46d), `front-frame-R-pin` (fc529f9df46d), `rear-frame-L-pin` (fc529f9df46d), `rear-frame-R-pin` (fc529f9df46d), `align-aid-front` (f4d05babd297), `align-aid-top` (f99404108ae4), `align-aid-fan` (8cf8430e70b6)
- Slice folder: `/mnt/c/Users/user/Documents/Codex/2026-09-17/for-x20/work/d9-p5-print-pass/asa/17-splice-plate-contact`
- Notes: Submitted into FINISH after plate 15. First articles of the splice plate (standing print, rear tongue), the merged seat-and-fence contact, the L trim and the glue-up keys; the four frame-end pins replace the too-tight 8.2 mm trial. Bed clear confirmed by the user. Cancelled by the user at layer 1; the bridge recorded printer_error. Resubmitted as P-0011.

## P-0009 - D9 P5 plate 15: M1 fan guard + front/rear ties L/R (calibrated PolyLite ASA)

- When: 2026-09-19 06:41; status: **printed**; job `1556c722df0b44de8289231317fcfa9a`; file `D9-P5-15-M1-guard-ties-ASA.gcode.3mf`; AMS physical slot 3; repo commit `9a8410f`.
- Profiles: Repro - ASA - Polymaker PolyLite - Calibrated; process Repro Normal - 0.4 nozzle; Polymaker PolyLite ASA, calibrated (flow 0.93, shrink 99.46 %, PA 0.034), AMS slot 3
- Process: layer_height 0.2, wall_loops 5, top_shell_layers 6, sparse_infill_density 40%, sparse_infill_pattern gyroid, support_type normal(auto), support_style snug, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.93, filament_shrink 99.46%, pressure_advance 0.034, nozzle_temperature 260, hot_plate_temp 100
- Estimate: 7h 52m 29s; 141.52 g; 100 layers; 16.0 mm tall; toolpath audit passed.
- Parts: `M1-fan-guard` (6ac137d69478), `front-tie-L` (8ff49336782f), `front-tie-R` (460a16da9593), `rear-tie-L` (5f493fbd40b8), `rear-tie-R` (d3c141ca15fd)
- Slice folder: `/mnt/c/Users/user/Documents/Codex/2026-09-17/for-x20/work/d9-p5-print-pass/asa/15-M1-guard-ties`
- Notes: Submitted into FINISH after the overnight plate; identical ASA in slots 3 and 4 for auto-refill. Ties carry the 12.7 mm tongue; guard has the bonus M4 holes.
- Lessons: Finished about 13:10 on 19 September (7 h 52 m estimate). Guard has the M4 pilots; ties carry the 12.7 mm tongue. Inspect: tongue nests flush, key windows, guard standoffs.

## P-0008 - D9 P5 overnight plate: M1 + M2 inner plenums, 4 contact pegs, 2 insert pins, 4 round-shaft frame-end pins + keys (calibrated PolyLite ASA)

- When: 2026-09-18 16:58; status: **printed**; job `1cb99fd5`; file `D9-P5-10-inner-pair-pegs-ASA.gcode.3mf`; AMS physical slot 3; repo commit `6cc690c`.
- Profiles: Repro - ASA - Polymaker PolyLite - Calibrated; process Repro Normal - 0.4 nozzle; Polymaker PolyLite ASA, calibrated (flow 0.93, shrink 99.46 %, PA 0.034), AMS slot 3
- Process: layer_height 0.2, wall_loops 5, top_shell_layers 6, sparse_infill_density 40%, sparse_infill_pattern gyroid, support_type normal(auto), support_style snug, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.93, filament_shrink 99.46%, pressure_advance 0.034, nozzle_temperature 260, hot_plate_temp 100
- Estimate: 14h 33m 48s; 326.58 g; 990 layers; 91.8 mm tall; toolpath audit passed.
- Parts: `M1-fence-peg` (bdc102d6c48c), `M2-fence-peg` (5cd84efe43b1), `M1-seat-peg` (0aed55942890), `M2-seat-peg` (8d2c053555c7), `M1-insert-pin` (fc300ddeb418), `M2-insert-pin` (fc300ddeb418), `front-frame-L-pin` (e515c5742f37), `front-frame-R-pin` (e515c5742f37), `rear-frame-L-pin` (e515c5742f37), `rear-frame-R-pin` (e515c5742f37), `front-frame-L-key` (3905db7246ec), `front-frame-R-key` (3905db7246ec), `rear-frame-L-key` (3905db7246ec), `rear-frame-R-key` (3905db7246ec), `M1-inner-shell` (34fdd0866440), `M2-inner-shell` (0583ada73437)
- Slice folder: `/mnt/c/Users/user/Documents/Codex/2026-09-17/for-x20/work/d9-p5-print-pass/asa/10-inner-pair-pegs`
- Notes: Submitted straight into FINISH; printer went IDLE then RUNNING within 30 s. Pegs, pins and keys at the plate's 40 % gyroid rather than 100 %. Round-shaft trial on the four frame-end pins. Predates the fan-screw pilots and the gussets.
- Lessons: Finished about 06:40 on 19 September, an hour under the estimate. Inspect: seat/fence peg fit in the M1 cradle, round-shaft frame pins in their 8.4 mm bores, key retention. Fit check 19 Sept: the round 8.2 mm frame-end pins (the trial) would not enter the printed 8.4 mm bores in the plenum; the octagonal pins were the loose ones on P2. Decision: one pin type, round 7.9 mm (0.5 mm diametral); reprint pins from plate 07.

## P-0007 - D9 P5 plate 01, M1 outer cradle (calibrated PolyLite ASA)

- When: 2026-09-18 08:08; status: **printed**; job `059ef858`; file `D9-P5-01-M1-outer-cradle-ASA.gcode.3mf`; AMS physical slot 3; repo commit `4834be6`.
- Profiles: Repro - ASA - Polymaker PolyLite - Calibrated; process Repro Normal - 0.4 nozzle; Polymaker PolyLite ASA, calibrated (flow 0.93, shrink 99.46 %, PA 0.034), AMS slot 3
- Process: layer_height 0.2, wall_loops 5, top_shell_layers 6, sparse_infill_density 40%, sparse_infill_pattern gyroid, support_type normal(auto), support_style snug, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.93, filament_shrink 99.46%, pressure_advance 0.034, nozzle_temperature 260, hot_plate_temp 100
- Estimate: 9h 36m 19s; 170.35 g; 548 layers; 74.4 mm tall; toolpath audit passed.
- Parts: `M1-outer-cradle-shell` (1d11da52c6cd)
- Slice folder: `/mnt/c/Users/user/Documents/Codex/2026-09-17/for-x20/work/d9-p5-print-pass/asa/01`
- Notes: Resubmitted after the watchdog fix. Finished about 16:20. Snug normal supports, 5 walls, 40 % gyroid. The bridge job row still reads "preparing": its JobRun died in the watchdog-fix restart and was re-attached as started_at.recovered; the printer completed the part.
- Lessons: Part came out nice; supports were acceptable to remove. Predates the fan-screw pilots (drill by hand with the guard as jig) and the socket-boss gussets.

## P-0006 - D9 P5 plate 01, M1 outer cradle (calibrated PolyLite ASA), first attempt

- When: 2026-09-18 07:50; status: **failed**; job `405f9ec4`; file `D9-P5-01-M1-outer-cradle-ASA.gcode.3mf`; AMS physical slot 3; repo commit `4834be6`.
- Profiles: Repro - ASA - Polymaker PolyLite - Calibrated; process Repro Normal - 0.4 nozzle; Polymaker PolyLite ASA, calibrated (flow 0.93, shrink 99.46 %, PA 0.034), AMS slot 3
- Process: layer_height 0.2, wall_loops 5, top_shell_layers 6, sparse_infill_density 40%, sparse_infill_pattern gyroid, support_type normal(auto), support_style snug, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.93, filament_shrink 99.46%, pressure_advance 0.034, nozzle_temperature 260, hot_plate_temp 100
- Estimate: 9h 36m 19s; 170.35 g; 548 layers; 74.4 mm tall; toolpath audit passed.
- Parts: `M1-outer-cradle-shell` (1d11da52c6cd)
- Slice folder: `/mnt/c/Users/user/Documents/Codex/2026-09-17/for-x20/work/d9-p5-print-pass/asa/01`
- Notes: Killed by the bridge watchdog (FED_NO_PROGRESS, 600 s) during the 100 C bed preheat before any layer printed.
- Lessons: Bridge feed deadline raised to 1800 s (BRIDGE_FEED_DEADLINE_S), PR #28, deployed on pve the same morning.

## P-0005 - D9 P5 plate 02, M1 inner plenum (PETG grey)

- When: 2026-09-18 07:22; status: **not-started**; job `ede6ad47`; file `D9-P5-02-M1-inner-plenum.gcode.3mf`; AMS physical slot 2; repo commit `4834be6`.
- Profiles: Repro Generic PETG - 0.4 nozzle - Starter; process Repro Normal - 0.4 nozzle
- Process: layer_height 0.2, wall_loops 5, top_shell_layers 6, sparse_infill_density 40%, sparse_infill_pattern gyroid, support_type normal(auto), support_style snug, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.95, filament_shrink 100%, nozzle_temperature 255, hot_plate_temp 70
- Estimate: 6h 35m 37s; 188.94 g; 725 layers; 91.8 mm tall; toolpath audit passed.
- Parts: `M1-inner-shell` (34fdd0866440)
- Slice folder: `/mnt/c/Users/user/Documents/Codex/2026-09-17/for-x20/work/d9-p5-print-pass/plates-prev-tongue-12.1/02`
- Notes: Bridge accepted the job but the printer refused the start with BBSTART_NOT_IDLE while showing FINISH from the R4-C plate. Dismissed on screen; plate 02 was not printed in PETG.
- Lessons: Consecutive jobs normally submit straight into FINISH; this refusal was a one-off. If it recurs, dismiss on the screen and resubmit.

## P-0004 - R4-C bracket pair + D9 P2 fastener fit parts (PETG grey, 8 h plate)

- When: 2026-09-17 22:11; status: **printed**; job `9c88a11e`; file `OPEN-ME.gcode.3mf`; AMS physical slot 2; repo commit `30998a6`.
- Profiles: Repro Generic PETG - 0.4 nozzle - Starter; process Repro Normal 15 grid - 0.4 nozzle
- Process: layer_height 0.2, wall_loops 4, top_shell_layers 5, sparse_infill_density 15%, sparse_infill_pattern grid, support_type normal(auto), support_style tree_slim, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.95, filament_shrink 100%, nozzle_temperature 255, hot_plate_temp 70
- Estimate: 6h 59m 10s; 217.3 g; 298 layers; 38.0 mm tall; toolpath audit passed.
- Parts: `D8-R4-C-quick-fit-bracket-print-TWO` (76cd2acca0a5), `D8-R4-C-quick-fit-bracket-print-TWO-2` (76cd2acca0a5), `fan-socket-fit-fixture` (8ff048783540), `side-socket-fit-fixture` (5bb130ef78d6), `T-joint-fit-L` (561c060bed9f), `T-joint-fit-R` (ac9eaaeb9872), `M1-fan-1-pin` (fc300ddeb418), `M1-fan-3-pin` (fc300ddeb418), `front-lap-pin` (42d48155efdb), `M1-fan-1-key` (82f5a4d12c23), `M1-fan-3-key` (7a9efd6c3943), `front-lap-key` (82f5a4d12c23)
- Slice folder: `/mnt/c/Users/user/Documents/Codex/2026-09-17/for-x20/work/quartet-team/architect/r4-C-8h-orca`
- Notes: Two beefed-up R4-C brackets plus the P2 fit fixtures, three pins and keys.
- Lessons: Brackets seat the laptop well (cradle is great). Octagonal pins rattle in the 8.8 mm bores (0.6 mm diametral at corners): bores to 8.4 mm. Key barbs need 1 mm more total interference (0.8 to 1.8 mm). T tongue looked 0.6 mm proud but it was stuck support debris; the cleaned pair nests flush.

## P-0003 - V5 rail +3.5 mm fit coupons A/B/C (PETG grey)

- When: 2026-09-17 20:06; status: **printed**; job `0eec266d`; file `Precision_5680_V5_Rail_Plus_3p5mm_Fit_Coupons.gcode.3mf`; AMS physical slot 2; repo commit `f442cc2`.
- Profiles: Repro Generic PETG - 0.4 nozzle - Starter; process Repro Normal - 0.4 nozzle
- Process: layer_height 0.2, wall_loops 4, top_shell_layers 5, sparse_infill_density 20%, sparse_infill_pattern gyroid, support_type normal(auto), support_style tree_slim, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.95, filament_shrink 100%, nozzle_temperature 255, hot_plate_temp 70
- Estimate: 1h 52m 33s; 48.18 g; 120 layers; 24.0 mm tall; toolpath audit passed.
- Parts: `A_R1_full_rail_plus_3p5mm_X_to_print_Z` (c3fbe9c04abd), `B_R2_full_rail_plus_3p5mm_X_to_print_Z` (dad7d63de9b7), `C_R2_full_rail_plus_3p5mm_plus_1mm_seat_relief_X_to_print_Z` (0e5512bfb011)
- Slice folder: `/mnt/c/Users/user/Documents/Codex/2026-09-17/for-x20/work/quartet-team/architect/v5-orca`
- Notes: Lid rail moved 3.5 mm away from seat and fence after the V4 trio all bound.
- Lessons: C (R2 seat + 1 mm relief) seated best: 3 dots wins. Rail offset confirmed at 3.5 mm.

## P-0002 - V4 full-rail fit coupons A/B/C (PETG grey)

- When: 2026-09-17 18:41; status: **printed**; job `0d353e7416234f1498326c701b233e2a`; file `Precision_5680_V4_Full_Rail_Fit_Coupons_V4 FULL RAIL A B C FIT COUPONS - ONE EACH`; AMS physical slot 2; repo commit `3e8792b`.
- Profiles: Repro Generic PETG - 0.4 nozzle - Starter; process Repro Normal - 0.4 nozzle
- Process: layer_height 0.2, wall_loops 4, top_shell_layers 5, sparse_infill_density 20%, sparse_infill_pattern gyroid, support_type normal(auto), support_style tree_slim, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.95, filament_shrink 100%, nozzle_temperature 255, hot_plate_temp 70
- Estimate: 1h 50m 46s; 47.02 g; 120 layers; 24.0 mm tall; toolpath audit passed.
- Parts: `A_R1_full_native_rail_X_to_print_Z` (11bb78ab79a1), `B_R2_full_native_rail_X_to_print_Z` (a2ec03ec6196), `C_R2_full_rail_plus_1mm_seat_relief_X_to_print_Z` (eb23e9dbe01a)
- Slice folder: `/mnt/c/Users/user/Documents/Codex/2026-09-17/for-x20/work/quartet-team/architect/v4-orca`
- Notes: Recovered from the bridge job list (57 min actual).
- Lessons: All three V4 sizers bound: the tall lid-stop wall sat too close to the seat and fence. Fixed by moving the rail 3.5 mm outward in V5 (P-0003, the V5 coupons).

## P-0001 - D8 quick-fit bracket pair, pre-R4 revision (PETG)

- When: 2026-09-16 18:44; status: **printed**; job `b8c11d5e2216487ba26385df0b79d6fa`; file `D8-quick-fit-bracket-print-TWO_plate_1`; AMS physical slot None; repo commit `502a85e`.
- Notes: Pre-session print recovered from the bridge job list (2 h 36 m actual). Exact bracket revision not recorded; the D8 quick-fit R1/R2 sources are in desk-dock/D8/quick-fit.
- Lessons: Seat and fence needed the V-series coupons to converge; superseded by the R4-C pair (P-0004, the R4-C plate).
