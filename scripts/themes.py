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
# 10h (not 12h) — YouTube rejected exactly-12h uploads as "too long".
LONG_HOURS_DEFAULT = 10

# Daily publishing plan, spread across 6 scheduled runs (one video each):
#   LONGS_PER_DAY long-forms + SHORTS_PER_DAY Shorts, each a different music.
# Quota: 5 longs (1600 insert + 50 thumbnail) + 1 short (1600, no thumbnail)
#        = 9,850 units/day, within the free 10,000/day YouTube API quota.
LONGS_PER_DAY = 5
SHORTS_PER_DAY = 1
DAILY_COUNT = LONGS_PER_DAY + SHORTS_PER_DAY  # distinct musics used per day

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
            "rain sounds for sleeping", "sleep music", "rain sounds", "deep sleep music",
            "relaxing rain", "rain and thunder sounds", "rain sounds black screen",
            "black screen", "calm music", "study music", "meditation music",
            "insomnia relief music", "white noise", "rain ambience", "sleep sounds",
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
            "waterfall sounds", "water sounds for sleeping", "sleep music",
            "relaxing water sounds", "nature sounds", "deep sleep music",
            "waterfall white noise", "black screen", "focus music", "meditation music",
            "study music", "calming water sounds", "stress relief music", "sleep sounds",
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
            "forest sounds", "nature sounds for sleeping", "birds singing", "sleep music",
            "relaxing nature sounds", "deep sleep music", "forest ambience", "birdsong",
            "black screen", "meditation music", "calming nature sounds", "study music",
            "forest white noise", "sleep sounds",
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
            "sleep music", "deep sleep music", "relaxing sleep music",
            "calm music for sleeping", "meditation music", "ambient sleep music",
            "black screen sleep", "sleep aid", "insomnia relief music", "soothing music",
            "healing music", "stress relief music", "spa music", "sleep sounds",
        ],
    },
    {
        "key": "indian",
        "name": "Indian Sleep Music",
        "synth": "indian",
        "emoji": "\U0001FAB7",  # 🪷
        "short_title": "Indian Flute Sleep Music \U0001FAB7 Deep Sleep in 59s #shorts",
        "long_title": "Indian Sleep Music \U0001FAB7 {hours} Hours Tanpura & Flute for Deep Sleep | Black Screen",
        "description": (
            "Soothing Indian classical sleep music: a gentle tanpura drone with soft "
            "bansuri-style flute in a calming raga. Let the meditative sound quiet your "
            "mind and guide you into deep, restful sleep."
        ),
        "tags": [
            "indian sleep music", "tanpura meditation", "indian flute music",
            "raga for sleep", "meditation music", "deep sleep music",
            "relaxing indian music", "indian classical music", "yoga music", "spa music",
            "healing music", "calming flute music", "black screen", "sleep sounds",
        ],
    },
    {
        "key": "romantic",
        "name": "Romantic Love Music",
        "synth": "romantic",
        "emoji": "\U0001F495",  # 💕
        "short_title": "Romantic Love Music \U0001F495 Warm & Soothing #shorts",
        "long_title": "Romantic Music \U0001F495 {hours} Hours Warm Instrumental Love Songs | Black Screen",
        "description": (
            "Warm, tender instrumental love music with lush chords and a soft melody. "
            "Perfect for a romantic evening, a candle-lit dinner, relaxing together, or "
            "simply unwinding in a gentle, heartfelt mood."
        ),
        "tags": [
            "romantic music", "romantic instrumental", "relaxing romantic music",
            "calm romantic music", "dinner music", "date night music",
            "background music", "soft piano music", "mood music", "relaxing music",
            "romantic background music", "instrumental music", "black screen",
        ],
    },
    {
        "key": "romantic_night",
        "name": "Romantic Night Music",
        "synth": "romantic_night",
        "emoji": "\U0001F339",  # 🌹
        "short_title": "Romantic Night Music \U0001F339 Smooth & Relaxing #shorts",
        "long_title": "Romantic Night Music \U0001F339 {hours} Hours Smooth Relaxing Instrumental | Black Screen",
        "description": (
            "Slow, smooth, and warm instrumental music for a relaxing romantic evening. "
            "Mellow chords and a soft melody set a calm, cozy mood — perfect for a quiet "
            "dinner, unwinding after a long day, or peaceful time together."
        ),
        "tags": [
            "romantic music", "relaxing romantic music", "romantic instrumental",
            "smooth relaxing music", "date night music", "dinner music",
            "calm background music", "evening music", "soft instrumental music",
            "mood music", "chill music", "relaxing music", "black screen",
        ],
    },
    {
        "key": "gamma_focus",
        "name": "40 Hz Gamma Focus",
        "synth": "none",
        "tone": "200", "beat": "gamma", "beat_type": "binaural",
        "emoji": "\U0001F9E0",  # 🧠
        "short_title": "40 Hz Gamma Focus Music \U0001F9E0 Study & Concentration #shorts",
        "long_title": "40 Hz Gamma Binaural Beats \U0001F9E0 {hours} Hours Focus, Study & Concentration | Black Screen",
        "description": (
            "40 Hz gamma binaural beats to support deep focus, studying, reading, and "
            "concentration. Use headphones for the binaural effect. Black screen, "
            "distraction-free."
        ),
        "tags": [
            "40 hz", "gamma binaural beats", "binaural beats focus", "focus music",
            "concentration music", "study music", "deep focus", "binaural beats study",
            "brain waves", "productivity music", "gamma waves", "black screen",
        ],
    },
    {
        "key": "528hz_sleep",
        "name": "528 Hz Sleep Music",
        "synth": "sleeping",
        "tone": "528", "beat": "delta", "beat_type": "binaural",
        "emoji": "\U00002728",  # ✨
        "short_title": "528 Hz Sleep Music \U00002728 Solfeggio Deep Sleep #shorts",
        "long_title": "528 Hz Sleep Music \U00002728 {hours} Hours Solfeggio Tone for Deep Sleep | Black Screen",
        "description": (
            "528 Hz Solfeggio tone blended with warm sleep music and gentle delta-rate "
            "binaural beats for deep, restful sleep. Use headphones for the binaural "
            "effect. Black screen."
        ),
        "tags": [
            "528 hz", "528 hz music", "solfeggio frequencies", "528 hz sleep",
            "sleep music", "deep sleep music", "solfeggio 528", "healing frequency",
            "meditation music", "delta waves", "binaural beats sleep", "black screen",
        ],
    },
    {
        "key": "delta_sleep",
        "name": "Delta Waves Sleep",
        "synth": "sleeping",
        "tone": "110", "beat": "delta", "beat_type": "binaural",
        "emoji": "\U0001F4A4",  # 💤
        "short_title": "Delta Waves Sleep \U0001F4A4 Binaural Beats for Deep Sleep #shorts",
        "long_title": "Delta Waves \U0001F4A4 {hours} Hours Binaural Beats for Deep Sleep | Black Screen",
        "description": (
            "Deep delta-wave binaural beats with warm ambient sleep music to help you "
            "fall into deep, restorative sleep. Use headphones for the binaural effect. "
            "Black screen."
        ),
        "tags": [
            "delta waves", "binaural beats sleep", "deep sleep music", "delta waves sleep",
            "sleep music", "binaural beats", "brain waves", "meditation music",
            "insomnia relief music", "relaxing music", "black screen", "healing music",
        ],
    },
    {
        "key": "432hz_relax",
        "name": "432 Hz Relaxing Music",
        "synth": "sleeping",
        "tone": "432",
        "emoji": "\U0001F338",  # 🌸
        "short_title": "432 Hz Music \U0001F338 Relaxing 432 Hz for Sleep #shorts",
        "long_title": "432 Hz Music \U0001F338 {hours} Hours Relaxing 432 Hz for Sleep & Calm | Black Screen",
        "description": (
            "Warm, relaxing music tuned to 432 Hz for sleep, calm, and meditation. "
            "Soothing tones to help unwind the mind and body. Black screen."
        ),
        "tags": [
            "432 hz", "432 hz music", "432 hz sleep", "relaxing music", "sleep music",
            "meditation music", "calm music", "healing frequency", "432 hz meditation",
            "deep sleep music", "black screen", "spa music",
        ],
    },
]

BRAND_NAME = "Meditated Sleeping"
BRAND_TAGLINE = "Calm. Sleep. Restore."

# Appended to every description.
DESCRIPTION_FOOTER = (
    "\n\n— {brand} — {tagline}\n\n"
    "\U0001F3A7 Best experienced with headphones at a low, comfortable volume.\n"
    "\U0001F3B5 All music is original, thoughtfully created with the help of AI for a "
    "calm and relaxing listening experience.\n\n"
    "Please note: this content is for relaxation and ambience only and is not a "
    "substitute for medical advice or treatment."
)


def theme_for_date(d: date | None = None) -> dict:
    """Return the active theme dict for the given date (defaults to today)."""
    d = d or date.today()
    idx = (d - ANCHOR).days % len(THEMES)
    return THEMES[idx]


def daily_selection(d: date | None = None, count: int = DAILY_COUNT) -> list[dict]:
    """Return `count` themes for the given date.

    A sliding window of `count` themes advances by `count` positions each day, so
    over successive days the whole library is cycled through for variety (rather
    than the same set repeating). Deterministic: the date fully fixes the picks.
    """
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
