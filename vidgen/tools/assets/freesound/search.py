#!/usr/bin/env python3
"""
Freesound search — Creative Commons sound effects.
Free signup at https://freesound.org/help/developers/ (token-based auth, no OAuth).

Usage:
  search.py --q "soft whoosh ui" [--max-duration 5]

Requires FREESOUND_API_KEY in api-keys.yaml.

NOTE: Freesound uses CC licenses. Each sound has its own license (CC0, CC-BY, CC-BY-NC, etc.).
The license is in each result. Check before using commercially.
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

CONFIG_PATH = Path.home() / ".claude/skills/autarqui-video-gen/config/api-keys.yaml"


def load_api_key() -> str:
    if not CONFIG_PATH.exists():
        sys.exit(f"ERROR: {CONFIG_PATH} not found.")
    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f) or {}
    key = cfg.get("freesound", "")
    if not key:
        sys.exit("ERROR: 'freesound' empty in api-keys.yaml. Get free key at https://freesound.org/apiv2/apply/")
    return key


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--q", required=True)
    p.add_argument("--max-duration", type=float, help="Filter to sounds shorter than N seconds")
    p.add_argument("--page-size", type=int, default=10)
    args = p.parse_args()

    key = load_api_key()
    params = {
        "query": args.q,
        "page_size": args.page_size,
        "fields": "id,name,description,duration,username,license,previews,download,url,tags",
        "token": key,
    }
    if args.max_duration:
        params["filter"] = f"duration:[0 TO {args.max_duration}]"

    url = "https://freesound.org/apiv2/search/text/?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read())

    results = [
        {
            "id": s["id"],
            "name": s.get("name"),
            "duration_s": s.get("duration"),
            "author": s.get("username"),
            "preview_url": s.get("previews", {}).get("preview-hq-mp3"),
            "download_url": s.get("download"),  # requires OAuth for actual download
            "page_url": s.get("url"),
            "license": s.get("license"),
            "tags": s.get("tags"),
        }
        for s in data.get("results", [])
    ]
    json.dump(
        {"source": "freesound", "query": args.q, "count": len(results), "results": results},
        sys.stdout,
        indent=2,
        ensure_ascii=False,
    )
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
