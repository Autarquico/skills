#!/usr/bin/env bash
# demucs-stems — separate an audio track into vocals/drums/bass/other.
# Useful when you want to remove vocals from a Pixabay track, or use just the
# drums for a punchy intro.
#
# Usage:
#   demucs-stems.sh <input.mp3> [output_dir]
#
# Default output_dir: same dir as input, subfolder "<basename>_stems/"
# Outputs: vocals.wav, drums.wav, bass.wav, other.wav

set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <input.mp3> [output_dir]"
  exit 1
fi

INPUT="$1"
OUT_DIR="${2:-$(dirname "$INPUT")/$(basename "$INPUT" .mp3)_stems}"

if ! command -v demucs &>/dev/null; then
  echo "ERROR: 'demucs' not installed."
  echo "  Install: pip install demucs"
  exit 1
fi

mkdir -p "$OUT_DIR"

# htdemucs is the default high-quality model (~500MB, downloads on first use)
echo "==> Separating stems with htdemucs (this takes 30-60s for a 3min track)…"
demucs --out "$OUT_DIR" --model htdemucs "$INPUT"

# demucs writes to <out>/htdemucs/<basename>/{vocals,drums,bass,other}.wav
# Flatten that
ACTUAL_DIR="$OUT_DIR/htdemucs/$(basename "$INPUT" | sed 's/\.[^.]*$//')"
if [ -d "$ACTUAL_DIR" ]; then
  mv "$ACTUAL_DIR"/*.wav "$OUT_DIR/"
  rm -rf "$OUT_DIR/htdemucs"
fi

echo "OK. Stems at: $OUT_DIR"
ls "$OUT_DIR"
