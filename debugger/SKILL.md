---
name: debugger
description: >
  Full-stack bug investigator. Use when the user reports something broken,
  failing, or behaving unexpectedly — UI errors, 500s, exceptions, failed
  tests, CI failures, "why is X broken in prod", "look at the logs",
  "reproduce this bug", stack-trace pastes, or anything that needs to be
  diagnosed and fixed end-to-end. Drives Playwright to reproduce UI bugs
  (console errors, network failures, screenshots), pulls backend logs from
  Dozzle or docker, correlates frontend errors with backend traces, and runs
  a propose → confirm → apply → re-verify fix loop (capped at 5 iterations).
  Requires per-repo config at `.claude/debugger.md` (generate with
  `scripts/discover-stack.sh`). Reports root cause + evidence + alternatives
  before proposing a patch. Never applies edits without explicit user OK.
license: MIT
argument-hint: "[discover-stack] [bug description | URL | stack trace]"
allowed-tools:
  - Bash
  - Read
  - Edit
  - Grep
  - Glob
metadata:
  version: 1.0.0
  author: autarqui
  domains: [debugging, observability, qa, playwright, dozzle]
  type: orchestrator
---

# debugger

Investigates and fixes bugs across UI and backend. Reproduces, diagnoses, proposes a patch, applies it on your OK, and re-verifies. Iterates up to 5 times.

## Commands

Dispatch on the first argument:

| Command | Action |
|---|---|
| `/debugger discover-stack` | Run `~/.claude/skills/debugger/scripts/discover-stack.sh` from the current repo root via Bash, then read `.claude/debugger.md` (or `.new`) and propose curated values for the `[FILL IN]` sections. Stop after proposal — user commits the file. |
| `/debugger <bug description>` | Investigation mode (Step 1 onward). |
| `/debugger` (no arg) | Investigation mode. Ask the user what's broken if no context. |

For `discover-stack`:

1. Confirm the user is at a repo root (`.git/` exists).
2. If `.claude/debugger.md` already exists, parse the Dozzle URL from the "Backend log source" section and pass it as `DOZZLE_URL` when invoking the script. Same for `DOZZLE_TOKEN` if declared.
3. If no config exists yet, ask the user once: "Dozzle URL? (blank to use local docker)" and pass the answer through.
4. Run the script with the resolved env: `DOZZLE_URL=<url> [DOZZLE_TOKEN=<token>] ~/.claude/skills/debugger/scripts/discover-stack.sh`.
5. After the script exits, read the generated file (`.claude/debugger.md` or `.claude/debugger.md.new`).
6. Propose values for each `[FILL IN]` block using the discovery samples, in a single message. Don't apply edits — show the proposal and wait.

## Step 1: load repo config (ALWAYS FIRST)

Read `.claude/debugger.md` from the current repo.

- **Missing?** Tell the user:
  > No `.claude/debugger.md` in this repo. Run `~/.claude/skills/debugger/scripts/discover-stack.sh` to generate one (needs `DOZZLE_URL`/`DOZZLE_TOKEN` env vars, or falls back to local docker).
  Stop. Do not attempt to investigate without config.
- **Present?** Parse it. Expect these sections:
  - Backend log source (Dozzle URL + token env var, OR docker-compose project name).
  - Service → container map.
  - Logging conventions (request-id header/field, log format).
  - Frontend base URL + auth setup.
  - Common repro recipes (named flows).
  - Decision tree by symptom.
  - Known noise to ignore.

## Step 2: classify the entry

Pick a lane from how the user reported the bug:

| Input shape | First action |
|---|---|
| Symptom only ("login is broken", "checkout fails") | Consult repo decision tree. If UI-flavored → Playwright. If backend → logs. If unclear → ask the user which they want to start with. |
| URL + repro steps ("go to /x, click y, see error") | Playwright drives the steps, then correlate with logs. |
| Pasted stack trace / error message | Grep logs and codebase for the exact message. |
| Failing test or CI output | Read test output; reproduce locally if possible. |

## Step 3a: UI investigation (Playwright)

Use `mcp__playwright__browser_*` tools.

1. `browser_navigate` to the URL (use base URL from repo config if relative).
2. Set up listeners — Playwright auto-captures console and network. Drive the repro steps via `browser_click` / `browser_type` / `browser_fill_form`.
3. At the failure point capture:
   - `browser_console_messages` → console errors, uncaught exceptions, unhandled rejections.
   - `browser_network_requests` → 4xx/5xx responses, CORS errors, request/response headers.
   - `browser_take_screenshot` → save to `/tmp/debugger-<timestamp>.png`, reference by path.
   - `browser_snapshot` → DOM/accessibility tree at moment of failure.
