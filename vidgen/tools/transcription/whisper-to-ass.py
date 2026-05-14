#!/usr/bin/env python3
"""
whisper-to-ass — convert Whisper.cpp JSON output to ASS subtitle format
                 with word-level timing (karaoke-style).

Usage:
  whisper-to-ass.py <whisper.json> <output.ass> [--font Poppins] [--size 50] [--color "#1a1a1a"]

ASS format is preferred over SRT because it supports per-word highlighting
(\\k tag), styling, and is widely supported by ffmpeg subtitles burn-in.

Style maps to autarqui-video-gen brand defaults; override via flags.
"""

import argparse
import json
import sys
from pathlib import Path


def hex_to_ass(hex_color: str) -> str:
    """Convert #RRGGBB to ASS &HBBGGRR& format."""
    h = hex_color.lstrip("#")
    if len(h) == 6:
        r, g, b = h[0:2], h[2:4], h[4:6]
        return f"&H00{b}{g}{r}".upper()
    return "&H00000000"


def fmt_time(seconds: float) -> str:
    """ASS time format: H:MM:SS.cc"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("whisper_json")
    parser.add_argument("output_ass")
    parser.add_argument("--font", default="Poppins")
    parser.add_argument("--size", type=int, default=50)
    parser.add_argument("--color", default="#1a1a1a")
    parser.add_argument("--highlight-color", default="#000000")
    parser.add_argument("--bg-color", default="#ffffff")
    parser.add_argument("--bg-opacity", type=float, default=0.92, help="0..1")
    parser.add_argument(
        "--max-words-per-line",
        type=int,
        default=4,
        help="Group words into lines of N max",
    )
    parser.add_argument("--video-width", type=int, default=1080)
    parser.add_argument("--video-height", type=int, default=1920)
    args = parser.parse_args()

    with open(args.whisper_json) as f:
        data = json.load(f)

    # Whisper.cpp JSON has: { "transcription": [{"timestamps": {...}, "text": "..."}] }
    # Word-level data is in segments — we need to extract per-word timing.
    # Whisper.cpp with -ml 1 puts each word as a segment.
    segments = data.get("transcription", [])
    words = []
    for seg in segments:
        ts = seg.get("timestamps", {})
        # Whisper.cpp timestamps are in 10ms units (cs)
        from_cs = ts.get("from", 0)
        to_cs = ts.get("to", 0)
        text = seg.get("text", "").strip()
        if text:
            words.append({
                "start": from_cs / 100.0,
                "end": to_cs / 100.0,
                "text": text,
            })

    if not words:
        sys.exit("ERROR: no word-level data in input. Run whisper-cli with -ml 1.")

    # Group into lines of max-words-per-line
    lines = []
    for i in range(0, len(words), args.max_words_per_line):
        chunk = words[i : i + args.max_words_per_line]
        lines.append(chunk)

    # Build ASS
    primary = hex_to_ass(args.color)
    secondary = hex_to_ass(args.highlight_color)
    bg = hex_to_ass(args.bg_color)
    bg_alpha = int(255 * (1 - args.bg_opacity))
    back_color = f"&H{bg_alpha:02X}{bg[2:]}"

    out_lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {args.video_width}",
        f"PlayResY: {args.video_height}",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
        "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        # BorderStyle=3 = opaque box (BackColour fills behind text)
        f"Style: Default,{args.font},{args.size},{primary},{secondary},&H00000000,{back_color},"
        f"-1,0,0,0,100,100,0,0,3,4,0,2,40,40,80,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    for line in lines:
        if not line:
            continue
        start = line[0]["start"]
        end = line[-1]["end"]
        # Karaoke-style: each word highlighted as it's spoken
        text_parts = []
        for w in line:
            dur_cs = max(1, int((w["end"] - w["start"]) * 100))
            text_parts.append(f"{{\\k{dur_cs}}}{w['text']} ")
        text = "".join(text_parts).strip()
        out_lines.append(
            f"Dialogue: 0,{fmt_time(start)},{fmt_time(end)},Default,,0,0,0,,{text}"
        )

    out_path = Path(args.output_ass)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"OK: {out_path} ({len(lines)} lines, {len(words)} words)", file=sys.stderr)


if __name__ == "__main__":
    main()
