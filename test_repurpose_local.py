"""Tests for the local repurpose fallback's pure helpers (no AI required)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest

from repurpose_local import derive_title, format_output, SECTION_RULE
from prompts import PLATFORMS


def test_explicit_title_wins():
    assert derive_title("anything here", "My Title", "file.txt") == "My Title"


def test_title_falls_back_to_first_source_line():
    src = "\n\nThe Sunk Cost Trap\nmore body text\n"
    assert derive_title(src, None, None) == "The Sunk Cost Trap"


def test_title_falls_back_to_filename_then_default():
    assert derive_title("   ", None, "/x/the_big_idea.txt") == "The Big Idea"
    assert derive_title("", None, None) == "Repurposed Content"


def test_format_output_matches_pipeline_layout():
    # Act
    out = format_output("My Title", [("LinkedIn Post", "hello world"),
                                     ("Facebook Post", "hi there")])

    # Assert — header, ruled blocks, labels, content all present in order
    assert out.startswith("# My Title\n")
    assert out.count(SECTION_RULE) == 4          # 2 rules per section
    assert "## LinkedIn Post" in out
    assert "## Facebook Post" in out
    assert out.index("LinkedIn Post") < out.index("Facebook Post")
    assert "hello world" in out and "hi there" in out


def test_all_seven_platforms_are_defined():
    # The fallback depends on prompts.PLATFORMS — guard the contract.
    assert len(PLATFORMS) == 7
    for spec in PLATFORMS.values():
        assert "label" in spec and "prompt" in spec
