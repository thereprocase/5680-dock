"""Slice the prepared ASA plate folders once each with the native Orca CLI (mirrors prepare_and_slice.run)."""
from pathlib import Path
import json, os, subprocess, sys, time
HERE = Path(__file__).resolve().parent
for plate in sys.argv[1:]:
    folder = HERE/'asa'/plate
    (folder/'data').mkdir(exist_ok=True); (folder/'temp').mkdir(exist_ok=True)
    cmd = [r'C:\Program Files\OrcaSlicer\orca-slicer.exe', '--datadir', str(folder/'data'), '--debug', '2', '--logfile', str(folder/'slice.log'),
           '--load-settings', str(folder/'machine.json')+';'+str(folder/'process.json'), '--load-filaments', str(folder/'filament.json'),
           '--arrange', '0', '--orient', '0', '--slice', '0', '--export-3mf', 'sliced.3mf', '--outputdir', str(folder), str(folder/'input.3mf')]
    env = os.environ.copy(); env.update(TEMP=str(folder/'temp'), TMP=str(folder/'temp'))
    start = time.time()
    with (folder/'console.log').open('w') as log:
        p = subprocess.run(cmd, cwd=folder, env=env, stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
    (folder/'slice-execution.json').write_text(json.dumps({'plate': plate, 'exit_code': p.returncode, 'elapsed_s': time.time()-start, 'command': cmd}, indent=2)+'\n')
    assert p.returncode == 0 and (folder/'plate_1.gcode').is_file(), plate
    summary = [l for l in (folder/'plate_1.gcode').read_text(encoding='utf-8').splitlines()[:80] if l.startswith(('; model printing time', '; filament used [g]', '; total layer number'))]
    print(plate, summary, flush=True)
