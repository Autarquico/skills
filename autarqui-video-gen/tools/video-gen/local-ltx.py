#!/usr/bin/env python3
"""
local-ltx — LTX-Video 2.0 local inference on Apple Silicon (MPS) or CUDA.

Generates short video clips from text prompts (or text + reference image).
Caches outputs by hash of (prompt + config) so re-running same input is free.

Usage:
  local-ltx.py text-to-video --prompt "..." --duration 5 --aspect 16:9 --to clip.mp4
  local-ltx.py image-to-video --image ./photo.jpg --prompt "slow zoom" --duration 5 --to clip.mp4

Requires (installed by `avg install --tool local-video`):
  pip install diffusers transformers accelerate sentencepiece torch torchvision imageio[ffmpeg]

Model (downloads on first use, cached at ~/.claude/skills/autarqui-video-gen/cache/models/ltx-video/):
  Lightricks/LTX-Video  (~7 GB bfloat16, runs in ~10-14 GB peak VRAM)
"""

import argparse
import hashlib
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Skill paths
SKILL_DIR = Path(__file__).resolve().parents[2]
CACHE_DIR = SKILL_DIR / "cache" / "local-video"
MODEL_CACHE = SKILL_DIR / "cache" / "models" / "ltx-video"

# LTX-Video constraints (per Lightricks docs):
#   - width/height multiples of 32, recommended ≥ 480 wide
#   - num_frames must satisfy (num_frames - 1) % 8 == 0 → 9, 17, 25, ... 121, 129, 137, ...
#   - native fps = 24
DEFAULT_FPS = 24


def hash_config(prompt: str, width: int, height: int, num_frames: int, seed: int, steps: int, image_path: str = "") -> str:
    h = hashlib.sha256()
    h.update(prompt.encode("utf-8"))
    h.update(f"|{width}x{height}|{num_frames}f|seed={seed}|steps={steps}|img={image_path}".encode("utf-8"))
    return h.hexdigest()[:16]


def normalize_num_frames(target_frames: int) -> int:
    """LTX requires (num_frames - 1) % 8 == 0. Snap to nearest valid count, min 9."""
    valid_options = [9 + 8 * i for i in range(0, 40)]  # 9, 17, 25, ..., 321
    return min(valid_options, key=lambda v: abs(v - target_frames))


def resolve_dimensions(aspect: str, resolution: str) -> tuple[int, int]:
    """Map (aspect, resolution_preset) → (width, height) — multiples of 32."""
    presets = {
        ("16:9", "small"):  (704, 384),
        ("16:9", "medium"): (1024, 576),
        ("16:9", "large"):  (1216, 704),
        ("9:16", "small"):  (384, 704),
        ("9:16", "medium"): (576, 1024),
        ("9:16", "large"):  (704, 1216),
        ("1:1",  "small"):  (512, 512),
        ("1:1",  "medium"): (768, 768),
        ("1:1",  "large"):  (1024, 1024),
        ("4:5",  "small"):  (480, 608),
        ("4:5",  "medium"): (704, 864),
        ("4:5",  "large"):  (864, 1088),
    }
    if (aspect, resolution) not in presets:
        sys.exit(f"ERROR: unsupported (aspect, resolution): {aspect}, {resolution}")
    return presets[(aspect, resolution)]


def detect_device():
    """Detect best available device: MPS (Apple Silicon), CUDA, or CPU."""
    import torch
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


# ---------------------------------------------------------------------------
# text-to-video
# ---------------------------------------------------------------------------

