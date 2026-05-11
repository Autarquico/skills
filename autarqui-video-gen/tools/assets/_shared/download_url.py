#!/usr/bin/env python3
"""
download_url — generic URL download with cache + sidecar metadata.
Used by Pexels/Unsplash/Freesound/LottieFiles download.py wrappers.

Usage:
  download_url.py --url <URL> --to <path> --source pexels --kind photo \\
                  [--id 123] [--author NAME] [--query Q] [--license LICENSE_TEXT]
"""

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--to", required=True)
    p.add_argument("--source", required=True, help="pexels|unsplash|freesound|lottiefiles|...")
    p.add_argument("--kind", required=True, help="music|image|video|sfx|lottie")
    p.add_argument("--id")
    p.add_argument("--author")
    p.add_argument("--query")
    p.add_argument("--license", default="See source platform for license details")
    p.add_argument("--page-url", dest="page_url")
    args = p.parse_args()

    out = Path(args.to).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)

    if out.exists():
        print(f"Cached (no re-download): {out}", file=sys.stderr)
    else:
        print(f"Downloading {args.url} → {out}", file=sys.stderr)
        req = urllib.request.Request(args.url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r, open(out, "wb") as f:
            f.write(r.read())

    sidecar = out.with_suffix(out.suffix + ".json")
    metadata = {
        "source": args.source,
        "kind": args.kind,
        "asset_id": args.id,
        "url": args.url,
        "page_url": args.page_url,
        "author": args.author,
        "query": args.query,
        "license": args.license,
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "local_path": str(out),
    }
    with open(sidecar, "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(json.dumps({"path": str(out), "metadata": str(sidecar)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
