#!/usr/bin/env python3
"""Unsplash search-link generator."""
import argparse
import urllib.parse

p = argparse.ArgumentParser()
p.add_argument("--q", required=True)
p.add_argument("--orientation", choices=["landscape", "portrait", "squarish", "all"], default="all")
args = p.parse_args()
q = urllib.parse.quote_plus(args.q)
url = f"https://unsplash.com/s/photos/{q}"
if args.orientation != "all":
    url += f"?orientation={args.orientation}"
print(url)
