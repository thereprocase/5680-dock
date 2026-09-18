from pathlib import Path
import sys
import json
import cadquery as cq
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parent
d8=r.parents[1]
sys.path.insert(0,str(d8))
from raster import render,font
new=cq.importers.importStep(str(r/'D8-R3-quick-fit-bracket.step')).val()
old=cq.importers.importStep(str(r.parent/'R2/D8-R2-quick-fit-bracket.step')).val()
def crop(s):
    window=cq.Workplane('XY').box(42,40,30,centered=False).translate((-2,-22,45)).val()
    return s.intersect(window)
canvas=Image.new('RGB',(1600,1140),'#f8f8f8');draw=ImageDraw.Draw(canvas)
draw.text((35,24),'D8 R3 | Swept air relief in the short lip',font=font(32,True),fill='#20313c')
draw.text((35,79),'Three rounded scallops open through the lip; shallow channels flare into their mouths.',font=font(22),fill='#354a55')
for x,label,shape in [(20,'R2 / SMOOTH LIP',old),(820,'R3 / AIR-RELIEF LIP',new)]:
    draw.text((x+15,145),label,font=font(25,True),fill='#20313c')
    im,_=render([(crop(shape),(62,117,139))],(760,610),(.7,-1,.65),pad=35)
    canvas.paste(im,(x,195))
    draw.line([(x+15,810),(x+740,810)],fill='#b7c7ce',width=2)
lip=cq.Shape.importBrep(str(r/'lip-local.brep'))
p=json.loads((d8/'parameters.json').read_text())
h=p['rear_case_seat_z']
printed=new.rotate((0,0,0),(0,1,0),-90)
bb=printed.BoundingBox()
print_lip=lip.rotate((0,0,h),(1,0,h),-p['laptop_lean_deg']).rotate((0,0,0),(0,1,0),-90).translate((-bb.xmin,-bb.ymin,-bb.zmin))
lb=print_lip.BoundingBox()
(r/'lip-print-bounds.json').write_text(json.dumps([lb.xmin,lb.ymin,lb.zmin,lb.xmax,lb.ymax,lb.zmax])+'\n')
im,_=render([(lip,(62,117,139))],(750,255),(.35,1,.25),pad=20)
canvas.paste(im,(20,825))
draw.text((825,855),'Inner face: grooves fade in over 12 mm',font=font(24),fill='#20313c')
draw.text((825,898),'0.8 mm relief / 12.7 mm channel pitch',font=font(24),fill='#20313c')
draw.text((825,941),'Open tops / gentle printable slopes',font=font(24),fill='#20313c')
draw.text((35,1090),'CAD geometry shown. Chevron-inspired shape; airflow and noise benefit still require a physical comparison.',font=font(21),fill='#5b6570')
canvas.save(r/'D8-R3-air-relief.png')
