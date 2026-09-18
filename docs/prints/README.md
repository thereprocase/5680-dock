# Print log

Every job sent to the P1S, newest first, with the exact geometry (source-STL SHA-256 per part), profiles, estimate,
outcome and what we learned. Source of truth is `print-log.json`; append with `tools/print-log.py add`, close out with
`tools/print-log.py update`. Printer: Bambu P1S 01P00A3C1300643 via bambu-bridge on pve.

| Id | When | What | Status | Job | Slot | Estimate | Commit |
| --- | --- | --- | --- | --- | --- | ---: | --- |
| P-0008 | 2026-09-18 16:58 | D9 P5 overnight plate: M1 + M2 inner plenums, 4 contact pegs, 2 insert pins, 4 round-shaft frame-end pins + keys (calibrated PolyLite ASA) | running | 1cb99fd5 | 3 | 14h 33m 48s / 326.58 g | 6cc690c |
| P-0007 | 2026-09-18 08:08 | D9 P5 plate 01, M1 outer cradle (calibrated PolyLite ASA) | printed | 059ef858 | 3 | 9h 36m 19s / 170.35 g | 4834be6 |
| P-0006 | 2026-09-18 07:50 | D9 P5 plate 01, M1 outer cradle (calibrated PolyLite ASA), first attempt | failed | 405f9ec4 | 3 | 9h 36m 19s / 170.35 g | 4834be6 |
| P-0005 | 2026-09-18 07:22 | D9 P5 plate 02, M1 inner plenum (PETG grey) | not-started | ede6ad47 | 2 | 6h 35m 37s / 188.94 g | 4834be6 |
| P-0004 | 2026-09-17 22:11 | R4-C bracket pair + D9 P2 fastener fit parts (PETG grey, 8 h plate) | printed | 9c88a11e | 2 | 6h 59m 10s / 217.3 g | 30998a6 |
| P-0003 | 2026-09-17 20:06 | V5 rail +3.5 mm fit coupons A/B/C (PETG grey) | printed | 0eec266d | 2 | 1h 52m 33s / 48.18 g | f442cc2 |
| P-0002 | 2026-09-17 18:41 | V4 full-rail fit coupons A/B/C (PETG grey) | printed | 0d353e74 | 2 | 1h 50m 46s / 47.02 g | 3e8792b |
| P-0001 | 2026-09-16 18:44 | D8 quick-fit bracket pair, pre-R4 revision (PETG) | printed | b8c11d5e | None |  | 502a85e |

## P-0008 - D9 P5 overnight plate: M1 + M2 inner plenums, 4 contact pegs, 2 insert pins, 4 round-shaft frame-end pins + keys (calibrated PolyLite ASA)

- When: 2026-09-18 16:58; status: **running**; job `1cb99fd5`; file `D9-P5-10-inner-pair-pegs-ASA.gcode.3mf`; AMS physical slot 3; repo commit `6cc690c`.
- Profiles: Repro - ASA - Polymaker PolyLite - Calibrated; process Repro Normal - 0.4 nozzle; Polymaker PolyLite ASA, calibrated (flow 0.93, shrink 99.46 %, PA 0.034), AMS slot 3
- Process: layer_height 0.2, wall_loops 5, top_shell_layers 6, sparse_infill_density 40%, sparse_infill_pattern gyroid, support_type normal(auto), support_style snug, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.93, filament_shrink 99.46%, pressure_advance 0.034, nozzle_temperature 260, hot_plate_temp 100
- Estimate: 14h 33m 48s; 326.58 g; 990 layers; 91.8 mm tall; toolpath audit passed.
- Parts: `M1-fence-peg` (bdc102d6c48c), `M2-fence-peg` (5cd84efe43b1), `M1-seat-peg` (0aed55942890), `M2-seat-peg` (8d2c053555c7), `M1-insert-pin` (fc300ddeb418), `M2-insert-pin` (fc300ddeb418), `front-frame-L-pin` (e515c5742f37), `front-frame-R-pin` (e515c5742f37), `rear-frame-L-pin` (e515c5742f37), `rear-frame-R-pin` (e515c5742f37), `front-frame-L-key` (3905db7246ec), `front-frame-R-key` (3905db7246ec), `rear-frame-L-key` (3905db7246ec), `rear-frame-R-key` (3905db7246ec), `M1-inner-shell` (34fdd0866440), `M2-inner-shell` (0583ada73437)
- Slice folder: `/mnt/c/Users/repro/Documents/Codex/2026-09-17/for-x20/work/d9-p5-print-pass/asa/10-inner-pair-pegs`
- Notes: Submitted straight into FINISH; printer went IDLE then RUNNING within 30 s. Pegs, pins and keys at the plate's 40 % gyroid rather than 100 %. Round-shaft trial on the four frame-end pins. Predates the fan-screw pilots and the gussets.

