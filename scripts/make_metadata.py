#!/usr/bin/env python3
"""
Build SEO metadata (title, description, tags) for a theme + format.

Usage:
    python make_metadata.py --theme rain --format long --hours 10 --out meta_long.json
    python make_metadata.py --theme auto --format short --out meta_short.json

Writes a JSON file consumed by the uploader, plus prints a human-readable summary.
"""
import argparse
import json
import sys

import themes as T

# Windows consoles default to cp1252 and choke on emoji in titles; force UTF-8.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CATEGORY_MUSIC = "10"


def build_metadata(theme: dict, fmt: str, hours: int) -> dict:
    if fmt == "short":
        title = theme["short_title"]
    else:
        title = theme["long_title"].format(hours=hours)

    # YouTube hard-caps titles at 100 characters.
    title = title[:100]

    hashtags = " ".join("#" + t.replace(" ", "") for t in theme["tags"][:3])
    description = (
        f"{theme['description']}\n\n{hashtags}"
        + T.DESCRIPTION_FOOTER.format(brand=T.BRAND_NAME, tagline=T.BRAND_TAGLINE)
    )

    tags = theme["tags"] + (["shorts"] if fmt == "short" else [])

    return {
        "theme": theme["key"],
        "format": fmt,
        "hours": hours if fmt == "long" else None,
        "title": title,
        "description": description,
        "tags": tags,
        "categoryId": CATEGORY_MUSIC,
        # Informational only; the actual upload visibility is set by
        # publish_queue.py --privacy (the workflow uploads PUBLIC by default).
        "privacyStatus": "public",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--theme", default="auto", help="theme key or 'auto' for date rotation")
    p.add_argument("--format", required=True, choices=["short", "long"])
    p.add_argument("--hours", type=int, default=T.LONG_HOURS_DEFAULT)
    p.add_argument("--out", default="metadata.json")
    args = p.parse_args()

    theme = T.resolve_theme(args.theme)
    meta = build_metadata(theme, args.format, args.hours)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"Wrote {args.out}")
    print(f"  theme : {meta['theme']} ({args.format})")
    print(f"  title : {meta['title']}")
    print(f"  tags  : {len(meta['tags'])} tags")


if __name__ == "__main__":
    main()
