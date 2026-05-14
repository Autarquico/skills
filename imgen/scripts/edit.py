#!/usr/bin/env python3
"""Direct API Fallback: Image Editing with optional brand anchoring.

Edit images via Gemini REST API when MCP is unavailable. With --brand, attaches
the brand's reference images as additional anchors so edits stay on-brand.

Uses only Python stdlib (no pip dependencies).

Usage:
    edit.py --image path/to/image.png --prompt "remove the background"
            [--model MODEL] [--api-key KEY] [--brand NAME]
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

sys.path.insert(0, str(Path(__file__).parent))
try:
    from brands import load_brand, resolve_default  # type: ignore
except Exception:
    def load_brand(_name):
        return None
    def resolve_default():
        return None

DEFAULT_MODEL = "gemini-3.1-flash-image-preview"
OUTPUT_DIR = Path.home() / "Documents" / "nanobanana_generated"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
MAX_REFERENCE_IMAGES = 13  # leave one slot for the source image (limit 14)


def _inline_image(path):
    path = Path(path)
    mime, _ = mimetypes.guess_type(str(path))
    mime = mime or "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return {"inlineData": {"mimeType": mime, "data": b64}}


def _apply_brand(prompt, brand):
    if not brand:
        return prompt
    anchors = brand.get("positive_anchors") or []
    banned = brand.get("banned") or []
    suffix = []
    if anchors:
        suffix.append("Maintain the spirit of " + ", ".join(anchors) + ".")
    if banned:
        suffix.append("NEVER include any of: " + ", ".join(banned) + ".")
    if suffix:
        return prompt.rstrip() + "\n\n" + " ".join(suffix)
    return prompt


def edit_image(image_path, prompt, model, api_key, reference_images=None, brand=None):
    image_path = Path(image_path).resolve()
    if not image_path.exists():
        print(json.dumps({"error": True, "message": f"Image not found: {image_path}"}))
        sys.exit(1)

    final_prompt = _apply_brand(prompt, brand)
    refs = (reference_images or [])[:MAX_REFERENCE_IMAGES]

    parts = []
    # Brand references first as anchors
    for r in refs:
        if Path(r).exists():
            parts.append(_inline_image(r))
    # Source image
    parts.append(_inline_image(image_path))
    # Edit instruction
    if refs:
        prefix = ("The image to edit is the LAST attached image; the earlier "
                  "images are brand references for palette/material/typographic "
                  "feel. Apply this edit: ")
    else:
        prefix = ""
    parts.append({"text": prefix + final_prompt})

    url = f"{API_BASE}/{model}:generateContent?key={api_key}"
    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")

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

    parts_out = candidates[0].get("content", {}).get("parts", [])
    image_data = None
    text_response = ""
    for part in parts_out:
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
    filename = f"banana_edit{suffix}_{timestamp}.png"
    output_path = (OUTPUT_DIR / filename).resolve()

    with open(output_path, "wb") as f:
        f.write(base64.b64decode(image_data))

    return {
        "path": str(output_path),
        "model": model,
        "source": str(image_path),
        "brand": brand.get("name") if brand else None,
        "reference_images_used": refs,
        "final_prompt": final_prompt,
        "text": text_response,
    }


def main():
    parser = argparse.ArgumentParser(description="Edit images via Gemini REST API")
    parser.add_argument("--image", required=True, help="Path to input image")
    parser.add_argument("--prompt", required=True, help="Edit instruction")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model ID (default: {DEFAULT_MODEL})")
    parser.add_argument("--api-key", default=None, help="Google AI API key (or set GOOGLE_AI_API_KEY env)")
    parser.add_argument("--brand", default="", help="Apply a brand from ~/.banana/brands/<name>/")
    parser.add_argument("--no-default-brand", action="store_true", help="Ignore the default brand")

    args = parser.parse_args()

    brand_name = args.brand or ("" if args.no_default_brand else (resolve_default() or ""))
    brand = load_brand(brand_name) if brand_name else None
    if brand_name and not brand:
        print(json.dumps({"error": True, "message": f"Brand '{brand_name}' not found in ~/.banana/brands/"}))
        sys.exit(1)

    api_key = args.api_key or os.environ.get("GOOGLE_AI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print(json.dumps({"error": True, "message": "No API key. Set GOOGLE_AI_API_KEY env or pass --api-key"}))
        sys.exit(1)

    reference_images = brand.get("reference_images_abs") if brand else []

    result = edit_image(
        image_path=args.image,
        prompt=args.prompt,
        model=args.model,
        api_key=api_key,
        reference_images=reference_images,
        brand=brand,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
