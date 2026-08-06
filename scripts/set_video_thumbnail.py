#!/usr/bin/env python3
"""
Set a custom thumbnail on an existing YouTube video.

Requires a verified channel (youtube.com/verify) and the same env vars as
upload_youtube.py (YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN).

Usage:
    python set_video_thumbnail.py --video-id F9JbJA0zQvo
    python set_video_thumbnail.py --video-id ABC --thumbnail path/to/thumb.png
"""
import argparse

import upload_youtube as U


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--video-id", required=True)
    p.add_argument("--thumbnail", default="assets/branding/thumbnail_1280x720.png")
    args = p.parse_args()

    youtube = U.get_service()
    U.set_thumbnail(youtube, args.video_id, args.thumbnail)
    print(f"Thumbnail set on https://youtu.be/{args.video_id}")


if __name__ == "__main__":
    main()
