"""Defaults para /pm next.

Sin weights numéricos configurables: solo presets cerrados, filtros
booleanos y listas de strings. Si los presets se quedan cortos en uso
real, se reconsideran (v2).
"""
from __future__ import annotations


# Presets disponibles. El default lo decide config (.pm/config.yaml) o
# el flag --preset. Cada preset es una tupla de tags que se traduce a
# orden de comparación en ranking.py.
PRESETS = ("wip-first", "priority-first", "small-wins", "stale-first")


DEFAULT_NEXT: dict = {
    "preset": "wip-first",
    "include_drafts": True,
    "include_active_without_pr": True,
    "include_board_statuses": ["Backlog", "Ready"],
    "exclude_labels": ["wontfix", "on-hold"],
    "blocking_labels": ["blocked", "waiting", "needs-design", "on-hold"],
    "default_top": 5,
}


# Mapeo priority → orden numérico (mayor = más urgente). Hardcoded; no
# configurable porque los nombres P0/P1/P2 son convención del sistema.
PRIORITY_RANK = {
    "P0": 3,
    "P1": 2,
    "P2": 1,
    "unknown": 0,
}


# Mapeo size → momentum score (mayor = más empuje al avance). S/M
# favorecidos sobre XS/L; XL al final. Mismo razonamiento: convención
# del sistema, hardcoded.
SIZE_MOMENTUM = {
    "S": 3,
    "M": 3,
    "XS": 2,
    "L": 2,
    "XL": 1,
    "unknown": 0,
}


# Fuentes posibles del candidate (ordenadas conceptualmente: WIP primero).
SOURCE_LABELS = {
    "spec_active_no_pr": "WIP (active sin PR)",
    "spec_draft":        "draft local",
    "board_with_spec":   "board + spec",
    "board_no_spec":     "board sin spec",
}
