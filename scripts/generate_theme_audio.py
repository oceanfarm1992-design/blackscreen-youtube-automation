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
# Wellness frequency reference tables
#
# These are tuning values only. The "purpose" labels are the descriptions used
# by the meditation/wellness market for SEO; they are NOT medical claims and no
# clinical efficacy is implied or asserted by this code.
# --------------------------------------------------------------------------- #
SOLFEGGIO = {  # Hz -> common label
    "174": 174.0,  # grounding
    "285": 285.0,  # tissue / cell
    "396": 396.0,  # releasing fear
    "417": 417.0,  # change / clearing
    "528": 528.0,  # "miracle tone"
    "639": 639.0,  # relationships
    "741": 741.0,  # detox / solving
    "852": 852.0,  # awareness
    "963": 963.0,  # "pineal"
}
TUNING_432 = 432.0  # alternative concert pitch (vs standard 440 Hz)

# Brainwave-entrainment beat rates (Hz). Bands use a representative mid-value.
BRAINWAVE = {
    "delta": 2.5,     # 0.5-4 Hz   deep sleep
    "theta": 6.0,     # 4-8 Hz     meditation / REM
    "alpha": 10.0,    # 8-13 Hz    calm wakefulness
    "schumann": 7.83, # Earth resonance
    "beta": 18.0,     # 13-30 Hz   alert / active thinking
    "gamma": 40.0,    # 30-100 Hz  focus / productivity
}


def resolve_tone(s):
    """A Solfeggio key ('528'), '432', or any Hz number -> float; 'none' -> None."""
    if not s or str(s).lower() == "none":
        return None
    if s in SOLFEGGIO:
        return SOLFEGGIO[s]
    return float(s)


def resolve_tones(s):
    """One or more carrier freqs: a single Solfeggio key/'432'/Hz number, or a
    comma-separated combo like '432,528,741'. Returns a list (possibly empty)."""
    if not s or str(s).lower() == "none":
        return []
    return [resolve_tone(part.strip()) for part in str(s).split(",") if part.strip()]


def resolve_beat(s):
    """A band name ('delta'/'theta'/'alpha'/'schumann') or any Hz number -> float."""
    if not s or str(s).lower() == "none":
        return None
    if str(s).lower() in BRAINWAVE:
        return BRAINWAVE[str(s).lower()]
    return float(s)


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


def lowpass(x, corner, order=2):
    """Zero-phase low-pass in the frequency domain (Butterworth-magnitude).

    Used to tame the hollow/tinny highs of stacked pure sines so tonal themes
    sound warm rather than like an old radio.
    """
    n = len(x)
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, 1.0 / SR)
    mag = 1.0 / np.sqrt(1.0 + (freqs / corner) ** (2 * order))
    return np.fft.irfft(spec * mag, n=n)


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


def _droplet(rng):
    """One resonant water drop: a short 'plink' that falls in pitch (watery
    'ploop'), plus a tiny lower body, exponential decay."""
    dur = rng.uniform(0.10, 0.22)
    m = int(dur * SR)
    f0 = rng.uniform(1100, 1800)
    f1 = f0 * rng.uniform(0.45, 0.6)
    sweep = np.linspace(f0, f1, m)
    ph = 2 * np.pi * np.cumsum(sweep) / SR
    env = np.exp(-np.linspace(0, 30, m))
    body = 0.25 * np.sin(2 * np.pi * f1 * _t(m)) * np.exp(-np.linspace(0, 18, m))
    return env * np.sin(ph) + body


def _slow_drops(n, rng, mean_gap=1.9):
    """Sparse droplets with long, varied gaps so they're heard drop by drop."""
    out = np.zeros(n)
    pos = int(rng.uniform(0.2, mean_gap) * SR)
    while pos < n:
        d = _droplet(rng) * rng.uniform(0.6, 1.0)
        e = min(n, pos + len(d))
        out[pos:e] += d[:e - pos]
        pos += int(rng.uniform(0.6, 1.6) * mean_gap * SR)
    return out


