"""Defaults hardcoded de la repo policy.

Estos valores son los que toda policy hereda salvo override explícito,
ya sea en `~/.config/claudio/repo-policy.default.yaml` (override global
opcional) o en `.pm/config.yaml` del repo bajo el bloque `policy:`.

Vivir aquí en código (no en YAML externo) garantiza:
- El paquete es autosuficiente.
- Migraciones (renombrar keys, añadir campos) son tracables vía git.
- No hay "magia" sin código que la documente.
"""
from __future__ import annotations


DEFAULT_POLICY: dict = {
    "branch": {
        "default": "main",
        "naming": "<type>/<slug>",
        "delete_after_merge": True,
    },
    "commits": {
        "conventional": True,
        "co_author": "Claude Opus 4.7 (1M context) <noreply@anthropic.com>",
        "sign": False,
    },
    "pr": {
        "draft_first": False,
        "title_format": "<type>(<scope>): <subject>",
        "body_max_kb": 20,
        "labels_managed": ["pm-managed"],
        "assignees": ["@me"],
        "reviewers": [],
        "teams": [],
    },
    "ci": {
        "wait_for_checks": "all",       # all | listed
        "required_checks": [],
        "timeout_minutes": 30,
    },
    "review": {
        "require_internal": True,
        "require_external": True,
        "require_human_approval": False,
        "light_path_ok_for_auto_merge": False,
    },
    "merge": {
        "strategy": "squash",            # squash | rebase | merge
        "auto_merge": "conditional",     # conditional | manual
    },
    "merge_handoff": {
        "method": "none",                # github_action | external | runbook | none
        "triggers_on": ["main"],
        "smoke_url": "",
        "runbook": "",
    },
    "rollback": {
        "method": "revert-pr",           # revert-pr | redeploy-previous | manual
        "runbook": "",
    },
}


PRESETS: dict[str, dict] = {
    "conservative": {
        "review": {"require_human_approval": True},
        "merge": {"auto_merge": "manual"},
    },
    "standard": {
        # mismo que default — explícito para claridad
        "review": {"require_human_approval": False},
        "merge": {"auto_merge": "conditional"},
    },
    "solo": {
        "review": {
            "require_human_approval": False,
            "light_path_ok_for_auto_merge": True,
        },
        "merge": {"auto_merge": "conditional"},
    },
}


# Labels canónicos del sistema. Cualquier otra cosa con prefijo `pm/` que
# no aparezca aquí es responsabilidad del usuario.
LABELS = {
    "managed":              "pm/policy-managed",
    "internal_clean":       "pm/internal-clean",
    "internal_escalated":   "pm/internal-escalated",
    "internal_skipped":     "pm/internal-skipped",
    "external_mergeable":   "pm/external-mergeable",
    "external_needs":       "pm/external-needs-changes",
    "automerge_eligible":   "pm/automerge-eligible",
    "blocked_inconsistent": "pm/blocked-inconsistent",
    "blocked_conflicts":    "pm/blocked-conflicts",
}

INTERNAL_LABELS = {LABELS["internal_clean"], LABELS["internal_escalated"], LABELS["internal_skipped"]}
EXTERNAL_LABELS = {LABELS["external_mergeable"], LABELS["external_needs"]}
BLOCKED_LABELS  = {LABELS["blocked_inconsistent"], LABELS["blocked_conflicts"]}
