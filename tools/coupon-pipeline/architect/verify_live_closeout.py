from pathlib import Path
from urllib.request import build_opener,ProxyHandler,Request
from urllib.error import HTTPError
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[3];REPO=ROOT/'work/5680-site-handoff'
OUT=ROOT/'outputs/5680-design-team/CLOSEOUT-20260917'
BASE='https://thereprocase.github.io/5680-dock/'
git=['git','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO)]
commit=subprocess.check_output(git+['rev-parse','HEAD']).decode().strip()
build=json.loads(subprocess.check_output(['gh','api','repos/thereprocase/5680-dock/pages/builds/latest']))
opener=build_opener(ProxyHandler({}));records=[]
for name in ('index.html','desk-dock.html','handoff-2026-09-17.html','handoff/2026-09-17/NEXT-STEPS.md'):
 url=BASE+name+'?checkpoint='+commit[:8]
 try:
  with opener.open(Request(url,headers={'User-Agent':'5680-handoff-verification'}),timeout=30) as response:
   data=response.read();status=response.status
  expected=subprocess.check_output(git+['show','HEAD:docs/'+name])
  records.append({'url':url,'status':status,'sha256':hashlib.sha256(data).hexdigest(),'matches_published_commit':data==expected,'bytes':len(data)})
 except HTTPError as e:records.append({'url':url,'status':e.code,'matches_published_commit':False})
passed=build.get('status')=='built' and build.get('commit')==commit and all(r.get('matches_published_commit') for r in records)
receipt={'passed':passed,'commit':commit,'pages_build':{'status':build.get('status'),'commit':build.get('commit'),'updated_at':build.get('updated_at'),'error':build.get('error')},'pages':records,'scope':'Live HTTP status and exact served bytes; browser visual inspection unavailable.'}
(OUT/'live-publication-verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
if not passed:raise SystemExit(2)
