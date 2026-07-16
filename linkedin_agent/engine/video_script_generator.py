"""TikTok/Reels video script generator.

Generates the caption segments the Remotion TikTokReel composition renders into
a silent vertical video. The LLM's only job is to write short, punchy, FIRST-
PERSON caption lines in the proven TikTok style; timing (durationFrames) and
beat structure (hook/body/pause/cta) are assigned deterministically so pacing
is consistent.

Proven format (the 240-594 view TikTok winners use exactly this): short lines,
POV/first-person, concrete, a turn, a closing question. Same winning DNA as the
LinkedIn loop, paced for video.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from linkedin_agent.json_utils import extract_json
from ai_client_factory import get_ai_client

FPS = 30
# Snappy pace — captions cut fast (word-by-word animation fills each line).
FRAMES_PER_WORD = 11
MIN_SEGMENT_FRAMES = 26
PAUSE_FRAMES = 8
# First 3 captions are rapid-fire (≤OPENING_MAX_FRAMES each) so the opening
# ~3 seconds has 3 quick cuts — the retention-critical window.
OPENING_SEGMENTS = 3
OPENING_MAX_FRAMES = 34

VIDEO_SYSTEM_PROMPT = """You are Dr. Sahawat, an IMG who left the residency chase, writing a short TikTok/Reels script as on-screen captions.

These are CAPTIONS, not a paragraph. Each line appears on screen for a couple seconds.

RULES (proven by what gets views):
- First person, a single real moment. "I matched into residency at 26." "At 34 I held a stop sign."
- The FIRST 2 lines are the hook: 3-5 words each, MAX punch (they flash by in the first 2 seconds). e.g. "I was a doctor." / "Now I hold a stop sign."
- Remaining lines: one beat each, 4-9 words. Concrete numbers and objects ($18,000, 11 years, the yellow vest).
- Build a turn. End on a question.
- No hashtags, no emojis, no second-person advice, no AI slop.

Return ONLY a JSON array of 7-11 short caption strings, in order. No other text."""


class VideoScriptGenerator:
    def __init__(self):
        self.provider, self.client = get_ai_client()

    def _generate_lines(self, theme: str) -> list:
        user = f"""Write a 7-11 line first-person TikTok caption script on this theme:

THEME: {theme}

Return ONLY the JSON array of short caption lines."""
        try:
            if self.provider == "claude":
                resp = self.client.messages.create(
                    model="claude-haiku-4-5-20251001", max_tokens=800,
                    system=VIDEO_SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user}],
                )
            else:
                resp = self.client.create(
                    messages=[{"role": "user", "content": user}],
                    system=VIDEO_SYSTEM_PROMPT, max_tokens=800,
                )
            lines = extract_json(resp.content[0].text)
            return [str(x).strip() for x in lines if str(x).strip()] if isinstance(lines, list) else []
        except Exception as e:
            print(f"  ✗ Video script generation failed: {e}")
            return []

    @staticmethod
    def _frames_for(line: str, opening: bool = False) -> int:
        f = max(MIN_SEGMENT_FRAMES, len(line.split()) * FRAMES_PER_WORD)
        return min(f, OPENING_MAX_FRAMES) if opening else f

    def build_segments(self, theme: str) -> list:
        """Return Remotion-ready segments: [{text,type,durationFrames}].

        Hook = first 1-2 lines, CTA = last line, body = middle. The first 3
        captions are capped short (rapid cuts in the first ~3s); pauses only
        appear AFTER the opening so the hook never stalls.
        """
        lines = self._generate_lines(theme)
        if len(lines) < 4:
            return []

        segments = []
        last = len(lines) - 1
        for i, line in enumerate(lines):
            seg_type = "hook" if i < 2 else ("cta" if i == last else "body")
            opening = i < OPENING_SEGMENTS
            segments.append({"text": line, "type": seg_type,
                            "durationFrames": self._frames_for(line, opening)})
            # No pauses during the rapid opening; sparse short beats afterward
            if OPENING_SEGMENTS <= i < last and i % 2 == 0:
                segments.append({"text": "", "type": "pause", "durationFrames": PAUSE_FRAMES})
        return segments


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"))
    import json
    segs = VideoScriptGenerator().build_segments("Watching former classmates advance while you stand still")
    print(json.dumps(segs, indent=1))
    print(f"total frames: {sum(s['durationFrames'] for s in segs)} (~{sum(s['durationFrames'] for s in segs)//FPS}s)")
