"""Export the exact 43 manufacturing solids to one named, separated STEP assembly.
Uses the validated BREP cache and the existing manufacturing poses/unloaded springs.
"""
from pathlib import Path
import sys,json,hashlib
import cadquery as cq
R=Path(__file__).resolve().parent
from fan_service import fan_dimensions,POSE_ANCHOR_Z
from fan_retention import add_top_clips
from breakaway_geometry import make_spring
p=json.loads((R/'parameters.json').read_text(encoding='utf-8'))
manifest=json.loads((R/'print-manifest.json').read_text(encoding='utf-8'))['parts']
cache=Path(sys.argv[1]);out=R.parents[1]/'docs/downloads/Precision_5680_D8_Printables.step'
def box(x,y,z,a,b,c):return cq.Workplane('XY').box(a,b,c,centered=False).translate((x,y,z))
class NullRoof:
 def union(self,x):return self
 def cut(self,x):return self
free={};angle=90+p['fan_exhaust_elevation_deg']
for i,fx in enumerate(p['fan_centers_x'],1):
 def pose(s):return s.translate((-fx,-91,-POSE_ANCHOR_Z)).rotate((0,0,0),(1,0,0),angle).translate((fx,p['fan_center_y'],p['fan_center_z']))
 fit=p['fan_fit'];d=fan_dimensions(p['fan_thickness'],fit['pad_thickness_mm'])
 gf=30-fit['pocket_axial_envelope_mm']-fit['guard_gap_mm']-fit['guard_bar_depth_mm']
 _,_,_,f=add_top_clips(i,fx,NullRoof(),pose,box,lambda *a:None,gf,d['envelope_front'],30)
 free.update(f)
assembly=cq.Assembly(name='D8_43_PRINTABLE_PARTS');rows=[]
for j,row in enumerate(manifest):
 n=row['part'];s=cq.Shape.importBrep(str(cache/(n+'.brep')))
 if n in free:s=free[n].val()
 if not n.startswith(('01_','02_','bridge_key_')):s=s.rotate((0,0,p['rear_case_seat_z']),(1,0,p['rear_case_seat_z']),p['laptop_lean_deg'])
 if n=='breakaway_spring_cartridge':s=make_spring(p,delta=0).val()
 for axis,angle in row['rotations']:s=s.rotate((0,0,0),{'X':(1,0,0),'Y':(0,1,0),'Z':(0,0,1)}[axis],angle)
 b=s.BoundingBox();s=s.translate((-b.xmin,-b.ymin,-b.zmin));b=s.BoundingBox()
 assert s.isValid() and len(s.Solids())==1,n
 assert abs(s.Volume()-row['volume_mm3'])<.01,n
 assert max(abs(a-b) for a,b in zip([b.xlen,b.ylen,b.zlen],row['dimensions_mm']))<.001,n
 # Spaced inventory, not a claimed printer plate layout. All objects are separate.
 s=s.translate(((j%7)*240,(j//7)*240,0));assembly.add(s,name=n)
 rows.append(dict(name=n,material=row['material'],volume_mm3=s.Volume(),print_pose_matches_manifest=True))
assembly.save(str(out))
reloaded=cq.importers.importStep(str(out)).val();assert len(reloaded.Solids())==43
errors=[abs(a-b)/b for a,b in zip(sorted(v.Volume() for v in reloaded.Solids()), sorted(r['volume_mm3'] for r in rows))]
assert all(v.isValid() for v in reloaded.Solids())
assert max(errors)<1e-4, max(errors)
record=dict(passed=True,step_roundtrip_max_relative_volume_error=max(errors),parts=rows,solid_count=43,filename=out.name,bytes=out.stat().st_size,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),scope='Separate named solids, spaced inventory in manufacturing orientations; arrange onto plates in slicer. Includes TPU stop tip separately; no laptop, fans, optional desk pads or hardware references.',manifest_sha256=hashlib.sha256((R/'print-manifest.json').read_bytes()).hexdigest())
(R/'printables-step-check.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('Printable STEP verified:',len(rows),'solids,',out.stat().st_size,'bytes',flush=True)
