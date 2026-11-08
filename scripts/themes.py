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

# Long-form length in hours, matched to what wins per sub-niche on YouTube:
#   - Solfeggio COMBOS  -> 3h  : the viral combo format is a short binge series
#   - Solo FREQUENCIES  -> 8h  : solid length, faster/safer render than 10h
#   - Nature / music     -> 10h : all-night ambient watch-time
# QC allows 2-12h and checks the actual render is close to the theme's target.
# (10h max, not 12h — YouTube rejected exactly-12h uploads as "too long".)
LONG_HOURS_DEFAULT = 10
LONG_HOURS_MIN = 2      # QC floor for a "long-form"
LONG_HOURS = {
    "solfeggio_heal": 3, "solfeggio_spirit": 3, "solfeggio_deepsleep": 3,
    "528hz_sleep": 8, "432hz_relax": 8, "delta_sleep": 8, "gamma_focus": 8,
    "om_136": 8, "963hz_awakening": 8, "852hz_intuition": 8, "741hz_clarity": 8,
    # rain, waterfall, forest, sleeping, indian, romantic, romantic_night,
    # rain_drops -> LONG_HOURS_DEFAULT (10)
}


def long_hours_for(theme_key: str) -> int:
    """Content-matched long-form duration for a theme (falls back to 10h)."""
    return LONG_HOURS.get(theme_key, LONG_HOURS_DEFAULT)

# Daily publishing plan: 1 long-form + 1 Short/day (reduced from 6+6 -- less
# upload volume, still a different, unique music each day via the rotation).
# All uploads go through the app's ONE Cloud project (YouTube API policy: one
# project per API client; extra projects for quota get suspended).
LONGS_PER_DAY = 1
SHORTS_PER_DAY = 1
DAILY_COUNT = LONGS_PER_DAY + SHORTS_PER_DAY

# Cadence (scripts/channel_kit.py): one Short every day, one feature every
# 4 days. FEATURE_DAY_OFFSET staggers which day of the 4 this channel's
# feature lands on, so the channels don't all post long videos together.
# (LONGS_PER_DAY / SHORTS_PER_DAY above only describe the old daily
# rotation, used to continue its Vol. numbers.)
FEATURE_DAY_OFFSET = 0

