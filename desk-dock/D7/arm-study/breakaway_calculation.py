import json,math,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(r'D:\Code\Modeling\dell-5560-wall-mount\desk-dock\D7');sys.path.insert(0,str(r))
import breakaway_geometry as g
p=json.loads((r/'parameters.json').read_text());a=p['breakaway'];L=a['spring_leaf_length_mm'];b=a['spring_width_mm'];t=a['spring_thickness_mm'];d=a['spring_preload_deflection_mm'];h=a['cam_rise_mm'];E=a['nominal_E_MPa'];k=2*E*b*t**3/L**3;T=50*27.15
rows=[]
for modulus in [800,1200,1500,1800]:
 for mu in [0,.1,.2]:
  forces=[]
  for u in np.linspace(0,h,61):
   nominalP=k*(d+u);actualP=nominalP*modulus/E;slope=T/(20*nominalP)
   torque=actualP*20*(slope+mu)/(1-mu*slope)
   forces.append(torque/27.15)
  rows.append(dict(E_MPa=modulus,assumed_friction=mu,initial_release_N=forces[0],maximum_over_ramp_N=max(forces)))
data=dict(scope='Ideal spring and face-cam energy calculation, not measured PETG mechanism or impact simulation.',load_basis='USB-IF R2.5 normal insertion5–20N;50N chosen user target for misaligned docking impact, no standard establishes this limit.',spring=dict(type='two fixed-guided beams plus assumed rigid island and frame',leaf_length_mm=L,width_mm=b,thickness_mm=t,nominal_E_MPa=E,stiffness_N_per_mm=k,assembled_preload_deflection_mm=d,preload_N=k*d,maximum_deflection_mm=d+h,maximum_force_N=k*(d+h),preload_surface_strain=3*t*d/L**2,maximum_surface_strain=3*t*(d+h)/L**2),cam=dict(mean_radius_mm=20,rise_mm=h,angular_ramp_deg=math.degrees(g.cam_angle(p)),stored_energy_increment_J=(k*d*h+.5*k*h*h)/1000,ideal_release_torque_Nmm=T,axial_or_downward_lever_mm=27.15,normal20N_torque_Nmm=20*27.15,ideal_axial_release_N=50,ideal_downward_release_N=50,ideal_45deg_combined_release_resultant_N=50/math.sqrt(2),lateral_release='No calibrated lateral-Y release. Do not claim omnidirectional protection.'),sensitivity=rows,qualification='Use detached dummy-plug test fixture, not laptop, for load calibration. Verify <=0.20mm axial movement at20N, reset repeatability, 50N-class axial/downward release, warm dwell and repeated resets. Impact peak may exceed static release; cable slack and stop travel matter. Tuning preload changes force profile; fit and print orientation need qualification.')
(r/'arm-study'/'breakaway-calculation.json').write_text(json.dumps(data,indent=2)+'\n')
fig,axs=plt.subplots(1,2,figsize=(11,4.2),layout='constrained')
x=np.linspace(0,h,80);angle=np.degrees((k*d*x+.5*k*x*x)/T)
for mu in [0,.1,.2]:
 P=k*(d+x);slope=T/(20*P);force=P*20*(slope+mu)/(1-mu*slope)/27.15
 axs[0].plot(angle,force,label=f'Assumed friction = {mu:g}')
axs[0].axhline(20,c='#6b7872',ls='--',label='Normal insertion scenario')
axs[0].set(xlabel='Cam travel (degrees)',ylabel='Equivalent axial tip force (N)',title='Release ramp: ideal model at E = 1.2 GPa');axs[0].legend(fontsize=8);axs[0].grid(alpha=.2)
px,pz=g.datum(p)
theta=np.radians(np.linspace(0,45,91));X=px+27.15*np.cos(theta)-27.15*np.sin(theta);Z=pz-27.15*np.sin(theta)-27.15*np.cos(theta)
axs[1].plot(X,Z,c='#477369');axs[1].scatter([X[0],X[-1]],[Z[0],Z[-1]],c=['#2b5c50','#a57338']);axs[1].annotate('Ready',(X[0],Z[0]),xytext=(5,5),textcoords='offset points');axs[1].annotate('Folded 45°',(X[-1],Z[-1]),xytext=(-10,12),textcoords='offset points');axs[1].set(xlabel='Plug tip X (mm)',ylabel='Plug tip height (mm)',title='Misaligned-docking retreat in laptop frame');axs[1].axis('equal');axs[1].grid(alpha=.2)
fig.savefig(r/'arm-study'/'breakaway-study.png',dpi=180)
print(json.dumps(data,indent=2))
