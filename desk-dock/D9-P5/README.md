# Precision 5680 D9 P5: current cleanup prototype

The generated manifest is the inventory authority: **49 installed printed
parts**, two purchased wire fan guards and eight M4 x 35 fan screws. Two
120 x 120 x 25 mm fans and the laptop are reference/purchased bodies, outside
that ten-item fastening-hardware count. Fit coupons and the alternate fan-only
socket blank are not installed assembly parts.

This revision uses the 8-degree R7 cradle frame, three one-piece H contact
cassettes, bonded scalloped plenum-half joints, a two-piece centre splice ring,
and a polar plug positioner on a large-shaft face-clamp pivot (50-mm hollow shaft,
70-mm arm disc, leaf-lobe cam spatula braced under the plug carrier, knurled 72-mm nut
on an outboard 47 x 3 mm printed thread, keyed pressure washer) with printed clamps,
thrust washers and an independent laptop slide stop. The pivot is offset 25 mm lidward of the accessory socket so the arm
can reach the laptop's USB-C ports; the builder now solves and checks that reach
(`generated/port-reach.json`) and reports a first-order plug-axis compliance estimate
against the 0.5-degree-at-20-N target; that number is a beam estimate, not a measurement. Retired printed fan guards, separate seat/fence
pegs, four individual splice clips and Cartesian plug-holder parts are invalid
manufacturing inputs.

The splice arcs alternate shell capture: back and fan lap M1; front and floor
lap M2. The fan-seat plate has an exact 1.2-mm-deep pocket with about 3.85 mm
axial engagement. The ring replaces that material flush and supplies 297.6 mm3
of fan-arc engagement without moving the fan face or nominal airway. The
builder asserts positive engagement on all four arcs. Four registration-key
clearances account for the remaining 5.9 mm3 of joint void (about 0.12%).

## Build and review

Use Python with the repository's pinned CadQuery/trimesh dependencies, from
this directory:

```text
python build_d9.py
python export_viewer_p5.py viewer-export
python verify_enclosure.py
python prepare_and_slice.py
python verify_plates.py
python verify_and_package.py
```

The builder removes stale disposable files from `generated/` only; retain
independent evidence outside that directory. Assembly exports are named
`D9-P5-assembly.step` and `D9-P5-assembly.png`. Manufacturing STEP files use
assembly coordinates; STL files carry the intended print orientations.

`prepare_and_slice.py --prepare-only` writes placed 3MFs without slicing.
Preparation refuses to overwrite existing plate folders. The native Windows
Orca CLI uses the frozen profiles in `profiles/`, with arrangement and
orientation disabled. Packing reserves room for 5-mm brims and the front-left
exclusion zone. Each installed part must appear exactly once.

## Current plate inventory

| Plate | Contents |
| --- | --- |
| 01 | M1 outer cradle shell |
| 02 | M1 inner shell |
| 03 | M2 inner shell |
| 04 | M2 outer cradle shell |
| 05 | Four frame ties |
| 06 | Three H contact cassettes, two cassette pins, upper and lower splice rings |
| 07 | Six frame/tie pins and six keys |
| 08 | Accessory socket, inner arm, outer arm and plug carrier |
| 09 | Clamp nut, keyed pressure washer, plug-positioner screws and nuts, clamps, carrier pinch screw and nut, endstop and soft-tip geometry |
| 10 | Clamp shoulder (ring on the bed, 50-mm shaft and 47-mm thread vertical) |
| 11 | Leaf-lobe cam spatula, two tip thrust washers and the carrier bearing shim (all flat) |

Plate 00 contains the two T-joint fit coupons, the alternate fan-only socket
blank, and the full-diameter clamp fit coupons (47-mm threaded shaft stub with
both keyways, and the real knurled nut). Print and hand-turn that pair before
trusting the clamp thread. The generated cradle-end trial is an optional separate STL, not plate
09. Do not use earlier plate packages or their historical part counts.

Thread axes are vertical for the accessory clamp, slide stop, both annular
pivots and both length clamps. Frame pins remain horizontal on their
longitudinal chord flats. Washers lie flat. Do not auto-orient these parts.
The upper splice ring needs localized support under its opposing flange and
fork; inspect support access before committing to a print.

The frozen profile is a 0.4-mm P1S Generic PETG Starter at 0.20-mm layers, five
walls and six top/bottom layers, with 40% gyroid on structural plates and 100%
on plates 00, 06, 07 and 09. These are **review slices**. In particular, the
plate-09 PETG soft-tip shape does not make a flexible bumper: that part needs
a separate flexible-material profile and slice before functional use.

## Assembly and qualification

Dry-fit and clean supports before bonding the scalloped plenum joints and
centre ring with epoxy. Standard wire fan guards replace the printed guards;
use the specified M4 x 35 screws and check retention in the blind pilots.
Install the contact cassettes, frame ties, polar linkage and independent depth
stop before adjusting plug alignment. Thread fit, epoxy procedure and clamp
loads need physical trials.

The recovery rebuild passed single-solid/watertight export, nominal part,
laptop and fan interference, sampled insertion, positive splice engagement,
fan-seat gap and unchanged nominal airway checks. See
[RECOVERY-VALIDATION.md](RECOVERY-VALIDATION.md) for the actual recovery run.

**The legacy bare-shell enclosure test fails on both the base and recovered
revisions.** It detects exterior-connected air with the ports capped; bonded
seam sealing has not been qualified. `verify_and_package.py` retains this
release gate and refuses to label the current slices a verified print kit.
Nominal airway preservation does not prove airtightness.

Printed thread durability, clamp holding force and backlash, accessory-socket capacity,
epoxy fit/bonding, loaded laptop support, screw retention, cooling, support
removal and full docking/plug alignment remain physical-test questions.
Successful CAD and Orca checks do not establish those results.
