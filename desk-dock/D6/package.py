"""Create and verify a portable CAD/source review archive from final outputs."""
from pathlib import Path
import json,hashlib,zipfile,sys,importlib.metadata
R=Path(__file__).resolve().parent
required=['Precision_5680_D6.step','overview.png','docking-cycle.gif','contact-study.png','validation.json','alignment-validation.json','airflow-sizing.json','README.md','PORT_STUDY.md','AIRFLOW_STUDY.md']
assert all((R/n).is_file() for n in required)
v=json.loads((R/'validation.json').read_text())
assert v['step_all_valid'] and v['step_solids']==56
assert not v['nominal_rigid_collisions']
assert all(not x['collisions'] and not x['expanded_foot_keepout_collisions'] for x in v['docking_path_samples'])
runtime=dict(python=sys.version,packages={x:importlib.metadata.version(x) for x in ['cadquery','numpy','trimesh','Pillow','matplotlib']})
(R/'runtime-versions.json').write_text(json.dumps(runtime,indent=2)+'\n')
files=sorted(p for p in R.iterdir() if p.is_file() and p.suffix in ['.py','.json','.md','.png','.gif','.step'] and p.name!='package-manifest.json')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(R/'package-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
archive=R/'Precision_5680_D6_Review.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files+[R/'package-manifest.json']:z.write(p,p.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in manifest.items())
print('Verified archive:',archive,'bytes:',archive.stat().st_size,flush=True)
