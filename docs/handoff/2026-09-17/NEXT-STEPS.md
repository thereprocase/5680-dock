# D9 P5 — 18 September 2026 (current model)

Lean 8°. Modular contact on the R7 frame: seat peg per machine, fence peg
per end (tall at the plug end), one horizontal fan pin with a 0.15-mm cam
offset, push-out holes; the 8° lid rail is the only fixed contact. Plenum
front wall 24 → 26.5 for the 8° lid. P4 fit corrections kept, except the T tongue,
which is back to 12.7 mm: the 0.6 mm “proud” reading was stuck support debris.
Round-shaft trial: the four frame-end pins are round 8.2 mm with a bed flat (the
printed octagons rattled in their 8.4 mm bores); judge them before converting the rest.
[Kit](../../printables/d9-p5/Precision_5680_D9_P5_Print_Kit.zip) · [fit plate](../../printables/d9-p5/OPEN-ME.3mf) · [notes](../../printables/d9-p5/README.md).

1. Plates 02, 03, 05, 06, 07 (668 g, 26 h 36 m) do not depend on contact geometry: start any time.
2. Fit plate 00 (40 g, 1 h 53 m) for the P4 clearances; pegs plate 08 (30 g, 1 h 19 m); plate 09 cradle-end trial (136 g, 7 h 01 m) to feel the 8° seat and peg fit before the cradles.
   Plate 01 (M1 outer cradle) printed in calibrated PolyLite ASA on 18 September. Overnight: 02 + 03 with the pegs,
   insert pins and round frame-end pins on one plate (`desk-dock/D9-P5/asa-10-receipts`); then 04, 05, 06, 07.
3. Outer cradles 01 and 04 (441 g, 20 h 03 m) once the pegs are trusted.
4. Other machines: re-head the pegs (`R7/build_quick_fit.py --demo-thickness`), the frame stays.

---

# D9 P4 — 18 September 2026 (current model)

[P4 kit](../../printables/d9-p4/Precision_5680_D9_P4_Print_Kit.zip) · [fit plate](../../printables/d9-p4/OPEN-ME.3mf) · [notes](../../printables/d9-p4/README.md). Fit plate 40 g / 1 h 53 m; plates 01–07 1,105 g / 46 h 31 m. The underside rail is on the plug-end cradle only; the far end keeps R4 because the rear foot strip sweeps through it during docking (0.47 mm overlap in X). No further leg prints planned; the formal model is P4.

The R4-C pair holds the laptop but nothing stops it tipping toward the
underside side. R5 raises the short fence at the bracket ends into a 6-mm
underside rail 64 mm above the seat datum (2.25-mm clearance, lead-in at the
top); feet and vents lie between the brackets. D9 P4 = P3 with the R5-C
cradles plus fit corrections from the printed P2 fit plate: 8.4-mm pin bores,
key barbs 1 mm more total interference (1.8 mm), T tongue 0.6 mm lower (withdrawn in P5).

1. Print the P4 fit plate 00 first and check pin friction, key retention and the T joint flush.
2. Print an R5-C bracket pair to feel the underside rail.
3. Then P4 plates 01 and 04 (cradles), and the five contact-independent plates whenever convenient.

Design note for later: make the seat, fence lower profile and hinge relief a
keyed insert per laptop so the two walls and brace stay common; try an 8-degree
lean on a bracket pair before changing the dock pose.

---

# D9 P3 kit — 17 September 2026 (late)

P3 = P2 with the outer cradles on the R4-C contact profile (V5 C seat, lid
rail +3.5 mm, thicker rail/fence, 4-mm base) and a printable edge treatment on
shells, guards and ties (fillets on print-axis corners, chamfered tie tops,
bed edges and all mating zones untouched). Pins, keys and fit plate are
identical to P2. Enclosure audits pass with zero air-volume change; all seven
plates verified in Orca. [Kit]( ../../printables/d9-p3/Precision_5680_D9_P3_Print_Kit.zip) · [notes](../../printables/d9-p3/README.md).

