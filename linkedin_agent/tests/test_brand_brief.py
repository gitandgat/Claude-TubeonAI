"""Tests for the client brand-brief renderer (pure, no AI/IO)."""

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from linkedin_agent.engine.brand_brief import render_brand_brief, UNIVERSAL_VOICE_RULES


def _client(**over):
    base = dict(
        name="Jane Doe", niche="fractional CFO for SaaS startups",
        themes=("the day a founder ignored the burn rate", "a board call that went sideways"),
        hashtags="#Finance #SaaS", first_comment="DM me 'RUNWAY' for the cash model.",
        cta_fallback="Share this with one founder who needs it.",
    )
    base.update(over)
    return SimpleNamespace(**base)


def test_brief_contains_client_identity_and_cta():
    out = render_brand_brief(_client(), voice_profile={"tone": "dry, numbers-first"})
    assert "Jane Doe" in out
    assert "fractional CFO for SaaS startups" in out
    assert "DM me 'RUNWAY'" in out
    assert "dry, numbers-first" in out


def test_themes_become_the_story_vault():
    out = render_brand_brief(_client())
    assert "- the day a founder ignored the burn rate" in out
    assert "- a board call that went sideways" in out


def test_wedge_is_used_when_supplied():
    out = render_brand_brief(_client(), wedge="Most CFOs optimize the wrong metric.")
    assert "Most CFOs optimize the wrong metric." in out
    assert "TBD" not in out.split("## Story Vault")[0].split("## Strong Opinion / Wedge")[1]


def test_missing_wedge_and_customer_fall_back_to_tbd_prompts():
    out = render_brand_brief(_client(themes=()))
    assert "TBD" in out  # wedge + customer + story vault prompts
    assert "## Story Vault" in out


def test_universal_voice_rules_and_antislop_are_baked_in():
    out = render_brand_brief(_client())
    assert UNIVERSAL_VOICE_RULES.splitlines()[0] in out
    assert "No em dashes" in out
    assert "stop-slop gate" in out
    assert "—" not in out  # the brief itself must be em-dash clean


def test_empty_voice_profile_does_not_crash():
    out = render_brand_brief(_client(), voice_profile=None)
    assert "First person, specific moments" in out
