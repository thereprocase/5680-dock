from pathlib import Path
p=Path('build_d9.py');t=p.read_text()
def rep(a,b):
    global t
    assert a in t,('MISSING',a[:90]);t=t.replace(a,b)
rep("""REACH['pinch_screw']={'thread':'printed M%.0f x %.0f'%(PINCH_D,PINCH_P),'axis':'along the plug minor axis through the 10-mm wall, captured scalloped nut on the outer face','tip_clearance_to_9mm_boot_mm':0.5}
# Pinch screw and nut: built along +Z (head at -Z), printed thread-axis vertical, then
# laid along -W in the plug frame so the tip stops 0.5 mm short of a 9-mm boot.
_pinch_len=WALL_S+0.5+(POCKET_W/2-4.5)-0.5
pinch_screw0=make_screw(_pinch_len,diameter=PINCH_D,pitch=PINCH_P,core_diameter=6.2,head_diameter=PINCH_HEAD,thread_length=_pinch_len-2).val()
pinch_nut0=make_nut(PINCH_NUT_T,diameter=PINCH_D,pitch=PINCH_P,core_diameter=6.2,outer_diameter=PINCH_HEAD,radial_clearance=.30,phase_z=-(PINCH_NUT_T+0.3)).val()
# +Z of the screw -> +W (into the pocket): rotate -90 about X maps +Z to +Y
pinch_screw=_plugframe(pinch_screw0.rotate((0,0,0),(1,0,0),-90).translate((PINCH_X,_bw0-0.5,_pc[1])))
pinch_nut=_plugframe(pinch_nut0.rotate((0,0,0),(1,0,0),-90).translate((PINCH_X,_bw0+0.3,_pc[1])))
add('plug-holder-rotor-pinch-screw',pinch_screw,'base','Printed M8 x 2 pinch screw for the plug carrier; its tip presses the plug boot in the window. Print thread axis vertical.',pinch_screw0)""",
"""# Pinch screw, nut and bearing shim. The screw is built along +Z (head at -Z) and
# printed thread-axis vertical, then laid along +W in the plug frame. Its flat tip seats
# in a shallow round recess on the back of a loose 5-mm shim that fills the rest of the
# window's width; the shim's front is a concave cradle so the clamp load is spread along
# 33 mm of the boot instead of a point. With a 9-mm boot against the far wall the shim
# sits at W -5..0 and the screw tip 0.2 mm off the recess floor.
SHIM_T=5.0;SHIM_L=33.0;SHIM_RECESS=1.5;BOOT_R=4.5
_shim_w0=_pc[0]-POCKET_W/2                         # against the thick wall side of the window
_pinch_len=16.0
_pinch_tip_w=_shim_w0+SHIM_RECESS-0.2
pinch_screw0=make_screw(_pinch_len,diameter=PINCH_D,pitch=PINCH_P,core_diameter=6.2,head_diameter=PINCH_HEAD,thread_length=_pinch_len-2,tip_chamfer=0).val()
pinch_nut0=make_nut(PINCH_NUT_T,diameter=PINCH_D,pitch=PINCH_P,core_diameter=6.2,outer_diameter=PINCH_HEAD,radial_clearance=.30,phase_z=-(PINCH_NUT_T+0.3)).val()
pinch_screw=_plugframe(pinch_screw0.rotate((0,0,0),(1,0,0),-90).translate((PINCH_X,_pinch_tip_w-_pinch_len,_pc[1])))
pinch_nut=_plugframe(pinch_nut0.rotate((0,0,0),(1,0,0),-90).translate((PINCH_X,_bw0+0.3,_pc[1])))
_shim=box(PINCH_X-SHIM_L/2,_shim_w0,_pc[1]-(POCKET_H/2-0.2),SHIM_L,SHIM_T,POCKET_H-0.4)
_shim=_shim.cut(cy(PINCH_X,_shim_w0-1,_pc[1],PINCH_D/2+0.3,SHIM_RECESS+1))                                   # tip recess on the back
_shim=_shim.cut(cx(PINCH_X-SHIM_L/2-1,_pc[0]+POCKET_W/2-BOOT_R,_pc[1],BOOT_R+0.1,SHIM_L+2))                # concave cradle around the boot centre
pinch_shim0=_shim.clean()
pinch_shim=_plugframe(pinch_shim0)
add('plug-holder-rotor-pinch-shim',pinch_shim,'left','Loose 5-mm bearing shim in the carrier window: the pinch screw tip seats in the round recess on its back and its concave front spreads the clamp along 33 mm of the plug boot. Print recess face down.',
    pinch_shim0.translate((-PINCH_X,-_shim_w0,-_pc[1])).rotate((0,0,0),(1,0,0),90))
REACH['pinch_screw']={'thread':'printed M%.0f x %.0f, %.0f mm shank'%(PINCH_D,PINCH_P,_pinch_len),'axis':'along the plug minor axis through the 10-mm wall, captured scalloped nut on the outer face','bearing_shim_mm':[SHIM_L,POCKET_H-0.4,SHIM_T],'shim_cradle_radius_mm':BOOT_R+0.1,'tip_to_recess_floor_mm':0.2}
add('plug-holder-rotor-pinch-screw',pinch_screw,'base','Printed M8 x 3 pinch screw for the plug carrier, 16-mm shank with a flat tip that seats in the bearing shim. Print thread axis vertical.',pinch_screw0)""")
rep("             'plug-holder-length-clamp-2-screw','plug-holder-length-clamp-2-nut','plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut']\nCAM_PART=",
    "             'plug-holder-length-clamp-2-screw','plug-holder-length-clamp-2-nut','plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut','plug-holder-rotor-pinch-shim']\nCAM_PART=")
