#!/usr/bin/env python3
"""pm_policy_install_check — copia el workflow pm-policy.yml al repo.

Instala `.github/workflows/pm-policy.yml` desde el template del paquete.
Idempotente: si ya existe y es idéntico, no-op. Si difiere, pide
confirmación salvo --force.

Tras la instalación, imprime el comando `gh api` para configurar
`pm-policy/ready` como required status check en branch protection
(operación manual, no se automatiza).
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import banner, confirm, die, find_pm_root, load_config, log, ok, warn


SKILL_DIR = Path(__file__).resolve().parent.parent  # skills/pm/
TEMPLATE = SKILL_DIR / "assets" / "workflows" / "pm-policy.yml"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--force", action="store_true", help="sobrescribir sin confirmar")
    args = ap.parse_args()

    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")
    repo = cfg["github"]["repo"]
    default_branch = (cfg.get("policy", {}).get("branch", {}).get("default")) or "main"

    target = pm_root / ".github" / "workflows" / "pm-policy.yml"
    banner(f"/pm policy install-check — {repo}")

    if not TEMPLATE.is_file():
        die(f"template no encontrado: {TEMPLATE}")

    template_text = TEMPLATE.read_text(encoding="utf-8")

    if target.is_file():
        current = target.read_text(encoding="utf-8")
        if current == template_text:
            ok(f"{target.relative_to(pm_root)} ya está al día")
            _print_next_steps(repo, default_branch)
            return
        warn(f"{target.relative_to(pm_root)} ya existe y difiere del template")
        if not args.force and not confirm("¿Sobrescribir?"):
            die("abortado por el usuario", code=0)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(template_text, encoding="utf-8")
    ok(f"workflow instalado en {target.relative_to(pm_root)}")

    _print_next_steps(repo, default_branch)


def _print_next_steps(repo: str, default_branch: str) -> None:
    print()
    print("Siguientes pasos manuales:")
    print(f"  1. git add .github/workflows/pm-policy.yml && git commit -m 'chore(pm): install policy check'")
    print(f"  2. git push")
    print(f"  3. Configura 'pm-policy/ready' como required check en branch protection.")
    print(f"     Comando gh equivalente:")
    print(f"       gh api -X PATCH repos/{repo}/branches/{default_branch}/protection/required_status_checks \\")
    print(f"         -f strict=true -f 'contexts[]=pm-policy/ready'")
    print(f"  4. /pm policy validate")


if __name__ == "__main__":
    main()
