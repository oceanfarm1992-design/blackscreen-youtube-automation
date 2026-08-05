#!/usr/bin/env python3
"""
Generate a YouTube thumbnail by overlaying title/duration text onto a background
image chosen from a small rotating pool (moon/gradient/stars/etc).

Usage:
    python generate_thumbnail.py --title "Deep Sleep Music" --duration "8 Hours" \
        --background assets/bg_moon.png --out thumbnail.png

Keep a small pool (5-10) of pre-made calming background images in assets/ and
rotate through them (e.g. by row index % pool size) so thumbnails aren't 100%
identical across uploads, without needing a new AI image per video.
"""
import argparse
from PIL import Image, ImageDraw, ImageFont

THUMB_SIZE = (1280, 720)


def load_font(size: int):
    # Falls back to Pillow's default bitmap font if no truetype font is bundled.
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default()


def generate_thumbnail(title: str, duration: str, background_path: str | None, out_path: str,
                        accent_color=(200, 170, 255)):
    if background_path:
        img = Image.open(background_path).convert("RGB").resize(THUMB_SIZE)
    else:
        img = Image.new("RGB", THUMB_SIZE, (8, 8, 16))  # plain near-black fallback

    # Dark overlay so text stays readable regardless of background brightness
    overlay = Image.new("RGBA", THUMB_SIZE, (0, 0, 0, 110))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(img)
    title_font = load_font(72)
    duration_font = load_font(48)

    draw.text((60, 260), title, font=title_font, fill=(255, 255, 255))
    draw.text((60, 360), duration.upper(), font=duration_font, fill=accent_color)

    img.save(out_path)
    return out_path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True)
    p.add_argument("--duration", required=True, help='e.g. "8 Hours"')
    p.add_argument("--background", default=None, help="path to a background image; omit for plain dark bg")
    p.add_argument("--out", default="thumbnail.png")
    args = p.parse_args()

    path = generate_thumbnail(args.title, args.duration, args.background, args.out)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
