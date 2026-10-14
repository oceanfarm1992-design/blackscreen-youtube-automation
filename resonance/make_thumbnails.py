#!/usr/bin/env python3
"""
"Aether Resonance" feature-thumbnail STYLE (1280x720). The rendering itself is
shared -- see channel_kit.render_thumbnail in scripts/channel_kit.py.

produce.py calls this once per feature upload with that upload's seed and
volume, so every upload gets its own thumbnail (a fresh noise background from the
video's own engine, plus '14 MIN · VOL. N'). Run it locally to
regenerate the committed fallbacks in assets/resonance/thumbnails/gen/.

Usage:
    python resonance/make_thumbnails.py --theme still_water --seed 7 --volume 3 --out t.png
    python resonance/make_thumbnails.py --all          # regenerate committed fallbacks
"""
import os
import sys

import themes as T  # this channel's themes.py (script dir is first on sys.path)

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import channel_kit  # noqa: E402

STYLE = {
    'background': 'noise',
    'pill_fill': (100, 130, 150),
    'text_fill': (245, 250, 250),
    'font_sizes': (72, 48),
    'min_font': 34,
    'glow_strength': 0.6,
    'headlines': {
        'still_water': ['STILL WATER', '432 Hz SOUND BATH'],
        'crown_light': ['CROWN LIGHT', '963 Hz SOUND BATH'],
        'root_anchor': ['ROOT ANCHOR', '396 Hz GROUNDING'],
        'heart_bloom': ['HEART BLOOM', '639 Hz SINGING BOWL'],
        'third_eye_drift': ['THIRD EYE DRIFT', '852 Hz SOUND BATH'],
        'cellular_renewal': ['CELLULAR RENEWAL', '285 Hz HEALING DRONE'],
        'miracle_tone': ['MIRACLE TONE', '528 Hz SOUND BATH'],
        'singing_bowl_sanctuary': ['SINGING BOWL SANCTUARY', 'OM 136 Hz'],
        'theta_gateway': ['THETA GATEWAY', 'GENERATIVE DRONE'],
        'pink_noise_veil': ['PINK NOISE VEIL', 'SOOTHING SOUND BATH'],
    },
    'hand_made': set(),
}

if __name__ == "__main__":
    channel_kit.thumbnails_main(T, STYLE)
