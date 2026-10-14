#!/usr/bin/env python3
"""
Give a channel's EXISTING feature videos their custom thumbnails -- for
features uploaded before the channel was phone-verified (YouTube refused the
thumbnail at upload time, so those videos show an auto-picked frame).

For each long video (> 60s) on the channel it finds the theme from the title,
reads "Vol. N" from the title if present, renders that theme's thumbnail
exactly as a new upload would (channel_kit.render_thumbnail, seeded by the
video id so each video gets its own), and sets it. Shorts are skipped:
YouTube's Shorts feed doesn't show custom thumbnails.

Dry run by default -- prints what it would change and sets nothing.
Needs the channel's <FOLDER>_YT_* secrets, so it normally runs in CI via
.github/workflows/set-thumbnail.yml.

Usage:
    python scripts/backfill_thumbnails.py --channel aether            # dry run
    python scripts/backfill_thumbnails.py --channel aether --apply
    python scripts/backfill_thumbnails.py --channel hearth --apply --video-id B9conZk53jo
"""
import argparse
import os
import re
import sys
import zlib

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS)
CHANNELS = ["aether", "sanctuary", "hearth", "horizon", "resonance", "manor"]


def iso_seconds(duration):
    """'PT14M30S' -> 870."""
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return ((d * 24 + h) * 60 + mi) * 60 + s


def channel_videos(youtube):
    """Every video on the authenticated channel: (id, title, seconds)."""
    me = youtube.channels().list(part="contentDetails", mine=True).execute()
    uploads = me["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, page = [], None
    while True:
        res = youtube.playlistItems().list(part="contentDetails", playlistId=uploads,
                                           maxResults=50, pageToken=page).execute()
        ids += [it["contentDetails"]["videoId"] for it in res["items"]]
        page = res.get("nextPageToken")
        if not page:
            break
    for i in range(0, len(ids), 50):
        res = youtube.videos().list(part="snippet,contentDetails", id=",".join(ids[i:i + 50])).execute()
        for v in res["items"]:
            yield v["id"], v["snippet"]["title"], iso_seconds(v["contentDetails"]["duration"])


def theme_for_title(T, title):
    """The theme whose name the title starts with (longest match wins)."""
    hits = [t for t in T.THEMES if title.startswith(t["name"])]
    return max(hits, key=lambda t: len(t["name"])) if hits else None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser()
    p.add_argument("--channel", required=True, choices=CHANNELS)
    p.add_argument("--apply", action="store_true", help="actually set thumbnails (default: dry run)")
    p.add_argument("--video-id", default=None, help="only this video")
    p.add_argument("--out-dir", default="out_thumbs")
    args = p.parse_args()

    sys.path.insert(0, os.path.join(ROOT, args.channel))
    sys.path.insert(1, SCRIPTS)
    import themes as T  # this channel's themes.py
    from make_thumbnails import STYLE

    import channel_kit as K
    import upload_youtube as U

    ch = K.Channel(T)
    youtube = U.get_service(ch.secret_prefix)
    os.makedirs(args.out_dir, exist_ok=True)

    done = skipped = failed = 0
    for vid, title, secs in channel_videos(youtube):
        if args.video_id and vid != args.video_id:
            continue
        if secs <= 60:
            continue  # a Short
        theme = theme_for_title(T, title)
        if not theme:
            print(f"  ? {vid}  no matching theme: {title}")
            skipped += 1
            continue
        m = re.search(r"\bVol\. (\d+)\b", title)
        volume = int(m.group(1)) if m else None
        out = os.path.join(args.out_dir, f"{vid}.png")
        K.render_thumbnail(T, STYLE, theme["key"], out, seed=zlib.crc32(vid.encode()), volume=volume)
        if not args.apply:
            print(f"  would set  {vid}  {theme['key']:22s} vol={volume or '-'}  {title[:60]}")
            done += 1
            continue
        try:
            U.set_thumbnail(youtube, vid, out)
            print(f"  set        {vid}  {theme['key']:22s} vol={volume or '-'}  https://youtu.be/{vid}")
            done += 1
        except Exception as e:
            print(f"  ! failed   {vid}: {e}")
            failed += 1

    verb = "set" if args.apply else "would set (dry run)"
    print(f"\n{T.BRAND_NAME}: {done} thumbnail(s) {verb}, {skipped} unmatched, {failed} failed.")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
