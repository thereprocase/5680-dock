"""Geometry-led duct sizing and bounded loss estimates; not CFD or a fan solve."""
from pathlib import Path
import math,json
import numpy as np
import build
R=Path(__file__).resolve().parent
rho=1.2;cfm=0.00047194745
areas=[m['area_mm2']*1e-6 for m in build.mouth_records]
# Screen each separate branch: a total area alone can conceal the smaller inlet.
plenums=[]
for i,(void,fx) in enumerate(zip(build.flow_voids,build.p['fan_centers_x'])):
 solid=void.Solids()[0]
 assert len(void.Solids())==1 and solid.isValid()
 # Normal to +Y at the start of the broad under-hinge transfer passage.
 slab=build.box(-100,15,0,700,.05,200).val()
 section=void.intersect(slab).Volume()/.05
 # Normal ray clearance from fan suction plane to rear/ceiling/floor walls.
 rays=[]
 angle=math.radians(build.ANGLE)
 for r in [0,20,35,45,50,54]:
  for phi in np.linspace(0,2*math.pi,16,endpoint=False) if r else [0]:
   u=r*math.cos(phi);v=r*math.sin(phi)
   start=np.array([build.W-fx-u,build.FAN_Y+v*math.cos(angle)-7.5*math.sin(angle),build.FAN_Z+v*math.sin(angle)+7.5*math.cos(angle)])
   inward=np.array([0,-math.cos(build.ELEV),-math.sin(build.ELEV)])
   inside=[]
   for d in np.arange(3.1,150,.5):
    if solid.isInside(tuple(start+d*inward)):inside.append(float(d))
    elif inside:break
   assert inside,(i,r,phi)
   rays.append({'radius_mm':r,'angle_deg':math.degrees(phi),'clear_depth_mm':inside[-1]-inside[0]+.5})
 plenums.append({'module':i+1,'volume_litres':void.Volume()/1e6,'transfer_section_mm2':section,'fan_ray_min_clear_mm':min(a['clear_depth_mm'] for a in rays),'fan_axis_clear_mm':rays[0]['clear_depth_mm'],'ray_sample_count':len(rays)})
# Guard area projected onto the fan plane. Ring sits outside the 113 mm aperture.
r=56.5
def integral(y):return y*math.sqrt(r*r-y*y)+r*r*math.asin(y/r)
blocked=sum(integral(off+.5)-integral(off-.5) for off in range(-54,55,9))
guard_free=1-blocked/(math.pi*r*r)
fan_area=(math.pi*(56.5**2-17**2)-4*4.4*(56.5-17))*1e-6
rows=[]
for total in build.p['flow_checks_cfm']:
 q=total*cfm/2
 branches=[]
 for a,plenum in zip(areas,plenums):
  v=q/a;vp=rho*v*v/2
  vt=q/(plenum['transfer_section_mm2']*1e-6);vpt=rho*vt*vt/2
  vf=q/fan_area;vpf=rho*vf*vf/2
  # Engineering sensitivity bounds, referenced to local velocity pressure.
  # Entrance .2-.5; turning/mixing .5-1.5; slot-jet mixing / roughness allowance .4-1.0;
  # inlet/discharge/guard combined 1.2-1.8 at the rotor free area.
  low=.2*vp+.5*vpt+.4*vp+1.2*vpf
  high=.5*vp+1.5*vpt+1.0*vp+1.8*vpf
  branches.append({'mouth_velocity_m_s':v,'mouth_velocity_pressure_Pa':vp,'transfer_velocity_m_s':vt,'fan_free_area_velocity_m_s':vf,'external_duct_loss_estimate_Pa':[low,high]})
 rows.append({'assumed_total_CFM':total,'assumed_branch_CFM':total/2,'branches':branches})
data={'design_basis':'30 CFM total, assumed equal fan split; 20/40 CFM sensitivity. This does not predict actual flow.','density_kg_m3':rho,'mouths':build.mouth_records,'mouth_total_mm2':sum(areas)*1e6,'plenums':plenums,'guard_projected_open_fraction':guard_free,'flow_cases':rows,'fan_static_pressure_endpoint_Pa':1.53*9.80665,'limitations':'Loss-coefficient bounds are engineering assumptions, not calibrated coefficients for this geometry. Excludes the laptop grille/heatsink/blowers, seal leakage and unsteady acoustic effects. No measured P-Q curve/system intersection, CFD, whistle guarantee, or thermal claim.'}
(R/'airflow-sizing.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data,indent=2),flush=True)
