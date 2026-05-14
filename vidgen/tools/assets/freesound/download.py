#!/usr/bin/env python3
"""Freesound download. Use the preview URL from search.py results
(higher-quality 'download' field requires OAuth, not just API key).
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.argv = [sys.argv[0]] + sys.argv[1:] + ["--source", "freesound"]
exec(open(HERE.parent / "_shared" / "download_url.py").read(), {"__name__": "__main__"})
