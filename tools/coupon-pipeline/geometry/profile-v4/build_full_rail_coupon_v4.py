#!/usr/bin/env python3
"""Create the V4 full native lid-rail diagnostic coupon.

V2 remains frozen.  This separate study preserves V2's imported R1/R2 source
solids and C-only leaned seat-relief Boolean, but its crop reaches the full
original 86-mm unleaned lid-side rail instead of stopping at V2's z=72 mm.
It deliberately does *not* fabricate the reported slight lid-top curve.
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


HERE = Path(__file__).resolve().parent
V2_DIR = HERE.parent / "profile-v2"
sys.path.insert(0, str(V2_DIR))
import build_native_datum_coupon_v2 as v2  # V2 is imported read-only.


DEFAULT_D8 = Path("/mnt/f/Code/5680-dock-fit-20260917/desk-dock/D8")
WIDTH_MM = 24.0
CROP_Z0_MM = 44.0
MARGIN_MM = 0.5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native_crop(shape: cq.Shape, x0: float, y0: float, y1: float, z0: float, z1: float) -> cq.Shape:
    crop = v2.box(x0, y0, z0, WIDTH_MM, y1 - y0, z1 - z0)
    result = shape.intersect(crop).clean()
    assert result.isValid() and len(result.Solids()) == 1
    return result


def source_lean_yz(y: float, z: float, seat_z: float, lean_deg: float) -> tuple[float, float]:
    """The original R1/R2 `lean()` equation, evaluated for native bounds."""
    angle = math.radians(-lean_deg)
    dz = z - seat_z
    return (
        math.cos(angle) * y - math.sin(angle) * dz,
        math.sin(angle) * y + math.cos(angle) * dz + seat_z,
    )


def source_rail(x0: float, thickness: float, seat_z: float, lean_deg: float) -> cq.Shape:
    """Exact R1/R2 lid-side rail primitive before its source `lean()` call."""
    rail = v2.prism([(thickness / 2.0, 48.0), (thickness / 2.0 + 4.0, 48.0), (thickness / 2.0 + 4.0, 134.0), (thickness / 2.0, 134.0)], WIDTH_MM, x0)
    return rail.rotate((0, 0, seat_z), (1, 0, seat_z), -lean_deg)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--d8", type=Path, default=DEFAULT_D8)
    parser.add_argument("--out", type=Path, default=HERE / "generated")
    args = parser.parse_args()
    d8, out = args.d8.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    source = {
        "parameters": d8 / "parameters.json",
        "r1_step": d8 / "quick-fit" / "D8-quick-fit-bracket.step",
        "r2_step": d8 / "quick-fit" / "R2" / "D8-R2-quick-fit-bracket.step",
        "r2_fit_parameters": d8 / "quick-fit" / "R2" / "fit-parameters.json",
        "r2_seat_profile": d8 / "quick-fit" / "R2" / "seat-profile.json",
        "r2_builder": d8 / "quick-fit" / "R2" / "build_quick_fit.py",
        "v2_builder": V2_DIR / "build_native_datum_coupon_v2.py",
    }
    missing = [name for name, path in source.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))

    params = json.loads(source["parameters"].read_text(encoding="utf-8"))
    r2_fit = json.loads(source["r2_fit_parameters"].read_text(encoding="utf-8"))
    r2_profile = json.loads(source["r2_seat_profile"].read_text(encoding="utf-8"))
    thickness = float(params["laptop_thickness"])
    seat_z = float(params["rear_case_seat_z"])
    lean_deg = float(params["laptop_lean_deg"])
    x0 = (38.1 - WIDTH_MM) / 2.0

    # Full native rail: R1/R2 construct lean(box(T/2, 48, 4, 86)).  Bounds
    # derive from its actual leaned corners.  R2's lower deck reaches y=-17
    # before lean and controls the other side of this contact-region crop.
    rail_unleaned = [(thickness / 2.0, z) for z in (48.0, 134.0)] + [(thickness / 2.0 + 4.0, z) for z in (48.0, 134.0)]
    deck_unleaned = [(y, z) for y in (-15.0 - float(r2_fit["lip_outward_shift_mm"]), 17.0) for z in (46.0, 51.0)]
    rail_leaned = [source_lean_yz(y, z, seat_z, lean_deg) for y, z in rail_unleaned]
    deck_leaned = [source_lean_yz(y, z, seat_z, lean_deg) for y, z in deck_unleaned]
    crop_y0 = min(y for y, _ in deck_leaned + rail_leaned) - MARGIN_MM
    crop_y1 = max(y for y, _ in rail_leaned) + MARGIN_MM
    crop_z1 = max(z for _, z in rail_leaned) + MARGIN_MM

    crop_box = v2.box(x0, crop_y0, CROP_Z0_MM, WIDTH_MM, crop_y1 - crop_y0, crop_z1 - CROP_Z0_MM)
    rail = source_rail(x0, thickness, seat_z, lean_deg)
    assert rail.cut(crop_box).Volume() < 1e-6, "crop clips the explicit full-height native rail"

    r1 = cq.importers.importStep(str(source["r1_step"])).val()
    r2 = cq.importers.importStep(str(source["r2_step"])).val()
    native_a = native_crop(r1, x0, crop_y0, crop_y1, CROP_Z0_MM, crop_z1)
    native_b = native_crop(r2, x0, crop_y0, crop_y1, CROP_Z0_MM, crop_z1)
    # The imported source must retain the entire explicit rail, not merely fit
    # it inside the bounding crop.  This test is common to A/B and then C.
    rail_volume = rail.Volume()
    rail_a_retained = native_a.intersect(rail).Volume()
    rail_b_retained = native_b.intersect(rail).Volume()
    assert abs(rail_a_retained - rail_volume) < 1e-5
    assert abs(rail_b_retained - rail_volume) < 1e-5

    relief_band = v2.r2_relief_ring(r2_profile["revised_yz_mm"], x0, seat_z, lean_deg)
    removed_band = native_b.intersect(relief_band).clean()
    c_pre_id = native_b.cut(relief_band).clean()
    assert removed_band.isValid() and removed_band.Volume() > 0.0
    assert c_pre_id.isValid() and len(c_pre_id.Solids()) == 1
    assert abs((native_b.Volume() - c_pre_id.Volume()) - removed_band.Volume()) < 1e-5
    rail_c_retained = c_pre_id.intersect(rail).Volume()
    assert abs(rail_c_retained - rail_volume) < 1e-5

    # Manufacturing correction chosen geometrically after V3's failed ID
    # verification: 2-mm square holes on a 4-mm pitch, with a 1-mm solid
    # halo in the source before cuts. Through-X holes remain vertical voids
    # in the chosen print orientation, requiring neither support nor bridges.
    id_receipts = {}
    def mark(shape, count, letter):
        result = shape
        for index in range(count):
            y, z = -5.0 + index * 4.0, 47.8
            hole = v2.box(x0, y, z, WIDTH_MM, 2.0, 2.0)
            halo = v2.box(x0, y-1.0, z-1.0, WIDTH_MM, 4.0, 4.0)
            assert halo.cut(shape).Volume() < 1e-5, (letter, index, "one-mm material halo")
            assert abs(shape.intersect(hole).Volume()-96.0) < 1e-5
            assert hole.intersect(rail).Volume() < 1e-6
            assert hole.intersect(relief_band).Volume() < 1e-6
            result = result.cut(hole).clean()
        assert result.isValid() and len(result.Solids()) == 1
        assert abs(shape.Volume()-result.Volume()-count*96.0) < 1e-5
        assert abs(result.intersect(rail).Volume()-rail_volume) < 1e-5
        id_receipts[letter] = {"count":count,"removed_volume_mm3":shape.Volume()-result.Volume(),"hole_side_mm":2.0,"pitch_mm":4.0,"native_y_starts_mm":[-5.0+i*4.0 for i in range(count)],"native_z_mm":[47.8,49.8],"source_solid_halo_mm":1.0,"inter_hole_ligament_mm":2.0,"rail_and_relief_intersection_mm3":0.0}
        return result
    a = mark(native_a, 1, "A")
    b = mark(native_b, 2, "B")
    c = mark(c_pre_id, 3, "C")

    variants = {
        "A_R1_full_native_rail": (a, 1, "R1 direct crop with the complete source lid-side rail height"),
        "B_R2_full_native_rail": (b, 2, "R2 direct crop with the complete source lid-side rail height"),
        "C_R2_full_rail_plus_1mm_seat_relief": (c, 3, "B plus only the isolated, leaned one-mm R2 seat-relief band"),
    }
    validation, outputs = {}, []
    for name, (shape, identifier, meaning) in variants.items():
        step = out / f"{name}.step"
        stl = out / f"{name}_X_to_print_Z.stl"
        cq.exporters.export(shape, str(step))
        cq.exporters.export(v2.print_oriented(shape), str(stl), tolerance=0.04, angularTolerance=0.1)
        reread = cq.importers.importStep(str(step)).val()
        mesh = trimesh.load_mesh(stl)
        validation[name] = {
            "id_holes": identifier,
            "meaning": meaning,
            "step_valid": bool(reread.isValid()),
            "step_solids": len(reread.Solids()),
            "stl_watertight": bool(mesh.is_watertight),
            "stl_components": len(mesh.split()),
            "print_bounds_mm": [float(value) for value in mesh.extents],
            "geometry_first_print_proof": "The full rail, fence, seat, crop, C band and ID holes are all constant YZ profiles extruded along original X. Rotating original X to print Z makes every layer identical in lateral outline; this is geometry evidence only, not an Orca result.",
        }
        assert validation[name]["step_valid"] and validation[name]["step_solids"] == 1
        assert validation[name]["stl_watertight"] and validation[name]["stl_components"] == 1
        outputs += [step, stl]

    v2.render_png(
        out / "ABC_full_native_rail_comparison.png",
        [(a.translate((-36, 0, 0)), (55, 111, 139)), (b, (193, 128, 49)), (c.translate((36, 0, 0)), (180, 75, 63))],
        "A / B / C — full native lid-rail height coupons",
        "Direct R1/R2 rail retained through its original 86-mm unleaned span. C changes only the leaned local seat band. No physical lid-curve fit claimed.",
        d8,
    )
    section_x = x0 + WIDTH_MM / 2.0
    slab = v2.box(section_x - 0.12, crop_y0, CROP_Z0_MM, 0.24, crop_y1 - crop_y0, crop_z1 - CROP_Z0_MM)
    b_section = native_b.intersect(slab).clean()
    c_section = c_pre_id.intersect(slab).clean()
    removed_section = removed_band.intersect(slab).clean()
    v2.render_png(
        out / "C_full_rail_boolean_X_section.png",
        [(removed_section.translate((0, -32, 0)), (188, 64, 55)), (b_section.translate((0, -32, 0)), (193, 128, 49)), (c_section.translate((0, 32, 0)), (55, 111, 139))],
        f"C Boolean receipt — full rail, X={section_x:.2f} mm",
        f"Left: B with B intersection relief band in red ({removed_band.Volume():.3f} mm3). Right: C after the same sole Boolean.",
        d8,
        camvec=(1.0, 0.0, 0.0),
    )
    outputs += [out / "ABC_full_native_rail_comparison.png", out / "C_full_rail_boolean_X_section.png"]

    manifest = {
        "format": "precision-5680-full-native-lid-rail-contact-coupon-v4",
        "status": "analysis candidate; V3 frozen as ID-toolpath HOLD; V4 retains full native geometry with enlarged noncontact identifiers pending independent review",
        "scope": "small hand-held local contact/clearance-reading specimen; no freestanding, strength, CFD, print, production or physical-fit qualification",
        "physical_input": "User reports a slight closed-lid top curve and asks for a taller coupon. No curvature amplitude, radius, contact location or physical correction is measured here.",
        "crop": {
            "x_mm": [x0, x0 + WIDTH_MM],
            "y_mm": [crop_y0, crop_y1],
            "z_mm": [CROP_Z0_MM, crop_z1],
            "derivation": "Y/Z bounds derive from the exact R2 lower-deck and full lid-rail corners after original source lean(), each with a 0.5-mm crop margin.",
        },
        "full_native_rail": {
            "unleaned_source_equation": "lean(box(T/2, 48, 4, 86))",
            "unleaned_yz_mm": [thickness / 2.0, thickness / 2.0 + 4.0, 48.0, 134.0],
            "unleaned_height_above_seat_mm": 80.0,
            "leaned_yz_corners_mm": rail_leaned,
            "full_rail_volume_mm3_over_24mm_coupon_width": rail_volume,
            "retained_volume_mm3": {"A": rail_a_retained, "B": rail_b_retained, "C_pre_ID": rail_c_retained},
            "proof": "Each imported crop contains the full explicit source rail volume; no tall rail face is truncated by the crop.",
        },
        "C_boolean_receipt": {
            "operation": "C_pre_ID = imported_R2_crop.cut(leaned_R2_curve_band)",
            "source_transform": "rotate((0,0,H), (1,0,H), -laptop_lean_deg), matching R2 build_quick_fit.py lean()",
            "removed_by_B_minus_C_mm3": native_b.Volume() - c_pre_id.Volume(),
            "removed_by_B_intersect_band_mm3": removed_band.Volume(),
            "difference_mm3": abs((native_b.Volume() - c_pre_id.Volume()) - removed_band.Volume()),
            "section_x_mm": section_x,
            "section_render": "C_full_rail_boolean_X_section.png",
        },
        "curved_lid_contact_reading_envelope": {
            "hypothesis_only": "The taller source rail can reveal whether the reported local lid-top curvature reaches it before the intended seat. It does not model the actual curve.",
            "numeric_variable": "full native rail height: 86 mm before lean, spanning unleaned z=48..134; V4 crop upper Z is derived from its leaned corners.",
            "protocol": [
                "Hand-position only; do not use the tall rail as a lever or press it toward the lid.",
                "Observe first contact among intended seat, short fence and the retained tall rail. Stop if rail flex, forced capture or rocking occurs.",
                "If a future print is authorized, record one scaled perpendicular photo/trace at the tested X section and variant ID. Do not infer curvature amplitude from this coupon alone.",
            ],
        },
        "rail_stiffness_and_brace_limit": {
            "geometry": "24-mm-wide by 4-mm unleaned rail section, 86-mm source span before lean; direct crop retains only whatever source brace material lies within the fixed local window.",
            "limit": "No rail stiffness, allowable hand force, retention, impact or fatigue value is established. Treat this as a no-force hand-contact reader; visible flex or required push is an abort condition.",
            "cropped_brace_remnants": "No arbitrary base or brace is added. Any adjacent source material inside the direct crop is a cropped remnant and must not be credited as structural bracing.",
        },
        "limits": [
            "The source reference is an AR visualization, not manufacturing metrology.",
            "V4 records but does not quantify the user's curved-lid observation.",
            "Two-mm square through-holes were selected before slicing with full source halo and contact-separation checks; actual toolpath survival remains a later gate.",
            "No slice, print, solver, CFD, acoustic, strength or physical-fit conclusion follows from this artifact.",
        ],
        "validation": validation,
        "identifier_geometry": id_receipts,
        "builder_sha256": sha256(Path(__file__)),
        "input_sha256": {name: sha256(path) for name, path in source.items()},
        "output_sha256": {path.name: sha256(path) for path in outputs},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"crop": manifest["crop"], "outputs": [path.name for path in outputs]}, indent=2))


if __name__ == "__main__":
    main()
