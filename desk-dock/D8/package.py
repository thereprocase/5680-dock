"""Package D8 print/source review and separate complete STEP for GitHub Pages.

Run after updating CAD exports, reports and presentation files. This script
does not regenerate CAD or claim printer/physical qualification.
"""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

R = Path(__file__).resolve().parent
ROOT = R.parents[1]
OUT = ROOT / "docs" / "downloads"
OUT.mkdir(parents=True, exist_ok=True)


def digest(data):
    return hashlib.sha256(data).hexdigest()


step_record = json.loads((R / "step-archive.json").read_text())
step = R / step_record["archive"]
assert digest(step.read_bytes()) == step_record["archive_sha256"]
with zipfile.ZipFile(step) as source:
    assert digest(source.read(step_record["member"])) == step_record["extracted_sha256"]
shutil.copyfile(step, OUT / step.name)

assert json.loads((R / "validation.json").read_text())["passed"]
assert json.loads((R / "print-review/mesh-preflight-summary.json").read_text())["geometric_preflight_pass"]
assert len(list((R / "print").glob("*.stl"))) == 43

files = sorted(
    p for p in R.rglob("*")
    if p.is_file()
    and p.suffix in {".py", ".json", ".md", ".png", ".stl"}
    and p.name not in {"checkpoint-manifest.json", "download-manifest.json"}
    and "__pycache__" not in p.parts
)
files += [ROOT / "LICENSE", ROOT / "AGENTS.md"]
members = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in files}
members["START_HERE.md"] = b"""# Precision 5680 D8 print and source package

This archive contains all 43 manufacturing STLs, editable D8 source, renders,
design notes and the recorded CAD/manufacturing checks.

The complete STEP CAD is a separate download:
https://thereprocase.github.io/5680-dock/downloads/Precision_5680_D8_STEP.zip
Extract that archive into desk-dock/D8 if you want the STEP beside these files.

Start with desk-dock/D8/README.md and CURRENT_STATUS.md. Use the full GitHub
repository for historical references and the web viewer. This package contains
no approved P1S G-code; physical fit and strength still need qualification.

Current source and interactive model:
https://github.com/thereprocase/5680-dock
https://thereprocase.github.io/5680-dock/desk-dock.html
"""
hashes = {name: digest(data) for name, data in members.items()}
members["package-manifest.json"] = (json.dumps(hashes, indent=2) + "\n").encode()
archive = OUT / "Precision_5680_D8_Review.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for name, data in members.items():
        entry = zipfile.ZipInfo(name, (2026, 9, 8, 0, 0, 0))
        entry.external_attr = 0o100644 << 16
        z.writestr(entry, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert all(digest(z.read(name)) == expected for name, expected in hashes.items())

record = {
    "revision": "D8",
    "notice": "Print/source and STEP are separate downloads; no approved P1S machine jobs.",
    "print_source": {"file": archive.name, "bytes": archive.stat().st_size,
                     "sha256": digest(archive.read_bytes()), "members": len(members),
                     "member_hashes_verified": True, "print_meshes": 43},
    "step": {"file": step.name, "bytes": step.stat().st_size,
             "sha256": digest(step.read_bytes()), "extracted_sha256": step_record["extracted_sha256"]},
}
(R / "download-manifest.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
