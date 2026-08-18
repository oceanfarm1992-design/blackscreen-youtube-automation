#!/usr/bin/env python3
"""
Build long-form audio by blending AI-generated clips with the procedural
synth engine. This is the hybrid approach:

    AI clips (heart, warmth, harmony) + Procedural (frequencies, nature, precision)

The AI clips provide organic musical texture that pure math cannot — warm
piano, gentle strings, evolving harmony. The procedural engine adds the
therapeutic precision — exact Solfeggio frequencies, binaural beats, rain
sounds, and tone shaping.

Strategy:
  1. Load all available AI clips for the theme
  2. Randomly select and shuffle clips (different every run via seed)
  3. Crossfade clips together into a longer musical bed
  4. If the bed is shorter than the target, loop it seamlessly
  5. Mix with the procedural synth layer at a balanced ratio
  6. Output the final blended audio

Falls back to pure procedural if no AI clips exist for a theme.

Usage:
    python build_long_audio.py --theme sleeping --seconds 600 --seed 42 --out audio.wav
"""
import argparse
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import themes as T  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CLIPS_DIR = os.path.join(ROOT, "assets", "clips")
SR = 44100

CROSSFADE_SEC = 2.0      # crossfade between AI clips
AI_MIX = 0.45            # AI clip level in the final blend (0.0-1.0)
PROC_MIX = 0.65          # procedural level (sum > 1.0 is fine, we normalize)


def load_clips(theme_key, rng):
    clip_dir = os.path.join(CLIPS_DIR, theme_key)
    if not os.path.isdir(clip_dir):
        return None

    files = sorted(f for f in os.listdir(clip_dir) if f.endswith(".wav"))
    if not files:
        return None

    clips = []
    for f in files:
        audio, sr = sf.read(os.path.join(clip_dir, f))
        if sr != SR:
            ratio = SR / sr
            n_out = int(len(audio) * ratio)
            indices = (np.arange(n_out) / ratio).astype(int)
            indices = np.clip(indices, 0, len(audio) - 1)
            audio = audio[indices]
        if audio.ndim == 1:
            audio = np.column_stack([audio, audio])
        clips.append(audio)

    if not clips:
        return None

    rng.shuffle(clips)
    return clips


def crossfade_concat(clips, crossfade_sec=CROSSFADE_SEC):
    if not clips:
        return np.zeros((SR, 2))

    nfx = int(crossfade_sec * SR)
    result = clips[0].copy()

    for clip in clips[1:]:
        if len(result) < nfx or len(clip) < nfx:
            result = np.concatenate([result, clip])
            continue

        t = np.linspace(0, 1, nfx)[:, None]
        fade_out = np.sqrt(1.0 - t)
        fade_in = np.sqrt(t)

        overlap = result[-nfx:] * fade_out + clip[:nfx] * fade_in
        result = np.concatenate([result[:-nfx], overlap, clip[nfx:]])

    return result


def loop_to_length(audio, target_samples):
    if len(audio) >= target_samples:
        return audio[:target_samples]

    nfx = int(3.0 * SR)
    if len(audio) < nfx * 2:
        repeats = (target_samples // len(audio)) + 1
        audio = np.tile(audio, (repeats, 1))
        return audio[:target_samples]

    t = np.linspace(0, 1, nfx)[:, None]
    fin = np.sqrt(t)
    fout = np.sqrt(1.0 - t)
    head = audio[:nfx] * fin + audio[-nfx:] * fout
    loop = np.concatenate([head, audio[nfx:-nfx]])

    result = loop.copy()
    while len(result) < target_samples:
        result = np.concatenate([result[:-nfx],
                                 result[-nfx:] * fout + loop[:nfx] * fin,
                                 loop[nfx:]])

    return result[:target_samples]


def render_procedural(theme, seconds, seed, out_path):
    cmd = [sys.executable, os.path.join(HERE, "generate_theme_audio.py"),
           "--theme", theme["synth"], "--loop-seconds", str(seconds),
           "--seed", str(seed), "--out", out_path] + T.synth_args(theme)
    subprocess.run(cmd, check=True, capture_output=True)
    audio, _ = sf.read(out_path)
    return audio


def build_hybrid(theme, seconds, seed, out_path):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    key = theme["key"]

    clips = load_clips(key, rng)
    if clips is None:
        print(f"  No AI clips for {key}, using pure procedural")
        render_procedural(theme, seconds, seed, out_path)
        return "procedural"

    print(f"  Loaded {len(clips)} AI clip(s) for {key}")

    # Pick a random subset (2-5 clips) and concatenate with crossfades.
    # Using different subsets each run means different videos sound different.
    if len(clips) == 1:
        pick_count = 1
    else:
        pick_count = min(len(clips), max(2, rng.integers(2, min(6, len(clips) + 1))))
    selected = list(rng.choice(clips, size=pick_count, replace=False))
    print(f"  Selected {pick_count} clips, crossfading...")

    ai_bed = crossfade_concat(selected)
    ai_bed = loop_to_length(ai_bed, n)

    # Render the procedural layer
    proc_path = out_path + ".proc.wav"
    proc = render_procedural(theme, seconds, seed, proc_path)
    if proc.ndim == 1:
        proc = np.column_stack([proc, proc])
    proc = proc[:n] if len(proc) >= n else np.pad(proc, ((0, n - len(proc)), (0, 0)))

    # Blend: AI provides warmth, procedural provides precision
    blended = ai_bed[:n] * AI_MIX + proc[:n] * PROC_MIX

    # Normalize to safe level
    peak = np.max(np.abs(blended))
    if peak > 0.01:
        blended = blended * (0.9 / peak)

    sf.write(out_path, blended, SR)

    # Clean up temp file
    if os.path.exists(proc_path):
        os.remove(proc_path)

    print(f"  Hybrid blend: {AI_MIX:.0%} AI + {PROC_MIX:.0%} procedural")
    return "hybrid"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--theme", required=True, help="theme key")
    p.add_argument("--seconds", type=float, required=True, help="total audio length")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="hybrid_audio.wav")
    args = p.parse_args()

    theme = T.theme_by_key(args.theme)
    mode = build_hybrid(theme, args.seconds, args.seed, args.out)
    dur = args.seconds
    print(f"Wrote {args.out}: {dur:.0f}s ({dur/60:.1f}min), mode={mode}")


if __name__ == "__main__":
    main()
