#!/usr/bin/env python3
"""
"Moss & Manor" feature-thumbnail STYLE (1280x720). The rendering itself is
shared -- see channel_kit.render_thumbnail in scripts/channel_kit.py.

produce.py calls this once per feature upload with that upload's seed and
volume, so every upload gets its own thumbnail (a fresh noise background from the
video's own engine, plus '14 MIN · VOL. N'). Run it locally to
regenerate the committed fallbacks in assets/manor/thumbnails/gen/.

Usage:
    python manor/make_thumbnails.py --theme greenhouse_ruins --seed 7 --volume 3 --out t.png
    python manor/make_thumbnails.py --all          # regenerate committed fallbacks
"""
import os
import sys

import themes as T  # this channel's themes.py (script dir is first on sys.path)

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import channel_kit  # noqa: E402

STYLE = {
    'background': 'noise',
    'pill_fill': (90, 125, 80),
    'text_fill': (235, 240, 225),
    'font_sizes': (68, 46),
    'min_font': 34,
    'glow_strength': 0.6,
    'headlines': {
        'greenhouse_ruins': ['GREENHOUSE RUINS', 'GUITAR & NATURE AMBIENT'],
        'rainy_cottage_garden': ['RAINY COTTAGE GARDEN', 'GUITAR & RAIN AMBIENT'],
        'misty_forest_floor': ['MISTY FOREST FLOOR', 'GUITAR & WIND AMBIENT'],
        'creek_hollow': ['CREEK HOLLOW', 'GUITAR & STREAM AMBIENT'],
        'ancient_grove': ['ANCIENT GROVE', 'BOWED BASS & WIND'],
        'thunder_garden': ['THUNDER GARDEN', 'GUITAR & RAIN AMBIENT'],
        'mossy_stonework': ['MOSSY STONEWORK', 'MINIMAL NATURE AMBIENT'],
        'wildflower_meadow': ['WILDFLOWER MEADOW', 'GUITAR & BIRDSONG'],
        'fernwood_path': ['FERNWOOD PATH', 'GUITAR & CREEK AMBIENT'],
        'twilight_greenhouse': ['TWILIGHT GREENHOUSE', 'DUSK GUITAR AMBIENT'],
    },
    'hand_made': set(),
}

if __name__ == "__main__":
    channel_kit.thumbnails_main(T, STYLE)
