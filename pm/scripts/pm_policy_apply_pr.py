#!/usr/bin/env python3
"""pm_policy_apply_pr — cierre automatizado de Fase 3.

Para una spec activa con branch lista:
1. Verifica git root coincide con find_pm_root.
2. /pm policy validate (sin --strict; errors abortan).
3. git push origin <branch>.
4. Construye título y body según policy.
5. gh pr create con labels (pm/policy-managed + internal-*), assignees, etc.
6. Actualiza frontmatter spec: prs: [+N].

Idempotente: si el branch ya tiene un PR open vinculado al issue,
solo refresca labels que falten.

Flags:
    --internal clean|skipped|escalated   resultado del bucle interno
    --branch <name>                       override del nombre del branch (default: rama actual)
    --type <feat|fix|chore|...>           tipo para el title_format
    --adopt --pr N --internal X           adoptar un PR preexistente
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    banner, die, find_pm_root, gh, gh_auth_check, gh_json, load_config, log, ok,
    parse_frontmatter, today, warn, working_tree_clean, write_frontmatter,
)
from pm_lib.policy import effective_policy
from pm_lib.policy_defaults import LABELS
from pm_lib.specs import resolve_issue


def current_branch(repo_root: Path) -> str:
    r = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return r.stdout.strip()


def git_root(start: Path) -> Path:
    r = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    )
    return Path(r.stdout.strip())


def ensure_labels(repo: str, names: list[str]) -> None:
    """Crea labels que falten en el repo."""
    existing = gh_json("label", "list", "-R", repo, "--limit", "200", "--json", "name")
    have = {l["name"] for l in existing}
    for n in names:
        if n in have:
            continue
        color = "1f6feb" if "policy-managed" in n else "0e8a16" if "clean" in n or "mergeable" in n \
                else "d73a4a" if "escalated" in n or "needs-changes" in n or "blocked" in n \
                else "fbca04"
        gh("label", "create", n, "-R", repo, "--color", color,
           "--description", "managed by pm-policy",
           check=False)


def add_label(repo: str, pr: int, label: str) -> None:
    gh("pr", "edit", str(pr), "-R", repo, "--add-label", label, check=False)


def find_open_pr_for_issue(repo: str, issue: int) -> int | None:
    data = gh_json(
        "pr", "list", "-R", repo, "--state", "open", "--limit", "50",
        "--search", f"#{issue}",
        "--json", "number,title,body,state",
    )
    for pr in data:
        body = (pr.get("body") or "").lower()
        if f"#{issue}" in body and any(kw in body for kw in (
                "closes ", "close ", "fixes ", "fix ", "resolves ")):
            return pr["number"]
    return None


def build_pr_body(spec_path: Path, fm: dict, body_md: str, max_kb: int) -> str:
    title = fm.get("title") or spec_path.stem
    issue = resolve_issue(fm)
    # Extract Contexto y scenarios del body
    sections = re.split(r"^## ", body_md, flags=re.M)
    contexto = scenarios = ""
    for sec in sections:
        head = sec.split("\n", 1)[0].strip().lower()
        rest = sec.split("\n", 1)[1].strip() if "\n" in sec else ""
        if head.startswith(("contexto", "problema")):
            contexto = rest
        elif head.startswith("criterios"):
            scenarios = rest

    parts = [
        f"## Summary",
        f"{title}.",
        "",
        f"## Scenarios cubiertos",
        scenarios or "_(ver spec)_",
        "",
    ]
    if contexto:
        parts.extend(["## Contexto", contexto, ""])
    parts.append(f"Closes #{issue}" if issue else "")

    out = "\n".join(parts)
    if len(out.encode("utf-8")) > max_kb * 1024:
        # truncar scenarios; el handoff irá como comentario o gist en v2
        out = "\n".join([
            f"## Summary", f"{title}.", "",
            f"_PR body excede {max_kb}KB; ver spec docs/specs/{spec_path.name} para detalle._",
            "", f"Closes #{issue}" if issue else "",
        ])
    return out


def apply_internal_label(repo: str, pr: int, internal: str) -> None:
    """Pone el label internal correspondiente; quita los otros internal-* si están."""
    mapping = {
        "clean":     LABELS["internal_clean"],
        "skipped":   LABELS["internal_skipped"],
        "escalated": LABELS["internal_escalated"],
    }
    target = mapping[internal]
    add_label(repo, pr, target)
    # remove conflicting
    for k, v in mapping.items():
        if v == target:
            continue
        gh("pr", "edit", str(pr), "-R", repo, "--remove-label", v, check=False)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug")
    ap.add_argument("--internal", choices=["clean", "skipped", "escalated"],
                    default="clean", help="resultado del bucle interno")
    ap.add_argument("--branch", help="override nombre de branch (default: rama actual)")
    ap.add_argument("--type", default="feat", help="<type> para el title_format")
    ap.add_argument("--adopt", action="store_true",
                    help="adoptar un PR preexistente (requiere --pr)")
    ap.add_argument("--pr", type=int, help="con --adopt: nº de PR a adoptar")
    ap.add_argument("--skip-validate", action="store_true",
                    help="saltar validate (NO recomendado)")
    args = ap.parse_args()

    if args.internal == "escalated" and not args.adopt:
        die("internal=escalated: el bucle interno escaló; NO se debería abrir PR. "
            "Abre uno a mano cuando esté listo o usa --adopt sobre uno existente.")

    gh_auth_check()
    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")
    repo = cfg["github"]["repo"]
    policy = effective_policy(cfg)

    # git root coincide con pm root
    g = git_root(pm_root)
    if g.resolve() != pm_root.resolve():
        die(f"git root ({g}) != pm root ({pm_root}); ejecuta desde la raíz del repo")

    # Validate
    if not args.skip_validate:
        from pm_policy_validate import check as do_validate
        errors = do_validate(pm_root, cfg, strict=True)
        if errors:
            die(f"validate falló con {errors} errors; arregla o usa --skip-validate.")

    # Spec
    spec_path = pm_root / cfg["paths"]["specs"] / f"{args.slug}.md"
    if not spec_path.is_file():
        die(f"no existe {spec_path}")
    fm, body_md = parse_frontmatter(spec_path)
    issue = resolve_issue(fm)
    if not issue:
        die(f"spec {args.slug} sin issue vinculado; ejecuta /pm spec to-issue primero")

    # Labels canónicos
    base_labels = [LABELS["managed"]] + list(policy["pr"].get("labels_managed") or [])
    ensure_labels(repo, base_labels + list(LABELS.values()))

    if args.adopt:
        if not args.pr:
            die("--adopt requiere --pr <N>")
        pr_num = args.pr
        # Verificar que existe + open
        info = gh_json("pr", "view", str(pr_num), "-R", repo, "--json", "number,state,labels")
        if info["state"] != "OPEN":
            die(f"PR #{pr_num} no está OPEN (state={info['state']})")
        for lbl in base_labels:
            add_label(repo, pr_num, lbl)
        apply_internal_label(repo, pr_num, args.internal)
        ok(f"PR #{pr_num} adoptado con labels: {', '.join(base_labels + [LABELS[f'internal_{args.internal}']])}")
    else:
        # Comprobar si ya existe un PR para este issue
        existing = find_open_pr_for_issue(repo, issue)
        if existing:
            log(f"PR ya open #{existing} para issue #{issue}; refrescando labels")
            for lbl in base_labels:
                add_label(repo, existing, lbl)
            apply_internal_label(repo, existing, args.internal)
            ok(f"labels refrescados en PR #{existing}")
            pr_num = existing
        else:
            # Push y crear PR
            branch = args.branch or current_branch(pm_root)
            log(f"git push origin {branch}")
            subprocess.run(["git", "-C", str(pm_root), "push", "origin", branch], check=True)

            title_format = policy["pr"]["title_format"]
            title = title_format.replace("<type>", args.type) \
                                .replace("<scope>", args.slug) \
                                .replace("<subject>", fm.get("title") or args.slug)

            body = build_pr_body(spec_path, fm, body_md, policy["pr"]["body_max_kb"])
            label_args = []
            for lbl in base_labels:
                label_args += ["--label", lbl]

            create_args = ["pr", "create", "-R", repo,
                           "--title", title, "--body", body,
                           "--head", branch, "--base", policy["branch"]["default"],
                           *label_args]
            if policy["pr"].get("draft_first"):
                create_args.append("--draft")
            for a in policy["pr"].get("assignees") or []:
                create_args += ["--assignee", a]
            for r in policy["pr"].get("reviewers") or []:
                create_args += ["--reviewer", r]
            r = gh(*create_args)
            # URL en stdout, extraer número
            url = r.stdout.strip().splitlines()[-1]
            m = re.search(r"/pull/(\d+)", url)
            if not m:
                die(f"no pude extraer nº de PR de: {url}")
            pr_num = int(m.group(1))
            ok(f"PR #{pr_num} creado: {url}")

            apply_internal_label(repo, pr_num, args.internal)

    # Actualizar frontmatter spec: prs
    prs_fm = fm.get("prs") or []
    if not isinstance(prs_fm, list):
        prs_fm = []
    if pr_num not in prs_fm:
        prs_fm.append(pr_num)
        fm["prs"] = prs_fm
        fm["updated"] = today()
        write_frontmatter(spec_path, fm, body_md)
        log(f"spec actualizada: prs={prs_fm}")

    print()
    print("Siguiente paso:")
    print(f"  /pm cycle review {args.slug}   # genera payload para codex")
    print(f"  tras codex: /pm cycle review-resolved {args.slug} <mergeable|needs-changes>")


if __name__ == "__main__":
    main()
