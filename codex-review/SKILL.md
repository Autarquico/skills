---
name: codex-review
description: >
  Adversarial second-opinion code review on a git diff using the `codex` CLI.
  Use this skill BEFORE merging a PR, after completing a feature, when the
  user asks for a "second opinion", "adversarial review", "double-check this",
  "review my changes", or proactively suggest it before a significant push.
  Reviews PR-vs-base diffs, last N commits, or the working tree. Classifies
  findings as critical / important / suggestion. NEVER applies changes — only
  reports. Use when the user wants an independent reviewer to find bugs,
  security issues, race conditions, missing edge cases, or weak error handling
  in code they've already written.
license: MIT
argument-hint: "[pr | uncommitted | last <N> | <free-form intent>]"
allowed-tools:
  - Bash
metadata:
  version: 1.0.0
  author: autarqui
  domains: [code-review, quality, security]
  type: assistant
---

# codex-review

Adversarial reviewer. Uses the `codex` CLI as a second pair of eyes on a diff. Reports findings; never patches.

## When to invoke

- User asks for "review", "second opinion", "adversarial review", "another set of eyes", "double-check this PR".
- Before a significant push (proactive suggestion when 100+ lines have changed since last review).
- After completing a feature, before merging.

If the user only wants stylistic suggestions or refactors, this is the wrong skill — use `review` or `simplify`. This skill is adversarial: it hunts for things that will break.

## Preflight

Run before invoking `codex`:

1. `command -v codex` — if missing, tell the user: *"codex CLI not installed. Install with `brew install codex` (or see https://github.com/openai/codex)."* Stop. No retry.
2. `codex --version` — if it errors with auth/login text, tell the user to run `codex login` and stop. No retry.
3. Confirm `git rev-parse --is-inside-work-tree` is true. If not, stop with "Not in a git repo."
4. Determine scope (see "Scope selection" below) and verify the diff is non-empty before calling `codex`. Empty diff → *"No changes to review."* Stop.

## Scope selection

Pick exactly one. Ask the user only if ambiguous.

| User intent | Scope | Diff probe | Codex invocation |
|---|---|---|---|
| "review this PR" / "review my branch" | PR vs base | `git diff --stat <base>...HEAD` | `codex exec review --base <base>` |
| "review the last N commits" | Last N commits | `git diff --stat HEAD~<N>` | `codex exec review --commit HEAD~<N>..HEAD` (or per-commit loop) |
| "review my working changes" / no commit yet | Working tree | `git diff --stat` + `git diff --stat --staged` | `codex exec review --uncommitted` |

### Auto-detect base branch

```bash
base=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
[ -z "$base" ] && git show-ref --verify --quiet refs/heads/main && base=main
[ -z "$base" ] && git show-ref --verify --quiet refs/heads/master && base=master
[ -z "$base" ] && { echo "Could not detect base branch"; exit 1; }
```

## Large diff handling

If the diff is > 2000 lines (check with `git diff --stat <scope> | tail -1`), split by area and review each separately. Detect areas by common top-level paths:

- `src/api/`, `api/`, `backend/`, `server/`
- `src/web/`, `web/`, `frontend/`, `client/`, `ui/`
- `tests/`, `test/`, `__tests__/`
- `migrations/`, `db/`
- everything else → `misc`

For per-area review, drop the built-in subcommand and pipe a path-filtered diff:

```bash
git diff "$base...HEAD" -- <area-path> | codex exec - <<'PROMPT'
[see adversarial prompt below]
PROMPT
```

Combine findings across areas in the final report.

## Invoking codex

**Preferred: the built-in review subcommand** (codex ≥ 0.130 ships `codex exec review`):

```bash
# PR vs base
codex exec review --base "$base"

# Working tree
codex exec review --uncommitted

# Single commit
codex exec review --commit <sha>
```

Pass your adversarial focus as a custom prompt argument so the built-in review uses your criteria:

```bash
codex exec review --base "$base" "$(cat <<'PROMPT'
Adversarial reviewer. Focus exclusively on bugs that ship, not style:

  1. Logic bugs (wrong condition, off-by-one, swapped args, missing return)
  2. Race conditions and concurrency hazards
  3. Security: injection (SQL/command/template), auth bypass, leaked secrets,
     unsafe deserialization, SSRF, missing authz checks
  4. Missing edge cases (empty input, null, very large, unicode, timezone)
  5. Error handling gaps (swallowed exceptions, wrong error type, missing cleanup)
  6. Obvious performance traps (N+1, unbounded loops, O(n^2) on hot paths)

Skip: style, naming, micro-refactors, "could be cleaner" suggestions.

For each finding, output exactly:
  SEVERITY: critical | important | suggestion
  FILE: <path>:<line>
  ISSUE: <one sentence>
  WHY IT BREAKS: <one sentence>

If you find nothing in a category, do not mention it.
PROMPT
)"
```

**Fallback: raw `codex exec`** when you need to feed a filtered or pre-computed diff (the per-area split above, or a diff fragment the user supplies):

```bash
git diff "$base...HEAD" -- <path> | codex exec - <<'PROMPT'
[same adversarial prompt as above; treat stdin as the diff to review]
PROMPT
```

Add `-m <model>` only if the user explicitly requests a non-default model. Otherwise let Codex pick.

### If Codex returns vague output

If a finding lacks a file/line reference or says something like "consider reviewing X", re-prompt:

```
The following finding is too vague to act on:
<finding>
Reply with FILE:LINE and a concrete failure scenario, or drop the finding.
```

Only show the user findings that survive this filter.

## Severity classification

Codex outputs `SEVERITY:` per finding. Trust it but sanity-check:

- **critical** — data loss, security breach, crash on common input, money/auth bug. Must fix before merge.
- **important** — broken in a real but narrower scenario, missing error path, perf regression on hot path. Should fix before merge.
- **suggestion** — defensive improvement, edge case unlikely in this codebase, hardening. Worth noting.

If a `critical` claim doesn't pass the sniff test, demote it and explain why.

## Reporting back

Group findings by severity. For each:

```
### critical
1. `path/to/file.py:142` — <issue>
   *Why it breaks:* <one sentence>
   *Codex evidence:* <quoted snippet>
```

End every report with:

> **What do you want to incorporate?** I won't apply anything without your say-so.

## Conflicts with prior analysis

If, earlier in this chat, Claude analyzed the same code and reached a different conclusion than Codex on a specific point, present **both positions** side-by-side and let the user decide. Do not silently pick a side.

```
On `auth.py:88`:
  - Claude (earlier): said the token check is sufficient because X.
  - Codex (now):     flags it as critical because Y.
  Your call.
```

## Hard rules

- Never run `git apply`, `git commit`, or any `Edit`-equivalent shell command.
- Never re-invoke `codex` after an auth failure or missing-binary failure.
- Never dump the raw codex output verbatim if it exceeds ~80 lines — summarize and group.
- Never mention "style" or "naming" findings even if Codex includes them.
