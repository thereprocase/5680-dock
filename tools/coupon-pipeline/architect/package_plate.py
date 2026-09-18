"""Package a verified mixed plate (from prepare_mixed_plate + verify_mixed_plate).

Writes <out>/ with OPEN-ME.3mf (locked, titled), the standalone G-code, the
frozen profiles, verification receipts, previews, fallback CAD and sources,
plus manifest.json with every file's SHA-256, then <out>.zip.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
import zipfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slice-dir', type=Path, required=True)
    parser.add_argument('--readme', type=Path, required=True)
    parser.add_argument('--title', required=True)
    parser.add_argument('--gcode-name', default='plate-P1S-0.4-PETG.gcode')
    parser.add_argument('--cad', action='append', type=Path, default=[], help='files or folders copied into fallback-CAD/')
    parser.add_argument('--source', action='append', type=Path, default=[], help='files or folders copied into source/')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out
    assert not out.exists() and not out.with_suffix('.zip').exists(), 'Preserve existing release evidence'
    slice_dir = args.slice_dir
    verify = json.loads((slice_dir / 'toolpath-verification.json').read_text())
    assert verify['passed'] is True
    gcode = slice_dir / 'plate_1.gcode'
    assert sha(gcode) == verify['gcode_sha256']
    prep = json.loads((slice_dir / 'plate-preparation.json').read_text())
    for record in prep['objects']:
        assert sha(Path(record['source'])) == record['sha256'], 'Geometry changed after plate preparation: ' + record['name']
    out.mkdir(parents=True)
    shutil.copy2(args.readme, out / 'README.md')
    shutil.copy2(gcode, out / args.gcode_name)
    with zipfile.ZipFile(slice_dir / 'coupons-sliced.3mf') as original, zipfile.ZipFile(out / 'OPEN-ME.3mf', 'w', zipfile.ZIP_DEFLATED) as frozen:
        for entry in original.infolist():
            payload = original.read(entry.filename)
            if entry.filename == 'Metadata/model_settings.config':
                xml = ET.fromstring(payload)
                plate = xml.find('plate')
                for key, value in [('plater_name', args.title), ('locked', 'true')]:
                    element = plate.find(f"metadata[@key='{key}']")
                    if element is None:
                        element = ET.SubElement(plate, 'metadata', {'key': key})
                    element.set('value', value)
                payload = ET.tostring(xml, encoding='utf-8', xml_declaration=True)
            frozen.writestr(entry, payload)
    with zipfile.ZipFile(out / 'OPEN-ME.3mf') as archive:
        assert archive.testzip() is None
        assert archive.read('Metadata/plate_1.gcode') == gcode.read_bytes()
        xml = ET.fromstring(archive.read('Metadata/model_settings.config'))
        assert xml.find("plate/metadata[@key='plater_name']").get('value') == args.title
    folders = {'frozen-profiles': ('machine.json', 'process.json', 'filament.json', 'profile-selection.json'),
               'verification': ('plate-preparation.json', 'geometry-review-receipt.md', 'toolpath-verification.json', 'slice.log', 'slice-execution.json'),
               'previews': ('plate-layout.png', 'actual-toolpaths.png')}
    for folder, names in folders.items():
        (out / folder).mkdir()
        for name in names:
            shutil.copy2(slice_dir / name, out / folder / name)
    for folder, sources in (('fallback-CAD', args.cad), ('source', args.source)):
        (out / folder).mkdir(exist_ok=True)
        for src in sources:
            if src.is_dir():
                for path in src.iterdir():
                    if path.is_file() and not path.name.startswith('__'):
                        shutil.copy2(path, out / folder / path.name)
            else:
                shutil.copy2(src, out / folder / src.name)
    manifest = {'plate_name': args.title, 'summary': verify['summary'], 'strict_objects': verify['strict_objects'],
                'qualification': verify['qualification'], 'files': {}}
    for path in sorted(out.rglob('*')):
        if path.is_file():
            manifest['files'][path.relative_to(out).as_posix()] = {'bytes': path.stat().st_size, 'sha256': sha(path)}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    archive_path = out.with_suffix('.zip')
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(out.rglob('*')):
            if path.is_file():
                archive.write(path, Path(out.name) / path.relative_to(out))
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        for name, record in manifest['files'].items():
            assert hashlib.sha256(archive.read(out.name + '/' + name)).hexdigest() == record['sha256']
    print(json.dumps({'directory': str(out), 'archive': str(archive_path), 'files': len(manifest['files']), 'archive_sha256': sha(archive_path)}, indent=2))


if __name__ == '__main__':
    main()
