#!/usr/bin/env python3
"""Independent V4-to-V5 comparison: V5 must equal V4 split, shifted and filled.

This check does not reuse the V5 builder's face-extrusion filler.  It rebuilds
the expected V5 solid from the frozen V4 STEP with explicit half-space boxes
and an explicit unleaned deck box, then requires zero symmetric difference.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import cadquery as cq
import trimesh


ROOT = Path(__file__).resolve().parents[3]
V2 = ROOT / "work/quartet-team/geometry/profile-v2"
sys.path.insert(0, str(V2))
import build_native_datum_coupon_v2 as v2

WIDTH_MM = 24.0
X0_MM = (38.1 - WIDTH_MM) / 2.0
SHIFT_MM = 3.5
PAIRS = {
    "A_R1_full_rail_plus_3p5mm": ("A_R1_full_native_rail", 1),
    "B_R2_full_rail_plus_3p5mm": ("B_R2_full_native_rail", 2),
    "C_R2_full_rail_plus_3p5mm_plus_1mm_seat_relief": ("C_R2_full_rail_plus_1mm_seat_relief", 3),
}


def section_signature(mesh: trimesh.Trimesh, z: float) -> dict:
    """Scipy-free planar section signature: loop count and per-loop perimeter."""
    segments = trimesh.intersections.mesh_plane(mesh, [0, 0, 1], [0, 0, z])
    assert len(segments) > 0
    key = lambda point: (round(float(point[0]), 5), round(float(point[1]), 5))
    parent = {}
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    lengths = []
    for start, end in segments:
        a, b = key(start), key(end)
        parent.setdefault(a, a); parent.setdefault(b, b)
        parent[find(a)] = find(b)
        lengths.append((a, math.dist(start[:2], end[:2])))
    per_loop = {}
    for a, length in lengths:
        root = find(a); per_loop[root] = per_loop.get(root, 0.0) + float(length)
    perimeters = sorted(per_loop.values())
    return {"z_mm": z, "closed_paths": len(perimeters), "perimeter_mm": float(sum(perimeters)), "loop_perimeters_mm": perimeters}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--d8", type=Path, default=Path("F:/Code/5680-dock-fit-20260917/desk-dock/D8"))
    args = parser.parse_args()
    params = json.loads((args.d8 / "parameters.json").read_text(encoding="utf-8"))
    profile = json.loads((args.d8 / "quick-fit/R2/seat-profile.json").read_text(encoding="utf-8"))
    thickness, seat_z, lean = float(params["laptop_thickness"]), float(params["rear_case_seat_z"]), float(params["laptop_lean_deg"])
    angle = math.radians(-lean)
    normal = cq.Vector(0.0, math.cos(angle), math.sin(angle))
    seat_end = max(float(y) for y, _ in profile["revised_yz_mm"])
    split = (seat_end + thickness / 2.0) / 2.0

    def lean_shape(shape):
        return shape.rotate((0, 0, seat_z), (1, 0, seat_z), -lean)

    big = 400.0
    minus_box = lean_shape(v2.box(X0_MM - 1, split - big, -big, WIDTH_MM + 2, big, 2 * big))
    plus_box = lean_shape(v2.box(X0_MM - 1, split, -big, WIDTH_MM + 2, big, 2 * big))
    deck_filler = lean_shape(v2.box(X0_MM, split, 46.0, WIDTH_MM, SHIFT_MM, 5.0))  # explicit unleaned deck box
    rail_moved = lean_shape(v2.prism([(thickness / 2, 48), (thickness / 2 + 4, 48), (thickness / 2 + 4, 134), (thickness / 2, 134)], WIDTH_MM, X0_MM)).translate(normal * SHIFT_MM)
    channel = lean_shape(v2.box(X0_MM, thickness / 2, 51.001, WIDTH_MM, SHIFT_MM, 83.0))

    results = {}
    for v5_name, (v4_name, count) in PAIRS.items():
        v4 = cq.importers.importStep(str(ROOT / "work/quartet-team/geometry/profile-v4/generated" / f"{v4_name}.step")).val()
        v5 = cq.importers.importStep(str(ROOT / "work/quartet-team/geometry/profile-v5/generated" / f"{v5_name}.step")).val()
        expected = v4.intersect(minus_box).fuse(v4.intersect(plus_box).translate(normal * SHIFT_MM)).fuse(deck_filler).clean()
        difference = expected.cut(v5).Volume() + v5.cut(expected).Volume()
        mesh = trimesh.load_mesh(ROOT / "work/quartet-team/geometry/profile-v5/generated" / f"{v5_name}_X_to_print_Z.stl")
        sections = [section_signature(mesh, z) for z in (0.2, 12.0, 23.8)]
        reference = sections[0]
        invariant = all(item["closed_paths"] == reference["closed_paths"] and abs(item["perimeter_mm"] - reference["perimeter_mm"]) < 1e-6 and all(abs(a - b) < 1e-6 for a, b in zip(item["loop_perimeters_mm"], reference["loop_perimeters_mm"])) for item in sections[1:])
        result = {
            "v4_source": v4_name,
            "expected_vs_v5_symmetric_difference_mm3": difference,
            "v5_minus_v4_volume_mm3": v5.Volume() - v4.Volume(),
            "expected_added_volume_mm3": WIDTH_MM * SHIFT_MM * 5.0,
            "rail_retained_at_moved_position_mm3": v5.intersect(rail_moved).Volume(),
            "new_channel_intersection_mm3": v5.intersect(channel).Volume(),
            "id_hole_rings_in_print_section": reference["closed_paths"] - 1,
            "expected_id_holes": count,
            "step_valid": v5.isValid(), "step_solids": len(v5.Solids()),
            "stl_section_signatures": sections, "stl_section_invariant": invariant,
        }
        assert result["expected_vs_v5_symmetric_difference_mm3"] < 1e-6, result
        assert abs(result["v5_minus_v4_volume_mm3"] - result["expected_added_volume_mm3"]) < 1e-5, result
        assert abs(result["rail_retained_at_moved_position_mm3"] - 8256.0) < 1e-5
        assert result["new_channel_intersection_mm3"] < 1e-6
        assert result["id_hole_rings_in_print_section"] == count
        assert result["step_valid"] and result["step_solids"] == 1 and result["stl_section_invariant"]
        results[v5_name] = result
    report = {
        "passed": True,
        "purpose": "Independent V5 geometry comparison: each V5 STEP equals the frozen V4 STEP split on the rail-side plane, its rail side translated 3.5 mm along the leaned rail normal, plus an explicit 24 x 3.5 x 5 mm unleaned deck box. No slicer, print, fit, force, airflow, CFD or solver conclusion.",
        "split_plane_unleaned_y_mm": split, "shift_vector_mm": [0.0, normal.y * SHIFT_MM, normal.z * SHIFT_MM],
        "checks": results,
        "scope_limit": "V5 remains analysis-only until the fixed-placement Orca G-code audits in this folder pass.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "output": str(args.output)}))


if __name__ == "__main__":
    main()
