"""Independent small-displacement screening of D7's open connector bracket.

This is a sensitivity model, not a load qualification. The shell-wall boundary
is an optimistic idealization. Source CAD and printed PETG are not modified.
"""
from pathlib import Path
import json,math
import numpy as np

R=Path(__file__).resolve().parent
p=json.loads((R.parent/'parameters.json').read_text())
P=p['rear_case_seat_z']+p['port_from_rear_case']
F=20.0; nu=.38
base_z=29.85; shelf_z=P-21.35
L=shelf_z-base_z; h=P-shelf_z; root_span=31.2
ey=p['port_y']-21.5


def rectangle_J(a,b):
    a,b=max(a,b),min(a,b)
    return a*b**3*(1/3-.21*(b/a)*(1-b**4/(12*a**4)))


def frame(E,braced=False,brace_band=8):
    # Coordinates are X,Z in the cassette's unleaned frame. A and D represent
    # two wall attachment elevations, not proven fixed points on the real dock.
    xy=np.array([[-5.8,base_z],[-37,base_z],[-37,shelf_z],[-5.8,47.6]])
    if braced:
        # Full-width 6x43 back spine, full-width 43x6.3 bottom tie, and two
        # 4 mm cheeks represented only by their 8 mm-wide diagonal load bands.
        members=[(0,1,43*6.3,43*6.3**3/12),
                 (1,2,6*43,43*6**3/12),
                 (2,3,2*4*brace_band,(2*4)*brace_band**3/12)]
    else:
        members=[(0,1,7*6.3,7*6.3**3/12),(1,2,6*7,7*6**3/12)]
    K=np.zeros((12,12)); records=[]
    for a,b,A,I in members:
        d=xy[b]-xy[a];ell=float(np.linalg.norm(d));c,s=d/ell
        k=np.array([[A/ell,0,0,-A/ell,0,0],
          [0,12*I/ell**3,6*I/ell**2,0,-12*I/ell**3,6*I/ell**2],
          [0,6*I/ell**2,4*I/ell,0,-6*I/ell**2,2*I/ell],
          [-A/ell,0,0,A/ell,0,0],
          [0,-12*I/ell**3,-6*I/ell**2,0,12*I/ell**3,-6*I/ell**2],
          [0,6*I/ell**2,2*I/ell,0,-6*I/ell**2,4*I/ell]])*E
        T=np.array([[c,s,0,0,0,0],[-s,c,0,0,0,0],[0,0,1,0,0,0],
                    [0,0,0,c,s,0],[0,0,0,-s,c,0],[0,0,0,0,0,1]])
        idx=[3*a+i for i in range(3)]+[3*b+i for i in range(3)]
        K[np.ix_(idx,idx)]+=T.T@k@T
        records.append((a,b,A,I,ell,idx,k,T))
    load=np.zeros(12);load[6]=F;load[8]=-F*h
    free=list(range(3,9));u=np.zeros(12)
    u[free]=np.linalg.solve(K[np.ix_(free,free)],load[free])
    result={'port_axial_deflection_mm':float(u[6]-h*u[8]),
            'shelf_rotation_deg':float(math.degrees(u[8])),
            'shelf_center_displacement_xz_mm':[float(u[6]),float(u[7])],
            'member_local_end_forces':[]}
    for a,b,A,I,ell,idx,k,T in records:
        end=k@T@u[idx]
        result['member_local_end_forces'].append({'nodes':[a,b],'length_mm':ell,
          'area_mm2':A,'in_plane_I_mm4':I,'N_V_M_end_values':[float(v) for v in end]})
    return result


rows=[]
for E in [800,1200,1800]:
    G=E/(2*(1+nu));Iy=7*6**3/12; J=rectangle_J(7,6)
    spine_bending=F/(E*Iy)*(L**3/3+h*L**2+h*h*L)
    spine_torsion=F*ey**2*L/(G*J)
    total_h=P-base_z
    bottom_bending=F*total_h**2*root_span/(E*(7*6.3**3/12))
    bottom_lateral=F*ey**2*root_span/(E*(6.3*7**3/12))
    bottom_axial=F*root_span/(E*(7*6.3))
    baseline=frame(E)
    assert abs(baseline['port_axial_deflection_mm']-(spine_bending+bottom_bending+bottom_axial))<1e-6
    rows.append({'E_MPa_assumed':E,'G_MPa_derived_assumed_nu_0p38':G,
      'current_spine_bending_mm':spine_bending,
      'current_spine_eccentric_torsion_mm':spine_torsion,
      'current_return_vertical_bending_mm':bottom_bending,
      'current_return_lateral_bending_mm':bottom_lateral,
      'current_return_axial_mm':bottom_axial,
      'current_member_sum_mm':spine_bending+spine_torsion+bottom_bending+bottom_lateral+bottom_axial,
      'current_2D_frame_check':baseline,
      'candidate_2D_braced_frame':frame(E,True),
      'candidate_2D_braced_frame_16mm_load_band':frame(E,True,16),
      'shelf_cantilever_23mm_full_width_optimistic_mm':F*h*h*23/(E*(43*5.3**3/12)),
      'shelf_torsion_full_width_optimistic_mm':F*h*h*abs(ey)/(G*rectangle_J(39.4,5.3)),
      'shelf_torsion_6mm_effective_width_sensitivity_mm':F*h*h*abs(ey)/(G*rectangle_J(6,5.3))})

result={'scope':'Linear elastic, small-displacement isotropic sensitivity only. Current large predicted '
                'rotations violate this model; values flag insufficiency, not realistic displacement. '
                'Neither shell fixity nor printed modulus, strength, creep, bolt preload or friction is verified.',
        'force_N':F,'assumed_moduli_MPa':[800,1200,1800],'assumed_poisson_ratio':nu,
        'dimensions_mm':{'spine_cross_section':[6,7],'spine_centerline_length':L,
                         'return_cross_section':[7,6.3],'return_to_shell_centerline_span':root_span,
                         'port_above_shelf':h,'port_y_minus_spine_y':ey,
                         'shelf_nominal_dimensions':[39.4,43,5.3],
                         'wall_attachment_x_bounds':[-7,-4.6]},
        'rows':rows,
        'current_spine_linear_base_bending_stress_MPa':F*(P-base_z)*3/(7*6**3/12),
        'current_return_linear_bending_stress_MPa':F*(P-base_z)*3.15/(7*6.3**3/12),
        'root_rotation_stiffness_needed_Nmm_per_rad_for_0p1mm_budget':F*(P-base_z)**2/.1,
        'root_translation_stiffness_needed_N_per_mm_for_0p1mm_budget':F/.1,
        'cassette_friction_sensitivity':{'mu_assumed':[.15,.2,.3],
          'minimum_total_preload_for_axial_F_only_N':[F/mu for mu in [.15,.2,.3]],
          'max_bolt_group_axial_share_N':F/2+F*abs(p['port_y'])/16,
          'shelf_interface_overturning_moment_Nmm':F*18.7,
          'clamp_interface_overturning_moment_Nmm':F*13.7}}
(R/'independent_arm_results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['dimensions_mm','current_spine_linear_base_bending_stress_MPa',
 'current_return_linear_bending_stress_MPa','root_rotation_stiffness_needed_Nmm_per_rad_for_0p1mm_budget']},indent=2))
for row in rows:
    print('E',row['E_MPa_assumed'],'member_sum',round(row['current_member_sum_mm'],3),
          'braced_in_plane',round(row['candidate_2D_braced_frame']['port_axial_deflection_mm'],3),
          'shelf_full_width',round(row['shelf_torsion_full_width_optimistic_mm'],3))
