#!/usr/bin/env python3
"""
Merge a short audio loop with a solid black frame into a long-duration MP4.

Usage:
    python make_video.py --loop loop.wav --duration-hours 8 --out final.mp4

Relies on ffmpeg being installed and on PATH. Uses -stream_loop to repeat the
audio without re-encoding it hours' worth of times, and a single black color
source for video so encoding cost stays near-zero regardless of duration.
"""
import argparse
import subprocess


def build_command(loop_path: str, duration_hours: float, out_path: str,
                   resolution: str = "1280x720", audio_bitrate: str = "128k"):
    duration_sec = int(duration_hours * 3600)
    return [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=black:s={resolution}:r=1",
        "-stream_loop", "-1", "-i", loop_path,
        "-t", str(duration_sec),
        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", audio_bitrate,
        "-shortest",
        out_path,
    ]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--loop", required=True, help="path to short audio loop (wav/mp3)")
    p.add_argument("--duration-hours", type=float, required=True)
    p.add_argument("--out", default="final.mp4")
    p.add_argument("--resolution", default="1280x720")
    args = p.parse_args()

    cmd = build_command(args.loop, args.duration_hours, args.out, args.resolution)
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"Wrote {args.out} ({args.duration_hours}h)")


if __name__ == "__main__":
    main()
