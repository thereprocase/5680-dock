"""Replaceable fan top clips, printed on a broad YZ side with X as build height.

Each clip closes the top without a tall return on the large grille. A rear hook
locks into a shell ear. Two long compliant leaves take up nominal fan clearance;
local contact shoes follow the selected bare/padded fan stack. The production
export uses the unloaded shape in PRINT_OVERRIDES, not its assembly pose.
"""
import cadquery as cq


def add_top_clips(i,fx,roof,fanpose,box,add,guard_front,fan_envelope_front,back):
    contacts=[];free_shapes={};positions=[]
    for j,x in enumerate([fx-52.5,fx+52.5],1):
        # Anchors live outside the airflow aperture, behind the frame corners.
        ear=box(x-5,138,back+.1,10,17,6.5)
        ear=ear.cut(box(x-5.2,142.9,back+5.2,10.4,2.2,1.6))
        roof=roof.union(fanpose(ear))
        # The existing sloping duct crown reaches behind the fan above the
        # nominal top. A local clearance notch keeps the removable cap free.
        roof=roof.cut(fanpose(box(x-4.3,155.4,guard_front-2.2,8.6,2.8,
                                  back+9.4-(guard_front-2.2))))
        def clip(unloaded):
            xf=x-4
            z0=guard_front-1.8
            shape=box(xf,155.8,z0,8,2.0,back+9-z0)
            # The front leg prevents a grille lifting past the installed cap.
            shape=shape.union(box(xf,150.5,z0,8,7.3,1.4))
            # This 13 mm snap leg deflects outward to clear the rear ear.
            shape=shape.union(box(xf,142.8,back+7,8,15,1.6))
            shape=shape.union(box(xf,143.2,back+5.6,8,1.6,3))
            # Smooth inclined beams have no sacrificial crush fit. Their bending
            # remains in the print plane when the clip is printed on its side.
            ty=150.4 if unloaded else 151.2
            top=[(155.8,back-1),(155.8,back-2.5),
                 (ty,8),(ty+.8,7.5),(156.6,back-2.5),(156.6,back-1)]
            leaf=cq.Workplane('YZ',origin=(xf,0,0)).polyline(top).close().extrude(8)
            shape=shape.union(leaf)
            # Axial leaf contacts the selected frame/pad stack at a corner. A
            # different fan depth changes this small replaceable clip only.
            tip=fan_envelope_front+(.30 if unloaded else -.15)
            ax=[(156.6,fan_envelope_front-2.3),(156.6,fan_envelope_front-1.5),
                (140.5,tip),(140.5,tip-.8)]
            leaf=cq.Workplane('YZ',origin=(xf,0,0)).polyline(ax).close().extrude(8)
            return shape.union(leaf).clean()
        nominal=clip(False);unloaded=clip(True)
        assert nominal.val().isValid() and len(nominal.val().Solids())==1
        assert unloaded.val().isValid() and len(unloaded.val().Solids())==1
        name=f'{i:02}_fan_top_clip_{j}'
        add(name,fanpose(nominal),(93,125,116),False)
        free_shapes[name]=fanpose(unloaded)
        contacts.append(fanpose(box(x-4.2,139.8,fan_envelope_front-.2,8.4,13,1.2)).val())
        positions.append([x,155.8,back])
    return roof,{
        'count':2,'material':'PETG','print_pose':'Broad YZ side down; extruded X width is 8 mm build height.',
        'unloaded_export_required':True,'unloaded_shape_registry':'fan_service.PRINT_OVERRIDES',
        'retention':'Rear snap hook in an open shell-ear notch; lift rear release leg before removing clip.',
        'grille_return_removed':True,'top_leaf_nominal_deflection_mm':.8,
        'axial_leaf_nominal_deflection_mm':.45,'leaf_thickness_mm':.8,
        'axial_contact_envelope_front_z_mm':fan_envelope_front,
        'positions_fan_local_mm':positions,
        'limits':'Nominal geometry and low-strain design intent only. Measure actual fan/pads, fit coupons, warm dwell, vibration and repeated service; no measured clamp force claimed.',
        'seal':'No full fan gasket required. Overlapping rigid duct/frame seat limits direct bypass; optional small corner damping patches remain a fit choice.'
    },contacts,free_shapes
