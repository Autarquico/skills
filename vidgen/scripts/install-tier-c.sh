#!/usr/bin/env bash
# Tier C — heavy local AI deps (Stable Diffusion, AnimateDiff). Opt-in.
# Requires: GPU (CUDA on Linux/Windows, MPS on Apple Silicon).

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$SKILL_DIR/.venv"

cat <<EOF
═══════════════════════════════════════════════════════════
  Tier C installer (opt-in, GPU-required)
═══════════════════════════════════════════════════════════

This installs heavy AI generation models that run locally:

  • Stable Diffusion XL Turbo  (~6 GB, image gen)
  • AnimateDiff                (~4 GB, short video gen)

Requirements:
  • macOS Apple Silicon (M1/M2/M3/M4) — uses MPS backend, OR
  • Linux/Windows with NVIDIA GPU + CUDA 12+

Disk: ~15 GB total
Download time: 30-60 min on first install
Render time per asset: 30s-5min depending on settings

Tier C is NOT required to use the skill. Pixabay + Pexels + Three.js
+ Lottie cover most needs at zero local cost.

EOF

read -p "Continue? [y/N] " ans
[[ "$ans" =~ ^[Yy] ]] || { echo "Aborted."; exit 0; }

# Detect GPU
GPU="cpu"
if [ "$(uname -s)" = "Darwin" ] && [ "$(uname -m)" = "arm64" ]; then
  GPU="mps"
elif command -v nvidia-smi &>/dev/null; then
  GPU="cuda"
fi

if [ "$GPU" = "cpu" ]; then
  echo "ERROR: No GPU detected. Tier C requires Apple Silicon (MPS) or NVIDIA (CUDA)."
  echo "  CPU-only inference is too slow to be practical (10+ min per image)."
  exit 1
fi

echo "==> GPU backend: $GPU"
echo

# Install diffusers + dependencies
echo "==> Installing diffusers + transformers + accelerate (~1 GB)…"
if [ "$GPU" = "mps" ]; then
  "$VENV_DIR/bin/pip" install --quiet torch torchvision diffusers transformers accelerate
elif [ "$GPU" = "cuda" ]; then
  "$VENV_DIR/bin/pip" install --quiet torch torchvision --index-url https://download.pytorch.org/whl/cu121
  "$VENV_DIR/bin/pip" install --quiet diffusers transformers accelerate
fi

echo "==> Tier C installed."
echo "   Models will download to ~/.cache/huggingface/ on first use."
echo "   See $SKILL_DIR/tools/local_ai/ for invocation helpers (TODO — out of scope for MVP)."
