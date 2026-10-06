"""Does the plug-positioner arm actually reach the laptop's USB-C port?

The builder dimensions the whole arm from BX/BY/BZ and never reads
port_from_rear_case / port_y / rear_case_seat_z.  D1-D7 all use
P = rear_case_seat_z + port_from_rear_case (unleaned frame).  This script
carries that same datum into the leaned D9 assembly frame and measures.
"""
import json,math,sys
from pathlib import Path
import cadquery as cq
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'generated'
P=json.loads((HERE.parent/'source-inputs/parameters.json').read_text())
LEAN=P['laptop_lean_deg']

def lean(y,z):
    t=math.radians(-LEAN);dy,dz=y-0.0,z-54.0
    return (dy*math.cos(t)-dz*math.sin(t), 54.0+dy*math.sin(t)+dz*math.cos(t))

for tag,off in (('port1',P['port_from_rear_case']),('port2',P['second_port_from_rear_case'])):
    uy,uz=P['port_y'],P['rear_case_seat_z']+off
    ly,lz=lean(uy,uz)
    print(f'{tag}: unleaned y={uy:.3f} z={uz:.3f}  ->  leaned y={ly:.3f} z={lz:.3f}')

py,pz=lean(P['port_y'],P['rear_case_seat_z']+P['port_from_rear_case'])
man=json.loads((OUT/'manifest.json').read_text())
rx0,ry0,rz0=man['accessory_socket']['socket_origin']
BY,BZ=ry0+19,rz0+24
print(f'socket_origin={rx0,ry0,rz0}  pivot (y,z)=({BY},{BZ})')
print(f'pivot->port  dy={py-BY:.2f}  dz={pz-BZ:.2f}  radius={math.hypot(py-BY,pz-BZ):.2f} mm')

for n in ('plug-holder-polar-plug-rotor','plug-holder-polar-outer-arm','plug-holder-polar-inner-arm'):
    s=cq.importers.importStep(str(OUT/(n+'.step'))).val();b=s.BoundingBox()
    print(f'{n}: x[{b.xmin:.1f},{b.xmax:.1f}] y[{b.ymin:.1f},{b.ymax:.1f}] z[{b.zmin:.1f},{b.zmax:.1f}]')
    c=s.Center();print(f'    centroid y={c.y:.1f} z={c.z:.1f}  radius from pivot={math.hypot(c.y-BY,c.z-BZ):.1f}')
