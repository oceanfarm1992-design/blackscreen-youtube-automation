#!/usr/bin/env python3
"""
Theme definitions, daily rotation, and SEO metadata for the "Meditated Sleeping"
channel.

Four themes rotate one-per-day in this fixed order:
    0 rain -> 1 waterfall -> 2 forest -> 3 sleeping -> (wrap)

Each theme carries:
- audio synthesis parameters (consumed by generate_theme_audio.py)
- SEO metadata templates for both the 59s Short and the 8-12h long-form video
  (consumed by make_metadata.py)

Rotation is anchored to a fixed date so it is deterministic and reproducible: given
any calendar date, the active theme is fully determined (no state file needed).
"""
from datetime import date

# Day 0 of the rotation. Chosen as the channel's automation start date so that
# 2026-08-05 == theme index 0 (rain). Changing this shifts the whole schedule.
ANCHOR = date(2026, 8, 5)

# Long-form target length in hours. Spec allows 8-12h; QC enforces that window.
LONG_HOURS_DEFAULT = 10

# Ordered rotation. `synth` names a function in generate_theme_audio.py.
THEMES = [
    {
        "key": "rain",
        "name": "Rainy with Calm Music",
        "synth": "rain",
        "emoji": "\U0001F327️",  # 🌧️
        "short_title": "Fall Asleep Fast to Rain \U0001F327️ Calm Rain Sounds for Deep Sleep #shorts",
        "long_title": "Rain Sounds for Sleeping \U0001F327️ {hours} Hours Deep Sleep Music, Rain & Thunder | Black Screen",
        "description": (
            "Gentle rainfall, distant thunder, and soft ambient pads to help you fall "
            "asleep fast and stay asleep. Let the calm rain wash the day away and drift "
            "into deep, restful sleep."
        ),
        "tags": [
            "rain sounds", "rain sounds for sleeping", "sleep music", "rain and thunder",
            "deep sleep", "relaxing rain", "ambient music", "black screen", "calm music",
            "study music", "meditation", "insomnia relief", "white noise",
        ],
    },
    {
        "key": "waterfall",
        "name": "Waterfall Music",
        "synth": "waterfall",
        "emoji": "\U0001F4A7",  # 💧
        "short_title": "Soothing Waterfall Sounds \U0001F4A7 Relax & Sleep in 59 Seconds #shorts",
        "long_title": "Waterfall Sounds \U0001F4A7 {hours} Hours of Flowing Water for Sleep & Focus | Black Screen",
        "description": (
            "Flowing water streams and cascading falls blended with soothing natural "
            "harmony. Perfect for deep sleep, relaxation, meditation, and focused study."
        ),
        "tags": [
            "waterfall sounds", "water sounds", "sleep music", "relaxing water",
            "nature sounds", "deep sleep", "ambient music", "black screen", "focus music",
            "meditation", "study music", "white noise", "stress relief",
        ],
    },
    {
        "key": "forest",
        "name": "Natural Green Forest Sounds",
        "synth": "forest",
        "emoji": "\U0001F332",  # 🌲
        "short_title": "Peaceful Forest Sounds \U0001F332 Birds, Water Drops & Calm #shorts",
        "long_title": "Forest Sounds \U0001F332 {hours} Hours of Birdsong & Gentle Nature for Sleep | Black Screen",
        "description": (
            "Gentle water drops, natural bird chirps, and soft wind rustling through the "
            "trees. Immerse yourself in a calm green forest for restful sleep, relaxation, "
            "and peaceful focus."
        ),
        "tags": [
            "forest sounds", "nature sounds", "bird sounds", "sleep music",
            "relaxing nature", "deep sleep", "ambient music", "black screen",
            "meditation", "study music", "calm music", "forest ambience", "birdsong",
        ],
    },
    {
        "key": "sleeping",
        "name": "Sleeping Music",
        "synth": "sleeping",
        "emoji": "\U0001F319",  # 🌙
        "short_title": "Deep Sleep Music \U0001F319 Drift Off in Under a Minute #shorts",
        "long_title": "Deep Sleep Music \U0001F319 {hours} Hours Ambient Drone for Deep Sleep | Black Screen",
        "description": (
            "Deep ambient drone and slow evolving chords for peaceful, restorative sleep. "
            "Soft, calming tones designed to quiet the mind and guide you into deep rest."
        ),
        "tags": [
            "sleep music", "deep sleep music", "ambient music", "relaxing music",
            "calm music", "meditation music", "black screen", "sleep aid",
            "insomnia relief", "delta waves", "healing music", "stress relief", "spa music",
        ],
    },
]

BRAND_NAME = "Meditated Sleeping"
BRAND_TAGLINE = "Calm. Sleep. Restore."

# Appended to every description.
DESCRIPTION_FOOTER = (
    "\n\n— {brand} — {tagline}\n\n"
    "\U0001F3A7 Best experienced with headphones at a low, comfortable volume.\n"
    "All audio is original and generated for this channel.\n\n"
    "Please note: this content is for relaxation and ambience only and is not a "
    "substitute for medical advice or treatment."
)


def theme_for_date(d: date | None = None) -> dict:
    """Return the active theme dict for the given date (defaults to today)."""
    d = d or date.today()
    idx = (d - ANCHOR).days % len(THEMES)
    return THEMES[idx]


def theme_by_key(key: str) -> dict:
    for t in THEMES:
        if t["key"] == key:
            return t
    raise KeyError(f"Unknown theme key: {key!r}. Valid: {[t['key'] for t in THEMES]}")


def resolve_theme(selector: str | None, d: date | None = None) -> dict:
    """`selector` is a theme key, or 'auto'/None for the date-based rotation."""
    if selector in (None, "auto"):
        return theme_for_date(d)
    return theme_by_key(selector)


if __name__ == "__main__":
    # Quick manual check: print the 4-day rotation starting today.
    from datetime import timedelta
    today = date.today()
    for i in range(len(THEMES)):
        t = theme_for_date(today + timedelta(days=i))
        print(f"{today + timedelta(days=i)}  ->  {t['key']:10s}  {t['name']}")
