#!/bin/bash
# ==========================================================================
# One-time setup for the Hetzner CX23 live streaming server.
# Run this after SSHing into your server for the first time.
#
# Usage:
#   ssh root@YOUR_SERVER_IP
#   git clone https://github.com/oceanfarm1992-design/blackscreen-youtube-automation.git
#   cd blackscreen-youtube-automation
#   bash livestream/setup_server.sh
# ==========================================================================

set -euo pipefail

echo "=== Setting up Meditated Sleeping live stream server ==="
echo ""

# 1. Install dependencies
echo "[1/5] Installing system packages..."
apt-get update
apt-get install -y ffmpeg python3 python3-pip git

# 2. Install Python deps
echo "[2/5] Installing Python packages..."
pip3 install numpy soundfile

# 3. Create directory structure
echo "[3/5] Setting up directories..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$SCRIPT_DIR/audio" "$SCRIPT_DIR/assets" "$SCRIPT_DIR/pids" "$SCRIPT_DIR/logs"

# 4. Copy brand image
echo "[4/5] Copying brand assets..."
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cp "$PROJECT_DIR/assets/branding/brand_16x9.png" "$SCRIPT_DIR/assets/"

# 5. Generate audio loops
echo "[5/5] Generating audio loops (this takes ~30 minutes)..."
bash "$SCRIPT_DIR/generate_stream_audio.sh"

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Next steps:"
echo "  1. Get stream keys from YouTube Studio:"
echo "     YouTube Studio → Go Live → Manage → Create New Stream"
echo "     Create one stream per theme, copy each stream key."
echo ""
echo "  2. Edit streams.conf with your keys:"
echo "     nano $SCRIPT_DIR/streams.conf"
echo ""
echo "  3. Start streaming:"
echo "     bash $SCRIPT_DIR/stream_manager.sh start"
echo ""
echo "  4. Check status:"
echo "     bash $SCRIPT_DIR/stream_manager.sh status"
echo ""
echo "  5. Enable auto-start on boot (optional):"
echo "     crontab -e"
echo "     Add: @reboot cd $SCRIPT_DIR && bash stream_manager.sh start"
