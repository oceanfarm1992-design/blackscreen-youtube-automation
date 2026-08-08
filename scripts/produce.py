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
        if not (8 * 3600 <= dur <= 12 * 3600):
            problems.append(f"Long duration {dur/3600:.2f}h is outside the 8-12h window")
        if res != "1920x1080":
            problems.append(f"Long resolution {res} is not 1920x1080")
    return {"duration_sec": round(dur, 2), "resolution": res, "problems": problems}


def produce_one(theme, fmt, out_dir, hours, seed):
    key = theme["key"]
    stem = os.path.join(out_dir, f"{key}_{fmt}")
    audio = f"{stem}_audio.wav"
    video = f"{stem}.mp4"
    thumb = f"{stem}_thumb.png"
    meta = f"{stem}_meta.json"

    gta = os.path.join(HERE, "generate_theme_audio.py")
    mv = os.path.join(HERE, "make_video.py")
    mm = os.path.join(HERE, "make_metadata.py")

    if fmt == "short":
        run([sys.executable, gta, "--theme", theme["synth"], "--seconds", str(SHORT_SECONDS),
             "--seed", str(seed), "--out", audio])
        run([sys.executable, mv, "--audio", audio, "--background", FRAME_9x16,
             "--duration-seconds", str(SHORT_SECONDS), "--fps", "24", "--out", video])
        run([sys.executable, mm, "--theme", key, "--format", "short", "--out", meta])
    else:
        run([sys.executable, gta, "--theme", theme["synth"], "--loop-seconds", str(LONG_LOOP_SECONDS),
             "--seed", str(seed), "--out", audio])
        run([sys.executable, mv, "--audio", audio, "--background", FRAME_16x9,
             "--duration-hours", str(hours), "--fps", "1", "--out", video])
        run([sys.executable, mm, "--theme", key, "--format", "long", "--hours", str(hours),
             "--out", meta])

    shutil.copyfile(THUMBNAIL, thumb)
    report = qc(fmt, video, hours)

    manifest = {
        "date": date.today().isoformat(),
        "theme": key,
        "theme_name": theme["name"],
        "format": fmt,
        "video": os.path.relpath(video, ROOT),
        "thumbnail": os.path.relpath(thumb, ROOT),
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
    p.add_argument("--hours", type=int, default=T.LONG_HOURS_DEFAULT)
    p.add_argument("--seed", type=int, default=None, help="defaults to YYYYMMDD")
    p.add_argument("--out-dir", default="out")
    args = p.parse_args()

    if not args.daily and not args.format:
        p.error("either --daily or --format is required")

    seed = args.seed if args.seed is not None else int(date.today().strftime("%Y%m%d"))
    os.makedirs(args.out_dir, exist_ok=True)

    results = []
    if args.daily:
        # N different musics per day (DAILY_COUNT); each gets a 12h long + a Short.
        selection = T.daily_selection(count=args.count)
        print(f"Daily batch ({len(selection)} musics x long+short): "
              + ", ".join(t["key"] for t in selection))
        for i, theme in enumerate(selection):
            for j, fmt in enumerate(["long", "short"]):
                results.append(produce_one(theme, fmt, args.out_dir, args.hours,
                                           seed + i * 10 + j))
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
