"""Reach, telescoping travel and loosened angular sweep for the clamp pivot.

Radius is measured from the base pivot axis to the TIP PIVOT axis, which is
where the plug rotor turns.  The port datum is the one D1-D7 all use:
P = rear_case_seat_z + port_from_rear_case, port_y, in the unleaned frame,
then carried through the same -8 deg lean the builder applies.
"""
import json,math,sys
from pathlib import Path
import cadquery as cq
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'generated'
P=json.loads((HERE.parent/'source-inputs/parameters.json').read_text());LEAN=P['laptop_lean_deg']
man=json.loads((OUT/'manifest.json').read_text())
BY,BZ=man['accessory_socket']['base_clamp']['pivot_axis_yz_mm'];RE=man['accessory_socket']['reach']
def lean(y,z):
    t=math.radians(-LEAN);dy,dz=y,z-54.0
    return (dy*math.cos(t)-dz*math.sin(t),54.0+dy*math.sin(t)+dz*math.cos(t))

print('== required radius to each port (base pivot -> port axis) ==')
need={}
for tag,off in (('port-1',P['port_from_rear_case']),('port-2',P['second_port_from_rear_case'])):
    py,pz=lean(P['port_y'],P['rear_case_seat_z']+off)
    r=math.hypot(py-BY,pz-BZ);a=math.degrees(math.atan2(BY-py,pz-BZ))
    need[tag]=(r,a);print(f'  {tag}: leaned y={py:7.2f} z={pz:7.2f}  radius={r:6.2f} mm  swing={a:5.1f} deg toward the laptop')

def travel(tongue0,slot0,slot1,sleeve0,bore_a,bore_b,tip):
    """Slot and both sleeve bores are given as absolute Z in the modelled pose."""
    s_max=min(bore_a-slot0,bore_b-slot0)          # retract until the low bore hits the slot floor
    s_min=-min(slot1-bore_a,slot1-bore_b)         # extend until the high bore hits the slot roof
    return s_min,s_max,tip-s_max,tip+(-s_min)

print('\n== travel and reach (from the manifest) ==');print(json.dumps(RE,indent=1))

# ---- loosened angular sweep, by boolean, against everything that is fixed ----
ARM=['plug-holder-polar-inner-arm','plug-holder-polar-outer-arm','plug-holder-polar-plug-rotor','plug-holder-clamp-cam-spatula','plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut','plug-holder-rotor-pinch-shim',
     'plug-holder-tip-annular-screw','plug-holder-tip-annular-nut','plug-holder-tip-head-thrust-washer',
     'plug-holder-tip-nut-thrust-washer','plug-holder-length-clamp-1-screw','plug-holder-length-clamp-1-nut',
     'plug-holder-length-clamp-2-screw','plug-holder-length-clamp-2-nut']
FIXED=[p['part'] for p in man['parts'] if p['part'] not in ARM]
def load(n):return cq.importers.importStep(str(OUT/(n+'.step'))).val()
arm=[load(n) for n in ARM];fixed=[load(n) for n in FIXED]
laptop=cq.Solid.makeBox(P['laptop_width'],P['laptop_thickness'],232.33,
        cq.Vector(0,-P['laptop_thickness']/2,62)).rotate((0,0,54),(1,0,54),-LEAN)
desk=cq.Solid.makeBox(600,600,20,cq.Vector(-200,-300,-24.0))   # desk top at z = -4
axis0=cq.Vector(0,BY,BZ);axis1=cq.Vector(1,BY,BZ)
clear=[]
for deg in range(-180,181,3):
    moved=[s.rotate(axis0,axis1,deg) for s in arm]
    hit=None
    for s in moved:
        bb=s.BoundingBox()
        if bb.zmin<-4.0: hit='desk';break
        for o in fixed+[laptop]:
            ob=o.BoundingBox()
            if not all(min(getattr(bb,k+'max'),getattr(ob,k+'max'))-max(getattr(bb,k+'min'),getattr(ob,k+'min'))>1e-5 for k in 'xyz'):continue
            if s.intersect(o).Volume()>0.01: hit='part';break
        if hit:break
    if not hit:clear.append(deg)
print('\n== loosened angular sweep, 3-deg steps, arm group vs dock + laptop + desk ==')
if clear:
    run=[clear[0]];best=[clear[0],clear[0]]
    for a,b in zip(clear,clear[1:]):
        if b-a==3:run.append(b)
        else:
            if run[-1]-run[0]>best[1]-best[0]:best=[run[0],run[-1]]
            run=[b]
    if run[-1]-run[0]>best[1]-best[0]:best=[run[0],run[-1]]
    cont=[d for d in clear if best[0]<=d<=best[1]]
    print(f'  clear angles: {len(clear)} of 121 sampled')
    print(f'  largest continuous window containing the modelled pose: {best[0]:+d} .. {best[1]:+d} deg  ({best[1]-best[0]} deg)')
    print(f'  modelled pose (0 deg) inside that window: {0 in cont}')
else:
    print('  NO clear angle found')
