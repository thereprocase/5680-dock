# Precision 5680 slide-in desk dock — D0 concept

[CAD overview](concept.png) · [Review STEP](Desk_Dock_CONCEPT.step) · [Parameters](parameters.json)

An independent design branch from the M1.1 wall mount. Set a closed Precision
5680 into an upright trough, hinge up, then slide it sideways into the original
SD25TB5 host plug. Pull it sideways to disconnect before lifting it out.

**D0 is a mechanism layout, not a printable or precision-mating release.** The
STEP includes separate unfastened component envelopes. It does not yet resolve
guide attachments, cassette adjustment hardware, cable strain relief or the
lift interlock. Port and overmold dimensions are explicit placeholders.

## Mechanism

- Two padded saddles support the laptop's front edge. Replaceable low-friction
  face liners register its base surface; the lid must not establish port position.
- A local guide at port height controls lean before the plug reaches the port.
  Tapered entry geometry and compliant opposing pads belong in the next revision.
  The modeled square guide blocks only reserve their space.
- A split cassette captures the original Dell overmold mechanically in both
  insertion and extraction. It must locate on measured shoulders and retain the
  cable without crushing it. Do not clamp the metal USB-C shell.
- Slotted setup adjustment establishes port height; lateral shims establish the
  base-to-port offset. A small spring-centered transverse float is proposed for
  residual alignment error. Float is not a substitute for accurate registration.
- An independently adjustable, padded chassis stop defines full engagement.
  Set it from the actual fully seated connector; do not infer insertion depth
  from generic USB-C dimensions. The connector must not absorb the user's push.
- Add a mechanical lift keeper that releases only after sideways withdrawal.
  The current layout does not protect against lifting a connected laptop.
- Retain the original cable and provide a relaxed service loop and separate
  strain relief. The SD25TB5 electronics stay elsewhere on the desk.

The 18 mm withdrawal shown in the parameters is a design allowance, not a
measured connector stroke. Either left-side Thunderbolt port can be the target
after its coordinates and neighboring connector clearances are measured.

## Why the base needs restraint

An illustrative 15 N docking push at 205 mm above the desk creates 3.08 N·m.
For a centered 2.5 kg laptop, the docked center lies about 158 mm inside the
left foot edge, providing about 3.87 N·m of gravity resistance in the insertion
direction, excluding stand mass. That is only a 1.26 ratio for this assumed
push. With laptop weight alone, resisting 15 N of sliding also requires a
friction coefficient of about 0.61. Neither calculation qualifies this stand.
Use the modeled desk screw points or develop a desk-edge clamp, then verify
sliding, tipping and frame deflection for the actual layout. The 15 N is an
assumed test load, not a Dell connector specification.

## Measurements needed to release mating geometry

Use the laptop's **front edge** (bottom of the upright stand) as the height
datum and its **underside base surface** as the thickness-direction datum.
Measure the closed machine where the support and guides will contact it.

| Measurement | Purpose |
|---|---|
| Front edge to center of each left USB-C port | Cassette height and port selection |
| Underside base surface to each port center | Transverse alignment, independent of lid thickness |
| Closed thickness at lower supports and near ports | Pad spacing and guide taper |
| Front edge curvature / chamfer and rubber protrusions | Repeatable vertical seating |
| Plug overmold length, width, thickness, taper, shoulder locations | Positive split-clamp capture |
| Exposed metal length and overmold-to-chassis gap when seated | Calibrated chassis stop |
| Cable diameter, exit direction and relaxed bend envelope | Strain relief and service clearance |
| Clear chassis contact zones around target port | Guide/stop placement without obstructing ports or vents |

Straight-on photos of the left edge and the plug beside a ruler can establish
the layout. Calipers and an actual fit coupon must establish final mating fit.

## Qualification sequence

1. Confirm the assumed upright orientation and that manual SD25TB5 connection
   already supplies the desired charging, display and peripheral behavior.
2. Measure the interface and rebuild the cassette, supports and local guide.
3. Print only the interface coupons; inspect in OrcaSlicer (repo default).
   Establish material, shrinkage, pad compression and slot clearance empirically.
4. Fit a dummy connector first. Verify the laptop seats and registers before
   contact; verify the stop and withdrawal/lift interlock independently.
5. Fit the real plug with the stop backed off. Align without forcing, calibrate
   full seating, then check repeated insertion/extraction and case marking.
6. Test warm loaded behavior, cable tug, base restraint and accidental lift.
   Measure charging and thermal behavior during a representative workload.

No final STL, sliced plates, connector-force certification or physical fit claim
is supplied at D0. Long rails would need metal stock or segmented printed
construction for the P1S; the current one-piece spine represents metal stock.

## Sources and uncertainty

- [Dell Precision 5680 product specifications](https://www.dell.com/en-us/shop/dell-laptops/precision-5680-workstation/spd/precision-16-5680-laptop):
  353.68 × 240.33 mm; front/rear heights 20.05/22.17 mm.
- [Dell owner's manual dimensions](https://www.dell.com/support/manuals/en-si/precision-16-5680-laptop/precision-5680-owners-manual/dimensions-and-weight?guid=guid-362133ff-c5e8-4acd-a164-4ce876572659&lang=en-us):
  353.68 × 240.27 mm, height 26.17 mm. This conflicts with the product page.
  D0 uses the larger thickness envelope; it does not resolve the discrepancy.
- [Dell external ports](https://www.dell.com/support/manuals/en-us/precision-16-5680-laptop/precision-5680-owners-manual/external-ports-and-slots?guid=guid-b8f739cc-a41e-4ac9-b3f8-ff6d9c6d8c19&lang=en-us):
  two Thunderbolt 4 ports and a separate USB 3.2 Gen 2 Type-C port.
- [SD25TB5 specifications](https://www.dell.com/en-us/shop/dell-pro-thunderbolt-5-smart-dock-sd25tb5/apd/210-brqs/docks):
  original host cable and up-to-300 W Dell-system rating. That rating alone
  does not establish the 5680's negotiated charging power.

Retrieved 2026-09-08. No dimensioned port/overmold drawing was established.

## Reproduction and record

Run `python desk-dock/build_concept.py` with CadQuery 2.8 and Matplotlib.
The builder exports a named STEP assembly, a CAD-derived PNG and a per-solid
validity report. These checks establish valid solid geometry only.

User brief: “another fork … Dell 5680 … slide-in desk bearing dock … securely
mount a Dell SD25TB5 plug … plop my laptop into the trough and slide it up
against the TB plug … precisely insert into one of the two USB C side ports.”

D0 decision: preserve the wall designs, develop a separate passive mechanical
dock, and keep unmeasured interface dimensions visible rather than presenting
an inferred envelope as a precision fit.
