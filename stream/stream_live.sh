#!/usr/bin/env bash
# Stream the black branded frame + audio to YouTube Live 24/7.
#
#   stream_live.sh --theme rain      -> streams just the "rain" loop (one channel)
#   stream_live.sh                    -> streams all musics on rotation (playlist)
#
# The audio loops forever; the still image is a low-fps video (ultrafast preset,
# tiny CPU) so one small VM can run several theme streams at once. systemd
# restarts this on any exit, so a dropped connection self-heals in seconds.
#
# STREAM_KEY must be in the environment (systemd loads it from the per-theme
# EnvironmentFile). Never commit the key.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
FRAME="${FRAME:-$REPO/assets/branding/brand_16x9.png}"
AUDIO_DIR="${AUDIO_DIR:-$REPO/stream/audio}"
RTMP_URL="${RTMP_URL:-rtmp://a.rtmp.youtube.com/live2}"

THEME=""
if [ "${1:-}" = "--theme" ] && [ -n "${2:-}" ]; then
  THEME="$2"
fi

: "${STREAM_KEY:?STREAM_KEY not set — put STREAM_KEY=... in the theme EnvironmentFile}"
[ -f "$AUDIO_DIR/playlist.txt" ] || bash "$REPO/stream/refresh_audio.sh"

# Choose the audio input: a single theme loop, or the rotating playlist.
if [ -n "$THEME" ]; then
  AUDIO_FILE="$AUDIO_DIR/${THEME}.wav"
  [ -f "$AUDIO_FILE" ] || { echo "No audio for theme '$THEME' in $AUDIO_DIR"; exit 1; }
  AUDIO_INPUT=(-re -stream_loop -1 -i "$AUDIO_FILE")
else
  AUDIO_INPUT=(-re -stream_loop -1 -f concat -safe 0 -i "$AUDIO_DIR/playlist.txt")
fi

exec ffmpeg -hide_banner -loglevel warning -fflags +genpts \
  -re -loop 1 -framerate 15 -i "$FRAME" \
  "${AUDIO_INPUT[@]}" \
  -c:v libx264 -preset ultrafast -tune stillimage -pix_fmt yuv420p \
  -r 15 -g 30 -keyint_min 30 -b:v 2500k -maxrate 2500k -bufsize 5000k \
  -c:a aac -b:a 160k -ar 44100 \
  -f flv "$RTMP_URL/$STREAM_KEY"
