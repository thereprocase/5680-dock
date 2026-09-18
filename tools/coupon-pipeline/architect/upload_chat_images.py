"""Post explicitly selected renders through the existing trusted web operator API."""
import argparse
import http.cookiejar
import json
from pathlib import Path
import urllib.parse
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("--base", required=True)
parser.add_argument("--channel", required=True)
parser.add_argument("--caption", required=True)
parser.add_argument("images", nargs="+", type=Path)
args = parser.parse_args()
if not 1 <= len(args.images) <= 8:
    raise SystemExit("Select one to eight images.")
base = args.base.rstrip("/")
query = urllib.parse.urlencode({"channel": args.channel})
opener = urllib.request.build_opener(
    urllib.request.ProxyHandler({}),
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
)
with opener.open(base + "/?" + query, timeout=15) as reply:
    reply.read()
attachments = []
for path in args.images:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) > 10 * 1024 * 1024:
        raise ValueError("Only PNG renders under 10 MiB are accepted by this helper.")
    request = urllib.request.Request(base + "/api/upload?" + query, data=data,
        headers={"Content-Type": "image/png", "X-Filename": urllib.parse.quote(path.name)}, method="POST")
    with opener.open(request, timeout=30) as reply:
        result = json.load(reply)
    if not result.get("ok"):
        raise RuntimeError("Upload did not succeed.")
    attachments.append(result["id"])
payload = json.dumps({"content": args.caption, "attachment_ids": attachments}).encode()
request = urllib.request.Request(base + "/api/send?" + query, data=payload,
    headers={"Content-Type": "application/json"}, method="POST")
with opener.open(request, timeout=30) as reply:
    result = json.load(reply)
print(json.dumps({"send": result, "attachment_ids": attachments,
                  "filenames": [p.name for p in args.images]}))