# Ordered rotation. `synth` names a function in generate_theme_audio.py.
THEMES = [
    {
        "key": "rain",
        "name": "Rainy with Calm Music",
        "synth": "rain",
        "emoji": "\U0001F327️",  # 🌧️
        "short_title": "Fall Asleep Fast to Rain \U0001F327️ Calm Rain Sounds for Deep Sleep #shorts",
        "long_title": "Rain Sounds for Sleeping \U0001F327️ {hours} Hours Deep Sleep Music, Rain & Thunder | Dark Screen",
        "description": (
            "Gentle rainfall, distant thunder, and soft ambient pads to help you fall "
            "asleep fast and stay asleep. Let the calm rain wash the day away and drift "
            "into deep, restful sleep."
        ),
        "tags": [
            "rain sounds for sleeping", "sleep music", "rain sounds", "deep sleep music",
            "relaxing rain", "rain and thunder sounds", "rain sounds dark screen",
            "dark screen", "calm music", "study music", "meditation music",
            "insomnia relief music", "white noise", "rain ambience", "sleep sounds",
        ],
    },
    {
        "key": "waterfall",
        "name": "Waterfall Music",
        "synth": "waterfall",
        "emoji": "\U0001F4A7",  # 💧
        "short_title": "Soothing Waterfall Sounds \U0001F4A7 Relax & Sleep in 59 Seconds #shorts",
        "long_title": "Waterfall Sounds \U0001F4A7 {hours} Hours of Flowing Water for Sleep & Focus | Dark Screen",
        "description": (
            "Flowing water streams and cascading falls blended with soothing natural "
            "harmony. Perfect for deep sleep, relaxation, meditation, and focused study."
        ),
        "tags": [
            "waterfall sounds", "water sounds for sleeping", "sleep music",
            "relaxing water sounds", "nature sounds", "deep sleep music",
            "waterfall white noise", "dark screen", "focus music", "meditation music",
            "study music", "calming water sounds", "stress relief music", "sleep sounds",
        ],
    },
    {
        "key": "forest",
        "name": "Natural Green Forest Sounds",
        "synth": "forest",
        "emoji": "\U0001F332",  # 🌲
        "short_title": "Peaceful Forest Sounds \U0001F332 Birds, Water Drops & Calm #shorts",
        "long_title": "Forest Sounds \U0001F332 {hours} Hours of Birdsong & Gentle Nature for Sleep | Dark Screen",
        "description": (
            "Gentle water drops, natural bird chirps, and soft wind rustling through the "
            "trees. Immerse yourself in a calm green forest for restful sleep, relaxation, "
            "and peaceful focus."
        ),
        "tags": [
            "forest sounds", "nature sounds for sleeping", "birds singing", "sleep music",
            "relaxing nature sounds", "deep sleep music", "forest ambience", "birdsong",
            "dark screen", "meditation music", "calming nature sounds", "study music",
            "forest white noise", "sleep sounds",
        ],
    },
    {
        "key": "sleeping",
        "name": "Sleeping Music",
        "synth": "sleeping",
        "emoji": "\U0001F319",  # 🌙
        "short_title": "Deep Sleep Music \U0001F319 Drift Off in Under a Minute #shorts",
        "long_title": "Deep Sleep Music \U0001F319 {hours} Hours Ambient Drone for Deep Sleep | Dark Screen",
        "description": (
            "Deep ambient drone and slow evolving chords for peaceful, restorative sleep. "
            "Soft, calming tones designed to quiet the mind and guide you into deep rest."
        ),
        "tags": [
            "sleep music", "deep sleep music", "relaxing sleep music",
            "calm music for sleeping", "meditation music", "ambient sleep music",
            "dark screen sleep", "sleep aid", "insomnia relief music", "soothing music",
            "healing music", "stress relief music", "spa music", "sleep sounds",
        ],
    },
    {
        "key": "indian",
        "name": "Indian Sleep Music",
        "synth": "indian",
        "emoji": "\U0001FAB7",  # 🪷
        "short_title": "Indian Flute Sleep Music \U0001FAB7 Deep Sleep in 59s #shorts",
        "long_title": "Indian Sleep Music \U0001FAB7 {hours} Hours Tanpura & Flute for Deep Sleep | Dark Screen",
        "description": (
            "Soothing Indian classical sleep music: a gentle tanpura drone with soft "
            "bansuri-style flute in a calming raga. Let the meditative sound quiet your "
            "mind and guide you into deep, restful sleep."
        ),
        "tags": [
            "indian sleep music", "tanpura meditation", "indian flute music",
            "raga for sleep", "meditation music", "deep sleep music",
            "relaxing indian music", "indian classical music", "yoga music", "spa music",
            "healing music", "calming flute music", "dark screen", "sleep sounds",
        ],
    },
    {
        "key": "romantic",
        "name": "Romantic Love Music",
        "synth": "romantic",
        "emoji": "\U0001F495",  # 💕
        "short_title": "Romantic Love Music \U0001F495 Warm & Soothing #shorts",
        "long_title": "Romantic Music \U0001F495 {hours} Hours Warm Instrumental Love Songs | Dark Screen",
        "description": (
            "Warm, tender instrumental love music with lush chords and a soft melody. "
            "Perfect for a romantic evening, a candle-lit dinner, relaxing together, or "
            "simply unwinding in a gentle, heartfelt mood."
        ),
        "tags": [
            "romantic music", "romantic instrumental", "relaxing romantic music",
            "calm romantic music", "dinner music", "date night music",
            "background music", "soft piano music", "mood music", "relaxing music",
            "romantic background music", "instrumental music", "dark screen",
        ],
    },
    {
        "key": "romantic_night",
        "name": "Romantic Night Music",
        "synth": "romantic_night",
        "emoji": "\U0001F339",  # 🌹
        "short_title": "Romantic Night Music \U0001F339 Smooth & Relaxing #shorts",
        "long_title": "Romantic Night Music \U0001F339 {hours} Hours Smooth Relaxing Instrumental | Dark Screen",
        "description": (
            "Slow, smooth, and warm instrumental music for a relaxing romantic evening. "
            "Mellow chords and a soft melody set a calm, cozy mood — perfect for a quiet "
            "dinner, unwinding after a long day, or peaceful time together."
        ),
        "tags": [
            "romantic music", "relaxing romantic music", "romantic instrumental",
            "smooth relaxing music", "date night music", "dinner music",
            "calm background music", "evening music", "soft instrumental music",
            "mood music", "chill music", "relaxing music", "dark screen",
        ],
    },
    {
        "key": "gamma_focus",
        "name": "40 Hz Gamma Focus",
        "synth": "none",
        "tone": "200", "beat": "gamma", "beat_type": "binaural",
        "emoji": "\U0001F9E0",  # 🧠
        "short_title": "40 Hz Gamma Focus Music \U0001F9E0 Study & Concentration #shorts",
        "long_title": "40 Hz Gamma Binaural Beats \U0001F9E0 {hours} Hours Focus, Study & Concentration | Dark Screen",
        "description": (
            "40 Hz gamma binaural beats to support deep focus, studying, reading, and "
            "concentration. Use headphones for the binaural effect. Dim, slow-moving "
            "visuals, distraction-free."
        ),
        "tags": [
            "40 hz", "gamma binaural beats", "binaural beats focus", "focus music",
            "concentration music", "study music", "deep focus", "binaural beats study",
            "brain waves", "productivity music", "gamma waves", "dark screen",
        ],
    },
    {
        "key": "528hz_sleep",
        "name": "528 Hz Sleep Music",
        "synth": "sleeping",
        "tone": "528", "beat": "delta", "beat_type": "binaural",
        "emoji": "\U00002728",  # ✨
        "short_title": "528 Hz Sleep Music \U00002728 Solfeggio Deep Sleep #shorts",
        "long_title": "528 Hz Sleep Music \U00002728 {hours} Hours Solfeggio Tone for Deep Sleep | Dark Screen",
        "description": (
            "528 Hz Solfeggio tone blended with warm sleep music and gentle delta-rate "
            "binaural beats for deep, restful sleep. Use headphones for the binaural "
            "effect. Dim, slow-moving visuals."
        ),
        "tags": [
            "528 hz", "528 hz music", "solfeggio frequencies", "528 hz sleep",
            "sleep music", "deep sleep music", "solfeggio 528", "healing frequency",
            "meditation music", "delta waves", "binaural beats sleep", "dark screen",
        ],
    },
    {
        "key": "delta_sleep",
        "name": "Delta Waves Sleep",
        "synth": "sleeping",
        "tone": "110", "beat": "delta", "beat_type": "binaural",
        "emoji": "\U0001F4A4",  # 💤
        "short_title": "Delta Waves Sleep \U0001F4A4 Binaural Beats for Deep Sleep #shorts",
        "long_title": "Delta Waves \U0001F4A4 {hours} Hours Binaural Beats for Deep Sleep | Dark Screen",
        "description": (
            "Deep delta-wave binaural beats with warm ambient sleep music to help you "
            "fall into deep, restorative sleep. Use headphones for the binaural effect. "
            "Dim, slow-moving visuals."
        ),
        "tags": [
            "delta waves", "binaural beats sleep", "deep sleep music", "delta waves sleep",
            "sleep music", "binaural beats", "brain waves", "meditation music",
            "insomnia relief music", "relaxing music", "dark screen", "healing music",
        ],
    },
    {
        "key": "432hz_relax",
        "name": "432 Hz Relaxing Music",
        "synth": "sleeping",
        "tone": "432",
        "emoji": "\U0001F338",  # 🌸
        "short_title": "432 Hz Music \U0001F338 Relaxing 432 Hz for Sleep #shorts",
        "long_title": "432 Hz Music \U0001F338 {hours} Hours Relaxing 432 Hz for Sleep & Calm | Dark Screen",
        "description": (
            "Warm, relaxing music tuned to 432 Hz for sleep, calm, and meditation. "
            "Soothing tones to help unwind the mind and body. Dim, slow-moving visuals."
        ),
        "tags": [
            "432 hz", "432 hz music", "432 hz sleep", "relaxing music", "sleep music",
            "meditation music", "calm music", "healing frequency", "432 hz meditation",
            "deep sleep music", "dark screen", "spa music",
        ],
    },
    {
        "key": "rain_drops",
        "name": "Soft Rain & Water Drops",
        "synth": "rain_drops",
        "emoji": "\U0001F4A7",  # 💧
        "short_title": "Soft Rain & Water Drops \U0001F4A7 Gentle Rain Sounds for Sleep #shorts",
        "long_title": "Soft Rain & Water Drops \U0001F4A7 {hours} Hours Gentle Rain for Sleep, No Thunder | Dark Screen",
        "description": (
            "Soft, gentle rainfall with slow water drops falling one by one — no "
            "thunder, no music, just calm rain to help you relax, focus, and fall "
            "asleep. Let the quiet patter and gentle drips soothe you into deep, "
            "restful sleep. Dim, slow-moving visuals."
        ),
        "tags": [
            "soft rain", "gentle rain", "rain sounds for sleeping", "water drops",
            "rain without thunder", "rain no thunder", "light rain sounds",
            "rain sounds dark screen", "calm rain", "relaxing rain", "sleep sounds",
            "rain ambience", "deep sleep music", "dark screen", "white noise",
        ],
    },
    # --- Solfeggio combos & high tones: rendered soft (pure tone, no bright
    # harmonics) + dark reverb + high-tone de-emphasis (tone_tilt) so 741/852/963
    # sit gently under the warm 'sleeping' bed instead of piercing. ---
    {
        "key": "solfeggio_heal",
        "name": "432 528 741 Hz Healing Sleep",
        "synth": "sleeping",
        "tone": "432,528,741", "tone_soft": True, "reverb": 0.4, "tone_tilt": 2,
        "tone_gain": 0.11,
        "emoji": "\U0001F319",  # 🌙
        "short_title": "432+528+741 Hz \U0001F319 Deep Healing Sleep Music #shorts",
        "long_title": "432 Hz + 528 Hz + 741 Hz \U0001F319 {hours} Hours Deep Healing Sleep Music, Calm & Anxiety Relief | Dark Screen",
        "description": (
            "A gentle blend of 432 Hz, 528 Hz and 741 Hz Solfeggio tones woven into "
            "warm sleep music for deep rest, calm, and anxiety relief. Soft and "
            "soothing for a peaceful night's sleep. Dim, slow-moving visuals."
        ),
        "tags": [
            "432 hz", "528 hz", "741 hz", "solfeggio frequencies", "solfeggio sleep",
            "deep sleep music", "healing frequency", "anxiety relief music",
            "meditation music", "calm music", "sleep music", "dark screen",
        ],
    },
    {
        "key": "solfeggio_spirit",
        "name": "528 741 963 Hz Body & Spirit",
        "synth": "sleeping",
        "tone": "528,741,963", "tone_soft": True, "reverb": 0.4, "tone_tilt": 3,
        "tone_gain": 0.11,
        "emoji": "\U00002728",  # ✨
        "short_title": "528+741+963 Hz \U00002728 Body & Spirit Healing #shorts",
        "long_title": "528 Hz + 741 Hz + 963 Hz \U00002728 {hours} Hours Body & Spirit Healing Music, Deep Sleep & Positive Energy | Dark Screen",
        "description": (
            "528 Hz, 741 Hz and 963 Hz Solfeggio tones layered into calm sleep music "
            "for deep rest and positive energy. High tones kept soft and subtle. "
            "Dim, slow-moving visuals."
        ),
        "tags": [
            "528 hz", "741 hz", "963 hz", "solfeggio frequencies", "positive energy",
            "deep sleep music", "healing frequency", "meditation music",
            "spiritual music", "sleep music", "calm music", "dark screen",
        ],
    },
    {
        "key": "solfeggio_deepsleep",
        "name": "Solfeggio + Delta Deep Sleep",
        "synth": "sleeping",
        "tone": "528,741,963", "tone_soft": True, "reverb": 0.4, "tone_tilt": 3,
        "tone_gain": 0.11, "beat": "delta", "beat_type": "isochronic",
        "emoji": "\U0001F634",  # 😴
        "short_title": "Solfeggio + Delta Waves \U0001F634 Deep Sleep Music #shorts",
        "long_title": "Solfeggio + Delta Waves \U0001F634 {hours} Hours Deep Sleep Meditation, Fall Asleep Fast | Dark Screen",
        "description": (
            "Soft Solfeggio tones with gentle delta-rate pulses and warm sleep music "
            "to help you fall asleep fast and sleep deeply through the night. Works "
            "on speakers or headphones. Dim, slow-moving visuals."
        ),
        "tags": [
            "delta waves", "solfeggio frequencies", "deep sleep music", "fall asleep fast",
            "sleep meditation", "sleep music", "healing frequency", "meditation music",
            "insomnia relief music", "relaxing music", "dark screen", "brain waves",
        ],
    },
    {
        "key": "om_136",
        "name": "OM 136.1 Hz Meditation",
        "synth": "sleeping",
        "tone": "136.1", "tone_soft": True, "reverb": 0.35, "tone_gain": 0.14,
        "emoji": "\U0001F549",  # 🕉️
        "short_title": "OM 136.1 Hz \U0001F549 Deep Meditation & Inner Peace #shorts",
        "long_title": "OM 136.1 Hz \U0001F549 {hours} Hours Tibetan Om Frequency for Deep Meditation & Inner Peace | Dark Screen",
        "description": (
            "The deep OM frequency (136.1 Hz) with warm ambient music for meditation, "
            "inner peace, and calm. A grounding, soothing tone to quiet the mind. "
            "Dim, slow-moving visuals."
        ),
        "tags": [
            "om", "136 hz", "om frequency", "tibetan meditation", "meditation music",
            "inner peace", "deep meditation", "chanting", "calm music", "sleep music",
            "healing frequency", "dark screen",
        ],
    },
    {
        "key": "963hz_awakening",
        "name": "963 Hz Crown Chakra",
        "synth": "sleeping",
        "tone": "963", "tone_soft": True, "reverb": 0.4, "tone_tilt": 2,
        "tone_gain": 0.11,
        "emoji": "\U0001F30C",  # 🌌
        "short_title": "963 Hz \U0001F30C Crown Chakra Meditation Music #shorts",
        "long_title": "963 Hz \U0001F30C {hours} Hours Crown Chakra Music for Spiritual Awakening & Deep Meditation | Dark Screen",
        "description": (
            "The 963 Hz crown-chakra Solfeggio tone kept soft and subtle over warm "
            "meditation music for spiritual calm and deep relaxation. Dim, slow-moving visuals."
        ),
        "tags": [
            "963 hz", "crown chakra", "solfeggio frequencies", "spiritual music",
            "meditation music", "deep meditation", "963 hz meditation", "calm music",
            "sleep music", "healing frequency", "dark screen", "chakra healing",
        ],
    },
    {
        "key": "852hz_intuition",
        "name": "852 Hz Third Eye",
        "synth": "sleeping",
        "tone": "852", "tone_soft": True, "reverb": 0.4, "tone_tilt": 2,
        "tone_gain": 0.11,
        "emoji": "\U0001F52E",  # 🔮
        "short_title": "852 Hz \U0001F52E Third Eye Awakening Meditation #shorts",
        "long_title": "852 Hz \U0001F52E {hours} Hours Awaken Intuition, Third Eye Meditation Music for Calm | Dark Screen",
        "description": (
            "The 852 Hz Solfeggio tone, gentle and soft, over calm meditation music "
            "to awaken intuition and settle the mind. Dim, slow-moving visuals."
        ),
        "tags": [
            "852 hz", "third eye", "intuition", "solfeggio frequencies", "meditation music",
            "852 hz meditation", "spiritual music", "calm music", "sleep music",
            "healing frequency", "dark screen", "chakra healing",
        ],
    },
    {
        "key": "rooftop_rain",
        "name": "Rooftop Rain & Gentle Thunder",
        "synth": "rain",
        "emoji": "\U0001F3E0",  # 🏠
        "short_title": "Rain on Rooftop \U0001F3E0 Cozy Rain & Soft Thunder #shorts",
        "long_title": "Rain on Rooftop \U0001F3E0 {hours} Hours Cozy Rain & Gentle Thunder for Sleep | Dark Screen",
        "description": (
            "Rain falling softly on a rooftop with gentle, distant thunder. A cozy, "
            "intimate atmosphere to help you relax, feel safe, and drift into deep, "
            "restful sleep. Dim, slow-moving visuals."
        ),
        "tags": [
            "rain on roof", "rooftop rain", "rain sounds for sleeping", "cozy rain",
            "gentle thunder", "rain and thunder", "rain on rooftop", "sleep sounds",
            "rain sounds dark screen", "relaxing rain", "deep sleep music",
            "rain ambience", "calm rain", "dark screen", "asmr rain",
        ],
    },
    {
        "key": "741hz_clarity",
        "name": "741 Hz Cleanse & Clarity",
        "synth": "sleeping",
        "tone": "741", "tone_soft": True, "reverb": 0.4, "tone_tilt": 2,
        "tone_gain": 0.11,
        "emoji": "\U0001F343",  # 🍃
        "short_title": "741 Hz \U0001F343 Cleanse & Clarity Meditation #shorts",
        "long_title": "741 Hz \U0001F343 {hours} Hours Cleanse & Clarity, Let Go of Stress | Calm Focus Music | Dark Screen",
        "description": (
            "The 741 Hz Solfeggio tone kept soft over calm music to cleanse the mind, "
            "release stress, and support clarity and focus. Dim, slow-moving visuals."
        ),
        "tags": [
            "741 hz", "cleanse", "clarity", "solfeggio frequencies", "stress relief",
            "741 hz meditation", "focus music", "meditation music", "calm music",
            "sleep music", "healing frequency", "dark screen",
        ],
    },
    {
        "key": "ocean",
        "name": "Ocean Waves",
        "synth": "ocean",
        "emoji": "\U0001F30A",  # 🌊
        "short_title": "Ocean Waves for Sleep \U0001F30A Relaxing Sea Sounds #shorts",
        "long_title": "Ocean Waves \U0001F30A {hours} Hours Relaxing Sea Sounds for Deep Sleep | Dark Screen",
        "description": (
            "Gentle ocean waves rolling onto the shore to help you relax and drift into "
            "deep sleep. Soothing sea sounds for rest, calm, and focus. Dim, slow-moving visuals."
        ),
        "tags": [
            "ocean sounds", "ocean waves", "sea sounds for sleeping", "relaxing ocean",
            "ocean waves sleep", "wave sounds", "beach sounds", "deep sleep music",
            "dark screen", "white noise", "nature sounds", "calming ocean", "sleep sounds",
        ],
    },
    {
        "key": "fireplace",
        "name": "Crackling Fireplace",
        "synth": "fireplace",
        "emoji": "\U0001F525",  # 🔥
        "short_title": "Crackling Fireplace \U0001F525 Cozy Fire Sounds for Sleep #shorts",
        "long_title": "Fireplace Sounds \U0001F525 {hours} Hours Crackling Fire for Sleep, Relax & Study | Dark Screen",
        "description": (
            "The cozy crackle of a warm fireplace to help you relax, sleep, read, or "
            "study. Soothing crackling fire sounds all night. Dim, slow-moving visuals."
        ),
        "tags": [
            "fireplace sounds", "crackling fire", "fireplace", "fire sounds",
            "cozy fireplace", "fireplace ambience", "relaxing fire", "campfire sounds",
            "sleep sounds", "study music", "dark screen", "white noise", "fire crackling",
        ],
    },
    {
        "key": "thunderstorm",
        "name": "Thunderstorm",
        "synth": "thunderstorm",
        "emoji": "\U000026C8️",  # ⛈️
        "short_title": "Thunderstorm for Sleep \U000026C8️ Heavy Rain & Thunder #shorts",
        "long_title": "Thunderstorm Sounds \U000026C8️ {hours} Hours Heavy Rain & Thunder for Sleep | Dark Screen",
        "description": (
            "Heavy rain and rolling thunder for deep, cozy sleep. A powerful, calming "
            "storm to relax the mind and drift away. Dim, slow-moving visuals."
        ),
        "tags": [
            "thunderstorm sounds", "thunder and rain", "heavy rain sounds", "storm sounds",
            "thunderstorm for sleeping", "rain and thunder", "thunder sounds",
            "deep sleep music", "dark screen", "relaxing storm", "sleep sounds", "rain sounds",
        ],
    },
    {
        "key": "brown_noise",
        "name": "Brown Noise",
        "synth": "brown_noise",
        "emoji": "\U0001F7EB",  # 🟫
        "short_title": "Brown Noise for Sleep & Focus \U0001F7EB #shorts",
        "long_title": "Brown Noise \U0001F7EB {hours} Hours for Deep Sleep, Focus & Relaxation | Dark Screen",
        "description": (
            "Deep, smooth brown noise to help you fall asleep fast, focus, and block out "
            "distractions. Great for sleep, study, and concentration. Dim, slow-moving visuals."
        ),
        "tags": [
            "brown noise", "brown noise for sleeping", "brown noise sleep",
            "brown noise focus", "brown noise study", "deep brown noise", "focus music",
            "white noise", "study music", "sleep sounds", "dark screen", "relaxing noise",
        ],
    },
    {
        "key": "white_noise",
        "name": "White Noise",
        "synth": "white_noise",
        "emoji": "\U000026AA",  # ⚪
        "short_title": "White Noise for Sleep \U000026AA Baby Sleep & Focus #shorts",
        "long_title": "White Noise \U000026AA {hours} Hours for Sleep, Baby Sleep & Focus | Dark Screen",
        "description": (
            "Soothing white noise to help you and your baby sleep, and to stay focused "
            "while studying or working. Blocks out distractions all night. Dim, slow-moving visuals."
        ),
        "tags": [
            "white noise", "white noise for sleeping", "white noise baby",
            "white noise sleep", "baby sleep sounds", "focus music", "study music",
            "sleep sounds", "dark screen", "relaxing noise", "soothing white noise",
        ],
    },
    {
        "key": "pink_noise",
        "name": "Pink Noise",
        "synth": "pink_noise",
        "emoji": "\U0001FA77",  # 🩷
        "short_title": "Pink Noise for Deep Sleep \U0001FA77 #shorts",
        "long_title": "Pink Noise \U0001FA77 {hours} Hours for Deep Sleep & Relaxation | Dark Screen",
        "description": (
            "Balanced, gentle pink noise to help you fall into deep, restful sleep and "
            "relax the mind. Softer than white noise. Dim, slow-moving visuals."
        ),
        "tags": [
            "pink noise", "pink noise for sleeping", "pink noise sleep",
            "pink noise deep sleep", "sleep sounds", "white noise", "relaxing noise",
            "focus music", "dark screen", "soothing noise", "calming noise",
        ],
    },
    {
        "key": "wind",
        "name": "Wind Sounds",
        "synth": "wind",
        "emoji": "\U0001F32C️",  # 🌬️
        "short_title": "Wind Sounds for Sleep \U0001F32C️ Calming Wind #shorts",
        "long_title": "Wind Sounds \U0001F32C️ {hours} Hours Calming Wind for Sleep & Relaxation | Dark Screen",
        "description": (
            "Soft, calming wind blowing gently to soothe you into deep sleep and quiet the "
            "mind. Relaxing wind ambience all night. Dim, slow-moving visuals."
        ),
        "tags": [
            "wind sounds", "wind sounds for sleeping", "howling wind", "relaxing wind",
            "wind ambience", "nature sounds", "sleep sounds", "white noise", "dark screen",
            "calming wind", "wind noise", "deep sleep music",
        ],
    },
    {
        "key": "night",
        "name": "Night Sounds",
        "synth": "night",
        "emoji": "\U0001F30C",  # 🌌
        "short_title": "Night Sounds for Sleep \U0001F30C Crickets & Calm #shorts",
        "long_title": "Night Sounds \U0001F30C {hours} Hours Crickets & Nature for Deep Sleep | Dark Screen",
        "description": (
            "The peaceful sounds of a summer night — gentle crickets and soft nature "
            "ambience — to help you relax and fall into deep sleep. Dim, slow-moving visuals."
        ),
        "tags": [
            "night sounds", "cricket sounds", "crickets for sleeping", "summer night sounds",
            "nature sounds for sleeping", "night ambience", "relaxing night", "sleep sounds",
            "dark screen", "calming nature", "deep sleep music", "cricket sounds sleep",
        ],
    },
    {
        "key": "stream",
        "name": "Stream Sounds",
        "synth": "stream",
        "emoji": "\U0001F3DE️",  # 🏞️
        "short_title": "Stream Sounds for Sleep \U0001F3DE️ Gentle Creek #shorts",
        "long_title": "Stream Sounds \U0001F3DE️ {hours} Hours Gentle Creek & Flowing Water for Sleep | Dark Screen",
        "description": (
            "A gentle stream flowing over rocks — soft, calming water sounds for deep "
            "sleep, relaxation, and focus. Dim, slow-moving visuals."
        ),
        "tags": [
            "stream sounds", "creek sounds", "flowing water", "river sounds",
            "water sounds for sleeping", "relaxing stream", "nature sounds", "sleep sounds",
            "dark screen", "white noise", "calming water", "deep sleep music",
        ],
    },
]

