"""File the frozen fit kit and an explicitly diagnostic research handoff."""
from pathlib import Path
import hashlib, json, shutil, zipfile

ROOT=Path(__file__).resolve().parents[3]
TEAM=ROOT/'outputs/5680-design-team'
REPO=ROOT/'work/5680-site-handoff'
DOCS=REPO/'docs'
OUT=TEAM/'CLOSEOUT-20260917'
EVIDENCE=DOCS/'handoff/2026-09-17'
KIT=TEAM/'PRINT-ME-V4-FULL-RAIL-COUPONS'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(source,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,dest)
    assert sha(source)==sha(dest)

def tree(source,dest):
    for p in sorted(source.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.log'):
            copy(p,dest/p.relative_to(source))

manifest=json.loads((KIT/'manifest.json').read_text())
for name,record in manifest['files'].items():
    assert sha(KIT/name)==record['sha256'],name
zip_source=TEAM/(KIT.name+'.zip')
assert sha(zip_source)=='5d98ca89825dc0012866ddff6cc93e13835a561b51cc547a12badd7109ee9cf2'
with zipfile.ZipFile(zip_source) as z:
    assert z.testzip() is None
    entries=[i for i in z.infolist() if not i.is_dir()]
    for i in entries:
        relative=Path(i.filename)
        if relative.parts[0]==KIT.name:relative=Path(*relative.parts[1:])
        assert (KIT/relative).is_file(),str(relative)
        assert hashlib.sha256(z.read(i)).hexdigest()==sha(KIT/relative)
    assert len(entries)==len([p for p in KIT.rglob('*') if p.is_file()])==len(manifest['files'])+1==44

OUT.mkdir(parents=True,exist_ok=True)
EVIDENCE.mkdir(parents=True,exist_ok=True)
copy(zip_source,DOCS/'downloads/Precision_5680_V4_Full_Rail_Fit_Kit.zip')
copy(KIT/'OPEN-ME.3mf',DOCS/'downloads/Precision_5680_V4_Full_Rail_Fit_Coupons.3mf')
for name in ('README.md','manifest.json'):
    copy(KIT/name,EVIDENCE/'fit'/name)
copy(KIT/'verification/verification-coordinate-correction.md',EVIDENCE/'fit/verification-coordinate-correction.md')
for name in ('ABC_full_native_rail_comparison.png','actual-toolpaths.png','id-holes-toolpaths.png'):
    copy(KIT/'previews'/name,EVIDENCE/'fit'/name)
for name in ('toolpath-verification.json','independent-geometry-verification.json'):
    copy(ROOT/'work/quartet-team/architect/v4-orca'/name,EVIDENCE/'fit'/name)
for name in ('V3-ID-HOLE-FRAME-CORRECTION.md','V3-ID-HOLE-FRAME-CORRECTION.json','FAN-DUCT-SCREEN-R2-VERIFICATION.md','D9-PRESSURE-CONVENTION-REVIEW.md'):
    copy(TEAM/'verification'/name,EVIDENCE/'verification'/name)
copy(TEAM/'physical-fit-evidence/CURRENT-INTERPRETATION.md',EVIDENCE/'fit/CURRENT-INTERPRETATION.md')

for name in ('fan-duct-screen-r2-noctua-corrected','d9-mouth-pressure-area-budget','r3-ideal-cap-bound'):
    tree(TEAM/'cfd'/name,EVIDENCE/'flow'/name)
for name in ('D9-MOUTH-PRESSURE-AREA-BUDGET.md','D9-PRESCRIBED-FLOW-RESISTANCE-PLAN.md','D9-INTAKE-TOPOLOGY.md','D9-INTAKE-TOPOLOGY-MAP.json','CFD-WRAP-HANDOFF.md','d9-fanpressure-algebraic-check.json'):
    copy(TEAM/'cfd'/name,EVIDENCE/'flow'/name)
for p in (ROOT/'work/quartet-team/cfd').glob('*'):
    if p.is_file() and p.suffix in ('.py','.json'):copy(p,EVIDENCE/'flow/source'/p.name)

for name in ('D9-ACOUSTIC-ARCHITECTURE-NOTES.md','D9-JOINT-SCHEME-VIBRATION-REVIEW.md','D9-FAN-PLATE-MOUNT-REQUIREMENTS.md','FLOW-VS-STRUCTURE-BENCH-CHECK.md','ACOUSTIC-RISK-PLAN.md','GEOMETRY-RISK-COMPARISON.md','geometry-comparison.svg'):
    copy(TEAM/'acoustics'/name,EVIDENCE/'acoustics'/name)
for name in ('D9-FAN-POD-JOINT-SCHEME.md','D9-SIDE-FRAME-PROPOSAL.md','D9-PRINTABILITY-AUDIT.md'):
    copy(TEAM/'geometry-review'/name,EVIDENCE/'design-proposals'/name)
tree(ROOT/'work/quartet-team/geometry/d9-fan-pod',EVIDENCE/'d9-diagnostic/geometry')
tree(ROOT/'work/quartet-team/architect/closed-v3-review',EVIDENCE/'d9-diagnostic/independent-review')
tree(ROOT/'work/quartet-team/architect/enclosure-auditor-fixtures-v2',EVIDENCE/'d9-diagnostic/auditor-fixtures')
for name in ('audit_closed_intake.py','audit_print_mesh_support.py','check_enclosure_auditor.py','localize_d9_v3_defects.py','review_closed_v3_exports.py'):
    copy(ROOT/'work/quartet-team/architect'/name,EVIDENCE/'d9-diagnostic/review-source'/name)

readme='''# 17 September 2026 handoff: read this first

The separately linked V4 full-height A/B/C kit is ready for a supported,
handheld physical contact test. Its toolpaths were verified; fit has not been
tested. D8 remains the last complete CAD reference, with the reported seating
problem unresolved. There is no qualified D9 dock or demonstrated cooling or
acoustic improvement.

## Evidence boundaries

- fit/: current interpretation, frozen kit manifest, CAD and actual toolpath
  previews, geometry/toolpath receipts. The full kit has 43 hashed payload
  files plus its manifest (44 ZIP entries), and has its own ZIP.
- verification/: the V3 identifier failure was a coordinate-checker error and
  was withdrawn. Corrected raw-motion-to-plate offset is (0,+2) mm. The larger
  V4 identifiers were retained; no physical nozzle calibration is claimed.
- flow/: corrected fixed-800-RPM parameter screen and source-mouth budgets.
  These use assumed loss coefficients; they are not installed CFD results.
  The selected 10-CFM component CFD plan was never run. Prior workspace CFD
  experiments outside this D9 effort are not a D9 result or part of this kit.
- d9-diagnostic/: development snapshots, not printable releases. Original
  closed-v3/generated failed independent enclosure and tray/lid print-normal
  checks. generated-r1 also failed print-normal review. closed-v4 contains a
  construction plan only. The latest V3 builder is a later source revision and
  DOES NOT reproduce the frozen original generated manifest; this mismatch is
  preserved explicitly. The independent review hashes identify the exact
  failed output bytes. No repair is implied by a watertight individual STL.
- design-proposals/ and acoustics/: proposals, geometric reasoning, and test
  plans only. Docking forces are design targets, not measured loads. Original
  R3 top_cut/face_cut crest continuity remains an open geometry lead if reused.

The original four V1 photos remain in the local physical-fit-evidence folder;
they were not republished. Their interpretation is included. Neither the
photos nor agreement with the simplified CAD establishes a measured lid
thickness, pivot, seal, vent area, or flow direction. A blanket 4-mm correction
is not supported.

Start with NEXT-STEPS.md or the site's September handoff page. SHA256SUMS.json
covers every filed evidence file. Relative paths inside historical receipts
refer to their original workspace; use this folder's index for navigation.
'''
(EVIDENCE/'README.md').write_text(readme,encoding='utf-8')
copy(EVIDENCE/'README.md',OUT/'README.md')
print(json.dumps({'fit_kit_sha256':sha(zip_source),'fit_kit_files':len(entries),'evidence_files_so_far':sum(p.is_file() for p in EVIDENCE.rglob('*')),'evidence':str(EVIDENCE)},indent=2))
