# D9 P2 — no added metal hardware

Preserve the R2 contact profile and D9 P1 mouth geometry/fan pose. Replace every
added screw, nut and washer with printable mechanical connections. Purchased
fans still contain their normal motor and frame components; the plug mechanism
remains outside this revision.

The ten major parts now use 20 large printed pins and 20 flat locking keys:
eight fan pins, six internal plenum pins, four frame-end pins and two tie pins.
Sixteen keys have a 16-mm grip; four short keys have an 8-mm grip. The short
keys serve the two T-joint pins and two outboard lower fan sockets. Those two
fan sockets use side access through the cradle face; their neighboring inboard
lower fan keys insert from above, clear of the rear tie.
Floor-backed T joints transfer tie loads through shoulders; their pins prevent
uplift. The front tie/foot moved 20 mm forward from P1 to clear its accessible
printed retainers. Rear tie height remains 16 mm to clear the fans.

Pin sections: P2/P3 octagonal 8.2 mm across corners in 8.8 mm holes; P4 8.4 mm holes; from 19 September every pin is a round 7.9 mm shaft with a chord flat on the bed (0.5 mm diametral), after the octagons rattled and a round 8.2 mm trial would not enter the printed bores.
Pin axes print parallel to the bed, on a longitudinal flat. Head notches identify
fan (1), frame (2), seam (3) and T-joint (4) pins. The keys print flat and bend in
their layer plane. Long keys use 1.2 mm leaves; short keys use 1 mm leaves and a
longer rounded root. Barbs must compress inward by approximately 0.4 mm each
to pass a nominal 5.4 mm slot. These are design dimensions, not calibrated fits
or measured insertion force/fatigue limits.

Fan sockets are external and blind. No fan fastener enters the air wall, so the
nominal enclosure audit needs no idealized bolt seals. (P5, 18 September: optional
M4 screw path added as bonus holes: 4.5-mm guard clearance, 3.5-mm blind pilots 6 mm
deep in the flange on the 105-mm pattern. Still blind, so the audit is unchanged.) Thin seam sealant remains
optional for physical airtightness, not structural attachment.

Manufacturing: broad shell exterior X faces down, cavities up; guard faces down;
male T ties broad top down, female ties broad base down. Hidden accessible support
is acceptable. No slicer search for orientations; Orca verifies the selected poses.
The fastener and fit-test plates use 100% infill; the six main plates retain five
walls, six top/bottom layers and 40% gyroid PETG.

The small fit-test plate includes both blind socket arrangements and guard spacing,
exact cropped T-joint ends, three production pins and their keys. Test insertion, positive
retention and deliberate removal before committing to the full shell print.
Physical laptop fit, loaded stability, clip durability, creep, airflow and noise
remain separate qualification steps.


# D9 P3 delta (17 September 2026)

Cradle contact from the R4-C bracket profile: R2 seat plus the 1-mm local
relief that seated on the printed V5 C coupon, lid rail moved 3.5 mm outward,
rail 6 mm thick, fence outer face +2 mm, base kept at 4 mm so all feet stay
coplanar. Cosmetic edge treatment on shells, guards and ties (3-mm concave and
1.5-mm convex fillets on print-Z profile corners, 0.8-mm chamfer on tie top
edges, bed edges untouched) with every mating zone protected; air volume of
each module unchanged to the mm3. Pins, keys and fit fixtures identical to P2.


# D9 P4 delta (18 September 2026)

Cradle source R5-C: R4-C plus the 64-mm underside rail (6 mm, 2.25-mm running
clearance, 4 x 2 mm lead-in) at the cradle ends. Fit corrections from the
printed P2 fit plate: pin bores 8.4 mm (BORE_R 4.2), key barbs 7.2 mm wide
(KEY_BARB 3.6, 1.8 mm total interference), T tongue 12.7 mm (TONGUE_H; P4's 12.1 withdrawn). Plate 00
regenerated. Edge treatment and everything else as P3.

Revised the same day: the underside rail is on the plug-end cradle (module 1) only. The far-end cradle keeps the R4-C profile because the rear rubber-foot strip (x 30..323, starting 18 mm further out when undocked) slides through that cradle's x range during docking and would catch on a wall there.

# D9 P5 delta (18 September 2026)

Lean 8 degrees. R7 frame on both cradle ends with the socket void subtracted from the fused cradle; drop-in seat peg and fence peg per end locked by one horizontal fan pin (0.15-mm cam offset, push-out holes); plenum front wall 24 -> 26.5 for the 8-degree lid; plate 08 pegs, plate 09 cradle-end trial. P4 fit corrections kept.

Support-reducing gussets (18 September): ribs or 34-degree wedges under every external socket boss (clipped 0.5 mm clear of the tie envelopes) and a 34-degree wedge on the pin-tip end of each seam tab (bore extended through it). Proven additive-only against the previous geometry; air volume follows the material, audits unchanged.

Splice plate and centre contact (19 September): fixed splice plate (2-mm fin in the 2.3-mm gap, floor-following foot 0.5 mm above the corner feet, R7 outer wall and lid rail, flat shelf at z 51, bore and slot for the front lap pin and key, trimmed to the printed halves' envelope at 0.15 mm, epoxied) and an exchangeable centre contact (the unchanged 15-mm fence peg with its foot in the splice-plate channel, the seat head merged onto it through a plate bearing on the shelf). Gap trim (plate 10): L strip, 2-mm tongue in the gap, 1.2-mm flange 4 mm over the M2 front skin, traced from the dressed M2 end face, above the rear tie; prints flat. 59 printed parts.
