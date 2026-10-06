#!/usr/bin/env python3
"""Generate A/B/C diagnostic coupons directly from R1/R2 native-datum solids.

Unlike superseded v1, A and B are cropped from the original R1/R2 STEP
contact-region solids.  The short fence, intended bearing and lower lid rail
therefore retain their source coordinates.  C changes only the R2 seat cavity
by a numeric, one-mm profile-normalized relief cut; it never translates a
whole laptop or changes the fence/rail/base datum.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import cadquery as cq
import trimesh
from PIL import Image, ImageDraw


HERE = Path(__file__).resolve().parent
DEFAULT_D8 = Path("/mnt/f/Code/5680-dock-fit-20260917/desk-dock/D8")
WIDTH_MM = 24.0
CROP_Z0_MM = 44.0
CROP_Z1_MM = 72.0
ID_NOTCH_Z0_MM = 49.0
ID_NOTCH_HEIGHT_MM = 0.7
ID_NOTCH_Y0_MM = -2.5
ID_NOTCH_WIDTH_MM = 0.48
ID_NOTCH_PITCH_MM = 1.05


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prism(points: list[tuple[float, float]], width: float, x0: float) -> cq.Shape:
    return cq.Workplane("YZ", origin=(x0, 0, 0)).polyline(points).close().extrude(width).val()


def box(x0: float, y: float, z: float, dx: float, dy: float, dz: float) -> cq.Shape:
    return cq.Workplane("XY").box(dx, dy, dz, centered=False).translate((x0, y, z)).val()


def native_crop(shape: cq.Shape, x0: float, y0: float, y1: float) -> cq.Shape:
    crop = box(x0, y0, CROP_Z0_MM, WIDTH_MM, y1 - y0, CROP_Z1_MM - CROP_Z0_MM)
    result = shape.intersect(crop).clean()
    assert result.isValid() and len(result.Solids()) == 1
    return result


def add_noncontact_source_id(shape: cq.Shape, identifier: int, x0: float) -> cq.Shape:
    """Cut an integral 1/2/3-notch ID into the native low support region.

    The R1/R2 imported crops already stay connected after C's relief boolean,
    so no added base is necessary or permitted.  These shallow through-X
    notches live in the source's low seat-support material at z=49.0..49.7,
    below the actual leaned bearing curve and remote from the lid rail.
    """
    result = shape
    expected_notch_volume = WIDTH_MM * ID_NOTCH_WIDTH_MM * ID_NOTCH_HEIGHT_MM
    # One, two, or three through-notches provide integral A/B/C identification
    # without reconstructing or moving any source contact feature.
    for index in range(identifier):
        notch = box(x0, ID_NOTCH_Y0_MM + index * ID_NOTCH_PITCH_MM, ID_NOTCH_Z0_MM, WIDTH_MM, ID_NOTCH_WIDTH_MM, ID_NOTCH_HEIGHT_MM)
        # Each mark must cut a full rectangular volume from material; a mark
        # that merely grazes an edge would not be a legible integral ID.
        assert abs(shape.intersect(notch).Volume() - expected_notch_volume) < 1e-5
        result = result.cut(notch).clean()
    assert result.isValid() and len(result.Solids()) == 1
    return result


def r2_relief_ring(r2_curve: list[list[float]], x0: float, seat_z: float, lean_deg: float) -> cq.Shape:
    """Return C's local one-mm R2 seat band in the *same leaned frame* as R2.

    R2 builds its revised seat profile in the unleaned YZ plane and applies
    ``rotate((0,0,H), (1,0,H), -A)`` only afterwards.  Applying precisely
    that original transform here is essential: a band built from the stored
    YZ points but left unleaned is not registered to the imported R2 solid.
    """
    original = [(float(y), float(z)) for y, z in r2_curve]
    lowered = [(y, z - 1.0) for y, z in reversed(original)]
    # This is deliberately a local curve-following band, not a flat extension
    # or blanket stack translation.  Its original source span is
    # y=-3.585..6.415; the returned solid uses the source's rigid lean frame.
    return prism(original + lowered, WIDTH_MM, x0).rotate((0, 0, seat_z), (1, 0, seat_z), -lean_deg)


def source_lean_yz(y: float, z: float, seat_z: float, lean_deg: float) -> tuple[float, float]:
    """Apply the R1/R2 builder's source lean() to one YZ point."""
    angle = math.radians(-lean_deg)
    dz = z - seat_z
    return (
        math.cos(angle) * y - math.sin(angle) * dz,
        math.sin(angle) * y + math.cos(angle) * dz + seat_z,
    )


