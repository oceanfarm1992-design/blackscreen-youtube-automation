#!/usr/bin/env python3
"""
Generate the "Aether Resonance" branded icon (and a fallback static frame,
kept only as a safety net -- the real video background is the procedural
animation in scripts/make_animated_video.py).

Local dev tool, not run in CI -- output PNGs are committed. Requires Pillow.
Icon: concentric soft ripple rings (resonance / sound bath), in a soft
teal/lavender palette with gentle, minimal lighting -- no sharp edges.

Usage:
    python make_brand_frames.py
"""
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

TEAL = (90, 170, 180)
LAVENDER = (140, 120, 190)
SOFT_GREY = (190, 195, 200)

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


def ripple_icon(size):
    """Concentric soft ripple rings radiating from a glowing center point."""
    img = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size[0] // 2, size[1] // 2
    max_r = min(size) // 2 - 6

    rings = 4
    for i in range(rings, 0, -1):
        r = max_r * i / rings
        color = TEAL if i % 2 == 0 else LAVENDER
        width = max(2, int(size[0] * 0.012))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)

    core_r = max_r * 0.12
    d.ellipse([cx - core_r, cy - core_r, cx + core_r, cy + core_r], fill=(230, 235, 240))

    glow = img.filter(ImageFilter.GaussianBlur(max_r * 0.18))
    return ImageChops.screen(img, glow)


def ripple_icon_rgba(size):
    rgb = ripple_icon(size).convert("RGB")
    alpha = rgb.convert("L").point(lambda v: min(255, int(v * 1.3)))
    out = rgb.copy()
    out.putalpha(alpha)
    return out


def build(w, h, layout):
    img = Image.new("RGB", (w, h), (0, 0, 0))

    icon_size = layout["icon_size"]
    icon = ripple_icon((icon_size, icon_size))
    img.paste(icon, layout["icon_pos"])

    title_font = load_font(FONT_CANDIDATES_BOLD, layout["title_size"])
    tag_font = load_font(FONT_CANDIDATES_REGULAR, layout["tag_size"])

    title = "Aether Resonance"
    tagline = "Pure Tone. Deep Calm."

    def draw_title(d, color):
        d.text(layout["title_pos"], title, font=title_font, fill=color)

    img = ImageChops.screen(img, glow_layer((w, h), draw_title, (90, 110, 140), 14))
    draw = ImageDraw.Draw(img)
    draw.text(layout["title_pos"], title, font=title_font, fill=(215, 225, 230))
    draw.text(layout["tag_pos"], tagline, font=tag_font, fill=SOFT_GREY)

    return img.convert("RGBA")


def main():
    wide = build(1920, 1080, {
        "icon_size": 300,
        "icon_pos": (740, 390),
        "title_pos": (1100, 470),
        "title_size": 64,
        "tag_pos": (1104, 560),
        "tag_size": 34,
    })
    wide.save(os.path.join(HERE, "brand_16x9_fallback.png"), "PNG", optimize=True)

    icon = ripple_icon_rgba((300, 300))
    icon.save(os.path.join(HERE, "icon.png"), "PNG", optimize=True)

    fallback = wide.convert("RGB").resize((1280, 720))
    fallback.save(os.path.join(HERE, "thumbnail_1280x720.png"), "PNG", optimize=True)

    print("Wrote icon.png, brand_16x9_fallback.png, and thumbnail_1280x720.png")


if __name__ == "__main__":
    main()
