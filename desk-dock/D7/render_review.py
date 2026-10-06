"""Render the exact D7 CAD, without a mirrored projection."""
from pathlib import Path
import build
from raster import render
R=Path(__file__).resolve().parent
objects=[(a['shape'],a['color']) for a in build.parts]
img,_=render(objects,(1500,1080),(-.55,1,.55),pad=45)
img.save(R/'D7-assembled.png')
objects=[(a['shape'],a['color']) for a in build.parts if a['name']!='Precision_5680_REFERENCE' and not a['name'].startswith('RUBBER_FOOT_') and not any(k in a['name'] for k in ['fan_guard','fan_thumb_lock','fan_M3_screw'])]
img,_=render(objects,(1500,850),(-.15,1,.28),pad=45)
img.save(R/'D7-fan-pockets.png')
img,_=render(objects,(1500,850),(.15,-1,.45),pad=45)
img.save(R/'D7-continuous-lip.png')
print('CAD review images saved',flush=True)

# Exact ready/folded CAD comparison at the plug station, including spring shape.
from breakaway_geometry import datum,cam_lift,make_spring,moving_names
from PIL import Image,ImageDraw
px,pz=datum(build.p);lift=cam_lift(build.p,45)
panels=[]
for folded in [False,True]:
    objects=[]
    for a in build.parts:
        n=a['name'];s=a['shape']
        if n=='01_manifold_with_cradle':
            s=s.intersect(build.box(-100,-100,-10,140,250,250).val())
        elif not(moving_names(n) or n.startswith('breakaway_') or 'chassis_stop_screw' in n or n=='stop_soft_tip'):
            continue
        if folded:
            if n=='breakaway_spring_cartridge':s=build.leaned(make_spring(build.p,build.p['breakaway']['spring_preload_deflection_mm']+lift).val())
            elif moving_names(n) or n in ['breakaway_pivot_pin_10mm','breakaway_preload_hand_nut']:
                s=s.rotate((0,0,build.H),(1,0,build.H),build.LEAN)
                if moving_names(n):s=s.rotate((px,0,pz),(px,1,pz),45)
                s=build.leaned(s.translate((0,-lift,0)))
        objects.append((s,a['color']))
    img,_=render(objects,(950,950),(-.65,-1,.4),pad=55)
    img.save(R/('D7-breakaway-folded.png' if folded else 'D7-breakaway-ready.png'))
    panels.append(img.convert('RGB'))
canvas=Image.new('RGB',(1900,1010),(240,243,239));draw=ImageDraw.Draw(canvas)
for x,label,im in [(0,'READY - locating seats engaged',panels[0]),(950,'FOLDED - return by hand to reset',panels[1])]:
    canvas.paste(im,(x,60));draw.text((x+30,22),label,fill=(38,57,53),font_size=24)
canvas.save(R/'D7-breakaway.png')
