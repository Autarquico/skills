#!/usr/bin/env python3
"""Brand Inventory CRUD.

Manage the local brand inventory at ~/.banana/brands/<name>/. Each brand owns:
  - brand.yml      tokens (palette, materials, lighting, mood, banned, anchors)
  - dossier.md     editorial context for Claude
  - references/    logo + sample images (visual anchors)

Brand authoring is a hybrid wizard: this script handles file I/O and asks
the author for non-derivable fields (essence, banned). The visual analysis
(palette, materials, mood) is done by Claude reading the reference images,
not by this script.

Usage:
    brands.py list
    brands.py show NAME
    brands.py init NAME --images path1,path2,... [--essence "..."] [--ratio 4:3]
    brands.py set-default NAME
    brands.py import PATH [--name NAME]
    brands.py delete NAME --confirm

Stdlib only (no PyYAML dependency). Writes brand.yml in a strict YAML subset
that PyYAML and Claude both parse cleanly.
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

BANANA_HOME = Path.home() / ".banana"
BRANDS_DIR = BANANA_HOME / "brands"
CONFIG_PATH = BANANA_HOME / "config.yml"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _ensure_dirs():
    BRANDS_DIR.mkdir(parents=True, exist_ok=True)


def _sanitize_name(name):
    safe = re.sub(r"[^a-z0-9_\-]", "", name.lower())
    if not safe:
        print("Error: brand name must contain letters, numbers, hyphens, or underscores.", file=sys.stderr)
        sys.exit(1)
    return safe


def _brand_dir(name):
    return BRANDS_DIR / _sanitize_name(name)


# ---------- Minimal YAML reader/writer (stdlib only) ----------
# Supports: top-level scalars, nested objects (one level), lists of strings.
# Sufficient for the brand.yml schema. NOT a general YAML parser.

def _yaml_dump(data, indent=0):
    lines = []
    pad = "  " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{pad}{key}:")
            lines.append(_yaml_dump(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{pad}{key}:")
            for item in value:
                lines.append(f"{pad}  - {_yaml_scalar(item)}")
        else:
            lines.append(f"{pad}{key}: {_yaml_scalar(value)}")
    return "\n".join(filter(None, lines))


def _yaml_scalar(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if any(c in s for c in [":", "#", "\n", '"']) or s.strip() != s:
        return json.dumps(s)
    return s


def _yaml_load(text):
    """Parse the subset we emit. Returns dict."""
    data = {}
    current_key = None
    current_list = None
    current_obj = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if indent == 0:
            current_obj = None
            if stripped.endswith(":"):
                current_key = stripped[:-1].strip()
                data[current_key] = None
                current_list = None
            else:
                k, _, v = stripped.partition(":")
                data[k.strip()] = _parse_scalar(v.strip())
                current_key = k.strip()
                current_list = None
        elif indent == 2:
            if stripped.startswith("- "):
                item = _parse_scalar(stripped[2:].strip())
                if not isinstance(data.get(current_key), list):
                    data[current_key] = []
                data[current_key].append(item)
                current_list = data[current_key]
            else:
                # nested object key
                if not isinstance(data.get(current_key), dict):
                    data[current_key] = {}
                k, _, v = stripped.partition(":")
                data[current_key][k.strip()] = _parse_scalar(v.strip())
    return data


def _parse_scalar(s):
    if s == "" or s == "null":
        return None
    if s == "true":
        return True
    if s == "false":
        return False
    if s.startswith('"') and s.endswith('"'):
        return json.loads(s)
    return s


# ---------- Commands ----------

def cmd_list(args):
    _ensure_dirs()
    brands = sorted(p for p in BRANDS_DIR.iterdir() if p.is_dir())
    if not brands:
        print("No brands found. Create one with: brands.py init NAME --images path1,path2")
        return
    default = _read_default()
    print(f"Brands ({len(brands)}):")
    for b in brands:
        marker = " *" if b.name == default else "  "
        essence = ""
        bf = b / "brand.yml"
        if bf.exists():
            try:
                y = _yaml_load(bf.read_text())
                essence = y.get("essence") or ""
            except Exception:
                essence = "(invalid brand.yml)"
        print(f"{marker} {b.name:20s} -- {essence}")
    print("\n* = default brand")


def cmd_show(args):
    bd = _brand_dir(args.name)
    if not bd.exists():
        print(f"Error: brand '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    bf = bd / "brand.yml"
    if bf.exists():
        print(f"=== {bf} ===")
        print(bf.read_text())
    df = bd / "dossier.md"
    if df.exists():
        print(f"\n=== {df} ===")
        print(df.read_text())
    refs = bd / "references"
    if refs.exists():
        files = sorted(p.name for p in refs.iterdir() if p.is_file())
        print(f"\n=== references ({len(files)}) ===")
        for f in files:
            print(f"  {f}")


def cmd_init(args):
    _ensure_dirs()
    bd = _brand_dir(args.name)
    if bd.exists():
        print(f"Error: brand '{args.name}' already exists at {bd}", file=sys.stderr)
        sys.exit(1)

    # Stage reference images
    ref_paths = []
    if args.images:
        ref_paths = [Path(p.strip()).expanduser().resolve() for p in args.images.split(",") if p.strip()]
        for p in ref_paths:
            if not p.exists():
                print(f"Error: reference image not found: {p}", file=sys.stderr)
                sys.exit(1)
            if p.suffix.lower() not in IMAGE_EXTS:
                print(f"Warning: '{p}' does not look like an image (suffix {p.suffix}); copying anyway.", file=sys.stderr)

    bd.mkdir(parents=True)
    refs_dir = bd / "references"
    refs_dir.mkdir()
    copied = []
    for p in ref_paths:
        dest = refs_dir / p.name
        shutil.copy2(p, dest)
        copied.append(p.name)

    brand = {
        "name": _sanitize_name(args.name),
        "essence": args.essence or "TODO: one defensive sentence about what this brand stands for.",
        "colors": [],
        "typography": {"headline": "", "body": ""},
        "materials": [],
        "lighting": "",
        "mood": "",
        "positive_anchors": [],
        "banned": [],
        "default_ratio": args.ratio or "1:1",
        "default_resolution": args.resolution or "2K",
        "reference_images": copied,
    }

    (bd / "brand.yml").write_text(_yaml_dump(brand) + "\n")

    dossier = f"""# {brand['name']} -- brand dossier

