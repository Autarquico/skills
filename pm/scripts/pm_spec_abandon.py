#!/usr/bin/env python3
"""pm_spec_abandon — marca una spec como abandoned y archiva con razón.

Acciones:
- spec.frontmatter.status → abandoned, abandoned_at, abandoned_reason
- mover a docs/specs/archive/YYYY-MM-DD-<slug>.md (idempotente)
- si hay issue vinculado: cerrar como not_planned + label `abandoned`
  + comentario `[pm-sync] abandoned: <motivo>`

Usage:
    pm_spec_abandon.py <slug> --reason "<motivo>" [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    banner, die, find_pm_root, gh, gh_auth_check, gh_json, load_config, log,
    ok, parse_frontmatter, today, warn, working_tree_clean, write_frontmatter,
)
from pm_lib.specs import resolve_issue


PM_SYNC_TAG = "[pm-sync]"


def ensure_label(repo: str, name: str, dry: bool) -> None:
    labels = gh_json(
        "label", "list", "-R", repo, "--limit", "200", "--json", "name",
    )
    if any(l["name"] == name for l in labels):
        return
    if dry:
        log(f"[dry] crear label '{name}'")
        return
    gh("label", "create", name, "-R", repo,
       "--description", "Spec abandoned via /pm spec abandon", "--color", "BFBFBF")


def close_issue_not_planned(repo: str, issue_num: int, reason: str, dry: bool) -> None:
    body = f"{PM_SYNC_TAG} abandoned: {reason}"
    if dry:
        log(f"[dry] comment + close --reason not-planned #{issue_num}")
        return
    gh("issue", "comment", str(issue_num), "-R", repo, "--body", body)
    gh("issue", "edit", str(issue_num), "-R", repo, "--add-label", "abandoned")
    gh("issue", "close", str(issue_num), "-R", repo, "--reason", "not planned")


def archive_path(archive_dir: Path, slug: str, when: str) -> Path:
    return archive_dir / f"{when}-{slug}.md"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug")
    ap.add_argument("--reason", required=True, help="por qué se abandona")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    gh_auth_check()
    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")
    repo = cfg["github"]["repo"]
    specs_dir = pm_root / cfg["paths"]["specs"]
    archive_dir = pm_root / cfg["paths"]["specs_archive"]

    spec_path = specs_dir / f"{args.slug}.md"
    if not spec_path.is_file():
        die(f"no existe {spec_path}")
    if not args.dry_run and not working_tree_clean(pm_root):
        die("working tree no limpio. Commit o stash antes.")

    banner(f"/pm spec abandon — {args.slug} — {today()}")
    log(f"Motivo: {args.reason}")
    log(f"Modo:   {'DRY-RUN' if args.dry_run else 'APPLY'}")

    fm, body = parse_frontmatter(spec_path)
    when = today()
    fm["status"] = "abandoned"
    fm["abandoned_at"] = when
    fm["abandoned_reason"] = args.reason
    fm["updated"] = when

    target = archive_path(archive_dir, args.slug, when)
    if target.exists():
        die(f"ya existe {target} — abandono previo o colisión. Revisa.")

    if args.dry_run:
        log(f"[dry] reescribir frontmatter en {spec_path}")
        log(f"[dry] mover a {target}")
    else:
        write_frontmatter(spec_path, fm, body)
        archive_dir.mkdir(parents=True, exist_ok=True)
        spec_path.rename(target)
        ok(f"spec → {target.relative_to(pm_root)}")

    issue_num = resolve_issue(fm)
    if issue_num is not None:
        ensure_label(repo, "abandoned", args.dry_run)
        close_issue_not_planned(repo, issue_num, args.reason, args.dry_run)
        ok(f"issue #{issue_num} cerrado como not-planned")
    else:
        warn("sin issue vinculado en frontmatter; solo se archiva la spec.")

    ok("listo.")


if __name__ == "__main__":
    main()
