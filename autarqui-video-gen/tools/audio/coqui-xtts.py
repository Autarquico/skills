#!/usr/bin/env python3
"""
coqui-xtts — high-quality multilingual TTS with optional voice cloning.

Uses Coqui XTTS-v2 (CC-BY license, free for any use as long as attribution).
Supports 17 languages + voice cloning from a 6-second reference sample.

Model auto-downloads on first use (~2GB) to ~/Library/Application Support/tts/
or platform equivalent.

Usage:
  coqui-xtts.py --text "Hola mundo" --lang es --out /tmp/out.wav
  coqui-xtts.py --text "..." --lang es --out /tmp/out.wav --reference-voice ./sample.wav

Requires: pip install TTS  (NOT piper-tts; this is Coqui's repo)
"""

import argparse
import sys
from pathlib import Path

LANGS = ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko", "hi"]


def main():
    parser = argparse.ArgumentParser(description="Coqui XTTS-v2 TTS")
    parser.add_argument("--text", required=True)
    parser.add_argument("--lang", required=True, choices=LANGS)
    parser.add_argument("--out", required=True, help="Output WAV path")
    parser.add_argument(
        "--reference-voice",
        help="Path to a 6+ second WAV/MP3 sample to clone voice from. Optional.",
    )
    parser.add_argument(
        "--speaker",
        help="Built-in speaker name (when not cloning). Default: 'Damien Black'",
        default="Damien Black",
    )
    args = parser.parse_args()

    try:
        from TTS.api import TTS
    except ImportError:
        sys.exit(
            "ERROR: TTS not installed. Install with: pip install TTS\n"
            "(Note: Coqui TTS, not piper-tts.)"
        )

    out_path = Path(args.out).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"==> Loading XTTS-v2 model (downloads ~2GB on first use)…", file=sys.stderr)
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True)

    print(f"==> Synthesizing ({args.lang})…", file=sys.stderr)
    if args.reference_voice:
        ref_path = Path(args.reference_voice).expanduser()
        if not ref_path.exists():
            sys.exit(f"ERROR: reference voice not found: {ref_path}")
        tts.tts_to_file(
            text=args.text,
            file_path=str(out_path),
            speaker_wav=str(ref_path),
            language=args.lang,
        )
    else:
        tts.tts_to_file(
            text=args.text,
            file_path=str(out_path),
            speaker=args.speaker,
            language=args.lang,
        )

    print(f"OK: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
