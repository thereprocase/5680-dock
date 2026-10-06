# Large-shaft clamp pivot — CAD validation, 21 September 2026 (compact revision + carrier bearing land)

Branch `feat/carrier-bearing-land`, on top of the compact revision merged in PR #17. Everything below is CAD, slicer and mesh
evidence. Nothing was printed; no fit, torque, backlash or stiffness was measured.

## What was found before anything was changed

The polar plug positioner on `main` could not reach the laptop's USB-C port. The
port datum every earlier revision (D1–D7) uses, `rear_case_seat_z +
port_from_rear_case` at `port_y`, carried through the builder's own −8° lean,
puts port 1 at (y 11.39, z 119.03) — 59.4 mm from the old pivot at (45, 70) — and
port 2 at 72.2 mm. The tip pivot ran 108–148 mm from that pivot, the rotor pad
sat at x ≈ −60 for a 25-mm plug at x ≤ 0, and the first Ø100 draft's skirt cone
passed straight through the port-1 axis. None of the five validation scripts
referenced the port datum. `audit/port-reach.png` and `audit/plug-end-views.png`
are the renders that exposed it.

## What is on the branch

| item | value |
| --- | --- |
| pivot axis | (y 70, z 70), 25 mm lidward of the socket centre |
| shaft | Ø50 hollow (Ø30 bore); smooth journal x −63..−40 (23 mm) |
| thread | 47 × 3 mm, D8 trapezoidal, core 44.7, depth 1.15, crest 0.45; 0.35 radial / 0.15 axial clearance; x −75.5..−63 |
| stack (outboard is −X) | shoulder face −40 (plate 10 mm, Ø70) · arm disc −50..−40 (Ø70, bore 50.5) · cam spatula −60..−50 (10 mm) · keyed washer −62.5..−60 (Ø75) · knurled nut −71.5..−62.5 (Ø72, 16 flutes, 3 turns engaged, 4 mm spare thread) |
| nut lands | 0.5 mm inboard of the thread start; journal 0.5 mm longer than the clamped stack; nut face 71.5 mm outboard of the shoulder-side cradle face (was 101) |
| shoulder | socket stem + 6.5-mm bridge, 3-mm skirt Ø70→Ø80 with twelve 50° ribs, Ø80 backing ring on the cradle face; plate, skirt, ring and ribs cut clear of the bonded receiver; 144 cm³, 80 × 83 × 85 (was 274 cm³, 130 × 130 × 97) |
| arm | Ø70 × 10 disc; tongue 10 mm at the root, 20 mm deep from r 37.5; 25.6-mm sleeve, two length clamps 15 mm apart; tip 103.5–125.5 mm (22 mm travel); Ø12 hollow tip screw in a Ø28 clevis with 3-mm cheeks, r 13 eye |
| carrier | 18-mm eye/bar/plate; carrier block built in the plug frame (faces square to the plug, pre-rolled to the mean working angle plus the lean) from the cam face (x −49.9) to x −5; 14 × 13 mm window; walls 12 mm (thin, pivot side), 10 mm (screw side), 5 mm above and an **18-mm bearing land below** the window, so the back face bears on the lobe over 375 mm² at port 1 and 404 mm² at port 2 (5-mm walls gave 46 / 75 mm²); long edges rounded r 3.5, front face chamfered 1.5, window mouth flared 1.5 mm at 45°, back (bed, bearing) face square; the overmold is clamped **on its 6.5-mm flats** over x −17.5..−5 between the thin wall and a loose flat 7 × 11.5 mm bearing shim; M8 × 3 pinch screw (16-mm shank, flat tip seated in a Ø8.6 recess on the shim) through the 10-mm wall into a captured scalloped nut; r 4.7 relief behind the clamp zone for boots to Ø9. Clamped overmold axis (0.25 mm off the thin wall) is the reach target; window centre offset 3.5 mm |
| cam spatula | 10 mm; hub r 15–35; leaf lobe ≈ 50° of arc: radial near edge at 3°, spiral r = 58·e^(1.2θ) to 24° (r 96), spline tip and back edge; edge set 0.5 mm inside the window's nearest corner, lobe runs past the carrier |
| port 1 pose | arm 22.5°, tip r 107.6 (3.1 / 18.9 mm to the travel limits), rotor trim −1.9°, cam +44.4°, edge r 69.6 |
| port 2 pose | arm 18.7°, tip r 121.8 (17.3 / 4.7 mm), rotor trim +2.0°, cam +28.2°, edge r 78.7 |
| loosened sweep | −120° … +39° clear (3° steps), arm, carrier, pinch hardware and spatula moving together, against dock, laptop and desk |
| printed parts | 50 (48 on main − clevis/screw/nut/2 washers + shoulder, nut, keyed washer, spatula, pinch screw, pinch nut, shim) |
| plates | 12: 00 fit/alternates (4 h 40 m), 01–09 as before (08 socket + arms + carrier 6 h 37 m / 157 g (was 5 h 28 m / 142 g before the bearing land), 09 rings + hardware 3 h 27 m / 67 g), 10 shoulder 6 h 17 m / 144 g, 11 spatula + tip washers + shim 1 h 37 m / 35 g; all Orca toolpath audits pass |
| viewer | 53 entries (50 printed + laptop + two fans), 651,576 bytes, revision `D9-P5-CARRIER-BEARING-LAND`, cache key `clamp-20260921c`; offsets, index ranges and coverage validated by `validate_viewer_bundle.py` |

