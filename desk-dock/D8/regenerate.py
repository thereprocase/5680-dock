"""Build D8 once, export STEP/print poses and cache exact shapes for review.

No slicer or printer is launched. The optional cache is an intermediate, not
part of the delivered CAD package. Run from any directory with CadQuery 2.7.
"""
import argparse,json
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('--cache',type=Path)
args=parser.parse_args()
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
print('Regeneration complete',flush=True)
