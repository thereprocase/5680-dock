"""CAD-derived, fixed-camera docking animation. Requires ffmpeg, CadQuery, Pillow."""
from pathlib import Path
import math,json,subprocess
import numpy as np
from PIL import Image,ImageDraw
import build
from raster import render,font,arrow
R=Path(__file__).resolve().parent
F=R/'frames';F.mkdir(exist_ok=True)
class Cached:
 def __init__(self,s): self.v,self.f=s.tessellate(.45,.25)
 def tessellate(self,*args):return self.v,self.f
 def shifted(self,x,z):
  import cadquery as cq
  t=object.__new__(Cached);t.v=[cq.Vector(v.x+x,v.y+math.sin(math.radians(build.LEAN))*z,v.z+math.cos(math.radians(build.LEAN))*z) for v in self.v];t.f=self.f;return t
fixed=[(Cached(a['shape']),a['color']) for a in build.parts if a['name']!='Precision_5680_REFERENCE' and not a['name'].startswith('RUBBER_FOOT_')]
laptop=Cached(next(a['shape'] for a in build.parts if a['name']=='Precision_5680_REFERENCE'))
# Thin lid seam makes the orientation of the simplified closed envelope visible.
seam=Cached(build.leaned(build.box(5,build.T/2+.015,build.H+7,build.W-10,.08,.65).val()))
moving=[(laptop,(188,192,195)),(seam,(89,98,105))]+[(Cached(a['shape']),a['color']) for a in build.parts if a['name'].startswith('RUBBER_FOOT_')]
bounds=[(x,y,z) for x in [-52,build.W+22] for y in [-30,127] for z in [0,build.H+build.p['laptop_depth']+135]]
size=(960,790);cam=(-1.15,2.4,.95)
static,project=render(fixed,size,cam,bounds=bounds,return_buffers=True)
# Plug close-up stays at fixed scale and camera to reveal the final 18 mm slide.
near=[(s,c) for (s,c),a in zip(fixed,[a for a in build.parts if a['name']!='Precision_5680_REFERENCE' and not a['name'].startswith('RUBBER_FOOT_')]) if a['shape'].BoundingBox().xmin<20 and not 'manifold' in a['name'] and not 'foot' in a['name'] and a['name']!='removable_adjustment_cover']
ib=[(x,y,z) for x in [-50,35] for y in [-30,35] for z in [87,151]]
inset_bg,ip=render(near,(420,350),(-1.25,2.4,.7),bounds=ib,return_buffers=True)
def smooth(t):return t*t*(3-2*t)
# Lower, align/engage, docked dwell, withdraw, lift, elevated dwell.
phases=[('Lower onto the seats',12,lambda t:(18,135*(1-smooth(t)))),('Slide toward the far plug',8,lambda t:(18*(1-smooth(t)),0)),('Docked',8,lambda t:(0,0)),('Withdraw from the plug',8,lambda t:(18*smooth(t),0)),('Lift out',12,lambda t:(18,135*smooth(t))),('Ready to dock',4,lambda t:(18,135))]
frames=[];index=0
for phase,count,fn in phases:
 for j in range(count):
  x,z=fn(j/max(1,count-1));objs=[(s.shifted(x,z),c) for s,c in moving]
  main,_=render(objs,size,cam,bounds=bounds,background=static)
  close,_=render(objs,(420,350),(-1.25,2.4,.7),bounds=ib,background=inset_bg)
  page=Image.new('RGB',(1440,900),(248,248,248));page.paste(main,(0,88));page.paste(close,(992,194))
  d=ImageDraw.Draw(page)
  d.text((38,25),'PRECISION 5680  /  D6',font=font(30,True),fill=(37,46,51))
  d.text((39,66),'Your lid-facing view · hinge down · keyboard-left ports at the far end',font=font(19),fill=(96,107,112))
  d.text((1000,139),'PLUG DETAIL',font=font(19,True),fill=(37,46,51))
  d.text((1000,565),phase,font=font(22,True),fill=(33,107,111))
  d.text((1000,604),f'Travel to dock   {abs(x):4.1f} mm',font=font(18),fill=(70,80,85))
  d.text((1000,634),f'Lift above seat   {z:5.1f} mm',font=font(18),fill=(70,80,85))
  d.text((1000,691),'5° lean onto the plenum',font=font(19,True),fill=(37,46,51))
  d.text((1000,723),'Exhaust points 18° upward.',font=font(17),fill=(70,80,85))
  d.text((1000,749),'Open intake · feet stay clear.',font=font(17),fill=(70,80,85))
  d.text((38,856),'CAD motion study · nominal fit · adjustment locks set before docking · cooling performance untested',font=font(16),fill=(105,114,120))
  # Outlet arrows are anchored to the actual fan axes in model coordinates.
  for fx in build.p['fan_centers_x']:
   pts=project([(fx,build.FAN_Y+11,75),(fx,build.FAN_Y+40,75+29*math.tan(build.ELEV))])[:,:2]+[0,88]
   arrow(d,*pts,(49,149,161),3)
  label=project([(build.W/2+x,build.T/2+.2,build.H+build.p['laptop_depth']/2+z)])[:,:2][0]+[0,88]
  d.text(tuple(label),'LID / TOWARD YOU',anchor='mm',font=font(17,True),fill=(66,76,83))
  if phase=='Docked':
   pt=project([(-15,20,build.P+15)])[:,:2][0]+[0,88]
   d.text((pt[0]-115,pt[1]-58),'FAR END / PLUG',font=font(16,True),fill=(33,107,111))
   arrow(d,(pt[0]-10,pt[1]-30),tuple(pt),(33,107,111),2)
  d.line((976,128,976,811),fill=(217,223,226),width=2)
  path=F/f'{index:04}.png';page.save(path);frames.append(page);index+=1
  if phase=='Docked' and j==0:page.save(R/'overview.png')
 print('Rendered',phase,index,flush=True)
# Portable local animation output (no ffmpeg installation required).
small=[]
for f in frames:
    q=f.copy();q.thumbnail((960,600));small.append(q)
small[0].save(R/'docking-cycle.gif',save_all=True,append_images=small[1:],duration=160,loop=0)
print('Animation complete',flush=True)
