#!/usr/bin/env python3
"""
Shared pipeline for the animated channels: Aether & Ash, Sanctuary of Sci,
Hearth & Quill, The Static Horizon, Aether Resonance, Moss & Manor.

Each channel folder holds only its DATA -- themes.py (rotation, SEO copy,
colors, topics, HOW_TO) and make_thumbnails.py (thumbnail style) -- plus
thin entry points (produce.py, make_metadata.py, publish_queue.py) that hand
their themes module to the functions here. Rendering, metadata, QC and
upload logic live once, in this file, so a fix reaches all six channels.

A channel's asset folder (assets/<folder>/) and upload secrets
(<FOLDER>_YT_CLIENT_ID / _CLIENT_SECRET / _REFRESH_TOKEN) are derived from
its folder name, e.g. hearth/ -> assets/hearth/, HEARTH_YT_*.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import zlib
from datetime import date

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS)

SHORT_SECONDS = 59
CATEGORY_MUSIC = "10"

# Hours-long features, for channels whose themes.py sets LONG_HOURS_CYCLE
# (only phone-verified channels: unverified ones can't upload over 15 min).
# A fresh, seamlessly loopable LONG_SEGMENT_SECONDS of animation and a
# LONG_AUDIO_LOOP_SECONDS seamless audio loop are rendered per video, then
# looped out to the full length.
LONG_SEGMENT_SECONDS = 3600
LONG_AUDIO_LOOP_SECONDS = 900
# YouTube counts the combined length of all tags against a 500-char cap (and
# adds quotes around multi-word tags). Pack to a safe 480.
TAG_CHAR_LIMIT = 480


def utf8_stdout():
    """Windows consoles default to cp1252 and choke on emoji in titles."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class Channel:
    """Paths and names derived from a channel's themes module location."""

    def __init__(self, T):
        self.T = T
        self.dir = os.path.dirname(os.path.abspath(T.__file__))
        self.slug = os.path.basename(self.dir)
        self.brand = os.path.join(ROOT, "assets", self.slug, "branding")
        self.thumbs_gen = os.path.join(ROOT, "assets", self.slug, "thumbnails", "gen")
        self.secret_prefix = f"{self.slug.upper()}_YT"

    def script(self, name):
        return os.path.join(self.dir, name)


# --------------------------------------------------------------------------- #
# Metadata

def pack_tags(T, theme, fmt):
    """Theme-specific tags first, then the shared niche pool, deduped, filled
    up to the tag-character budget."""
    pool = list(theme["tags"]) + T.GLOBAL_TAGS
    if fmt == "short":
        pool = ["shorts", "short video"] + pool
    tags, seen, used = [], set(), 0
    for t in pool:
        t = t.strip()
        key = t.lower()
        if not t or key in seen:
            continue
        cost = len(t) + (2 if " " in t else 0) + 1  # quotes for phrases + comma
        if used + cost > TAG_CHAR_LIMIT:
            continue
        tags.append(t)
        seen.add(key)
        used += cost
    return tags


def with_volume(title, volume):
    """Add 'Vol. N' just before the title's emoji ('Creek Hollow Vol. 3 🏞️ ...'),
    so every repeat of a theme gets a distinct title instead of a duplicate."""
    if not volume:
        return title
    tag = f" Vol. {volume}"
    for i, ch in enumerate(title):
        if i and title[i - 1] == " " and ord(ch) > 0x2500:  # first emoji/symbol
            return title[:i - 1] + tag + title[i - 1:]
    if title.endswith(" #shorts"):
        return title[:-len(" #shorts")] + tag + " #shorts"
    return title + tag


def fit_title(title, limit=100):
    """YouTube hard-caps titles at 100 chars. Trim the trailing descriptor at a
    word boundary, keeping a Short's closing '#shorts'."""
    if len(title) <= limit:
        return title
    tail = " #shorts" if title.endswith(" #shorts") else ""
    head = title[:len(title) - len(tail)]
    room = limit - len(tail)
    cut = head[:room]
    if head[room] != " ":
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" |-&,") + tail


