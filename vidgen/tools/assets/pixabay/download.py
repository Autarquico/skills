#!/usr/bin/env python3
"""
Pixabay download — fetch a music/image/video asset to local cache.

Usage:
  download.py --id 12345 --kind music [--to <path>]
  download.py --url <download_url> --kind image [--to <path>]

If --to omitted, saves to ~/.claude/skills/autarqui-video-gen/cache/pixabay/<kind>/<id>.<ext>
Writes a sidecar .json with metadata (author, source, license, query if known).
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

CACHE_ROOT = Path.home() / ".claude/skills/autarqui-video-gen/cache/pixabay"
EXT_BY_KIND = {"music": "mp3", "image": "jpg", "video": "mp4"}


def main():
    parser = argparse.ArgumentParser(description="Download a Pixabay asset")
    parser.add_argument("--id", help="Pixabay asset ID (with --kind)")
    parser.add_argument("--url", help="Direct download URL (alternative to --id)")
    parser.add_argument("--kind", choices=["music", "image", "video"], required=True)
    parser.add_argument("--to", help="Output path (defaults to cache)")
    parser.add_argument("--query", help="Optional: original query for metadata")
    parser.add_argument("--author", help="Optional: author name for metadata")
    parser.add_argument(
        "--page-url", help="Optional: pageURL for metadata", dest="page_url"
    )
    args = parser.parse_args()

    if not args.url and not args.id:
        sys.exit("ERROR: provide --url or --id")

    if not args.url:
        # If only --id given, the user must also know the URL — Pixabay download URL
        # is in the search results (download_url field). For now require explicit --url
        # unless we re-search by ID, which costs a request.
        sys.exit(
            "ERROR: --url required (Pixabay search results include download_url; pass that). "
            "If you only have --id, run search.py again and pluck the URL."
        )

    # Determine output path
    if args.to:
        out_path = Path(args.to).expanduser()
    else:
        ext = EXT_BY_KIND.get(args.kind, "bin")
        # Try to keep the original extension from URL
        url_ext = Path(urllib.parse.urlparse(args.url).path).suffix.lstrip(".") or ext
        cache_dir = CACHE_ROOT / args.kind
        cache_dir.mkdir(parents=True, exist_ok=True)
        asset_id = args.id or "unknown"
        out_path = cache_dir / f"{asset_id}.{url_ext}"

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Skip if cached
    if out_path.exists():
        print(f"Cached (no re-download): {out_path}", file=sys.stderr)
    else:
        print(f"Downloading {args.url} → {out_path}", file=sys.stderr)
        urllib.request.urlretrieve(args.url, out_path)

    # Write sidecar metadata
    sidecar = out_path.with_suffix(out_path.suffix + ".json")
    metadata = {
        "source": "pixabay",
        "kind": args.kind,
        "pixabay_id": args.id,
        "url": args.url,
        "page_url": args.page_url,
        "author": args.author,
        "query": args.query,
        "license": "Pixabay Content License (uso comercial libre, no requiere atribución)",
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "local_path": str(out_path),
    }
    with open(sidecar, "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Output to stdout: JSON with the local path
    print(json.dumps({"path": str(out_path), "metadata": str(sidecar)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
