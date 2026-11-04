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
def scheduled_uploads(T, days):
    """What the scheduler publishes from RULES_START: [(date, slot, theme, fmt, vol)]."""
    out = []
    for i in range(days):
        d = K.RULES_START + timedelta(days=i)
        if K.is_feature_day(T, d):
            theme, vol = K.feature_for(T, d)
            out.append((d, 0, theme["key"], "long", vol))
        theme, vol = K.short_for(T, d)
        out.append((d, 1, theme["key"], "short", vol))
    return out


@pytest.mark.parametrize("folder", ALL)
def test_two_years_of_uploads_are_all_unique(folder):
    T = THEMES[folder]
    seen_titles, seen_seeds = set(), set()
    for d, slot, key, fmt, vol in scheduled_uploads(T, 730):
        seed = int(d.strftime("%Y%m%d")) * 1000 + slot  # produce.py's seed for a slot
        assert (key, fmt, vol) not in seen_titles, f"duplicate upload {key} {fmt} Vol. {vol} on {d}"
        assert seed not in seen_seeds, f"seed {seed} reused on {d}"
        seen_titles.add((key, fmt, vol))
        seen_seeds.add(seed)


@pytest.mark.parametrize("folder", ALL)
def test_one_short_daily_and_a_feature_every_4_days(folder):
    T = THEMES[folder]
    ups = scheduled_uploads(T, 120)
    shorts = [u for u in ups if u[3] == "short"]
    features = [u for u in ups if u[3] == "long"]
    assert len(shorts) == 120 and len({u[0] for u in shorts}) == 120
    gaps = {(b[0] - a[0]).days for a, b in zip(features, features[1:])}
    assert gaps == {4} and len(features) == 30
    # every theme gets both formats within a full rotation
    L = len(T.THEMES)
    assert {u[2] for u in shorts[:L]} == {t["key"] for t in T.THEMES}
    assert {u[2] for u in scheduled_uploads(T, 4 * L) if u[3] == "long"} == {t["key"] for t in T.THEMES}


@pytest.mark.parametrize("folder", ALL)
def test_new_volumes_continue_above_the_old_rotation(folder):
    """Vol. numbers from the new cadence start above every Vol. the old
    one-feature-a-day rotation used, so no new title can repeat an old one."""
    T = THEMES[folder]
    old_max = max(K.volume_for(T, K.RULES_START, T.DAILY_COUNT, pos) for pos in range(T.DAILY_COUNT))
    assert min(u[4] for u in scheduled_uploads(T, 60)) > old_max


@pytest.mark.parametrize("folder", ALL)
def test_late_runs_for_old_days_never_collide_with_new_cadence(folder):
    """A run scheduled for a day before RULES_START can start after the switch
    (GitHub runs crons hours late); it must keep the old rotation and still
    never repeat a title the new cadence uses."""
    T = THEMES[folder]
    seen = set()
    for i in range(-10, 90):
        d = K.RULES_START + timedelta(days=i)
        for slot in (0, 1):
            pick = K.scheduled_slot(T, d, slot)
            if pick is None:
                continue
            theme, fmt, vol = pick
            key = (theme["key"], fmt, vol)
            assert key not in seen, f"{d} slot {slot}: duplicate {key}"
            seen.add(key)


def test_feature_days_are_staggered_across_channels():
    on_day = [sum(K.is_feature_day(THEMES[f], K.RULES_START + timedelta(days=i)) for f in ALL)
              for i in range(4)]
    assert sorted(on_day) == [1, 2, 2, 2], on_day
    assert not any(K.is_feature_day(THEMES["aether"], K.RULES_START + timedelta(days=i))
                   and K.is_feature_day(THEMES["hearth"], K.RULES_START + timedelta(days=i))
                   for i in range(8)), "the two hours-long channels should render on different days"


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


def test_verified_channels_rotate_3_8_10_hours():
    for folder in ANIMATED:
        T = THEMES[folder]
        hours = [K.long_hours_for(T, u[0]) for u in scheduled_uploads(T, 24) if u[3] == "long"]
        if folder in ("aether", "hearth"):
            assert hours == [3, 8, 10, 3, 8, 10]
        else:
            assert hours == [None] * 6, f"{folder} isn't phone-verified: must stay under 15 min"


@pytest.mark.parametrize("folder", ["aether", "hearth"])
def test_hours_long_metadata(folder):
    T = THEMES[folder]
    for theme in T.THEMES:
        meta = K.build_metadata(T, theme, "long", 4, hours=10)
        assert "10 Hours" in meta["title"] and "14 Minute" not in meta["title"]
        assert len(meta["title"]) <= 100 and "Vol. 4" in meta["title"]
        assert meta["description"].startswith(f"10 Hours of {theme['name']} (Vol. 4)")
        assert "never a static loop" not in meta["description"]  # the hour repeats


