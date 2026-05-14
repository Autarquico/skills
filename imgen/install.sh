#!/usr/bin/env bash
# autarqui-branding-image-generator -- install into ~/.claude/skills/
#
# Usage:
#   bash install.sh                          # install / update
#   bash install.sh --with-mcp AIza...       # also configure the MCP server
#   bash install.sh --uninstall              # remove the installed copy
#
# Reads from this folder (the skill source) and copies into
# ~/.claude/skills/autarqui-branding-image-generator/ — the path used by both
# Claude Code CLI and Claude Desktop.

set -euo pipefail

SKILL_NAME="autarqui-branding-image-generator"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HOME/.claude/skills/$SKILL_NAME"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

API_KEY=""
WITH_MCP=0
UNINSTALL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-mcp)  WITH_MCP=1; API_KEY="${2:-}"; shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help)   sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) error "Unknown argument: $1"; exit 1 ;;
  esac
done

if [[ $UNINSTALL -eq 1 ]]; then
  if [[ -d "$DEST" ]]; then
    rm -rf "$DEST"
    info "Removed $DEST"
  else
    warn "Skill not installed at $DEST"
  fi
  exit 0
fi

info "Installing $SKILL_NAME → $DEST"
mkdir -p "$DEST"
# rsync-style: copy contents, not the source dir itself
cp -R "$SRC"/. "$DEST"/
# Don't ship the installer to the runtime location — Claude reads SKILL.md there
rm -f "$DEST/install.sh"
chmod +x "$DEST"/scripts/*.py 2>/dev/null || true
info "Skill installed."

mkdir -p "$HOME/.banana/presets" "$HOME/.banana/brands"
info "Inventory dirs ready: ~/.banana/{presets,brands}/"

if [[ $WITH_MCP -eq 1 ]]; then
  if [[ -z "$API_KEY" ]]; then error "--with-mcp requires an API key"; exit 1; fi
  info "Configuring MCP server (@ycse/nanobanana-mcp)…"
  python3 "$DEST/scripts/setup_mcp.py" --key "$API_KEY"
else
  warn "MCP not configured. Run later:"
  warn "  python3 \"$DEST/scripts/setup_mcp.py\" --key AIza..."
  warn "Or export GOOGLE_AI_API_KEY in your shell to use the REST fallback scripts."
fi

python3 "$DEST/scripts/validate_setup.py" || true

cat <<EOF

${GREEN}Done.${NC}
  Skill: $SKILL_NAME
  Path:  $DEST
  Data:  $HOME/.banana/{presets,brands}/

Next:
  - In Claude Code / Claude Desktop, try: "generate an image of …"
  - Create a brand:
      python3 "$DEST/scripts/brands.py" init my-brand --images logo.png,sample.jpg
EOF