BRAND_NAME = "Meditated Sleeping"
BRAND_TAGLINE = "Calm. Sleep. Restore."

# Broad, high-value niche tags appended to every video AFTER the theme-specific
# ones. make_metadata dedupes and packs tags up to YouTube's 500-char total
# limit. (Tags are a minor ranking signal — relevance > volume — but harmless.)
GLOBAL_TAGS = [
    "sleep music", "dark screen", "relaxing music", "meditation music",
    "deep sleep music", "calm music", "study music", "sleep sounds",
    "healing music", "insomnia relief music", "stress relief music",
    "sleep meditation", "relaxing sleep music", "ambient music",
    "background music", "spa music", "music for sleeping",
    "dark screen sleep music", "sleeping music", "relaxation music",
    "calming music", "peaceful music",
]

# Natural-language phrase for the description (NOT a keyword dump — over-stuffing
# risks a spam flag). Kept short and readable.
PERFECT_FOR = "sleep, studying, meditation, relaxation, yoga, spa, and stress relief"

# Auto-playlists: every long-form is added to its sub-niche playlist on upload
# (playlistItems.insert, 50 units, through the app's single project). Shorts are skipped — they surface via the Shorts
# feed, where playlists add little. Playlists are found-or-created by TITLE,
# so renaming a title here creates a NEW playlist.
PLAYLISTS = {
    "rain_nature": {
        "title": "Rain & Nature Sounds for Sleep \U0001F327️",
        "description": "Gentle rain, waterfalls, forest birdsong and calm nature "
                       "ambience for deep sleep, study, and relaxation. Dim, slow-moving visuals.",
        "themes": ["rain", "rain_drops", "rooftop_rain", "waterfall", "forest"],
    },
    "deep_sleep": {
        "title": "Deep Sleep Music \U0001F319",
        "description": "Warm ambient sleep music, delta waves, and soothing tones "
                       "to fall asleep fast and sleep deeply. Dim, slow-moving visuals.",
        "themes": ["sleeping", "delta_sleep", "528hz_sleep", "432hz_relax"],
    },
    "solfeggio": {
        "title": "Solfeggio & Healing Frequencies \U00002728",
        "description": "Solfeggio tones and healing frequency blends — 432 Hz, "
                       "528 Hz, 741 Hz, 852 Hz, 963 Hz and OM — woven into calm "
                       "sleep music. Dim, slow-moving visuals.",
        "themes": ["solfeggio_heal", "solfeggio_spirit", "solfeggio_deepsleep",
                    "om_136", "963hz_awakening", "852hz_intuition", "741hz_clarity"],
    },
    "instrumental": {
        "title": "Romantic & Instrumental Sleep Music \U0001F49E",
        "description": "Smooth romantic instrumentals, Indian tanpura and flute — "
                       "warm melodic music for sleep and unwinding. Dim, slow-moving visuals.",
        "themes": ["romantic", "romantic_night", "indian"],
    },
    "focus": {
        "title": "Focus & Study Music \U0001F3AF",
        "description": "Gamma-wave focus tracks and calm concentration music for "
                       "deep work and study. Dim, slow-moving visuals.",
        "themes": ["gamma_focus"],
    },
}


