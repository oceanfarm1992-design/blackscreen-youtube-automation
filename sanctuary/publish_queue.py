#!/usr/bin/env python3
"""
Upload every queued "Sanctuary of Sci" asset in --out-dir to YouTube (PUBLIC by
default). Needs SANCTUARY_YT_CLIENT_ID / _CLIENT_SECRET / _REFRESH_TOKEN.

All logic is shared with the other animated channels -- see
scripts/channel_kit.py. This file only binds the "Sanctuary of Sci" themes
(themes.py in this folder).

Usage:
    python sanctuary/publish_queue.py --out-dir out                    # public
    python sanctuary/publish_queue.py --out-dir out --privacy unlisted
"""
import os
import sys

import themes as T  # this channel's themes.py (script dir is first on sys.path)

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import channel_kit  # noqa: E402

if __name__ == "__main__":
    channel_kit.publish_main(T)
