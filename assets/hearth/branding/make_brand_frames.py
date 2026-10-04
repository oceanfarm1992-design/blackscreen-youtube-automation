#!/usr/bin/env python3
"""
Generate the "Hearth & Quill" branded icon (and a fallback static frame,
kept only as a safety net -- the real video background is the procedural
animation in scripts/make_animated_video.py).

Local dev tool, not run in CI -- output PNGs are committed. Requires Pillow.
Icon: a quill feather with a small warm flame at its tip, in the channel's
amber/gold palette.

Usage:
    python make_brand_frames.py
"""
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

AMBER = (230, 160, 70)
AMBER_SOFT = (190, 125, 55)
PARCHMENT = (205, 185, 150)

FONT_CANDIDATES_BOLD = [
    r"C:\Windows\Fonts\arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
FONT_CANDIDATES_REGULAR = [
    r"C:\Windows\Fonts\arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def load_font(candidates, size):
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def glow_layer(size, draw_fn, color, blur):
    layer = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d, color)
    return layer.filter(ImageFilter.GaussianBlur(blur))


def quill_icon(size):
    """A small glowing quill feather with a warm flame at its tip."""
    img = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(img)
    w, h = size
    base = (w * 0.3, h * 0.82)
    tip = (w * 0.72, h * 0.18)

    # feather shaft
    d.line([base, tip], fill=(60, 50, 40), width=max(3, int(w * 0.03)))

    # feather barbs (short diagonal strokes along the shaft)
    n = 10
    for i in range(1, n):
        t = i / n
        px = base[0] + (tip[0] - base[0]) * t
        py = base[1] + (tip[1] - base[1]) * t
        length = (1 - t) * w * 0.22 + w * 0.04
        ang = math.atan2(tip[1] - base[1], tip[0] - base[0]) + math.pi / 2
        for side in (-1, 1):
            ex = px + math.cos(ang) * length * side * 0.6
            ey = py + math.sin(ang) * length * side * 0.6
            d.line([(px, py), (ex, ey)], fill=PARCHMENT, width=2)

    # small flame glow at the tip
    fr = w * 0.09
    d.ellipse([tip[0] - fr, tip[1] - fr, tip[0] + fr, tip[1] + fr], fill=(255, 210, 140))
    d.ellipse([tip[0] - fr * 0.5, tip[1] - fr * 0.5, tip[0] + fr * 0.5, tip[1] + fr * 0.5],
              fill=(255, 240, 200))

    glow = img.filter(ImageFilter.GaussianBlur(w * 0.03))
    return ImageChops.screen(img, glow)


def quill_icon_rgba(size):
    rgb = quill_icon(size).convert("RGB")
    alpha = rgb.convert("L").point(lambda v: min(255, int(v * 1.4)))
    out = rgb.copy()
    out.putalpha(alpha)
    return out


def build(w, h, layout):
    img = Image.new("RGB", (w, h), (0, 0, 0))

    icon_size = layout["icon_size"]
    icon = quill_icon((icon_size, icon_size))
    img.paste(icon, layout["icon_pos"])

    title_font = load_font(FONT_CANDIDATES_BOLD, layout["title_size"])
    tag_font = load_font(FONT_CANDIDATES_REGULAR, layout["tag_size"])

    title = "Hearth & Quill"
    tagline = "Warm Worlds. Quiet Work."

    def draw_title(d, color):
        d.text(layout["title_pos"], title, font=title_font, fill=color)

    img = ImageChops.screen(img, glow_layer((w, h), draw_title, AMBER_SOFT, 14))
    draw = ImageDraw.Draw(img)
    draw.text(layout["title_pos"], title, font=title_font, fill=(240, 220, 190))
    draw.text(layout["tag_pos"], tagline, font=tag_font, fill=PARCHMENT)

    return img.convert("RGBA")


def main():
    wide = build(1920, 1080, {
        "icon_size": 300,
        "icon_pos": (740, 390),
        "title_pos": (1100, 470),
        "title_size": 68,
        "tag_pos": (1104, 560),
        "tag_size": 34,
    })
    wide.save(os.path.join(HERE, "brand_16x9_fallback.png"), "PNG", optimize=True)

    icon = quill_icon_rgba((300, 300))
    icon.save(os.path.join(HERE, "icon.png"), "PNG", optimize=True)

    fallback = wide.convert("RGB").resize((1280, 720))
    fallback.save(os.path.join(HERE, "thumbnail_1280x720.png"), "PNG", optimize=True)

    print("Wrote icon.png, brand_16x9_fallback.png, and thumbnail_1280x720.png")


if __name__ == "__main__":
    main()
