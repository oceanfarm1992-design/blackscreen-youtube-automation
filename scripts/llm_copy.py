#!/usr/bin/env python3
"""
Optional: a fresh opening paragraph for each upload's description, written
by a FREE model on OpenRouter. The rest of the description, the title, the
tags, the audio and the video stay exactly as the pipeline makes them.

Why only description text (and never code): it changes what viewers read on
every video without being able to break a render or an upload. Model output
is validated (length, no links/hashtags/@, no health claims, no "AI") and
anything that fails is thrown away.

Never blocks a video: no OPENROUTER_API_KEY, no free model available, a
rate limit, a timeout, a bad answer -- all just keep the normal description.

Free models are looked up at run time (GET /models, price 0), because the
free line-up changes often. Set OPENROUTER_MODEL to force one model id.
Free-tier limits are per OpenRouter account (a few dozen requests a day
without credits); the 7 channels together make ~8-9 requests a day.
"""
import json
import os
import re
import urllib.error
import urllib.request

API = "https://openrouter.ai/api/v1"
TIMEOUT = 45
MAX_MODELS_TRIED = 3

# Tried first when free; anything else free is a fallback.
PREFERRED = ("llama-3.3-70b", "deepseek", "gemini", "qwen3", "qwen", "mistral", "gemma", "llama")

# Rotating "angle" per upload, so even the same theme gets a different opening.
ANGLES = (
    "the first quiet minutes after you lie down",
    "a long day finally ending",
    "rain or wind outside a dark window",
    "a slow breath in and a slower breath out",
    "the house going still late at night",
    "letting thoughts drift past without following them",
    "a calm morning before anyone else is awake",
    "settling in to read, write or study",
    "the warmth of a blanket and a dim room",
    "time slowing down for a while",
    "the space between sounds",
    "returning to this place again",
)

_BANNED = re.compile(
    r"https?://|www\.|@|#|\bAI\b|artificial intelligence|language model|"
    r"\bcures?\b|\btreat(s|ment)?\b|therap|clinical|proven|guarantee|diagnos|"
    r"black screen|subscribe|like and",
    re.I,
)


def _request(path, key, body=None):
    req = urllib.request.Request(
        API + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/oceanfarm1992-design/blackscreen-youtube-automation",
            "X-Title": "ambient-channel-descriptions",
        },
        method="POST" if body is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode())


def _is_free(m):
    p = m.get("pricing") or {}
    try:
        return float(p.get("prompt", 1)) == 0 and float(p.get("completion", 1)) == 0
    except (TypeError, ValueError):
        return False


def free_models(models):
    """Ids of the free text models in a /models listing, best first."""
    ids = []
    for m in models:
        mod = (m.get("architecture") or {}).get("output_modalities") or ["text"]
        if _is_free(m) and "text" in mod and m.get("id"):
            ids.append(m["id"])

    def rank(mid):
        low = mid.lower()
        for i, p in enumerate(PREFERRED):
            if p in low:
                return i
        return len(PREFERRED)

    return sorted(ids, key=lambda i: (rank(i), i))


def clean(text):
    """The model's paragraph, tidied -- or None if it isn't usable."""
    if not text:
        return None
    t = re.sub(r"<think>.*?</think>", "", text, flags=re.S)  # reasoning models
    t = t.strip().strip('"“”').strip()
    t = re.sub(r"[*_`>]+", "", t)
    t = " ".join(t.split())
    if _BANNED.search(t):
        return None
    t = re.sub(r"[\U0001F000-\U0001FFFF☀-➿]", "", t).strip()
    if len(t) > 520:  # trim at a sentence end
        cut = t[:520]
        t = cut[: max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? ")) + 1].strip()
    if not (120 <= len(t) <= 520) or t[-1] not in ".!?":
        return None
    return t


def build_prompt(brand, theme, fmt, volume, title, angle):
    kind = "a 59-second YouTube Short" if fmt == "short" else "a long ambient YouTube video"
    return (
        f"Write the opening paragraph of the description for {kind} on the channel "
        f"\"{brand}\".\nTitle: {title}\nTheme: {theme['name']} -- {theme['description']}\n"
        f"This is volume {volume or 1} of the theme; open from this angle: {angle}.\n\n"
        "Rules: 2-3 sentences, 45-75 words, calm and warm, second person. Fresh wording -- "
        "do not reuse phrases from the theme text above. No hashtags, emoji, links, "
        "calls to subscribe, or health/medical claims. Do not mention AI or how it was "
        "made. Reply with the paragraph only."
    )


def intro_for(brand, theme, fmt, volume, title, seed, key=None):
    """(paragraph, model) or (None, reason)."""
    key = key or os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        return None, "no OPENROUTER_API_KEY"
    angle = ANGLES[(int(seed) + (volume or 0)) % len(ANGLES)]
    prompt = build_prompt(brand, theme, fmt, volume, title, angle)
    forced = os.environ.get("OPENROUTER_MODEL", "").strip()
    try:
        models = [forced] if forced else free_models(_request("/models", key).get("data", []))
    except Exception as e:
        return None, f"model list failed: {e}"
    if not models:
        return None, "no free model available"
    last = "no answer"
    for model in models[:MAX_MODELS_TRIED]:
        try:
            res = _request("/chat/completions", key, {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.9,
                "max_tokens": 400,
            })
            text = clean(((res.get("choices") or [{}])[0].get("message") or {}).get("content"))
            if text:
                return text, model
            last = f"{model}: answer failed validation"
        except urllib.error.HTTPError as e:
            last = f"{model}: HTTP {e.code}"  # 429 = free-tier limit; try the next model
        except Exception as e:
            last = f"{model}: {e}"
    return None, last


def enrich_metadata(meta_path, brand, theme, fmt, volume, seed):
    """Insert the paragraph after the description's first line. Never raises."""
    try:
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        text, info = intro_for(brand, theme, fmt, volume, meta["title"], seed)
        if not text:
            print(f"  (description: standard text -- {info})")
            return False
        head, sep, rest = meta["description"].partition("\n\n")
        desc = f"{head}\n\n{text}{sep}{rest}" if sep else f"{head}\n\n{text}"
        if len(desc) > 4900:  # YouTube's cap is 5000
            print("  (description: AI paragraph skipped -- would exceed 5000 chars)")
            return False
        meta["description"] = desc
        meta["description_ai_model"] = info
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        print(f"  + description: unique opening written by {info}")
        return True
    except Exception as e:
        print(f"  (description: standard text -- {e})")
        return False
