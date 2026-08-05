# Rollout Plan — Black-Screen YouTube Automation

This is the end-to-end plan to get the pipeline live. The **code** in this repo is done;
the remaining work is **account/config setup** that can't be scripted from here (it needs
your Google account, browser logins, and secrets). Do the steps in order.

Legend: 🤖 = automated by this repo · 🙋 = you do it manually (one-time)

---

## Phase 0 — Repo (done)

- 🤖 Scripts, GitHub Actions workflow, requirements, docs, and templates are committed.
- 🤖 `.gitignore` guarantees no secret or render artifact is ever committed.

## Phase 1 — Google Sheet content queue  🙋

1. Create a Google Sheet. Give the first tab the header row from
   [`content_queue_template.csv`](content_queue_template.csv):
   `title, style, key, tempo_bpm, duration_hours, status, video_id, scheduled_date`
2. Add a few rows with `status = pending`. Vary `key`/`tempo_bpm` per row (policy — see
   guardrails below).
3. Copy the **Sheet ID** from its URL (`docs.google.com/spreadsheets/d/<SHEET_ID>/edit`).

## Phase 2 — Google service account (Sheets access)  🙋

1. In [Google Cloud Console](https://console.cloud.google.com) create/pick a project.
2. Enable the **Google Sheets API**.
3. Create a **Service Account**, then create a **JSON key** for it and download it.
4. **Share the Sheet** with the service account's email (`...@...iam.gserviceaccount.com`)
   as an **Editor** — otherwise it can't read/write the queue.

## Phase 3 — YouTube OAuth (the fragile part)  🙋

Read [`references/youtube_oauth.md`](references/youtube_oauth.md) carefully — this is the
step most likely to break. See also [`references/troubleshooting.md`](references/troubleshooting.md).

1. Same Cloud project: enable **YouTube Data API v3**.
2. Create **OAuth 2.0 credentials → Desktop app**; download the client-secret JSON.
3. Configure the **OAuth consent screen** (External), add the `youtube.upload` scope, and
   add yourself as a test user.
4. **Publish the app to Production.** Tokens issued while the app is in *Testing* expire
   after **7 days** and the upload will silently start failing. Publishing a *sensitive*
   scope (which `youtube.upload` is) does **not** need Google's full review for a personal
   tool — you'll click through a warning. The usual blocker is a **privacy-policy URL**:
   host [`docs/privacy-policy.md`](docs/privacy-policy.md) for free via **GitHub Pages**
   (Settings → Pages → deploy from `main` `/docs`) and use that URL.
5. Get the long-lived refresh token by running **locally**, once:
   ```bash
   pip install google-auth-oauthlib
   python scripts/get_refresh_token.py --client-secret client_secret.json
   ```
   > ⚠️ Python isn't currently on this machine's PATH. Install Python 3.11+ first, or run
   > this step in Google Colab. It opens a browser login and prints the three `YT_*` values.
6. Re-run step 5 **after** publishing to Production — tokens minted under Testing do not
   retroactively become long-lived.

## Phase 4 — GitHub Secrets  🙋

In the repo: **Settings → Secrets and variables → Actions → New repository secret**. Add:

| Secret | Value |
|---|---|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | full contents of the Phase-2 JSON key |
| `SHEET_ID` | the Phase-1 Sheet ID |
| `YT_CLIENT_ID` | from `get_refresh_token.py` output |
| `YT_CLIENT_SECRET` | from `get_refresh_token.py` output |
| `YT_REFRESH_TOKEN` | from `get_refresh_token.py` output |

## Phase 5 — First run & verify  🙋🤖

1. **Actions** tab → **publish-video** → **Run workflow** (manual `workflow_dispatch`).
2. Watch the log. Success = a new (public) video on your channel and that Sheet row flipped
   to `done` with its `video_id` filled in.
3. Start conservative — **upload as `unlisted` first** by editing the `--privacy` flag in
   the workflow, confirm quality, then switch to `public`.
4. Once verified, the daily **cron** (`0 6 * * *` UTC) takes over. Add more `cron:` lines
   for multiple runs/day.

---

## Guardrails to respect (these decide whether the channel survives)

- **API quota:** 10,000 units/day, ~1,600 per upload → **~6 uploads/day max** on default
  quota. Keep cron frequency under that.
- **Reused/inauthentic-content policy:** YouTube demonetizes/suspends channels posting
  near-identical high-volume content. **Vary key/tempo/instrumentation per row** and give
  each video a distinct title/thumbnail. Never reuse the same audio file.
- **7-day token expiry:** if uploads start failing ~a week after setup, the OAuth app
  slipped back to Testing status — re-publish to Production and re-mint the token.

## Out of scope (intentionally not built)

- No custom domain (GitHub Pages `github.io` domain is enough for the privacy policy).
- No Zapier in the critical path (cron + Sheets replaces it); Zapier only optional for a
  publish notification.
- No per-video AI thumbnail generation — the pipeline rotates a fixed pool of 9 pre-made
  branded thumbnails in `assets/thumbnails/` (`scripts/select_thumbnail.py`, indexed by
  Sheet row so it cycles evenly). Add more images to the folder to widen the rotation.
