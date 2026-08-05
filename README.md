# Black-Screen YouTube Automation

A fully automated pipeline for a low-effort, high-volume ambient/calm-music YouTube
channel: Python-generated music → black-screen video → thumbnail → scheduled YouTube
upload, orchestrated by **GitHub Actions** and driven by a **Google Sheets** content queue.

```
Google Sheet (content queue: title, key, tempo, duration, status)
        │
        ▼
GitHub Actions (cron trigger, public repo = free unmetered minutes)
        ├─ scripts/generate_music.py      numpy sine-pad loop, crossfaded seam
        ├─ scripts/make_video.py          ffmpeg: black frame + -stream_loop audio → mp4
        ├─ scripts/generate_thumbnail.py  Pillow: text over a rotating background pool
        └─ scripts/upload_youtube.py      YouTube Data API v3 upload + thumbnail
        │
        ▼
Sheet row flipped to "done", video_id written back
```

## Status

Code is ready. Going live requires one-time account setup (Google Cloud, OAuth, GitHub
Secrets) — **follow [PLAN.md](PLAN.md) step by step.**

## Repo layout

| Path | Purpose |
|---|---|
| `.github/workflows/publish.yml` | Cron + manual pipeline: reads a pending row, renders, uploads, marks done |
| `scripts/generate_music.py` | Synthesize a short seamless ambient loop (vary `--key`/`--tempo`/`--seed`) |
| `scripts/make_video.py` | ffmpeg-merge the loop with a black frame to full length |
| `scripts/generate_thumbnail.py` | Pillow thumbnail from title/duration + a background image |
| `scripts/upload_youtube.py` | Upload via YouTube Data API v3 using a refresh token |
| `scripts/get_refresh_token.py` | **Run locally once** to mint the long-lived refresh token |
| `scripts/read_sheet.py` | Read next `pending` row / write status + video_id back |
| `content_queue_template.csv` | The columns your Google Sheet must have |
| `docs/privacy-policy.md` | Host via GitHub Pages for OAuth "Production" publishing |
| `assets/` | Drop 5–10 calming background images here for thumbnail rotation |

## Local development

The pipeline is designed to run on GitHub's Ubuntu runners — **you don't need Python
locally** except for the one-time `get_refresh_token.py` step. To run scripts locally
anyway:

```bash
pip install -r requirements.txt   # plus system ffmpeg on PATH
python scripts/generate_music.py --key C --tempo 60 --loop-minutes 4 --out loop.wav
python scripts/make_video.py --loop loop.wav --duration-hours 8 --out final.mp4
```

## Guardrails

- **Quota:** ~6 uploads/day max on the default 10k-unit/day YouTube API quota.
- **Content policy:** vary music parameters and metadata per video; never reuse audio.
- **Secrets:** live only in GitHub Secrets — never commit them (`.gitignore` enforces this).

See [PLAN.md](PLAN.md) for the full rollout and the failure modes to watch for.
