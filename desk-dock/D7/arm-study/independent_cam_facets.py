"""Read-only ruled-loft height and fixed-guided spring audit; no CAD rebuild."""
from pathlib import Path
import math,json,hashlib
import numpy as np
R=Path(__file__).resolve().parent
p=json.loads((R.parent/'parameters.json').read_text());a=p['breakaway']
k=2*a['nominal_E_MPa']*a['spring_width_mm']*a['spring_thickness_mm']**3/a['spring_leaf_length_mm']**3
d=a['spring_preload_deflection_mm'];h=a['cam_rise_mm'];lever=27.15;T=a['nominal_release_N']*lever
alpha=(k*d*h+.5*k*h*h)/T
def smooth(q):return min(h,math.sqrt(d*d+2*T*abs(q)/k)-d)
def ruled(q):
    if q>=alpha:return h,0.
    q=max(q,0);j=min(11,int(q/(alpha/12)));qa=alpha*j/12;qb=alpha*(j+1)/12
    sa,sb=math.sin(q-qa),math.sin(qb-q);dy=smooth(qb)-smooth(qa)
    # Polar-ray intersection with the actual straight chord between loft wires.
    return smooth(qa)+dy*sa/(sa+sb),dy*math.sin(qb-qa)/(sa+sb)**2
rows=[]
for j in range(12):
    for q in [alpha*j/12+1e-10,alpha*(j+.5)/12,alpha*(j+1)/12-1e-10]:
        lift,slope=ruled(q);torque=k*(d+lift)*slope
        rows.append(dict(facet=j+1,angle_deg=math.degrees(q),lift_mm=lift,
          lift_derivative_mm_per_rad=slope,torque_Nmm=torque,
          negative_X_force_N=torque/(lever*(math.cos(q)+math.sin(q))),
          negative_Z_force_N=torque/(lever*(math.cos(q)-math.sin(q)))))
diff=[ruled(q)[0]-smooth(q) for q in np.linspace(0,alpha-1e-10,5001)]
def bounds(key):return [min(r[key] for r in rows),max(r[key] for r in rows)]
poses=[]
for deg in [0,math.degrees(alpha),10,30,45]:
    q=math.radians(deg)
    poses.append(dict(angle_deg=deg,tip_delta_xz_mm=[lever*(math.cos(q)-math.sin(q)-1),lever*(1-math.sin(q)-math.cos(q))],carrier_delta_y_mm=-smooth(q)))
rail_k=4*(3*a['nominal_E_MPa']*(14*11**3/12)/38**3)
data=dict(scope='Ruled-loft axial height after female radial relief; not proof of radial CAD clearance, contact stiffness, friction, preload, manufactured fit, creep, strength or impact response.',
    source_sha256=hashlib.sha256((R.parent/'breakaway_geometry.py').read_bytes()).hexdigest(),
    ideal_leaf_k_N_per_mm=k,preload_N=k*d,full_lift_spring_force_N=k*(d+h),
    preload_surface_strain=3*a['spring_thickness_mm']*d/a['spring_leaf_length_mm']**2,
    full_lift_surface_strain=3*a['spring_thickness_mm']*(d+h)/a['spring_leaf_length_mm']**2,
    ramp_angle_deg=math.degrees(alpha),target_torque_Nmm=T,cam_lift_energy_Nmm=k*d*h+.5*k*h*h,
    ruled_minus_smooth_lift_range_mm=[min(diff),max(diff)],
    facet_derivative_range_mm_per_rad=bounds('lift_derivative_mm_per_rad'),
    frictionless_facet_torque_range_Nmm=bounds('torque_Nmm'),
    negative_X_force_range_N=bounds('negative_X_force_N'),negative_Z_force_range_N=bounds('negative_Z_force_N'),
    nominal_equal_diagonal_resultant_release_N=a['nominal_release_N']/math.sqrt(2),
    radial_chord_error_r24_2p5deg_crown_mm=24*(1-math.cos(math.radians(1.25))),
    frame_sensitivity=dict(assumption='Four 38 mm rail cantilevers, not a calibrated frame model.',
       frame_stiffness_N_per_mm=rail_k,series_cartridge_stiffness_N_per_mm=1/(1/k+1/rail_k)),
    tip_release_path=poses,facets=rows)
(R/'independent_cam_results.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({key:value for key,value in data.items() if key!='facets'},indent=2))
