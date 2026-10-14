#!/bin/bash
set -euo pipefail
echo "=== Meditated Sleeping - Full Server Setup ==="

# Stream keys: prompted for (hidden) when not passed as arguments. Passing them
# as arguments also works but leaves them in your shell history.
K1="${1:-}" K2="${2:-}" K3="${3:-}" K4="${4:-}" K5="${5:-}"
if [ -z "$K1" ]; then
  read -rsp "Stream key for sleeping:  " K1; echo
  read -rsp "Stream key for solfeggio: " K2; echo
  read -rsp "Stream key for forest:    " K3; echo
  read -rsp "Stream key for romantic:  " K4; echo
  read -rsp "Stream key for rain:      " K5; echo
fi
if [ -z "$K1" ] || [ -z "$K2" ] || [ -z "$K3" ] || [ -z "$K4" ] || [ -z "$K5" ]; then
  echo "Need all 5 stream keys (sleeping, solfeggio, forest, romantic, rain)."
  exit 1
fi

cd /root/blackscreen-youtube-automation

echo "[1/6] Adding swap space (prevents out-of-memory)..."
if [ ! -f /swapfile ]; then
  fallocate -l 2G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
  echo "  2GB swap created."
else
  swapon /swapfile 2>/dev/null || true
  echo "  Swap already exists."
fi

echo "[2/6] Creating streams.conf..."
printf '%s\n' \
  "sleeping|sleeping_loop.wav|${K1}|Deep Sleep Music 24/7" \
  "solfeggio|solfeggio_heal_loop.wav|${K2}|Solfeggio Healing 24/7" \
  "forest|forest_loop.wav|${K3}|Forest Night Sounds 24/7" \
  "romantic|romantic_loop.wav|${K4}|Romantic Piano 24/7" \
  "rain|rain_loop.wav|${K5}|Rain Sounds 24/7" \
  > livestream/streams.conf
chmod 600 livestream/streams.conf  # holds the stream keys
echo "  Done! 5 streams configured."

echo "[3/6] Setting up directories..."
mkdir -p livestream/audio livestream/pids livestream/logs livestream/assets
cp assets/branding/brand_16x9.png livestream/assets/
echo "  Done!"

echo "[4/6] Generating 5-minute audio loops (ffmpeg loops them forever)..."
THEMES="sleeping solfeggio_heal forest romantic rain rain_drops 528hz_sleep rooftop_rain"
for theme in $THEMES; do
  out="livestream/audio/${theme}_loop.wav"
  if [ -f "$out" ]; then
    echo "  [$theme] already exists, skipping"
    continue
  fi
  echo "  [$theme] generating..."
  synth=$(python3 -c "import sys; sys.path.insert(0,'scripts'); import themes as T; print(T.theme_by_key('$theme')['synth'])")
  args=$(python3 -c "import sys; sys.path.insert(0,'scripts'); import themes as T; print(' '.join(T.synth_args(T.theme_by_key('$theme'))))")
  python3 scripts/generate_theme_audio.py --theme "$synth" --loop-seconds 300 --seed 55555 --out "$out" $args
  echo "  [$theme] done"
done
echo "  All audio loops ready!"

echo "[5/6] Starting all streams..."
bash livestream/stream_manager.sh start

echo "[6/6] Setting up auto-restart on reboot..."
# Replace (never append) the entry, so re-running this script can't stack up
# duplicate @reboot lines that would start two ffmpeg pushes per stream key.
REBOOT_LINE="@reboot cd /root/blackscreen-youtube-automation && bash livestream/stream_manager.sh start"
(crontab -l 2>/dev/null | grep -vF "livestream/stream_manager.sh start"; echo "$REBOOT_LINE") | crontab -

echo ""
echo "=== ALL DONE! 5 streams running 24/7 ==="
echo "Check status: bash livestream/stream_manager.sh status"
