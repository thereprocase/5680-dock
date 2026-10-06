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
    render_html(log)

HTML = ROOT / 'docs/prints/index.html'
def esc(t): return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def render_html(log):
    css = ('body{font:15px/1.5 system-ui,sans-serif;margin:0;padding:24px 16px;background:#f6f5f2;color:#1d1d1b;max-width:1100px;margin-inline:auto}'
           'h1{font-size:26px;margin:0 0 6px}p.lead{margin:0 0 20px;color:#5a5852}table{border-collapse:collapse;width:100%;font-size:14px;margin-bottom:28px}'
           'th,td{text-align:left;padding:6px 8px;border-bottom:1px solid #d9d6cf;vertical-align:top}th{background:#e9e6df}td.num{text-align:right;white-space:nowrap}'
           'article{background:#fff;border:1px solid #d9d6cf;border-radius:6px;padding:14px 16px;margin-bottom:14px}article h2{font-size:17px;margin:0 0 8px}'
           'code{font:13px ui-monospace,monospace;background:#eeece6;padding:1px 4px;border-radius:3px}.st{display:inline-block;padding:0 8px;border-radius:10px;font-size:12px;font-weight:600}'
           '.st-printed{background:#dcefdc;color:#1e5a1e}.st-running{background:#dde8f7;color:#1c4a8a}.st-failed,.st-not-started{background:#f7dede;color:#8a1c1c}ul{margin:6px 0 0 18px;padding:0}'
           '@media(max-width:600px){table{font-size:12px}th,td{padding:4px}}')
    h = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>5680 dock print log</title><style>' + css + '</style></head><body>',
         '<h1>5680 dock print log</h1><p class="lead">Every job sent to the P1S, newest first, with the exact geometry printed (source-STL SHA-256 per part), profiles, estimate, outcome and lessons. Source of truth: <code>print-log.json</code>.</p>',
         '<div style="overflow-x:auto"><table><thead><tr><th>Id</th><th>When</th><th>What</th><th>Status</th><th>Job</th><th>Slot</th><th>Estimate</th><th>Commit</th></tr></thead><tbody>']
    for e in reversed(log['entries']):
        est = e.get('estimate') or {}; est_s = f"{est.get('time') or ''} / {est.get('filament_g') or ''} g" if est else ''
        h.append(f"<tr><td><a href=\"#{e['id']}\">{e['id']}</a></td><td>{esc(e['when'])}</td><td>{esc(e['label'])}</td><td><span class=\"st st-{e['status']}\">{esc(e['status'])}</span></td><td><code>{esc((e.get('job_id') or '')[:8])}</code></td><td>{esc(e.get('ams_physical_slot') or '')}</td><td class=\"num\">{esc(est_s)}</td><td><code>{esc((e.get('repo_commit') or '')[:7])}</code></td></tr>")
    h.append('</tbody></table></div>')
    for e in reversed(log['entries']):
        h.append(f"<article id=\"{e['id']}\"><h2>{e['id']} &middot; {esc(e['label'])}</h2><ul>")
        h.append(f"<li>When {esc(e['when'])}; status <span class=\"st st-{e['status']}\">{esc(e['status'])}</span>; job <code>{esc(e.get('job_id') or 'n/a')}</code>; file <code>{esc(e.get('file_name') or 'n/a')}</code>; AMS physical slot {esc(e.get('ams_physical_slot') or '?')}; repo commit <code>{esc(e.get('repo_commit') or '?')}</code>.</li>")
        p = e.get('profiles') or {}
        if p: h.append('<li>Profiles: ' + esc(p.get('filament_preset') or p.get('filament', '')) + '; process ' + esc(p.get('process', '')) + ('; ' + esc(p['material']) if p.get('material') else '') + '</li>')
        pr = e.get('process') or {}
        if pr: h.append('<li>Process: ' + esc(', '.join(f'{k} {v}' for k, v in pr.items())) + '</li>')
        fs = e.get('filament_settings') or {}
        if fs: h.append('<li>Filament: ' + esc(', '.join(f'{k} {v}' for k, v in fs.items())) + '</li>')
        est = e.get('estimate') or {}
        if est: h.append(f"<li>Estimate: {esc(est.get('time'))}; {esc(est.get('filament_g'))} g; {esc(est.get('layers'))} layers; {esc(est.get('max_z_mm'))} mm tall; toolpath audit {'passed' if e.get('toolpath_audit_passed') else 'n/a'}.</li>")
        if e.get('actual_duration_s'): h.append(f"<li>Actual duration: {e['actual_duration_s'] // 3600} h {(e['actual_duration_s'] % 3600) // 60} min.</li>")
        if e.get('parts'): h.append('<li>Parts: ' + ', '.join(f"<code>{esc(x['name'])}</code> ({esc((x.get('source_sha256') or '')[:12])})" for x in e['parts']) + '</li>')
        if e.get('notes'): h.append('<li>Notes: ' + esc(e['notes']) + '</li>')
        if e.get('lessons'): h.append('<li>Lessons: ' + esc(e['lessons']) + '</li>')
        for f in e.get('follow_ups', []): h.append('<li>Follow-up: ' + esc(f) + '</li>')
        h.append('</ul></article>')
    h.append('</body></html>')
    HTML.write_text('\n'.join(h), encoding='utf-8')

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
