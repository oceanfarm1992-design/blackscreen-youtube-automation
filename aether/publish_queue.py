#!/usr/bin/env python3
"""
Upload every produced "Aether & Ash" asset in the output dir to YouTube
(PUBLIC by default).

Reads the *_manifest.json files written by produce.py, and for each with
status "queued", uploads the video + metadata + thumbnail. Pass --privacy to
upload as private or unlisted instead.

At this channel's launch cadence (2 long + 1 short/day = ~4,950 units), a
single OAuth/Cloud project is enough -- unlike the "Meditated Sleeping"
channel, there is no second "Shorts" project to route around.

Requires env vars: AETHER_YT_CLIENT_ID, AETHER_YT_CLIENT_SECRET,
AETHER_YT_REFRESH_TOKEN (see scripts/upload_youtube.py / get_refresh_token.py).

Usage:
    python publish_queue.py --out-dir out                    # public
    python publish_queue.py --out-dir out --privacy private  # queue for review
"""
import argparse
import glob
import json
import os
import sys

import themes as T

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import upload_youtube as U  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SECRET_PREFIX = "AETHER_YT"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", default="out")
    p.add_argument("--privacy", default="public", choices=["private", "unlisted", "public"])
    args = p.parse_args()

    manifests = sorted(glob.glob(os.path.join(args.out_dir, "*_manifest.json")))
    if not manifests:
        print(f"No manifests found in {args.out_dir}; nothing to publish.")
        return

    youtube = U.get_service(SECRET_PREFIX)
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
            category_id=meta.get("categoryId", "10"), privacy=args.privacy,
        )
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
        man["status"] = "uploaded_private" if args.privacy == "private" else f"uploaded_{args.privacy}"
        with open(mpath, "w", encoding="utf-8") as f:
            json.dump(man, f, ensure_ascii=False, indent=2)
        print(f"  -> https://youtu.be/{video_id}  (status: {man['status']})")


if __name__ == "__main__":
    main()
