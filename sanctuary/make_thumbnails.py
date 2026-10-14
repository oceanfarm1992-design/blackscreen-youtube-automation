#!/usr/bin/env python3
"""
"Sanctuary of Sci" feature-thumbnail STYLE (1280x720). The rendering itself is
shared -- see channel_kit.render_thumbnail in scripts/channel_kit.py.

produce.py calls this once per feature upload with that upload's seed and
volume, so every upload gets its own thumbnail (a fresh noise background from the
video's own engine, plus '14 MIN · VOL. N'). Run it locally to
regenerate the committed fallbacks in assets/sanctuary/thumbnails/gen/.

Usage:
    python sanctuary/make_thumbnails.py --theme sleeper_drift --seed 7 --volume 3 --out t.png
    python sanctuary/make_thumbnails.py --all          # regenerate committed fallbacks
"""
import os
import sys

import themes as T  # this channel's themes.py (script dir is first on sys.path)

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import channel_kit  # noqa: E402

STYLE = {
    'background': 'noise',
    'pill_fill': (70, 120, 210),
    'text_fill': (255, 255, 255),
    'font_sizes': (88, 56),
    'min_font': 40,
    'glow_strength': 0.6,
    'headlines': {
        'sleeper_drift': ['SLEEPER DRIFT', 'DEEP SPACE DRONE'],
        'nebula_watch': ['NEBULA WATCH', 'COSMIC OBSERVATORY'],
        'station_hum': ['STATION HUM', 'SPACE STATION AMBIENCE'],
        'cryo_bay': ['CRYO BAY', 'COLD SLEEPER AMBIENT'],
        'observatory_deck': ['OBSERVATORY DECK', 'GENERATIVE FOCUS'],
        'ion_trail': ['ION TRAIL', 'CODING FOCUS MUSIC'],
        'long_dark': ['THE LONG DARK', 'MINIMAL DEEP DRONE'],
        'starlight_convergence': ['STARLIGHT CONVERGENCE', 'HOPEFUL COSMIC AMBIENT'],
        'zero_g_drift': ['ZERO-G DRIFT', 'WEIGHTLESS AMBIENT'],
        'signal_lost': ['SIGNAL LOST', 'MYSTERIOUS SPACE STATIC'],
    },
    'hand_made': set(),
}

if __name__ == "__main__":
    channel_kit.thumbnails_main(T, STYLE)
