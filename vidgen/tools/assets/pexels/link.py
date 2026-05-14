#!/usr/bin/env python3
"""Pexels search-link generator for browsing manually."""
import argparse
import sys
import urllib.parse


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="kind", required=True)
    for name in ("photo", "video"):
        sp = sub.add_parser(name)
        sp.add_argument("--q", required=True)
        sp.add_argument(
            "--orientation",
            choices=["landscape", "portrait", "square", "all"],
            default="all",
        )
    args = p.parse_args()
    q = urllib.parse.quote_plus(args.q)
    if args.kind == "photo":
        url = f"https://www.pexels.com/search/{q}/"
    else:
        url = f"https://www.pexels.com/search/videos/{q}/"
    if hasattr(args, "orientation") and args.orientation != "all":
        url += f"?orientation={args.orientation}"
    print(url)


if __name__ == "__main__":
    main()