def synth_rain_drops(n, rng):
    """Soft, gentle rain (NO thunder) with slow individual water drops on top,
    each drop given a little reverb so it 'plinks' with air around it. The rain
    bed is thin and quiet (a distant patter), so it reads as light rain rather
    than a downpour, with the drops clearly on top."""
    bed = colored_noise(n, rng, tilt=0.7, highpass=700, lowpass=4500)
    bed *= slow_env(n, rng, rate_hz=0.08, depth=0.16)
    drops = reverb(_norm(_slow_drops(n, rng, mean_gap=2.1), 0.8), rng, decay=2.2, mix=0.3)
    return _norm(0.26 * bed + 1.0 * drops, 0.9)


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
    # Foundation kept in the 110-220 Hz range so it is audible on laptop/phone
    # speakers (a 55 Hz drone is inaudible there and reads as silence + hiss).
    drone = np.zeros(n)
    for f in (110.0, 164.81, 220.00):  # A2 E3 A3
        drone += sine(f, n, rng.uniform(0, 2 * np.pi))
        drone += sine(f * (1 + 0.0015), n, rng.uniform(0, 2 * np.pi))  # gentle beating
    sub = sine(55.0, n, rng.uniform(0, 2 * np.pi))  # light sub-bass for headphones
    # Prominent mid-range pad carries the melody on small speakers.
    chord = pad_layer(n, rng, roots=[220.00, 261.63, 329.63, 392.00], detune=0.003, amp=0.24)
    warm = lowpass(0.4 * _norm(drone) + 0.18 * sub + chord, corner=1600)
    # Very slow swell instead of a 2 Hz flutter (which reads as warble/wobble).
    delta = 1 + 0.04 * np.sin(2 * np.pi * 0.1 * _t(n))
    return _norm(warm * delta, 0.9)


def _pluck(freq, dur, rng, bright=1.4):
    """An additive plucked-string tone (tanpura/sitar-like) with harmonic shimmer."""
    m = int(dur * SR)
    t = _t(m)
    out = np.zeros(m)
    n_harm = int(min(24, (SR / 2.0) / freq))
    for h in range(1, n_harm + 1):
        amp = 1.0 / (h ** (1.2 / bright))
        hdecay = np.exp(-t * (1.5 + 0.5 * h) / dur)
        out += amp * hdecay * np.sin(2 * np.pi * freq * h * t + rng.uniform(0, 2 * np.pi))
    attack = np.minimum(1.0, t * 400.0)
    return _norm(out) * attack


def tanpura(n, rng, sa=220.0, pluck_sec=1.1):
    """Repeating tanpura cycle: Pa - Sa - Sa - Sa(low), plucks ringing into each other."""
    seq = [sa * 0.75, sa, sa, sa * 0.5]  # Pa (lower 5th), Sa, Sa, Sa (lower octave)
    out = np.zeros(n)
    pos, i = 0, 0
    ring = pluck_sec * 3.2               # each pluck rings well past the next
    while pos < n:
        ev = 0.5 * _pluck(seq[i % len(seq)], ring, rng, bright=1.6)
        end = min(n, pos + len(ev))
        out[pos:end] += ev[:end - pos]
        pos += int(pluck_sec * SR)
        i += 1
    return out


def _indian_melody(n, rng, sa=220.0):
    """Sparse bansuri-style flute over Raga Bhupali (S R G P D), with meend glides."""
    scale = np.array([sa * r for r in (5 / 6, 1, 9 / 8, 5 / 4, 3 / 2, 5 / 3, 2)])
    out = np.zeros(n)
    pos, prev = 0, None
    while pos < n:
        note = float(rng.choice(scale))
        dur = rng.uniform(1.8, 3.8)
        m = int(dur * SR)
        t = _t(m)
        if prev is not None and rng.random() < 0.45:
            f = np.linspace(prev, note, m)          # meend: glide from previous note
        else:
            f = np.full(m, note)
        vib = 1.0 + 0.006 * np.sin(2 * np.pi * 5.0 * t)   # gentle flute vibrato
        phase = 2 * np.pi * np.cumsum(f * vib) / SR
        tone = np.sin(phase) + 0.15 * np.sin(2 * phase)   # soft 2nd harmonic
        breath = 0.03 * colored_noise(m, rng, tilt=1.0, highpass=2000, lowpass=6000)
        env = np.sin(np.linspace(0, np.pi, m)) ** 1.5     # soft swell in and out
        seg = min(n - pos, m)
        out[pos:pos + seg] += (0.5 * env * tone + env * breath)[:seg]
        prev = note
        pos += m + int(rng.uniform(0.6, 2.2) * SR)        # long rests -> sleepy
    return _norm(out)