def build_metadata(T, theme, fmt, volume=None, hours=None):
    title = theme["short_title"] if fmt == "short" else theme["long_title"]
    if fmt == "long" and hours:
        title = title.replace("14 Minute", f"{hours} Hours")
    title = fit_title(with_volume(title, volume))

    name = f"{theme['name']} (Vol. {volume})" if volume else theme["name"]
    if fmt == "short":
        lead, visual_line = name, ""
    elif hours:
        lead = f"{hours} Hours of {name}"
        # The hour of animation repeats, so don't claim "never a loop" here.
        visual_line = " Paired with a slow, generative ambient animation, rendered fresh for this video."
    else:
        lead = f"{T.FEATURE_SECONDS // 60} Minutes of {name}"
        visual_line = (" Paired with a slow, generative ambient animation — unique every "
                       "time, never a static loop.")
    hashtags = " ".join("#" + t.replace(" ", "") for t in theme["tags"][:3])
    if fmt == "short":
        hashtags += " #shorts"
    description = (
        f"{lead}.{visual_line}\n\n"
        f"{theme['description']}\n\n"
        f"\U0001F3A7 How to use: play at a low, comfortable volume to {T.HOW_TO}.\n\n"
        f"Perfect for {T.PERFECT_FOR}.\n\n"
        f"{hashtags}"
        + T.DESCRIPTION_FOOTER.format(brand=T.BRAND_NAME, tagline=T.BRAND_TAGLINE)
    )
    return {
        "theme": theme["key"],
        "format": fmt,
        "title": title,
        "description": description,
        "tags": pack_tags(T, theme, fmt),
        "categoryId": CATEGORY_MUSIC,
        "privacyStatus": "public",  # informational; publish_queue --privacy decides
    }


def metadata_main(T):
    utf8_stdout()
    p = argparse.ArgumentParser(description=f"Build SEO metadata for a {T.BRAND_NAME} video.")
    p.add_argument("--theme", default="auto", help="theme key or 'auto' for date rotation")
    p.add_argument("--format", required=True, choices=["short", "long"])
    p.add_argument("--volume", type=int, default=None,
                   help="repeat number of this theme; adds 'Vol. N' to the title")
    p.add_argument("--hours", type=int, default=None, help="hours-long feature length")
    p.add_argument("--out", default="metadata.json")
    args = p.parse_args()

    meta = build_metadata(T, T.resolve_theme(args.theme), args.format, args.volume, args.hours)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"Wrote {args.out}")
    print(f"  theme : {meta['theme']} ({args.format})")
    print(f"  title : {meta['title']}")
    print(f"  tags  : {len(meta['tags'])} tags")


# --------------------------------------------------------------------------- #
# Production

def run(cmd):
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True)


def volume_for(T, d, count, pos):
    """1-based count of how many times this rotation position's theme has come
    up since ANCHOR, so a theme's repeat uploads get distinct titles (Vol. N)."""
    return max(1, ((d - T.ANCHOR).days * count + pos) // len(T.THEMES) + 1)


def ffprobe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nk=1:nw=1", path],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def ffprobe_resolution(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", path],
        capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def qc(T, fmt, video_path, target_sec=None):
    dur = ffprobe_duration(video_path)
    res = ffprobe_resolution(video_path)
    problems = []
    if fmt == "short":
        if abs(dur - SHORT_SECONDS) > 1.0:
            problems.append(f"Short duration {dur:.1f}s is not ~{SHORT_SECONDS}s")
        if res != "1080x1920":
            problems.append(f"Short resolution {res} is not 1080x1920 (vertical)")
    else:
        target = target_sec or T.FEATURE_SECONDS
        if abs(dur - target) > max(5.0, 0.003 * target):
            problems.append(f"Feature duration {dur:.1f}s is not ~{target}s")
        if res != "1920x1080":
            problems.append(f"Feature resolution {res} is not 1920x1080")
    return {"duration_sec": round(dur, 2), "resolution": res, "problems": problems}


def long_hours_for(T, d):
    """Hours for the feature on day d if this channel makes hours-long
    features (LONG_HOURS_CYCLE, e.g. (3, 8, 10) -> 3h, 8h, 10h, 3h, ...), else
    None for the standard 14:30 feature."""
    cycle = getattr(T, "LONG_HOURS_CYCLE", ())
    return cycle[(d - T.ANCHOR).days % len(cycle)] if cycle else None


