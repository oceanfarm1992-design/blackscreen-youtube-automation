#!/usr/bin/env python3
"""
Theme definitions, daily rotation, and SEO metadata for "The Static
Horizon" channel (nostalgic, tape-degraded hauntology/liminal-space
ambient -- late-night driving, forgotten spaces, lost signals).

Same contract as aether/themes.py, sanctuary/themes.py, hearth/themes.py --
only the data below differs.

10 themes rotate through a sliding daily window (see daily_selection below).
"""
from datetime import date

ANCHOR = date(2026, 10, 4)

FEATURE_SECONDS = 870  # 14:30
SHORT_SECONDS = 59

LONGS_PER_DAY = 1
SHORTS_PER_DAY = 1
DAILY_COUNT = LONGS_PER_DAY + SHORTS_PER_DAY

# Ordered rotation. `synth` names a function in scripts/generate_theme_audio.py.
THEMES = [
    {
        "key": "night_drive",
        "name": "Night Drive",
        "synth": "night_drive",
        "emoji": "\U0001F697",  # 🚗
        "short_title": "Night Drive \U0001F697 Nostalgic Synth Ambient #shorts",
        "long_title": "Night Drive \U0001F697 14 Minute Nostalgic Synth Ambient for Late Night Driving | Liminal Visualizer",
        "description": (
            "A slow, reverb-drenched chord progression with tape hiss and "
            "the occasional distant car. The quiet solitude of a late-"
            "night drive down an empty highway."
        ),
        "tags": [
            "synthwave ambient", "liminal space music", "night drive music",
            "tape hiss ambient", "nostalgic ambient", "hauntology",
            "focus music", "ambient visualizer", "chill synth", "retro ambient",
            "relaxing music", "vaporwave ambient",
        ],
    },
    {
        "key": "empty_parking_structure",
        "name": "Empty Parking Structure",
        "synth": "empty_parking_structure",
        "emoji": "\U0001F3DA️",  # 🏚️
        "short_title": "Empty Parking Structure \U0001F3DA️ Liminal Space Ambient #shorts",
        "long_title": "Empty Parking Structure \U0001F3DA️ 14 Minute Liminal Space Ambient | Hauntology Visualizer",
        "description": (
            "A sparse, minimal chord drowned in huge concrete reverb, with "
            "the occasional water drip. The eerie stillness of an empty "
            "parking structure."
        ),
        "tags": [
            "liminal space music", "backrooms ambient", "hauntology",
            "eerie ambient", "dark ambient", "focus music",
            "ambient visualizer", "atmospheric music", "relaxing music",
            "minimal ambient", "dreamcore ambient", "concrete ambient",
        ],
    },
    {
        "key": "forgotten_mall",
        "name": "Forgotten Mall",
        "synth": "forgotten_mall",
        "emoji": "\U0001F6CD️",  # 🛍️
        "short_title": "Forgotten Mall \U0001F6CD️ Muffled Nostalgic Ambient #shorts",
        "long_title": "Forgotten Mall \U0001F6CD️ 14 Minute Muffled Nostalgic Dead Mall Ambient | Liminal Visualizer",
        "description": (
            "A nostalgic synth melody heard as if through walls — "
            "everything heavily muffled, like memories of a mall that no "
            "longer exists."
        ),
        "tags": [
            "liminal space music", "dead mall ambient", "nostalgic ambient",
            "hauntology", "vaporwave ambient", "dreamcore ambient",
            "focus music", "ambient visualizer", "retro ambient",
            "atmospheric music", "muffled ambient", "relaxing music",
        ],
    },
    {
        "key": "static_transmission",
        "name": "Static Transmission",
        "synth": "static_transmission",
        "emoji": "\U0001F4FB",  # 📻
        "short_title": "Static Transmission \U0001F4FB Lost Signal Ambient #shorts",
        "long_title": "Static Transmission \U0001F4FB 14 Minute Lost Signal Tape Static Ambient | Hauntology Visualizer",
        "description": (
            "Mostly tape hiss and lost-signal static, with distant warped "
            "tones drifting through — the sound of a transmission from "
            "somewhere far away."
        ),
        "tags": [
            "tape hiss ambient", "static noise", "hauntology",
            "lost signal ambient", "dark ambient", "focus noise",
            "ambient visualizer", "atmospheric music", "eerie ambient",
            "relaxing noise", "liminal space music", "white noise",
        ],
    },
    {
        "key": "rain_interstate",
        "name": "Rain on the Interstate",
        "synth": "rain_interstate",
        "emoji": "\U0001F327️",  # 🌧️
        "short_title": "Rain on the Interstate \U0001F327️ Highway Ambient #shorts",
        "long_title": "Rain on the Interstate \U0001F327️ 14 Minute Rain & Highway Ambient for Focus & Sleep | Liminal Visualizer",
        "description": (
            "Rain over a lowpassed synth pad with distant passing traffic "
            "— the solitude of a long drive through the rain."
        ),
        "tags": [
            "rain sounds", "highway ambient", "synthwave ambient",
            "night drive music", "focus music", "sleep music",
            "ambient visualizer", "relaxing rain", "nostalgic ambient",
            "liminal space music", "chill synth", "calm music",
        ],
    },
    {
        "key": "suburban_hush",
        "name": "Suburban Hush",
        "synth": "suburban_hush",
        "emoji": "\U0001F3D8️",  # 🏘️
        "short_title": "Suburban Hush \U0001F3D8️ Quiet Night Ambient #shorts",
        "long_title": "Suburban Hush \U0001F3D8️ 14 Minute Quiet Suburban Night Ambient | Liminal Visualizer",
        "description": (
            "A soft pad and tape hiss over a quiet ambient floor — the "
            "stillness of a sleeping suburban street at night."
        ),
        "tags": [
            "liminal space music", "suburban ambient", "night ambient",
            "hauntology", "nostalgic ambient", "focus music",
            "ambient visualizer", "sleep music", "calm music",
            "dreamcore ambient", "relaxing music", "atmospheric music",
        ],
    },
    {
        "key": "vhs_afterglow",
        "name": "VHS Afterglow",
        "synth": "vhs_afterglow",
        "emoji": "\U0001F4FC",  # 📼
        "short_title": "VHS Afterglow \U0001F4FC Retro Synth Ambient #shorts",
        "long_title": "VHS Afterglow \U0001F4FC 14 Minute Retro Synth Ambient with Tape Wobble | Liminal Visualizer",
        "description": (
            "A warm, nostalgic chord progression with a wobbly, lowpassed "
            "melody — the glow of an old recorded tape played one more "
            "time."
        ),
        "tags": [
            "vaporwave ambient", "synthwave ambient", "retro ambient",
            "vhs aesthetic music", "nostalgic ambient", "focus music",
            "ambient visualizer", "chill synth", "hauntology",
            "relaxing music", "liminal space music", "tape music",
        ],
    },
    {
        "key": "neon_corridor",
        "name": "Neon Corridor",
        "synth": "neon_corridor",
        "emoji": "\U0001F3EE",  # 🏮
        "short_title": "Neon Corridor \U0001F3EE Retro Liminal Ambient #shorts",
        "long_title": "Neon Corridor \U0001F3EE 14 Minute Retro Neon Liminal Ambient | Hauntology Visualizer",
        "description": (
            "A wobbly retro arpeggio drenched in hallway reverb — walking "
            "an empty, glowing liminal corridor at night."
        ),
        "tags": [
            "liminal space music", "synthwave ambient", "retro ambient",
            "neon ambient", "hauntology", "focus music",
            "ambient visualizer", "dreamcore ambient", "atmospheric music",
            "relaxing music", "vaporwave ambient", "chill synth",
        ],
    },
    {
        "key": "last_broadcast",
        "name": "Last Broadcast",
        "synth": "last_broadcast",
        "emoji": "\U0001F4E1",  # 📡
        "short_title": "Last Broadcast \U0001F4E1 Eerie Fading Signal Ambient #shorts",
        "long_title": "Last Broadcast \U0001F4E1 14 Minute Eerie Fading Signal Ambient | Hauntology Visualizer",
        "description": (
            "Sparse, slightly dissonant tones under frequent static "
            "bursts and heavy hiss — an eerie, fading transmission that "
            "won't quite go silent."
        ),
        "tags": [
            "hauntology", "eerie ambient", "dark ambient", "static noise",
            "liminal space music", "focus music", "ambient visualizer",
            "atmospheric music", "dreamcore ambient", "relaxing noise",
            "lost signal ambient", "mysterious ambient",
        ],
    },
    {
        "key": "overpass_3am",
        "name": "Overpass at 3AM",
        "synth": "overpass_3am",
        "emoji": "\U0001F309",  # 🌉
        "short_title": "Overpass at 3AM \U0001F309 Liminal Night Ambient #shorts",
        "long_title": "Overpass at 3AM \U0001F309 14 Minute Liminal Night Highway Ambient | Hauntology Visualizer",
        "description": (
            "Deep distant-traffic rumble under a sparse, muffled melody "
            "and tape hiss — standing alone beneath the highway in the "
            "dead of night."
        ),
        "tags": [
            "liminal space music", "night ambient", "hauntology",
            "highway ambient", "nostalgic ambient", "focus music",
            "ambient visualizer", "dreamcore ambient", "sleep music",
            "atmospheric music", "relaxing music", "dark ambient",
        ],
    },
]

