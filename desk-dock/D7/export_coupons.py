"""Current printed interface samples; import after build to reuse final CAD."""
import hashlib,json,shutil
from pathlib import Path
import cadquery as cq
import build
from breakaway_geometry import datum,cyl
R=Path(__file__).resolve().parent;OUT=R/'print';OUT.mkdir(exist_ok=True)
rows=[]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record_copy(source,purpose):
 target=OUT/('coupon_'+source.name);shutil.copy2(source,target)
 rows.append(dict(file=target.name,purpose=purpose,source=str(source.relative_to(R)),source_sha256=digest(source),sha256=digest(target)))
for source in sorted((R/'printed-fastener-review').glob('*.stl')):
 if 'custom12' not in source.name:record_copy(source,'Matched8x2 or10x2 thread fit; custom pair, not ISO. Print supplied orientation.')
for source in sorted((R/'cassette-review').glob('cap_pin_receiver_bore_*.stl')):
 record_copy(source,'Use actual6.5mm cap pin as male; bore friction sample, not full clevis strength.')
def save(name,shape,purpose):
 s=shape.val() if isinstance(shape,cq.Workplane) else shape
 assert s.isValid() and len(s.Solids())==1,(name,len(s.Solids()))
 b=s.BoundingBox();s=s.translate((-b.xmin,-b.ymin,-b.zmin));b=s.BoundingBox()
 target=OUT/('coupon_'+name+'.stl');cq.exporters.export(s,str(target),tolerance=.05,angularTolerance=.1)
 rows.append(dict(file=target.name,purpose=purpose,dimensions_mm=[b.xlen,b.ylen,b.zlen],sha256=digest(target),valid_single_solid=True))
by={a['name']:a['shape'] for a in build.parts}
def fan_unpose(s):return s.translate((-84,-build.FAN_Y,-build.FAN_Z)).rotate((0,0,0),(1,0,0),-build.ANGLE).translate((84,91,22.5))
crop=build.box(16.5,30,build.FAN_D['rail_front']-.2,9,20,build.FAN_D['back']+2.8-(build.FAN_D['rail_front']-.2)).val()
for name,key in [('fan_slide_rail','01_manifold_with_cradle'),('fan_grille_edge','01_fan_guard_retainer')]:
 s=fan_unpose(by[key]).intersect(crop)
 save(name,s,'Actual short lower rail/friction-land pair. Does not sample whole-frame shrinkage or fan fit.')
px,pz=datum(build.p)
def unlean(s):return s.rotate((0,0,build.H),(1,0,build.H),build.LEAN)
fixed=unlean(by['01_manifold_with_cradle']).intersect(cyl(px,26,pz,34,8).val())
rotor=unlean(by['breakaway_carrier']).intersect(cyl(px,18,pz,34,13).val())
save('fixed_cam_and_pilot',fixed.rotate((0,0,0),(1,0,0),-90),'Combined female cam/pilot seat; back face on bed. Seat-fit and repeatability sample, not force calibration.')
save('rotor_cam_and_pilot',rotor.rotate((0,0,0),(1,0,0),90),'Combined male cam/pilot seat; flat back on bed. Fit with female sample before full holder.')
P=build.P;cy=build.Y
body=unlean(by['Dell_plug_overmold_REFERENCE']).intersect(build.box(-50,-30,P-20,70,60,25.9).val())
nose=build.box(-2,cy-3.25,P-5.5,7.15,6.5,11)
eye=cyl(5.15,cy-3.25,P,7.5,6.5).cut(cyl(5.15,cy-3.4,P,3.4,6.8))
dummy=cq.Workplane(obj=body).union(nose).union(eye).cut(cyl(5.15,cy-3.4,P,3.4,6.8))
save('dummy_plug_load_eye',dummy.rotate((0,0,0),(1,0,0),90),'BENCH ONLY, laptop removed. Nonfunctional dummy withload eye centered at nominal tip. Cap squeeze relieved for rigidPETG. Apply measured symmetric load; verify fixture itself survives.')
(OUT/'coupon-manifest.json').write_text(json.dumps(dict(parts=rows,count=len(rows),scope='Print fit and detached bench samples. No tested force, fatigue, shrinkage or impact claim.'),indent=2)+'\n')
print('Current coupons:',len(rows),flush=True)
