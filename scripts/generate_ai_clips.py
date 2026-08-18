#!/usr/bin/env python3
"""
Generate AI music clips via Replicate's MusicGen API and store them in a
per-theme clip library. These clips provide the warm, organic musical bed
that procedural synthesis cannot — heart-touching harmony, natural piano,
gentle strings — while the existing engine adds precision layers on top
(Solfeggio tones, binaural beats, nature sounds).

Each theme gets a curated prompt describing the emotional quality of the
music. Multiple clips per theme (default 10) ensure every video sounds
different, avoiding YouTube duplicate detection.

Requires: REPLICATE_API_TOKEN env var (or --token flag).

Usage:
    python generate_ai_clips.py --theme sleeping          # 10 clips for one theme
    python generate_ai_clips.py --all                     # 10 clips × 19 themes
    python generate_ai_clips.py --theme rain --clips 5    # 5 clips for rain
    python generate_ai_clips.py --theme rain --clip-id 3  # regenerate clip #3 only
"""
import argparse
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import themes as T  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIPS_DIR = os.path.join(ROOT, "assets", "clips")

CLIP_DURATION = 30  # seconds per clip
MODEL = "meta/musicgen"

# Heart-touching, calm prompts per theme. Each describes the emotional
# quality so MusicGen generates warm, organic audio — not test tones.
PROMPTS = {
    "rain": (
        "gentle ambient piano with soft rain atmosphere, peaceful and melancholic, "
        "warm harmonic pads, slow tender melody, no drums, no vocals, calm and soothing"
    ),
    "waterfall": (
        "flowing ambient music with gentle water textures, ethereal pads, "
        "soft reverb piano, peaceful and meditative, no drums, no vocals"
    ),
    "forest": (
        "peaceful nature-inspired ambient music, gentle wooden flute with warm "
        "string pads, birdsong atmosphere, pure serene harmony, no drums, no vocals"
    ),
    "sleeping": (
        "deep ambient sleep music, warm evolving pad chords, gentle piano melody, "
        "tender and heartfelt lullaby, extremely calm, no drums, no vocals"
    ),
    "indian": (
        "soft indian classical meditation music, gentle sitar with warm tanpura drone, "
        "peaceful raga, spiritual and calming, no drums, no vocals"
    ),
    "romantic": (
        "romantic slow piano with warm strings, heartfelt emotional melody, tender "
        "and gentle love music, soft and intimate, no drums, no vocals"
    ),
    "romantic_night": (
        "smooth romantic evening music, gentle piano and soft strings, warm mellow "
        "chords, intimate and cozy atmosphere, no drums, no vocals"
    ),
    "gamma_focus": (
        "minimal ambient focus music, soft electronic pads, clean and clear tones, "
        "calm concentration atmosphere, subtle and steady, no drums, no vocals"
    ),
    "528hz_sleep": (
        "ethereal healing ambient music, warm celestial harmony, gentle glowing pads, "
        "deeply emotional and soothing sleep music, pure tones, no drums, no vocals"
    ),
    "delta_sleep": (
        "deep ambient drone music for sleep, very slow warm pad evolution, gentle "
        "low tones, peaceful and dark atmosphere, no drums, no vocals"
    ),
    "432hz_relax": (
        "warm relaxing ambient music tuned to natural harmony, soft piano with "
        "gentle pad layers, calm and peaceful, no drums, no vocals"
    ),
    "rooftop_rain": (
        "gentle rain falling on a rooftop, cozy indoor atmosphere, soft distant "
        "thunder rumbles, warm ambient pad, peaceful and intimate, no drums, no vocals"
    ),
    "rain_drops": (
        "extremely gentle ambient music with soft water drop textures, minimal "
        "warm piano notes, calm and tender, thin and delicate, no drums, no vocals"
    ),
    "solfeggio_heal": (
        "healing ambient sleep music, warm layered harmonic pads, gentle glowing "
        "tones, deeply calming and restorative, pure harmony, no drums, no vocals"
    ),
    "solfeggio_spirit": (
        "spiritual ambient meditation music, ethereal floating pads, gentle "
        "celestial harmony, warm and uplifting yet calm, no drums, no vocals"
    ),
    "solfeggio_deepsleep": (
        "very deep ambient sleep music, ultra slow warm drone pads, gentle pulsing "
        "rhythm, dark and peaceful, deeply restful, no drums, no vocals"
    ),
    "om_136": (
        "deep om meditation music, warm resonant drone, gentle tibetan atmosphere, "
        "grounding and spiritual, slow breathing pace, no drums, no vocals"
    ),
    "963hz_awakening": (
        "ethereal spiritual ambient music, high gentle glowing tones with warm base, "
        "celestial and pure, crown chakra meditation, no drums, no vocals"
    ),
    "852hz_intuition": (
        "mystical ambient meditation music, soft ethereal pads, gentle mysterious "
        "harmony, intuitive and dreamy atmosphere, no drums, no vocals"
    ),
    "741hz_clarity": (
        "clear and pure ambient music, gentle crystalline tones with warm pad "
        "foundation, calm clarity and focus, clean and soothing, no drums, no vocals"
    ),
}


