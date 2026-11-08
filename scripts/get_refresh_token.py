#!/usr/bin/env python3
"""
ONE-TIME per channel, run locally (not in CI): opens a browser login and stores
that channel's refresh token in GitHub Secrets.

This app uses ONE Google Cloud project / ONE OAuth client for every channel
(YouTube API Services policy: one project per API client -- several projects
acting as one, e.g. for extra quota, gets the projects suspended). So:
  * always pass the SAME client secret file (the app's single OAuth client);
  * sign in with the Google account that owns the channel, and pick that
    channel if Google asks which one;
  * each channel then gets its own <PREFIX>_REFRESH_TOKEN, while
    YT_CLIENT_ID / YT_CLIENT_SECRET are shared and set once.

Run it again whenever a token is revoked or expires (tokens issued while the
OAuth app is in "Testing" expire after 7 days -- publish it to Production).

Usage (from inside the repo folder):
    # once: the main channel, which also stores the shared client id/secret
    python scripts/get_refresh_token.py --client-secret client_secret.json --set-secrets

    # each other channel: same file, its own prefix
    python scripts/get_refresh_token.py --client-secret client_secret.json --prefix HEARTH_YT --set-secrets
    (AETHER_YT, SANCTUARY_YT, HORIZON_YT, RESONANCE_YT, MANOR_YT likewise)
"""
import argparse
import shutil
import subprocess

from google_auth_oauthlib.flow import InstalledAppFlow

# upload = video uploads + thumbnails; youtube = playlist create/manage (needed
# by the auto-playlist step). Tokens minted before playlists existed carry only
# the upload scope and keep working for uploads — re-mint to enable playlists.
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--client-secret", required=True)
    p.add_argument("--prefix", default="YT",
                   help="whose refresh token this is: YT (Meditated Sleeping), HEARTH_YT, "
                        "AETHER_YT, SANCTUARY_YT, HORIZON_YT, RESONANCE_YT or MANOR_YT")
    p.add_argument("--set-secrets", action="store_true",
                   help="store the token directly with gh (no copy-paste)")
    p.add_argument("--set-client", action="store_true",
                   help="also store the shared YT_CLIENT_ID / YT_CLIENT_SECRET "
                        "(done automatically for --prefix YT)")
    args = p.parse_args()

    flow = InstalledAppFlow.from_client_secrets_file(args.client_secret, SCOPES)
    creds = flow.run_local_server(port=0)

    pairs = [(f"{args.prefix}_REFRESH_TOKEN", creds.refresh_token)]
    if args.prefix == "YT" or args.set_client:
        pairs = [("YT_CLIENT_ID", creds.client_id),
                 ("YT_CLIENT_SECRET", creds.client_secret)] + pairs
    print(f"\nOAuth client used: {creds.client_id}")
    print("Every channel must use this SAME client (one Cloud project for the whole app).")

    if args.set_secrets:
        gh = shutil.which("gh") or r"C:\Program Files\GitHub CLI\gh.exe"
        print("\nSetting GitHub secrets via gh (run this inside the repo folder)...")
        for name, val in pairs:
            subprocess.run([gh, "secret", "set", name], input=val, text=True, check=True)
            print(f"  set {name}")
    else:
        print("\nSave these as GitHub Secrets:")
        for name, val in pairs:
            print(f"{name}={val}")


if __name__ == "__main__":
    main()
