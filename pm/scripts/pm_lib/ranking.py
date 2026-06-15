"""Ranking lexicográfico de candidates para /pm next.

Sin fórmulas de score sumando weights heterogéneos. Comparación por
tupla determinista: blocked → wip → priority → size momentum → age → slug.

Funciones puras: dado un Candidate y un preset, generan la tupla de
ordenación. `sorted(candidates, key=lambda c: sort_key(c, preset))`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .next_defaults import PRIORITY_RANK, SIZE_MOMENTUM


@dataclass
class Candidate:
    slug: str
    issue: int | None
    title: str
    priority: str               # P0|P1|P2|unknown
    size: str                   # XS|S|M|L|XL|unknown
    source: str                 # spec_active_no_pr | spec_draft | board_with_spec | board_no_spec
    age_days: int
    blocked: bool = False
    blockers: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)

    @property
    def is_wip(self) -> bool:
        return self.source == "spec_active_no_pr"

    @property
    def reasons(self) -> list[str]:
        out: list[str] = []
        if self.is_wip:
            out.append("WIP active sin PR")
        if self.priority != "unknown":
            out.append(self.priority)
        if self.blocked:
            out.append(f"bloqueado por {', '.join(self.blockers) or 'razón desconocida'}")
        if not self.blocked and self.age_days > 0:
            out.append(f"{self.age_days}d")
        return out


def sort_key(c: Candidate, preset: str) -> tuple:
    """Devuelve la tupla de comparación para sorted().

    Convención: menor tupla = aparece antes en el output (ranking más
    alto). Usamos negativos para los "más es mejor".
    """
    p_rank = PRIORITY_RANK.get(c.priority, 0)
    s_mom = SIZE_MOMENTUM.get(c.size, 0)

    if preset == "wip-first":
        return (
            c.blocked,            # False < True (blocked al final)
            not c.is_wip,         # is_wip=True (False) antes que False (True)
            -p_rank,              # mayor rank antes
            -s_mom,               # mayor momentum antes
            -c.age_days,          # más viejo antes
            c.slug,               # desempate alfabético
        )

    if preset == "priority-first":
        return (
            c.blocked,
            -p_rank,
            -s_mom,
            -c.age_days,
            c.slug,
        )

    if preset == "small-wins":
        return (
            c.blocked,
            -s_mom,
            -p_rank,
            -c.age_days,
            c.slug,
        )

    if preset == "stale-first":
        return (
            c.blocked,
            -c.age_days,
            -p_rank,
            -s_mom,
            c.slug,
        )

    # Fallback: como wip-first
    return sort_key(c, "wip-first")


def rank(candidates: list[Candidate], preset: str,
         include_blocked: bool = False) -> list[Candidate]:
    """Ordena y opcionalmente filtra los bloqueados."""
    items = candidates if include_blocked else [c for c in candidates if not c.blocked]
    return sorted(items, key=lambda c: sort_key(c, preset))


def classify_source(*, has_spec: bool, has_issue: bool, spec_status: str | None,
                    has_pr: bool) -> str:
    """Decide la categoría del candidate.

    - spec_active_no_pr: spec local con status=active y sin PRs.
    - spec_draft: spec local con status=draft, sin issue (a punto de promoverse).
    - board_with_spec: item del board que tiene spec local asociada (no encajada en las dos anteriores).
    - board_no_spec: item del board sin spec local.
    """
    if has_spec:
        if spec_status == "active" and not has_pr:
            return "spec_active_no_pr"
        if spec_status == "draft" and not has_issue:
            return "spec_draft"
        return "board_with_spec"
    return "board_no_spec"


def is_blocked_by_deps(
    depends_on: Iterable[str],
    spec_statuses: dict[str, str],
) -> tuple[bool, list[str]]:
    """Decide si una spec está bloqueada por sus depends_on.

    spec_statuses: mapping slug → status. Si algún dep no está shipped
    ni abandoned, está bloqueado.
    """
    blocking: list[str] = []
    for dep in depends_on or []:
        st = spec_statuses.get(dep)
        if st not in ("shipped", "abandoned"):
            blocking.append(dep)
    return (len(blocking) > 0, blocking)


def is_blocked_by_labels(
    labels: Iterable[str],
    blocking_labels: Iterable[str],
) -> tuple[bool, list[str]]:
    """Decide si está bloqueado por labels en el issue."""
    blocking_set = {l.lower() for l in blocking_labels}
    hits = [l for l in (labels or []) if l.lower() in blocking_set]
    return (len(hits) > 0, hits)


def detect_inconsistencies(
    specs: list[dict],
    issues_by_num: dict[int, dict],
) -> list[dict]:
    """Detecta estados inconsistentes entre spec y board.

    Cada inconsistencia: {slug, kind, issue?, remediation}.
    """
    out: list[dict] = []
    for spec in specs:
        slug = spec.get("slug") or "unknown"
        status = spec.get("status")
        issue_num = spec.get("issue")

        if status == "shipped" and issue_num:
            iss = issues_by_num.get(issue_num)
            if iss and iss.get("state") == "OPEN":
                out.append({
                    "slug": slug,
                    "kind": "spec_shipped_issue_open",
                    "issue": issue_num,
                    "remediation": "ejecuta /pm sync para reconciliar o reabrir manualmente la spec",
                })
        elif status == "active" and issue_num:
            iss = issues_by_num.get(issue_num)
            if iss and iss.get("state") == "CLOSED":
                out.append({
                    "slug": slug,
                    "kind": "spec_active_issue_closed",
                    "issue": issue_num,
                    "remediation": "ejecuta /pm sync (la spec debería pasar a shipped)",
                })
        # spec activa con todos PRs mergeados → debería ser shipped
        if status == "active":
            prs = spec.get("prs") or []
            pr_states = spec.get("_pr_states", [])
            if prs and pr_states and all(s == "MERGED" for s in pr_states):
                out.append({
                    "slug": slug,
                    "kind": "spec_active_all_prs_merged",
                    "issue": issue_num,
                    "remediation": "ejecuta /pm sync (todos los PRs mergeados; spec debería ser shipped)",
                })
    return out
