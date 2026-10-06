from pathlib import Path
p=Path('build_d9.py');t=p.read_text()
def rep(a,b):
    global t
    assert a in t,('MISSING',a[:90]);t=t.replace(a,b)
s=t.index("def _solve_pose(py,pz):");e=t.index("assert all(v['within_travel'] for v in REACH['ports'].values()),'Plug pocket cannot be placed on every USB-C port'")
new='''def _rot(v,deg):
    a=math.radians(deg);return (v[0]*math.cos(a)-v[1]*math.sin(a),v[0]*math.sin(a)+v[1]*math.cos(a))
def _solve_pose(py,pz,roll):
    """Arm angle (deg, +toward -Y) and tip radius that put the clamped plug axis on (py,pz).
    The rotor is trimmed about the tip by psi = -(phi+LEAN)-roll so the carrier window is
    square to the port; the pocket offset from the tip therefore rotates with phi. With
    roll=None the rotor is left at neutral."""
    d=(py-BY,pz-BZ)
    def resid(phi):
        psi=0.0 if roll is None else -(phi+LEAN)-roll
        v=_rot((-PAD_LAT,-PAD_RAD),psi);w=_rot(d,-phi)          # (lateral, radial) the tip-relative axis must equal, in the arm frame
        return w[0]-v[0],w[1]-v[1]
    lo,hi=-30.0,90.0;flo=resid(lo)[0]
    for _ in range(80):
        mid=(lo+hi)/2;fm=resid(mid)[0]
        if (fm>0)==(flo>0):lo,flo=mid,fm
        else:hi=mid
    phi=(lo+hi)/2;R=resid(phi)[1]
    psi=0.0 if roll is None else -(phi+LEAN)-roll
    v=_rot((-PAD_LAT,-PAD_RAD),psi);chk=_rot((v[0],R+v[1]),phi)
    assert abs(chk[0]-d[0])<1e-6 and abs(chk[1]-d[1])<1e-6,(chk,d)
    return phi,R,psi
# pre-roll the window to the mean working arm angle plus the lean, iterating because the
# working angles themselves move slightly with the trim
POCKET_ROLL=None
for _it in range(3):
    _sol={tag:_solve_pose(py,pz,POCKET_ROLL) for tag,(py,pz) in PORTS.items()}
    POCKET_ROLL=-(sum(s[0] for s in _sol.values())/len(_sol)+LEAN)
REACH['ports']={}
for _tag,(_py,_pz) in PORTS.items():
    _phi,_R,_psi=_sol[_tag]
    _ok=TIP_MIN<=BZ+_R<=TIP_MAX
    REACH['ports'][_tag]={'leaned_yz_mm':[round(_py,3),round(_pz,3)],'radius_from_pivot_mm':round(math.hypot(_py-BY,_pz-BZ),2),
                          'arm_angle_deg':round(_phi,2),'tip_radius_mm':round(_R,2),'rotor_trim_deg':round(_psi,2),
                          'within_travel':_ok,'margin_to_travel_limits_mm':[round(BZ+_R-TIP_MIN,2),round(TIP_MAX-(BZ+_R),2)]}
    print('Port reach',_tag,json.dumps(REACH['ports'][_tag]),flush=True)
'''
t=t[:s]+new+t[e:]
rep("POCKET_ROLL=-(sum(v['arm_angle_deg'] for v in REACH['ports'].values())/len(REACH['ports'])+LEAN)\ntip_eye=","tip_eye=")
# cam target: corners rotate with the trim
rep('''def _pocket_corners(R):
    """Pocket window corners in the arm frame (lateral, radial from the pivot) for tip radius R."""
    c=(-PAD_LAT,R-PAD_RAD);a=math.radians(POCKET_ROLL);out=[]
    for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1)):
        u,v=sx*POCKET_W/2,sy*POCKET_H/2
        out.append((c[0]+u*math.cos(a)-v*math.sin(a),c[1]+u*math.sin(a)+v*math.cos(a)))
    return out
def _cam_target(R):
    """Radius the spiral must have under the pocket, and the pocket's angle from the arm line."""
    lo=min(_pocket_corners(R),key=lambda p:math.hypot(*p))
    return math.hypot(*lo)-CAM_GAP,math.degrees(math.atan2(-lo[0],lo[1]))
def _cam_rotation(phi,R):
    """Cam rotation (deg, same sense as the arm) placing the spiral point of the needed radius at the pocket angle."""
    r_need,alpha=_cam_target(R)''',
'''def _pocket_corners(R,psi=0.0):
    """Window corners in the arm frame (lateral, radial from the pivot) for tip radius R and rotor trim psi."""
    cw=_rot((_pc[0]-tip_y,_pc[1]-tip_z),psi);c=(cw[0],R+cw[1]);a=math.radians(POCKET_ROLL+psi);out=[]
    for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1)):
        u,v=sx*POCKET_W/2,sy*POCKET_H/2
        out.append((c[0]+u*math.cos(a)-v*math.sin(a),c[1]+u*math.sin(a)+v*math.cos(a)))
    return out
def _cam_target(R,psi=0.0):
    """Radius the spiral must have under the window, and the window's angle from the arm line."""
    lo=min(_pocket_corners(R,psi),key=lambda p:math.hypot(*p))
    return math.hypot(*lo)-CAM_GAP,math.degrees(math.atan2(-lo[0],lo[1]))
def _cam_rotation(phi,R,psi=0.0):
    """Cam rotation (deg, same sense as the arm) placing the spiral point of the needed radius at the window angle."""
    r_need,alpha=_cam_target(R,psi)''')
rep("    _rec['cam_rotation_deg']=round(_cam_rotation(_rec['arm_angle_deg'],_rec['tip_radius_mm']),2)\n    _rec['cam_edge_radius_mm']=round(_cam_target(_rec['tip_radius_mm'])[0],2)",
    "    _rec['cam_rotation_deg']=round(_cam_rotation(_rec['arm_angle_deg'],_rec['tip_radius_mm'],_rec['rotor_trim_deg']),2)\n    _rec['cam_edge_radius_mm']=round(_cam_target(_rec['tip_radius_mm'],_rec['rotor_trim_deg'])[0],2)")
# pose check: use the solved trim
rep("    _psi=-(_phi+LEAN)-POCKET_ROLL                     # rotor trim that squares the window to the port at this arm angle\n","    _psi=_rec['rotor_trim_deg']                        # rotor trim that squares the window to the port at this arm angle\n")
rep("    REACH['ports'][_tag]['rotor_trim_deg']=round(_psi,2)\n","")
p.write_text(t);print('ok')
