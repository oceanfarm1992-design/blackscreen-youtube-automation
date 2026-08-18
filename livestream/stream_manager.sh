#!/bin/bash
# ==========================================================================
# 24/7 Multi-Stream Manager for "Meditated Sleeping" YouTube channel
#
# Runs multiple simultaneous YouTube live streams from one Hetzner CX23.
# Each stream = one ffmpeg process pushing branded black screen + looped
# audio to YouTube via RTMP.
#
# Usage:
#   ./stream_manager.sh start          # start all streams
#   ./stream_manager.sh stop           # stop all streams
#   ./stream_manager.sh status         # show running streams
#   ./stream_manager.sh restart        # restart all
#   ./stream_manager.sh start rain     # start one specific stream
#   ./stream_manager.sh stop rain      # stop one specific stream
# ==========================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/assets"
AUDIO_DIR="$SCRIPT_DIR/audio"
PID_DIR="$SCRIPT_DIR/pids"
LOG_DIR="$SCRIPT_DIR/logs"
BRAND_IMG="$ASSETS_DIR/brand_16x9.png"

mkdir -p "$PID_DIR" "$LOG_DIR"

# Stream definitions: name|audio_file|youtube_stream_key
# Add your YouTube stream keys here (YouTube Studio → Go Live → Manage → each stream's key)
STREAMS_FILE="$SCRIPT_DIR/streams.conf"

if [ ! -f "$STREAMS_FILE" ]; then
    cat > "$STREAMS_FILE" << 'CONF'
# Stream configuration: one stream per line
# Format: name|audio_file|stream_key|title
#
# Get stream keys from: YouTube Studio → Go Live → Manage → Create New
# Each stream needs its own key.
#
# Example:
# rain|rain_loop.wav|xxxx-xxxx-xxxx-xxxx|🔴 24/7 Rain Sounds for Deep Sleep
# solfeggio|solfeggio_loop.wav|yyyy-yyyy-yyyy-yyyy|🔴 24/7 Solfeggio Healing Frequencies
# sleeping|sleeping_loop.wav|zzzz-zzzz-zzzz-zzzz|🔴 24/7 Deep Sleep Music
# romantic|romantic_loop.wav|aaaa-aaaa-aaaa-aaaa|🔴 24/7 Romantic & Calm Piano
CONF
    echo "Created $STREAMS_FILE — edit it with your stream keys first."
    exit 1
fi

RTMP_URL="rtmp://a.rtmp.youtube.com/live2"

start_stream() {
    local name="$1"
    local audio="$2"
    local key="$3"
    local pid_file="$PID_DIR/$name.pid"
    local log_file="$LOG_DIR/$name.log"

    if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
        echo "  [$name] already running (PID $(cat "$pid_file"))"
        return 0
    fi

    if [ ! -f "$AUDIO_DIR/$audio" ]; then
        echo "  [$name] ERROR: audio file not found: $AUDIO_DIR/$audio"
        return 1
    fi

    echo "  [$name] starting..."

    # ffmpeg: loop image + loop audio → RTMP
    # -re: real-time pacing (essential for live streaming)
    # -tune stillimage: optimized for static frames (very low CPU)
    # -b:v 1500k: YouTube recommends 1500-4000k for 720p live
    # -maxrate/bufsize: CBR for stable stream
    # -g 120: keyframe every 2s (YouTube requirement)
    nohup bash -c "
        while true; do
            ffmpeg -re \
                -stream_loop -1 -i '$AUDIO_DIR/$audio' \
                -loop 1 -framerate 1 -i '$BRAND_IMG' \
                -c:v libx264 -preset ultrafast -tune stillimage \
                -b:v 1500k -maxrate 1500k -bufsize 3000k \
                -pix_fmt yuv420p -g 120 -r 30 \
                -c:a aac -b:a 192k -ar 44100 \
                -f flv '$RTMP_URL/$key' \
                >> '$log_file' 2>&1
            echo '[$(date)] Stream ended, restarting in 10s...' >> '$log_file'
            sleep 10
        done
    " &
    echo $! > "$pid_file"
    echo "  [$name] started (PID $!)"
}

stop_stream() {
    local name="$1"
    local pid_file="$PID_DIR/$name.pid"

    if [ ! -f "$pid_file" ]; then
        echo "  [$name] not running"
        return 0
    fi

    local pid
    pid=$(cat "$pid_file")
    if kill -0 "$pid" 2>/dev/null; then
        # Kill the wrapper bash and all child ffmpeg processes
        pkill -P "$pid" 2>/dev/null || true
        kill "$pid" 2>/dev/null || true
        echo "  [$name] stopped (was PID $pid)"
    else
        echo "  [$name] was not running (stale PID)"
    fi
    rm -f "$pid_file"
}

stream_status() {
    local name="$1"
    local pid_file="$PID_DIR/$name.pid"

    if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
        echo "  [$name] RUNNING (PID $(cat "$pid_file"))"
    else
        echo "  [$name] STOPPED"
        rm -f "$pid_file" 2>/dev/null
    fi
}

read_streams() {
    grep -v '^#' "$STREAMS_FILE" | grep -v '^$' | while IFS='|' read -r name audio key title; do
        echo "$name|$audio|$key|$title"
    done
}

ACTION="${1:-status}"
TARGET="${2:-all}"

case "$ACTION" in
    start)
        echo "Starting streams..."
        read_streams | while IFS='|' read -r name audio key title; do
            if [ "$TARGET" = "all" ] || [ "$TARGET" = "$name" ]; then
                start_stream "$name" "$audio" "$key"
            fi
        done
        ;;
    stop)
        echo "Stopping streams..."
        read_streams | while IFS='|' read -r name audio key title; do
            if [ "$TARGET" = "all" ] || [ "$TARGET" = "$name" ]; then
                stop_stream "$name"
            fi
        done
        ;;
    restart)
        echo "Restarting streams..."
        read_streams | while IFS='|' read -r name audio key title; do
            if [ "$TARGET" = "all" ] || [ "$TARGET" = "$name" ]; then
                stop_stream "$name"
                sleep 2
                start_stream "$name" "$audio" "$key"
            fi
        done
        ;;
    status)
        echo "Stream status:"
        read_streams | while IFS='|' read -r name audio key title; do
            stream_status "$name"
        done
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status} [stream_name|all]"
        exit 1
        ;;
esac
