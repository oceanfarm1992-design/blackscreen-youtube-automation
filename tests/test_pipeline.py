"""
Guards for the guarantees every channel relies on: each upload is unique
(theme + volume, render seed, thumbnail), titles fit YouTube's limits, every
theme is fully configured, schedules map to slots, and uploads retry
transient failures. Run: python -m pytest -q
"""
import importlib.util
import os
import re
import sys
from datetime import date, timedelta

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)

import channel_kit as K  # noqa: E402
import generate_theme_audio as G  # noqa: E402
import upload_youtube as U  # noqa: E402
from make_animated_video import TOPIC_PROFILES  # noqa: E402

ANIMATED = ["aether", "sanctuary", "hearth", "horizon", "resonance", "manor"]
ALL = ["scripts"] + ANIMATED


def load(folder, module, alias=None):
    """Import <folder>/<module>.py under a unique name (every channel has its
    own 'themes' module, so plain imports would collide)."""
    spec = importlib.util.spec_from_file_location(
        alias or f"{folder}_{module}", os.path.join(ROOT, folder, f"{module}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


THEMES = {f: load(f, "themes") for f in ALL}


def volume_for(folder, d, count, pos):
    T = THEMES[folder]
    return K.volume_for(T, d, count, pos)


def titles(folder, theme, fmt, volume):
    T = THEMES[folder]
    if folder == "scripts":
        sys.modules["themes"] = T
        meta = load("scripts", "make_metadata", "scripts_meta")
        return meta.build_metadata(theme, fmt, 10, volume)["title"]
    return K.build_metadata(T, theme, fmt, volume)["title"]


# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("folder", ALL)
def test_two_years_of_uploads_are_all_unique(folder):
    T = THEMES[folder]
    seen_titles, seen_seeds = set(), set()
    start = max(T.ANCHOR, date(2026, 10, 14))
    for day in range(730):
        d = start + timedelta(days=day)
        selection = T.daily_selection(d, count=T.DAILY_COUNT)
        for slot in range(T.DAILY_COUNT):
            pos = slot % len(selection)
            fmt = "long" if slot < T.LONGS_PER_DAY else "short"
            key = (selection[pos]["key"], fmt, volume_for(folder, d, T.DAILY_COUNT, pos))
            seed = int(d.strftime("%Y%m%d")) * 1000 + slot  # produce.py's seed for a slot
            assert key not in seen_titles, f"duplicate upload {key} on {d}"
            assert seed not in seen_seeds, f"seed {seed} reused on {d}"
            seen_titles.add(key)
            seen_seeds.add(seed)


@pytest.mark.parametrize("folder", ALL)
def test_titles_fit_and_carry_volume(folder):
    for theme in THEMES[folder].THEMES:
        for fmt in ("long", "short"):
            seen = set()
            for vol in (1, 2, 99, 365):
                t = titles(folder, theme, fmt, vol)
                assert len(t) <= 100, t
                assert f"Vol. {vol}" in t, t
                assert fmt != "short" or t.endswith("#shorts"), t
                seen.add(t)
            assert len(seen) == 4, f"{theme['key']} {fmt}: volumes don't change the title"


def test_fit_title_trims_at_a_word_boundary():
    long = "Rain Sounds Vol. 3 🌧️ " + "word " * 30 + "#shorts"
    t = K.fit_title(long.strip())
    assert len(t) <= 100 and t.endswith(" #shorts")
    assert t[:-len(" #shorts")].split()[-1] == "word"


@pytest.mark.parametrize("folder", ANIMATED)
def test_every_theme_is_fully_configured(folder):
    T = THEMES[folder]
    style = load(folder, "make_thumbnails").STYLE
    for theme in T.THEMES:
        k = theme["key"]
        assert re.fullmatch(r"[0-9a-fA-F]{6}", T.ACCENT_COLORS[k]), k
        assert T.topic_for(k) in TOPIC_PROFILES, k
        assert theme["synth"] == "none" or theme["synth"] in G.SYNTHS, k
        assert k in style["headlines"] or k in style["hand_made"], f"{k}: no thumbnail"
    keys = {t["key"] for t in T.THEMES}
    for pl in T.PLAYLISTS.values():
        assert set(pl["themes"]) <= keys, pl["title"]
    assert T.HOW_TO and not T.HOW_TO.endswith(".")


@pytest.mark.parametrize("wf", sorted(f for f in os.listdir(os.path.join(ROOT, ".github", "workflows"))
                                      if f.startswith("publish")))
def test_every_cron_maps_to_a_slot(wf):
    text = open(os.path.join(ROOT, ".github", "workflows", wf), encoding="utf-8").read()
    crons = re.findall(r'- cron: "([^"]+)"', text)
    slots = dict(re.findall(r'"([^"]+)"\)\s+echo "slot=(\d+)"', text))
    assert crons and set(crons) == set(slots), f"{wf}: cron/slot mismatch"
    assert sorted(int(s) for s in slots.values()) == list(range(len(crons)))
    assert "--date \"$RUN_DATE\"" in text and "MANUAL_SEED" in text


@pytest.mark.parametrize("folder", ANIMATED)
def test_two_uploads_of_a_theme_get_different_thumbnails(folder, tmp_path):
    try:
        K.load_font(40)
    except RuntimeError:
        pytest.skip("no TrueType font installed")
    from PIL import Image, ImageChops
    T = THEMES[folder]
    style = load(folder, "make_thumbnails").STYLE
    key = T.THEMES[0]["key"]
    a = K.render_thumbnail(T, style, key, str(tmp_path / "a.png"), seed=20261020000, volume=3)
    b = K.render_thumbnail(T, style, key, str(tmp_path / "b.png"), seed=20261025000, volume=4)
    ia, ib = Image.open(a), Image.open(b)
    assert ia.size == ib.size == (1280, 720)
    assert ImageChops.difference(ia.convert("RGB"), ib.convert("RGB")).getbbox() is not None


def test_failed_thumbnail_falls_back_to_committed_art(tmp_path, monkeypatch):
    class Failed:
        returncode = 1
    monkeypatch.setattr(K.subprocess, "run", lambda *a, **k: Failed())
    T = THEMES["hearth"]
    out = str(tmp_path / "t.png")
    K.make_feature_thumbnail(K.Channel(T), T.THEMES[0]["key"], out, 1, 1)
    committed = os.path.join(ROOT, "assets", "hearth", "thumbnails", "gen", f"{T.THEMES[0]['key']}.png")
    assert open(out, "rb").read() == open(committed, "rb").read()


@pytest.mark.parametrize("folder", ANIMATED)
def test_description_names_the_volume(folder):
    T = THEMES[folder]
    meta = K.build_metadata(T, T.THEMES[0], "long", 5)
    assert f"{T.THEMES[0]['name']} (Vol. 5)" in meta["description"].splitlines()[0]


def test_backfill_parses_durations_and_titles():
    B = load("scripts", "backfill_thumbnails")
    assert B.iso_seconds("PT14M30S") == 870
    assert B.iso_seconds("PT59S") == 59
    assert B.iso_seconds("PT10H") == 36000
    for folder in ANIMATED:
        T = THEMES[folder]
        for theme in T.THEMES:
            for vol in (None, 4):
                title = K.build_metadata(T, theme, "long", vol)["title"]
                assert B.theme_for_title(T, title)["key"] == theme["key"], title


# --------------------------------------------------------------------------- #
class _Resp(dict):
    def __init__(self, status):
        super().__init__(status=str(status))
        self.status, self.reason = status, "x"


class _Request:
    def __init__(self, script):
        self.script = list(script)

    def next_chunk(self):
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


class _YouTube:
    def __init__(self, request):
        self.request = request

    def videos(self):
        return self

    def insert(self, **_):
        return self.request


@pytest.fixture
def fast_upload(monkeypatch):
    monkeypatch.setattr(U.time, "sleep", lambda s: None)
    monkeypatch.setattr(U, "MediaFileUpload", lambda *a, **k: None)


def test_upload_retries_transient_errors(fast_upload):
    from googleapiclient.errors import HttpError
    req = _Request([HttpError(_Resp(503), b""), ConnectionResetError(), (None, {"id": "V1"})])
    assert U.upload_video(_YouTube(req), "v.mp4", "t", "d", []) == "V1"


def test_upload_does_not_retry_quota_or_auth_errors(fast_upload):
    from googleapiclient.errors import HttpError
    req = _Request([HttpError(_Resp(403), b"quota"), (None, {"id": "never"})])
    with pytest.raises(HttpError):
        U.upload_video(_YouTube(req), "v.mp4", "t", "d", [])


def test_upload_gives_up_after_max_retries(fast_upload):
    from googleapiclient.errors import HttpError
    req = _Request([HttpError(_Resp(500), b"")] * (U.MAX_RETRIES + 1))
    with pytest.raises(RuntimeError):
        U.upload_video(_YouTube(req), "v.mp4", "t", "d", [])


def test_noise_field_is_seed_unique():
    from make_animated_video import _noise_field
    a = _noise_field(64, 36, np.random.default_rng(1))
    b = _noise_field(64, 36, np.random.default_rng(2))
    assert not np.allclose(a, b)
