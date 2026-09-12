#!/usr/bin/env python3
"""
Render a branded, procedurally-animated "Aether & Ash" video: a slow, unique
generative visual (a soft organic noise-cloud, tinted to the theme's accent
color, slowly drifting/panning) plus the branded ember icon, muxed with the
theme's audio track.

The noise field itself is generated in Python (numpy FFT-shaped noise +
one-time PIL Gaussian blur), then the camera pans slowly across it per
frame (cheap array slicing -- no per-frame blur/regeneration) and the
tinted frames are piped to ffmpeg as raw video. ffmpeg only does standard,
universally-available work from there (eq/vignette/scale/overlay/encode).

This deliberately avoids ffmpeg's `perlin`/`gradients` lavfi source filters:
an earlier version used `perlin`, which rendered correctly on a local full
ffmpeg build but does NOT exist in the Ubuntu apt ffmpeg package GitHub
Actions installs (confirmed by a real CI failure: "No such filter: 'perlin'").
Generating the noise in Python instead of relying on the runner's ffmpeg
feature set removes that whole class of "works locally, breaks in CI" risk.

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

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ICON = os.path.join(ROOT, "assets", "aether", "branding", "icon.png")

FPS = 18                 # slow, deliberate motion -- matches the ambient mood
INTERNAL_SCALE = 0.4167  # render the generative layer at ~5/12 size, then upscale
PAN_MARGIN = 0.35        # fraction of viewport size the camera can drift across


def _even(n):
    n = int(n)
    return n - (n % 2)


def _channel_gain(hex_color):
    """Hex color -> (r, g, b) 0..1 tint gains (each channel scaled by its
    component; floored so no channel goes fully to 0 and loses shadow detail)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    return tuple(max(0.12, v) for v in (r, g, b))


def _noise_field(w, h, rng, tilt=1.6, blur_frac=0.03):
    """A large soft cloud-like grayscale field (0..1): white noise shaped in
    the 2D frequency domain (darker/softer at higher tilt), then blurred."""
    white = rng.standard_normal((h, w)).astype(np.float32)
    spec = np.fft.rfft2(white)
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    freq = np.sqrt(fy ** 2 + fx ** 2)
    freq[0, 0] = 1e-6
    shape = 1.0 / (freq ** (tilt / 2.0))
    shape[0, 0] = 0.0
    field = np.fft.irfft2(spec * shape, s=(h, w))
    field -= field.min()
    field /= (field.max() + 1e-9)

    img = Image.fromarray((field * 255).astype(np.uint8), mode="L")
    img = img.filter(ImageFilter.GaussianBlur(radius=max(2, int(min(w, h) * blur_frac))))
    return np.asarray(img).astype(np.float32) / 255.0


def _pan_path(n_frames, duration_sec, max_dx, max_dy, rng):
    """Smooth, slow lissajous-style drift across the noise field, so the
    camera never repeats the same path twice (random phase per render)."""
    t = np.linspace(0, 2 * np.pi, n_frames)
    px, py = rng.uniform(0, 2 * np.pi, size=2)
    fx, fy = rng.uniform(0.7, 1.3, size=2)
    dx = (0.5 + 0.5 * np.sin(t * fx + px)) * max_dx
    dy = (0.5 + 0.5 * np.sin(t * fy + py)) * max_dy
    return dx.astype(int), dy.astype(int)


def render_frames(out_pipe, duration_sec, iw, ih, color, seed):
    rng = np.random.default_rng(seed)
    max_dx = _even(iw * PAN_MARGIN)
    max_dy = _even(ih * PAN_MARGIN)
    field = _noise_field(iw + max_dx, ih + max_dy, rng)

    n_frames = int(round(duration_sec * FPS))
    dxs, dys = _pan_path(n_frames, duration_sec, max_dx, max_dy, rng)
    rr, gg, bb = _channel_gain(color)
    gains = np.array([rr, gg, bb], dtype=np.float32)

    for i in range(n_frames):
        view = field[dys[i]:dys[i] + ih, dxs[i]:dxs[i] + iw]
        rgb = (view[:, :, None] * gains[None, None, :] * 255.0)
        out_pipe.write(np.clip(rgb, 0, 255).astype(np.uint8).tobytes())


def build_ffmpeg_command(audio_path, duration_sec, width, height, out_path, iw, ih):
    icon_w = _even(width * 0.09)
    filter_complex = (
        f"[0:v]eq=saturation=1.3:brightness='0.03*sin(2*PI*t/240)':eval=frame,"
        f"vignette=PI/3.5,scale={width}:{height}:flags=lanczos,format=rgba[bg];"
        f"[1:v]scale={icon_w}:-1,colorchannelmixer=aa=0.32[icon];"
        f"[bg][icon]overlay=W-w-{_even(width*0.03)}:H-h-{_even(height*0.03)}:format=auto,"
        f"format=yuv420p[vout]"
    )
    return [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{iw}x{ih}", "-r", str(FPS),
        "-i", "pipe:0",
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

    iw = _even(args.width * INTERNAL_SCALE)
    ih = _even(args.height * INTERNAL_SCALE)

    cmd = build_ffmpeg_command(args.audio, args.duration_seconds, args.width,
                                args.height, args.out, iw, ih)
    print("Running:", " ".join(cmd))
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        render_frames(proc.stdin, args.duration_seconds, iw, ih, args.color, args.seed)
    finally:
        proc.stdin.close()
    ret = proc.wait()
    if ret != 0:
        raise subprocess.CalledProcessError(ret, cmd)
    print(f"Wrote {args.out} ({args.duration_seconds:.0f}s, {args.width}x{args.height})")


if __name__ == "__main__":
    main()
