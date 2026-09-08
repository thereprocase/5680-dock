"""Compact-depth sensitivity and CAD passage screen; not CFD or a fan solve."""
from pathlib import Path
import math,json
import numpy as np
import build
R=Path(__file__).resolve().parent
rho=1.2;cfm=.00047194745;E=build.ELEV;L=math.radians(build.LEAN)
radius=56.5
def lid_y(z):return build.T/2/math.cos(L)+(z-build.H)*math.tan(L)
def section_row(fy):
    top_z=build.FAN_Z+60*math.cos(E)-7.5*math.sin(E)
    top_y=fy-60*math.sin(E)-7.5*math.cos(E)
    top_gap=(top_y-lid_y(top_z))*math.cos(L)
    # Horizontal feeder sections above the lower turn, with a uniform loading
    # assumption on the fan disk. Flow remaining above each section equals the
    # circular segment fraction, not the full branch flow at every height.
    velocities=[]
    for z in np.linspace(66,128,125):
        back=build.rest_y(z)+2.4
        front=build.front_y(z,True)+fy-build.FAN_Y
        v=(z-build.FAN_Z+7.5*math.sin(E))/math.cos(E)
        segment=0 if v>=radius else math.pi*radius**2 if v<=-radius else radius**2*math.acos(v/radius)-v*math.sqrt(radius**2-v*v)
        flow=15*cfm*segment/(math.pi*radius**2)
        velocities.append(flow/(119.2*(front-back)*1e-6) if front>back else 999.)
    min_ray=999
    for v in [-54,-35,0,35,54]:
        z=build.FAN_Z+v*math.cos(E)-7.5*math.sin(E)
        y=fy-v*math.sin(E)-7.5*math.cos(E)
        d=(y-build.rest_y(z)-2.4)/(math.cos(E)-math.tan(L)*math.sin(E))-3.1
        min_ray=min(min_ray,d)
    return dict(fan_center_y_mm=fy,top_suction_face_to_lid_normal_mm=top_gap,upper_feed_velocity_at_30cfm_m_s=max(velocities),analytical_upper_wall_ray_clearance_mm=min_ray,meets_screen=bool(top_gap>=12 and min_ray>=12 and max(velocities)<=2.0))
sweep=[section_row(y) for y in [95,70,64,60,58,56,54,52,50]]
plenums=[]
for i,(void,fx) in enumerate(zip(build.flow_voids,build.p['fan_centers_x'])):
    assert len(void.Solids())==1 and void.isValid()
    section=void.intersect(build.box(-100,15,0,700,.05,200).val()).Volume()/.05
    rays=[]
    for r in [0,20,35,45,50,54]:
        for phi in np.linspace(0,2*math.pi,16,endpoint=False) if r else [0]:
            u=r*math.cos(phi);v=r*math.sin(phi)
            start=np.array([fx+u,build.FAN_Y-v*math.sin(E)-7.5*math.cos(E),build.FAN_Z+v*math.cos(E)-7.5*math.sin(E)])
            inward=np.array([0,-math.cos(E),-math.sin(E)])
            inside=[]
            for distance in np.arange(3.1,150,.5):
                if void.isInside(tuple(start+distance*inward)):inside.append(float(distance))
                elif inside:break
            assert inside,(i,r,phi)
            rays.append(inside[-1]-inside[0]+.5)
    plenums.append(dict(module=i+1,volume_litres=void.Volume()/1e6,transfer_section_mm2=section,minimum_sampled_fan_normal_clearance_mm=min(rays),fan_axis_clearance_mm=rays[0],ray_sample_count=len(rays)))
fan_area=(math.pi*(radius**2-17**2)-4*4.4*(radius-17))*1e-6
flows=[]
for total in [20,30,40]:
    q=total*cfm/2;branches=[]
    for m,pl in zip(build.mouth_records,plenums):
        vm=q/(m['area_mm2']*1e-6);vt=q/(pl['transfer_section_mm2']*1e-6);vf=q/fan_area
        qm=.5*rho*vm*vm;qt=.5*rho*vt*vt;qf=.5*rho*vf*vf
        branches.append(dict(mouth_velocity_m_s=vm,transfer_velocity_m_s=vt,baseline_loss_sensitivity_Pa=[.6*qm+.5*qt+1.2*qf,1.5*qm+1.5*qt+1.8*qf]))
    flows.append(dict(assumed_total_cfm=total,branches=branches))
chosen=section_row(build.FAN_Y)
assert chosen['meets_screen'],chosen
assert min(p['minimum_sampled_fan_normal_clearance_mm'] for p in plenums)>=12
data=dict(assumed_total_design_cfm=30,assumed_equal_branch_split=True,laptop_lean_deg=build.LEAN,fan_discharge_deg=math.degrees(E),selected=chosen,depth_sweep=sweep,plenums=plenums,flow_cases=flows,screen_rule='Engineering screening allowances, not measured limits: >=12 mm lid/top gap and upper wall clearance; <=2 m/s upper feeder speed at assumed 30 CFM. CAD ray clearance checked separately.',limitations='Uniform disk loading is an assumption. Baseline loss coefficients are inherited sensitivity assumptions, NOT a reliable bound on close-inlet system effect. Laptop resistance, inlet distortion, stall, bypass leakage and noise are unmodeled. No P-Q curve intersection or thermal claim. The final minimum usable depth requires prototype flow/pressure/noise measurements.',fan_example=dict(model='Noctua NF-A12x15 PWM',free_air_max_cfm=55.44,shutoff_pressure_Pa=1.53*9.80665,source='https://www.noctua.at/en/products/nf-a12x15-pwm/specifications',note='Separate endpoints; parallel fans do not double pressure. Example fan, not a verified installed fan.'))
(R/'airflow-sizing.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(dict(selected=chosen,sweep=sweep,plenums=plenums,flow_cases=flows),indent=2),flush=True)
