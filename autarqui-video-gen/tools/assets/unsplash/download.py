#!/usr/bin/env python3
"""Unsplash download. NOTE: per Unsplash API ToS, hit /download_location endpoint
to register download (see https://unsplash.com/documentation#triggering-a-download).

For internal/non-distributed use, direct URL download is fine.
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.argv = [sys.argv[0]] + sys.argv[1:] + ["--source", "unsplash"]
exec(open(HERE.parent / "_shared" / "download_url.py").read(), {"__name__": "__main__"})
