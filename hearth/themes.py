#!/usr/bin/env python3
"""
Theme definitions, daily rotation, and SEO metadata for the "Hearth &
Quill" channel (co-working/co-studying ambient in warm historical, fantasy,
and literary settings).

Same contract as aether/themes.py and sanctuary/themes.py so produce.py /
make_metadata.py / publish_queue.py work unchanged against any channel's
theme module -- only the data below differs.

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
        "key": "candlelit_study",
        "name": "Candlelit Study",
        "synth": "candlelit_study",
        "emoji": "\U0001F56F️",  # 🕯️
        "short_title": "Candlelit Study \U0001F56F️ Warm Piano Co-Working Ambient #shorts",
        "long_title": "Candlelit Study \U0001F56F️ 14 Minute Warm Piano Co-Working Ambient | Fantasy Study Visualizer",
        "description": (
            "A warm felt-piano melody over a soft chord bed, with a quiet "
            "fire crackling nearby. Cozy candlelit co-working ambience for "
            "deep, focused study sessions."
        ),
        "tags": [
            "study music", "co-working music", "piano ambient",
            "fantasy ambient", "focus music", "cozy music",
            "ambient visualizer", "concentration music", "deep work music",
            "relaxing piano music", "warm ambient", "medieval ambient",
        ],
    },
    {
        "key": "leaded_glass_rain",
        "name": "Leaded Glass Rain",
        "synth": "leaded_glass_rain",
        "emoji": "\U0001F327️",  # 🌧️
        "short_title": "Leaded Glass Rain \U0001F327️ Cello & Rain Study Ambient #shorts",
        "long_title": "Leaded Glass Rain \U0001F327️ 14 Minute Rain & Cello Study Ambient | Fantasy Co-Working Visualizer",
        "description": (
            "Soft rain against an old leaded-glass window, with warm cello "
            "notes drifting through. Calm, literary ambience for reading, "
            "writing, or study."
        ),
        "tags": [
            "rain sounds", "cello music", "study music", "fantasy ambient",
            "co-working music", "focus music", "rain ambience",
            "ambient visualizer", "relaxing rain", "cozy music",
            "medieval ambient", "reading music",
        ],
    },
    {
        "key": "quiet_scriptorium",
        "name": "Quiet Scriptorium",
        "synth": "quiet_scriptorium",
        "emoji": "\U0001FAB6",  # 🪶
        "short_title": "Quiet Scriptorium \U0001FAB6 Writing Ambient with Piano #shorts",
        "long_title": "Quiet Scriptorium \U0001FAB6 14 Minute Writing Ambient with Soft Piano | Fantasy Study Visualizer",
        "description": (
            "A soft pad, sparse piano phrases, and the occasional page "
            "turn — the quiet of an old scriptorium. Contemplative "
            "ambience for writing and study."
        ),
        "tags": [
            "writing music", "study music", "piano ambient", "fantasy ambient",
            "focus music", "co-working music", "ambient visualizer",
            "concentration music", "medieval ambient", "calm music",
            "reading music", "deep work music",
        ],
    },
    {
        "key": "tavern_hearth",
        "name": "Tavern Hearth",
        "synth": "tavern_hearth",
        "emoji": "\U0001F37B",  # 🍻
        "short_title": "Tavern Hearth \U0001F37B Cozy Fantasy Co-Working Ambient #shorts",
        "long_title": "Tavern Hearth \U0001F37B 14 Minute Cozy Fantasy Tavern Ambient for Study & Co-Working | Visualizer",
        "description": (
            "A crackling fireplace under a warm, folk-leaning piano motif "
            "— the cozy bustle of a fantasy tavern, perfect for communal "
            "study and co-working."
        ),
        "tags": [
            "fantasy ambient", "tavern music", "fireplace sounds",
            "study music", "co-working music", "cozy music", "piano ambient",
            "ambient visualizer", "focus music", "medieval ambient",
            "rpg ambient", "relaxing music",
        ],
    },
    {
        "key": "lantern_ink",
        "name": "Lantern & Ink",
        "synth": "lantern_ink",
        "emoji": "\U0001F3EE",  # 🏮
        "short_title": "Lantern & Ink \U0001F3EE Minimal Piano Study Ambient #shorts",
        "long_title": "Lantern & Ink \U0001F3EE 14 Minute Minimal Piano Ambient for Deep Focus | Fantasy Study Visualizer",
        "description": (
            "A sparse, intimate piano line over a quiet pad — the "
            "stillness of writing by lantern light. Minimal ambience for "
            "deep, uninterrupted focus."
        ),
        "tags": [
            "piano ambient", "study music", "minimal ambient",
            "fantasy ambient", "focus music", "deep work music",
            "ambient visualizer", "concentration music", "calm music",
            "writing music", "relaxing piano music", "co-working music",
        ],
    },
    {
        "key": "old_library_hush",
        "name": "Old Library Hush",
        "synth": "old_library_hush",
        "emoji": "\U0001F4DA",  # 📚
        "short_title": "Old Library Hush \U0001F4DA Cozy Study Ambient #shorts",
        "long_title": "Old Library Hush \U0001F4DA 14 Minute Cozy Library Study Ambient with Piano | Fantasy Visualizer",
        "description": (
            "A dusty, soft pad with distant page turns and a sparse piano "
            "line — the hush of tall shelves and old paper. Calm ambience "
            "for deep study."
        ),
        "tags": [
            "library ambient", "study music", "piano ambient",
            "fantasy ambient", "focus music", "co-working music",
            "ambient visualizer", "reading music", "concentration music",
            "cozy music", "medieval ambient", "calm music",
        ],
    },
    {
        "key": "winter_study",
        "name": "Winter Study",
        "synth": "winter_study",
        "emoji": "\U00002744️",  # ❄️
        "short_title": "Winter Study \U00002744️ Cozy Fireplace & Cello Ambient #shorts",
        "long_title": "Winter Study \U00002744️ 14 Minute Cozy Winter Fireplace & Cello Ambient | Fantasy Study Visualizer",
        "description": (
            "A crackling fire and a slow cello drone under rare piano "
            "phrases — cozy warmth against the cold outside. Perfect for "
            "winter study sessions."
        ),
        "tags": [
            "fireplace sounds", "cello music", "winter ambient",
            "study music", "fantasy ambient", "cozy music", "focus music",
            "ambient visualizer", "co-working music", "relaxing music",
            "medieval ambient", "calm music",
        ],
    },
    {
        "key": "moonlit_manuscript",
        "name": "Moonlit Manuscript",
        "synth": "moonlit_manuscript",
        "emoji": "\U0001F319",  # 🌙
        "short_title": "Moonlit Manuscript \U0001F319 Night Writing Ambient #shorts",
        "long_title": "Moonlit Manuscript \U0001F319 14 Minute Night Writing Ambient with Piano | Fantasy Study Visualizer",
        "description": (
            "A gentle string-like pad under a sparse, reflective piano "
            "line — the quiet of a night spent writing by moonlight."
        ),
        "tags": [
            "piano ambient", "writing music", "night ambient",
            "fantasy ambient", "study music", "focus music",
            "ambient visualizer", "calm music", "relaxing piano music",
            "co-working music", "reading music", "medieval ambient",
        ],
    },
    {
        "key": "hearthside_tales",
        "name": "Hearthside Tales",
        "synth": "hearthside_tales",
        "emoji": "\U0001F525",  # 🔥
        "short_title": "Hearthside Tales \U0001F525 Warm Cello Storytelling Ambient #shorts",
        "long_title": "Hearthside Tales \U0001F525 14 Minute Warm Cello & Fireplace Storytelling Ambient | Fantasy Visualizer",
        "description": (
            "A warm cello melody and a crackling fire — the mood of a "
            "story told by firelight. Cozy ambience for reading, writing, "
            "or unwinding."
        ),
        "tags": [
            "cello music", "fireplace sounds", "fantasy ambient",
            "storytelling music", "cozy music", "study music",
            "ambient visualizer", "relaxing music", "focus music",
            "medieval ambient", "rpg ambient", "co-working music",
        ],
    },
    {
        "key": "ink_parchment",
        "name": "Ink & Parchment",
        "synth": "ink_parchment",
        "emoji": "\U0001FAB6",  # 🪶
        "short_title": "Ink & Parchment \U0001FAB6 Minimal Writing Ambient #shorts",
        "long_title": "Ink & Parchment \U0001FAB6 14 Minute Minimal Scratchy Writing Ambient | Fantasy Study Visualizer",
        "description": (
            "Minimal scratchy pen-on-paper texture with a very sparse "
            "piano line — the quietest, most minimal writing ambience for "
            "deep focus."
        ),
        "tags": [
            "writing music", "minimal ambient", "study music",
            "fantasy ambient", "focus music", "piano ambient",
            "ambient visualizer", "concentration music", "asmr writing",
            "deep work music", "calm music", "co-working music",
        ],
    },
]

BRAND_NAME = "Hearth & Quill"
BRAND_TAGLINE = "Warm Worlds. Quiet Work."

GLOBAL_TAGS = [
    "study music", "co-working music", "fantasy ambient", "focus music",
    "piano ambient", "cozy music", "ambient visualizer",
    "concentration music", "deep work music", "medieval ambient",
    "relaxing music", "writing music", "cello music", "fireplace sounds",
    "background music for studying",
]

PERFECT_FOR = "studying, co-working, reading, writing, and cozy focus sessions"

PLAYLISTS = {
    "piano_study": {
        "title": "Piano Study & Focus \U0001F56F️",
        "description": "Warm felt-piano ambient for study, co-working, and "
                       "deep focus. Fantasy study visualizer.",
        "themes": ["candlelit_study", "quiet_scriptorium", "lantern_ink", "old_library_hush"],
    },
    "cello_fireside": {
        "title": "Cello & Fireside Ambient \U0001F525",
        "description": "Warm cello melodies and crackling fireplaces for "
                       "cozy focus and storytelling moods. Fantasy visualizer.",
        "themes": ["leaded_glass_rain", "tavern_hearth", "winter_study", "hearthside_tales"],
    },
    "writing_ambient": {
        "title": "Writing & Manuscript Ambient \U0001FAB6",
        "description": "Minimal, literary ambient textures for writing "
                       "and deep concentration. Fantasy study visualizer.",
        "themes": ["moonlit_manuscript", "ink_parchment"],
    },
}

ACCENT_COLORS = {
    "candlelit_study": "c9862f",
    "leaded_glass_rain": "6b5a3a",
    "quiet_scriptorium": "8a6a3a",
    "tavern_hearth": "b5651d",
    "lantern_ink": "9a7a40",
    "old_library_hush": "7a6244",
    "winter_study": "a86a3a",
    "moonlit_manuscript": "5a4a6a",
    "hearthside_tales": "c2742f",
    "ink_parchment": "8a7050",
}

# Topic for each theme's generative animation (scripts/make_animated_video.py
# --topic) -- matches the pan motion/flicker profile to what the theme is
# actually about (e.g. the crackling-fireplace themes get a fast, warm
# flicker). Falls back to "neutral" for any key left unlisted.
TOPICS = {
    "candlelit_study": "fire",
    "leaded_glass_rain": "water",
    "quiet_scriptorium": "stone",
    "tavern_hearth": "fire",
    "lantern_ink": "fire",
    "old_library_hush": "stone",
    "winter_study": "fire",
    "moonlit_manuscript": "void",
    "hearthside_tales": "fire",
    "ink_parchment": "stone",
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
        print(f"{today + timedelta(days=i)}  ->  {t['key']:20s}  {t['name']}")
