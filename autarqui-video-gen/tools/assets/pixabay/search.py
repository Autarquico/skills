#!/usr/bin/env python3
"""
Pixabay search — programmatic API search for music, images, video.

Usage:
  search.py music --q "calm piano cinematic" [--duration 60-120] [--per-page 10]
  search.py image --q "editorial office" [--orientation horizontal] [--per-page 10]
  search.py video --q "minimal product motion" [--per-page 10]

Output: JSON to stdout with top matches (id, preview_url, download_url, duration, author, tags).

Requires PIXABAY_API_KEY in ~/.claude/skills/autarqui-video-gen/config/api-keys.yaml
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

CONFIG_PATH = Path.home() / ".claude/skills/autarqui-video-gen/config/api-keys.yaml"


def load_api_key() -> str:
    if not CONFIG_PATH.exists():
        sys.exit(
            f"ERROR: {CONFIG_PATH} not found. Copy api-keys.yaml.template to api-keys.yaml "
            "and add your Pixabay key (free signup at https://pixabay.com/api/docs/)."
        )
    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f) or {}
    key = cfg.get("pixabay", "")
    if not key:
        sys.exit(
            "ERROR: 'pixabay' key empty in api-keys.yaml. "
            "Get a free key at https://pixabay.com/api/docs/"
        )
    return key


def search_music(q: str, duration: str | None, per_page: int, key: str) -> list[dict]:
    # Pixabay music API: https://pixabay.com/api/docs/#api_music
    params = {
        "key": key,
        "q": q,
        "per_page": min(max(per_page, 3), 200),
    }
    if duration:
        # Pixabay supports min_duration and max_duration in seconds
        try:
            lo, hi = duration.split("-")
            params["min_duration"] = int(lo)
            params["max_duration"] = int(hi)
        except ValueError:
            pass

    url = "https://pixabay.com/api/music/?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read())

    return [
        {
            "id": h["id"],
            "title": h.get("title") or h.get("tags"),
            "duration_s": h.get("duration"),
            "author": h.get("user"),
            "preview_url": h.get("preview_url") or h.get("audio"),
            "download_url": h.get("audio"),
            "page_url": h.get("pageURL"),
            "tags": h.get("tags"),
            "license": "Pixabay Content License",
        }
        for h in data.get("hits", [])
    ]


def search_image(q: str, orientation: str | None, per_page: int, key: str) -> list[dict]:
    params = {
        "key": key,
        "q": q,
        "per_page": min(max(per_page, 3), 200),
        "image_type": "photo",
    }
    if orientation:
        params["orientation"] = orientation  # horizontal | vertical | all

    url = "https://pixabay.com/api/?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read())

    return [
        {
            "id": h["id"],
            "tags": h.get("tags"),
            "author": h.get("user"),
            "preview_url": h.get("previewURL"),
            "download_url": h.get("largeImageURL") or h.get("webformatURL"),
            "width": h.get("imageWidth"),
            "height": h.get("imageHeight"),
            "page_url": h.get("pageURL"),
            "license": "Pixabay Content License",
        }
        for h in data.get("hits", [])
    ]


def search_video(q: str, per_page: int, key: str) -> list[dict]:
    params = {
        "key": key,
        "q": q,
        "per_page": min(max(per_page, 3), 200),
    }
    url = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as r:
        data = json.loads(r.read())

    return [
        {
            "id": h["id"],
            "tags": h.get("tags"),
            "author": h.get("user"),
            "duration_s": h.get("duration"),
            "preview_url": h.get("videos", {}).get("tiny", {}).get("url"),
            "download_url": h.get("videos", {}).get("large", {}).get("url")
            or h.get("videos", {}).get("medium", {}).get("url"),
            "width": h.get("videos", {}).get("large", {}).get("width"),
            "height": h.get("videos", {}).get("large", {}).get("height"),
            "page_url": h.get("pageURL"),
            "license": "Pixabay Content License",
        }
        for h in data.get("hits", [])
    ]


def main():
    parser = argparse.ArgumentParser(description="Pixabay programmatic search")
    sub = parser.add_subparsers(dest="kind", required=True)

    pm = sub.add_parser("music", help="Search Pixabay music")
    pm.add_argument("--q", required=True, help="Query string")
    pm.add_argument("--duration", help="Duration range in seconds, e.g. 60-120")
    pm.add_argument("--per-page", type=int, default=10)

    pi = sub.add_parser("image", help="Search Pixabay images")
    pi.add_argument("--q", required=True)
    pi.add_argument(
        "--orientation",
        choices=["horizontal", "vertical", "all"],
        default="all",
    )
    pi.add_argument("--per-page", type=int, default=10)

    pv = sub.add_parser("video", help="Search Pixabay videos")
    pv.add_argument("--q", required=True)
    pv.add_argument("--per-page", type=int, default=10)

    args = parser.parse_args()
    key = load_api_key()

    if args.kind == "music":
        results = search_music(args.q, args.duration, args.per_page, key)
    elif args.kind == "image":
        results = search_image(args.q, args.orientation, args.per_page, key)
    elif args.kind == "video":
        results = search_video(args.q, args.per_page, key)

    json.dump(
        {"kind": args.kind, "query": args.q, "count": len(results), "results": results},
        sys.stdout,
        indent=2,
        ensure_ascii=False,
    )
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
