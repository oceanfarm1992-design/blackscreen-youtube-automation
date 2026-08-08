#!/usr/bin/env bash
# One-time setup for the 24/7 YouTube live stream on a fresh Ubuntu VM
# (e.g. Oracle Cloud Always Free). Run from inside the cloned repo:
#
#     sudo bash stream/setup.sh
#
# Installs ffmpeg + Python deps, stores your stream key, generates the audio,
# installs a systemd service (auto-start + auto-restart), and a daily refresh.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
RUN_USER="${SUDO_USER:-$(whoami)}"
echo "Repo:        $REPO"
echo "Service user: $RUN_USER"

# 1. System dependencies
apt-get update
apt-get install -y ffmpeg python3 python3-pip
# numpy/soundfile for the synth engine (system-wide so root cron + service agree)
pip3 install -r "$REPO/requirements.txt" 2>/dev/null \
  || pip3 install --break-system-packages -r "$REPO/requirements.txt"

# 2. Stream key (stored root-only, never in the repo)
if [ ! -f /etc/youtube-live.env ]; then
  read -rp "Paste your YouTube stream key: " KEY
  echo "STREAM_KEY=$KEY" > /etc/youtube-live.env
  chmod 600 /etc/youtube-live.env
  echo "Saved stream key to /etc/youtube-live.env"
else
  echo "/etc/youtube-live.env already exists — leaving it as is."
fi

# 3. Generate the initial audio loops + playlist
bash "$REPO/stream/refresh_audio.sh"

# 4. systemd service (path-correct for this clone location)
cat > /etc/systemd/system/youtube-live.service <<EOF
[Unit]
Description=YouTube 24/7 live music stream (Meditated Sleeping)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
EnvironmentFile=/etc/youtube-live.env
WorkingDirectory=$REPO
ExecStart=/usr/bin/env bash $REPO/stream/stream_live.sh
Restart=always
RestartSec=5
User=$RUN_USER

[Install]
WantedBy=multi-user.target
EOF

# 5. Daily audio refresh + restart (keeps content fresh; ~1 short reconnect/day)
TMP_CRON="$(mktemp)"
crontab -l 2>/dev/null > "$TMP_CRON" || true
if ! grep -q "stream/refresh_audio.sh" "$TMP_CRON"; then
  echo "17 4 * * * bash $REPO/stream/refresh_audio.sh && systemctl restart youtube-live" >> "$TMP_CRON"
  crontab "$TMP_CRON"
fi
rm -f "$TMP_CRON"

# 6. Start it
systemctl daemon-reload
systemctl enable --now youtube-live

echo
echo "Live stream started. Useful commands:"
echo "  sudo systemctl status youtube-live      # is it running?"
echo "  journalctl -u youtube-live -f           # live logs"
echo "  sudo systemctl restart youtube-live     # restart"
