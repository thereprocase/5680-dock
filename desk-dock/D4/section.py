"""Exact orthographic CAD section through one fan, with intended-flow annotations."""
import json,math
from pathlib import Path
from PIL import Image,ImageDraw
import build
from raster import render,font,arrow
R=Path(__file__).resolve().parent
fx=build.W-build.p['fan_centers_x'][0]
slab=build.box(fx-.3,-45,-1,.6,220,190).val()
objects=[]
for a in build.parts:
 if any(k in a['name'] for k in ['blade']):continue
 bb=a['shape'].BoundingBox()
 if bb.xmin>fx+.3 or bb.xmax<fx-.3:continue
 shape=a['shape'].intersect(slab)
 if shape.Volume()>.0001:objects.append((shape,a['color']))
# Cavity color comes from the actual cavity intersection, not a drawn envelope.
for void in build.flow_voids:
 shape=void.intersect(slab)
 if shape.Volume()>.01:objects.append((shape,(203,232,235)))
bounds=[(fx,y,z) for y in [-40,155] for z in [-5,195]]
im,proj=render(objects,(900,760),(-1,0,0),bounds=bounds,pad=28)
page=Image.new('RGB',(1480,890),(248,248,248));page.paste(im,(20,98));d=ImageDraw.Draw(page)
d.text((36,25),'D4  /  UNDER-HINGE EXTRACTION',font=font(29,True),fill=(37,46,51))
d.text((36,67),'True side section · the fan exhaust axis rises 15° above the desk',font=font(20),fill=(80,94,100))
def pt(y,z):return tuple(proj([(fx,y,z)])[:,:2][0]+[20,98])
d.line([pt(-40,0),pt(155,0)],fill=(89,102,108),width=3)
for a,b in [((0,55),(0,26)),((3,25),(40,25)),((44,27),(72,51)),((105,75),(150,75+45*math.tan(math.radians(15))))]:arrow(d,pt(*a),pt(*b),(31,134,148),4)
d.text(pt(-30,160),'UNDERSIDE',font=font(15,True),fill=(70,80,85))
d.text(pt(19,160),'LID / USER SIDE →',font=font(15,True),fill=(70,80,85))
d.text(pt(117,69),'15°',font=font(22,True),fill=(31,134,148))
d.line([pt(105,75),pt(152,75)],fill=(143,166,173),width=2)
d.text(pt(-31,12),'DESK',font=font(16,True),fill=(70,80,85))
a=json.loads((R/'airflow-sizing.json').read_text())
vol=sum(v['volume_litres'] for v in a['plenums']);depth=min(v['fan_ray_min_clear_mm'] for v in a['plenums'])
case=next(v for v in a['flow_cases'] if v['assumed_total_CFM']==30)
vmax=max(v['mouth_velocity_m_s'] for v in case['branches'])
rows=[('AIR PATH',None),('Rounded hinge mouths',f"{a['mouth_total_mm2']/100:.1f} cm² total clear throat"),('Broad transfer passage',f"≥{min(v['transfer_section_mm2'] for v in a['plenums'])/100:.0f} cm² per branch at section"),('Curved inner turn','R24.4 mm'),('Fan inlet space',f"≥{depth:.0f} mm at sampled normal rays"),('Connected plenum volume',f"{vol:.2f} L total"),('At assumed 30 CFM total',f"≤{vmax:.2f} m/s through either mouth"),('Rounded-wire guard',f"{a['guard_projected_open_fraction']*100:.0f}% projected open area")]
y=140
for title,sub in rows:
 d.text((966,y),title,font=font(19,True),fill=(37,46,51));y+=28
 if sub:d.text((966,y),sub,font=font(17),fill=(80,94,100));y+=52
 else:y+=17
d.line((936,127,936,813),fill=(217,223,226),width=2)
d.text((36,858),'Arrows show intended flow, not CFD streamlines. Actual airflow and acoustics require prototype measurements.',font=font(16),fill=(99,110,116))
page.save(R/'air-path.png')
print('Section exported',flush=True)
