#!/usr/bin/env python3
"""
Upload a finished video to YouTube via the Data API v3, using a long-lived
refresh token (see references/youtube_oauth.md for how to obtain one and keep
it from expiring).

Requires: google-auth, google-auth-oauthlib, google-api-python-client
Requires env vars (populate from GitHub Secrets in CI):
    YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN

Usage:
    python upload_youtube.py --video final.mp4 --thumbnail thumbnail.png \
        --title "Deep Sleep Music - 8 Hours Black Screen" \
        --description "Ambient calm music for sleep and focus." \
        --tags sleep,ambient,calm,black screen
"""
import argparse
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_service():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    return build("youtube", "v3", credentials=creds)


def upload_video(youtube, video_path, title, description, tags, category_id="10", privacy="public"):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,  # 10 = Music
        },
        "status": {"privacyStatus": privacy},
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")
    return response["id"]


def set_thumbnail(youtube, video_id, thumbnail_path):
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(thumbnail_path),
    ).execute()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--video", required=True)
    p.add_argument("--thumbnail", default=None)
    p.add_argument("--title", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--tags", default="", help="comma-separated")
    p.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"])
    args = p.parse_args()

    youtube = get_service()
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    video_id = upload_video(youtube, args.video, args.title, args.description, tags, privacy=args.privacy)
    print(f"Uploaded video ID: {video_id}")

    if args.thumbnail:
        set_thumbnail(youtube, video_id, args.thumbnail)
        print("Thumbnail set")


if __name__ == "__main__":
    main()
