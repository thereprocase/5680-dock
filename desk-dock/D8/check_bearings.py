from pathlib import Path
import sys,json,argparse
import cadquery as cq
import numpy as np
parser=argparse.ArgumentParser();parser.add_argument('cache',type=Path);args=parser.parse_args()
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from raster import render,font
from PIL import Image,ImageDraw
p=json.loads((ROOT/'parameters.json').read_text())
H=p['rear_case_seat_z'];lean=p['laptop_lean_deg']
def leaned(s):return s.rotate((0,0,H),(1,0,H),-lean)
def box(x,y,z,a,b,c):return cq.Workplane('XY').box(a,b,c,centered=False).translate((x,y,z))
cache=args.cache
parts={a['name']:cq.Shape.importBrep(str(cache/(a['name']+'.brep'))) for a in json.loads((cache/'parts.json').read_text())}
layout=json.loads((ROOT/'hinge-bearing-layout.json').read_text())
laptop=parts['Precision_5680_REFERENCE']
rows=[]
for row in layout:
    i=row['module'];j=p['hinge_bearings']['fractions'].index(row['fraction'])+1
    pad=parts[f'hinge_bearing_liner_{i}_{j}']
    shell=parts[f'{i:02}_manifold_with_cradle']
    # Local upward/downward probes demonstrate seated contact on both faces.
    v=leaned(cq.Vertex.makeVertex(0,0,H+.01)).Center()-cq.Vector(0,0,H)
    row=dict(row, pad_laptop_overlap_mm3=pad.intersect(laptop).Volume(),
             contact_probe_laptop_mm3=pad.translate(v).intersect(laptop).Volume(),
             contact_probe_shell_mm3=pad.translate(-v).intersect(shell).Volume(),
             shell_valid=shell.isValid(),shell_solids=len(shell.Solids()))
    row['passed']=row['pad_laptop_overlap_mm3']<.001 and row['contact_probe_laptop_mm3']>.1 and row['contact_probe_shell_mm3']>.1 and row['shell_valid'] and row['shell_solids']==1
    rows.append(row)
seal_hits=[]
for name,s in parts.items():
    if name.startswith('hinge_seal_'):
        for i in (1,2):
            vol=s.intersect(parts[f'{i:02}_manifold_with_cradle']).Volume()
            if vol>.01:seal_hits.append(dict(seal=name,shell=i,volume_mm3=vol))
out=ROOT;out.mkdir(parents=True,exist_ok=True)
report=dict(passed=all(r['passed'] for r in rows) and not seal_hits,bearings=rows,seal_intersections=seal_hits,scope='Exact nominal contact checks; physical fit and strength not measured.')
(out/'bearing-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
assert report['passed'], 'Bearing contact or seal clearance failed'
objects=[]
for name,s in parts.items():
    if name.endswith('manifold_with_cradle'):objects.append((s,(143,156,163)))
    elif name.startswith(('hinge_bearing_liner_','corner_pad_')):objects.append((s,(242,165,46)))
im,_=render(objects,(1600,850),(.12,-1,1.9),pad=65)
canvas=Image.new('RGB',(1600,990),(248,248,248));canvas.paste(im,(0,95))
d=ImageDraw.Draw(canvas);d.text((40,24),'D8 | Intermediate hinge-edge bearings',font=font(32,True),fill=(32,49,60))
d.text((40,68),'Six quarter-interval bridges | 1 mm sliding chamfers | Beveled contact pads in amber',font=font(22),fill=(55,66,74))
d.text((40,950),'Exact revised CAD | Laptop omitted to expose supports | Fit and toolpaths require review',font=font(20),fill=(55,66,74))
canvas.save(out/'D8-hinge-bearings.png')
