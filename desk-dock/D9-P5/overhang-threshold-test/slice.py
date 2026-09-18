import subprocess,os,sys
from pathlib import Path
d=Path(__file__).resolve().parent;(d/'data').mkdir(exist_ok=True);(d/'temp').mkdir(exist_ok=True)
cmd=[r'C:\Program Files\OrcaSlicer\orca-slicer.exe','--datadir',str(d/'data'),'--load-settings',str(d/'machine.json')+';'+str(d/'process.json'),'--load-filaments',str(d/'filament.json'),'--arrange','0','--orient','0','--slice','0','--export-3mf','sliced.3mf','--outputdir',str(d),str(d/'input.3mf')]
env=os.environ.copy();env.update(TEMP=str(d/'temp'),TMP=str(d/'temp'))
p=subprocess.run(cmd,cwd=d,env=env,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW);print('exit',p.returncode,(p.stdout+p.stderr)[-300:])
