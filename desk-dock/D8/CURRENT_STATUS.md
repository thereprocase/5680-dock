# D8 work checkpoint — not a print release

This branch preserves the removable live Y/Z connector module, independent X stop, dedicated shell feet, light covers, researched fan clearances and separate flat-printing fan clips.

The latest regeneration produced 83 valid CAD solids, a STEP assembly and 43 manufacturing meshes. Shells now print upright with a continuous lower perimeter and sparse roof gussets; the carrier also prints upright. The partial-thread preload screws were repaired and independently exported as watertight meshes.

## Active checks

- Final mesh preflight and changed-part offline Cura screening are running. Earlier slice/mesh reports may describe superseded poses or screw meshes; consult their input hashes.
- Earlier exact assembly checks passed all 12 sampled laptop docking poses, OEM foot keepouts and port handedness. Three shell collisions were found and corrected with local clearance pockets; the revised complete assembly is being checked.
- **Module removal is not yet clear.** The nominal receiver pockets do not provide the full advertised −Y then −X service path. This remains an active geometry fix.
- Live Y/Z travel passed nominal and four corner positions with invariant part volumes and no unintended housing collisions in a check using cylindrical thread envelopes. Exact matched thread geometry was checked separately.
- Actual P1S slicing, printed fits, complete-holder stiffness, spring creep/release force and cooling remain unqualified.

This is a deliberate development checkpoint so work is recoverable. Do not treat the presence of STEP/STL files or an earlier passing subset as production approval. D7's public viewer and download remain D7.
