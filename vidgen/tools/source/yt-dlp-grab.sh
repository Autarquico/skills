#!/usr/bin/env bash
# yt-dlp-grab — download video/audio from YouTube + 1000 sites.
# ONLY use for content you have rights to (your own channel, CC, etc.).
#
# Usage:
#   yt-dlp-grab.sh <url> <output_dir> [--audio-only] [--format <fmt>]

set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <url> <output_dir> [--audio-only] [--format mp4|webm|...]"
  exit 1
fi

URL="$1"; OUT_DIR="$2"; shift 2

AUDIO_ONLY=0
FORMAT="mp4"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --audio-only) AUDIO_ONLY=1; shift ;;
    --format)     FORMAT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

if ! command -v yt-dlp &>/dev/null; then
  echo "ERROR: yt-dlp not installed. Install: pip install yt-dlp"
  exit 1
fi

mkdir -p "$OUT_DIR"
cd "$OUT_DIR"

if [ "$AUDIO_ONLY" -eq 1 ]; then
  yt-dlp -x --audio-format mp3 -o "%(title)s.%(ext)s" "$URL"
else
  yt-dlp -f "bestvideo[ext=$FORMAT]+bestaudio[ext=m4a]/best[ext=$FORMAT]/best" -o "%(title)s.%(ext)s" "$URL"
fi
