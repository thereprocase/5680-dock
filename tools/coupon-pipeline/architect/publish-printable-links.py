"""Publish the two printables explicitly requested by the user, plus text updates."""
import hashlib
import json
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
REPO = ROOT / "work/5680-site-handoff"
CLOSEOUT = ROOT / "outputs/5680-design-team/CLOSEOUT-20260917"
FILES = ["docs/handoff-2026-09-17.html", "docs/handoff/2026-09-17/NEXT-STEPS.md",
         "docs/printables/fit-v4/Precision_5680_V4_Full_Rail_Fit_Kit.zip",
         "docs/printables/fit-v4/Precision_5680_V4_Full_Rail_Fit_Coupons.3mf"]
EXPECTED = {FILES[2]: "5d98ca89825dc0012866ddff6cc93e13835a561b51cc547a12badd7109ee9cf2",
            FILES[3]: "82cd4bf29be99299e998e19c7518982df635f766afd07686e72e33da386de8f0"}

def git(*args, raw=False):
    out = subprocess.check_output(["git", "-c", f"safe.directory={REPO.as_posix()}", *args], cwd=REPO)
    return out if raw else out.decode().strip()

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.ids = set()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if "href" in a:
            self.hrefs.append(a["href"])

page = REPO / FILES[0]
links = Links()
links.feed(page.read_text(encoding="utf-8"))
for href in links.hrefs:
    ref = urlsplit(href)
    if ref.scheme or ref.netloc:
        continue
    if ref.path:
        assert (page.parent / unquote(ref.path)).is_file(), href
    elif ref.fragment:
        assert ref.fragment in links.ids, href
assert sum("printables/fit-v4/" in href for href in links.hrefs) == 6
for filename, expected in EXPECTED.items():
    assert hashlib.sha256((REPO / filename).read_bytes()).hexdigest() == expected
    assert (REPO / filename).read_bytes() == (CLOSEOUT / Path(filename).name).read_bytes()
git("diff", "--check")
git("fetch", "origin", "main")
assert git("rev-parse", "HEAD") == git("rev-parse", "origin/main"), "Remote main advanced; review before publishing"
git("add", "--", *FILES)
assert set(git("diff", "--cached", "--name-only").splitlines()) == set(FILES)
for filename, expected in EXPECTED.items():
    assert hashlib.sha256(git("show", f":{filename}", raw=True)).hexdigest() == expected
git("diff", "--cached", "--check")
git("-c", "user.name=thereprocase", "-c", "user.email=128980993+thereprocase@users.noreply.github.com",
    "commit", "-m", "Link downloadable V4 fit printables and clarify support criteria")
commit = git("rev-parse", "HEAD")
git("push", "origin", "HEAD:main")
receipt = {"commit": commit, "files": FILES, "printable_sha256": EXPECTED,
           "local_links_checked": len(links.hrefs), "push_succeeded": True,
           "live_verification": "pending", "raw_diagnostic_archive_published": False}
(CLOSEOUT / "printable-links-publication.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
