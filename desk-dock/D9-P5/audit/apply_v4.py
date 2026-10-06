from pathlib import Path
p=Path('build_d9.py');t=p.read_text()
def rep(a,b):
    global t
    assert a in t,('MISSING',a[:90]);t=t.replace(a,b)
# ---- cheeks 1.5 mm outboard so the rotor can start on the cam face
rep("tip_bore=cx(SLV_X0-1,tip_y,tip_z,8.4,SLV_W+2)\ntip_l=cx(SLV_X0,tip_y,tip_z,18,4).cut(tip_bore)\ntip_r=cx(SLV_X0+SLV_W-4,tip_y,tip_z,18,4).cut(tip_bore)",
    "CHEEK_SHIFT=1.5                                     # cheeks sit 1.5 mm outboard of the sleeve walls so the rotor's eye, neck and block share the cam-face plane\ntip_bore=cx(SLV_X0-CHEEK_SHIFT-1,tip_y,tip_z,8.4,SLV_W+2)\ntip_l=cx(SLV_X0-CHEEK_SHIFT,tip_y,tip_z,18,4).cut(tip_bore)\ntip_r=cx(SLV_X0+SLV_W-4-CHEEK_SHIFT,tip_y,tip_z,18,4).cut(tip_bore)")
rep("sleeve=sleeve.cut(tip_bore).cut(box(SLV_X0+4,tip_y-17,tip_z-18.5,SLV_W-8,34,25)).clean()",
    "sleeve=sleeve.cut(tip_bore).cut(box(SLV_X0+4-CHEEK_SHIFT,tip_y-17,tip_z-18.5,SLV_W-8,34,25)).clean()")
rep("ROT_X0=SLV_X0+4.4;ROT_T=SLV_W-8.8                   # rotor eye between the cheeks, 0.4 mm each side",
    "ROT_X0=SLV_X0-CHEEK_SHIFT+4.4;ROT_T=SLV_W-8.8       # rotor eye between the cheeks, 0.4 mm each side")
