#!/usr/bin/env python3
"""
Read-only check of every channel's YouTube sign-in. For each channel it uses
the app's one OAuth client + that channel's refresh token, asks YouTube which
channel the token belongs to (channels.list mine=true, 1 quota unit), and
compares it with the channel the token is meant for. Uploads nothing.

Catches: a token not set yet, an expired/revoked token, a token minted with
another project's client (after the move to one project), and a token saved
for the WRONG channel (picked the wrong one at Google's channel chooser).

Usage: python scripts/check_youtube_auth.py [--summary $GITHUB_STEP_SUMMARY]
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# secret prefix -> the channel it must belong to
CHANNELS = {
    "YT": "Meditated Sleeping",
    "HEARTH_YT": "Hearth & Quill",
    "AETHER_YT": "Aether & Ash",
    "SANCTUARY_YT": "Sanctuary of Sci",
    "HORIZON_YT": "The Static Horizon",
    "RESONANCE_YT": "Aether Resonance",
    "MANOR_YT": "Moss & Manor",
}


def _key(s):
    return re.sub(r"[^a-z0-9]", "", s.lower().replace("&", "and"))


def names_match(expected, actual):
    e, a = _key(expected), _key(actual)
    return bool(e and a and (e in a or a in e))


def check(prefix, expected):
    """(status, detail) for one channel's token."""
    if not os.environ.get(f"{prefix}_REFRESH_TOKEN"):
        return "MISSING", f"{prefix}_REFRESH_TOKEN is not set"
    try:
        import upload_youtube as U
        res = U.get_service(prefix).channels().list(part="snippet", mine=True).execute()
    except Exception as e:  # invalid_grant, unauthorized_client, 403 ...
        msg = str(e)
        if "unauthorized_client" in msg:
            msg = "token was made with a different OAuth client -- sign in again with the shared one"
        elif "invalid_grant" in msg:
            msg = "token expired or revoked -- sign in again"
        return "FAILED", msg[:200]
    items = res.get("items", [])
    if not items:
        return "FAILED", "signed in, but this Google account has no YouTube channel"
    title = items[0]["snippet"]["title"]
    if names_match(expected, title):
        return "OK", f"{title} ({items[0]['id']})"
    return "WRONG CHANNEL", f"token belongs to '{title}' ({items[0]['id']})"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--summary", default=None, help="append a markdown table here")
    args = p.parse_args()
    if not (os.environ.get("YT_CLIENT_ID") and os.environ.get("YT_CLIENT_SECRET")):
        sys.exit("YT_CLIENT_ID / YT_CLIENT_SECRET (the app's one OAuth client) are not set")

    rows = [(prefix, expected, *check(prefix, expected)) for prefix, expected in CHANNELS.items()]
    for prefix, expected, status, detail in rows:
        print(f"{status:13} {expected:20} [{prefix}_REFRESH_TOKEN] {detail}")
    if args.summary:
        with open(args.summary, "a", encoding="utf-8") as f:
            f.write("### YouTube sign-in check (one shared OAuth client)\n\n")
            f.write("| Channel | Secret | Result | Details |\n|---|---|---|---|\n")
            for prefix, expected, status, detail in rows:
                icon = {"OK": "✅"}.get(status, "❌")
                f.write(f"| {expected} | `{prefix}_REFRESH_TOKEN` | {icon} {status} | {detail} |\n")
    bad = [r for r in rows if r[2] != "OK"]
    if bad:
        print(f"\n{len(bad)} channel(s) need a fresh sign-in "
              "(python scripts/get_refresh_token.py --client-secret client_secret.json "
              "--prefix <PREFIX> --set-secrets).")
        sys.exit(1)
    print("\nAll 7 channels signed in through the one shared client.")


if __name__ == "__main__":
    main()