1. After the R4-C pair carries the laptop, print P3 plates 01 and 04 (430 g, 19 h 45 m).
2. Plates 02, 03, 05, 06, 07 (668 g, 26 h 34 m) do not depend on the contact result and can start any time.
3. Nothing was sent to the printer for P3.

---

# R4-C bracket pair — 17 September 2026 (night)

V5 coupon **C seated** (R2 seat + 1-mm relief, lid rail 3.5 mm outward). The
R4 quick-fit bracket pair carries that geometry with thicker rail, fence,
base and brace (outward/downward only), and was sent to the P1S on one plate
with the ten D9 P2 fastener fit parts: about 7 h 05 m, 217 g, dark-grey PETG.

1. [R4-C plate](../../printables/r4-fit-pair/Precision_5680_R4C_Bracket_Pair_plus_P2_Fit.3mf) · [kit]( ../../printables/r4-fit-pair/Precision_5680_R4C_Bracket_Pair_plus_P2_Fit_Kit.zip) · [notes](../../printables/r4-fit-pair/README.md).
2. Test the pair loaded: seat engagement, rocking, lid-to-rail contact, nudge stability, docking travel. Trial the P2 pins, keys, sockets and T joint.
3. If the pair passes, apply the rail move and C seat to the D9 P2 outer cradles (plates 01 and 04) and re-slice them before printing the kit.

---

# V5 fit coupons — 17 September 2026 (evening)

The printed V4 A/B/C plate was handled against the laptop: all three coupons
were wrong in the same way and C (three openings) was still not enough. The
tall lid-side rail sits too close to the seat / hinge-bearing surface and the
short fence.

V5 keeps every V4 feature and moves the entire rail side 3.5 mm further away,
normal to the rail face; the deck between seat and rail grows by 3.5 mm. Seat,
fence, C relief and identifiers are unchanged. The plate was submitted to the
P1S through the bridge (PETG, AMS slot 1). V4 prints are superseded; keep them
apart from V5 (the deck between seat and rail is 3.5 mm longer on V5).

1. [Compare the V5 coupons](../../printables/fit-v5/Precision_5680_V5_Rail_Plus_3p5mm_Fit_Coupons.3mf) on the real laptop, same protocol as before. [Complete V5 kit with instructions](../../printables/fit-v5/Precision_5680_V5_Rail_Plus_3p5mm_Fit_Kit.zip).
2. If the lid still reaches the rail first, measure the remaining gap; do not guess another increment.
3. The P2 steps below still apply once the contact geometry is settled.

---

# D9 P2 no-metal update — 17 September 2026

P2 supersedes P1 for the current cradle, plenum, fan-guard and brace print kit.
No added metal hardware: 20 printed pins and 20 keys join ten major parts.

1. [Print the P2 fastener fit plate](../../printables/d9-p2/OPEN-ME.3mf). Check insertion, retention and deliberate removal. About 40 g / 1 h 52 m.
2. [Print the V4 laptop-contact coupons](../../printables/fit-v4/Precision_5680_V4_Full_Rail_Fit_Coupons.3mf). Resolve the reported seating issue before committing to large cradles; R2 contact geometry is retained.
3. [Download the complete P2 kit](../../printables/d9-p2/Precision_5680_D9_P2_Print_Kit.zip) and [read assembly instructions](../../printables/d9-p2/README.md). Plates 01–07 make one assembly; about 1,099 g / 44 h 54 m.
4. Dry-assemble braces on the bench and install internal plenum keys before fans. Test seating with the laptop independently supported, then qualify loading, retention durability, creep, cooling and noise.

The older diagnostic next steps below are historical. Instructions to finish the D9 CAD/enclosure are superseded by P2; physical fit and performance checks remain open.

---

# D9 P1 update — 17 September 2026

