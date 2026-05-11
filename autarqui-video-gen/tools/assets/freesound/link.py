#!/usr/bin/env python3
"""Freesound search-link generator."""
import argparse
import urllib.parse

p = argparse.ArgumentParser()
p.add_argument("--q", required=True)
p.add_argument("--max-duration", type=float, help="Filter to <= N seconds")
args = p.parse_args()
q = urllib.parse.quote_plus(args.q)
url = f"https://freesound.org/search/?q={q}"
if args.max_duration:
    url += f"&f=duration:[0+TO+{args.max_duration}]"
print(url)
