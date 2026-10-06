# TODO

- [x] Redesign the plug-positioner base pivot as a large face clamp (implemented on
  `feat/large-shaft-clamp-pivot`, `desk-dock/D9-P5/build_d9.py`).
  - Shaft: hollow **Ø50 mm** (Ø30 bore), smooth journal, outboard flat-crested 47 × 3 mm
    trapezoidal thread (depth 1.15, crest 0.45, 0.35 radial / 0.15 axial clearance, 3 turns
    engaged, 4 mm spare). The brief said approximately Ø100; the Ø100 draft could not reach
    the port, Ø75 (PR #16) could, and the compact Ø50 revision is what face-friction torque,
    three thread turns and finger room actually need.
  - Arm base disc Ø70 × 10 with a Ø50.5 bore on the journal; keyed Ø75 pressure washer in
    two journal keyways; knurled Ø72 nut with sixteen flutes; nut face 71.5 mm outboard of
    the shoulder-side cradle face. Nut lands 0.5 mm inboard
    of the thread start; journal is 3 mm longer than the disc.
  - Shoulder: bridge from the socket stem, 3-mm skirt narrowing from a Ø80 backing
    ring on the cradle face to a Ø70 × 10 shoulder plate, twelve 50-degree internal ribs so
    the plate prints without support, cut clear of the bonded receiver and of the
    rear-frame-L pin's extraction path.
  - The pivot axis is offset 25 mm lidward of the socket centre, to (y 70, z 70).
  - Full-diameter fit coupons: `clamp-shaft-fit-coupon` (47-mm thread stub with both
    keyways) and `clamp-nut-fit-coupon` (the real nut), on plate 00.
- [x] **Port reach.** The polar arm on `main` could not reach either USB-C port: the
  D1–D7 port datum (`rear_case_seat_z + port_from_rear_case`, `port_y`) puts port 1
  59.4 mm from the old pivot while the tip ran 108–148 mm, and the rotor pad sat at
  x ≈ −60 for a 25-mm plug. The builder now solves the arm angle and reach for both
  ports, swings the arm there, passes a plug-and-boot envelope through the port and
  fails on any contact (`generated/port-reach.json`). Port 1: arm 22.5°, tip r 107.6 mm
  (3.1 / 18.9 mm travel margin); port 2: 18.7°, 121.8 mm (17.3 / 4.7 mm). Loosened
  sweep clear from −120° to +39° (3° steps) against dock, laptop and desk.
- [x] Plug carrier cranked to put its 14 × 13 mm window 34 mm lateral and 41 mm inboard
  of the tip; the block is built in the plug frame (rolled −28.6°, faces square to the plug),
  spans the cam face (x −49.9) to x −5, and carries a 16-mm M8 × 3 pinch screw into a
  captured scalloped nut. Walls: 12 mm thin (pivot) side, 10 mm screw side, 5 mm above the
  window and an 18-mm bearing land below it, so the back face bears on the leaf lobe over
  375 / 404 mm² at the two ports instead of the 46 / 75 mm² sliver 5-mm walls gave. Long
  edges rounded r 3.5, front face chamfered, window mouth flared; back face left square. The plug is clamped on its overmold flats between the thin wall and
  a loose flat 7 × 11.5 bearing shim (screw tip in a recess on the shim), so it cannot roll;
  the window is relieved behind for Ø9 boots. The clamped overmold axis is the reach target
  and the rotor trim is part of the reach solve.
- [x] Plates 08–11 rebuilt (12 plates, all toolpath audits pass), viewer regenerated (53
  entries, 651,576 bytes, revision `D9-P5-CARRIER-BEARING-LAND`, cache key
  `clamp-20260921c`), arm toggle still defaults off including after Reset. 50 printed parts.

- [x] **Plug-axis stiffness target: ≤ 0.5° tilt at 20 N along the plug axis** (user,
  2026-09-20). Rather than a deeper arm, a separate 10-mm leaf-lobe spatula (50° of arc, spiral
  r 58→96 to 24°, spline tip) rides the journal outboard of the arm disc, pinched by
  the same nut; it is turned until its edge runs up to the plug boot, and the carrier's back face bears on the lobe, so
  the docking push loads a clamped plate. Arm: 10-mm tongue root, 20 mm deep from r 37.5, 25.6-mm sleeve.
  Beam estimate (manifest `accessory_socket.reach.plug_axis_compliance_estimate`):
  docking push through the lobe and shoulder 0.25–0.33°, withdrawal pull through the arm
  and shoulder 0.39–0.52°; not asserted, not a measurement.

## Not yet qualified (physical)

- [ ] Print and hand-turn the shaft/nut fit coupon pair before printing the shoulder:
  thread fit, drag, whether 0.35 / 0.15 mm clearance is right for the P1S PETG profile.
- [ ] Clamp holding torque: how much nut torque the arm needs to stay put under plug
  insertion and cable pull; whether the keyed washer stops the arm creeping.
- [ ] **Plug-axis tilt at 20 N, dial indicator on the plug boot**: the acceptance test for
  the 0.5° target. The estimate excludes the socket cartridge's 0.3 mm/side clearance
  (worth up to 0.88° of rocking unless the M12 bolt preloads the stem against one face),
  clamp-face slip and layer anisotropy.
- [ ] Backlash and play at the port after tightening (journal 0.5 mm diametral, thread
  clearances). The large diameter does not remove it by itself.
- [ ] Shoulder stiffness under the plug load, and whether the Ø112 ring / socket clamp
  bolt hold the 45-mm offset without rocking.
- [ ] Rear-frame-L pin extraction past the Ø100 ring with fingers/pliers.
- [ ] Cam lobe: set-up procedure by hand (loosen, set arm, turn lobe to the boot, tighten); does the
  lobe edge actually touch the boot without pinching the cable; lobe face contact area once printed.
- [ ] Carrier clamp on a real cable: the 6.5-mm flat is the spec maximum; a thinner overmold just
  takes more screw travel. Check the boot (relief to Ø9) and that the pinch does not crush anything.
- [ ] Both ports sit 3–4 mm from a travel limit; lengthen the tongue slot a few mm each way if the
  bench setup wants more. Rotor roll trim is ~9° toward the sleeve,
  free away from it.
- [ ] Support removal inside the shoulder (through the Ø78 ring opening), in the
  rotor's pocket window and under the outer arm's inboard cheek.
- [ ] Legacy enclosure gate still fails (pre-existing, both modules); no verified
  production ZIP until the bonded-seam sealing model is replaced.