def produce_one(ch, theme, fmt, out_dir, seed, run_date, volume=None, hours=None):
    T = ch.T
    key = theme["key"]
    hours = hours if fmt == "long" else None
    if fmt == "short":
        duration = SHORT_SECONDS
    else:
        duration = hours * 3600 if hours else T.FEATURE_SECONDS
    width, height = (1080, 1920) if fmt == "short" else (1920, 1080)

    stem = os.path.join(out_dir, f"{key}_{fmt}")
    audio = f"{stem}_audio.wav"
    video = f"{stem}.mp4"
    thumb = f"{stem}_thumb.png"
    meta = f"{stem}_meta.json"

    # Hours-long: a seamless audio loop and a seamless hour of animation,
    # both fresh for this video, looped out to the full length.
    length = (["--loop-seconds", str(LONG_AUDIO_LOOP_SECONDS)] if hours
              else ["--seconds", str(duration)])
    segment = ["--segment-seconds", str(LONG_SEGMENT_SECONDS)] if hours else []
    run([sys.executable, os.path.join(SCRIPTS, "generate_theme_audio.py"),
         "--theme", theme["synth"]] + length +
        ["--seed", str(seed), "--out", audio] + T.synth_args(theme))
    run([sys.executable, os.path.join(SCRIPTS, "make_animated_video.py"),
         "--audio", audio, "--duration-seconds", str(duration),
         "--width", str(width), "--height", str(height),
         "--color", T.ACCENT_COLORS[key], "--icon", os.path.join(ch.brand, "icon.png"),
         "--topic", T.topic_for(key)] + segment + ["--seed", str(seed), "--out", video])
    vol = ["--volume", str(volume)] if volume else []
    hrs = ["--hours", str(hours)] if hours else []
    run([sys.executable, ch.script("make_metadata.py"),
         "--theme", key, "--format", fmt, "--out", meta] + vol + hrs)

    # Features get their own thumbnail, rendered from this upload's seed. Shorts
    # use an auto-selected video frame -- skip the custom thumbnail to save quota.
    if fmt == "long":
        label = f"{hours} HOURS" if hours else None
        thumbnail_rel = os.path.relpath(
            make_feature_thumbnail(ch, key, thumb, seed, volume, label), ROOT)
    else:
        thumbnail_rel = None
    report = qc(T, fmt, video, duration)

    manifest = {
        "date": run_date.isoformat(),
        "theme": key,
        "theme_name": theme["name"],
        "format": fmt,
        "video": os.path.relpath(video, ROOT),
        "thumbnail": thumbnail_rel,
        "metadata": os.path.relpath(meta, ROOT),
        "qc": report,
        "status": "queued" if not report["problems"] else "qc_failed",
    }
    with open(f"{stem}_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    tag = "OK" if not report["problems"] else "QC FAILED"
    print(f"[{tag}] {key} {fmt}: {report['resolution']} {report['duration_sec']}s -> {video}")
    for pr in report["problems"]:
        print("   ! " + pr)
    return manifest


def produce_main(T):
    utf8_stdout()
    ch = Channel(T)
    p = argparse.ArgumentParser(
        description=f"Render, describe and QC {T.BRAND_NAME} video(s). Uploading is "
                    "a separate step (publish_queue.py).")
    p.add_argument("--theme", default="auto", help="theme key or 'auto' for date rotation")
    p.add_argument("--format", choices=["short", "long", "both"],
                   help="with --theme: which format(s) to render")
    p.add_argument("--daily", action="store_true",
                   help=f"produce the day's batch: {T.DAILY_COUNT} videos "
                        f"({T.LONGS_PER_DAY} feature + {T.SHORTS_PER_DAY} short)")
    p.add_argument("--shorts", type=int, default=0,
                   help="test batch: produce Shorts for the first N of the day's themes")
    p.add_argument("--longs", type=int, default=0,
                   help="test batch: produce features for the first M of the day's themes")
    p.add_argument("--slot", type=int, default=None,
                   help="produce ONE video: slot 0..(DAILY_COUNT-1) of the day's rotation "
                        "(slots < LONGS_PER_DAY = feature, rest = short)")
    p.add_argument("--seed", type=int, default=None,
                   help="default: the run date's seed block (YYYYMMDD*1000)")
    p.add_argument("--date", default=None,
                   help="YYYY-MM-DD this run is FOR (default: today). The scheduler "
                        "passes the day the cron was scheduled for, because GitHub "
                        "often starts crons hours late -- sometimes past midnight.")
    p.add_argument("--hours", type=int, default=None,
                   help="override the feature length in hours (channels with "
                        "LONG_HOURS_CYCLE only -- i.e. phone-verified channels)")
    p.add_argument("--out-dir", default="out")
    args = p.parse_args()

    if (not args.daily and not args.format and not (args.shorts or args.longs)
            and args.slot is None):
        p.error("give --daily, --format, --slot, or --shorts/--longs")
    if args.hours and not getattr(T, "LONG_HOURS_CYCLE", ()):
        p.error(f"{T.BRAND_NAME} has no LONG_HOURS_CYCLE: YouTube rejects uploads over "
                "15 minutes until the channel is phone-verified")

    run_date = date.fromisoformat(args.date) if args.date else date.today()
    # Each day owns a block of 1000 seeds (slot/batch offsets stay inside it), so
    # one day's Short (date+1) can never reuse the next day's feature seed.
    seed = args.seed if args.seed is not None else int(run_date.strftime("%Y%m%d")) * 1000
    hours = args.hours or long_hours_for(T, run_date)
    os.makedirs(args.out_dir, exist_ok=True)

    def one(theme, fmt, s, volume=None):
        return produce_one(ch, theme, fmt, args.out_dir, s, run_date, volume, hours)

    results = []
    if args.slot is not None:
        selection = T.daily_selection(run_date, count=T.DAILY_COUNT)
        pos = args.slot % len(selection)
        theme = selection[pos]
        fmt = "long" if args.slot < T.LONGS_PER_DAY else "short"
        print(f"Slot {args.slot} for {run_date}: {theme['key']} {fmt}")
        results.append(one(theme, fmt, seed + args.slot,
                           volume_for(T, run_date, T.DAILY_COUNT, pos)))
    elif args.shorts or args.longs:
        need = max(args.shorts, args.longs, 1)
        count = max(need, T.DAILY_COUNT)
        selection = T.daily_selection(run_date, count=count)
        print(f"Test batch: {args.longs} feature(s) + {args.shorts} short(s) from: "
              + ", ".join(t["key"] for t in selection[:need]))
        for i in range(args.longs):
            results.append(one(selection[i], "long", seed + i * 10,
                               volume_for(T, run_date, count, i)))
        for i in range(args.shorts):
            results.append(one(selection[i], "short", seed + i * 10 + 1,
                               volume_for(T, run_date, count, i)))
    elif args.daily:
        selection = T.daily_selection(run_date, count=T.DAILY_COUNT)
        longs = selection[:T.LONGS_PER_DAY]
        shorts = selection[T.LONGS_PER_DAY:T.LONGS_PER_DAY + T.SHORTS_PER_DAY]
        print("Daily batch: " + ", ".join(t["key"] for t in longs) + " (feature) + "
              + ", ".join(t["key"] for t in shorts) + " (short)")
        for i, theme in enumerate(longs):
            results.append(one(theme, "long", seed + i,
                               volume_for(T, run_date, T.DAILY_COUNT, i)))
        for i, theme in enumerate(shorts):
            results.append(one(theme, "short", seed + 100 + i,
                               volume_for(T, run_date, T.DAILY_COUNT, T.LONGS_PER_DAY + i)))
    else:
        theme = T.resolve_theme(args.theme, run_date)
        formats = ["short", "long"] if args.format == "both" else [args.format]
        results = [one(theme, f, seed + i) for i, f in enumerate(formats)]

    failed = [r for r in results if r["status"] != "queued"]
    if failed:
        print(f"\n{len(failed)} of {len(results)} asset(s) failed QC.")
        sys.exit(1)
    print(f"\nAll {len(results)} asset(s) queued.")


# --------------------------------------------------------------------------- #
# Thumbnails
#
# A channel's make_thumbnails.py holds only a STYLE dict:
#   background   "noise" (the video's own noise engine) or a repo-relative photo
#   headlines    {theme_key: [line1, line2]}  -- themes rendered from scratch
#   hand_made    {theme_key, ...}  -- finished art in thumbnails/gen/, never redrawn
#   glow         optional {theme_key: (r, g, b)}; default = the theme's accent color
#   glow_strength, pill_fill, text_fill, font_sizes (line1, line2), min_font
#
# With a per-upload seed, every feature gets its own thumbnail: a fresh noise
# background (or a new crop of the photo), a moved glow, and a "VOL. N"
# badge -- so no two uploads of a theme ever share a thumbnail. Without a seed
# (local regeneration of the committed fallbacks) output is stable per theme.

THUMB_W, THUMB_H = 1280, 720
THUMB_MARGIN_X = 62
THUMB_MAX_TEXT_W = 660
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\impact.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",  # fonts-dejavu-extra
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",           # fonts-dejavu-core
]


