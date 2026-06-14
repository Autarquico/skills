#!/usr/bin/env python3
"""pm_sync — reconcilia board ← PRs, specs ← board, STATUS.md ← board.

Pasos:
  1. Fetch: PRs (open + merged en ventana), issues, specs, project items.
  2. Reconcile board ← evidencia: PR mergeado con Closes #N → issue Done + comment.
  3. Sync specs ← board: specs con todos sus related_issues cerrados → status: shipped.
  4. Regen STATUS.md entre markers HTML <!-- pm-sync:* -->.

Idempotente: dedupe comentarios [pm-sync] antes de añadir.

Usage:
    pm_sync.py [--dry-run] [--since YYYY-MM-DD] [--only board|specs|status]

Exit codes:
    0 ok, 1 error fatal, 2 sync parcial
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    banner, die, find_pm_root, gh, gh_auth_check, gh_json, load_config, log,
    ok, parse_frontmatter, today, warn, write_frontmatter,
)


CLOSES_RE = re.compile(
    r"(?:closes|close|closed|fixes|fix|fixed|resolves|resolve|resolved)\s+#(\d+)",
    re.IGNORECASE,
)
PM_SYNC_TAG = "[pm-sync]"


def fetch_prs(repo: str, since: str) -> list[dict]:
    """Open + merged PRs since date. State all to cover both."""
    fields = "number,title,state,isDraft,author,mergedAt,closedAt,body,headRefName"
    data = gh_json("pr", "list", "-R", repo, "--state", "all",
                   "--limit", "300", "--json", fields,
                   "--search", f"updated:>={since}")
    return data


def fetch_issues(repo: str) -> dict[int, dict]:
    """All issues (open + closed recently) indexed by number."""
    fields = "number,title,state,closedAt,labels"
    data = gh_json("issue", "list", "-R", repo, "--state", "all",
                   "--limit", "500", "--json", fields)
    return {i["number"]: i for i in data}


def fetch_issue_comments(repo: str, issue_num: int) -> list[dict]:
    data = gh_json("issue", "view", str(issue_num), "-R", repo,
                   "--json", "comments")
    return data.get("comments", [])


def has_pm_sync_comment(comments: list[dict], match: str) -> bool:
    for c in comments:
        body = c.get("body", "")
        if PM_SYNC_TAG in body and match in body:
            return True
    return False


def add_issue_comment(repo: str, issue_num: int, body: str, dry: bool) -> None:
    if dry:
        log(f"   [dry] comment #{issue_num}: {body[:70]}")
        return
    gh("issue", "comment", str(issue_num), "-R", repo, "--body", body)


def close_issue(repo: str, issue_num: int, reason: str, dry: bool) -> None:
    if dry:
        log(f"   [dry] close #{issue_num}: {reason}")
        return
    gh("issue", "close", str(issue_num), "-R", repo, "--reason", "completed")


def find_specs(pm_root: Path, cfg: dict) -> list[Path]:
    specs_dir = pm_root / cfg["paths"]["specs"]
    if not specs_dir.is_dir():
        return []
    return sorted(p for p in specs_dir.glob("*.md") if p.is_file())


def closes_issues(body: str | None) -> list[int]:
    if not body:
        return []
    return [int(m.group(1)) for m in CLOSES_RE.finditer(body)]


# --------- STATUS.md regen


MARKER_BEGIN = "<!-- pm-sync:%s -->"
MARKER_END = "<!-- /pm-sync:%s -->"


def replace_marker_block(text: str, name: str, content: str) -> tuple[str, bool]:
    begin = MARKER_BEGIN % name
    end = MARKER_END % name
    pattern = re.compile(
        re.escape(begin) + r".*?" + re.escape(end),
        re.DOTALL,
    )
    if not pattern.search(text):
        return text, False
    new = pattern.sub(begin + "\n" + content.rstrip() + "\n" + end, text)
    return new, new != text


def status_section(title: str, items: list[str]) -> str:
    if not items:
        return f"_(nada)_"
    return "\n".join(f"- {x}" for x in items)


def regen_status(pm_root: Path, cfg: dict, issues: dict[int, dict],
                 prs: list[dict], since: str, dry: bool) -> int:
    status_path = pm_root / cfg["paths"]["tracking"]["status"]
    if not status_path.is_file():
        warn(f"STATUS.md no existe ({status_path}); skip step 4.")
        return 0
    text = status_path.read_text(encoding="utf-8")

    # Done this week
    done = []
    for num, iss in sorted(issues.items()):
        if iss["state"] == "CLOSED" and iss.get("closedAt"):
            if iss["closedAt"][:10] >= since:
                done.append(f"#{num} {iss['title']}")
    # In progress: issues open with linked open PR
    open_issue_nums = {n for n, i in issues.items() if i["state"] == "OPEN"}
    in_progress_nums: set[int] = set()
    for pr in prs:
        if pr["state"] == "OPEN":
            for n in closes_issues(pr.get("body")):
                if n in open_issue_nums:
                    in_progress_nums.add(n)
    in_progress = [f"#{n} {issues[n]['title']}" for n in sorted(in_progress_nums)]
    # Blocked: labeled
    blocked = []
    for num, iss in sorted(issues.items()):
        if iss["state"] == "OPEN" and any(
            (l.get("name") or "").lower() in ("blocked", "bloqueado")
            for l in iss.get("labels", [])
        ):
            blocked.append(f"#{num} {iss['title']}")

    changes = 0
    for marker_name, items in (
        ("done-this-week", done),
        ("in-progress", in_progress),
        ("blocked", blocked),
    ):
        new_text, changed = replace_marker_block(text, marker_name, status_section(marker_name, items))
        if changed:
            text = new_text
            changes += 1

    if changes and not dry:
        status_path.write_text(text, encoding="utf-8")
        ok(f"STATUS.md regenerado ({changes} secciones)")
    elif changes:
        log(f"[dry] STATUS.md regeneraría {changes} secciones")
    else:
        log("STATUS.md sin cambios")
    return changes


# --------- Main reconciliation


def reconcile_board(repo: str, prs: list[dict], issues: dict[int, dict], dry: bool) -> int:
    """For each merged PR with Closes #N: ensure issue is closed + has [pm-sync] comment."""
    moved = 0
    for pr in prs:
        if pr["state"] != "MERGED":
            continue
        closed_nums = closes_issues(pr.get("body"))
        for n in closed_nums:
            iss = issues.get(n)
            if not iss:
                continue
            if iss["state"] == "CLOSED":
                # Still need to verify pm-sync comment exists; if not, add it
                comments = fetch_issue_comments(repo, n)
                marker = f"merged via PR #{pr['number']}"
                if not has_pm_sync_comment(comments, marker):
                    add_issue_comment(
                        repo, n,
                        f"{PM_SYNC_TAG} Closed: {marker}.", dry,
                    )
                    moved += 1
                continue
            # Issue still open but PR merged → close it
            comments = fetch_issue_comments(repo, n)
            marker = f"merged via PR #{pr['number']}"
            if not has_pm_sync_comment(comments, marker):
                add_issue_comment(repo, n, f"{PM_SYNC_TAG} Closing: {marker}.", dry)
            close_issue(repo, n, marker, dry)
            moved += 1
            if not dry:
                issues[n]["state"] = "CLOSED"
                issues[n]["closedAt"] = datetime.utcnow().isoformat() + "Z"
    return moved


