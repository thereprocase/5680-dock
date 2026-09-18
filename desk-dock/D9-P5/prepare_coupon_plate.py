"""Freeze already-oriented reviewed STL coupons into an explicitly placed 3MF.

This prepares the plate; it neither searches orientations nor runs a slicer.
Only standard library modules are required. No existing output is overwritten.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import struct
import xml.etree.ElementTree as ET
import zipfile

NS = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('', NS)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mesh(path):
    data = path.read_bytes()
    vertices, faces, lookup = [], [], {}
    def vertex(point):
        if point not in lookup:
            lookup[point] = len(vertices)
            vertices.append(point)
        return lookup[point]
    n = struct.unpack_from('<I', data, 80)[0] if len(data) >= 84 else 0
    if len(data) == 84 + n * 50:
        for i in range(n):
            values = struct.unpack_from('<12fH', data, 84 + i * 50)
            faces.append(tuple(vertex(tuple(values[j:j+3])) for j in (3, 6, 9)))
    else:
        triangle = []
        for line in data.decode('ascii').splitlines():
            words = line.split()
            if words and words[0] == 'vertex':
                triangle.append(vertex(tuple(map(float, words[1:]))))
                if len(triangle) == 3:
                    faces.append(tuple(triangle))
                    triangle = []
        assert not triangle
    assert vertices and faces
    lo = [min(v[i] for v in vertices) for i in range(3)]
    hi = [max(v[i] for v in vertices) for i in range(3)]
    return vertices, faces, lo, hi


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stl', action='append', type=Path, required=True)
    parser.add_argument('--profiles', type=Path, required=True)
    parser.add_argument('--review-receipt', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert args.review_receipt.is_file(), 'Reviewed geometry receipt required'
    assert 1 <= len(args.stl) <= 3, 'This plate holds one to three coupons'
    assert not args.out.exists(), 'Use a new output directory to preserve evidence'
    inputs = [(p.resolve(), *mesh(p)) for p in args.stl]
    gap = 16.0  # Accommodates separate 5-mm brims, no touching objects.
    total_width = sum(hi[0]-lo[0] for _, _, _, lo, hi in inputs) + gap * 2
    cell_width = max(hi[0]-lo[0] for _, _, _, lo, hi in inputs)
    cell_depth = max(hi[1]-lo[1] for _, _, _, lo, hi in inputs)
    columns = min(len(inputs), 3 if total_width < 220 else 2)
    rows = (len(inputs)+columns-1)//columns
    layout_width = columns*cell_width+(columns-1)*gap
    layout_depth = rows*cell_depth+(rows-1)*gap
    assert layout_width < 230 and layout_depth < 210, 'Reviewed orientation does not fit this plate layout'
    layout_x,layout_y = (256-layout_width)/2,(256-layout_depth)/2
    root = ET.Element(f'{{{NS}}}model', {'unit':'millimeter', 'xml:lang':'en-US'})
    resources = ET.SubElement(root, f'{{{NS}}}resources')
    build = ET.SubElement(root, f'{{{NS}}}build')
    records = []
    for oid, (path, vertices, faces, lo, hi) in enumerate(inputs, 1):
        obj = ET.SubElement(resources, f'{{{NS}}}object', {'id':str(oid), 'type':'model', 'name':path.stem})
        objmesh = ET.SubElement(obj, f'{{{NS}}}mesh')
        verts = ET.SubElement(objmesh, f'{{{NS}}}vertices')
        tris = ET.SubElement(objmesh, f'{{{NS}}}triangles')
        for v in vertices:
            ET.SubElement(verts, f'{{{NS}}}vertex', dict(zip(('x','y','z'), map(lambda n:format(n,'.9g'), v))))
        for face in faces:
            ET.SubElement(tris, f'{{{NS}}}triangle', dict(zip(('v1','v2','v3'), map(str, face))))
        col,row = (oid-1)%columns,(oid-1)//columns
        shift = [layout_x+col*(cell_width+gap)-lo[0],layout_y+row*(cell_depth+gap)-lo[1],-lo[2]]
        transform = '1 0 0 0 1 0 0 0 1 ' + ' '.join(format(n,'.9g') for n in shift)
        ET.SubElement(build, f'{{{NS}}}item', {'objectid':str(oid), 'transform':transform})
        records.append({'name':path.stem, 'source':str(path), 'sha256':digest(path),
                        'bounds_before_mm':[lo,hi], 'translation_mm':shift,
                        'bed_bounds_mm':[[lo[i]+shift[i] for i in range(3)], [hi[i]+shift[i] for i in range(3)]]})
    args.out.mkdir(parents=True)
    path = args.out/'reviewed-coupons-input.3mf'
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        archive.writestr('_rels/.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        archive.writestr('3D/3dmodel.model', ET.tostring(root, encoding='utf-8', xml_declaration=True))
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        assert len(ET.fromstring(archive.read('3D/3dmodel.model')).findall(f'{{{NS}}}build/{{{NS}}}item')) == len(inputs)
    profile_receipt = {}
    for name in ('machine.json','process.json','filament.json','profile-selection.json'):
        source = args.profiles/name
        shutil.copy2(source, args.out/name)
        profile_receipt[name] = digest(source)
    shutil.copy2(args.review_receipt, args.out/'geometry-review-receipt.md')
    receipt = {'stage':'prepared, not sliced', 'orientation':'source STL rotation retained; translation only',
               'objects':records, 'input_3mf_sha256':digest(path), 'profile_sha256':profile_receipt,
               'geometry_review_sha256':digest(args.review_receipt)}
    (args.out/'plate-preparation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    main()
