#!/usr/bin/env python3
"""pm_policy_init — wizard o preset para escribir el bloque `policy:`.

Modos:
    (sin args)         wizard interactivo con detección de estado del repo
    --preset NAME      aplica preset (conservative|standard|solo) sin prompts
    --yes              acepta todos los defaults detectados en wizard

Escribe en .pm/config.yaml. Si el bloque policy: ya existe, pide
confirmación antes de sobrescribir (salvo --force).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    banner, confirm, die, find_pm_root, gh, gh_auth_check, gh_json, load_config, log, ok, warn,
    yaml_dumps, yaml_loads,
)
from pm_lib.policy import effective_policy
from pm_lib.policy_defaults import DEFAULT_POLICY, PRESETS


# ---------------------------------------------------------------- detection


def detect_merge_strategy(repo: str) -> str:
    """Mira últimos PRs mergeados para inferir estrategia mayoritaria."""
    try:
        data = gh_json(
            "pr", "list", "-R", repo, "--state", "merged", "--limit", "20",
            "--json", "mergeCommit,number",
        )
    except SystemExit:
        return "squash"
    # Sin acceso a mergeMethod via gh, asumir squash (más común). Heurística pobre
    # pero suficiente: el usuario lo confirma en el wizard.
    return "squash"


def detect_branch_protection(repo: str, branch: str) -> dict | None:
    """Devuelve protección de la rama default, o None si no hay/error."""
    try:
        r = gh(
            "api", f"repos/{repo}/branches/{branch}/protection",
            check=False,
        )
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)
    except Exception:
        return None


def detect_deploy_provider(pm_root: Path) -> str:
    """Heurística por archivos de config conocidos en la raíz del repo."""
    repo_root = pm_root
    if (repo_root / "vercel.json").is_file() or (repo_root / ".vercel").is_dir():
        return "github_action"   # vercel auto-deploys; el push a main lo dispara
    if (repo_root / "wrangler.toml").is_file():
        return "github_action"
    if (repo_root / "netlify.toml").is_file():
        return "github_action"
    if (repo_root / ".github" / "workflows").is_dir():
        # tiene workflows; asumimos uno hace deploy
        return "github_action"
    return "none"


def detect_default_branch(repo: str) -> str:
    try:
        d = gh_json("repo", "view", repo, "--json", "defaultBranchRef")
        return d["defaultBranchRef"]["name"]
    except Exception:
        return "main"


# ---------------------------------------------------------------- wizard


def ask_choice(prompt: str, default: str, choices: list[str]) -> str:
    options = "/".join(c if c != default else c.upper() for c in choices)
    while True:
        try:
            r = input(f"  {prompt} [{options}] ").strip().lower()
        except EOFError:
            return default
        if not r:
            return default
        if r in choices:
            return r
        print(f"  → opciones: {', '.join(choices)}")


def ask_bool(prompt: str, default: bool) -> bool:
    label = "Y/n" if default else "y/N"
    try:
        r = input(f"  {prompt} [{label}] ").strip().lower()
    except EOFError:
        return default
    if not r:
        return default
    return r in ("y", "yes", "s", "si", "sí")


def ask_str(prompt: str, default: str) -> str:
    try:
        r = input(f"  {prompt} [{default}] ").strip()
    except EOFError:
        return default
    return r or default


def run_wizard(cfg: dict, pm_root: Path, accept_all: bool) -> dict:
    """Devuelve el bloque policy: a escribir."""
    repo = cfg["github"]["repo"]
    log("Detectando estado del repo...")
    default_branch = detect_default_branch(repo)
    bp = detect_branch_protection(repo, default_branch)
    suggested_human_approval = False
    if bp:
        prs_required = (bp.get("required_pull_request_reviews") or {})
        if prs_required.get("required_approving_review_count", 0) >= 1:
            suggested_human_approval = True
            log("  branch protection exige reviews → propongo require_human_approval=true")
    deploy = detect_deploy_provider(pm_root)
    if deploy != "none":
        log(f"  provider de deploy detectado → merge_handoff.method={deploy}")
    suggested_strategy = detect_merge_strategy(repo)
    log(f"  merge strategy sugerida → {suggested_strategy}")

    if accept_all:
        log("Modo --yes: aceptando todos los defaults detectados.")
        return {
            "branch": {"default": default_branch},
            "merge": {"strategy": suggested_strategy},
            "review": {"require_human_approval": suggested_human_approval},
            "merge_handoff": {"method": deploy},
        }

    print()
    banner("Wizard — decisiones de la policy")
    print("(Enter acepta el default entre [corchetes])")
    print()

    print("Merge y push:")
    strategy = ask_choice("Merge strategy", suggested_strategy, ["squash", "rebase", "merge"])
    auto_merge = ask_choice("Auto-merge mode (conditional=auto cuando reviews+CI ok / manual=mergeas a mano)",
                            "conditional", ["conditional", "manual"])
    delete_branch = ask_bool("Borrar branch tras merge", True)

    print("\nReviews:")
    require_internal = ask_bool("Requerir review interna (bucle interno reviewer panel)", True)
    require_external = ask_bool("Requerir review externa (codex Fase 4)", True)
    require_human = ask_bool("Requerir aprobación humana (gh review)", suggested_human_approval)
    light_ok = ask_bool("Light path puede auto-mergear (útil en repos solo)", False)

    print("\nBranch y commits:")
    naming = ask_str("Convención de branch naming", "<type>/<slug>")
    conventional = ask_bool("Conventional commits", True)

    print("\nMerge handoff:")
    handoff = ask_choice("Método de handoff post-merge",
                         deploy if deploy != "none" else "none",
                         ["github_action", "external", "runbook", "none"])

    block = {
        "branch": {
            "default": default_branch,
            "naming": naming,
            "delete_after_merge": delete_branch,
        },
        "commits": {
            "conventional": conventional,
        },
        "merge": {
            "strategy": strategy,
            "auto_merge": auto_merge,
        },
        "review": {
            "require_internal": require_internal,
            "require_external": require_external,
            "require_human_approval": require_human,
            "light_path_ok_for_auto_merge": light_ok,
        },
        "merge_handoff": {
            "method": handoff,
        },
    }

    print()
    banner("Bloque policy propuesto")
    print(yaml_dumps({"policy": block}))
    if not confirm("¿Aplicar?"):
        die("abortado por el usuario", code=0)
    return block


def apply_preset(name: str) -> dict:
    if name not in PRESETS:
        die(f"preset desconocido: {name}. Opciones: {', '.join(PRESETS)}")
    return PRESETS[name]


# ---------------------------------------------------------------- write


def write_policy_to_config(config_path: Path, policy_block: dict, force: bool) -> None:
    text = config_path.read_text(encoding="utf-8")
    existing = yaml_loads(text) or {}
    if not isinstance(existing, dict):
        die(f"{config_path}: no parsea como mapping")

    if existing.get("policy") and not force:
        if not confirm(
            "Ya existe un bloque policy: en .pm/config.yaml. ¿Sobrescribir?"
        ):
            die("abortado: bloque policy ya presente. Usa --force.", code=0)

    existing["policy"] = policy_block
    config_path.write_text(yaml_dumps(existing) + "\n", encoding="utf-8")
    ok(f"policy escrita en {config_path}")


# ---------------------------------------------------------------- main


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--preset", choices=list(PRESETS.keys()),
                    help="aplicar preset sin prompts")
    ap.add_argument("--yes", action="store_true",
                    help="wizard sin preguntas (acepta defaults detectados)")
    ap.add_argument("--force", action="store_true",
                    help="sobrescribir bloque policy: existente sin confirmar")
    args = ap.parse_args()

    if args.preset and args.yes:
        die("--preset y --yes son mutuamente excluyentes")

    gh_auth_check()
    pm_root = find_pm_root()
    cfg_path = pm_root / ".pm" / "config.yaml"
    cfg = load_config(cfg_path)

    banner("/pm policy init")

    if args.preset:
        block = apply_preset(args.preset)
        log(f"Aplicando preset: {args.preset}")
    else:
        block = run_wizard(cfg, pm_root, accept_all=args.yes)

    write_policy_to_config(cfg_path, block, force=args.force)
    log("Siguiente: /pm policy install-check y luego /pm policy validate")


if __name__ == "__main__":
    main()
