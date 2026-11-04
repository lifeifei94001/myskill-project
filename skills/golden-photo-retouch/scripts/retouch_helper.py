#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Golden Photo Retouch Helper Script
Assists agents in inspecting images, assessing image qualities, formulating
enhanced aesthetic prompts, and generating 3-stage execution plans.
"""

import sys
import os
import json
import argparse
from pathlib import Path

try:
    from PIL import Image, ImageStat
except ImportError:
    Image = None

STYLE_PROMPTS = {
    "vintage-film": (
        "shot on 35mm Kodak Portra 400, analog film photography, subtle natural film grain, "
        "authentic skin texture, warm vintage undertones, soft golden hour rim lighting, "
        "nostalgic depth, f/2.0 aperture bokeh, unedited natural feel"
    ),
    "hk-cinema": (
        "cinematography by Wong Kar-wai, 1990s Hong Kong cinema aesthetic, moody tungsten and "
        "neon light streaks, rich emerald greens and deep crimson hues, vintage bloom effect, "
        "soft diffuse haze, emotional depth, intense cinematic lighting, 35mm lens"
    ),
    "quiet-luxury": (
        "high-end editorial portrait, quiet luxury aesthetic, studio octa softbox illumination, "
        "Rembrandt lighting, neutral warm grey seamless backdrop, authentic pore-level skin texture, "
        "pristine crisp clarity, shot on Hasselblad H6D-100c, 85mm portrait lens, f/2.8"
    ),
    "japanese-airy": (
        "Japanese magazine portrait aesthetic, Kawauchi Rinko style, airy ethereal lighting, "
        "soft natural daylight, overexposed high-key lighting, pastel tone palette, "
        "translucent luminous skin, gentle morning breeze atmosphere, 50mm f/1.4 lens"
    ),
    "cyberpunk": (
        "cyberpunk neon noir aesthetic, dual-tone lighting with electric cyan and magenta highlights, "
        "wet asphalt reflections, futuristic city backdrop, sharp dramatic shadows, "
        "edge glow rim lighting, ultra-sharp detail, cinematic anamorphic lens flare"
    ),
    "pop-mart": (
        "Pop Mart designer toy blind box figurine style, 3D collectible vinyl figure, "
        "smooth matte clay texture, rounded cute chibi proportions, adorable facial features, "
        "studio miniature photography, macro depth of field, vibrant pastel color palette, soft ray-traced shadows"
    ),
    "natural-beauty": (
        "hyper-realistic clean natural beauty portrait, soft flattering diffused window light, "
        "flawless yet realistic skin texture with visible pores, radiant complexion, "
        "sharp expressive catchlights in eyes, clean studio background, 8k resolution"
    )
}

def inspect_image(image_path: str):
    p = Path(image_path)
    if not p.exists():
        return {"error": f"File not found: {image_path}"}

    file_size_kb = round(os.path.getsize(p) / 1024, 2)

    if Image is None:
        return {
            "path": str(p),
            "size_kb": file_size_kb,
            "status": "PIL not available for deeper analysis"
        }

    try:
        with Image.open(p) as img:
            w, h = img.size
            mode = img.mode
            format_name = img.format

            # Calculate brightness and contrast
            grayscale = img.convert("L")
            stat = ImageStat.Stat(grayscale)
            avg_brightness = round(stat.mean[0], 2)  # 0 to 255
            std_contrast = round(stat.stddev[0], 2)   # higher = higher contrast

            # Diagnostics
            aspect_ratio = round(w / h, 2)
            issues = []
            if avg_brightness < 60:
                issues.append("Image is notably underexposed/dark (needs lighting boost in Phase 1/2)")
            elif avg_brightness > 210:
                issues.append("Image is overexposed/high-key")

            if std_contrast < 30:
                issues.append("Low contrast/flat tones (needs contrast & color grading)")

            if max(w, h) < 1000:
                issues.append("Low resolution (Phase 3 super-resolution/upscale is strongly recommended)")

            return {
                "path": str(p),
                "width": w,
                "height": h,
                "aspect_ratio": aspect_ratio,
                "format": format_name,
                "color_mode": mode,
                "size_kb": file_size_kb,
                "brightness_score": avg_brightness,
                "contrast_score": std_contrast,
                "diagnosed_issues": issues
            }
    except Exception as e:
        return {"error": f"Failed to analyze image: {str(e)}"}

def build_prompt(style: str, custom_text: str = ""):
    base = STYLE_PROMPTS.get(style, STYLE_PROMPTS["natural-beauty"])
    if custom_text:
        return f"{custom_text.strip()}, {base}"
    return base

def generate_plan(image_path: str, style: str = "natural-beauty", custom_text: str = ""):
    inspection = inspect_image(image_path)
    prompt = build_prompt(style, custom_text)

    needs_upscale = True
    needs_restore = True
    if "width" in inspection:
        if inspection["width"] >= 2500 and inspection["height"] >= 2500:
            needs_upscale = False

    plan = {
        "image_inspection": inspection,
        "selected_style": style,
        "enhanced_aesthetic_prompt": prompt,
        "pipeline": [
            {
                "step": 1,
                "name": "Phase 1: Face & Detail Restoration (fal-restore)",
                "recommended": needs_restore,
                "goal": "Denoise, deblur, reconstruct facial pores and catchlights, correct underexposure.",
                "endpoint": "fal-ai/image-restore (or codeformer)",
                "params": {"fidelity": 0.75, "restore_background": True}
            },
            {
                "step": 2,
                "name": "Phase 2: Context Edit & Aesthetic Re-lighting (fal-image-edit)",
                "recommended": True,
                "goal": f"Apply '{style}' aesthetic style transfer, balance directional rim lighting, and clean background distractions.",
                "endpoint": "fal-ai/flux/context (or flux/inpainting)",
                "params": {"prompt": prompt, "strength": 0.42 if style != "pop-mart" else 0.75}
            },
            {
                "step": 3,
                "name": "Phase 3: Super Resolution & Polish (fal-upscale)",
                "recommended": needs_upscale,
                "goal": "Upscale by 2x-4x to bring out macro fabric and hair details with pristine clarity.",
                "endpoint": "fal-ai/clarity-upscaler",
                "params": {"scale": 2, "creativity": 0.2, "resemblance": 0.85}
            }
        ]
    }
    return plan

def main():
    parser = argparse.ArgumentParser(description="Golden Photo Retouch Helper")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Inspect
    inspect_parser = subparsers.add_parser("inspect", help="Inspect image quality & specs")
    inspect_parser.add_argument("image_path", help="Path to image file")

    # Prompt
    prompt_parser = subparsers.add_parser("prompt", help="Build aesthetic prompt")
    prompt_parser.add_argument("--style", default="natural-beauty", choices=list(STYLE_PROMPTS.keys()), help="Style preset")
    prompt_parser.add_argument("--custom", default="", help="Custom user requirement")

    # Plan
    plan_parser = subparsers.add_parser("plan", help="Generate 3-stage retouch plan")
    plan_parser.add_argument("image_path", help="Path to image file")
    plan_parser.add_argument("--style", default="natural-beauty", choices=list(STYLE_PROMPTS.keys()), help="Style preset")
    plan_parser.add_argument("--custom", default="", help="Custom user requirement")

    args = parser.parse_args()

    if args.command == "inspect":
        res = inspect_image(args.image_path)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.command == "prompt":
        res = build_prompt(args.style, args.custom)
        print(res)
    elif args.command == "plan":
        plan = generate_plan(args.image_path, args.style, args.custom)
        print(json.dumps(plan, indent=2, ensure_ascii=False))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
