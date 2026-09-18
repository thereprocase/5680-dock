#!/usr/bin/env python3
"""Fail-closed all-layer, road-width-aware audit for V5's 2-mm through IDs."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path

import cadquery as cq
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
STEPS = {
    "A_R1_full_rail_plus_3p5mm_X_to_print_Z": ROOT / "work/quartet-team/geometry/profile-v5/generated/A_R1_full_rail_plus_3p5mm.step",
    "B_R2_full_rail_plus_3p5mm_X_to_print_Z": ROOT / "work/quartet-team/geometry/profile-v5/generated/B_R2_full_rail_plus_3p5mm.step",
    "C_R2_full_rail_plus_3p5mm_plus_1mm_seat_relief_X_to_print_Z": ROOT / "work/quartet-team/geometry/profile-v5/generated/C_R2_full_rail_plus_3p5mm_plus_1mm_seat_relief.step",
}
ID_STARTS = {
    "A_R1_full_rail_plus_3p5mm_X_to_print_Z": [-5.0],
    "B_R2_full_rail_plus_3p5mm_X_to_print_Z": [-5.0, -1.0],
    "C_R2_full_rail_plus_3p5mm_plus_1mm_seat_relief_X_to_print_Z": [-5.0, -1.0, 3.0],
}
ID_Z0, ID_SIDE, CORE_INSET = 47.8, 2.0, 0.5  # Original 1-mm square core requirement.
NS = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
PRODUCTION = "{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_paths(gcode: Path, default_width: float) -> list[dict]:
    """Parse G0/G1/G2/G3 positive roads, preserving arc geometry and width."""
    pos = {key: 0.0 for key in "XYZE"}
    relative_e, absolute_xyz = True, True
    object_name, role, width = None, "Custom", default_width
    roads = []
    for number, line in enumerate(gcode.read_text(encoding="utf-8").splitlines(), 1):
        match = re.match(r"; printing object (.+) id:", line)
        if match:
            object_name = match.group(1)
            continue
        if line.startswith("; FEATURE: "):
            role = line[11:]
            continue
        match = re.match(r"; LINE_WIDTH: ([0-9.]+)", line)
        if match:
            width = float(match.group(1))
            continue
        code = line.split(";", 1)[0].strip()
        if not code:
            continue
        operation = code.split()[0]
        if operation == "M83": relative_e = True; continue
        if operation == "M82": relative_e = False; continue
        if operation == "G90": absolute_xyz = True; continue
        if operation == "G91": absolute_xyz = False; continue
        values = {key: float(value) for key, value in re.findall(r"([XYZEIJ])([-+]?(?:\d*\.)?\d+)", code)}
        if operation == "G92":
            pos.update({key: value for key, value in values.items() if key in pos})
            continue
        if operation not in ("G0", "G1", "G2", "G3"):
            continue
        before = pos.copy()
        for key in "XYZ":
            if key in values: pos[key] = values[key] if absolute_xyz else pos[key] + values[key]
        extrusion = values.get("E", 0.0) if relative_e else values.get("E", pos["E"]) - pos["E"]
        if "E" in values: pos["E"] = pos["E"] + values["E"] if relative_e else values["E"]
        if not (object_name and extrusion > 0.0 and role != "Custom"):
            continue
        points = [(before["X"], before["Y"]), (pos["X"], pos["Y"])]
        if operation in ("G2", "G3"):
            assert "I" in values or "J" in values, "unsupported arc encoding"
            cx, cy = before["X"] + values.get("I", 0.0), before["Y"] + values.get("J", 0.0)
            start, end = math.atan2(before["Y"] - cy, before["X"] - cx), math.atan2(pos["Y"] - cy, pos["X"] - cx)
            sweep = (end - start) % (2 * math.pi) if operation == "G3" else -((start - end) % (2 * math.pi))
            if abs(sweep) < 1e-9: sweep = 2 * math.pi * (1 if operation == "G3" else -1)
            radius = math.hypot(before["X"] - cx, before["Y"] - cy)
            count = max(2, math.ceil(abs(sweep) / .02))
            points = [(cx + radius * math.cos(start + sweep * index / count),
                       cy + radius * math.sin(start + sweep * index / count))
                      for index in range(count + 1)]
        for start, end in zip(points, points[1:]):
            if start != end:
                roads.append({"object": object_name, "z_mm": round(pos["Z"], 3), "role": role, "width_mm": width, "start": start, "end": end, "line": number, "gcode": line})
    return roads


def point_segment_distance(point, start, end):
    dx, dy = end[0] - start[0], end[1] - start[1]
    length2 = dx * dx + dy * dy
    if length2 == 0.0: return math.dist(point, start)
    t = max(0.0, min(1.0, ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / length2))
    return math.dist(point, (start[0] + t * dx, start[1] + t * dy))


def segment_hits_rect(start, end, rect):
    x0, y0, x1, y1 = rect
    dx, dy = end[0] - start[0], end[1] - start[1]
    low, high = 0.0, 1.0
    for p, q in ((-dx, start[0] - x0), (dx, x1 - start[0]), (-dy, start[1] - y0), (dy, y1 - start[1])):
        if abs(p) < 1e-12:
            if q < 0.0: return False
        else:
            value = q / p
            if p < 0.0: low = max(low, value)
            else: high = min(high, value)
        if low > high: return False
    return True


def road_rect_clearance(road, rect):
    if segment_hits_rect(road["start"], road["end"], rect): return -road["width_mm"] / 2
    x0, y0, x1, y1 = rect
    corners = [(x0, y0), (x0, y1), (x1, y0), (x1, y1)]
    def point_rect_distance(point):
        return math.hypot(max(x0 - point[0], 0.0, point[0] - x1), max(y0 - point[1], 0.0, point[1] - y1))
    distance = min(point_rect_distance(road["start"]), point_rect_distance(road["end"]), *(point_segment_distance(corner, road["start"], road["end"]) for corner in corners))
    return distance - road["width_mm"] / 2


def actual_lower_bounds(folder: Path, project: Path, preparation: dict) -> dict:
    expected = {item["name"]: item["bed_bounds_mm"] for item in preparation["objects"]}
    with zipfile.ZipFile(project) as archive:
        settings = ET.fromstring(archive.read("Metadata/model_settings.config"))
        names = {item.get("id"): item.find("metadata[@key='name']").get("value") for item in settings.findall("object")}
        root = ET.fromstring(archive.read("3D/3dmodel.model"))
        result = {}
        for item in root.findall("m:build/m:item", NS):
            transform = [float(value) for value in item.get("transform").split()]
            assert transform[:9] == [1, 0, 0, 0, 1, 0, 0, 0, 1], "non-native orientation"
            name = names[item.get("objectid")]
            component = root.find(f"m:resources/m:object[@id='{item.get('objectid')}']/m:components/m:component", NS)
            assert component is not None and [float(value) for value in component.get("transform").split()] == [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
            mesh = ET.fromstring(archive.read(component.get(PRODUCTION + "path").lstrip("/")))
            vertices = [tuple(float(vertex.get(axis)) + transform[9 + index] for index, axis in enumerate(("x", "y", "z"))) for vertex in mesh.findall(".//m:vertices/m:vertex", NS)]
            bounds = [[min(vertex[index] for vertex in vertices) for index in range(3)], [max(vertex[index] for vertex in vertices) for index in range(3)]]
            assert all(abs(a - b) < 1e-4 for actual, wanted in zip(bounds, expected[name]) for a, b in zip(actual, wanted)), "Orca moved prepared object"
            # Orca centers each component mesh before applying this native
            # identity transform.  The validated world lower bound, not its
            # centered-mesh translation, is the origin for print_oriented's
            # source-minimum-normalized coordinate system.
            result[name] = bounds[0]
    assert set(result) <= set(STEPS) and result, sorted(result)
    return result


def expected_holes(lower_bounds: dict) -> list[dict]:
    result = []
    for name, starts in ID_STARTS.items():
        if name not in lower_bounds: continue
        bounds = cq.importers.importStep(str(STEPS[name])).val().BoundingBox()
        tx, ty, _ = lower_bounds[name]
        for ordinal, native_y in enumerate(starts, 1):
            nominal = [tx + bounds.zmax - (ID_Z0 + ID_SIDE), ty + native_y - bounds.ymin, tx + bounds.zmax - ID_Z0, ty + native_y - bounds.ymin + ID_SIDE]
            result.append({"object": name, "id": ordinal, "nominal_void_xy_mm": nominal, "required_clear_core_xy_mm": [nominal[0] + CORE_INSET, nominal[1] + CORE_INSET, nominal[2] - CORE_INSET, nominal[3] - CORE_INSET]})
    return result


def wall_sides(roads, nominal):
    x0, y0, x1, y1 = nominal
    probes = {"left": (x0, (y0 + y1) / 2), "right": (x1, (y0 + y1) / 2), "bottom": ((x0 + x1) / 2, y0), "top": ((x0 + x1) / 2, y1)}
    result = {}
    for side, probe in probes.items():
        candidates = []
        for road in roads:
            if "wall" not in road["role"].lower(): continue
            dx, dy = abs(road["end"][0] - road["start"][0]), abs(road["end"][1] - road["start"][1])
            if side in ("left", "right") and dy < dx: continue
            if side in ("bottom", "top") and dx < dy: continue
            candidates.append((point_segment_distance(probe, road["start"], road["end"]) - road["width_mm"] / 2, road))
        if candidates:
            clearance, road = min(candidates, key=lambda item: item[0])
            result[side] = {"edge_distance_mm": clearance, "witness_line": road["line"], "role": road["role"], "present": clearance <= .35}
        else:
            result[side] = {"edge_distance_mm": None, "witness_line": None, "role": None, "present": False}
    return result


def preview(records, layer_roads, output: Path) -> None:
    image = Image.new("RGB", (1500, 920), "#f7f8fa"); draw = ImageDraw.Draw(image); font = ImageFont.load_default()
    draw.text((24, 20), "V5 actual Orca deposited-coordinate ID through-hole audit", fill="#17364b", font=font)
    draw.text((24, 42), "Green = required 1-mm deposited-road-clear core; red = nominal CAD void; gray = actual deposited roads at the chosen mid-layer.", fill="#435765", font=font)
    for index, record in enumerate(records):
        column, row = index % 3, index // 3; left, top, width, height = 25 + column * 490, 95 + row * 400, 450, 340
        x0, y0, x1, y1 = record["nominal_void_xy_mm"]; bounds = (x0 - 1.6, y0 - 1.6, x1 + 1.6, y1 + 1.6); sx, sy = width / (bounds[2] - bounds[0]), height / (bounds[3] - bounds[1])
        def point(x, y): return (int(left + (x - bounds[0]) * sx), int(top + height - (y - bounds[1]) * sy))
        def clipped_point(x, y): return point(min(max(x, bounds[0]), bounds[2]), min(max(y, bounds[1]), bounds[3]))
        for road in layer_roads[record["object"]]:
            if max(road["start"][0], road["end"][0]) < bounds[0] or min(road["start"][0], road["end"][0]) > bounds[2] or max(road["start"][1], road["end"][1]) < bounds[1] or min(road["start"][1], road["end"][1]) > bounds[3]: continue
            draw.line((clipped_point(*road["start"]), clipped_point(*road["end"])), fill="#aeb9c2",
                      width=max(1, int(round(road["width_mm"] * min(sx, sy)))))
        a, b = point(x0, y0), point(x1, y1); draw.rectangle((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])), outline="#d63031", width=2)
        cx0, cy0, cx1, cy1 = record["required_clear_core_xy_mm"]; a, b = point(cx0, cy0), point(cx1, cy1); draw.rectangle((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])), outline="#118a42", width=3)
        draw.text((left, top - 18), f"{record['object'][0]}{record['id']}  selected Z={record['preview_z_mm']:g} mm", fill="#17364b", font=font)
    image.save(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, required=True); parser.add_argument("--json", type=Path, required=True); parser.add_argument("--png", type=Path, required=True)
    args = parser.parse_args(); folder = args.folder.resolve(); gcode = folder / "plate_1.gcode"; project = folder / "coupons-sliced.3mf"
    process = json.loads((folder / "process.json").read_text(encoding="utf-8")); machine = json.loads((folder / "machine.json").read_text(encoding="utf-8")); prep = json.loads((folder / "plate-preparation.json").read_text(encoding="utf-8"))
    assert str(process["enable_support"]) == "1"
    header_offset = re.search(r"^; extruder_offset = (-?[0-9.]+)x(-?[0-9.]+)$", gcode.read_text(encoding="utf-8"), re.MULTILINE)
    assert header_offset and machine["extruder_offset"] == [header_offset.group(0).split("= ", 1)[1]], "unverified G-code deposition offset"
    deposition_offset = (float(header_offset.group(1)), float(header_offset.group(2)))
    lower_bounds = actual_lower_bounds(folder, project, prep); roads = parse_paths(gcode, float(process["line_width"]))
    for road in roads:
        road["start"] = (road["start"][0] + deposition_offset[0], road["start"][1] + deposition_offset[1])
        road["end"] = (road["end"][0] + deposition_offset[0], road["end"][1] + deposition_offset[1])
    by_layer = defaultdict(list)
    for road in roads:
        if road["role"].lower() != "brim": by_layer[(road["object"], road["z_mm"])].append(road)
    records = [record for record in expected_holes(lower_bounds) if record['object'] in lower_bounds]; all_pass = True; preview_roads = {}
    for record in records:
        layers = sorted(z for name, z in by_layer if name == record["object"]); report_layers = []
        for z in layers:
            local = by_layer[(record["object"], z)]; core = record["required_clear_core_xy_mm"]
            breaches = [road for road in local if road_rect_clearance(road, core) < -0.02]
            walls = wall_sides(local, record["nominal_void_xy_mm"])
            passed = not breaches and all(side["present"] for side in walls.values())
            all_pass &= passed
            report_layers.append({"z_mm": z, "road_core_breach_count": len(breaches), "first_core_breach": breaches[0] if breaches else None, "surrounding_walls": walls, "passed": passed})
        expected_layers = round(24.0 / float(process["layer_height"])) if float(process["initial_layer_print_height"]) == float(process["layer_height"]) else 1 + round((24.0 - float(process["initial_layer_print_height"])) / float(process["layer_height"]))
        assert len(report_layers) == expected_layers, f"{record['object']}: expected {expected_layers} model layers, got {len(report_layers)}"
        record["all_layer_count"] = len(report_layers); record["all_layers_pass"] = all(layer["passed"] for layer in report_layers); record["layers"] = report_layers
        record["preview_z_mm"] = min((layer["z_mm"] for layer in report_layers), key=lambda z: abs(z - 12.0)); preview_roads[record["object"]] = by_layer[(record["object"], record["preview_z_mm"])]
        all_pass &= record["all_layers_pass"]
    report = {"passed": all_pass, "gcode_sha256": sha256(gcode), "sliced_3mf_sha256": sha256(project), "method": {"coordinate_frame": "Raw G-code nozzle motion plus frozen active-extruder offset before comparison to CAD/3MF bed coordinates", "deposition_offset_xy_mm": deposition_offset, "all_layers": True, "motion_types": ["G0", "G1", "G2", "G3"], "road_width": "LINE_WIDTH comments, default process line_width", "required_clear_core_square_mm": ID_SIDE - 2 * CORE_INSET, "wall_edge_proximity_limit_mm": 0.35, "pass_rule": "Every original 1-mm square inset core stays clear of every deposited road and each nominal-hole side has an actual wall-road witness within 0.35 mm on every model layer."}, "objects": records, "limits": "Toolpath-only check; no physical print, fit, strength, airflow, acoustic, thermal or CFD result."}
    args.json.parent.mkdir(parents=True, exist_ok=True); args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8"); preview(records, preview_roads, args.png); print(json.dumps({"passed": all_pass, "gcode_sha256": report["gcode_sha256"]}))


if __name__ == "__main__": main()
