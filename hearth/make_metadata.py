#!/usr/bin/env python3
"""
Build SEO metadata (title, description, tags) for a "Hearth & Quill" theme + format.

Usage:
    python make_metadata.py --theme candlelit_study --format long --out meta_long.json
    python make_metadata.py --theme auto --format short --out meta_short.json

Writes a JSON file consumed by the uploader, plus prints a human-readable summary.
"""
import argparse
import json
import sys

import themes as T

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CATEGORY_MUSIC = "10"
TAG_CHAR_LIMIT = 480


def pack_tags(theme: dict, fmt: str) -> list:
    pool = list(theme["tags"]) + T.GLOBAL_TAGS
    if fmt == "short":
        pool = ["shorts", "short video"] + pool
    tags, seen, used = [], set(), 0
    for t in pool:
        t = t.strip()
        key = t.lower()
        if not t or key in seen:
            continue
        cost = len(t) + (2 if " " in t else 0) + 1
        if used + cost > TAG_CHAR_LIMIT:
            continue
        tags.append(t)
        seen.add(key)
        used += cost
    return tags


def build_metadata(theme: dict, fmt: str) -> dict:
    title = theme["short_title"] if fmt == "short" else theme["long_title"]
    title = title[:100]

    lead = f"14 Minutes of {theme['name']}" if fmt == "long" else theme["name"]
    hashtags = " ".join("#" + t.replace(" ", "") for t in theme["tags"][:3])
    if fmt == "short":
        hashtags += " #shorts"
    visual_line = (
        " Paired with a slow, generative ambient animation — unique every "
        "time, never a static loop." if fmt == "long" else ""
    )
    description = (
        f"{lead}.{visual_line}\n\n"
        f"{theme['description']}\n\n"
        f"\U0001F3A7 How to use: play at a low, comfortable volume to focus, "
        f"study, write, read, or relax — leave it on for uninterrupted work.\n\n"
        f"Perfect for {T.PERFECT_FOR}.\n\n"
        f"{hashtags}"
        + T.DESCRIPTION_FOOTER.format(brand=T.BRAND_NAME, tagline=T.BRAND_TAGLINE)
    )

    tags = pack_tags(theme, fmt)

    return {
        "theme": theme["key"],
        "format": fmt,
        "title": title,
        "description": description,
        "tags": tags,
        "categoryId": CATEGORY_MUSIC,
        "privacyStatus": "public",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--theme", default="auto", help="theme key or 'auto' for date rotation")
    p.add_argument("--format", required=True, choices=["short", "long"])
    p.add_argument("--out", default="metadata.json")
    args = p.parse_args()

    theme = T.resolve_theme(args.theme)
    meta = build_metadata(theme, args.format)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"Wrote {args.out}")
    print(f"  theme : {meta['theme']} ({args.format})")
    print(f"  title : {meta['title']}")
    print(f"  tags  : {len(meta['tags'])} tags")


if __name__ == "__main__":
    main()