def get_clip_dir(theme_key):
    d = os.path.join(CLIPS_DIR, theme_key)
    os.makedirs(d, exist_ok=True)
    return d


def existing_clips(theme_key):
    d = get_clip_dir(theme_key)
    return sorted(f for f in os.listdir(d) if f.endswith(".wav"))


def generate_clip(theme_key, clip_id, token, max_retries=3):
    import replicate

    prompt = PROMPTS.get(theme_key)
    if not prompt:
        print(f"  ! no prompt for {theme_key}, skipping")
        return None

    out_dir = get_clip_dir(theme_key)
    fname = f"clip_{clip_id:03d}.wav"
    out_path = os.path.join(out_dir, fname)

    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        print(f"  {theme_key}/{fname} already exists, skipping")
        return out_path

    for attempt in range(1, max_retries + 1):
        print(f"  Generating {theme_key}/{fname} ({CLIP_DURATION}s)"
              + (f" [retry {attempt}]" if attempt > 1 else "") + "...",
              end=" ", flush=True)
        t0 = time.time()
        try:
            output = replicate.run(
                f"{MODEL}:671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb",
                input={
                    "model_version": "stereo-large",
                    "prompt": prompt,
                    "duration": CLIP_DURATION,
                    "output_format": "wav",
                    "normalization_strategy": "peak",
                },
            )
            audio_url = str(output)
            urllib.request.urlretrieve(audio_url, out_path)
            elapsed = time.time() - t0
            size_mb = os.path.getsize(out_path) / 1024 / 1024
            print(f"done ({elapsed:.1f}s, {size_mb:.1f}MB)")
            return out_path
        except Exception as e:
            print(f"error: {e}")
            if attempt < max_retries:
                wait = 10 * attempt
                print(f"    waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                print(f"    ! failed after {max_retries} attempts, skipping")
                return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--theme", default=None, help="theme key")
    p.add_argument("--all", action="store_true", help="generate for all themes")
    p.add_argument("--clips", type=int, default=10, help="clips per theme (default 10)")
    p.add_argument("--clip-id", type=int, default=None, help="regenerate one specific clip")
    p.add_argument("--token", default=None, help="Replicate API token (or set REPLICATE_API_TOKEN)")
    args = p.parse_args()

    token = args.token or os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        p.error("set REPLICATE_API_TOKEN or pass --token")
    os.environ["REPLICATE_API_TOKEN"] = token

    if args.all:
        keys = [t["key"] for t in T.THEMES]
    elif args.theme:
        keys = [args.theme]
    else:
        p.error("give --theme KEY or --all")

    generated, skipped, failed = 0, 0, 0
    for key in keys:
        if key not in PROMPTS:
            print(f"  ! no prompt for {key}, skipping")
            continue

        print(f"\n{key}:")
        ids = [args.clip_id] if args.clip_id is not None else list(range(1, args.clips + 1))
        for i in ids:
            result = generate_clip(key, i, token)
            if result and "already exists" not in str(result):
                generated += 1
            elif result:
                skipped += 1
            else:
                failed += 1

    cost = generated * 0.05
    print(f"\nDone. Generated {generated}, skipped {skipped} existing, {failed} failed.")
    print(f"Estimated cost: ${cost:.2f}")
    print(f"Clips stored in: assets/clips/")


if __name__ == "__main__":
    main()
