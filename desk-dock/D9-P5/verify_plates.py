"""Verify every sliced P3 plate with the per-object toolpath audit.

Adapts each plate's preparation.json to the plate-preparation.json shape that
verify_mixed_plate.py expects (bed bounds = bounds + translation). Shells,
guards and ties may carry the kit's intended hidden supports, so no object is
strict; support and bridge counts are reported per object. Writes
plates-verification.json with the per-plate summaries.
"""
from pathlib import Path
import json, subprocess, sys

HERE = Path(__file__).resolve().parent
VERIFY = HERE.parents[0] / 'quartet-team/architect/verify_mixed_plate.py'
results = {}
for folder in sorted((HERE / 'plates').iterdir()):
    prep = json.loads((folder / 'preparation.json').read_text())
    objects = []
    for o in prep['objects']:
        lo, hi = o['bounds']; t = o['translation']
        objects.append({'name': o['name'], 'source': str(HERE / 'generated' / (o['name'] + '.stl')), 'sha256': o['source_sha256'], 'strict': False,
                        'bed_bounds_mm': [[lo[i] + t[i] for i in range(3)], [hi[i] + t[i] for i in range(3)]], 'translation_mm': t})
    (folder / 'plate-preparation.json').write_text(json.dumps({'stage': 'prepared', 'objects': objects}, indent=2) + '\n')
    run = subprocess.run([sys.executable, str(VERIFY), '--dir', str(folder), '--project', 'sliced.3mf'], capture_output=True, text=True)
    if run.returncode != 0:
        print(folder.name, 'FAILED', run.stdout[-800:], run.stderr[-1500:]); results[folder.name] = {'passed': False}; continue
    report = json.loads((folder / 'toolpath-verification.json').read_text())
    summary = {line.split(':')[0].strip('; '): line.split(':', 1)[1].strip() for line in report['summary'] if ':' in line}
    results[folder.name] = {'passed': report['passed'], 'time': summary.get('model printing time'), 'filament_g': summary.get('filament used [g]', '').split('=')[-1].strip(),
                            'objects': {k: {'support': v['support_segments'], 'external_bridge': v['external_bridge_segments']} for k, v in report['objects'].items()}}
    print(folder.name, results[folder.name]['time'], results[folder.name]['filament_g'], 'g', flush=True)
(HERE / 'plates-verification.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps({k: (v.get('time'), v.get('filament_g')) for k, v in results.items()}))
