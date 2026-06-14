#!/usr/bin/env python3
"""pm_policy_adopt_prs — bulk-adopt PRs preexistentes.

Recorre `gh pr list --state open` y para cada PR sin label pm/policy-managed:
- añade pm/policy-managed
- clasifica internal según política:
    --default-internal skipped → asume light path (más conservador)
    --default-internal clean   → asume bucle limpio
    --default-internal escalated → atención humana
    --default-internal ask     → pregunta uno por uno
- añade label pm/internal-<verdict>
- comentario [pm-sync] PR adopted

NO añade external-* (decisión consciente del usuario después).

Usage:
    pm_policy_adopt_prs.py [--default-internal skipped|clean|escalated|ask]
                          [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import banner, die, find_pm_root, gh, gh_auth_check, gh_json, load_config, log, ok
from pm_lib.policy_defaults import LABELS


VALID = ["clean", "skipped", "escalated"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--default-internal", choices=VALID + ["ask"], default="skipped")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    gh_auth_check()
    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")
    repo = cfg["github"]["repo"]

    banner(f"/pm policy adopt-prs — {repo}")
    log(f"Default internal: {args.default_internal}")
    log(f"Modo: {'DRY-RUN' if args.dry_run else 'APPLY'}")

    prs = gh_json(
        "pr", "list", "-R", repo, "--state", "open", "--limit", "200",
        "--json", "number,title,labels,author",
    )
    if not prs:
        ok("(sin PRs open)")
        return

    adopted = skipped = 0
    print()
    print(f"{'#PR':<6} {'INT':<10} TITLE")
    for pr in prs:
        labels = [l["name"] for l in (pr.get("labels") or [])]
        if LABELS["managed"] in labels:
            print(f"#{pr['number']:<5} {'skip':<10} {pr['title'][:60]} (ya gestionado)")
            skipped += 1
            continue

        if args.default_internal == "ask":
            try:
                ans = input(f"  #{pr['number']} {pr['title'][:60]} → clean/skipped/escalated [skipped]: ").strip().lower()
            except EOFError:
                ans = "skipped"
            internal = ans if ans in VALID else "skipped"
        else:
            internal = args.default_internal

        print(f"#{pr['number']:<5} {internal:<10} {pr['title'][:60]}")
        if args.dry_run:
            adopted += 1
            continue

        internal_label = LABELS[f"internal_{internal}"]
        gh("pr", "edit", str(pr["number"]), "-R", repo,
           "--add-label", LABELS["managed"],
           "--add-label", internal_label,
           check=False)
        gh("pr", "comment", str(pr["number"]), "-R", repo,
           "--body", f"[pm-sync] PR adopted (internal={internal} by /pm policy adopt-prs)",
           check=False)
        adopted += 1

    print()
    ok(f"adopted: {adopted}, skipped: {skipped}")
    if adopted:
        print()
        print("Para cada PR adoptado, cuando estés listo para mergeo automático:")
        print("  /pm cycle review-resolved <slug> mergeable")


if __name__ == "__main__":
    main()
