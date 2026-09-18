"""Audit a sliced mixed plate: per-object support/bridge roads, placement, bed.

Strict objects (flagged in plate-preparation.json) must have zero support and
zero external bridge roads. Other objects may use hidden supports and bridges;
their counts are reported. Placement, spacing, bed bounds, excluded zone,
build height and embedded-G-code identity are checked as for the coupon plates.
"""
from pathlib import Path
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
import zipfile
from PIL import Image, ImageDraw, ImageFont


FILAMENT = {}


def roads(text, default_width):
    pos = {k: 0.0 for k in 'XYZE'}
    relative_e, absolute_xyz, role, width, obj = True, True, 'Custom', default_width, None
    labels, pending = {}, None  # Orca/Bambu: '; printing object NAME' names the label id that follows
    out = []
    for line in text.splitlines():
        m = re.match(r'; printing object (.+) id:', line)
        if m:
            pending = m.group(1); continue
        m = re.match(r'; start printing object, unique label id: (\d+)', line)
        if m:
            if pending is not None:
                labels[m.group(1)] = pending; pending = None
            obj = labels.get(m.group(1), obj); continue
        if line.startswith('; stop printing object, unique label id'):
            obj = None; continue
        if line.startswith('; FEATURE: '):
            role = line[11:]; continue
        m = re.match(r'; LINE_WIDTH: ([0-9.]+)', line)
        if m:
            width = float(m.group(1)); continue
        code = line.split(';', 1)[0].strip()
        if not code:
            continue
        op = code.split()[0]
        if op == 'M83': relative_e = True
        if op == 'M82': relative_e = False
        if op == 'G90': absolute_xyz = True
        if op == 'G91': absolute_xyz = False
        values = {k: float(v) for k, v in re.findall(r'([XYZEIJ])([-+]?(?:\d*\.)?\d+)', code)}
        if op == 'G92':
            pos.update({k: v for k, v in values.items() if k in pos}); continue
        if op not in ('G0', 'G1', 'G2', 'G3'):
            continue
        before = pos.copy()
        for k in 'XYZ':
            if k in values: pos[k] = values[k] if absolute_xyz else pos[k] + values[k]
        extrusion = values.get('E', 0.0) if relative_e else values.get('E', pos['E']) - pos['E']
        if 'E' in values: pos['E'] = pos['E'] + values['E'] if relative_e else values['E']
        if extrusion <= 0 or role == 'Custom':
            continue
        p0, p1 = (before['X'], before['Y']), (pos['X'], pos['Y'])
        if p0 == p1 and op not in ('G2', 'G3'):
            continue
        out.append((p0, p1, pos['Z'], role, obj, width))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dir', type=Path, required=True)
    parser.add_argument('--project', default='coupons-sliced.3mf')
    args = parser.parse_args()
    folder = args.dir
    gcode = folder / 'plate_1.gcode'
    data = gcode.read_bytes(); text = data.decode('utf-8')
    prep = json.loads((folder / 'plate-preparation.json').read_text())
    process = json.loads((folder / 'process.json').read_text())
    machine = json.loads((folder / 'machine.json').read_text())
    global FILAMENT; FILAMENT = json.loads((folder / 'filament.json').read_text())
    with zipfile.ZipFile(folder / args.project) as archive:
        assert archive.testzip() is None
        assert archive.read('Metadata/plate_1.gcode') == data
        assert archive.read('Metadata/plate_1.gcode.md5').decode().strip().lower() == hashlib.md5(data).hexdigest()
        settings = ET.fromstring(archive.read('Metadata/model_settings.config'))
        assert len(settings.findall('object')) == len(prep['objects'])
        assert len(settings.findall('plate')) == 1
        placement = verify_placement(archive, settings, prep)
    offset = tuple(map(float, machine['extruder_offset'][0].split('x')))
    declared = re.search(r'^; extruder_offset = (.+)$', text, re.M).group(1).strip()
    assert declared == machine['extruder_offset'][0]
    segs = [((a[0] + offset[0], a[1] + offset[1]), (b[0] + offset[0], b[1] + offset[1]), z, role, obj, w) for a, b, z, role, obj, w in roads(text, float(process['line_width']))]
    assert segs
    per_object = defaultdict(Counter)
    for _, _, _, role, obj, _ in segs:
        per_object[obj or '(unassigned)'][role] += 1
    strict = {o['name'] for o in prep['objects'] if o.get('strict')}
    report_objects = {}
    for name in [o['name'] for o in prep['objects']]:
        counts = per_object.get(name, Counter())
        supports = sum(v for k, v in counts.items() if 'support' in k.lower())
        external = sum(v for k, v in counts.items() if 'bridge' in k.lower() and 'internal' not in k.lower())
        internal = sum(v for k, v in counts.items() if 'internal bridge' in k.lower())
        report_objects[name] = {'strict': name in strict, 'support_segments': supports, 'external_bridge_segments': external, 'internal_bridge_segments': internal, 'roles': dict(counts)}
        if name in strict:
            assert supports == 0, f'{name}: support paths emitted'
            assert external == 0, f'{name}: external bridge emitted'
    assert not [k for k in per_object if k == '(unassigned)' and any('support' in r.lower() for r in per_object[k])], 'unassigned support roads'
    points = [p for a, b, _, _, _, _ in segs for p in (a, b)]
    bounds = [min(p[0] for p in points), min(p[1] for p in points), max(p[0] for p in points), max(p[1] for p in points)]
    assert all(.25 < p[0] < 255.75 and .25 < p[1] < 255.75 for p in points)
    assert all(not (p[0] < 18.5 and p[1] < 28.5) for p in points), 'Front-left excluded zone'
    height = max(s[2] for s in segs if s[3].lower() != 'brim')
    intended = max(o['bed_bounds_mm'][1][2] for o in prep['objects'])
    assert abs(height - intended) <= float(process['layer_height']) + .01, (height, intended)
    summary = [s for s in text.splitlines() if s.startswith(('; generated by', '; model printing time:', '; filament used [g]', '; total layer number:', '; max_z_height:'))]
    report = {'passed': True, 'source': 'actual Orca G-code roads in the declared nozzle/plate frame', 'raw_motion_to_plate_xy_offset_mm': offset,
              'summary': summary, 'objects': report_objects, 'strict_objects': sorted(strict),
              'model_and_brim_bounds_xy_mm': bounds, 'actual_print_height_mm': height, 'embedded_gcode_matches': True,
              'placement': placement, 'gcode_sha256': hashlib.sha256(data).hexdigest(),
              'qualification': 'Orca toolpath verification only; physical fit, stand loads and strength untested.'}
    (folder / 'toolpath-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    preview(segs, bounds, height, folder / 'actual-toolpaths.png', prep['objects'])
    print(json.dumps({'passed': True, 'summary': summary, 'objects': {k: {kk: v[kk] for kk in ('strict', 'support_segments', 'external_bridge_segments', 'internal_bridge_segments')} for k, v in report_objects.items()}}, indent=1))


def verify_placement(archive, settings, prep):
    ns = {'m': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
    production = '{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
    root = ET.fromstring(archive.read('3D/3dmodel.model'))
    expected = {o['name']: o for o in prep['objects']}
    metadata = {o.get('id'): o for o in settings.findall('object')}
    result = []
    for item in root.findall('m:build/m:item', ns):
        oid = item.get('objectid')
        name = metadata[oid].find("metadata[@key='name']").get('value')
        transform = list(map(float, item.get('transform').split()))
        assert all(abs(a - b) < 1e-8 for a, b in zip(transform[:9], [1, 0, 0, 0, 1, 0, 0, 0, 1])), 'Source orientation changed'
        comp = root.find(f"m:resources/m:object[@id='{oid}']/m:components/m:component", ns)
        assert comp is not None
        ct = list(map(float, comp.get('transform').split()))
        assert ct == [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
        meshroot = ET.fromstring(archive.read(comp.get(production + 'path').lstrip('/')))
        vertices = [tuple(float(v.get(axis)) + transform[9 + i] for i, axis in enumerate(('x', 'y', 'z'))) for v in meshroot.findall('.//m:vertices/m:vertex', ns)]
        lo = [min(v[i] for v in vertices) for i in range(3)]; hi = [max(v[i] for v in vertices) for i in range(3)]
        target = expected[name]['bed_bounds_mm']
        # Filament shrinkage compensation scales each object about its own centre in XY (Z when
        # filament_shrinkage_compensation_z is set); allow exactly that much, nothing more.
        scale = 1.0 / (float(str(FILAMENT.get('filament_shrink', ['100%'])[0]).rstrip('%')) / 100.0)
        zscale = 1.0 / (float(str(FILAMENT.get('filament_shrinkage_compensation_z', ['100%'])[0]).rstrip('%')) / 100.0)
        tol = [(target[1][i] - target[0][i]) * abs((scale if i < 2 else zscale) - 1.0) / 2 + 1e-3 for i in range(3)]
        assert all(abs(a - b) <= tol[i] for bb, t in zip((lo, hi), target) for i, (a, b) in enumerate(zip(bb, t))), f'Orca moved {name}: {lo} {hi} vs {target} tol {tol}'
        result.append({'name': name, 'bounds_mm': [lo, hi]})
    assert len(result) == len(prep['objects'])
    return result


def preview(segments, bounds, height, out, objects):
    image = Image.new('RGB', (1600, 560), '#f7f8fa'); draw = ImageDraw.Draw(image)
    font = lambda n: ImageFont.truetype('C:/Windows/Fonts/arial.ttf', n)
    draw.text((35, 25), 'Mixed plate | Actual Orca toolpaths', font=font(32), fill='#17364b')
    levels = sorted(set(round(s[2], 3) for s in segments))
    selected = [min(levels, key=lambda z: abs(z - t)) for t in (.2, height / 2, height)]
    colors = {'Outer wall': '#087dad', 'Inner wall': '#42a9a0', 'Gap infill': '#d38421', 'Internal Bridge': '#a43583', 'Bridge': '#d62828', 'Support': '#6a994e', 'Brim': '#a3acb2', 'Top surface': '#cc9366'}
    for column, z in enumerate(selected):
        x0, y0 = 30 + column * 525, 95
        draw.text((x0, y0), f'Print Z {z:g} mm', font=font(23), fill='#17364b')
        scale = min(490 / (bounds[2] - bounds[0] + 4), 335 / (bounds[3] - bounds[1] + 4))
        def project(p): return (x0 + (p[0] - bounds[0] + 2) * scale, y0 + 40 + (bounds[3] + 2 - p[1]) * scale)
        for a, b, zz, role, _, _ in segments:
            if abs(zz - z) < .01:
                draw.line((project(a), project(b)), fill=colors.get(role, '#b7c1c8'), width=2)
    draw.text((35, 520), 'Blue outer | Teal inner | Orange gap | Magenta internal bridge | Red bridge | Green support | Gray brim', font=font(20), fill='#314854')
    image.save(out)


if __name__ == '__main__':
    main()
