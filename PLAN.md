# Rollout Plan — Meditated Sleeping Production Pipeline

The **code is done and verified**: the daily workflow produces both videos (59s Short +
8–12h long-form), brands them `#0D0D0D`, writes SEO metadata, and QCs durations. What
remains is optional account setup so the queued videos can be uploaded to your channel.

Legend: 🤖 = automated · 🙋 = you do it once

---

## Phase 0 — Production pipeline (done & verified 🤖)

- Theme rotation, 4 theme audio synths, `#0D0D0D` branded frames, metadata, QC, manifest.
- Verified locally: today's Short renders at **1080×1920, 59.0s**; the long-form render
  path renders at **1920×1080** with exact duration. All four themes synthesize cleanly.
- The daily GitHub Actions workflow runs on cron with **no secrets required** — without
  them it produces the assets and saves metadata as run artifacts.

## Phase 1 — Turn on automatic queuing (optional)  🙋

Only needed if you want the workflow to upload each day's videos to the channel as
**private drafts** (instead of just producing the files). This is the fragile part.

1. [Google Cloud Console](https://console.cloud.google.com): create/pick a project,
   enable **YouTube Data API v3**.
2. Create **OAuth 2.0 credentials → Desktop app**; download the client-secret JSON.
3. Configure the **OAuth consent screen** (External), add the `youtube.upload` scope,
   add yourself as a test user.
4. **Publish the app to Production.** Tokens minted while the app is in *Testing* expire
   after **7 days** and uploads then fail silently. Sensitive scopes like `youtube.upload`
   don't need Google's full review for a personal tool — click through the warning. The
   usual blocker is a **privacy-policy URL**: host [`docs/privacy-policy.md`](docs/privacy-policy.md)
   free via **GitHub Pages** (Settings → Pages → deploy from `main` `/docs`).
   Full detail: [`references/youtube_oauth.md`](references/youtube_oauth.md).
5. Mint the long-lived refresh token **locally, once**:
   ```bash
   pip install google-auth-oauthlib
   python scripts/get_refresh_token.py --client-secret client_secret.json
   ```
   Re-run this **after** publishing to Production (Testing-era tokens don't become
   long-lived retroactively).

## Phase 2 — GitHub Secrets  🙋

Repo → **Settings → Secrets and variables → Actions**. Add the three values printed by
`get_refresh_token.py`:

| Secret | Value |
|---|---|
| `YT_CLIENT_ID` | from the OAuth client |
| `YT_CLIENT_SECRET` | from the OAuth client |
| `YT_REFRESH_TOKEN` | the minted long-lived token |

Once these exist, the daily run uploads both videos as **private**. No Google Sheet or
service account is needed — the theme is chosen by the date.

## Phase 3 — First run & verify  🙋🤖

1. **Actions** tab → **daily-produce** → **Run workflow** (set hours 8–12 if you like).
2. Watch the log: it produces the Short + long-form, prints the QC manifests, and (if
   secrets are set) uploads both as private.
3. Review the two private videos on your channel, then flip to **public** when happy.
4. The daily **cron** (`0 6 * * *` UTC) then runs on its own.

---

## Guardrails (these decide whether the channel survives)

- **API quota:** 10,000 units/day; ~1,600 per upload → **~6 uploads/day max**. Two
  videos/day is well within it.
- **Reused/inauthentic-content policy:** YouTube demonetizes/suspends channels posting
  near-identical high-volume content. Audio is re-synthesized each run with a date-based
  seed so no two uploads share a file; titles/descriptions vary by theme. Don't crank the
  cron to many-per-day with the same theme.
- **7-day token expiry:** if uploads start failing ~a week after setup, the OAuth app
  slipped back to Testing — re-publish to Production and re-mint the token.
- **Long renders:** an 8–12h file is ~1 GB+ and uploads slowly; the workflow allows 120
  minutes. Keep to one long-form per run.

## Notes on the pivot from the earlier version

- The **Google Sheets queue** and its service account are **removed** — the theme now
  rotates by date, so there's nothing to hand-edit. (Recoverable from git history if ever
  wanted.)
- Thumbnails are now the single **`#0D0D0D` brand** per spec (zero distractions). The 9
  scenic thumbnails from before are kept in `assets/thumbnails/` but are **not used**.
