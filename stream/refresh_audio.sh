#!/usr/bin/env bash
# Regenerate the rotating audio loops for the 24/7 live stream.
#
# Produces one seamless loop per music into stream/audio/, then writes an ffmpeg
# concat playlist listing them in order. Run once by setup.sh and then daily by
# cron so the stream stays original (fresh seeds each day) instead of looping the
# exact same file forever.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
AUDIO_DIR="${AUDIO_DIR:-$REPO/stream/audio}"
LOOP_SECONDS="${LOOP_SECONDS:-600}"   # 10-min seamless loop per music
THEMES=(rain waterfall forest sleeping indian romantic romantic_night)

mkdir -p "$AUDIO_DIR"
SEED="$(date +%Y%m%d)"

i=0
for th in "${THEMES[@]}"; do
  echo ">> generating $th loop (${LOOP_SECONDS}s, seed $((SEED + i)))"
  python3 "$REPO/scripts/generate_theme_audio.py" \
    --theme "$th" --loop-seconds "$LOOP_SECONDS" \
    --seed "$((SEED + i))" --out "$AUDIO_DIR/${th}.wav"
  i=$((i + 1))
done

# ffmpeg concat playlist (absolute paths, in rotation order)
PLAYLIST="$AUDIO_DIR/playlist.txt"
: > "$PLAYLIST"
for th in "${THEMES[@]}"; do
  echo "file '$AUDIO_DIR/${th}.wav'" >> "$PLAYLIST"
done

echo "Wrote ${#THEMES[@]} loops + playlist -> $AUDIO_DIR"