## P-0007 - D9 P5 plate 01, M1 outer cradle (calibrated PolyLite ASA)

- When: 2026-09-18 08:08; status: **printed**; job `059ef858`; file `D9-P5-01-M1-outer-cradle-ASA.gcode.3mf`; AMS physical slot 3; repo commit `4834be6`.
- Profiles: Repro - ASA - Polymaker PolyLite - Calibrated; process Repro Normal - 0.4 nozzle; Polymaker PolyLite ASA, calibrated (flow 0.93, shrink 99.46 %, PA 0.034), AMS slot 3
- Process: layer_height 0.2, wall_loops 5, top_shell_layers 6, sparse_infill_density 40%, sparse_infill_pattern gyroid, support_type normal(auto), support_style snug, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.93, filament_shrink 99.46%, pressure_advance 0.034, nozzle_temperature 260, hot_plate_temp 100
- Estimate: 9h 36m 19s; 170.35 g; 548 layers; 74.4 mm tall; toolpath audit passed.
- Parts: `M1-outer-cradle-shell` (1d11da52c6cd)
- Slice folder: `/mnt/c/Users/repro/Documents/Codex/2026-09-17/for-x20/work/d9-p5-print-pass/asa/01`
- Notes: Resubmitted after the watchdog fix. Finished about 16:20. Snug normal supports, 5 walls, 40 % gyroid. The bridge job row still reads "preparing": its JobRun died in the watchdog-fix restart and was re-attached as started_at.recovered; the printer completed the part.
- Lessons: Part came out nice; supports were acceptable to remove. Predates the fan-screw pilots (drill by hand with the guard as jig) and the socket-boss gussets.

## P-0006 - D9 P5 plate 01, M1 outer cradle (calibrated PolyLite ASA), first attempt

- When: 2026-09-18 07:50; status: **failed**; job `405f9ec4`; file `D9-P5-01-M1-outer-cradle-ASA.gcode.3mf`; AMS physical slot 3; repo commit `4834be6`.
- Profiles: Repro - ASA - Polymaker PolyLite - Calibrated; process Repro Normal - 0.4 nozzle; Polymaker PolyLite ASA, calibrated (flow 0.93, shrink 99.46 %, PA 0.034), AMS slot 3
- Process: layer_height 0.2, wall_loops 5, top_shell_layers 6, sparse_infill_density 40%, sparse_infill_pattern gyroid, support_type normal(auto), support_style snug, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.93, filament_shrink 99.46%, pressure_advance 0.034, nozzle_temperature 260, hot_plate_temp 100
- Estimate: 9h 36m 19s; 170.35 g; 548 layers; 74.4 mm tall; toolpath audit passed.
- Parts: `M1-outer-cradle-shell` (1d11da52c6cd)
- Slice folder: `/mnt/c/Users/repro/Documents/Codex/2026-09-17/for-x20/work/d9-p5-print-pass/asa/01`
- Notes: Killed by the bridge watchdog (FED_NO_PROGRESS, 600 s) during the 100 C bed preheat before any layer printed.
- Lessons: Bridge feed deadline raised to 1800 s (BRIDGE_FEED_DEADLINE_S), PR #28, deployed on pve the same morning.

