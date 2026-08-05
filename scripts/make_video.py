#!/usr/bin/env python3
"""
Merge an audio track with a static branded #0D0D0D frame into an MP4.

Usage:
    python make_video.py --audio audio.wav --background assets/branding/brand_16x9.png \
        --duration-hours 10 --out final.mp4
    python make_video.py --audio short.wav --background assets/branding/brand_9x16.png \
        --duration-seconds 59 --fps 24 --out short.mp4

Relies on ffmpeg on PATH. The video is a single still image looped for the whole
duration (`-tune stillimage`, long GOP), so encoding cost stays near-zero regardless
of length. The audio is repeated to fill the duration with `-stream_loop -1`.
"""
import argparse
import subprocess


def build_command(audio_path, duration_sec, out_path, background_image,
                  fps=1, audio_bitrate="192k"):
    return [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", str(fps), "-i", background_image,
        "-stream_loop", "-1", "-i", audio_path,
        "-t", str(int(duration_sec)),
        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", str(fps),
        "-c:a", "aac", "-b:a", audio_bitrate,
        "-shortest",
        out_path,
    ]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--audio", required=True, help="path to audio track (wav/mp3)")
    p.add_argument("--background", required=True, help="branded still image")
    dur = p.add_mutually_exclusive_group(required=True)
    dur.add_argument("--duration-hours", type=float)
    dur.add_argument("--duration-seconds", type=float)
    p.add_argument("--fps", type=int, default=1, help="1 for long-form, ~24 for Shorts")
    p.add_argument("--out", default="final.mp4")
    args = p.parse_args()

    duration_sec = args.duration_seconds if args.duration_seconds else args.duration_hours * 3600
    cmd = build_command(args.audio, duration_sec, args.out, args.background, fps=args.fps)
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"Wrote {args.out} ({duration_sec/3600:.2f}h)")


if __name__ == "__main__":
    main()