def synth_indian(n, rng):
    sa = 220.0
    drone = tanpura(n, rng, sa=sa)
    melody = _indian_melody(n, rng, sa=sa)
    pad = pad_layer(n, rng, roots=[sa * 0.5, sa * 0.75, sa], amp=0.08)  # Sa Pa Sa support
    warm = lowpass(0.6 * _norm(drone) + 0.4 * melody + pad, corner=2500)
    return _norm(warm, 0.9)


def progression_pad(n, rng, chords, chord_sec=8.0, amp=0.18, detune=0.004):
    """Sustained chord pad that steps through `chords` (lists of Hz), crossfading."""
    out = np.zeros(n)
    seg = int(chord_sec * SR)
    xf = int(min(1.5, chord_sec * 0.3) * SR)
    pos, i = 0, 0
    while pos < n:
        L = min(seg + xf, n - pos)
        if L <= 0:
            break
        t = _t(L)
        chord = np.zeros(L)
        for f in chords[i % len(chords)]:
            for k in (1.0, 1 + detune, 1 - detune):
                chord += np.sin(2 * np.pi * f * k * t + rng.uniform(0, 2 * np.pi))
        env = np.ones(L)
        fi = min(xf, L // 2)
        if fi > 0:
            env[:fi] = np.linspace(0, 1, fi)
            env[-fi:] = np.linspace(1, 0, fi)
        out[pos:pos + L] += amp * _norm(chord) * env
        pos += seg
        i += 1
    return out


def _bell(freq, dur, rng):
    """Soft music-box / celesta note: quick-decaying bell partials."""
    m = int(dur * SR)
    t = _t(m)
    out = np.zeros(m)
    for r, w in ((1.0, 1.0), (2.0, 0.5), (3.0, 0.25), (4.2, 0.12)):
        out += w * np.exp(-t * 3.0 / dur * (1 + 0.2 * r)) * \
            np.sin(2 * np.pi * freq * r * t + rng.uniform(0, 2 * np.pi))
    return _norm(out) * np.minimum(1.0, t * 300.0)


def _warm_note(freq, dur, rng):
    """Sustained warm note (sax/rhodes-ish) with gentle vibrato, for intimate moods."""
    m = int(dur * SR)
    t = _t(m)
    vib = 1.0 + 0.008 * np.sin(2 * np.pi * 5.0 * t)
    ph = 2 * np.pi * np.cumsum(freq * vib) / SR
    tone = np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    env = np.sin(np.linspace(0, np.pi, m)) ** 1.2
    return _norm(tone * env)


def _sparse_melody(n, rng, scale, gap=(1.0, 3.0), dur=(0.8, 2.0), amp=0.3, maker=_bell):
    """Place notes from `scale` (Hz array) at random spots with rests between them."""
    out = np.zeros(n)
    pos = 0
    while pos < n:
        ev = amp * maker(float(rng.choice(scale)), rng.uniform(*dur), rng)
        end = min(n, pos + len(ev))
        out[pos:end] += ev[:end - pos]
        pos += int(rng.uniform(*gap) * SR)
    return out


def synth_romantic(n, rng):
    """Warm 'love' music: lush major-7th progression + soft music-box melody."""
    chords = [
        [261.63, 329.63, 392.00, 493.88],  # Cmaj7
        [220.00, 261.63, 329.63, 392.00],  # Am7
        [174.61, 220.00, 261.63, 329.63],  # Fmaj7
        [196.00, 246.94, 293.66, 349.23],  # G7
    ]
    pad = progression_pad(n, rng, chords, chord_sec=8.0, amp=0.18)
    scale = np.array([261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25])
    melody = _sparse_melody(n, rng, scale, gap=(1.2, 3.2), dur=(0.8, 1.8), amp=0.30, maker=_bell)
    warm = lowpass(pad + melody, corner=3000)
    return _norm(warm, 0.9)


def synth_romantic_night(n, rng):
    """Slow, low, smoky 'bedroom love' mood: minor-7th changes + sultry warm melody."""
    chords = [
        [110.00, 130.81, 164.81, 196.00],  # Am7
        [146.83, 174.61, 220.00, 261.63],  # Dm7
        [174.61, 220.00, 261.63, 329.63],  # Fmaj7
        [164.81, 196.00, 246.94, 293.66],  # Em7
    ]
    pad = progression_pad(n, rng, chords, chord_sec=12.0, amp=0.20, detune=0.005)
    scale = np.array([146.83, 164.81, 196.00, 220.00, 261.63, 293.66, 329.63])
    melody = _sparse_melody(n, rng, scale, gap=(2.0, 5.0), dur=(2.0, 4.0), amp=0.26, maker=_warm_note)
    warm = lowpass(pad + melody, corner=1800)
    return _norm(warm, 0.9)


SYNTHS = {
    "rain": synth_rain,
    "rain_drops": synth_rain_drops,
    "waterfall": synth_waterfall,
    "forest": synth_forest,
    "sleeping": synth_sleeping,
    "indian": synth_indian,
    "romantic": synth_romantic,
    "romantic_night": synth_romantic_night,
}


# --------------------------------------------------------------------------- #
# Wellness frequency layers (Solfeggio / 432 tone, binaural + isochronic
# brainwave entrainment, Tibetan singing bowl). All mono unless noted.
# --------------------------------------------------------------------------- #
def _edge_fade(x, sec=1.5):
    """Raised-cosine fade in/out to avoid clicks at clip edges."""
    m = min(int(sec * SR), len(x) // 2)
    if m <= 0:
        return x
    w = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, m))
    x = np.array(x, dtype=float)
    x[:m] *= w
    x[-m:] *= w[::-1]
    return x


