"""Honor publication review: keep raw payload local; publish requested summary."""
from pathlib import Path
import re,shutil

ROOT=Path(__file__).resolve().parents[3]
REPO=ROOT/'work/5680-site-handoff';DOCS=REPO/'docs'
OUT=ROOT/'outputs/5680-design-team/CLOSEOUT-20260917'
HELD=OUT/'unpublished-site-payload'
HELD.mkdir(exist_ok=True)
# Preserve the exact rejected publication draft and all bytes before narrowing.
shutil.copy2(DOCS/'handoff-2026-09-17.html',HELD/'handoff-with-archives.html')
for rel in ('handoff/2026-09-17','downloads/Precision_5680_V4_Full_Rail_Fit_Kit.zip','downloads/Precision_5680_V4_Full_Rail_Fit_Coupons.3mf','downloads/Precision_5680_20260917_Diagnostic_Evidence.zip'):
 source=(DOCS/rel).resolve();target=(HELD/rel).resolve()
 assert source.is_relative_to(DOCS.resolve()) and target.is_relative_to(HELD.resolve())
 assert not target.exists()
 target.parent.mkdir(parents=True,exist_ok=True)
 shutil.move(str(source),str(target))
(DOCS/'handoff/2026-09-17').mkdir(parents=True,exist_ok=True)
shutil.copy2(OUT/'NEXT-STEPS.md',DOCS/'handoff/2026-09-17/NEXT-STEPS.md')
p=DOCS/'handoff/2026-09-17/NEXT-STEPS.md'
p.write_text(p.read_text(encoding='utf-8').replace('Work is paused at this checkpoint.','Work is paused at this checkpoint. The kit and full evidence are filed locally\nin `outputs/5680-design-team/CLOSEOUT-20260917/`.'),encoding='utf-8')

