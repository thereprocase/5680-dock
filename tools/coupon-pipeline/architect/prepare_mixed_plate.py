"""Place already-oriented STLs of mixed sizes on one P1S plate as a frozen 3MF.

Footprint-aware: each object's bed outline is taken from a section just above
its base, rotated about Z as requested, and objects are placed greedily on a
2-mm grid keeping a minimum clearance between outlines (default 16 mm, room
for two 5-mm brims). Large objects go first in the order given; a hollow
triangular bracket and its 180-degree twin therefore nest hypotenuse to
hypotenuse instead of wasting two bounding boxes. No slicer is run here.

  cadpy prepare_mixed_plate.py --profiles profiles/frozen-normal --review-receipt R4-REVIEW.md --out r4-orca \
      --stl bracket.stl --rot 0 --strict --stl bracket.stl --rot 180 --strict --stl pin.stl ...

`--rot`, `--strict` and `--pos x,y` attach to the most recent `--stl`. Strict
objects must slice with zero support and zero external bridge paths.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import shutil
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh
from shapely.geometry import Polygon, box as shapely_box
from shapely.ops import unary_union
from PIL import Image, ImageDraw

NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('', NS)
BED = 256.0
EDGE = 1.0
EXCLUDED = shapely_box(0, 0, 18.5, 28.5)  # P1S front-left excluded zone (purge area)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Item:
    def __init__(self, path, rot, strict, pos):
        self.path, self.rot, self.strict, self.pos = path, rot, strict, pos
        mesh = trimesh.load_mesh(path)
        assert mesh.is_watertight, path
        if rot:
            mesh.apply_transform(trimesh.transformations.rotation_matrix(math.radians(rot), [0, 0, 1]))
        mesh.apply_translation(-mesh.bounds[0])
        self.mesh = mesh
        section = mesh.section(plane_origin=[0, 0, min(0.4, mesh.extents[2] / 2)], plane_normal=[0, 0, 1])
        planar, to_3d = section.to_2D()
        def back(coords):  # map the section's local 2-D frame back into mesh XY
            pts = np.c_[np.asarray(coords)[:, :2], np.zeros(len(coords)), np.ones(len(coords))] @ to_3d.T
            return pts[:, :2]
        outline = unary_union([Polygon(back(p.exterior.coords), [back(r.coords) for r in p.interiors]) for p in planar.polygons_full])
        self.outline = outline.buffer(0)
        assert self.outline.area > 0
        self.name = Path(path).stem
        self.translation = None

    def placed(self, x, y):
        return trimesh.transformations.translation_matrix([x, y, 0])

    def outline_at(self, x, y):
        from shapely.affinity import translate
        return translate(self.outline, x, y)


def place(items, gap):
    occupied = []
    keepout = EXCLUDED.buffer(gap / 2)
    for item in items:
        w, d = item.mesh.extents[0], item.mesh.extents[1]
        if item.pos is not None:
            candidates = [item.pos]
        else:
            xs = np.arange(EDGE + gap / 2, BED - EDGE - gap / 2 - w + 1e-9, 2.0)
            ys = np.arange(EDGE + gap / 2, BED - EDGE - gap / 2 - d + 1e-9, 2.0)
            candidates = [(x, y) for y in ys for x in xs]
        best = None
        blocked = unary_union([o.buffer(gap / 2) for o in occupied]) if occupied else None
        for x, y in candidates:
            outline = item.outline_at(x, y)
            if outline.intersects(keepout):
                continue
            if blocked is not None and outline.buffer(gap / 2 - 1e-6).intersects(blocked):
                continue
            union = unary_union(occupied + [outline]) if occupied else outline
            score = (union.bounds[2] - union.bounds[0]) * (union.bounds[3] - union.bounds[1]) + 0.01 * (x + y)
            if best is None or score < best[0]:
                best = (score, x, y, outline)
        assert best is not None, f'no placement for {item.name}'
        _, x, y, outline = best
        item.translation = [float(x), float(y), 0.0]
        occupied.append(outline)
    return occupied


def preview(items, path):
    scale = 3
    image = Image.new('RGB', (int(BED * scale), int(BED * scale)), '#f7f8fa')
    draw = ImageDraw.Draw(image)
    def pt(p):
        return (p[0] * scale, (BED - p[1]) * scale)
    draw.rectangle((pt((0, BED)), pt((BED, 0))), outline='#888')
    draw.rectangle((pt((0, 28.5)), pt((18.5, 0))), fill='#f3c9c9')
    for item in items:
        outline = item.outline_at(item.translation[0], item.translation[1])
        polys = [outline] if outline.geom_type == 'Polygon' else list(outline.geoms)
        for poly in polys:
            draw.polygon([pt(c) for c in poly.exterior.coords], outline='#0b5f8a' if item.strict else '#a35a00', fill='#bfe0f2' if item.strict else '#f7dfb8')
        b = outline.bounds
        draw.text(pt(((b[0] + b[2]) / 2 - 8, (b[1] + b[3]) / 2)), item.name[:22], fill='#17364b')
    image.save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--stl', action='append', type=Path, required=True)
    parser.add_argument('--rot', action='append', type=float, default=[])
    parser.add_argument('--strict', action='append_const', const=True, default=[])
    parser.add_argument('--pos', action='append', default=[])
    parser.add_argument('--gap', type=float, default=16.0)
    parser.add_argument('--profiles', type=Path, required=True)
    parser.add_argument('--review-receipt', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args, _ = parser.parse_known_args()
    # Re-parse attaching per-object options to the preceding --stl.
    specs, current = [], None
    import sys
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--stl':
            current = {'path': Path(argv[i + 1]), 'rot': 0.0, 'strict': False, 'pos': None}; specs.append(current); i += 2
        elif a == '--rot':
            current['rot'] = float(argv[i + 1]); i += 2
        elif a == '--pos':
            current['pos'] = tuple(float(v) for v in argv[i + 1].split(',')); i += 2
        elif a == '--strict':
            current['strict'] = True; i += 1
        elif a in ('--gap', '--profiles', '--review-receipt', '--out'):
            i += 2
        else:
            raise SystemExit(f'unexpected argument {a}')
    assert args.review_receipt.is_file(), 'Reviewed geometry receipt required'
    assert not args.out.exists(), 'Use a new output directory to preserve evidence'
    items = [Item(str(s['path'].resolve()), s['rot'], s['strict'], s['pos']) for s in specs]
    # Unique object names for duplicates (e.g. the bracket pair).
    seen = {}
    for item in items:
        seen[item.name] = seen.get(item.name, 0) + 1
        if seen[item.name] > 1:
            item.name = f'{item.name}-{seen[item.name]}'
    place(items, args.gap)

    root = ET.Element(f'{{{NS}}}model', {'unit': 'millimeter', 'xml:lang': 'en-US'})
    resources = ET.SubElement(root, f'{{{NS}}}resources')
    build = ET.SubElement(root, f'{{{NS}}}build')
    records = []
    for oid, item in enumerate(items, 1):
        obj = ET.SubElement(resources, f'{{{NS}}}object', {'id': str(oid), 'type': 'model', 'name': item.name})
        objmesh = ET.SubElement(obj, f'{{{NS}}}mesh')
        verts = ET.SubElement(objmesh, f'{{{NS}}}vertices')
        tris = ET.SubElement(objmesh, f'{{{NS}}}triangles')
        for v in item.mesh.vertices:
            ET.SubElement(verts, f'{{{NS}}}vertex', {'x': format(v[0], '.9g'), 'y': format(v[1], '.9g'), 'z': format(v[2], '.9g')})
        for face in item.mesh.faces:
            ET.SubElement(tris, f'{{{NS}}}triangle', {'v1': str(face[0]), 'v2': str(face[1]), 'v3': str(face[2])})
        shift = item.translation
        ET.SubElement(build, f'{{{NS}}}item', {'objectid': str(oid), 'transform': '1 0 0 0 1 0 0 0 1 ' + ' '.join(format(n, '.9g') for n in shift)})
        lo, hi = item.mesh.bounds
        records.append({'name': item.name, 'source': item.path, 'sha256': digest(Path(item.path)), 'rotation_z_deg': item.rot, 'strict': item.strict,
                        'bounds_before_mm': [lo.tolist(), hi.tolist()], 'translation_mm': shift,
                        'bed_bounds_mm': [[float(lo[i] + shift[i]) for i in range(3)], [float(hi[i] + shift[i]) for i in range(3)]],
                        'footprint_area_mm2': float(item.outline.area)})
    args.out.mkdir(parents=True)
    path = args.out / 'reviewed-coupons-input.3mf'
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        archive.writestr('_rels/.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        archive.writestr('3D/3dmodel.model', ET.tostring(root, encoding='utf-8', xml_declaration=True))
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
    profile_receipt = {}
    for name in ('machine.json', 'process.json', 'filament.json', 'profile-selection.json'):
        shutil.copy2(args.profiles / name, args.out / name)
        profile_receipt[name] = digest(args.profiles / name)
    shutil.copy2(args.review_receipt, args.out / 'geometry-review-receipt.md')
    preview(items, args.out / 'plate-layout.png')
    receipt = {'stage': 'prepared, not sliced', 'orientation': 'source STL pose retained except the recorded Z rotation; translation only',
               'gap_mm': args.gap, 'objects': records, 'input_3mf_sha256': digest(path), 'profile_sha256': profile_receipt,
               'geometry_review_sha256': digest(args.review_receipt)}
    (args.out / 'plate-preparation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'objects': [(r['name'], [round(v, 1) for v in r['bed_bounds_mm'][0][:2]], [round(v, 1) for v in r['bed_bounds_mm'][1][:2]]) for r in records]}, indent=1))


if __name__ == '__main__':
    main()