def synth_args(theme: dict) -> list:
    """generate_theme_audio.py CLI flags for a theme's frequency layers and tone
    shaping. Single source of truth so videos (produce.py) and distribution
    exports (make_album.py) render identical audio."""
    a = []
    if theme.get("tone"):
        a += ["--tone", str(theme["tone"])]  # single Hz or a combo "432,528,741"
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

# Appended to every description.
# ---- Visuals: a dim, slow animation per video (scripts/make_animated_video.py)
# Each theme's motion profile follows its sound; colours are deep night tones
# and the picture is rendered at --dim VISUAL_DIM so it stays dark enough to
# sleep to. Every upload still gets its own look (layer, palette, light).
VISUAL_DIM = 0.45
_SYNTH_TOPIC = {
    "rain": "water", "rain_drops": "water", "waterfall": "water", "ocean": "water",
    "stream": "water", "thunderstorm": "water", "fireplace": "fire",
    "forest": "wind", "wind": "wind", "night": "void", "sleeping": "void",
    "none": "void", "indian": "fire", "romantic": "neutral", "romantic_night": "neutral",
    "brown_noise": "stone", "white_noise": "stone", "pink_noise": "stone",
}
_TOPIC_COLOR = {
    "water": "2f5f8a", "fire": "a0522d", "wind": "3d6b5a", "void": "4b3f8f",
    "stone": "5a5a6e", "neutral": "7a3f6e",
}


