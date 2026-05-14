#!/usr/bin/env python3
"""pm_bots_review — analiza un major bump y genera plan de migración.

Flujo:
    1. Identifica paquete + from/to del título del PR.
    2. Fetch changelog (GitHub releases o CHANGELOG.md del repo del paquete).
    3. Parsea breaking changes (heurísticas: secciones, conventional commits,
       keywords).
    4. Localiza call sites en el repo (grep o ast-grep).
    5. Output: plan en stderr; con --to-spec genera specs locales; con
       --to-issues materializa epic + sub-issues en el board.

Limitaciones honestas:
    - Parsing de changelogs es heurístico. Funciona bien con Keep-a-Changelog
      o Conventional Commits; prosa libre tiene recall bajo.
    - Grep produce falsos positivos con nombres comunes. Usa --grep-tool
      ast-grep si está instalado.
    - No detecta behavior changes invisibles (mismo símbolo, semántica
      distinta).
    - No ejecuta la migración: solo planifica.

Usage:
    pm_bots_review.py <pr_number> [--to-spec] [--to-issues]
                       [--changelog-url URL] [--grep-tool grep|ast-grep]
                       [--apply]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    banner, die, find_pm_root, gh, gh_auth_check, gh_json, load_config, log,
    ok, today, warn, yaml_dumps,
)


# Title parsing — Bump dependencies-name from A.B.C to X.Y.Z
BUMP_RE = re.compile(
    r"[Bb]ump\s+([A-Za-z0-9_\-./@]+)\s+from\s+v?([\d.]+)\s+to\s+v?([\d.]+)"
)

# Breaking change heuristics
BREAKING_SECTION_RE = re.compile(
    r"^#+\s*(breaking\s+changes?|breaking|migration\s+guide|removed|deprecated)",
    re.IGNORECASE | re.MULTILINE,
)
CONVENTIONAL_BREAKING_RE = re.compile(
    r"^\s*[*\-]?\s*(?:[a-z]+(?:\([^)]+\))?!:|BREAKING\s+CHANGE\s*:)\s*(.+)",
    re.IGNORECASE | re.MULTILINE,
)

# Keywords that suggest breaking changes within a bullet
KEYWORDS = [
    r"removed?",
    r"renamed?",
    r"replaced\s+by",
    r"no\s+longer",
    r"must\s+now",
    r"deprecated",
    r"breaking",
]
KEYWORD_RE = re.compile(r"\b(" + "|".join(KEYWORDS) + r")\b", re.IGNORECASE)


def fetch_pr(repo: str, num: int) -> dict:
    fields = "number,title,body,headRefName,baseRefName,author"
    return gh_json("pr", "view", str(num), "-R", repo, "--json", fields)


def parse_bump(title: str) -> tuple[str, str, str] | None:
    m = BUMP_RE.search(title)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def semver_level(a: str, b: str) -> str:
    pa = a.split(".") + ["0"] * 3
    pb = b.split(".") + ["0"] * 3
    if pa[0] != pb[0]:
        return "major"
    if pa[1] != pb[1]:
        return "minor"
    return "patch"


def guess_pkg_repo(pkg: str) -> str | None:
    """Try to guess the GitHub repo of a package. Pretty naive; works for npm
    scoped packages (@scope/name → scope/name) and a few common patterns."""
    if pkg.startswith("@") and "/" in pkg:
        owner, name = pkg[1:].split("/", 1)
        return f"{owner}/{name}"
    return None


def fetch_changelog_from_releases(repo: str, from_v: str, to_v: str) -> str | None:
    """Use gh release list to fetch release notes between versions."""
    try:
        releases = gh_json("release", "list", "-R", repo, "--limit", "50",
                           "--json", "tagName,name,publishedAt")
    except SystemExit:
        return None
    # Filter releases between from_v and to_v (inclusive of to_v)
    def norm(t: str) -> str:
        return t.lstrip("v")
    candidates = []
    for r in releases:
        tag = norm(r["tagName"])
        if tag <= norm(to_v) and tag > norm(from_v):
            candidates.append(r["tagName"])
    if not candidates:
        return None
    parts = []
    for tag in candidates:
        try:
            r = gh_json("release", "view", tag, "-R", repo,
                        "--json", "body,name,tagName")
            parts.append(f"## {r.get('name') or r['tagName']}\n\n{r.get('body','')}")
        except SystemExit:
            continue
    return "\n\n".join(parts) if parts else None


def fetch_changelog_file(repo: str) -> str | None:
    for name in ("CHANGELOG.md", "CHANGELOG", "HISTORY.md"):
        r = gh("api", f"repos/{repo}/contents/{name}", check=False)
        if r.returncode == 0:
            import base64, json as _json
            try:
                data = _json.loads(r.stdout)
                if data.get("encoding") == "base64":
                    return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            except Exception:
                continue
    return None


def parse_breaking_changes(changelog: str) -> list[dict]:
    """Returns list of {summary, symbols_old, category, migration_hint}."""
    found: list[dict] = []

    # 1. Extract "Breaking Changes" sections, take bullets
    for m in BREAKING_SECTION_RE.finditer(changelog):
        start = m.end()
        # Read until next H1/H2/H3
        rest = changelog[start:]
        end = re.search(r"\n#{1,3}\s+", rest)
        block = rest[: end.start()] if end else rest
        for line in block.splitlines():
            s = line.strip()
            if not s or not (s.startswith("- ") or s.startswith("* ")):
                continue
            text = s[2:].strip()
            found.append(_to_bc(text, "breaking-section"))

    # 2. Conventional commits with `!:` or BREAKING CHANGE:
    for m in CONVENTIONAL_BREAKING_RE.finditer(changelog):
        found.append(_to_bc(m.group(1).strip(), "conventional"))

    # 3. Bullets anywhere containing breaking keywords
    for line in changelog.splitlines():
        s = line.strip()
        if not (s.startswith("- ") or s.startswith("* ")):
            continue
        text = s[2:].strip()
        if KEYWORD_RE.search(text) and not any(text == bc["summary"] for bc in found):
            found.append(_to_bc(text, "keyword"))

    # Dedupe by summary
    seen = set()
    unique = []
    for bc in found:
        key = bc["summary"].lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(bc)
    return unique


SYMBOL_RE = re.compile(r"`([A-Za-z_][\w.<>]*)`")


def _to_bc(text: str, source: str) -> dict:
    symbols = SYMBOL_RE.findall(text)
    category = "behavior-change"
    low = text.lower()
    if "removed" in low or "deprecated" in low:
        category = "api-removal"
    elif "renamed" in low or "replaced" in low:
        category = "api-rename"
    elif "must now" in low or "now requires" in low or "no longer" in low:
        category = "signature-change"
    return {
        "summary": text,
        "category": category,
        "symbols_old": symbols[:3],
        "source": source,
    }


def find_call_sites(repo_root: Path, symbol: str, tool: str = "grep") -> list[tuple[str, int, str]]:
    """Return list of (relpath, line, snippet)."""
    if tool == "ast-grep":
        cmd = ["ast-grep", "--pattern", symbol, "--json", str(repo_root)]
    else:
        cmd = ["grep", "-rn", "--include=*.js", "--include=*.jsx",
               "--include=*.ts", "--include=*.tsx", "--include=*.py",
               "--include=*.go", "--include=*.rs", "--include=*.java",
               "-E", r"\b" + re.escape(symbol) + r"\b", str(repo_root)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []
    out = []
    for line in (r.stdout or "").splitlines():
        # grep format: path:line:content
        m = re.match(r"^(.+?):(\d+):(.*)$", line)
        if not m:
            continue
        path = m.group(1)
        try:
            rel = str(Path(path).resolve().relative_to(repo_root.resolve()))
        except ValueError:
            rel = path
        if "/node_modules/" in rel or "/.git/" in rel or "/dist/" in rel:
            continue
        out.append((rel, int(m.group(2)), m.group(3).strip()))
    return out[:20]  # cap


def build_plan(pkg: str, from_v: str, to_v: str, bcs: list[dict],
               call_sites_by_bc: dict[int, list]) -> str:
    lines = [f"=== Plan: {pkg} {from_v} → {to_v} ===", ""]
    total_sites = sum(len(v) for v in call_sites_by_bc.values())
    lines.append(f"Breaking changes: {len(bcs)}   Call sites: {total_sites}")
    lines.append("")
    for i, bc in enumerate(bcs, 1):
        sites = call_sites_by_bc.get(i, [])
        lines.append(f"[bc-{i}] {bc['summary']}   ({len(sites)} call sites)")
        for path, line_no, snippet in sites[:5]:
            lines.append(f"  · {path}:{line_no}  {snippet[:80]}")
        if len(sites) > 5:
            lines.append(f"  ... y {len(sites)-5} más")
        lines.append("")
    return "\n".join(lines)


def write_specs(pm_root: Path, cfg: dict, pkg: str, from_v: str, to_v: str,
                bcs: list[dict], call_sites_by_bc: dict[int, list],
                pr_num: int) -> tuple[Path, list[Path]]:
    specs_dir = pm_root / cfg["paths"]["specs"]
    specs_dir.mkdir(parents=True, exist_ok=True)
    base_slug = f"migrate-{pkg.replace('@', '').replace('/', '-')}-{to_v.split('.')[0]}"
    epic_path = specs_dir / f"{base_slug}.md"
    epic_fm = {
        "codename": cfg["codename"],
        "title": f"Migrate {pkg} {from_v} → {to_v}",
        "type": "epic",
        "status": "draft",
        "priority": "P1",
        "size": "L",
        "related_issues": [pr_num],
        "sub_issues": [],
        "created": today(),
        "updated": today(),
    }
    epic_body = [f"# Migrate {pkg} {from_v} → {to_v}", "",
                 f"Disparado por PR #{pr_num} (major bump).", "",
                 f"## Breaking changes ({len(bcs)})", ""]
    for i, bc in enumerate(bcs, 1):
        sites = call_sites_by_bc.get(i, [])
        epic_body.append(f"- **bc-{i}** {bc['summary']} ({len(sites)} sitios)")
    epic_body.append("")
    epic_path.write_text(
        f"---\n{yaml_dumps(epic_fm)}\n---\n\n" + "\n".join(epic_body) + "\n",
        encoding="utf-8",
    )

    sub_paths: list[Path] = []
    for i, bc in enumerate(bcs, 1):
        sub_slug = f"{base_slug}-bc-{i}"
        sub_path = specs_dir / f"{sub_slug}.md"
        sub_fm = {
            "codename": cfg["codename"],
            "title": f"[bc-{i}] {bc['summary'][:60]}",
            "type": "task",
            "status": "draft",
            "priority": "P1",
            "size": "S",
            "related_issues": [],
            "created": today(),
            "updated": today(),
        }
        sites = call_sites_by_bc.get(i, [])
        body = [f"# bc-{i}: {bc['summary']}", "",
                f"**Categoría:** {bc['category']}",
                f"**Símbolos viejos:** {', '.join(bc['symbols_old']) or '_n/a_'}",
                "", "## Call sites", ""]
        for path, line_no, snippet in sites:
            body.append(f"- `{path}:{line_no}` — `{snippet[:80]}`")
        if not sites:
            body.append("_No se encontraron call sites con grep. Revisar manualmente._")
        sub_path.write_text(
            f"---\n{yaml_dumps(sub_fm)}\n---\n\n" + "\n".join(body) + "\n",
            encoding="utf-8",
        )
        sub_paths.append(sub_path)

    return epic_path, sub_paths


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pr_number", type=int)
    ap.add_argument("--to-spec", action="store_true",
                    help="Genera epic + sub-specs locales")
    ap.add_argument("--to-issues", action="store_true",
                    help="Genera specs y materializa como epic + sub-issues")
    ap.add_argument("--changelog-url", help="URL custom del changelog")
    ap.add_argument("--grep-tool", choices=["grep", "ast-grep"], default="grep")
    ap.add_argument("--pkg-repo", help="OWNER/REPO del paquete (si no se puede inferir)")
    args = ap.parse_args()

    gh_auth_check()
    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")
    repo = cfg["github"]["repo"]

    banner(f"/pm bots review — PR #{args.pr_number}")
    pr = fetch_pr(repo, args.pr_number)
    bump = parse_bump(pr["title"])
    if not bump:
        die(f"No pude parsear bump del título: {pr['title']}")
    pkg, from_v, to_v = bump
    level = semver_level(from_v, to_v)
    log(f"Paquete: {pkg}  ({from_v} → {to_v}, {level})")
    if level != "major":
        warn(f"No es major ({level}); review tiene más sentido en majors. Continúo.")

    pkg_repo = args.pkg_repo or guess_pkg_repo(pkg)
    changelog = None
    if pkg_repo:
        log(f"Intentando releases de {pkg_repo}...")
        changelog = fetch_changelog_from_releases(pkg_repo, from_v, to_v)
        if not changelog:
            log("Sin releases relevantes; intento CHANGELOG.md...")
            changelog = fetch_changelog_file(pkg_repo)
    if not changelog and args.changelog_url:
        try:
            import urllib.request
            with urllib.request.urlopen(args.changelog_url, timeout=20) as r:
                changelog = r.read().decode("utf-8", errors="replace")
        except Exception as e:
            warn(f"No pude bajar {args.changelog_url}: {e}")
    if not changelog:
        die("No pude obtener changelog. Usa --pkg-repo OWNER/REPO o --changelog-url URL.")

    bcs = parse_breaking_changes(changelog)
    log(f"Breaking changes detectados: {len(bcs)}")
    if not bcs:
        warn("Ninguno. Revisa el changelog manualmente y considera --pkg-repo.")
        return

    call_sites_by_bc: dict[int, list] = {}
    for i, bc in enumerate(bcs, 1):
        sites = []
        for sym in bc["symbols_old"]:
            sites.extend(find_call_sites(pm_root, sym, args.grep_tool))
        call_sites_by_bc[i] = sites

    plan = build_plan(pkg, from_v, to_v, bcs, call_sites_by_bc)
    print(plan, file=sys.stderr)

    if not (args.to_spec or args.to_issues):
        log("Modo plan. Usa --to-spec o --to-issues para materializar.")
        return

    epic_path, sub_paths = write_specs(pm_root, cfg, pkg, from_v, to_v,
                                        bcs, call_sites_by_bc, args.pr_number)
    ok(f"epic spec: {epic_path.relative_to(pm_root)}")
    for p in sub_paths:
        ok(f"sub-spec:  {p.relative_to(pm_root)}")

    if args.to_issues:
        warn("--to-issues: invoca manualmente pm_spec_to_issue.py para cada spec generada.")
        log("Razón: cada spec puede necesitar revisión antes de subir al board.")
        for p in [epic_path, *sub_paths]:
            slug = p.stem
            log(f"  python3 scripts/pm_spec_to_issue.py {slug}")


if __name__ == "__main__":
    main()
