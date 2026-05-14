#!/usr/bin/env bash
# whisper-cpp — local transcription with word-level timestamps.
#
# Usage:
#   whisper-cpp.sh <audio.wav> <output.json> [--lang es] [--model base]
#
# Models auto-download to ~/.claude/skills/autarqui-video-gen/cache/models/whisper/
# Options: tiny | base | small | medium | large-v3
# Output: Whisper.cpp JSON with segment + word timing.

set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <audio.wav> <output.json> [--lang es] [--model base]"
  exit 1
fi

AUDIO="$1"; OUT="$2"; shift 2

LANG="auto"
MODEL="base"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --lang) LANG="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# whisper-cli is the binary name from the brew formula whisper-cpp
if ! command -v whisper-cli &>/dev/null; then
  echo "ERROR: 'whisper-cli' not installed."
  echo "  macOS: brew install whisper-cpp"
  echo "  Other: build from https://github.com/ggml-org/whisper.cpp"
  exit 1
fi

MODELS_DIR="$HOME/.claude/skills/autarqui-video-gen/cache/models/whisper"
mkdir -p "$MODELS_DIR"

MODEL_PATH="$MODELS_DIR/ggml-${MODEL}.bin"

if [ ! -f "$MODEL_PATH" ]; then
  echo "==> Downloading Whisper model: $MODEL"
  curl -sSL -o "$MODEL_PATH" "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-${MODEL}.bin" || {
    echo "ERROR: failed to download Whisper model"
    rm -f "$MODEL_PATH"
    exit 1
  }
  echo "    Cached at $MODEL_PATH"
fi

# Whisper.cpp wants 16kHz mono WAV. Convert if needed.
TMP_WAV="$(mktemp -u).wav"
ffmpeg -y -i "$AUDIO" -ar 16000 -ac 1 -f wav "$TMP_WAV" 2>/dev/null

# Run with output-json + word timestamps
mkdir -p "$(dirname "$OUT")"
TMP_BASE="$(dirname "$OUT")/$(basename "$OUT" .json)"

whisper-cli \
  -m "$MODEL_PATH" \
  -l "$LANG" \
  -ml 1 \
  -of "$TMP_BASE" \
  -oj \
  "$TMP_WAV" \
  >/dev/null 2>&1

# Whisper writes ${TMP_BASE}.json
mv "${TMP_BASE}.json" "$OUT"
rm -f "$TMP_WAV"

echo "OK: $OUT"
