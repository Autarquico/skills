#!/usr/bin/env python3
"""pm_policy_show — imprime la policy.

Modos:
    --raw        solo el bloque policy: del .pm/config.yaml del repo
    --effective  default + global override + repo (default)
    --diff       diferencias entre default y el override del repo

Read-only.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import banner, die, find_pm_root, load_config, yaml_dumps
from pm_lib.policy import effective_policy, raw_policy
from pm_lib.policy_defaults import DEFAULT_POLICY


def diff_dicts(base: dict, overlay: dict, path: str = "") -> list[str]:
    """Returns dotted-path lines describing each key that differs."""
    out: list[str] = []
    for k in sorted(set(base) | set(overlay)):
        full = f"{path}.{k}" if path else k
        b, o = base.get(k), overlay.get(k)
        if isinstance(b, dict) and isinstance(o, dict):
            out.extend(diff_dicts(b, o, full))
        elif b != o and o is not None:
            out.append(f"{full}: {b!r} → {o!r}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--raw", action="store_true")
    mode.add_argument("--effective", action="store_true")
    mode.add_argument("--diff", action="store_true")
    args = ap.parse_args()

    pm_root = find_pm_root()
    cfg = load_config(pm_root / ".pm" / "config.yaml")

    if args.raw:
        banner("policy (raw, solo override del repo)")
        block = raw_policy(cfg)
        if not block:
            print("# (sin bloque policy: en .pm/config.yaml)")
        else:
            print(yaml_dumps({"policy": block}))
        return

    if args.diff:
        banner("policy (diff: default → repo override)")
        diffs = diff_dicts(DEFAULT_POLICY, raw_policy(cfg))
        if not diffs:
            print("(sin diferencias: el repo usa defaults completos)")
        else:
            for line in diffs:
                print(f"  · {line}")
        return

    # default: effective
    banner("policy (efectiva: default + global override + repo)")
    print(yaml_dumps({"policy": effective_policy(cfg)}))


if __name__ == "__main__":
    main()