def _pr_index_by_issue(prs: list[dict]) -> dict[int, list[int]]:
    """Map issue_number → [pr_number, ...] descubiertos vía Closes #N."""
    idx: dict[int, list[int]] = {}
    for pr in prs:
        for n in closes_issues(pr.get("body")):
            idx.setdefault(n, [])
            num = pr.get("number")
            if isinstance(num, int) and num not in idx[n]:
                idx[n].append(num)
    return idx


def _archive_target(archive_dir: Path, spec_path: Path, when: str) -> Path:
    """Path destino con prefijo de fecha. Idempotente: si ya existe, devuelve None."""
    return archive_dir / f"{when}-{spec_path.name}"


def sync_specs(pm_root: Path, cfg: dict, issues: dict[int, dict],
               prs: list[dict], dry: bool) -> int:
    """Specs cuyos related_issues están todos cerrados → status: shipped.

    También mantiene `issue` (singular canonical) y `prs` en frontmatter
    al día. Archive con prefijo de fecha YYYY-MM-DD-<slug>.md, idempotente.
    """
    archive_on_ship = cfg.get("sync", {}).get("archive_on_ship", False)
    archive_dir = pm_root / cfg["paths"]["specs_archive"]
    pr_idx = _pr_index_by_issue(prs)
    changed = 0
    for spec_path in find_specs(pm_root, cfg):
        try:
            fm, body = parse_frontmatter(spec_path)
        except SystemExit:
            continue
        if fm.get("status") in ("shipped", "abandoned"):
            continue
        rel = fm.get("related_issues") or []

        # Mantener `issue` (singular) y `prs` al día — incluso si aún no se shippea.
        fm_dirty = False
        if not fm.get("issue") and rel:
            fm["issue"] = rel[0]
            fm_dirty = True
        canonical_issue = fm.get("issue")
        if canonical_issue:
            existing_prs = fm.get("prs") or []
            if not isinstance(existing_prs, list):
                existing_prs = []
            new_prs = [p for p in pr_idx.get(int(canonical_issue), []) if p not in existing_prs]
            if new_prs:
                fm["prs"] = existing_prs + new_prs
                fm_dirty = True

        ship = bool(rel) and all(
            (issues.get(int(n), {}).get("state") == "CLOSED") for n in rel
        )
        if ship:
            fm["status"] = "shipped"
            fm["updated"] = today()
            fm_dirty = True

        if not fm_dirty:
            continue

        if dry:
            log(f"[dry] update frontmatter: {spec_path.name}"
                + (" (shipped)" if ship else ""))
        else:
            write_frontmatter(spec_path, fm, body)
            if ship:
                ok(f"shipped: {spec_path.name}")
            else:
                log(f"frontmatter actualizado: {spec_path.name}")

        if ship and archive_on_ship:
            target = _archive_target(archive_dir, spec_path, today())
            if target.exists():
                warn(f"  archive ya existe ({target.name}); skip rename")
            else:
                if dry:
                    log(f"  [dry] → {target.relative_to(pm_root)}")
                else:
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    spec_path.rename(target)
                    log(f"  → {target.relative_to(pm_root)}")
        changed += 1
    return changed


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--since", help="YYYY-MM-DD (default: hace 7 días)")
    ap.add_argument("--only", choices=["board", "specs", "status"])
    args = ap.parse_args()

    gh_auth_check()
    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")
    repo = cfg["github"]["repo"]
    since_days = cfg.get("sync", {}).get("default_since_days", 7)
    since = args.since or (date.today() - timedelta(days=since_days)).isoformat()

    banner(f"/pm sync — {cfg['codename']} — {today()}")
    log(f"Repo:    {repo}")
    log(f"Periodo: {since} → ahora")
    log(f"Modo:    {'DRY-RUN' if args.dry_run else 'APPLY'}")

    log("Fetching PRs...")
    prs = fetch_prs(repo, since)
    log(f"  {len(prs)} PRs en ventana")
    log("Fetching issues...")
    issues = fetch_issues(repo)
    log(f"  {len(issues)} issues")

    board_moves = 0
    spec_changes = 0
    status_changes = 0
    if args.only in (None, "board"):
        log("Step 2: reconcile board ← PRs")
        board_moves = reconcile_board(repo, prs, issues, args.dry_run)
        log(f"  {board_moves} issues actualizados")
    if args.only in (None, "specs"):
        log("Step 3: sync specs ← board")
        spec_changes = sync_specs(pm_root, cfg, issues, prs, args.dry_run)
        log(f"  {spec_changes} specs marcadas como shipped")
    if args.only in (None, "status"):
        log("Step 4: regen STATUS.md")
        status_changes = regen_status(pm_root, cfg, issues, prs, since, args.dry_run)

    log("Resumen:")
    log(f"  board   {board_moves}")
    log(f"  specs   {spec_changes}")
    log(f"  status  {status_changes}")
    if args.dry_run:
        ok("DRY-RUN: nada mutado.")
    else:
        ok("sync completo.")


if __name__ == "__main__":
    main()
