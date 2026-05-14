#!/usr/bin/env python3
"""Direct API Fallback: Image Generation with optional brand anchoring.

Generate images via Gemini REST API when MCP is unavailable. With --brand,
loads the brand from ~/.banana/brands/<name>/ and attaches its reference
images inline so the model anchors palette / materials / typography.

Uses only Python stdlib (no pip dependencies).

Usage:
    generate.py --prompt "a cat in space" [--aspect-ratio 16:9] [--resolution 1K]
                [--model MODEL] [--api-key KEY] [--thinking LEVEL] [--image-only]
                [--brand NAME]
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

# Import the brand loader from the sibling script
sys.path.insert(0, str(Path(__file__).parent))
try:
    from brands import load_brand, resolve_default  # type: ignore
except Exception:  # pragma: no cover -- brands.py optional at runtime
    def load_brand(_name):
        return None
    def resolve_default():
        return None

DEFAULT_MODEL = "gemini-3.1-flash-image-preview"
DEFAULT_RESOLUTION = "2K"  # Must be uppercase
DEFAULT_RATIO = "1:1"
OUTPUT_DIR = Path.home() / "Documents" / "nanobanana_generated"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

VALID_RATIOS = {"1:1", "16:9", "9:16", "4:3", "3:4", "2:3", "3:2",
                "4:5", "5:4", "1:4", "4:1", "1:8", "8:1", "21:9"}
VALID_RESOLUTIONS = {"512", "1K", "2K", "4K"}

MAX_REFERENCE_IMAGES = 14  # Gemini multi-image input limit


def _build_parts(prompt, reference_paths):
    """Build the contents.parts array. Reference images go before the prompt
    so the model treats them as anchors, with a directive prefix."""
    parts = []
    for p in reference_paths[:MAX_REFERENCE_IMAGES]:
        path = Path(p)
        if not path.exists():
            continue
        mime, _ = mimetypes.guess_type(str(path))
        mime = mime or "image/png"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        parts.append({"inlineData": {"mimeType": mime, "data": b64}})

    if parts:
        prefix = ("Using the attached images as visual references for palette, "
                  "materials, typographic feel, and overall mood, render: ")
        parts.append({"text": prefix + prompt})
    else:
        parts.append({"text": prompt})
    return parts


def _apply_brand(prompt, brand):
    """Augment the prompt with brand positive_anchors and banned exclusions."""
    if not brand:
        return prompt
    anchors = brand.get("positive_anchors") or []
    banned = brand.get("banned") or []
    suffix_parts = []
    if anchors:
        suffix_parts.append("In the spirit of " + ", ".join(anchors) + ".")
    if banned:
        suffix_parts.append(
            "NEVER include any of: " + ", ".join(banned) + "."
        )
    if suffix_parts:
        return prompt.rstrip() + "\n\n" + " ".join(suffix_parts)
    return prompt


def generate_image(prompt, model, aspect_ratio, resolution, api_key,
                   thinking_level=None, image_only=False,
                   reference_images=None, brand=None):
    """Call Gemini API to generate an image."""
    url = f"{API_BASE}/{model}:generateContent?key={api_key}"

    final_prompt = _apply_brand(prompt, brand)
    refs = reference_images or []

    modalities = ["IMAGE"] if image_only else ["TEXT", "IMAGE"]
    body = {
        "contents": [{"parts": _build_parts(final_prompt, refs)}],
        "generationConfig": {
            "responseModalities": modalities,
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": resolution,
            },
        },
    }

    if thinking_level:
        body["generationConfig"]["thinkingConfig"] = {"thinkingLevel": thinking_level}

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    max_retries = 3
    result = None
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            if e.code == 429 and attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                print(json.dumps({"retry": True, "attempt": attempt + 1, "wait_seconds": wait, "reason": "rate_limited"}), file=sys.stderr)
                time.sleep(wait)
                req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
                continue
            if e.code == 400 and "FAILED_PRECONDITION" in error_body:
                print(json.dumps({"error": True, "status": 400, "message": "Billing not enabled. Enable billing at https://aistudio.google.com/apikey"}))
                sys.exit(1)
            print(json.dumps({"error": True, "status": e.code, "message": error_body}))
            sys.exit(1)
        except urllib.error.URLError as e:
            print(json.dumps({"error": True, "message": str(e.reason)}))
            sys.exit(1)

    if result is None:
        print(json.dumps({"error": True, "message": "Max retries exceeded"}))
        sys.exit(1)

    candidates = result.get("candidates", [])
    if not candidates:
        finish_reason = result.get("promptFeedback", {}).get("blockReason", "UNKNOWN")
        print(json.dumps({"error": True, "message": f"No candidates returned. Reason: {finish_reason}"}))
        sys.exit(1)

    parts = candidates[0].get("content", {}).get("parts", [])
    image_data = None
    text_response = ""
    for part in parts:
        if "inlineData" in part:
            image_data = part["inlineData"]["data"]
        elif "text" in part:
            text_response = part["text"]

    if not image_data:
        finish_reason = candidates[0].get("finishReason", "UNKNOWN")
        print(json.dumps({"error": True, "message": f"No image in response. finishReason: {finish_reason}"}))
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    suffix = f"_{brand['name']}" if brand and brand.get("name") else ""
    filename = f"banana{suffix}_{timestamp}.png"
    output_path = (OUTPUT_DIR / filename).resolve()

    with open(output_path, "wb") as f:
        f.write(base64.b64decode(image_data))

    return {
        "path": str(output_path),
        "model": model,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "brand": brand.get("name") if brand else None,
        "reference_images_used": refs,
        "final_prompt": final_prompt,
        "text": text_response,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate images via Gemini REST API")
    parser.add_argument("--prompt", required=True, help="Image generation prompt")
    parser.add_argument("--aspect-ratio", default="", help=f"Aspect ratio (default: brand or {DEFAULT_RATIO})")
    parser.add_argument("--resolution", default="", help=f"Resolution: 512, 1K, 2K, 4K (default: brand or {DEFAULT_RESOLUTION})")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model ID (default: {DEFAULT_MODEL})")
    parser.add_argument("--api-key", default=None, help="Google AI API key (or set GOOGLE_AI_API_KEY env)")
    parser.add_argument("--thinking", default=None, choices=["minimal", "low", "medium", "high"], help="Thinking level")
    parser.add_argument("--image-only", action="store_true", help="Return image only (no text)")
    parser.add_argument("--brand", default="", help="Apply a brand from ~/.banana/brands/<name>/")
    parser.add_argument("--no-default-brand", action="store_true", help="Ignore the default brand from ~/.banana/config.yml")

    args = parser.parse_args()

    # Resolve brand
    brand_name = args.brand or ("" if args.no_default_brand else (resolve_default() or ""))
    brand = load_brand(brand_name) if brand_name else None
    if brand_name and not brand:
        print(json.dumps({"error": True, "message": f"Brand '{brand_name}' not found in ~/.banana/brands/"}))
        sys.exit(1)

    # Resolve defaults from brand or built-in
    aspect_ratio = args.aspect_ratio or (brand and brand.get("default_ratio")) or DEFAULT_RATIO
    resolution = args.resolution or (brand and brand.get("default_resolution")) or DEFAULT_RESOLUTION

    if aspect_ratio not in VALID_RATIOS:
        print(json.dumps({"error": True, "message": f"Invalid aspect ratio '{aspect_ratio}'. Valid: {sorted(VALID_RATIOS)}"}))
        sys.exit(1)
    if resolution not in VALID_RESOLUTIONS:
        print(json.dumps({"error": True, "message": f"Invalid resolution '{resolution}'. Valid: {sorted(VALID_RESOLUTIONS)}"}))
        sys.exit(1)

    api_key = args.api_key or os.environ.get("GOOGLE_AI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print(json.dumps({"error": True, "message": "No API key. Set GOOGLE_AI_API_KEY env or pass --api-key"}))
        sys.exit(1)

    reference_images = brand.get("reference_images_abs") if brand else []

    result = generate_image(
        prompt=args.prompt,
        model=args.model,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        api_key=api_key,
        thinking_level=args.thinking,
        image_only=args.image_only,
        reference_images=reference_images,
        brand=brand,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
