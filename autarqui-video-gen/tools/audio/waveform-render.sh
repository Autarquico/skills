#!/usr/bin/env bash
# waveform-render — generate a static waveform PNG from an audio file via ffmpeg.
# Output is a transparent PNG with the waveform shape, usable in WaveformOverlay scene.
#
# Usage:
#   waveform-render.sh <input.mp3> <output.png> [--width 1920] [--height 240] [--color "#1a1a1a"]

set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <input.mp3> <output.png> [--width N] [--height N] [--color #hex]"
  exit 1
fi

IN="$1"; OUT="$2"; shift 2

W=1920; H=240; COLOR="0x1a1a1a"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --width)  W="$2"; shift 2 ;;
    --height) H="$2"; shift 2 ;;
    --color)
      C="${2#\#}"
      COLOR="0x$C"
      shift 2
      ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

mkdir -p "$(dirname "$OUT")"

ffmpeg -y -i "$IN" -filter_complex \
  "showwavespic=s=${W}x${H}:colors=$COLOR:split_channels=0:scale=lin" \
  -frames:v 1 "$OUT"

echo "OK: $OUT"
