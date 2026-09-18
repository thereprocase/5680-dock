"""Run one native Orca verification pass on an already reviewed frozen plate."""
from pathlib import Path
import argparse,json,os,subprocess,time

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--slice-dir',type=Path,required=True)
args=parser.parse_args()
folder=args.slice_dir.resolve()
assert (folder/'geometry-review-receipt.md').is_file()
assert (folder/'plate-preparation.json').is_file()
assert not (folder/'plate_1.gcode').exists(), 'Preserve previous slice evidence'
temp=folder/'temp'
temp.mkdir(exist_ok=True)
data=folder/'data'
data.mkdir(exist_ok=True)
env=os.environ.copy()
env.update(TEMP=str(temp),TMP=str(temp))
command=[r'C:\Program Files\OrcaSlicer\orca-slicer.exe','--datadir',str(data),
         '--debug','2','--logfile',str(folder/'slice.log'),
         '--load-settings',str(folder/'machine.json')+';'+str(folder/'process.json'),
         '--load-filaments',str(folder/'filament.json'),
         '--arrange','0','--orient','0',
         '--slice','0','--export-3mf','coupons-sliced.3mf','--outputdir',str(folder),
         str(folder/'reviewed-coupons-input.3mf')]
startup=subprocess.STARTUPINFO()
startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
startup.wShowWindow=0
started=time.time()
with (folder/'orca-console.log').open('w') as log:
    result=subprocess.run(command,cwd=folder,env=env,stdout=log,stderr=subprocess.STDOUT,
                          startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
receipt={'exit_code':result.returncode,'elapsed_seconds':time.time()-started,
         'command':command,'purpose':'Single verification slice of geometrically selected orientation; no printer connection'}
(folder/'slice-execution.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
assert result.returncode==0 and (folder/'plate_1.gcode').is_file()
assert (folder/'coupons-sliced.3mf').is_file()
