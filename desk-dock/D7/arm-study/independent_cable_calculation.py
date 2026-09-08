"""Independent source-based cable kinematics and notched-carrier sensitivity.

No production CAD imports/rebuilds. This is not FEA, a contact solve, an
actual flexible-cable model, or physical qualification. All lengths are mm.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
p = json.loads((HERE.parent / "parameters.json").read_text(encoding="utf-8"))
ba = p["breakaway"]
P = p["rear_case_seat_z"] + p["port_from_rear_case"]
PX = ba["pivot_x_mm"]
PZ = P + ba["pivot_above_port_mm"]
K = (2 * ba["nominal_E_MPa"] * ba["spring_width_mm"]
     * ba["spring_thickness_mm"] ** 3 / ba["spring_leaf_length_mm"] ** 3)
T = ba["nominal_release_N"] * ba["pivot_above_port_mm"]


def lift(angle_deg):
    pre = ba["spring_preload_deflection_mm"]
    return min(ba["cam_rise_mm"],
               math.sqrt(pre ** 2 + 2 * T * abs(math.radians(angle_deg)) / K) - pre)


def fold(point, angle_deg):
    """Unleaned frame: rigid +Y rotation followed by axial cam translation."""
    a = math.radians(angle_deg)
    x, y, z = point
    return (PX + (x - PX) * math.cos(a) + (z - PZ) * math.sin(a),
            y - lift(angle_deg),
            PZ - (x - PX) * math.sin(a) + (z - PZ) * math.cos(a))


def bounds(points):
    return {axis: [min(v[i] for v in points), max(v[i] for v in points)]
            for i, axis in enumerate(("x_mm", "y_mm", "z_mm"))}


def cable_path(dy=0, dz=0, dx=0, include_tail=True):
    """Sample exactly the provisional path in make_rear_cable_keepout()."""
    cy, cz = p["port_y"] + dy, P + dz
    cx = -26.5 + dx
    points = [(cx + (-77 - cx) * n / 120, cy, cz) for n in range(121)]
    # R30 quarter turn centered at X=-77, Z=cz-30.
    for n in range(1, 241):
        a = math.pi / 2 * n / 240
        points.append((-77 - 30 * math.sin(a), cy, cz - 30 + 30 * math.cos(a)))
    if include_tail:
        points += [(-107, cy, cz - 30 - 30 * n / 120) for n in range(1, 121)]
    return points


def j_rectangle(a, b):
    a, b = max(a, b), min(a, b)
    return a * b ** 3 * (1 / 3 - .21 * (b / a) * (1 - b ** 4 / (12 * a ** 4)))


J_INTACT = sum(j_rectangle(a, b) for a, b in [(46.1, 7), (35.5, 7.8), (35.5, 7.6)])
J_WEB = j_rectangle(39, 7.8)
SPAN = 18.85  # Shelf top P-18.7 to circular hub bottom P+0.15.


def local_torsion(E, dy, dz, flare_band):
    # Positive web centerline retains the historical conservative eccentricity.
    e = 21.9 - (p["port_y"] + dy)
    # Lower intact band ends at trough/flare bottom. The actual flare only
    # affects part of wall thickness; using its full height is a sensitivity.
    radius = 6.25 if flare_band else 4.25
    weak_length = min(SPAN, max(0, .15 - (dz - radius)))
    G = E / (2 * (1 + .38))
    delta = 20 * e ** 2 / G * ((SPAN - weak_length) / J_INTACT + weak_length / J_WEB)
    return dict(E_MPa=E, load_N=20, dy_mm=dy, dz_mm=dz,
                affected_band="whole flare height" if flare_band else "plain trough height",
                weak_length_mm=weak_length, local_axial_torsion_proxy_mm=delta)


angle = ba["fold_angle_deg"]
nominal_path = cable_path()
near_path = cable_path(include_tail=False)
samples = []
for theta in (0, .1, 1, 2, 3, 3.112, 5, 15, 30, angle):
    samples.append(dict(angle_deg=theta, cam_lift_mm=lift(theta),
                        tip_mm=fold((5.15, p["port_y"], P), theta),
                        rear_outlet_mm=fold((-47, p["port_y"], P), theta)))
swept = [fold(q, theta / 4) for theta in range(int(angle * 4) + 1) for q in nominal_path]
corner_folded = [fold(q, angle) for dy in p["lateral_range"]
                 for dz in p["height_range"] for dx in p["depth_range"]
                 for q in cable_path(dy, dz, dx)]
data = {
    "scope": "Source-derived unleaned kinematics and local torsion sensitivity; no CAD collision, flexible cable, contact, or complete-holder solve.",
    "reference_geometry": {"P_mm": P, "pivot_x_mm": PX, "pivot_z_mm": PZ,
                           "provisional_cable_diameter_mm": 6.5,
                           "screening_diameter_mm": 8, "straight_after_wall_mm": 30,
                           "illustrative_bend_radius_mm": 30, "tail_after_arc_mm": 30},
    "kinematic_samples": samples,
    "nominal_ready_centerline_bounds": bounds(nominal_path),
    "nominal_folded_centerline_bounds": bounds([fold(q, angle) for q in nominal_path]),
    "nominal_folded_straight_plus_arc_only_bounds": bounds([fold(q, angle) for q in near_path]),
    "nominal_sampled_sweep_centerline_bounds": bounds(swept),
    "all_adjustment_corners_folded_centerline_bounds": bounds(corner_folded),
    "sweep_limits": "0.25 degree angle samples; path samples <=0.5 mm. Bounds omit cable radius. Actual flexible slack must keep its far endpoint fixed; this rigid moving keepout is only a screening envelope.",
    "carrier_proxy": {
        "bare_span_mm": SPAN, "intact_J_mm4": J_INTACT, "positive_web_J_mm4": J_WEB,
        "formula": "delta = F*e^2/G * ((span-weak)/J_intact + weak/J_web)",
        "cases": [local_torsion(E, dy, dz, flare) for E in (800, 1200, 1800)
                  for dy, dz in [(0, 0), (0, -4), (-3, 0), (-3, -4)]
                  for flare in (False, True)],
        "limits": "Segmented open-section torsion proxy; not a rigorous bound. Retained material, shear center, transition/warping and other holder compliance are unresolved. Removed volume does not determine stiffness."
    },
    "complete_holder_target_qualified": False
}
out = HERE / "independent_cable_results.json"
out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(out), "folded_centerline_bounds": data["nominal_folded_centerline_bounds"],
                  "E800_local_proxy": data["carrier_proxy"]["cases"][:8]}, indent=2))
