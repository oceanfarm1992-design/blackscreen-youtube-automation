# Meditated Sleeping — Automated Video Production

*Calm. Sleep. Restore.*

An autonomous pipeline that produces **6 videos per day** for the "Meditated Sleeping"
YouTube channel and publishes them — **3 different musics**, each as a
long-form + a Short. Videos are produced **one per run, ~3.8h apart**, so runs never
overlap:

- **Shorts** — exactly **59 seconds**, vertical **1080×1920**, for reach/discovery.
- **Long-form** — **10 hours**, **1920×1080**, for deep sleep and background ambience.

All use the same immersive **`#0D0D0D`** black branded frame + thumbnail (glowing
headphone icon + "Meditated Sleeping / Calm. Sleep. Restore."). Everything runs on
GitHub's Ubuntu runners; no machine of yours needs to stay on.

## Daily music rotation

The library has **7 musics**. Each day publishes **3 of them** (a sliding window that
advances 3 per day), so the whole library is cycled through for variety — date-driven,
no state file needed:

| Music | Sound design |
|----|----|
| **Rainy with Calm Music** | gentle rainfall + distant thunder + soft ambient pads |
| **Waterfall Music** | steady flowing water + low rumble + gentle harmony |
| **Natural Green Forest** | soft wind + random water drops + bird chirps + pad |
| **Sleeping Music** | warm mid-range drone + slow evolving chords + slow swell |
| **Indian Sleep Music** | tanpura drone + soft bansuri-style flute (Raga Bhupali) |
| **Romantic Love Music** | lush major-7th chords + soft music-box melody |
| **Romantic Night Music** | slow low minor-7th chords + sultry warm melody |

Anchor date `2026-08-05` (see `scripts/themes.py`).

### Optional wellness frequency layers

Any music can be mixed with healing frequencies via `generate_theme_audio.py` flags:
`--tone` (9 Solfeggio tones, 432 Hz, or any Hz), `--beat`
(delta/theta/alpha/schumann/beta/gamma as **binaural** or **isochronic**), and
`--bowl` (Tibetan singing bowl). Example:
`generate_theme_audio.py --theme rain --beat gamma --beat-type binaural --loop-seconds 123`.

## How a day runs

```
scripts/produce.py --slot N        (N = 0..5, one video per run)
   │  slot//2 = which of today's 3 musics; even=10h long, odd=59s Short
   ├─ generate_theme_audio.py   numpy synthesis (Short = 59s; long = seamless loop)
   ├─ make_video.py             ffmpeg: branded #0D0D0D still + audio → mp4
   ├─ assets/branding/…         assign the 1280×720 black #0D0D0D thumbnail
   ├─ make_metadata.py          SEO title / description / tags per music & format
   └─ QC                        assert 59s / 8–12h and correct resolution
        → writes *_manifest.json, status "queued"

.github/workflows/publish.yml (6 crons/day, ~3.8h apart)
   → maps each cron to a slot, runs produce.py --slot N, then (if YT secrets
     are set) uploads as PUBLIC. One video per run so runs never overlap.
```

Audio is **synthesized from numpy every run** (no samples), so each upload is original;
the seed defaults to the date, and varies per format, so consecutive videos differ.

## Repo layout

| Path | Purpose |
|---|---|
| `scripts/themes.py` | 7 musics: synth params, SEO metadata, 4-per-day rotation |
| `scripts/generate_theme_audio.py` | Synthesize all 7 musics + wellness frequency layers |
| `scripts/make_video.py` | ffmpeg-merge audio with the branded still frame |
| `scripts/make_metadata.py` | Emit SEO title/description/tags JSON per theme & format |
| `scripts/produce.py` | Orchestrator: audio → video → thumbnail → metadata → QC → manifest |
| `scripts/publish_queue.py` | Upload produced assets to YouTube as **private** (queued) |
| `scripts/upload_youtube.py` | YouTube Data API v3 upload helper |
| `scripts/get_refresh_token.py` | **Run locally once** to mint the OAuth refresh token |
| `assets/branding/` | The `#0D0D0D` brand frames: 16:9, 9:16, and 1280×720 thumbnail |
| `assets/thumbnails/` | The original 9 scenic thumbnails — **unused** alternate set (kept for reference) |
| `.github/workflows/publish.yml` | Daily produce-and-queue workflow |

## Run it locally

Needs Python 3.11+ and ffmpeg on PATH.

```bash
pip install -r requirements.txt
python scripts/produce.py --daily                        # today's full batch (6 assets)
python scripts/produce.py --format short                 # today's first theme, 59s Short
python scripts/produce.py --slot 0                        # one video by schedule slot
python scripts/produce.py --theme forest --format long --hours 10   # one 10h long-form
```

Outputs land in `out/` (git-ignored) with a `*_manifest.json` QC report per asset.

## Publishing

If the three `YT_*` secrets are set, the daily workflow uploads the day's assets as
**public** automatically. Override per manual run with the `workflow_dispatch`
"privacy" input (`private` / `unlisted` / `public`). Without the secrets, videos are
produced and saved as run artifacts only. See [PLAN.md](PLAN.md) for the one-time
OAuth setup and the guardrails (API quota, content-policy, token expiry).

> **YouTube API quota:** the default is 10,000 units/day and each upload costs
> 1,600 units. The **6 uploads/day** (3 musics × long + Short) = 9,600 units, which
> fits within the free quota. Raising `DAILY_COUNT` in `themes.py` beyond 3 needs a
> quota increase (Google Cloud console), or the extra uploads fail with `quotaExceeded`.
