#!/usr/bin/env python3
"""
Unsplash search — premium lifestyle / editorial photo API.
Free demo tier: 50 req/h. Production tier: 5000 req/h after approval.

Usage:
  search.py --q "editorial office" [--orientation landscape] [--per-page 10]

Requires UNSPLASH_API_KEY (Access Key) in api-keys.yaml.
Get one at https://unsplash.com/developers (free).
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
    key = cfg.get("unsplash", "")
    if not key:
        sys.exit("ERROR: 'unsplash' empty in api-keys.yaml. Get free key at https://unsplash.com/developers")
    return key


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--q", required=True)
    p.add_argument("--orientation", choices=["landscape", "portrait", "squarish", "all"], default="all")
    p.add_argument("--per-page", type=int, default=10)
    args = p.parse_args()

    key = load_api_key()
    params = {"query": args.q, "per_page": args.per_page}
    if args.orientation != "all":
        params["orientation"] = args.orientation
    url = "https://api.unsplash.com/search/photos?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Client-ID {key}"})
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read())

    results = [
        {
            "id": p["id"],
            "author": p.get("user", {}).get("name"),
            "author_username": p.get("user", {}).get("username"),
            "preview_url": p["urls"].get("small"),
            "download_url": p["urls"].get("full"),
            "width": p.get("width"),
            "height": p.get("height"),
            "page_url": p.get("links", {}).get("html"),
            "license": "Unsplash License (uso libre + atribución apreciada — formato: 'Photo by NAME on Unsplash')",
        }
        for p in data.get("results", [])
    ]
    json.dump(
        {"source": "unsplash", "query": args.q, "count": len(results), "results": results},
        sys.stdout,
        indent=2,
        ensure_ascii=False,
    )
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