## P-0005 - D9 P5 plate 02, M1 inner plenum (PETG grey)

- When: 2026-09-18 07:22; status: **not-started**; job `ede6ad47`; file `D9-P5-02-M1-inner-plenum.gcode.3mf`; AMS physical slot 2; repo commit `4834be6`.
- Profiles: Repro Generic PETG - 0.4 nozzle - Starter; process Repro Normal - 0.4 nozzle
- Process: layer_height 0.2, wall_loops 5, top_shell_layers 6, sparse_infill_density 40%, sparse_infill_pattern gyroid, support_type normal(auto), support_style snug, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.95, filament_shrink 100%, nozzle_temperature 255, hot_plate_temp 70
- Estimate: 6h 35m 37s; 188.94 g; 725 layers; 91.8 mm tall; toolpath audit passed.
- Parts: `M1-inner-shell` (34fdd0866440)
- Slice folder: `/mnt/c/Users/repro/Documents/Codex/2026-09-17/for-x20/work/d9-p5-print-pass/plates-prev-tongue-12.1/02`
- Notes: Bridge accepted the job but the printer refused the start with BBSTART_NOT_IDLE while showing FINISH from the R4-C plate. Dismissed on screen; plate 02 was not printed in PETG.
- Lessons: Consecutive jobs normally submit straight into FINISH; this refusal was a one-off. If it recurs, dismiss on the screen and resubmit.

## P-0004 - R4-C bracket pair + D9 P2 fastener fit parts (PETG grey, 8 h plate)

- When: 2026-09-17 22:11; status: **printed**; job `9c88a11e`; file `OPEN-ME.gcode.3mf`; AMS physical slot 2; repo commit `30998a6`.
- Profiles: Repro Generic PETG - 0.4 nozzle - Starter; process Repro Normal 15 grid - 0.4 nozzle
- Process: layer_height 0.2, wall_loops 4, top_shell_layers 5, sparse_infill_density 15%, sparse_infill_pattern grid, support_type normal(auto), support_style tree_slim, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.95, filament_shrink 100%, nozzle_temperature 255, hot_plate_temp 70
- Estimate: 6h 59m 10s; 217.3 g; 298 layers; 38.0 mm tall; toolpath audit passed.
- Parts: `D8-R4-C-quick-fit-bracket-print-TWO` (76cd2acca0a5), `D8-R4-C-quick-fit-bracket-print-TWO-2` (76cd2acca0a5), `fan-socket-fit-fixture` (8ff048783540), `side-socket-fit-fixture` (5bb130ef78d6), `T-joint-fit-L` (561c060bed9f), `T-joint-fit-R` (ac9eaaeb9872), `M1-fan-1-pin` (fc300ddeb418), `M1-fan-3-pin` (fc300ddeb418), `front-lap-pin` (42d48155efdb), `M1-fan-1-key` (82f5a4d12c23), `M1-fan-3-key` (7a9efd6c3943), `front-lap-key` (82f5a4d12c23)
- Slice folder: `/mnt/c/Users/repro/Documents/Codex/2026-09-17/for-x20/work/quartet-team/architect/r4-C-8h-orca`
- Notes: Two beefed-up R4-C brackets plus the P2 fit fixtures, three pins and keys.
- Lessons: Brackets seat the laptop well (cradle is great). Octagonal pins rattle in the 8.8 mm bores (0.6 mm diametral at corners): bores to 8.4 mm. Key barbs need 1 mm more total interference (0.8 to 1.8 mm). T tongue looked 0.6 mm proud but it was stuck support debris; the cleaned pair nests flush.

## P-0003 - V5 rail +3.5 mm fit coupons A/B/C (PETG grey)