def topic_for(theme_key: str) -> str:
    """The --topic for make_animated_video.py for this theme."""
    return _SYNTH_TOPIC.get(theme_by_key(theme_key)["synth"], "neutral")


def accent_for(theme_key: str) -> str:
    """The theme's base colour: its topic colour, nudged per theme so themes
    sharing a topic (e.g. the Solfeggio tracks) don't share one tint."""
    import colorsys
    import zlib
    base = _TOPIC_COLOR[topic_for(theme_key)]
    r, g, b = (int(base[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    h, l, sat = colorsys.rgb_to_hls(r, g, b)
    h = (h + ((zlib.crc32(theme_key.encode()) % 41) - 20) / 360.0) % 1.0
    return "%02x%02x%02x" % tuple(int(round(c * 255)) for c in colorsys.hls_to_rgb(h, l, sat))


# ---- ACE-Step 1.5 (AI music) blended with this repo's own Python audio -------
# Shorts get their music from ACE-Step; the channel's own code adds the nature
# bed and, for wellness themes, the exact tones (scripts/channel_kit.py
# render_ai_music). Any failure falls back to the synth for that upload, and
# every AI upload says so in its description and is flagged as synthetic.
ACESTEP_FORMATS = ("short",)
ACESTEP_STYLE = "slow soothing instrumental sleep music, soft pads and gentle piano"
# Nature bed overrides where the visual topic is the wrong cue for the sound.
ACESTEP_AMBIENCE = {"indian": "ambience_air", "night": "ambience_night",
                    "waterfall": "stream", "forest": "ambience_meadow"}


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
