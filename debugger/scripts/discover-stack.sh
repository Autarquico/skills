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

DOZZLE_URL="${DOZZLE_URL:-}"
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
DOZZLE_API=""
if [ -n "$DOZZLE_URL" ]; then
  SOURCE="dozzle"
  info "Source: Dozzle at $DOZZLE_URL"
elif command -v docker >/dev/null 2>&1; then
  SOURCE="docker"
  info "DOZZLE_URL unset — using local docker."
else
  err "No DOZZLE_URL and no docker CLI available. Set DOZZLE_URL or install docker."
  exit 1
fi

# --- Probe -------------------------------------------------------------------

CONTAINERS_JSON=""
DOZZLE_HOST_ID=""
case "$SOURCE" in
  dozzle)
    # Reachability probe.
    if ! curl -s --max-time 5 -o /dev/null -w '%{http_code}' "$DOZZLE_URL/" | grep -q '^[23]'; then
      err "Dozzle unreachable at $DOZZLE_URL."
      exit 1
    fi

    AUTH=()
    [ -n "$DOZZLE_TOKEN" ] && AUTH=(-H "Authorization: Bearer $DOZZLE_TOKEN")

    # Dozzle v10+ uses SSE at /api/events/stream emitting a `containers-changed`
    # event with the full container list. Older versions had /api/containers.
    HTTP_CODE=$(curl -s ${AUTH[@]+"${AUTH[@]}"} -o /tmp/dz-containers.json -w '%{http_code}' \
      "$DOZZLE_URL/api/containers" 2>/dev/null || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
      DOZZLE_API="rest"
      CONTAINERS_JSON=$(cat /tmp/dz-containers.json)
    else
      # SSE path — read events for ~2s, extract the first containers-changed payload.
      info "REST API not present (HTTP $HTTP_CODE); falling back to SSE (Dozzle v10+)."
      DOZZLE_API="sse"
      curl -s --max-time 3 ${AUTH[@]+"${AUTH[@]}"} "$DOZZLE_URL/api/events/stream" 2>/dev/null \
        > /tmp/dz-stream.txt || true
      if [ ! -s /tmp/dz-stream.txt ]; then
        err "Dozzle SSE stream returned nothing. Check auth or URL."
        exit 1
      fi
      CONTAINERS_JSON=$(awk '
        /^event: containers-changed/ { want=1; next }
        want && /^data: / { sub(/^data: /,""); print; exit }
      ' /tmp/dz-stream.txt)
      if [ -z "$CONTAINERS_JSON" ]; then
        err "Could not parse containers from Dozzle SSE stream."
        exit 1
      fi
      if [ "$HAS_JQ" = "1" ]; then
        DOZZLE_HOST_ID=$(echo "$CONTAINERS_JSON" | jq -r '.[0].host // empty' 2>/dev/null)
      fi
    fi
    ;;
  docker)
    if ! docker ps >/dev/null 2>&1; then
      err "docker ps failed. Is the docker daemon running?"
      exit 1
    fi
    CONTAINERS_JSON=$(docker ps --format '{"name":"{{.Names}}","image":"{{.Image}}","status":"{{.Status}} ({{.State}})","host":"local"}' \
                       | jq -s '.' 2>/dev/null || docker ps --format '{{.Names}}|{{.Image}}|{{.Status}}')
    ;;
esac

# --- Fetch log samples -------------------------------------------------------

fetch_logs_dozzle() {
  local container_id="$1"
  local auth=()
  [ -n "$DOZZLE_TOKEN" ] && auth=(-H "Authorization: Bearer $DOZZLE_TOKEN")
  if [ "$DOZZLE_API" = "sse" ] && [ -n "$DOZZLE_HOST_ID" ]; then
    # v10: /api/hosts/<host>/containers/<id>/logs?... — also an SSE-ish stream.
    curl -s --max-time 3 ${auth[@]+"${auth[@]}"} \
      "$DOZZLE_URL/api/hosts/$DOZZLE_HOST_ID/containers/$container_id/logs?lastEventId=0" 2>/dev/null \
      | sed -n 's/^data: //p' | tail -n 20
  else
    curl -s --max-time 3 ${auth[@]+"${auth[@]}"} \
      "$DOZZLE_URL/api/logs/$container_id?since=5m" 2>/dev/null | tail -n 20
  fi
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

  # Extract container identifiers. Dozzle v10 needs the container id for log
  # fetch; docker can use the name.
  ENTRIES=""
  if [ "$HAS_JQ" = "1" ] && echo "$CONTAINERS_JSON" | jq -e . >/dev/null 2>&1; then
    ENTRIES=$(echo "$CONTAINERS_JSON" | jq -r '
      (if type == "array" then . else [.] end)[]
      | "\(.name // .Name // "?")\t\(.id // .Id // .name // .Name // "?")"
    ')
  fi

  if [ -z "$ENTRIES" ] && [ "$SOURCE" = "docker" ]; then
    ENTRIES=$(docker ps --format '{{.Names}}	{{.Names}}')
  fi

  while IFS=$'\t' read -r name id; do
    [ -z "$name" ] && continue
    echo "#### $name"
    echo ""
    echo '```'
    if [ "$SOURCE" = "dozzle" ]; then
      out=$(fetch_logs_dozzle "$id")
    else
      out=$(fetch_logs_docker "$name")
    fi
    if [ -z "$out" ]; then
      echo "(no recent logs)"
    else
      echo "$out"
    fi
    echo '```'
    echo ""
  done <<< "$ENTRIES"
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
