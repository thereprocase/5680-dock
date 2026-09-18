#!/usr/bin/env python3
"""Independent V3-to-V4 contact/identifier comparison; writes one receipt."""

from __future__ import annotations

import argparse
import json
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
VARIANTS = {
    "A_R1_full_native_rail": (1, [(-2.5, 49.0, 0.48, 0.7)], [(-5.0, 47.8, 2.0, 2.0)]),
    "B_R2_full_native_rail": (2, [(-2.5 + index * 1.05, 49.0, 0.48, 0.7) for index in range(2)], [(-5.0 + index * 4.0, 47.8, 2.0, 2.0) for index in range(2)]),
    "C_R2_full_rail_plus_1mm_seat_relief": (3, [(-2.5 + index * 1.05, 49.0, 0.48, 0.7) for index in range(3)], [(-5.0 + index * 4.0, 47.8, 2.0, 2.0) for index in range(3)]),
}


def symmetric_difference(a: cq.Shape, b: cq.Shape) -> float:
    return a.cut(b).Volume() + b.cut(a).Volume()


def source_rail_and_relief() -> tuple[cq.Shape, cq.Shape]:
    d8 = Path("/mnt/f/Code/5680-dock-fit-20260917/desk-dock/D8")
    parameters = json.loads((d8 / "parameters.json").read_text(encoding="utf-8"))
    profile = json.loads((d8 / "quick-fit/R2/seat-profile.json").read_text(encoding="utf-8"))
    thickness, seat_z, lean = parameters["laptop_thickness"], parameters["rear_case_seat_z"], parameters["laptop_lean_deg"]
    rail = v2.prism([(thickness / 2, 48), (thickness / 2 + 4, 48), (thickness / 2 + 4, 134), (thickness / 2, 134)], WIDTH_MM, X0_MM)
    rail = rail.rotate((0, 0, seat_z), (1, 0, seat_z), -lean)
    relief = v2.r2_relief_ring(profile["revised_yz_mm"], X0_MM, seat_z, lean)
    return rail, relief


def section_signature(mesh: trimesh.Trimesh, z: float) -> dict:
    section = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    assert section is not None
    planar, _ = section.to_planar()
    areas = []
    for path in planar.discrete:
        area = sum(path[index, 0] * path[(index + 1) % len(path), 1] - path[(index + 1) % len(path), 0] * path[index, 1] for index in range(len(path))) / 2
        areas.append(abs(float(area)))
    return {"z_mm": z, "closed_paths": len(planar.discrete), "perimeter_mm": float(planar.length), "ring_areas_mm2": sorted(areas)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rail, relief = source_rail_and_relief()
    results = {}
    for name, (count, v3_holes, v4_holes) in VARIANTS.items():
        v3 = cq.importers.importStep(str(ROOT / "work/quartet-team/geometry/profile-v3/generated" / f"{name}.step")).val()
        v4 = cq.importers.importStep(str(ROOT / "work/quartet-team/geometry/profile-v4/generated" / f"{name}.step")).val()
        restored_v3, restored_v4 = v3, v4
        for y, z, dy, dz in v3_holes:
            restored_v3 = restored_v3.fuse(v2.box(X0_MM, y, z, WIDTH_MM, dy, dz)).clean()
        new_holes = []
        for y, z, dy, dz in v4_holes:
            hole = v2.box(X0_MM, y, z, WIDTH_MM, dy, dz)
            new_holes.append(hole)
            restored_v4 = restored_v4.fuse(hole).clean()
        halos = [v2.box(X0_MM, y - 1.0, z - 1.0, WIDTH_MM, 4.0, 4.0) for y, z, _, _ in v4_holes]
        mesh = trimesh.load_mesh(ROOT / "work/quartet-team/geometry/profile-v4/generated" / f"{name}_X_to_print_Z.stl")
        sections = [section_signature(mesh, z) for z in (0.2, 12.0, 23.8)]
        reference = sections[0]
        invariant = all(item["closed_paths"] == reference["closed_paths"] and abs(item["perimeter_mm"] - reference["perimeter_mm"]) < 1e-9 and all(abs(a - b) < 1e-9 for a, b in zip(item["ring_areas_mm2"], reference["ring_areas_mm2"])) for item in sections[1:])
        result = {
            "restored_v3_vs_restored_v4_symmetric_difference_mm3": symmetric_difference(restored_v3, restored_v4),
            "v4_id_removed_by_restore_mm3": restored_v4.Volume() - v4.Volume(),
            "expected_id_removed_mm3": count * 96.0,
            "rail_retained_v4_mm3": v4.intersect(rail).Volume(),
            "new_hole_rail_intersection_mm3": [hole.intersect(rail).Volume() for hole in new_holes],
            "new_hole_relief_intersection_mm3": [hole.intersect(relief).Volume() for hole in new_holes],
            "halo_outside_restored_source_mm3": [halo.cut(restored_v4).Volume() for halo in halos],
            "step_valid": v4.isValid(), "step_solids": len(v4.Solids()),
            "stl_section_signatures": sections, "stl_section_invariant": invariant,
        }
        assert result["restored_v3_vs_restored_v4_symmetric_difference_mm3"] < 1e-6
        assert abs(result["v4_id_removed_by_restore_mm3"] - result["expected_id_removed_mm3"]) < 1e-6
        assert abs(result["rail_retained_v4_mm3"] - 8256.0) < 1e-5
        assert all(value < 1e-6 for key in ("new_hole_rail_intersection_mm3", "new_hole_relief_intersection_mm3", "halo_outside_restored_source_mm3") for value in result[key])
        assert result["step_valid"] and result["step_solids"] == 1 and result["stl_section_invariant"]
        results[name] = result
    report = {
        "passed": True,
        "purpose": "Independent V4 geometry comparison against V3 with each revision's identifiers restored; no slicer, print, fit, force, airflow, CFD or solver conclusion.",
        "checks": results,
        "scope_limit": "V4 remains analysis-only until a fixed-placement actual Orca G-code audit proves the larger holes survive with a clear deposited-road core and surrounding walls.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "output": str(args.output)}))


if __name__ == "__main__":
    main()
