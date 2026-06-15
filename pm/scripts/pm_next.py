#!/usr/bin/env python3
"""pm_next — analizador del backlog y proposer de "qué toca ahora".

Read-only. Combina 4 fuentes (specs activas sin PR, specs draft, board
con spec, board sin spec), aplica ranking lexicográfico según preset,
reporta inconsistencias por separado.

Usage:
    pm_next.py                       # markdown, wip-first, top 5
    pm_next.py --top 10
    pm_next.py --json                # JSON estructurado (para architect)
    pm_next.py --preset priority-first|small-wins|stale-first
    pm_next.py --include-blocked     # bloqueados al final
    pm_next.py --source spec_draft   # filtra por fuente
    pm_next.py --no-wip-first        # quita boost de WIP

Output exit 0 siempre salvo error fatal (config inválida, gh sin auth).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    banner, die, find_pm_root, gh, gh_auth_check, gh_json, load_config, log,
    parse_frontmatter, today, warn,
)
from pm_lib.next_defaults import (
    DEFAULT_NEXT, PRESETS, SOURCE_LABELS,
)
from pm_lib.ranking import (
    Candidate, classify_source, detect_inconsistencies, is_blocked_by_deps,
    is_blocked_by_labels, rank,
)
from pm_lib.specs import iter_specs, resolve_issue, resolve_prs


# ---------------------------------------------------------------- config


def _deep_merge(base: dict, overlay: dict) -> dict:
    out = dict(base)
    for k, v in (overlay or {}).items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def effective_next(cfg: dict) -> dict:
    return _deep_merge(DEFAULT_NEXT, (cfg or {}).get("next") or {})


# ---------------------------------------------------------------- fuentes


def age_days_from_iso(iso: str | None) -> int:
    if not iso:
        return 0
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return 0
    now = datetime.now(timezone.utc)
    return max(0, (now - dt).days)


def load_local_specs(pm_root: Path, cfg: dict) -> list[dict]:
    """Devuelve lista de specs locales con frontmatter parseado + metadatos."""
    specs_dir = pm_root / cfg["paths"]["specs"]
    out: list[dict] = []
    for path in iter_specs(specs_dir):
        try:
            fm, _ = parse_frontmatter(path)
        except SystemExit:
            continue
        slug = path.stem
        # age desde `created` o `updated` del frontmatter
        age_iso = fm.get("created") or fm.get("updated")
        age = age_days_from_iso(age_iso + "T00:00:00Z" if age_iso and "T" not in str(age_iso) else age_iso)
        out.append({
            "slug": slug,
            "frontmatter": fm,
            "status": fm.get("status"),
            "priority": fm.get("priority", "unknown"),
            "size": fm.get("size", "unknown"),
            "issue": resolve_issue(fm),
            "prs": resolve_prs(fm),
            "depends_on": fm.get("depends_on") or [],
            "age_days": age,
            "title": fm.get("title") or slug,
        })
    return out


def fetch_board_items(repo: str, statuses: list[str], next_cfg: dict) -> tuple[list[dict], list[str]]:
    """Devuelve (items, warnings). items normalizado a dicts con num, title, status, priority, size, labels, age_days.

    Si gh project no funciona, degrada a `gh issue list` sin Status field.
    """
    warnings: list[str] = []
    # Intentar project items vía gh issue list con filtros básicos
    # (gh project item-list requiere project number + token con scope; lo evitamos
    # por simplicidad y portabilidad, usando gh issue list).
    try:
        data = gh_json(
            "issue", "list", "-R", repo, "--state", "open", "--limit", "200",
            "--json", "number,title,labels,createdAt,body",
        )
    except SystemExit:
        warnings.append("gh issue list falló; sin items del board")
        return [], warnings

    exclude_labels = {l.lower() for l in next_cfg.get("exclude_labels") or []}
    items: list[dict] = []
    for iss in data:
        labels = [l.get("name", "") for l in (iss.get("labels") or [])]
        if any(l.lower() in exclude_labels for l in labels):
            continue
        # Heurística para priority/size desde labels (P0, P1, P2; XS/S/M/L/XL)
        priority = "unknown"
        size = "unknown"
        for l in labels:
            up = l.upper()
            if up in ("P0", "P1", "P2"):
                priority = up
            elif up in ("XS", "S", "M", "L", "XL"):
                size = up
        items.append({
            "number": iss["number"],
            "title": iss["title"],
            "labels": labels,
            "priority": priority,
            "size": size,
            "age_days": age_days_from_iso(iss.get("createdAt")),
            "body": iss.get("body") or "",
        })
    if items and all(i["priority"] == "unknown" for i in items):
        warnings.append("ningún issue tiene label de priority (P0/P1/P2); ranking degrada a edad/momentum")
    if items and all(i["size"] == "unknown" for i in items):
        warnings.append("ningún issue tiene label de size (XS/S/M/L/XL); ranking degrada")
    return items, warnings


# ---------------------------------------------------------------- candidates


def build_candidates(
    specs: list[dict],
    board_items: list[dict],
    next_cfg: dict,
) -> list[Candidate]:
    """Combina fuentes en candidates únicos. Spec local prevalece sobre board."""
    blocking_labels = next_cfg.get("blocking_labels") or []
    spec_statuses = {s["slug"]: s["status"] for s in specs}

    # Index por issue para dedup
    spec_by_issue: dict[int, dict] = {}
    for s in specs:
        if s.get("issue"):
            spec_by_issue[int(s["issue"])] = s

    candidates: list[Candidate] = []

    # 1. Specs locales
    include_drafts = next_cfg.get("include_drafts", True)
    include_active = next_cfg.get("include_active_without_pr", True)
    for s in specs:
        status = s.get("status")
        if status not in ("draft", "active"):
            continue
        if status == "active":
            if not include_active:
                continue
            if s["prs"]:
                continue  # active CON PR ya está en Develop/Review
            source = "spec_active_no_pr"
        else:  # draft
            if not include_drafts:
                continue
            if s.get("issue"):
                # Draft con issue es raro; lo tratamos como board_with_spec
                source = "board_with_spec"
            else:
                source = "spec_draft"

        # blocked?
        blocked_dep, blockers_dep = is_blocked_by_deps(
            s.get("depends_on") or [], spec_statuses,
        )
        # Labels (si tiene issue, vendrán del board en el merge de abajo;
        # aquí sin labels)
        candidates.append(Candidate(
            slug=s["slug"],
            issue=s.get("issue"),
            title=s.get("title") or s["slug"],
            priority=str(s.get("priority", "unknown")),
            size=str(s.get("size", "unknown")),
            source=source,
            age_days=s.get("age_days", 0),
            blocked=blocked_dep,
            blockers=blockers_dep,
            labels=[],
        ))

    # 2. Board items sin spec local
    for item in board_items:
        if item["number"] in spec_by_issue:
            continue  # ya cubierto por spec
        labels = item.get("labels") or []
        blocked, hits = is_blocked_by_labels(labels, blocking_labels)
        # Slug derivado del título (kebab simple)
        slug = item["title"].lower().strip()
        slug = "".join(c if c.isalnum() or c in "- " else "" for c in slug)
        slug = "-".join(slug.split())[:50] or f"issue-{item['number']}"
        candidates.append(Candidate(
            slug=slug,
            issue=item["number"],
            title=item["title"],
            priority=item["priority"],
            size=item["size"],
            source="board_no_spec",
            age_days=item["age_days"],
            blocked=blocked,
            blockers=[f"label:{h}" for h in hits],
            labels=labels,
        ))

    # 3. Enriquecer specs con labels del board si tienen issue
    board_by_num = {b["number"]: b for b in board_items}
    for c in candidates:
        if c.issue and c.issue in board_by_num and not c.labels:
            b = board_by_num[c.issue]
            c.labels = b.get("labels") or []
            # Re-check labels de bloqueo
            if not c.blocked:
                blocked, hits = is_blocked_by_labels(c.labels, blocking_labels)
                if blocked:
                    c.blocked = True
                    c.blockers = (c.blockers or []) + [f"label:{h}" for h in hits]

    return candidates


# ---------------------------------------------------------------- output


def _fmt_row(rank_n: int, c: Candidate) -> str:
    wip = "[WIP]" if c.is_wip else "     "
    mark = "⚠" if c.blocked else "✓"
    reasons = " · ".join(c.reasons) or "—"
    issue = f" · #{c.issue}" if c.issue else ""
    return (
        f"  {rank_n}.  {wip} {c.priority:<3} {c.size:<3} {c.slug:<25} "
        f"{mark} {reasons}\n"
        f"       {SOURCE_LABELS.get(c.source, c.source)}{issue} {c.title[:60]}"
    )


def output_markdown(
    codename: str,
    preset: str,
    candidates: list[Candidate],
    total_considered: int,
    top: int,
    inconsistencies: list[dict],
    warnings: list[str],
) -> None:
    banner(f"/pm next — {codename} — {today()}")
    log(f"Preset: {preset} · {total_considered} candidatos, top {top}")
    for w in warnings:
        warn(w)

    wip = [c for c in candidates[:top] if c.is_wip]
    others = [c for c in candidates[:top] if not c.is_wip]

    if not wip and not others:
        print()
        print("(backlog vacío)")
        print()
        print("Próximo paso: /pm spec new <slug>  o  /pm cycle seed")
        return

    print()
    if wip:
        print("WIP (continuar antes que empezar):\n")
        for i, c in enumerate(wip, 1):
            print(_fmt_row(i, c))
            print()
    if others:
        print("Nuevo trabajo:\n")
        start = len(wip) + 1
        for i, c in enumerate(others, start):
            print(_fmt_row(i, c))
            print()

    if inconsistencies:
        print("\n## Inconsistencias\n")
        for inc in inconsistencies:
            print(f"  ⚠ {inc['slug']}: {inc['kind']}"
                  + (f" (issue #{inc['issue']})" if inc.get("issue") else ""))
            print(f"    → {inc['remediation']}")
        print()

    print("Para arrancar: di al architect \"implementa <slug>\"")
    print("O ejecuta: /pm cycle status <slug>")


def output_json(
    codename: str,
    preset: str,
    candidates: list[Candidate],
    total_considered: int,
    top: int,
    inconsistencies: list[dict],
    warnings: list[str],
) -> None:
    data = {
        "codename": codename,
        "preset": preset,
        "total_considered": total_considered,
        "top": top,
        "warnings": warnings,
        "candidates": [
            {
                "rank": i + 1,
                "slug": c.slug,
                "issue": c.issue,
                "title": c.title,
                "priority": c.priority,
                "size": c.size,
                "source": c.source,
                "is_wip": c.is_wip,
                "blocked": c.blocked,
                "blockers": c.blockers,
                "age_days": c.age_days,
                "labels": c.labels,
                "reasons": c.reasons,
            }
            for i, c in enumerate(candidates[:top])
        ],
        "inconsistencies": inconsistencies,
    }
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


# ---------------------------------------------------------------- main


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--top", type=int, help="cuántos mostrar (default: del config)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--preset", choices=PRESETS,
                    help="override del preset (default: del config)")
    ap.add_argument("--include-blocked", action="store_true")
    ap.add_argument("--source", choices=list(SOURCE_LABELS.keys()),
                    help="filtra por fuente")
    ap.add_argument("--no-wip-first", action="store_true",
                    help="ignora boost de WIP (equivalente a --preset priority-first)")
    args = ap.parse_args()

    gh_auth_check()
    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")
    repo = cfg["github"]["repo"]
    nxt = effective_next(cfg)

    preset = args.preset or nxt.get("preset", "wip-first")
    if args.no_wip_first and preset == "wip-first":
        preset = "priority-first"
    top = args.top or nxt.get("default_top", 5)

    # Fuentes
    specs = load_local_specs(pm_root, cfg)
    board_items, warnings = fetch_board_items(
        repo, nxt.get("include_board_statuses") or ["Backlog", "Ready"], nxt,
    )

    # Para inconsistencias necesitamos issue states
    issue_nums = [s["issue"] for s in specs if s.get("issue")]
    issues_by_num: dict[int, dict] = {}
    if issue_nums:
        try:
            data = gh_json(
                "issue", "list", "-R", repo, "--state", "all", "--limit", "300",
                "--json", "number,state,closedAt",
            )
            issues_by_num = {i["number"]: i for i in data}
        except SystemExit:
            warnings.append("no se pudo fetch issues state para inconsistencias")

    inconsistencies = detect_inconsistencies(specs, issues_by_num)

    # Build candidates
    candidates = build_candidates(specs, board_items, nxt)

    # Filtros opcionales
    if args.source:
        candidates = [c for c in candidates if c.source == args.source]

    # Ranking
    ranked = rank(candidates, preset, include_blocked=args.include_blocked)

    if args.json:
        output_json(cfg["codename"], preset, ranked, len(ranked), top,
                    inconsistencies, warnings)
    else:
        output_markdown(cfg["codename"], preset, ranked, len(ranked), top,
                        inconsistencies, warnings)


if __name__ == "__main__":
    main()
