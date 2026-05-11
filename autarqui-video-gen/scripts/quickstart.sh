#!/usr/bin/env bash
# autarqui-video-gen — one-line installer
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/Autarquico/skills/main/autarqui-video-gen/scripts/quickstart.sh | bash
#
# What it does:
#   1. Verifies system tools (git, node, npm, ffmpeg, python3)
#   2. Sparse-clones autarqui-video-gen/ from the Autarquico/skills monorepo
#      into ~/.claude/skills/autarqui-video-gen/
#   3. Runs install.sh (creates venv, installs Remotion, bootstraps config)
#   4. Optionally adds `avg` to PATH
#   5. Runs `avg doctor`

set -euo pipefail

SKILL_NAME="autarqui-video-gen"
SKILL_DIR="$HOME/.claude/skills/$SKILL_NAME"
REPO_URL="${AUTARQUI_REPO_URL:-https://github.com/Autarquico/skills.git}"
REPO_BRANCH="${AUTARQUI_REPO_BRANCH:-main}"
SUBFOLDER="autarqui-video-gen"

# ---------------------------------------------------------------------------
# Pretty output
# ---------------------------------------------------------------------------

bold() { printf "\033[1m%s\033[0m\n" "$1"; }
info() { printf "  \033[36m·\033[0m %s\n" "$1"; }
ok()   { printf "  \033[32m✓\033[0m %s\n" "$1"; }
err()  { printf "  \033[31m✗\033[0m %s\n" "$1" >&2; }

bold "════════════════════════════════════════════════════════════"
bold "  autarqui-video-gen — quickstart installer"
bold "════════════════════════════════════════════════════════════"
echo

# ---------------------------------------------------------------------------
# 1. System prerequisites
# ---------------------------------------------------------------------------

bold "→ Checking system tools"

require() {
  if command -v "$1" &>/dev/null; then
    ok "$1"
  else
    err "$1 — MISSING"
    return 1
  fi
}

MISSING=0
require git     || MISSING=$((MISSING+1))
require node    || MISSING=$((MISSING+1))
require npm     || MISSING=$((MISSING+1))
require ffmpeg  || MISSING=$((MISSING+1))
require python3 || MISSING=$((MISSING+1))

if [ "$MISSING" -gt 0 ]; then
  echo
  err "$MISSING required tools missing. Install instructions:"
  echo "    macOS:   brew install git node ffmpeg python@3.12"
  echo "    Linux:   sudo apt install git nodejs npm ffmpeg python3 python3-venv"
  echo "    Windows: install via WSL2 (Ubuntu) and re-run"
  exit 1
fi
echo

# ---------------------------------------------------------------------------
# 2. Clone (or update) the skill
# ---------------------------------------------------------------------------

bold "→ Installing skill at $SKILL_DIR"

mkdir -p "$(dirname "$SKILL_DIR")"

if [ -d "$SKILL_DIR" ] && [ -e "$SKILL_DIR/SKILL.md" ]; then
  info "Skill already present at $SKILL_DIR"
  read -r -p "  Reinstall (overwrites tracked files, keeps cache/.venv/projects)? [y/N] " ans
  if [[ ! "$ans" =~ ^[Yy] ]]; then
    info "Skipping. Run with empty target dir for fresh install."
    exit 0
  fi
fi

# Sparse-checkout the subfolder from the monorepo into a temp dir, then move it.
TMP_CLONE="$(mktemp -d -t autarqui-skills-XXXXXX)"
trap "rm -rf '$TMP_CLONE'" EXIT

info "Cloning $REPO_URL ($SUBFOLDER subfolder only)"
git clone --quiet --depth 1 --branch "$REPO_BRANCH" \
  --filter=blob:none --no-checkout \
  "$REPO_URL" "$TMP_CLONE" >/dev/null
git -C "$TMP_CLONE" sparse-checkout init --cone --quiet
git -C "$TMP_CLONE" sparse-checkout set "$SUBFOLDER" --quiet
git -C "$TMP_CLONE" checkout --quiet "$REPO_BRANCH"

if [ ! -d "$TMP_CLONE/$SUBFOLDER" ]; then
  err "Subfolder '$SUBFOLDER' not found in $REPO_URL@$REPO_BRANCH"
  exit 1
fi

mkdir -p "$SKILL_DIR"
# Copy without overwriting cache/.venv/projects
rsync -a --exclude=cache --exclude=.venv \
  --exclude=compositions/node_modules --exclude=compositions/out \
  "$TMP_CLONE/$SUBFOLDER/" "$SKILL_DIR/"
ok "Installed at $SKILL_DIR"
echo

# ---------------------------------------------------------------------------
# 3. Run install.sh (creates venv, installs Remotion deps, bootstraps config)
# ---------------------------------------------------------------------------

bold "→ Running install.sh (creates Python venv, npm install Remotion, ~3-5 min)"
"$SKILL_DIR/scripts/install.sh"
echo

# ---------------------------------------------------------------------------
# 4. PATH offer
# ---------------------------------------------------------------------------

bold "→ Add \`avg\` CLI to PATH?"

PATH_LINE="export PATH=\"\$HOME/.claude/skills/$SKILL_NAME/scripts:\$PATH\""

if echo ":$PATH:" | grep -q ":$SKILL_DIR/scripts:"; then
  ok "Already on PATH"
else
  RC_FILE=""
  case "${SHELL:-}" in
    */zsh)  RC_FILE="$HOME/.zshrc" ;;
    */bash) RC_FILE="$HOME/.bashrc" ;;
    */fish) RC_FILE="$HOME/.config/fish/config.fish" ;;
  esac

  if [ -t 0 ] && [ -n "$RC_FILE" ]; then
    info "Detected shell rc: $RC_FILE"
    read -r -p "  Add to PATH automatically? [y/N] " ans
    if [[ "$ans" =~ ^[Yy] ]]; then
      if [[ "$RC_FILE" == *fish* ]]; then
        echo "fish_add_path \$HOME/.claude/skills/$SKILL_NAME/scripts" >> "$RC_FILE"
      else
        echo "$PATH_LINE" >> "$RC_FILE"
      fi
      ok "Added to $RC_FILE — open a new terminal or run: source $RC_FILE"
    else
      info "Skipped. To add manually later:"
      echo "    echo '$PATH_LINE' >> $RC_FILE"
    fi
  else
    info "Non-interactive run — to add to PATH manually:"
    echo "    echo '$PATH_LINE' >> ~/.zshrc"
    echo "    source ~/.zshrc"
  fi
fi
echo

# ---------------------------------------------------------------------------
# 5. Doctor
# ---------------------------------------------------------------------------

bold "→ Running avg doctor"
"$SKILL_DIR/scripts/avg" doctor
echo

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

bold "════════════════════════════════════════════════════════════"
bold "  Done."
bold "════════════════════════════════════════════════════════════"
cat <<EOF

  Try a render now (uses pre-included demo, ~30s):
      $SKILL_DIR/scripts/avg render delta-launch-demo

  Create a new video:
      $SKILL_DIR/scripts/avg new my-first-video --aspect 9:16 --duration 30

  Optional features (install on demand):
      $SKILL_DIR/scripts/avg install --tool piper        # local TTS
      $SKILL_DIR/scripts/avg install --tool whisper      # subtitle generation
      $SKILL_DIR/scripts/avg install --tool local-video  # LTX-Video local AI gen
      $SKILL_DIR/scripts/avg install --all               # everything above

  Configure free API keys (Pixabay/Pexels/Unsplash/Freesound):
      \$EDITOR $SKILL_DIR/config/api-keys.yaml

  Docs: $SKILL_DIR/README.md
EOF
