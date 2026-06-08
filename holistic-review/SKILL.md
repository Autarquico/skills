---
name: holistic-review
description: >
  Holistic, mentoring-style code review on a git diff using the `codex` CLI,
  modeled on Google's eng-practices reviewer guide. Walks the 9 review
  dimensions in order (Design → Functionality → Complexity → Tests → Naming →
  Comments → Style → Consistency → Docs), labels each finding by obligation
  (Blocking / Nit / Optional / FYI / Question), applies the "good enough"
  principle, and always calls out what the change does well. Use BEFORE asking
  a human reviewer to approve, for PRs from juniors where mentoring matters,
  or whenever the user asks for a "full review", "holistic review", "google-
  style review", "CL review", or "review like a staff engineer". Complement to
  `codex-review` (which is adversarial and bug-hunting); this one is broader
  and collaborative. NEVER applies changes — only reports.
license: MIT
argument-hint: "[pr | uncommitted | last <N> | --reconsider <n> | <free-form intent>]"
allowed-tools:
  - Bash
metadata:
  version: 1.0.0
  author: autarqui
  domains: [code-review, mentoring, quality]
  type: assistant
---

# holistic-review

Staff-engineer reviewer. Uses the `codex` CLI as a holistic second pair of eyes on a diff, following Google's eng-practices reviewer guide. Reports findings organized by **dimension**, labeled by **obligation**, with explicit recognition of good work. Never patches.

## When to invoke

- User asks for "full review", "holistic review", "google-style review", "CL review", "staff-engineer review", "review with mentoring".
- Before asking a human reviewer to approve a PR.
- PR from a less senior engineer where the goal includes teaching, not just bug-hunting.
- After `codex-review` has hunted for bugs and the user wants the broader view.

If the user wants **adversarial bug hunting** (race conditions, security, edge cases) → use `codex-review` instead. This skill is broader and collaborative: it questions design, recognizes good work, and labels nits as nits.

## Preflight

Same as `codex-review`:

1. `command -v codex` — if missing, tell user to install (`brew install codex`). Stop.
2. `codex --version` — if auth error, tell user to run `codex login`. Stop.
3. `git rev-parse --is-inside-work-tree` — must be true.
4. Determine scope (see below), verify diff is non-empty.

## Scope selection

| User intent | Scope | Codex invocation |
|---|---|---|
| "review this PR" / "review my branch" | PR vs base | `codex exec review --base <base>` |
| "review the last N commits" | Last N commits | `codex exec review --commit HEAD~<N>..HEAD` |
| "review my working changes" | Working tree | `codex exec review --uncommitted` |

Auto-detect base branch via `git symbolic-ref refs/remotes/origin/HEAD` → fallback `main` → `master`.

## Diff size cap

Holistic review needs the whole picture. Hard cap:

```bash
lines=$(git diff --numstat "$scope" | awk '{a+=$1; d+=$2} END{print a+d+0}')
```

- `lines` ≤ 1500 → proceed.
- `1500 < lines ≤ 4000` → proceed but warn the user the design assessment may be shallow.
- `lines > 4000` → **refuse and ask for a split**. Output:

  > Diff is N lines. A holistic review needs to fit the design in one pass; over ~4000 lines that's no longer one review, it's three. Split the PR by feature/concern and re-run, or use `codex-review` (adversarial bug hunt) which tolerates larger diffs.

Don't try to be clever and area-split here. Holistic review loses its value when the reviewer can't hold the whole change in mind.

## The 9 dimensions (Google order)

Codex must walk these **in this order**. Design first, style last — so a design flaw isn't drowned in nits.

1. **Design** — Does this change belong? Does it fit the system's architecture? Could it be done in a substantially simpler way? Is it solving the right problem?
2. **Functionality** — Does it do what it claims? Edge cases, error paths, concurrency, user-visible behavior.
3. **Complexity** — Over-engineered? Premature abstraction? Could a junior pick this up in 6 months? Are there 2 vs 3 implementations of the same pattern (the threshold for extracting one)?
4. **Tests** — Do they exist? Do they describe behavior, not implementation? Do they cover the change? Right place in the pyramid (unit vs integration)?
5. **Naming** — Identifiers self-explanatory? Or do comments compensate for poor names?
6. **Comments** — Comments explain *why*, not *what*? Any that should be deleted? Any missing for genuinely non-obvious code?
7. **Style** — Matches repo conventions and linter output?
8. **Consistency** — Aligned with how the rest of the codebase does similar things?
9. **Documentation** — User-facing docs, README, runbooks, CHANGELOG updated where needed?

If a dimension has nothing to say, **skip it in the output**. Don't pad.

## Obligation labels

Every finding gets exactly one:

- **[Blocking]** — must address before merge. Bug, broken contract, security issue, design flaw that will hurt later.
- **[Nit]** — optional polish. Author may decline freely. Style, micro-naming, comment wording.
- **[Optional]** — worth doing but not required. Refactor opportunity, alternative approach.
- **[FYI]** — informational, no action required. Pattern note, related work elsewhere, future consideration.
- **[Question]** — reviewer doesn't understand something. Author should answer, not necessarily change code. **If the answer would be "let me explain", the right outcome is a code comment or rename — not a reply in the review thread.**

## The "good enough" principle

This skill applies Google's standard: **approve when the change improves overall code health, even if not perfect**. Concretely:

- A finding that doesn't make the code measurably better → drop it, don't pad the report.
- Mentoring comments (teaching a pattern) → label `[FYI]` or `[Optional]`, never `[Blocking]`.
- Reviewer perfectionism is a bug. If you find yourself listing 15 things, ask which 3 actually matter.

## "What this does well" — mandatory

