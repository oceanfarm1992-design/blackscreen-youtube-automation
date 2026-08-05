# Architecture Reasoning

## Why loop-then-stretch instead of synthesizing full-length audio
An 8-hour video doesn't need 8 hours of unique synthesis. Generate a short seamless
loop (2-10 min, crossfaded at the seam so it's not audibly repetitive at small scale),
then use `ffmpeg -stream_loop -1 -i loop.wav -t <seconds>` to stretch it. This turns an
8-hour render into an I/O-bound job that finishes in minutes, not hours.

## Why a near-static black frame is cheap to encode
A single black (or very slowly shifting) frame compresses extremely well with a long
GOP and low bitrate — ffmpeg does not need to encode 8 hours of unique frames, just a
handful of keyframes repeated. Expect final 8-hour files in the 500MB-1GB range.

## Why GitHub Actions on a public repo
Standard GitHub-hosted Linux runners are free and unmetered on public repositories
(no minute cap, unlike the 2,000 min/month private-repo free tier). Real limits that
still apply: 6-hour max per job, 20 concurrent jobs on free/public tier, and GitHub's
general abuse policy for extreme non-development use — none of which a daily
few-minute render job comes close to.

Secrets (YouTube refresh token, Google service account JSON) must go in GitHub
Secrets, never hardcoded, since the repo code itself is public.

## Why cron + Sheets instead of Zapier for the core loop
Zapier's free tier caps at 100 tasks/month and only allows single-step Zaps. At 3
videos/day (90 runs/month) you're already near the ceiling, and any additional step
(notifications, status updates) pushes you over. GitHub Actions can poll/read Google
Sheets directly via the Sheets API (e.g. `gspread` in Python) on a cron schedule,
removing Zapier from the critical path entirely. Reserve Zapier (still free tier) for
low-frequency, single-step extras like a Slack/Telegram notification on publish.

## Why Sheets as the queue instead of hardcoding a list
Non-technical to edit, gives a visual queue/status view, and is trivially readable
from Python via a service account — no need to touch code to plan a week of content.
