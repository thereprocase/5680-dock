"""Eccentrically loaded hollow-beam sizing, N/mm/MPa. Not whole-dock FEA."""
from pathlib import Path
import itertools,json,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent
p=json.loads((R.parent/'parameters.json').read_text())
P=p['rear_case_seat_z']+p['port_from_rear_case']
L=p['plug_arm']['root_x_mm']-p['plug_arm']['free_end_x_mm']
NU=.38

def section(b,h,t):
    bi,hi=b-2*t,h-2*t
    assert min(bi,hi)>0
    A=b*h-bi*hi
    Iy=(b*h**3-bi*hi**3)/12
    Iz=(h*b**3-hi*bi**3)/12
    # Closed thin-wall torsion estimate, reduced 25% for its approximation.
    bm,hm=b-t,h-t
    J=.75*4*(bm*hm)**2/(2*(bm+hm)/t)
    return A,Iy,Iz,J

def compliance(b,h,t,E):
    A,Iy,Iz,J=section(b,h,t);G=E/(2*(1+NU))
    C=np.zeros((6,6))
    C[0,0]=L/(E*A)
    C[1,1]=L**3/(3*E*Iz)+L/(.5*G*A)
    C[2,2]=L**3/(3*E*Iy)+L/(.5*G*A)
    C[3,3]=L/(G*J)
    C[4,4]=L/(E*Iy); C[5,5]=L/(E*Iz)
    C[1,5]=C[5,1]=L**2/(2*E*Iz)
    C[2,4]=C[4,2]=-L**2/(2*E*Iy)
    assert np.all(np.linalg.eigvalsh(C)>0)
    return C

def evaluate(b,h,t,E=800,F=20,dx=0,dy=0,dz=0,force_axis=0):
    # Beam axes: u=-X, v=+Y, w=-Z, a right-handed frame.
    cy=p['plug_arm']['near_y_mm']+b/2;cz=P-18.7-h/2
    r=np.array([-(5.15+dx+40),p['port_y']+dy-cy,-(P+dz-cz)])
    load=np.zeros(3);load[force_axis]=F
    wrench=np.r_[load,np.cross(r,load)]
    q=compliance(b,h,t,E)@wrench
    remote=q[:3]+np.cross(q[3:],r)
    A,Iy,Iz,J=section(b,h,t)
    normal_bound=abs(load[0])/A+abs(wrench[4])*(h/2)/Iy+abs(wrench[5])*(b/2)/Iz
    return dict(displacement_local_mm=remote.tolist(),axial_deflection_mm=abs(remote[0]),
        resultant_deflection_mm=float(np.linalg.norm(remote)),
        beam_tip_rotation_deg=np.degrees(q[3:]).tolist(),
        plug_axis_tilt_deg=float(np.degrees(np.linalg.norm(q[4:]))),
        nominal_normal_stress_bound_MPa=normal_bound,
        adjustment_mm=[dx,dy,dz])

settings=[(0,0,0)]+list(itertools.product(p['depth_range'],p['lateral_range'],p['height_range']))
grid=[]
for b,h,t in itertools.product([12,14,16,18,20,24],range(24,49,2),[2.4,3.2,4,4.8]):
    cases=[evaluate(b,h,t,dx=x,dy=y,dz=z) for x,y,z in settings]
    worst=max(cases,key=lambda q:q['axial_deflection_mm'])
    grid.append(dict(width_mm=b,depth_mm=h,wall_mm=t,volume_cm3=section(b,h,t)[0]*L/1000,
        worst_axial_mm=worst['axial_deflection_mm'],worst_tilt_deg=max(c['plug_axis_tilt_deg'] for c in cases),
        passes_member_target=bool(worst['axial_deflection_mm']<=.12 and max(c['plug_axis_tilt_deg'] for c in cases)<=.25)))
feasible=sorted((q for q in grid if q['passes_member_target']),key=lambda q:q['volume_cm3'])
chosen=tuple(p['plug_arm'][k] for k in ['width_y_mm','depth_z_mm','wall_mm'])
cases=[]
for E,F in itertools.product([800,1200,1500,1800],[20,40]):
    poses=[evaluate(*chosen,E=E,F=F,dx=x,dy=y,dz=z) for x,y,z in settings]
    cases.append(dict(E_MPa=E,load_N=F,nominal=poses[0],worst=max(poses,key=lambda c:c['axial_deflection_mm'])))
sidecases=[dict(axis=axis,load_N=5,pose=evaluate(*chosen,E=800,F=5,force_axis=axis)) for axis in [1,2]]
A,Iy,Iz,J=section(*chosen)
worst=cases[0]['worst']['axial_deflection_mm']
data=dict(scope='Linear isotropic member sizing with fully fixed root and rigid cassette transfer. Not FEA, measured deflection, complete assembly stiffness, or a thermal/creep model.',
    load_basis='20 N provisional insertion/extraction case informed by USB-IF R2.5 and Molex; docking excluded from those force requirements. 40 N is an independently chosen sensitivity case.',
    target_total_axial_mm_at_20N=.20,member_target_mm=.12,
    chosen=dict(width_y_mm=chosen[0],depth_z_mm=chosen[1],wall_mm=chosen[2],length_x_mm=L,root_x_mm=p['plug_arm']['root_x_mm'],free_end_x_mm=-40,
        area_mm2=A,I_y_mm4=Iy,I_z_mm4=Iz,J_torsion_screen_mm4=J,beam_material_cm3=A*L/1000),
    smallest_screened_section=feasible[0],feasible_count=len(feasible),sweep=grid,cases=cases,side_load_screens=sidecases,
    residual_movement_budget_mm=.20-worst,required_residual_assembly_stiffness_N_per_mm=20/(.20-worst),
    model_boundary='Actual root collar, deck/tower flexibility, cassette and shelf deformation, hinge, spring/cam contacts, printed fastener slip and contact clearances are excluded. Their combined movement must fit the residual budget. Section assumes dense PETG walls; sparse infill is not credited. Corner radii, anisotropy and stress concentrations are not resolved.')
(R/'arm-stiffness.json').write_text(json.dumps(data,indent=2)+'\n')
fig,ax=plt.subplots(figsize=(8,4.6),layout='constrained')
for E in [800,1200,1500,1800]:
    fs=np.linspace(0,40,81)
    ds=[evaluate(*chosen,E=E,F=f,dy=p['lateral_range'][0],dz=p['height_range'][1])['axial_deflection_mm'] for f in fs]
    ax.plot(fs,ds,label=f'Assumed E = {E/1000:g} GPa')
ax.axhline(.20,color='#333333',ls='--',label='Whole-holder target (includes joints)')
ax.axvline(20,color='#aaaaaa',lw=1)
ax.set(xlabel='Axial load (N)',ylabel='Calculated brace deflection at plug (mm)',title=f'{chosen[0]:g} x {chosen[1]:g} mm hollow brace | {chosen[2]:g} mm walls | {L:g} mm span')
ax.grid(alpha=.2);ax.legend(fontsize=8);fig.savefig(R/'arm-stiffness.png',dpi=180);plt.close(fig)
print(json.dumps({k:data[k] for k in ['chosen','smallest_screened_section','residual_movement_budget_mm','required_residual_assembly_stiffness_N_per_mm']},indent=2))
print('20 N cases:',[(c['E_MPa'],round(c['nominal']['axial_deflection_mm'],4),round(c['worst']['axial_deflection_mm'],4)) for c in cases if c['load_N']==20])
