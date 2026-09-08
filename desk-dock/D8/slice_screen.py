#!/usr/bin/env python3
"""Offline CuraEngine path screening; never a printer-ready P1S export.

Example:
  python slice_screen.py print --output /absolute/scratch/review \
      --engine-root /absolute/path/to/cura-root --supports normal

Requires a Cura installation root containing usr/bin/CuraEngine and
usr/share/cura/resources/definitions. D8_CURA_ROOT can supply that root.
Uses only the Python standard library. Does not import or regenerate CAD.
The .gcode.txt files belong in scratch and must not enter a print release.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import subprocess
import time

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
NOTICE = "OFFLINE PATH SCREEN ONLY; generic Cura toolpaths, not executable P1S print files"
NUMBER = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def definitions(root):
    directory = root / "usr/share/cura/resources/definitions"
    printer = directory / "fdmprinter.def.json"
    extruder = directory / "fdmextruder.def.json"
    index = {}

    def visit(nodes):
        for key, value in nodes.items():
            if isinstance(value, dict):
                index[key] = value
                visit(value.get("children", {}))

    for source in [printer, extruder]:
        visit(json.loads(source.read_text())["settings"])
    return directory, printer, extruder, index


def settings(machine, support):
    # All temperatures/speeds are explicit generic path-screen assumptions.
    # No Bambu start/end sequence, homing, heating preamble or printer connection.
    return {
        "machine_name": "D8 generic offline P1S-envelope path screen",
        "machine_width": 256, "machine_depth": 256,
        "machine_height": float(machine["printable_height"]),
        "machine_center_is_zero": False, "machine_extruder_count": 1,
        # CuraEngine adds the bed center to STL coordinates in this mode.
        # Our STL already uses bed coordinates, so cancel that offset explicitly.
        "center_object": False, "mesh_position_x": -128, "mesh_position_y": -128,
        "machine_nozzle_size": 0.4, "material_diameter": 1.75,
        "machine_disallowed_areas": [machine["exclusion_points"]],
        "machine_start_gcode": "", "machine_end_gcode": "",
        "machine_nozzle_temp_enabled": False,
        "material_print_temp_prepend": False, "material_bed_temp_prepend": False,
        "material_print_temp_wait": False, "material_bed_temp_wait": False,
        "material_print_temperature": 250, "material_print_temperature_layer_0": 250,
        "material_initial_print_temperature": 250, "material_final_print_temperature": 250,
        "material_bed_temperature": 80, "material_bed_temperature_layer_0": 80,
        "layer_height": 0.2, "layer_height_0": 0.2,
        "line_width": 0.45, "wall_line_width": 0.45,
        "wall_line_width_0": 0.45, "wall_line_width_x": 0.45,
        "skin_line_width": 0.45, "infill_line_width": 0.45,
        "wall_line_count": 5, "wall_thickness": 2.25,
        "top_layers": 6, "bottom_layers": 6,
        "top_thickness": 1.2, "bottom_thickness": 1.2,
        "top_bottom_thickness": 1.2,
        "infill_sparse_density": 100, "infill_line_distance": 0.45,
        "infill_sparse_thickness": 0.2, "infill_pattern": "lines",
        "infill_angles": [0, 90], "skin_angles": [0, 90],
        "inset_direction": "inside_out", "wall_0_wipe_dist": 0,
        "meshfix_union_all": True, "meshfix_extensive_stitching": False,
        "min_wall_line_width": 0.3, "min_even_wall_line_width": 0.3,
        "min_odd_wall_line_width": 0.3,
        "speed_print": 80, "speed_wall_0": 50, "speed_wall_x": 80,
        "speed_topbottom": 50, "speed_infill": 80,
        "speed_layer_0": 25, "speed_print_layer_0": 25,
        "speed_travel": 150, "speed_travel_layer_0": 75,
        "bridge_settings_enabled": True, "bridge_wall_speed": 25,
        "bridge_skin_speed": 25, "bridge_skin_speed_2": 25,
        "bridge_skin_speed_3": 25, "bridge_wall_min_length": 1,
        "bridge_wall_material_flow": 100, "bridge_skin_material_flow": 100,
        "bridge_skin_material_flow_2": 100, "bridge_skin_material_flow_3": 100,
        "bridge_fan_speed": 100, "cool_fan_speed": 30,
        "cool_fan_speed_min": 30, "cool_fan_speed_max": 30,
        "support_enable": support == "normal", "support_structure": "normal",
        "support_type": "everywhere", "support_angle": 45,
        "support_pattern": "zigzag", "support_wall_count": 0,
        "support_infill_rate": 20, "support_line_distance": 2.25,
        "support_initial_layer_line_distance": 2.25,
        "support_line_width": 0.45, "support_xy_distance": 0.4,
        "support_xy_distance_overhang": 0.2,
        "support_z_distance": 0.2, "support_top_distance": 0.2,
        "support_bottom_distance": 0.2, "support_infill_sparse_thickness": 0.2,
        "support_interface_enable": True, "support_roof_enable": True,
        "support_bottom_enable": False, "support_roof_height": 0.4,
        "support_roof_density": 70, "support_roof_line_distance": 0.45 / 0.7,
        "support_roof_line_width": 0.45, "support_roof_pattern": "lines",
        "speed_support": 50, "speed_support_interface": 40,
        "support_brim_enable": True, "support_brim_width": 4.5,
        "support_brim_line_count": 10,
        "adhesion_type": "brim", "brim_width": 8,
        "brim_line_count": 18, "brim_outside_only": True,
        "skirt_brim_line_width": 0.45,
    }


def validate_settings(values, index):
    for key, value in values.items():
        if key not in index:
            raise ValueError(f"Cura definition does not advertise {key}")
        if index[key].get("type") == "enum" and value not in index[key].get("options", {}):
            raise ValueError(f"Invalid enum value {key}={value}")


def binary_stl(source):
    raw = bytearray(source.read_bytes())
    if len(raw) >= 84 and len(raw) == 84 + struct.unpack_from("<I", raw, 80)[0] * 50:
        return raw
    text = raw.decode("ascii")
    vertices = [tuple(map(float, match)) for match in re.findall(
        rf"vertex\s+({NUMBER})\s+({NUMBER})\s+({NUMBER})", text)]
    if not vertices or len(vertices) % 3:
        raise ValueError("Empty or malformed STL")
    output = bytearray(b"D8 ASCII-converted mesh".ljust(80, b" "))
    output.extend(struct.pack("<I", len(vertices) // 3))
    for offset in range(0, len(vertices), 3):
        a, b, c = vertices[offset:offset + 3]
        u, v = [b[j] - a[j] for j in range(3)], [c[j] - a[j] for j in range(3)]
        normal = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
        length = math.sqrt(sum(x*x for x in normal))
        normal = [x / length for x in normal] if length else [0, 0, 0]
        output.extend(struct.pack("<12fH", *normal, *a, *b, *c, 0))
    return output


def exclusion_box(machine):
    points = machine["exclusion_points"]
    return [min(p[0] for p in points), min(p[1] for p in points),
            max(p[0] for p in points), max(p[1] for p in points)]


def rectangles_overlap(a, b):
    return a[0] <= b[2] and a[2] >= b[0] and a[1] <= b[3] and a[3] >= b[1]


def place(source, destination, machine):
    raw = binary_stl(source)
    count = struct.unpack_from("<I", raw, 80)[0]
    if not count:
        raise ValueError("Empty STL")
    lo, hi = [math.inf] * 3, [-math.inf] * 3
    for face in range(count):
        for vertex in range(3):
            xyz = struct.unpack_from("<3f", raw, 84 + face * 50 + 12 + vertex * 12)
            if not all(math.isfinite(x) for x in xyz):
                raise ValueError("Non-finite mesh coordinates")
            lo, hi = [min(lo[j], xyz[j]) for j in range(3)], [max(hi[j], xyz[j]) for j in range(3)]
    size = [hi[j] - lo[j] for j in range(3)]
    if size[2] > float(machine["printable_height"]):
        raise ValueError(f"Height exceeds recorded P1S profile: {size[2]}")
    fit = None
    # 18 lines at 0.45 mm occupy 8.1 mm; allow a further edge allowance.
    margin = 8.5
    for cx, cy in [(128, 138), (128, 128), (136, 136)]:
        box = [cx-size[0]/2-margin, cy-size[1]/2-margin,
               cx+size[0]/2+margin, cy+size[1]/2+margin]
        if min(box[:2]) >= 0 and max(box[2:]) <= 256 and not rectangles_overlap(box, exclusion_box(machine)):
            fit = (cx, cy, box)
            break
    if fit is None:
        raise ValueError(f"Part plus conservative brim fails P1S bed/exclusion: {size}")
    shift = [fit[0]-(lo[0]+hi[0])/2, fit[1]-(lo[1]+hi[1])/2, -lo[2]]
    for face in range(count):
        for vertex in range(3):
            offset = 84 + face * 50 + 12 + vertex * 12
            xyz = struct.unpack_from("<3f", raw, offset)
            struct.pack_into("<3f", raw, offset, *(xyz[j] + shift[j] for j in range(3)))
    destination.write_bytes(raw)
    return {"triangles": count, "size_mm": size, "translation_mm": shift,
            "conservative_brim_bounds_mm": fit[2], "placement_pass": True,
            "orientation": "Input STL orientation preserved; translation only",
            "mesh_validation": "Finite vertices and nonempty STL only; no topology repair or watertightness claim"}


def summarize_paths(path, machine, density):
    position, epos, debt = [0., 0., 0.], 0., 0.
    absolute_e, absolute_xyz, kind = True, True, "UNCLASSIFIED"
    totals = defaultdict(float)
    counts = defaultdict(int)
    lo, hi = [math.inf]*3, [-math.inf]*3
    bad_segments, elapsed, header_elapsed, layers = 0, None, None, 0
    xy_margin = 0.225
    pattern = re.compile(rf"([XYZE])({NUMBER})")
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            if line.startswith(";TYPE:"):
                kind = line.strip()[6:]
                continue
            if line.startswith(";TIME:"):
                try:
                    header_elapsed = float(line.strip()[6:])
                except ValueError:
                    pass
            if line.startswith(";TIME_ELAPSED:"):
                # Standalone CuraEngine leaves a placeholder ;TIME:6666 header;
                # use the final cumulative layer time instead.
                elapsed = float(line.strip().split(":", 1)[1])
            if line.startswith(";LAYER_COUNT:"):
                layers = int(line.split(":", 1)[1])
            code = line.split(";", 1)[0].strip()
            if not code:
                continue
            command = code.split()[0]
            if command in ("M82", "M83"):
                absolute_e = command == "M82"
            elif command in ("G90", "G91"):
                absolute_xyz = command == "G90"
            elif command == "G92":
                values = {k: float(v) for k, v in pattern.findall(code)}
                if "E" in values:
                    epos = values["E"]
                for j, axis in enumerate("XYZ"):
                    if axis in values:
                        position[j] = values[axis]
            elif command in ("G0", "G1"):
                values = {k: float(v) for k, v in pattern.findall(code)}
                new = [values.get(axis, position[j]) if absolute_xyz else position[j]+values.get(axis, 0)
                       for j, axis in enumerate("XYZ")]
                delta = (values["E"] - epos if absolute_e else values["E"]) if "E" in values else 0.
                if "E" in values:
                    epos = values["E"] if absolute_e else epos + values["E"]
                if delta < 0:
                    debt -= delta
                else:
                    recovered = min(debt, delta)
                    debt -= recovered
                    deposited = delta - recovered
                    if deposited > 1e-7 and math.dist(position, new) > 1e-7:
                        totals[kind] += deposited
                        counts[kind] += 1
                        lo = [min(lo[j], position[j], new[j]) for j in range(3)]
                        hi = [max(hi[j], position[j], new[j]) for j in range(3)]
                        rectangle = [min(position[0], new[0])-xy_margin, min(position[1], new[1])-xy_margin,
                                     max(position[0], new[0])+xy_margin, max(position[1], new[1])+xy_margin]
                        if (min(rectangle[:2]) < 0 or max(rectangle[2:]) > 256 or
                            max(position[2], new[2]) > float(machine["printable_height"]) or
                            rectangles_overlap(rectangle, exclusion_box(machine))):
                            bad_segments += 1
                position = new
    area = math.pi * (1.75 / 2)**2
    volumes = {key: value * area for key, value in totals.items()}
    support = sum(value for key, value in volumes.items() if "SUPPORT" in key)
    adhesion = sum(value for key, value in volumes.items() if key in {"SKIRT", "BRIM"})
    total = sum(volumes.values())
    return {"estimated_time_s": elapsed, "header_time_s_untrusted": header_elapsed,
            "time_source": "Final TIME_ELAPSED layer comment; header may be a placeholder",
            "time_is_generic_cura_estimate": True,
            "layers": layers, "deposited_segments": sum(counts.values()),
            "extruded_filament_mm_by_type": dict(totals), "volume_mm3_by_type": volumes,
            "total_deposited_volume_mm3": total, "support_volume_mm3": support,
            "adhesion_volume_mm3": adhesion, "model_volume_mm3": total-support-adhesion,
            "density_assumed_g_cm3": density, "total_estimated_mass_g": total*density/1000,
            "support_estimated_mass_g": support*density/1000,
            "deposited_centerline_bounds_mm": [lo, hi] if total else None,
            "bed_exclusion_flagged_segments": bad_segments,
            "deposited_paths_within_envelope": bad_segments == 0 and total > 0,
            "method": "Integrate positive G0/G1 E after retraction recovery; 1.75 mm circular filament. Excludes stationary priming. Segment AABBs plus 0.225 mm screen exclusion conservatively.",
            "limits": "Support volume is a slicer estimate, not proof of necessity, accessibility or removability. No unsupported-layer or bridge-anchoring certification."}


def setting_text(value):
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (list, dict)):
        return json.dumps(value, separators=(",", ":"))
    return str(value)


def screen(source, mode, args, machine, defs, engine, env):
    directory = args.output / source.stem / mode
    directory.mkdir(parents=True, exist_ok=True)
    record = {"notice": NOTICE, "source": str(source), "source_sha256": sha(source),
              "support_mode": mode, "path_screen_pass": False}
    try:
        placed = directory / "plate.stl"
        record["placement"] = place(source, placed, machine)
        values = settings(machine, mode)
        validate_settings(values, defs[3])
        save(directory / "settings.json", {"notice": NOTICE, "values": values})
        destination = directory / "paths.REVIEW_ONLY.gcode.txt"
        command = [str(engine), "slice", "-m2", "-j", str(defs[1])]
        for key, value in values.items():
            command.extend(["-s", f"{key}={setting_text(value)}"])
        command.extend(["-e0", "-j", str(defs[2]), "-s", "machine_nozzle_size=0.4",
                        "-s", "material_diameter=1.75", "-l", str(placed), "-o", str(destination)])
        record["command"] = command
        started = time.monotonic()
        with (directory / "slice.log").open("w", encoding="utf-8") as logfile:
            try:
                completed = subprocess.run(command, env=env, stdout=logfile,
                                           stderr=subprocess.STDOUT, timeout=args.timeout, check=False)
                record["exit_code"] = completed.returncode
                record["timeout"] = False
            except subprocess.TimeoutExpired:
                record["exit_code"], record["timeout"] = None, True
        record["elapsed_seconds"] = round(time.monotonic()-started, 3)
        record["engine_warnings"] = [line for line in (directory / "slice.log").read_text(
            encoding="utf-8", errors="replace").splitlines()
            if line.startswith("[WARNING]") and not line.startswith("[WARNING]  -s")]
        record["exclusion_enforcement"] = "This runner checks placed brim and deposited paths; it does not rely on CuraEngine accepting polygon metadata."
        if record["exit_code"] == 0 and destination.exists():
            # A .txt suffix and explicit first-line notice keep review output
            # distinct from downloadable printer files. Do not strip Cura paths.
            content = destination.read_text(encoding="utf-8")
            destination.write_text(f"; {NOTICE}\n; NO PRINTER START/END SEQUENCE\n"+content, encoding="utf-8")
            record["toolpaths_sha256"] = sha(destination)
            record["estimates"] = summarize_paths(destination, machine, args.density)
            record["path_screen_pass"] = record["estimates"]["deposited_paths_within_envelope"]
        record["qualified_for_printing"] = False
    except (OSError, ValueError, KeyError, UnicodeError) as error:
        record["error"] = str(error)
    save(directory / "review.json", record)
    print(json.dumps({"part": source.stem, "supports": mode,
                      "pass": record["path_screen_pass"],
                      "mass_g": record.get("estimates", {}).get("total_estimated_mass_g"),
                      "support_g": record.get("estimates", {}).get("support_estimated_mass_g"),
                      "error": record.get("error")}), flush=True)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("models", nargs="+", type=Path, help="STL files or directories of STL files")
    parser.add_argument("--output", required=True, type=Path, help="Scratch directory outside this repository")
    parser.add_argument("--engine-root", type=Path, default=os.environ.get("D8_CURA_ROOT"))
    parser.add_argument("--machine-profile", type=Path,
                        default=ROOT.parent / "D7/print-review/profile-evidence.json")
    parser.add_argument("--supports", choices=("normal", "off", "both"), default="normal")
    parser.add_argument("--timeout", type=int, default=60, help="Bounded seconds per part/mode")
    parser.add_argument("--density", type=float, default=1.27, help="Assumed PETG density g/cm3")
    args = parser.parse_args()
    args.output = args.output.resolve()
    if args.output.is_relative_to(REPO):
        parser.error("Keep generic Cura review paths outside the repository/release")
    if not args.engine_root:
        parser.error("Supply --engine-root or D8_CURA_ROOT for the local Cura installation")
    args.engine_root = args.engine_root.resolve()
    if args.timeout < 1 or args.density <= 0:
        parser.error("Timeout and density must be positive")
    engine = args.engine_root / "usr/bin/CuraEngine"
    defs = definitions(args.engine_root)
    machine = json.loads(args.machine_profile.read_text())
    if machine["printable_area"] != ["0x0", "256x0", "256x256", "0x256"]:
        parser.error("This runner requires the recorded 256 mm square P1S bed")
    machine["exclusion_points"] = [[float(v) for v in p.split("x")] for p in machine["bed_exclude_area"]]
    sources = []
    for item in args.models:
        sources.extend(sorted(item.glob("*.stl")) if item.is_dir() else [item])
    sources = list(dict.fromkeys(p.resolve() for p in sources))
    if not sources or any(p.suffix.lower() != ".stl" or not p.is_file() for p in sources):
        parser.error("Supply at least one existing STL")
    if len({p.stem for p in sources}) != len(sources):
        parser.error("Part stems must be unique to prevent output collisions")
    args.output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = str(args.engine_root / "usr/lib/x86_64-linux-gnu")
    env["CURA_ENGINE_SEARCH_PATH"] = str(defs[0])
    modes = ["off", "normal"] if args.supports == "both" else [args.supports]
    summary = {"notice": NOTICE, "fallback_reason": "Orca unavailable; offline generic Cura path screening only",
               "engine_sha256": sha(engine), "definition_sha256": {p.name: sha(p) for p in defs[1:3]},
               "machine_profile_sha256": sha(args.machine_profile),
               "machine_envelope": {k: machine[k] for k in ("printable_area", "printable_height", "bed_exclude_area")},
               "parts": []}
    for source in sources:
        for mode in modes:
            summary["parts"].append(screen(source, mode, args, machine, defs, engine, env))
            save(args.output / "summary.json", summary)
    raise SystemExit(0 if all(p["path_screen_pass"] for p in summary["parts"]) else 1)


if __name__ == "__main__":
    main()
