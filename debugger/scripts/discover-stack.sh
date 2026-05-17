#!/usr/bin/env bash
# discover-stack.sh — generate or refresh `.claude/debugger.md` for the current repo.
#
# Probes Dozzle (or local docker as fallback), lists containers, samples recent
# logs, and writes a curatable skeleton. Never overwrites an existing config:
# if `.claude/debugger.md` exists, the new content lands at `.claude/debugger.md.new`
# for the user to diff.
#
# Env:
#   DOZZLE_URL     default http://localhost:8080
#   DOZZLE_TOKEN   if set, uses Dozzle; if unset, falls back to local docker
#
# Usage: run from repo root.

set -euo pipefail

DOZZLE_URL="${DOZZLE_URL:-http://localhost:8080}"
DOZZLE_TOKEN="${DOZZLE_TOKEN:-}"
OUT_DIR=".claude"
OUT_FILE="$OUT_DIR/debugger.md"
TARGET_FILE="$OUT_FILE"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

err()  { printf '\033[31merror:\033[0m %s\n' "$*" >&2; }
warn() { printf '\033[33mwarn:\033[0m %s\n' "$*" >&2; }
info() { printf '\033[36m•\033[0m %s\n' "$*" >&2; }

# --- Preflight ---------------------------------------------------------------

if [ ! -d .git ]; then
  err "Must be run from a repo root (no .git/ here)."
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  warn "jq not installed — JSON parsing will be best-effort. Install jq for clean output."
  HAS_JQ=0
else
  HAS_JQ=1
fi

mkdir -p "$OUT_DIR"

if [ -e "$OUT_FILE" ]; then
  TARGET_FILE="$OUT_FILE.new"
  info "$OUT_FILE exists — writing to $TARGET_FILE instead. Diff and merge manually."
fi

# --- Source selection --------------------------------------------------------

SOURCE=""
if [ -n "$DOZZLE_TOKEN" ]; then
  SOURCE="dozzle"
  info "Source: Dozzle at $DOZZLE_URL"
elif command -v docker >/dev/null 2>&1; then
  SOURCE="docker"
  info "DOZZLE_TOKEN unset — falling back to local docker."
else
  err "No DOZZLE_TOKEN and no docker CLI available. Set DOZZLE_TOKEN or install docker."
  exit 1
fi

# --- Probe -------------------------------------------------------------------

CONTAINERS_JSON=""
case "$SOURCE" in
  dozzle)
    # Dozzle exposes /api/containers (v6+) or /api/hosts/<host>/containers.
    # Try the simple endpoint first; if it 404s, try the host-scoped one.
    HTTP_CODE=$(curl -s -o /tmp/dz-containers.json -w '%{http_code}' \
      -H "Authorization: Bearer $DOZZLE_TOKEN" \
      "$DOZZLE_URL/api/containers" || echo "000")
    if [ "$HTTP_CODE" = "000" ]; then
      err "Dozzle unreachable at $DOZZLE_URL (connection refused)."
      exit 1
    fi
    if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
      err "Dozzle auth failed (HTTP $HTTP_CODE). Check DOZZLE_TOKEN."
      exit 1
    fi
    if [ "$HTTP_CODE" = "404" ]; then
      warn "GET /api/containers returned 404 — your Dozzle may use a different API path."
      warn "Try DOZZLE_URL with trailing path, or inspect Dozzle docs for your version."
      exit 1
    fi
    if [ "$HTTP_CODE" != "200" ]; then
      err "Dozzle returned HTTP $HTTP_CODE."
      exit 1
    fi
    CONTAINERS_JSON=$(cat /tmp/dz-containers.json)
    ;;
  docker)
    if ! docker ps >/dev/null 2>&1; then
      err "docker ps failed. Is the docker daemon running?"
      exit 1
    fi
    CONTAINERS_JSON=$(docker ps --format '{"name":"{{.Names}}","image":"{{.Image}}","status":"{{.Status}}","host":"local"}' \
                       | jq -s '.' 2>/dev/null || docker ps --format '{{.Names}}|{{.Image}}|{{.Status}}')
    ;;
esac

# --- Fetch log samples -------------------------------------------------------

fetch_logs_dozzle() {
  local container="$1"
  # since=10m, limit lines client-side
  curl -s -H "Authorization: Bearer $DOZZLE_TOKEN" \
    "$DOZZLE_URL/api/logs/$container?since=5m" 2>/dev/null | tail -n 20
}

