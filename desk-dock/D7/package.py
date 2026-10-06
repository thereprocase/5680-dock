"""Package verified CAD, individual meshes, evidence, and local viewer assets."""
from pathlib import Path
import hashlib, importlib.metadata, json, sys, zipfile
R=Path(__file__).resolve().parent
ROOT=R.parents[1]
v=json.loads((R/'validation.json').read_text())
geometry=json.loads((R/'geometry.json').read_text())
assert v['step_all_valid'] and v['step_solids']==len(geometry['parts']) and not v['nominal_rigid_collisions']
assert json.loads((R/'service-validation.json').read_text())['passed']
pre=json.loads((R/'print-review/mesh-preflight-summary.json').read_text())
print_files={row['file'] for row in json.loads((R/'print-manifest.json').read_text())['parts']}
print_files|={row['file'] for row in json.loads((R/'print/coupon-manifest.json').read_text())['parts']}
assert {Path(row['source']).name for row in pre}==print_files
for row in pre:
    assert row['watertight'] and row['bed_and_exclusion_pass']
    p=R/'print'/Path(row['source']).name
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['source_sha256']
assert all((R/n).exists() for n in ['D7-assembled.png','D7-fan-pockets.png','alignment-validation.json','airflow-sizing.json'])
(R/'runtime-versions.json').write_text(json.dumps(dict(python=sys.version,packages={n:importlib.metadata.version(n) for n in ['cadquery','numpy','trimesh','Pillow']}),indent=2)+'\n')
files=[p for p in R.iterdir() if p.is_file() and p.suffix in ['.py','.json','.md','.step','.png'] and p.name!='package-manifest.json']
files+=[R/'print'/name for name in sorted(print_files)]+[R/'print/coupon-manifest.json']
for directory in ['arm-study','printed-fastener-review','cassette-review']:
    files += [p for p in (R/directory).glob('*') if p.suffix in ['.py','.md','.json','.png']]
files+=[p for p in (R/'print-review').rglob('*.json') if 'profiles' not in p.parts]
for n in ['desk-dock.html','desk-dock-d7.html','desk-dock-viewer-d7.js','desk-dock.css','desk-dock-software.js']:
    files.append(ROOT/'docs'/n)
files+=list((ROOT/'docs/vendor').glob('*.js'))
files+=list((ROOT/'docs/models/desk-dock-d7').glob('*'))
files+=[ROOT/'Open-Desk-Dock.ps1']
files+=[R.parent/'D6'/n for n in ['PORT_STUDY.md','AIRFLOW_STUDY.md','port-study.json','airflow-sizing.json']]
files=sorted(set(files))
manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(R/'package-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
archive=R/'Precision_5680_D7_Review.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files+[R/'package-manifest.json']:z.write(p,p.relative_to(ROOT))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in manifest.items())
print(json.dumps(dict(archive=str(archive),bytes=archive.stat().st_size,files=len(files)+1,verified=True)),flush=True)
