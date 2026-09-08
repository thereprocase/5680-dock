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
  t=object.__new__(Cached);t.v=[cq.Vector(v.x+x,v.y,v.z+z) for v in self.v];t.f=self.f;return t
fixed=[(Cached(a['shape']),a['color']) for a in build.parts if a['name']!='Precision_5680_REFERENCE']
laptop=Cached(next(a['shape'] for a in build.parts if a['name']=='Precision_5680_REFERENCE'))
# Thin lid seam makes the orientation of the simplified closed envelope visible.
seam=Cached(build.box(5,build.T/2+.015,build.H+7,build.W-10,.08,.65).val())
moving=[(laptop,(188,192,195)),(seam,(89,98,105))]
bounds=[(x,y,z) for x in [-22,build.W+52] for y in [-30,75] for z in [0,build.H+build.p['laptop_depth']+135]]
size=(960,790);cam=(1.15,2.4,.95)
static,project=render(fixed,size,cam,bounds=bounds,return_buffers=True)
# Plug close-up stays at fixed scale and camera to reveal the final 18 mm slide.
near=[(s,c) for (s,c),a in zip(fixed,[a for a in build.parts if a['name']!='Precision_5680_REFERENCE']) if a['shape'].BoundingBox().xmax>build.W-20 and not 'manifold' in a['name'] and not 'foot' in a['name']]
ib=[(x,y,z) for x in [build.W-35,build.W+50] for y in [-30,35] for z in [87,151]]
inset_bg,ip=render(near,(420,350),(1.25,2.4,.7),bounds=ib,return_buffers=True)
def smooth(t):return t*t*(3-2*t)
# Lower, align/engage, docked dwell, withdraw, lift, elevated dwell.
phases=[('Lower into the guides',24,lambda t:(-18,135*(1-smooth(t)))),('Slide toward the far plug',18,lambda t:(-18*(1-smooth(t)),0)),('Docked',18,lambda t:(0,0)),('Withdraw from the plug',18,lambda t:(-18*smooth(t),0)),('Lift out',24,lambda t:(-18,135*smooth(t))),('Ready to dock',12,lambda t:(-18,135))]
frames=[];index=0
for phase,count,fn in phases:
 for j in range(count):
  x,z=fn(j/max(1,count-1));objs=[(s.shifted(x,z),c) for s,c in moving]
  main,_=render(objs,size,cam,bounds=bounds,background=static)
  close,_=render(objs,(420,350),(1.25,2.4,.7),bounds=ib,background=inset_bg)
  page=Image.new('RGB',(1440,900),(248,248,248));page.paste(main,(0,88));page.paste(close,(992,194))
  d=ImageDraw.Draw(page)
  d.text((38,25),'PRECISION 5680  /  D3',font=font(30,True),fill=(37,46,51))
  d.text((39,66),'Your lid-facing view · hinge down · keyboard-left ports at the far end',font=font(19),fill=(96,107,112))
  d.text((1000,139),'FAR END / KEYBOARD LEFT',font=font(19,True),fill=(37,46,51))
  d.text((1000,565),phase,font=font(22,True),fill=(33,107,111))
  d.text((1000,604),f'Travel to dock   {abs(x):4.1f} mm',font=font(18),fill=(70,80,85))
  d.text((1000,634),f'Lift above seat   {z:5.1f} mm',font=font(18),fill=(70,80,85))
  d.text((1000,691),'Lid + fans face you',font=font(19,True),fill=(37,46,51))
  d.text((1000,723),'Fans stand 10° from vertical.',font=font(17),fill=(70,80,85))
  d.text((1000,749),'Intake face stays behind.',font=font(17),fill=(70,80,85))
  d.text((38,856),'CAD motion study · nominal fit · adjustment locks set before docking · cooling performance untested',font=font(16),fill=(105,114,120))
  # Outlet arrows are anchored to the actual fan axes in model coordinates.
  for fx in build.p['fan_centers_x']:
   pts=project([(fx,64,68),(fx,91,63)])[:,:2]+[0,88]
   arrow(d,*pts,(49,149,161),3)
  label=project([(build.W/2,build.T/2+.2,build.H+build.p['laptop_depth']/2+z)])[:,:2][0]+[0,88]
  d.text(tuple(label),'LID / TOWARD YOU',anchor='mm',font=font(17,True),fill=(66,76,83))
  if phase=='Docked':
   pt=project([(build.W+15,20,build.P+15)])[:,:2][0]+[0,88]
   d.text((pt[0]-115,pt[1]-58),'FAR END / PLUG',font=font(16,True),fill=(33,107,111))
   arrow(d,(pt[0]-10,pt[1]-30),tuple(pt),(33,107,111),2)
  d.line((976,128,976,811),fill=(217,223,226),width=2)
  path=F/f'{index:04}.png';page.save(path);frames.append(page);index+=1
  if phase=='Docked' and j==0:page.save(R/'overview.png')
 print('Rendered',phase,index,flush=True)
# 114 frames / 12 fps = 9.5 seconds. MP4 is the full-resolution master.
subprocess.run(['ffmpeg','-y','-framerate','12','-i',str(F/'%04d.png'),'-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(R/'docking-cycle.mp4')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
subprocess.run(['ffmpeg','-y','-i',str(R/'docking-cycle.mp4'),'-vf','fps=12,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer','-loop','0',str(R/'docking-cycle.gif')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print('Animation complete',flush=True)