@pytest.mark.parametrize("topic", sorted(TOPIC_PROFILES))
def test_loop_segment_path_is_seamless(topic):
    from make_animated_video import _pan_path
    n = 18 * 60
    dx, dy = _pan_path(n, 60, 200, 120, np.random.default_rng(4), TOPIC_PROFILES[topic], periodic=True)
    step = max(np.abs(np.diff(dx)).max(), np.abs(np.diff(dy)).max())
    seam = max(abs(int(dx[0]) - int(dx[-1])), abs(int(dy[0]) - int(dy[-1])))
    assert seam <= step + 1, f"{topic}: loop seam jumps {seam}px (normal step {step}px)"


def test_loop_flicker_period_divides_the_segment():
    from make_animated_video import loop_period
    for period in (7.0, 55.0, 90.0, 240.0, 300.0, 420.0):
        p = loop_period(period, 3600)
        assert abs(3600 / p - round(3600 / p)) < 1e-9 and abs(p - period) / period < 0.1


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


# --------------------------------------------------------------------------- #
# Visual variety: every upload has its own look, not just a reshuffled cloud.

@pytest.mark.parametrize("topic", sorted(TOPIC_PROFILES))
def test_every_look_loops_seamlessly(topic):
    """Hours-long features loop an animated segment: the frame after the last
    must match the first for every layer, or the loop point would jump."""
    from make_animated_video import TOPIC_LAYERS, frame_maker
    for v in range(len(TOPIC_LAYERS[topic])):
        n, frame, look = frame_maker(20, 160, 90, "4a6a4a", 20261104000 + v, topic,
                                     periodic=True, variant=v)
        seam = np.abs(frame(0).astype(int) - frame(n).astype(int)).mean()
        assert seam < 0.5, f"{topic}/{look['layer']}: loop seam differs by {seam:.2f}"


def color_of(T, key):
    return T.ACCENT_COLORS[key] if hasattr(T, "ACCENT_COLORS") else T.accent_for(key)


@pytest.mark.parametrize("folder", ALL)
def test_consecutive_uploads_of_a_theme_never_share_a_layer(folder):
    """The animated layer cycles with the Vol. number, so when a theme comes
    round again (in either format) it never looks like its last upload."""
    from make_animated_video import pick_look
    T = THEMES[folder]
    last = {}
    for d, slot, key, fmt, vol in scheduled_uploads(T, 730):
        seed = K.render_seed(T, int(d.strftime("%Y%m%d")) * 1000 + slot)
        layer = pick_look(seed, T.topic_for(key), vol)["layer"]
        assert last.get((key, fmt)) != layer, f"{key} {fmt} Vol. {vol} repeats layer {layer}"
        last[(key, fmt)] = layer


@pytest.mark.parametrize("folder", ALL)
def test_two_uploads_of_a_theme_look_clearly_different(folder):
    """Not just different pixels: the same moment of two consecutive uploads
    of a theme should differ visibly -- by more than 15% of the picture's own
    brightness, so dark themes and the dim main channel are judged fairly."""
    from make_animated_video import frame_maker
    T = THEMES[folder]
    for theme in T.THEMES:
        key = theme["key"]
        frames = []
        for vol, seed in ((7, 20261105000), (8, 20261115000)):
            dim = getattr(T, "VISUAL_DIM", 1.0)
            n, frame, _ = frame_maker(10, 192, 108, color_of(T, key), K.render_seed(T, seed),
                                      T.topic_for(key), variant=vol, dim=dim)
            frames.append(frame(90).astype(int))
        rel = np.abs(frames[0] - frames[1]).mean() / (np.mean(frames) + 1e-9)
        assert rel > 0.15, f"{folder}/{key}: consecutive uploads differ by only {rel:.0%}"


# --------------------------------------------------------------------------- #
# Duplicate guard: a title already on the channel is never uploaded again.

