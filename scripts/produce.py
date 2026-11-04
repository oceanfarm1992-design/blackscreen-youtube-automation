#!/usr/bin/env python3
"""
Produce the day's video asset(s) end-to-end for the "Meditated Sleeping" channel.

For a chosen theme (or the date-based rotation) and format, this:
  1. synthesizes theme audio            (generate_theme_audio.py)
  2. renders a dim, per-video animation   (make_animated_video.py)
  3. assigns the branded thumbnail       (assets/branding/thumbnail_1280x720.png)
  4. writes SEO metadata                 (make_metadata.py)
  5. runs QC on the durations            (59s Short / 8-12h long-form)
  6. writes a manifest and marks it "queued" for publishing

Nothing is uploaded here. Publishing is a separate, credentialed step.

Usage:
    python produce.py --format short                 # today's theme, 59s Short
    python produce.py --format long --hours 10        # today's theme, 10h long-form
    python produce.py --theme forest --format both    # both formats for a given theme
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import date

import channel_kit as K
import themes as T

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BRAND = os.path.join(ROOT, "assets", "branding")
THUMBNAIL = os.path.join(BRAND, "thumbnail_1280x720.png")
THUMBS_GEN = os.path.join(ROOT, "assets", "thumbnails", "gen")  # per-theme clickable thumbnails
ICON = os.path.join(BRAND, "icon.png")  # headphone logo, a faint corner watermark
LONG_SEGMENT_SECONDS = 1800  # 30 seamless minutes of animation, looped to the full 8-12h

SHORT_SECONDS = 59
PILL_FILL = (232, 74, 95)  # channel red/pink, matches the thumbnail duration pill
LONG_LOOP_SECONDS = 600  # 10 min seamless loop, stream-looped to full length by ffmpeg
CLIPS_DIR = os.path.join(ROOT, "assets", "clips")  # AI-generated clip library


def run(cmd):
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True)


def feature_thumbnail(key, out_path, seed, volume):
    """The theme's scenic thumbnail with a per-upload color grade and a
    'VOL. N' badge, so no two uploads share a thumbnail. Falls back to the
    committed image if anything goes wrong -- never blocks an upload."""
    gen = os.path.join(THUMBS_GEN, f"{key}.png")
    src = gen if os.path.exists(gen) else THUMBNAIL
    try:
        import numpy as np
        from PIL import Image

        img = Image.open(src).convert("RGB").resize((K.THUMB_W, K.THUMB_H))
        img = K.grade_and_badge(img, volume, PILL_FILL, np.random.default_rng(seed))
        img.save(out_path, "PNG", optimize=True)
    except Exception as e:
        print(f"  ! per-upload thumbnail failed ({e}); using the committed one")
        shutil.copyfile(src, out_path)
    return out_path



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


def qc(fmt, video_path, hours):
    dur = ffprobe_duration(video_path)
    res = ffprobe_resolution(video_path)
    problems = []
    if fmt == "short":
        if abs(dur - SHORT_SECONDS) > 1.0:
            problems.append(f"Short duration {dur:.1f}s is not ~{SHORT_SECONDS}s")
        if res != "1080x1920":
            problems.append(f"Short resolution {res} is not 1080x1920 (vertical)")
    else:
        target = hours * 3600
        if not (T.LONG_HOURS_MIN * 3600 <= dur <= 12 * 3600):
            problems.append(f"Long duration {dur/3600:.2f}h outside the "
                            f"{T.LONG_HOURS_MIN}-12h window")
        elif abs(dur - target) > max(120, 0.03 * target):
            problems.append(f"Long duration {dur/3600:.2f}h is not near the "
                            f"target {hours}h")
        if res != "1920x1080":
            problems.append(f"Long resolution {res} is not 1920x1080")
    return {"duration_sec": round(dur, 2), "resolution": res, "problems": problems}


def produce_one(theme, fmt, out_dir, hours, seed, run_date, volume=None):
    key = theme["key"]
    seed = K.render_seed(T, seed)  # this channel's own seed: never shared with another channel
    variant = ["--variant", str(volume)] if volume else []
    # Long-form length is content-matched per theme (combos 3h, solo freq 8h,
    # nature/music 10h). An explicit --hours overrides it; otherwise use the map.
    if fmt == "long":
        hours = hours if hours else T.long_hours_for(key)
    stem = os.path.join(out_dir, f"{key}_{fmt}")
    audio = f"{stem}_audio.wav"
    video = f"{stem}.mp4"
    thumb = f"{stem}_thumb.png"
    meta = f"{stem}_meta.json"

    gta = os.path.join(HERE, "generate_theme_audio.py")
    mv = os.path.join(HERE, "make_animated_video.py")

    def animate(seconds, width, height, segment=None):
        cmd = [sys.executable, mv, "--audio", audio, "--duration-seconds", str(seconds),
               "--width", str(width), "--height", str(height),
               "--color", T.accent_for(key), "--icon", ICON, "--topic", T.topic_for(key),
               "--dim", str(T.VISUAL_DIM), "--seed", str(seed), "--out", video] + variant
        if segment:
            cmd += ["--segment-seconds", str(segment)]
        run(cmd)
    mm = os.path.join(HERE, "make_metadata.py")

    # Optional wellness frequency layers (Solfeggio/432 tone(s), brainwave beat,
    # bowl) plus tone-shaping (soft timbre, reverb wash, high-tone de-emphasis).
    freq = T.synth_args(theme)
    vol = ["--volume", str(volume)] if volume else []

    has_ai_clips = os.path.isdir(os.path.join(CLIPS_DIR, key)) and any(
        f.endswith(".wav") for f in os.listdir(os.path.join(CLIPS_DIR, key))
    ) if os.path.isdir(os.path.join(CLIPS_DIR, key)) else False
    bla = os.path.join(HERE, "build_long_audio.py")

    if fmt == "short":
        run([sys.executable, gta, "--theme", theme["synth"], "--seconds", str(SHORT_SECONDS),
             "--seed", str(seed), "--out", audio] + variant + freq)
        animate(SHORT_SECONDS, 1080, 1920)
        run([sys.executable, mm, "--theme", key, "--format", "short", "--out", meta] + vol)
    elif has_ai_clips:
        run([sys.executable, bla, "--theme", key, "--seconds", str(LONG_LOOP_SECONDS),
             "--seed", str(seed), "--out", audio])
        animate(hours * 3600, 1920, 1080, LONG_SEGMENT_SECONDS)
        run([sys.executable, mm, "--theme", key, "--format", "long", "--hours", str(hours),
             "--out", meta] + vol)
    else:
        run([sys.executable, gta, "--theme", theme["synth"], "--loop-seconds", str(LONG_LOOP_SECONDS),
             "--seed", str(seed), "--out", audio] + variant + freq)
        animate(hours * 3600, 1920, 1080, LONG_SEGMENT_SECONDS)
        run([sys.executable, mm, "--theme", key, "--format", "long", "--hours", str(hours),
             "--out", meta] + vol)

    # Long-form gets this upload's own version of the per-theme scenic
    # thumbnail. Shorts use an auto-selected video frame — skip the custom
    # thumbnail to save API quota (thumbnails.set costs 50 units).
    if fmt == "long":
        thumbnail_rel = os.path.relpath(feature_thumbnail(key, thumb, seed, volume), ROOT)
    else:
        thumbnail_rel = None
    report = qc(fmt, video, hours)

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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--theme", default="auto", help="theme key or 'auto' for date rotation")
    p.add_argument("--format", choices=["short", "long", "both"],
                   help="required unless --daily is used")
    p.add_argument("--daily", action="store_true",
                   help="produce the day's Short, plus the long-form on long-form days")
    p.add_argument("--shorts", type=int, default=0,
                   help="test batch: produce Shorts for the first N of today's musics")
    p.add_argument("--longs", type=int, default=0,
                   help="test batch: produce long-forms for the first M of today's musics")
    p.add_argument("--slot", type=int, default=None,
                   help="produce ONE scheduled video: 0 = the long-form (only on long-form "
                        "days -- otherwise exits without producing), 1 = the daily Short")
    p.add_argument("--hours", type=int, default=None,
                   help="override long-form length; default = per-theme map "
                        "(combos 3h, solo freq 8h, nature/music 10h)")
    p.add_argument("--seed", type=int, default=None, help="defaults to YYYYMMDD")
    p.add_argument("--date", default=None,
                   help="YYYY-MM-DD this run is FOR (default: today). The scheduler "
                        "passes the day the cron was scheduled for, because GitHub "
                        "often starts crons hours late -- sometimes past midnight.")
    p.add_argument("--out-dir", default="out")
    args = p.parse_args()

    if (not args.daily and not args.format and not (args.shorts or args.longs)
            and args.slot is None):
        p.error("give --daily, --format, --slot, or --shorts/--longs")

    run_date = date.fromisoformat(args.date) if args.date else date.today()
    # Each day owns a block of 1000 seeds (slot/batch offsets stay inside it), so
    # one day's Short (date+1) can never reuse the next day's feature seed.
    seed = args.seed if args.seed is not None else int(run_date.strftime("%Y%m%d")) * 1000
    os.makedirs(args.out_dir, exist_ok=True)

    # Cadence shared with every channel (see channel_kit): a Short every day,
    # a long-form every FEATURE_EVERY_DAYS days, each on its own full rotation.

    results = []
    if args.slot is not None:
        pick = K.scheduled_slot(T, run_date, args.slot)
        if pick is None:
            print(f"No long-form on {run_date}: they go out every {K._every(T)} days "
                  f"(next: {K.next_feature_day(T, run_date)}). Nothing to produce.")
            return
        theme, fmt, vol = pick
        print(f"Slot {args.slot} for {run_date}: {theme['key']} {fmt} Vol. {vol}")
        results.append(produce_one(theme, fmt, args.out_dir, args.hours, seed + args.slot,
                                   run_date, vol))
    elif args.shorts or args.longs:
        k, n = K.feature_number(T, run_date), K._rules_day(run_date)
        for i in range(args.longs):
            theme, vol = K.feature_at(T, k + i)
            results.append(produce_one(theme, "long", args.out_dir, args.hours,
                                       seed + i * 10, run_date, vol))
        for i in range(args.shorts):
            theme, vol = K.short_at(T, n + i)
            results.append(produce_one(theme, "short", args.out_dir, args.hours,
                                       seed + i * 10 + 1, run_date, vol))
    elif args.daily:
        if K.is_feature_day(T, run_date):
            theme, vol = K.feature_for(T, run_date)
            results.append(produce_one(theme, "long", args.out_dir, args.hours, seed,
                                       run_date, vol))
        theme, vol = K.short_for(T, run_date)
        results.append(produce_one(theme, "short", args.out_dir, args.hours, seed + 1,
                                   run_date, vol))
    else:
        theme = T.resolve_theme(args.theme, run_date)
        formats = ["short", "long"] if args.format == "both" else [args.format]
        results = [produce_one(theme, f, args.out_dir, args.hours, seed + i, run_date)
                   for i, f in enumerate(formats)]

    failed = [r for r in results if r["status"] != "queued"]
    if failed:
        print(f"\n{len(failed)} of {len(results)} asset(s) failed QC.")
        sys.exit(1)
    print(f"\nAll {len(results)} asset(s) queued.")


if __name__ == "__main__":
    main()
