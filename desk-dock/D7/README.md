# D7 - the plenum is the stand

**Saved for shutdown:** two corrected shell exports still need regeneration. The source is saved; this is not a print release. See [current status](CURRENT_STATUS.md).

The laptop leans 5 degrees onto the plenum. The recessed 120 x 120 x 25 mm fans keep their 18-degree plane and drop into open-top pockets; their grilles slide down into rails. Their suction faces preserve the intake space, with the frame thickness extending outward. Removable bottom panels expose the ducts, and two deck bridges join the halves. The low retention lip leaves the loading end open.

The connector sits on a keyed, calibrated carrier with a resettable cam-and-spring hinge. Its independent chassis stop stays fixed. The targets are at most 0.20 mm axial movement at 20 N and a 50 N-class release during misaligned docking. These are prototype targets, not measured performance or an impact-force limit.

All fastening hardware is printable: large coarse threaded locks, a 10 mm hinge axle and a 6.5 mm cap push pin. Fans, cables, ties, desk pads and compliant contacts remain separate functional materials.

Target: **PETG, Bambu P1S, 0.4 mm nozzle**. The current package is a **geometric preflight, unsliced**. OrcaSlicer has not been relaunched after its crash. No toolpaths are approved and nothing has been sent to a printer.

- [Interactive viewer](../../docs/desk-dock.html)
- [Review and assembly sequence](REVIEW.md)
- [Print preparation](PRINT_PREPARATION.md)
- [Holder stiffness and resettable breakaway](arm-study/HOLDER_AND_BREAKAWAY.md)
- [Connector assembly and calibration](CASSETTE_ASSEMBLY.md)
- [Fan service](FAN_SERVICE.md) and [lay-in cable routing](CABLE_ROUTING.md)
- [Current print parts and orientations](print-manifest.json), [assembly geometry](geometry.json) and [package hashes](package-manifest.json)
- [STEP assembly](Precision_5680_D7.step)

Use the regenerated manifests for dimensions, part lists and export evidence. The [port study](../D6/PORT_STUDY.md) preserves the Precision 5680's keyboard-left Thunderbolt ports, which appear on the right in a lid-facing view. The [material and load source notes](arm-study/material-load-sources.md) explain the assumptions behind the holder study.