4. Pull the request-id / trace-id from any backend response headers and feed it to Step 3b.

If the user gave a named repro recipe from the repo config ("run the checkout repro"), follow that recipe's steps verbatim.

## Step 3b: backend investigation (logs)

**Choose source per repo config.** Read the Dozzle URL (and token, if any) directly from `.claude/debugger.md` — do not require an env var from the user. Use the value inline in your curl command.

- **Dozzle (v10+, SSE):** `curl -s --max-time 5 "<DOZZLE_URL>/api/hosts/<host-id>/containers/<id>/logs?lastEventId=0"` (omit Authorization header if no token in config; add `-H "Authorization: Bearer <token>"` only if config declares one). If the v10 path 404s, fall back to legacy `<DOZZLE_URL>/api/logs/<container>?since=10m`.
- **Docker fallback:** `docker logs --since 10m <container>` or `docker compose -p <project> logs --since 10m <service>`.

**Methodology:**

1. Find the request-id / trace-id in the error (or from Step 3a).
2. Grep that ID across every relevant container per the repo's service→container map.
3. Reconstruct the request flow in time order.
4. Locate the code by grepping the codebase for the exact message or symbol from the stack trace.
5. Read the code + surrounding context (use `Read` with a tight line range).
6. Form 2–3 hypotheses; describe how each could be ruled out with one more piece of evidence.

## Step 4: diagnose

Report to the user in this exact shape:

```
## Diagnosis

**Symptom:** <one line>
**Root cause (most likely):** <one paragraph>
**Evidence:**
  - <log line / Playwright capture / code reference> at <path:line or container@time>
  - ...
**Alternative hypotheses:**
  1. <hypothesis> — ruled out by <evidence> / would need <evidence to confirm>
  2. ...
```

## Step 5: propose patch (do not apply yet)

```
## Proposed fix

File: <path>
Change: <one sentence>

<diff-style snippet or before/after>

Apply? (yes / no / change-direction)
```

Wait for explicit user OK. If the user pushes back, re-diagnose with their feedback.

## Step 6: apply + re-verify

On user OK:

1. `Edit` the file(s).
2. Re-run the reproduction:
   - **UI bug** → Playwright re-runs the same script. Same capture set. Compare to baseline.
   - **Backend** → re-trigger (curl, retry the failing test, or the user-provided trigger) and re-check logs for the trace-id pattern.
3. **Green?** Done. Report what was fixed and what was verified.
4. **Still failing?** Loop back to Step 4 with the new evidence. New diagnosis, new proposal, new OK.

## Iteration cap

After **5 iterations** without green, stop:

```
## Out of iterations

Tried (in order):
  1. <one-line summary of each attempt>
  ...

Current understanding: <what we now believe>
Next thing to try: <suggestion>

Handing back to you.
```

Do not silently keep looping.

## Policy (non-negotiable)

| Rule | Why |
|---|---|
| **PII redaction** | Never quote emails, tokens, full request bodies. Summarize ("user email", "auth token", "8KB JSON payload with 12 line items"). |
| **`since=10m` default** | Keeps log volume bounded. Widen only with explicit cause (e.g., "intermittent, last seen 2 hours ago"). |
| **≤500 log lines to chat** | Refine the filter first. If you'd need more, narrow by trace-id, container, or grep pattern. |
| **Screenshots by path, not embed** | Save to `/tmp/`, reference path. Embedding large base64 wastes context. |
| **Tunnel down = stop** | If curl returns "connection refused" or Dozzle is 5xx, tell the user once and stop. No retry loop. |
| **No silent edits** | Every `Edit` requires explicit user OK in this turn. Prior "yes" does not authorize future edits. |
| **No destructive ops** | Never `rm`, `git reset --hard`, `docker rm`, drop tables, etc., even if it'd "isolate" the bug. |

## Conventions to read from repo config

Use these names exactly as the repo declares them — do not invent your own:

- Service name → container ID mapping.
- Request-ID header (e.g., `X-Request-ID`, `traceparent`, `x-correlation-id`).
- Log format (JSON vs text, field names).
- Known noise patterns to grep -v.
- Decision tree: "symptom X → check container Y first".

## Scripts

| Script | Purpose |
|---|---|
| `scripts/discover-stack.sh` | One-time per repo: probes Dozzle + docker, generates `.claude/debugger.md` skeleton with real container names and recent log samples. Never overwrites existing config — writes `.new` for diff. |

Invoke via:

```
/debugger discover-stack
```

The skill reads `DOZZLE_URL` / `DOZZLE_TOKEN` from the existing `.claude/debugger.md` if present, or prompts once on first run. No manual env-var setup required.