def tone_drone(n, rng, freq, amp=0.22, soft=False):
    """A warm sustained tone: fundamental + soft harmonics, low-passed, breathing.

    Used for Solfeggio frequencies and 432 Hz tuning so they sound musical
    rather than like a raw test tone.

    soft=True renders a much gentler tone for high Solfeggio carriers
    (741/852/963 Hz) that are fatiguing as bright drones: pure fundamental plus
    a quiet sub-octave for body, NO upper harmonics, a tight low-pass just above
    the fundamental, and a deeper slow swell so it moves instead of staring.
    """
    if soft:
        out = sine(freq, n, phase=rng.uniform(0, 2 * np.pi))
        out += 0.20 * sine(freq / 2.0, n, phase=rng.uniform(0, 2 * np.pi))  # warmth
        out = lowpass(out, corner=freq + 150)
        env = 0.55 + 0.45 * slow_env(n, rng, rate_hz=0.06, depth=1.0)  # breathes more
        return amp * _norm(out) * env
    out = sine(freq, n, phase=rng.uniform(0, 2 * np.pi))
    out += 0.22 * sine(freq * 2, n, phase=rng.uniform(0, 2 * np.pi))
    out += 0.08 * sine(freq * 3, n, phase=rng.uniform(0, 2 * np.pi))
    out = lowpass(out, corner=freq * 3 + 400)
    env = 0.85 + 0.15 * slow_env(n, rng, rate_hz=0.05, depth=1.0)
    return amp * _norm(out) * env


def reverb(x, rng, decay=2.2, mix=0.35):
    """Cheap dark reverb (FFT convolution with a decaying, low-passed noise
    impulse). Smears pure sine tones into a soft wash, which is the single
    biggest thing that stops steady Solfeggio tones sounding like a test tone.
    Works on mono (n,) or stereo (n, 2). `mix` is the wet fraction."""
    ir_len = int(decay * SR)
    tail = rng.standard_normal(ir_len) * np.exp(-5.0 * np.linspace(0, 1, ir_len))
    ir = lowpass(tail, 2500)          # dark reverb tail
    ir = ir / (np.max(np.abs(ir)) + 1e-9)

    def _conv(mono):
        nn = len(mono) + ir_len - 1
        nf = 1 << (nn - 1).bit_length()
        y = np.fft.irfft(np.fft.rfft(mono, nf) * np.fft.rfft(ir, nf), nf)[:len(mono)]
        return y

    wet = _conv(x) if x.ndim == 1 else np.stack([_conv(x[:, 0]), _conv(x[:, 1])], axis=1)
    wet = _norm(wet, 0.9)
    return (1.0 - mix) * x + mix * wet


def binaural(n, rng, carrier, beat, amp=0.20):
    """Binaural beat: L/R detuned by +-beat/2 so the brain perceives `beat` Hz.

    Returns stereo (n, 2). Requires headphones to work as intended.
    """
    ph = rng.uniform(0, 2 * np.pi)
    left = sine(carrier - beat / 2.0, n, phase=ph)
    right = sine(carrier + beat / 2.0, n, phase=ph)
    return amp * np.stack([left, right], axis=1)


