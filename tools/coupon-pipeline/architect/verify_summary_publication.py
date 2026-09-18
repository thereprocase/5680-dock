from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[3];REPO=ROOT/'work/5680-site-handoff';DOCS=REPO/'docs'
OUT=ROOT/'outputs/5680-design-team/CLOSEOUT-20260917'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.refs=[];self.ids=[];self.scripts=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.append(d['id'])
  if tag=='script':self.scripts.append(d.get('src',''))
  self.refs.extend(d[k] for k in ('href','src') if k in d)
checked=0
for name in ('handoff-2026-09-17.html','index.html','desk-dock.html'):
 p=DOCS/name;a=Links();a.feed(p.read_text(encoding='utf-8'))
 assert len(a.ids)==len(set(a.ids))
 for ref in a.refs:
  u=urlsplit(ref)
  if u.scheme or ref.startswith('//'):continue
  t=(p.parent/unquote(u.path)).resolve() if u.path else p
  if t.is_dir():t=t/'index.html'
  assert t.is_relative_to(DOCS.resolve()) and t.exists(),(name,ref)
  if u.fragment and t.suffix=='.html':
   b=Links();b.feed(t.read_text(encoding='utf-8'));assert unquote(u.fragment) in b.ids,(name,ref)
  checked+=1
 if name!='handoff-2026-09-17.html':
  old=subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),'show','origin/main:docs/'+name]).decode()
  b=Links();b.feed(old);assert set(b.ids)<=set(a.ids) and b.scripts==a.scripts
assert [p.relative_to(DOCS/'handoff').as_posix() for p in (DOCS/'handoff').rglob('*') if p.is_file()]==['2026-09-17/NEXT-STEPS.md']
assert not list((DOCS/'downloads').glob('Precision_5680_*V4*'))
assert not (DOCS/'downloads/Precision_5680_20260917_Diagnostic_Evidence.zip').exists()
manifest=json.loads((OUT/'evidence/SHA256SUMS.json').read_text())['files']
for n,r in manifest.items():assert hashlib.sha256((OUT/'evidence'/n).read_bytes()).hexdigest()==r['sha256'],n
catalog=json.loads((OUT/'DELIVERABLES.json').read_text())
for d in catalog['downloads']:
 p=OUT/d['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==d['sha256']
 d.pop('url',None);d['local_file']=d['file']
catalog['publication']='Status and next steps only. CAD, source, renders and raw evidence archives remain local; public upload was rejected by automatic approval review.'
for p in (OUT/'DELIVERABLES.json',OUT/'evidence/DELIVERABLES.json'):p.write_text(json.dumps(catalog,indent=2)+'\n')
(OUT/'unpublished-site-payload/README.md').write_text('This is the preserved, UNPUBLISHED full-payload website draft. Automatic approval review rejected public disclosure of the CAD/source/evidence bundle. URLs in this draft are proposed paths, not live downloads. The actual published site contains only the requested status and next-step summary.\n')
report={'passed':True,'publication_scope':'Five text files: status, local artifact index, ordered next steps, and entry links. No CAD/source/render/archive uploads.','links_checked':checked,'viewer_ids_and_scripts_preserved':True,'local_evidence_files_hash_verified':len(manifest),'local_downloads_hash_verified':len(catalog['downloads']),'browser_visual_check':'No browser available; no visual sweep claimed.'}
(OUT/'summary-publication-preflight.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
