#!/usr/bin/env bash
# svg-render — convert SVG to PNG via rsvg-convert (librsvg).
#
# Usage:
#   svg-render.sh <input.svg> <output.png> [--width N] [--height N]

set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <input.svg> <output.png> [--width N] [--height N]"
  exit 1
fi

INPUT="$1"; OUTPUT="$2"; shift 2

WIDTH=""
HEIGHT=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --width)  WIDTH="$2"; shift 2 ;;
    --height) HEIGHT="$2"; shift 2 ;;
    *) echo "Unknown: $1"; exit 1 ;;
  esac
done

if ! command -v rsvg-convert &>/dev/null; then
  echo "ERROR: rsvg-convert not installed. brew install librsvg"
  exit 1
fi

ARGS=()
[ -n "$WIDTH" ] && ARGS+=(-w "$WIDTH")
[ -n "$HEIGHT" ] && ARGS+=(-h "$HEIGHT")
mkdir -p "$(dirname "$OUTPUT")"
rsvg-convert "${ARGS[@]}" -o "$OUTPUT" "$INPUT"
echo "OK: $OUTPUT"