def load_font(size):
    from PIL import ImageFont
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    # PIL's default bitmap font is tiny and would ruin the thumbnail; failing
    # here makes produce fall back to the committed per-theme thumbnail.
    raise RuntimeError("no TrueType font found for thumbnail text")


def _fit_font(draw, text, start, min_size):
    size = start
    while size > min_size:
        f = load_font(size)
        if draw.textlength(text, font=f) <= THUMB_MAX_TEXT_W:
            return f
        size -= 2
    return load_font(min_size)


def _glow(img, color, strength, rng, jitter):
    """Soft radial accent glow behind the headline area (screen-blended)."""
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
    x0, y0, x1, y1 = -220, 60, 700, 660
    if jitter:
        dx, dy = rng.integers(-90, 91), rng.integers(-70, 71)
        grow = rng.uniform(0.88, 1.12)
        cx, cy = (x0 + x1) / 2 + dx, (y0 + y1) / 2 + dy
        hw, hh = (x1 - x0) / 2 * grow, (y1 - y0) / 2 * grow
        x0, y0, x1, y1 = cx - hw, cy - hh, cx + hw, cy + hh
        strength *= rng.uniform(0.85, 1.15)
    layer = Image.new("RGB", (THUMB_W, THUMB_H), (0, 0, 0))
    ImageDraw.Draw(layer).ellipse(
        [x0, y0, x1, y1], fill=tuple(min(255, int(c * strength)) for c in color))
    return ImageChops.screen(img, layer.filter(ImageFilter.GaussianBlur(170)))


