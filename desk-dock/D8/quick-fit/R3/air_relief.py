"""Smooth open-edge relief; X becomes print Z on the existing broad-side bed face."""
import math
import cadquery as cq


def relieve_lip(lip, width, outer, inner, top, cfg):
    count = cfg['channel_count']
    pitch = width/count
    xs = [width*i/(count*16) for i in range(count*16+1)]
    def wave(x):
        return math.sin(math.pi*x/pitch)**2
    def wire(x, points):
        return cq.Workplane('YZ',origin=(x,0,0)).polyline(points).close().wire().val()
    # Each channel is open above the lip. Its bottom sweeps gently through
    # the wall: lower at the two entrances and higher at the central throat.
    half = (inner-outer)/2
    middle = (inner+outer)/2
    ys = [outer-.4+(inner-outer+.8)*i/12 for i in range(13)]
    top_wires = []
    face_wires = []
    for x in xs:
        f = wave(x)
        bottom = [(y,top+.05-f*(cfg['scallop_depth_mm']+
                   cfg['mouth_flare_mm']*((y-middle)/half)**2)) for y in ys]
        top_wires.append(wire(x,bottom+[(ys[-1],top+5),(ys[0],top+5)]))
        zs = [cfg['groove_start_z_mm']+(top+2-cfg['groove_start_z_mm'])*i/24 for i in range(25)]
        floor = []
        for z in zs:
            t = max(0,min(1,(z-cfg['groove_start_z_mm'])/(top-2-cfg['groove_start_z_mm'])))
            smooth = t*t*(3-2*t)
            # A 0.032 mm continuous blend avoids tangent pinches between the
            # three grooves, where separate zero-depth lofts would meet.
            groove_f = .04+.96*f
            floor.append((inner-cfg['face_relief_depth_mm']*groove_f*smooth,z))
        face_wires.append(wire(x,floor+[(inner+3,zs[-1]),(inner+3,zs[0])]))
    top_cut = cq.Solid.makeLoft(top_wires,ruled=False)
    face_cut = cq.Solid.makeLoft(face_wires,ruled=False)
    result = lip.cut(top_cut).cut(face_cut).clean()
    assert result.isValid() and len(result.Solids())==1
    assert result.cut(lip).Volume()<.001
    # Bound slopes in X (the layer direction), within the actual wall span.
    top_gradient = (cfg['scallop_depth_mm']+cfg['mouth_flare_mm'])*math.pi/pitch
    face_gradient = cfg['face_relief_depth_mm']*math.pi/pitch
    report = dict(channel_count=count,pitch_mm=pitch,
        central_scallop_depth_mm=cfg['scallop_depth_mm']-.05,
        mouth_scallop_depth_mm=cfg['scallop_depth_mm']+cfg['mouth_flare_mm']-.05,
        maximum_face_relief_mm=cfg['face_relief_depth_mm'],
        nominal_remaining_wall_at_full_relief_mm=inner-outer-cfg['face_relief_depth_mm'],
        analytic_max_overhang_from_vertical_deg=math.degrees(math.atan(max(top_gradient,face_gradient))),
        removed_lip_volume_mm3=lip.Volume()-result.Volume(),
        topology='Three open-top rounded scallops; inner-face channels taper smoothly to zero depth at their roots. No enclosed passages.',
        scope='Geometric slope bound in broad-side print orientation; corroborate with layer sections and Orca toolpaths.')
    return result,report
