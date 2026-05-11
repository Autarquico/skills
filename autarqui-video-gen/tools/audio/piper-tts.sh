#!/usr/bin/env bash
# piper-tts — local TTS via Piper. Free, fast, robotic-but-acceptable.
#
# Usage:
#   piper-tts.sh <lang> <text> <output.wav> [--voice <voice_id>]
#   piper-tts.sh es "Tu negocio sabe más" /tmp/out.wav
#   piper-tts.sh en "Hello world" /tmp/out.wav --voice en_US-amy-medium
#
# Voices auto-download to ~/.claude/skills/autarqui-video-gen/cache/models/piper/

set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <lang:es|en> <text> <output.wav> [--voice <voice_id>]"
  exit 1
fi

LANG="$1"; TEXT="$2"; OUT="$3"; shift 3

VOICE=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --voice) VOICE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# Default voices per language (Piper has many; pick one decent quality default)
if [ -z "$VOICE" ]; then
  case "$LANG" in
    es) VOICE="es_ES-davefx-medium" ;;
    en) VOICE="en_US-amy-medium" ;;
    *)  echo "No default voice for lang '$LANG'. Pass --voice."; exit 1 ;;
  esac
fi

MODELS_DIR="$HOME/.claude/skills/autarqui-video-gen/cache/models/piper"
mkdir -p "$MODELS_DIR"

MODEL_PATH="$MODELS_DIR/$VOICE.onnx"
CONFIG_PATH="$MODELS_DIR/$VOICE.onnx.json"

# Download if missing — Piper hosts voices on Hugging Face
if [ ! -f "$MODEL_PATH" ] || [ ! -f "$CONFIG_PATH" ]; then
  echo "==> Downloading Piper voice: $VOICE"
  # Voice IDs are like "es_ES-davefx-medium" → URL parts: es/es_ES/davefx/medium/
  IFS='-' read -r LOCALE NAME QUALITY <<< "$VOICE"
  COUNTRY="${LOCALE%_*}"  # "es_ES" → "es"
  BASE="https://huggingface.co/rhasspy/piper-voices/resolve/main/${COUNTRY}/${LOCALE}/${NAME}/${QUALITY}"

  curl -sSL -o "$MODEL_PATH" "$BASE/${VOICE}.onnx" || {
    echo "ERROR: failed to download $BASE/${VOICE}.onnx"
    rm -f "$MODEL_PATH"
    exit 1
  }
  curl -sSL -o "$CONFIG_PATH" "$BASE/${VOICE}.onnx.json" || {
    echo "ERROR: failed to download $BASE/${VOICE}.onnx.json"
    rm -f "$CONFIG_PATH"
    exit 1
  }
  echo "    Cached at $MODELS_DIR"
fi

# Verify piper installed
if ! command -v piper &>/dev/null; then
  echo "ERROR: 'piper' CLI not installed."
  echo "  Install: pip install piper-tts"
  exit 1
fi

# Synthesize
mkdir -p "$(dirname "$OUT")"
echo "$TEXT" | piper --model "$MODEL_PATH" --output_file "$OUT" 2>/dev/null

if [ -f "$OUT" ]; then
  echo "OK: $OUT"
else
  echo "ERROR: synthesis failed"
  exit 1
fi
