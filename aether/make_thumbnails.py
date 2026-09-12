#!/usr/bin/env python3
"""
Generate per-theme long-form thumbnails (1280x720) for the "Aether & Ash"
channel, for the themes that don't already have hand-made art.

4 themes (void_drone, ember_focus, creative_flow, calm_the_night) already
have finished, hand-made thumbnails copied straight into
assets/aether/thumbnails/gen/ -- this script never overwrites those (same
"only generate if missing" default as scripts/make_thumbnails.py). The
remaining 11 themes get a generated thumbnail using the same glow/headline/
duration-pill technique, built on the shared blank "ember hand" background.

Local dev tool -- thumbnails are committed as PNGs and consumed by
produce.py, so this is NOT run in CI. Requires Pillow (pip install pillow).

Usage:
    python make_thumbnails.py                 # only themes with no thumbnail yet
    python make_thumbnails.py --all           # regenerate every generated theme
    python make_thumbnails.py --themes abyssal_silence,cosmic_drift
    python make_thumbnails.py --stale         # only ones whose badge is wrong
"""
import argparse
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import themes as T  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = os.path.join(ROOT, "assets", "aether", "thumbnails", "src", "ember_hand_blank.jpg")
OUT_DIR = os.path.join(ROOT, "assets", "aether", "thumbnails", "gen")

# Themes with finished, hand-made art already in OUT_DIR -- never regenerated
# by this script even with --all.
HAND_MADE = {"void_drone", "ember_focus", "creative_flow", "calm_the_night"}

W, H = 1280, 720
MARGIN_X = 62
MAX_TEXT_W = 660
PILL_FILL = (196, 92, 48)  # warm ember accent, matches the source art

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\impact.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

# headline lines + accent glow colour per theme
STYLES = {
    "abyssal_silence": (["ABYSSAL SILENCE", "DARK AMBIENT"], (45, 65, 115)),
    "cosmic_drift":    (["COSMIC DRIFT", "SPACE AMBIENT"], (120, 80, 200)),
    "shadow_ink":      (["SHADOW & INK", "GOTHIC WRITING"], (60, 75, 95)),
    "slumber_of_ash":  (["SLUMBER OF ASH", "RESTORATIVE SLEEP"], (75, 65, 140)),
    "ethereal_ruins":  (["ETHEREAL RUINS", "DARK FANTASY"], (150, 120, 70)),
    "ember_solitude":  (["EMBER SOLITUDE", "QUIET REFLECTION"], (175, 95, 55)),
    "markov_chamber":  (["MARKOV CHAMBER", "GENERATIVE FOCUS"], (115, 75, 185)),
    "ash_rain_wind":   (["ASH RAIN & WIND", "DARK NATURE NOISE"], (80, 105, 110)),
    "black_hole":      (["BLACK HOLE", "RESONANCE"], (100, 40, 40)),
    "monastic_echoes": (["MONASTIC ECHOES", "SACRED DARK CHANT"], (145, 115, 65)),
    "obsidian_tower":  (["THE OBSIDIAN TOWER", "DARK ACADEMIA"], (55, 65, 90)),
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


def glow(img, color):
    """Soft radial accent glow behind the headline area (screen-blended)."""
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([-220, 60, 700, 660], fill=tuple(int(c * 0.5) for c in color))
    layer = layer.filter(ImageFilter.GaussianBlur(170))
    return ImageChops.screen(img, layer)


def duration_label(key):
    return "14 MIN"


def build(key, lines, color):
    base = Image.open(BASE).convert("RGB").resize((W, H))
    img = glow(base, color)
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

    label = duration_label(key)
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
    p.add_argument("--all", action="store_true", help="regenerate every generated theme")
    p.add_argument("--stale", action="store_true",
                   help="only themes whose duration badge no longer matches")
    p.add_argument("--themes", default=None, help="comma-separated theme keys")
    args = p.parse_args()

    keys = [t["key"] for t in T.THEMES if t["key"] not in HAND_MADE]
    if args.themes:
        keys = [k.strip() for k in args.themes.split(",") if k.strip() and k.strip() not in HAND_MADE]
    elif args.stale:
        keys = [k for k in keys
                if os.path.exists(os.path.join(OUT_DIR, f"{k}.png"))]
    elif not args.all:
        keys = [k for k in keys
                if not os.path.exists(os.path.join(OUT_DIR, f"{k}.png"))]

    if not keys:
        print("Nothing to generate.")
        return

    for k in keys:
        if k not in STYLES:
            print(f"  ! no style defined for {k}, skipping")
            continue
        lines, color = STYLES[k]
        path = build(k, lines, color)
        print(f"  {k:18s} {duration_label(k):8s} -> {os.path.relpath(path, ROOT)}")
    print(f"\nDone: {len(keys)} thumbnail(s). "
          f"({len(HAND_MADE)} hand-made themes left untouched: {', '.join(sorted(HAND_MADE))})")


if __name__ == "__main__":
    main()
