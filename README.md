# Meditated Sleeping — Automated Video Production

*Calm. Sleep. Restore.*

An autonomous pipeline that produces **two videos per day** for the "Meditated Sleeping"
YouTube channel and queues them for publishing:

- **Short** — exactly **59 seconds**, vertical **1080×1920**, for reach/discovery.
- **Long-form** — **8–12 hours**, **1920×1080**, for deep sleep and background ambience.

Both use the same immersive **`#0D0D0D`** branded frame (glowing headphone icon +
"Meditated Sleeping / Calm. Sleep. Restore."). Everything runs on GitHub's Ubuntu
runners; no machine of yours needs to stay on.

## Daily theme rotation

One theme per day, cycling in order (date-driven, no state file needed):

| Day | Theme | Sound design |
|----|----|----|
| 1 | **Rainy with Calm Music** | gentle rainfall + distant thunder + soft ambient pads |
| 2 | **Waterfall Music** | steady flowing water + low rumble + gentle harmony |
| 3 | **Natural Green Forest** | soft wind + random water drops + bird chirps + pad |
| 4 | **Sleeping Music** | deep drone + slow evolving chords + subtle delta-rate tremolo |

Anchor date `2026-08-05` = Rain (see `scripts/themes.py`).

## How a day runs

```
scripts/produce.py --format both
   │  pick today's theme (themes.py)
   ├─ generate_theme_audio.py   numpy synthesis (Short = 59s; long = seamless loop)
   ├─ make_video.py             ffmpeg: branded #0D0D0D still + audio → mp4
   ├─ assets/branding/…         assign the 1280×720 #0D0D0D thumbnail
   ├─ make_metadata.py          SEO title / description / tags per theme & format
   └─ QC                        assert 59s / 8–12h and correct resolution
        → writes *_manifest.json, status "queued"

.github/workflows/publish.yml (daily cron)
   → runs produce.py, then (only if YT secrets are set) uploads both as PRIVATE
```

Audio is **synthesized from numpy every run** (no samples), so each upload is original;
the seed defaults to the date, and varies per format, so consecutive videos differ.

## Repo layout

| Path | Purpose |
|---|---|
| `scripts/themes.py` | 4 themes: synth params, SEO metadata, date-based rotation |
| `scripts/generate_theme_audio.py` | Synthesize rain / waterfall / forest / sleeping audio |
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
python scripts/produce.py --format short                 # today's theme, 59s Short
python scripts/produce.py --theme forest --format long --hours 10   # a 10h long-form
```

Outputs land in `out/` (git-ignored) with a `*_manifest.json` QC report per asset.

## Publishing

The daily workflow **never publishes public automatically.** If the three `YT_*`
secrets are set it uploads both videos as **private** (queued on the channel); you
review and flip them to public yourself. See [PLAN.md](PLAN.md) for the one-time
OAuth setup and the guardrails (API quota, content-policy, token expiry).
