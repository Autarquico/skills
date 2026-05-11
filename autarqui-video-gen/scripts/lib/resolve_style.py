#!/usr/bin/env python3
"""
resolve_style.py — visual-style.md → TypeScript tokens.ts file.

Reads YAML frontmatter, applies same defaults as lib/tokens-node.ts, writes
a `tokens.ts` file ready to be imported by a project's Composition.tsx.

Usage:
  resolve_style.py --slug autarqui-co --to <project_dir>/tokens.ts
  resolve_style.py --slug autarqui-co --validate          # just check it parses
  resolve_style.py --list                                  # list available styles

The output TS file matches the StyleTokens interface in lib/tokens.ts.
"""

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2]
STYLES_DIR = SKILL_DIR / "styles"


def load_frontmatter(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    parts = raw.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path}: no YAML frontmatter found")
    try:
        import yaml
    except ImportError:
        sys.exit(
            "ERROR: pyyaml not installed.\n"
            "  Run: avg install --tool pyyaml\n"
            "  Or:  pip install pyyaml"
        )
    return yaml.safe_load(parts[1])


def color_by_role(cs: list, role: str) -> dict | None:
    for c in cs or []:
        if role.lower() in str(c.get("role", "")).lower():
            return c
    return None


def parse_tokens(data: dict, slug: str) -> dict:
    primary = data.get("colors", {}).get("primary") or []
    neutral = data.get("colors", {}).get("neutral") or []
    accent = data.get("colors", {}).get("accent") or []

    bg = (color_by_role(primary, "background") or {}).get("hex", "#ffffff")
    ink = (
        color_by_role(primary, "body text")
        or color_by_role(primary, "text")
        or {}
    ).get("hex", "#1a1a1a")
    heading = (color_by_role(primary, "heading") or {}).get("hex", "#000000")
    muted = (color_by_role(neutral, "muted") or color_by_role(neutral, "labels") or {}).get("hex", "#6e6e6e")
    faint = (color_by_role(neutral, "faint") or color_by_role(neutral, "tertiary") or {}).get("hex", "#9a9a9a")
    rule = (color_by_role(neutral, "rule") or color_by_role(neutral, "hairline") or {}).get("hex", "#d4d4d4")
    rule_soft = (color_by_role(neutral, "soft") or {}).get("hex", "#ebebeb")
    surface = (color_by_role(neutral, "surface") or {}).get("hex", "#fafafa")

    typo = data.get("typography", {})
    layout = data.get("layout", {})
    motion = data.get("motion", {})
    audio = data.get("audio", {})

    def font(spec, dflt):
        spec = spec or {}
        return {
            "family": spec.get("family", dflt["family"]),
            "fallback": spec.get("fallback", dflt.get("fallback", "")),
            "weights": spec.get("weights", dflt["weights"]),
            "italic_available": spec.get("italic_available", dflt.get("italic_available", False)),
        }

    return {
        "meta": {
            "name": data.get("name", slug),
            "slug": data.get("slug", slug),
            "version": data.get("version", "1.0"),
            "source_url": data.get("source_url"),
            "style_prompt_short": data.get("style_prompt_short", ""),
            "style_prompt_full": data.get("style_prompt_full", ""),
        },
        "typography": {
            "display": font(
                typo.get("display"),
                {"family": "Lora", "fallback": "Georgia, serif", "weights": [400, 500], "italic_available": True},
            ),
            "body": font(
                typo.get("body"),
                {"family": "Poppins", "fallback": "system-ui, sans-serif", "weights": [400, 500]},
            ),
            "mono": font(
                typo.get("mono"),
                {"family": "Menlo", "weights": [400]},
            ),
        },
        "colors": {
            "primary": primary,
            "accent": accent,
            "neutral": neutral,
            "bg": bg,
            "ink": ink,
            "heading": heading,
            "muted": muted,
            "faint": faint,
            "rule": rule,
            "ruleSoft": rule_soft,
            "surface": surface,
        },
        "layout": {
            "hero": {
                "font_size_px": layout.get("hero", {}).get("font_size_px", 96),
                "line_height": layout.get("hero", {}).get("line_height", 1.1),
                "letter_spacing_em": layout.get("hero", {}).get("letter_spacing_em", -0.02),
                "alignment": layout.get("hero", {}).get("alignment", "flush-left"),
                "max_width_pct": layout.get("hero", {}).get("max_width_pct", 92),
            },
            "body": {
                "font_size_px": layout.get("body", {}).get("font_size_px", 28),
                "line_height": layout.get("body", {}).get("line_height", 1.55),
            },
            "list_item": {
                "numeral_font_size_px": layout.get("list_item", {}).get("numeral_font_size_px", 38),
                "main_font_size_px": layout.get("list_item", {}).get("main_font_size_px", 78),
                "indent_pct": layout.get("list_item", {}).get("indent_pct", 8),
            },
            "master_quote": {
                "font_size_px": layout.get("master_quote", {}).get("font_size_px", 56),
                "alignment": layout.get("master_quote", {}).get("alignment", "center"),
                "has_rules": layout.get("master_quote", {}).get("has_rules", True),
            },
            "closing": {
                "logo_size_px": layout.get("closing", {}).get("logo_size_px", 320),
                "spacing_px": layout.get("closing", {}).get("spacing_px", 30),
            },
        },
        "motion": {
            "in": {
                "type": motion.get("in", {}).get("type", "fade"),
                "duration_ms": motion.get("in", {}).get("duration_ms", 900),
                "easing": motion.get("in", {}).get("easing", "ease-out-cubic"),
            },
            "out": {
                "type": motion.get("out", {}).get("type", "fade"),
                "duration_ms": motion.get("out", {}).get("duration_ms", 700),
                "easing": motion.get("out", {}).get("easing", "ease-out-cubic"),
            },
            "pacing": motion.get("pacing", "slow"),
            "transitions": motion.get("transitions", ["fade", "hold"]),
            "forbidden": motion.get("forbidden", []),
        },
        "audio": {
            "music_curve": audio.get("music_curve", "editorial"),
            "prefer_voice": audio.get("prefer_voice", "piper"),
            "voice_language": audio.get("voice_language", "es"),
        },
        "ios_chrome": data.get("ios_chrome", False),
        "forbidden": data.get("forbidden", []),
        "verbatim_lines": data.get("verbatim_lines", {}),
    }


