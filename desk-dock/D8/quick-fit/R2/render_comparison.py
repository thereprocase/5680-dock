from pathlib import Path
import sys, json, math
import cadquery as cq
from PIL import Image, ImageDraw
root = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root))
from raster import render,font
r=root/'quick-fit/R2'
old=cq.importers.importStep(str(root/'quick-fit/D8-quick-fit-bracket.step')).val()
new=cq.importers.importStep(str(r/'D8-R2-quick-fit-bracket.step')).val()
added=new.cut(old)
canvas=Image.new('RGB',(1500,1020),'#f8f8f8')
d=ImageDraw.Draw(canvas)
d.text((35,22),'D8 fit trial R2 | Underside lip and heel seat',font=font(32,True),fill='#20313c')
d.text((35,77),'Same seat height, 5-degree lean and bracket spacing. Orange = added material.',font=font(21),fill='#354a55')
bounds=[(0,y,z) for y in [-19,18] for z in [45,74]]
for x,title,objects in [(20,'PRINTED TEST / R1',[(old,(62,117,139))]),
                         (770,'NEXT FIT TRIAL / R2',[(new,(62,117,139)),(added,(224,132,50))])]:
    d.text((x+15,140),title,font=font(24,True),fill='#20313c')
    im,_=render(objects,(710,580),(1,0,0),pad=30,bounds=bounds)
    canvas.paste(im,(x,185))
    d.line([(x+15,765),(x+690,765)],fill='#b7c7ce',width=2)
d.text((35,790),'0.25 mm nominal gap to underside',font=font(23),fill='#20313c')
d.text((35,831),'Lip top: 12 mm above seat datum',font=font(23),fill='#20313c')
d.text((35,872),'Curved seat width: 9 mm',font=font(23),fill='#20313c')
d.text((785,790),'2.25 mm gap  /  lip moved outward 2 mm',font=font(23,True),fill='#20313c')
d.text((785,831),'Lip raised 3 mm  /  upper edges R0.65',font=font(23),fill='#20313c')
d.text((785,872),'1 mm more seat wrap  /  rim +1.19 mm',font=font(23),fill='#20313c')
d.text((35,957),'Nominal CAD fit checked. Trial dimensions; vent noise and physical R2 fit remain untested.',font=font(21),fill='#5b6570')
canvas.save(r/'D8-R2-comparison.png')