[Download the complete D9 P1 print kit](../../printables/d9-p1/Precision_5680_D9_P1_Print_Kit.zip). [Six native Orca plates and assembly instructions](../../handoff-2026-09-17.html#d9-printables).

Ten new parts have completed CAD, nominal enclosure and Orca path verification. Plug mechanism excluded. Physical contact and load qualification remain open; the fit trial below still applies. Earlier instructions to finish or repair the proposed D9 enclosure are superseded by this package.

# Precision 5680 — next steps after the 17 September handoff

Work is paused at this checkpoint. V4 means the full-height A/B/C **fit
coupons** below. The separate D9 duct's proposed V4 is only a construction
plan; it is not the printable V4 fit kit.

1. **Print the V4 fit coupons.** Download the [native Orca 3MF](https://thereprocase.github.io/5680-dock/printables/fit-v4/Precision_5680_V4_Full_Rail_Fit_Coupons.3mf) or [complete fit-kit ZIP with G-code and instructions](https://thereprocase.github.io/5680-dock/printables/fit-v4/Precision_5680_V4_Full_Rail_Fit_Kit.zip). Open the 3MF in OrcaSlicer. The
   frozen plate is one each of A, B and C, P1S / 0.4 mm / Generic PETG /
   textured PEI, 47.02 g and 1 h 56 m 58 s estimated. Check that this matches
   the actual printer and material. Keep the supplied orientations. No print
   has been sent. Use the complete kit for matching G-code, profiles and CAD.
2. **Compare first contact on the real laptop.** Independently support the
   laptop; gently present each coupon at the same section and pose. Record
   variant, first-contact surface (curved seat, short fence or tall rail),
   whether the seat catches, and any remaining rock/gap. Do not load the
   coupons or flex the rails to force a fit. The original four photos are
   already retained. No need to resend them.
3. **Resolve the contact profile before a full stand print.** Use the A/B/C
   observations and, where needed, direct local measurements to select the
   seat/capture geometry. A is original R1; B retains the actual R2 changes;
   C adds a local 1-mm relief to B. Improvement with B does not identify which
   of its changes helped; C does not measure lid thickness. Do not apply a
   blanket 4-mm change from the published overall thickness. Then check full
   rail engagement, loaded stability, docking alignment and connector stops.
4. **Reassess the D9 duct and complete its supporting frame.** Supports are
   welcome on hidden/internal surfaces with removal access. Protect outward
   finished surfaces exposed to users; prefer gentler overhangs and short
   bridges anchored at both ends over cantilevers. Nonzero downward-facing
   area alone is not a failure. Classify the existing tray/lid/coupler by
   visibility, support access, fit and load path before choosing a repair or
   panel split. Repair the independently observed enclosure leak and verify
   both named ports, sections, fan clearance, joints and service access.
   Structural frame and cross-ties carry laptop/docking loads. V3/R1 remain
   unqualified diagnostic references; D9 V4 has no CAD release.
5. **Verify manufacturing after geometric design.** Once that assembly passes
   geometric review, use Orca to verify the chosen orientations, supports,
   support removal, actual bridge direction/anchoring, visible surface finish,
   small features and bed clearance. Correct specific demonstrated
   defects. Start with the relevant joint/contact specimen and inspect physical
   assembly and leakage before a complete dock print. Do not search for a
   workable design by repeated slicing.
6. **Run the bounded duct-resistance screen when ready.** The selected future
   test is one module-1 10-CFM prescribed-flow load case, after released void,
   patch/diagnostic-plane, BC and mesh checks. The recorded limit is 15 minutes,
   4 CPU workers and 8 GiB. Report computed total-pressure loss and separate
   forward/reverse flow. This is not an 800-RPM operating-point prediction.
   ARCTIC's pressure test convention remains unresolved for such a claim.
7. **Test the assembled dock at two fixed 800-RPM fans.** Establish loaded
   retention, connector protection and service access, then check normal and
   displaced seating, useful airflow versus bypass, temperatures, noise and
   rattle. Compare fan-mount compliance with fan position, speed, grille,
   sealing and microphone position held fixed. Record repeatability. No
   measured cooling or acoustic improvement is established by this handoff.

If the earlier R3 scalloped retainer is reused, inspect the saved top_cut /
face_cut crest-overlap lead before promoting that surface. It was not resolved
or tested as an installed airflow path.

The 20-N docking and 50-N release values in earlier proposals are design/test
targets, not measured performance. The complete D8 CAD remains a reference;
the reported real seating problem is still open.
