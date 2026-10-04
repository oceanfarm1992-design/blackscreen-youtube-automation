#!/usr/bin/env python3
"""
Generate per-theme long-form thumbnails (1280x720) for the "Aether
Resonance" channel. No supplied source art -- the thumbnail background
reuses the same procedural noise-field engine as the video itself
(scripts/make_animated_video.py), tinted to each theme's soft, luminous
accent color.

Local dev tool -- thumbnails are committed as PNGs and consumed by
produce.py, so this is NOT run in CI. Requires Pillow.

Usage:
    python make_thumbnails.py                 # only themes with no thumbnail yet
    python make_thumbnails.py --all           # regenerate every theme
    python make_thumbnails.py --themes still_water,crown_light
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import themes as T  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SHARED = os.path.join(ROOT, "scripts")
sys.path.insert(0, SHARED)
from make_animated_video import _noise_field, _channel_gain  # noqa: E402

OUT_DIR = os.path.join(ROOT, "assets", "resonance", "thumbnails", "gen")

W, H = 1280, 720
MARGIN_X = 62
MAX_TEXT_W = 660
PILL_FILL = (100, 130, 150)  # soft teal accent

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\impact.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

HEADLINES = {
    "still_water": ["STILL WATER", "432 Hz SOUND BATH"],
    "crown_light": ["CROWN LIGHT", "963 Hz SOUND BATH"],
    "root_anchor": ["ROOT ANCHOR", "396 Hz GROUNDING"],
    "heart_bloom": ["HEART BLOOM", "639 Hz SINGING BOWL"],
    "third_eye_drift": ["THIRD EYE DRIFT", "852 Hz SOUND BATH"],
    "cellular_renewal": ["CELLULAR RENEWAL", "285 Hz HEALING DRONE"],
    "miracle_tone": ["MIRACLE TONE", "528 Hz SOUND BATH"],
    "singing_bowl_sanctuary": ["SINGING BOWL SANCTUARY", "OM 136 Hz"],
    "theta_gateway": ["THETA GATEWAY", "GENERATIVE DRONE"],
    "pink_noise_veil": ["PINK NOISE VEIL", "SOOTHING SOUND BATH"],
}


def load_font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def fit_font(draw, text, start, min_size=34):
    size = start
    while size > min_size:
        f = load_font(size)
        if draw.textlength(text, font=f) <= MAX_TEXT_W:
            return f
        size -= 2
    return load_font(min_size)


def noise_background(key, seed):
    rng = np.random.default_rng(seed)
    field = _noise_field(W, H, rng)
    gains = np.array(_channel_gain(T.ACCENT_COLORS.get(key, "4a6a7a")), dtype=np.float32)
    rgb = np.clip(field[:, :, None] * gains[None, None, :] * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(rgb, mode="RGB")


def glow(img, color):
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([-220, 60, 700, 660], fill=tuple(int(c * 0.6) for c in color))
    layer = layer.filter(ImageFilter.GaussianBlur(170))
    return ImageChops.screen(img, layer)


def build(key, lines):
    base = noise_background(key, seed=hash(key) % (2**31))
    accent = tuple(int(c * 255) for c in _channel_gain(T.ACCENT_COLORS.get(key, "4a6a7a")))
    img = glow(base, accent)
    draw = ImageDraw.Draw(img)

    f1 = fit_font(draw, lines[0], 72)
    f2 = fit_font(draw, lines[1], 48)
    h1 = draw.textbbox((0, 0), lines[0], font=f1)[3]
    h2 = draw.textbbox((0, 0), lines[1], font=f2)[3]

    y = 430
    for text, font, hh in ((lines[0], f1, h1), (lines[1], f2, h2)):
        draw.text((MARGIN_X, y), text, font=font, fill=(245, 250, 250),
                  stroke_width=6, stroke_fill=(0, 0, 0))
        y += hh + 14

    label = "14 MIN"
    pf = load_font(40)
    tw = draw.textlength(label, font=pf)
    px0, py0 = MARGIN_X, y + 12
    px1, py1 = px0 + tw + 60, py0 + 62
    draw.rounded_rectangle([px0, py0, px1, py1], radius=31, fill=PILL_FILL)
    draw.text((px0 + 30, py0 + 10), label, font=pf, fill=(255, 255, 255))

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{key}.png")
    img.save(path, "PNG", optimize=True)
    return path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--all", action="store_true", help="regenerate every theme")
    p.add_argument("--themes", default=None, help="comma-separated theme keys")
    args = p.parse_args()

    keys = [t["key"] for t in T.THEMES]
    if args.themes:
        keys = [k.strip() for k in args.themes.split(",") if k.strip()]
    elif not args.all:
        keys = [k for k in keys
                if not os.path.exists(os.path.join(OUT_DIR, f"{k}.png"))]

    if not keys:
        print("Nothing to generate.")
        return

    for k in keys:
        if k not in HEADLINES:
            print(f"  ! no headline defined for {k}, skipping")
            continue
        path = build(k, HEADLINES[k])
        print(f"  {k:24s} -> {os.path.relpath(path, ROOT)}")
    print(f"\nDone: {len(keys)} thumbnail(s).")


if __name__ == "__main__":
    main()
