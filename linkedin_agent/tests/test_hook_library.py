"""Tests for the viral hook framework library (pure data + selectors)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from linkedin_agent.engine.hook_library import (
    HOOK_LIBRARY, CATEGORY_ORDER, DEFAULT_CATEGORIES,
    pick_categories, frameworks_block, all_templates,
)


def test_library_is_a_substantial_framework_set():
    # Assert — a meaningful chunk of the 100-hook pack is ported
    assert len(all_templates()) >= 60
    assert set(CATEGORY_ORDER) == set(HOOK_LIBRARY)


def test_numbers_theme_picks_the_receipt_category():
    # Act
    cats = pick_categories("I tested 47 things and only 3 worked", limit=2)

    # Assert
    assert "receipt" in cats


def test_opinion_theme_picks_contrarian():
    # Act
    cats = pick_categories("most people think prevention is wrong", limit=2)

    # Assert
    assert "contrarian" in cats


def test_vague_theme_falls_back_to_account_proven_defaults():
    # Act
    cats = pick_categories("a thing that happened", limit=2)

    # Assert — never empty; biased to first-person/story defaults
    assert cats
    assert cats[0] in DEFAULT_CATEGORIES


def test_frameworks_block_is_injectable_and_self_contained():
    # Act
    block = frameworks_block("the day I stopped chasing residency", categories=2)

    # Assert
    assert "PROVEN HOOK FRAMEWORKS" in block
    assert "First-3-words test" in block
    # Safe to concatenate even on an empty theme
    assert isinstance(frameworks_block(""), str)
