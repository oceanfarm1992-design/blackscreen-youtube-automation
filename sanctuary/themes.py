#!/usr/bin/env python3
"""
Theme definitions, daily rotation, and SEO metadata for the "Sanctuary of
Sci" channel (deep space / sleeper ship / cosmic observatory ambient for
focus, coding, and late-night study).

Same contract as aether/themes.py so produce.py / make_metadata.py /
publish_queue.py work unchanged against any channel's theme module -- only
the data below differs.

10 themes rotate through a sliding daily window (see daily_selection below).
Rotation is anchored to a fixed date so it is deterministic and reproducible.
"""
from datetime import date

ANCHOR = date(2026, 10, 4)  # this channel's automation start date

# Fixed video lengths (this channel runs real procedural animation, not an
# hours-long static frame, so "long" is a short, animated "feature" rather
# than an all-night background loop).
FEATURE_SECONDS = 870  # 14:30
SHORT_SECONDS = 59

# Launch cadence: 1 feature + 1 Short/day on a single OAuth project.
LONGS_PER_DAY = 1
SHORTS_PER_DAY = 1
DAILY_COUNT = LONGS_PER_DAY + SHORTS_PER_DAY

# Ordered rotation. `synth` names a function in scripts/generate_theme_audio.py.
THEMES = [
    {
        "key": "sleeper_drift",
        "name": "Sleeper Drift",
        "synth": "sleeper_drift",
        "emoji": "\U0001F6F8",  # 🛸
        "short_title": "Sleeper Drift \U0001F6F8 Deep Space Engine Drone #shorts",
        "long_title": "Sleeper Drift \U0001F6F8 14 Minute Deep Space Engine Drone for Focus & Sleep | Sci-Fi Ambient Visualizer",
        "description": (
            "The slow idling hum of a sleeper ship's engine, deep in open "
            "space. A low, steady drone for background focus, coding, or "
            "drifting off to sleep."
        ),
        "tags": [
            "space ambient", "sci fi ambient", "dark ambient", "drone music",
            "deep space music", "sleep music", "focus music", "sleeper ship",
            "cosmic ambient", "ambient visualizer", "study music",
            "concentration music",
        ],
    },
    {
        "key": "nebula_watch",
        "name": "Nebula Watch",
        "synth": "nebula_watch",
        "emoji": "\U0001F30C",  # 🌌
        "short_title": "Nebula Watch \U0001F30C Cosmic Observatory Ambient #shorts",
        "long_title": "Nebula Watch \U0001F30C 14 Minute Cosmic Observatory Ambient for Focus & Study | Sci-Fi Visualizer",
        "description": (
            "A wide, slowly shifting cosmic pad — gazing out at a distant "
            "nebula from the observation deck. Calm, spacious ambience for "
            "deep focus and study."
        ),
        "tags": [
            "space ambient", "cosmic ambient", "sci fi ambient", "focus music",
            "study music", "nebula", "deep work music", "ambient visualizer",
            "concentration music", "relaxing space music", "meditation music",
            "generative music",
        ],
    },
    {
        "key": "station_hum",
        "name": "Station Hum",
        "synth": "station_hum",
        "emoji": "\U0001F6F0️",  # 🛰️
        "short_title": "Station Hum \U0001F6F0️ Space Station Ambience #shorts",
        "long_title": "Station Hum \U0001F6F0️ 14 Minute Space Station Ambience for Deep Work | Sci-Fi Ambient Visualizer",
        "description": (
            "The steady mechanical hum of a space station's life-support "
            "systems — a grounding, reassuring texture for background "
            "focus and deep work."
        ),
        "tags": [
            "space station ambience", "sci fi ambient", "space ambient",
            "focus music", "deep work music", "study music",
            "concentration music", "ambient visualizer", "white noise",
            "productivity music", "coding music", "background noise",
        ],
    },
    {
        "key": "cryo_bay",
        "name": "Cryo Bay",
        "synth": "cryo_bay",
        "emoji": "\U00002744️",  # ❄️
        "short_title": "Cryo Bay \U00002744️ Cold Sleeper Pod Ambient #shorts",
        "long_title": "Cryo Bay \U00002744️ 14 Minute Cold Ambient Soundscape for Deep Sleep | Sci-Fi Visualizer",
        "description": (
            "A cold, sparse, icy pad drenched in long reverb — the quiet "
            "stillness of a cryo-sleep bay. For deep, restful sleep and "
            "calm relaxation."
        ),
        "tags": [
            "space ambient", "sleep music", "deep sleep music", "cold ambient",
            "sci fi ambient", "relaxing sleep music", "meditation music",
            "ambient visualizer", "calm music", "insomnia relief music",
            "sleep sounds", "healing music",
        ],
    },
    {
        "key": "observatory_deck",
        "name": "Observatory Deck",
        "synth": "observatory_deck",
        "emoji": "\U0001F52D",  # 🔭
        "short_title": "Observatory Deck \U0001F52D Generative Focus Ambient #shorts",
        "long_title": "Observatory Deck \U0001F52D 14 Minute Generative Focus Soundtrack | Sci-Fi Ambient Visualizer",
        "description": (
            "A quiet pad under sparse, soft radar-ping accents — distant "
            "star data scrolling by. A generative, non-distracting "
            "soundtrack for focus and study."
        ),
        "tags": [
            "generative music", "focus music", "study music", "space ambient",
            "concentration music", "sci fi ambient", "deep work music",
            "ambient visualizer", "productivity music", "coding music",
            "instrumental focus music", "ambient focus music",
        ],
    },
    {
        "key": "ion_trail",
        "name": "Ion Trail",
        "synth": "ion_trail",
        "emoji": "\U00002728",  # ✨
        "short_title": "Ion Trail \U00002728 Coding Focus Music #shorts",
        "long_title": "Ion Trail \U00002728 14 Minute Coding Focus Music, Pulsing Sci-Fi Ambient | Ambient Visualizer",
        "description": (
            "A pulsing sub-bass under a generative, ever-shifting melodic "
            "trail — brighter, more rhythmic focus music for coding "
            "sessions and deep work."
        ),
        "tags": [
            "coding music", "focus music", "study music", "deep work music",
            "generative music", "sci fi ambient", "concentration music",
            "productivity music", "ambient visualizer", "programming music",
            "instrumental focus music", "space ambient",
        ],
    },
    {
        "key": "long_dark",
        "name": "The Long Dark",
        "synth": "long_dark",
        "emoji": "\U000026AB",  # ⚫
        "short_title": "The Long Dark \U000026AB Minimal Deep Space Drone #shorts",
        "long_title": "The Long Dark \U000026AB 14 Minute Minimal Deep Space Drone for Sleep & Isolation | Sci-Fi Ambient",
        "description": (
            "An ultra-sparse, minimal deep drone — the silence of open "
            "space between the stars. For deep sleep, isolation, and "
            "quiet focus."
        ),
        "tags": [
            "dark ambient", "deep drone music", "space ambient", "sleep music",
            "minimal ambient", "deep sleep music", "sci fi ambient",
            "meditation music", "ambient visualizer", "calm music",
            "isolation music", "drone music",
        ],
    },
    {
        "key": "starlight_convergence",
        "name": "Starlight Convergence",
        "synth": "starlight_convergence",
        "emoji": "\U0001F31F",  # 🌟
        "short_title": "Starlight Convergence \U0001F31F Hopeful Cosmic Ambient #shorts",
        "long_title": "Starlight Convergence \U0001F31F 14 Minute Hopeful Cosmic Ambient for Focus & Study | Sci-Fi Visualizer",
        "description": (
            "A warmer, hopeful cosmic pad — starlight converging across "
            "the void. Cinematic ambience for long focus sessions and "
            "quiet reflection."
        ),
        "tags": [
            "cosmic ambient", "space ambient", "cinematic ambient",
            "focus music", "study music", "sci fi ambient", "relaxing music",
            "ambient visualizer", "concentration music", "meditation music",
            "deep work music", "calm music",
        ],
    },
    {
        "key": "zero_g_drift",
        "name": "Zero-G Drift",
        "synth": "zero_g_drift",
        "emoji": "\U0001FA90",  # 🪐
        "short_title": "Zero-G Drift \U0001FA90 Weightless Ambient #shorts",
        "long_title": "Zero-G Drift \U0001FA90 14 Minute Weightless Ambient Soundscape for Focus & Relaxation | Sci-Fi Visualizer",
        "description": (
            "A wide, floaty pad with a slow, directionless drift — the "
            "weightlessness of zero gravity. For relaxation, soft focus, "
            "and unwinding."
        ),
        "tags": [
            "space ambient", "weightless music", "relaxing music",
            "sci fi ambient", "focus music", "ambient visualizer",
            "calm music", "meditation music", "cosmic ambient",
            "study music", "chill ambient", "background music",
        ],
    },
    {
        "key": "signal_lost",
        "name": "Signal Lost",
        "synth": "signal_lost",
        "emoji": "\U0001F4E1",  # 📡
        "short_title": "Signal Lost \U0001F4E1 Mysterious Space Static #shorts",
        "long_title": "Signal Lost \U0001F4E1 14 Minute Mysterious Deep Space Static Ambient | Sci-Fi Ambient Visualizer",
        "description": (
            "Faint radio static and distant tone blips, drifting signals "
            "from somewhere out in the dark. A mysterious, atmospheric "
            "texture for focus and background noise."
        ),
        "tags": [
            "space ambient", "radio static", "mysterious ambient",
            "sci fi ambient", "focus noise", "ambient visualizer",
            "atmospheric music", "dark ambient", "study noise",
            "relaxing noise", "background noise", "cosmic ambient",
        ],
    },
]

