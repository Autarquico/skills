#!/usr/bin/env python3
"""pm_bots_process — triage de PRs de bots.

Matriz de decisiones:
    CI verde + patch/minor + sin conflictos  → MERGE
    Superseded (PR más nuevo del mismo pkg)   → CLOSE
    Conflictos + stale (>N días)              → CLOSE
    Major                                     → SKIP
    CI rojo (no por conflicto)                → SKIP
    Security update                           → MERGE prioritario

Dry-run por defecto. --apply para ejecutar.

Usage:
    pm_bots_process.py [--apply] [--only merge|close] [--include-major]
                       [--stale-days N] [--delete-branches]

Exit codes: 0 ok, 1 error fatal, 2 algunas acciones fallaron.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    banner, die, find_pm_root, gh, gh_auth_check, gh_json, load_config, log,
    ok, today, warn,
)


DEFAULT_BOT_AUTHORS = ("dependabot[bot]", "renovate[bot]", "github-actions[bot]")
DEFAULT_TITLE_PATTERNS = (r"^chore\(deps\):", r"^chore: bump ", r"^build\(deps\):")
PM_SYNC_TAG = "[pm-sync]"

# Parse "Bump <pkg> from A.B.C to X.Y.Z"
BUMP_RE = re.compile(
    r"[Bb]ump\s+([A-Za-z0-9_\-./@]+)\s+from\s+v?([\d.]+)\s+to\s+v?([\d.]+)"
)


def get_cleanup_config(cfg: dict) -> dict:
    gh_cfg = cfg.get("gh", {}) or {}
    cleanup = gh_cfg.get("cleanup", {}) or {}
    return {
        "bot_authors": cleanup.get("bot_authors") or list(DEFAULT_BOT_AUTHORS),
        "title_patterns": cleanup.get("title_patterns") or list(DEFAULT_TITLE_PATTERNS),
        "stale_days": cleanup.get("stale_days") or 30,
        "auto_merge_levels": cleanup.get("auto_merge_levels") or ["patch", "minor"],
        "delete_branches": bool(cleanup.get("delete_branches")),
    }


def fetch_bot_prs(repo: str, authors: list[str], title_patterns: list[str]) -> list[dict]:
    fields = "number,title,author,state,mergeable,headRefName,updatedAt,createdAt,labels,body,isDraft,mergeStateStatus"
    data = gh_json("pr", "list", "-R", repo, "--state", "open",
                   "--limit", "200", "--json", fields)
    pats = [re.compile(p) for p in title_patterns]
    out = []
    for pr in data:
        author = (pr.get("author") or {}).get("login", "")
        title = pr.get("title", "")
        if author in authors or any(p.search(title) for p in pats):
            out.append(pr)
    return out


def get_pr_checks(repo: str, number: int) -> str:
    """Returns 'pass' | 'fail' | 'pending' | 'none'."""
    r = gh("pr", "checks", str(number), "-R", repo, check=False)
    output = (r.stdout or "") + "\n" + (r.stderr or "")
    if r.returncode == 0:
        return "pass" if output.strip() else "none"
    if "no checks" in output.lower():
        return "none"
    if "pending" in output.lower() or "in progress" in output.lower():
        return "pending"
    return "fail"


def parse_bump(title: str) -> tuple[str, str, str] | None:
    m = BUMP_RE.search(title)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def semver_level(from_v: str, to_v: str) -> str:
    a = from_v.split(".")
    b = to_v.split(".")
    while len(a) < 3:
        a.append("0")
    while len(b) < 3:
        b.append("0")
    if a[0] != b[0]:
        return "major"
    if a[1] != b[1]:
        return "minor"
    if a[2] != b[2]:
        return "patch"
    return "patch"


def is_security(pr: dict) -> bool:
    labels = [(l.get("name") or "").lower() for l in pr.get("labels") or []]
    return any("security" in l for l in labels)


def is_stale(pr: dict, days: int) -> bool:
    upd = pr.get("updatedAt")
    if not upd:
        return False
    try:
        dt = datetime.fromisoformat(upd.replace("Z", "+00:00"))
    except ValueError:
        return False
    return datetime.now(timezone.utc) - dt > timedelta(days=days)


def classify(prs: list[dict], cfg: dict, include_major: bool, stale_days: int,
             auto_merge_levels: list[str], repo: str) -> list[dict]:
    """Return list of {pr, action, reason}."""
    # Group by package to detect superseded
    by_pkg: dict[str, list[dict]] = {}
    for pr in prs:
        bump = parse_bump(pr.get("title", ""))
        if bump:
            pkg = bump[0]
            by_pkg.setdefault(pkg, []).append(pr)

    # Sort each group by number desc; older = superseded
    superseded: set[int] = set()
    for pkg, group in by_pkg.items():
        if len(group) <= 1:
            continue
        group.sort(key=lambda p: p["number"], reverse=True)
        for pr in group[1:]:
            superseded.add(pr["number"])

    plan = []
    for pr in prs:
        num = pr["number"]
        title = pr.get("title", "")
        bump = parse_bump(title)
        mergeable = (pr.get("mergeable") or "").upper()  # MERGEABLE, CONFLICTING, UNKNOWN
        if num in superseded:
            newer = next((p["number"] for p in by_pkg[bump[0]] if p["number"] > num), None)
            plan.append({"pr": pr, "action": "CLOSE", "reason": f"superseded by #{newer}"})
            continue
        if mergeable == "CONFLICTING" and is_stale(pr, stale_days):
            plan.append({"pr": pr, "action": "CLOSE",
                         "reason": f"stale {stale_days}d con conflicts"})
            continue
        if is_security(pr):
            checks = get_pr_checks(repo, num)
            if checks in ("pass", "none") and mergeable == "MERGEABLE":
                plan.append({"pr": pr, "action": "MERGE", "reason": "security update"})
            else:
                plan.append({"pr": pr, "action": "SKIP",
                             "reason": f"security pero checks={checks} mergeable={mergeable}"})
            continue
        if not bump:
            plan.append({"pr": pr, "action": "SKIP", "reason": "no parsea como bump"})
            continue
        level = semver_level(bump[1], bump[2])
        if level == "major" and not include_major:
            plan.append({"pr": pr, "action": "SKIP",
                         "reason": f"major {bump[1]}→{bump[2]} (usa --include-major)"})
            continue
        if level not in auto_merge_levels:
            plan.append({"pr": pr, "action": "SKIP",
                         "reason": f"level {level} no en auto_merge_levels"})
            continue
        if mergeable == "CONFLICTING":
            plan.append({"pr": pr, "action": "SKIP", "reason": "conflictos (no stale)"})
            continue
        checks = get_pr_checks(repo, num)
        if checks == "fail":
            plan.append({"pr": pr, "action": "SKIP", "reason": "CI rojo"})
            continue
        if checks == "pending":
            plan.append({"pr": pr, "action": "SKIP", "reason": "CI pending"})
            continue
        plan.append({"pr": pr, "action": "MERGE", "reason": f"{level}, CI {checks}"})
    return plan


def execute(plan: list[dict], repo: str, dry: bool, delete_branches: bool) -> tuple[int, int]:
    done = 0
    errors = 0
    for entry in plan:
        pr = entry["pr"]
        num = pr["number"]
        action = entry["action"]
        reason = entry["reason"]
        if action == "SKIP":
            continue
        comment = f"{PM_SYNC_TAG} {action.lower()}: {reason}"
        if dry:
            log(f"[dry] {action} #{num} ({reason})")
            continue
        try:
            if action == "MERGE":
                gh("pr", "comment", str(num), "-R", repo, "--body", comment)
                merge_args = ["pr", "merge", str(num), "-R", repo, "--squash"]
                if delete_branches:
                    merge_args.append("--delete-branch")
                gh(*merge_args)
                ok(f"merged #{num}")
            elif action == "CLOSE":
                gh("pr", "comment", str(num), "-R", repo, "--body", comment)
                gh("pr", "close", str(num), "-R", repo,
                   *(["--delete-branch"] if delete_branches else []))
                ok(f"closed #{num}")
            done += 1
        except SystemExit:
            errors += 1
            warn(f"acción {action} en #{num} falló")
    return done, errors


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true", help="Ejecuta acciones (por defecto dry-run)")
    ap.add_argument("--only", choices=["merge", "close"])
    ap.add_argument("--include-major", action="store_true")
    ap.add_argument("--stale-days", type=int)
    ap.add_argument("--delete-branches", action="store_true")
    args = ap.parse_args()

    gh_auth_check()
    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")
    repo = cfg["github"]["repo"]
    cleanup_cfg = get_cleanup_config(cfg)
    stale_days = args.stale_days or cleanup_cfg["stale_days"]
    delete_branches = args.delete_branches or cleanup_cfg["delete_branches"]

    banner(f"/pm bots process — {repo} — {today()}")
    log(f"Modo: {'APPLY' if args.apply else 'DRY-RUN'}")

    prs = fetch_bot_prs(repo, cleanup_cfg["bot_authors"], cleanup_cfg["title_patterns"])
    log(f"PRs de bots detectados: {len(prs)}")
    if not prs:
        ok("Nada que procesar.")
        return

    plan = classify(prs, cfg, args.include_major, stale_days,
                    cleanup_cfg["auto_merge_levels"], repo)

    if args.only:
        target = "MERGE" if args.only == "merge" else "CLOSE"
        for entry in plan:
            if entry["action"] != target and entry["action"] != "SKIP":
                entry["action"] = "SKIP"
                entry["reason"] = f"filtered by --only {args.only}"

    # Resumen
    counts = {"MERGE": 0, "CLOSE": 0, "SKIP": 0}
    for entry in plan:
        counts[entry["action"]] += 1
    log(f"Plan: MERGE={counts['MERGE']}  CLOSE={counts['CLOSE']}  SKIP={counts['SKIP']}")
    log("")
    for entry in plan:
        pr = entry["pr"]
        log(f"  #{pr['number']:4d}  {entry['action']:6s}  {pr['title'][:60]:60s}  · {entry['reason']}")
    log("")

    done, errors = execute(plan, repo, not args.apply, delete_branches)

    if args.apply:
        ok(f"{done} acciones aplicadas. errores: {errors}")
        if errors:
            sys.exit(2)
    else:
        log("Ejecuta con --apply para aplicar.")


if __name__ == "__main__":
    main()
