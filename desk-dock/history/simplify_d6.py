from pathlib import Path
import json
r=Path(r'D:\Code\Modeling\dell-5560-wall-mount\desk-dock\D6')
t=(r/'build.py').read_text()
# A continuous plenum back wall replaces the raised guide posts and open frame.
# In the untilted frame the bearing plane is at y=T/2. The wall is 0.6 mm
# farther lidward; a replaceable strip bridges it. Rotating that plane by the
# laptop lean makes a physical shared bearing surface, not a camera adjustment.
t=t.replace("def front_y(z,inner=False):return (INNER_C if inner else FACE_C)-math.tan(ELEV)*z", "def front_y(z,inner=False):return (INNER_C if inner else FACE_C)-math.tan(ELEV)*z\n\ndef rest_y(z):return (T/2+.6)/math.cos(math.radians(LEAN))+(z-H)*math.tan(math.radians(LEAN))")
start=t.index("        if not inner:\n")
end=t.index('    def low(',start)
t=t[:start]+'''        if not inner:
            return (cq.Workplane('YZ',origin=(x,0,0)).moveTo(-24,3)
              .lineTo(-24,41).threePointArc((-21,48),(-13,50)).lineTo(13,50)
              .lineTo(rest_y(66),66).lineTo(rest_y(129),129)
              .lineTo(rest_y(134)+2,134).lineTo(front_y(134),134)
              .lineTo(front_y(3),3).close().extrude(length))
        return (cq.Workplane('YZ',origin=(x,0,0)).moveTo(-21.6,5.4)
              .lineTo(-21.6,40).threePointArc((-18,46),(-12,47.6)).lineTo(13,47.6)
              .lineTo(rest_y(66)+2.4,66).lineTo(rest_y(129)+2.4,129)
              .lineTo(rest_y(131.6)+3,131.6).lineTo(front_y(131.6,True),131.6)
              .lineTo(front_y(5.4,True),5.4).close().extrude(length))
''' + t[end:]
start=t.index('    for sign in [-1,1]:');end=t.index("    if tag=='right':",start)
t=t[:start]+'''    # A low underside lip catches the bare case end margin during lowering.
    # The lid rests directly on the plenum. No separate tall cheeks.
    pts=[(-G-3,52),(-G-3,H+12),(-G-1,H+12),(-G,H+8),(-G,52)]
    lip=cq.Workplane('YZ',origin=(xx,0,0)).polyline(pts).close().extrude(span)
    cradle=cradle.union(lip)
''' +t[end:]
start=t.index('# Open underside ribs');end=t.index('for yy in [-12.3,11.0]:',start)
t=t[:start]+'''# Thin replaceable liners on the plenum wall carry the lid-side lean load.
# Two broad, separated contacts use the duct itself as the stand structure.
for i,fx in enumerate([84,269.68],1):
    add(f'lid_bearing_liner_{i}',box(fx-43,T/2,H+20,86,.6,52),(119,131,124))
''' +t[end:]
start=t.index('# A single sculpted end cheek');end=t.index('# Overmold is 25',start)
t=t[:start]+'''# One integrated shelf supports a two-piece plug cassette. Shims set height;
# two broad slots allow in-plane calibration before locking. No stacked stages.
dz=p['height_adjustment'];dy=p['lateral_adjustment'];dx=p['depth_adjustment']
shelf=rb(-40,-18,P-24,39.4,43,5.3,3)
for yy in [-8,8]:
    slot=rb(-20.7,yy-4.7,P-25,13.4,9.4,8,1.7)
    shelf=shelf.cut(slot)
spine=box(-40,18,30,6,7,P-49)
spine=spine.union(box(-40,18,26.7,55,7,6.3))
add('plug_support',shelf.union(spine))
shim=box(-28.3+dx,-9.8+dy,P-18.7,27.7,19.6,5+dz)
for yy in [-8+dy,8+dy]:shim=shim.cut(hole((0,0,1),(-14+dx,yy,P-20),1.7,20))
add('height_shim_pack',shim,(123,137,127))
''' +t[end:]
start=t.index('# Jack screw pushes Z carrier');end=t.index('# Separate stop stays',start)
t=t[:start]+'''# Two M3 screws and broad washers lock the calibrated cassette through shelf slots.
for yy in [-8+dy,8+dy]:
    screw('cassette_lock_'+str(yy),(0,0,1),(-14+dx,yy,P-25),22)
    washer=hole((0,0,1),(-14+dx,yy,P-25),7,1).cut(hole((0,0,1),(-14+dx,yy,P-25.1),1.7,1.2))
    add('cassette_washer_'+str(yy),washer,(175,181,185),True)
''' +t[end:]
start=t.index('# Removable service cover');end=t.index('# Simplified closed laptop',start)
t=t[:start]+'''# Cassette remains exposed for calibration; its rounded cap is the finished surface.

''' +t[end:]
t=t.replace("rib_frame=take('open_underside_rib_frame')",'')
start=t.index("    clip=box(-100 if side=='left'");end=t.index("    if side=='left':",start)
t=t[:start]+t[end:]
t=t.replace("'scope':'Every component is one valid solid. End contact profiles use Dell mesh sections; nominal closed lid envelope is simplified. References are simplified; this is not full physical qualification.'", "'scope':'D6 simplified plenum bearing study. End seats and lid liners support the laptop; no tall cheeks or underside frame. Source-handed USB-C ports. Physical qualification remains outstanding.'")
(r/'build.py').write_text(t)
p=json.loads((r/'parameters.json').read_text())
p['revision']='D6 - plenum as bearing, compact cassette, source-handed ports'
p['contact_scheme']='Profiled hinge-end seats carry weight; laptop leans directly on two thin plenum-wall liners. Two low end lips assist lowering. No upright guide posts or underside rib frame.'
p['height_range']=[-4,5]
p['cassette_adjustment']='1-10 mm shim stack (5 mm nominal) sets height; broad shelf slots permit +/-3 mm transverse and +/-5 mm insertion adjustment. Two M3 locks with 14 mm washers. Select screw length for engagement; nominal hardware represented only.'
(r/'parameters.json').write_text(json.dumps(p,indent=2)+'\n')
# New wall means historical funnel and rib tests are inapplicable; replace with
# load contact and intake checks rather than relabeling previous results.
(r/'alignment_check.py').write_text('''"""D6 bearing-contact and open-intake geometry screen."""
from pathlib import Path
import json,math
import build
R=Path(__file__).resolve().parent
lap=next(a['shape'] for a in build.parts if a['name']=='Precision_5680_REFERENCE')
body=[a for a in build.parts if 'manifold' in a['name']]
liners=[a for a in build.parts if 'lid_bearing_liner' in a['name']]
checks=[]
for a in liners:
    # Faces touch the simplified lid; backing touches its supporting plenum.
    gap=lap.distance(a['shape']); backing=min(a['shape'].distance(b['shape']) for b in body)
    overlap=lap.intersect(a['shape']).Volume()
    assert gap<1e-5 and backing<1e-5 and overlap<1e-5,(a['name'],gap,backing,overlap)
    checks.append(dict(name=a['name'],lid_gap_mm=gap,backing_gap_mm=backing,overlap_mm3=overlap))
lo,hi=build.contacts['intake_window_case_relative_bounds_mm']
# Thin test slab outside the OEM underside, spanning the whole intake window.
slab=build.leaned(build.box(lo[0],lo[1]-5,build.H+lo[2],hi[0]-lo[0],2,hi[2]-lo[2]).val())
blocked=sum(slab.intersect(a['shape']).Volume() for a in body)
assert blocked<1e-5,blocked
data=dict(bearing_contacts=checks,intake_screen_blockage_mm3=blocked,rib_net_free_fraction=1.0,scope='Nominal geometry only. Added stand has no structure over the intake window; excludes OEM grille solidity. Direct plenum contact checked; no claim of passive self-centering, strength or friction qualification.')
(R/'alignment-validation.json').write_text(json.dumps(data,indent=2)+'\\n')
print(json.dumps(data,indent=2))
''')
# Animation is delivered as a GIF with no external encoder requirement.
t=(r/'animate.py').read_text().replace('2° lean onto fixed guides','2° lean onto the plenum').replace('Open ribs · feet stay clear.','Open intake · feet stay clear.').replace('Lower into the guides','Lower onto the seats')
t=t[:t.index('# 114 frames /')]+'''# Portable local animation output (no ffmpeg installation required).
small=[]
for f in frames:
    q=f.copy();q.thumbnail((960,600));small.append(q)
small[0].save(R/'docking-cycle.gif',save_all=True,append_images=small[1:],duration=83,loop=0)
print('Animation complete',flush=True)
'''
(r/'animate.py').write_text(t)
print('Simplified D6 prepared')
