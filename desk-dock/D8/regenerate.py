"""Build D8 once, export STEP/print poses and cache exact shapes for review.

No slicer or printer is launched. The optional cache is an intermediate, not
part of the delivered CAD package. Run from any directory with CadQuery 2.7.
"""
import argparse,json,hashlib,datetime
import cadquery as cq
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('--cache',type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parent
input_names=['regenerate.py','build.py','body_service.py','body_print_geometry.py',
 'fan_service.py','fan_retention.py','cable_service.py','cassette.py',
 'connector_mount.py','connector_clearance.py','breakaway_geometry.py',
 'printed_fasteners.py','export_print.py','parameters.json',
 'contact-profiles.json','port-study.json']
def hashes():
    return {name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in input_names}
source_hashes=hashes()
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
import build
from export_print import export_all
if args.cache:
    args.cache.mkdir(parents=True,exist_ok=True)
    meta=[]
    for part in build.parts:
        name=part['name']
        part['shape'].exportBrep(str(args.cache/(name+'.brep')))
        meta.append({k:part[k] for k in ('name','color','reference')})
    (args.cache/'parts.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('Exact review cache saved',flush=True)
records=export_all(build)
assert source_hashes==hashes(),'Generation inputs changed while building; regenerate before publishing'
outputs=['Precision_5680_D8.step','geometry.json','flow-geometry.json',
         'assembly-details.json','print-manifest.json']
outputs.extend('print/'+row['file'] for row in records)
provenance=dict(revision='D8',started_utc=started,
    completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    cadquery_version=cq.__version__,source_sha256=source_hashes,
    output_sha256={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in outputs},
    scope='One successful generation with unchanged source inputs; not physical qualification.')
(root/'generation-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
print('Regeneration complete',flush=True)