def cmd_text_to_video(args):
    width, height = resolve_dimensions(args.aspect, args.resolution)
    target_frames = int(args.duration * DEFAULT_FPS)
    num_frames = normalize_num_frames(target_frames)
    actual_duration = num_frames / DEFAULT_FPS

    cache_hash = hash_config(args.prompt, width, height, num_frames, args.seed, args.steps)
    cache_path = CACHE_DIR / f"{cache_hash}.mp4"
    sidecar_path = cache_path.with_suffix(".json")
    out_path = Path(args.to).expanduser()

    print(f"==> Config:", file=sys.stderr)
    print(f"    Prompt: {args.prompt[:120]}{'...' if len(args.prompt) > 120 else ''}", file=sys.stderr)
    print(f"    Size: {width}x{height}", file=sys.stderr)
    print(f"    Frames: {num_frames} ({actual_duration:.2f}s @ {DEFAULT_FPS}fps)", file=sys.stderr)
    print(f"    Seed: {args.seed}, Steps: {args.steps}", file=sys.stderr)
    print(f"    Cache hash: {cache_hash}", file=sys.stderr)

    # Cache check
    if not args.no_cache and cache_path.exists():
        print(f"==> Cached hit: {cache_path}", file=sys.stderr)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(cache_path, out_path)
        print(json.dumps({"path": str(out_path), "cached": True, "duration_s": actual_duration}, ensure_ascii=False))
        return

    # Lazy load — these imports are heavy
    print(f"==> Loading model from {MODEL_CACHE} (first time: ~10 min download)...", file=sys.stderr)
    import torch
    from diffusers import LTXPipeline
    from diffusers.utils import export_to_video

    device = detect_device()
    print(f"==> Device: {device}", file=sys.stderr)
    if device == "cpu":
        print("WARNING: MPS/CUDA not available, falling back to CPU. This will take HOURS.", file=sys.stderr)
        if not args.force_cpu:
            sys.exit("Aborting. Pass --force-cpu to override.")

    dtype = torch.bfloat16 if device != "cpu" else torch.float32
    MODEL_CACHE.mkdir(parents=True, exist_ok=True)

    pipe = LTXPipeline.from_pretrained(
        "Lightricks/LTX-Video",
        torch_dtype=dtype,
        cache_dir=str(MODEL_CACHE),
    )
    pipe = pipe.to(device)

    # Memory optimization for Apple Silicon
    if device == "mps":
        try:
            pipe.enable_attention_slicing()
        except Exception:
            pass

    print(f"==> Generating ({num_frames} frames)…", file=sys.stderr)
    t0 = time.time()
    result = pipe(
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        width=width,
        height=height,
        num_frames=num_frames,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance_scale,
        generator=torch.Generator(device=device).manual_seed(args.seed),
    )
    frames = result.frames[0]
    elapsed = time.time() - t0

    print(f"==> Encoding to MP4…", file=sys.stderr)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    export_to_video(frames, str(cache_path), fps=DEFAULT_FPS)
    shutil.copy(cache_path, out_path)

    # Sidecar metadata
    metadata = {
        "prompt": args.prompt,
        "negative_prompt": args.negative_prompt,
        "width": width,
        "height": height,
        "aspect": args.aspect,
        "resolution_preset": args.resolution,
        "num_frames": num_frames,
        "duration_s": actual_duration,
        "fps": DEFAULT_FPS,
        "seed": args.seed,
        "steps": args.steps,
        "guidance_scale": args.guidance_scale,
        "model": "Lightricks/LTX-Video",
        "device": device,
        "dtype": str(dtype),
        "elapsed_s": round(elapsed, 1),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    sidecar_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"==> Done in {elapsed:.1f}s. Saved: {out_path}", file=sys.stderr)
    print(json.dumps({
        "path": str(out_path),
        "cached": False,
        "elapsed_s": round(elapsed, 1),
        "duration_s": actual_duration,
        "metadata": str(sidecar_path),
    }, ensure_ascii=False))


# ---------------------------------------------------------------------------
# image-to-video
# ---------------------------------------------------------------------------

