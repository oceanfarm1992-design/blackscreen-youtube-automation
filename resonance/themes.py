#!/usr/bin/env python3
"""
Theme definitions, daily rotation, and SEO metadata for the "Aether
Resonance" channel (functional wellness/sleep/meditation ambient built
around pure frequencies, sound baths, and generative drones).

NOTE: this is a DIFFERENT channel from "Aether & Ash" (the aether/ folder)
-- similar name, unrelated brand/catalog/credentials. Kept in its own
resonance/ folder specifically to avoid any collision with aether/.

Same contract as aether/themes.py, sanctuary/themes.py, hearth/themes.py,
horizon/themes.py -- only the data below differs. Most themes here lean on
the existing wellness-frequency layer (tone_drone/binaural/isochronic/
singing_bowl in scripts/generate_theme_audio.py) via synth="none" plus
tone/beat/bowl fields, exactly like the Meditated Sleeping channel's
frequency themes -- see synth_args() below.

10 themes rotate through a sliding daily window (see daily_selection below).
"""
from datetime import date

ANCHOR = date(2026, 10, 4)

FEATURE_SECONDS = 870  # 14:30
SHORT_SECONDS = 59

LONGS_PER_DAY = 1
SHORTS_PER_DAY = 1
DAILY_COUNT = LONGS_PER_DAY + SHORTS_PER_DAY

