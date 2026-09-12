#!/usr/bin/env python3
"""
Produce the day's video asset(s) end-to-end for the "Aether & Ash" channel.

For a chosen theme (or the date-based rotation) and format, this:
  1. synthesizes theme audio            (../scripts/generate_theme_audio.py)
  2. renders a branded, procedurally-animated video (make_animated_video.py)
  3. assigns the per-theme thumbnail     (assets/aether/thumbnails/gen/<key>.png)
  4. writes SEO metadata                 (make_metadata.py)
  5. runs QC on the durations            (59s Short / 870s (14:30) feature)
  6. writes a manifest and marks it "queued" for publishing

Nothing is uploaded here. Publishing is a separate, credentialed step.

Usage:
    python produce.py --format short                 # today's theme, 59s Short
    python produce.py --format long                   # today's theme, 14:30 feature
    python produce.py --theme void_drone --format both
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
SHARED = os.path.join(ROOT, "scripts")  # engine shared with the "Meditated Sleeping" channel
BRAND = os.path.join(ROOT, "assets", "aether", "branding")
THUMBNAIL = os.path.join(BRAND, "thumbnail_1280x720.png")
THUMBS_GEN = os.path.join(ROOT, "assets", "aether", "thumbnails", "gen")

SHORT_SECONDS = 59


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


def qc(fmt, video_path):
    dur = ffprobe_duration(video_path)
    res = ffprobe_resolution(video_path)
    problems = []
    if fmt == "short":
        if abs(dur - SHORT_SECONDS) > 1.0:
            problems.append(f"Short duration {dur:.1f}s is not ~{SHORT_SECONDS}s")
        if res != "1080x1920":
            problems.append(f"Short resolution {res} is not 1080x1920 (vertical)")
    else:
        if abs(dur - T.FEATURE_SECONDS) > 5.0:
            problems.append(f"Feature duration {dur:.1f}s is not ~{T.FEATURE_SECONDS}s")
        if res != "1920x1080":
            problems.append(f"Feature resolution {res} is not 1920x1080")
    return {"duration_sec": round(dur, 2), "resolution": res, "problems": problems}


def produce_one(theme, fmt, out_dir, seed):
    key = theme["key"]
    duration = SHORT_SECONDS if fmt == "short" else T.FEATURE_SECONDS
    width, height = (1080, 1920) if fmt == "short" else (1920, 1080)
    color = T.ACCENT_COLORS.get(key, "3c4b5f")

    stem = os.path.join(out_dir, f"{key}_{fmt}")
    audio = f"{stem}_audio.wav"
    video = f"{stem}.mp4"
    thumb = f"{stem}_thumb.png"
    meta = f"{stem}_meta.json"

    gta = os.path.join(SHARED, "generate_theme_audio.py")
    mav = os.path.join(HERE, "make_animated_video.py")
    mm = os.path.join(HERE, "make_metadata.py")

    # Optional wellness frequency layers (tone/beat) plus tone-shaping.
    freq = T.synth_args(theme)

    run([sys.executable, gta, "--theme", theme["synth"], "--seconds", str(duration),
         "--seed", str(seed), "--out", audio] + freq)
    run([sys.executable, mav, "--audio", audio, "--duration-seconds", str(duration),
         "--width", str(width), "--height", str(height), "--color", color,
         "--seed", str(seed), "--out", video])
    run([sys.executable, mm, "--theme", key, "--format", fmt, "--out", meta])

    # Long-form (feature) gets the per-theme clickable thumbnail. Shorts use
    # an auto-selected video frame -- skip the custom thumbnail to save quota.
    if fmt == "long":
        gen_thumb = os.path.join(THUMBS_GEN, f"{key}.png")
        src_thumb = gen_thumb if os.path.exists(gen_thumb) else THUMBNAIL
        shutil.copyfile(src_thumb, thumb)
        thumbnail_rel = os.path.relpath(thumb, ROOT)
    else:
        thumbnail_rel = None
    report = qc(fmt, video)

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
                   help=f"produce the day's batch: {T.DAILY_COUNT} videos "
                        f"({T.LONGS_PER_DAY} feature + {T.SHORTS_PER_DAY} short)")
    p.add_argument("--count", type=int, default=T.DAILY_COUNT,
                   help="number of musics per day for --daily")
    p.add_argument("--shorts", type=int, default=0,
                   help="test batch: produce Shorts for the first N of today's musics")
    p.add_argument("--longs", type=int, default=0,
                   help="test batch: produce features for the first M of today's musics")
    p.add_argument("--slot", type=int, default=None,
                   help="produce ONE video: slot 0..(DAILY_COUNT-1) of today's rotation "
                        "(slots < LONGS_PER_DAY = feature, rest = short)")
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
        selection = T.daily_selection(count=T.DAILY_COUNT)
        theme = selection[args.slot % len(selection)]
        fmt = "long" if args.slot < T.LONGS_PER_DAY else "short"
        print(f"Slot {args.slot}: {theme['key']} {fmt}")
        results.append(produce_one(theme, fmt, args.out_dir, seed + args.slot))
    elif args.shorts or args.longs:
        need = max(args.shorts, args.longs, 1)
        selection = T.daily_selection(count=max(need, T.DAILY_COUNT))
        print(f"Test batch: {args.longs} feature(s) + {args.shorts} short(s) from: "
              + ", ".join(t["key"] for t in selection[:need]))
        for i in range(args.longs):
            results.append(produce_one(selection[i], "long", args.out_dir, seed + i * 10))
        for i in range(args.shorts):
            results.append(produce_one(selection[i], "short", args.out_dir, seed + i * 10 + 1))
    elif args.daily:
        selection = T.daily_selection(count=T.DAILY_COUNT)
        longs = selection[:T.LONGS_PER_DAY]
        shorts = selection[T.LONGS_PER_DAY:T.LONGS_PER_DAY + T.SHORTS_PER_DAY]
        print("Daily batch: " + ", ".join(t["key"] for t in longs) + " (feature) + "
              + ", ".join(t["key"] for t in shorts) + " (short)")
        for i, theme in enumerate(longs):
            results.append(produce_one(theme, "long", args.out_dir, seed + i))
        for i, theme in enumerate(shorts):
            results.append(produce_one(theme, "short", args.out_dir, seed + 100 + i))
    else:
        theme = T.resolve_theme(args.theme)
        formats = ["short", "long"] if args.format == "both" else [args.format]
        results = [produce_one(theme, f, args.out_dir, seed + i)
                   for i, f in enumerate(formats)]

    failed = [r for r in results if r["status"] != "queued"]
    if failed:
        print(f"\n{len(failed)} of {len(results)} asset(s) failed QC.")
        sys.exit(1)
    print(f"\nAll {len(results)} asset(s) queued.")


if __name__ == "__main__":
    main()
