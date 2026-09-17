# Precision 5680 — next steps after the 17 September handoff

Work is paused at this checkpoint. The kit and full evidence are filed locally
in `outputs/5680-design-team/CLOSEOUT-20260917/`. V4 means the full-height A/B/C **fit
coupons** below. The separate D9 duct's proposed V4 is only a construction
plan; it is not the printable V4 fit kit.

1. **Print the V4 fit coupons.** Open the supplied 3MF in OrcaSlicer. The
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
4. **Rebuild the D9 duct and its supporting frame.** Resume from the saved
   shared air-volume / flat-panel construction proposal. Derive every panel
   from the same boundary; specify joints, hardware, fan clearance and service
   access. Structural frame and cross-ties carry laptop/docking loads.
   Independently verify nominal enclosure, both named open ports, sections,
   actual fan clearance, and every selected bed face/underside. V3 and R1 are
   failed diagnostic references; do not print them. D9 V4 has no CAD release.
5. **Verify manufacturing after geometric design.** Once that assembly passes
   geometric review, use Orca to verify the chosen orientations, supports,
   bridges, small features and bed clearance. Correct specific demonstrated
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
