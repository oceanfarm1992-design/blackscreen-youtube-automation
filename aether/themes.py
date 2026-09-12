#!/usr/bin/env python3
"""
Theme definitions, daily rotation, and SEO metadata for the "Aether & Ash"
channel (dark ambient / drone / focus / writing / cinematic / sleep music).

Same contract as scripts/themes.py (the "Meditated Sleeping" channel) so
produce.py / make_metadata.py / publish_queue.py work unchanged against
either theme module -- only the data below differs.

15 themes rotate through a sliding daily window (see daily_selection below).
Rotation is anchored to a fixed date so it is deterministic and reproducible.
"""
from datetime import date

# Day 0 of the rotation -- the channel's automation start date.
ANCHOR = date(2026, 9, 12)

# Every long-form is now a fixed-length "feature" video (real generative
# animation, not an hours-long static background) -- see
# aether/make_animated_video.py. No more per-theme hour targets.
FEATURE_SECONDS = 870  # 14:30

# Daily publishing plan: 1 feature (14:30) + 1 Short per day, on a SINGLE
# OAuth/Cloud project (1*1650(+thumb) + 1*1600 + 50 playlist-add ~= 3,300 /
# 10,000 units -- very comfortable headroom).
LONGS_PER_DAY = 1
SHORTS_PER_DAY = 1
DAILY_COUNT = LONGS_PER_DAY + SHORTS_PER_DAY

# Accent color (hex) for each theme's generative animated background --
# drives the colorchannelmixer tint in make_animated_video.py. Chosen to
# match each theme's mood/thumbnail palette.
ACCENT_COLORS = {
    "void_drone": "28325a",
    "abyssal_silence": "2d4173",
    "ember_focus": "ff7a33",
    "cosmic_drift": "7850c8",
    "creative_flow": "c85a3c",
    "shadow_ink": "3c4b5f",
    "calm_the_night": "32376e",
    "slumber_of_ash": "4b418c",
    "ethereal_ruins": "967846",
    "ember_solitude": "af5f37",
    "markov_chamber": "734bb9",
    "ash_rain_wind": "50696e",
    "black_hole": "642828",
    "monastic_echoes": "917341",
    "obsidian_tower": "37415a",
}

