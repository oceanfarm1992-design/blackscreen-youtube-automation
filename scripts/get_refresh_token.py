#!/usr/bin/env python3
"""
ONE-TIME, run locally (not in CI): opens a browser login and prints a refresh
token to store in GitHub Secrets as YT_REFRESH_TOKEN.

Prerequisite: download the OAuth "Desktop app" client secret JSON from Cloud
Console (APIs & Services -> Credentials) and pass its path here.

Run this again any time you re-publish the OAuth app (Testing -> Production) or
if the token is ever revoked — tokens issued under Testing status do not
retroactively become long-lived after publishing.

Usage:
    python get_refresh_token.py --client-secret client_secret.json
"""
import argparse
import shutil
import subprocess

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--client-secret", required=True)
    p.add_argument("--set-secrets", action="store_true",
                   help="set all 3 GitHub Actions secrets directly via gh (no copy-paste, "
                        "guarantees client id/secret/token all come from this same client)")
    args = p.parse_args()

    flow = InstalledAppFlow.from_client_secrets_file(args.client_secret, SCOPES)
    creds = flow.run_local_server(port=0)

    triples = [
        ("YT_CLIENT_ID", creds.client_id),
        ("YT_CLIENT_SECRET", creds.client_secret),
        ("YT_REFRESH_TOKEN", creds.refresh_token),
    ]

    if args.set_secrets:
        gh = shutil.which("gh") or r"C:\Program Files\GitHub CLI\gh.exe"
        print("\nSetting GitHub secrets via gh (run this inside the repo folder)...")
        for name, val in triples:
            subprocess.run([gh, "secret", "set", name], input=val, text=True, check=True)
            print(f"  set {name}")
        print("Done — all three secrets updated from the same OAuth client.")
    else:
        print("\nSave these as GitHub Secrets (ALL THREE, from this same run):")
        for name, val in triples:
            print(f"{name}={val}")


if __name__ == "__main__":
    main()
