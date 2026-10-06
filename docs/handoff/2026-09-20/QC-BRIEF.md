# QC brief — Precision 5680 desk dock, D9 P5

Written 2026-09-20 for an agent picking this up cold. Repo `thereprocase/5680-dock`,
branch `main`, commit `4af3e3b`, site https://thereprocase.github.io/5680-dock/.
Everything described here is on main and on GitHub.

## What you are checking

A printed laptop dock. Two plenum halves (M1, M2) meet in the middle; a four-clip
ring splices them. The most recent change made that joint one consistent thickness.
Your job is to reproduce the claims below and to form an independent opinion on the
three open issues. Do not change geometry unless the owner asks.

## Where things are

The **live work tree** is on the Windows side and holds all generated geometry and
slice folders:

```
/mnt/c/Users/user/Documents/Codex/2026-09-17/for-x20/work/d9-p5-print-pass/
```

The repo carries a **snapshot** of the sources in `desk-dock/D9-P5/` (builder,
plate script, DESIGN.md, README.md) plus the published plates, kit and viewer under
`docs/`. If the two disagree, the work tree is what was actually run; refresh the
snapshot rather than editing it in place.

CadQuery runs only through `cadpy`, a wrapper on the Windows venv. No WSL Python has
CadQuery. Run everything from the work tree.

## The chain

```
cadpy build_d9.py          # geometry, interference and motion checks
cadpy verify_enclosure.py  # both plenums closed, each port open
cadpy prepare_and_slice.py # 11 plates through OrcaSlicer 2.4.2 CLI
cadpy verify_plates.py
cadpy verify_and_package.py
cadpy export_viewer_p5.py  # optional, writes the 3D viewer model
```

`prepare_and_slice.py` refuses to overwrite an existing `plates/` folder. Move it
aside first. A full chain is roughly fifteen minutes.

## Claims to reproduce

| claim | expected |
|---|---|
| printed parts | 64 |
| interferences | none |
| enclosure audit, module 1 and module 2 | both pass |
| splice clips, body count each | 1 |
| clip volumes, back / front / fan / floor | 6555.6 / 1556.8 / 1083.2 / 964.2 mm3 |
| centre fence volume | 1240.0 mm3 |
| joint fill, ideal | 4929.1 mm3 |
| joint fill, achieved | 4923.1 mm3 |
| unfilled, the four key clearances | 5.9 mm3 |
| ASA plate 18, ring plus fence plus three keys | 13.24 g, 49 m 56 s, zero support |
| kit SHA-256 | 2ab6cc67d790bc835da249f38d3c77dc4451aa5f8f6a3bfaa46e6db9692eaa23 |

`build_d9.py` prints the joint-fill line and the per-clip body list itself.

**Counter mismatch, not a discrepancy.** `verify_and_package.py` reports
`support_segments`, which counts slicer segments. Ad-hoc analysis in this session
counted support *extrusion moves* from the G-code. The two differ by roughly ten
percent on the same plate. Compare like with like.

**Where the G-code lives.** Each plate's `sliced.3mf` holds `Metadata/plate_1.gcode`.
The ASA plates under `asa/` keep a loose `plate_1.gcode` as well. Bambu flavour marks
extrusion type as `; FEATURE: Support`, not `;TYPE:`.

## Zero-support claim, stated precisely

The splice ring, the centre fence and the three glue-up alignment keys slice with no
support at all. Verified three ways:

- Plate 10, the three alignment keys on their own: zero.
- ASA plate 18, the whole set: zero.
- Plate 08 mixes the ring and fence with the seat pegs, fence pegs and insert pins.
  That plate does carry support, about 4,300 moves, but all of it lies below y = 98
  while the clips sit at y = 110 and beyond. Nothing falls inside the clip or fence
  footprints. Re-check this rather than taking the plate total at face value.

## Open issues, worst first

**1. The ties are the largest unexplained support load.** On plate 05 every one of
7,630 support moves belongs to the two front ties; the fan guard on the same plate
has none. The support concentrates between 4.8 and 12.0 mm on a 16 mm tall part,
which is the pin-bore band. Teardrop bores with a tangent crest at 40 degrees were
added to fix exactly this and did not reduce it. Measured overhang area on those
parts is only about 33 mm2, which does not explain thousands of support moves. The
cause is not identified. Plate 06 and the rear ties behave the same way. This is the
best target for a fresh pair of eyes.

**2. The outer cradles still carry heavy support.** The M2 outer cradle on ASA plate
14 slices with 17,329 support moves spanning the full 74 mm height. None of it is
trapped: of 489 sampled points, zero were enclosed by part material at their own
layer, and the two peg channels are clear. So it cleans out, but the support-reduction
work so far only covered socket bosses and seam-tab tips, never the cradle frame
pocket. Fixing it means re-printing plates 01 and 04, about 20 hours.

**3. The fan clip has no flange, by necessity.** Three of the four splice clips lap a
plenum skin: back onto M1, front and floor onto M2. The fan arc has no lap because the
fan mounting boss stands more than 5 mm proud of the plenum outline on that face of
both halves, leaving no free skin. Measured: a flange at the standard 1.2 mm proud
yields zero surviving volume in the lap slab anywhere along that arc, and it takes
6 mm of offset before any survives. That clip is held by a 3 mm key at each of its two
junctions and by the half-lap shiplaps into its neighbours, plus epoxy. An independent
structural opinion on whether that is sufficient would be worth having. An earlier
build put a flange there anyway and it came off as a disconnected island.

## Deliberately not verified

Nothing physical has been qualified: laptop fit under load, stability, clip retention
and durability, creep, airflow, noise, epoxy bond strength, and airtightness of the
printed seam. The enclosure audit is a nominal CAD check on closed volume, not a
leakage measurement. Pin fit is the one exception: 7.9 mm round pins in 8.4 mm bores
were printed and confirmed by hand on 19 September.

Also stale: the parts off ASA plate 17, printed 19 September, are the superseded
splice plate, centre contact and gap trim. Plate 18 replaces all of them. Treat the
plate 17 set as scrap.

## House rules you must follow

- **Printer.** Jobs go through the bambu-bridge on the Tailscale node `bambu-bridge`.
  The API key lives only on that node. Never read, print or copy it. Run curl on the
  node and source its env there. The only gate before submitting is the owner saying
  the plate is clear; ask every time. `ams_mapping` is zero-indexed, so physical slot
  N is N-1.
- **Bash.** Never put `$(...)` or backticks in a single Bash call. Split into two
  calls: run the inner command, then inline its literal output.
- **Foreign code.** Anything downloaded is inspected and hand-transcribed by
  understanding, never piped or pasted into the repo.
- **No claude.ai artifacts.** Deliverables go in the repo, on the Pages site, or in a
  local file.
- **Print log.** Every submission gets an entry via `tools/print-log.py add` right
  after the bridge accepts it, closed out with `update` when the part comes off.

## Print state as of 07:00, 20 September

Plate 18, the splice ring, is on the printer as job `01a7a8be`, slot 3 ASA. Plate 14
is done. Plate 16, the M2 fan guard, two hours, is the last plate for a complete dock.
