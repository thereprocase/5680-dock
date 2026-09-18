# 5680-dock — working notes for Claude Code

Read AGENTS.md too (slicer and print-design rules, Gridline site rules). This
file covers where things actually live and how to get a fit coupon printed
without rediscovering the environment.

## Where the pipeline lives

Snapshots of the pipeline sources are in this repo: `tools/coupon-pipeline/`
(coupon and mixed-plate scripts, profiles, audits) and `desk-dock/D9-P5/` (the
P5 dock builder and its inputs). The LIVE working copy, with generated geometry
and slice folders, is the Codex work tree
`C:\Users\repro\Documents\Codex\2026-09-17\for-x20\work\quartet-team\`
(WSL: `/mnt/c/Users/repro/Documents/Codex/2026-09-17/for-x20/work/quartet-team/`):

- `geometry/profile-v2 … v5/` — CadQuery builders; `generated/` holds STEP/STL,
  previews and `manifest.json` with hashes. V5 = V4 with the lid rail moved
  3.5 mm outward (`build_full_rail_coupon_v5.py`).
- `architect/` — `run_coupon_pipeline.py` (one command: place → Orca slice →
  toolpath verify → identifier audit → optional package), the individual
  scripts it calls, `profiles/` (see below), `vN-orca/` slice folders,
  `V5-GEOMETRY-REVIEW.md`, `V5-PRINT-KIT-README.md`.
- `verification/` — `audit_v5_id_holes.py`, `verify_v5_geometry.py`.
- Mixed plates (brackets + small parts): `architect/prepare_mixed_plate.py`
  (footprint-aware, `--rot`/`--strict` per `--stl`), `verify_mixed_plate.py`,
  `package_plate.py`. Example: the R4-C pair + P2 fit parts in `r4-C-8h-orca/`.
- Packaged kits: `...\for-x20\outputs\5680-design-team\PRINT-ME-*` and `D9-P*-PRINT-KIT`.
- D9 dock passes: `work/d9-p2-print-pass/` (frozen P2), `d9-p3-print-pass/`, `d9-p4-print-pass/`
  and `d9-p5-print-pass/` (current: 8° lean, R7 frame, drop-in pegs, plate 09 trial). Chain there:
  `cadpy build_d9.py` → `cadpy verify_enclosure.py` → `cadpy prepare_and_slice.py`
  → `cadpy verify_plates.py` → `cadpy verify_and_package.py`. Edge rules: fillet
  print-Z profile corners, chamfer tops, never bed edges, protect every mating zone.

The R4 loaded bracket pair builder is in this repo: `desk-dock/D8/quick-fit/R4/build_quick_fit.py --variant A|B|C`
(run with `cadpy` from that folder; needs `desk-dock/history/reference-assets/laptop.glb`).

This repo supplies only `desk-dock/D8` inputs (parameters.json, quick-fit R1/R2
STEPs and JSON). The R2 quick-fit files are untracked in the main checkout at
`/mnt/f/code/5680-dock-fit-20260917`; builders take `--d8 F:\Code\5680-dock-fit-20260917\desk-dock\D8`.

## Python and slicer

- `cadpy script.py …` (in `~/.local/bin`) runs the Windows CadQuery venv
  `F:\Code\tmp\5680-cad-env` (CadQuery, trimesh, scipy, Pillow) from WSL and
  converts `/mnt/...` paths. No WSL Python has CadQuery.
- OrcaSlicer 2.4.2 CLI: `C:\Program Files\OrcaSlicer\orca-slicer.exe`, driven by
  `architect/run_coupon_orca.py` under `cadpy`.

## Print profiles (`architect/profiles/`)

- `frozen-normal/` — the "Repro Normal" 0.20 mm structural set used for V4/V5.
- `structural-8h/` — Repro Normal with 15 % grid infill; walls/shells unchanged so P2 pin/key
  clearances hold. Used for the R4-C pair + fit-parts plate (7 h 05 m).
- `coupon-fast/` — "Repro Coupon Fast" (0.28 mm, 3 walls, 3 top/bottom, 15 % grid,
  no brim, 0.15 mm elephant-foot) plus "Repro Polymaker PETG" (16 mm³/s, 260 °C;
  flow ratio and pressure advance still placeholders until calibrated).
  Use this for handheld fit coupons. One coupon ≈ 29 min / 13 g.

## Fit-coupon workflow

1. Change geometry in a new `geometry/profile-vN/` builder that imports the
   previous one; run it with `cadpy`; read `generated/manifest.json`.
2. Write `architect/VN-GEOMETRY-REVIEW.md` (hashes from the manifest).
3. `cd architect && cadpy run_coupon_pipeline.py --stl <1..3 STLs> --profiles profiles/coupon-fast --out vN-orca --review VN-GEOMETRY-REVIEW.md [--package <out> --geometry-dir ../geometry/profile-vN --readme VN-PRINT-KIT-README.md --title "…"]`
4. Print: `p1s-print <slice-dir or package>/OPEN-ME.3mf 1` (physical slot;
   see the `p1s-print` skill). Check `p1s-status` first.
5. Publish: copy the kit zip and 3MF to `docs/printables/fit-vN/`, update
   `docs/handoff-2026-09-17.html`, `docs/handoff/2026-09-17/NEXT-STEPS.md`,
   `docs/index.html` and `docs/desk-dock.html`. GitHub Pages serves `main`.
   Commit and push only when asked.

Default to a single coupon (usually C, or B) for a quick trial; print all
three only when the variants are the question.

Bracket revisions R1–R7 live in `desk-dock/D8/quick-fit/` (R7 = modular peg
frame; run its builder with `cadpy` from that folder). After changing pipeline
sources on C:, refresh the snapshots here so GitHub stays current.

## Git hygiene

The checkout at `/mnt/f/code/5680-dock-fit-20260917` sits on a stale branch
with line-ending noise across ~1000 files. For site edits use a worktree from
`origin/main` (2026-09-17: `/mnt/f/code/5680-dock-v5`, branch `fit-v5-rail-offset`).
