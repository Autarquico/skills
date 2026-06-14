#!/usr/bin/env python3
"""pm_policy_state — decodifica el estado de un PR según labels + policy.

Imprime:
- labels presentes
- estado internal/external derivado
- veredicto: elegible o no, y qué falta

Read-only. Útil para debuggear por qué un PR no se está auto-mergeando.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import banner, die, find_pm_root, gh_auth_check, gh_json, load_config
from pm_lib.policy import effective_policy, evaluate_eligibility
from pm_lib.policy_defaults import LABELS


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pr", type=int, help="número de PR")
    args = ap.parse_args()

    gh_auth_check()
    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")
    repo = cfg["github"]["repo"]
    policy = effective_policy(cfg)

    data = gh_json(
        "pr", "view", str(args.pr), "-R", repo,
        "--json", "number,title,labels,mergeable,reviews,state,autoMergeRequest",
    )
    labels = [l["name"] for l in (data.get("labels") or [])]
    mergeable_str = data.get("mergeable") or "UNKNOWN"
    has_conflicts = mergeable_str == "CONFLICTING"
    approvals = sum(1 for r in (data.get("reviews") or []) if r.get("state") == "APPROVED")
    auto_merge_active = data.get("autoMergeRequest") is not None

    e = evaluate_eligibility(
        labels, policy,
        pr_has_conflicts=has_conflicts,
        approvals_count=approvals,
    )

    banner(f"PR #{args.pr} — {data.get('title','')[:60]}")
    print(f"State:        {data.get('state')}")
    print(f"Mergeable:    {mergeable_str}")
    print(f"Approvals:    {approvals}")
    print(f"Auto-merge:   {'enabled' if auto_merge_active else 'disabled'}")
    print()
    print("Labels presentes:")
    if not labels:
        print("  (ninguno)")
    for l in sorted(labels):
        prefix = "✓" if l.startswith("pm/") else "·"
        print(f"  {prefix} {l}")
    print()
    print(f"Estado internal: {e.internal_state}")
    print(f"Estado external: {e.external_state}")
    print()
    print(f"Auto-merge eligible: {'sí' if e.eligible else 'NO'}")
    if e.blockers:
        print("Razones por las que no:")
        for b in e.blockers:
            print(f"  ! {b}")
    if e.warnings:
        print("Avisos:")
        for w in e.warnings:
            print(f"  ⚠ {w}")


if __name__ == "__main__":
    main()
