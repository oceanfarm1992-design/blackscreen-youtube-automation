#!/usr/bin/env python3
"""
"Hearth & Quill" feature-thumbnail STYLE (1280x720). The rendering itself is
shared -- see channel_kit.render_thumbnail in scripts/channel_kit.py.

produce.py calls this once per feature upload with that upload's seed and
volume, so every upload gets its own thumbnail (a fresh noise background from the
video's own engine, plus '14 MIN · VOL. N'). Run it locally to
regenerate the committed fallbacks in assets/hearth/thumbnails/gen/.

Usage:
    python hearth/make_thumbnails.py --theme candlelit_study --seed 7 --volume 3 --out t.png
    python hearth/make_thumbnails.py --all          # regenerate committed fallbacks
"""
import os
import sys

import themes as T  # this channel's themes.py (script dir is first on sys.path)

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import channel_kit  # noqa: E402

STYLE = {
    'background': 'noise',
    'pill_fill': (196, 134, 47),
    'text_fill': (255, 250, 235),
    'font_sizes': (80, 52),
    'min_font': 40,
    'glow_strength': 0.6,
    'headlines': {
        'candlelit_study': ['CANDLELIT STUDY', 'WARM PIANO AMBIENT'],
        'leaded_glass_rain': ['LEADED GLASS RAIN', 'CELLO & RAIN AMBIENT'],
        'quiet_scriptorium': ['QUIET SCRIPTORIUM', 'WRITING AMBIENT'],
        'tavern_hearth': ['TAVERN HEARTH', 'COZY FANTASY AMBIENT'],
        'lantern_ink': ['LANTERN & INK', 'MINIMAL PIANO AMBIENT'],
        'old_library_hush': ['OLD LIBRARY HUSH', 'COZY STUDY AMBIENT'],
        'winter_study': ['WINTER STUDY', 'FIRESIDE CELLO AMBIENT'],
        'moonlit_manuscript': ['MOONLIT MANUSCRIPT', 'NIGHT WRITING AMBIENT'],
        'hearthside_tales': ['HEARTHSIDE TALES', 'CELLO STORYTELLING'],
        'ink_parchment': ['INK & PARCHMENT', 'MINIMAL WRITING AMBIENT'],
    },
    'hand_made': set(),
}

if __name__ == "__main__":
    channel_kit.thumbnails_main(T, STYLE)
