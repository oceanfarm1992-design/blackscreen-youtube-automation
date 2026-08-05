# Privacy Policy

_Last updated: 2026-08-05_

This is the privacy policy for a **personal, single-user automated tool** that uploads
ambient/calm-music videos to the owner's own YouTube channel.

## What data the app accesses

- **YouTube Data API v3 (`youtube.upload` scope)** — used solely to upload video files
  and set thumbnails/metadata on the app owner's own YouTube channel.
- **Google Sheets API** — used solely to read a private content-queue spreadsheet owned
  by the app owner and write back the resulting video ID and status.

## What the app does NOT do

- It does not collect, store, or process data from any third party or end user.
- It does not share, sell, or transfer any data to anyone.
- It does not use the data for advertising, profiling, or analytics.

## Data storage

The app holds no user database. OAuth credentials and the service-account key are stored
only as encrypted GitHub Actions Secrets and are used at runtime to authenticate to
Google's APIs. No content is retained beyond the transient files created during a single
render/upload run.

## Contact

Questions about this policy can be directed to the repository owner via the GitHub
repository's Issues page.
