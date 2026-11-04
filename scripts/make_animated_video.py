#!/usr/bin/env python3
"""
Render a branded, procedurally-animated video for any of the dark-ambient
channels: a slow, unique generative visual (a soft organic noise-cloud,
tinted to the theme's accent color, slowly drifting/panning) plus the
channel's branded icon, muxed with the theme's audio track.

On top of the cloud every render draws its own LOOK (see pick_look): one
animated layer suited to the topic (rising embers, spreading ripples,
twinkling stars, drifting light bands, a second mist layer), a per-video
palette with its own hue shift and highlight colour, an optional wandering
light, and a mirrored composition. `--variant` (the Vol. number) cycles the
layer so consecutive uploads of a theme never share one.

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
import os
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

    img = Image.fromarray((field * 255).astype(np.uint8))  # uint8 HxW -> L
    img = img.filter(ImageFilter.GaussianBlur(radius=max(2, int(min(w, h) * blur_frac))))
    return np.asarray(img).astype(np.float32) / 255.0


def _pan_path(n_frames, duration_sec, max_dx, max_dy, rng, profile, periodic=False):
    """Smooth, slow lissajous-style drift across the noise field, so the
    camera never repeats the same path twice (random phase per render).
    `profile` (a TOPIC_PROFILES entry) scales the amplitude/frequency of
    that drift and can layer a faster jitter and a one-way drift bias on
    top, so e.g. a fire topic flickers quickly in place while a void topic
    barely moves at all.

    periodic=True makes the path end exactly where it began (whole-number
    frequencies, no one-way drift, no duplicated end frame), so the clip can
    be looped back-to-back without a visible jump -- used for long videos."""
    t = np.linspace(0, 2 * np.pi, n_frames, endpoint=not periodic)
    px, py = rng.uniform(0, 2 * np.pi, size=2)
    fx = rng.uniform(*profile["fx_range"])
    fy = rng.uniform(*profile["fy_range"])
    if periodic:
        fx, fy = max(1, round(fx)), max(1, round(fy))
    amp_x = max_dx * profile["amp_x"]
    amp_y = max_dy * profile["amp_y"]
    dx = (0.5 + 0.5 * np.sin(t * fx + px)) * amp_x
    dy = (0.5 + 0.5 * np.sin(t * fy + py)) * amp_y

    if profile["drift_y"] and not periodic:
        dy = dy + profile["drift_y"] * max_dy * (t / (2 * np.pi))

    if profile["jitter"]:
        jlo, jhi = profile["jitter_freq"]
        jfx, jfy = rng.uniform(jlo, jhi, size=2)
        if periodic:
            jfx, jfy = round(jfx), round(jfy)
        jpx, jpy = rng.uniform(0, 2 * np.pi, size=2)
        dx = dx + profile["jitter"] * max_dx * np.sin(t * jfx + jpx)
        dy = dy + profile["jitter"] * max_dy * np.sin(t * jfy + jpy)

    dx = np.clip(dx, 0, max_dx)
    dy = np.clip(dy, 0, max_dy)
    return dx.astype(int), dy.astype(int)


# --------------------------------------------------------------------------- #
# Per-video "looks".
#
# A random cloud alone makes every upload of a theme look the same to a viewer
# (and to YouTube's repetitious-content review): same tint, same drifting blob.
# So each render also picks a LOOK -- a second animated layer drawn on top of
# the cloud, a two-tone palette with its own hue shift and highlight colour, an
# optional moving light, and a mirrored composition. The layer is chosen from
# the ones that suit the theme's topic (embers rise for fire, ripples spread
# for water, stars twinkle for void, ...).
#
# `variant` (the upload's Vol. number) cycles the layer, so two consecutive
# uploads of a theme never share one; the seed varies everything else. All
# motion uses whole cycles over the clip when periodic=True, so hour-long loop
# segments stay seamless.

TOPIC_LAYERS = {
    "neutral": ("motes", "bands", "ripples", "parallax"),
    "fire": ("motes", "parallax", "bands"),
    "water": ("ripples", "parallax", "bands", "motes"),
    "wind": ("parallax", "bands", "motes"),
    "void": ("motes", "ripples", "parallax"),
    "stone": ("motes", "parallax", "bands"),
}

# Particle behaviour per topic. Speeds are px/s at the internal render size.
MOTE_STYLE = {
    "neutral": dict(vx=(-4, 4), vy=(-4, 4), size=(0.9, 2.2), count=(35, 70), twinkle=0.5),
    "fire": dict(vx=(-2, 2), vy=(-14, -6), size=(0.9, 2.2), count=(45, 85), twinkle=0.6),   # embers rise
    "water": dict(vx=(-2, 2), vy=(-7, -2), size=(1.2, 2.8), count=(25, 50), twinkle=0.25),  # bubbles
    "wind": dict(vx=(8, 18), vy=(-2, 2), size=(0.8, 1.8), count=(45, 85), twinkle=0.3),     # blown seeds
    "void": dict(vx=(-0.6, 0.6), vy=(-0.6, 0.6), size=(0.7, 1.6), count=(70, 130), twinkle=0.9),  # stars
    "stone": dict(vx=(-2, 2), vy=(1, 4), size=(0.8, 1.8), count=(30, 60), twinkle=0.2),     # settling dust
}


def _hex_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def _rotate_hue(rgb, degrees, lighten=0.0):
    import colorsys
    h, l, s = colorsys.rgb_to_hls(*rgb)
    l = l + (1.0 - l) * lighten
    return colorsys.hls_to_rgb((h + degrees / 360.0) % 1.0, l, s)


def pick_look(seed, topic="neutral", variant=None):
    """This render's look. Deterministic in (seed, topic, variant), and drawn
    from its own random stream so the cloud itself is unchanged by it."""
    rng = np.random.default_rng([abs(int(seed)), 7919])
    layers = TOPIC_LAYERS.get(topic, TOPIC_LAYERS["neutral"])
    pick = int(rng.integers(len(layers)))
    layer = layers[pick if variant is None else int(variant) % len(layers)]
    return dict(
        layer=layer,
        hue_shift=float(rng.uniform(-28, 28)),
        highlight_hue=float(rng.choice([-1, 1]) * rng.uniform(22, 65)),
        highlight_mix=float(rng.uniform(0.35, 0.8)),
        glow=bool(rng.random() < 0.6),
        flip_x=bool(rng.random() < 0.5),
        flip_y=bool(rng.random() < 0.5),
        strength=float(rng.uniform(0.75, 1.15)),
    )


def _palette(color, look):
    """256-entry RGB lookup (0..255 floats): dark -> the theme colour (hue-
    shifted for this video) -> a lighter highlight hue in the brightest areas."""
    base = np.array(_channel_gain("%02x%02x%02x" % tuple(
        int(round(c * 255)) for c in _rotate_hue(_hex_rgb(color), look["hue_shift"]))),
        dtype=np.float32)
    hi = np.array(_rotate_hue(tuple(base), look["highlight_hue"], lighten=0.35), dtype=np.float32)
    i = np.linspace(0.0, 1.0, 256, dtype=np.float32)[:, None]
    w = np.clip((i - 0.55) / 0.45, 0, 1) ** 1.5 * look["highlight_mix"]
    lut = i * ((1 - w) * base[None, :] + w * hi[None, :]) * 255.0
    return lut.astype(np.float32), hi * 255.0, base * 255.0


def _cycles(rate_hz, duration_sec, periodic, minimum=0):
    """A frequency, snapped to a whole number of cycles over the clip when it
    must loop seamlessly."""
    if not periodic:
        return rate_hz
    n = round(rate_hz * duration_sec)
    if minimum and abs(n) < minimum:
        n = minimum if rate_hz >= 0 else -minimum
    return n / duration_sec


def _periodic_noise(w, h, rng, tilt, sigma_frac):
    """A cloud field that tiles seamlessly (FFT noise + Gaussian low-pass done
    in the frequency domain), so it can scroll forever with wrap-around."""
    white = rng.standard_normal((h, w)).astype(np.float32)
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    freq = np.sqrt(fy ** 2 + fx ** 2)
    freq[0, 0] = 1e-6
    sigma = max(2.0, min(w, h) * sigma_frac)
    shape = freq ** (-tilt / 2.0) * np.exp(-2 * (np.pi * sigma * freq) ** 2)
    shape[0, 0] = 0.0
    f = np.fft.irfft2(np.fft.rfft2(white) * shape, s=(h, w)).astype(np.float32)
    f -= f.min()
    f /= f.max() + 1e-9
    return f


class _Motes:
    def __init__(self, iw, ih, rng, topic, D, periodic):
        st = MOTE_STYLE.get(topic, MOTE_STYLE["neutral"])
        n = int(rng.integers(*st["count"]))
        self.iw, self.ih = iw, ih
        self.x0 = rng.uniform(0, iw, n)
        self.y0 = rng.uniform(0, ih, n)
        sign = rng.choice([-1, 1]) if topic == "wind" else 1
        vx = sign * rng.uniform(*st["vx"], n)
        vy = rng.uniform(*st["vy"], n)
        # whole laps across the frame per loop, so particles end where they began
        self.vx = np.array([_cycles(v / iw, D, periodic) * iw for v in vx])
        self.vy = np.array([_cycles(v / ih, D, periodic) * ih for v in vy])
        self.sway_a = rng.uniform(1.0, 4.0, n)
        self.sway_f = np.array([_cycles(f, D, periodic, 1) for f in rng.uniform(0.03, 0.12, n)])
        self.tw_f = np.array([_cycles(f, D, periodic, 1) for f in rng.uniform(0.05, 0.35, n)])
        self.phase = rng.uniform(0, 2 * np.pi, n)
        self.tw = st["twinkle"]
        self.bright = rng.uniform(0.35, 1.0, n)
        sizes = rng.uniform(*st["size"], n)
        self.R = 8
        self.sprites, self.kind = [], np.digitize(sizes, [1.3, 1.9])
        for sig in (1.0, 1.6, 2.3):
            yy, xx = np.mgrid[-self.R:self.R + 1, -self.R:self.R + 1]
            self.sprites.append(np.exp(-(xx ** 2 + yy ** 2) / (2 * sig ** 2)).astype(np.float32))
        self.canvas = np.zeros((ih + 2 * self.R, iw + 2 * self.R), np.float32)

    def __call__(self, t):
        c, R = self.canvas, self.R
        c.fill(0)
        x = (self.x0 + self.vx * t + self.sway_a * np.sin(2 * np.pi * self.sway_f * t + self.phase)) % self.iw
        y = (self.y0 + self.vy * t) % self.ih
        b = self.bright * (1 - self.tw + self.tw * (0.5 + 0.5 * np.sin(2 * np.pi * self.tw_f * t + self.phase)))
        for xi, yi, bi, k in zip(x.astype(int), y.astype(int), b, self.kind):
            c[yi:yi + 2 * R + 1, xi:xi + 2 * R + 1] += bi * self.sprites[k]
        return c[R:R + self.ih, R:R + self.iw]


class _Bands:
    """Slow aurora / light-curtain bands that wave across the frame."""
    def __init__(self, iw, ih, rng, topic, D, periodic):
        self.ih, self.iw = ih, iw
        self.bands = []
        xs = np.arange(iw, dtype=np.float32) / iw
        for _ in range(int(rng.integers(2, 4))):
            self.bands.append(dict(
                y0=rng.uniform(0.2, 0.8) * ih, amp=rng.uniform(0.04, 0.14) * ih,
                k=rng.uniform(0.4, 1.6), w=_cycles(rng.choice([-1, 1]) * rng.uniform(0.004, 0.02), D, periodic, 1),
                k2=rng.uniform(1.0, 3.0), w2=_cycles(rng.uniform(0.003, 0.015), D, periodic, 1),
                ph=rng.uniform(0, 2 * np.pi), s=rng.uniform(0.25, 0.5)))
        self.xs = xs
        width = rng.uniform(0.05, 0.12) * ih
        d = np.arange(-2 * ih, 2 * ih + 1, dtype=np.float32)
        self.prof = np.exp(-(d / width) ** 2).astype(np.float32)
        self.yy = np.arange(ih, dtype=np.float32)[:, None]
        self.off = 2 * ih

    def __call__(self, t):
        out = np.zeros((self.ih, self.iw), np.float32)
        for b in self.bands:
            yc = b["y0"] + b["amp"] * np.sin(2 * np.pi * (b["k"] * self.xs + b["w"] * t) + b["ph"])
            shimmer = 0.55 + 0.45 * np.sin(2 * np.pi * (b["k2"] * self.xs + b["w2"] * t) + b["ph"])
            idx = (self.yy - yc[None, :]).astype(np.int32) + self.off
            out += self.prof[idx] * (b["s"] * shimmer)[None, :]
        return out


class _Ripples:
    """Soft rings spreading out from a point -- rain on a pond, a pulse in space."""
    def __init__(self, iw, ih, rng, topic, D, periodic):
        cx, cy = rng.uniform(0.15, 0.85) * iw, rng.uniform(0.2, 0.8) * ih
        yy, xx = np.mgrid[0:ih, 0:iw].astype(np.float32)
        r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        lam = rng.uniform(0.06, 0.14) * min(iw, ih) + 8
        self.r_l = (r / lam).astype(np.float32)
        self.v = _cycles(rng.uniform(4, 12) / lam, D, periodic, 1)  # rings per second
        self.fall = (np.exp(-r / (0.4 * max(iw, ih))) * rng.uniform(0.15, 0.3)).astype(np.float32)
        p = np.linspace(0, 1, 256, endpoint=False)
        self.lut = ((0.5 + 0.5 * np.cos(2 * np.pi * p)) ** 3).astype(np.float32)

    def __call__(self, t):
        phase = (self.r_l - self.v * t) % 1.0
        return self.lut[(phase * 255).astype(np.uint8)] * self.fall


class _Parallax:
    """A second, finer cloud drifting a different way -- depth, like mist
    passing in front of the main field."""
    def __init__(self, iw, ih, rng, topic, D, periodic):
        H, W = ih, iw
        f = _periodic_noise(W, H, rng, tilt=rng.uniform(1.2, 2.0), sigma_frac=rng.uniform(0.012, 0.03))
        f = np.clip((f - 0.45) / 0.55, 0, 1) ** 1.6
        self.f = np.tile(f, (2, 2)).astype(np.float32) * rng.uniform(0.3, 0.55)
        ang = rng.uniform(0, 2 * np.pi)
        speed = rng.uniform(3, 9)
        self.vx = _cycles(np.cos(ang) * speed / W, D, periodic) * W
        self.vy = _cycles(np.sin(ang) * speed / H, D, periodic) * H
        if periodic and self.vx == 0 and self.vy == 0:
            self.vx = W / D
        self.W, self.H = W, H

    def __call__(self, t):
        ox = int(self.vx * t) % self.W
        oy = int(self.vy * t) % self.H
        return self.f[oy:oy + self.H, ox:ox + self.W]


class _Glow:
    """A soft light that wanders slowly around the frame."""
    def __init__(self, iw, ih, rng, D, periodic):
        yy, xx = np.mgrid[-ih:ih, -iw:iw].astype(np.float32)
        rad = rng.uniform(0.25, 0.45) * max(iw, ih)
        self.blob = (np.exp(-(xx ** 2 + yy ** 2) / (2 * rad ** 2)) * rng.uniform(0.15, 0.3)).astype(np.float32)
        self.fx = _cycles(rng.uniform(0.002, 0.01), D, periodic, 1)
        self.fy = _cycles(rng.uniform(0.002, 0.01), D, periodic, 1)
        self.ph = rng.uniform(0, 2 * np.pi, 2)
        self.iw, self.ih = iw, ih

    def __call__(self, t):
        cx = 0.5 + 0.3 * np.sin(2 * np.pi * self.fx * t + self.ph[0])
        cy = 0.5 + 0.3 * np.sin(2 * np.pi * self.fy * t + self.ph[1])
        ox = int((1 - cx) * self.iw)
        oy = int((1 - cy) * self.ih)
        return self.blob[oy:oy + self.ih, ox:ox + self.iw]


LAYER_CLASSES = {"motes": _Motes, "bands": _Bands, "ripples": _Ripples, "parallax": _Parallax}


def frame_maker(duration_sec, iw, ih, color, seed, topic="neutral", periodic=False, variant=None,
                dim=1.0):
    """(n_frames, frame(i) -> HxWx3 uint8, look). frame(n_frames) equals
    frame(0) when periodic -- that is what makes the loop seamless."""
    profile = TOPIC_PROFILES.get(topic, TOPIC_PROFILES["neutral"])
    rng = np.random.default_rng(seed)
    max_dx = _even(iw * PAN_MARGIN)
    max_dy = _even(ih * PAN_MARGIN)
    field = _noise_field(iw + max_dx, ih + max_dy, rng,
                          tilt=profile["tilt"], blur_frac=profile["blur_frac"])
    n_frames = int(round(duration_sec * FPS))
    dxs, dys = _pan_path(n_frames, duration_sec, max_dx, max_dy, rng, profile, periodic)

    look = pick_look(seed, topic, variant)
    lrng = np.random.default_rng([abs(int(seed)), 104729])
    if look["flip_x"]:
        field = field[:, ::-1]
    if look["flip_y"]:
        field = field[::-1, :]
    field_idx = np.ascontiguousarray((np.clip(field, 0, 1) * 255).astype(np.uint8))
    lut, hi_rgb, base_rgb = _palette(color, look)
    lut = lut * dim  # dim < 1: a near-dark picture for sleep channels
    layer = LAYER_CLASSES[look["layer"]](iw, ih, lrng, topic, duration_sec, periodic)
    glow = _Glow(iw, ih, lrng, duration_sec, periodic) if look["glow"] else None
    hi = (hi_rgb * look["strength"] * dim).astype(np.float32)
    glow_k = float(np.mean(base_rgb) / max(1.0, np.mean(hi)) * 1.4)
    buf = np.empty((ih, iw, 3), np.float32)

    def frame(i):
        t = i / FPS
        j = i % n_frames
        rgb = np.take(lut, field_idx[dys[j]:dys[j] + ih, dxs[j]:dxs[j] + iw], axis=0)
        light = layer(t)
        if glow is not None:
            light = light + glow(t) * glow_k
        np.multiply(light[:, :, None], hi, out=buf)
        rgb += buf
        return np.clip(rgb, 0, 255, out=rgb).astype(np.uint8)

    return n_frames, frame, look


def render_frames(out_pipe, duration_sec, iw, ih, color, seed, topic="neutral", periodic=False,
                  variant=None, dim=1.0):
    n_frames, frame, look = frame_maker(duration_sec, iw, ih, color, seed, topic, periodic, variant,
                                        dim)
    print(f"Look: {look}")
    for i in range(n_frames):
        out_pipe.write(frame(i).tobytes())


def loop_period(period, segment_sec):
    """Nearest flicker period that fits a whole number of times into the
    segment, so the brightness pulse is continuous across the loop point."""
    return segment_sec / max(1, round(segment_sec / period))


def build_ffmpeg_command(audio_path, duration_sec, width, height, out_path, iw, ih, icon,
                          topic="neutral", periodic=False):
    """Encode the piped frames. audio_path=None renders a silent, loopable
    video-only segment (see main's --segment-seconds)."""
    profile = TOPIC_PROFILES.get(topic, TOPIC_PROFILES["neutral"])
    period = profile["flicker_period"]
    if periodic:
        period = loop_period(period, duration_sec)
    icon_w = _even(width * 0.09)
    filter_complex = (
        f"[0:v]eq=saturation={profile['saturation']}:contrast={profile['contrast']}:"
        f"brightness='{profile['flicker_amp']}*sin(2*PI*t/{period:g})':eval=frame,"
        f"vignette={profile['vignette']},scale={width}:{height}:flags=lanczos,format=rgba[bg];"
        f"[1:v]scale={icon_w}:-1,colorchannelmixer=aa=0.32[icon];"
        f"[bg][icon]overlay=W-w-{_even(width*0.03)}:H-h-{_even(height*0.03)}:format=auto,"
        f"format=yuv420p[vout]"
    )
    cmd = ["ffmpeg", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{iw}x{ih}", "-r", str(FPS),
           "-i", "pipe:0",
           "-i", icon]
    if audio_path:
        cmd += ["-i", audio_path]
    cmd += ["-filter_complex", filter_complex, "-map", "[vout]"]
    if audio_path:
        cmd += ["-map", "2:a", "-t", str(duration_sec), "-r", str(FPS),
                "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-shortest", out_path]
    else:
        cmd += ["-an", "-t", str(duration_sec), "-r", str(FPS),
                "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", out_path]
    return cmd


def loop_mux_command(segment_path, audio_path, duration_sec, out_path):
    """Repeat the seamless video segment and the (separately seamless) audio
    loop out to the full length -- stream copy, so a 10h video takes minutes."""
    return ["ffmpeg", "-y",
            "-stream_loop", "-1", "-i", segment_path,
            "-stream_loop", "-1", "-i", audio_path,
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-t", str(duration_sec), "-movflags", "+faststart", out_path]


def render(audio, duration, width, height, color, icon, topic, seed, out, periodic=False,
           variant=None, dim=1.0):
    iw = _even(width * INTERNAL_SCALE)
    ih = _even(height * INTERNAL_SCALE)
    cmd = build_ffmpeg_command(audio, duration, width, height, out, iw, ih, icon, topic, periodic)
    print("Running:", " ".join(cmd))
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        render_frames(proc.stdin, duration, iw, ih, color, seed, topic, periodic, variant, dim)
    finally:
        proc.stdin.close()
    ret = proc.wait()
    if ret != 0:
        raise subprocess.CalledProcessError(ret, cmd)


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
    p.add_argument("--segment-seconds", type=float, default=0,
                   help="long videos: render only this many seconds of seamlessly "
                        "loopable animation, then loop it (and --audio, itself a "
                        "seamless loop) out to --duration-seconds. 0 = animate it all.")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--variant", type=int, default=None,
                   help="the upload's Vol. number: cycles the animated layer so two "
                        "consecutive uploads of a theme never share a look")
    p.add_argument("--dim", type=float, default=1.0,
                   help="overall brightness, 0..1 (e.g. 0.45 keeps a sleep channel near-dark)")
    p.add_argument("--out", default="animated.mp4")
    args = p.parse_args()

    seg = args.segment_seconds
    if 0 < seg < args.duration_seconds:
        segment = args.out + ".segment.mp4"
        render(None, seg, args.width, args.height, args.color, args.icon, args.topic,
               args.seed, segment, periodic=True, variant=args.variant, dim=args.dim)
        cmd = loop_mux_command(segment, args.audio, args.duration_seconds, args.out)
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=True)
        os.remove(segment)
    else:
        render(args.audio, args.duration_seconds, args.width, args.height, args.color,
               args.icon, args.topic, args.seed, args.out, variant=args.variant, dim=args.dim)
    print(f"Wrote {args.out} ({args.duration_seconds:.0f}s, {args.width}x{args.height})")


if __name__ == "__main__":
    main()
