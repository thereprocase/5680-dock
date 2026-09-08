"""Rear CAD review and a scaled source-derived heel profile, generated from data."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import build
from raster import render,font
R=Path(__file__).resolve().parent
objs=[(a['shape'],a['color']) for a in build.parts]
lo,hi=build.contacts['intake_window_case_relative_bounds_mm']
zone=build.box(build.W-hi[0],-build.T/2-.12,build.H+lo[2],hi[0]-lo[0],.1,hi[2]-lo[2]).val()
objs.append((build.leaned(zone),(99,133,139)))
pic,_=render(objs,(1000,830),(-1.05,-2.4,.8),pad=45)
page=Image.new('RGB',(1600,1040),(248,248,248));page.paste(pic,(0,125));d=ImageDraw.Draw(page)
d.text((38,27),'D5  /  FIXED GUIDES + OPEN RIBS',font=font(31,True),fill=(37,46,51))
d.text((38,74),'Intake region tinted · rubber feet shown in black · laptop leans 2° toward the lid-side guides',font=font(19),fill=(80,94,100))
a=json.loads((R/'alignment-validation.json').read_text())
# Aspect ratio is equal: no exaggeration of the carefully extracted heel curve.
fig,ax=plt.subplots(figsize=(5.2,3.4),dpi=120);fig.patch.set_facecolor('#f8f8f8');ax.set_facecolor('#f8f8f8')
for c in build.contacts['curves']:
 q=np.array(c['rear_curve_local_yz_mm']);ax.plot(q[:,0],q[:,1],color='#9aabb0',lw=1)
q=np.array(build.curve);q[:,1]-=build.H
ax.plot(q[:,0],q[:,1],color='#258b95',lw=2,label='Seat envelope')
ax.fill_between(q[:,0],q[:,1]-.3,-3,color='#47565b',alpha=.9)
ax.set_aspect('equal');ax.set_xlim(-4,8);ax.set_ylim(-3,7);ax.set_xlabel('Across case thickness (mm)');ax.set_ylabel('Above rear datum (mm)');ax.spines[['top','right']].set_visible(False);ax.tick_params(labelsize=9);fig.tight_layout();fig.savefig(R/'profile-detail.png',facecolor=fig.get_facecolor());plt.close(fig)
profile=Image.open(R/'profile-detail.png');profile.thumbnail((570,385));page.paste(profile,(1010,205));d=ImageDraw.Draw(page)
d.text((1030,145),'SCALED HINGE-END PROFILE',font=font(20,True),fill=(37,46,51))
y=615
for title,sub in [('Five Dell case sections','Profiled seat + replaceable 0.3 mm liner'),('Rubber-foot keepout','2 mm expansion; checked along insertion'),('Stand ventilation opening',f"{a['rib_net_free_fraction']*100:.1f}% net free over the OEM intake region"),('Bearing load path','Hinge-end case seats + lid-side guides')]:
 d.text((1030,y),title,font=font(19,True),fill=(37,46,51));d.text((1030,y+29),sub,font=font(16),fill=(80,94,100));y+=81
d.line((1000,135,1000,965),fill=(217,223,226),width=2)
d.text((38,994),'Visualization-mesh dimensions, not factory tolerances. Prescribed motion checks do not replace fit, friction or load testing.',font=font(17),fill=(99,110,116))
page.save(R/'contact-study.png');print('Contact study exported',flush=True)
