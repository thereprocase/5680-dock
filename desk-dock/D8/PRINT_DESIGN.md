# D8 print design — P1S, PETG, 0.4 mm nozzle

Design each part around its print pose and load path. These are the D8 orientation decisions; the regenerated per-part print manifest must implement them and identify any remaining support. A CAD export or bed-fit check alone does not qualify deposited paths or strength.

## Process basis

Use OrcaSlicer by default, as required by the repository's [project instructions](../../AGENTS.md). Start with 0.20 mm layers, five walls and six top/bottom layers. Keep the connector support, carrier, bearing seats, cams, printed pins, printed spring and loaded fasteners dense for initial qualification. Hollow CAD passages remain hollow. Lightweight covers and grilles need their modeled skins and ribs; they do not need the same bulk infill as loaded mechanisms.

Use the current P1S profile for the actual PETG formulation, with its appropriate temperature and calibrated flow limit. Preserve bridge-specific cooling. Increasing cooling everywhere can improve shape while weakening layer bonding; turning it off everywhere makes bridge and overhang quality harder to control. These tradeoffs follow [Bambu's cooling documentation](https://wiki.bambulab.com/en/software/bambu-studio/auto-cooling) and [Prusa's PETG guidance](https://help.prusa3d.com/article/petg_2059). Prusa's numerical temperature and fan settings are not P1S settings.

Five walls and dense critical sections are a qualification starting point, not evidence of adequate strength. The process must preserve continuous deposited material through the intended load path. [Prusa's perimeter guidance](https://help.prusa3d.com/article/layers-and-perimeters_1748) supports increasing perimeters when seeking stronger parts; it does not establish a strength value for this geometry.

## Geometry rules

The following rules are conservative engineering choices for D8. They are not measured P1S limits.

- Give each part a broad, intentional first-layer datum. Put locating ribs, bosses and keys above that datum instead of starting a broad plate on a small projecting key.
- Target unsupported underside ramps at least **45 degrees above the horizontal bed plane**. Use chamfers and rising gussets underneath; retain fillets where they do not create a low-angle underside. The longest low-wing ribs have an explicit approximately 44-degree exception so their lower ends clear the removable cover by at least 0.3 mm; review that actual ramp in the slicer.
- Use bridges only where deposited strands have a landing at both ends. Favor the shorter clear span and inspect the actual bridge direction in the slicer. A feature that merely projects from one wall is an overhang, even if it resembles a roof in CAD.
- Do not assign a universal allowable bridge length. Review the longest required clear span with the selected PETG and profile. The underside of a bridge must not establish plug position, cam seating, a sliding fit or another precision datum.
- Give horizontal holes a self-supporting roof where the fit allows it. Use an accessible local support or a deliberately removable bridge layer where a true round bore or counterbore requires one. Keep removal access visible in the assembled-part design.
- Put primary bending tension and flexure length in the print bed plane where practical. A vertical rib is not automatically weak: its stress direction matters. Compression down through a foot differs from bending that peels its root across layer interfaces.
- Carry laptop gravity from its bearing pads through shell webs into dedicated shell feet. Keep the service lid out of that load path. Blend foot roots into webs and perimeter walls in the selected shell print pose.
- Retain local solid material and continuous perimeter paths at arm roots, screw seats, bearings and locating interfaces. Increasing infill does not repair an unfavorable layer direction or a poorly anchored wall.
- Add entry chamfers to sliding interfaces and relief at bed-contact fit edges. Correct fit parameters; do not scale the complete assembly to fit a pin or fan.

[Prusa's design guide](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135) supports choosing orientation for strength, splitting geometry to improve its print pose, short supported-at-both-ends bridges, underside chamfers and fit allowances. Its overhang examples and printer-specific accuracy figures are not performance claims for the P1S. [Bambu's overhang guide](https://wiki.bambulab.com/en/filament-acc/filament/print-quality/overhang) also treats cooling and material selection as part of overhang performance; geometry still determines whether each line has support.

## Chosen orientation families

The table follows the explicit part poses in [export_print.py](export_print.py). The export manifest must resolve every production part to a named face and transformation, including mirrored or repeated parts. No new part may silently inherit a generic pose from its name prefix. An optional 90-degree rotation about print Z can improve bed placement without changing the face on the bed or the layer direction.

| Part family | D8 print decision | Reason and remaining check |
|---|---|---|
| Both manifold shells | Upright assembly orientation: flat lower shell perimeter and corner feet on the bed. | A continuous lower perimeter connects the first-layer load paths while preserving the cover cable-removal notch. Vertical shell walls carry laptop gravity into the feet. Sparse underside ribs provide roof bridge landings; the projecting fan pocket still needs accessible local support. |
| Bottom service covers | Broad exterior skin on the bed; perimeter ribs and local fastening bosses upward. | Produces a continuous flat skin and upward ribs. Keep feet and laptop reactions in the shell. Do not reintroduce a nearly full-area second plate through the locating tongue. |
| Fan grille retainers | Broad grille front face on the bed; bars lie in the bed plane. | Bars begin on the plate. Shape rail engagement and returns as rising geometry; inspect any lip that begins above an opening. |
| Four fan top clips (`01/02_fan_top_clip_1/2`) | Unloaded broad fan-local YZ side on the bed; remove fan tilt and rotate about Y by -90 degrees. | Leaf length and bending stress lie in the bed plane. The exported free shape comes from the clip's manufacturing override. Review the hook and capture geometry; fan variation must not require large permanent flexure strain. |
| `connector_module_body` | Broad rear Y=50 support face on the bed; after removing laptop lean, rotate about X by -90 degrees. | Main arm/root XZ load path lies within layers; working cam grows upward. Two 45-degree internal haunches reduce the former 40 mm cavity roof span to an 8 mm bridge. The opening remains accessible at X=-40. Review that bridge, bearing and module-locating openings in the slicer. |
| `chassis_stop_bracket` | Broad rear support face on the bed; after removing laptop lean, rotate about X by -90 degrees. | Stop bending lies in the bed plane. The horizontal female thread requires a deposited-path review. |
| `breakaway_carrier` | Upright on its reinforced lower face and guide feet after removing laptop lean; no further face-changing rotation. | The docking X reaction lies in the bed plane. Vertical-web bending still depends on layer bonding and requires whole-holder qualification. This pose sharply reduces automatic support relative to laying the front return/web face down. Remaining local supports must clear the open carrier and avoid cam and bearing seats. |
| `cassette_Z_saddle` | Broad Y=17.5 outside face on the bed; after removing laptop lean, rotate about X by -90 degrees. | Saddle load path lies in XZ layers. Inspect the open gusset bridge and screw openings. The live Z slide replaces the old keyed shim pack. |
| `X_depth_overmold_clamp` | Broad cradle underside on the bed after removing laptop lean. | This cradle supplies the live Y slide; its shoulders retain X position. Its base and thrust shoulders lie along layers, with the cable cavity open upward. |
| `sliding_plug_cap` | Broad outside face on the bed; remove laptop lean and invert about X. | The broad outer face now reaches the clevis top, removing the former 2.5 mm suspended broad ledge. Gripping features grow upward; inspect the pin bore and cable-contact details. |
| `breakaway_spring_cartridge` | Export the unloaded spring; common flat outside face on the bed, rotated about X by -90 degrees. | The assembly's preloaded shape is not the manufacturing shape. Leaf length and bending stress lie in the bed plane. D8 currently retains this printed preload mechanism; the proposed steel-spring clutch is a subsequent mechanism change. |
| Two `breakaway_spring_spacer_*` parts | Flat spacer end on the bed; remove laptop lean and rotate about X by +90 degrees. | These separate clearance-bored spacers replace the integrated standoffs that obstructed the module's bed face. Compression acts along build Z through continuous perimeter walls. The original long screws engage the module's female-threaded land. |
| Loaded printed pivot and retaining pins | Shaft axis parallel to the bed. | Prioritize continuous material along the shaft. Use a designed flat/self-supporting underside only where bearing geometry permits; otherwise use removable, accessible local support and inspect the shaft surface. A purchased shoulder pivot eliminates the printed-shaft orientation compromise. |
| Printed hand screws, module locks, stop-bracket locks, cassette Y/Z locks and threaded stop | Broad head/hand face on the bed; thread axis upright. | The exporter lists each part's required transform. This leaves screw tension and head separation dependent on layer bonding; keep dense and verify the actual clamping/release load. Keys and thrust shoulders carry docking reactions where provided. |
| Printed nuts | Broad hand/seat face on the bed; thread axis upright. | Provides clean thread geometry and flat seating. Inspect thread roots and the first-layer fit edge. |
| Bridge keys | Broad plate face on the bed. | Keeps the plate load path within layers and preserves support-free locating faces. |
| Soft stop tip | Closed contact face on the bed; socket upward. | Use the actual flexible material when specified. A PETG stand-in needs a separate soft contact pad and a rechecked stop setting. |

The foot load path and module locating interface are structural decisions. A pleasing outer form does not substitute for checking the direction of stress at those roots. Likewise, a pin laid horizontally improves continuity along its length but can still fail at a notch, local bearing surface or insufficient section.

[body_print_geometry.py](body_print_geometry.py) adds 1.6 mm thick underside ribs at a nominal 10 mm pitch, leaving 8.4 mm between adjacent roof landings. Rear-wall brackets support the outlet lip; crosswise brackets grow from the end walls beneath the low wings. A full-width vertical mouth keepout removes any new rib material from the straight outlet path. These dimensions describe the current design, not a universal approved bridge span. Verify the slicer's strand direction and anchoring between each pair of ribs, especially at end bays and cut-back portions near the mouth.

The shell orientation changed after a bounded comparison of the earlier unribbed candidate. With the same generic Cura support settings, the right shell requested approximately 518 g of support on its fan rim, 509 g on its center-seam end, and 182 g upright. Those results identify the reason for the upright pose and underside ribs; they are not current D8 print totals. The final manifest and matching toolpath report govern the current geometry.

A bounded candidate comparison also blocked automatic supports only in the rib-supported roof bays and the upper hood. It reduced estimated support, but the deposited paths failed the intended bridge direction: both hood roofs contained approximately 93 mm skin roads along X where the short bridge should run 6.61 mm along Y. The [recorded path review](print-review/bridge-path-review.json) includes the source/toolpath hashes, endpoints and preceding-layer contact check. **That reduced-support scenario was rejected.** Retain the automatic-support material estimate until the actual P1S slicer deposits correctly anchored short bridges; a support blocker alone does not establish that behavior.

The current cassette has continuous Z travel from -4 to +5 mm and Y travel from -3 to +3 mm. The independent chassis stop supplies the remaining laptop-position adjustment. These are live adjustments in [cassette.py](cassette.py); they do not require a fitting jig or replacement height shim.

## Deposited-path review and evidence

For each exported part, record its face on the bed, dimensions including brim, material, local dense regions, bridge locations, support locations and access for removal. Check the first deposited layers and every change from supported material to a bridge or overhang. Inspect continuity at thin ribs, gusset roots and fastener seats. Keep supports away from connector-contact surfaces, cam seats, sliding datums and threads.

[print_check.py](print_check.py) performs a no-launch geometric preflight after the complete print manifest exists. It checks one edge-connected watertight component, winding, signed volume and manifest agreement. Its bed screen uses the 256 by 256 mm nominal bed, conservative 250 mm print height and 18 by 28 mm lower-left exclusion. It tries 8 mm and 5 mm brims, with an optional 90-degree print-Z rotation. The report distinguishes a conservative bounding footprint from the CAD mean area through the first 0.20 mm; neither establishes adhesion or deposited-path quality.

Use [OrcaSlicer's bridge controls](https://github.com/OrcaSlicer/OrcaSlicer/wiki/quality_settings_bridging) only after inspecting the geometry. Orca distinguishes bridges across open space from internal bridging over infill. Thick internal bridges, additional bridge layers and counterbore bridge options can help where appropriate; they do not remove the need for two-ended support or a sound load path. [Prusa's bridging guidance](https://help.prusa3d.com/article/poor-bridging_1802) likewise identifies span, speed and cooling as relevant to bridge quality.

The inherited [D7 preparation record](../D7/PRINT_PREPARATION.md) reports an Orca crash and no approved toolpaths. Its [CLI discovery record](../D7/print-review/cli-discovery.json) also records a failed Windows Bambu Studio help invocation. Those records do not constitute a successful slice of D8. If Orca remains unavailable in the current environment, an explained offline slicer fallback may screen deposited paths. Label such output by the actual slicer/profile used; do not present generic review G-code as a qualified P1S print file.

[slice_screen.py](slice_screen.py) uses that offline fallback and records separate deposited model, support and brim volumes. Every input retains its SHA-256 hash. Its optional `--reuse-summary` argument reuses a completed screen only when the STL hash, Cura binary, printer/extruder definitions, machine profile, every explicit slicing setting and material-density assumption match. The reused record retains its original toolpath hash and source-summary hash. A changed CAD export therefore triggers a new screen rather than inheriting an old part-name result. Keep the generic `.gcode.txt` outputs outside the repository and out of any print release.

The [current material screen](print-review/path-screen-summary.json) covers all 42 PETG parts in the regenerated 43-part manifest; the soft stop tip is excluded from PETG slicing. Eight changed parts were sliced again and 34 reused matching evidence. All 43 meshes pass the geometric preflight; all 42 screened PETG parts keep deposited paths within the recorded bed/exclusion envelope. Those passes do not certify bridge behavior, support removal or strength.

| Material allocation | Generic estimate |
|---|---:|
| Deposited PETG model | 1,255 g |
| Automatic supports | 380 g |
| Individual part brims | 25 g |
| Total deposited PETG | **1,659 g** |

The assumptions are 1.27 g/cm³ PETG, a 0.4 mm nozzle, 0.20 mm layers, five walls, six top/bottom layers, dense infill and normal automatic supports. The CAD solid volume alone corresponds to 1,243 g. Reserve roughly **1.8–2.0 kg** for an initial build with fit/strength samples and some reprints; this is a planning allowance, not a measured production requirement. Flexible pads/liners, the soft stop, purge/start waste and hardware are additional. The generic Cura time sum is about 89 hours under its conservative speed assumptions and must not be used as a P1S timing prediction.

After toolpath review, qualify the complete connector mechanism and its adjustments with a dummy plug, including sustained warm preload, reset/release and the intended loads. Check the fan and panel fits using the actual hardware. Record measured material use from the final slicer output; separate finished parts, supports, brims and qualification samples.
