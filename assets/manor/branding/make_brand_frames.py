#!/usr/bin/env python3
"""
Generate the "Moss & Manor" branded icon (and a fallback static frame,
kept only as a safety net -- the real video background is the procedural
animation in scripts/make_animated_video.py).

Local dev tool, not run in CI -- output PNGs are committed. Requires Pillow.
Icon: a simple fern frond, in the channel's moss-green/earthy palette.

Usage:
    python make_brand_frames.py
"""
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

MOSS = (110, 150, 90)
MOSS_SOFT = (85, 120, 70)
STONE_GREY = (175, 180, 165)

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


def fern_icon(size):
    """A simple fern frond: a central stem with paired leaflets."""
    img = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(img)
    w, h = size
    base = (w * 0.5, h * 0.88)
    tip = (w * 0.5, h * 0.12)

    d.line([base, tip], fill=MOSS_SOFT, width=max(3, int(w * 0.025)))

    n = 9
    for i in range(1, n):
        t = i / n
        px = base[0] + (tip[0] - base[0]) * t
        py = base[1] + (tip[1] - base[1]) * t
        length = (1 - t * 0.6) * w * 0.26
        for side in (-1, 1):
            ex = px + length * side
            ey = py - length * 0.35
            d.line([(px, py), (ex, ey)], fill=MOSS, width=max(2, int(w * 0.012)))

    glow = img.filter(ImageFilter.GaussianBlur(w * 0.02))
    return ImageChops.screen(img, glow)


def fern_icon_rgba(size):
    rgb = fern_icon(size).convert("RGB")
    alpha = rgb.convert("L").point(lambda v: min(255, int(v * 1.5)))
    out = rgb.copy()
    out.putalpha(alpha)
    return out


def build(w, h, layout):
    img = Image.new("RGB", (w, h), (0, 0, 0))

    icon_size = layout["icon_size"]
    icon = fern_icon((icon_size, icon_size))
    img.paste(icon, layout["icon_pos"])

    title_font = load_font(FONT_CANDIDATES_BOLD, layout["title_size"])
    tag_font = load_font(FONT_CANDIDATES_REGULAR, layout["tag_size"])

    title = "Moss & Manor"
    tagline = "Wild Gardens. Quiet Moments."

    def draw_title(d, color):
        d.text(layout["title_pos"], title, font=title_font, fill=color)

    img = ImageChops.screen(img, glow_layer((w, h), draw_title, MOSS_SOFT, 14))
    draw = ImageDraw.Draw(img)
    draw.text(layout["title_pos"], title, font=title_font, fill=(225, 235, 215))
    draw.text(layout["tag_pos"], tagline, font=tag_font, fill=STONE_GREY)

    return img.convert("RGBA")


def main():
    wide = build(1920, 1080, {
        "icon_size": 300,
        "icon_pos": (740, 390),
        "title_pos": (1100, 470),
        "title_size": 66,
        "tag_pos": (1104, 560),
        "tag_size": 34,
    })
    wide.save(os.path.join(HERE, "brand_16x9_fallback.png"), "PNG", optimize=True)

    icon = fern_icon_rgba((300, 300))
    icon.save(os.path.join(HERE, "icon.png"), "PNG", optimize=True)

    fallback = wide.convert("RGB").resize((1280, 720))
    fallback.save(os.path.join(HERE, "thumbnail_1280x720.png"), "PNG", optimize=True)

    print("Wrote icon.png, brand_16x9_fallback.png, and thumbnail_1280x720.png")


if __name__ == "__main__":
    main()