# ---- rotor: block in the plug frame with a pinch screw
s=t.index("# Plug rotor. The USB-C port face is at x=0");e=t.index("# Cam-lobe spatula.")
new='''# Plug carrier. The USB-C port face is at x=0 and the plug is 25 mm long, so the boot
# pocket sits inboard of the arm plane and, because the tip clevis can never get closer
# than about 120 mm to the pivot, inboard of the tip as well: an eye on the tip pivot, a
# bar and plate beside the sleeve, and a carrier block built in the PLUG's frame (faces
# parallel to the plug's major and minor axes, rolled to the mean working arm angle plus
# the lean) with a 14 x 16 mm window and a printed M8 pinch screw through the thick wall
# into a captured hex nut. The block's back face lies on the cam plate's face.
PAD_X1=-22.0
BLK_X0=ROT_X0
assert BLK_X0>=CAM_X0+CAM_T+0.1-1e-9,'rotor must clear the cam face'
POCKET_W,POCKET_H=14.0,16.0                         # W along the plug's minor axis, H along its major axis
WALL_N,WALL_S,WALL_H=5.0,10.0,5.0                   # thin wall, screw-side wall, walls along H
POCKET_ROLL=-(sum(v['arm_angle_deg'] for v in REACH['ports'].values())/len(REACH['ports'])+LEAN)
tip_eye=cx(ROT_X0,tip_y,tip_z,16.8,ROT_T)
rot_bar=box(ROT_X0,tip_y-20,tip_z-15,ROT_T,6,30)                    # eye to plate, inside the sleeve's rotor slot
rot_plate=box(ROT_X0,tip_y-48,tip_z-36,ROT_T,28,42)                 # 9 mm clear of the sleeve side wall
_pc=(tip_y-PAD_LAT,tip_z-PAD_RAD)
def _plugframe(s):
    """Rotate a solid built with W along +Y and H along +Z about the pocket centre into the plug frame."""
    return s.rotate((0,_pc[0],_pc[1]),(1,_pc[0],_pc[1]),POCKET_ROLL)
_bw0=_pc[0]-POCKET_W/2-WALL_S;_bw=POCKET_W+WALL_S+WALL_N;_bh0=_pc[1]-POCKET_H/2-WALL_H;_bh=POCKET_H+2*WALL_H
carrier=_plugframe(box(BLK_X0,_bw0,_bh0,PAD_X1-BLK_X0,_bw,_bh))
pocket=_plugframe(box(BLK_X0-1,_pc[0]-POCKET_W/2,_pc[1]-POCKET_H/2,(PAD_X1-BLK_X0)+2,POCKET_W,POCKET_H))
PINCH_X=(BLK_X0+PAD_X1)/2                           # screw axis: through the thick wall along -W, at mid-block
PINCH_D=8.0;PINCH_P=2.0;PINCH_HEAD=14.0;PINCH_NUT_T=6.0
_pin_hole=_plugframe(cy(PINCH_X,_bw0-1,_pc[1],PINCH_D/2+0.3,WALL_S+2))                       # clearance hole through the thick wall
_nut_pocket=_plugframe(cq.Workplane('XZ',origin=(PINCH_X,_bw0+PINCH_NUT_T+0.3,_pc[1])).polygon(6,PINCH_HEAD+0.6).extrude(PINCH_NUT_T+0.3+1).val())   # hex pocket open to the outer face (XZ normal is -Y)
plug_rotor=tip_eye.fuse(rot_bar).fuse(rot_plate).fuse(carrier).cut(pocket).cut(_pin_hole).cut(_nut_pocket)
plug_rotor=plug_rotor.cut(cx(ROT_X0-1,tip_y,tip_z,8.4,ROT_T+2)).clean()
add('plug-holder-polar-plug-rotor',plug_rotor,'left','Plug carrier, %.1f mm wide: eye on the tip pivot, bar and plate beside the sleeve, and a carrier block in the plug frame (rolled %.1f deg) with a 14 x 16 mm window, a 10-mm wall carrying a captured hex nut and an M8 printed pinch screw. Its back face bears on the cam lobe. Prints eye, plate and block face down, window vertical.'%(ROT_T,POCKET_ROLL))
PROTECT['plug-holder-polar-plug-rotor']=[cx(ROT_X0-1,tip_y,tip_z,8.4,ROT_T+2),_pin_hole,_nut_pocket]
REACH['pocket_window_mm']=[POCKET_W,POCKET_H];REACH['pocket_pre_roll_deg']=round(POCKET_ROLL,2);REACH['pocket_block_x_mm']=[BLK_X0,PAD_X1]
REACH['pinch_screw']={'thread':'printed M%.0f x %.0f'%(PINCH_D,PINCH_P),'axis':'along the plug minor axis through the 10-mm wall, captured hex nut on the outer face','tip_clearance_to_9mm_boot_mm':0.5}
# Pinch screw and nut: built along +Z (head at -Z), printed thread-axis vertical, then
# laid along -W in the plug frame so the tip stops 0.5 mm short of a 9-mm boot.
_pinch_len=WALL_S+0.5+(POCKET_W/2-4.5)-0.5
pinch_screw0=make_screw(_pinch_len,diameter=PINCH_D,pitch=PINCH_P,core_diameter=6.2,head_diameter=PINCH_HEAD,thread_length=_pinch_len-2).val()
pinch_nut0=make_nut(PINCH_NUT_T,diameter=PINCH_D,pitch=PINCH_P,core_diameter=6.2,outer_diameter=PINCH_HEAD,radial_clearance=.30,phase_z=-(PINCH_NUT_T+0.3)).val()
# +Z of the screw -> +W (into the pocket): rotate -90 about X maps +Z to +Y
pinch_screw=_plugframe(pinch_screw0.rotate((0,0,0),(1,0,0),-90).translate((PINCH_X,_bw0-0.5,_pc[1])))
pinch_nut=_plugframe(pinch_nut0.rotate((0,0,0),(1,0,0),-90).translate((PINCH_X,_bw0+0.3,_pc[1])))
add('plug-holder-rotor-pinch-screw',pinch_screw,'base','Printed M8 x 2 pinch screw for the plug carrier; its tip presses the plug boot in the window. Print thread axis vertical.',pinch_screw0)
add('plug-holder-rotor-pinch-nut',pinch_nut,'base','Captured printed hex nut for the carrier pinch screw; drops into the hex pocket on the carrier wall. Print thread axis vertical.',pinch_nut0)

'''
t=t[:s]+new+t[e:]
# ---- cam: leaf lobe
s=t.index("CAM_R0=65.0;CAM_B=1.8;CAM_RMAX=135.0;CAM_GAP=0.5");e=t.index("CAM_ROT0=_cam_rotation(0.0,tip_z-BZ)")
new='''CAM_R0=76.0;CAM_B=0.9;CAM_ARC=24.0;CAM_GAP=0.5       # gentle spiral over the first 24 deg, r 76 -> 110
CAM_RMAX=CAM_R0*math.exp(CAM_B*math.radians(CAM_ARC))
def _pocket_corners(R):
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
    r_need,alpha=_cam_target(R)
    assert CAM_R0<=r_need<=CAM_RMAX,('cam spiral cannot reach',r_need)
    psi=math.degrees(math.log(r_need/CAM_R0)/CAM_B)   # angle along the lobe, from its near edge
    return phi+alpha-psi
# Leaf outline in the cam frame: a radial near edge from inside the hub up to the spiral
# start, the spiral, then a spline tip and back edge returning into the hub about 53 deg
# from the near edge. +theta is toward -Y, like the arm angle.
_pt=lambda r,deg:(-r*math.sin(math.radians(deg)),r*math.cos(math.radians(deg)))
_lead=[_pt(CAM_HUB_R-2.0,0.0),_pt(CAM_R0,0.0)]
_spiral=[_pt(CAM_R0*math.exp(CAM_B*math.radians(CAM_ARC*_k/40.0)),CAM_ARC*_k/40.0) for _k in range(1,41)]
_back=[_pt(CAM_RMAX+1.0,CAM_ARC+4.0),_pt(CAM_RMAX-4.0,CAM_ARC+10.0),_pt(CAM_RMAX-16.0,CAM_ARC+17.0),_pt(CAM_RMAX-34.0,CAM_ARC+23.0),_pt(CAM_RMAX-52.0,CAM_ARC+27.0),_pt(CAM_HUB_R-2.0,CAM_ARC+29.0)]
_lobe=cq.Workplane('YZ').polyline(_lead+_spiral).spline(_back,includeCurrent=True).close().extrude(CAM_T).val()
_lobe=_lobe.translate((CAM_X0,BY,BZ))
cam=cx(CAM_X0,BY,BZ,CAM_HUB_R,CAM_T).fuse(_lobe).cut(cx(CAM_X0-1,BY,BZ,CAM_BORE/2,CAM_T+2))
'''
t=t[:s]+new+t[e:]
rep("CLAMP['cam_plate'].update({'lobe':'log spiral r = %.0f*exp(%.1f*theta) over %.1f deg to r %.0f, radial cuts at both ends'%(CAM_R0,CAM_B,math.degrees(CAM_SPAN),CAM_RMAX),",
    "CLAMP['cam_plate'].update({'lobe':'leaf: radial near edge, log spiral r = %.0f*exp(%.1f*theta) over %.0f deg to r %.0f, spline tip and back edge closing at %.0f deg'%(CAM_R0,CAM_B,CAM_ARC,CAM_RMAX,CAM_ARC+29.0),")
