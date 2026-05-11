#!/usr/bin/env python3
"""Pexels download wrapper. Pass --url from search.py results."""
import os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.argv = [sys.argv[0]] + sys.argv[1:] + ["--source", "pexels"]
exec(open(HERE.parent / "_shared" / "download_url.py").read(), {"__name__": "__main__"})
