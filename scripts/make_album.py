#!/usr/bin/env python3
"""
Export distribution-ready audio for streaming platforms (DistroKid/TuneCore ->
Spotify, Apple Music, Amazon, etc.) from the same synth engine the videos use.

Streaming needs a different shape than YouTube: ~4-6 minute tracks, not 59s
Shorts or 8-10h long-forms. This renders an album per theme: N tracks at M
minutes each, WAV 16-bit/44.1kHz stereo (DistroKid's required format), plus
3000x3000 cover art and a metadata CSV to type into the distributor.

Audio uses themes.synth_args(), so tracks are sonically identical to the
channel's videos — same tones, same reverb, same tone-tilt.

Local dev tool (needs Pillow). NOT run in CI.

Usage:
    python make_album.py --theme rain_drops                 # 8 x 5min album
    python make_album.py --theme solfeggio_heal --tracks 6 --minutes 6
    python make_album.py --all                              # every theme
"""
import argparse
import csv
import os
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import themes as T  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT_ROOT = os.path.join(ROOT, "dist_music")
BASE_THUMB = os.path.join(ROOT, "assets", "branding", "thumbnail_1280x720.png")

COVER_PX = 3000           # distributors require >=3000x3000 square
FADE_SECONDS = 4.0        # gentle fade in/out so tracks don't click

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\impact.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

# Album title + accent colour per theme (accent matches the video thumbnails).
ALBUMS = {
    "rain_drops":          ("Soft Rain & Water Drops", (60, 150, 200)),
    "rooftop_rain":        ("Rooftop Rain & Gentle Thunder", (90, 130, 180)),
    "rain":                ("Rain Sounds for Sleep", (60, 140, 190)),
    "waterfall":           ("Waterfall Ambience", (60, 170, 190)),
    "forest":              ("Forest Sounds & Birdsong", (70, 170, 110)),
    "sleeping":            ("Deep Sleep Music", (70, 110, 200)),
    "indian":              ("Indian Sleep Ragas", (210, 140, 60)),
    "romantic":            ("Romantic Instrumental", (215, 80, 130)),
    "romantic_night":      ("Romantic Night", (180, 70, 150)),
    "gamma_focus":         ("Gamma Focus 40 Hz", (200, 160, 60)),
    "528hz_sleep":         ("528 Hz Sleep", (80, 170, 190)),
    "delta_sleep":         ("Delta Waves Sleep", (70, 100, 200)),
    "432hz_relax":         ("432 Hz Relaxation", (200, 110, 170)),
    "solfeggio_heal":      ("432 528 741 Hz Healing Sleep", (70, 90, 210)),
    "solfeggio_spirit":    ("528 741 963 Hz Body & Spirit", (150, 80, 210)),
    "solfeggio_deepsleep": ("Solfeggio & Delta Deep Sleep", (60, 100, 200)),
    "om_136":              ("OM 136.1 Hz Meditation", (215, 150, 60)),
    "963hz_awakening":     ("963 Hz Crown Chakra", (150, 90, 220)),
    "852hz_intuition":     ("852 Hz Third Eye", (110, 90, 220)),
    "741hz_clarity":       ("741 Hz Cleanse & Clarity", (70, 180, 150)),
}

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]


def load_font(size):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_track(theme, seconds, seed, out_path):
    """Render one seamless-loop track via the shared synth engine."""
    cmd = [sys.executable, os.path.join(HERE, "generate_theme_audio.py"),
           "--theme", theme["synth"], "--loop-seconds", str(seconds),
           "--seed", str(seed), "--out", out_path] + T.synth_args(theme)
    subprocess.run(cmd, check=True, capture_output=True)


def apply_fades(path):
    """Fade in/out so a track never starts or ends on an abrupt edge."""
    import numpy as np
    import soundfile as sf
    x, sr = sf.read(path)
    n = int(FADE_SECONDS * sr)
    if len(x) > 2 * n:
        ramp = np.linspace(0.0, 1.0, n) ** 2
        if x.ndim > 1:
            ramp = ramp[:, None]
        x[:n] *= ramp
        x[-n:] *= ramp[::-1]
    sf.write(path, x, sr, subtype="PCM_16")


