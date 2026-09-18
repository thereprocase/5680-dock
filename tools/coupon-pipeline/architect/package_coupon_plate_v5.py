"""Package a verified native Orca candidate as a standalone folder and ZIP (V5: rail +3.5 mm)."""
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
    parser.add_argument('--slice-dir',type=Path,required=True)
    parser.add_argument('--geometry-dir',type=Path,required=True)
    parser.add_argument('--readme',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--project',default='coupons-sliced.3mf')
    parser.add_argument('--title',default='V5 RAIL +3.5MM A B C FIT COUPONS - ONE EACH')
    parser.add_argument('--d8',type=Path,default=Path('F:/Code/5680-dock-fit-20260917/desk-dock/D8'))
    args = parser.parse_args()
    assert not args.out.exists(), 'Preserve all existing release evidence'
    assert not args.out.with_suffix('.zip').exists()
    verify = json.loads((args.slice_dir/'toolpath-verification.json').read_text())
    assert verify['passed'] is True
    gcode = args.slice_dir/'plate_1.gcode'
    assert sha(gcode) == verify['gcode_sha256']
    identifier = json.loads((args.slice_dir/'id-hole-verification.json').read_text())
    assert identifier.get('passed') is True, 'ID-opening survival must pass before packaging'
    assert identifier.get('gcode_sha256') == sha(gcode), 'ID audit must name this exact G-code'
    preparation = json.loads((args.slice_dir/'plate-preparation.json').read_text())
    for record in preparation['objects']:
        assert sha(Path(record['source'])) == record['sha256'], 'Geometry changed after plate preparation'
    generated = args.geometry_dir/'generated'
    geometry_manifest = json.loads((generated/'manifest.json').read_text())
    for name,expected in geometry_manifest['output_sha256'].items():
        assert sha(generated/name)==expected, 'Generated geometry changed after review: '+name
    if geometry_manifest.get('builder_sha256'):
        assert any(sha(p)==geometry_manifest['builder_sha256'] for p in args.geometry_dir.glob('build*.py')), 'Builder changed after geometry freeze'
    assert identifier['objects'] and all(o['all_layer_count']>=80 and o['all_layers_pass'] for o in identifier['objects'])
    out = args.out
    out.mkdir(parents=True)
    shutil.copy2(args.readme,out/'README.md')
    shutil.copy2(gcode,out/'A-B-C-handheld-coupons-P1S-0.4-PETG.gcode')
    title = args.title
    with zipfile.ZipFile(args.slice_dir/args.project) as original, zipfile.ZipFile(out/'OPEN-ME.3mf','w',zipfile.ZIP_DEFLATED) as frozen:
        for entry in original.infolist():
            payload = original.read(entry.filename)
            if entry.filename == 'Metadata/model_settings.config':
                xml = ET.fromstring(payload)
                plate = xml.find('plate')
                assert plate is not None
                for key,value in [('plater_name',title),('locked','true')]:
                    element = plate.find(f"metadata[@key='{key}']")
                    if element is None: element = ET.SubElement(plate,'metadata',{'key':key})
                    element.set('value',value)
                payload = ET.tostring(xml,encoding='utf-8',xml_declaration=True)
            frozen.writestr(entry,payload)
    with zipfile.ZipFile(out/'OPEN-ME.3mf') as archive:
        assert archive.testzip() is None
        assert archive.read('Metadata/plate_1.gcode') == gcode.read_bytes()
        assert archive.read('Metadata/plate_1.gcode.md5').decode().strip().lower() == hashlib.md5(gcode.read_bytes()).hexdigest()
        xml = ET.fromstring(archive.read('Metadata/model_settings.config'))
        assert xml.find("plate/metadata[@key='plater_name']").get('value') == title
        assert xml.find("plate/metadata[@key='locked']").get('value') == 'true'
    folders = {'frozen-profiles':('machine.json','process.json','filament.json','profile-selection.json'),
               'verification':('plate-preparation.json','geometry-review-receipt.md','toolpath-verification.json','slice.log','slice-execution.json','id-hole-verification.json'),
               'previews':('actual-toolpaths.png',)}
    for folder,names in folders.items():
        target = out/folder
        target.mkdir()
        for name in names:
            shutil.copy2(args.slice_dir/name,target/name)
    generated = args.geometry_dir/'generated'
    for folder,suffixes in [('fallback-CAD',{'.step','.stl'}),('previews',{'.png'})]:
        target = out/folder
        target.mkdir(exist_ok=True)
        for path in generated.iterdir():
            if path.suffix.lower() in suffixes:
                shutil.copy2(path,target/path.name)
    source = out/'source'
    source.mkdir()
    geometry_source = source/args.geometry_dir.name
    geometry_source.mkdir()
    for path in args.geometry_dir.iterdir():
        if path.is_file() and path.suffix in ('.py','.md','.json'):
            shutil.copy2(path,geometry_source/path.name)
    shutil.copy2(generated/'manifest.json',geometry_source/'geometry-manifest.json')
    geometry_manifest = json.loads((generated/'manifest.json').read_text())
    if 'v2_builder' in geometry_manifest['input_sha256']:
        dependency=args.geometry_dir.parent/'profile-v2/build_native_datum_coupon_v2.py'
        assert sha(dependency)==geometry_manifest['input_sha256']['v2_builder']
        (source/'profile-v2').mkdir()
        shutil.copy2(dependency,source/'profile-v2'/dependency.name)
    if 'v4_builder' in geometry_manifest['input_sha256']:
        dependency=args.geometry_dir.parent/'profile-v4/build_full_rail_coupon_v4.py'
        assert sha(dependency)==geometry_manifest['input_sha256']['v4_builder']
        (source/'profile-v4').mkdir()
        shutil.copy2(dependency,source/'profile-v4'/dependency.name)
        v4_step=args.geometry_dir.parent/'profile-v4/generated/B_R2_full_native_rail.step'
        assert sha(v4_step)==geometry_manifest['input_sha256']['v4_b_step']
        (source/'profile-v4/generated').mkdir()
        shutil.copy2(v4_step,source/'profile-v4/generated'/v4_step.name)
    required_sources = {
        'parameters':'parameters.json',
        'r1_builder':'quick-fit/build_quick_fit.py',
        'r1_contact_profiles':'contact-profiles.json',
        'r1_step':'quick-fit/D8-quick-fit-bracket.step',
        'r2_builder':'quick-fit/R2/build_quick_fit.py',
        'r2_step':'quick-fit/R2/D8-R2-quick-fit-bracket.step',
        'r2_fit_parameters':'quick-fit/R2/fit-parameters.json',
        'r2_seat_profile':'quick-fit/R2/seat-profile.json',
    }
    for key,relative in required_sources.items():
        original = args.d8/relative
        if key in geometry_manifest['input_sha256']:
            assert sha(original) == geometry_manifest['input_sha256'][key], 'Source changed after geometry build'
        target = source/'D8'/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(original,target)
    shutil.copy2(args.d8/'raster.py',source/'D8/raster.py')
    shutil.copy2(args.d8.parents[1]/'LICENSE',source/'LICENSE')
    for name in ('prepare_coupon_plate.py','verify_coupon_plate.py','package_coupon_plate.py','run_coupon_orca.py'):
        shutil.copy2(Path(__file__).parent/name,source/name)
    for name in ('id-holes-toolpaths.png','id-hole-verification.md','independent-geometry-review.md','independent-geometry-verification.json','verification-coordinate-correction.md'):
        if (args.slice_dir/name).is_file():
            shutil.copy2(args.slice_dir/name,out/('previews' if name.endswith('.png') else 'verification')/name)
    manifest = {'plate_name':title, 'quantity':'one each A/B/C', 'qualification':verify['qualification'],
                'source_geometry_sha256':sha(generated/'manifest.json'), 'files':{}}
    for path in sorted(out.rglob('*')):
        if path.is_file():
            manifest['files'][path.relative_to(out).as_posix()] = {'bytes':path.stat().st_size,'sha256':sha(path)}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive_path = out.with_suffix('.zip')
    with zipfile.ZipFile(archive_path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in sorted(out.rglob('*')):
            if path.is_file(): archive.write(path,Path(out.name)/path.relative_to(out))
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        assert archive.read(out.name+'/manifest.json') == (out/'manifest.json').read_bytes()
        for name,record in manifest['files'].items():
            assert hashlib.sha256(archive.read(out.name+'/'+name)).hexdigest() == record['sha256']
    print(json.dumps({'directory':str(out),'archive':str(archive_path),'verified_files':len(manifest['files']),
                      'archive_sha256':sha(archive_path)},indent=2))


if __name__ == '__main__':
    main()
