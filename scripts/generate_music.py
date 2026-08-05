#!/usr/bin/env python3
"""
Generate an ambient/calm music loop and stretch it to a target duration.

Usage:
    python generate_music.py --key C --tempo 60 --loop-minutes 4 \
        --duration-hours 8 --out output.wav

Design notes:
- Synthesizes a short seamless loop directly (sine-wave pad layers over a slow
  chord progression), rather than hours of raw audio.
- Loop-to-length is done by the caller via ffmpeg -stream_loop (see make_video.py),
  not inside this script, so this script only needs to produce a few minutes of audio.
- Vary --key / --tempo / --seed per run so consecutive uploads are not identical
  (see SKILL.md "Volume and policy guardrails").
"""
import argparse
import numpy as np
import soundfile as sf

NOTE_FREQS = {
    "C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23,
    "G": 392.00, "A": 440.00, "B": 493.88,
}

# Simple pentatonic-ish calming progression (scale degrees relative to root)
PROGRESSION = [0, 4, 7, 9]  # e.g. root, major third, fifth, sixth -> calm/open


def make_pad(freq, duration_sec, sample_rate, amp=0.15):
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    # Layer a few harmonics with slow amplitude modulation for a soft pad sound
    wave = (
        np.sin(2 * np.pi * freq * t)
        + 0.5 * np.sin(2 * np.pi * freq * 2 * t)
        + 0.25 * np.sin(2 * np.pi * freq * 3 * t)
    )
    envelope = np.clip(np.minimum(t, duration_sec - t) / 2.0, 0, 1)  # slow fade in/out
    lfo = 1 + 0.05 * np.sin(2 * np.pi * 0.1 * t)  # gentle amplitude wobble
    return amp * wave * envelope * lfo


def generate_loop(key: str, tempo_bpm: int, loop_minutes: float, sample_rate=44100, seed=0):
    rng = np.random.default_rng(seed)
    root = NOTE_FREQS[key]
    beat_sec = 60.0 / tempo_bpm
    chord_sec = beat_sec * 8  # each chord holds for 8 beats -> slow, calm pacing
    total_sec = loop_minutes * 60
    n_chords = max(1, int(total_sec / chord_sec))

    audio = np.zeros(int(total_sec * sample_rate))
    for i in range(n_chords):
        degree = PROGRESSION[i % len(PROGRESSION)]
        freq = root * (2 ** (degree / 12))
        # slight randomized octave layering for texture, seeded for reproducibility
        detune = 1 + rng.uniform(-0.003, 0.003)
        pad = make_pad(freq * detune, chord_sec, sample_rate)
        start = int(i * chord_sec * sample_rate)
        end = start + len(pad)
        if end > len(audio):
            pad = pad[: len(audio) - start]
            end = len(audio)
        audio[start:end] += pad

    audio = audio / max(1.0, np.max(np.abs(audio)) * 1.2)
    return audio, sample_rate


def crossfade_loop_seam(audio: np.ndarray, sample_rate: int, crossfade_sec: float = 2.0):
    """Crossfade the tail into the head so the loop point isn't audible."""
    n = int(crossfade_sec * sample_rate)
    if n * 2 >= len(audio):
        return audio
    fade_out = np.linspace(1, 0, n)
    fade_in = np.linspace(0, 1, n)
    head = audio[:n] * fade_in + audio[-n:] * fade_out
    body = audio[n:-n]
    return np.concatenate([head, body])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--key", default="C", choices=list(NOTE_FREQS.keys()))
    p.add_argument("--tempo", type=int, default=60, help="tempo in BPM, slow=calmer")
    p.add_argument("--loop-minutes", type=float, default=4.0)
    p.add_argument("--seed", type=int, default=0, help="vary per video to avoid identical output")
    p.add_argument("--out", default="loop.wav")
    args = p.parse_args()

    audio, sr = generate_loop(args.key, args.tempo, args.loop_minutes, seed=args.seed)
    audio = crossfade_loop_seam(audio, sr)
    sf.write(args.out, audio, sr)
    print(f"Wrote {args.out}: {len(audio) / sr:.1f}s loop, key={args.key}, tempo={args.tempo}")


if __name__ == "__main__":
    main()