# Ordered rotation. `synth` names a function in scripts/generate_theme_audio.py.
THEMES = [
    {
        "key": "void_drone",
        "name": "Void Drones",
        "synth": "void_drone",
        "emoji": "\U0001F311",  # 🌑
        "short_title": "Void Drones \U0001F311 Deep Dark Ambient Drone #shorts",
        "long_title": "Void Drones \U0001F311 14 Minute Deep Cosmic Drone for Focus & Sleep | Dark Ambient Visualizer",
        "description": (
            "A deep, layered sub-bass drone for cosmic isolation and heavy "
            "focus. Dark, minimal, and immersive — let the low rumble clear "
            "your mind for deep work, meditation, or sleep."
        ),
        "tags": [
            "dark ambient", "drone music", "dark drone", "deep drone music",
            "ambient drone", "sub bass drone", "dark ambient music",
            "cosmic ambient", "focus music", "sleep music",
            "meditation music", "dark academia music", "study music",
        ],
    },
    {
        "key": "abyssal_silence",
        "name": "Abyssal Silence",
        "synth": "abyssal_silence",
        "emoji": "\U0001F30C",  # 🌌
        "short_title": "Abyssal Silence \U0001F30C Dark Ambient for Anxiety Relief #shorts",
        "long_title": "Abyssal Silence \U0001F30C 14 Minute Dark Ambient for Anxiety Relief & Deep Sleep | Dark Ambient Visualizer",
        "description": (
            "A still, low drone chord over a soft dark noise floor — deep "
            "stillness for anxiety relief, calm, and dark, restful sleep."
        ),
        "tags": [
            "dark ambient", "anxiety relief music", "drone music",
            "deep sleep music", "dark drone", "calm music",
            "ambient music", "relaxing dark music", "sleep sounds",
            "stress relief music", "meditation music",
        ],
    },
    {
        "key": "ember_focus",
        "name": "Deep Ember Focus",
        "synth": "ember_focus",
        "emoji": "\U0001F525",  # 🔥
        "short_title": "Deep Ember Focus \U0001F525 Late Night Study Music #shorts",
        "long_title": "Deep Ember Focus \U0001F525 14 Minute Study Music for Late Night Coding & Deep Work | Dark Ambient Visualizer",
        "description": (
            "Gentle plucked tones with a long reverb tail over a warm sub "
            "pad — minimal-distraction music for late night coding, deep "
            "study, and focused work."
        ),
        "tags": [
            "study music", "focus music", "deep work music", "coding music",
            "concentration music", "dark academia music", "ambient study music",
            "productivity music", "generative music",
            "instrumental study music", "dark ambient",
        ],
    },
    {
        "key": "cosmic_drift",
        "name": "Cosmic Drift",
        "synth": "cosmic_drift",
        "emoji": "\U00002728",  # ✨
        "short_title": "Cosmic Drift \U00002728 Astral Study & Space Ambient #shorts",
        "long_title": "Cosmic Drift \U00002728 14 Minute Astral Space Ambient for Study & Soft Focus | Dark Ambient Visualizer",
        "description": (
            "A warm, slowly shifting pad drifting through soft modulation — "
            "astral space ambient for studying, soft focus, and unwinding."
        ),
        "tags": [
            "space ambient", "study music", "focus music", "ambient music",
            "cosmic music", "soft focus music", "dark academia music",
            "chill study music", "concentration music",
            "relaxing ambient", "meditation music",
        ],
    },
    {
        "key": "creative_flow",
        "name": "Creative Flow",
        "synth": "creative_flow",
        "emoji": "\U0001FAB6",  # 🪶
        "short_title": "Creative Flow \U0001FAB6 Inspiring Writing Ambient #shorts",
        "long_title": "Creative Flow \U0001FAB6 14 Minute Inspiring Writing Ambient for Fantasy & Dark Storytelling | Dark Ambient Visualizer",
        "description": (
            "An evolving pad with a slow sweeping tone, built for fantasy "
            "writing, dark storytelling, and creative flow. Let the mood "
            "carry the story forward."
        ),
        "tags": [
            "writing music", "writing ambient", "fantasy music", "focus music",
            "dark academia music", "creative writing music", "ambient music",
            "study music", "concentration music",
            "storytelling music", "instrumental ambient",
        ],
    },
    {
        "key": "shadow_ink",
        "name": "Shadow & Ink",
        "synth": "shadow_ink",
        "emoji": "\U0001F58B️",  # 🖋️
        "short_title": "Shadow & Ink \U0001F58B️ Moody Gothic Writing Ambient #shorts",
        "long_title": "Shadow & Ink \U0001F58B️ 14 Minute Moody Gothic Writing Ambient with Rain | Dark Ambient Visualizer",
        "description": (
            "A moody minor-key pad under a soft rain wash — gothic writing "
            "ambience for dark fiction, journaling, and quiet focus."
        ),
        "tags": [
            "writing music", "gothic music", "dark academia music",
            "rain ambience", "writing ambient", "focus music", "study music",
            "dark ambient", "rainy day music",
            "concentration music", "moody ambient",
        ],
    },
    {
        "key": "calm_the_night",
        "name": "Calm the Night",
        "synth": "sleeping",
        "tone": "432", "beat": "delta", "beat_type": "binaural",
        "emoji": "\U0001F319",  # 🌙
        "short_title": "Calm the Night \U0001F319 432 Hz Anxiety Relief & Sleep #shorts",
        "long_title": "Calm the Night \U0001F319 14 Minute 432 Hz Anxiety Relief & Deep Sleep Soundscape | Dark Ambient Visualizer",
        "description": (
            "A 432 Hz tuned soundscape with gentle delta-rate binaural beats "
            "over warm sleep music, for insomnia relief and deep, restorative "
            "sleep. Use headphones for the binaural effect."
        ),
        "tags": [
            "432 hz", "anxiety relief music", "sleep music", "deep sleep music",
            "binaural beats sleep", "delta waves", "insomnia relief music",
            "meditation music", "healing frequency",
            "calm music", "relaxing sleep music",
        ],
    },
    {
        "key": "slumber_of_ash",
        "name": "Slumber of Ash",
        "synth": "sleeping",
        "tone": "246.9", "beat": "theta", "beat_type": "binaural",
        "emoji": "\U0001F4A4",  # 💤
        "short_title": "Slumber of Ash \U0001F4A4 Restorative Sleep & Binaural Beats #shorts",
        "long_title": "Slumber of Ash \U0001F4A4 14 Minute Restorative Sleep Music with Binaural Beats | Dark Ambient Visualizer",
        "description": (
            "A dark, warm sleep soundscape layered with gentle binaural "
            "beats for deep, restorative rest. Use headphones for the "
            "binaural effect."
        ),
        "tags": [
            "deep sleep music", "binaural beats sleep", "restorative sleep",
            "sleep music", "brain waves", "insomnia relief music",
            "meditation music", "relaxing music",
            "healing music", "calm sleep music",
        ],
    },
    {
        "key": "ethereal_ruins",
        "name": "Ethereal Ruins",
        "synth": "ethereal_ruins",
        "emoji": "\U0001FAA8",  # 🪨
        "short_title": "Ethereal Ruins \U0001FAA8 Epic Dark Fantasy Ambience #shorts",
        "long_title": "Ethereal Ruins \U0001FAA8 14 Minute Epic Dark Fantasy Ambience for Focus & Study | Dark Ambient Visualizer",
        "description": (
            "Layered pads and a soft, sparse melodic lead conjure an ancient, "
            "twilight-fog atmosphere — epic dark fantasy backdrop for focus, "
            "study, or tabletop gaming sessions."
        ),
        "tags": [
            "fantasy music", "dark ambient", "epic ambient music",
            "cinematic ambient", "dnd music", "study music", "focus music",
            "dark academia music", "atmospheric music",
            "medieval fantasy music", "ambient music",
        ],
    },
    {
        "key": "ember_solitude",
        "name": "Ember Solitude",
        "synth": "ember_solitude",
        "emoji": "\U0001F3D5️",  # 🏕️
        "short_title": "Ember Solitude \U0001F3D5️ Melancholic Dark Ambient #shorts",
        "long_title": "Ember Solitude \U0001F3D5️ 14 Minute Melancholic Dark Ambient for Quiet Reflection | Dark Ambient Visualizer",
        "description": (
            "A slow, reverb-drenched pad with a soft granular shimmer — "
            "melancholic, reflective dark ambient for quiet contemplation."
        ),
        "tags": [
            "dark ambient", "melancholic music", "ambient music",
            "reflective music", "cinematic ambient", "focus music",
            "study music", "atmospheric music",
            "calm dark music", "instrumental ambient", "meditation music",
        ],
    },
    {
        "key": "markov_chamber",
        "name": "Markov Chamber",
        "synth": "markov_chamber",
        "emoji": "\U0001F52E",  # 🔮
        "short_title": "Markov Chamber \U0001F52E Endless Generative Focus Music #shorts",
        "long_title": "Markov Chamber \U0001F52E 14 Minute Endless Generative Focus Soundtrack | Dark Ambient Visualizer",
        "description": (
            "A generative, ever-shifting melody that never repeats exactly "
            "the same way twice — an endless, non-distracting soundtrack for "
            "deep focus and study."
        ),
        "tags": [
            "generative music", "focus music", "study music",
            "concentration music", "ambient music", "deep work music",
            "productivity music", "dark academia music",
            "instrumental focus music", "coding music", "ambient focus music",
        ],
    },
    {
        "key": "ash_rain_wind",
        "name": "Ash Rain & Wind",
        "synth": "ash_rain_wind",
        "emoji": "\U0001F32B️",  # 🌫️
        "short_title": "Ash Rain & Wind \U0001F32B️ Dark Nature Noise for Relaxation #shorts",
        "long_title": "Ash Rain & Wind \U0001F32B️ 14 Minute Dark Nature Noise for Relaxation, Focus & Sleep | Dark Ambient Visualizer",
        "description": (
            "Filtered wind and soft rain woven into an organic dark noise "
            "bed — for relaxation, background focus, and sleep."
        ),
        "tags": [
            "rain and wind sounds", "nature noise", "relaxing noise",
            "sleep sounds", "focus noise", "wind sounds", "rain sounds",
            "ambient noise", "calming noise",
            "dark nature sounds", "study noise",
        ],
    },
    {
        "key": "black_hole",
        "name": "Black Hole Resonance",
        "synth": "black_hole",
        "emoji": "\U000026AB",  # ⚫
        "short_title": "Black Hole Resonance \U000026AB Ultra Deep Sub Bass Ambient #shorts",
        "long_title": "Black Hole Resonance \U000026AB 14 Minute Ultra Deep Sub Bass Dark Sci-Fi Ambient | Dark Ambient Visualizer",
        "description": (
            "Ultra-deep sub-bass tones for a dark, sci-fi ambient atmosphere "
            "— best felt on a subwoofer or headphones. For deep focus, "
            "meditation, or sleep."
        ),
        "tags": [
            "sub bass", "dark ambient", "sci fi ambient", "drone music",
            "deep bass music", "space ambient", "meditation music",
            "focus music", "sleep music", "ambient drone",
            "cosmic music",
        ],
    },
    {
        "key": "monastic_echoes",
        "name": "Monastic Echoes",
        "synth": "monastic_echoes",
        "emoji": "\U0001F6D5",  # 🛕
        "short_title": "Monastic Echoes \U0001F6D5 Sacred Dark Chant Ambient #shorts",
        "long_title": "Monastic Echoes \U0001F6D5 14 Minute Sacred Dark Chant Ambient for Deep Focus & Meditation | Dark Ambient Visualizer",
        "description": (
            "Deep, choir-like drones washed in cathedral reverb — sacred, "
            "gothic ambience for deep focus, meditation, and contemplation."
        ),
        "tags": [
            "gothic ambient", "sacred music", "dark ambient", "choir ambient",
            "meditation music", "cathedral ambient", "focus music",
            "dark academia music", "ambient chant",
            "atmospheric music", "contemplative music",
        ],
    },
    {
        "key": "obsidian_tower",
        "name": "The Obsidian Tower",
        "synth": "obsidian_tower",
        "emoji": "\U0001F5FC",  # 🗼
        "short_title": "The Obsidian Tower \U0001F5FC Dark Academia Study Session #shorts",
        "long_title": "The Obsidian Tower \U0001F5FC 14 Minute Dark Academia Study Ambient with Vinyl Crackle | Dark Ambient Visualizer",
        "description": (
            "A dark organ-like pad with soft vinyl-crackle texture — heavy "
            "focus ambience for dark academia study sessions and deep work."
        ),
        "tags": [
            "dark academia music", "study music", "focus music",
            "vinyl crackle music", "ambient study music", "concentration music",
            "gothic ambient", "deep work music",
            "instrumental study music", "dark ambient", "productivity music",
        ],
    },
]

