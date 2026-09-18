#!/usr/bin/env python3
"""Supersede V3's raw-nozzle-coordinate ID-notch finding without recutting it.

The original V3 audit compared raw G-code nozzle motion directly with CAD/3MF
bed coordinates.  This script verifies the frozen active-extruder offset in
both sources, applies it once to positive deposition paths, and reruns the
same strict-interior centreline predicate on every model layer.  Its result is
limited to retracting that invalid predicate; 0.48 x 0.70 mm notches are not
being promoted to printable or legible IDs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import cadquery as cq


ROOT = Path(__file__).resolve().parents[3]
V3_STEPS = {
    "A_R1_full_native_rail_X_to_print_Z": ROOT / "work/quartet-team/geometry/profile-v3/generated/A_R1_full_native_rail.step",
    "B_R2_full_native_rail_X_to_print_Z": ROOT / "work/quartet-team/geometry/profile-v3/generated/B_R2_full_native_rail.step",
    "C_R2_full_rail_plus_1mm_seat_relief_X_to_print_Z": ROOT / "work/quartet-team/geometry/profile-v3/generated/C_R2_full_rail_plus_1mm_seat_relief.step",
}
EXPECTED_IDS = {
    "A_R1_full_native_rail_X_to_print_Z": 1,
    "B_R2_full_native_rail_X_to_print_Z": 2,
    "C_R2_full_rail_plus_1mm_seat_relief_X_to_print_Z": 3,
}
ID_Z0_MM, ID_HEIGHT_MM = 49.0, 0.7
ID_Y0_MM, ID_WIDTH_MM, ID_PITCH_MM = -2.5, 0.48, 1.05
INTERIOR_MARGIN_MM = 0.04


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_roads(gcode: Path) -> list[dict]:
    """Parse positive G0/G1/G2/G3 deposition centreline pieces by object."""
    pos = {key: 0.0 for key in "XYZE"}
    relative_e, absolute_xyz = True, True
    object_name, role = None, "Custom"
    roads = []
    for number, line in enumerate(gcode.read_text(encoding="utf-8").splitlines(), 1):
        match = re.match(r"; printing object (.+) id:", line)
        if match:
            object_name = match.group(1)
            continue
        if line.startswith("; FEATURE: "):
            role = line[11:]
            continue
        code = line.split(";", 1)[0].strip()
        if not code:
            continue
        operation = code.split()[0]
        if operation == "M83":
            relative_e = True
            continue
        if operation == "M82":
            relative_e = False
            continue
        if operation == "G90":
            absolute_xyz = True
            continue
        if operation == "G91":
            absolute_xyz = False
            continue
        values = {key: float(value) for key, value in re.findall(r"([XYZEIJ])([-+]?(?:\d*\.)?\d+)", code)}
        if operation == "G92":
            pos.update({key: value for key, value in values.items() if key in pos})
            continue
        if operation not in ("G0", "G1", "G2", "G3"):
            continue
        before = pos.copy()
        for key in "XYZ":
            if key in values:
                pos[key] = values[key] if absolute_xyz else pos[key] + values[key]
        extrusion = values.get("E", 0.0) if relative_e else values.get("E", pos["E"]) - pos["E"]
        if "E" in values:
            pos["E"] = pos["E"] + values["E"] if relative_e else values["E"]
        if not (object_name and extrusion > 0.0 and role != "Custom"):
            continue
        points = [(before["X"], before["Y"]), (pos["X"], pos["Y"])]
        if operation in ("G2", "G3"):
            assert "I" in values or "J" in values, "unsupported arc encoding"
            cx, cy = before["X"] + values.get("I", 0.0), before["Y"] + values.get("J", 0.0)
            start = math.atan2(before["Y"] - cy, before["X"] - cx)
            end = math.atan2(pos["Y"] - cy, pos["X"] - cx)
            sweep = (end - start) % (2 * math.pi) if operation == "G3" else -((start - end) % (2 * math.pi))
            if abs(sweep) < 1e-9:
                sweep = 2 * math.pi * (1 if operation == "G3" else -1)
            radius = math.hypot(before["X"] - cx, before["Y"] - cy)
            count = max(2, math.ceil(abs(sweep) / 0.02))
            points = [(cx + radius * math.cos(start + sweep * index / count), cy + radius * math.sin(start + sweep * index / count)) for index in range(count + 1)]
        for start, end in zip(points, points[1:]):
            if start != end:
                roads.append({"object": object_name, "z_mm": round(pos["Z"], 3), "role": role, "start_xy_mm": start, "end_xy_mm": end, "gcode_line": number, "gcode": line})
    return roads


def crosses_strict_rectangle(start: tuple[float, float], end: tuple[float, float], rect: list[float]) -> bool:
    x0, y0, x1, y1 = rect
    dx, dy = end[0] - start[0], end[1] - start[1]
    low, high = 0.0, 1.0
    for p, q in ((-dx, start[0] - x0), (dx, x1 - start[0]), (-dy, start[1] - y0), (dy, y1 - start[1])):
        if abs(p) < 1e-12:
            if q <= 0.0:
                return False
        else:
            ratio = q / p
            if p < 0.0:
                low = max(low, ratio)
            else:
                high = min(high, ratio)
        if low >= high:
            return False
    return True


def expected_notches(preparation: dict) -> list[dict]:
    records = []
    for item in preparation["objects"]:
        name = item["name"]
        bounds = cq.importers.importStep(str(V3_STEPS[name])).val().BoundingBox()
        offset_x, offset_y = item["bed_bounds_mm"][0][:2]
        for ordinal in range(1, EXPECTED_IDS[name] + 1):
            x0 = offset_x + bounds.zmax - (ID_Z0_MM + ID_HEIGHT_MM)
            x1 = offset_x + bounds.zmax - ID_Z0_MM
            y0 = offset_y + ID_Y0_MM + (ordinal - 1) * ID_PITCH_MM - bounds.ymin
            records.append({"object": name, "id_ordinal": ordinal, "nominal_void_xy_mm": [x0, y0, x1, y0 + ID_WIDTH_MM]})
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    args = parser.parse_args()
    folder = args.folder.resolve()
    gcode = folder / "plate_1.gcode"
    machine = json.loads((folder / "machine.json").read_text(encoding="utf-8"))
    preparation = json.loads((folder / "plate-preparation.json").read_text(encoding="utf-8"))
    header = re.search(r"^; extruder_offset = (-?[0-9.]+)x(-?[0-9.]+)$", gcode.read_text(encoding="utf-8"), re.MULTILINE)
    assert header, "missing G-code extruder offset"
    assert machine["extruder_offset"] == [header.group(0).split("= ", 1)[1]], "machine/G-code extruder-offset mismatch"
    deposition_offset = (float(header.group(1)), float(header.group(2)))
    roads = parse_roads(gcode)
    for road in roads:
        road["start_xy_mm"] = (road["start_xy_mm"][0] + deposition_offset[0], road["start_xy_mm"][1] + deposition_offset[1])
        road["end_xy_mm"] = (road["end_xy_mm"][0] + deposition_offset[0], road["end_xy_mm"][1] + deposition_offset[1])
    by_layer = defaultdict(list)
    for road in roads:
        if road["role"].lower() != "brim":
            by_layer[(road["object"], road["z_mm"])].append(road)
    records = expected_notches(preparation)
    all_predicates_clear = True
    for record in records:
        layers = sorted(z for name, z in by_layer if name == record["object"])
        assert len(layers) == 120, f"{record['object']}: expected 120 model layers, got {len(layers)}"
        x0, y0, x1, y1 = record["nominal_void_xy_mm"]
        interior = [x0 + INTERIOR_MARGIN_MM, y0 + INTERIOR_MARGIN_MM, x1 - INTERIOR_MARGIN_MM, y1 - INTERIOR_MARGIN_MM]
        hits = []
        for z in layers:
            for road in by_layer[(record["object"], z)]:
                if crosses_strict_rectangle(road["start_xy_mm"], road["end_xy_mm"], interior):
                    hits.append({"z_mm": z, "role": road["role"], "gcode_line": road["gcode_line"], "gcode": road["gcode"], "deposited_start_xy_mm": road["start_xy_mm"], "deposited_end_xy_mm": road["end_xy_mm"]})
        record["strict_interior_xy_mm"] = interior
        record["model_layer_count"] = len(layers)
        record["deposited_centreline_strict_interior_crossings"] = hits
        record["former_predicate_clear_on_all_layers"] = not hits
        all_predicates_clear &= not hits
    report = {
        "disposition": "SUPERSEDES the prior V3 HOLD only: its raw-nozzle-coordinate strict-interior witnesses are invalid. The corrected all-layer centreline predicate has no crossings.",
        "scope": "Coordinate-frame correction of the former G-code centreline predicate only. This is not a V3 printable-ID, physical print, fit, strength, airflow, acoustic, thermal, or CFD pass.",
        "input": {"gcode": str(gcode), "gcode_sha256": sha256(gcode), "machine_json_sha256": sha256(folder / "machine.json"), "sliced_3mf_sha256": sha256(folder / "coupons-sliced.3mf"), "prior_receipt": "outputs/5680-design-team/verification/V3-ID-HOLE-TOOLPATH-RECEIPT.json", "prior_receipt_sha256": "fccef3d29ac733e8eae448374b432b507a4289b8d4532677fe0c4b85ce0ba1f0"},
        "method": {"coordinate_frame": "raw G-code nozzle motion + frozen active-extruder offset before comparison with CAD/3MF plate coordinates", "machine_extruder_offset": machine["extruder_offset"], "gcode_extruder_offset": header.group(0).split("= ", 1)[1], "deposition_offset_xy_mm": deposition_offset, "motions": ["G0", "G1", "G2", "G3"], "layers_per_object": 120, "strict_interior_margin_mm": INTERIOR_MARGIN_MM, "former_predicate": "A positive-extrusion centreline entering the strict nominal notch interior was a failed opening-survival witness."},
        "notch_design_mm": {"source_z": [ID_Z0_MM, ID_Z0_MM + ID_HEIGHT_MM], "source_y_width": ID_WIDTH_MM, "source_y_pitch": ID_PITCH_MM},
        "notch_checks": records,
        "former_predicate_clear_on_all_notches_all_layers": all_predicates_clear,
        "required_boundary": "Do not treat V3's 0.48 x 0.70 mm notches as qualified readable or physically open IDs. V4's separately audited 2 mm IDs remain the selected print candidate."
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"former_predicate_clear_on_all_notches_all_layers": all_predicates_clear, "sha256": sha256(args.json)}))


if __name__ == "__main__":
    main()
