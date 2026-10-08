#!/usr/bin/env python3
"""
Render a branded, procedurally-animated video for any of the dark-ambient
channels: a slow, unique generative visual (a soft organic noise-cloud,
tinted to the theme's accent color, slowly drifting/panning) plus the
channel's branded icon, muxed with the theme's audio track.

Shared across channels (Aether & Ash, Sanctuary of Sci, ...) -- each channel
just passes its own --icon and per-theme --color. See each channel's
produce.py for how it's invoked.

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

`_noise_field` and `_channel_gain` are also imported directly by each
channel's make_thumbnails.py, to render a matching still frame as the
thumbnail background (same visual engine, no separate art needed).

`--topic` (one of TOPIC_PROFILES: fire/water/wind/void/stone/neutral) keeps
the field itself fully abstract -- no literal flame/water/leaf shapes are
drawn -- but pushes the noise-field *texture* (tilt/blur, i.e. how
turbulent vs. smooth the cloud shape is), its pan motion, and the color
grade to match the theme's subject (e.g. fire is sharper/grainier and
flickers fast with a warm, jittery pan; water is smooth and glossy and
drifts slow; void is extremely soft and barely moves at all). Each
channel's themes.py maps its theme keys to a topic; produce.py passes it
straight through.

Usage:
    python make_animated_video.py --audio audio.wav --duration-seconds 870 \
        --width 1920 --height 1080 --color ff7a33 --icon path/to/icon.png \
        --topic fire --seed 20260912 --out feature.mp4
"""
import argparse
import subprocess

import numpy as np
from PIL import Image, ImageFilter

FPS = 18                 # slow, deliberate motion -- matches the ambient mood
INTERNAL_SCALE = 0.4167  # render the generative layer at ~5/12 size, then upscale
PAN_MARGIN = 0.35        # fraction of viewport size the camera can drift across

# Per-topic motion/color profiles. These keep the shared engine fully
# abstract -- no literal flame/water/leaf shapes are drawn -- but push the
# existing noise-field's *pan motion* and *color grade* to evoke each
# theme's subject (e.g. a fast, jittery, warm flicker for a fireside theme
# vs. a slow, smooth, cool drift for a water theme). `neutral` reproduces
# the original single-profile behavior exactly, so themes that don't pass
# --topic are unaffected.
TOPIC_PROFILES = {
    "neutral": dict(
        fx_range=(0.7, 1.3), fy_range=(0.7, 1.3), amp_x=1.0, amp_y=1.0,
        jitter=0.0, jitter_freq=(10, 16), drift_y=0.0,
        flicker_period=240.0, flicker_amp=0.03, saturation=1.3, contrast=1.0,
        vignette="PI/3.5", tilt=1.6, blur_frac=0.030,
    ),
    "fire": dict(
        fx_range=(1.1, 1.6), fy_range=(1.3, 1.9), amp_x=0.55, amp_y=0.5,
        jitter=0.10, jitter_freq=(12, 20), drift_y=0.15,
        flicker_period=7.0, flicker_amp=0.07, saturation=1.5, contrast=1.08,
        vignette="PI/3.2", tilt=1.15, blur_frac=0.016,
    ),
    "water": dict(
        fx_range=(0.5, 0.8), fy_range=(0.3, 0.5), amp_x=1.0, amp_y=0.35,
        jitter=0.02, jitter_freq=(6, 10), drift_y=0.0,
        flicker_period=55.0, flicker_amp=0.035, saturation=1.38, contrast=1.0,
        vignette="PI/3.5", tilt=2.10, blur_frac=0.050,
    ),
    "wind": dict(
        fx_range=(0.6, 1.0), fy_range=(0.4, 0.7), amp_x=0.85, amp_y=0.55,
        jitter=0.015, jitter_freq=(5, 9), drift_y=0.0,
        flicker_period=90.0, flicker_amp=0.03, saturation=1.25, contrast=1.0,
        vignette="PI/3.6", tilt=1.35, blur_frac=0.024,
    ),
    "void": dict(
        fx_range=(0.3, 0.5), fy_range=(0.3, 0.5), amp_x=0.4, amp_y=0.4,
        jitter=0.0, jitter_freq=(10, 16), drift_y=0.0,
        flicker_period=420.0, flicker_amp=0.02, saturation=1.2, contrast=1.02,
        vignette="PI/3.2", tilt=2.30, blur_frac=0.055,
    ),
    "stone": dict(
        fx_range=(0.4, 0.6), fy_range=(0.4, 0.6), amp_x=0.45, amp_y=0.45,
        jitter=0.0, jitter_freq=(10, 16), drift_y=0.0,
        flicker_period=300.0, flicker_amp=0.015, saturation=1.05, contrast=0.98,
        vignette="PI/3.8", tilt=1.75, blur_frac=0.022,
    ),
}


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