> {brand['essence']}

## Visual system

(To fill in: geometry, color, typography, composition, material principles.)

## Aesthetic references

(To fill in: brands, magazines, designers, art movements that anchor the style.)

## Tone principles

(To fill in: 4–6 single-word principles that should be felt in every image.)

## Hard rules for image generation

ALWAYS:
- (To fill in.)

NEVER:
- (To fill in. These also live in brand.yml `banned` for programmatic use.)
"""
    (bd / "dossier.md").write_text(dossier)

    print(f"Brand '{brand['name']}' scaffolded at {bd}")
    print(f"  - {len(copied)} reference image(s) copied")
    print()
    print("Next steps (hybrid wizard, conversational with Claude):")
    print(f"  1. Ask Claude to read the images in {refs_dir} and propose")
    print(f"     palette (hex), materials, lighting, mood for brand.yml.")
    print(f"  2. Confirm the essence sentence and any banned tokens.")
    print(f"  3. Fill in dossier.md with editorial context.")
    print(f"  4. (optional) brands.py set-default {brand['name']}")


def cmd_delete(args):
    if not args.confirm:
        print("Error: pass --confirm to delete the brand.", file=sys.stderr)
        sys.exit(1)
    bd = _brand_dir(args.name)
    if not bd.exists():
        print(f"Error: brand '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    shutil.rmtree(bd)
    if _read_default() == _sanitize_name(args.name):
        _write_default(None)
        print(f"Note: default_brand was '{args.name}'; cleared.")
    print(f"Brand '{args.name}' deleted.")


def cmd_set_default(args):
    _ensure_dirs()
    if args.name.lower() in {"none", "null", ""}:
        _write_default(None)
        print("default_brand cleared.")
        return
    bd = _brand_dir(args.name)
    if not bd.exists():
        print(f"Error: brand '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    _write_default(_sanitize_name(args.name))
    print(f"default_brand set to '{args.name}'.")


def cmd_import(args):
    _ensure_dirs()
    src = Path(args.path).expanduser().resolve()
    if not src.is_dir():
        print(f"Error: source is not a directory: {src}", file=sys.stderr)
        sys.exit(1)
    src_brand_yml = src / "brand.yml"
    if not src_brand_yml.exists():
        print(f"Error: source folder has no brand.yml: {src}", file=sys.stderr)
        sys.exit(1)

    name = args.name or src.name
    bd = _brand_dir(name)
    if bd.exists():
        print(f"Error: brand '{name}' already exists at {bd}", file=sys.stderr)
        sys.exit(1)
    shutil.copytree(src, bd)
    print(f"Brand imported as '{_sanitize_name(name)}' at {bd}")


def _read_default():
    if not CONFIG_PATH.exists():
        return None
    try:
        cfg = _yaml_load(CONFIG_PATH.read_text())
        return cfg.get("default_brand")
    except Exception:
        return None


def _write_default(name):
    _ensure_dirs()
    cfg = {}
    if CONFIG_PATH.exists():
        try:
            cfg = _yaml_load(CONFIG_PATH.read_text()) or {}
        except Exception:
            cfg = {}
    cfg["default_brand"] = name
    CONFIG_PATH.write_text(_yaml_dump(cfg) + "\n")


# Public helper for generate.py / edit.py
def load_brand(name):
    """Load a brand by name. Returns dict with absolute reference_image paths,
    or None if the brand does not exist."""
    bd = _brand_dir(name)
    bf = bd / "brand.yml"
    if not bf.exists():
        return None
    brand = _yaml_load(bf.read_text())
    refs = brand.get("reference_images") or []
    abs_refs = [str((bd / "references" / r).resolve()) for r in refs]
    brand["reference_images_abs"] = [p for p in abs_refs if Path(p).exists()]
    brand["_dir"] = str(bd)
    return brand


def resolve_default():
    return _read_default()


def main():
    parser = argparse.ArgumentParser(description="Brand inventory CRUD")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List brands")

    p = sub.add_parser("show", help="Show brand details")
    p.add_argument("name")

    p = sub.add_parser("init", help="Scaffold a new brand from reference images")
    p.add_argument("name")
    p.add_argument("--images", default="", help="Comma-separated image paths")
    p.add_argument("--essence", default="", help="Defensive one-line essence")
    p.add_argument("--ratio", default="", help="Default aspect ratio")
    p.add_argument("--resolution", default="", help="Default resolution")

    p = sub.add_parser("delete", help="Delete a brand")
    p.add_argument("name")
    p.add_argument("--confirm", action="store_true")

    p = sub.add_parser("set-default", help="Set the default brand (use 'none' to clear)")
    p.add_argument("name")

    p = sub.add_parser("import", help="Import a brand folder into the inventory")
    p.add_argument("path", help="Path to a folder containing brand.yml")
    p.add_argument("--name", default="", help="Override the slug (defaults to folder name)")

    args = parser.parse_args()
    cmds = {
        "list": cmd_list,
        "show": cmd_show,
        "init": cmd_init,
        "delete": cmd_delete,
        "set-default": cmd_set_default,
        "import": cmd_import,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
