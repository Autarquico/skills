"""Policy: carga, merge default→global→repo, eligibility evaluator.

`effective_policy(repo_cfg)` devuelve la policy efectiva para un repo
combinando, por orden de menos a más específico:

1. DEFAULT_POLICY (constante hardcoded en policy_defaults.py).
2. ~/.config/claudio/repo-policy.default.yaml (override global, opcional).
3. repo_cfg["policy"] (override per-repo en .pm/config.yaml).

`evaluate_eligibility(labels, policy)` devuelve un veredicto +
una lista de razones. Es el mirror de la lógica de la GitHub Action;
vivir en código permite testearla y compartirla.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _common import yaml_loads  # noqa: E402

from .policy_defaults import (  # noqa: E402
    DEFAULT_POLICY, LABELS, INTERNAL_LABELS, EXTERNAL_LABELS, BLOCKED_LABELS,
)


GLOBAL_OVERRIDE_PATH = Path(os.path.expanduser("~/.config/claudio/repo-policy.default.yaml"))


def _deep_merge(base: dict, overlay: dict) -> dict:
    """Merge key-by-key. Overlay wins; sub-dicts se mergean recursivamente."""
    out = dict(base)
    for k, v in (overlay or {}).items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _load_global_override() -> dict:
    if not GLOBAL_OVERRIDE_PATH.is_file():
        return {}
    data = yaml_loads(GLOBAL_OVERRIDE_PATH.read_text(encoding="utf-8")) or {}
    if isinstance(data, dict) and "policy" in data and isinstance(data["policy"], dict):
        return data["policy"]
    if isinstance(data, dict):
        return data
    return {}


def effective_policy(repo_cfg: dict) -> dict:
    """Calcula la policy efectiva. repo_cfg es el dict de .pm/config.yaml."""
    repo_policy = (repo_cfg or {}).get("policy") or {}
    global_override = _load_global_override()
    return _deep_merge(_deep_merge(DEFAULT_POLICY, global_override), repo_policy)


def raw_policy(repo_cfg: dict) -> dict:
    """Sólo el bloque policy del repo (sin merge). Útil para `show --raw`."""
    return (repo_cfg or {}).get("policy") or {}


# ---------------------------------------------------------------- eligibility


class Eligibility:
    """Resultado de evaluar el estado de un PR contra la policy."""
    def __init__(self):
        self.eligible: bool = False
        self.blockers: list[str] = []          # por qué NO es elegible
        self.warnings: list[str] = []          # cosas raras pero no bloqueantes
        self.internal_state: str = "unset"     # unset|clean|escalated|skipped
        self.external_state: str = "unset"     # unset|mergeable|needs-changes

    def to_dict(self) -> dict:
        return {
            "eligible": self.eligible,
            "blockers": self.blockers,
            "warnings": self.warnings,
            "internal_state": self.internal_state,
            "external_state": self.external_state,
        }


def _label_set(labels: Iterable[str]) -> set[str]:
    return {l for l in labels if isinstance(l, str)}


def _internal_state(labels: set[str]) -> tuple[str, str | None]:
    """Devuelve (estado, error) según los labels internal-* presentes."""
    present = labels & INTERNAL_LABELS
    if not present:
        return "unset", None
    if len(present) > 1:
        return "inconsistent", f"labels internal contradictorios: {sorted(present)}"
    label = next(iter(present))
    if label == LABELS["internal_clean"]:
        return "clean", None
    if label == LABELS["internal_escalated"]:
        return "escalated", None
    if label == LABELS["internal_skipped"]:
        return "skipped", None
    return "unset", None


def _external_state(labels: set[str]) -> tuple[str, str | None]:
    present = labels & EXTERNAL_LABELS
    if not present:
        return "unset", None
    if len(present) > 1:
        return "inconsistent", f"labels external contradictorios: {sorted(present)}"
    label = next(iter(present))
    if label == LABELS["external_mergeable"]:
        return "mergeable", None
    if label == LABELS["external_needs"]:
        return "needs-changes", None
    return "unset", None


def evaluate_eligibility(
    pr_labels: Iterable[str],
    policy: dict,
    *,
    pr_has_conflicts: bool = False,
    approvals_count: int = 0,
) -> Eligibility:
    """Decide si un PR es elegible para auto-merge bajo la policy efectiva.

    pr_labels: nombres de los labels del PR (string list).
    policy: la policy efectiva (de effective_policy()).
    pr_has_conflicts: True si gh marca el PR con conflictos.
    approvals_count: nº de approvals humanos en el PR.
    """
    result = Eligibility()
    labels = _label_set(pr_labels)

    if LABELS["managed"] not in labels:
        result.blockers.append("PR sin label pm/policy-managed; no gestionado por el sistema")
        return result

    if pr_has_conflicts:
        result.blockers.append("PR tiene conflictos de merge")

    internal_state, internal_err = _internal_state(labels)
    external_state, external_err = _external_state(labels)
    result.internal_state = internal_state
    result.external_state = external_state
    if internal_err:
        result.blockers.append(internal_err)
    if external_err:
        result.blockers.append(external_err)

    review = policy.get("review") or {}
    require_internal = bool(review.get("require_internal"))
    require_external = bool(review.get("require_external"))
    require_human = bool(review.get("require_human_approval"))
    light_ok = bool(review.get("light_path_ok_for_auto_merge"))

    if require_internal:
        if internal_state == "unset":
            result.blockers.append("falta label internal-* (require_internal=true)")
        elif internal_state == "escalated":
            result.blockers.append("internal review escaló; no mergear")
        elif internal_state == "skipped" and not light_ok:
            result.blockers.append("internal=skipped pero light_path_ok_for_auto_merge=false")

    if require_external:
        if external_state == "unset":
            result.blockers.append("falta label external-* (require_external=true)")
        elif external_state == "needs-changes":
            result.blockers.append("external review pidió cambios")

    if require_human and approvals_count < 1:
        result.blockers.append("falta aprobación humana (require_human_approval=true)")

    if not result.blockers:
        result.eligible = True
    return result