class _Exec:
    def __init__(self, result):
        self.result = result

    def execute(self):
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class _Channel:
    """Fake client: channels().list -> uploads playlist; playlistItems pages."""
    def __init__(self, pages, channels=None):
        self.pages, self.channels_result = list(pages), channels

    def channels(self):
        return self

    def playlistItems(self):
        return self

    def list(self, **kw):
        if "mine" in kw:
            return _Exec(self.channels_result or
                         {"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "UU1"}}}]})
        return _Exec(self.pages.pop(0))

    def list_next(self, req, res):
        return _Exec(self.pages.pop(0)) if self.pages else None


def _page(*titles):
    return {"items": [{"snippet": {"title": t}} for t in titles]}


def test_duplicate_titles_are_detected_across_pages():
    yt = _Channel([_page("Creek Hollow Vol. 6 #shorts"), _page("Creek  Hollow Vol. 7 #Shorts")])
    existing = U.recent_upload_titles(yt)
    assert U.is_duplicate_title(existing, "Creek Hollow Vol. 7 #shorts")
    assert not U.is_duplicate_title(existing, "Creek Hollow Vol. 8 #shorts")


def test_duplicate_check_never_blocks_an_upload_when_it_cannot_read():
    """Upload-only tokens get a 403 on channels.list: the check must fail open."""
    from googleapiclient.errors import HttpError
    yt = _Channel([], channels=HttpError(_Resp(403), b"insufficientPermissions"))
    existing = U.recent_upload_titles(yt)
    assert existing is None
    assert not U.is_duplicate_title(existing, "anything")


# --------------------------------------------------------------------------- #
# Every video on every channel is its own render, and its music is its own.

def test_render_seeds_are_unique_across_all_channels():
    """Channels share date-based schedule seeds (and some share a music
    preset); the per-channel render seed keeps every render distinct."""
    seen = {}
    for folder in ALL:
        T = THEMES[folder]
        for d, slot, key, fmt, vol in scheduled_uploads(T, 730):
            s = K.render_seed(T, int(d.strftime("%Y%m%d")) * 1000 + slot)
            assert s not in seen, f"{folder} {d} reuses the render seed of {seen[s]}"
            seen[s] = (folder, d)


def test_main_channel_is_no_longer_sold_as_a_black_screen():
    T = THEMES["scripts"]
    for theme in T.THEMES:
        for fmt in ("short", "long"):
            meta_title = titles("scripts", theme, fmt, 3)
            assert "black" not in meta_title.lower(), meta_title
        assert not any("black" in t.lower() for t in theme["tags"]), theme["key"]
        assert "black" not in theme["description"].lower(), theme["key"]
        assert T.topic_for(theme["key"]) in TOPIC_PROFILES
        assert re.fullmatch(r"[0-9a-f]{6}", T.accent_for(theme["key"]))


def test_consecutive_uploads_never_share_a_key_or_tape_speed():
    n = len(G._TRANSPOSE_SEMITONES)
    for vol in range(1, 200):
        assert (vol * 3) % n != ((vol + 1) * 3) % n  # key index, as main() sets it
        a = G.varispeed_semitones(np.random.default_rng(vol), vol)
        b = G.varispeed_semitones(np.random.default_rng(vol + 1), vol + 1)
        assert abs(a - b) > 0.2, (vol, a, b)


def test_varispeed_keeps_the_length_and_shifts_the_pitch():
    sr = G.SR
    tone = lambda m: np.sin(2 * np.pi * 440.0 * np.arange(m) / sr)
    out = G.varispeed(tone, sr * 2, 2.0)  # +2 semitones
    assert len(out) == sr * 2
    f = np.fft.rfftfreq(len(out), 1 / sr)[np.argmax(np.abs(np.fft.rfft(out)))]
    assert abs(f - 440.0 * 2 ** (2 / 12)) < 1.0, f


def _render_audio(tmp_path, name, *args):
    import subprocess
    import soundfile as sf
    out = tmp_path / f"{name}.wav"
    subprocess.run([sys.executable, os.path.join(SCRIPTS, "generate_theme_audio.py"),
                    "--seconds", "6", "--out", str(out)] + [str(a) for a in args],
                   check=True, capture_output=True)
    return sf.read(str(out))[0]


@pytest.mark.parametrize("synth_args", [
    ["--theme", "creek_hollow"],
    ["--theme", "sleeping", "--tone", "528", "--beat", "delta", "--beat-type", "binaural"],
])
def test_two_uploads_of_a_theme_have_different_music(tmp_path, synth_args):
    a = _render_audio(tmp_path, "a", "--seed", 11, "--variant", 4, *synth_args)
    b = _render_audio(tmp_path, "b", "--seed", 12, "--variant", 5, *synth_args)
    corr = abs(np.corrcoef(a[:, 0], b[:, 0])[0, 1])
    assert corr < 0.5, f"consecutive uploads correlate {corr:.2f}"


def test_frequency_tracks_vary_but_keep_their_exact_tone(tmp_path):
    """Pure-frequency tracks get a seed-varied texture under the tone; the
    carrier itself must still dominate and stay exactly on frequency."""
    args = ["--theme", "none", "--tone", "963", "--tone-soft", "--tone-gain", "0.14"]
    a = _render_audio(tmp_path, "a", "--seed", 21, "--variant", 1, *args)
    b = _render_audio(tmp_path, "b", "--seed", 22, "--variant", 2, *args)
    for x in (a, b):
        spec = np.abs(np.fft.rfft(x.mean(1))) ** 2
        f = np.fft.rfftfreq(len(x), 1 / G.SR)
        assert abs(f[np.argmax(spec)] - 963.0) < 0.5
        assert spec[(f > 958) & (f < 968)].sum() / spec.sum() > 0.6
    # the texture under the tone differs between uploads
    def texture(x):
        spec = np.abs(np.fft.rfft(x.mean(1)))
        f = np.fft.rfftfreq(len(x), 1 / G.SR)
        spec[(f > 900) & (f < 1030)] = 0
        return spec / np.linalg.norm(spec)
    assert texture(a) @ texture(b) < 0.9
