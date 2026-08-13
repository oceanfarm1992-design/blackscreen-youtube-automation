# Meditated Sleeping — Automated Video Production

*Calm. Sleep. Restore.*

An autonomous pipeline that produces **12 videos per day** for the "Meditated Sleeping"
YouTube channel and publishes them — **6 long-forms + 6 Shorts**. Videos are produced
**one per run**, every 2h alternating long/short, so runs never overlap. Long-forms upload
through the main Cloud project and Shorts through a **separate Cloud project**, so each
stays under its own YouTube API quota:

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
scripts/produce.py --slot N        (N = 0..11, one video per run)
   │  slots 0-5 = 10h long-forms, slots 6-11 = 59s Shorts (each a music)
   ├─ generate_theme_audio.py   numpy synthesis (Short = 59s; long = seamless loop)
   ├─ make_video.py             ffmpeg: branded #0D0D0D still + audio → mp4
   ├─ assets/branding/…         assign the 1280×720 black #0D0D0D thumbnail
   ├─ make_metadata.py          SEO title / description / tags per music & format
   └─ QC                        assert 59s / 8–12h and correct resolution
        → writes *_manifest.json, status "queued"

.github/workflows/publish.yml (12 crons/day, every 2h)
   → maps each cron to a slot, runs produce.py --slot N, then (if YT secrets
     are set) uploads as PUBLIC — longs via the main project, Shorts via the
     YT_SHORTS project. One video per run so runs never overlap.
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
python scripts/produce.py --daily                        # today's full batch (12 assets)
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

> **YouTube API quota:** the default is 10,000 units/day **per Cloud project** and each
> upload costs 1,600 units. Uploads are split across two projects so neither is exceeded:
> **6 long-forms** → main project (6 × 1,650 = 9,900, *tight* — 100 units of headroom) and
> **6 Shorts** → the `YT_SHORTS` project (6 × 1,600 = 9,600). Set `YT_SHORTS_CLIENT_ID` /
> `YT_SHORTS_CLIENT_SECRET` / `YT_SHORTS_REFRESH_TOKEN` (a 2nd Cloud project's OAuth for the
> same channel) to enable the split; without them, Shorts fall back to the main project and
> blow past the quota. Raising `LONGS_PER_DAY`/`SHORTS_PER_DAY` in `themes.py` must keep
> **each project** under 10,000, or the extra uploads fail with `quotaExceeded`.
