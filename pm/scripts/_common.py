"""Shared primitives for pm scripts.

Stdlib only. Provides:
- find_pm_root, load_config, save_config
- parse_frontmatter, write_frontmatter
- gh, gh_json wrappers around `gh` CLI
- log/ok/warn/die output helpers (stderr)
- working_tree_clean, confirm, today

YAML parser is minimal: handles strings, numbers, booleans, inline lists,
list items, and one level of nesting. Sufficient for .pm/config.yaml and
spec frontmatter. Not a full YAML implementation.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------- output


def _stderr(prefix: str, msg: str) -> None:
    print(f"{prefix} {msg}", file=sys.stderr)


def log(msg: str) -> None:
    _stderr("·", msg)


def ok(msg: str) -> None:
    _stderr("✓", msg)


def warn(msg: str) -> None:
    _stderr("⚠", msg)


def die(msg: str, code: int = 1):
    _stderr("✗", msg)
    sys.exit(code)


def banner(title: str) -> None:
    _stderr("===", title)


# ---------------------------------------------------------------- fs / git


def find_pm_root(start: Path | None = None) -> Path:
    """Walk up from cwd (or start) looking for .pm/config.yaml."""
    p = (start or Path.cwd()).resolve()
    for parent in [p, *p.parents]:
        if (parent / ".pm" / "config.yaml").is_file():
            return parent
    die("no .pm/config.yaml encontrado (subiendo desde cwd). Ejecuta /pm adopt primero.")


def working_tree_clean(repo: Path | None = None) -> bool:
    try:
        r = subprocess.run(
            ["git", "-C", str(repo or Path.cwd()), "status", "--porcelain"],
            capture_output=True, text=True, check=True,
        )
        return r.stdout.strip() == ""
    except subprocess.CalledProcessError:
        return False


def today() -> str:
    return date.today().isoformat()


def confirm(prompt: str, default_no: bool = True) -> bool:
    suffix = " [y/N] " if default_no else " [Y/n] "
    try:
        r = input(prompt + suffix).strip().lower()
    except EOFError:
        return False
    if not r:
        return not default_no
    return r in ("y", "yes", "s", "si", "sí")


# ---------------------------------------------------------------- YAML (minimal)


_NUM_RE = re.compile(r"^-?\d+(\.\d+)?$")
_INLINE_LIST_RE = re.compile(r"^\[(.*)\]$")


def _yaml_value(s: str) -> Any:
    s = s.strip()
    if not s:
        return None
    if s.lower() in ("true", "yes"):
        return True
    if s.lower() in ("false", "no"):
        return False
    if s.lower() in ("null", "~"):
        return None
    if _NUM_RE.match(s):
        return float(s) if "." in s else int(s)
    m = _INLINE_LIST_RE.match(s)
    if m:
        inner = m.group(1).strip()
        if not inner:
            return []
        return [_yaml_value(x) for x in _split_csv(inner)]
    # Strip surrounding quotes
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def _split_csv(s: str) -> list[str]:
    """Split comma-separated values respecting simple quoting."""
    out, cur, in_quote, q = [], [], False, ""
    for ch in s:
        if in_quote:
            cur.append(ch)
            if ch == q:
                in_quote = False
        elif ch in ("'", '"'):
            in_quote = True
            q = ch
            cur.append(ch)
        elif ch == ",":
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur).strip())
    return out


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def yaml_loads(text: str) -> Any:
    """Parse a YAML document (one root mapping or list)."""
    lines = []
    for raw in text.splitlines():
        # Strip comments (not inside strings — naive but enough for our schemas)
        stripped = raw
        if "#" in stripped:
            # Don't strip # inside quotes
            in_q, q = False, ""
            for i, ch in enumerate(stripped):
                if in_q:
                    if ch == q:
                        in_q = False
                elif ch in ("'", '"'):
                    in_q = True
                    q = ch
                elif ch == "#":
                    stripped = stripped[:i].rstrip()
                    break
        if stripped.strip() == "":
            continue
        lines.append(stripped)
    return _parse_block(lines, 0, 0)[0]


def _parse_block(lines: list[str], i: int, base_indent: int) -> tuple[Any, int]:
    """Return (value, next_index)."""
    if i >= len(lines):
        return None, i
    first = lines[i]
    ind = _indent(first)
    if ind < base_indent:
        return None, i

    # List?
    if first.lstrip().startswith("- "):
        items = []
        while i < len(lines):
            ln = lines[i]
            if _indent(ln) != ind or not ln.lstrip().startswith("- "):
                break
            item_text = ln.lstrip()[2:]
            if item_text and ":" in item_text and not item_text.startswith("["):
                # Inline mapping start: "- key: value [+ further keys nested]"
                # Build sub-block by indenting the rest
                k, _, v = item_text.partition(":")
                m = {k.strip(): _yaml_value(v)}
                i += 1
                # Consume further nested keys at deeper indent
                while i < len(lines) and _indent(lines[i]) > ind:
                    sub = _indent(lines[i])
                    sub_val, i = _parse_block(lines[i:], 0, sub) if False else _parse_kv(lines, i, sub)
                    m.update(sub_val)
                items.append(m)
            else:
                items.append(_yaml_value(item_text))
                i += 1
        return items, i

    # Mapping
    return _parse_mapping(lines, i, ind)


def _parse_mapping(lines: list[str], i: int, ind: int) -> tuple[dict, int]:
    out: dict = {}
    while i < len(lines):
        ln = lines[i]
        if _indent(ln) < ind:
            break
        if _indent(ln) > ind:
            # shouldn't happen at this level
            i += 1
            continue
        stripped = ln.strip()
        if ":" not in stripped:
            break
        key, _, val = stripped.partition(":")
        key = key.strip()
        val = val.strip()
        if val == "":
            # Nested block: detect list or mapping by looking ahead
            i += 1
            if i < len(lines) and _indent(lines[i]) > ind:
                child_ind = _indent(lines[i])
                if lines[i].lstrip().startswith("- "):
                    child, i = _parse_block(lines, i, child_ind)
                else:
                    child, i = _parse_mapping(lines, i, child_ind)
                out[key] = child
            else:
                out[key] = None
        else:
            out[key] = _yaml_value(val)
            i += 1
    return out, i


def _parse_kv(lines, i, ind):
    """Helper: parse a single nested key under list item."""
    ln = lines[i]
    stripped = ln.strip()
    key, _, val = stripped.partition(":")
    key = key.strip()
    val = val.strip()
    if val == "":
        i += 1
        if i < len(lines) and _indent(lines[i]) > ind:
            child_ind = _indent(lines[i])
            if lines[i].lstrip().startswith("- "):
                child, i = _parse_block(lines, i, child_ind)
            else:
                child, i = _parse_mapping(lines, i, child_ind)
            return {key: child}, i
        return {key: None}, i
    else:
        return {key: _yaml_value(val)}, i + 1


def yaml_dumps(data: Any, indent: int = 0) -> str:
    """Serialize a dict/list/scalar to YAML. Minimal but readable."""
    pad = " " * indent
    if data is None:
        return "null"
    if isinstance(data, bool):
        return "true" if data else "false"
    if isinstance(data, (int, float)):
        return str(data)
    if isinstance(data, str):
        if data == "" or any(c in data for c in ":#[]{}\n") or data.strip() != data:
            return json.dumps(data, ensure_ascii=False)
        return data
    if isinstance(data, list):
        if not data:
            return "[]"
        # Inline scalars-only short lists
        if all(isinstance(x, (int, float, str, bool)) for x in data) and sum(
            len(str(x)) for x in data
        ) < 60:
            return "[" + ", ".join(yaml_dumps(x) for x in data) + "]"
        out = []
        for item in data:
            if isinstance(item, dict):
                body = yaml_dumps(item, indent + 2).rstrip()
                # First line goes with "- "
                lines = body.splitlines()
                if lines:
                    out.append(f"{pad}- {lines[0].lstrip()}")
                    for l in lines[1:]:
                        out.append(l)
            else:
                out.append(f"{pad}- {yaml_dumps(item)}")
        return "\n".join(out)
    if isinstance(data, dict):
        if not data:
            return "{}"
        out = []
        for k, v in data.items():
            if isinstance(v, (dict, list)) and v:
                out.append(f"{pad}{k}:")
                out.append(yaml_dumps(v, indent + 2))
            else:
                out.append(f"{pad}{k}: {yaml_dumps(v)}")
        return "\n".join(out)
    return str(data)


# ---------------------------------------------------------------- frontmatter


_FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    if not m:
        die(f"{path}: no tiene frontmatter YAML válido (--- ... ---)")
    fm_text, body = m.group(1), m.group(2)
    fm = yaml_loads(fm_text)
    if not isinstance(fm, dict):
        die(f"{path}: frontmatter no es un mapping")
    return fm, body


def write_frontmatter(path: Path, fm: dict, body: str) -> None:
    yaml_text = yaml_dumps(fm)
    text = f"---\n{yaml_text}\n---\n{body}"
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- config


REQUIRED_CONFIG_FIELDS = [
    "codename",
    "github.repo",
    "github.project.owner",
    "github.project.owner_type",
    "github.project.number",
    "paths.specs",
    "paths.specs_archive",
    "paths.tracking.status",
]


def _get_path(d: dict, dotted: str) -> Any:
    cur: Any = d
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def load_config(path: Path) -> dict:
    if not path.is_file():
        die(f"{path}: no existe")
    cfg = yaml_loads(path.read_text(encoding="utf-8"))
    if not isinstance(cfg, dict):
        die(f"{path}: no parsea como mapping")
    missing = [f for f in REQUIRED_CONFIG_FIELDS if _get_path(cfg, f) is None]
    if missing:
        die(f"{path}: faltan campos obligatorios: {', '.join(missing)}")
    return cfg


def save_config(path: Path, cfg: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml_dumps(cfg) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- gh CLI


def gh(*args: str, check: bool = True, input: str | None = None) -> subprocess.CompletedProcess:
    """Run `gh <args>` and return CompletedProcess. By default, die on failure."""
    try:
        r = subprocess.run(
            ["gh", *args],
            capture_output=True, text=True, check=check, input=input,
        )
        return r
    except FileNotFoundError:
        die("`gh` CLI no encontrado en PATH. Instala https://cli.github.com/")
    except subprocess.CalledProcessError as e:
        die(f"gh {' '.join(args)} falló:\n{e.stderr.strip()}")


def gh_json(*args: str) -> Any:
    r = gh(*args)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError as e:
        die(f"gh {' '.join(args)}: stdout no es JSON ({e})")


def gh_auth_check() -> None:
    r = gh("auth", "status", check=False)
    if r.returncode != 0:
        die("gh auth status falló. Ejecuta `gh auth login`.")


# ---------------------------------------------------------------- misc


def slug_to_title(slug: str) -> str:
    return " ".join(w.capitalize() for w in slug.replace("_", "-").split("-"))


def fill_template(text: str, mapping: dict[str, str]) -> str:
    out = text
    for k, v in mapping.items():
        out = out.replace("{{ " + k + " }}", str(v))
        out = out.replace("{{" + k + "}}", str(v))
    return out


def repo_slug_from_config(cfg: dict) -> str:
    return cfg["github"]["repo"]


def project_url(cfg: dict) -> str:
    p = cfg["github"]["project"]
    return f"https://github.com/orgs/{p['owner']}/projects/{p['number']}" if p["owner_type"] == "org" \
        else f"https://github.com/users/{p['owner']}/projects/{p['number']}"
