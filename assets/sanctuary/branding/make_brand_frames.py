#!/usr/bin/env python3
"""
Generate the "Sanctuary of Sci" branded icon (and a fallback static frame,
kept only as a safety net -- the real video background is the procedural
animation in scripts/make_animated_video.py).

Local dev tool, not run in CI -- output PNGs are committed. Requires Pillow.
Style mirrors assets/aether/branding/make_brand_frames.py: pure black
canvas, a small glowing brand icon, the brand name in a soft cool-blue glow,
and the tagline underneath. Icon: a ringed planet, in the channel's cool
blue / deep violet palette.

Usage:
    python make_brand_frames.py
"""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

ION_BLUE = (90, 160, 255)
ION_SOFT = (70, 110, 200)
STAR_GREY = (160, 170, 195)

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


def planet_icon(size):
    """A small glowing ringed planet -- a dark violet-blue sphere with a
    luminous blue ring and a scatter of distant stars."""
    img = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size[0] // 2, size[1] // 2
    r = min(size) // 2 - 10

    rng = random.Random(11)
    for _ in range(18):
        sx = rng.uniform(0, size[0])
        sy = rng.uniform(0, size[1])
        if (sx - cx) ** 2 / (r * 1.8) ** 2 + (sy - cy) ** 2 / (r * 1.3) ** 2 < 1.1:
            continue
        s = rng.uniform(0.6, 1.8)
        d.ellipse([sx - s, sy - s, sx + s, sy + s], fill=STAR_GREY)

    ring_w, ring_h = r * 1.9, r * 0.55
    d.ellipse([cx - ring_w / 2, cy - ring_h / 2, cx + ring_w / 2, cy + ring_h / 2],
              outline=ION_BLUE, width=max(2, int(r * 0.07)))

    d.ellipse([cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62],
              fill=(26, 24, 46))
    d.ellipse([cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62],
              outline=(70, 75, 110), width=2)
    # crescent highlight
    d.pieslice([cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62],
               200, 330, fill=(70, 90, 150))

    glow = img.filter(ImageFilter.GaussianBlur(r * 0.3))
    return ImageChops.screen(img, glow)


def planet_icon_rgba(size):
    """Standalone transparent-background version, for overlaying onto the
    animated video. Alpha derived from brightness."""
    rgb = planet_icon(size).convert("RGB")
    alpha = rgb.convert("L").point(lambda v: min(255, int(v * 1.3)))
    out = rgb.copy()
    out.putalpha(alpha)
    return out


def build(w, h, layout):
    img = Image.new("RGB", (w, h), (0, 0, 0))

    icon_size = layout["icon_size"]
    icon = planet_icon((icon_size, icon_size))
    img.paste(icon, layout["icon_pos"])

    title_font = load_font(FONT_CANDIDATES_BOLD, layout["title_size"])
    tag_font = load_font(FONT_CANDIDATES_REGULAR, layout["tag_size"])

    title = "Sanctuary of Sci"
    tagline = "Deep Space. Deep Focus."

    def draw_title(d, color):
        d.text(layout["title_pos"], title, font=title_font, fill=color)

    img = ImageChops.screen(img, glow_layer((w, h), draw_title, ION_SOFT, 14))
    draw = ImageDraw.Draw(img)
    draw.text(layout["title_pos"], title, font=title_font, fill=(200, 215, 240))
    draw.text(layout["tag_pos"], tagline, font=tag_font, fill=STAR_GREY)

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

    icon = planet_icon_rgba((300, 300))
    icon.save(os.path.join(HERE, "icon.png"), "PNG", optimize=True)

    # 1280x720 fallback thumbnail (used only if a per-theme thumbnail is missing)
    fallback = wide.convert("RGB").resize((1280, 720))
    fallback.save(os.path.join(HERE, "thumbnail_1280x720.png"), "PNG", optimize=True)

    print("Wrote icon.png, brand_16x9_fallback.png, and thumbnail_1280x720.png")


if __name__ == "__main__":
    main()