old=(HELD/'handoff-with-archives.html').read_text(encoding='utf-8')
steps=re.search(r'    <section class="ps-section" id="next-steps">.*?</section>',old,re.S).group()
status=re.search(r'    <section class="ps-section" id="status">.*?</section>',old,re.S).group()
head=old.split('<body',1)[0].replace('verified V4 fit-coupon downloads, D9 diagnostic evidence','filed V4 fit coupons, D9 diagnostic status')
page=head+'''<body class="project-site" data-project="5680-dock">
<a class="gl-skip" href="#main">Skip to content</a>
<div class="ps-frame handoff">
<header class="ps-network"><a href="index.html">Precision 5680 dock</a><span>17 SEPTEMBER 2026 · WORK FILED / DEVELOPMENT PAUSED</span><a href="https://github.com/thereprocase/5680-dock">Source repository ↗</a></header>
<nav class="handoff-nav" aria-label="Handoff navigation"><a href="#status">Current status</a><a href="#files">Filed deliverables</a><a href="#next-steps">Next steps</a><a href="#evidence">Evidence summary</a><a href="desk-dock.html">D8 reference viewer</a></nav>
<main class="ps-main" id="main">
<section class="ps-hero" aria-labelledby="title"><p class="ps-eyebrow">A concrete checkpoint for the next session</p><h1 id="title">The fit kit is ready.<br>The D9 dock is unfinished.</h1><p class="ps-lead">Start with the full-height A/B/C coupons to understand why the real laptop rocks onto the short fence instead of seating on its cradles. The complete dock has not been qualified.</p><div class="ps-actions"><a class="ps-button primary" href="#next-steps">Read the next steps ↓</a><a class="ps-button" href="#files">Find the filed deliverables ↓</a></div></section>
'''+status+'''
<section class="ps-section" id="files"><h2>Filed deliverables · local handoff</h2><div class="ps-body">
<p>The complete files are preserved in the local project workspace at <code>outputs/5680-design-team/CLOSEOUT-20260917/</code>. The public page records their status and the next steps; raw CAD, source and diagnostic archives have not been uploaded.</p>
<div class="table-scroll"><table><thead><tr><th scope="col">File or folder</th><th scope="col">Contents and status</th></tr></thead><tbody>
<tr><th scope="row"><code>Precision_5680_V4_Full_Rail_Fit_Kit.zip</code></th><td>The full kit: 43 hashed payload files plus the manifest. Native Orca project, matching G-code, fallback STEP/STL, editable source, profiles, previews and verification receipts. Toolpaths verified; physical fit untested.</td></tr>
<tr><th scope="row"><code>Precision_5680_V4_Full_Rail_Fit_Coupons.3mf</code></th><td>One each A/B/C, P1S, 0.4-mm nozzle, Generic PETG, textured PEI. Estimated 47.02 g and 1 h 56 m 58 s. Open in Orca and confirm it matches the actual printer/material. No print was sent.</td></tr>
<tr><th scope="row"><code>Precision_5680_20260917_Diagnostic_Evidence.zip</code></th><td>Failed D9 snapshots, independent review, calculations, source revisions and unexecuted test plans. <strong>Not a print release.</strong> The later V3 builder does not reproduce the original frozen export; that mismatch is recorded.</td></tr>
<tr><th scope="row"><code>evidence/</code>, <code>DELIVERABLES.json</code>, <code>NEXT-STEPS.md</code></th><td>Readable evidence folders, download identities and hashes, and the ordered resume list. Original four V1 photos remain in the adjacent <code>physical-fit-evidence/</code> folder.</td></tr>
</tbody></table></div>
<p><strong>Coupon identifiers:</strong> A has one square opening and the original R1 profile. B has two and the actual R2 capture changes. C has three and adds the local 1-mm seat relief to B. All retain the full original lid-side rail.</p>
<p><strong>Fit-kit SHA-256:</strong> <code>5d98ca89825dc0012866ddff6cc93e13835a561b51cc547a12badd7109ee9cf2</code></p>
</div></section>
'''+steps+'''
<section class="ps-section linked" id="evidence"><h2>Evidence summary · scope matters</h2><div class="ps-body">
<ul>
<li><strong>V4 manufacturing:</strong> selected constant-section print geometry, zero support paths and zero external bridges in Orca. All six identifiers retain the checked 1-mm clear cores across 120 layers. Native embedded and standalone G-code match. Physical print quality is untested.</li>
<li><strong>V1 photos:</strong> the reported rocking and missed cradle engagement are documented. Exact local contour, clearances, pivot and sealing remain unresolved. Neither the photos nor nominal CAD supports a blanket 4-mm correction.</li>
<li><strong>V3 identifier correction:</strong> the first failed hole check omitted the frozen nozzle coordinate offset. That failure was withdrawn; larger V4 identifiers remain the selected trial. This is not a physical nozzle calibration.</li>
<li><strong>D9 V3:</strong> the intended air volume remained connected to exterior even with both named ports capped. The tray and lid had unsupported undersides in their nominated poses. R1 also failed its print-normal check. Individual watertight STLs do not prove an enclosed or printable assembly.</li>
<li><strong>Flow calculations:</strong> the corrected generic fan/area screen reproduced 140 operating rows and 30 constraints. Assumed loss coefficients and source-mouth areas do not establish actual D9 or useful laptop flow.</li>
<li><strong>Unexecuted work:</strong> D9 V4 is a panel-construction plan only. No D9 mesh or CFD solve, physical cooling test, noise measurement or full-dock qualification was performed. The future 10-CFM resistance test and acoustic comparison remain plans.</li>
</ul>
<p>The local evidence archive includes exact output hashes and the diagnostic receipts needed to resume without repeating the same failures.</p>
</div></section>
</main><footer class="ps-footer"><span>5680 DOCK / 17 SEPTEMBER CHECKPOINT</span><a href="index.html">Project home ↗</a><a href="#next-steps">Next steps ↑</a></footer>
</div></body></html>
'''
(DOCS/'handoff-2026-09-17.html').write_text(page,encoding='utf-8')
for name in ('index.html','desk-dock.html'):
 p=DOCS/name;s=p.read_text(encoding='utf-8')
 s=s.replace('Download the verified full-height coupons and see the filed evidence and next steps.','The verified full-height coupons and diagnostic evidence are filed locally; see the handoff for their locations and next steps.')
 s=s.replace('Open the handoff, downloads and next steps','Open the handoff, deliverables and next steps')
 p.write_text(s,encoding='utf-8')
p=REPO/'README.md';s=p.read_text(encoding='utf-8')
s=s.replace('[V4 full-height A/B/C fit kit](docs/downloads/Precision_5680_V4_Full_Rail_Fit_Kit.zip)','V4 full-height A/B/C fit kit (filed locally)')
p.write_text(s,encoding='utf-8')
p=REPO/'.gitattributes';s=p.read_text(encoding='utf-8')
s=s.replace('\n# Frozen September handoff evidence retains original byte hashes, including\n# historical line endings and whitespace. Do not normalize copied receipts.\n/docs/handoff/2026-09-17/** -text whitespace=-blank-at-eol,cr-at-eol\n','')
p.write_text(s,encoding='utf-8')
print('Summary-only publication prepared. Full draft and raw payload preserved locally.')
