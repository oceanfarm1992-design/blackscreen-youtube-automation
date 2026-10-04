#!/usr/bin/env python3
"""
Generate "The Static Horizon" branded icon (and a fallback static frame,
kept only as a safety net -- the real video background is the procedural
animation in scripts/make_animated_video.py).

Local dev tool, not run in CI -- output PNGs are committed. Requires Pillow.
Icon: a retro sunset/horizon line with a glowing orb and a few VHS-style
static scanlines, in the channel's retro neon magenta/cyan palette.

Usage:
    python make_brand_frames.py
"""
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

MAGENTA = (210, 70, 200)
CYAN = (70, 200, 210)
GREY = (170, 165, 185)

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


def horizon_icon(size):
    """A retro sunset orb sinking below a horizon line, crossed by a few
    VHS-style static scanlines."""
    img = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(img)
    w, h = size
    cx, cy = w // 2, int(h * 0.48)
    r = int(min(w, h) * 0.3)

    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=MAGENTA)
    # horizon line cuts the lower part of the orb
    d.rectangle([0, cy, w, h], fill=(0, 0, 0))
    d.line([(0, cy), (w, cy)], fill=CYAN, width=max(2, int(h * 0.012)))

    rng = random.Random(3)
    for _ in range(5):
        y = rng.uniform(cy * 0.2, cy * 1.6)
        x0 = rng.uniform(0, w * 0.4)
        x1 = x0 + rng.uniform(w * 0.2, w * 0.5)
        d.line([(x0, y), (x1, y)], fill=GREY, width=1)

    glow = img.filter(ImageFilter.GaussianBlur(r * 0.3))
    return ImageChops.screen(img, glow)


def horizon_icon_rgba(size):
    rgb = horizon_icon(size).convert("RGB")
    alpha = rgb.convert("L").point(lambda v: min(255, int(v * 1.3)))
    out = rgb.copy()
    out.putalpha(alpha)
    return out


def build(w, h, layout):
    img = Image.new("RGB", (w, h), (0, 0, 0))

    icon_size = layout["icon_size"]
    icon = horizon_icon((icon_size, icon_size))
    img.paste(icon, layout["icon_pos"])

    title_font = load_font(FONT_CANDIDATES_BOLD, layout["title_size"])
    tag_font = load_font(FONT_CANDIDATES_REGULAR, layout["tag_size"])

    title = "The Static Horizon"
    tagline = "Lost Signals. Quiet Miles."

    def draw_title(d, color):
        d.text(layout["title_pos"], title, font=title_font, fill=color)

    img = ImageChops.screen(img, glow_layer((w, h), draw_title, (140, 60, 150), 14))
    draw = ImageDraw.Draw(img)
    draw.text(layout["title_pos"], title, font=title_font, fill=(225, 205, 230))
    draw.text(layout["tag_pos"], tagline, font=tag_font, fill=GREY)

    return img.convert("RGBA")


def main():
    wide = build(1920, 1080, {
        "icon_size": 300,
        "icon_pos": (740, 390),
        "title_pos": (1100, 470),
        "title_size": 60,
        "tag_pos": (1104, 560),
        "tag_size": 34,
    })
    wide.save(os.path.join(HERE, "brand_16x9_fallback.png"), "PNG", optimize=True)

    icon = horizon_icon_rgba((300, 300))
    icon.save(os.path.join(HERE, "icon.png"), "PNG", optimize=True)

    fallback = wide.convert("RGB").resize((1280, 720))
    fallback.save(os.path.join(HERE, "thumbnail_1280x720.png"), "PNG", optimize=True)

    print("Wrote icon.png, brand_16x9_fallback.png, and thumbnail_1280x720.png")


if __name__ == "__main__":
    main()
