#!/usr/bin/env python3
"""
beat-detect — detect beat / downbeat / onset times in an audio file via librosa.

Outputs JSON with:
  - tempo (BPM)
  - beat_times (seconds)
  - downbeat_times (every 4th beat, approximation)
  - onset_times (perceptual onsets, useful for syncing visuals)

Usage:
  beat-detect.py <input.mp3> [--out beats.json]

Requires: pip install librosa soundfile
(install via: avg install --tool librosa  — see scripts/install.sh extras)
"""

import argparse
import json
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--out", default="-", help="Output JSON path (default stdout)")
    args = p.parse_args()

    try:
        import librosa
    except ImportError:
        sys.exit(
            "ERROR: librosa not installed.\n"
            "  Install: pip install librosa\n"
            "  Or via skill venv: ~/.claude/skills/autarqui-video-gen/.venv/bin/pip install librosa"
        )

    in_path = Path(args.input).expanduser()
    if not in_path.exists():
        sys.exit(f"ERROR: input not found: {in_path}")

    print(f"==> Loading {in_path}", file=sys.stderr)
    y, sr = librosa.load(str(in_path), mono=True)

    print("==> Beat tracking…", file=sys.stderr)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()

    # Downbeats: take every 4th beat (rough approximation in 4/4 time)
    downbeat_times = beat_times[::4]

    print("==> Onset detection…", file=sys.stderr)
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units="frames")
    onset_times = librosa.frames_to_time(onset_frames, sr=sr).tolist()

    duration = librosa.get_duration(y=y, sr=sr)

    out = {
        "input": str(in_path),
        "duration_s": float(duration),
        "tempo_bpm": float(tempo if hasattr(tempo, "__float__") else tempo[0]),
        "beat_times": [round(float(t), 4) for t in beat_times],
        "downbeat_times": [round(float(t), 4) for t in downbeat_times],
        "onset_times": [round(float(t), 4) for t in onset_times],
    }

    payload = json.dumps(out, indent=2, ensure_ascii=False)
    if args.out == "-":
        print(payload)
    else:
        Path(args.out).expanduser().write_text(payload, encoding="utf-8")
        print(f"OK: {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
