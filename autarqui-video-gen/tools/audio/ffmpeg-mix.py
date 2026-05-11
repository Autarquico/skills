#!/usr/bin/env python3
"""
ffmpeg-mix — opinionated audio mixing presets for the skill.

Subcommands:
  voice-over-music — mix narration on top of music with sidechain ducking
  music-curve      — apply editorial/punchy/cinematic volume curve to a track
  master           — final mastering pass (loudness normalization to -14 LUFS)
  trim-tail-to     — trim the START of a track so its END lands at duration N
                     (matches the lib/audio.ts trimBefore approach)

Examples:
  ffmpeg-mix.py voice-over-music \\
    --voice voice.wav --music music.mp3 --out mixed.mp3 \\
    --music-volume 0.35 --duck-amount 12

  ffmpeg-mix.py music-curve \\
    --in music.mp3 --out music-shaped.mp3 \\
    --preset editorial --total-duration 60 --fade-in-duration 2

  ffmpeg-mix.py trim-tail-to \\
    --in music.mp3 --out music-trimmed.mp3 --target-duration 35.4
"""

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], dry: bool = False) -> None:
    print("$ " + " ".join(shlex.quote(c) for c in cmd), file=sys.stderr)
    if not dry:
        subprocess.run(cmd, check=True)


def ffprobe_duration(path: str) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            path,
        ]
    )
    return float(out.decode().strip())


# ---------------------------------------------------------------------------
# voice-over-music
# ---------------------------------------------------------------------------

def voice_over_music(args):
    """
    Mix voice on top of music with sidechain compression so the music ducks
    when voice is present. Output is single mp3.
    """
    voice = args.voice
    music = args.music
    out = args.out
    music_vol = args.music_volume
    duck_db = args.duck_amount

    # ffmpeg filter_complex:
    # - amix the voice (full vol) with music (reduced vol)
    # - sidechaincompress: music ducks based on voice envelope
    fc = (
        f"[1:a]volume={music_vol}[bg];"
        f"[bg][0:a]sidechaincompress=threshold=0.05:ratio=8:attack=200:release=800:level_in=1:level_sc=1:makeup={-duck_db/2}[bgduck];"
        f"[0:a][bgduck]amix=inputs=2:duration=longest:dropout_transition=0[mix]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", voice,
        "-i", music,
        "-filter_complex", fc,
        "-map", "[mix]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        out,
    ]
    run(cmd, args.dry)


# ---------------------------------------------------------------------------
# music-curve
# ---------------------------------------------------------------------------

def music_curve(args):
    """
    Apply a volume envelope to a track. Used to shape music across a video's
    duration without doing it in Remotion (useful for pre-rendered audio bed).
    """
    preset = args.preset
    total = args.total_duration
    fade_in = args.fade_in_duration
    fade_out = args.fade_out_duration

    # afade filter for in/out
    filters = []
    filters.append(f"afade=t=in:st=0:d={fade_in}")
    filters.append(f"afade=t=out:st={total - fade_out}:d={fade_out}")

    # Adjust based on preset (editorial/punchy/cinematic just tweak the curves)
    if preset == "punchy":
        # Faster attack, faster decay
        filters[0] = f"afade=t=in:st=0:d={min(fade_in, 1.0)}:curve=ipar"
        filters[1] = f"afade=t=out:st={total - 0.3}:d=0.3:curve=ipar"
    elif preset == "cinematic":
        # Quadratic crescendo, slow tail
        filters[0] = f"afade=t=in:st=0:d={fade_in}:curve=qsin"
        filters[1] = f"afade=t=out:st={total - fade_out}:d={fade_out}:curve=ihsin"

    fc = ",".join(filters)
    cmd = [
        "ffmpeg", "-y",
        "-i", args.in_path,
        "-af", fc,
        "-t", str(total),
        "-c:a", "libmp3lame", "-b:a", "192k",
        args.out,
    ]
    run(cmd, args.dry)


# ---------------------------------------------------------------------------
# master
# ---------------------------------------------------------------------------

def master(args):
    """Final loudness normalization to -14 LUFS (standard for streaming)."""
    cmd = [
        "ffmpeg", "-y",
        "-i", args.in_path,
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-ar", "44100",
        "-c:a", "libmp3lame", "-b:a", "192k",
        args.out,
    ]
    run(cmd, args.dry)


# ---------------------------------------------------------------------------
# trim-tail-to
# ---------------------------------------------------------------------------

def trim_tail_to(args):
    """
    Trim the START of a track so its END is preserved and total duration
    matches `target_duration`. Useful for end-of-track-aligned video music.
    """
    src_dur = ffprobe_duration(args.in_path)
    if args.target_duration >= src_dur:
        print(f"WARN: target {args.target_duration}s >= source {src_dur}s — no trim needed.", file=sys.stderr)
        cmd = ["cp", args.in_path, args.out]
        run(cmd, args.dry)
        return

    skip_s = src_dur - args.target_duration
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{skip_s:.3f}",
        "-i", args.in_path,
        "-c:a", "libmp3lame", "-b:a", "192k",
        args.out,
    ]
    run(cmd, args.dry)
    print(f"OK: skipped {skip_s:.3f}s, output is {args.target_duration}s", file=sys.stderr)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="ffmpeg-mix presets")
    p.add_argument("--dry", action="store_true", help="Print commands, don't run")
    sub = p.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("voice-over-music")
    pv.add_argument("--voice", required=True)
    pv.add_argument("--music", required=True)
    pv.add_argument("--out", required=True)
    pv.add_argument("--music-volume", type=float, default=0.35)
    pv.add_argument("--duck-amount", type=float, default=12.0, help="dB of ducking when voice present")
    pv.set_defaults(func=voice_over_music)

    pm = sub.add_parser("music-curve")
    pm.add_argument("--in", dest="in_path", required=True)
    pm.add_argument("--out", required=True)
    pm.add_argument(
        "--preset",
        choices=["editorial", "punchy", "cinematic"],
        default="editorial",
    )
    pm.add_argument("--total-duration", type=float, required=True)
    pm.add_argument("--fade-in-duration", type=float, default=2.0)
    pm.add_argument("--fade-out-duration", type=float, default=3.0)
    pm.set_defaults(func=music_curve)

    pma = sub.add_parser("master")
    pma.add_argument("--in", dest="in_path", required=True)
    pma.add_argument("--out", required=True)
    pma.set_defaults(func=master)

    pt = sub.add_parser("trim-tail-to")
    pt.add_argument("--in", dest="in_path", required=True)
    pt.add_argument("--out", required=True)
    pt.add_argument("--target-duration", type=float, required=True)
    pt.set_defaults(func=trim_tail_to)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
