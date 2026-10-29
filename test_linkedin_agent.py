#!/usr/bin/env python3
"""Tests for the LinkedIn agent's pure logic — the parts that have silently
failed before (JSON parsing, gates, dedup, validation).

Runs with NO dependencies:  python3 test_linkedin_agent.py
Also works under pytest if installed:  pytest test_linkedin_agent.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from linkedin_agent.json_utils import extract_json
from linkedin_agent.stop_slop_gate import score_post, PASS_THRESHOLD
from linkedin_agent.dedup import overlaps
from linkedin_agent.engine.post_writer import (
    PostWriter, find_markdown, opener_issue, strip_markdown,
)

# A real post writer instance for validate_post (a pure method — no API client).
_pw = PostWriter.__new__(PostWriter)


# ---------- json_utils.extract_json ----------

def test_extract_json_bare_object():
    assert extract_json('{"a": 1}') == {"a": 1}

def test_extract_json_markdown_fenced():
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}

def test_extract_json_with_preamble():
    assert extract_json('Here you go:\n{"a": 1, "b": 2}') == {"a": 1, "b": 2}

def test_extract_json_array():
    assert extract_json('["x", "y"]') == ["x", "y"]

def test_extract_json_garbage_raises():
    try:
        extract_json("no json here at all")
        assert False, "should have raised"
    except ValueError:
        pass


# ---------- stop_slop_gate.score_post ----------

def test_proven_winner_passes_stop_slop():
    winner = ("I spent $18,000 and 11 years becoming a doctor. Then I quit to "
              "hold a stop sign for $19 an hour. My father did not speak to me "
              "for a month. I kept the vest.")
    score, _, _ = score_post(winner)
    assert score >= PASS_THRESHOLD, f"proven winner scored {score}"

def test_adverb_heavy_slop_fails():
    # Piles on every tell: adverbs, extremes, em-dashes, passive voice, meta-joiners
    slop = ("Honestly — and this is literally true — the journey is always "
            "shaped by what is believed. Clearly, everyone simply needs to "
            "truly take action. Furthermore, the problem is obviously that "
            "the fear becomes the cage — basically, nothing is ever certain.")
    score, _, _ = score_post(slop)
    assert score < PASS_THRESHOLD, f"slop scored {score}, expected < {PASS_THRESHOLD}"

def test_em_dashes_penalized():
    clean = "I quit medicine. I held a stop sign. I felt free."
    dashed = "I quit medicine — I held a stop sign — I felt free — finally."
    assert score_post(dashed)[0] < score_post(clean)[0]


# ---------- dedup.overlaps ----------

def test_dedup_detects_repeated_opening():
    a = "I sat in my car for 47 minutes after the second CaRMS rejection. It was cold."
    b = "I sat in my car for 47 minutes after the second CaRMS rejection. The lot emptied."
    assert overlaps(a, [b]), "should detect repeated opening"

def test_dedup_detects_signature_reuse():
    a = "The day my $18,000 gamble ended, I had spent 11 years chasing it."
    b = "It cost me $18,000 and 11 years before I walked away."
    assert overlaps(a, [b]), "should detect shared signature details"

def test_dedup_passes_fresh_post():
    a = "I sat in my car for 47 minutes after the second CaRMS rejection."
    fresh = "My landlord raised the rent the week my NAC results came back. $340 left."
    assert overlaps(fresh, [a]) == [], "fresh post should pass"


# ---------- post_writer.validate_post (the publish gates) ----------

def _story(extra=""):
    base = ("I matched into residency at 26. At 34 I was holding a stop sign in "
            "the Canadian cold for nineteen dollars an hour. My mother still "
            "tells relatives I am almost a doctor. I stopped correcting her the "
            "winter I realized the correction was for me, not them. The vest "
            "kept me warmer than the white coat ever did. ")
    return (base * 2) + extra + " What did your detour teach you? comment below"

def test_validate_accepts_first_person_story():
    v = _pw.validate_post(_story())
    assert v["valid"], v

def test_validate_blocks_second_person_opening():
    bad = "You are not afraid to leave medicine. " + _story()
    v = _pw.validate_post("You " + bad)
    assert not v["valid"]
    assert v["second_person_open"]

def test_validate_blocks_banned_phrase():
    v = _pw.validate_post(_story(extra="This will supercharge your pivot."))
    assert not v["valid"]
    assert v["banned_phrases_found"]

def test_validate_blocks_over_char_limit():
    v = _pw.validate_post("I " + ("x " * 1600) + "? comment")
    assert not v["valid"]
    assert not v["length_ok"]


# ---------- the opener hard gate ----------
# 0 of the last 130 published posts opened with "I "/"My " even though
# winning_patterns.json has recommended exactly that since it was first built.
# The old check only rejected second-person openers; it never required
# first-person, and it lstripped "*#" so a bold title slipped through.

def test_opener_gate_accepts_first_person_with_number():
    assert opener_issue("I was 34 and still paying $890 a month.") == ""

def test_opener_gate_accepts_my_with_time():
    assert opener_issue("My last shift ended at 6:40am on a Tuesday.") == ""

def test_opener_gate_accepts_named_place():
    assert opener_issue("I stood at the crosswalk on Bank Street in the cold.") == ""

def test_opener_gate_rejects_bold_title():
    assert opener_issue("**The Weight I Carried**\n\nI stood there.") != ""

def test_opener_gate_rejects_abstract_first_person():
    assert opener_issue("I learned something important that changed everything.") != ""

def test_opener_gate_rejects_second_person():
    assert opener_issue("You need to stop waiting for permission.") != ""

def test_opener_gate_rejects_empty():
    assert opener_issue("") != ""

def test_validate_blocks_non_first_person_opening():
    v = _pw.validate_post("Three years ago something changed. " + _story())
    assert not v["valid"]
    assert not v["opener_ok"]


# ---------- markdown must never reach the composer ----------
# LinkedIn has no markdown renderer: "**Bold Title**" publishes with the
# asterisks visible. 178 posts shipped that way (median 35 impressions vs 49
# for plain openers; 34 vs 44 within Jul-Sep alone).

def test_strip_removes_bold():
    assert strip_markdown("**The Weight**\n\nI stood there.").startswith("The Weight")
    assert "*" not in strip_markdown("**The Weight**\n\nI stood there.")

def test_strip_removes_heading_lines():
    out = strip_markdown("# LinkedIn — safe-place\n\n## Hook\n\nMy shift ended.")
    assert "#" not in out
    assert "Hook" in out

def test_strip_removes_links_keeping_text_and_url():
    out = strip_markdown("I paid $890. See [the map](https://x.com/a).")
    assert "[" not in out and "](" not in out
    assert "the map" in out and "https://x.com/a" in out

def test_strip_removes_rules_backticks_and_fences():
    out = strip_markdown("I paid $890.\n\n---\n\n```\nx\n```\n\nUse `code` now.")
    assert "---" not in out and "`" not in out
    assert "\n\n\n" not in out, "collapsed blank lines"

def test_strip_leaves_clean_post_untouched():
    clean = "I was 34 and still paying $890 a month.\n\nIt took two years.\n\n#IMG #CaRMS"
    assert strip_markdown(clean) == clean

def test_strip_preserves_hashtags():
    assert "#IMG" in strip_markdown("I quit at 34.\n\n#IMG #CaRMS #MedicalCareers")

def test_find_markdown_flags_destructive_cases():
    assert find_markdown("**bold**")
    assert find_markdown("## Hook")
    assert find_markdown("[t](https://x.com)")
    assert find_markdown("I was 34 and paid $890. #IMG") == []

def test_validate_blocks_surviving_markdown():
    v = _pw.validate_post("**I matched at 26.** " + _story())
    assert not v["valid"]
    assert v["markdown_found"]


def _run():
    fns = [g for n, g in sorted(globals().items()) if n.startswith("test_") and callable(g)]
    passed = failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {fn.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ {fn.__name__}: ERROR {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if _run() else 1)
