#!/usr/bin/env python3
"""
Pixabay link generator — builds a curated search URL for the user to browse.

Use this when the user wants to pick visually instead of accepting top API matches.

Usage:
  link.py music --q "calm cinematic piano" [--duration 60-180]
  link.py image --q "editorial monochrome office" [--orientation horizontal]
  link.py video --q "product reveal motion"

Prints a clickable URL.
"""

import argparse
import sys
import urllib.parse


def music_url(q: str, duration: str | None) -> str:
    q_slug = urllib.parse.quote_plus(q)
    base = f"https://pixabay.com/music/search/{q_slug}/"
    params = []
    if duration:
        params.append(f"duration={duration}")
    # order=ec means "Editor's Choice" — usually higher quality
    params.append("order=ec")
    return base + ("?" + "&".join(params) if params else "")


def image_url(q: str, orientation: str | None) -> str:
    q_slug = urllib.parse.quote_plus(q)
    base = f"https://pixabay.com/images/search/{q_slug}/"
    params = ["order=ec"]
    if orientation and orientation != "all":
        params.append(f"orientation={orientation}")
    return base + "?" + "&".join(params)


def video_url(q: str) -> str:
    q_slug = urllib.parse.quote_plus(q)
    return f"https://pixabay.com/videos/search/{q_slug}/?order=ec"


def main():
    parser = argparse.ArgumentParser(description="Generate Pixabay search URL")
    sub = parser.add_subparsers(dest="kind", required=True)

    pm = sub.add_parser("music")
    pm.add_argument("--q", required=True)
    pm.add_argument("--duration", help="e.g. 60-180")

    pi = sub.add_parser("image")
    pi.add_argument("--q", required=True)
    pi.add_argument(
        "--orientation",
        choices=["horizontal", "vertical", "all"],
        default="all",
    )

    pv = sub.add_parser("video")
    pv.add_argument("--q", required=True)

    args = parser.parse_args()

    if args.kind == "music":
        url = music_url(args.q, args.duration)
    elif args.kind == "image":
        url = image_url(args.q, args.orientation)
    elif args.kind == "video":
        url = video_url(args.q)

    print(url)


if __name__ == "__main__":
    main()
