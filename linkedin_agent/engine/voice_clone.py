"""Voice cloning + creative brief from a pasted post corpus.

Standalone on purpose: the free "voice-match demo" must run with NO client
credentials (no Zernio, no LinkedIn) — a prospect just pastes their recent
posts. So this module depends only on the AI client, not on VoiceEngine /
ZernioClient. The analyst prompt mirrors
`engine/voice_engine.py:analyze_voice_profile` so a cloned profile is shaped
identically to the in-house one and feeds PostWriter the same way.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from linkedin_agent.json_utils import extract_json
from ai_client_factory import get_ai_client

_ANALYST_PROMPT = """You are a linguistic and brand voice analyst.
Analyze the provided LinkedIn posts to extract the unique voice and style of this creator.
Focus on:
1. Tone and personality (formal, casual, inspirational, analytical, etc.)
2. Recurring sentence structures and patterns
3. Favorite vocabulary and phrases
4. Emotional appeals used most frequently
5. The 5 most common post structures (hook -> body -> CTA pattern)
6. Signature linguistic quirks

Return your analysis as a JSON object with these keys:
- tone: string (brief description)
- vocabulary_examples: list of 10-15 common words/phrases
- sentence_patterns: list of 3-5 structural patterns
- recurring_phrases: list of 5-10 phrases that appear frequently
- emotional_triggers: list of 3-5 emotions/appeals used
- structural_templates: list of 5 post structure templates (hook -> body -> cta)
- linguistic_quirks: list of unique speech patterns
- avg_sentence_length: number
- complexity_level: "simple" | "moderate" | "complex"
- hashtag_style: string describing how hashtags are used"""

_BRIEF_PROMPT = """You are a LinkedIn content strategist.
Given a creator and their niche, propose story themes that would produce
high-reach FIRST-PERSON posts (specific moments, real numbers, honest
reflection — not generic advice), plus 3-5 relevant topic hashtags.

Return ONLY a JSON object:
{"themes": ["5 short, specific theme strings"], "hashtags": "#A #B #C"}"""

_WEDGE_PROMPT = """You are a LinkedIn positioning strategist.
Given a creator and their niche, propose ONE sharp contrarian wedge: a strong
opinion most people in that niche would push back on. Specific and arguable, not
a platitude. It is the single biggest viral fuel for their content.

Return ONLY a JSON object: {"wedge": "one or two sentences"}"""


def _complete(system: str, user: str, max_tokens: int, provider=None, client=None) -> str:
    """One completion against whichever AI client is active (Ollama/Claude)."""
    if provider is None or client is None:
        provider, client = get_ai_client()
    if provider == "claude":
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
    else:
        resp = client.create(
            messages=[{"role": "user", "content": user}],
            system=system,
            max_tokens=max_tokens,
        )
    return resp.content[0].text


def analyze_corpus(posts: list[str], provider=None, client=None) -> dict:
    """Build a voice fingerprint from a list of raw post texts."""
    corpus = "\n\n---\n\n".join(p.strip() for p in posts if p and p.strip())
    if not corpus:
        return {}
    user = (
        "Analyze this creator's LinkedIn post corpus and extract their voice "
        f"fingerprint:\n\n{corpus[:15000]}\n\n"
        "Return ONLY valid JSON, no markdown formatting, no extra text."
    )
    try:
        text = _complete(_ANALYST_PROMPT, user, 2000, provider, client)
        profile = extract_json(text)
        return profile if isinstance(profile, dict) else {}
    except Exception as e:  # noqa: BLE001 — demo must degrade, not crash
        print(f"  Voice analysis failed: {e}")
        return {}


def suggest_brief(name: str, niche: str, provider=None, client=None) -> dict:
    """Suggest demo themes + hashtags for a creator/niche. Always returns the
    two keys so callers can rely on the shape even if the AI call fails."""
    user = f"Creator: {name}\nNiche: {niche}\n\nReturn only the JSON object."
    data: dict = {}
    try:
        parsed = _complete(_BRIEF_PROMPT, user, 600, provider, client)
        parsed = extract_json(parsed)
        if isinstance(parsed, dict):
            data = parsed
    except Exception as e:  # noqa: BLE001
        print(f"  Brief suggestion failed: {e}")
    data.setdefault("themes", [])
    data.setdefault("hashtags", "")
    return data


def suggest_wedge(name: str, niche: str, provider=None, client=None) -> str:
    """Suggest the client's contrarian wedge (viral fuel). "" if the AI call
    fails, so the brand brief falls back to a TBD prompt instead of crashing."""
    user = f"Creator: {name}\nNiche: {niche}\n\nReturn only the JSON object."
    try:
        parsed = extract_json(_complete(_WEDGE_PROMPT, user, 300, provider, client))
        if isinstance(parsed, dict):
            return (parsed.get("wedge") or "").strip()
    except Exception as e:  # noqa: BLE001 — demo must degrade, not crash
        print(f"  Wedge suggestion failed: {e}")
    return ""