BRAND_NAME = "Sanctuary of Sci"
BRAND_TAGLINE = "Deep Space. Deep Focus."

GLOBAL_TAGS = [
    "space ambient", "sci fi ambient", "cosmic ambient", "focus music",
    "study music", "coding music", "deep space music", "ambient visualizer",
    "concentration music", "deep work music", "generative music",
    "productivity music", "relaxing music", "meditation music",
    "dark ambient animation", "background music for studying",
]

PERFECT_FOR = "coding, deep work, studying, late-night focus, and space-themed relaxation"

PLAYLISTS = {
    "dark_drone": {
        "title": "Deep Space Drone \U000026AB",
        "description": "Deep, minimal drones and engine hums from the far "
                       "reaches of space. Sci-fi ambient visualizer.",
        "themes": ["sleeper_drift", "long_dark"],
    },
    "mechanical": {
        "title": "Station & Engine Ambience \U0001F6F0️",
        "description": "Mechanical hums and pulsing engine textures for "
                       "deep work and coding. Sci-fi ambient visualizer.",
        "themes": ["station_hum", "ion_trail"],
    },
    "cosmic_pad": {
        "title": "Cosmic Pads & Nebulae \U0001F30C",
        "description": "Wide, slowly shifting cosmic pads for focus, "
                       "study, and relaxation. Sci-fi ambient visualizer.",
        "themes": ["nebula_watch", "starlight_convergence", "zero_g_drift"],
    },
    "generative_focus": {
        "title": "Generative Focus & Coding \U00002728",
        "description": "Generative, non-distracting soundtracks for deep "
                       "focus and coding sessions. Sci-fi ambient visualizer.",
        "themes": ["observatory_deck"],
    },
    "cold_ambient": {
        "title": "Cryo Sleep & Cold Ambient \U00002744️",
        "description": "Cold, sparse ambient soundscapes for deep sleep "
                       "and relaxation. Sci-fi ambient visualizer.",
        "themes": ["cryo_bay"],
    },
    "atmosphere": {
        "title": "Deep Space Atmosphere \U0001F4E1",
        "description": "Mysterious, atmospheric space textures and "
                       "signals. Sci-fi ambient visualizer.",
        "themes": ["signal_lost"],
    },
}

# Per-theme accent color (hex) for the procedural animated background --
# cool blues and deep violets, matching the channel's visual identity.
ACCENT_COLORS = {
    "sleeper_drift": "1a2744",
    "nebula_watch": "4a3a7a",
    "station_hum": "35506b",
    "cryo_bay": "2e6b7a",
    "observatory_deck": "3a3a7a",
    "ion_trail": "2a5aa0",
    "long_dark": "10182e",
    "starlight_convergence": "5a4a9a",
    "zero_g_drift": "4a5a9a",
    "signal_lost": "3a4a5a",
}


def synth_args(theme: dict) -> list:
    """generate_theme_audio.py CLI flags for a theme's frequency layers and
    tone shaping. Same contract as aether/themes.py."""
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

# Truthful, non-AI disclosure: 100% algorithmic sound synthesis, no samples,
# no AI generation.
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