def cmd_image_to_video(args):
    if not Path(args.image).exists():
        sys.exit(f"ERROR: image not found: {args.image}")

    width, height = resolve_dimensions(args.aspect, args.resolution)
    target_frames = int(args.duration * DEFAULT_FPS)
    num_frames = normalize_num_frames(target_frames)
    actual_duration = num_frames / DEFAULT_FPS

    cache_hash = hash_config(args.prompt, width, height, num_frames, args.seed, args.steps, image_path=args.image)
    cache_path = CACHE_DIR / f"{cache_hash}.mp4"
    sidecar_path = cache_path.with_suffix(".json")
    out_path = Path(args.to).expanduser()

    if not args.no_cache and cache_path.exists():
        print(f"==> Cached hit: {cache_path}", file=sys.stderr)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(cache_path, out_path)
        print(json.dumps({"path": str(out_path), "cached": True}, ensure_ascii=False))
        return

    print(f"==> Loading image-to-video model…", file=sys.stderr)
    import torch
    from diffusers import LTXImageToVideoPipeline
    from diffusers.utils import export_to_video, load_image

    device = detect_device()
    dtype = torch.bfloat16 if device != "cpu" else torch.float32
    MODEL_CACHE.mkdir(parents=True, exist_ok=True)

    pipe = LTXImageToVideoPipeline.from_pretrained(
        "Lightricks/LTX-Video",
        torch_dtype=dtype,
        cache_dir=str(MODEL_CACHE),
    ).to(device)

    if device == "mps":
        try:
            pipe.enable_attention_slicing()
        except Exception:
            pass

    image = load_image(args.image)

    print(f"==> Generating from image…", file=sys.stderr)
    t0 = time.time()
    result = pipe(
        image=image,
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        width=width,
        height=height,
        num_frames=num_frames,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance_scale,
        generator=torch.Generator(device=device).manual_seed(args.seed),
    )
    frames = result.frames[0]
    elapsed = time.time() - t0

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    export_to_video(frames, str(cache_path), fps=DEFAULT_FPS)
    shutil.copy(cache_path, out_path)

    metadata = {
        "prompt": args.prompt,
        "image": args.image,
        "width": width,
        "height": height,
        "num_frames": num_frames,
        "duration_s": actual_duration,
        "fps": DEFAULT_FPS,
        "seed": args.seed,
        "steps": args.steps,
        "model": "Lightricks/LTX-Video (image-to-video)",
        "device": device,
        "elapsed_s": round(elapsed, 1),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    sidecar_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"==> Done in {elapsed:.1f}s. Saved: {out_path}", file=sys.stderr)
    print(json.dumps({"path": str(out_path), "cached": False, "elapsed_s": round(elapsed, 1)}, ensure_ascii=False))


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def add_common_args(p):
    p.add_argument("--prompt", required=True, help="Cinematic prompt — see references/prompting-guide for formula")
    p.add_argument("--negative-prompt", default="worst quality, blurry, distorted, jittery, watermark, text artifacts")
    p.add_argument("--duration", type=float, default=5.0, help="Target duration in seconds (snaps to LTX frame constraints)")
    p.add_argument("--aspect", default="16:9", choices=["16:9", "9:16", "1:1", "4:5"])
    p.add_argument("--resolution", default="medium", choices=["small", "medium", "large"])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--steps", type=int, default=40, help="Inference steps (40 = balance, 50+ = sharper)")
    p.add_argument("--guidance-scale", type=float, default=3.0)
    p.add_argument("--to", required=True, help="Output MP4 path")
    p.add_argument("--no-cache", action="store_true", help="Force regeneration even if cached")
    p.add_argument("--force-cpu", action="store_true", help="Allow CPU fallback (extremely slow)")


def main():
    parser = argparse.ArgumentParser(description="LTX-Video local generation")
    sub = parser.add_subparsers(dest="cmd", required=True)

    pt = sub.add_parser("text-to-video", help="Generate video from text prompt only")
    add_common_args(pt)
    pt.set_defaults(func=cmd_text_to_video)

    pi = sub.add_parser("image-to-video", help="Generate video from image + text prompt")
    pi.add_argument("--image", required=True, help="Path to source image")
    add_common_args(pi)
    pi.set_defaults(func=cmd_image_to_video)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
