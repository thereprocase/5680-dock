from pathlib import Path
p=Path('build_d9.py');t=p.read_text()
def rep(a,b):
    global t
    assert a in t,('MISSING',a[:90]);t=t.replace(a,b)
rep("PAD_X1=-22.0\nBLK_X0=ROT_X0","PAD_X1=-5.0                                         # block runs to 5 mm short of the docked laptop face so the window clamps the overmold\nBLK_X0=ROT_X0")
rep("POCKET_W,POCKET_H=14.0,16.0                         # W along the plug's minor axis, H along its major axis",
    "POCKET_W,POCKET_H=14.0,13.0                         # W along the plug's minor axis, H along its major axis (12.35 max, 0.3 per side)")
rep("BOOT_R=4.5                                          # largest common USB-C strain-relief boot; smaller boots just travel further\nCLAMP_OFF=POCKET_W/2-BOOT_R-0.3                     # clamped, the boot sits 0.3 mm off the thin wall (room for the residual roll at either port): its axis is this far from the window centre along +W",
    "BOOT_R=4.5                                          # largest common USB-C strain-relief boot, relieved behind the clamp zone\nCLAMP_OFF=POCKET_W/2-P['plug_minor']/2-0.25          # clamped, the overmold's flat sits 0.25 mm off the thin wall: its axis is this far from the window centre along +W\nCLAMP_X0=-17.5                                      # the overmold (x -18.35..0) is clamped from here to the block end; behind it the window is relieved for the boot")
rep("pocket=_plugframe(box(BLK_X0-1,_pc[0]-POCKET_W/2,_pc[1]-POCKET_H/2,(PAD_X1-BLK_X0)+2,POCKET_W,POCKET_H))",
    "pocket=_plugframe(box(BLK_X0-1,_pc[0]-POCKET_W/2,_pc[1]-POCKET_H/2,(PAD_X1-BLK_X0)+2,POCKET_W,POCKET_H))\n_boot_relief=_plugframe(cx(BLK_X0-1,_pc[0]+CLAMP_OFF,_pc[1],BOOT_R+0.2,CLAMP_X0-BLK_X0+1))   # round boots up to 9 mm clear the thin wall behind the clamp zone")
rep("PINCH_X=(BLK_X0+PAD_X1)/2                           # screw axis: through the thick wall along -W, at mid-block","PINCH_X=(CLAMP_X0+PAD_X1)/2                         # screw axis: through the thick wall along -W, mid overmold clamp zone")
rep("plug_rotor=tip_eye.fuse(rot_bar).fuse(rot_plate).fuse(carrier).cut(pocket).cut(_pin_hole).cut(_nut_pocket)",
    "plug_rotor=tip_eye.fuse(rot_bar).fuse(rot_plate).fuse(carrier).cut(pocket).cut(_boot_relief).cut(_pin_hole).cut(_nut_pocket)")
rep("SHIM_T=7.0;SHIM_L=33.0;SHIM_RECESS=1.5","SHIM_T=POCKET_W-P['plug_minor']-0.5;SHIM_L=(PAD_X1-CLAMP_X0)-1.0;SHIM_RECESS=1.5   # 7.0 x 11.5: fills the window beside the 6.5-mm overmold with 0.5 mm to spare")
rep("_shim=_shim.cut(cx(PINCH_X-SHIM_L/2-1,_pc[0]+CLAMP_OFF,_pc[1],BOOT_R+0.1,SHIM_L+2))                # concave cradle around the clamped boot, 2.1 mm deep at the centre\n","")
rep("# in a shallow round recess on the back of a loose 5-mm shim that fills the rest of the\n# window's width; its front is a concave cradle so the clamp load is spread along 33 mm\n# of the boot instead of a point. Clamped, the boot sits against the thin wall (that\n# clamped axis is the reach target, so the window centre is offset by CLAMP_OFF); a 9-mm\n# boot there is wrapped by a 7-mm shim with a 2.1-mm cradle, and a 6-mm boot just lets\n# the shim and screw travel 3 mm further. The tip sits 0.2 mm off the recess floor.",
    "# in a shallow round recess on the back of a loose flat shim; the shim's front and the\n# thin wall are the two jaws on the overmold's 6.5-mm FLATS, so the plug cannot roll in\n# the carrier. Clamped, the overmold sits 0.25 mm off the thin wall (that clamped axis is\n# the reach target, so the window centre is offset by CLAMP_OFF). A thinner overmold just\n# lets the shim and screw travel further. The tip sits 0.2 mm off the recess floor.")
