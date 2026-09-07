# Design process and reproduction

Revision F is a prototype checkpoint. The work combined parametric CAD, manufacturer-image reconstruction, geometric print checks, a limited structural calculation and comparative CFD. The useful next step is physical measurement and coupon testing.

## Decisions that shaped the design

| Stage | Question | Decision and evidence |
|---|---|---|
| Layout | How can a server laptop remain easy to remove? | Hinge up, underside toward wall, tall front tines and a vertical lift-out path. Retain four room-facing wall bolts. |
| Vent identification | Where does the underside actually admit air? | Scale Dell side and inside-cover images. The covered center of the exterior grille leads to two inferred intake windows, with explicit uncertainty. |
| Plenum | How can the fans feed pressure at the intake? | Contain the rear gap with cheeks and place the contraction above the estimated intake band. Keep the laptop vertical. |
| Flow comparison | Does the smallest slot create the fastest exit? | Run eight OpenFOAM cases. Under assumed fixed supply pressure, the smaller slot retains more pressure but gives lower exit speed. Start with 12 mm. |
| Material reduction | Where can solid plastic be removed? | Use hollow box cradles, thin duct skins, framed trays and pocketed caps. Check actual net sections. Revision F uses 35.0% less CAD volume than D. |
| Manufacturing | How can the brackets print on their sides? | Orient each family around its load path and support geometry; use sloping roofs and short bridges. Audit every 0.20 mm layer. |
| Assembly | Can all hardware except wall bolts disappear? | Use keyed CA joints for fixed parts and printed split pins for removable fan caps. Keep tray joints dry. |
| Fit | What clearance should the printer reproduce? | Record coordinate, radial and diametral allowances separately. Supply coupons; no global ASA shrink correction. |

The rendered images come from actual CAD or computed fields. The laptop profile is image-derived and the fan/laptop envelopes are simplified. No physical prototype, topology optimization, generative structure solver, thermal simulation or full 3D flow solution is represented as completed work.

## Repository map

| Location | Contents |
|---|---|
| Root STEP files | Printable assembly and explicitly named reference assemblies |
| `parts/` | Fourteen individual exact solids |
| `print_ready/` | Oriented 3MF/STL parts, alternate rails and fit coupons |
| `outlet_gap_variants/` | 8 and 16 mm outlet STEP alternatives |
| `reference/` | Attributed reference images and measurement evidence |
| `cfd/` | Case dictionaries, parameters, result summary and per-case raw-evidence ZIPs |
| Root Python files | CAD generation, analysis, validation, rendering and packaging |
| Root JSON files | Machine-readable geometry, fit, print and structural results |

Older design volumes are retained in `material_comparison.json` and `reference/Revision_D_Geometry.json`. This repository begins at Revision F; it does not fabricate earlier git commits or include nested historical project archives.

## Python setup and CAD regeneration

Use Python 3.12 on a platform supported by CadQuery 2.8.0. The recorded dependency versions are in `requirements.txt`; dependencies with lower bounds may resolve differently on a future installation.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python build_mount.py
python reconstruct_profile.py
python section_properties.py
python strength_check.py
python prepare_prints.py
python audit_layers.py
python validate_assembly.py
python render_preview.py
python render_fdm_guide.py
python vent_layout.py
```

Run these commands from the repository root. Regeneration overwrites the associated exported files. CAD uses millimeters. `base_geometry.py` retains supporting primitives and baseline construction functions; `build_mount.py` defines the current Revision F assembly. Edit the current construction and its referenced primitives rather than obsolete baseline assembly functions.

The reference images are already included. [SOURCES.md](SOURCES.md) records their origins. Pillow and the CAD renderer need available fonts; font substitution can alter the layout of regenerated figures without changing CAD.

## CFD reproduction

The recorded run uses OpenFOAM v1912, Ubuntu package `1912.200626-2build3`. Install a compatible runtime and source its normal OpenFOAM shell environment. The scripts fall back to the inherited environment when the original optional local runtime tree is absent. Newer OpenFOAM versions may require dictionary changes.

To inspect or reanalyze the recorded study, first unpack its per-case evidence:

```bash
python unpack_cfd_evidence.py
python analyze_cfd.py
python render_cfd.py
```

To perform new runs, use a separate checkout or copy of the case evidence so the original results remain available:

```bash
python run_cfd_sweep.py
python analyze_cfd.py
for case in cfd/*/; do
  if [ -f "$case/system/controlDict" ]; then
    foamToVTK -case "$case" -latestTime -ascii
  fi
done
python render_cfd.py
```

Each run executes `blockMesh`, `checkMesh` and `simpleFoam -noFunctionObjects`. The flag avoids an old binary's function-object compatibility failure; it does not replace the solver or suppress field output. Postprocessing reads the written fields. [foam_environment.md](foam_environment.md) and [CFD_Design_Report.md](CFD_Design_Report.md) give the environment, boundary conditions and numerical limits.

Per-case ZIPs retain the existing mesh, saved states, logs and VTK files. The finest-mesh archive is split into numbered 4 MiB pieces for transfer; the unpack script joins them automatically. The plain case dictionaries and `results.json` are also directly browsable. ZIP compression keeps the repository practical without discarding numerical evidence. The original saved states are not a promise that every case met its residual target.

## Package and check

```bash
python create_package.py
```

This generates a portable ZIP and a SHA-256 manifest from the public project files. It excludes local environments, git metadata and generated archives. Original validation results accompany the package. The scripts and stored results do not replace physical print, bond, retention, thermal or wall-anchor tests.

Before printing, follow [P1S_ASA_Print_Guide.md](P1S_ASA_Print_Guide.md). Before adjusting a fit, read [TOLERANCES.md](TOLERANCES.md). The ordered prototype evaluation appears in [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md).
