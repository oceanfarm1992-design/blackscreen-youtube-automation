#!/usr/bin/env bash
# Stream the black branded frame + rotating audio loops to YouTube Live 24/7.
#
# The audio playlist (stream/audio/playlist.txt) is looped forever; the still
# image is looped as a low-fps video (near-zero CPU). systemd restarts this on
# any exit, so a dropped connection self-heals within seconds.
#
# Requires STREAM_KEY in the environment (systemd loads it from
# /etc/youtube-live.env). Never commit the key.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
FRAME="${FRAME:-$REPO/assets/branding/brand_16x9.png}"
AUDIO_DIR="${AUDIO_DIR:-$REPO/stream/audio}"
PLAYLIST="$AUDIO_DIR/playlist.txt"
RTMP_URL="${RTMP_URL:-rtmp://a.rtmp.youtube.com/live2}"

: "${STREAM_KEY:?STREAM_KEY not set — put STREAM_KEY=... in /etc/youtube-live.env}"
[ -f "$PLAYLIST" ] || bash "$REPO/stream/refresh_audio.sh"

exec ffmpeg -hide_banner -loglevel warning -fflags +genpts \
  -re -loop 1 -framerate 15 -i "$FRAME" \
  -re -stream_loop -1 -f concat -safe 0 -i "$PLAYLIST" \
  -c:v libx264 -preset veryfast -tune stillimage -pix_fmt yuv420p \
  -r 15 -g 30 -keyint_min 30 -b:v 2500k -maxrate 2500k -bufsize 5000k \
  -c:a aac -b:a 160k -ar 44100 \
  -f flv "$RTMP_URL/$STREAM_KEY"