# Ordered rotation. `synth` is "none" (pure frequency layer) or a function
# name in scripts/generate_theme_audio.py for a generative drone/noise bed.
THEMES = [
    {
        "key": "still_water",
        "name": "Still Water",
        "synth": "none",
        "tone": "432", "beat": "delta", "beat_type": "binaural",
        "emoji": "\U0001F4A7",  # 💧
        "short_title": "Still Water \U0001F4A7 432 Hz Anxiety Relief & Sleep #shorts",
        "long_title": "Still Water \U0001F4A7 14 Minute 432 Hz Delta Wave Sound Bath for Anxiety Relief & Sleep | Visualizer",
        "description": (
            "A still, 432 Hz tuned tone with gentle delta-rate binaural "
            "beats — a calm sound bath for anxiety relief and deep rest. "
            "Use headphones for the binaural effect."
        ),
        "tags": [
            "432 hz", "sound bath", "anxiety relief music", "delta waves",
            "binaural beats sleep", "meditation music", "healing frequency",
            "ambient visualizer", "sleep music", "calm music",
            "relaxation music", "deep sleep music",
        ],
    },
    {
        "key": "crown_light",
        "name": "Crown Light",
        "synth": "none",
        "tone": "963", "tone_soft": True, "reverb": 0.4, "tone_tilt": 2,
        "tone_gain": 0.14,
        "emoji": "\U00002728",  # ✨
        "short_title": "Crown Light \U00002728 963 Hz Sound Bath Meditation #shorts",
        "long_title": "Crown Light \U00002728 14 Minute 963 Hz Crown Chakra Sound Bath for Deep Meditation | Visualizer",
        "description": (
            "The 963 Hz crown-chakra Solfeggio tone, kept soft and subtle, "
            "for spiritual calm and deep meditation."
        ),
        "tags": [
            "963 hz", "crown chakra", "sound bath", "solfeggio frequencies",
            "meditation music", "spiritual music", "healing frequency",
            "ambient visualizer", "calm music", "deep meditation",
            "relaxation music", "chakra healing",
        ],
    },
    {
        "key": "root_anchor",
        "name": "Root Anchor",
        "synth": "none",
        "tone": "396", "beat": "theta", "beat_type": "isochronic",
        "emoji": "\U0001FAB4",  # 🪴
        "short_title": "Root Anchor \U0001FAB4 396 Hz Grounding Sound Bath #shorts",
        "long_title": "Root Anchor \U0001FAB4 14 Minute 396 Hz Grounding Sound Bath, Release Fear & Anxiety | Visualizer",
        "description": (
            "The grounding 396 Hz Solfeggio tone with theta-rate isochronic "
            "pulses — a steady anchor for releasing fear and anxiety. "
            "Works on speakers or headphones."
        ),
        "tags": [
            "396 hz", "grounding meditation", "sound bath",
            "solfeggio frequencies", "anxiety relief music", "theta waves",
            "meditation music", "ambient visualizer", "healing frequency",
            "calm music", "relaxation music", "isochronic tones",
        ],
    },
    {
        "key": "heart_bloom",
        "name": "Heart Bloom",
        "synth": "none",
        "tone": "639", "tone_soft": True, "bowl": True, "reverb": 0.3,
        "tone_gain": 0.13,
        "emoji": "\U0001F49A",  # 💚
        "short_title": "Heart Bloom \U0001F49A 639 Hz Singing Bowl Sound Bath #shorts",
        "long_title": "Heart Bloom \U0001F49A 14 Minute 639 Hz Singing Bowl Sound Bath for Harmony & Connection | Visualizer",
        "description": (
            "The 639 Hz Solfeggio tone layered with Tibetan singing bowl "
            "overtones — a warm sound bath for harmony, connection, and "
            "calm."
        ),
        "tags": [
            "639 hz", "singing bowl", "sound bath", "solfeggio frequencies",
            "heart chakra", "meditation music", "healing frequency",
            "ambient visualizer", "relaxation music", "calm music",
            "chakra healing", "tibetan bowl meditation",
        ],
    },
    {
        "key": "third_eye_drift",
        "name": "Third Eye Drift",
        "synth": "none",
        "tone": "852", "tone_soft": True, "reverb": 0.4, "tone_tilt": 2,
        "tone_gain": 0.13,
        "emoji": "\U0001F52E",  # 🔮
        "short_title": "Third Eye Drift \U0001F52E 852 Hz Sound Bath #shorts",
        "long_title": "Third Eye Drift \U0001F52E 14 Minute 852 Hz Third Eye Sound Bath for Intuition & Calm | Visualizer",
        "description": (
            "The 852 Hz Solfeggio tone, gentle and soft, to awaken "
            "intuition and settle a busy mind."
        ),
        "tags": [
            "852 hz", "third eye", "sound bath", "solfeggio frequencies",
            "intuition meditation", "meditation music", "healing frequency",
            "ambient visualizer", "calm music", "relaxation music",
            "chakra healing", "spiritual music",
        ],
    },
    {
        "key": "cellular_renewal",
        "name": "Cellular Renewal",
        "synth": "resonance_drone",
        "tone": "285", "tone_soft": True, "tone_gain": 0.1,
        "emoji": "\U0001F331",  # 🌱
        "short_title": "Cellular Renewal \U0001F331 285 Hz Healing Drone #shorts",
        "long_title": "Cellular Renewal \U0001F331 14 Minute 285 Hz Healing Frequency Drone Sound Bath | Visualizer",
        "description": (
            "A slow generative drone under the 285 Hz Solfeggio tone — "
            "deep, restorative ambience for rest and renewal."
        ),
        "tags": [
            "285 hz", "healing frequency", "sound bath", "solfeggio frequencies",
            "drone music", "meditation music", "ambient visualizer",
            "calm music", "relaxation music", "deep sleep music",
            "generative music", "restorative music",
        ],
    },
    {
        "key": "miracle_tone",
        "name": "Miracle Tone",
        "synth": "none",
        "tone": "528", "tone_soft": True, "beat": "delta", "beat_type": "binaural",
        "tone_gain": 0.13,
        "emoji": "\U0001F33F",  # 🍃
        "short_title": "Miracle Tone \U0001F33F 528 Hz Sound Bath for Sleep #shorts",
        "long_title": "Miracle Tone \U0001F33F 14 Minute 528 Hz Solfeggio Sound Bath with Delta Waves for Sleep | Visualizer",
        "description": (
            "The 528 Hz \"miracle tone\" blended with gentle delta-rate "
            "binaural beats — a calm sound bath for deep, restful sleep."
        ),
        "tags": [
            "528 hz", "solfeggio frequencies", "sound bath", "delta waves",
            "binaural beats sleep", "deep sleep music", "healing frequency",
            "meditation music", "ambient visualizer", "calm music",
            "relaxation music", "miracle tone",
        ],
    },
    {
        "key": "singing_bowl_sanctuary",
        "name": "Singing Bowl Sanctuary",
        "synth": "none",
        "tone": "136.1", "tone_soft": True, "bowl": True, "reverb": 0.35,
        "tone_gain": 0.14,
        "emoji": "\U0001F6D5",  # 🛕
        "short_title": "Singing Bowl Sanctuary \U0001F6D5 OM Frequency Sound Bath #shorts",
        "long_title": "Singing Bowl Sanctuary \U0001F6D5 14 Minute OM 136.1 Hz Tibetan Singing Bowl Sound Bath | Visualizer",
        "description": (
            "The deep OM frequency (136.1 Hz) layered with Tibetan singing "
            "bowl overtones — a grounding, soothing sanctuary of sound."
        ),
        "tags": [
            "singing bowl", "om frequency", "sound bath", "136 hz",
            "tibetan meditation", "meditation music", "healing frequency",
            "ambient visualizer", "calm music", "relaxation music",
            "deep meditation", "chanting",
        ],
    },
    {
        "key": "theta_gateway",
        "name": "Theta Gateway",
        "synth": "resonance_drone",
        "beat": "theta", "beat_type": "binaural", "tone": "210",
        "emoji": "\U0001F300",  # 🌀
        "short_title": "Theta Gateway \U0001F300 Deep Meditation Drone #shorts",
        "long_title": "Theta Gateway \U0001F300 14 Minute Theta Wave Generative Drone for Deep Meditation | Sound Bath Visualizer",
        "description": (
            "A generative drone bed with theta-rate binaural beats — a "
            "gateway into deep meditative states. Use headphones for the "
            "binaural effect."
        ),
        "tags": [
            "theta waves", "binaural beats meditation", "drone music",
            "sound bath", "deep meditation", "meditation music",
            "ambient visualizer", "calm music", "relaxation music",
            "generative music", "brain waves", "healing frequency",
        ],
    },
    {
        "key": "pink_noise_veil",
        "name": "Pink Noise Veil",
        "synth": "pink_veil",
        "tone": "174", "tone_soft": True, "tone_gain": 0.08,
        "emoji": "\U0001FA77",  # 🩷
        "short_title": "Pink Noise Veil \U0001FA77 Soothing Sound Bath #shorts",
        "long_title": "Pink Noise Veil \U0001FA77 14 Minute Soothing Pink Noise Sound Bath for Deep Sleep | Visualizer",
        "description": (
            "An organic, continuous pink-noise wash under a soft 174 Hz "
            "grounding tone — a soothing veil of sound for deep, restful "
            "sleep."
        ),
        "tags": [
            "pink noise", "sound bath", "174 hz", "deep sleep music",
            "grounding frequency", "meditation music", "ambient visualizer",
            "calm music", "relaxation music", "white noise",
            "healing frequency", "sleep sounds",
        ],
    },
]

