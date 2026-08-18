#!/bin/bash
# Generate long audio loops for each live stream theme.
# Run this on the Hetzner server after deploying the project.
# Each loop is 30 minutes — ffmpeg will loop it infinitely for the 24/7 stream.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
AUDIO_DIR="$SCRIPT_DIR/audio"

mkdir -p "$AUDIO_DIR"

# Themes for live streams (match your streams.conf names to these)
THEMES=("rain" "sleeping" "solfeggio_heal" "romantic" "forest" "rain_drops" "528hz_sleep" "rooftop_rain")

echo "Generating 30-minute audio loops for live streams..."
echo "This takes ~5 minutes per theme."
echo ""

for theme in "${THEMES[@]}"; do
    out="$AUDIO_DIR/${theme}_loop.wav"
    if [ -f "$out" ]; then
        echo "  [$theme] already exists, skipping"
        continue
    fi

    echo "  [$theme] generating 30-minute loop..."

    # Check if AI clips exist for hybrid audio
    clips_dir="$PROJECT_DIR/assets/clips/$theme"
    if [ -d "$clips_dir" ] && ls "$clips_dir"/*.wav 1>/dev/null 2>&1; then
        python3 "$PROJECT_DIR/scripts/build_long_audio.py" \
            --theme "$theme" --seconds 1800 --seed 55555 --out "$out"
        echo "  [$theme] done (hybrid AI + procedural)"
    else
        python3 "$PROJECT_DIR/scripts/generate_theme_audio.py" \
            --theme "$(python3 -c "import sys; sys.path.insert(0,'$PROJECT_DIR/scripts'); import themes as T; print(T.theme_by_key('$theme')['synth'])")" \
            --loop-seconds 1800 --seed 55555 --out "$out" \
            $(python3 -c "import sys; sys.path.insert(0,'$PROJECT_DIR/scripts'); import themes as T; print(' '.join(T.synth_args(T.theme_by_key('$theme'))))")
        echo "  [$theme] done (procedural)"
    fi
done

echo ""
echo "All audio loops ready in: $AUDIO_DIR"
ls -lh "$AUDIO_DIR"/*.wav 2>/dev/null