rep("'Loose 7-mm bearing shim in the carrier window: the pinch screw tip seats in the round recess on its back and its concave front spreads the clamp along 33 mm of the plug boot. Print recess face down.'",
    "'Loose 7-mm flat bearing shim in the carrier window: the pinch screw tip seats in the round recess on its back and its flat front bears on the overmold flat, so the plug is held on its flats and cannot roll. Print recess face down.'")
rep("'bearing_shim_mm':[SHIM_L,POCKET_H-0.4,SHIM_T],'shim_cradle_radius_mm':BOOT_R+0.1,'tip_to_recess_floor_mm':0.2,'boot_diameter_design_mm':[6.0,2*BOOT_R],'clamped_axis_offset_from_window_centre_mm':CLAMP_OFF,",
    "'bearing_shim_mm':[SHIM_L,POCKET_H-0.4,SHIM_T],'clamps':'overmold flats (6.5 mm) between the shim and the thin wall, x %.1f..%.1f; boot relief r %.1f behind'%(CLAMP_X0,PAD_X1,BOOT_R+0.2),'tip_to_recess_floor_mm':0.2,'boot_diameter_design_mm':[6.0,2*BOOT_R],'clamped_axis_offset_from_window_centre_mm':CLAMP_OFF,")
rep("with a 14 x 16 mm window, a 10-mm wall carrying a captured scalloped nut and an M8 x 3 printed pinch screw. Its back face bears on the cam lobe.",
    "with a 14 x 13 mm window that clamps the overmold on its flats, a 10-mm wall carrying a captured scalloped nut and an M8 x 3 printed pinch screw. Its back face bears on the cam lobe.")
rep("""    moved={n:PARTS[n].rotate((0,BY,BZ),(1,BY,BZ),_phi) for n in ARM_GROUP}
    moved.update({n:PARTS[n].translate((0,0,_dR)).rotate((0,BY,BZ),(1,BY,BZ),_phi) for n in OUTER_GROUP})""",
"""    _psi=-(_phi+LEAN)-POCKET_ROLL                     # rotor trim that squares the window to the port at this arm angle
    ROTOR_GROUP=['plug-holder-polar-plug-rotor','plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut','plug-holder-rotor-pinch-shim']
    moved={n:PARTS[n].rotate((0,BY,BZ),(1,BY,BZ),_phi) for n in ARM_GROUP}
    moved.update({n:PARTS[n].translate((0,0,_dR)).rotate((0,BY,BZ),(1,BY,BZ),_phi) for n in OUTER_GROUP if n not in ROTOR_GROUP})
    moved.update({n:PARTS[n].rotate((0,tip_y,tip_z),(1,tip_y,tip_z),_psi).translate((0,0,_dR)).rotate((0,BY,BZ),(1,BY,BZ),_phi) for n in ROTOR_GROUP})
    REACH['ports'][_tag]['rotor_trim_deg']=round(_psi,2)""")
p.write_text(t)
c=Path('audit/clamp_views.py');u=c.read_text()
a="""    for n in OUTER:out[n]=S[n].translate((0,0,dR)).rotate((0,BY,BZ),(1,BY,BZ),phi)
    out[CAM]=S[CAM].rotate((0,BY,BZ),(1,BY,BZ),rec['cam_rotation_deg']-CAM_ROT0)"""
b="""    psi=rec.get('rotor_trim_deg',0.0);ROTG=('plug-holder-polar-plug-rotor','plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut','plug-holder-rotor-pinch-shim')
    for n in OUTER:
        s=S[n].rotate((0,tip_y,tip_z),(1,tip_y,tip_z),psi) if n in ROTG else S[n]
        out[n]=s.translate((0,0,dR)).rotate((0,BY,BZ),(1,BY,BZ),phi)
    out[CAM]=S[CAM].rotate((0,BY,BZ),(1,BY,BZ),rec['cam_rotation_deg']-CAM_ROT0)"""
assert a in u;u=u.replace(a,b)
u=u.replace("BY,BZ=CL['pivot_axis_yz_mm'];tip_z=BZ+138.0","BY,BZ=CL['pivot_axis_yz_mm'];tip_z=BZ+138.0;tip_y=BY")
u=u.replace("cutx=box(-200,-100,-100,400,400,400).intersect(box(-46.5,-100,-100,4.0,400,400))   # a 4-mm slab about the pinch axis, x -46.5..-42.5","cutx=box(-13.25,-100,-100,4.0,400,400)   # a 4-mm slab about the pinch axis, x -13.25..-9.25")
u=u.replace("'4-mm slab at x -46..-42 seen from the plug end: screw through the thick wall and nut, flat tip in the shim recess, concave shim on the boot, boot against the thin wall'","'4-mm slab at x -13..-9 seen from the plug end: screw through the thick wall and nut, flat tip in the shim recess, flat shim on the overmold flat, overmold against the thin wall'")
c.write_text(u);print('ok')
