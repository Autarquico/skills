#!/usr/bin/env bash
# autarqui-video-gen — installer
#
# Usage:
#   install.sh                  Install Tier A required (always) + skill venv + Remotion
#   install.sh --tier-a         Same as above (default)
#   install.sh --all            Tier A + all optional tools (Piper, Whisper, Manim, etc.)
#   install.sh --tool <name>    Install a single optional tool (yt-dlp|piper|whisper|coqui|manim|demucs)
#   install.sh --tier-c         Opt-in heavy tools (Stable Diffusion etc, requires GPU)

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSITIONS_DIR="$SKILL_DIR/compositions"
VENV_DIR="$SKILL_DIR/.venv"

# Parse mode
MODE="${1:-tier-a}"
case "$MODE" in
  --all)        MODE="all" ;;
  --tier-a|"")  MODE="tier-a" ;;
  --tool)       MODE="tool"; shift; SINGLE_TOOL="${1:-}"; [ -n "$SINGLE_TOOL" ] || { echo "ERROR: --tool requires a name"; exit 1; } ;;
  --tier-c)     bash "$SKILL_DIR/scripts/install-tier-c.sh"; exit 0 ;;
esac

PLATFORM="unknown"
case "$(uname -s)" in
  Darwin*)   PLATFORM="macos" ;;
  Linux*)    PLATFORM="linux" ;;
esac

echo "═══════════════════════════════════════════════════════════"
echo "  autarqui-video-gen installer  ·  mode: $MODE  ·  $PLATFORM"
echo "═══════════════════════════════════════════════════════════"
echo

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

require_cmd() {
  command -v "$1" &>/dev/null
}

brew_install() {
  if [ "$PLATFORM" = "macos" ] && require_cmd brew; then
    brew install "$@" || true
  else
    return 1
  fi
}

apt_install() {
  if [ "$PLATFORM" = "linux" ] && require_cmd apt-get; then
    sudo apt-get install -y "$@" || true
  else
    return 1
  fi
}

confirm() {
  local prompt="$1"
  read -p "$prompt [y/N] " ans
  [[ "$ans" =~ ^[Yy] ]]
}

# ---------------------------------------------------------------------------
# Tier A required: ffmpeg, node, python3
# ---------------------------------------------------------------------------

check_required() {
  local missing=0
  echo "==> Tier A required tools:"
  for cmd in node npm ffmpeg python3; do
    if require_cmd "$cmd"; then
      printf "    ✓ %s\n" "$cmd"
    else
      printf "    ✗ %s — MISSING\n" "$cmd"
      missing=$((missing + 1))
    fi
  done
  if [ $missing -gt 0 ]; then
    echo
    echo "Required tools missing. Install instructions:"
    echo "  • Node.js + npm:  https://nodejs.org  (or: brew install node / apt install nodejs npm)"
    echo "  • ffmpeg:         brew install ffmpeg / sudo apt install ffmpeg"
    echo "  • Python 3.10+:   https://www.python.org  (or: brew install python@3.12)"
    exit 1
  fi
  echo
}

check_required

# ---------------------------------------------------------------------------
# Skill-local Python venv (so PyYAML and others Just Work regardless of system Python)
# ---------------------------------------------------------------------------

if [ ! -d "$VENV_DIR" ]; then
  echo "==> Creating skill-local Python venv at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

# Always upgrade pip + install pyyaml in the venv
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet pyyaml

echo "    ✓ venv ready (pyyaml installed)"
echo

# ---------------------------------------------------------------------------
# Remotion compositions — npm install
# ---------------------------------------------------------------------------

echo "==> Installing Remotion compositions ($COMPOSITIONS_DIR)"
if [ ! -d "$COMPOSITIONS_DIR/node_modules" ]; then
  (cd "$COMPOSITIONS_DIR" && npm install --no-fund --no-audit) || {
    echo "ERROR: npm install failed"
    exit 1
  }
else
  echo "    node_modules already present (run \`rm -rf $COMPOSITIONS_DIR/node_modules && avg install\` to refresh)"
fi
echo

# ---------------------------------------------------------------------------
# Config bootstrap
# ---------------------------------------------------------------------------

if [ ! -f "$SKILL_DIR/config/api-keys.yaml" ]; then
  cp "$SKILL_DIR/config/api-keys.yaml.template" "$SKILL_DIR/config/api-keys.yaml"
  echo "==> Created $SKILL_DIR/config/api-keys.yaml from template"
  echo "    → Edit and add your free Pixabay/Pexels/Unsplash/Freesound keys."
else
  echo "==> $SKILL_DIR/config/api-keys.yaml already exists (leaving as-is)"
fi
echo

# ---------------------------------------------------------------------------
# .gitkeep markers
# ---------------------------------------------------------------------------

