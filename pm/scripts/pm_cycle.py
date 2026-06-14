#!/usr/bin/env python3
"""pm_cycle — observador read-only del ciclo refine→ship.

Observa la fase de cada spec combinando frontmatter, board (GitHub Project),
y filesystem. NUNCA muta nada. Si las señales se contradicen reporta
`unknown` con las discrepancias listadas — no infiere a ciegas.

Subcomandos:
    status <slug>     fase + evidencia + confianza
    next <slug>        imprime el comando que tocaría (no ejecuta)
    list               tabla de specs activos con su fase
    seed               imprime plantilla refine-seed.md

Estados: refine, adopt, develop, review, sync, done, abandoned, unknown.

Autoridad (en caso de conflicto): frontmatter > board > filesystem.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    banner, die, find_pm_root, gh_auth_check, gh_json, load_config, log,
    parse_frontmatter, warn,
)
from pm_lib.specs import iter_specs, resolve_issue, resolve_prs


PHASES = ("refine", "adopt", "develop", "review", "sync", "done", "abandoned", "unknown")


class Phase:
    def __init__(self, name: str, confidence: str = "high"):
        assert name in PHASES, name
        assert confidence in ("high", "medium", "low")
        self.name = name
        self.confidence = confidence
        self.evidence: list[str] = []
        self.discrepancies: list[str] = []
        self.next_action: str | None = None

    def add(self, line: str) -> None:
        self.evidence.append(line)

    def conflict(self, line: str) -> None:
        self.discrepancies.append(line)
        self.confidence = "low"
        self.name = "unknown"


def fetch_issue(repo: str, num: int) -> dict | None:
    try:
        return gh_json(
            "issue", "view", str(num), "-R", repo,
            "--json", "number,state,title,closedAt,labels",
        )
    except SystemExit:
        return None


def fetch_pr(repo: str, num: int) -> dict | None:
    try:
        return gh_json(
            "pr", "view", str(num), "-R", repo,
            "--json", "number,state,title,isDraft,mergedAt,body",
        )
    except SystemExit:
        return None


def find_linked_prs(repo: str, issue_num: int) -> list[dict]:
    """PRs that reference 'Closes #N' for this issue. Cheap heuristic."""
    data = gh_json(
        "pr", "list", "-R", repo, "--state", "all", "--limit", "100",
        "--search", f"#{issue_num}",
        "--json", "number,state,title,body,mergedAt,isDraft",
    )
    out = []
    for pr in data:
        body = (pr.get("body") or "").lower()
        if f"#{issue_num}" in body and any(
            kw in body for kw in ("closes ", "close ", "fixes ", "fix ", "resolves ")
        ):
            out.append(pr)
    return out


def derive_phase(repo: str, spec_path: Path, fm: dict) -> Phase:
    status = fm.get("status")
    if status == "abandoned":
        ph = Phase("abandoned")
        ph.add(f"frontmatter: status=abandoned")
        return ph
    if status == "shipped":
        ph = Phase("done")
        ph.add(f"frontmatter: status=shipped")
        return ph

    issue_num = resolve_issue(fm)
    prs_fm = resolve_prs(fm)

    if status == "draft":
        if issue_num is None:
            ph = Phase("adopt")
            ph.add("frontmatter: status=draft, sin issue vinculado")
            ph.next_action = f"/pm spec to-issue {spec_path.stem}"
            return ph
        # draft con issue es raro: el flujo normal pasa a active al crear el issue.
        ph = Phase("adopt", confidence="medium")
        ph.add(f"frontmatter: status=draft pero issue={issue_num} ya existe")
        ph.next_action = "revisar manualmente: ¿reabrir issue o pasar spec a active?"
        return ph

    if status != "active":
        ph = Phase("unknown", confidence="low")
        ph.conflict(f"frontmatter: status={status!r} no reconocido")
        return ph

    # status == active. Necesitamos board + PRs.
    if issue_num is None:
        ph = Phase("unknown", confidence="low")
        ph.conflict("status=active pero sin issue/related_issues. /pm spec to-issue lo arregla.")
        return ph

    issue = fetch_issue(repo, issue_num)
    if issue is None:
        ph = Phase("unknown", confidence="low")
        ph.conflict(f"issue #{issue_num} no se pudo leer de GitHub")
        return ph

    ph = Phase("develop")
    ph.add(f"frontmatter: status=active, issue={issue_num}, prs={prs_fm}")
    ph.add(f"board: #{issue_num} {issue['state']}")

    # Recolectar PRs: frontmatter ∪ linked vía búsqueda
    pr_numbers = set(prs_fm)
    for pr in find_linked_prs(repo, issue_num):
        pr_numbers.add(pr["number"])

    if not pr_numbers:
        if issue["state"] == "CLOSED":
            ph.conflict(f"issue #{issue_num} cerrado pero spec sigue active y sin PRs")
            return ph
        ph.next_action = "implementar; abrir PR con `Closes #" + str(issue_num) + "`"
        return ph

    # Tenemos PRs. Clasificarlos.
    prs_info = [pr for pr in (fetch_pr(repo, n) for n in sorted(pr_numbers)) if pr]
    if not prs_info:
        ph.conflict("PRs vinculados existían pero ninguno se pudo leer")
        return ph

    open_prs = [p for p in prs_info if p["state"] == "OPEN"]
    merged_prs = [p for p in prs_info if p["state"] == "MERGED"]
    closed_prs = [p for p in prs_info if p["state"] == "CLOSED"]

    ph.add(f"prs: {len(open_prs)} open, {len(merged_prs)} merged, {len(closed_prs)} closed")

    if open_prs:
        ph.name = "review"
        ph.next_action = f"/pm cycle review {spec_path.stem}   # genera payload local"
        return ph

    if merged_prs and issue["state"] == "OPEN":
        ph.conflict(
            f"PR #{merged_prs[-1]['number']} mergeado pero issue #{issue_num} sigue abierto"
        )
        return ph

    if merged_prs and issue["state"] == "CLOSED":
        ph.name = "sync"
        ph.next_action = "/pm sync   # cierra el ciclo: spec → shipped, archive con fecha"
        return ph

    # Solo PRs cerrados sin merge: vuelta a develop
    ph.name = "develop"
    ph.add("PR(s) cerrados sin merge — sigue desarrollo")
    ph.next_action = "abrir nuevo PR con `Closes #" + str(issue_num) + "`"
    return ph


# ---------------------------------------------------------------- output


def print_status(spec_path: Path, ph: Phase) -> None:
    print(f"=== /pm cycle status — {spec_path.stem} ===")
    print(f"Fase:       {ph.name} (confianza: {ph.confidence})")
    print(f"Spec:       {spec_path}")
    print("Evidencia:")
    for line in ph.evidence:
        print(f"  · {line}")
    if ph.discrepancies:
        print("Discrepancias:")
        for d in ph.discrepancies:
            print(f"  ! {d}")
    if ph.next_action:
        print(f"Próximo:    {ph.next_action}")
    elif ph.name == "done":
        print("Próximo:    (terminado)")
    elif ph.name == "abandoned":
        print("Próximo:    (abandonado)")
    elif ph.name == "unknown":
        print("Próximo:    revisar manualmente; /pm sync no reconciliará esto.")


def cmd_status(args, pm_root: Path, cfg: dict) -> int:
    repo = cfg["github"]["repo"]
    specs_dir = pm_root / cfg["paths"]["specs"]
    spec_path = specs_dir / f"{args.slug}.md"
    if not spec_path.is_file():
        # Could be in refine phase: no spec yet
        ph = Phase("refine")
        ph.add(f"no existe {spec_path}")
        ph.next_action = (
            f"trae el .md desde codex y ejecuta: /pm spec adopt <file.md> --slug {args.slug}"
        )
        print(f"=== /pm cycle status — {args.slug} ===")
        print(f"Fase:       {ph.name}")
        for line in ph.evidence:
            print(f"  · {line}")
        print(f"Próximo:    {ph.next_action}")
        return 0
    fm, _ = parse_frontmatter(spec_path)
    ph = derive_phase(repo, spec_path, fm)
    print_status(spec_path, ph)
    return 0 if ph.name != "unknown" else 2


def cmd_next(args, pm_root: Path, cfg: dict) -> int:
    repo = cfg["github"]["repo"]
    specs_dir = pm_root / cfg["paths"]["specs"]
    spec_path = specs_dir / f"{args.slug}.md"
    if not spec_path.is_file():
        print(f"/pm spec adopt <file.md> --slug {args.slug}")
        return 0
    fm, _ = parse_frontmatter(spec_path)
    ph = derive_phase(repo, spec_path, fm)
    if ph.next_action:
        print(ph.next_action)
    elif ph.name == "done":
        print("# ciclo terminado")
    elif ph.name == "abandoned":
        print("# spec abandonada")
    else:
        print("# revisar manualmente")
    return 0


def cmd_list(args, pm_root: Path, cfg: dict) -> int:
    repo = cfg["github"]["repo"]
    specs_dir = pm_root / cfg["paths"]["specs"]
    specs = iter_specs(specs_dir)
    if not specs:
        print("(sin specs)")
        return 0
    rows: list[tuple[str, str, str, str]] = []
    for spec_path in specs:
        try:
            fm, _ = parse_frontmatter(spec_path)
        except SystemExit:
            rows.append((spec_path.stem, "unknown", "low", "frontmatter inválido"))
            continue
        ph = derive_phase(repo, spec_path, fm)
        evidence = ph.evidence[0] if ph.evidence else ""
        rows.append((spec_path.stem, ph.name, ph.confidence, evidence))
    w_slug = max(len(r[0]) for r in rows)
    w_phase = max(len(r[1]) for r in rows)
    print(f"{'SLUG':<{w_slug}}  {'FASE':<{w_phase}}  CONF   EVIDENCIA")
    for slug, phase, conf, ev in rows:
        print(f"{slug:<{w_slug}}  {phase:<{w_phase}}  {conf:<5}  {ev}")
    return 0


def cmd_seed(args, pm_root: Path, cfg: dict) -> int:
    seed_path = Path(__file__).parent.parent / "assets" / "templates" / "refine-seed.md"
    if not seed_path.is_file():
        die(f"no encuentro {seed_path}")
    sys.stdout.write(seed_path.read_text(encoding="utf-8"))
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    s_status = sub.add_parser("status", help="fase + evidencia de un slug")
    s_status.add_argument("slug")
    s_next = sub.add_parser("next", help="imprime el comando que tocaría")
    s_next.add_argument("slug")
    sub.add_parser("list", help="tabla de todos los specs con su fase")
    sub.add_parser("seed", help="imprime plantilla refine-seed.md")

    args = ap.parse_args()

    if args.cmd == "seed":
        # seed no necesita repo ni gh
        sys.exit(cmd_seed(args, Path.cwd(), {}))

    gh_auth_check()
    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")

    dispatch = {
        "status": cmd_status,
        "next": cmd_next,
        "list": cmd_list,
    }
    sys.exit(dispatch[args.cmd](args, pm_root, cfg))


if __name__ == "__main__":
    main()