BRAND_NAME = "The Static Horizon"
BRAND_TAGLINE = "Lost Signals. Quiet Miles."

GLOBAL_TAGS = [
    "liminal space music", "hauntology", "synthwave ambient",
    "nostalgic ambient", "night drive music", "tape hiss ambient",
    "focus music", "ambient visualizer", "dreamcore ambient",
    "retro ambient", "vaporwave ambient", "atmospheric music",
    "relaxing music", "sleep music", "background music for studying",
]

PERFECT_FOR = "late-night focus, driving playlists, studying, and unwinding"

PLAYLISTS = {
    "driving": {
        "title": "Night Drive & Highway Ambient \U0001F697",
        "description": "Synthwave-adjacent ambient for late-night driving "
                       "and highway solitude. Liminal space visualizer.",
        "themes": ["night_drive", "rain_interstate", "overpass_3am"],
    },
    "liminal_spaces": {
        "title": "Liminal Spaces & Hauntology \U0001F3DA️",
        "description": "Eerie, nostalgic ambient for forgotten and "
                       "in-between places. Hauntology visualizer.",
        "themes": ["empty_parking_structure", "forgotten_mall", "neon_corridor"],
    },
    "tape_static": {
        "title": "Tape Static & Lost Signals \U0001F4FB",
        "description": "Tape hiss, static, and fading transmissions for "
                       "atmospheric background focus. Hauntology visualizer.",
        "themes": ["static_transmission", "last_broadcast"],
    },
    "retro_nights": {
        "title": "Retro Nights & VHS Ambient \U0001F4FC",
        "description": "Warm, wobbly retro synth ambient for nostalgic "
                       "focus sessions. Liminal space visualizer.",
        "themes": ["vhs_afterglow", "suburban_hush"],
    },
}