p.write_text(t)
q=Path('prepare_and_slice.py');u=q.read_text()
a="plug_hardware=clamp_big+sorted(n for n in part_names if n.startswith(('plug-holder-','accessory-socket-clamp-','laptop-slide-endstop-')) and n not in plug_structure+clamp_big+['plug-holder-clamp-shoulder','plug-holder-clamp-cam-spatula'])"
assert a in u
u=u.replace(a,"clamp_big+=['plug-holder-rotor-pinch-shim']   # the long shim leads the small-hardware rows\nplug_hardware=clamp_big+sorted(n for n in part_names if n.startswith(('plug-holder-','accessory-socket-clamp-','laptop-slide-endstop-')) and n not in plug_structure+clamp_big+['plug-holder-clamp-shoulder','plug-holder-clamp-cam-spatula'])")
q.write_text(u)
c=Path('audit/clamp_views.py');v=c.read_text()
v=v.replace("'plug-holder-rotor-pinch-screw':(200,170,90),'plug-holder-rotor-pinch-nut':(200,170,90),","'plug-holder-rotor-pinch-screw':(200,170,90),'plug-holder-rotor-pinch-nut':(200,170,90),'plug-holder-rotor-pinch-shim':(240,210,140),")
v=v.replace("for n in ('plug-holder-polar-plug-rotor','plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut','plug-holder-clamp-cam-spatula','plug-holder-polar-outer-arm','plug-holder-clamp-shoulder',","for n in ('plug-holder-polar-plug-rotor','plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut','plug-holder-rotor-pinch-shim','plug-holder-clamp-cam-spatula','plug-holder-polar-outer-arm','plug-holder-clamp-shoulder',")
v=v.replace("for n in ('plug-holder-polar-plug-rotor','plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut','plug-holder-clamp-cam-spatula','plug-holder-polar-outer-arm','plug-holder-polar-inner-arm','plug-holder-clamp-nut'):","for n in ('plug-holder-polar-plug-rotor','plug-holder-rotor-pinch-screw','plug-holder-rotor-pinch-nut','plug-holder-rotor-pinch-shim','plug-holder-clamp-cam-spatula','plug-holder-polar-outer-arm','plug-holder-polar-inner-arm','plug-holder-clamp-nut'):")
v=v.replace("'plug-holder-rotor-pinch-screw':-25,'plug-holder-rotor-pinch-nut':-25}","'plug-holder-rotor-pinch-screw':-25,'plug-holder-rotor-pinch-nut':-25,'plug-holder-rotor-pinch-shim':-25}")
c.write_text(v);print('edits ok')
