"""Measure how much of the carrier's back face actually bears on the leaf lobe at each
solved port pose: the cam is pushed 0.3 mm into the rotor along +X and the overlap volume
is divided by 0.3 to give the bearing area. Also reports the patch's extent."""
import json,math,sys
from pathlib import Path
import cadquery as cq
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'generated'
man=json.loads((OUT/'manifest.json').read_text());ACC=man['accessory_socket'];CL=ACC['base_clamp'];RE=ACC['reach']
BY,BZ=CL['pivot_axis_yz_mm'];tip_y,tip_z=RE.get('tip_pivot_yz_mm',[BY,BZ+115.5])
def L(n):return cq.importers.importStep(str(OUT/(n+'.step'))).val()
CAM='plug-holder-clamp-cam-spatula';ROT='plug-holder-polar-plug-rotor';CAM_ROT0=CL['cam_plate']['modelled_rotation_deg']
cam=L(CAM);rot=L(ROT)
bb=rot.BoundingBox();print('rotor x',round(bb.xmin,2),round(bb.xmax,2),'cam x',round(cam.BoundingBox().xmin,2),round(cam.BoundingBox().xmax,2))
D=0.3
for tag,rec in RE['ports'].items():
    phi=rec['arm_angle_deg'];dR=(BZ+rec['tip_radius_mm'])-tip_z;psi=rec['rotor_trim_deg']
    r=rot.rotate((0,tip_y,tip_z),(1,tip_y,tip_z),psi).translate((0,0,dR)).rotate((0,BY,BZ),(1,BY,BZ),phi)
    c=cam.rotate((0,BY,BZ),(1,BY,BZ),rec['cam_rotation_deg']-CAM_ROT0)
    ov=c.translate((D,0,0)).intersect(r)
    v=ov.Volume();b=ov.BoundingBox() if v>1e-6 else None
    # whole back face of the block region (x within 0.31 of the cam face)
    slab=cq.Solid.makeBox(D,400,400,cq.Vector(c.BoundingBox().xmax-1e-3,-100,-100))
    back=r.intersect(slab).Volume()/D
    print(tag,'bearing area mm2 %.1f'%(v/D),'of back face %.1f'%back,'patch yz extent',(round(b.ymin,1),round(b.ymax,1),round(b.zmin,1),round(b.zmax,1)) if b else None,'span %.1f x %.1f'%((b.ylen,b.zlen) if b else (0,0)))
