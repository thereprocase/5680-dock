"""Trial carrier wall thicknesses against the real posed lobe without rebuilding: rebuild
just the carrier block box in the plug frame for candidate (thin wall, bottom wall, top wall)
and report the lobe bearing area at both port poses plus contact with the laptop, sleeve,
shoulder and cam hub."""
import json,math,sys
from pathlib import Path
import cadquery as cq
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'generated'
P=json.loads((HERE.parent/'source-inputs/parameters.json').read_text());LEAN=P['laptop_lean_deg']
man=json.loads((OUT/'manifest.json').read_text());ACC=man['accessory_socket'];CL=ACC['base_clamp'];RE=ACC['reach']
BY,BZ=CL['pivot_axis_yz_mm'];tip_y,tip_z=RE.get('tip_pivot_yz_mm',[BY,BZ+115.5])
def L(n):return cq.importers.importStep(str(OUT/(n+'.step'))).val()
CAM_ROT0=CL['cam_plate']['modelled_rotation_deg']
cam=L('plug-holder-clamp-cam-spatula');rot=L('plug-holder-polar-plug-rotor');outer=L('plug-holder-polar-outer-arm');shoulder=L('plug-holder-clamp-shoulder');socket=L('accessory-socket-body');arm=L('plug-holder-polar-inner-arm')
laptop=cq.Solid.makeBox(P['laptop_width'],P['laptop_thickness'],232.33,cq.Vector(0,-P['laptop_thickness']/2,62)).rotate((0,0,54),(1,0,54),-LEAN)
desk=cq.Solid.makeBox(600,600,20,cq.Vector(-300,-300,-20))
rho=RE['pocket_pre_roll_deg'];W,H=RE['pocket_window_mm'];X0,X1=RE['pocket_block_x_mm'];WALL_S=10.0;CO=RE['pinch_screw']['clamped_axis_offset_from_window_centre_mm']
ax=(tip_y-34.0,tip_z-41.0);pc=(ax[0]-CO*math.cos(math.radians(rho)),ax[1]-CO*math.sin(math.radians(rho)))
def block(wn,hb,ht):
    b=cq.Solid.makeBox(X1-X0,W+WALL_S+wn,H+hb+ht,cq.Vector(X0,pc[0]-W/2-WALL_S,pc[1]-H/2-hb))
    return b.rotate((0,pc[0],pc[1]),(1,pc[0],pc[1]),rho)
def pose(s,rec,moving=True):
    phi=rec['arm_angle_deg'];dR=(BZ+rec['tip_radius_mm'])-tip_z;psi=rec['rotor_trim_deg']
    return s.rotate((0,tip_y,tip_z),(1,tip_y,tip_z),psi).translate((0,0,dR)).rotate((0,BY,BZ),(1,BY,BZ),phi)
D=0.3
for wn,hb,ht in [(5,5,5),(5,15,5),(10,10,5),(10,15,5),(12,18,5),(15,15,5),(15,20,5)]:
    row=[]
    for tag,rec in RE['ports'].items():
        b=pose(block(wn,hb,ht),rec);c=cam.rotate((0,BY,BZ),(1,BY,BZ),rec['cam_rotation_deg']-CAM_ROT0)
        area=c.translate((D,0,0)).intersect(b).Volume()/D
        sl=outer.translate((0,0,(BZ+rec['tip_radius_mm'])-tip_z)).rotate((0,BY,BZ),(1,BY,BZ),rec['arm_angle_deg'])
        ar=arm.rotate((0,BY,BZ),(1,BY,BZ),rec['arm_angle_deg'])
        hits={n:round(b.intersect(s).Volume(),1) for n,s in (('laptop',laptop),('sleeve',sl),('arm',ar),('shoulder',shoulder),('socket',socket),('cam',c),('desk',desk))}
        hits={k:v for k,v in hits.items() if v>0.01}
        bb=b.BoundingBox()
        row.append('%s area %.0f mm2 zmin %.1f ymax %.1f hits %s'%(tag,area,bb.zmin,bb.ymax,hits or 'none'))
    print('walls N %g / bottom %g / top %g:'%(wn,hb,ht),' | '.join(row),flush=True)
