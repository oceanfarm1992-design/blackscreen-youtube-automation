#!/usr/bin/env python3
"""
Render an upload's music with ACE-Step 1.5 (acestep.cpp, CPU) instead of the
numpy synth. Used by channels that list a format in themes.ACESTEP_FORMATS
(trial: Moss & Manor Shorts).

Every upload gets its own composition: the seed is the upload's render seed,
the key steps through 12 keys with the Vol. number (so consecutive uploads of
a theme are never in the same key), and the tempo and a mood phrase also vary.
Always instrumental.

The result is checked (length, not silent, no clipping) and the script exits
non-zero if anything is wrong -- the caller then falls back to the synth, so
a bad render never reaches YouTube.

Usage:
    python scripts/acestep_audio.py --bin acestep.cpp/build/ace-synth \
        --models ~/.cache/ai-models/acestep15 --caption "..." --seconds 59 \
        --seed 123 --variant 7 --out audio.wav
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf

SYNTH_MODEL = "acestep-v15-turbo-Q4_K_M.gguf"
KEYS = ("D major", "B minor", "F major", "A minor", "G major", "E minor",
        "C major", "D minor", "A major", "F# minor", "E flat major", "C minor")
MOODS = ("soft and intimate", "warm and unhurried", "gentle, with space between notes",
         "dreamy and slow", "hushed and peaceful", "tender, late-evening feel",
         "airy and calm", "quiet and reflective")


def build_request(caption, seconds, seed, variant=None):
    v = int(variant) if variant is not None else int(seed)
    return {
        "synth_model": SYNTH_MODEL,
        "caption": f"{caption}, {MOODS[(int(seed) // 7) % len(MOODS)]}, instrumental",
        "lyrics": "[Instrumental]",
        "bpm": 58 + int(seed) % 23,                  # 58-80 bpm
        "keyscale": KEYS[(v * 5) % len(KEYS)],      # every key before one repeats
        "timesignature": "4",
        "duration": float(seconds),
        "inference_steps": 8,
        "guidance_scale": 1.0,
        "shift": 3.0,
        "seed": int(seed) % (2 ** 62),
        "output_format": "wav16",
    }


def check_audio(x, sr, seconds):
    """List of problems with a render (empty = usable)."""
    problems = []
    if x.ndim == 1:
        x = x[:, None]
    dur = len(x) / sr
    if abs(dur - seconds) > 1.5:
        problems.append(f"length {dur:.1f}s, wanted {seconds:.0f}s")
    if not np.isfinite(x).all():
        problems.append("NaN/inf samples")
    rms = float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0
    if rms < 0.003:
        problems.append(f"near-silent (rms {rms:.4f})")
    if len(x) and float(np.mean(np.abs(x) > 0.999)) > 0.01:
        problems.append("heavily clipped")
    return problems


def finish(x, sr, seconds, fade=1.5):
    """Exact length, gentle fades, peak 0.9."""
    n = int(round(seconds * sr))
    x = x[:n] if len(x) >= n else np.pad(x, ((0, n - len(x)), (0, 0)))
    m = min(int(fade * sr), n // 2)
    w = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, m))[:, None]
    x = x.copy()
    x[:m] *= w
    x[-m:] *= w[::-1]
    return x / (np.max(np.abs(x)) + 1e-9) * 0.9


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bin", default=os.environ.get("ACESTEP_BIN"))
    p.add_argument("--models", default=os.environ.get("ACESTEP_MODELS"))
    p.add_argument("--caption", required=True)
    p.add_argument("--seconds", type=float, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--variant", type=int, default=None)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    if not (args.bin and os.path.exists(args.bin) and args.models and os.path.isdir(args.models)):
        sys.exit("ACE-Step not available (ACESTEP_BIN / ACESTEP_MODELS)")

    req = build_request(args.caption, args.seconds, args.seed, args.variant)
    print(f"ACE-Step: {req['keyscale']}, {req['bpm']} bpm -- {req['caption']}")
    with tempfile.TemporaryDirectory() as tmp:
        rpath = os.path.join(tmp, "request.json")
        with open(rpath, "w", encoding="utf-8") as f:
            json.dump(req, f)
        subprocess.run([args.bin, "--models", args.models, "--request", rpath], check=True)
        x, sr = sf.read(os.path.join(tmp, "request0.wav"), always_2d=True)
    problems = check_audio(x, sr, args.seconds)
    if problems:
        sys.exit("ACE-Step render rejected: " + "; ".join(problems))
    sf.write(args.out, finish(x, sr, args.seconds), sr)
    print(f"Wrote {args.out} ({args.seconds:.0f}s, {sr} Hz, ACE-Step 1.5)")


if __name__ == "__main__":
    main()
