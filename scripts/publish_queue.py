#!/usr/bin/env python3
"""
Upload every produced asset in the output dir to YouTube (PUBLIC by default).

Reads the *_manifest.json files written by produce.py, and for each with
status "queued", uploads the video + metadata + thumbnail. Pass --privacy to
upload as private or unlisted instead.

Requires the same env vars as upload_youtube.py (YT_CLIENT_ID/SECRET/REFRESH_TOKEN).

Usage:
    python publish_queue.py --out-dir out                    # public
    python publish_queue.py --out-dir out --privacy private  # queue for review
"""
import argparse
import glob
import json
import os
import sys

import upload_youtube as U

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", default="out")
    p.add_argument("--privacy", default="public", choices=["private", "unlisted", "public"])
    args = p.parse_args()

    manifests = sorted(glob.glob(os.path.join(args.out_dir, "*_manifest.json")))
    if not manifests:
        print(f"No manifests found in {args.out_dir}; nothing to publish.")
        return

    youtube = U.get_service()
    for mpath in manifests:
        man = json.load(open(mpath, encoding="utf-8"))
        if man.get("status") != "queued":
            print(f"Skipping {os.path.basename(mpath)} (status={man.get('status')})")
            continue

        meta = json.load(open(os.path.join(ROOT, man["metadata"]), encoding="utf-8"))
        video = os.path.join(ROOT, man["video"])
        thumb = os.path.join(ROOT, man["thumbnail"])

        print(f"Uploading {man['theme']} {man['format']} as {args.privacy}: {meta['title']}")
        video_id = U.upload_video(
            youtube, video, meta["title"], meta["description"], meta.get("tags", []),
            category_id=meta.get("categoryId", "10"), privacy=args.privacy,
        )
        # Custom thumbnails require a verified channel (youtube.com/verify). If that's
        # not enabled the API returns 403 — don't fail the run over an optional extra;
        # the branded video frame already serves as the auto-thumbnail.
        try:
            U.set_thumbnail(youtube, video_id, thumb)
            man["thumbnail_status"] = "set"
        except Exception as e:
            man["thumbnail_status"] = "skipped"
            print(f"  ! custom thumbnail not set (needs a verified channel): {e}")

        man["video_id"] = video_id
        man["status"] = "uploaded_private" if args.privacy == "private" else f"uploaded_{args.privacy}"
        with open(mpath, "w", encoding="utf-8") as f:
            json.dump(man, f, ensure_ascii=False, indent=2)
        print(f"  -> https://youtu.be/{video_id}  (status: {man['status']})")


if __name__ == "__main__":
    main()
