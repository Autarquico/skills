#!/usr/bin/env python3
"""pm_policy_validate — compara policy declarada vs realidad del repo.

Comprueba:
- Branch protection y rulesets: require_human_approval coincide con required reviews.
- Workflow .github/workflows/pm-policy.yml instalado.
- Estrategia de merge declarada está permitida por el repo (allow_*).

Severidades:
- info: cosa documental ok
- warning: discrepancia que no bloquea pero conviene alinear
- error: discrepancia que rompe auto-merge si no se corrige

Exit code 0 siempre salvo --strict (entonces 1 si hay errors).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import banner, die, find_pm_root, gh, gh_auth_check, gh_json, load_config
from pm_lib.policy import effective_policy


def _gh_api(path: str) -> dict | None:
    r = gh("api", path, check=False)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def check(pm_root: Path, cfg: dict, strict: bool = False) -> int:
    """Devuelve nº de errors."""
    repo = cfg["github"]["repo"]
    policy = effective_policy(cfg)
    default_branch = policy["branch"]["default"]

    findings: list[tuple[str, str]] = []  # (severity, msg)

    # Branch protection
    protection = _gh_api(f"repos/{repo}/branches/{default_branch}/protection")
    require_human = policy["review"]["require_human_approval"]
    if protection is None:
        findings.append((
            "warning",
            f"sin branch protection en {default_branch} (o sin permisos para leerla)"
        ))
    else:
        prs_required = (protection.get("required_pull_request_reviews") or {})
        n = prs_required.get("required_approving_review_count", 0)
        if require_human and n < 1:
            findings.append((
                "error",
                f"policy.review.require_human_approval=true pero branch protection no exige reviews"
            ))
        elif not require_human and n >= 1:
            findings.append((
                "error",
                f"branch protection exige {n} review(s) pero policy.require_human_approval=false; auto-merge se quedará colgado"
            ))

        # Required status checks
        rsc = (protection.get("required_status_checks") or {}).get("contexts") or []
        if "pm-policy/ready" not in rsc:
            findings.append((
                "warning",
                "branch protection NO exige `pm-policy/ready`; alguien podría saltarse la policy desde la UI"
            ))

    # Workflow instalado
    wf_path = pm_root / ".github" / "workflows" / "pm-policy.yml"
    if not wf_path.is_file():
        findings.append((
            "error",
            f"falta {wf_path.relative_to(pm_root)}; ejecuta `/pm policy install-check`"
        ))

    # Merge strategy permitida
    repo_data = _gh_api(f"repos/{repo}")
    strategy = policy["merge"]["strategy"]
    if repo_data:
        allowed = {
            "squash": repo_data.get("allow_squash_merge", True),
            "merge": repo_data.get("allow_merge_commit", True),
            "rebase": repo_data.get("allow_rebase_merge", True),
        }
        if not allowed.get(strategy, True):
            findings.append((
                "error",
                f"policy.merge.strategy={strategy} no está permitida por el repo (allow_{strategy}_merge=false)"
            ))

    # Imprimir
    banner(f"/pm policy validate — {repo}")
    if not findings:
        print("✓ Sin discrepancias.")
        return 0

    errors = 0
    for sev, msg in findings:
        icon = {"info": "·", "warning": "⚠", "error": "✗"}[sev]
        print(f"  {icon} [{sev}] {msg}")
        if sev == "error":
            errors += 1

    if errors and strict:
        return errors
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true", help="exit 1 si hay errors")
    args = ap.parse_args()

    gh_auth_check()
    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")

    errors = check(pm_root, cfg, strict=args.strict)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
