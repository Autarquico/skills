#!/usr/bin/env python3
"""pm_spec_adopt — convierte markdown genérico en spec formal del sistema PM.

Heurísticas para inferir type/priority/size/title del fuente. Interactivo por
defecto: propone, el usuario confirma o edita.

Usage:
    pm_spec_adopt.py <source.md> [--slug SLUG] [--yes] [--keep-original]
                                  [--force] [--dry-run]

Exit codes: 0 ok, 1 error.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    banner, confirm, die, find_pm_root, load_config, log, ok,
    slug_to_title, today, warn, yaml_dumps,
)


# Heurísticas

PRIORITY_KEYWORDS = {
    "P0": ["urgente", "crítico", "critico", "bloqueante", "blocker", "critical", "urgent"],
    "P1": ["importante", "prioritario", "important", "high priority"],
    "P2": ["nice to have", "nice-to-have", "low priority", "opcional"],
}

# Map common source headings → template sections
SECTION_MAP = [
    (re.compile(r"^#+\s*(por qu[eé]|context[oa]|background|motivaci[oó]n|why)", re.I), "Contexto"),
    (re.compile(r"^#+\s*(qu[eé] decid|decisiones?|decisions?)", re.I), "Decisiones tomadas"),
    (re.compile(r"^#+\s*(scope|alcance|qu[eé] incluye|incluye|in scope)", re.I), "Scope"),
    (re.compile(r"^#+\s*(criterios?|acceptance|definition of done|dod|done)", re.I), "Criterios de aceptación"),
    (re.compile(r"^#+\s*(stack|t[eé]cnic|technical|notas?)", re.I), "Notas técnicas"),
    (re.compile(r"^#+\s*(referencias?|references?|links?)", re.I), "Referencias"),
]


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text or "spec"


def split_sections(md: str) -> list[tuple[str, str]]:
    """Split markdown by H2/H3 headings. Returns [(heading, body), ...]."""
    lines = md.splitlines()
    sections: list[tuple[str, list[str]]] = []
    current_h = ""
    current_body: list[str] = []
    for ln in lines:
        if re.match(r"^#{2,3}\s+", ln):
            sections.append((current_h, current_body))
            current_h = ln
            current_body = []
        else:
            current_body.append(ln)
    sections.append((current_h, current_body))
    return [(h, "\n".join(b).strip()) for h, b in sections if h or "\n".join(b).strip()]


def infer_title(source: str, fallback: str) -> str:
    for ln in source.splitlines():
        m = re.match(r"^#\s+(.+)$", ln)
        if m:
            return m.group(1).strip()
    return slug_to_title(fallback)


def infer_priority(text: str) -> str:
    low = text.lower()
    for prio, words in PRIORITY_KEYWORDS.items():
        if any(w in low for w in words):
            return prio
    return "P1"


def infer_type(sections: list[tuple[str, str]]) -> str:
    # epic if many sub-headings or long checklist
    n_sub = sum(1 for h, _ in sections if h.startswith("### "))
    checklist = sum(text.count("- [ ]") for _, text in sections)
    if n_sub >= 4 or checklist >= 8:
        return "epic"
    return "task"


def infer_size(source: str, n_criteria: int) -> str:
    n_lines = len(source.splitlines())
    if n_lines > 400 or n_criteria > 10:
        return "XL"
    if n_lines > 200 or n_criteria > 6:
        return "L"
    if n_lines > 80 or n_criteria > 3:
        return "M"
    return "S"


def map_sections(sections: list[tuple[str, str]]) -> tuple[dict[str, str], list[tuple[str, str]]]:
    """Returns (mapped: template_section -> body, unmapped: list)."""
    mapped: dict[str, str] = {}
    unmapped: list[tuple[str, str]] = []
    for h, body in sections:
        target = None
        for rx, dest in SECTION_MAP:
            if rx.search(h):
                target = dest
                break
        if target:
            if target in mapped:
                mapped[target] += "\n\n" + body
            else:
                mapped[target] = body
        else:
            if h:
                unmapped.append((h, body))
    return mapped, unmapped


def build_body(title: str, mapped: dict[str, str], unmapped: list[tuple[str, str]]) -> str:
    parts = [f"# {title}", ""]
    for sec in ["Contexto", "Decisiones tomadas", "Scope",
                "Criterios de aceptación", "Notas técnicas", "Referencias"]:
        parts.append(f"## {sec}")
        parts.append("")
        body = mapped.get(sec, "").strip()
        if body:
            parts.append(body)
        elif sec == "Criterios de aceptación":
            parts.append("- [ ] _Pendiente de definir — no extraído del fuente_")
        else:
            parts.append("_Sin contenido extraído del fuente._")
        parts.append("")
    if unmapped:
        parts.append("## Notas adicionales")
        parts.append("")
        for h, b in unmapped:
            parts.append(h)
            parts.append("")
            if b:
                parts.append(b)
                parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", help="Fichero markdown a adoptar")
    ap.add_argument("--slug", help="Slug destino (default: derivado del título)")
    ap.add_argument("--title", help="Override título")
    ap.add_argument("--type", choices=["task", "epic"], help="Override tipo")
    ap.add_argument("--priority", choices=["P0", "P1", "P2"], help="Override prioridad")
    ap.add_argument("--size", choices=["XS", "S", "M", "L", "XL"], help="Override tamaño")
    ap.add_argument("--yes", action="store_true", help="Acepta heurísticas sin confirmación")
    ap.add_argument("--keep-original", action="store_true")
    ap.add_argument("--force", action="store_true", help="Sobrescribe si el slug existe")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")

    source_path = Path(args.source)
    if not source_path.is_file():
        die(f"Fichero no encontrado: {source_path}")
    source = source_path.read_text(encoding="utf-8")

    sections = split_sections(source)
    title = args.title or infer_title(source, source_path.stem)
    slug = args.slug or slugify(title)
    target = pm_root / cfg["paths"]["specs"] / f"{slug}.md"

    banner(f"/pm spec adopt — {source_path.name}")

    if target.exists() and not args.force:
        die(f"Ya existe: {target.relative_to(pm_root)} (usa --force o --slug otro)")

    sec_type = args.type or infer_type(sections)
    sec_priority = args.priority or infer_priority(source)
    n_criteria = source.count("- [ ]")
    sec_size = args.size or infer_size(source, n_criteria)

    mapped, unmapped = map_sections(sections)

    log("Propuesta:")
    log(f"  slug      {slug}")
    log(f"  title     {title}")
    log(f"  type      {sec_type}")
    log(f"  priority  {sec_priority}")
    log(f"  size      {sec_size}")
    log("Mapeo:")
    for sec, body in mapped.items():
        log(f"  ✓ {sec} ({len(body.splitlines())} líneas)")
    for sec in ["Contexto", "Decisiones tomadas", "Scope",
                "Criterios de aceptación", "Notas técnicas", "Referencias"]:
        if sec not in mapped:
            log(f"  ✗ {sec} (sin mapeo del fuente)")
    if unmapped:
        log(f"  → {len(unmapped)} secciones extras irán a 'Notas adicionales'")

    if not args.yes and not args.dry_run:
        if not confirm("¿Aplicar?"):
            die("abortado por el usuario", code=0)

    fm = {
        "codename": cfg["codename"],
        "title": title,
        "type": sec_type,
        "status": "draft",
        "priority": sec_priority,
        "size": sec_size,
        "related_issues": [],
        "depends_on": [],
        "supersedes": [],
        "related_specs": [],
        "created": today(),
        "updated": today(),
    }
    body = build_body(title, mapped, unmapped)
    content = f"---\n{yaml_dumps(fm)}\n---\n\n{body}"

    if args.dry_run:
        ok("DRY-RUN: contenido propuesto:\n" + "-" * 60)
        print(content)
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    ok(f"creada: {target.relative_to(pm_root)}")

    if not args.keep_original:
        source_path.unlink()
        log(f"borrado fuente: {source_path}")
    else:
        log(f"fuente conservado: {source_path}")

    log(f"Siguiente: /pm spec to-issue {slug}")


if __name__ == "__main__":
    main()
