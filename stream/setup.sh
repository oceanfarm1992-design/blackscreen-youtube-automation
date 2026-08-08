#!/usr/bin/env bash
# One-time setup for 24/7 YouTube live streams on a fresh Ubuntu VM
# (e.g. Oracle Cloud Always Free). Run from inside the cloned repo:
#
#     sudo bash stream/setup.sh
#
# Runs ONE dedicated 24/7 stream per music you give a stream key for, using a
# systemd template service (youtube-live@<theme>) that auto-starts on boot and
# auto-restarts on drop. Installs deps, generates audio, and adds a daily refresh.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
RUN_USER="${SUDO_USER:-$(whoami)}"
THEMES=(rain waterfall forest sleeping indian romantic romantic_night)
ENV_DIR=/etc/youtube-live

echo "Repo:         $REPO"
echo "Service user: $RUN_USER"

# 1. System dependencies
apt-get update
apt-get install -y ffmpeg python3 python3-pip
pip3 install -r "$REPO/requirements.txt" 2>/dev/null \
  || pip3 install --break-system-packages -r "$REPO/requirements.txt"

# 2. Generate the audio loops (all themes) + playlist
bash "$REPO/stream/refresh_audio.sh"

# 3. systemd TEMPLATE service: youtube-live@<theme>
cat > /etc/systemd/system/youtube-live@.service <<EOF
[Unit]
Description=YouTube 24/7 live: %i (Meditated Sleeping)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
EnvironmentFile=$ENV_DIR/%i.env
WorkingDirectory=$REPO
ExecStart=/usr/bin/env bash $REPO/stream/stream_live.sh --theme %i
Restart=always
RestartSec=5
User=$RUN_USER

[Install]
WantedBy=multi-user.target
EOF

# 4. Ask for a stream key per music (blank = skip that one). Each music that
#    gets a key becomes its own 24/7 stream.
mkdir -p "$ENV_DIR"
chmod 700 "$ENV_DIR"
ENABLED=()
echo
echo "Enter the YouTube stream key for each music (leave blank to skip):"
for th in "${THEMES[@]}"; do
  if [ -f "$ENV_DIR/$th.env" ]; then
    echo "  $th: already configured — keeping existing key."
    ENABLED+=("$th"); continue
  fi
  read -rp "  $th stream key: " KEY
  if [ -n "$KEY" ]; then
    echo "STREAM_KEY=$KEY" > "$ENV_DIR/$th.env"
    chmod 600 "$ENV_DIR/$th.env"
    ENABLED+=("$th")
  fi
done

if [ ${#ENABLED[@]} -eq 0 ]; then
  echo "No stream keys entered — nothing to start. Re-run to add keys."
  exit 0
fi

# 5. Daily audio refresh + restart of all enabled streams (freshness)
TMP_CRON="$(mktemp)"
crontab -l 2>/dev/null > "$TMP_CRON" || true
if ! grep -q "stream/refresh_audio.sh" "$TMP_CRON"; then
  echo "17 4 * * * bash $REPO/stream/refresh_audio.sh && systemctl restart 'youtube-live@*'" >> "$TMP_CRON"
  crontab "$TMP_CRON"
fi
rm -f "$TMP_CRON"

# 6. Start one stream per configured music
systemctl daemon-reload
for th in "${ENABLED[@]}"; do
  systemctl enable --now "youtube-live@$th"
  echo "Started youtube-live@$th"
done

echo
echo "Live streams running: ${ENABLED[*]}"
echo "  systemctl status 'youtube-live@*'      # all streams"
echo "  journalctl -u youtube-live@rain -f     # one stream's logs"
echo "  sudo systemctl restart youtube-live@rain"
