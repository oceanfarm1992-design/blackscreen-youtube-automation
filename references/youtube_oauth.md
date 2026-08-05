# YouTube Data API v3 — One-Time OAuth Setup

This is the step most likely to break the pipeline. Read fully before starting.

## One-time setup steps

1. Create a Google Cloud project at console.cloud.google.com.
2. Enable **YouTube Data API v3** for that project.
3. Create **OAuth 2.0 credentials**, type **Desktop app**.
4. Configure the **OAuth consent screen**:
   - User type: External (unless the user has a Google Workspace org and wants Internal)
   - App name, developer contact email — required
   - Scopes: add the YouTube upload scope (`youtube.upload`), which Google treats as
     a **sensitive** (not restricted) scope
5. While in **Testing** status, add yourself as a test user and run the one-time
   local/Colab auth script to open a browser login, approve access, and capture the
   **refresh token**.
6. Store the refresh token in **GitHub Secrets** — never in code.

## The 7-day expiry problem (and the fix)

Refresh tokens issued while the app is in **Testing** publishing status expire after
7 days. This is a Cloud Console app-status setting, not a YouTube-specific limitation.
Symptom: the upload step in GitHub Actions starts failing with an auth error roughly
a week after the last manual re-auth.

**Fix: publish the app to Production.**

1. Cloud Console → your project → **APIs & Services → OAuth consent screen**
2. Under **Publishing status**, click **Publish App**
3. Sensitive (not restricted) scopes like YouTube upload do **not** require Google's
   full security review to publish for a small number of users — you'll see a warning
   screen, click through it
4. Once published, refresh tokens no longer expire on a 7-day cycle
5. **Re-run the one-time auth flow after publishing** — tokens issued under Testing do
   not retroactively become long-lived. Get a fresh token and update the GitHub Secret.

## "Publish App" fails or won't complete

Publishing for a sensitive scope generally requires:

- **App name, developer contact email** — straightforward
- **Privacy policy URL** — this is the usual blocker. It must be:
  - Publicly accessible (not a password-protected page or a private Google Doc link)
  - Actually reachable when Google's validator checks it (test the URL yourself first)
  - Cheapest fix: host a minimal static privacy-policy page for free via **GitHub
    Pages** (the same repo can serve this) or a public Notion/Google Sites page.
    Content can be a simple template stating what data is accessed (YouTube upload
    scope only) and that it isn't shared or sold — doesn't need to be lawyer-drafted
    for a single-user personal tool.
- **Authorized domains** — must match the domain hosting the privacy policy. A
  `username.github.io` GitHub Pages domain is typically pre-verified and doesn't
  require the separate Search Console domain-verification step that a custom domain
  would need.
- **App logo** — optional, safe to skip.
- **Terms of service URL** — often optional depending on scope combination; safe to
  skip for a single sensitive scope like this.
- **Scope justification text** — some consent-screen flows ask for a short written
  justification for why the app needs the sensitive scope even without full review.
  Leaving this blank can silently block publishing — fill it in with a one-line
  explanation ("personal automated upload tool for my own YouTube channel").

If publishing still fails after checking all of the above, get the exact error text
or describe exactly where the flow stops (which field, error message, or silent
button failure) — that narrows it to one of the causes above rather than guessing.

## Ongoing quota limits (separate from the token issue)

Default quota is 10,000 units/day. An upload costs roughly 1,600 units, so about 6
uploads/day max without requesting a quota increase. This is unrelated to the token
expiry problem above — a token failure and a quota failure look different in the
error response (auth error vs. quota-exceeded error), so check which one is actually
happening before applying a fix.