def to_typescript(tokens: dict) -> str:
    """Render the tokens dict as a typed TypeScript const literal."""
    body = json.dumps(tokens, ensure_ascii=False, indent=2)
    # JSON strings use double quotes, which is fine for TS.
    return (
        '/**\n'
        f' * Auto-generated from styles/{tokens["meta"]["slug"]}.visual-style.md\n'
        ' * via scripts/lib/resolve_style.py — do not edit by hand.\n'
        ' */\n'
        '\n'
        'import type { StyleTokens } from "../../lib/tokens";\n'
        '\n'
        f'export const TOKENS: StyleTokens = {body} as StyleTokens;\n'
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--slug", help="Style slug (filename without .visual-style.md)")
    p.add_argument("--to", help="Output path for the generated tokens.ts")
    p.add_argument("--validate", action="store_true", help="Just validate, don't write")
    p.add_argument("--list", action="store_true", help="List available styles")
    args = p.parse_args()

    if args.list:
        for f in sorted(STYLES_DIR.glob("*.visual-style.md")):
            print(f.stem.replace(".visual-style", ""))
        return

    if not args.slug:
        sys.exit("ERROR: --slug required (or --list)")

    style_path = STYLES_DIR / f"{args.slug}.visual-style.md"
    if not style_path.exists():
        sys.exit(f"ERROR: style not found: {style_path}")

    data = load_frontmatter(style_path)
    tokens = parse_tokens(data, args.slug)

    if args.validate:
        # Sanity check
        assert tokens["colors"]["bg"], "missing background color"
        assert tokens["typography"]["display"]["family"], "missing display font"
        print(f"OK: {args.slug} parsed cleanly.")
        print(f"  display: {tokens['typography']['display']['family']}")
        print(f"  body: {tokens['typography']['body']['family']}")
        print(f"  bg: {tokens['colors']['bg']}, ink: {tokens['colors']['ink']}")
        print(f"  pacing: {tokens['motion']['pacing']}")
        return

    if not args.to:
        sys.exit("ERROR: --to required (path to write tokens.ts)")

    out = Path(args.to).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_typescript(tokens), encoding="utf-8")
    print(f"OK: wrote {out}")


if __name__ == "__main__":
    main()
