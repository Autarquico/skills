#!/usr/bin/env python3
"""pm_spec_new — crea una spec en docs/specs/<slug>.md desde el template.

Usage:
    pm_spec_new.py <slug> [--title TITLE] [--type TYPE] [--priority P] [--size S] [--dry-run]

Exit codes:
    0  success
    1  error (slug existe, config inválido, template no encontrado)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    banner, die, find_pm_root, fill_template, load_config, log, ok,
    slug_to_title, today,
)


VALID_TYPES = ("task", "epic", "adr", "bug")
VALID_PRIORITIES = ("P0", "P1", "P2")
VALID_SIZES = ("XS", "S", "M", "L", "XL")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug", help="Slug del fichero (kebab-case), p.ej. auth-refactor")
    ap.add_argument("--title", help="Título; por defecto deriva del slug")
    ap.add_argument("--type", choices=VALID_TYPES, default="task")
    ap.add_argument("--priority", choices=VALID_PRIORITIES, default="P1")
    ap.add_argument("--size", choices=VALID_SIZES, default="M")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")

    specs_dir = pm_root / cfg["paths"]["specs"]
    target = specs_dir / f"{args.slug}.md"

    banner(f"/pm spec new — {args.slug}")

    if target.exists():
        die(f"Ya existe: {target}")

    title = args.title or slug_to_title(args.slug)

    # Template
    skill_dir = Path(__file__).resolve().parent.parent
    template_path = skill_dir / "assets" / "templates" / "spec.md"
    if not template_path.is_file():
        die(f"Template no encontrado: {template_path}")
    template = template_path.read_text(encoding="utf-8")

    content = fill_template(template, {
        "codename": cfg["codename"],
        "title": title,
        "today": today(),
    })

    # Aplicar overrides en frontmatter (sustitución simple line-based)
    lines = content.splitlines()
    overrides = {"type": args.type, "priority": args.priority, "size": args.size}
    for i, ln in enumerate(lines):
        for key, val in overrides.items():
            if ln.startswith(f"{key}:"):
                lines[i] = f"{key}: {val}"
    content = "\n".join(lines) + ("\n" if not content.endswith("\n") else "")

    log(f"codename: {cfg['codename']}")
    log(f"title:    {title}")
    log(f"type:     {args.type}")
    log(f"status:   draft")
    log(f"priority: {args.priority}")
    log(f"size:     {args.size}")
    log(f"target:   {target.relative_to(pm_root)}")

    if args.dry_run:
        ok("DRY-RUN: no se ha creado nada.")
        return

    specs_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    ok(f"Creada: {target.relative_to(pm_root)}")
    log(f"Siguiente: /pm spec to-issue {args.slug}")


if __name__ == "__main__":
    main()