BRAND_NAME = "Aether & Ash"
BRAND_TAGLINE = "Dark Ambient. Deep Focus."

# Broad, high-value niche tags appended to every video AFTER the theme-specific
# ones. make_metadata dedupes and packs tags up to YouTube's 500-char limit.
GLOBAL_TAGS = [
    "dark ambient music", "drone music", "study music", "deep focus music",
    "dark academia music", "ambient music for writing",
    "sleep music", "binaural beats", "concentration music",
    "atmospheric music", "cinematic ambient", "meditation music",
    "calm music", "background music for studying", "generative music",
    "ambient visualizer", "dark ambient animation", "generative art",
    "aesthetic background video", "screensaver visuals",
]

# Natural-language phrase for the description (kept short and readable).
PERFECT_FOR = "deep work, studying, dark academia, writing, meditation, and sleep"

# Auto-playlists: every long-form is added to its sub-niche playlist on upload.
PLAYLISTS = {
    "dark_drone": {
        "title": "Dark Drone & Deep Bass \U0001F311",
        "description": "Deep sub-bass drones and dark ambient tones for "
                       "focus, meditation, and sleep.",
        "themes": ["void_drone", "abyssal_silence", "black_hole"],
    },
    "generative_study": {
        "title": "Focus & Generative Study \U0001F3AF",
        "description": "Generative and ambient focus tracks for deep work, "
                       "study, and concentration.",
        "themes": ["ember_focus", "cosmic_drift", "markov_chamber"],
    },
    "writing_ambient": {
        "title": "Writing & Dark Academia Ambient \U0001FAB6",
        "description": "Moody, atmospheric ambient music for writing, dark "
                       "academia study sessions, and deep focus.",
        "themes": ["creative_flow", "shadow_ink", "monastic_echoes", "obsidian_tower"],
    },
    "sleep_meditation": {
        "title": "Dark Ambient Sleep & Meditation \U0001F319",
        "description": "Dark, warm soundscapes and binaural beats for "
                       "anxiety relief, meditation, and deep sleep.",
        "themes": ["calm_the_night", "slumber_of_ash"],
    },
    "cinematic": {
        "title": "Cinematic Dark Atmosphere \U0001F3AC",
        "description": "Epic, cinematic dark ambient soundscapes for focus, "
                       "study, and quiet reflection.",
        "themes": ["ethereal_ruins", "ember_solitude"],
    },
    "noise": {
        "title": "Ash Noise & Atmosphere \U0001F32B️",
        "description": "Filtered noise and nature textures for relaxation, "
                       "background focus, and sleep.",
        "themes": ["ash_rain_wind"],
    },
}


