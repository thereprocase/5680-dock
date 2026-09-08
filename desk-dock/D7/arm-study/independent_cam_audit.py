"""Optional slow cam-only CAD scan. Use --full-cad to run explicitly.

The current analytic audit is independent_cam_facets.py. This diagnostic
excludes the pilot, stop and other assembly geometry and is not a release.
"""
from pathlib import Path
import sys,json,math
import cadquery as cq
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent))
import breakaway_geometry as b
if '--full-cad' not in sys.argv:
    raise SystemExit('Use independent_cam_facets.py for the fast ruled-height audit, or add --full-cad for this optional cam-only intersection scan.')
p=json.loads((R.parent/'parameters.json').read_text())
px,pz=b.datum(p)
male=b.cam_teeth(p).val()
fixed=b.cyl(px,26,pz,34,2).cut(b.cam_teeth(p,.15)).val()
axis=((px,0,pz),(px,1,pz))

def volume(rotated,lift):
    return rotated.translate((0,-lift,0)).intersect(fixed).Volume()

rows=[]
for theta in [.1,.5,1,2,3]:
    rotated=male.rotate(*axis,theta)
    ideal=b.cam_lift(p,theta)
    checks=[]
    for extra in [0,.02,.1]:
        lift=min(.8,ideal+extra)
        checks.append({'lift_mm':lift,'intersection_mm3':volume(rotated,lift)})
    lo,hi=ideal,.800001
    for _ in range(10):
        mid=(lo+hi)/2
        if volume(rotated,mid)>1e-5:lo=mid
        else:hi=mid
    row={'angle_deg':theta,'ideal_lift_mm':ideal,'checks':checks,
         'minimum_lift_for_volume_under_1e_5_mm3':hi}
    rows.append(row);print(json.dumps(row),flush=True)

a=p['breakaway'];k=2*a['nominal_E_MPa']*a['spring_width_mm']*a['spring_thickness_mm']**3/a['spring_leaf_length_mm']**3
d=a['spring_preload_deflection_mm'];h=a['cam_rise_mm'];T=a['nominal_release_N']*27.15
alpha=b.cam_angle(p)
data={'scope':'Exact nominal CAD intersection screening of cam lofts only, not a contact-force model.',
 'cam_rows':rows,'spring_stiffness_N_per_mm_ideal_fixed_guided':k,
 'preload_N':k*d,'full_lift_spring_force_N':k*(d+h),
 'preload_surface_strain':3*a['spring_thickness_mm']*d/a['spring_leaf_length_mm']**2,
 'full_lift_surface_strain':3*a['spring_thickness_mm']*(d+h)/a['spring_leaf_length_mm']**2,
 'ramp_angle_deg':math.degrees(alpha),'target_torque_Nmm':T,
 'energy_to_lift_Nmm':k*d*h+.5*k*h*h,
 'axial_force_at_end_of_ideal_ramp_N':T/(27.15*(math.cos(alpha)+math.sin(alpha))),
 'downward_force_at_end_of_ideal_ramp_N':T/(27.15*(math.cos(alpha)-math.sin(alpha))),
 'equal_downward_axial_diagonal_resultant_at_initial_release_N':50/math.sqrt(2)}
(R/'independent_cam_cad_results.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({k:v for k,v in data.items() if k!='cam_rows'},indent=2))
