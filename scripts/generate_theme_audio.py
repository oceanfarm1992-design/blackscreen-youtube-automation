#!/usr/bin/env python3
"""
Synthesize original ambient audio for one of the four channel themes.

    rain      - gentle rainfall + distant thunder + soft ambient pads
    waterfall - steady flowing water + low rumble + gentle harmony
    forest    - soft wind gusts + random water drops + occasional bird chirps + pad
    sleeping  - deep drone + slow evolving chords + subtle delta-rate tremolo

Two modes:
    --seconds 59            produce an exact-length clip (used for the 59s Short)
    --loop-seconds 120      produce a seamless, crossfaded loop (stretched to hours
                            later by make_video.py via ffmpeg -stream_loop)

Everything is generated from numpy (no samples, no external audio), so every render
is original. Vary --seed per run so consecutive uploads are not identical.

Design note: colored/filtered noise is produced in the frequency domain (one FFT +
one inverse FFT), which is fast even for multi-minute loops, instead of per-sample
IIR filtering in a Python loop.
"""
import argparse

import numpy as np
import soundfile as sf

SR = 44100


# --------------------------------------------------------------------------- #
# Building blocks
# --------------------------------------------------------------------------- #
def _t(n: int) -> np.ndarray:
    return np.arange(n) / SR


def colored_noise(n, rng, tilt=1.0, highpass=None, lowpass=None):
    """
    Noise shaped in the frequency domain.
    tilt: spectral slope (0=white, 1=pink, 2=brown/red). Higher = darker/deeper.
    highpass/lowpass: soft roll-off corner frequencies in Hz.
    """
    white = rng.standard_normal(n)
    spec = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n, 1.0 / SR)
    shape = np.ones_like(freqs)
    nz = freqs > 0
    shape[nz] = 1.0 / (freqs[nz] ** (tilt / 2.0))
    shape[0] = 0.0
    if highpass:
        shape *= freqs / np.sqrt(freqs**2 + highpass**2)  # 1st-order HPF magnitude
    if lowpass:
        shape *= lowpass / np.sqrt(freqs**2 + lowpass**2)  # 1st-order LPF magnitude
    out = np.fft.irfft(spec * shape, n=n)
    return _norm(out)


def slow_env(n, rng, rate_hz=0.1, depth=0.3):
    """A slowly varying gain envelope in [1-depth, 1+depth] (for gusts/intensity)."""
    ctrl = colored_noise(n, rng, tilt=2.0, lowpass=max(0.05, rate_hz))
    ctrl = ctrl / (np.max(np.abs(ctrl)) + 1e-9)
    return 1.0 + depth * ctrl


def _norm(x, peak=1.0):
    m = np.max(np.abs(x)) + 1e-9
    return x * (peak / m)


def sine(freq, n, phase=0.0):
    return np.sin(2 * np.pi * freq * _t(n) + phase)


def pad_layer(n, rng, roots, detune=0.004, amp=0.12):
    """Soft sustained chord pad from stacked, slightly detuned sines."""
    out = np.zeros(n)
    for f in roots:
        for k in (1.0, 1 + detune, 1 - detune):
            out += sine(f * k, n, phase=rng.uniform(0, 2 * np.pi))
    env = 0.5 - 0.5 * np.cos(2 * np.pi * np.minimum(_t(n), _t(n)[::-1]) / _t(n)[-1])
    return amp * _norm(out) * (0.6 + 0.4 * slow_env(n, rng, 0.03, 0.5))


def sprinkle(n, rng, count, make_event):
    """Place `count` short events (returned by make_event(dur_n, rng)) at random spots."""
    out = np.zeros(n)
    for _ in range(count):
        ev = make_event(rng)
        start = rng.integers(0, max(1, n - len(ev)))
        out[start:start + len(ev)] += ev
    return out


def _thunder_event(rng):
    dur = rng.uniform(3.0, 7.0)
    m = int(dur * SR)
    rumble = colored_noise(m, rng, tilt=2.4, lowpass=180)
    sub = sine(rng.uniform(38, 60), m)
    env = np.exp(-np.linspace(0, 5, m)) * (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, m)))
    return 0.35 * env * (0.7 * rumble + 0.3 * sub)


def _drop_event(rng):
    dur = rng.uniform(0.08, 0.18)
    m = int(dur * SR)
    f = rng.uniform(900, 2600)
    env = np.exp(-np.linspace(0, 22, m))
    return 0.25 * env * sine(f, m)


