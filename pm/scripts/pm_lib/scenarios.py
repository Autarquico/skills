"""Parse Given/When/Then scenarios from a spec markdown body.

Format expected:

    ### Scenario: <title>
    - **Given** ...
    - **When** ...
    - **Then** ...

The parser is tolerant: `Given/When/Then` can be in **bold**, plain, or
after a `- ` bullet. Multiple lines per clause are joined. Anything
between scenarios that isn't part of one is ignored.

Returns a list of dicts: {title, given, when, then, line, raw}.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


_SCENARIO_RE = re.compile(r"^###\s+Scenario\s*:\s*(.+?)\s*$", re.IGNORECASE)
_CLAUSE_RE = re.compile(
    r"^\s*[-*]?\s*(?:\*\*)?(Given|When|Then|And|But)(?:\*\*)?\s+(.+?)\s*$",
    re.IGNORECASE,
)


@dataclass
class Scenario:
    title: str
    given: str
    when: str
    then: str
    line: int
    raw: str

    def is_complete(self) -> bool:
        return bool(self.given and self.when and self.then)

    def missing(self) -> list[str]:
        return [k for k in ("given", "when", "then") if not getattr(self, k)]


def parse(body: str) -> list[Scenario]:
    lines = body.splitlines()
    out: list[Scenario] = []
    i = 0
    while i < len(lines):
        m = _SCENARIO_RE.match(lines[i])
        if not m:
            i += 1
            continue
        title = m.group(1).strip()
        start = i
        i += 1
        clauses: dict[str, list[str]] = {"given": [], "when": [], "then": []}
        current: str | None = None
        while i < len(lines):
            ln = lines[i]
            if _SCENARIO_RE.match(ln) or ln.startswith("## "):
                break
            cm = _CLAUSE_RE.match(ln)
            if cm:
                tag = cm.group(1).lower()
                text = cm.group(2).strip()
                if tag in ("given", "when", "then"):
                    current = tag
                    clauses[current].append(text)
                elif tag in ("and", "but") and current:
                    clauses[current].append(text)
            i += 1
        raw = "\n".join(lines[start:i]).rstrip()
        out.append(
            Scenario(
                title=title,
                given=" ".join(clauses["given"]).strip(),
                when=" ".join(clauses["when"]).strip(),
                then=" ".join(clauses["then"]).strip(),
                line=start + 1,
                raw=raw,
            )
        )
    return out


def validate(scenarios: list[Scenario]) -> list[str]:
    """Return list of error messages. Empty list = valid."""
    errors: list[str] = []
    for s in scenarios:
        if not s.is_complete():
            missing = ", ".join(s.missing())
            errors.append(
                f"scenario en línea {s.line} '{s.title}': falta {missing}"
            )
    return errors