for d in "$SKILL_DIR"/cache/*/; do
  touch "$d/.gitkeep"
done

# ---------------------------------------------------------------------------
# Optional tool installers (called from --all or --tool)
# ---------------------------------------------------------------------------

install_yt_dlp() {
  echo "==> Installing yt-dlp (Tier A optional)"
  "$VENV_DIR/bin/pip" install --quiet yt-dlp
  # symlink so it's on PATH when user has venv activated, OR direct call via avg
  echo "    ✓ yt-dlp"
}

install_piper() {
  echo "==> Installing Piper TTS (Tier A optional)"
  if [ "$PLATFORM" = "macos" ]; then
    brew_install piper-tts || "$VENV_DIR/bin/pip" install --quiet piper-tts
  else
    "$VENV_DIR/bin/pip" install --quiet piper-tts || true
  fi
  echo "    ✓ Piper (run \`piper --help\` to verify; voices auto-download on first use)"
}

install_whisper() {
  echo "==> Installing whisper.cpp (Tier A optional)"
  if [ "$PLATFORM" = "macos" ]; then
    brew_install whisper-cpp
  else
    echo "    ⚠ Linux: build from https://github.com/ggml-org/whisper.cpp (no apt package)"
  fi
}

install_coqui() {
  echo "==> Installing Coqui XTTS (Tier A optional, ~500MB models on first use)"
  "$VENV_DIR/bin/pip" install --quiet TTS
  echo "    ✓ Coqui (run \`tts --list_models\` to verify; XTTS-v2 ~2GB downloads on first synth)"
}

install_manim() {
  echo "==> Installing Manim CE (Tier A optional)"
  if [ "$PLATFORM" = "macos" ]; then
    brew_install cairo pango pkg-config || true
  else
    apt_install libcairo2-dev libpango1.0-dev pkg-config || true
  fi
  "$VENV_DIR/bin/pip" install --quiet manim
  echo "    ✓ Manim (run \`manim --version\` to verify)"
}

install_demucs() {
  echo "==> Installing DemucS (Tier A optional, ~500MB model on first use)"
  "$VENV_DIR/bin/pip" install --quiet demucs
  echo "    ✓ DemucS"
}

install_imagemagick() {
  echo "==> Installing ImageMagick + librsvg (Tier A optional)"
  if [ "$PLATFORM" = "macos" ]; then
    brew_install imagemagick librsvg
  else
    apt_install imagemagick librsvg2-bin
  fi
}

install_local_video() {
  echo "==> Installing local video generation deps (LTX-Video on Apple Silicon / CUDA)"
  echo "    Python packages (~3 GB): diffusers + transformers + accelerate + torch + sentencepiece + imageio"
  "$VENV_DIR/bin/pip" install --quiet --upgrade pip
  "$VENV_DIR/bin/pip" install --quiet diffusers transformers accelerate sentencepiece tiktoken protobuf "imageio[ffmpeg]"
  "$VENV_DIR/bin/pip" install --quiet torch torchvision
  echo "    ✓ deps installed in $VENV_DIR"
  echo
  echo "    Note: The LTX-Video model (~7 GB bfloat16) downloads on FIRST generation,"
  echo "    cached at: $SKILL_DIR/cache/models/ltx-video/"
  echo "    First generation takes ~10 min (download + load). Subsequent: 3-5 min on M-series."
  echo
  echo "    Quick test:"
  echo "      avg local-video generate \\"
  echo "        --prompt 'Slow cinematic dolly across a quiet workshop, natural light' \\"
  echo "        --duration 4 --aspect 16:9 --resolution medium --to /tmp/test.mp4"
}

install_one_tool() {
  case "$1" in
    yt-dlp)        install_yt_dlp ;;
    piper)         install_piper ;;
    whisper)       install_whisper ;;
    coqui)         install_coqui ;;
    manim)         install_manim ;;
    demucs)        install_demucs ;;
    imagemagick)   install_imagemagick ;;
    local-video)   install_local_video ;;
    pyyaml)        "$VENV_DIR/bin/pip" install --quiet pyyaml; echo "✓ pyyaml" ;;
    *)
      echo "ERROR: unknown tool '$1'. Available: yt-dlp piper whisper coqui manim demucs imagemagick local-video pyyaml"
      exit 1
      ;;
  esac
}

if [ "$MODE" = "tool" ]; then
  install_one_tool "$SINGLE_TOOL"
elif [ "$MODE" = "all" ]; then
  echo "==> Installing ALL optional Tier A tools (this takes a while)..."
  install_imagemagick
  install_yt_dlp
  install_piper
  install_whisper
  install_manim
  install_demucs
  echo "    (Skipping Coqui XTTS by default — run \`avg install --tool coqui\` if you want it; it's ~2GB)"
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

echo
echo "═══════════════════════════════════════════════════════════"
echo "  Install complete."
echo
echo "  Next steps:"
echo "    1. Edit free API keys (optional but recommended for Pixabay etc):"
echo "         $SKILL_DIR/config/api-keys.yaml"
echo "    2. Verify everything:"
echo "         avg doctor"
echo "    3. Try the demo render:"
echo "         avg render delta-launch-demo"
echo "    4. Create a new video:"
echo "         avg new my-video --style autarqui-co --duration 30"
echo
echo "  Add the avg CLI to PATH for convenience:"
echo "         export PATH=\"$SKILL_DIR/scripts:\$PATH\""
echo "    (add that line to ~/.zshrc or ~/.bashrc)"
echo "═══════════════════════════════════════════════════════════"
