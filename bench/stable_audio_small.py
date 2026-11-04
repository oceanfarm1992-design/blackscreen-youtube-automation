#!/usr/bin/env python3
"""
Benchmark: Stable Audio Open Small (341M) on CPU.

The model makes clips of up to ~11 s, so a longer sample is built from
several clips, each with its own seed and a slightly different prompt,
crossfaded together. Prints timings and writes a WAV.

Needs HF_TOKEN for an account that has accepted the model's licence at
https://huggingface.co/stabilityai/stable-audio-open-small

Usage: python bench/stable_audio_small.py --prompt "..." --seconds 59 --out sao.wav
"""
import argparse
import json
import math
import time

import numpy as np
import soundfile as sf
import torch

VARIATIONS = ("", ", gentle", ", slow evolving", ", soft and warm", ", spacious", ", distant")


def crossfade_join(clips, sr, xf_sec=2.0):
    xf = int(xf_sec * sr)
    out = clips[0]
    t = np.linspace(0, 1, xf)[:, None]
    for c in clips[1:]:
        head = out[-xf:] * np.sqrt(1 - t) + c[:xf] * np.sqrt(t)
        out = np.concatenate([out[:-xf], head, c[xf:]])
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", required=True)
    p.add_argument("--seconds", type=float, default=59)
    p.add_argument("--steps", type=int, default=8)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--out", default="stable_audio_small.wav")
    p.add_argument("--report", default="stable_audio_small.json")
    args = p.parse_args()

    from stable_audio_tools import get_pretrained_model
    from stable_audio_tools.inference.generation import generate_diffusion_cond

    torch.set_num_threads(max(1, torch.get_num_threads()))
    t0 = time.time()
    model, cfg = get_pretrained_model("stabilityai/stable-audio-open-small")
    model = model.to("cpu").eval()
    load_s = time.time() - t0
    sr, sample_size = cfg["sample_rate"], cfg["sample_size"]
    clip_s = min(11.0, sample_size / sr)
    n = max(1, math.ceil((args.seconds - 2.0) / (clip_s - 2.0)))

    clips, times = [], []
    for i in range(n):
        prompt = args.prompt + VARIATIONS[i % len(VARIATIONS)]
        t = time.time()
        with torch.inference_mode():
            audio = generate_diffusion_cond(
                model, steps=args.steps,
                conditioning=[{"prompt": prompt, "seconds_total": clip_s}],
                sample_size=sample_size, sampler_type="pingpong",
                seed=args.seed + i, device="cpu")
        times.append(time.time() - t)
        a = audio[0].to(torch.float32).cpu().numpy().T  # (samples, channels)
        a = a[: int(clip_s * sr)]
        clips.append(a / (np.max(np.abs(a)) + 1e-9) * 0.9)
        print(f"clip {i + 1}/{n}: {times[-1]:.1f}s  ({prompt})", flush=True)

    out = crossfade_join(clips, sr)[: int(args.seconds * sr)]
    sf.write(args.out, out, sr)
    report = {
        "model": "stabilityai/stable-audio-open-small",
        "load_seconds": round(load_s, 1),
        "clips": n,
        "clip_seconds": clip_s,
        "seconds_per_clip": round(float(np.mean(times)), 1),
        "total_generate_seconds": round(float(np.sum(times)), 1),
        "audio_seconds": round(len(out) / sr, 1),
        "realtime_factor": round(float(np.sum(times)) / (len(out) / sr), 2),
        "threads": torch.get_num_threads(),
    }
    json.dump(report, open(args.report, "w"), indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
