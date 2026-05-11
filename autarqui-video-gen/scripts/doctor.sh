#!/usr/bin/env bash
# autarqui-video-gen — health check
# Reports: tools, API keys, styles, scene registry, music library, cache, demo status.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "═══════════════════════════════════════════════════════════"
echo "  autarqui-video-gen — doctor"
echo "═══════════════════════════════════════════════════════════"
echo

# ----------------------------------------------------------------------------
# System tools
# ----------------------------------------------------------------------------

check() {
  local label="$1"; local cmd="$2"
  if command -v "$cmd" &>/dev/null; then
    local v=""
    case "$cmd" in
      ffmpeg)        v=$(ffmpeg -version 2>&1 | head -1 | awk '{print $3}') ;;
      node)          v=$(node --version) ;;
      npm)           v=$(npm --version) ;;
      python3)       v=$(python3 --version 2>&1 | awk '{print $2}') ;;
      yt-dlp)        v=$(yt-dlp --version 2>&1) ;;
      manim)         v=$(manim --version 2>&1 | head -1 | awk '{print $NF}') ;;
      magick)        v=$(magick --version 2>/dev/null | head -1 | awk '{print $3}') ;;
      rsvg-convert)  v=$(rsvg-convert --version 2>/dev/null | head -1 | awk '{print $3}') ;;
      *)             v="installed" ;;
    esac
    printf "  ✓ %-18s %s\n" "$label" "$v"
  else
    printf "  ✗ %-18s (not installed)\n" "$label"
  fi
}

echo "TIER A — required (local tools)"
check "ffmpeg"       ffmpeg
check "node"         node
check "npm"          npm
check "python3"      python3
echo

echo "TIER A — optional"
check "yt-dlp"       yt-dlp
check "whisper.cpp"  whisper-cli
check "piper"        piper
check "coqui XTTS"   tts
check "manim"        manim
check "demucs"       demucs
check "ImageMagick"  magick
check "rsvg-convert" rsvg-convert
echo

# ----------------------------------------------------------------------------
# Remotion compositions
# ----------------------------------------------------------------------------

echo "REMOTION COMPOSITIONS"
if [ -d "$SKILL_DIR/compositions/node_modules" ]; then
  REMOTION_VERSION=$(node -e "console.log(require('$SKILL_DIR/compositions/node_modules/remotion/package.json').version)" 2>/dev/null || echo "unknown")
  printf "  ✓ %-18s %s\n" "remotion" "$REMOTION_VERSION"
else
  printf "  ✗ %-18s (run scripts/install.sh)\n" "node_modules"
fi
echo

# ----------------------------------------------------------------------------
# Scene registry
# ----------------------------------------------------------------------------

echo "SCENE REGISTRY (compositions/src/scenes/)"
SCENES=$(grep -E '^\s*"[a-z-]+":\s*\{' "$SKILL_DIR/compositions/src/scenes/index.ts" 2>/dev/null | sed -E 's/.*"([a-z-]+)".*/  • \1/' | sort -u || true)
if [ -n "$SCENES" ]; then
  echo "$SCENES"
else
  echo "  ✗ Could not parse scenes/index.ts"
fi
echo

# ----------------------------------------------------------------------------
# API keys
# ----------------------------------------------------------------------------

echo "API KEYS (config/api-keys.yaml)"
KEYS_FILE="$SKILL_DIR/config/api-keys.yaml"
if [ ! -f "$KEYS_FILE" ]; then
  echo "  ✗ Not configured. Run scripts/install.sh, then edit $KEYS_FILE"
else
  python3 - <<EOF
import yaml
with open("$KEYS_FILE") as f:
    cfg = yaml.safe_load(f) or {}
for name in ["pixabay", "pexels", "unsplash", "freesound", "lottiefiles"]:
    val = cfg.get(name, "")
    mark = "✓" if val else "⌀"
    masked = (val[:4] + "…" + val[-4:]) if val and len(val) > 8 else ("(empty)" if not val else "***")
    print(f"  {mark} {name:18}{masked}")
EOF
fi
echo

# ----------------------------------------------------------------------------
# Styles (with parse validation)
# ----------------------------------------------------------------------------