def _pan_path(n_frames, duration_sec, max_dx, max_dy, rng, profile):
    """Smooth, slow lissajous-style drift across the noise field, so the
    camera never repeats the same path twice (random phase per render).
    `profile` (a TOPIC_PROFILES entry) scales the amplitude/frequency of
    that drift and can layer a faster jitter and a one-way drift bias on
    top, so e.g. a fire topic flickers quickly in place while a void topic
    barely moves at all."""
    t = np.linspace(0, 2 * np.pi, n_frames)
    px, py = rng.uniform(0, 2 * np.pi, size=2)
    fx = rng.uniform(*profile["fx_range"])
    fy = rng.uniform(*profile["fy_range"])
    amp_x = max_dx * profile["amp_x"]
    amp_y = max_dy * profile["amp_y"]
    dx = (0.5 + 0.5 * np.sin(t * fx + px)) * amp_x
    dy = (0.5 + 0.5 * np.sin(t * fy + py)) * amp_y

    if profile["drift_y"]:
        dy = dy + profile["drift_y"] * max_dy * (t / (2 * np.pi))

    if profile["jitter"]:
        jlo, jhi = profile["jitter_freq"]
        jfx, jfy = rng.uniform(jlo, jhi, size=2)
        jpx, jpy = rng.uniform(0, 2 * np.pi, size=2)
        dx = dx + profile["jitter"] * max_dx * np.sin(t * jfx + jpx)
        dy = dy + profile["jitter"] * max_dy * np.sin(t * jfy + jpy)

    dx = np.clip(dx, 0, max_dx)
    dy = np.clip(dy, 0, max_dy)
    return dx.astype(int), dy.astype(int)


def render_frames(out_pipe, duration_sec, iw, ih, color, seed, topic="neutral"):
    profile = TOPIC_PROFILES.get(topic, TOPIC_PROFILES["neutral"])
    rng = np.random.default_rng(seed)
    max_dx = _even(iw * PAN_MARGIN)
    max_dy = _even(ih * PAN_MARGIN)
    field = _noise_field(iw + max_dx, ih + max_dy, rng,
                          tilt=profile["tilt"], blur_frac=profile["blur_frac"])

    n_frames = int(round(duration_sec * FPS))
    dxs, dys = _pan_path(n_frames, duration_sec, max_dx, max_dy, rng, profile)
    gains = np.array(_channel_gain(color), dtype=np.float32)

    for i in range(n_frames):
        view = field[dys[i]:dys[i] + ih, dxs[i]:dxs[i] + iw]
        rgb = (view[:, :, None] * gains[None, None, :] * 255.0)
        out_pipe.write(np.clip(rgb, 0, 255).astype(np.uint8).tobytes())


def build_ffmpeg_command(audio_path, duration_sec, width, height, out_path, iw, ih, icon,
                          topic="neutral"):
    profile = TOPIC_PROFILES.get(topic, TOPIC_PROFILES["neutral"])
    icon_w = _even(width * 0.09)
    filter_complex = (
        f"[0:v]eq=saturation={profile['saturation']}:contrast={profile['contrast']}:"
        f"brightness='{profile['flicker_amp']}*sin(2*PI*t/{profile['flicker_period']})':eval=frame,"
        f"vignette={profile['vignette']},scale={width}:{height}:flags=lanczos,format=rgba[bg];"
        f"[1:v]scale={icon_w}:-1,colorchannelmixer=aa=0.32[icon];"
        f"[bg][icon]overlay=W-w-{_even(width*0.03)}:H-h-{_even(height*0.03)}:format=auto,"
        f"format=yuv420p[vout]"
    )
    return [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{iw}x{ih}", "-r", str(FPS),
        "-i", "pipe:0",
        "-i", icon,
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
    p.add_argument("--icon", required=True, help="path to the channel's branded icon PNG")
    p.add_argument("--topic", default="neutral", choices=sorted(TOPIC_PROFILES),
                   help="motion/flicker profile matching the theme's subject "
                        "(fire/water/wind/void/stone/neutral)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="animated.mp4")
    args = p.parse_args()

    iw = _even(args.width * INTERNAL_SCALE)
    ih = _even(args.height * INTERNAL_SCALE)

    cmd = build_ffmpeg_command(args.audio, args.duration_seconds, args.width,
                                args.height, args.out, iw, ih, args.icon, args.topic)
    print("Running:", " ".join(cmd))
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        render_frames(proc.stdin, args.duration_seconds, iw, ih, args.color, args.seed, args.topic)
    finally:
        proc.stdin.close()
    ret = proc.wait()
    if ret != 0:
        raise subprocess.CalledProcessError(ret, cmd)
    print(f"Wrote {args.out} ({args.duration_seconds:.0f}s, {args.width}x{args.height})")


if __name__ == "__main__":
    main()
