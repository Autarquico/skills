#!/usr/bin/env bash
# manim-runner — invoke Manim CE to render educational animations to MP4.
# The output MP4 can then be imported into a Remotion composition with <Video>.
#
# Usage:
#   manim-runner.sh <scene_file.py> <SceneClassName> <output.mp4> [--quality h|l|m] [--bg "#ffffff"]
#
# Example scene_file.py:
#   from manim import *
#   class MyScene(Scene):
#       def construct(self):
#           text = Text("Delta", font="Lora").scale(3)
#           self.play(Write(text))
#           self.wait(2)
#
# Quality flags map to Manim's: l=480p, m=720p, h=1080p (default), p=1440p, k=2160p.

set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <scene_file.py> <SceneClassName> <output.mp4> [--quality h] [--bg \"#ffffff\"]"
  exit 1
fi

SCENE_FILE="$1"; CLASS_NAME="$2"; OUTPUT="$3"; shift 3

QUALITY="h"
BG_COLOR="#ffffff"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --quality) QUALITY="$2"; shift 2 ;;
    --bg)      BG_COLOR="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if ! command -v manim &>/dev/null; then
  echo "ERROR: 'manim' CLI not installed."
  echo "  Install: pip install manim"
  echo "  See https://docs.manim.community/en/stable/installation.html for system deps (cairo, pango, ffmpeg)."
  exit 1
fi

# Manim renders to media/videos/<filename>/<quality>/<ClassName>.mp4 by default.
# Use --output_file to control the filename, but it still goes under media/.
WORK_DIR="$(mktemp -d)"
trap "rm -rf '$WORK_DIR'" EXIT

manim \
  -q"$QUALITY" \
  --media_dir "$WORK_DIR" \
  --output_file "out" \
  --background_color "$BG_COLOR" \
  "$SCENE_FILE" "$CLASS_NAME"

# Find the produced MP4 in WORK_DIR (path varies by quality + scene name)
PRODUCED=$(find "$WORK_DIR" -name "out.mp4" -type f | head -1)
if [ -z "$PRODUCED" ]; then
  echo "ERROR: Manim did not produce expected MP4. Check above output."
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT")"
cp "$PRODUCED" "$OUTPUT"
echo "OK: $OUTPUT"