ACCENT_COLORS = {
    "night_drive": "2a1a4a",
    "empty_parking_structure": "2a2a3a",
    "forgotten_mall": "4a2a4a",
    "static_transmission": "3a3a3a",
    "rain_interstate": "2a3a4a",
    "suburban_hush": "2a2a4a",
    "vhs_afterglow": "5a2a4a",
    "neon_corridor": "3a1a5a",
    "last_broadcast": "3a2a2a",
    "overpass_3am": "1a1a3a",
}

# Topic for each theme's generative animation (scripts/make_animated_video.py
# --topic) -- matches the pan motion/flicker profile to what the theme is
# actually about. Falls back to "neutral" for any key left unlisted.
TOPICS = {
    "night_drive": "wind",
    "empty_parking_structure": "stone",
    "forgotten_mall": "stone",
    "static_transmission": "void",
    "rain_interstate": "water",
    "suburban_hush": "void",
    "vhs_afterglow": "fire",
    "neon_corridor": "fire",
    "last_broadcast": "void",
    "overpass_3am": "stone",
}


def synth_args(theme: dict) -> list:
    a = []
    if theme.get("tone"):
        a += ["--tone", str(theme["tone"])]
    if theme.get("beat"):
        a += ["--beat", str(theme["beat"]),
              "--beat-type", theme.get("beat_type", "binaural")]
    if theme.get("bowl"):
        a += ["--bowl"]
    if theme.get("tone_soft"):
        a += ["--tone-soft"]
    if theme.get("reverb"):
        a += ["--reverb", str(theme["reverb"])]
    if theme.get("tone_tilt"):
        a += ["--tone-tilt", str(theme["tone_tilt"])]
    if theme.get("tone_gain"):
        a += ["--tone-gain", str(theme["tone_gain"])]
    return a


def playlist_for(theme_key: str) -> dict | None:
    for p in PLAYLISTS.values():
        if theme_key in p["themes"]:
            return p
    return None


def topic_for(theme_key: str) -> str:
    """The --topic to pass to make_animated_video.py for this theme."""
    return TOPICS.get(theme_key, "neutral")

DESCRIPTION_FOOTER = (
    "\n\n— {brand} — {tagline}\n\n"
    "\U0001F3A7 Best experienced with headphones or a good speaker at a low volume.\n"
    "\U0001F3B5 All music is composed algorithmically with original sound-synthesis "
    "software — no samples, no loops, no AI generation.\n\n"
    "Please note: this content is for ambience and focus only and is not a "
    "substitute for medical or mental-health advice."
)


def theme_for_date(d: date | None = None) -> dict:
    d = d or date.today()
    idx = (d - ANCHOR).days % len(THEMES)
    return THEMES[idx]


def daily_selection(d: date | None = None, count: int = DAILY_COUNT) -> list[dict]:
    d = d or date.today()
    day_idx = (d - ANCHOR).days
    start = (day_idx * count) % len(THEMES)
    return [THEMES[(start + i) % len(THEMES)] for i in range(count)]


def theme_by_key(key: str) -> dict:
    for t in THEMES:
        if t["key"] == key:
            return t
    raise KeyError(f"Unknown theme key: {key!r}. Valid: {[t['key'] for t in THEMES]}")


def resolve_theme(selector: str | None, d: date | None = None) -> dict:
    if selector in (None, "auto"):
        return theme_for_date(d)
    return theme_by_key(selector)


if __name__ == "__main__":
    from datetime import timedelta
    today = date.today()
    for i in range(len(THEMES)):
        t = theme_for_date(today + timedelta(days=i))
        print(f"{today + timedelta(days=i)}  ->  {t['key']:26s}  {t['name']}")