def isochronic(n, rng, carrier, beat, amp=0.20, duty=0.5):
    """Isochronic tone: a single carrier pulsed on/off at `beat` Hz.

    Works on speakers (no headphones needed). The gate is a raised-cosine pulse
    so pulses are click-free.
    """
    tone = sine(carrier, n, phase=rng.uniform(0, 2 * np.pi))
    ph = (beat * _t(n)) % 1.0
    gate = np.where(ph < duty, 0.5 - 0.5 * np.cos(2 * np.pi * ph / max(duty, 1e-6)), 0.0)
    return amp * tone * gate


def _bowl_strike(rng, base):
    """One Tibetan-bowl strike: inharmonic partials, mallet transient, long decay."""
    dur = rng.uniform(5.0, 9.0)
    m = int(dur * SR)
    ratios = (1.0, 2.7, 4.9, 7.4, 10.2)   # typical metal-bowl inharmonic series
    weights = (1.0, 0.55, 0.32, 0.18, 0.10)
    out = np.zeros(m)
    for r, w in zip(ratios, weights):
        f = base * r
        beat = rng.uniform(0.5, 1.6)      # shimmer between twin partials
        partial = (sine(f, m, rng.uniform(0, 2 * np.pi))
                   + sine(f + beat, m, rng.uniform(0, 2 * np.pi)))
        decay = np.exp(-np.linspace(0, rng.uniform(3.5, 5.5), m) / (1.0 + r * 0.05))
        out += w * partial * decay
    k = int(0.02 * SR)                     # short mallet contact transient
    out[:k] += 0.3 * np.exp(-np.linspace(0, 60, k)) * rng.standard_normal(k)
    return 0.5 * _edge_fade(_norm(out), 0.03)


def singing_bowl(n, rng, base, period_sec=12.0, amp=0.6):
    """Repeated singing-bowl strikes spaced ~period_sec apart across the clip."""
    out = np.zeros(n)
    t = 0
    while t < n:
        ev = _bowl_strike(rng, base)
        end = min(n, t + len(ev))
        out[t:end] += ev[:end - t]
        t += int(rng.uniform(period_sec * 0.7, period_sec * 1.3) * SR)
    return amp * out


# --------------------------------------------------------------------------- #
def to_stereo(mono, rng, width=0.12):
    """Add gentle stereo width via a decorrelated, quieter side channel.

    width <= 0 returns clean dual-mono with NO added noise (used for pure tone /
    frequency tracks, where any widener noise would read as radio-like hiss).
    The side channel is low-passed so it reads as soft "air" rather than the
    broadband hiss that stands out as static over pure-tone themes.
    """
    if width <= 0:
        s = _norm(mono, 0.9)
        return np.stack([s, s], axis=1)
    side = colored_noise(len(mono), rng, tilt=1.0, lowpass=1200)
    left = mono + width * side
    right = mono - width * side
    return np.stack([_norm(left, 0.9), _norm(right, 0.9)], axis=1)


def crossfade_loop(audio, crossfade_sec=3.0):
    """Crossfade the tail into the head so the loop point is inaudible."""
    nfx = int(crossfade_sec * SR)
    if nfx * 2 >= len(audio):
        return audio
    # Equal-power (constant-energy) crossfade: a linear fade dips ~6 dB in the
    # middle of the seam, which recurs every loop as an audible whoosh/warble.
    t = np.linspace(0, 1, nfx)[:, None]
    fin = np.sqrt(t)
    fout = np.sqrt(1.0 - t)
    head = audio[:nfx] * fin + audio[-nfx:] * fout
    return np.concatenate([head, audio[nfx:-nfx]])


