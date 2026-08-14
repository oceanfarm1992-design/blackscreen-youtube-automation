#!/usr/bin/env python3
"""
Generate per-theme long-form thumbnails (1280x720) in the channel style.

Local dev tool — thumbnails are committed as PNGs and consumed by produce.py,
so this is NOT run in CI. Requires Pillow (pip install pillow).

Style: the branded base (headphone logo + "Meditated Sleeping") with a soft
per-theme colour glow, a big two-line headline on the left, and a duration
pill. The duration is read from themes.long_hours_for(), so re-running this
after a duration change keeps the badges truthful.

Usage:
    python make_thumbnails.py                 # only themes with no thumbnail yet
    python make_thumbnails.py --all           # regenerate every theme
    python make_thumbnails.py --themes 963hz_awakening,om_136
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
BASE = os.path.join(ROOT, "assets", "branding", "thumbnail_1280x720.png")
OUT_DIR = os.path.join(ROOT, "assets", "thumbnails", "gen")

W, H = 1280, 720
MARGIN_X = 62
MAX_TEXT_W = 660          # keep the headline clear of the brand lockup
PILL_FILL = (232, 74, 95)  # channel red/pink

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\impact.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

# headline lines + accent glow colour per theme
STYLES = {
    "rain_drops":          (["SOFT RAIN", "& WATER DROPS"], (60, 150, 200)),
    "solfeggio_heal":      (["432·528·741 Hz", "HEALING SLEEP"], (70, 90, 210)),
    "solfeggio_spirit":    (["528·741·963 Hz", "BODY & SPIRIT"], (150, 80, 210)),
    "solfeggio_deepsleep": (["SOLFEGGIO + DELTA", "DEEP SLEEP"], (60, 100, 200)),
    "om_136":              (["OM 136 Hz", "MEDITATION"], (215, 150, 60)),
    "963hz_awakening":     (["963 Hz", "CROWN CHAKRA"], (150, 90, 220)),
    "852hz_intuition":     (["852 Hz", "THIRD EYE"], (110, 90, 220)),
    "741hz_clarity":       (["741 Hz", "CLEANSE & CLARITY"], (70, 180, 150)),
    # already-shipped themes, for --all / --stale regeneration
    "rain":                (["RAIN SOUNDS", "FOR SLEEPING"], (60, 140, 190)),
    "waterfall":           (["WATERFALL", "SOUNDS"], (60, 170, 190)),
    "forest":              (["FOREST", "SOUNDS"], (70, 170, 110)),
    "sleeping":            (["DEEP SLEEP", "MUSIC"], (70, 110, 200)),
    "indian":              (["INDIAN", "SLEEP MUSIC"], (210, 140, 60)),
    "romantic":            (["ROMANTIC", "MUSIC"], (215, 80, 130)),
    "romantic_night":      (["ROMANTIC NIGHT", "MUSIC"], (180, 70, 150)),
    "gamma_focus":         (["40 Hz GAMMA", "FOCUS MUSIC"], (200, 160, 60)),
    "528hz_sleep":         (["528 Hz", "SLEEP MUSIC"], (80, 170, 190)),
    "delta_sleep":         (["DELTA WAVES", "DEEP SLEEP"], (70, 100, 200)),
    "432hz_relax":         (["432 Hz", "RELAXING MUSIC"], (200, 110, 170)),
}


def load_font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def fit_font(draw, text, start, min_size=40):
    """Largest font size at which `text` fits MAX_TEXT_W."""
    size = start
    while size > min_size:
        f = load_font(size)
        if draw.textlength(text, font=f) <= MAX_TEXT_W:
            return f
        size -= 2
    return load_font(min_size)


def glow(img, color):
    """Soft radial accent glow behind the headline area.

    Screen-blended (lighten-only) so it lifts the black background without
    dimming the brand lockup — a straight blend darkens the logo.
    """
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([-220, 60, 700, 660], fill=tuple(int(c * 0.5) for c in color))
    layer = layer.filter(ImageFilter.GaussianBlur(170))
    return ImageChops.screen(img, layer)


def duration_label(key):
    h = T.long_hours_for(key)
    return f"{h} HOURS"


def build(key, lines, color):
    base = Image.open(BASE).convert("RGB").resize((W, H))
    img = glow(base, color)
    draw = ImageDraw.Draw(img)

    f1 = fit_font(draw, lines[0], 108)
    f2 = fit_font(draw, lines[1], 120)
    h1 = draw.textbbox((0, 0), lines[0], font=f1)[3]
    h2 = draw.textbbox((0, 0), lines[1], font=f2)[3]

    y = 196
    for text, font, hh in ((lines[0], f1, h1), (lines[1], f2, h2)):
        draw.text((MARGIN_X, y), text, font=font, fill=(255, 255, 255),
                  stroke_width=7, stroke_fill=(0, 0, 0))
        y += hh + 16

    # duration pill
    label = duration_label(key)
    pf = load_font(46)
    tw = draw.textlength(label, font=pf)
    px0, py0 = MARGIN_X, y + 18
    px1, py1 = px0 + tw + 68, py0 + 72
    draw.rounded_rectangle([px0, py0, px1, py1], radius=36, fill=PILL_FILL)
    draw.text((px0 + 34, py0 + 12), label, font=pf, fill=(255, 255, 255))

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{key}.png")
    img.save(path, "PNG", optimize=True)
    return path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--all", action="store_true", help="regenerate every theme")
    p.add_argument("--stale", action="store_true",
                   help="only themes whose duration badge no longer matches")
    p.add_argument("--themes", default=None, help="comma-separated theme keys")
    args = p.parse_args()

    keys = [t["key"] for t in T.THEMES]
    if args.themes:
        keys = [k.strip() for k in args.themes.split(",") if k.strip()]
    elif args.stale:
        keys = [k for k in keys if T.long_hours_for(k) != 10
                and os.path.exists(os.path.join(OUT_DIR, f"{k}.png"))]
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
        print(f"  {k:20s} {duration_label(k):9s} -> {os.path.relpath(path, ROOT)}")
    print(f"\nDone: {len(keys)} thumbnail(s).")


if __name__ == "__main__":
    main()
