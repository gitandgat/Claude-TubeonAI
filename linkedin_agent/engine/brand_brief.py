"""Render a Blotato-style brand-brief.md for a managed-service client.

The per-vertical brand briefs (linkedin_agent/data/verticals/<key>/brand-brief.md)
gave the Blotato content skills voice-accurate context. A paying client needs the
same artifact in their own folder. This generates it at onboarding from the
cloned Client + voice profile, with the project's anti-slop rules baked in so the
skills inherit the client's voice, not generic defaults.

`render_brand_brief` is pure (returns the markdown string) so it's testable with
no AI and no filesystem. `write_brand_brief` persists it to the client's data dir.
"""

from __future__ import annotations

import os
from datetime import date

# Reused verbatim across every brief so the Blotato skills + the generator share
# one voice contract. Mirrors the FORMAT_SPINE hard bans and the stop-slop gate.
UNIVERSAL_VOICE_RULES = """## Universal Voice Rules (these override generic Blotato defaults)
- THE ONE RULE: first person, a specific moment, concrete numbers + sensory detail. First-person scenes outperform abstract second-person advice by ~18x on this stack.
- Contractions always. Numbers as digits. No em dashes.
- HARD BANS: no second-person sermons ("you need to…"); no section labels; no AI slop (unleash, dive into, game-changer, supercharge, transformative, leverage, empower, unlock, paradigm shift, "here's what I learned", "at the end of the day", "honestly", "literally", "let's be real").
- Length 150-350 words. One concrete idea per post.
- Link/offer goes in the first comment, never the post body.
- BEFORE SCHEDULING: run every draft through the virality grade + stop-slop gate (min 35/50). viral-hooks templates are scaffolding; rewrite in this client's voice."""


def _voice_line(voice_profile: dict | None) -> str:
    """One-line voice description from the cloned profile (graceful if empty)."""
    vp = voice_profile or {}
    tone = (vp.get("tone") or "").strip()
    phrases = vp.get("recurring_phrases") or vp.get("vocabulary_examples") or []
    bits = []
    if tone:
        bits.append(tone.rstrip("."))
    if phrases:
        sample = ", ".join(str(p) for p in phrases[:4])
        bits.append(f"signature phrases: {sample}")
    base = ". ".join(bits) if bits else "Cloned from the client's own posts"
    return f"{base}. First person, specific moments, real numbers, honest reflection."


def render_brand_brief(client, voice_profile: dict | None = None,
                       wedge: str = "", customer: str = "",
                       story_seeds=None) -> str:
    """Build the brand-brief.md markdown for a client. Pure — no IO, no AI.

    `client` is duck-typed (name, niche, themes, hashtags, first_comment,
    cta_fallback), so a Client or any stand-in works.
    """
    name = getattr(client, "name", "Client")
    niche = getattr(client, "niche", "")
    hashtags = getattr(client, "hashtags", "") or "(set topic hashtags)"
    cta = getattr(client, "first_comment", "") or getattr(client, "cta_fallback", "") \
        or "TBD: the one action a reader should take (first comment, never the body)."
    seeds = list(story_seeds or getattr(client, "themes", ()) or [])

    wedge_block = wedge.strip() if wedge and wedge.strip() else (
        f"TBD: the contrarian belief most people in {niche or 'this niche'} would "
        "push back on. This is the viral fuel; fill it in before the first batch.")
    customer_block = customer.strip() if customer and customer.strip() else (
        "TBD: describe the one real person who reads and acts on these posts "
        "(not a demographic).")
    story_block = "\n".join(f"- {s}" for s in seeds) if seeds else \
        "- TBD: add 3-5 real moments, wins, or mistakes to draw on."

    return f"""# Brand Brief: {name}{f' ({niche})' if niche else ''}

> Captured: {date.today().isoformat()} (managed-service client; generated at onboarding)
> Read by the Blotato content skills (brand-brief, post-writer, viral-hooks, post-grader) from this folder, and mirrored by the client's voice_profile.json for the generator.

## Business
{niche or 'TBD: what the client does, in plain words.'}

## Customer
{customer_block}

## Primary CTA
{cta}

## Strong Opinion / Wedge
{wedge_block}

## Story Vault
{story_block}

## Voice
{_voice_line(voice_profile)}

{UNIVERSAL_VOICE_RULES}
"""


def write_brand_brief(client, voice_profile: dict | None = None,
                      wedge: str = "", customer: str = "",
                      story_seeds=None) -> str:
    """Render and write brand-brief.md into the client's data dir. Returns path."""
    md = render_brand_brief(client, voice_profile=voice_profile, wedge=wedge,
                            customer=customer, story_seeds=story_seeds)
    os.makedirs(client.data_dir, exist_ok=True)
    path = os.path.join(client.data_dir, "brand-brief.md")
    with open(path, "w") as f:
        f.write(md)
    return path
