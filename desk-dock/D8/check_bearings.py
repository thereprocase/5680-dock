"""Verify direct shell contacts, bare-foot clearance, and render the bearings."""
from pathlib import Path
import argparse,json,math,hashlib
import cadquery as cq
from raster import render,font
from PIL import Image,ImageDraw
parser=argparse.ArgumentParser();parser.add_argument('cache',type=Path);args=parser.parse_args()
ROOT=Path(__file__).resolve().parent
p=json.loads((ROOT/'parameters.json').read_text())
H=p['rear_case_seat_z'];lean=p['laptop_lean_deg']
def leaned(s):return s.rotate((0,0,H),(1,0,H),-lean)
def box(x,y,z,a,b,c):return cq.Workplane('XY').box(a,b,c,centered=False).translate((x,y,z)).val()
metadata=json.loads((args.cache/'parts.json').read_text())
parts={a['name']:cq.Shape.importBrep(str(args.cache/(a['name']+'.brep'))) for a in metadata}
layout=json.loads((ROOT/'hinge-bearing-layout.json').read_text())
laptop=parts['Precision_5680_REFERENCE'];rows=[]
for row in layout:
    shell=parts[f"{row['module']:02}_manifold_with_cradle"]
    x=row['x_mm'];top=row['contact_top_local_z_mm']
    width=row['bridge_width_mm']-2*row['sliding_chamfer_mm']
    y0,y1=p['hinge_bearings']['contact_y_bounds_mm']
    region=leaned(box(x-width/2+.1,y0+.1,top-.02,width-.2,y1-y0-.2,.03))
    surface=shell.intersect(region)
    delta=(0,.02*math.sin(math.radians(lean)),.02*math.cos(math.radians(lean)))
    row=dict(row,contact_material_mm3=surface.Volume(),seated_laptop_overlap_mm3=surface.intersect(laptop).Volume(),upward_contact_probe_mm3=surface.translate(delta).intersect(laptop).Volume(),shell_valid=shell.isValid(),shell_solids=len(shell.Solids()))
    row['passed']=row['contact_material_mm3']>.1 and row['seated_laptop_overlap_mm3']<.001 and row['upward_contact_probe_mm3']>.1 and row['shell_valid'] and row['shell_solids']==1
    rows.append(row)
extra=[]
for i,fx in enumerate(p['fan_centers_x'],1):
    shell=parts[f'{i:02}_manifold_with_cradle']
    region=leaned(box(fx-42,p['laptop_thickness']/2-.01,H+21,84,.03,50))
    surface=shell.intersect(region)
    delta=(0,-.02*math.cos(math.radians(lean)),.02*math.sin(math.radians(lean)))
    overlap=surface.intersect(laptop).Volume();contact=surface.translate(delta).intersect(laptop).Volume()
    zmin=shell.BoundingBox().zmin
    locks=[parts[f'{i:02}_bottom_thumb_lock_{j}'] for j in (1,2)]
    clearance=min(s.BoundingBox().zmin for s in locks)-zmin
    extra.append(dict(module=i,lid_overlap_mm3=overlap,lid_contact_probe_mm3=contact,bare_foot_z_mm=zmin,bottom_lock_desk_clearance_mm=clearance,passed=overlap<.001 and contact>1 and abs(zmin+5)<1e-5 and clearance>=1.49))
removed=[n for n in parts if any(k in n for k in ['corner_pad_','liner_','hinge_seal_'])]
report=dict(passed=all(r['passed'] for r in rows+extra) and not removed,bearings=rows,lid_and_bare_feet=extra,unexpected_liners_or_seals=removed,optional_desk_pad_count=sum('_desk_pad_' in n for n in parts),scope='Exact direct-contact and bare-foot clearance checks; physical fit, grip and cooling not measured.',input_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['check_bearings.py','parameters.json','hinge-bearing-layout.json']})
(ROOT/'bearing-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
assert report['passed'],'Direct contact or bare-foot check failed'
objects=[(s,(143,156,163)) for n,s in parts.items() if n.endswith('manifold_with_cradle')]
im,_=render(objects,(1600,850),(.12,-1,1.9),pad=65)
canvas=Image.new('RGB',(1600,990),(248,248,248));canvas.paste(im,(0,95))
d=ImageDraw.Draw(canvas);d.text((40,24),'D8 | Direct printed hinge bearings',font=font(32,True),fill=(32,49,60))
d.text((40,68),'Six quarter-interval bridges | 1 mm sliding chamfers | No liners or hinge seals',font=font(22),fill=(55,66,74))
d.text((40,950),'Exact revised CAD | Printed feet work bare; desk grip pads are optional',font=font(20),fill=(55,66,74))
canvas.save(ROOT/'D8-hinge-bearings.png')
