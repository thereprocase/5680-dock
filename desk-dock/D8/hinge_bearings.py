"""Intermediate bearing bridges across each inlet, in the laptop's leaned frame.

The nominal straight hinge datum follows the central relief in D8's reference
envelope, not the curved end-seat profile. Physical contact still needs fitting.
"""
import cadquery as cq


def add_hinge_bearings(p, mouth_records, box, leaned, add):
    cfg = p['hinge_bearings']
    width = cfg['bridge_width_mm']
    y0, y1 = cfg['contact_y_bounds_mm']
    top = p['rear_case_seat_z'] + cfg['straight_edge_offset_mm']
    lead = cfg['sliding_chamfer_mm']
    assert 0 < lead < width/2
    records = []
    for mouth in mouth_records:
        lo, hi = mouth['construction_x_bounds']
        module = mouth['module']
        for j, fraction in enumerate(cfg['fractions'], 1):
            x = lo + fraction * (hi - lo)
            # Full cross-slot bridge overlaps both deck banks. The shallow
            # central pedestal reaches the straight edge inside the relief.
            bridge = box(x-width/2, -14, 46, width, 28, 4)
            pedestal = box(x-width/2, y0, 49.8, width, y1-y0, top-49.8)
            pedestal = pedestal.edges('|Y and >Z').chamfer(lead)
            support = bridge.union(pedestal).val()
            name = f'{module:02}_hinge_bridge_{j}'
            # These are already leaned, and are fused into the final shells.
            add(name, leaned(support))
            records.append(dict(module=module, fraction=fraction, x_mm=x,
                bridge_width_mm=width, contact_top_local_z_mm=top,
                contact_material='Printed shell, no liner',
                sliding_chamfer_mm=lead, structural_part=name))
    return records
