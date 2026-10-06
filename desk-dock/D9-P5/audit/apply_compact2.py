from pathlib import Path
p=Path('build_d9.py');t=p.read_text()
def rep(a,b):
    global t
    assert a in t,('MISSING',a[:90]);t=t.replace(a,b)
rep("TONGUE_END=BZ+83.5","TONGUE_END=BZ+86.5")
rep("_sl0=BZ+46.0;_sl1=TONGUE_END-4.0","_sl0=BZ+45.5;_sl1=TONGUE_END-4.0")
rep("tip_z=BZ+113.0;tip_y=BY","tip_z=BZ+114.5;tip_y=BY")
rep("for zz in (tip_z-58.0,tip_z-44.0):","for zz in (tip_z-58.0,tip_z-43.0):")
rep("PAD_LAT=34.0;PAD_RAD=39.0                           # rotor pocket centre: 34 mm lateral (-Y at the modelled pose), 39 mm inboard of the tip","PAD_LAT=34.0;PAD_RAD=38.5                           # rotor pocket centre: 34 mm lateral (-Y at the modelled pose), 38.5 mm inboard of the tip")
# tip pivot: 12-mm screw, r 13 eye, r 14 cheeks 3 mm thick
rep("tip_bore=cx(SLV_X0-CHEEK_SHIFT-1,tip_y,tip_z,8.4,SLV_W+CHEEK_SHIFT+2)\ntip_l=cx(SLV_X0-CHEEK_SHIFT,tip_y,tip_z,18,4).cut(tip_bore)\ntip_r=cx(SLV_X0+SLV_W-4-CHEEK_SHIFT,tip_y,tip_z,18,4).cut(tip_bore)",
    "CHEEK_R=14.0;CHEEK_T=3.0;EYE_R=13.0;TIP_BORE_R=6.4  # 12-mm hollow tip screw\ntip_bore=cx(SLV_X0-CHEEK_SHIFT-1,tip_y,tip_z,TIP_BORE_R,SLV_W+CHEEK_SHIFT+2)\ntip_l=cx(SLV_X0-CHEEK_SHIFT,tip_y,tip_z,CHEEK_R,CHEEK_T).cut(tip_bore)\ntip_r=cx(SLV_X0+SLV_W-CHEEK_T-CHEEK_SHIFT,tip_y,tip_z,CHEEK_R,CHEEK_T).cut(tip_bore)")
rep("sleeve=sleeve.cut(tip_bore).cut(box(SLV_X0+4-CHEEK_SHIFT,tip_y-17,tip_z-18.5,SLV_W-8,34,25)).cut(box(SLV_X0+SLV_W-CHEEK_SHIFT,tip_y-17,tip_z-18.5,CHEEK_SHIFT+1,34,25)).clean()",
    "sleeve=sleeve.cut(tip_bore).cut(box(SLV_X0+CHEEK_T-CHEEK_SHIFT,tip_y-17,tip_z-(EYE_R+2.0),SLV_W-2*CHEEK_T,34,EYE_R+2.0+6.5)).cut(box(SLV_X0+SLV_W-CHEEK_SHIFT,tip_y-17,tip_z-(EYE_R+2.0),CHEEK_SHIFT+1,34,EYE_R+2.0+6.5)).clean()")
rep("ROT_X0=SLV_X0-CHEEK_SHIFT+4.4;ROT_T=SLV_W-8.8       # rotor eye between the cheeks, 0.4 mm each side","ROT_X0=SLV_X0-CHEEK_SHIFT+CHEEK_T+0.4;ROT_T=SLV_W-2*CHEEK_T-0.8   # rotor eye between the cheeks, 0.4 mm each side")
rep("assert TONGUE_END<=TIP_MIN-18.5-2.0,'tongue must stay clear of the rotor slot at full retraction'","assert TONGUE_END<=TIP_MIN-(EYE_R+2.0)-2.0,'tongue must stay clear of the rotor slot at full retraction'")
rep("tip_eye=cx(ROT_X0,tip_y,tip_z,16.8,ROT_T)\nrot_bar=box(ROT_X0,tip_y-20,tip_z-15,ROT_T,6,30)                    # eye to plate, inside the sleeve's rotor slot",
    "tip_eye=cx(ROT_X0,tip_y,tip_z,EYE_R,ROT_T)\nrot_bar=box(ROT_X0,tip_y-20,tip_z-13,ROT_T,8,26)                    # eye to plate, inside the sleeve's rotor slot")
rep("plug_rotor=plug_rotor.cut(cx(ROT_X0-1,tip_y,tip_z,8.4,ROT_T+2)).clean()","plug_rotor=plug_rotor.cut(cx(ROT_X0-1,tip_y,tip_z,TIP_BORE_R,ROT_T+2)).clean()")
rep("PROTECT['plug-holder-polar-plug-rotor']=[cx(ROT_X0-1,tip_y,tip_z,8.4,ROT_T+2),_pin_hole,_nut_pocket]","PROTECT['plug-holder-polar-plug-rotor']=[cx(ROT_X0-1,tip_y,tip_z,TIP_BORE_R,ROT_T+2),_pin_hole,_nut_pocket]")
rep("tip_screw=make_screw(SLV_W+12,diameter=16,pitch=4.5,core_diameter=13,head_diameter=28,thread_length=15).val().cut(cz(0,0,-2,4,SLV_W+19)).rotate((0,0,0),(0,1,0),90).translate((SLV_X0-CHEEK_SHIFT-3.5,tip_y,tip_z))\ntip_nut=make_nut(7,diameter=16,pitch=4.5,core_diameter=13,outer_diameter=28,radial_clearance=.35,phase_z=-(SLV_W+5.1)).val().rotate((0,0,0),(0,1,0),90).translate((SLV_X0-CHEEK_SHIFT+SLV_W+1.6,tip_y,tip_z))",
    "tip_screw=make_screw(SLV_W+11,diameter=12,pitch=3,core_diameter=10,head_diameter=22,thread_length=12).val().cut(cz(0,0,-2,3,SLV_W+18)).rotate((0,0,0),(0,1,0),90).translate((SLV_X0-CHEEK_SHIFT-3.5,tip_y,tip_z))\ntip_nut=make_nut(6,diameter=12,pitch=3,core_diameter=10,outer_diameter=22,radial_clearance=.30,phase_z=-(SLV_W+5.1)).val().rotate((0,0,0),(0,1,0),90).translate((SLV_X0-CHEEK_SHIFT+SLV_W+1.6,tip_y,tip_z))")
rep("for label,x,y,z,ro,ri in [('tip-head',SLV_X0-CHEEK_SHIFT-1.6,tip_y,tip_z,15,8.35),('tip-nut',SLV_X0-CHEEK_SHIFT+SLV_W,tip_y,tip_z,15,8.35)]:",
    "for label,x,y,z,ro,ri in [('tip-head',SLV_X0-CHEEK_SHIFT-1.6,tip_y,tip_z,11,6.35),('tip-nut',SLV_X0-CHEEK_SHIFT+SLV_W,tip_y,tip_z,11,6.35)]:")
rep("'adjustment':'polar: base angle by large face clamp + telescoping radius + independent plug-roll rotor, braced by a cam-lobe spatula pinched by the same nut','base_pivot_diameter_mm':SHAFT_D,'tip_pivot_diameter_mm':36,",
    "'adjustment':'polar: base angle by large face clamp + telescoping radius + independent plug-roll rotor, braced by a cam-lobe spatula pinched by the same nut','base_pivot_diameter_mm':SHAFT_D,'tip_pivot_diameter_mm':2*CHEEK_R,")
p.write_text(t);print('ok')
