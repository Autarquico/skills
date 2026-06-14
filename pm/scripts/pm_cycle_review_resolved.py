#!/usr/bin/env python3
"""pm_cycle_review_resolved — marca external review + sync.

Tras revisar el PR con codex (Fase 4), invoca este comando para:
1. Añadir label pm/external-{mergeable|needs-changes} al PR de la spec.
2. Quitar el label opuesto si existía.
3. Comentar [pm-sync] con el verdict.
4. Ejecutar /pm sync para que el Step 5 active auto-merge si procede.

Es el comando del happy path tras codex review.

Usage:
    pm_cycle_review_resolved.py <slug> <mergeable|needs-changes>
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    banner, die, find_pm_root, gh, gh_auth_check, gh_json, load_config, log, ok,
    parse_frontmatter,
)
from pm_lib.policy_defaults import LABELS
from pm_lib.specs import resolve_issue, resolve_prs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug")
    ap.add_argument("verdict", choices=["mergeable", "needs-changes"])
    ap.add_argument("--pr", type=int, help="override de PR (default: último prs[] de la spec o linked al issue)")
    ap.add_argument("--no-sync", action="store_true", help="no ejecutar /pm sync al final")
    args = ap.parse_args()

    gh_auth_check()
    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")
    repo = cfg["github"]["repo"]

    spec_path = pm_root / cfg["paths"]["specs"] / f"{args.slug}.md"
    if not spec_path.is_file():
        die(f"no existe {spec_path}")
    fm, _ = parse_frontmatter(spec_path)

    # Resolver PR
    pr_num = args.pr
    if pr_num is None:
        prs = resolve_prs(fm)
        if not prs:
            # try linked by issue
            issue = resolve_issue(fm)
            if issue is None:
                die("sin PR vinculado en frontmatter y sin issue para buscar linked")
            data = gh_json(
                "pr", "list", "-R", repo, "--state", "open", "--limit", "20",
                "--search", f"#{issue}", "--json", "number,body",
            )
            candidates = []
            for pr in data:
                body = (pr.get("body") or "").lower()
                if any(kw in body for kw in ("closes ", "fixes ", "resolves ")):
                    candidates.append(pr["number"])
            if not candidates:
                die(f"no encuentro PR open vinculado a issue #{issue}; usa --pr")
            if len(candidates) > 1:
                die(f"varios PRs candidatos; usa --pr: {candidates}")
            pr_num = candidates[0]
        else:
            # último PR open de la lista
            for n in reversed(prs):
                info = gh_json("pr", "view", str(n), "-R", repo, "--json", "state")
                if info.get("state") == "OPEN":
                    pr_num = n
                    break
            if pr_num is None:
                die(f"todos los PRs en frontmatter están cerrados; usa --pr")

    target_label = LABELS["external_mergeable"] if args.verdict == "mergeable" else LABELS["external_needs"]
    opposite = LABELS["external_needs"] if args.verdict == "mergeable" else LABELS["external_mergeable"]

    banner(f"/pm cycle review-resolved — {args.slug} → {args.verdict}")
    log(f"PR: #{pr_num}")

    gh("pr", "edit", str(pr_num), "-R", repo,
       "--add-label", target_label,
       "--remove-label", opposite,
       check=False)
    gh("pr", "comment", str(pr_num), "-R", repo,
       "--body", f"[pm-sync] external review resolved: {args.verdict}",
       check=False)
    ok(f"label aplicado: {target_label}")

    if not args.no_sync:
        log("Ejecutando /pm sync (Step 5 evaluará auto-merge)")
        rc = subprocess.call(["python3", str(Path(__file__).parent / "pm_sync.py")])
        if rc != 0:
            log(f"sync devolvió rc={rc} (no fatal)")


if __name__ == "__main__":
    main()
