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
MAX_MODELS_TRIED = 8  # free models are often busy (HTTP 429): keep trying others

# Free models that aren't general chat models (or are tiny) write poor prose.
_SKIP = re.compile(r"code|coder|embed|vision|-vl\b|guard|ocr|image|audio|tts|whisper|"
                   r"math|reward|safety|\b0\.[0-9]+b\b|\b[1-3]b\b", re.I)

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
        # text-only output: music/image models (e.g. google/lyria-*) are free too
        mod = (m.get("architecture") or {}).get("output_modalities") or ["text"]
        if (_is_free(m) and list(mod) == ["text"] and m.get("id")
                and not _SKIP.search(m["id"]) and "lyria" not in m["id"].lower()):
            ids.append(m["id"])

    def rank(mid):
        low = mid.lower()
        for i, p in enumerate(PREFERRED):
            if p in low:
                return i
        return len(PREFERRED)

    return sorted(ids, key=lambda i: (rank(i), i))


def validate(text):
    """(paragraph, None) if the model's answer is usable, else (None, reason)."""
    if not text or not text.strip():
        return None, "empty answer"
    t = text
    if "</think>" in t:                       # reasoning models: keep only the answer
        t = t.rsplit("</think>", 1)[1]
    t = re.sub(r"<think>.*", "", t, flags=re.S)
    paras = [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]
    # drop a lead-in such as "Here is the opening paragraph:"
    paras = [p for p in paras if not (len(p) < 100 and p.rstrip().endswith(":"))]
    if not paras:
        return None, "no paragraph"
    t = max(paras[:3], key=len)               # the paragraph itself, not notes around it
    t = t.strip().strip('"\u201c\u201d').strip()
    t = re.sub(r"[*_`>]+", "", t)
    t = " ".join(t.split())
    hit = _BANNED.search(t)
    if hit:
        return None, f"contains '{hit.group(0)}'"
    t = re.sub(r"[\U0001F000-\U0001FFFF\u2600-\u27BF]", "", t).strip()
    if len(t) > 520:  # trim at a sentence end
        cut = t[:520]
        t = cut[: max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? ")) + 1].strip()
    if len(t) < 120:
        return None, f"too short ({len(t)} chars)"
    if t[-1] not in ".!?":
        return None, "doesn't end in a full sentence"
    return t, None


def clean(text):
    """The model's paragraph, tidied -- or None if it isn't usable."""
    return validate(text)[0]


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
            text, why = validate(((res.get("choices") or [{}])[0].get("message") or {}).get("content"))
            if text:
                return text, model
            last = f"{model}: answer rejected -- {why}"
            print(f"  ({last})")
        except urllib.error.HTTPError as e:
            last = f"{model}: HTTP {e.code}"  # 429 = free-tier limit; try the next model
            print(f"  ({last})")
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
