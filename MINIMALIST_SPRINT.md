# Minimalist release development

## Scope and current boundary

Revision H is the ducted prototype. Its exact native model and prototype print
files remain available. Subsequent ducted releases may redesign the arms too;
the prototype's print freeze is not a permanent product constraint.

The minimalist fork is a complete independent set with no frozen parts. Its
purpose is to hold a laptop on a wall and point fans up its back while reducing
plastic and print time. Most enclosed ducting is removed. Structural webs,
fastener lands and working airflow surfaces retain the material they need.

Deliver an editable native FreeCAD model descended through Save As from the
Revision H model, with constrained sketches, stock features, an organized
parameter sheet, and reproducible builders. Keep construction visible in the
FreeCAD GUI and read its error log. Maintain 0.30 mm nominal clearance at new
printed mating surfaces, documenting intentional retention interference.

The target printer is a P1S with a 0.4 mm nozzle and ASA. OrcaSlicer is the
default for preparation and review. STEP/STL/3MF outputs carry their actual
print orientations; CAD acceptance and sliced paths do not prove physical fit
or warm-load durability.

## Implementation sequence

1. Preserve the Rev H prototype and supply print-oriented STEP files.
2. Create `codex/minimalist-release` in its own worktree and Save As the FCStd.
3. Build perforated structural arms, open fan cradles and removable retainers.
4. Add a positive ladder adjustment: two rungs engaged by a removable key,
   retained by a printed pin. The optional dam moves in discrete vertical steps.
5. Parameterize actual laptop width, base-to-hinge depth, closed thickness,
   rear wall gap, and fan dimensions. Screen-size labels are convenience presets,
   not a fit guarantee. Include 13, 14, 15.6, 16 and 17 inch classes.
6. Validate nominal and changed configurations, assembly and service clearances,
   load-path estimates, native reopen, meshes, and P1S-oriented slices. Compare
   material and print time with the ducted prototype using stated settings.
7. Publish the model, print files, measured comparison and interactive Pages
   presentation. Complete the Rev H gallery's missing corrected-geometry views.

## CFD coordination

The CFD collaborator owns `fusion/cfd/` additions and a self-contained
`docs/simulation/revh-transient/` package in `codex/cfd-revh-transient`.
The main Pages layout and minimalist model are owned here. Integrate the CFD
package when the collaborator provides actual results and provenance. The
836,278-cell Revision F exploration must never be relabeled as Revision H or
minimalist CFD. There are no new CFD results at this sprint's start.

## Checkpoints

- 2026-09-08: recovered the complete interrupted conversation and scope.
- 2026-09-08: all 14 Rev H STEP exports reimported as valid solids, matched
  released STL bounds, and delivered in print orientation for the prototype.
- 2026-09-08: independent minimalist branch/worktree created from `f47a03f`.

- 2026-09-08: native M1 complete: 20 installed parts, 51 constrained sketches,
  six dimensioned presets and all nine indexed dam positions checked.
- 2026-09-08: every preset saved/reopened, with valid STEP roundtrips, closed
  print meshes and P1S bed/brim/cutter clearance. Native clean reconstruction
  from the preserved H source also passes the nominal independent validator.
- 2026-09-08: full nominal Orca estimate 388.05 g / 15 h 24 m 54 s, compared
  with 1183.88 g / 34 h 00 m 15 s for the complete H layout. The expanded
  path review includes Overhang wall and all other extrusion features; bridge
  labels alone omitted 8.99 mm fan-hanger and 6.12 mm dam-slot spans.
- 2026-09-08: eight native-derived fit samples include both attachment build
  directions. Physical fit, retention, creep, anchors and cooling remain open.
- 2026-09-08: interactive site passed six-preset, dam-index, exploded-view,
  Rev F/H comparison, CFD gallery and mobile-layout checks. Archive publication
  and final download verification follow the completed all-feature path audit.
