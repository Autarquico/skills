#!/usr/bin/env python3
"""pm_cycle_review — genera payload local de review para codex.

Para una spec activa con PR(s) vinculados, construye un payload con:
- Resumen del proposal (Contexto / problema)
- Scenarios Given/When/Then numerados
- Diff del PR (gh pr diff)
- Prompt explícito pidiendo a codex: cobertura por scenario, findings
  con severidad, gaps, sugerencias de fix.

NO postea. NO muta. Output a stdout o --out <file>.

Selección de PR (orden determinista):
    1. --pr <N>
    2. frontmatter.prs[-1] que siga OPEN
    3. PR linked vía búsqueda "Closes #<issue>"
    4. fallar listando candidatos
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    die, find_pm_root, gh, gh_auth_check, gh_json, load_config,
    parse_frontmatter,
)
from pm_lib.scenarios import parse as parse_scenarios
from pm_lib.specs import resolve_issue, resolve_prs


def extract_section(body: str, heading_keywords: list[str]) -> str:
    """Find the first H2 section whose title contains any of the keywords.
    Returns the body of that section (stripped)."""
    lines = body.splitlines()
    out: list[str] = []
    in_section = False
    for ln in lines:
        if ln.startswith("## "):
            title = ln[3:].strip().lower()
            if in_section:
                break
            if any(k in title for k in heading_keywords):
                in_section = True
                continue
        if in_section:
            out.append(ln)
    return "\n".join(out).strip()


def pick_pr(repo: str, fm: dict, override: int | None) -> int:
    if override is not None:
        return override
    prs = resolve_prs(fm)
    # Try most recent in frontmatter that's still OPEN
    for n in reversed(prs):
        info = gh_json(
            "pr", "view", str(n), "-R", repo, "--json", "number,state",
        )
        if info.get("state") == "OPEN":
            return n
    # Fall back to linked PRs via search
    issue_num = resolve_issue(fm)
    if issue_num is None:
        die("no hay issue en frontmatter. Usa --pr explícito o ejecuta /pm spec to-issue.")
    data = gh_json(
        "pr", "list", "-R", repo, "--state", "open", "--limit", "50",
        "--search", f"#{issue_num}",
        "--json", "number,title,body",
    )
    candidates = []
    for pr in data:
        body = (pr.get("body") or "").lower()
        if f"#{issue_num}" in body and any(
            kw in body for kw in ("closes ", "close ", "fixes ", "fix ", "resolves ")
        ):
            candidates.append(pr)
    if len(candidates) == 1:
        return candidates[0]["number"]
    if not candidates:
        die(f"no encuentro PR open vinculado a issue #{issue_num}. Usa --pr <N>.")
    msg = "varios PRs candidatos; usa --pr <N>:\n" + "\n".join(
        f"  #{p['number']} {p['title']}" for p in candidates
    )
    die(msg)


def fetch_pr_diff(repo: str, pr_num: int) -> str:
    r = gh("pr", "diff", str(pr_num), "-R", repo)
    return r.stdout


def fetch_pr_meta(repo: str, pr_num: int) -> dict:
    return gh_json(
        "pr", "view", str(pr_num), "-R", repo,
        "--json", "number,title,state,isDraft,headRefName,baseRefName,author,url",
    )


def build_payload(spec_path: Path, fm: dict, body: str,
                  pr_meta: dict, pr_diff: str) -> str:
    title = fm.get("title") or spec_path.stem
    contexto = extract_section(body, ["contexto", "problema"])
    scope = extract_section(body, ["scope"])
    notas = extract_section(body, ["notas técnicas", "riesgos", "notas"])
    scenarios = parse_scenarios(body)

    parts: list[str] = []
    parts.append(f"# Review request — {title}")
    parts.append("")
    parts.append(
        f"Spec: `{spec_path.name}`  ·  PR: #{pr_meta['number']} "
        f"({pr_meta['headRefName']} → {pr_meta['baseRefName']})  ·  {pr_meta['url']}"
    )
    parts.append("")
    parts.append("## Contexto (del proposal)")
    parts.append(contexto or "_(sin sección Contexto)_")
    parts.append("")
    if scope:
        parts.append("## Scope")
        parts.append(scope)
        parts.append("")
    parts.append("## Scenarios a verificar")
    if scenarios:
        for i, sc in enumerate(scenarios, 1):
            parts.append(f"### {i}. {sc.title}")
            parts.append(f"- **Given** {sc.given or '_(falta)_'}")
            parts.append(f"- **When** {sc.when or '_(falta)_'}")
            parts.append(f"- **Then** {sc.then or '_(falta)_'}")
            parts.append("")
    else:
        parts.append("_(no se encontraron scenarios Given/When/Then en la spec)_")
        parts.append("")
    if notas:
        parts.append("## Notas técnicas / riesgos")
        parts.append(notas)
        parts.append("")
    parts.append("## Diff del PR")
    parts.append("")
    parts.append("```diff")
    parts.append(pr_diff.rstrip())
    parts.append("```")
    parts.append("")
    parts.append("## Petición a codex")
    parts.append("""
Por favor revisa el diff del PR contra los scenarios y el contexto:

1. **Cobertura por scenario**: para cada scenario numerado, ¿queda cubierto
   por el diff? Cita commit/fichero/línea como evidencia. Si no, márcalo
   como gap.

2. **Findings**: lista hallazgos con severidad y fix sugerido:
   - `blocker`: bloquea merge (regresión, scenario incumplido, seguridad)
   - `major`: debería arreglarse antes de merge (calidad, mantenimiento)
   - `minor`: nit / sugerencia opcional

3. **Gaps**: cosas que faltan respecto al proposal o a las notas técnicas
   y no son scenarios fallidos (tests, docs, refactor necesario, etc.).

4. **Veredicto**: ¿se puede mergear tal cual, con cambios menores, o
   requiere otro round?

Formato sugerido para findings:
```
[severity] [file:line] título
  evidencia: <quote del diff>
  fix: <propuesta concreta>
```
""".strip())
    return "\n".join(parts) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug")
    ap.add_argument("--pr", type=int, help="número de PR explícito")
    ap.add_argument("--out", help="escribir a fichero en vez de stdout")
    args = ap.parse_args()

    gh_auth_check()
    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")
    repo = cfg["github"]["repo"]
    specs_dir = pm_root / cfg["paths"]["specs"]
    spec_path = specs_dir / f"{args.slug}.md"
    if not spec_path.is_file():
        die(f"no existe {spec_path}")
    fm, body = parse_frontmatter(spec_path)

    pr_num = pick_pr(repo, fm, args.pr)
    pr_meta = fetch_pr_meta(repo, pr_num)
    pr_diff = fetch_pr_diff(repo, pr_num)
    payload = build_payload(spec_path, fm, body, pr_meta, pr_diff)

    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(f"✓ payload escrito en {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(payload)


if __name__ == "__main__":
    main()