Every report opens with a **What this does well** section (1-3 bullets). Forces a positive read of the diff and reduces false positives from the model. If genuinely nothing stands out, write "Solid, low-risk change — nothing notable to call out positively or negatively."

## Invoking codex

**Preferred: built-in review subcommand** with the holistic prompt:

```bash
codex exec review --base "$base" "$(cat <<'PROMPT'
You are a staff-engineer reviewer following Google's eng-practices guide.
Walk the 9 dimensions IN THIS ORDER. Skip any dimension where you have
nothing substantive to say. Do NOT pad.

  1. Design       — Does this change belong? Fit the system? Simpler alternative?
  2. Functionality — Does it work? Edge cases, error paths, concurrency.
  3. Complexity   — Over-engineered? Premature abstraction? Junior-readable?
  4. Tests        — Exist, describe behavior, cover the change, right level.
  5. Naming       — Self-explanatory identifiers?
  6. Comments     — Explain WHY, not WHAT? Missing where non-obvious?
  7. Style        — Matches repo conventions?
  8. Consistency  — Aligned with existing patterns in this codebase?
  9. Documentation — README, runbooks, CHANGELOG, user-facing docs.

For each finding, output exactly:
  DIMENSION: <1-9 name>
  LABEL: Blocking | Nit | Optional | FYI | Question
  FILE: <path>:<line>
  ISSUE: <one sentence>
  WHY: <one sentence — the reasoning, not just restating the issue>
  SUGGESTION: <concrete fix, or "open-ended — author's call">

START with a section "WHAT THIS DOES WELL" — 1-3 bullets recognizing good
choices in the diff. Be specific, not generic. If genuinely nothing stands
out, write a single line saying so.

Apply the "good enough" principle: approve-worthy changes get few findings,
not many. If a finding doesn't make the code measurably better, drop it.

If code confused you, do NOT ask for an explanation in the review — ask
the author to rename, add a code comment, or restructure. Label these
findings [Question] and say what would make the code self-explanatory.

Never invent file paths or line numbers. If you can't cite one, drop it.
PROMPT
)"
```

**Fallback: raw `codex exec`** when feeding a pre-computed diff:

```bash
git diff "$base...HEAD" | codex exec - <<'PROMPT'
[same prompt as above; treat stdin as the diff]
PROMPT
```

### If a finding is vague

Re-prompt:

```
The following finding lacks a concrete FILE:LINE or its WHY just restates
the ISSUE: <finding>
Reply with a precise location and a one-sentence reason this matters, or
drop the finding.
```

Only surface findings that survive.

## Reporting back

Order: **What this does well** → findings grouped **by dimension** (in the 9-dim order), **not** by label. Each finding shows its label inline.

```
## What this does well
- The `LinkValueProber` boundary is clean: pure function, no LLM dependency, easy to test.
- New JSONPath support in `_dispatch_composite` is gated by feature flag — safe rollout.

## Design
1. **[Blocking]** `backend/app/services/link_discovery_service_v2.py:88` — v2 service duplicates orchestration logic from v1 verbatim.
   *Why:* the duplicated path will drift; v1 is meant to be retired but the duplication makes rollback risky too.
   *Suggestion:* extract the shared phases into a small `LinkDiscoveryPipeline` that both v1 and v2 compose.

## Tests
2. **[Optional]** `backend/tests/test_link_discovery_service_v2.py:42` — only happy path is covered.
   *Why:* the three production scenarios (codigo, idCliente, email) each have a distinct failure mode worth pinning.
   *Suggestion:* add three failing-input fixtures, one per scenario.

## Naming
3. **[Nit]** `link_value_prober.py:15` — `probe_overlap` is the public method but returns score+evidence, not just overlap.
   *Why:* name undersells what it returns; future callers may miss the evidence payload.
   *Suggestion:* rename to `score_candidate` or document the return shape in the docstring.
```

End every report with:

> **Want me to dig deeper on any dimension, or is this enough to take to the human reviewer?** I won't apply anything without your say-so.

## Pushback / reconsider mode

When the user pushes back on a finding (`/holistic-review --reconsider 3` or "I disagree with #3"), re-invoke Codex with:

```
You previously made this finding:
<finding>

The author pushes back:
<user objection>

Do one of:
  (a) MAINTAIN — restate with concrete additional evidence (file:line, scenario, citation from the diff).
  (b) RETRACT — say "Withdrawn" and one sentence on why the objection holds.

Do not hedge. Pick one.
```

Report the outcome cleanly. Closes the review loop without copy-paste.

## Conflicts with prior analysis

If Claude analyzed the same code earlier in chat and reached a different conclusion than Codex on a point, present both side-by-side. Let the user decide. Don't silently pick.

## Hard rules

- Never run `git apply`, `git commit`, `Edit`, or any mutating shell command.
- Never re-invoke `codex` after an auth failure or missing-binary failure.
- Never skip the "What this does well" section.
- Never label a teaching/mentoring comment as `[Blocking]` — that's what `[FYI]` and `[Optional]` are for.
- Never reorder dimensions. Design comes first so it isn't drowned in style nits.
- Diff > 4000 lines → refuse with a split request. Do not produce a shallow review.

## Relationship to other skills

| Skill | Stance | Use when |
|---|---|---|
| `holistic-review` (this) | Mentoring, broad, by dimension | Before human review, mentoring PR, full picture |
| `codex-review` | Adversarial, narrow, by severity | Hunting bugs/security before merge |
| `code-review` | Local fixes, optionally applies | Diff cleanup with auto-apply |
| `simplify` | Same as code-review with `--fix` | Quick polish pass |

Recommend `codex-review` followed by `holistic-review` when the user wants both bug-hunting and design feedback. They cover different ground.
