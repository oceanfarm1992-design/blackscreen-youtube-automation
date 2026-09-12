#!/usr/bin/env python3
"""
Generate the "Aether & Ash" branded video-background frames (the still image
looped behind the audio for the whole video, per scripts/make_video.py).

Local dev tool, not run in CI -- output PNGs are committed. Requires Pillow.
Style mirrors assets/branding/brand_16x9.png: pure black canvas, a small
glowing brand icon, the brand name in a soft warm glow, and the tagline
underneath -- kept extremely dark/minimal so an hours-long render stays easy
on the eyes and cheap for ffmpeg to encode (mostly-black frame).

Usage:
    python make_brand_frames.py
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

EMBER = (255, 140, 60)
EMBER_SOFT = (200, 110, 60)
ASH_GREY = (170, 165, 160)

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
    """Render draw_fn onto a black RGB layer, then Gaussian-blur it for a
    soft glow that can be screen-blended onto the base image."""
    layer = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d, color)
    return layer.filter(ImageFilter.GaussianBlur(blur))


def ember_icon(size):
    """A small glowing 'cracked ember' rune -- an irregular dark disc with a
    bright orange fracture through the middle, echoing the thumbnail art."""
    img = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size[0] // 2, size[1] // 2
    r = min(size) // 2 - 6
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(26, 24, 22))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(60, 55, 50), width=3)

    # jagged crack lines radiating from the center
    import math
    import random
    rng = random.Random(7)
    for _ in range(6):
        ang = rng.uniform(0, 2 * math.pi)
        length = r * rng.uniform(0.5, 0.9)
        x1 = cx + math.cos(ang) * length * 0.15
        y1 = cy + math.sin(ang) * length * 0.15
        x2 = cx + math.cos(ang) * length
        y2 = cy + math.sin(ang) * length
        d.line([x1, y1, x2, y2], fill=EMBER, width=4)
    d.ellipse([cx - r * 0.28, cy - r * 0.28, cx + r * 0.28, cy + r * 0.28],
              fill=(255, 200, 140))

    glow = img.filter(ImageFilter.GaussianBlur(r * 0.35))
    from PIL import ImageChops
    return ImageChops.screen(img, glow)


def build(w, h, layout):
    img = Image.new("RGB", (w, h), (0, 0, 0))

    icon_size = layout["icon_size"]
    icon = ember_icon((icon_size, icon_size))
    img.paste(icon, layout["icon_pos"])

    title_font = load_font(FONT_CANDIDATES_BOLD, layout["title_size"])
    tag_font = load_font(FONT_CANDIDATES_REGULAR, layout["tag_size"])

    draw = ImageDraw.Draw(img)
    title = "Aether & Ash"
    tagline = "Dark Ambient. Deep Focus."

    def draw_title(d, color):
        d.text(layout["title_pos"], title, font=title_font, fill=color)

    def draw_tag(d, color):
        d.text(layout["tag_pos"], tagline, font=tag_font, fill=color)

    from PIL import ImageChops
    img = ImageChops.screen(img, glow_layer((w, h), draw_title, EMBER_SOFT, 14))
    draw = ImageDraw.Draw(img)
    draw.text(layout["title_pos"], title, font=title_font, fill=(225, 200, 185))
    draw.text(layout["tag_pos"], tagline, font=tag_font, fill=ASH_GREY)

    return img.convert("RGBA")


def main():
    wide = build(1920, 1080, {
        "icon_size": 300,
        "icon_pos": (740, 390),
        "title_pos": (1100, 470),
        "title_size": 72,
        "tag_pos": (1104, 560),
        "tag_size": 34,
    })
    wide.save(os.path.join(HERE, "brand_16x9.png"), "PNG", optimize=True)

    tall = build(1080, 1920, {
        "icon_size": 260,
        "icon_pos": (410, 830),
        "title_pos": (280, 1130),
        "title_size": 62,
        "tag_pos": (300, 1210),
        "tag_size": 30,
    })
    tall.save(os.path.join(HERE, "brand_9x16.png"), "PNG", optimize=True)
    print("Wrote brand_16x9.png and brand_9x16.png")


if __name__ == "__main__":
    main()
