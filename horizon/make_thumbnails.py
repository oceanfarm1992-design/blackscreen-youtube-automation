#!/usr/bin/env python3
"""
"The Static Horizon" feature-thumbnail STYLE (1280x720). The rendering itself is
shared -- see channel_kit.render_thumbnail in scripts/channel_kit.py.

produce.py calls this once per feature upload with that upload's seed and
volume, so every upload gets its own thumbnail (a fresh noise background from the
video's own engine, plus '14 MIN · VOL. N'). Run it locally to
regenerate the committed fallbacks in assets/horizon/thumbnails/gen/.

Usage:
    python horizon/make_thumbnails.py --theme night_drive --seed 7 --volume 3 --out t.png
    python horizon/make_thumbnails.py --all          # regenerate committed fallbacks
"""
import os
import sys

import themes as T  # this channel's themes.py (script dir is first on sys.path)

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import channel_kit  # noqa: E402

STYLE = {
    'background': 'noise',
    'pill_fill': (160, 60, 170),
    'text_fill': (240, 230, 250),
    'font_sizes': (72, 46),
    'min_font': 36,
    'glow_strength': 0.6,
    'headlines': {
        'night_drive': ['NIGHT DRIVE', 'NOSTALGIC SYNTH AMBIENT'],
        'empty_parking_structure': ['EMPTY PARKING', 'LIMINAL SPACE AMBIENT'],
        'forgotten_mall': ['FORGOTTEN MALL', 'MUFFLED NOSTALGIC AMBIENT'],
        'static_transmission': ['STATIC TRANSMISSION', 'LOST SIGNAL AMBIENT'],
        'rain_interstate': ['RAIN ON THE INTERSTATE', 'HIGHWAY AMBIENT'],
        'suburban_hush': ['SUBURBAN HUSH', 'QUIET NIGHT AMBIENT'],
        'vhs_afterglow': ['VHS AFTERGLOW', 'RETRO SYNTH AMBIENT'],
        'neon_corridor': ['NEON CORRIDOR', 'RETRO LIMINAL AMBIENT'],
        'last_broadcast': ['LAST BROADCAST', 'EERIE SIGNAL AMBIENT'],
        'overpass_3am': ['OVERPASS AT 3AM', 'LIMINAL NIGHT AMBIENT'],
    },
    'hand_made': set(),
}

if __name__ == "__main__":
    channel_kit.thumbnails_main(T, STYLE)
