#!/usr/bin/env python3
"""Fail-closed audit for V3's 1/2/3 through-ID notches in actual Orca G-code.

This is a read-only G-code/STEP inspection except for its requested receipt
and close-up image. A positive extrusion segment entering a nominal notch
interior is sufficient evidence that the respective opening does not survive.
It intentionally cannot certify a future replacement mark as printable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import cadquery as cq
from PIL import Image, ImageDraw, ImageFont


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
SAMPLE_TARGETS_MM = (0.2, 12.0, 23.8)
INTERIOR_MARGIN_MM = 0.04


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_segments(gcode: Path) -> list[dict]:
    """Read positive straight-extrusion moves with their Orca object/feature."""
    pos = {key: 0.0 for key in "XYZE"}
    relative_e, absolute_xyz = True, True
    object_name, role = None, "Custom"
    result = []
    for line_number, line in enumerate(gcode.read_text(encoding="utf-8").splitlines(), 1):
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
        values = {key: float(value) for key, value in re.findall(r"([XYZE])([-+]?(?:\d*\.)?\d+)", code)}
        if operation == "G92":
            pos.update({key: value for key, value in values.items() if key in pos})
            continue
        if operation not in ("G0", "G1"):
            continue
        before = pos.copy()
        for key in "XYZ":
            if key in values:
                pos[key] = values[key] if absolute_xyz else pos[key] + values[key]
        extrusion = values.get("E", 0.0) if relative_e else values.get("E", pos["E"]) - pos["E"]
        if "E" in values:
            pos["E"] = pos["E"] + values["E"] if relative_e else values["E"]
        if object_name and extrusion > 0.0 and role != "Custom" and (before["X"], before["Y"]) != (pos["X"], pos["Y"]):
            result.append({
                "object": object_name,
                "z_mm": round(pos["Z"], 3),
                "role": role,
                "start_xy_mm": [before["X"], before["Y"]],
                "end_xy_mm": [pos["X"], pos["Y"]],
                "gcode_line": line_number,
                "gcode": line,
            })
    return result


def crosses_strict_rectangle(start: list[float], end: list[float], rect: list[float]) -> bool:
    """Liang-Barsky segment clip against a strict interior rectangle."""
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


def overlaps(start: list[float], end: list[float], rect: list[float]) -> bool:
    return not (max(start[0], end[0]) < rect[0] or min(start[0], end[0]) > rect[2]
                or max(start[1], end[1]) < rect[1] or min(start[1], end[1]) > rect[3])


def expected_notches(preparation: dict) -> list[dict]:
    records = []
    for item in preparation["objects"]:
        name = item["name"]
        shape = cq.importers.importStep(str(V3_STEPS[name])).val()
        bounds = shape.BoundingBox()
        offset_x, offset_y = item["bed_bounds_mm"][0][:2]
        for ordinal in range(1, EXPECTED_IDS[name] + 1):
            # print_oriented() maps source z/y to print x/y as
            # (source_zmax - z, y - source_ymin); V3's 3MF applies translation only.
            x0 = offset_x + bounds.zmax - (ID_Z0_MM + ID_HEIGHT_MM)
            x1 = offset_x + bounds.zmax - ID_Z0_MM
            y0 = offset_y + ID_Y0_MM + (ordinal - 1) * ID_PITCH_MM - bounds.ymin
            records.append({"object": name, "object_letter": name[0], "id_ordinal": ordinal,
                            "nominal_void_xy_mm": [x0, y0, x1, y0 + ID_WIDTH_MM]})
    return records


def draw_closeup(records: list[dict], segments: list[dict], output: Path) -> None:
    image = Image.new("RGB", (1500, 920), "#f7f8fa")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((24, 20), "V3 actual Orca G-code: ID-notch failure witnesses", fill="#17364b", font=font)
    draw.text((24, 42), "Red = nominal through-notch interior; magenta = the actual positive-extrusion witness crossing it.", fill="#435765", font=font)
    for index, record in enumerate(records):
        column, row = index % 3, index // 3
        left, top, width, height = 25 + column * 490, 95 + row * 400, 450, 340
        x0, y0, x1, y1 = record["nominal_void_xy_mm"]
        witness = record["first_failure"]
        z = witness["z_mm"]
        padding = 1.4
        bounds = (x0 - padding, y0 - padding, x1 + padding, y1 + padding)
        sx, sy = width / (bounds[2] - bounds[0]), height / (bounds[3] - bounds[1])
        def point(x: float, y: float) -> tuple[int, int]:
            return (int(left + (x - bounds[0]) * sx), int(top + height - (y - bounds[1]) * sy))
        def clipped_point(x: float, y: float) -> tuple[int, int]:
            return point(min(max(x, bounds[0]), bounds[2]), min(max(y, bounds[1]), bounds[3]))
        draw.text((left, top - 25), f"{record['object_letter']}{record['id_ordinal']}  witness Z={z:g} mm  line {witness['gcode_line']}", fill="#17364b", font=font)
        nearby = [segment for segment in segments if segment["object"] == record["object"] and abs(segment["z_mm"] - z) < .001 and overlaps(segment["start_xy_mm"], segment["end_xy_mm"], bounds)]
        for segment in nearby:
            draw.line((clipped_point(*segment["start_xy_mm"]), clipped_point(*segment["end_xy_mm"])),
                      fill="#b9c2c9", width=1)
        draw.line((clipped_point(*witness["start_xy_mm"]), clipped_point(*witness["end_xy_mm"])),
                  fill="#a43583", width=4)
        corner_a, corner_b = point(x0, y0), point(x1, y1)
        draw.rectangle((min(corner_a[0], corner_b[0]), min(corner_a[1], corner_b[1]),
                        max(corner_a[0], corner_b[0]), max(corner_a[1], corner_b[1])),
                       outline="#d63031", width=3)
        draw.text((left, top + height + 4), f"{x1-x0:.2f} x {y1-y0:.2f} mm nominal void; {witness['role']} crosses interior", fill="#8a1d1d", font=font)
    image.save(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--png", type=Path, required=True)
    args = parser.parse_args()
    folder = args.folder.resolve()
    gcode = folder / "plate_1.gcode"
    preparation = json.loads((folder / "plate-preparation.json").read_text(encoding="utf-8"))
    segments = parse_segments(gcode)
    z_values = sorted({segment["z_mm"] for segment in segments})
    records = expected_notches(preparation)
    failures = []
    for record in records:
        x0, y0, x1, y1 = record["nominal_void_xy_mm"]
        interior = [x0 + INTERIOR_MARGIN_MM, y0 + INTERIOR_MARGIN_MM, x1 - INTERIOR_MARGIN_MM, y1 - INTERIOR_MARGIN_MM]
        record["sampled_layers"] = []
        for target in SAMPLE_TARGETS_MM:
            z = min(z_values, key=lambda value: abs(value - target))
            hits = [segment for segment in segments if segment["object"] == record["object"] and abs(segment["z_mm"] - z) < .001 and crosses_strict_rectangle(segment["start_xy_mm"], segment["end_xy_mm"], interior)]
            record["sampled_layers"].append({"z_mm": z, "interior_crossing_count": len(hits), "crossing_witnesses": hits})
        crossing_layers = [layer for layer in record["sampled_layers"] if layer["interior_crossing_count"]]
        record["survives_all_sampled_layers"] = not crossing_layers
        if crossing_layers:
            record["first_failure"] = crossing_layers[0]["crossing_witnesses"][0]
            failures.append(record)
    report = {
        "status": "HOLD — actual positive extrusion enters every nominal ID-notch interior in at least one sampled layer",
        "scope": "Actual Orca G-code aperture evidence only; not a physical print, fit, strength, airflow, acoustic, thermal, or CFD conclusion.",
        "input": {
            "gcode": str(gcode), "gcode_sha256": digest(gcode),
            "sliced_3mf_sha256": digest(folder / "coupons-sliced.3mf"),
            "root_toolpath_report_sha256": digest(folder / "toolpath-verification.json"),
        },
        "method": {
            "source": "V3 source STEPs plus actual G0/G1 positive-extrusion moves, object-scoped by Orca comments",
            "notch_design_mm": {"source_z": [ID_Z0_MM, ID_Z0_MM + ID_HEIGHT_MM], "source_y_width": ID_WIDTH_MM, "source_y_pitch": ID_PITCH_MM},
            "sample_target_layers_mm": list(SAMPLE_TARGETS_MM),
            "strict_interior_margin_mm": INTERIOR_MARGIN_MM,
            "fail_rule": "Any positive extrusion segment crossing a strict nominal notch interior is a failed opening-survival witness.",
        },
        "root_plate_checks_carried_forward": {"native_transform_and_spacing": "PASS per actual 3MF/toolpath-verification.json", "support_segments": 0, "external_bridge_segments": 0},
        "notch_checks": records,
        "all_notches_survive_all_sampled_layers": not failures,
        "required_next_step": "Do not package or print this plate. Select a printable marking geometry or non-hole ID strategy, regenerate a fixed-placement slice, and recheck its actual G-code apertures.",
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    draw_closeup(records, segments, args.png)
    print(json.dumps({"status": report["status"], "json_sha256": digest(args.json), "png_sha256": digest(args.png)}))


if __name__ == "__main__":
    main()
