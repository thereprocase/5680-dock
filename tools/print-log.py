#!/usr/bin/env python3
"""Print log for the 5680 dock: one entry per job sent to the P1S, with the exact geometry that was printed.

  tools/print-log.py add --slice-dir DIR --job JOBID --slot N --commit SHA --label "..." [--status running|printed|failed|not-started]
                         [--file NAME] [--when "2026-09-18 16:58"] [--notes "..."] [--lessons "..."]
  tools/print-log.py update --id P-0006 [--status printed] [--notes "..."] [--lessons "..."] [--follow-up "..."]
  tools/print-log.py render

DIR is an Orca slice folder from the pipeline (toolpath-verification.json, plate-preparation.json, profile-selection.json,
process.json). The entry records every object's name and source-STL SHA-256, so a printed part can always be tied back to
the builder revision that produced it. Data lives in docs/prints/print-log.json; docs/prints/README.md is rendered from it.
"""
import argparse, json, re, datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / 'docs/prints/print-log.json'
MD = ROOT / 'docs/prints/README.md'

def load():
    return json.loads(JSON.read_text(encoding='utf-8')) if JSON.exists() else {'printer': 'Bambu P1S 01P00A3C1300643 via bambu-bridge on pve', 'entries': []}

def save(log):
    JSON.write_text(json.dumps(log, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    render(log)

def from_slice_dir(d):
    d = Path(d); info = {'slice_dir': str(d)}
    tv = d / 'toolpath-verification.json'
    if tv.exists():
        j = json.loads(tv.read_text()); text = '\n'.join(j.get('summary', []))
        g = lambda pat, cast=str: (cast(re.search(pat, text).group(1)) if re.search(pat, text) else None)
        info['estimate'] = {'time': g(r'model printing time: ([^;\n]+)'), 'filament_g': g(r'filament used \[g\] = ([\d.]+)', float),
                            'layers': g(r'total layer number: (\d+)', int), 'max_z_mm': g(r'max_z_height: ([\d.]+)', float)}
        info['toolpath_audit_passed'] = j.get('passed'); info['gcode_sha256'] = j.get('gcode_sha256')
        info['supports_by_object'] = {k: v.get('support_segments') for k, v in j.get('objects', {}).items()}
    pp = d / 'plate-preparation.json'
    if pp.exists():
        j = json.loads(pp.read_text()); info['parts'] = [{'name': o['name'], 'source_sha256': o.get('sha256') or o.get('source_sha256')} for o in j.get('objects', [])]
    ps = d / 'profile-selection.json'
    if ps.exists():
        j = json.loads(ps.read_text()); info['profiles'] = {k: j.get(k) for k in ('machine', 'process', 'filament', 'material') if k in j}
    pr = d / 'process.json'
    if pr.exists():
        j = json.loads(pr.read_text()); info['process'] = {k: j.get(k) for k in ('layer_height', 'wall_loops', 'top_shell_layers', 'sparse_infill_density', 'sparse_infill_pattern', 'support_type', 'support_style', 'support_on_build_plate_only', 'support_object_xy_distance', 'brim_width') if k in j}
    fl = d / 'filament.json'
    if fl.exists():
        j = json.loads(fl.read_text()); info.setdefault('profiles', {})['filament_preset'] = j.get('name'); info['filament_settings'] = {k: (j.get(k)[0] if isinstance(j.get(k), list) else j.get(k)) for k in ('filament_flow_ratio', 'filament_shrink', 'pressure_advance', 'nozzle_temperature', 'hot_plate_temp') if k in j}
    return info

def next_id(log):
    n = max([int(e['id'].split('-')[1]) for e in log['entries']] + [0]) + 1
    return f'P-{n:04d}'

def cmd_add(a):
    log = load(); e = {'id': next_id(log), 'when': a.when or datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), 'label': a.label, 'status': a.status,
                       'job_id': a.job, 'file_name': a.file, 'ams_physical_slot': a.slot, 'repo_commit': a.commit, 'notes': a.notes or '', 'lessons': a.lessons or '', 'follow_ups': []}
    if a.slice_dir: e.update(from_slice_dir(a.slice_dir))
    log['entries'].append(e); save(log); print(e['id'])

def cmd_update(a):
    log = load(); e = next(x for x in log['entries'] if x['id'] == a.id)
    if a.status: e['status'] = a.status
    if a.notes: e['notes'] = (e.get('notes', '') + '\n' + a.notes).strip()
    if a.lessons: e['lessons'] = (e.get('lessons', '') + '\n' + a.lessons).strip()
    if a.follow_up: e.setdefault('follow_ups', []).append(a.follow_up)
    save(log); print('updated', a.id)

def render(log):
    lines = ['# Print log', '', 'Every job sent to the P1S, newest first, with the exact geometry (source-STL SHA-256 per part), profiles, estimate,',
             'outcome and what we learned. Source of truth is `print-log.json`; append with `tools/print-log.py add`, close out with', '`tools/print-log.py update`. Printer: ' + log['printer'] + '.', '',
             '| Id | When | What | Status | Job | Slot | Estimate | Commit |', '| --- | --- | --- | --- | --- | --- | ---: | --- |']
    for e in reversed(log['entries']):
        est = e.get('estimate') or {}; est_s = f"{est.get('time', '')} / {est.get('filament_g', '')} g" if est else ''
        lines.append(f"| {e['id']} | {e['when']} | {e['label']} | {e['status']} | {(e.get('job_id') or '')[:8]} | {e.get('ams_physical_slot', '')} | {est_s} | {(e.get('repo_commit') or '')[:7]} |")
    lines.append('')
    for e in reversed(log['entries']):
        lines += [f"## {e['id']} - {e['label']}", '', f"- When: {e['when']}; status: **{e['status']}**; job `{e.get('job_id') or 'n/a'}`; file `{e.get('file_name') or 'n/a'}`; AMS physical slot {e.get('ams_physical_slot', '?')}; repo commit `{e.get('repo_commit') or '?'}`."]
        p = e.get('profiles') or {}
        if p: lines.append(f"- Profiles: {p.get('filament_preset') or p.get('filament', '')}; process {p.get('process', '')}; {p.get('material', '')}".rstrip('; '))
        pr = e.get('process') or {}
        if pr: lines.append('- Process: ' + ', '.join(f'{k} {v}' for k, v in pr.items()))
        fs = e.get('filament_settings') or {}
        if fs: lines.append('- Filament: ' + ', '.join(f'{k} {v}' for k, v in fs.items()))
        est = e.get('estimate') or {}
        if est: lines.append(f"- Estimate: {est.get('time')}; {est.get('filament_g')} g; {est.get('layers')} layers; {est.get('max_z_mm')} mm tall; toolpath audit {'passed' if e.get('toolpath_audit_passed') else 'n/a'}.")
        if e.get('parts'): lines.append('- Parts: ' + ', '.join(f"`{x['name']}` ({(x.get('source_sha256') or '')[:12]})" for x in e['parts']))
        if e.get('slice_dir'): lines.append(f"- Slice folder: `{e['slice_dir']}`")
        if e.get('notes'): lines.append('- Notes: ' + e['notes'].replace('\n', ' '))
        if e.get('lessons'): lines.append('- Lessons: ' + e['lessons'].replace('\n', ' '))
        for f in e.get('follow_ups', []): lines.append('- Follow-up: ' + f)
        lines.append('')
    MD.write_text('\n'.join(lines), encoding='utf-8')

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter); sub = ap.add_subparsers(dest='cmd', required=True)
a = sub.add_parser('add'); a.add_argument('--slice-dir'); a.add_argument('--job'); a.add_argument('--slot', type=int); a.add_argument('--commit'); a.add_argument('--label', required=True)
a.add_argument('--status', default='running'); a.add_argument('--file'); a.add_argument('--when'); a.add_argument('--notes'); a.add_argument('--lessons'); a.set_defaults(fn=cmd_add)
u = sub.add_parser('update'); u.add_argument('--id', required=True); u.add_argument('--status'); u.add_argument('--notes'); u.add_argument('--lessons'); u.add_argument('--follow-up'); u.set_defaults(fn=cmd_update)
r = sub.add_parser('render'); r.set_defaults(fn=lambda a: render(load()))
def cmd_refresh(a):
    log = load()
    for e in log['entries']:
        if e.get('slice_dir') and Path(e['slice_dir']).exists(): e.update(from_slice_dir(e['slice_dir']))
    save(log); print('refreshed', len(log['entries']))
f = sub.add_parser('refresh'); f.set_defaults(fn=cmd_refresh)
args = ap.parse_args(); args.fn(args)