def synth_args(theme: dict) -> list:
    """generate_theme_audio.py CLI flags for a theme's frequency layers and tone
    shaping. Same contract as scripts/themes.py -- single source of truth so
    videos render identical audio to what the metadata describes."""
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
    """The playlist definition a theme belongs to, or None."""
    for p in PLAYLISTS.values():
        if theme_key in p["themes"]:
            return p
    return None

# Appended to every description. Truthful, non-AI disclosure: this channel's
# audio is 100% algorithmic sound synthesis (numpy/scipy DSP), no samples and
# no AI generation -- see references in scripts/generate_theme_audio.py.
DESCRIPTION_FOOTER = (
    "\n\n— {brand} — {tagline}\n\n"
    "\U0001F3A7 Best experienced with headphones or a good speaker at a low volume.\n"
    "\U0001F3B5 All music is composed algorithmically with original sound-synthesis "
    "software — no samples, no loops, no AI generation.\n\n"
    "Please note: this content is for ambience and focus only and is not a "
    "substitute for medical or mental-health advice."
)


def theme_for_date(d: date | None = None) -> dict:
    """Return the active theme dict for the given date (defaults to today)."""
    d = d or date.today()
    idx = (d - ANCHOR).days % len(THEMES)
    return THEMES[idx]


def daily_selection(d: date | None = None, count: int = DAILY_COUNT) -> list[dict]:
    """Return `count` themes for the given date (sliding window, cycles
    through the whole library over successive days)."""
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
    from datetime import timedelta
    today = date.today()
    for i in range(len(THEMES)):
        t = theme_for_date(today + timedelta(days=i))
        print(f"{today + timedelta(days=i)}  ->  {t['key']:16s}  {t['name']}")
