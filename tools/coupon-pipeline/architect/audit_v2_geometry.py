"""Independent imported-solid audit; does not invoke the coupon builder."""
from pathlib import Path
import hashlib,json
import cadquery as cq

root=Path(__file__).resolve().parents[3]
d8=Path('/mnt/f/Code/5680-dock-fit-20260917/desk-dock/D8')
generated=root/'work/quartet-team/geometry/profile-v2/generated'
output=root/'work/quartet-team/architect/v2-independent-geometry.json'
params=json.loads((d8/'parameters.json').read_text())
fit=json.loads((d8/'quick-fit/R2/fit-parameters.json').read_text())
profile=json.loads((d8/'quick-fit/R2/seat-profile.json').read_text())['revised_yz_mm']
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def box(x,y,z,dx,dy,dz):
    return cq.Workplane('XY').box(dx,dy,dz,centered=False).translate((x,y,z)).val()
def delta(a,b): return a.cut(b).Volume()+b.cut(a).Volume()
width=24.0
x0=(38.1-width)/2
y0=-params['laptop_thickness']/2-3-fit['lip_outward_shift_mm']-.5
y1=params['laptop_thickness']/2+6
crop=box(x0,y0,44,width,y1-y0,28)
r1=cq.importers.importStep(str(d8/'quick-fit/D8-quick-fit-bracket.step')).val().intersect(crop)
r2=cq.importers.importStep(str(d8/'quick-fit/R2/D8-R2-quick-fit-bracket.step')).val().intersect(crop)
points=[tuple(p) for p in profile]+[(y,z-1) for y,z in reversed(profile)]
band=cq.Workplane('YZ',origin=(x0,0,0)).polyline(points).close().extrude(width).val()
h=params['rear_case_seat_z']
band=band.rotate((0,0,h),(1,0,h),-params['laptop_lean_deg'])
before=r2
removed=before.intersect(band)
c0=before.cut(band)
assert removed.Volume()>1
assert 49.7<band.BoundingBox().zmin
identities=[('A_R1_native_control',r1,1),
            ('B_R2_native_documented_capture',before,2),
            ('C_R2_native_plus_1mm_seat_relief',c0,3)]
results={}
for name,expected,count in identities:
    for i in range(count):
        expected=expected.cut(box(x0,-2.5+i*1.05,49,width,.48,.7))
    path=generated/(name+'.step')
    actual=cq.importers.importStep(str(path)).val()
    difference=delta(actual,expected)
    assert difference<1e-5,(name,difference)
    samples=[]
    slab_reference=None
    for x in (8.0,19.05,30.0):
        slab=actual.intersect(box(x,-30,35,.25,60,45)).translate((-x,0,0))
        if slab_reference is None: slab_reference=slab
        mismatch=delta(slab,slab_reference)
        assert mismatch<1e-5,(name,x,mismatch)
        samples.append({'source_x_mm':x,'slab_width_mm':.25,'volume_mm3':slab.Volume(),'aligned_difference_mm3':mismatch})
    results[name]={'source_step_sha256':digest(path),'valid':actual.isValid(),'solids':len(actual.Solids()),
                   'volume_mm3':actual.Volume(),'symmetric_difference_from_independent_expected_mm3':difference,
                   'print_axis_samples':samples}
receipt={'passed':True,'method':'Imported actual STEP vs independently constructed native-source crop/ID/rotated relief; builder not imported',
         'C_relief_removed_volume_mm3':removed.Volume(),'C_removed_by_difference_mm3':before.Volume()-c0.Volume(),
         'added_base':False,'identification_notches_top_z_mm':49.7,
         'C_relief_min_z_mm':band.BoundingBox().zmin,
         'coupon_validation':results,
         'qualification':'CAD diagnostic geometry only. Original R1 physical identity, actual laptop fit and loads unverified.'}
output.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
