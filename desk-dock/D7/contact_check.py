"""Limit intentional interference to modeled compliant retention regions."""
import cadquery as cq

def intended_contact(a,b,p,leaned,intersection,extra_pin_shift=(0,0,0)):
    names={a['name'],b['name']}
    from fan_service import FRICTION_REGIONS
    for i in [1,2]:
        if names=={f'{i:02}_fan_guard_retainer',f'{i:02}_manifold_with_cradle'}:
            region=cq.Compound.makeCompound(FRICTION_REGIONS[i])
            return intersection.cut(region).Volume()<.01,'grille friction lands'
    pin='cassette_cap_push_pin_6p5'
    if names=={'sliding_plug_cap','Dell_plug_overmold_REFERENCE'}:
        P=p['rear_case_seat_z']+p['port_from_rear_case']+p['height_adjustment']
        cx=-26.5+p['depth_adjustment'];cy=p['port_y']+p['lateral_adjustment']
        region=cq.Workplane('XY').box(18.02,5.82,3,centered=False).translate((cx+5.99,cy-2.91,P+5.6)).val()
        return intersection.cut(leaned(region)).Volume()<.01,'provisional cap overmold squeeze'
    if pin in names and names&{'X_depth_overmold_clamp','sliding_plug_cap'}:
        P=p['rear_case_seat_z']+p['port_from_rear_case']+p['height_adjustment']
        x=-27.5+p['depth_adjustment'];z=P+9
        regions=[]
        for y in [8.55,9.75]:
            s=cq.Solid.makeCylinder(3.5,.9,cq.Vector(x,y,z),cq.Vector(0,1,0))
            regions.append(leaned(s).translate(extra_pin_shift))
        region=cq.Compound.makeCompound(regions)
        return intersection.cut(region).Volume()<.01,'cap push-pin retention ribs'
    return False,''
