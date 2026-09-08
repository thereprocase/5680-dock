"""Sparse underside ribs and a flat lower perimeter for upright shell printing.

The ribs provide closely spaced landings for roof bridges without filling the
whole duct with a solid haunch. They are outside the straight mouth keepout.
"""
import math
import cadquery as cq
RIB_WIDTH=1.6
RIB_PITCH=10.0

def box(x,y,z,a,b,c):
    return cq.Workplane('XY').box(a,b,c,centered=False).translate((x,y,z))

def roof_gussets(body,x0,x1,fx,front_y,W,wall=2.4,mouth_width=21):
    rear=-24+wall;top=50-wall+.2
    ma=max(42,x0+4);mb=min(W-24,x1-4)
    mouth=box(ma,-mouth_width/2,-3,mb-ma,mouth_width,70)
    ribs=[];min_angle=90.0
    # Short triangular brackets along the rear wall support the outlet lip.
    for n in range(math.ceil((x1-x0-2*wall-4)/RIB_PITCH)):
        x=x0+wall+2+n*RIB_PITCH
        if x+RIB_WIDTH>x1-wall:continue
        reach=-mouth_width/2-(rear-.2)
        rib=(cq.Workplane('YZ',origin=(x,0,0))
            .polyline([(rear-.2,top-reach),(rear-.2,top),(-mouth_width/2,top)])
            .close().extrude(RIB_WIDTH))
        ribs.append(rib)
    # Thin crosswise brackets grow from the end walls under the low wings.
    # At the widest wing the lower end clears the cover by >=0.3 mm. This
    # leaves a ~44-degree ramp, close to the nominal 45-degree design target.
    front=front_y(50-wall,True)
    wings=[(x0+wall-.2,fx-62+wall),(x1-wall+.2,fx+62-wall)]
    for outer,inner in wings:
        span=abs(inner-outer);base=max(2.8,top-span)
        min_angle=min(min_angle,math.degrees(math.atan2(top-base,span)))
        for n in range(math.ceil((front-rear-2)/RIB_PITCH)):
            y=rear+2+n*RIB_PITCH
            if y+RIB_WIDTH>front:continue
            rib=(cq.Workplane('XZ',origin=(0,y,0))
                .polyline([(outer,base),(outer,top),(inner,top)])
                .close().extrude(-RIB_WIDTH)).cut(mouth)
            if rib.val().Volume()>1e-6:ribs.append(rib)
    for rib in ribs:
        body=body.fuse(rib.val()).clean()
    assert body.isValid() and len(body.Solids())==1
    return body,dict(rib_width_mm=RIB_WIDTH,rib_pitch_mm=RIB_PITCH,
                     maximum_clear_roof_bridge_between_ribs_mm=RIB_PITCH-RIB_WIDTH,
                     minimum_wing_ramp_degrees_above_horizontal=min_angle,
                     mouth_keepout='Full-width vertical keepout through the low cavity; no new ribs in it.')

def lower_perimeter(body,i,x0,x1,front_y,wall=2.4):
    front=front_y(3)
    skirt=box(x0,-24,-2,x1-x0,front+24,5.2)
    skirt=skirt.cut(box(x0+wall,-24+wall,-2.1,x1-x0-2*wall,front+24-2*wall,5.4))
    outer=x0 if i==1 else x1
    # Open the cover saddle's removal channel all the way through the skirt.
    skirt=skirt.cut(box(outer-.15 if i==1 else outer-11.3,34-6.8,-2.1,11.45,13.6,8.3))
    body=body.fuse(skirt.val()).clean()
    assert body.isValid() and len(body.Solids())==1
    return body
