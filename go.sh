#!/bin/bash
set -euo pipefail
echo "=== Meditated Sleeping - Full Server Setup ==="

K1="${1:-}" K2="${2:-}" K3="${3:-}" K4="${4:-}" K5="${5:-}"
if [ -z "$K1" ] || [ -z "$K5" ]; then
  echo "Usage: bash go.sh SLEEP_KEY SOLF_KEY FOREST_KEY ROMANTIC_KEY RAIN_KEY"
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
(crontab -l 2>/dev/null; echo "@reboot cd /root/blackscreen-youtube-automation && bash livestream/stream_manager.sh start") | crontab -

echo ""
echo "=== ALL DONE! 5 streams running 24/7 ==="
echo "Check status: bash livestream/stream_manager.sh status"
