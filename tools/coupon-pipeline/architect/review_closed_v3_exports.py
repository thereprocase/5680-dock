"""Verify frozen D9 V3 hashes, nominal two-port enclosure, and print normals."""
import hashlib, json, subprocess, sys
from pathlib import Path
import cadquery as cq

here=Path(__file__).resolve().parent
source=here.parent/'geometry/d9-fan-pod/closed-v3/generated'
dest=here/'closed-v3-review'
manifest_path=source/'manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name,expected in manifest['output_sha256'].items():
 assert sha(source/name)==expected, name
before={p.name:sha(p) for p in source.iterdir() if p.is_file()}
dest.mkdir(exist_ok=True)
caps=[cq.importers.importStep(str(source/f'D9_closed_v3_TEMPORARY_{port}_port_cap.step')).val() for port in ('mouth','fan')]
cap_file=dest/'TEMPORARY_combined_port_caps.step'
cq.exporters.export(cq.Compound.makeCompound(caps),str(cap_file))
commands=[
 [sys.executable,str(here/'audit_closed_intake.py'),'--assembly',str(source/'D9_closed_v3_physical_assembly.step'),'--void',str(source/'D9_closed_v3_intended_air_volume.step'),'--caps',str(cap_file),'--out',str(dest/'nominal-enclosure.json')],
 [sys.executable,str(here/'audit_print_mesh_support.py'),*sum((['--stl',str(source/f'D9_closed_v3_{part}_print_pose.stl')] for part in ('intake_tray','solid_lid','fan_plate')),[]),'--out',str(dest/'print-pose-normals.json')]
]
results=[]
for command in commands:
 result=subprocess.run(command,capture_output=True,text=True)
 results.append({'tool':Path(command[1]).name,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
after={p.name:sha(p) for p in source.iterdir() if p.is_file()}
assert before==after,'Source exports changed during review; results are not a frozen-candidate receipt'
receipt={'manifest_sha256':sha(manifest_path),'source_sha256':before,'source_stable':True,'checks':results,
 'scope':'Nominal enclosure and nominated print-pose geometry; no slicer, physical fit, leakage, performance or structural qualification.'}
(dest/'review-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2))
if any(x['returncode'] for x in results):raise SystemExit(1)
