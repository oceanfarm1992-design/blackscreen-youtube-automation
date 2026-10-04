#!/usr/bin/env python3
"""
Theme definitions, daily rotation, and SEO metadata for the "Moss &
Manor" channel (micro-environmental natural ambient blending acoustic
guitar/bowed bass with pristine nature field recordings).

Same contract as aether/themes.py, sanctuary/themes.py, hearth/themes.py,
horizon/themes.py, resonance/themes.py -- only the data below differs.

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
        "key": "greenhouse_ruins",
        "name": "Greenhouse Ruins",
        "synth": "greenhouse_ruins",
        "emoji": "\U0001FAB4",  # 🪴
        "short_title": "Greenhouse Ruins \U0001FAB4 Guitar & Nature Ambient #shorts",
        "long_title": "Greenhouse Ruins \U0001FAB4 14 Minute Acoustic Guitar & Nature Ambient | Overgrown Visualizer",
        "description": (
            "Fingerpicked acoustic guitar over distant thunder and "
            "dripping water — an overgrown, half-forgotten glasshouse "
            "reclaimed by nature."
        ),
        "tags": [
            "acoustic guitar music", "nature ambient", "rain sounds",
            "focus music", "relaxing guitar music", "study music",
            "ambient visualizer", "calm music", "field recording ambient",
            "cottagecore music", "relaxation music", "instrumental acoustic",
        ],
    },
    {
        "key": "rainy_cottage_garden",
        "name": "Rainy Cottage Garden",
        "synth": "rainy_cottage_garden",
        "emoji": "\U0001F327️",  # 🌧️
        "short_title": "Rainy Cottage Garden \U0001F327️ Guitar & Rain Ambient #shorts",
        "long_title": "Rainy Cottage Garden \U0001F327️ 14 Minute Gentle Guitar & Rain Ambient for Focus & Sleep | Visualizer",
        "description": (
            "Soft rain with gentle guitar and sparse bowed bass — a quiet "
            "cottage garden in the rain."
        ),
        "tags": [
            "rain sounds", "acoustic guitar music", "cottagecore music",
            "nature ambient", "focus music", "sleep music",
            "ambient visualizer", "relaxing rain", "calm music",
            "garden ambient", "study music", "relaxation music",
        ],
    },
    {
        "key": "misty_forest_floor",
        "name": "Misty Forest Floor",
        "synth": "misty_forest_floor",
        "emoji": "\U0001F332",  # 🌲
        "short_title": "Misty Forest Floor \U0001F332 Guitar & Wind Ambient #shorts",
        "long_title": "Misty Forest Floor \U0001F332 14 Minute Guitar & Forest Wind Ambient for Focus & Sleep | Visualizer",
        "description": (
            "Soft wind through ancient trees under sparse guitar and a "
            "low bowed-bass drone — standing in a misty forest clearing."
        ),
        "tags": [
            "forest ambient", "acoustic guitar music", "wind sounds",
            "nature ambient", "focus music", "sleep music",
            "ambient visualizer", "calm music", "relaxing nature sounds",
            "study music", "relaxation music", "forest sounds",
        ],
    },
    {
        "key": "creek_hollow",
        "name": "Creek Hollow",
        "synth": "creek_hollow",
        "emoji": "\U0001F3DE️",  # 🏞️
        "short_title": "Creek Hollow \U0001F3DE️ Guitar & Stream Ambient #shorts",
        "long_title": "Creek Hollow \U0001F3DE️ 14 Minute Guitar & Flowing Creek Ambient for Focus & Relaxation | Visualizer",
        "description": (
            "Flowing stream water and small bubbles under bright "
            "fingerpicked guitar — a hidden creek hollow."
        ),
        "tags": [
            "stream sounds", "acoustic guitar music", "nature ambient",
            "creek sounds", "focus music", "relaxing water sounds",
            "ambient visualizer", "calm music", "study music",
            "relaxation music", "water sounds", "cottagecore music",
        ],
    },
    {
        "key": "ancient_grove",
        "name": "Ancient Grove",
        "synth": "ancient_grove",
        "emoji": "\U0001F333",  # 🌳
        "short_title": "Ancient Grove \U0001F333 Bowed Bass & Wind Ambient #shorts",
        "long_title": "Ancient Grove \U0001F333 14 Minute Bowed Bass & Wind Ambient Among Old Trees | Nature Visualizer",
        "description": (
            "Deep wind and a slow bowed-bass melody under rare guitar "
            "accents — standing among very old trees."
        ),
        "tags": [
            "nature ambient", "wind sounds", "forest ambient",
            "acoustic bass music", "focus music", "sleep music",
            "ambient visualizer", "calm music", "relaxing nature sounds",
            "study music", "relaxation music", "forest sounds",
        ],
    },
    {
        "key": "thunder_garden",
        "name": "Thunder Garden",
        "synth": "thunder_garden",
        "emoji": "\U000026C8️",  # ⛈️
        "short_title": "Thunder Garden \U000026C8️ Guitar & Rain Ambient #shorts",
        "long_title": "Thunder Garden \U000026C8️ 14 Minute Guitar, Rain & Distant Thunder Ambient | Nature Visualizer",
        "description": (
            "Rain and distant rolling thunder under a gentle guitar line "
            "— a garden settling in for a storm."
        ),
        "tags": [
            "thunderstorm sounds", "rain sounds", "acoustic guitar music",
            "nature ambient", "focus music", "sleep music",
            "ambient visualizer", "calm music", "relaxing storm",
            "study music", "relaxation music", "garden ambient",
        ],
    },
    {
        "key": "mossy_stonework",
        "name": "Mossy Stonework",
        "synth": "mossy_stonework",
        "emoji": "\U0001FAA8",  # 🪨
        "short_title": "Mossy Stonework \U0001FAA8 Minimal Nature Ambient #shorts",
        "long_title": "Mossy Stonework \U0001FAA8 14 Minute Minimal Dripping Water & Guitar Ambient | Overgrown Ruins Visualizer",
        "description": (
            "Minimal dripping water in long reverb under a very sparse "
            "guitar line — quiet, overgrown ruins."
        ),
        "tags": [
            "nature ambient", "water drops", "acoustic guitar music",
            "minimal ambient", "focus music", "sleep music",
            "ambient visualizer", "calm music", "relaxing nature sounds",
            "study music", "relaxation music", "cottagecore music",
        ],
    },
    {
        "key": "wildflower_meadow",
        "name": "Wildflower Meadow",
        "synth": "wildflower_meadow",
        "emoji": "\U0001F33C",  # 🌼
        "short_title": "Wildflower Meadow \U0001F33C Guitar & Birdsong Ambient #shorts",
        "long_title": "Wildflower Meadow \U0001F33C 14 Minute Guitar & Birdsong Ambient for Focus & Relaxation | Visualizer",
        "description": (
            "Light wind and birdsong under a cheerful, brighter guitar "
            "line — a sunlit wildflower meadow."
        ),
        "tags": [
            "birds singing", "acoustic guitar music", "nature ambient",
            "meadow ambient", "focus music", "relaxing nature sounds",
            "ambient visualizer", "calm music", "study music",
            "relaxation music", "birdsong", "cottagecore music",
        ],
    },
    {
        "key": "fernwood_path",
        "name": "Fernwood Path",
        "synth": "fernwood_path",
        "emoji": "\U0001F33F",  # 🌿
        "short_title": "Fernwood Path \U0001F33F Guitar & Creek Ambient #shorts",
        "long_title": "Fernwood Path \U0001F33F 14 Minute Guitar & Gentle Creek Ambient for Focus & Study | Nature Visualizer",
        "description": (
            "A gentle creek underfoot with a walking-pace guitar line and "
            "sparse bowed bass — a quiet path through the ferns."
        ),
        "tags": [
            "creek sounds", "acoustic guitar music", "nature ambient",
            "forest ambient", "focus music", "study music",
            "ambient visualizer", "calm music", "relaxing water sounds",
            "relaxation music", "water sounds", "cottagecore music",
        ],
    },
    {
        "key": "twilight_greenhouse",
        "name": "Twilight Greenhouse",
        "synth": "twilight_greenhouse",
        "emoji": "\U0001F306",  # 🌆
        "short_title": "Twilight Greenhouse \U0001F306 Dusk Guitar Ambient #shorts",
        "long_title": "Twilight Greenhouse \U0001F306 14 Minute Dusk Guitar & Distant Thunder Ambient | Nature Visualizer",
        "description": (
            "Soft wind and far-off thunder under a sparse, reflective "
            "guitar line as dusk settles over the greenhouse."
        ),
        "tags": [
            "acoustic guitar music", "nature ambient", "dusk ambient",
            "wind sounds", "focus music", "sleep music",
            "ambient visualizer", "calm music", "relaxing nature sounds",
            "study music", "relaxation music", "cottagecore music",
        ],
    },
]

BRAND_NAME = "Moss & Manor"
BRAND_TAGLINE = "Wild Gardens. Quiet Moments."

GLOBAL_TAGS = [
    "nature ambient", "acoustic guitar music", "cottagecore music",
    "focus music", "study music", "ambient visualizer", "calm music",
    "relaxing nature sounds", "field recording ambient", "rain sounds",
    "relaxation music", "sleep music", "forest ambient",
    "background music for studying", "instrumental acoustic",
]

PERFECT_FOR = "studying, relaxing, reading, gardening, and quiet nature focus"

PLAYLISTS = {
    "guitar_nature": {
        "title": "Guitar & Nature Ambient \U0001FAB4",
        "description": "Acoustic guitar fingerpicking over pristine nature "
                       "field recordings. Overgrown nature visualizer.",
        "themes": ["greenhouse_ruins", "wildflower_meadow", "fernwood_path"],
    },
    "rain_storm": {
        "title": "Rain & Thunder Garden Ambient \U000026C8️",
        "description": "Soft rain and distant thunder with gentle guitar "
                       "for focus and sleep. Nature visualizer.",
        "themes": ["rainy_cottage_garden", "thunder_garden"],
    },
    "forest_grove": {
        "title": "Forest & Grove Ambient \U0001F333",
        "description": "Wind through trees, bowed bass, and sparse guitar "
                       "for deep nature immersion. Nature visualizer.",
        "themes": ["misty_forest_floor", "ancient_grove", "twilight_greenhouse"],
    },
    "water_stone": {
        "title": "Creek & Stonework Ambient \U0001F3DE️",
        "description": "Flowing water and quiet dripping stonework ambience "
                       "with acoustic guitar. Nature visualizer.",
        "themes": ["creek_hollow", "mossy_stonework"],
    },
}

ACCENT_COLORS = {
    "greenhouse_ruins": "3a5a3a",
    "rainy_cottage_garden": "4a6a4a",
    "misty_forest_floor": "3a4a3a",
    "creek_hollow": "3a5a5a",
    "ancient_grove": "2a3a2a",
    "thunder_garden": "4a4a5a",
    "mossy_stonework": "4a5a4a",
    "wildflower_meadow": "6a7a4a",
    "fernwood_path": "3a5a4a",
    "twilight_greenhouse": "3a3a4a",
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
        print(f"{today + timedelta(days=i)}  ->  {t['key']:22s}  {t['name']}")
