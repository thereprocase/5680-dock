# D7 print preparation - P1S / PETG / 0.4 mm

Use the individual parts and poses in the regenerated [print manifest](print-manifest.json). Do not print the assembled STEP as one object. The current release has geometric preflight evidence only: **it is unsliced, no toolpaths are approved, and nothing has been sent to a printer**.

The initial structural review profile uses **0.20 mm layers, five walls, six top and bottom layers, 100% rectilinear infill and an 8 mm outer brim**. Dense printed material is required for the initial arm, carrier, cams, axle, spring and fastening checks. Deliberately hollow CAD ducts stay hollow. Sparse infill is not credited as solid material in the calculations. Use temperatures and flow limits appropriate to the actual PETG spool; the recorded profile is a starting point, not a qualified material process.

## Orientation and support review

- Print the spring cartridge in its **unloaded shape**, with its common flat outside face on the bed. Its leaf length and bending stress run in the bed plane. The assembled viewer shows preload deflection and is not the shape to print.
- Print hand screws, nuts and large pins with their intended head or hand face on the bed and their shaft or thread axis upright. Use the manifest pose, then inspect layer strength and support-free access to the actual mating faces.
- Print bottom panels and fan grilles broad-face down. Inspect recessed panel wells and the grille's upper return. Its bars share the front print plane.
- Print the left plenum with its center-seam end wall on the bed; its tall hinge support prevents using the fan rim as a common bed plane. The right shell retains the fan-pocket-face pose. Inspect the long retention lip, trunk shoulder, rail roots, threaded bosses and connector support. Open bottoms allow support access but do not prove that the shells are support-free. Recheck the current manifest and brim fit after any change in fan thickness.
- Inspect the carrier, cap, keyed shim and keeper around their shoulders, bores and overhangs. The inverted cap starts on its taller rear clevis, leaving a 2.5 mm ledge under the broad face. The keyed shim starts on its underside key with a 4.3 mm peripheral ledge. Keep support scars away from thread roots, cam seats, pin bores and cable-contact surfaces.

Every part needs a working slicer's deposited-path and support-removal review before printing. Keep scale at 100%; correct a fit parameter instead of scaling the complete dock.

## Fit and load samples first

Use the current [8 mm and 10 mm thread samples](printed-fastener-review/) to choose a printed fit. These have real custom helical profiles; they are not interchangeable with ISO metric nuts. Use the [cap-pin samples](cassette-review/) and the actual 6.5 mm pin to assess insertion and withdrawal. The [cassette guide](CASSETTE_ASSEMBLY.md) records their current geometry and limitations.

Check the actual fan in its pocket, tune the grille's small friction lands, and fit the bottom-panel tongue before printing the full set. Refer to the current [coupon manifest](print/coupon-manifest.json) for supplied interface samples. Short samples do not capture whole-part warping, long sliding friction or warm creep.

The spring and cam need detached bench testing with a dummy plug. Verify alignment at 20 N, calibrate the release in each relevant load direction, reset repeatedly and repeat after a representative warm dwell. Keep the real laptop out of this test. The [holder and breakaway guide](arm-study/HOLDER_AND_BREAKAWAY.md) defines the targets and preload limit; 100% infill does not establish that they have been met.

## Geometric preflight and current limits

The [mesh preflight summary](print-review/mesh-preflight-summary.json) records source hashes, mesh checks, print bounds and individual P1S placement with the complete brim clear of the excluded bed area. Use its current results rather than a remembered part count or earlier dimensions. Angle screening does not determine bridge anchoring, support removal or actual deposited paths.

OrcaSlicer is the repository default. It was not relaunched after its reported crash. The earlier Bambu Studio CLI discovery fallback also failed; no successful slice is claimed from either application. The current checks use meshes and recorded printer/profile geometry without launching a slicer or contacting a printer.

A no-launch check of an exported part can be reproduced with:

```text
python desk-dock/D7/print_check.py --preflight desk-dock/D7/print/<part>.stl
```

The isolated fan, cover, cable and printed-lock geometry check can be reproduced without rebuilding or exporting the full assembly:

```text
python desk-dock/D7/form_service_isolated_check.py
```

Current assembly parts and hashes are recorded in [geometry.json](geometry.json), [print-manifest.json](print-manifest.json) and [package-manifest.json](package-manifest.json). Their evidence remains a geometric review until toolpaths and a physical prototype have been checked.
