#!/usr/bin/env python3
"""pm_adopt — adopta un repo existente añadiendo scaffolding PM no-destructivo.

Genera:
  .pm/config.yaml
  docs/specs/.gitkeep
  docs/specs/archive/.gitkeep
  docs/STATUS.md  (si no existe)
  AGENT.md         (si no existe)

Nunca sobrescribe archivos existentes.

Usage:
    pm_adopt.py [--codename SLUG] [--project N] [--language es|en]
                [--mcp-server NAME] [--dry-run]

Exit codes:
    0  success
    1  error (no es repo git, ya adoptado, gh fail, project no encontrado)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    banner, die, fill_template, gh, gh_auth_check, gh_json, log, ok,
    save_config, today, warn,
)


def detect_repo_root() -> Path:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return Path(r.stdout.strip())
    except subprocess.CalledProcessError:
        die("cwd no es un repo git")
    except FileNotFoundError:
        die("`git` no está en PATH")


def detect_repo_slug() -> str:
    info = gh_json("repo", "view", "--json", "nameWithOwner")
    return info["nameWithOwner"]


def resolve_project_fields(owner: str, number: int, owner_type: str) -> dict:
    """Query Projects v2 GraphQL to resolve field IDs (status, priority, size, ticket_type)."""
    query = """
    query($login: String!, $number: Int!) {
      %s(login: $login) {
        projectV2(number: $number) {
          id
          fields(first: 50) {
            nodes {
              ... on ProjectV2FieldCommon { id name }
              ... on ProjectV2SingleSelectField { id name options { id name } }
            }
          }
        }
      }
    }
    """ % ("organization" if owner_type == "org" else "user")
    r = gh("api", "graphql",
           "-f", f"query={query}",
           "-F", f"login={owner}",
           "-F", f"number={number}")
    import json as _json
    data = _json.loads(r.stdout)
    root = data.get("data", {}).get("organization" if owner_type == "org" else "user")
    if not root or not root.get("projectV2"):
        die(f"Project #{number} no encontrado en {owner} ({owner_type})")
    proj = root["projectV2"]
    fields = {f["name"].lower(): f["id"] for f in proj["fields"]["nodes"] if f}
    # Look up by common names with fallbacks
    def pick(*candidates: str) -> str | None:
        for c in candidates:
            if c.lower() in fields:
                return fields[c.lower()]
        return None
    return {
        "project_id": proj["id"],
        "status": pick("Status"),
        "priority": pick("Priority"),
        "size": pick("Size", "Estimate"),
        "ticket_type": pick("Ticket Type", "Type", "TicketType"),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--codename", help="Slug (default: nombre del repo)")
    ap.add_argument("--project", type=int, help="Número del GitHub Project")
    ap.add_argument("--project-owner", help="Owner del project (default: org del repo)")
    ap.add_argument("--owner-type", choices=["org", "user"], default="org")
    ap.add_argument("--language", default="es", choices=["es", "en"])
    ap.add_argument("--mcp-server", default="github")
    ap.add_argument("--display-name", help="Display name (default: codename capitalizado)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    gh_auth_check()
    repo_root = detect_repo_root()

    if (repo_root / ".pm" / "config.yaml").is_file():
        die("Ya adoptado: .pm/config.yaml existe.")

    repo_slug = detect_repo_slug()
    owner, repo_name = repo_slug.split("/", 1)
    codename = args.codename or repo_name
    project_owner = args.project_owner or owner
    display_name = args.display_name or codename.capitalize()

    banner(f"/pm adopt — {codename}")
    log(f"Repo:    {repo_slug}")
    log(f"Codename: {codename}")

    field_ids = {"project_id": None, "status": None, "priority": None, "size": None, "ticket_type": None}
    if args.project:
        log(f"Project: {project_owner}/projects/{args.project} ({args.owner_type})")
        field_ids = resolve_project_fields(project_owner, args.project, args.owner_type)
        log(f"Field IDs resueltos: {sum(1 for k,v in field_ids.items() if v and k!='project_id')}/4")
    else:
        warn("Sin --project: campo github.project quedará vacío. Edita .pm/config.yaml manualmente.")

    # Build config
    cfg = {
        "codename": codename,
        "display_name": display_name,
        "github": {
            "repo": repo_slug,
            "project": {
                "owner": project_owner,
                "owner_type": args.owner_type,
                "number": args.project or 0,
            },
            "field_ids": {
                "status": field_ids["status"] or "",
                "priority": field_ids["priority"] or "",
                "size": field_ids["size"] or "",
                "ticket_type": field_ids["ticket_type"] or "",
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

    skill_dir = Path(__file__).resolve().parent.parent
    templates = skill_dir / "assets" / "templates"

    plan = []
    plan.append((repo_root / ".pm" / "config.yaml", "config", None))
    plan.append((repo_root / "docs" / "specs" / ".gitkeep", "gitkeep", ""))
    plan.append((repo_root / "docs" / "specs" / "archive" / ".gitkeep", "gitkeep", ""))

    status_path = repo_root / "docs" / "STATUS.md"
    if not status_path.exists():
        status_tpl = (templates / "STATUS.md").read_text(encoding="utf-8")
        plan.append((status_path, "status", fill_template(
            status_tpl, {"display_name": display_name, "today": today()})))

    agent_path = repo_root / "AGENT.md"
    if not agent_path.exists():
        agent_tpl = (templates / "AGENT.md").read_text(encoding="utf-8")
        plan.append((agent_path, "agent", fill_template(agent_tpl, {
            "display_name": display_name,
            "language": args.language,
            "codename": codename,
            "org": owner,
            "repo_name": repo_name,
            "project_owner": project_owner,
            "project_number": args.project or 0,
            "mcp_server": args.mcp_server,
        })))

    log("Plan:")
    for path, kind, _ in plan:
        rel = path.relative_to(repo_root)
        exists = " (skip: existe)" if path.exists() else ""
        log(f"  {kind:8s}  {rel}{exists}")

    if args.dry_run:
        ok("DRY-RUN: nada escrito.")
        return

    created = 0
    for path, kind, content in plan:
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        if kind == "config":
            save_config(path, cfg)
        else:
            path.write_text(content or "", encoding="utf-8")
        created += 1
        ok(f"creado {path.relative_to(repo_root)}")

    ok(f"{created} archivos creados.")
    log("Siguientes pasos:")
    log("  1. Revisa .pm/config.yaml")
    log("  2. git add .pm/ docs/ AGENT.md && git commit -m 'chore(pm): adopt PM system'")
    log("  3. python3 scripts/pm_sync.py --dry-run")


if __name__ == "__main__":
    main()
