#!/usr/bin/env python3
"""
lottie-fetch — download Lottie JSON from LottieFiles or any direct URL.

LottieFiles' public site exposes raw JSON URLs at lottie.host/<id>/<file>.json
(seen in their share links). This tool accepts either:
  - A direct URL to the JSON
  - A LottieFiles share URL (we'll resolve)
  - A LottieFiles asset ID

Usage:
  lottie-fetch.py --url https://lottie.host/abc-123/animation.json --to ./public/loader.json
  lottie-fetch.py --url https://lottiefiles.com/animations/rocket-xyz --to ./public/rocket.json

Output: lottie JSON saved to specified path. Sidecar .json with metadata.
"""

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def resolve_lottiefiles_url(url: str) -> str:
    """
    Try to resolve a lottiefiles.com page URL to its underlying JSON URL.
    The site embeds the JSON URL in og:image-style meta tags or in a JSON-LD blob.
    Heuristic: look for "lottie.host/<id>/...json" in the HTML.
    """
    print(f"==> Resolving {url}", file=sys.stderr)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        html = r.read().decode("utf-8", errors="ignore")

    matches = re.findall(r'https://lottie\.host/[a-zA-Z0-9-]+/[^"\s]+\.json', html)
    if matches:
        return matches[0]

    # Alternative: some pages embed cdn.lottiefiles.com URLs
    matches2 = re.findall(r'https://[^"\s]+lottiefiles\.com[^"\s]+\.json', html)
    if matches2:
        return matches2[0]

    sys.exit(
        f"ERROR: could not resolve JSON URL from {url}. "
        "Open the page in a browser, click 'JSON' or download, copy that direct URL."
    )


def main():
    parser = argparse.ArgumentParser(description="Download Lottie JSON")
    parser.add_argument("--url", required=True, help="Direct JSON URL or LottieFiles page URL")
    parser.add_argument("--to", required=True, help="Output JSON path")
    args = parser.parse_args()

    url = args.url
    # If it's a LottieFiles page (not a direct .json), try resolve.
    if "lottiefiles.com" in url and not url.endswith(".json"):
        url = resolve_lottiefiles_url(url)

    out = Path(args.to).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"==> Downloading {url} → {out}", file=sys.stderr)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        body = r.read()

    # Validate it's JSON
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: downloaded content is not valid JSON ({e}).")

    out.write_bytes(body)

    # Sidecar metadata
    sidecar = out.with_suffix(out.suffix + ".meta.json")
    sidecar.write_text(
        json.dumps(
            {
                "source": "lottiefiles" if "lottiefiles" in args.url else "url",
                "original_url": args.url,
                "resolved_url": url,
                "downloaded_at": datetime.now(timezone.utc).isoformat(),
                "lottie_version": parsed.get("v"),
                "frames": parsed.get("op"),
                "fps": parsed.get("fr"),
                "license": "Check LottieFiles asset page for license terms (most are free, some require attribution)",
            },
            indent=2,
        )
    )
    print(f"OK: {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
