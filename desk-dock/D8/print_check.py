#!/usr/bin/env python3
"""No-launch D8 mesh/bed preflight. Run after the print manifest is complete.

Uses numpy, but does not import CAD, run a slicer or communicate with a printer.
An optional 90-degree print-Z rotation preserves the selected face on the bed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import numpy as np

ROOT = Path(__file__).resolve().parent
BED = (256.0, 256.0)
HEIGHT = 250.0
EXCLUSION = (0.0, 0.0, 18.0, 28.0)
EXPORT_LINEAR_DEFLECTION = 0.06  # export_print.py's declared STL chord deflection
NOTICE = "Geometric preflight only: no CAD build, slicer, deposited-path approval or printer communication."


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_triangles(path):
    raw = path.read_bytes()
    count = struct.unpack_from("<I", raw, 80)[0] if len(raw) >= 84 else 0
    if count and len(raw) == 84 + 50 * count:
        dtype = np.dtype([("normal", "<f4", 3), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")])
        return np.frombuffer(raw, dtype=dtype, offset=84, count=count)["vertices"].astype(np.float64)
    number = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
    matches = re.findall(rf"vertex\s+({number})\s+({number})\s+({number})", raw.decode("ascii"))
    if not matches or len(matches) % 3:
        raise ValueError("Empty or malformed STL")
    return np.asarray(matches, dtype=np.float64).reshape((-1, 3, 3))


def topology(triangles):
    if not len(triangles) or not np.isfinite(triangles).all():
        raise ValueError("Empty mesh or non-finite triangle vertices")
    # Merge exactly equal vertices; never heal/round a mesh to obtain a pass.
    vertices, inverse = np.unique(triangles.reshape((-1, 3)), axis=0, return_inverse=True)
    faces = inverse.reshape((-1, 3))
    edge_rows = np.vstack((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]))
    owners = np.tile(np.arange(len(faces)), 3)
    _, edge_ids, counts = np.unique(np.sort(edge_rows, axis=1), axis=0, return_inverse=True, return_counts=True)
    directions = np.where(edge_rows[:, 0] < edge_rows[:, 1], 1, -1)
    winding_sums = np.bincount(edge_ids, weights=directions)
    ordered_owners = owners[np.argsort(edge_ids, kind="stable")]
    starts = np.cumsum(np.r_[0, counts[:-1]])
    parents = np.arange(len(faces))

    def find(index):
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    # Connectivity uses shared edges, not vertices. A point contact cannot
    # conceal two components. Nonmanifold incidence fails separately below.
    for start, count in zip(starts, counts):
        if count > 1:
            first = find(ordered_owners[start])
            for owner in ordered_owners[start + 1:start + count]:
                other = find(owner)
                if other != first:
                    parents[other] = first
    components = len({find(index) for index in range(len(faces))})
    twice_area = np.linalg.norm(np.cross(triangles[:, 1]-triangles[:, 0], triangles[:, 2]-triangles[:, 0]), axis=1)
    repeated = ((faces[:, 0] == faces[:, 1]) | (faces[:, 1] == faces[:, 2]) | (faces[:, 2] == faces[:, 0]))
    degenerate = int(np.count_nonzero(repeated | (twice_area <= 1e-12)))
    local = triangles - vertices.mean(axis=0)
    volume = float(np.einsum("ij,ij->i", local[:, 0], np.cross(local[:, 1], local[:, 2])).sum() / 6)
    return {
        "triangles": len(triangles), "unique_vertices": len(vertices),
        "edge_connected_components": components,
        "boundary_edges": int(np.count_nonzero(counts == 1)),
        "nonmanifold_edges": int(np.count_nonzero(counts > 2)),
        "watertight": bool(np.all(counts == 2)),
        "consistent_winding": bool(np.all((counts == 2) & (winding_sums == 0))),
        "degenerate_triangles": degenerate, "signed_volume_mm3": volume,
        "positive_volume": volume > 0,
        "bounds_mm": [vertices.min(axis=0).tolist(), vertices.max(axis=0).tolist()],
        "dimensions_mm": np.ptp(vertices, axis=0).tolist(),
        "surface_area_mm2": float(twice_area.sum()/2),
        "method": "Exact-coordinate vertex merge; edge incidence/winding; edge-connected components; signed volume. No healing or self-intersection certification.",
    }


def rectangle_intersects(first, second):
    return first[0] <= second[2] and first[2] >= second[0] and first[1] <= second[3] and first[3] >= second[1]


def placement(dimensions, bounds):
    attempts = []
    for brim in (8.0, 5.0):
        for turn in (0, 90):
            width, depth = dimensions[:2] if turn == 0 else dimensions[1::-1]
            if width+2*brim > BED[0] or depth+2*brim > BED[1] or dimensions[2] > HEIGHT:
                attempts.append({"rotation_z_deg": turn, "brim_mm": brim, "reason": "Part/brim exceeds rectangular envelope"})
                continue
            xmin, xmax = width/2+brim, BED[0]-width/2-brim
            ymin, ymax = depth/2+brim, BED[1]-depth/2-brim
            centers = [(128, 138), (128, 128), (136, 136), (xmax, ymax), (xmax, ymin), (xmin, ymax)]
            for cx, cy in centers:
                if not (xmin <= cx <= xmax and ymin <= cy <= ymax):
                    continue
                box = [cx-width/2-brim, cy-depth/2-brim, cx+width/2+brim, cy+depth/2+brim]
                if rectangle_intersects(box, EXCLUSION):
                    continue
                lower, upper = bounds
                rotated_lower = lower[:2] if turn == 0 else [-upper[1], lower[0]]
                translation = [cx-width/2-rotated_lower[0], cy-depth/2-rotated_lower[1], -lower[2]]
                return {"pass": True, "rotation_z_deg": turn, "brim_mm": brim,
                        "translation_after_rotation_mm": translation,
                        "placed_part_bounds_mm": [[cx-width/2, cy-depth/2, 0], [cx+width/2, cy+depth/2, dimensions[2]]],
                        "conservative_brim_bounds_mm": box,
                        "method": "Entire XY bounding rectangle plus brim avoids exclusion; exact brim toolpaths remain unreviewed."}
            attempts.append({"rotation_z_deg": turn, "brim_mm": brim, "reason": "No candidate rectangle clears the excluded corner"})
    return {"pass": False, "attempts": attempts,
            "method": "Conservative rectangle screen; does not prove every irregular-footprint placement impossible"}


def check_part(item, print_dir):
    record = {"part": item.get("part"), "file": item.get("file"), "failures": [], "warnings": []}
    try:
        source = print_dir / item["file"]
        if source.parent.resolve() != print_dir.resolve():
            raise ValueError("Manifest file must be directly inside print/")
        record["sha256"] = digest(source)
        if record["sha256"] != item.get("sha256"):
            record["failures"].append("STL hash differs from print manifest")
        mesh = topology(read_triangles(source))
        record["mesh"] = mesh
        for key, expected, message in [
            ("watertight", True, "Mesh is not watertight"),
            ("consistent_winding", True, "Triangle winding is inconsistent or open"),
            ("edge_connected_components", 1, "Mesh does not contain exactly one edge-connected component"),
            ("positive_volume", True, "Signed mesh volume is not positive"),
            ("degenerate_triangles", 0, "Mesh contains degenerate triangles"),
        ]:
            if mesh[key] != expected:
                record["failures"].append(message)
        # A tessellated circle need not contain a vertex at its exact CAD
        # extremum. Allow the declared deflection at each end of an extent;
        # retain the measured differences so this allowance is reviewable.
        record["cad_minus_mesh_dimensions_mm"] = [a-b for a,b in zip(item["dimensions_mm"],mesh["dimensions_mm"])]
        if not np.allclose(mesh["dimensions_mm"], item["dimensions_mm"], atol=2*EXPORT_LINEAR_DEFLECTION, rtol=0):
            record["failures"].append("Mesh/CAD dimensions differ by more than twice the declared 0.06 mm tessellation deflection")
        if abs(mesh["bounds_mm"][0][2]) > EXPORT_LINEAR_DEFLECTION:
            record["failures"].append("Exported lowest Z exceeds the 0.06 mm tessellation allowance at the CAD bed datum")
        record["pose"] = {key: item.get(key) for key in ["face_on_bed", "rotations", "load_orientation", "support", "material", "unloaded_export"]}
        record["placement"] = placement(mesh["dimensions_mm"], mesh["bounds_mm"])
        if not record["placement"]["pass"]:
            record["failures"].append("No conservative placement clears bed/brim/height/exclusion")
        footprint = mesh["dimensions_mm"][0]*mesh["dimensions_mm"][1]
        contact = float(item["first_layer_mean_contact_mm2"])
        if not math.isfinite(contact) or contact <= 0 or contact > footprint+0.05:
            record["failures"].append("Manifest first-layer mean area is invalid")
        fraction = contact/footprint if footprint else 0
        record["first_layer"] = {
            "xy_bounding_footprint_mm2": footprint,
            "cad_first_0p20mm_mean_area_mm2": contact,
            "mean_area_fraction_of_bounding_rectangle": fraction,
            "source": "Manifest CAD slab-intersection volume / 0.20 mm; not recalculated from STL and not exact Z=0 contact area",
        }
        if fraction < 0.05:
            record["warnings"].append("Mean first-layer area is below 5% of bounding rectangle; inspect adhesion and local supports")
        if item.get("support") != "None expected":
            record["warnings"].append("Manifest identifies an outstanding bridge/support review")
    except (OSError, ValueError, KeyError, UnicodeError, struct.error) as error:
        record["failures"].append(str(error))
    record["geometric_preflight_pass"] = not record["failures"]
    record["qualified_for_printing"] = False
    return record


def validate(root=ROOT, output=None, write=True):
    """Return report; missing/empty manifest raises before writing any output."""
    root = Path(root).resolve()
    manifest_path = root / "print-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    items = manifest.get("parts", [])
    if not items:
        raise ValueError("Print manifest has no production parts")
    if len({item.get("part") for item in items}) != len(items) or len({item.get("file") for item in items}) != len(items):
        raise ValueError("Print manifest contains duplicate parts or files")
    print_dir = root / "print"
    report = {"revision": "D8", "scope": NOTICE,
              "machine": {"bed_size_mm": list(BED), "conservative_height_mm": HEIGHT,
                          "lower_left_exclusion_rectangle_mm": list(EXCLUSION),
                          "brims_considered_mm": [8, 5], "in_plane_rotations_considered_deg": [0, 90]},
              "declared_export_linear_deflection_mm": EXPORT_LINEAR_DEFLECTION,
              "manifest_sha256": digest(manifest_path), "parts": [], "failures": []}
    expected = {item["file"] for item in items}
    extra = sorted(path.name for path in print_dir.glob("*.stl") if path.name not in expected)
    if extra:
        report["failures"].append("Unlisted STL files in print/: " + ", ".join(extra))
    for item in items:
        report["parts"].append(check_part(item, print_dir))
    report["part_count"] = len(items)
    report["failed_parts"] = [item["part"] for item in report["parts"] if not item["geometric_preflight_pass"]]
    report["geometric_preflight_pass"] = not report["failures"] and not report["failed_parts"]
    report["qualified_for_printing"] = False
    if write:
        destination = Path(output) if output else root / "print-review/mesh-preflight-summary.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = validate(args.root, args.output)
    print(json.dumps({key: report[key] for key in ["part_count", "geometric_preflight_pass", "failed_parts", "failures"]}, indent=2))
    raise SystemExit(0 if report["geometric_preflight_pass"] else 1)


if __name__ == "__main__":
    main()
