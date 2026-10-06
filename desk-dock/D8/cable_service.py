"""Split cover-edge cable tunnels and shell-mounted zip-tie bridges.

All geometry is integrated into existing parts. A 6 x 4 mm provisional bundle
fits inside a 7 x 5 mm rounded tunnel. The cover opens the tunnel at its edge,
so the electrical connector never has to pass through the finished opening.
"""
import cadquery as cq


def add_cable_routing(i,x0,x1,body,plate,box,rb,hole):
    side=1 if i==1 else -1
    outer=x0 if side==1 else x1
    yc=34.0
    # The saddle grows from the removable panel edge into its existing tongue.
    # Its exterior remains within the original endwall, above the desk feet.
    sx=outer if side==1 else outer-11
    saddle=rb(sx,yc-6.5,.5,11,13,5.3,1)
    plate=plate.union(saddle)
    # Clearance around the lower half of the passage lets the whole panel
    # lower away from a cable that remains attached to the stationary shell.
    clearance=box(outer-.15 if side==1 else outer-11.3,yc-6.8,2.79,11.45,13.6,3.31)
    body=body.cut(clearance.val()).clean()
    # R0.6 corners retain a full 6 x 4 rectangular nominal bundle envelope.
    tunnel=box(outer-1 if side==1 else outer-16,yc-3.5,2.5,17,7,5).edges('|X').fillet(.6)
    body=body.cut(tunnel.val()).clean()
    plate=plate.cut(tunnel)
    # Two rounded tie bridges retain the lead against the shell, not the cover.
    # The first relieves pull at the exit; the second guides the internal route.
    lug_centers=[]
    for y,z in [(34.0,14.0),(50.0,29.0)]:
        lx=outer+1.4 if side==1 else outer-9.4
        lug=rb(lx,y-6.5,z-4,8,13,8,1.5)
        slot_x=outer+4.4 if side==1 else outer-7.6
        # Continue through nearby roof ribs, not only through the lug. The
        # 20 mm service channel clears the adjacent 10 mm-pitch roof ribs
        # at both threading ends; cutting the lug alone makes a sealed void.
        slot=box(slot_x,y-10,z-.9,3.2,20,1.8).edges('|Y').fillet(.5)
        lug=lug.cut(slot)
        body=body.fuse(lug.val()).cut(slot.val()).clean()
        lug_centers.append([outer+side*6,y,z])
    assert body.isValid() and len(body.Solids())==1
    assert plate.val().isValid() and len(plate.val().Solids())==1
    return body,plate,{
        'exit_side':'far outer end' if i==1 else 'loading outer end',
        'exit_center_mm':[outer,yc,5.0],
        'nominal_bundle_envelope_mm':[6.0,4.0],
        'rounded_tunnel_envelope_mm':[7.0,5.0],
        'tunnel_corner_radius_mm':.6,
        'cover_edge_saddle_clearance_mm':.3,
        'cover_release_direction':[0,0,-1],
        'zip_tie_nominal_width_mm':2.5,
        'zip_tie_slot_mm':[3.2,1.8],
        'zip_tie_threading_channel_length_mm':20.0,
        'zip_tie_lug_centers_mm':lug_centers,
        'service':'Lay the cable into the open cover-edge groove, then close the panel. The tunnel captures with clearance; it must not crush insulation. Keep ties and wiring on the shell when removing the panel.',
        'qualification':'Actual fan lead, plug connector, bend radius and tie head are not modeled. Fit the intended fan and cable before fixing a route.',
    }
