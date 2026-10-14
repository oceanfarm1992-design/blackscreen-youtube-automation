#!/usr/bin/env python3
"""
Build SEO metadata (title, description, tags) for a "Hearth & Quill" theme + format.

All logic is shared with the other animated channels -- see
scripts/channel_kit.py. This file only binds the "Hearth & Quill" themes
(themes.py in this folder).

Usage:
    python hearth/make_metadata.py --theme candlelit_study --format long --volume 3 --out meta.json
"""
import os
import sys

import themes as T  # this channel's themes.py (script dir is first on sys.path)

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import channel_kit  # noqa: E402

if __name__ == "__main__":
    channel_kit.metadata_main(T)
