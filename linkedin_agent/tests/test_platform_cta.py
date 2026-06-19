"""Tests for per-platform CTA mapping (Blotato post-writer Step 4.5)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from linkedin_agent.engine.platform_cta import (
    rewarded_metric, cta_for, apply_crosspost_cta, REWARDED_METRIC,
)

POST = (
    "I sat in my car for 47 minutes after my second CaRMS rejection.\n\n"
    "That night I stopped taking the exam again.\n\n"
    "What's a choice you made that didn't look impressive but felt right?\n\n"
    "#IMG #CaRMS #MedicalCareers"
)


def test_metric_mapping_matches_algorithms():
    # Assert
    assert rewarded_metric("linkedin") == "comments"
    assert rewarded_metric("instagram") == "saves"
    assert rewarded_metric("facebook") == "shares"
    assert rewarded_metric("twitter") == "replies"
    assert rewarded_metric("tiktok") == "completion"


def test_unknown_platform_defaults_to_comments():
    assert rewarded_metric("myspace") == "comments"
    assert rewarded_metric("") == "comments"


def test_linkedin_is_left_unchanged():
    # LinkedIn's closing question already drives comments; no second CTA bolted on.
    assert cta_for("linkedin") == ""
    assert apply_crosspost_cta(POST, "linkedin") == POST


def test_instagram_gets_a_save_cta_before_hashtags():
    # Act
    out = apply_crosspost_cta(POST, "instagram")

    # Assert — CTA added, placed before the hashtag block, body preserved
    assert "save this" in out.lower()
    assert out.index("Save this") < out.index("#IMG")
    assert "47 minutes" in out


def test_facebook_gets_a_tag_cta():
    out = apply_crosspost_cta(POST, "facebook")
    assert "tag someone" in out.lower()


def test_cta_is_not_stacked_on_reruns():
    # Applying twice must not add the cue twice (idempotent).
    once = apply_crosspost_cta(POST, "instagram")
    twice = apply_crosspost_cta(once, "instagram")
    assert once == twice
    assert once.lower().count("save this for the next hard day") == 1


def test_cta_lines_have_no_em_dashes():
    # Stop-slop compliance: zero em dashes in any CTA line.
    assert all("—" not in line for line in REWARDED_METRIC)  # keys clean
    for plat in ("instagram", "facebook", "twitter", "tiktok", "youtube"):
        assert "—" not in cta_for(plat)


def test_appends_when_no_hashtags_present():
    plain = "I stopped taking the exam again."
    out = apply_crosspost_cta(plain, "facebook")
    assert out.endswith("Tag someone who needs to read this today.")
