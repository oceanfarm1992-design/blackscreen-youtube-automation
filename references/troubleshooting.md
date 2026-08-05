# Troubleshooting Index

| Symptom | Likely cause | Where to look |
|---|---|---|
| Upload step fails ~7 days after last manual auth | OAuth app still in "Testing" status | `youtube_oauth.md` — publish to Production |
| "Publish App" button fails / won't complete | Missing/invalid privacy policy URL, unverified domain, or blank scope justification | `youtube_oauth.md` — Publish App failure checklist |
| Upload fails with a quota-exceeded error | Default 10,000 units/day exceeded (~6 uploads/day max) | Reduce cron frequency or request a quota increase |
| Video flagged as spam / reused content | Near-identical audio/title/thumbnail across uploads | Vary key/tempo/instrumentation per row, distinct titles/thumbnails |
| GitHub Actions job hits a minute cap | Repo is private (2,000 min/month free tier cap) | Make the repo public for unmetered standard-runner minutes |
| Zapier stops triggering mid-month | Free tier 100-task/month cap hit, or a multi-step Zap on free tier | Move the core trigger to GitHub Actions cron; keep Zapier only for optional single-step notifications |
| Audio loop sounds like it "jumps" at the seam | No crossfade at loop point | Add a short crossfade (1-3 sec) between loop end and start in `generate_music.py` |

When the user reports an error, ask for the exact error message/text before assuming
which row above applies — auth errors, quota errors, and publish-flow errors look
different and need different fixes.
