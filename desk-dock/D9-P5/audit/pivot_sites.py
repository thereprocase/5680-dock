"""Candidate base-pivot centres: distance to the ports, desk clearance for a
given nut OD, and how much solid cradle face exists behind a backing ring at
the cradle plug-end face (x = 9.5), for each candidate."""
import json,math
from pathlib import Path
import cadquery as cq
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'generated'
P=json.loads((HERE.parent/'source-inputs/parameters.json').read_text());LEAN=P['laptop_lean_deg']
def lean(y,z):
    t=math.radians(-LEAN);dy,dz=y,z-54.0
    return (dy*math.cos(t)-dz*math.sin(t),54.0+dy*math.sin(t)+dz*math.cos(t))
p1=lean(P['port_y'],P['rear_case_seat_z']+P['port_from_rear_case'])
p2=lean(P['port_y'],P['rear_case_seat_z']+P['second_port_from_rear_case'])
cradle=cq.importers.importStep(str(OUT/'M1-outer-cradle-shell.step')).val()
socket=cq.importers.importStep(str(OUT/'accessory-socket-body.step')).val()
bb=cradle.BoundingBox();print(f'M1 outer cradle bbox x[{bb.xmin:.1f},{bb.xmax:.1f}] y[{bb.ymin:.1f},{bb.ymax:.1f}] z[{bb.zmin:.1f},{bb.zmax:.1f}]')
sb=socket.BoundingBox();print(f'socket body bbox x[{sb.xmin:.1f},{sb.xmax:.1f}] y[{sb.ymin:.1f},{sb.ymax:.1f}] z[{sb.zmin:.1f},{sb.zmax:.1f}]')
def face_solid(yc,zc,ro,ri,x0=10.5,t=1.0):
    slab=cq.Solid.makeCylinder(ro,t,cq.Vector(x0-t,yc,zc),cq.Vector(1,0,0)).cut(cq.Solid.makeCylinder(ri,t+2,cq.Vector(x0-t-1,yc,zc),cq.Vector(1,0,0)))
    v=slab.intersect(cradle).Volume()+slab.intersect(socket).Volume()
    return v/slab.Volume()
print(f'\nports (leaned): p1=({p1[0]:.1f},{p1[1]:.1f})  p2=({p2[0]:.1f},{p2[1]:.1f})')
print(f'{"pivot (y,z)":>14} {"r->p1":>6} {"r->p2":>6} {"swing1":>7} | ring 130/78 solid | ring 110/60 solid | nut100 bottom z | nut124 bottom z')
for yc,zc in [(45,70),(45,80),(60,70),(75,70),(90,70),(100,70),(100,80),(110,75),(60,60),(75,60)]:
    r1=math.hypot(p1[0]-yc,p1[1]-zc);r2=math.hypot(p2[0]-yc,p2[1]-zc)
    a1=math.degrees(math.atan2(yc-p1[0],p1[1]-zc))
    print(f'{str((yc,zc)):>14} {r1:6.1f} {r2:6.1f} {a1:6.1f}° | {face_solid(yc,zc,65,39):15.0%} | {face_solid(yc,zc,55,30):15.0%} | {zc-50:15.1f} | {zc-62:15.1f}')
