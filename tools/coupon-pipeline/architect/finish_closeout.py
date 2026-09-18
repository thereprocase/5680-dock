"""Finish the site handoff, package evidence, and verify local publication links."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib,json,shutil,zipfile,re,subprocess

ROOT=Path(__file__).resolve().parents[3]
REPO=ROOT/'work/5680-site-handoff';DOCS=REPO/'docs'
E=DOCS/'handoff/2026-09-17';OUT=ROOT/'outputs/5680-design-team/CLOSEOUT-20260917'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
notice='''
  <section class="ps-note handoff-notice" id="september-handoff" aria-label="Latest project status" style="margin:20px 0;padding:18px;background:#fff4dc;color:#101010;border:1px solid #b87900">
    <strong>17 September checkpoint: V4 fit kit ready; D9 unfinished.</strong>
    <p>The reported seating problem still needs a physical contact check. Download the verified full-height coupons and see the filed evidence and next steps.</p>
    <a href="handoff-2026-09-17.html" style="color:#0000a8;text-decoration:underline">Open the handoff, downloads and next steps →</a>
  </section>
'''
for name,marker in [('index.html','  <main id="main">'),('desk-dock.html','<main>')]:
 p=DOCS/name;s=p.read_text(encoding='utf-8')
 assert marker in s
 if 'id="september-handoff"' not in s:
  s=s.replace(marker,marker+notice,1)
  if name=='desk-dock.html':s=s.replace('</style>','.embedded .handoff-notice{display:none}\n</style>',1)
  p.write_text(s,encoding='utf-8')
p=REPO/'README.md';s=p.read_text(encoding='utf-8')
old='**D8 is the current design.** The CAD and manufacturing review is complete; physical fit, strength and cooling tests remain.'
new='''**17 September checkpoint:** the [V4 full-height A/B/C fit kit](docs/downloads/Precision_5680_V4_Full_Rail_Fit_Kit.zip) is toolpath-verified and ready for a supported contact test. The reported seating failure remains unresolved. **D9 is unfinished**: its diagnostic duct failed enclosure/print geometry, and the next panel construction exists only as a plan. No D9 airflow or acoustic improvement has been demonstrated.

**[Handoff, evidence and ordered next steps](https://thereprocase.github.io/5680-dock/handoff-2026-09-17.html)** · [Detailed next-step list](docs/handoff/2026-09-17/NEXT-STEPS.md)

D8 remains the last complete CAD reference. The earlier nominal CAD/manufacturing checks below do not establish physical seating, strength or cooling.'''
if old in s:p.write_text(s.replace(old,new,1),encoding='utf-8')
elif new not in s:raise AssertionError('Unexpected README current-status text')

# Exact file identities and known qualification boundaries, never a blanket PASS.
files={p.relative_to(E).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(E.rglob('*')) if p.is_file() and p.name not in ('SHA256SUMS.json','DELIVERABLES.json')}
(E/'SHA256SUMS.json').write_text(json.dumps({'scope':'Filed evidence bytes, not scientific qualification','files':files},indent=2)+'\n')
archive=DOCS/'downloads/Precision_5680_20260917_Diagnostic_Evidence.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(E.rglob('*')):
  if p.is_file() and p.name!='DELIVERABLES.json':z.write(p,'Precision_5680_20260917_Diagnostic_Evidence/'+p.relative_to(E).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for info in z.infolist():
  local=E/Path(*Path(info.filename).parts[1:])
  assert hashlib.sha256(z.read(info)).hexdigest()==sha(local)

downloads=[]
for name,status in [('Precision_5680_V4_Full_Rail_Fit_Kit.zip','Toolpath-verified handheld contact specimens; physical fit untested'),('Precision_5680_V4_Full_Rail_Fit_Coupons.3mf','Same frozen native Orca plate, one each A/B/C'),('Precision_5680_20260917_Diagnostic_Evidence.zip','Research and failed CAD snapshots, not printable releases')]:
 p=DOCS/'downloads'/name
 downloads.append({'file':name,'url':'https://thereprocase.github.io/5680-dock/downloads/'+name,'bytes':p.stat().st_size,'sha256':sha(p),'qualification':status})
catalog={'date':'2026-09-17','status':'Work paused at user-requested handoff','downloads':downloads,'evidence_files':len(files),'fit_kit_payload_files':43,'fit_kit_total_entries_including_manifest':44,'next_steps':'NEXT-STEPS.md','d9_status':'V3 enclosure/print geometry failed; R1 print geometry held; V4 construction plan only','physical_testing':'None in this handoff','D9_CFD_solver_runs':0}
(E/'DELIVERABLES.json').write_text(json.dumps(catalog,indent=2)+'\n')
shutil.copytree(E,OUT/'evidence',dirs_exist_ok=True)
for p in [archive,DOCS/'downloads/Precision_5680_V4_Full_Rail_Fit_Kit.zip',DOCS/'downloads/Precision_5680_V4_Full_Rail_Fit_Coupons.3mf',E/'NEXT-STEPS.md',E/'DELIVERABLES.json']:
 shutil.copy2(p,OUT/p.name)

class Links(HTMLParser):
 def __init__(self):super().__init__();self.refs=[];self.ids=[];self.scripts=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id'in a:self.ids.append(a['id'])
  if tag=='script':self.scripts.append(a.get('src',''))
  for key in ('href','src'):
   if key in a:self.refs.append(a[key])

checked=0
for name in ('handoff-2026-09-17.html','index.html','desk-dock.html'):
 p=DOCS/name;parser=Links();parser.feed(p.read_text(encoding='utf-8'))
 assert len(parser.ids)==len(set(parser.ids)),(name,'duplicate IDs')
 for ref in parser.refs:
  url=urlsplit(ref)
  if url.scheme or ref.startswith('//'):continue
  target=(p.parent/unquote(url.path)).resolve() if url.path else p
  if target.is_dir():target=target/'index.html'
  assert target.is_relative_to(DOCS.resolve()),ref
  assert target.exists(),(name,ref)
  if url.fragment and target.suffix=='.html':
   other=Links();other.feed(target.read_text(encoding='utf-8'))
   assert unquote(url.fragment) in other.ids,(name,ref)
  checked+=1
 if name!='handoff-2026-09-17.html':
  old=subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO),'show','origin/main:docs/'+name]).decode('utf-8')
  old_parser=Links();old_parser.feed(old)
  assert set(old_parser.ids)<=set(parser.ids),(name,'removed viewer/page IDs')
  assert old_parser.scripts==parser.scripts,(name,'changed script includes')
assert '# next' not in (E/'NEXT-STEPS.md').read_text().lower() # no placeholder headings
secret=re.compile(r'(?:sk-[A-Za-z0-9]{24,}|gh[pousr]_[A-Za-z0-9]{25,}|"(?:session_token|reclaim_secret)"\s*:\s*"[^"\s]{12,}")')
for p in E.rglob('*'):
 if p.is_file() and p.suffix in ('.md','.py','.json','.csv','.html','.txt'):
  assert not secret.search(p.read_text(encoding='utf-8',errors='ignore')),('credential-like content',str(p))
receipt={'passed':True,'local_links_checked':checked,'viewer_ids_and_script_includes_preserved':True,'evidence_zip_roundtrip':True,'evidence_files_hashed':len(files),'downloads':downloads,'browser_visual_check':'Unavailable: computer-use reports no browser; no visual sweep claimed.'}
(OUT/'publication-preflight.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
