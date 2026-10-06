"""Prepare and inspect D7 print plates without contacting a printer.

Uses the already-installed Bambu Studio CLI as an explicit fallback after the
installed OrcaSlicer failed even --help. All generated state lives below this
revision's print-review directory; the user's slicer preferences are not read.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parent
DEFAULT_EXE = Path(r"C:\Program Files\Bambu Studio\bambu-studio.exe")
DEFAULT_PROFILES = DEFAULT_EXE.parent / "resources" / "profiles" / "BBL"
OUTPUT = ROOT / "print-review"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def flatten_profiles(root):
    index = {}
    for path in sorted(root.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (ValueError, UnicodeError):
            continue
        if isinstance(data, dict) and data.get("name"):
            index[data["name"]] = (path, data)
    evidence = {}

    def flatten(name, trail=()):
        if name in trail:
            raise ValueError(f"Profile inheritance cycle: {trail + (name,)}")
        path, data = index[name]
        evidence[str(path)] = digest(path)
        merged = {}
        if data.get("inherits"):
            merged.update(flatten(data["inherits"], trail + (name,)))
        for parent in data.get("include", []):
            merged.update(flatten(parent, trail + (name,)))
        merged.update(data)
        merged.pop("inherits", None)
        merged.pop("include", None)
        return merged

    result = {
        "machine": flatten("Bambu Lab P1S 0.4 nozzle"),
        "process": flatten("0.20mm Standard @BBL X1C"),
        "filament": flatten("Generic PETG"),
    }
    assert result["machine"]["name"] in result["filament"]["compatible_printers"]
    assert result["filament"]["filament_type"] == ["PETG"]
    return result, evidence


def prepare_profiles(profile_root, output, support_mode="off"):
    profiles, evidence = flatten_profiles(profile_root)
    machine, process, filament = (profiles[k] for k in ("machine", "process", "filament"))
    process.update(
        wall_loops="5", top_shell_layers="6", bottom_shell_layers="6",
        layer_height="0.2", sparse_infill_density="100%", sparse_infill_pattern="rectilinear",
        brim_width="8", brim_type="outer_only", wall_generator="arachne",
        outer_wall_speed=["80", "80"], inner_wall_speed=["120", "120"],
        initial_layer_speed=["25", "25"], bridge_speed=["25", "25"],
        enable_support="1" if support_mode == "normal" else "0",
        support_type="normal(auto)", support_on_build_plate_only="0",
    )
    machine["curr_bed_type"] = "Textured PEI Plate"
    machine["printer_settings_id"] = machine["name"]
    process["print_settings_id"] = "D7 PETG structural review / 0.20 mm / 5 walls / 100%"
    filament["filament_settings_id"] = [filament["name"]]
    paths = {}
    for kind, data in profiles.items():
        data["from"] = "system"
        paths[kind] = output / "profiles" / (kind + ".json")
        write_json(paths[kind], data)
    record = {
        "purpose": "Local review only; no printing or printer communication",
        "printer": machine["name"], "material": filament["name"],
        "nozzle_mm": machine["nozzle_diameter"], "layer_mm": process["layer_height"],
        "support_mode": support_mode,
        "printable_area": machine["printable_area"],
        "printable_height": machine["printable_height"],
        "bed_exclude_area": machine["bed_exclude_area"],
        "nozzle_temperature_c": filament.get("nozzle_temperature"),
        "textured_plate_temperature_c": filament.get("textured_plate_temp"),
        "max_volumetric_speed_mm3_s": filament.get("filament_max_volumetric_speed"),
        "source_profile_sha256": evidence,
        "generated_profile_sha256": {k: digest(p) for k, p in paths.items()},
    }
    write_json(output / "profile-evidence.json", record)
    return paths, profiles, record


def run_hidden(command, logfile, timeout):
    """Bounded hidden child; suppress Windows crash dialogs, preserve exit code."""
    options = {}
    if os.name == "nt":
        # A child inherits its parent's error mode. This prevents the known
        # application-error discovery from opening another modal error dialog.
        previous = ctypes.windll.kernel32.SetErrorMode(0x0001 | 0x0002)
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
        options.update(startupinfo=startup, creationflags=subprocess.CREATE_NO_WINDOW)
    started = time.monotonic()
    logfile.parent.mkdir(parents=True, exist_ok=True)
    try:
        with logfile.open("w", encoding="utf-8") as log:
            try:
                result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT,
                                        timeout=timeout, check=False, **options)
                code, timed_out = result.returncode, False
            except subprocess.TimeoutExpired:
                code, timed_out = None, True
    finally:
        if os.name == "nt":
            ctypes.windll.kernel32.SetErrorMode(previous)
    return {"command": list(map(str, command)), "exit_code": code,
            "timeout": timed_out, "elapsed_seconds": round(time.monotonic() - started, 2),
            "log": str(logfile)}


def discover(exe, output):
    record_path = output / "cli-discovery.json"
    if record_path.exists():
        return json.loads(record_path.read_text())
    record = run_hidden([str(exe), "--datadir", str(output / "isolated-user"), "--help"],
                        output / "cli-help.txt", 20)
    record["executable_sha256"] = digest(exe)
    write_json(record_path, record)
    return record


def plate(source, output, machine, brim=8):
    import numpy as np
    import trimesh
    from shapely.geometry import box, Polygon

    mesh = trimesh.load_mesh(source, process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.to_mesh()
    # STL stores a separate vertex triplet for each face. Merge matching
    # coordinates before inspecting topology; this does not rotate or repair it.
    mesh.merge_vertices()
    if not len(mesh.faces) or not mesh.is_watertight:
        raise ValueError(f"Non-watertight or empty print mesh: {source.name}")
    before = np.asarray(mesh.bounds)
    extent = np.asarray(mesh.extents)
    bed = Polygon([tuple(map(float, pt.split("x"))) for pt in machine["printable_area"]])
    exclusion = Polygon([tuple(map(float, pt.split("x"))) for pt in machine["bed_exclude_area"]])
    fit = None
    # Preserve the supplied print orientation. Only XY placement and bed Z move.
    for cx, cy in [(128, 138), (128, 128), (136, 136)]:
        footprint = box(cx - extent[0] / 2 - brim, cy - extent[1] / 2 - brim,
                        cx + extent[0] / 2 + brim, cy + extent[1] / 2 + brim)
        if bed.covers(footprint) and not footprint.intersects(exclusion):
            fit = (cx, cy, footprint)
            break
    if fit is None or extent[2] > float(machine["printable_height"]):
        raise ValueError(f"Supplied orientation exceeds P1S bed/brim/height: {source.name}, {extent}")
    shift = [fit[0] - (before[0, 0] + before[1, 0]) / 2,
             fit[1] - (before[0, 1] + before[1, 1]) / 2, -before[0, 2]]
    mesh.apply_translation(shift)
    downward = (mesh.face_normals[:, 2] < -np.sqrt(0.5)) & (mesh.triangles_center[:, 2] > 0.4)
    face_ids = np.flatnonzero(downward)
    largest = sorted(face_ids, key=lambda idx: mesh.area_faces[idx], reverse=True)[:20]
    angle_screen = {
        "method": "Downward-facing triangles steeper than a 45-degree printable wall, above the first 0.4 mm. Angle screening alone cannot establish support requirements or bridge anchoring.",
        "candidate_area_mm2": float(mesh.area_faces[downward].sum()),
        "candidate_triangle_count": int(downward.sum()),
        "largest_candidate_triangles": [
            {"area_mm2": float(mesh.area_faces[idx]),
             "normal": mesh.face_normals[idx].tolist(),
             "bounds_mm": [mesh.triangles[idx].min(axis=0).tolist(), mesh.triangles[idx].max(axis=0).tolist()]}
            for idx in largest],
    }
    destination = output / "plate.stl"
    destination.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(destination)
    return destination, {"source": str(source), "source_sha256": digest(source),
                         "watertight": bool(mesh.is_watertight),
                         "part_size_mm": extent.tolist(), "translation_mm": shift,
                         "placed_bounds_mm": mesh.bounds.tolist(),
                         "conservative_brim_bounds_mm": list(fit[2].bounds),
                         "bed_and_exclusion_pass": True, "brim_mm": brim,
                         "orientation": "CAD export orientation preserved",
                         "overhang_angle_screen": angle_screen}


def slice_one(source, args, profiles, machine):
    output = args.output / source.stem
    placed, result = plate(source, output, machine)
    result["support_mode"] = args.supports
    result["profile_sha256"] = {key: digest(path) for key, path in profiles.items()}
    command = [str(args.slicer), "--datadir", str(args.output / "isolated-user"),
               "--load-settings", str(profiles["machine"]) + ";" + str(profiles["process"]),
               "--load-filaments", str(profiles["filament"]),
               "--slice", "0", "--orient", "0", "--arrange", "0",
               "--outputdir", str(output), "--export-3mf", source.stem + ".gcode.3mf",
               str(placed)]
    result.update(run_hidden(command, output / "slice.log", args.timeout))
    if (output / "result.json").exists():
        result["slicer_result"] = json.loads((output / "result.json").read_text())
    archives = sorted(output.glob("*.gcode.3mf"))
    if result["exit_code"] == 0 and not result["timeout"] and archives:
        archive = archives[-1]
        with zipfile.ZipFile(archive) as z:
            members = [name for name in z.namelist() if name.endswith(".gcode")]
            if len(members) != 1:
                raise ValueError(f"Expected one sliced plate in {archive}")
            gcode = z.read(members[0]).decode("utf-8", errors="replace")
        (output / "preview.gcode").write_text(gcode, encoding="utf-8")
        result["preview_archive"] = str(archive)
        result["preview_archive_sha256"] = digest(archive)
        result["estimates"] = [line for line in gcode.splitlines() if line.startswith(";")
                                and re.search(r"estimated.*time|printing time|filament used|filament weight", line)]
        result["slice_pass"] = True
    else:
        result["slice_pass"] = False
    result["qualification"] = "Slicing and plate-fit screening do not prove support removal, PETG fit, strength or physical print success."
    write_json(output / "review.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("models", nargs="*", type=Path)
    parser.add_argument("--slicer", type=Path, default=DEFAULT_EXE)
    parser.add_argument("--profiles", type=Path, default=DEFAULT_PROFILES)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--prepare", action="store_true", help="Resolve profiles only; do not launch any application")
    parser.add_argument("--preflight", action="store_true", help="Place models and inspect meshes without launching any application")
    parser.add_argument("--discover", action="store_true", help="One cached, hidden, bounded Bambu --help check")
    parser.add_argument("--supports", choices=("off", "normal"), default="off")
    parser.add_argument("--timeout", type=int, default=240, help="Maximum seconds per hidden slice")
    args = parser.parse_args()
    args.output = args.output.resolve()
    # Do not permit this runner to write to a user's slicer settings directory.
    if not args.output.is_relative_to(ROOT.resolve()):
        parser.error("Outputs must remain inside this D7 revision")
    settings, profiles, evidence = prepare_profiles(args.profiles, args.output, args.supports)
    if args.prepare:
        print(json.dumps({k: v for k, v in evidence.items() if not k.endswith("sha256")}, indent=2))
        return
    if args.discover:
        result = discover(args.slicer, args.output)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["exit_code"] == 0 and not result["timeout"] else 1)
    if args.preflight:
        if not args.models:
            parser.error("Supply print-oriented STL models for --preflight")
        reports = []
        for source in args.models:
            _, report = plate(source.resolve(), args.output / source.stem, profiles["machine"])
            reports.append(report)
            write_json(args.output / source.stem / "mesh-preflight.json", report)
            print(source.name, "plate fit", report["bed_and_exclusion_pass"], "size mm",
                  [round(v, 2) for v in report["part_size_mm"]], flush=True)
        write_json(args.output / "mesh-preflight-summary.json", reports)
        return
    discovery_path = args.output / "cli-discovery.json"
    if not discovery_path.exists():
        parser.error("Run --discover once before slicing; a failed discovery must be investigated without relaunches")
    discovery = json.loads(discovery_path.read_text())
    if discovery.get("exit_code") != 0 or discovery.get("timeout"):
        parser.error("Bambu CLI discovery failed; no slicing launch allowed")
    if not args.models:
        parser.error("Supply print-oriented STL models, or --prepare / --discover")
    summary = []
    for source in args.models:
        result = slice_one(source.resolve(), args, settings, profiles["machine"])
        summary.append(result)
        write_json(args.output / "slice-summary.json", summary)
        print(source.name, "slice", result["slice_pass"], "seconds", result["elapsed_seconds"], flush=True)
        if not result["slice_pass"]:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