echo "STYLES (styles/)"
shopt -s nullglob
STYLE_FILES=("$SKILL_DIR/styles/"*.visual-style.md)
if [ ${#STYLE_FILES[@]} -eq 0 ]; then
  echo "  ✗ No styles found."
else
  for s in "${STYLE_FILES[@]}"; do
    name=$(basename "$s" .visual-style.md)
    # Validate YAML frontmatter parses
    PARSE_OK=$(python3 - <<EOF
import sys
try:
    import yaml
except ImportError:
    print("noyaml"); sys.exit()
with open("$s") as f:
    raw = f.read()
parts = raw.split("---", 2)
if len(parts) < 3:
    print("nofm"); sys.exit()
try:
    data = yaml.safe_load(parts[1])
    has_colors = bool(data.get("colors"))
    has_typo = bool(data.get("typography"))
    print("ok" if (has_colors and has_typo) else "incomplete")
except Exception as e:
    print(f"invalid")
EOF
)
    case "$PARSE_OK" in
      ok)         printf "  ✓ %-30s tokens valid\n" "$name" ;;
      incomplete) printf "  △ %-30s frontmatter parses but incomplete (missing colors/typography)\n" "$name" ;;
      invalid)    printf "  ✗ %-30s YAML parse error\n" "$name" ;;
      nofm)       printf "  ✗ %-30s no frontmatter\n" "$name" ;;
      noyaml)     printf "  ? %-30s (pyyaml missing — can't validate)\n" "$name" ;;
    esac
  done
fi
echo

# ----------------------------------------------------------------------------
# Project workspaces (renders ready)
# ----------------------------------------------------------------------------

echo "PROJECT WORKSPACES (compositions/src/projects/)"
shopt -s nullglob
PROJECT_DIRS=("$SKILL_DIR/compositions/src/projects/"*/)
if [ ${#PROJECT_DIRS[@]} -eq 0 ]; then
  echo "  ⌀ No projects yet. Use script-director to create one."
else
  for pd in "${PROJECT_DIRS[@]}"; do
    name=$(basename "$pd")
    has_comp="✗"
    has_script="✗"
    [ -f "$pd/Composition.tsx" ] && has_comp="✓"
    [ -f "$pd/script.json" ] && has_script="✓"
    printf "  • %-30s Composition:%s  script.json:%s\n" "$name" "$has_comp" "$has_script"
  done
fi
echo

# ----------------------------------------------------------------------------
# Recent renders
# ----------------------------------------------------------------------------

echo "RENDERS (compositions/out/)"
if [ -d "$SKILL_DIR/compositions/out" ]; then
  RENDERS=$(ls -t "$SKILL_DIR/compositions/out/"*.mp4 2>/dev/null | head -5)
  if [ -n "$RENDERS" ]; then
    echo "$RENDERS" | while read -r r; do
      size=$(du -h "$r" | cut -f1)
      printf "  ✓ %s (%s)\n" "$(basename "$r")" "$size"
    done
  else
    echo "  ⌀ No renders yet."
  fi
else
  echo "  ⌀ No out/ directory."
fi
echo

# ----------------------------------------------------------------------------
# Music library
# ----------------------------------------------------------------------------

echo "MUSIC LIBRARY"
MUSIC_DIRS=("$HOME/music_library" "$HOME/Music/music_library")
FOUND=0
for md in "${MUSIC_DIRS[@]}"; do
  if [ -d "$md" ]; then
    count=$(find "$md" -maxdepth 1 \( -name "*.mp3" -o -name "*.wav" -o -name "*.m4a" \) 2>/dev/null | wc -l | tr -d ' ')
    printf "  ✓ %s (%s tracks)\n" "$md" "$count"
    FOUND=1
  fi
done
[ "$FOUND" -eq 0 ] && echo "  ⌀ No music_library/ found. Drop tracks at ~/music_library/ for asset director to consider before APIs."
echo

# ----------------------------------------------------------------------------
# Cache summary
# ----------------------------------------------------------------------------

echo "CACHE"
for kind in pixabay pexels unsplash fonts models; do
  d="$SKILL_DIR/cache/$kind"
  if [ -d "$d" ]; then
    count=$(find "$d" -type f -not -name ".gitkeep" 2>/dev/null | wc -l | tr -d ' ')
    printf "  • %s: %s files\n" "$kind" "$count"
  fi
done
echo

echo "═══════════════════════════════════════════════════════════"
echo "  Done. Skill at $SKILL_DIR"
echo "═══════════════════════════════════════════════════════════"
