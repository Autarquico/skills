#!/usr/bin/env python3
"""
Pexels search — programmatic API for photos and videos.
Pexels is stronger than Pixabay for editorial photography (lifestyle, hands-at-work).

Usage:
  search.py photo --q "editorial office monochrome" [--orientation landscape] [--per-page 10]
  search.py video --q "minimal product motion" [--per-page 10]

Requires PEXELS_API_KEY in api-keys.yaml (free at https://www.pexels.com/api/).
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
    key = cfg.get("pexels", "")
    if not key:
        sys.exit("ERROR: 'pexels' empty in api-keys.yaml. Get free key at https://www.pexels.com/api/")
    return key


def search_photo(q: str, orientation: str | None, per_page: int, key: str) -> list[dict]:
    params = {"query": q, "per_page": per_page}
    if orientation and orientation != "all":
        params["orientation"] = orientation
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": key})
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read())
    return [
        {
            "id": p["id"],
            "author": p.get("photographer"),
            "preview_url": p["src"].get("medium"),
            "download_url": p["src"].get("original"),
            "width": p.get("width"),
            "height": p.get("height"),
            "page_url": p.get("url"),
            "license": "Pexels License (uso comercial libre, atribución apreciada pero no requerida)",
        }
        for p in data.get("photos", [])
    ]


def search_video(q: str, per_page: int, key: str) -> list[dict]:
    params = {"query": q, "per_page": per_page}
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": key})
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read())
    out = []
    for v in data.get("videos", []):
        # pick the largest mp4 file
        files = sorted(
            [f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4"],
            key=lambda f: (f.get("width") or 0),
            reverse=True,
        )
        if not files:
            continue
        out.append(
            {
                "id": v["id"],
                "author": v.get("user", {}).get("name"),
                "duration_s": v.get("duration"),
                "preview_url": v.get("image"),
                "download_url": files[0].get("link"),
                "width": files[0].get("width"),
                "height": files[0].get("height"),
                "page_url": v.get("url"),
                "license": "Pexels License",
            }
        )
    return out


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="kind", required=True)
    pp = sub.add_parser("photo")
    pp.add_argument("--q", required=True)
    pp.add_argument("--orientation", choices=["landscape", "portrait", "square", "all"], default="all")
    pp.add_argument("--per-page", type=int, default=10)
    pv = sub.add_parser("video")
    pv.add_argument("--q", required=True)
    pv.add_argument("--per-page", type=int, default=10)
    args = p.parse_args()

    key = load_api_key()
    if args.kind == "photo":
        results = search_photo(args.q, args.orientation, args.per_page, key)
    else:
        results = search_video(args.q, args.per_page, key)
    json.dump(
        {"source": "pexels", "kind": args.kind, "query": args.q, "count": len(results), "results": results},
        sys.stdout,
        indent=2,
        ensure_ascii=False,
    )
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