BRAND_NAME = "Aether Resonance"
BRAND_TAGLINE = "Pure Tone. Deep Calm."

GLOBAL_TAGS = [
    "sound bath", "solfeggio frequencies", "meditation music",
    "healing frequency", "ambient visualizer", "calm music",
    "relaxation music", "deep sleep music", "anxiety relief music",
    "binaural beats", "singing bowl", "drone music", "generative music",
    "background music for studying", "sleep music",
]

PERFECT_FOR = "sound baths, meditation, deep sleep, anxiety relief, and relaxation"

PLAYLISTS = {
    "solfeggio": {
        "title": "Solfeggio Sound Baths \U00002728",
        "description": "Pure Solfeggio frequency sound baths for "
                       "meditation, calm, and healing. Ambient visualizer.",
        "themes": ["crown_light", "root_anchor", "heart_bloom", "third_eye_drift", "miracle_tone"],
    },
    "sleep_frequencies": {
        "title": "Sleep Frequencies & Delta Waves \U0001F4A7",
        "description": "Frequency-based sound baths with delta-wave "
                       "binaural beats for deep, restful sleep. Ambient visualizer.",
        "themes": ["still_water", "pink_noise_veil"],
    },
    "singing_bowl": {
        "title": "Singing Bowl Sound Baths \U0001F6D5",
        "description": "Tibetan singing bowl overtones layered with "
                       "healing frequencies. Ambient visualizer.",
        "themes": ["singing_bowl_sanctuary"],
    },
    "generative_drone": {
        "title": "Generative Drones & Frequencies \U0001F300",
        "description": "Generative drone soundscapes layered with healing "
                       "frequencies for deep meditation and renewal. Ambient visualizer.",
        "themes": ["cellular_renewal", "theta_gateway"],
    },
}

ACCENT_COLORS = {
    "still_water": "3a6a7a",
    "crown_light": "6a5a9a",
    "root_anchor": "7a4a3a",
    "heart_bloom": "4a8a6a",
    "third_eye_drift": "5a4a8a",
    "cellular_renewal": "4a7a8a",
    "miracle_tone": "4a6a9a",
    "singing_bowl_sanctuary": "8a7a4a",
    "theta_gateway": "5a5a8a",
    "pink_noise_veil": "9a6a7a",
}

# Topic for each theme's generative animation (scripts/make_animated_video.py
# --topic) -- matches the pan motion/flicker profile to what the theme is
# actually about. Falls back to "neutral" for any key left unlisted.
TOPICS = {
    "still_water": "water",
    "crown_light": "fire",
    "root_anchor": "stone",
    "heart_bloom": "wind",
    "third_eye_drift": "void",
    "cellular_renewal": "wind",
    "miracle_tone": "water",
    "singing_bowl_sanctuary": "stone",
    "theta_gateway": "void",
    "pink_noise_veil": "water",
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
    "Please note: this content is for relaxation and ambience only, no clinical "
    "efficacy is claimed, and it is not a substitute for medical or "
    "mental-health advice."
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
        print(f"{today + timedelta(days=i)}  ->  {t['key']:24s}  {t['name']}")
