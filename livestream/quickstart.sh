#!/bin/bash
# One-command setup for Meditated Sleeping 24/7 live streams
# Usage: curl -sL RAW_URL | bash
set -euo pipefail

echo "=== [1/6] Installing system packages ==="
apt-get update
apt-get install -y git ffmpeg python3 python3-pip

echo "=== [2/6] Installing Python packages ==="
pip3 install numpy soundfile

echo "=== [3/6] Cloning repo ==="
cd /root
if [ -d blackscreen-youtube-automation ]; then
    cd blackscreen-youtube-automation
    git pull
else
    git clone https://github.com/oceanfarm1992-design/blackscreen-youtube-automation.git
    cd blackscreen-youtube-automation
fi

echo "=== [4/6] Setting up directories ==="
mkdir -p livestream/audio livestream/pids livestream/logs livestream/assets
cp assets/branding/brand_16x9.png livestream/assets/

echo "=== [5/6] Generating audio loops (this takes ~30 minutes) ==="
bash livestream/generate_stream_audio.sh

echo "=== [6/6] Starting streams ==="
bash livestream/stream_manager.sh start

# Auto-restart on reboot
(crontab -l 2>/dev/null; echo "@reboot cd /root/blackscreen-youtube-automation && bash livestream/stream_manager.sh start") | crontab -

echo ""
echo "=== ALL DONE! ==="
echo "Check status: bash livestream/stream_manager.sh status"