fetch_logs_docker() {
  local container="$1"
  docker logs --since 5m "$container" 2>&1 | tail -n 20
}

# --- Emit --------------------------------------------------------------------

{
  cat <<EOF
# debugger config — $(basename "$(pwd)")

> Generated $TS by \`discover-stack.sh\` (source: $SOURCE).
> Curate the [FILL IN] sections below, then delete the \`## Discovery raw\` block at the end.

## Backend log source

[FILL IN] one of:
- **Dozzle:** URL \`$DOZZLE_URL\`, token env var \`DOZZLE_TOKEN\`
- **Docker:** \`docker logs\` / \`docker compose -p <project> logs\`

## Service → container map

[FILL IN] map your logical services to the container names below.

| Service | Container |
|---|---|
| api | [FILL IN] |
| web | [FILL IN] |
| worker | [FILL IN] |
| db | [FILL IN] |

## Logging conventions

- **Request-ID header:** [FILL IN] (e.g., \`X-Request-ID\`, \`traceparent\`)
- **Log format:** [FILL IN] (json | text)
- **Trace-id field name (in logs):** [FILL IN] (e.g., \`request_id\`, \`trace_id\`)

## Frontend (Playwright)

- **Base URL:** [FILL IN] (e.g., \`http://localhost:3000\`)
- **Auth setup:** [FILL IN] (test account, how to log in, or storageState path)

## Repro recipes

[FILL IN] named flows that come up often. Example:

\`\`\`
### checkout
1. Navigate to /products/sample
2. Click "Add to cart"
3. Navigate to /checkout
4. Fill the form and click "Pay"
\`\`\`

## Decision tree by symptom

[FILL IN] symptom → first place to look.

- "500 on /api/orders" → check api container, grep for trace-id, then db container.
- "Page won't load" → Playwright capture console + network first.
- "Login loop" → check session/auth middleware container.

## Known noise to ignore

[FILL IN] log patterns that are not interesting and should be \`grep -v\`'d.

- \`healthcheck\`
- \`GET /metrics\`

---

## Discovery raw

> Delete this section after you have filled in the above.

### Containers detected

EOF

  # Container table
  if [ "$HAS_JQ" = "1" ] && echo "$CONTAINERS_JSON" | jq -e . >/dev/null 2>&1; then
    echo "| name | image | status | host |"
    echo "|---|---|---|---|"
    echo "$CONTAINERS_JSON" | jq -r '
      (if type == "array" then . else [.] end)[]
      | "| \(.name // .Name // "?") | \(.image // .Image // "?") | \(.status // .Status // "?") | \(.host // .Host // "local") |"
    '
  else
    echo "\`\`\`"
    echo "$CONTAINERS_JSON"
    echo "\`\`\`"
  fi

  echo ""
  echo "### Recent log samples (last 5 min, 20 lines each)"
  echo ""

  # Extract container names for log sampling
  NAMES=""
  if [ "$HAS_JQ" = "1" ] && echo "$CONTAINERS_JSON" | jq -e . >/dev/null 2>&1; then
    NAMES=$(echo "$CONTAINERS_JSON" | jq -r '(if type == "array" then . else [.] end)[] | (.name // .Name // empty)')
  fi

  if [ -z "$NAMES" ] && [ "$SOURCE" = "docker" ]; then
    NAMES=$(docker ps --format '{{.Names}}')
  fi

  for c in $NAMES; do
    echo "#### $c"
    echo ""
    echo '```'
    if [ "$SOURCE" = "dozzle" ]; then
      out=$(fetch_logs_dozzle "$c")
    else
      out=$(fetch_logs_docker "$c")
    fi
    if [ -z "$out" ]; then
      echo "(no recent logs)"
    else
      echo "$out"
    fi
    echo '```'
    echo ""
  done
} > "$TARGET_FILE"

# --- Done --------------------------------------------------------------------

info "Wrote $TARGET_FILE"
cat <<EOF >&2

Next steps:
  1. Open $TARGET_FILE
  2. Ask Claude: "read .claude/debugger.md and propose how to fill in the empty
     sections using the log samples in 'Discovery raw'".
  3. Curate, commit, then delete the 'Discovery raw' section.
EOF