def _bird_event(rng):
    dur = rng.uniform(0.12, 0.35)
    m = int(dur * SR)
    f0, f1 = rng.uniform(1800, 3200), rng.uniform(2600, 4200)
    sweep = np.linspace(f0, f1, m)
    phase = 2 * np.pi * np.cumsum(sweep) / SR
    trill = 1 + 0.15 * np.sin(2 * np.pi * rng.uniform(18, 30) * _t(m))
    env = np.sin(np.linspace(0, np.pi, m)) ** 2
    return 0.14 * env * np.sin(phase) * trill


# --------------------------------------------------------------------------- #
# Theme synths -> return mono float array
# --------------------------------------------------------------------------- #
def synth_rain(n, rng):
    base = colored_noise(n, rng, tilt=0.9, highpass=200, lowpass=7000)
    base *= slow_env(n, rng, rate_hz=0.12, depth=0.18)
    thunder = sprinkle(n, rng, count=max(1, n // (SR * 90)), make_event=_thunder_event)
    pad = pad_layer(n, rng, roots=[130.81, 196.00, 261.63])  # C3 G3 C4
    return _norm(0.7 * base + thunder + 0.5 * pad, 0.9)


def synth_waterfall(n, rng):
    base = colored_noise(n, rng, tilt=1.2, highpass=350, lowpass=9000)
    base *= slow_env(n, rng, rate_hz=0.2, depth=0.08)  # steadier than rain
    rumble = colored_noise(n, rng, tilt=2.2, lowpass=140)
    pad = pad_layer(n, rng, roots=[146.83, 220.00, 293.66], amp=0.10)  # D3 A3 D4
    return _norm(0.72 * base + 0.18 * rumble + 0.45 * pad, 0.9)


def synth_forest(n, rng):
    wind = colored_noise(n, rng, tilt=1.4, lowpass=1500)
    wind *= slow_env(n, rng, rate_hz=0.05, depth=0.45)
    drops = sprinkle(n, rng, count=max(4, n // (SR * 4)), make_event=_drop_event)
    birds = sprinkle(n, rng, count=max(2, n // (SR * 12)), make_event=_bird_event)
    pad = pad_layer(n, rng, roots=[164.81, 246.94, 329.63], amp=0.08)  # E3 B3 E4
    return _norm(0.45 * wind + 0.9 * drops + birds + 0.4 * pad, 0.9)


def synth_sleeping(n, rng):
    drone = np.zeros(n)
    for f in (55.0, 82.41, 110.0):  # A1 E2 A2
        drone += sine(f, n, rng.uniform(0, 2 * np.pi))
        drone += sine(f * (1 + 0.003), n, rng.uniform(0, 2 * np.pi))  # slow beating
    chord = pad_layer(n, rng, roots=[220.00, 261.63, 329.63, 392.00], detune=0.005, amp=0.16)
    delta = 1 + 0.08 * np.sin(2 * np.pi * 2.0 * _t(n))  # subtle ~2 Hz tremolo
    mix = 0.5 * _norm(drone) + chord
    return _norm(mix * delta, 0.85)


SYNTHS = {
    "rain": synth_rain,
    "waterfall": synth_waterfall,
    "forest": synth_forest,
    "sleeping": synth_sleeping,
}


# --------------------------------------------------------------------------- #
def to_stereo(mono, rng, width=0.25):
    """Add gentle stereo width via a decorrelated, quieter side channel."""
    side = colored_noise(len(mono), rng, tilt=1.0)
    left = mono + width * side
    right = mono - width * side
    return np.stack([_norm(left, 0.9), _norm(right, 0.9)], axis=1)


def crossfade_loop(audio, crossfade_sec=3.0):
    """Crossfade the tail into the head so the loop point is inaudible."""
    nfx = int(crossfade_sec * SR)
    if nfx * 2 >= len(audio):
        return audio
    fin = np.linspace(0, 1, nfx)[:, None]
    fout = np.linspace(1, 0, nfx)[:, None]
    head = audio[:nfx] * fin + audio[-nfx:] * fout
    return np.concatenate([head, audio[nfx:-nfx]])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--theme", required=True, choices=list(SYNTHS.keys()))
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--seconds", type=float, help="exact clip length (for the 59s Short)")
    g.add_argument("--loop-seconds", type=float, help="seamless loop length (for long-form)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="audio.wav")
    args = p.parse_args()

    rng = np.random.default_rng(args.seed)
    length = args.seconds if args.seconds else args.loop_seconds
    n = int(length * SR)

    mono = SYNTHS[args.theme](n, rng)
    stereo = to_stereo(mono, rng)
    if args.loop_seconds:
        stereo = crossfade_loop(stereo)

    sf.write(args.out, stereo, SR)
    print(f"Wrote {args.out}: {len(stereo)/SR:.2f}s, theme={args.theme}, seed={args.seed}")


if __name__ == "__main__":
    main()
