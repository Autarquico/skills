#!/usr/bin/env python3
"""pm_init — crea proyecto nuevo desde cero: repo + project + scaffolding PM.

Flujo:
    1. gh repo create
    2. gh project copy desde source
    3. gh project link
    4. Clone local
    5. Materializa templates con field_ids resueltos
    6. Commit + push inicial

Usage:
    pm_init.py <codename> [--org ORG] [--repo NAME] [--public|--private]
               [--source-project OWNER/N] [--language es|en] [--mcp-server NAME]
               [--dry-run]

Requiere: gh CLI con scopes repo + project. Repo NO debe existir.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    banner, die, fill_template, gh, gh_auth_check, gh_json, log, ok,
    save_config, today, warn,
)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("codename")
    ap.add_argument("--org", default="Autarquico")
    ap.add_argument("--repo", help="Nombre del repo (default: codename)")
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--private", action="store_true")
    ap.add_argument("--source-project", default="Autarquico/1",
                    help="OWNER/N a copiar como base del project")
    ap.add_argument("--language", default="es", choices=["es", "en"])
    ap.add_argument("--mcp-server", default="github")
    ap.add_argument("--owner-type", choices=["org", "user"], default="org")
    ap.add_argument("--target-dir", help="Dir destino del clone (default: ./<repo>)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    gh_auth_check()
    codename = args.codename
    repo_name = args.repo or codename
    visibility = "--public" if args.public else "--private"
    repo_full = f"{args.org}/{repo_name}"
    src_owner, src_num = args.source_project.split("/")
    target_dir = Path(args.target_dir or repo_name).resolve()

    banner(f"/pm init — {codename}")
    log(f"Repo:           {repo_full} ({visibility[2:]})")
    log(f"Source project: {args.source_project}")
    log(f"Target dir:     {target_dir}")

    if args.dry_run:
        log("[dry] gh repo create")
        log("[dry] gh project copy")
        log("[dry] gh project link")
        log("[dry] git clone")
        log("[dry] scaffold + commit + push")
        ok("DRY-RUN: nada ejecutado.")
        return

    if target_dir.exists():
        die(f"Target dir ya existe: {target_dir}")

    # 1. Create repo
    log("Creating repo...")
    gh("repo", "create", repo_full, visibility, "--confirm")
    ok(f"repo creado: {repo_full}")

    # 2. Copy project
    log(f"Copying project from {args.source_project}...")
    r = gh("project", "copy", src_num, "--source-owner", src_owner,
           "--target-owner", args.org, "--title", f"{codename} PM",
           "--format", "json")
    proj = json.loads(r.stdout)
    project_number = proj.get("number") or proj.get("projectNumber")
    if not project_number:
        die(f"No pude extraer número del project copiado: {proj}")
    ok(f"project copiado: #{project_number}")

    # 3. Link project to repo
    gh("project", "link", str(project_number), "--owner", args.org,
       "--repo", repo_full, check=False)
    ok("project linked to repo")

    # 4. Resolve field IDs (reuse logic from pm_adopt)
    from pm_adopt import resolve_project_fields
    fields = resolve_project_fields(args.org, project_number, args.owner_type)
    log(f"Field IDs: {sum(1 for k,v in fields.items() if v and k!='project_id')}/4 resueltos")

    # 5. Clone + scaffold
    log("Cloning...")
    subprocess.run(["gh", "repo", "clone", repo_full, str(target_dir)], check=True)

    cfg = {
        "codename": codename,
        "display_name": codename.capitalize(),
        "github": {
            "repo": repo_full,
            "project": {"owner": args.org, "owner_type": args.owner_type, "number": project_number},
            "field_ids": {
                "status": fields["status"] or "",
                "priority": fields["priority"] or "",
                "size": fields["size"] or "",
                "ticket_type": fields["ticket_type"] or "",
            },
        },
        "paths": {
            "specs": "docs/specs/",
            "specs_archive": "docs/specs/archive/",
            "tracking": {"status": "docs/STATUS.md"},
        },
        "agent": {"language": args.language, "conventions": "AGENT.md"},
        "mcp": {"server": args.mcp_server},
        "sync": {"archive_on_ship": False, "default_since_days": 7},
    }
    save_config(target_dir / ".pm" / "config.yaml", cfg)
    (target_dir / "docs" / "specs" / "archive").mkdir(parents=True, exist_ok=True)
    (target_dir / "docs" / "specs" / ".gitkeep").write_text("", encoding="utf-8")
    (target_dir / "docs" / "specs" / "archive" / ".gitkeep").write_text("", encoding="utf-8")

    skill_dir = Path(__file__).resolve().parent.parent
    templates = skill_dir / "assets" / "templates"
    placeholders = {
        "display_name": codename.capitalize(),
        "today": today(),
        "codename": codename,
        "org": args.org,
        "repo_name": repo_name,
        "project_owner": args.org,
        "project_number": project_number,
        "mcp_server": args.mcp_server,
        "language": args.language,
    }
    (target_dir / "docs" / "STATUS.md").write_text(
        fill_template((templates / "STATUS.md").read_text(encoding="utf-8"), placeholders),
        encoding="utf-8",
    )
    (target_dir / "AGENT.md").write_text(
        fill_template((templates / "AGENT.md").read_text(encoding="utf-8"), placeholders),
        encoding="utf-8",
    )
    (target_dir / "README.md").write_text(
        f"# {codename}\n\nProject managed via `pm` skill.\n", encoding="utf-8"
    )
    ok("scaffolding materializado")

    # 6. Commit + push
    subprocess.run(["git", "-C", str(target_dir), "add", "."], check=True)
    subprocess.run(["git", "-C", str(target_dir), "commit",
                    "-m", "chore(pm): initialize PM system"], check=True)
    subprocess.run(["git", "-C", str(target_dir), "push", "origin", "HEAD"], check=True)
    ok("commit inicial pushed")

    log("Listo. Siguientes pasos:")
    log(f"  cd {target_dir}")
    log("  python3 -m pm.scripts.pm_sync --dry-run   # (o invoca via slash)")


if __name__ == "__main__":
    main()