- When: 2026-09-17 20:06; status: **printed**; job `0eec266d`; file `Precision_5680_V5_Rail_Plus_3p5mm_Fit_Coupons.gcode.3mf`; AMS physical slot 2; repo commit `f442cc2`.
- Profiles: Repro Generic PETG - 0.4 nozzle - Starter; process Repro Normal - 0.4 nozzle
- Process: layer_height 0.2, wall_loops 4, top_shell_layers 5, sparse_infill_density 20%, sparse_infill_pattern gyroid, support_type normal(auto), support_style tree_slim, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.95, filament_shrink 100%, nozzle_temperature 255, hot_plate_temp 70
- Estimate: 1h 52m 33s; 48.18 g; 120 layers; 24.0 mm tall; toolpath audit passed.
- Parts: `A_R1_full_rail_plus_3p5mm_X_to_print_Z` (c3fbe9c04abd), `B_R2_full_rail_plus_3p5mm_X_to_print_Z` (dad7d63de9b7), `C_R2_full_rail_plus_3p5mm_plus_1mm_seat_relief_X_to_print_Z` (0e5512bfb011)
- Slice folder: `/mnt/c/Users/repro/Documents/Codex/2026-09-17/for-x20/work/quartet-team/architect/v5-orca`
- Notes: Lid rail moved 3.5 mm away from seat and fence after the V4 trio all bound.
- Lessons: C (R2 seat + 1 mm relief) seated best: 3 dots wins. Rail offset confirmed at 3.5 mm.

## P-0002 - V4 full-rail fit coupons A/B/C (PETG grey)

- When: 2026-09-17 18:41; status: **printed**; job `0d353e7416234f1498326c701b233e2a`; file `Precision_5680_V4_Full_Rail_Fit_Coupons_V4 FULL RAIL A B C FIT COUPONS - ONE EACH`; AMS physical slot 2; repo commit `3e8792b`.
- Profiles: Repro Generic PETG - 0.4 nozzle - Starter; process Repro Normal - 0.4 nozzle
- Process: layer_height 0.2, wall_loops 4, top_shell_layers 5, sparse_infill_density 20%, sparse_infill_pattern gyroid, support_type normal(auto), support_style tree_slim, support_on_build_plate_only 0, support_object_xy_distance 0.35, brim_width 5
- Filament: filament_flow_ratio 0.95, filament_shrink 100%, nozzle_temperature 255, hot_plate_temp 70
- Estimate: 1h 50m 46s; 47.02 g; 120 layers; 24.0 mm tall; toolpath audit passed.
- Parts: `A_R1_full_native_rail_X_to_print_Z` (11bb78ab79a1), `B_R2_full_native_rail_X_to_print_Z` (a2ec03ec6196), `C_R2_full_rail_plus_1mm_seat_relief_X_to_print_Z` (eb23e9dbe01a)
- Slice folder: `/mnt/c/Users/repro/Documents/Codex/2026-09-17/for-x20/work/quartet-team/architect/v4-orca`
- Notes: Recovered from the bridge job list (57 min actual).
- Lessons: All three V4 sizers bound: the tall lid-stop wall sat too close to the seat and fence. Fixed by moving the rail 3.5 mm outward in V5 (P-0003, the V5 coupons).

## P-0001 - D8 quick-fit bracket pair, pre-R4 revision (PETG)

- When: 2026-09-16 18:44; status: **printed**; job `b8c11d5e2216487ba26385df0b79d6fa`; file `D8-quick-fit-bracket-print-TWO_plate_1`; AMS physical slot None; repo commit `502a85e`.
- Notes: Pre-session print recovered from the bridge job list (2 h 36 m actual). Exact bracket revision not recorded; the D8 quick-fit R1/R2 sources are in desk-dock/D8/quick-fit.
- Lessons: Seat and fence needed the V-series coupons to converge; superseded by the R4-C pair (P-0004, the R4-C plate).
