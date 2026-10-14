#!/usr/bin/env python3
"""
"Aether & Ash" feature-thumbnail STYLE (1280x720). The rendering itself is
shared -- see channel_kit.render_thumbnail in scripts/channel_kit.py.

produce.py calls this once per feature upload with that upload's seed and
volume, so every upload gets its own thumbnail (a fresh crop of the ember photo, or
the hand-made art plus a 'VOL. N' badge). Run it locally to
regenerate the committed fallbacks in assets/aether/thumbnails/gen/.

Usage:
    python aether/make_thumbnails.py --theme abyssal_silence --seed 7 --volume 3 --out t.png
    python aether/make_thumbnails.py --all          # regenerate committed fallbacks
"""
import os
import sys

import themes as T  # this channel's themes.py (script dir is first on sys.path)

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import channel_kit  # noqa: E402

STYLE = {
    'background': 'assets/aether/thumbnails/src/ember_hand_blank.jpg',
    'pill_fill': (196, 92, 48),
    'text_fill': (255, 255, 255),
    'font_sizes': (88, 56),
    'min_font': 40,
    'glow_strength': 0.5,
    'headlines': {
        'abyssal_silence': ['ABYSSAL SILENCE', 'DARK AMBIENT'],
        'cosmic_drift': ['COSMIC DRIFT', 'SPACE AMBIENT'],
        'shadow_ink': ['SHADOW & INK', 'GOTHIC WRITING'],
        'slumber_of_ash': ['SLUMBER OF ASH', 'RESTORATIVE SLEEP'],
        'ethereal_ruins': ['ETHEREAL RUINS', 'DARK FANTASY'],
        'ember_solitude': ['EMBER SOLITUDE', 'QUIET REFLECTION'],
        'markov_chamber': ['MARKOV CHAMBER', 'GENERATIVE FOCUS'],
        'ash_rain_wind': ['ASH RAIN & WIND', 'DARK NATURE NOISE'],
        'black_hole': ['BLACK HOLE', 'RESONANCE'],
        'monastic_echoes': ['MONASTIC ECHOES', 'SACRED DARK CHANT'],
        'obsidian_tower': ['THE OBSIDIAN TOWER', 'DARK ACADEMIA'],
    },
    'glow': {
        'abyssal_silence': (45, 65, 115),
        'cosmic_drift': (120, 80, 200),
        'shadow_ink': (60, 75, 95),
        'slumber_of_ash': (75, 65, 140),
        'ethereal_ruins': (150, 120, 70),
        'ember_solitude': (175, 95, 55),
        'markov_chamber': (115, 75, 185),
        'ash_rain_wind': (80, 105, 110),
        'black_hole': (100, 40, 40),
        'monastic_echoes': (145, 115, 65),
        'obsidian_tower': (55, 65, 90),
    },
    'hand_made': {'calm_the_night', 'creative_flow', 'ember_focus', 'void_drone'},
}

if __name__ == "__main__":
    channel_kit.thumbnails_main(T, STYLE)