def _photo_background(path, rng, jitter):
    """The style's photo, resized; per-upload, a fresh zoomed crop of it."""
    from PIL import Image
    img = Image.open(path).convert("RGB").resize((THUMB_W, THUMB_H))
    if not jitter:
        return img
    zoom = rng.uniform(1.0, 1.12)
    cw, chh = int(THUMB_W / zoom), int(THUMB_H / zoom)
    left = int(rng.integers(0, THUMB_W - cw + 1))
    top = int(rng.integers(0, THUMB_H - chh + 1))
    return img.crop((left, top, left + cw, top + chh)).resize((THUMB_W, THUMB_H))


def _noise_background(T, key, rng):
    """A still from the same engine (and topic texture) the video uses."""
    import numpy as np
    from PIL import Image
    from make_animated_video import TOPIC_PROFILES, _channel_gain, _noise_field
    prof = TOPIC_PROFILES.get(T.topic_for(key), TOPIC_PROFILES["neutral"])
    field = _noise_field(THUMB_W, THUMB_H, rng, tilt=prof["tilt"], blur_frac=prof["blur_frac"])
    gains = np.array(_channel_gain(T.ACCENT_COLORS[key]), dtype=np.float32)
    rgb = np.clip(field[:, :, None] * gains[None, None, :] * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(rgb)  # uint8 HxWx3 -> RGB


def _pill(draw, x, y, label, fill, size=40):
    font = load_font(size)
    tw = draw.textlength(label, font=font)
    h = int(size * 1.55)
    draw.rounded_rectangle([x, y, x + tw + 60, y + h], radius=h // 2, fill=fill)
    draw.text((x + 30, y + int(size * 0.25)), label, font=font, fill=(255, 255, 255))


def grade_and_badge(img, volume, fill, rng):
    """For finished art we must not redraw: a slight per-upload color grade
    (so the file differs) plus a 'VOL. N' badge in the bottom-left corner."""
    from PIL import ImageDraw, ImageEnhance
    img = ImageEnhance.Brightness(img).enhance(rng.uniform(0.95, 1.05))
    img = ImageEnhance.Contrast(img).enhance(rng.uniform(0.96, 1.06))
    img = ImageEnhance.Color(img).enhance(rng.uniform(0.92, 1.08))
    if volume:
        _pill(ImageDraw.Draw(img), 40, THUMB_H - 40 - 62, f"VOL. {volume}", fill)
    return img


def render_thumbnail(T, style, key, out_path, seed=None, volume=None, length_label=None):
    import numpy as np
    from PIL import Image, ImageDraw
    ch = Channel(T)
    jitter = seed is not None
    rng = np.random.default_rng(seed if jitter else zlib.crc32(key.encode()))

    if key in style.get("hand_made", ()) or key not in style["headlines"]:
        src = os.path.join(ch.thumbs_gen, f"{key}.png")
        if not os.path.exists(src):
            src = os.path.join(ch.brand, "thumbnail_1280x720.png")
        img = Image.open(src).convert("RGB").resize((THUMB_W, THUMB_H))
        img = grade_and_badge(img, volume, style["pill_fill"], rng) if jitter else img
    else:
        if style["background"] == "noise":
            base = _noise_background(T, key, rng)
        else:
            base = _photo_background(os.path.join(ROOT, style["background"]), rng, jitter)
        from make_animated_video import _channel_gain
        accent = style.get("glow", {}).get(key) or tuple(
            int(c * 255) for c in _channel_gain(T.ACCENT_COLORS[key]))
        img = _glow(base, accent, style["glow_strength"], rng, jitter)
        draw = ImageDraw.Draw(img)
        lines = style["headlines"][key]
        f1 = _fit_font(draw, lines[0], style["font_sizes"][0], style["min_font"])
        f2 = _fit_font(draw, lines[1], style["font_sizes"][1], style["min_font"])
        y = 430
        for text, font in ((lines[0], f1), (lines[1], f2)):
            draw.text((THUMB_MARGIN_X, y), text, font=font, fill=style["text_fill"],
                      stroke_width=6, stroke_fill=(0, 0, 0))
            y += draw.textbbox((0, 0), text, font=font)[3] + 14
        length = length_label or f"{T.FEATURE_SECONDS // 60} MIN"
        label = f"{length} · VOL. {volume}" if volume else length
        _pill(draw, THUMB_MARGIN_X, y + 12, label, style["pill_fill"])

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    return out_path


def thumbnails_main(T, style):
    """Per-upload mode (--theme/--out, used by produce) or local regeneration
    of the committed fallback thumbnails in assets/<channel>/thumbnails/gen/."""
    utf8_stdout()
    ch = Channel(T)
    p = argparse.ArgumentParser(description=f"{T.BRAND_NAME} feature thumbnails (1280x720).")
    p.add_argument("--theme", default=None, help="render ONE thumbnail for this theme")
    p.add_argument("--out", default=None, help="with --theme: output PNG path")
    p.add_argument("--seed", type=int, default=None, help="per-upload variation seed")
    p.add_argument("--volume", type=int, default=None, help="adds 'VOL. N' to the badge")
    p.add_argument("--length-label", default=None, help="badge length text, e.g. '10 HOURS'")
    p.add_argument("--all", action="store_true", help="regenerate every committed fallback")
    p.add_argument("--themes", default=None, help="comma-separated keys to regenerate")
    args = p.parse_args()

    if args.theme:
        out = args.out or os.path.join(ch.thumbs_gen, f"{args.theme}.png")
        render_thumbnail(T, style, args.theme, out, args.seed, args.volume, args.length_label)
        print(f"Wrote {out}")
        return

    keys = [k for k in style["headlines"] if k not in style.get("hand_made", ())]
    if args.themes:
        keys = [k.strip() for k in args.themes.split(",") if k.strip() in keys]
    elif not args.all:
        keys = [k for k in keys if not os.path.exists(os.path.join(ch.thumbs_gen, f"{k}.png"))]
    for k in keys:
        path = render_thumbnail(T, style, k, os.path.join(ch.thumbs_gen, f"{k}.png"))
        print(f"  {k:26s} -> {os.path.relpath(path, ROOT)}")
    print(f"Done: {len(keys)} thumbnail(s).")


def make_feature_thumbnail(ch, key, out_path, seed, volume, length_label=None):
    """Render this upload's own thumbnail; if that fails for any reason (fonts,
    missing art), fall back to the committed per-theme one so the upload is
    never blocked over an optional extra."""
    cmd = [sys.executable, ch.script("make_thumbnails.py"), "--theme", key,
           "--out", out_path, "--seed", str(seed)]
    if volume:
        cmd += ["--volume", str(volume)]
    if length_label:
        cmd += ["--length-label", length_label]
    print("+", " ".join(cmd))
    if subprocess.run(cmd).returncode == 0 and os.path.exists(out_path):
        return out_path
    print("  ! per-upload thumbnail failed; using the committed one")
    gen = os.path.join(ch.thumbs_gen, f"{key}.png")
    shutil.copyfile(gen if os.path.exists(gen)
                    else os.path.join(ch.brand, "thumbnail_1280x720.png"), out_path)
    return out_path


# --------------------------------------------------------------------------- #
# Publishing

def publish_main(T):
    utf8_stdout()
    import upload_youtube as U  # google client libs are only needed here

    ch = Channel(T)
    p = argparse.ArgumentParser(
        description=f"Upload every queued {T.BRAND_NAME} asset in --out-dir to YouTube. "
                    f"Needs {ch.secret_prefix}_CLIENT_ID / _CLIENT_SECRET / _REFRESH_TOKEN.")
    p.add_argument("--out-dir", default="out")
    p.add_argument("--privacy", default="public", choices=["private", "unlisted", "public"])
    args = p.parse_args()

    manifests = sorted(glob.glob(os.path.join(args.out_dir, "*_manifest.json")))
    if not manifests:
        print(f"No manifests found in {args.out_dir}; nothing to publish.")
        return

    youtube = U.get_service(ch.secret_prefix)
    playlist_ids = {}  # title -> id, resolved once per run

    def add_long_to_playlist(man, video_id):
        pl = T.playlist_for(man["theme"])
        if not pl:
            man["playlist_status"] = "skipped"
            return
        try:
            if pl["title"] not in playlist_ids:
                playlist_ids[pl["title"]] = U.find_or_create_playlist(
                    youtube, pl["title"], pl["description"])
            U.add_to_playlist(youtube, playlist_ids[pl["title"]], video_id)
            man["playlist_status"] = pl["title"]
            print(f"  + playlist: {pl['title']}")
        except Exception as e:
            man["playlist_status"] = "failed"
            print(f"  ! playlist add skipped (token may lack the 'youtube' scope): {e}")

    for mpath in manifests:
        man = json.load(open(mpath, encoding="utf-8"))
        if man.get("status") != "queued":
            print(f"Skipping {os.path.basename(mpath)} (status={man.get('status')})")
            continue

        meta = json.load(open(os.path.join(ROOT, man["metadata"]), encoding="utf-8"))
        video = os.path.join(ROOT, man["video"])

        print(f"Uploading {man['theme']} {man['format']} as {args.privacy}: {meta['title']}")
        video_id = U.upload_video(
            youtube, video, meta["title"], meta["description"], meta.get("tags", []),
            category_id=meta.get("categoryId", CATEGORY_MUSIC), privacy=args.privacy,
        )
        # Custom thumbnails need a phone-verified channel; without it the API
        # returns 403 -- never fail the upload over an optional extra.
        if man.get("thumbnail"):
            try:
                U.set_thumbnail(youtube, video_id, os.path.join(ROOT, man["thumbnail"]))
                man["thumbnail_status"] = "set"
            except Exception as e:
                man["thumbnail_status"] = "skipped"
                print(f"  ! custom thumbnail not set (needs a verified channel): {e}")
        else:
            man["thumbnail_status"] = "none"

        if man["format"] == "long":
            add_long_to_playlist(man, video_id)

        man["video_id"] = video_id
        man["status"] = f"uploaded_{args.privacy}"
        with open(mpath, "w", encoding="utf-8") as f:
            json.dump(man, f, ensure_ascii=False, indent=2)
        print(f"  -> https://youtu.be/{video_id}  (status: {man['status']})")