def main():
    p = argparse.ArgumentParser(
        description="Synthesize ambient themes and/or wellness frequency layers "
                    "(Solfeggio, 432 Hz, binaural/isochronic brainwaves, singing bowl).")
    p.add_argument("--theme", default="none", choices=list(SYNTHS.keys()) + ["none"],
                   help="ambient bed, or 'none' for a pure frequency track")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--seconds", type=float, help="exact clip length (for the 59s Short)")
    g.add_argument("--loop-seconds", type=float, help="seamless loop length (for long-form)")

    # Wellness frequency layers (all optional; combine freely with --theme)
    p.add_argument("--tone", default=None,
                   help="carrier/drone freq: a Solfeggio value "
                        f"({'/'.join(SOLFEGGIO)}), '432', any Hz number, or a "
                        "comma-separated combo like '432,528,741'")
    p.add_argument("--beat", default=None,
                   help="brainwave rate: delta/theta/alpha/schumann, or any Hz number")
    p.add_argument("--beat-type", default="binaural", choices=["binaural", "isochronic"],
                   help="binaural needs headphones; isochronic works on speakers")
    p.add_argument("--bowl", action="store_true", help="overlay Tibetan singing-bowl strikes")
    p.add_argument("--tone-soft", action="store_true",
                   help="gentler tone: pure fundamental + sub-octave, no bright harmonics "
                        "(recommended for high Solfeggio carriers 741/852/963 Hz)")
    p.add_argument("--reverb", type=float, default=0.0,
                   help="dark reverb wash, wet fraction 0..1 (e.g. 0.35); 0 = off. "
                        "Softens steady tones so they don't sound like a test tone.")
    p.add_argument("--tone-tilt", type=float, default=0.0,
                   help="de-emphasise high carriers: per-tone gain *= (350/freq)**tilt "
                        "for freq>350Hz. 0=off (equal). ~2 makes 741/852/963 very mild, "
                        "~3 barely-there, while 136/432/528 stay at full level.")
    p.add_argument("--tone-gain", type=float, default=0.22)
    p.add_argument("--beat-gain", type=float, default=0.20)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="audio.wav")
    args = p.parse_args()

    rng = np.random.default_rng(args.seed)
    length = args.seconds if args.seconds else args.loop_seconds
    n = int(length * SR)

    carriers = resolve_tones(args.tone)
    carrier = carriers[0] if carriers else None  # primary, used for beat pairing
    beat = resolve_beat(args.beat)
    layers = []

    # ---- mono bed: ambient theme + tone drone(s) + isochronic + bowl ----
    mono = SYNTHS[args.theme](n, rng) if args.theme != "none" else np.zeros(n)
    if args.theme != "none":
        layers.append(f"theme={args.theme}")

    binaural_carrier = beat is not None and args.beat_type == "binaural"
    # Sustained tone drones. With a binaural beat the primary carrier becomes the
    # L/R binaural pair (added in stereo below), so only the EXTRA combo tones
    # drone here; otherwise every carrier drones. Summed level is kept sane by
    # scaling each tone by 1/sqrt(count).
    drone_tones = carriers[1:] if binaural_carrier else carriers
    if drone_tones:
        amp_each = args.tone_gain / (len(drone_tones) ** 0.5)

        def tilt_gain(freq):
            if args.tone_tilt <= 0 or freq <= 350.0:
                return 1.0
            return (350.0 / freq) ** args.tone_tilt

        for c in drone_tones:
            mono = mono + tone_drone(n, rng, c, amp=amp_each * tilt_gain(c), soft=args.tone_soft)
        label = "+".join(f"{c:g}" for c in drone_tones)
        layers.append(f"tone={label}Hz" + (" soft" if args.tone_soft else "")
                      + (f" tilt{args.tone_tilt:g}" if args.tone_tilt > 0 else ""))
    if beat is not None and args.beat_type == "isochronic":
        mono = mono + isochronic(n, rng, carrier or 200.0, beat, amp=args.beat_gain)
        layers.append(f"isochronic={beat:g}Hz@{carrier or 200:g}Hz")
    if args.bowl:
        mono = mono + singing_bowl(n, rng, base=carrier or 196.0)
        layers.append("bowl")

    if np.max(np.abs(mono)) > 1e-9:
        mono = _norm(mono, 0.9)

    # ---- to stereo, then binaural overlay (must stay L/R distinct) ----
    # Ambient themes want the noise-based widener; pure tone/frequency tracks do
    # not (that noise is the "sss" hiss), so use clean dual-mono for those.
    width = 0.12 if args.theme != "none" else 0.0
    stereo = to_stereo(mono, rng, width=width)
    if binaural_carrier:
        stereo = stereo + binaural(n, rng, carrier or 200.0, beat, amp=args.beat_gain)
        layers.append(f"binaural={beat:g}Hz@{carrier or 200:g}Hz")
    stereo = _norm(stereo, 0.9)

    if args.reverb > 0:
        stereo = reverb(stereo, rng, mix=min(args.reverb, 1.0))
        stereo = _norm(stereo, 0.9)
        layers.append(f"reverb={args.reverb:g}")

    if args.loop_seconds:
        stereo = crossfade_loop(stereo)

    if not layers:
        p.error("nothing to synthesize: give --theme and/or --tone/--beat/--bowl")

    sf.write(args.out, stereo, SR)
    print(f"Wrote {args.out}: {len(stereo)/SR:.2f}s, layers=[{', '.join(layers)}], seed={args.seed}")


if __name__ == "__main__":
    main()
