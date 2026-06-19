"""Tests for the deterministic virality grader.

Calibration anchor: this account's 4k-14k-view posts are first-person scenes with
real numbers; abstract second-person advice is the losing format. The grader must
separate the two cleanly.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest

from linkedin_agent.engine.virality_grader import (
    grade, passes, VIRALITY_TARGET, HOOK_RESCUE_BELOW,
)

# A post in the proven winning shape: first person, mid-scene, real numbers,
# a turn, an honest reflection, a closing question, topic hashtags.
STRONG_POST = (
    "I sat in my car for 47 minutes after my second CaRMS rejection.\n\n"
    "The engine was off. $18,000 in exam fees behind me, 6 years of study, and a "
    "WhatsApp from my mother asking when I'd finally be a doctor in Canada.\n\n"
    "That night I decided to stop taking the exam again. For the first time in years "
    "I drove home without rehearsing a single answer. It felt like grief. It also "
    "felt like air in my chest.\n\n"
    "What's a choice you made that didn't look impressive but felt right?\n\n"
    "#IMG #CaRMS #MedicalCareers"
)

# The losing format: abstract, second-person sermon, no specifics, no question.
WEAK_POST = (
    "You need to overcome your fear. Discipline is a muscle. Success is a choice "
    "you make every single day. Here's what I learned about growth."
)


def test_strong_first_person_post_clears_the_target():
    # Act
    score, dims, fixes = grade(STRONG_POST)

    # Assert
    assert score >= VIRALITY_TARGET
    assert dims["hook"] >= 8
    assert passes(STRONG_POST) is True


def test_weak_second_person_post_scores_low():
    # Act
    score, dims, fixes = grade(WEAK_POST)

    # Assert
    assert score < 50
    assert dims["hook"] < HOOK_RESCUE_BELOW
    assert passes(WEAK_POST) is False


def test_second_person_opener_is_penalized_in_the_hook():
    # Arrange / Act
    _, first_person, _ = grade("I tested 47 candle scents. Only 3 sold.")
    _, second_person, _ = grade("You should test your candle scents before selling.")

    # Assert
    assert first_person["hook"] > second_person["hook"]


def test_number_in_first_line_raises_hook_score():
    # Arrange / Act
    _, with_number, _ = grade("I emailed 200 customers. 14 replied.")
    _, without_number, _ = grade("I emailed a lot of customers. Some replied.")

    # Assert
    assert with_number["hook"] >= without_number["hook"]


def test_fixes_lead_with_the_hook_when_hook_is_weak():
    # Act
    _, dims, fixes = grade(WEAK_POST)

    # Assert — the first recommendation should target the hook (50% of the score)
    assert fixes
    assert "hook" in fixes[0].lower() or "line 1" in fixes[0].lower()


def test_score_is_bounded_to_100():
    # Act
    score, dims, _ = grade(STRONG_POST)

    # Assert
    assert 0 <= score <= 100
    assert all(0 <= v <= 10 for v in dims.values())
