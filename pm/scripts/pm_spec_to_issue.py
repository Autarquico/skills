#!/usr/bin/env python3
"""pm_spec_to_issue — convierte una spec draft en issue del GitHub Project.

Usage:
    pm_spec_to_issue.py <slug> [--dry-run]

Pre-flight:
    - Spec existe y status == draft
    - related_issues vacío

Mutaciones:
    1. gh issue create con título + body (sin frontmatter)
    2. Añade el issue al project configurado
    3. Actualiza frontmatter: related_issues=[N], status=active, updated=today
    4. Comenta [pm-sync] Spec: docs/specs/<slug>.md en el issue

Exit codes: 0 ok, 1 error.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    banner, die, find_pm_root, gh, gh_auth_check, gh_json, load_config, log,
    ok, parse_frontmatter, today, warn, working_tree_clean, write_frontmatter,
)


def add_to_project(owner: str, owner_type: str, project_number: int,
                   issue_url: str, dry: bool) -> str | None:
    """Use `gh project item-add` to attach the issue to the project. Returns item id."""
    if dry:
        log(f"   [dry] project add → {owner}/projects/{project_number}")
        return None
    r = gh("project", "item-add", str(project_number),
           "--owner", owner, "--url", issue_url, "--format", "json")
    import json as _json
    try:
        data = _json.loads(r.stdout)
        return data.get("id")
    except Exception:
        return None


def build_labels(fm: dict) -> list[str]:
    labels = []
    if t := fm.get("type"):
        labels.append(f"type:{t}")
    if p := fm.get("priority"):
        labels.append(p)
    if s := fm.get("size"):
        labels.append(f"size:{s}")
    return labels


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-labels", action="store_true",
                    help="No intenta añadir labels (útil si no existen en el repo)")
    args = ap.parse_args()

    gh_auth_check()
    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")
    repo = cfg["github"]["repo"]

    spec_path = pm_root / cfg["paths"]["specs"] / f"{args.slug}.md"
    if not spec_path.is_file():
        die(f"Spec no encontrada: {spec_path}")

    fm, body = parse_frontmatter(spec_path)
    banner(f"/pm spec to-issue — {args.slug}")

    if fm.get("status") != "draft":
        die(f"Spec no está en draft (status: {fm.get('status')})")
    if fm.get("related_issues"):
        die(f"Spec ya tiene related_issues: {fm['related_issues']}")
    title = fm.get("title") or args.slug
    if not args.dry_run and not working_tree_clean(pm_root):
        die("Working tree no está limpio; commitea cambios antes.")

    log(f"Repo:  {repo}")
    log(f"Title: {title}")
    log(f"Type:  {fm.get('type')}  Priority: {fm.get('priority')}  Size: {fm.get('size')}")

    issue_body = body.strip()

    if args.dry_run:
        log("[dry] gh issue create")
        log(f"[dry] add to project {cfg['github']['project']['owner']}/{cfg['github']['project']['number']}")
        log("[dry] update frontmatter: status→active, related_issues=[N]")
        ok("DRY-RUN: nada mutado.")
        return

    # Step 1: create issue
    create_args = ["issue", "create", "-R", repo, "--title", title, "--body", issue_body]
    if not args.no_labels:
        for label in build_labels(fm):
            create_args.extend(["--label", label])
    r = gh(*create_args, check=False)
    if r.returncode != 0:
        # Retry without labels if they're the problem
        if not args.no_labels and "label" in (r.stderr or "").lower():
            warn("Falló por labels inexistentes. Reintento sin labels.")
            r = gh("issue", "create", "-R", repo, "--title", title, "--body", issue_body)
        else:
            die(f"gh issue create falló:\n{r.stderr}")
    issue_url = r.stdout.strip().splitlines()[-1]
    m = re.search(r"/issues/(\d+)", issue_url)
    if not m:
        die(f"No pude extraer número del issue de: {issue_url}")
    issue_num = int(m.group(1))
    ok(f"issue creado: #{issue_num}  {issue_url}")

    # Step 2: add to project
    p = cfg["github"]["project"]
    if p.get("number"):
        try:
            add_to_project(p["owner"], p["owner_type"], p["number"], issue_url, False)
            ok(f"añadido al project {p['owner']}/projects/{p['number']}")
        except SystemExit:
            warn("project item-add falló; sigue (el issue existe).")
    else:
        warn("Config no tiene github.project.number; salteando project add.")

    # Step 3: update frontmatter
    fm["related_issues"] = [issue_num]
    fm["status"] = "active"
    fm["updated"] = today()
    write_frontmatter(spec_path, fm, body)
    ok(f"frontmatter actualizado: status=active, related_issues=[{issue_num}]")

    # Step 4: pm-sync comment
    spec_rel = spec_path.relative_to(pm_root)
    gh("issue", "comment", str(issue_num), "-R", repo,
       "--body", f"[pm-sync] Spec: {spec_rel}")
    ok(f"comentario [pm-sync] en #{issue_num}")
    log(f"Siguiente: crear PR con 'Closes #{issue_num}' para cerrar el ciclo")


if __name__ == "__main__":
    main()
