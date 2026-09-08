# D8 verified-service checkpoint — not a print release

D8 includes a removable live Y/Z connector module, independent X stop, dedicated shell feet, light covers, researched fan clearances and separate flat-printing fan clips.

## Latest completed milestone

The spring cartridge is rotated 90 degrees while retaining its leaf dimensions, preload axis and cam. Both spacer/screw/thread mounts move consistently. The obsolete lower root is removed.

**The complete module now clears all 19 sampled service positions:** unload the laptop, remove two mounting locks, move local −Y by 4.3 mm, then withdraw along −X. No initial lift is required. The check found zero nominal connector collisions and 79 valid single CAD solids. See [the hashed service evidence](review-evidence/module-service-check.json).

Live Y/Z travel also passed nominal and four corner positions with invariant part volumes and no unintended housing collisions using cylindrical thread envelopes. Exact matched thread geometry was checked separately.

## Final integration in progress

- Final full regeneration from the corrected source is running. `generation-provenance.json` will record its unchanged input hashes and output hashes.
- Final full-assembly laptop/foot checks, mesh preflight, renders and changed-part slice checks will follow those exact exports. Earlier generated files and reports may describe superseded geometry; use their hashes.
- All 12 laptop docking samples, foot keepouts and port handedness passed the preceding full-assembly check.
- Generic automatic supports remain substantial under the shells. A bounded manual bridge-support scenario is being inspected; its smaller material estimate is not yet a print qualification.
- Actual P1S slicing, printed fits, complete-holder stiffness, spring creep/release force and cooling remain unqualified.

This checkpoint preserves progress while final integration finishes. D7's public viewer and archive remain D7. The presence of STEP/STL files does not establish a production release.
