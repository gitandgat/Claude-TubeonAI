"""Lenient JSON extraction for LLM responses.

LLMs often wrap JSON in markdown fences (```json ... ```) or add
preamble text. json.loads() on the raw response fails with
"Expecting value: line 1 column 1 (char 0)". This module extracts
the JSON payload before parsing.
"""

import json
import re


def extract_json(text: str):
    """Parse JSON from an LLM response, tolerating fences and preamble.

    Returns the parsed object (dict or list).
    Raises ValueError if no JSON can be extracted.
    """
    if not text or not text.strip():
        raise ValueError("Empty response - no JSON to extract")

    cleaned = text.strip()

    # 1. Try direct parse first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 2. Strip markdown fences: ```json ... ``` or ``` ... ```
    fence_match = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 3. Find the first { or [ and parse from there to the matching end
    for open_char, close_char in (("{", "}"), ("[", "]")):
        start = cleaned.find(open_char)
        if start == -1:
            continue
        end = cleaned.rfind(close_char)
        if end <= start:
            continue
        try:
            return json.loads(cleaned[start:end + 1])
        except json.JSONDecodeError:
            continue

    raise ValueError(f"Could not extract JSON from response: {cleaned[:200]}")