rep("'Cam-lobe spatula: 14-mm plate on the journal outboard of the arm disc, pinched by the same nut.","'Leaf-lobe spatula: 14-mm plate on the journal outboard of the arm disc, pinched by the same nut.")
# ---- threaded mates and pose groups
rep("    ('plug-holder-tip-annular-screw','plug-holder-tip-annular-nut')]}",
    "    ('plug-holder-tip-annular-screw','plug-holder-tip-annular-nut'),\n    ('plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut'),\n    ('plug-holder-length-clamp-1-screw','plug-holder-length-clamp-1-nut'),\n    ('plug-holder-length-clamp-2-screw','plug-holder-length-clamp-2-nut')]}")
rep("             'plug-holder-length-clamp-2-screw','plug-holder-length-clamp-2-nut']\nCAM_PART='plug-holder-clamp-cam-spatula'",
    "             'plug-holder-length-clamp-2-screw','plug-holder-length-clamp-2-nut','plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut']\nCAM_PART='plug-holder-clamp-cam-spatula'")
# tip hardware follows the cheeks
rep("tip_screw=make_screw(SLV_W+12,diameter=16,pitch=4.5,core_diameter=13,head_diameter=28,thread_length=15).val().cut(cz(0,0,-2,4,SLV_W+19)).rotate((0,0,0),(0,1,0),90).translate((SLV_X0-3.5,tip_y,tip_z))\ntip_nut=make_nut(7,diameter=16,pitch=4.5,core_diameter=13,outer_diameter=28,radial_clearance=.35,phase_z=-(SLV_W+5.1)).val().rotate((0,0,0),(0,1,0),90).translate((SLV_X0+SLV_W+1.6,tip_y,tip_z))",
    "tip_screw=make_screw(SLV_W+12,diameter=16,pitch=4.5,core_diameter=13,head_diameter=28,thread_length=15).val().cut(cz(0,0,-2,4,SLV_W+19)).rotate((0,0,0),(0,1,0),90).translate((SLV_X0-CHEEK_SHIFT-3.5,tip_y,tip_z))\ntip_nut=make_nut(7,diameter=16,pitch=4.5,core_diameter=13,outer_diameter=28,radial_clearance=.35,phase_z=-(SLV_W+5.1)).val().rotate((0,0,0),(0,1,0),90).translate((SLV_X0-CHEEK_SHIFT+SLV_W+1.6,tip_y,tip_z))")
rep("for label,x,y,z,ro,ri in [('tip-head',SLV_X0-1.6,tip_y,tip_z,15,8.35),('tip-nut',SLV_X0+SLV_W,tip_y,tip_z,15,8.35)]:",
    "for label,x,y,z,ro,ri in [('tip-head',SLV_X0-CHEEK_SHIFT-1.6,tip_y,tip_z,15,8.35),('tip-nut',SLV_X0-CHEEK_SHIFT+SLV_W,tip_y,tip_z,15,8.35)]:")
p.write_text(t);print('v4 applied')
