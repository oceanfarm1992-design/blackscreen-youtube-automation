#!/usr/bin/env python3
"""
Generate per-theme long-form thumbnails (1280x720) for the "Sanctuary of
Sci" channel. Unlike Aether & Ash (which had hand-made source photography),
this channel has no supplied art -- so the thumbnail background reuses the
SAME procedural noise-field engine as the video itself (scripts/
make_animated_video.py), rendered as one still frame per theme and tinted
to that theme's accent color. This keeps the thumbnail and video visually
consistent and needs no external art at all.

Local dev tool -- thumbnails are committed as PNGs and consumed by
produce.py, so this is NOT run in CI. Requires Pillow (pip install pillow).

Usage:
    python make_thumbnails.py                 # only themes with no thumbnail yet
    python make_thumbnails.py --all           # regenerate every theme
    python make_thumbnails.py --themes sleeper_drift,nebula_watch
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

OUT_DIR = os.path.join(ROOT, "assets", "sanctuary", "thumbnails", "gen")

W, H = 1280, 720
MARGIN_X = 62
MAX_TEXT_W = 660
PILL_FILL = (70, 120, 210)  # ion-blue accent, matches the brand icon

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\impact.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

# headline lines (title + subtitle) per theme
HEADLINES = {
    "sleeper_drift": ["SLEEPER DRIFT", "DEEP SPACE DRONE"],
    "nebula_watch": ["NEBULA WATCH", "COSMIC OBSERVATORY"],
    "station_hum": ["STATION HUM", "SPACE STATION AMBIENCE"],
    "cryo_bay": ["CRYO BAY", "COLD SLEEPER AMBIENT"],
    "observatory_deck": ["OBSERVATORY DECK", "GENERATIVE FOCUS"],
    "ion_trail": ["ION TRAIL", "CODING FOCUS MUSIC"],
    "long_dark": ["THE LONG DARK", "MINIMAL DEEP DRONE"],
    "starlight_convergence": ["STARLIGHT CONVERGENCE", "HOPEFUL COSMIC AMBIENT"],
    "zero_g_drift": ["ZERO-G DRIFT", "WEIGHTLESS AMBIENT"],
    "signal_lost": ["SIGNAL LOST", "MYSTERIOUS SPACE STATIC"],
}


def load_font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def fit_font(draw, text, start, min_size=40):
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
    gains = np.array(_channel_gain(T.ACCENT_COLORS.get(key, "2a3a5a")), dtype=np.float32)
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
    accent = tuple(int(c * 255) for c in _channel_gain(T.ACCENT_COLORS.get(key, "2a3a5a")))
    img = glow(base, accent)
    draw = ImageDraw.Draw(img)

    f1 = fit_font(draw, lines[0], 88)
    f2 = fit_font(draw, lines[1], 56)
    h1 = draw.textbbox((0, 0), lines[0], font=f1)[3]
    h2 = draw.textbbox((0, 0), lines[1], font=f2)[3]

    y = 430
    for text, font, hh in ((lines[0], f1, h1), (lines[1], f2, h2)):
        draw.text((MARGIN_X, y), text, font=font, fill=(255, 255, 255),
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
        print(f"  {k:22s} -> {os.path.relpath(path, ROOT)}")
    print(f"\nDone: {len(keys)} thumbnail(s).")


if __name__ == "__main__":
    main()