def print_oriented(shape: cq.Shape) -> cq.Shape:
    printed = shape.rotate((0, 0, 0), (0, 1, 0), -90)
    bounds = printed.BoundingBox()
    return printed.translate((-bounds.xmin, -bounds.ymin, -bounds.zmin))


def render_png(path: Path, objects: list[tuple[cq.Shape, tuple[int, int, int]]], title: str, subtitle: str, d8: Path, camvec: tuple[float, float, float] = (0.86, -0.96, 0.55)) -> None:
    sys.path.insert(0, str(d8))
    from raster import font, render

    image, _ = render(objects, (1600, 970), camvec, pad=65)
    canvas = Image.new("RGB", (1600, 1080), "#f7f7f7")
    canvas.paste(image, (0, 110))
    draw = ImageDraw.Draw(canvas)
    draw.text((34, 20), title, font=font(25, True), fill="#173a50")
    draw.text((34, 62), subtitle, font=font(18, False), fill="#435765")
    canvas.save(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--d8", type=Path, default=DEFAULT_D8)
    parser.add_argument("--out", type=Path, default=HERE / "generated")
    args = parser.parse_args()
    d8, out = args.d8.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    source = {
        "parameters": d8 / "parameters.json",
        "r1_builder": d8 / "quick-fit" / "build_quick_fit.py",
        "r1_contact_profiles": d8 / "contact-profiles.json",
        "r1_step": d8 / "quick-fit" / "D8-quick-fit-bracket.step",
        "r2_builder": d8 / "quick-fit" / "R2" / "build_quick_fit.py",
        "r2_step": d8 / "quick-fit" / "R2" / "D8-R2-quick-fit-bracket.step",
        "r2_fit_parameters": d8 / "quick-fit" / "R2" / "fit-parameters.json",
        "r2_seat_profile": d8 / "quick-fit" / "R2" / "seat-profile.json",
    }
    missing = [name for name, path in source.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    params = json.loads(source["parameters"].read_text(encoding="utf-8"))
    r1_contacts = json.loads(source["r1_contact_profiles"].read_text(encoding="utf-8"))
    r2_fit = json.loads(source["r2_fit_parameters"].read_text(encoding="utf-8"))
    r2_profile = json.loads(source["r2_seat_profile"].read_text(encoding="utf-8"))
    thickness = float(params["laptop_thickness"])
    seat_z = float(params["rear_case_seat_z"])
    lean_deg = float(params["laptop_lean_deg"])
    x0 = (38.1 - WIDTH_MM) / 2.0
    # Exact source-datum equations from R1/R2 builders; crop intentionally
    # includes the R2 outer lip shifted by 2 mm and the lower lid rail.
    r1_fence_inner = -thickness / 2.0 - 0.25
    r1_fence_outer = -thickness / 2.0 - 3.0
    r2_fence_outer = r1_fence_outer - float(r2_fit["lip_outward_shift_mm"])
    rail_y = thickness / 2.0
    crop_y0 = r2_fence_outer - 0.5
    crop_y1 = rail_y + 6.0

    r1 = cq.importers.importStep(str(source["r1_step"])).val()
    r2 = cq.importers.importStep(str(source["r2_step"])).val()
    # Keep these imported-solid crops explicit.  A/B do not reconstruct a
    # local curve or substitute nominal faces for the native R1/R2 geometry.
    native_a = native_crop(r1, x0, crop_y0, crop_y1)
    native_b = native_crop(r2, x0, crop_y0, crop_y1)
    a_pre_id = native_a
    b_pre_id = native_b
    assert a_pre_id.isValid() and len(a_pre_id.Solids()) == 1
    assert b_pre_id.isValid() and len(b_pre_id.Solids()) == 1

    # C begins with the exact B pre-ID solid and differs only by this R2
    # curve-derived local relief.  The transform is intentionally byte-for-
    # byte equivalent in geometry to R2's original lean() helper.
    relief_band = r2_relief_ring(r2_profile["revised_yz_mm"], x0, seat_z, lean_deg)
    removed_band = b_pre_id.intersect(relief_band).clean()
    c_pre_id = b_pre_id.cut(relief_band).clean()
    assert removed_band.isValid() and removed_band.Volume() > 0.0
    assert c_pre_id.isValid() and len(c_pre_id.Solids()) == 1
    removed_by_difference_mm3 = b_pre_id.Volume() - c_pre_id.Volume()
    removed_by_intersection_mm3 = removed_band.Volume()
    assert abs(removed_by_difference_mm3 - removed_by_intersection_mm3) < 1e-5
    # The integral IDs are in low source material.  Prove they cannot touch
    # C's actual changed bearing band (nor bridge toward the distant lid rail).
    id_z1 = ID_NOTCH_Z0_MM + ID_NOTCH_HEIGHT_MM
    r1_curve = [
        (float(point[0]), seat_z + min(float(curve["rear_curve_local_yz_mm"][index][1]) for curve in r1_contacts["curves"]))
        for index, point in enumerate(r1_contacts["curves"][0]["rear_curve_local_yz_mm"])
    ]
    r1_bearing_zmin = min(source_lean_yz(y, z, seat_z, lean_deg)[1] for y, z in r1_curve)
    r2_bearing_zmin = min(source_lean_yz(float(y), float(z), seat_z, lean_deg)[1] for y, z in r2_profile["revised_yz_mm"])
    rail_ymin = min(source_lean_yz(rail_y, z, seat_z, lean_deg)[0] for z in (48.0, 134.0))
    id_ymax = ID_NOTCH_Y0_MM + 2 * ID_NOTCH_PITCH_MM + ID_NOTCH_WIDTH_MM
    assert id_z1 < relief_band.BoundingBox().zmin
    assert id_z1 < r1_bearing_zmin and id_z1 < r2_bearing_zmin
    assert id_ymax < rail_ymin

    a = add_noncontact_source_id(native_a, 1, x0)
    b = add_noncontact_source_id(native_b, 2, x0)
    c = add_noncontact_source_id(c_pre_id, 3, x0)
    assert c.isValid() and len(c.Solids()) == 1

    variants = {
        "A_R1_native_control": {
            "shape": a,
            "id_notches": 1,
            "meaning": "exact native-datum R1 contact-region crop; source control, not asserted as the exact user print",
        },
        "B_R2_native_documented_capture": {
            "shape": b,
            "id_notches": 2,
            "meaning": "exact native-datum R2 contact-region crop; preserves the actual R2 GLB-re-extracted extension",
        },
        "C_R2_native_plus_1mm_seat_relief": {
            "shape": c,
            "id_notches": 3,
            "meaning": "B plus only a 1-mm downward band under the true R2 revised seat curve; a local stack/seat discriminator, not a measured correction",
        },
    }

    validation, outputs = {}, []
    for name, record in variants.items():
        shape = record["shape"]
        step = out / f"{name}.step"
        stl = out / f"{name}_X_to_print_Z.stl"
        cq.exporters.export(shape, str(step))
        cq.exporters.export(print_oriented(shape), str(stl), tolerance=0.04, angularTolerance=0.1)
        reread = cq.importers.importStep(str(step)).val()
        mesh = trimesh.load_mesh(stl)
        validation[name] = {
            "step_valid": bool(reread.isValid()),
            "step_solids": len(reread.Solids()),
            "stl_watertight": bool(mesh.is_watertight),
            "stl_components": len(mesh.split()),
            "print_bounds_mm": [float(value) for value in mesh.extents],
            "analytic_print_section": {
                "orientation": "original X rotated to print Z",
                "max_lateral_advance_per_print_layer_mm": 0.0,
                "reason": "R1/R2 source features, crop, relief band and integral ID notches are all constant YZ sections extruded through original X",
            },
        }
        assert validation[name]["step_valid"] and validation[name]["step_solids"] == 1
        assert validation[name]["stl_watertight"] and validation[name]["stl_components"] == 1
        outputs += [step, stl]

    render_png(out / "A_R1_native_control.png", [(a, (55, 111, 139))], "A — R1 native-datum control", "One integral underside ID notch; source contact crop, not a physical-fit claim.", d8)
    render_png(out / "B_R2_native_capture.png", [(b, (193, 128, 49))], "B — R2 native-datum documented capture", "Two integral underside ID notches; exact R2 crop with GLB-re-extracted seat extension.", d8)
    render_png(out / "C_R2_native_plus_1mm_relief.png", [(c, (180, 75, 63))], "C — R2 native datum plus 1-mm local seat relief", "Three integral underside ID notches; only the true R2 seat-cavity band is lowered.", d8)
    render_png(
        out / "ABC_native_datum_comparison.png",
        [(a.translate((-32, 0, 0)), (55, 111, 139)), (b, (193, 128, 49)), (c.translate((32, 0, 0)), (180, 75, 63))],
        "A / B / C native-datum handheld contact coupons",
        "A blue: R1 control. B amber: exact R2 capture. C red: B plus a local 1-mm R2 seat-cavity relief. No physical fit claimed.",
        d8,
    )
    # A thin physical X slab provides an actual Boolean section/projection,
    # rather than a schematic curve.  The left panel is B with the precise
    # B∩band volume highlighted red; the right panel is the resulting C.
    section_x = x0 + WIDTH_MM / 2.0
    section_slab = box(section_x - 0.12, crop_y0, CROP_Z0_MM, 0.24, crop_y1 - crop_y0, CROP_Z1_MM - CROP_Z0_MM)
    b_section = b_pre_id.intersect(section_slab).clean()
    c_section = c_pre_id.intersect(section_slab).clean()
    removed_section = removed_band.intersect(section_slab).clean()
    assert b_section.isValid() and c_section.isValid() and removed_section.isValid()
    render_png(
        out / "C_boolean_X_section_receipt.png",
        [
            (removed_section.translate((0, -22, 0)), (188, 64, 55)),
            (b_section.translate((0, -22, 0)), (193, 128, 49)),
            (c_section.translate((0, 22, 0)), (55, 111, 139)),
        ],
        "C Boolean receipt — actual X=19.05 mm sections",
        f"Left: B with actual B∩relief-band volume in red ({removed_by_intersection_mm3:.3f} mm³). Right: C = B minus that band.",
        d8,
        camvec=(1.0, 0.0, 0.0),
    )
    outputs += [
        out / "A_R1_native_control.png", out / "B_R2_native_capture.png", out / "C_R2_native_plus_1mm_relief.png", out / "ABC_native_datum_comparison.png", out / "C_boolean_X_section_receipt.png"
    ]

    manifest = {
        "format": "precision-5680-native-datum-contact-coupon-v2",
        "status": "analysis-only candidate pending independent same-datum geometry review; v1 is superseded for coordinate mismatch",
        "scope": "small hand-held fit/contact specimen only; not freestanding/load-qualified, a whole laptop model, print release, production D8 or CFD-contact release",
        "native_datum": {
            "x_crop_mm": [x0, x0 + WIDTH_MM],
            "y_crop_mm": [crop_y0, crop_y1],
            "z_crop_mm": [CROP_Z0_MM, CROP_Z1_MM],
            "laptop_thickness_mm": thickness,
            "r1_fence_inner_face_mm": r1_fence_inner,
            "r1_fence_outer_face_mm": r1_fence_outer,
            "r2_fence_outer_face_mm": r2_fence_outer,
            "lower_lid_rail_start_y_mm_unleaned": rail_y,
            "source_equations": "R1/R2 builders use inner=-T/2-.25-offset, outer=-T/2-3-offset and lower rail y=T/2 before lean(); v2 crops these imported solids rather than rebuilding from the 9-mm local curve span.",
        },
        "variants": {name: {key: value for key, value in record.items() if key != "shape"} for name, record in variants.items()},
        "C_changed_surface": {
            "parameter_mm": 1.0,
            "direction": "negative local Z within the unleaned R2 seat-cavity band, then the exact R2 source lean() transform",
            "source_curve": "R2/seat-profile.json revised_yz_mm, which preserves R2's actual GLB-re-extracted extension samples",
            "unchanged": ["R2 imported source solid except the Boolean band", "native fence", "native lower lid rail", "native crop datum", "low-source integral ID notch location"],
        },
        "boolean_receipt": {
            "operation": "C_pre_ID = B_pre_ID.cut(leaned_R2_curve_band)",
            "source_transform": "rotate((0,0,H), (1,0,H), -laptop_lean_deg), exactly as R2 build_quick_fit.py:45-46",
            "B_pre_ID_volume_mm3": b_pre_id.Volume(),
            "C_pre_ID_volume_mm3": c_pre_id.Volume(),
            "removed_by_B_minus_C_mm3": removed_by_difference_mm3,
            "removed_by_B_intersect_band_mm3": removed_by_intersection_mm3,
            "volume_discrepancy_mm3": abs(removed_by_difference_mm3 - removed_by_intersection_mm3),
            "relief_band_bounds_mm": [relief_band.BoundingBox().ymin, relief_band.BoundingBox().ymax, relief_band.BoundingBox().zmin, relief_band.BoundingBox().zmax],
            "x_section_mm": section_x,
            "section_render": "C_boolean_X_section_receipt.png",
        },
        "integral_id_safety_receipt": {
            "form": "one/two/three full-width through-notches in existing imported low source seat-support material; no added base is used",
            "notch_yz_bounds_mm": [ID_NOTCH_Y0_MM, id_ymax, ID_NOTCH_Z0_MM, id_z1],
            "R1_bearing_min_z_mm": r1_bearing_zmin,
            "R2_bearing_min_z_mm": r2_bearing_zmin,
            "relief_band_min_z_mm": relief_band.BoundingBox().zmin,
            "leaned_lid_rail_min_y_mm": rail_ymin,
            "proof": "ID top is below both source bearing curves and the relief band; its maximum Y is strictly inboard of the leaned source lid rail minimum Y. Every notch additionally removes its full analytic rectangular volume from native source material.",
        },
        "user_reported_behavior": "intended cradle capture misses and the laptop rocks into the short fence; this coupon separates that backup stop from the intended bearing but does not assert a measured cause or correction",
        "physical_reading_protocol": [
            "Use the integral 1/2/3-notch low-support ID to identify A/B/C; it is below the contact region.",
            "Hand-position the closed laptop local profile against the curved intended bearing; this specimen is not freestanding or load-qualified.",
            "Observe whether the intended bearing contacts before the short backup fence; do not force capture or infer force from the result.",
            "If a variant is later printed, capture one metric-scaled perpendicular photo/trace at the tested local section and retain the result with the variant ID.",
        ],
        "printability_geometry_first": {
            "orientation": "original X to print Z; X was the constant source extrusion axis",
            "proof": "Every generated feature is a constant YZ profile extruded along X. The imported R1/R2 source contact geometry is itself composed as YZ profiles extruded along X, and the crop/relief/integral-ID-notch preserve that axis. Therefore lateral layer advance is exactly zero.",
            "before_slice": "The geometry and section proof precede any slicer use. OrcaSlicer remains a later review-owned verification gate.",
        },
        "limits": [
            "R1 is a plausible V1 source but exact physical-export identity remains unproven.",
            "R1/R2 contact data derives from an AR-visualization mesh, not manufacturing metrology.",
            "C is a deliberate 1-mm discriminator, not a measured lid/case offset.",
            "No scallop, airflow, acoustic, thermal, strength, retention or CFD claim follows from this coupon.",
        ],
        "validation": validation,
        "input_sha256": {name: sha256(path) for name, path in source.items()},
        "output_sha256": {path.name: sha256(path) for path in outputs},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"variants": list(variants), "out": str(out), "manifest": "manifest.json"}, indent=2))


if __name__ == "__main__":
    main()
