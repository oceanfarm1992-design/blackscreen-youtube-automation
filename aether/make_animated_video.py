#!/usr/bin/env python3
"""
Render a branded, procedurally-animated "Aether & Ash" video: a slow, unique
generative visual (ffmpeg's native Perlin-noise filter, tinted to the theme's
accent color) plus the branded ember icon, muxed with the theme's audio track.

Built entirely from ffmpeg's native `perlin` lavfi source filter plus
standard color filters -- no extra Python rendering dependency, no external
footage. The generative layer is rendered at a reduced internal resolution
and upscaled (the soft cloud texture doesn't need native-res detail), which
is what keeps a ~14.5 minute render to roughly real-time instead of ~15x
real-time at full 1080p -- see the timing note in the repo's plan history.

Note: an earlier version of this recipe composited `perlin` with the
`gradients` filter via `blend`, but that combination silently corrupts color
on the RGB->YUV420p conversion needed for H.264 (confirmed by isolated
testing -- a plain solid color survives the conversion fine, but the
gradients+blend output does not). Tinting the grayscale noise directly with
`colorchannelmixer` avoids the bug entirely and was verified end-to-end
through a real H.264 encode.

Usage:
    python make_animated_video.py --audio audio.wav --duration-seconds 870 \
        --width 1920 --height 1080 --color ff7a33 \
        --seed 20260912 --out feature.mp4
    python make_animated_video.py --audio short.wav --duration-seconds 59 \
        --width 1080 --height 1920 --color 6a2fb0 \
        --seed 20260912 --out short.mp4
"""
import argparse
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ICON = os.path.join(ROOT, "assets", "aether", "branding", "icon.png")

FPS = 18                 # slow, deliberate motion -- matches the ambient mood
INTERNAL_SCALE = 0.4167  # render the generative layer at ~5/12 size, then upscale


def _even(n):
    n = int(n)
    return n - (n % 2)


def _channel_gain(hex_color):
    """Hex color -> (rr, gg, bb) colorchannelmixer gains that tint grayscale
    noise toward that color (each channel scaled by its 0..1 component)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    # Floor each gain a little so no channel goes fully to 0 (keeps some
    # depth/detail in the shadows instead of a flat-black channel).
    return tuple(max(0.12, v) for v in (r, g, b))


def build_command(audio_path, duration_sec, width, height, color, seed, out_path):
    iw = _even(width * INTERNAL_SCALE)
    ih = _even(height * INTERNAL_SCALE)
    icon_w = _even(width * 0.09)
    rr, gg, bb = _channel_gain(color)

    perlin_src = (
        f"perlin=size={iw}x{ih}:rate={FPS}:octaves=2:persistence=0.5:"
        f"xscale=2.2:yscale=2.2:tscale=0.12:seed={seed}"
    )

    filter_complex = (
        f"[0:v]format=gray,eq=contrast=1.4:brightness=0.1,format=rgba,"
        f"colorchannelmixer=rr={rr:.3f}:gg={gg:.3f}:bb={bb:.3f},"
        f"eq=saturation=1.3:brightness='0.03*sin(2*PI*t/240)':eval=frame,"
        f"vignette=PI/3.5,scale={width}:{height}:flags=lanczos,format=rgba[bg];"
        f"[1:v]scale={icon_w}:-1,colorchannelmixer=aa=0.32[icon];"
        f"[bg][icon]overlay=W-w-{_even(width*0.03)}:H-h-{_even(height*0.03)}:format=auto,"
        f"format=yuv420p[vout]"
    )

    return [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", perlin_src,
        "-i", ICON,
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "2:a",
        "-t", str(duration_sec),
        "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        out_path,
    ]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--audio", required=True)
    p.add_argument("--duration-seconds", type=float, required=True)
    p.add_argument("--width", type=int, required=True)
    p.add_argument("--height", type=int, required=True)
    p.add_argument("--color", required=True, help="hex accent color, e.g. ff7a33")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="animated.mp4")
    args = p.parse_args()

    cmd = build_command(args.audio, args.duration_seconds, args.width, args.height,
                         args.color, args.seed, args.out)
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"Wrote {args.out} ({args.duration_seconds:.0f}s, {args.width}x{args.height})")


if __name__ == "__main__":
    main()
