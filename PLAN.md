# Rollout Plan — Meditated Sleeping Production Pipeline

The **code is done and verified**: the daily workflow produces the day's batch — **6
long-forms (10h) + 6 Shorts (59s) = 12 videos**, one per run every 2h — brands them
`#0D0D0D`, writes SEO metadata, and QCs durations. Long-forms upload through the main Cloud
project; Shorts upload through a **separate Cloud project** (`YT_SHORTS_*`) so each project
stays under its own 10,000-unit/day quota. What remains is optional account setup so the
videos can be uploaded to your channel.

Legend: 🤖 = automated · 🙋 = you do it once

---

## Phase 0 — Production pipeline (done & verified 🤖)

- 7-music library, 4-per… **3-per-day** date rotation, `#0D0D0D` branded frames + black
  thumbnail, per-music SEO metadata, QC, manifest. Optional wellness frequency layers
  (Solfeggio, 432 Hz, binaural/isochronic brainwaves, singing bowl).
- All 7 musics synthesize cleanly; the long/short render paths produce **1920×1080** /
  **1080×1920** at exact durations.
- The daily GitHub Actions workflow runs on cron with **no secrets required** — without
  them it produces the assets and saves metadata as run artifacts.

## Phase 1 — Turn on automatic publishing (optional)  🙋

Only needed if you want the workflow to upload each day's videos to the channel (as
**public** by default). This is the fragile part.

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
| `YT_CLIENT_ID` | from the main OAuth client (long-forms) |
| `YT_CLIENT_SECRET` | from the main OAuth client |
| `YT_REFRESH_TOKEN` | the minted long-lived token |
| `YT_SHORTS_CLIENT_ID` | from the **2nd** OAuth client, Shorts project |
| `YT_SHORTS_CLIENT_SECRET` | from the 2nd OAuth client |
| `YT_SHORTS_REFRESH_TOKEN` | long-lived token for the same channel, 2nd project |

The `YT_SHORTS_*` set is **optional** — if absent, Shorts fall back to the main project
(watch the combined quota). With it, Shorts draw on their own 10,000-unit/day quota.

Once these exist, the daily run uploads the day's 12 videos as **public**. No Google Sheet
or service account is needed — the musics are chosen by the date.

## Phase 3 — First run & verify  🙋🤖

1. **Actions** tab → **daily-produce** → **Run workflow** (set hours 8–10 if you like;
   set `privacy` to `private`/`unlisted` for this run if you want to preview first).
2. Watch the log: a manual full run produces the 6 long-forms + 6 Shorts, prints the QC
   manifests, and (if secrets are set) uploads them.
3. Check the videos on your channel. The default is **public** — switch the `privacy`
   input to `private` for the first run if you'd rather review before going live.
4. The **12 daily crons** (every 2h, 00:00–22:00 UTC) then run on their own, one
   video each — slots 0-5 long-forms, slots 6-11 Shorts.

---

## Guardrails (these decide whether the channel survives)

- **API quota:** 10,000 units/day **per Cloud project**; ~1,600 per upload. Uploads are
  split across two projects: long-forms → main project (6 × 1,650 = **9,900, tight**),
  Shorts → `YT_SHORTS` project (6 × 1,600 = 9,600). Each stays under the free cap, but the
  long side has only 100 units of headroom — one retry could tip it over. Raising
  `LONGS_PER_DAY`/`SHORTS_PER_DAY` in `themes.py` must keep **each project** under 10,000.
- **Theme library (11) < 12 slots:** one music repeats each day (as a long + a Short).
  Add a 12th theme to `THEMES` in `themes.py` if you want all 12 distinct.
- **Daily upload count:** 12 uploads/day may bump YouTube's per-channel daily upload limit
  on a new/unverified channel — phone-verify the channel and ramp up if you see errors.
- **Reused/inauthentic-content policy:** YouTube demonetizes/suspends channels posting
  near-identical high-volume content. Audio is re-synthesized each run with a date-based
  seed so no two uploads share a file; titles/descriptions vary by music. The rotation
  cycles the whole music library in order across days rather than repeating one.
- **7-day token expiry:** if uploads start failing ~a week after setup, the OAuth app
  slipped back to Testing — re-publish to Production and re-mint the token.
- **Long renders:** each 10h file is ~1 GB+ and uploads slowly; each run makes one video
  and the workflow allows 90 minutes. (YouTube rejected exactly-12h uploads as "too
  long", so long-form is 10h.)
- **Spread schedule:** 12 crons/day every 2h (00:00–22:00 UTC), alternating long/short,
  one video each, so renders/uploads never run simultaneously.
- **Auto-public:** uploads go **public** with no manual review step. Anything off (audio
  glitch, wrong metadata) is live immediately — set the `privacy` input to `private` for
  a manual test run before trusting the daily cron.

## Notes on the pivot from the earlier version

- The **Google Sheets queue** and its service account are **removed** — the theme now
  rotates by date, so there's nothing to hand-edit. (Recoverable from git history if ever
  wanted.)
- Thumbnails are now the single **`#0D0D0D` brand** per spec (zero distractions). The 9
  scenic thumbnails from before are kept in `assets/thumbnails/` but are **not used**.
