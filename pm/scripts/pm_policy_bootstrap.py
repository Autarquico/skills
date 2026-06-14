#!/usr/bin/env python3
"""pm_policy_bootstrap — adopción a nivel proyecto.

Detecta el estado del repo y ejecuta lo que falte:
- sin .pm/config.yaml → recordatorio para correr /pm adopt
- sin bloque policy: → /pm policy init (wizard o preset)
- sin .github/workflows/pm-policy.yml → /pm policy install-check

Idempotente: si todo está, no-op.

Usage:
    pm_policy_bootstrap.py [--preset NAME] [--yes] [--force]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import banner, find_pm_root, log, ok, warn


SCRIPT_DIR = Path(__file__).resolve().parent


def run(cmd: list[str]) -> int:
    log(f"$ {' '.join(cmd)}")
    return subprocess.call(cmd)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--preset", help="aplicar preset en init (sin wizard)")
    ap.add_argument("--yes", action="store_true", help="wizard fast-forward (acepta defaults)")
    ap.add_argument("--force", action="store_true", help="forzar overwrites")
    args = ap.parse_args()

    banner("/pm policy bootstrap")

    try:
        pm_root = find_pm_root()
    except SystemExit:
        warn("no encuentro .pm/config.yaml hacia arriba. Ejecuta `/pm adopt` primero.")
        sys.exit(1)

    config_path = pm_root / ".pm" / "config.yaml"
    log(f"Repo root: {pm_root}")

    # Estado actual
    has_policy_block = False
    try:
        from _common import yaml_loads
        data = yaml_loads(config_path.read_text(encoding="utf-8")) or {}
        has_policy_block = bool(data.get("policy"))
    except Exception:
        has_policy_block = False

    has_workflow = (pm_root / ".github" / "workflows" / "pm-policy.yml").is_file()

    log(f"Bloque policy en config:    {'sí' if has_policy_block else 'NO'}")
    log(f"Workflow pm-policy.yml:     {'sí' if has_workflow else 'NO'}")

    # Init si falta
    if not has_policy_block or args.force:
        log("Paso: /pm policy init")
        cmd = ["python3", str(SCRIPT_DIR / "pm_policy_init.py")]
        if args.preset:
            cmd += ["--preset", args.preset]
        elif args.yes:
            cmd += ["--yes"]
        if args.force:
            cmd += ["--force"]
        rc = run(cmd)
        if rc != 0:
            sys.exit(rc)

    # Install workflow si falta
    if not has_workflow or args.force:
        log("Paso: /pm policy install-check")
        cmd = ["python3", str(SCRIPT_DIR / "pm_policy_install_check.py")]
        if args.force:
            cmd += ["--force"]
        rc = run(cmd)
        if rc != 0:
            sys.exit(rc)

    # PRs open?
    from _common import gh_json, gh_auth_check, load_config
    gh_auth_check()
    cfg = load_config(config_path)
    repo = cfg["github"]["repo"]
    prs = gh_json(
        "pr", "list", "-R", repo, "--state", "open", "--limit", "200",
        "--json", "number,labels",
    )
    unmanaged = [p for p in prs
                 if not any(l["name"] == "pm/policy-managed" for l in (p.get("labels") or []))]
    if unmanaged:
        print()
        warn(f"Hay {len(unmanaged)} PRs open sin label pm/policy-managed.")
        print("  Considera ejecutar:")
        print("    /pm policy adopt-prs --default-internal skipped")
        print("  (lo más conservador: ningún PR antiguo se auto-mergeará sin tu OK)")

    print()
    ok("bootstrap completo.")
    print()
    print("Checklist pendiente (manual):")
    print(f"  1. git add .pm/config.yaml .github/workflows/pm-policy.yml")
    print(f"  2. git commit + git push")
    print(f"  3. Configurar 'pm-policy/ready' como required check en branch protection")
    print(f"     (ver salida de /pm policy install-check para el comando gh)")
    print(f"  4. /pm policy validate")


if __name__ == "__main__":
    main()