def make_cover(album_title, color, out_path):
    """3000x3000 square cover: brand mark, album title, accent glow."""
    img = Image.new("RGB", (COVER_PX, COVER_PX), (10, 10, 12))
    glow = Image.new("RGB", (COVER_PX, COVER_PX), (0, 0, 0))
    ImageDraw.Draw(glow).ellipse(
        [-COVER_PX * 0.25, -COVER_PX * 0.15, COVER_PX * 0.95, COVER_PX * 0.85],
        fill=tuple(int(c * 0.55) for c in color))
    img = ImageChops.screen(img, glow.filter(ImageFilter.GaussianBlur(COVER_PX // 7)))

    # Brand headphone mark, lifted from the shared branding asset. The crop has
    # a near-black background, so screen-blend it onto a full-size layer instead
    # of pasting — pasting would show a hard black rectangle over the gradient.
    mark = Image.open(BASE_THUMB).convert("RGB").crop((505, 225, 745, 495))
    mw = int(COVER_PX * 0.40)
    mark = mark.resize((mw, int(mw * 270 / 240)))
    # Feather the crop to pure black at its edges, otherwise the rectangular
    # boundary stays faintly visible where screen-blending lifts the gradient.
    mask = Image.new("L", mark.size, 0)
    inset = int(mw * 0.06)
    ImageDraw.Draw(mask).ellipse(
        [inset, inset, mark.width - inset, mark.height - inset], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(mw * 0.07))
    mark = ImageChops.multiply(mark, Image.merge("RGB", (mask, mask, mask)))

    layer = Image.new("RGB", (COVER_PX, COVER_PX), (0, 0, 0))
    layer.paste(mark, ((COVER_PX - mark.width) // 2, int(COVER_PX * 0.14)))
    img = ImageChops.screen(img, layer)

    d = ImageDraw.Draw(img)
    # album title, wrapped to fit
    words, lines, cur = album_title.split(), [], ""
    font = load_font(int(COVER_PX * 0.085))
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= COVER_PX * 0.84:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)

    y = int(COVER_PX * 0.60)
    for line in lines:
        tw = d.textlength(line, font=font)
        d.text(((COVER_PX - tw) / 2, y), line, font=font, fill=(255, 255, 255),
               stroke_width=int(COVER_PX * 0.006), stroke_fill=(0, 0, 0))
        y += int(COVER_PX * 0.098)

    bf = load_font(int(COVER_PX * 0.038))
    brand = T.BRAND_NAME
    bw = d.textlength(brand, font=bf)
    d.text(((COVER_PX - bw) / 2, COVER_PX * 0.90), brand, font=bf,
           fill=(150, 220, 235))
    img.save(out_path, "PNG", optimize=True)


def build_album(theme, tracks, minutes):
    key = theme["key"]
    album, color = ALBUMS[key]
    out_dir = os.path.join(OUT_ROOT, key)
    os.makedirs(out_dir, exist_ok=True)
    seconds = int(minutes * 60)

    rows = []
    for i in range(tracks):
        title = f"{album}, Pt. {ROMAN[i] if i < len(ROMAN) else i + 1}"
        fname = f"{i + 1:02d} - {title}.wav".replace("/", "-")
        path = os.path.join(out_dir, fname)
        render_track(theme, seconds, seed=90000 + i * 17, out_path=path)
        apply_fades(path)
        rows.append({
            "track_number": i + 1,
            "title": title,
            "artist": T.BRAND_NAME,
            "album": album,
            "genre": "New Age",
            "duration_min": minutes,
            "file": fname,
            "instrumental": "yes",
            "explicit": "no",
            "ai_generated": "yes",
        })
        print(f"    {fname}")

    make_cover(album, color, os.path.join(out_dir, "cover_3000x3000.png"))
    with open(os.path.join(out_dir, "metadata.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"  -> {os.path.relpath(out_dir, ROOT)}  ({tracks} tracks + cover + metadata.csv)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--theme", default=None, help="theme key")
    p.add_argument("--all", action="store_true", help="every theme")
    p.add_argument("--tracks", type=int, default=8)
    p.add_argument("--minutes", type=float, default=5.0)
    args = p.parse_args()

    if args.all:
        keys = [t["key"] for t in T.THEMES]
    elif args.theme:
        keys = [args.theme]
    else:
        p.error("give --theme KEY or --all")

    for k in keys:
        theme = T.theme_by_key(k)
        if k not in ALBUMS:
            print(f"  ! no album defined for {k}, skipping")
            continue
        print(f"\n{ALBUMS[k][0]}:")
        build_album(theme, args.tracks, args.minutes)
    print(f"\nDone. Files in {os.path.relpath(OUT_ROOT, ROOT)}/")


if __name__ == "__main__":
    main()
