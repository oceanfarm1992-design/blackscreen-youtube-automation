#!/usr/bin/env python3
"""Write streams.conf from command-line args (no special chars needed).
Usage: python3 write_streams.py KEY1 KEY2 KEY3 KEY4 KEY5
  KEY1 = sleeping, KEY2 = solfeggio, KEY3 = forest, KEY4 = romantic, KEY5 = rain
"""
import sys, os

STREAMS = [
    ("sleeping",  "sleeping_loop.wav",       "Deep Sleep Music 24/7"),
    ("solfeggio", "solfeggio_heal_loop.wav",  "Solfeggio Healing 24/7"),
    ("forest",    "forest_loop.wav",          "Forest Night Sounds 24/7"),
    ("romantic",  "romantic_loop.wav",         "Romantic Piano 24/7"),
    ("rain",      "rain_loop.wav",             "Rain Sounds 24/7"),
]

if len(sys.argv) < 6:
    print("Usage: python3 write_streams.py SLEEP_KEY SOLF_KEY FOREST_KEY ROMANTIC_KEY RAIN_KEY")
    sys.exit(1)

conf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "streams.conf")
with open(conf, "w") as f:
    for i, (name, audio, title) in enumerate(STREAMS):
        f.write(f"{name}|{audio}|{sys.argv[i+1]}|{title}\n")

print(f"Written {len(STREAMS)} streams to {conf}")
