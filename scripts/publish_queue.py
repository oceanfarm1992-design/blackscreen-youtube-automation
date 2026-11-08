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

import themes as T
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

    # One project, one OAuth client for every upload (YouTube API policy: no
    # extra projects for extra quota -- see upload_youtube.SHARED_CLIENT).
    services = {}

    def service_for(fmt):
        if "YT" not in services:
            services["YT"] = U.get_service("YT")
        return services["YT"]

    # The channel's recent titles: a title already there is skipped, never re-posted.
    existing = []  # [set | None], read lazily on the first upload

    def already_on_channel(youtube, title):
        if not existing:
            existing.append(U.recent_upload_titles(youtube))
        return U.is_duplicate_title(existing[0], title)

    # Auto-playlists: long-forms are added to their sub-niche playlist (50
    # units/add) through the same single project. Needs the broader "youtube"
    # scope on the token -- without it the API returns 403 and we just skip,
    # never failing the upload.
    playlist_ids = {}  # title -> id, resolved once per run

    def add_long_to_playlist(man, video_id):
        pl = T.playlist_for(man["theme"])
        if not pl:
            man["playlist_status"] = "skipped"
            return
        try:
            svc = service_for("long")
            if pl["title"] not in playlist_ids:
                playlist_ids[pl["title"]] = U.find_or_create_playlist(
                    svc, pl["title"], pl["description"])
            U.add_to_playlist(svc, playlist_ids[pl["title"]], video_id)
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
        youtube = service_for(man["format"])

        if already_on_channel(youtube, meta["title"]):
            print(f"Skipping {man['theme']} {man['format']}: '{meta['title']}' is already "
                  "on the channel")
            man["status"] = "skipped_duplicate"
            with open(mpath, "w", encoding="utf-8") as f:
                json.dump(man, f, ensure_ascii=False, indent=2)
            continue

        print(f"Uploading {man['theme']} {man['format']} as {args.privacy}: {meta['title']}")
        video_id = U.upload_video(
            youtube, video, meta["title"], meta["description"], meta.get("tags", []),
            category_id=meta.get("categoryId", "10"), privacy=args.privacy,
            synthetic=bool(meta.get("containsSyntheticMedia")),
        )
        if existing[0] is not None:
            existing[0].add(U._norm_title(meta["title"]))
        # Shorts have no custom thumbnail (thumbnail=None) — skip to save API quota.
        # Custom thumbnails also require a verified channel; if not enabled the API
        # returns 403 — don't fail the run over an optional extra.
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