## Checks that run every build

- Port reach: solves the arm angle and reach that put the clamped plug axis on each
  port with the rotor trimmed so the window is square to the port (the trim rotates
  the window about the tip, so it is part of the solve); the window pre-roll is
  iterated to the mean working angle. Fails the build if either port is outside the
  travel. Both ports sit 3–4 mm from a travel limit — usable, but the slot could
  gain a few mm each way.
- Lobe bearing area: at each solved pose the cam is pushed 0.3 mm into the carrier and the
  overlap volume / 0.3 is reported as `lobe_bearing_area_mm2` (375 / 404 mm²). Reported, not
  asserted.
- Port-pose clearance: swings the arm and rotates the cam to each solved pose and
  intersects every moving part with every fixed part, the laptop and the desk, and
  with each other; passes a plug + boot + cable envelope through the port and the
  cam plate's band, and now against every moving part as well (this is what caught the
  shim sitting on the boot before the clamped-boot datum was introduced). Both poses:
  zero conflicts.
- Static interference (zero), insertion motion (zero), laptop and fan overlap
  (zero), watertight single-solid meshes, tessellation and bed size.
- First-order plug-axis compliance under 20 N, reported (not asserted), now including
  the shoulder plate + bridge as a cantilever over the 25-mm pivot offset in both
  directions: docking push (−X), through the cam lobe and shoulder: 0.25° at E 2000 MPa,
  0.33° at 1500; withdrawal pull (+X), through the arm and shoulder: 0.39° at 2000,
  0.52° at 1500. Not included:
  socket cartridge clearance (0.3 mm per side over 39 mm, up to 0.88° unless the M12
  bolt preloads it), clamp-face slip, layer anisotropy.

## Slicing notes

- Shoulder (plate 10): 6 h 17 m, 144 g; 39.3 k support segments inside the skirt
  (ribs and the bridge/stem lip). Open through the Ø56 ring bore. Inspect support
  access in the Orca GUI before printing.
- Carrier (plate 08): 3.2 k support segments, in the nut pocket, pinch hole and boot
  relief (all horizontal), window vertical.
- Outer arm: 6.5 k, under the inboard clevis cheek across the rotor slot.
- Spatula plate 11 (1 h 37 m, 35 g): spatula no support; shim 129 segments in its recess.
- Fit coupons (plate 00): shaft stub 21.8 k, nut 4.3 k, as before under the thread crests.
- Inner arm and pressure washer: no support.

## Gate status

`verify_and_package.py` passes the manifest, insertion-motion and plate gates and
stops at the legacy enclosure audit, which fails for M1 and M2 exactly as on the
base and recovered rebuilds (see RECOVERY-VALIDATION.md). It was not altered. No
production ZIP was generated.

## Not established

Thread fit and drag (print the two full-diameter fit coupons first), clamp holding
torque, backlash after tightening, plug-axis tilt at 20 N in both directions (dial
indicator on the boot), the cam set-up by hand, lobe face contact once printed,
the socket cartridge's clearance under the 45-mm offset moment, rear-frame-L pin
extraction past the Ø100 ring, support removal inside the shoulder, and the real
cable boot against the 14 × 16 mm window.
