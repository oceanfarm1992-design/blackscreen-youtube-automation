#!/bin/bash
set -euo pipefail
echo "=== Meditated Sleeping - Full Server Setup ==="

K1="${1:-}" K2="${2:-}" K3="${3:-}" K4="${4:-}" K5="${5:-}"
if [ -z "$K1" ] || [ -z "$K5" ]; then
  echo "Usage: bash go.sh SLEEP_KEY SOLF_KEY FOREST_KEY ROMANTIC_KEY RAIN_KEY"
  exit 1
fi

cd /root/blackscreen-youtube-automation

echo "[1/5] Creating streams.conf..."
printf '%s\n' \
  "sleeping|sleeping_loop.wav|${K1}|Deep Sleep Music 24/7" \
  "solfeggio|solfeggio_heal_loop.wav|${K2}|Solfeggio Healing 24/7" \
  "forest|forest_loop.wav|${K3}|Forest Night Sounds 24/7" \
  "romantic|romantic_loop.wav|${K4}|Romantic Piano 24/7" \
  "rain|rain_loop.wav|${K5}|Rain Sounds 24/7" \
  > livestream/streams.conf
echo "  Done! 5 streams configured."

echo "[2/5] Setting up directories..."
mkdir -p livestream/audio livestream/pids livestream/logs livestream/assets
cp assets/branding/brand_16x9.png livestream/assets/
echo "  Done!"

echo "[3/5] Generating audio loops (this takes ~30 minutes)..."
bash livestream/generate_stream_audio.sh

echo "[4/5] Starting all streams..."
bash livestream/stream_manager.sh start

echo "[5/5] Setting up auto-restart on reboot..."
(crontab -l 2>/dev/null; echo "@reboot cd /root/blackscreen-youtube-automation && bash livestream/stream_manager.sh start") | crontab -

echo ""
echo "=== ALL DONE! 5 streams running 24/7 ==="
echo "Check status anytime: cd /root/blackscreen-youtube-automation && bash livestream/stream_manager.sh status"
