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

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--client-secret", required=True)
    args = p.parse_args()

    flow = InstalledAppFlow.from_client_secrets_file(args.client_secret, SCOPES)
    creds = flow.run_local_server(port=0)

    print("\nSave these as GitHub Secrets:")
    print(f"YT_CLIENT_ID={creds.client_id}")
    print(f"YT_CLIENT_SECRET={creds.client_secret}")
    print(f"YT_REFRESH_TOKEN={creds.refresh_token}")


if __name__ == "__main__":
    main()
