"""Spec helpers: discover specs, resolve canonical issue/prs, write back fields.

`issue` and `prs` are the canonical fields used by `pm_cycle`. The legacy
`related_issues` list is preserved for backwards compatibility:

- `issue` (int): the single GitHub issue tracking this spec on the board.
- `prs` (list[int]): PRs opened against this spec, in order of opening.

When `issue` is absent, fall back to `related_issues[0]`.
When `prs` is absent, treat as empty.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow running both as `python3 -m pm_lib.specs` and via direct script imports.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _common import parse_frontmatter, write_frontmatter  # noqa: E402


SPECS_GLOB = "*.md"


def iter_specs(specs_dir: Path) -> list[Path]:
    """Return all spec files (legacy single-file format) under specs_dir,
    sorted by name. Archive directory is excluded."""
    if not specs_dir.is_dir():
        return []
    out = []
    for p in sorted(specs_dir.glob(SPECS_GLOB)):
        if p.is_file() and p.name != ".gitkeep":
            out.append(p)
    return out


def resolve_issue(fm: dict) -> int | None:
    """Return the single canonical issue for this spec, or None."""
    issue = fm.get("issue")
    if isinstance(issue, int):
        return issue
    related = fm.get("related_issues") or []
    if isinstance(related, list) and related:
        first = related[0]
        if isinstance(first, int):
            return first
    return None


def resolve_prs(fm: dict) -> list[int]:
    prs = fm.get("prs") or []
    if not isinstance(prs, list):
        return []
    return [p for p in prs if isinstance(p, int)]


def set_issue(fm: dict, issue: int) -> dict:
    """Update both `issue` (canonical) and `related_issues` (legacy)."""
    fm["issue"] = issue
    related = fm.get("related_issues") or []
    if not isinstance(related, list):
        related = []
    if issue not in related:
        related = [issue, *related]
    fm["related_issues"] = related
    return fm


def add_pr(fm: dict, pr: int) -> dict:
    prs = resolve_prs(fm)
    if pr not in prs:
        prs.append(pr)
    fm["prs"] = prs
    return fm


def slug_of(spec_path: Path) -> str:
    return spec_path.stem


def find_spec(specs_dir: Path, slug: str) -> Path | None:
    p = specs_dir / f"{slug}.md"
    return p if p.is_file() else None
