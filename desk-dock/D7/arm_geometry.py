"""Direct axial brace and positive insertion abutment for the plug cassette.

Dimensions are in the unleaned laptop frame. The hollow section is explicit CAD,
not an assumption that sparse infill behaves like solid PETG. Root/shelf/joint
stiffness still needs the loaded prototype check described in arm-study.
"""
import cadquery as cq

def make_arm_support(p,shelf,box,rb,hole):
    P=p['rear_case_seat_z']+p['port_from_rear_case']
    a=p['plug_arm']; x=a['free_end_x_mm']; end=a['root_x_mm']
    y=a['near_y_mm']; b=a['width_y_mm']; h=a['depth_z_mm']; t=a['wall_mm']
    top=P-18.7; bottom=top-h
    beam=box(x,y,bottom,end-x,b,h)
    # Open cable-side end permits inspection/support access. The root end is
    # closed, preventing this tube from bypassing the exhaust plenum.
    core=box(x-.1,y+t,bottom+t,end-t-x+.1,b-2*t,h-2*t)
    beam=beam.cut(core)
    # Load spreads into the tower's side wall, its lid-side wall, and the deck.
    shoe=box(18,12,46,8,24,top-46)
    foot=box(-7,y,46,33,b,bottom+t-46)
    # Fixed abutment behind the calibrated shim carries insertion load.
    # Its U-shaped upper opening leaves the exiting cable unobstructed.
    abutment=box(-40,-18,P-24,6,36,20.6)
    abutment=abutment.cut(box(-40.1,p['port_y']-7,P-8,6.2,14,10))
    return shelf.union(beam).union(shoe).union(foot).union(abutment)

def register_height_shim(p,shim,box):
    P=p['rear_case_seat_z']+p['port_from_rear_case']
    dx=p['depth_adjustment'];dy=p['lateral_adjustment'];dz=p['height_adjustment']
    face=-28.5+dx
    heel=box(-34,-9.8+dy,P-18.7,face+34,19.6,10.3+dz)
    # Lower tongue joins the existing height shim beneath the clamp base.
    toe=box(-34,-9.8+dy,P-18.7,face+34+.3,19.6,5+dz)
    return shim.union(heel).union(toe)
