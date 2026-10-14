#!/usr/bin/env python3
"""
Render, describe and QC the day's "The Static Horizon" video(s). Nothing is
uploaded here -- publishing is the separate publish_queue.py step.

All logic is shared with the other animated channels -- see
scripts/channel_kit.py. This file only binds the "The Static Horizon" themes
(themes.py in this folder).

Usage:
    python horizon/produce.py --slot 0 --date 2026-10-20     # one scheduled video
    python horizon/produce.py --longs 1 --shorts 1             # test batch
    python horizon/produce.py --theme night_drive --format both
"""
import os
import sys

import themes as T  # this channel's themes.py (script dir is first on sys.path)

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import channel_kit  # noqa: E402

if __name__ == "__main__":
    channel_kit.produce_main(T)
