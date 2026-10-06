#!/usr/bin/env python3
"""Create the V5 full-rail coupons: V4 with the lid-side rail moved 3.5 mm out.

Physical result of the printed V4 plate (user, 2026-09-17): all three A/B/C
coupons are wrong in the same way, and C (three identifier openings) is still
not enough.  The tall lid-side rail (the lid stop) sits too close to the
seat / hinge-bearing surface and the short fence.

V5 keeps every V4 feature and moves the *entire rail side* of each coupon
3.5 mm further away from everything on the seat/fence side, measured normal
to the rail face.  The flat deck between the seat and the rail is stretched
by the same 3.5 mm, so the whole coupon grows by 3.5 mm in that direction.
Nothing on the seat/fence side moves: the short fence, the curved seat, the
C relief band and the identifier openings keep their V4 coordinates.

Construction (per variant, in the imported source frame):
  1. V4 crop of the R1/R2 solid (identical to V4).
  2. Split the crop on a plane parallel to the rail face, between the end of
     the seat curve and the rail's inner face.  Only the flat deck crosses it.
  3. Translate the rail-side piece by 3.5 mm along the rail-face normal.
  4. Fill the 3.5-mm gap by extruding the deck's cut face along that normal.
  5. Fuse; then apply the unchanged V4 C relief cut and V4 identifier holes.
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
V4_DIR = HERE.parent / "profile-v4"
V2_DIR = HERE.parent / "profile-v2"
sys.path.insert(0, str(V4_DIR))
import build_full_rail_coupon_v4 as v4  # V4 is imported read-only; it imports V2.
v2 = v4.v2

DEFAULT_D8 = v4.DEFAULT_D8
WIDTH_MM = v4.WIDTH_MM
CROP_Z0_MM = v4.CROP_Z0_MM
MARGIN_MM = v4.MARGIN_MM
RAIL_SHIFT_MM = 3.5
DECK_Z_UNLEANED_MM = (46.0, 51.0)  # R1/R2 source: lean(box(-15-offset, 46, 32+offset, 5))
HALF_SPACE_MM = 400.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LeanFrame:
    """The R1/R2 source lean(): rotate about the X axis through (y=0, z=H)."""

    def __init__(self, seat_z: float, lean_deg: float):
        self.seat_z, self.lean_deg = seat_z, lean_deg
        angle = math.radians(-lean_deg)
        self.c, self.s = math.cos(angle), math.sin(angle)

    def lean(self, shape: cq.Shape) -> cq.Shape:
        return shape.rotate((0, 0, self.seat_z), (1, 0, self.seat_z), -self.lean_deg)

    def unleaned_yz(self, y: float, z: float) -> tuple[float, float]:
        dz = z - self.seat_z
        return (self.c * y + self.s * dz, -self.s * y + self.c * dz + self.seat_z)

    @property
    def rail_normal(self) -> cq.Vector:
        """Unit vector of unleaned +Y after lean(): normal to the rail face."""
        return cq.Vector(0.0, self.c, self.s)


def stretch_rail_side(shape: cq.Shape, frame: LeanFrame, split_y: float, x0: float) -> tuple[cq.Shape, dict]:
    """Move everything beyond ``split_y`` (unleaned) outward and fill the gap."""
    minus_box = frame.lean(v2.box(x0 - 1.0, split_y - HALF_SPACE_MM, -HALF_SPACE_MM, WIDTH_MM + 2.0, HALF_SPACE_MM, 2 * HALF_SPACE_MM))
    plus_box = frame.lean(v2.box(x0 - 1.0, split_y, -HALF_SPACE_MM, WIDTH_MM + 2.0, HALF_SPACE_MM, 2 * HALF_SPACE_MM))
    minus = shape.intersect(minus_box).clean()
    plus = shape.intersect(plus_box).clean()
    assert minus.isValid() and len(minus.Solids()) == 1
    assert plus.isValid() and len(plus.Solids()) == 1
    assert abs(minus.Volume() + plus.Volume() - shape.Volume()) < 1e-5

    # The cut face(s) of the rail-side piece lie exactly on the split plane.
    section_faces = []
    for face in plus.Faces():
        vertices = [frame.unleaned_yz(v.Y, v.Z) for v in face.Vertices()]
        if all(abs(y - split_y) < 1e-6 for y, _ in vertices):
            section_faces.append((face, vertices))
    assert len(section_faces) == 1, "expected exactly one deck section on the split plane"
    face, vertices = section_faces[0]
    z_values = sorted({round(z, 6) for _, z in vertices})
    assert z_values == [DECK_Z_UNLEANED_MM[0], DECK_Z_UNLEANED_MM[1]], ("split plane crosses more than the flat deck", z_values)
    expected_area = WIDTH_MM * (DECK_Z_UNLEANED_MM[1] - DECK_Z_UNLEANED_MM[0])
    assert abs(face.Area() - expected_area) < 1e-6, (face.Area(), expected_area)

    offset = frame.rail_normal * RAIL_SHIFT_MM
    filler = cq.Solid.extrudeLinear(face, offset)
    assert filler.isValid() and abs(filler.Volume() - expected_area * RAIL_SHIFT_MM) < 1e-6
    moved = plus.translate(offset)
    result = minus.fuse(moved).fuse(filler).clean()
    assert result.isValid() and len(result.Solids()) == 1
    assert abs(result.Volume() - (shape.Volume() + filler.Volume())) < 1e-5
    receipt = {
        "split_plane_unleaned_y_mm": split_y,
        "section_face_area_mm2": face.Area(),
        "section_unleaned_z_mm": z_values,
        "moved_volume_mm3": plus.Volume(),
        "kept_volume_mm3": minus.Volume(),
        "filler_volume_mm3": filler.Volume(),
        "shift_vector_mm": [offset.x, offset.y, offset.z],
    }
    return result, receipt


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
        "v4_builder": V4_DIR / "build_full_rail_coupon_v4.py",
        "v4_b_step": V4_DIR / "generated" / "B_R2_full_native_rail.step",
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
    frame = LeanFrame(seat_z, lean_deg)
    x0 = (38.1 - WIDTH_MM) / 2.0

    # V4 crop window, unchanged: derived from the R2 lower deck and the full
    # source rail corners after lean(), each with a 0.5-mm margin.
    rail_inner_y = thickness / 2.0
    rail_unleaned = [(rail_inner_y, z) for z in (48.0, 134.0)] + [(rail_inner_y + 4.0, z) for z in (48.0, 134.0)]
    deck_unleaned = [(y, z) for y in (-15.0 - float(r2_fit["lip_outward_shift_mm"]), 17.0) for z in (46.0, 51.0)]
    rail_leaned = [v4.source_lean_yz(y, z, seat_z, lean_deg) for y, z in rail_unleaned]
    deck_leaned = [v4.source_lean_yz(y, z, seat_z, lean_deg) for y, z in deck_unleaned]
    crop_y0 = min(y for y, _ in deck_leaned + rail_leaned) - MARGIN_MM
    crop_y1 = max(y for y, _ in rail_leaned) + MARGIN_MM
    crop_z1 = max(z for _, z in rail_leaned) + MARGIN_MM

    # Split plane: parallel to the rail face, midway between the end of the
    # R2 seat curve and the rail's inner face.  Only the flat deck is there.
    seat_end_y = max(float(y) for y, _ in r2_profile["revised_yz_mm"])
    split_y = (seat_end_y + rail_inner_y) / 2.0
    assert seat_end_y < split_y < rail_inner_y

    rail = v4.source_rail(x0, thickness, seat_z, lean_deg)
    rail_volume = rail.Volume()
    shift = frame.rail_normal * RAIL_SHIFT_MM
    rail_moved = rail.translate(shift)

    r1 = cq.importers.importStep(str(source["r1_step"])).val()
    r2 = cq.importers.importStep(str(source["r2_step"])).val()
    native_a = v4.native_crop(r1, x0, crop_y0, crop_y1, CROP_Z0_MM, crop_z1)
    native_b = v4.native_crop(r2, x0, crop_y0, crop_y1, CROP_Z0_MM, crop_z1)
    assert abs(native_a.intersect(rail).Volume() - rail_volume) < 1e-5
    assert abs(native_b.intersect(rail).Volume() - rail_volume) < 1e-5

    stretched_a, stretch_a = stretch_rail_side(native_a, frame, split_y, x0)
    stretched_b, stretch_b = stretch_rail_side(native_b, frame, split_y, x0)
    for name, shape in (("A", stretched_a), ("B", stretched_b)):
        # The full source rail is retained, now at its moved position.
        assert abs(shape.intersect(rail_moved).Volume() - rail_volume) < 1e-5, name
        # The old rail position is no longer a wall: only the 0.5-mm overlap
        # of the moved 4-mm rail and the stretched 5-mm deck remain there.
        old_rail_overlap = shape.intersect(rail).Volume()
        expected_overlap = WIDTH_MM * (4.0 - RAIL_SHIFT_MM) * 86.0 + WIDTH_MM * RAIL_SHIFT_MM * 3.0
        assert abs(old_rail_overlap - expected_overlap) < 1e-5, (name, old_rail_overlap, expected_overlap)
        # Nothing on the seat/fence side moved: the crop below the split plane
        # is byte-for-byte the V4 solid there.
        kept_box = frame.lean(v2.box(x0 - 1.0, split_y - HALF_SPACE_MM, -HALF_SPACE_MM, WIDTH_MM + 2.0, HALF_SPACE_MM, 2 * HALF_SPACE_MM))
        original = native_a if name == "A" else native_b
        kept_difference = shape.intersect(kept_box).cut(original).Volume() + original.intersect(kept_box).cut(shape).Volume()
        assert kept_difference < 1e-6, (name, kept_difference)

    # The new lid channel above the deck, between the old and new rail faces,
    # is empty: the lid can sit 3.5 mm further from the fence and seat.
    channel = frame.lean(v2.box(x0, rail_inner_y, DECK_Z_UNLEANED_MM[1] + 1e-3, WIDTH_MM, RAIL_SHIFT_MM, 134.0 - DECK_Z_UNLEANED_MM[1]))
    assert stretched_a.intersect(channel).Volume() < 1e-6
    assert stretched_b.intersect(channel).Volume() < 1e-6

    relief_band = v2.r2_relief_ring(r2_profile["revised_yz_mm"], x0, seat_z, lean_deg)
    removed_band = stretched_b.intersect(relief_band).clean()
    c_pre_id = stretched_b.cut(relief_band).clean()
    assert removed_band.isValid() and removed_band.Volume() > 0.0
    assert c_pre_id.isValid() and len(c_pre_id.Solids()) == 1
    assert abs((stretched_b.Volume() - c_pre_id.Volume()) - removed_band.Volume()) < 1e-5
    assert abs(c_pre_id.intersect(rail_moved).Volume() - rail_volume) < 1e-5
    v4_b = cq.importers.importStep(str(source["v4_b_step"])).val()

    # V4 identifiers, unchanged: 2-mm square through-X holes on a 4-mm pitch
    # with a 1-mm solid halo, in the low seat-support material.
    id_receipts = {}

    def mark(shape, count, letter):
        result = shape
        for index in range(count):
            y, z = -5.0 + index * 4.0, 47.8
            hole = v2.box(x0, y, z, WIDTH_MM, 2.0, 2.0)
            halo = v2.box(x0, y - 1.0, z - 1.0, WIDTH_MM, 4.0, 4.0)
            assert halo.cut(shape).Volume() < 1e-5, (letter, index, "one-mm material halo")
            assert abs(shape.intersect(hole).Volume() - 96.0) < 1e-5
            assert hole.intersect(rail_moved).Volume() < 1e-6
            assert hole.intersect(relief_band).Volume() < 1e-6
            result = result.cut(hole).clean()
        assert result.isValid() and len(result.Solids()) == 1
        assert abs(shape.Volume() - result.Volume() - count * 96.0) < 1e-5
        assert abs(result.intersect(rail_moved).Volume() - rail_volume) < 1e-5
        id_receipts[letter] = {"count": count, "removed_volume_mm3": shape.Volume() - result.Volume(), "hole_side_mm": 2.0, "pitch_mm": 4.0, "native_y_starts_mm": [-5.0 + i * 4.0 for i in range(count)], "native_z_mm": [47.8, 49.8], "source_solid_halo_mm": 1.0, "inter_hole_ligament_mm": 2.0, "rail_and_relief_intersection_mm3": 0.0}
        return result

    a = mark(stretched_a, 1, "A")
    b = mark(stretched_b, 2, "B")
    c = mark(c_pre_id, 3, "C")

    variants = {
        "A_R1_full_rail_plus_3p5mm": (a, 1, "V4 A (R1 crop, full rail) with the rail side moved 3.5 mm outward"),
        "B_R2_full_rail_plus_3p5mm": (b, 2, "V4 B (R2 crop, full rail) with the rail side moved 3.5 mm outward"),
        "C_R2_full_rail_plus_3p5mm_plus_1mm_seat_relief": (c, 3, "V4 C (B plus the 1-mm R2 seat-relief band) with the rail side moved 3.5 mm outward"),
    }
    validation, outputs = {}, []
    for name, (shape, identifier, meaning) in variants.items():
        step = out / f"{name}.step"
        stl = out / f"{name}_X_to_print_Z.stl"
        cq.exporters.export(shape, str(step))
        cq.exporters.export(v2.print_oriented(shape), str(stl), tolerance=0.04, angularTolerance=0.1)
        reread = cq.importers.importStep(str(step)).val()
        mesh = trimesh.load_mesh(stl)
        bounds = shape.BoundingBox()
        validation[name] = {
            "id_holes": identifier,
            "meaning": meaning,
            "step_valid": bool(reread.isValid()),
            "step_solids": len(reread.Solids()),
            "stl_watertight": bool(mesh.is_watertight),
            "stl_components": len(mesh.split()),
            "source_bounds_mm": [[bounds.xmin, bounds.ymin, bounds.zmin], [bounds.xmax, bounds.ymax, bounds.zmax]],
            "print_bounds_mm": [float(value) for value in mesh.extents],
            "geometry_first_print_proof": "The full rail, fence, seat, crop, deck filler, C band and ID holes are all constant YZ profiles extruded along original X. Rotating original X to print Z makes every layer identical in lateral outline; this is geometry evidence only, not an Orca result.",
        }
        assert validation[name]["step_valid"] and validation[name]["step_solids"] == 1
        assert validation[name]["stl_watertight"] and validation[name]["stl_components"] == 1
        outputs += [step, stl]

    v2.render_png(
        out / "ABC_full_rail_plus_3p5mm_comparison.png",
        [(a.translate((-36, 0, 0)), (55, 111, 139)), (b, (193, 128, 49)), (c.translate((36, 0, 0)), (180, 75, 63))],
        "A / B / C — V5: full lid rail moved 3.5 mm outward",
        "V4 crops with the whole rail side shifted 3.5 mm normal to the rail face; the deck between seat and rail grows by 3.5 mm. Seat, fence, relief and IDs unchanged.",
        d8,
    )
    section_x = x0 + WIDTH_MM / 2.0
    slab = v2.box(section_x - 0.12, crop_y0 - 1.0, CROP_Z0_MM - 1.0, 0.24, crop_y1 - crop_y0 + RAIL_SHIFT_MM + 2.0, crop_z1 - CROP_Z0_MM + 2.0)
    v4_section = v4_b.intersect(slab).clean()
    v5_section = stretched_b.intersect(slab).clean()
    filler_section = stretched_b.cut(v4_b).intersect(slab).clean()
    v2.render_png(
        out / "B_V4_vs_V5_X_section.png",
        [(v4_section.translate((0, -34, 0)), (150, 150, 150)), (v5_section.translate((0, 34, 0)), (193, 128, 49)), (filler_section.translate((0, 34, 0)), (188, 64, 55))],
        f"B section receipt — V4 (gray) vs V5 (amber), X={section_x:.2f} mm",
        f"Red on V5: material that is new relative to V4 ({stretched_b.cut(v4_b).Volume():.1f} mm3 = moved rail side plus the {stretch_b['filler_volume_mm3']:.0f} mm3 deck filler).",
        d8,
        camvec=(1.0, 0.0, 0.0),
    )
    outputs += [out / "ABC_full_rail_plus_3p5mm_comparison.png", out / "B_V4_vs_V5_X_section.png"]

    fence_inner_r1 = -thickness / 2.0 - 0.25
    fence_inner_r2 = fence_inner_r1 - float(r2_fit["lip_outward_shift_mm"])
    manifest = {
        "format": "precision-5680-full-native-lid-rail-contact-coupon-v5",
        "status": "V4 geometry with the rail side moved 3.5 mm outward after the printed V4 plate failed the same way on all three variants; pending independent review and one fixed-pose Orca verification",
        "scope": "small hand-held local contact/clearance-reading specimen; no freestanding, strength, CFD, production or physical-fit qualification",
        "physical_input": "User printed the V4 A/B/C plate: all three were wrong and C (three openings) was still not enough. Instruction: move the tall lid-stop wall 3.5 mm further from the seat/hinge/rest/bearing surface and the short fence so the whole coupon grows by 3.5 mm normal to the tall wall. The 3.5 mm is a requested trial increment, not a measured lid thickness.",
        "rail_offset": {
            "shift_mm": RAIL_SHIFT_MM,
            "direction": "unleaned source +Y after the R1/R2 lean(), i.e. the outward normal of the rail's inner face",
            "shift_vector_mm": [shift.x, shift.y, shift.z],
            "split_plane_unleaned_y_mm": split_y,
            "split_plane_between": {"r2_seat_curve_end_y_mm": seat_end_y, "rail_inner_face_y_mm": rail_inner_y},
            "moved": "every feature on the rail side of the split plane: the full 86-mm lid rail, its deck portion and any cropped brace remnant",
            "unchanged": "short fence, curved seat, seat-support column, C relief band, identifier holes, crop datum on the fence side",
            "rail_inner_face_unleaned_y_mm": {"V4": rail_inner_y, "V5": rail_inner_y + RAIL_SHIFT_MM},
            "fence_inner_to_rail_inner_mm": {
                "A_R1": {"V4": rail_inner_y - fence_inner_r1, "V5": rail_inner_y + RAIL_SHIFT_MM - fence_inner_r1},
                "B_and_C_R2": {"V4": rail_inner_y - fence_inner_r2, "V5": rail_inner_y + RAIL_SHIFT_MM - fence_inner_r2},
            },
            "stretch_receipts": {"A": stretch_a, "B": stretch_b},
        },
        "crop": {
            "x_mm": [x0, x0 + WIDTH_MM],
            "y_mm_before_shift": [crop_y0, crop_y1],
            "z_mm_before_shift": [CROP_Z0_MM, crop_z1],
            "derivation": "Identical V4 window: Y/Z bounds derive from the exact R2 lower-deck and full lid-rail corners after original source lean(), each with a 0.5-mm crop margin. The rail-side piece is shifted after cropping, so the finished coupon extends 3.5 mm beyond this window along the rail normal.",
        },
        "full_native_rail": {
            "unleaned_source_equation": "lean(box(T/2, 48, 4, 86)) then translate by shift_vector_mm",
            "unleaned_yz_mm_before_shift": [rail_inner_y, rail_inner_y + 4.0, 48.0, 134.0],
            "unleaned_height_above_seat_mm": 80.0,
            "leaned_yz_corners_mm_before_shift": rail_leaned,
            "full_rail_volume_mm3_over_24mm_coupon_width": rail_volume,
            "retained_moved_rail_volume_mm3": {"A": a.intersect(rail_moved).Volume(), "B": b.intersect(rail_moved).Volume(), "C": c.intersect(rail_moved).Volume()},
            "proof": "Each finished coupon contains the full explicit source rail volume at its moved position; the 3.5-mm channel between the old and new rail faces above the deck is empty.",
        },
        "C_boolean_receipt": {
            "operation": "C_pre_ID = stretched_B.cut(leaned_R2_curve_band)",
            "source_transform": "rotate((0,0,H), (1,0,H), -laptop_lean_deg), matching R2 build_quick_fit.py lean()",
            "removed_by_B_minus_C_mm3": stretched_b.Volume() - c_pre_id.Volume(),
            "removed_by_B_intersect_band_mm3": removed_band.Volume(),
            "difference_mm3": abs((stretched_b.Volume() - c_pre_id.Volume()) - removed_band.Volume()),
            "section_x_mm": section_x,
            "section_render": "B_V4_vs_V5_X_section.png",
        },
        "reading_protocol": [
            "Hand-position only; do not use the tall rail as a lever or press it toward the lid.",
            "Observe first contact among intended seat, short fence and the moved tall rail. Stop if rail flex, forced capture or rocking occurs.",
            "V5 prints look like V4 prints: tell them apart by the flat deck between the seat and the tall rail, which is 3.5 mm longer on V5. Label or discard the V4 prints before comparing.",
        ],
        "limits": [
            "The source reference is an AR visualization, not manufacturing metrology.",
            "3.5 mm is the user's requested increment from handling the printed V4 plate; it is not a measured lid thickness or curvature.",
            "No slice, print, solver, CFD, acoustic, strength or physical-fit conclusion follows from this artifact.",
        ],
        "validation": validation,
        "identifier_geometry": id_receipts,
        "builder_sha256": sha256(Path(__file__)),
        "input_sha256": {name: sha256(path) for name, path in source.items()},
        "output_sha256": {path.name: sha256(path) for path in outputs},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"rail_offset": {k: v for k, v in manifest["rail_offset"].items() if k != "stretch_receipts"}, "outputs": [path.name for path in outputs]}, indent=2))


if __name__ == "__main__":
    main()
