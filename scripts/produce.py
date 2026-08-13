#!/usr/bin/env python3
"""
Produce the day's video asset(s) end-to-end for the "Meditated Sleeping" channel.

For a chosen theme (or the date-based rotation) and format, this:
  1. synthesizes theme audio            (generate_theme_audio.py)
  2. renders a branded #0D0D0D video     (make_video.py)
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

import themes as T

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BRAND = os.path.join(ROOT, "assets", "branding")
THUMBNAIL = os.path.join(BRAND, "thumbnail_1280x720.png")
THUMBS_GEN = os.path.join(ROOT, "assets", "thumbnails", "gen")  # per-theme clickable thumbnails
FRAME_16x9 = os.path.join(BRAND, "brand_16x9.png")
FRAME_9x16 = os.path.join(BRAND, "brand_9x16.png")

SHORT_SECONDS = 59
LONG_LOOP_SECONDS = 123  # ~2 min seamless loop, stream-looped to full length by ffmpeg


def run(cmd):
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True)


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


def produce_one(theme, fmt, out_dir, hours, seed):
    key = theme["key"]
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
    mv = os.path.join(HERE, "make_video.py")
    mm = os.path.join(HERE, "make_metadata.py")

    # Optional wellness frequency layers (Solfeggio/432 tone(s), brainwave beat,
    # bowl) plus tone-shaping (soft timbre, reverb wash, high-tone de-emphasis).
    freq = []
    if theme.get("tone"):
        freq += ["--tone", str(theme["tone"])]  # single Hz or a combo "432,528,741"
    if theme.get("beat"):
        freq += ["--beat", str(theme["beat"]), "--beat-type", theme.get("beat_type", "binaural")]
    if theme.get("bowl"):
        freq += ["--bowl"]
    if theme.get("tone_soft"):
        freq += ["--tone-soft"]
    if theme.get("reverb"):
        freq += ["--reverb", str(theme["reverb"])]
    if theme.get("tone_tilt"):
        freq += ["--tone-tilt", str(theme["tone_tilt"])]
    if theme.get("tone_gain"):
        freq += ["--tone-gain", str(theme["tone_gain"])]

    if fmt == "short":
        run([sys.executable, gta, "--theme", theme["synth"], "--seconds", str(SHORT_SECONDS),
             "--seed", str(seed), "--out", audio] + freq)
        run([sys.executable, mv, "--audio", audio, "--background", FRAME_9x16,
             "--duration-seconds", str(SHORT_SECONDS), "--fps", "24", "--out", video])
        run([sys.executable, mm, "--theme", key, "--format", "short", "--out", meta])
    else:
        run([sys.executable, gta, "--theme", theme["synth"], "--loop-seconds", str(LONG_LOOP_SECONDS),
             "--seed", str(seed), "--out", audio] + freq)
        run([sys.executable, mv, "--audio", audio, "--background", FRAME_16x9,
             "--duration-hours", str(hours), "--fps", "1", "--out", video])
        run([sys.executable, mm, "--theme", key, "--format", "long", "--hours", str(hours),
             "--out", meta])

    # Long-form gets the per-theme clickable thumbnail (scenic + headline).
    # Shorts use an auto-selected video frame — skip the custom thumbnail to save
    # API quota (thumbnails.set costs 50 units and Shorts barely use them).
    if fmt == "long":
        gen_thumb = os.path.join(THUMBS_GEN, f"{key}.png")
        src_thumb = gen_thumb if os.path.exists(gen_thumb) else THUMBNAIL
        shutil.copyfile(src_thumb, thumb)
        thumbnail_rel = os.path.relpath(thumb, ROOT)
    else:
        thumbnail_rel = None
    report = qc(fmt, video, hours)

    manifest = {
        "date": date.today().isoformat(),
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
                   help=f"produce the day's batch: {T.DAILY_COUNT} musics x (12h long + Short)")
    p.add_argument("--count", type=int, default=T.DAILY_COUNT,
                   help="number of musics per day for --daily")
    p.add_argument("--shorts", type=int, default=0,
                   help="test batch: produce Shorts for the first N of today's musics")
    p.add_argument("--longs", type=int, default=0,
                   help="test batch: produce long-forms for the first M of today's musics")
    p.add_argument("--slot", type=int, default=None,
                   help="produce ONE video: slot 0..(2*DAILY_COUNT-1) of today's rotation "
                        "(even=long, odd=short); used by the spaced daily schedule")
    p.add_argument("--hours", type=int, default=None,
                   help="override long-form length; default = per-theme map "
                        "(combos 3h, solo freq 8h, nature/music 10h)")
    p.add_argument("--seed", type=int, default=None, help="defaults to YYYYMMDD")
    p.add_argument("--out-dir", default="out")
    args = p.parse_args()

    if (not args.daily and not args.format and not (args.shorts or args.longs)
            and args.slot is None):
        p.error("give --daily, --format, --slot, or --shorts/--longs")

    seed = args.seed if args.seed is not None else int(date.today().strftime("%Y%m%d"))
    os.makedirs(args.out_dir, exist_ok=True)

    results = []
    if args.slot is not None:
        # One video per run, so the day's uploads are spread out (never overlap).
        # slots 0..LONGS_PER_DAY-1 = long-forms; remaining slots = Shorts.
        # Each slot maps to a different music.
        selection = T.daily_selection(count=T.DAILY_COUNT)
        theme = selection[args.slot % len(selection)]
        fmt = "long" if args.slot < T.LONGS_PER_DAY else "short"
        print(f"Slot {args.slot}: {theme['key']} {fmt}")
        results.append(produce_one(theme, fmt, args.out_dir, args.hours, seed + args.slot))
    elif args.shorts or args.longs:
        # Custom test batch: M long-forms + N Shorts from today's rotation.
        need = max(args.shorts, args.longs, 1)
        selection = T.daily_selection(count=max(need, T.DAILY_COUNT))
        print(f"Test batch: {args.longs} long(s) + {args.shorts} short(s) from: "
              + ", ".join(t["key"] for t in selection[:need]))
        for i in range(args.longs):
            results.append(produce_one(selection[i], "long", args.out_dir, args.hours,
                                       seed + i * 10))
        for i in range(args.shorts):
            results.append(produce_one(selection[i], "short", args.out_dir, args.hours,
                                       seed + i * 10 + 1))
    elif args.daily:
        # LONGS_PER_DAY long-forms + SHORTS_PER_DAY Shorts, each a different music.
        selection = T.daily_selection(count=T.DAILY_COUNT)
        longs = selection[:T.LONGS_PER_DAY]
        shorts = selection[T.LONGS_PER_DAY:T.LONGS_PER_DAY + T.SHORTS_PER_DAY]
        print("Daily batch: " + ", ".join(t["key"] for t in longs) + " (long) + "
              + ", ".join(t["key"] for t in shorts) + " (short)")
        for i, theme in enumerate(longs):
            results.append(produce_one(theme, "long", args.out_dir, args.hours, seed + i))
        for i, theme in enumerate(shorts):
            results.append(produce_one(theme, "short", args.out_dir, args.hours, seed + 100 + i))
    else:
        theme = T.resolve_theme(args.theme)
        formats = ["short", "long"] if args.format == "both" else [args.format]
        results = [produce_one(theme, f, args.out_dir, args.hours, seed + i)
                   for i, f in enumerate(formats)]

    failed = [r for r in results if r["status"] != "queued"]
    if failed:
        print(f"\n{len(failed)} of {len(results)} asset(s) failed QC.")
        sys.exit(1)
    print(f"\nAll {len(results)} asset(s) queued.")


if __name__ == "__main__":
    main()
