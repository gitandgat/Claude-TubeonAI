import json
import os

# Add parent directories to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from linkedin_agent.config import (
    VOICE_PROFILE_FILE, BANNED_PHRASES,
    POST_MIN_LENGTH, POST_MAX_LENGTH, POST_MAX_CHARS,
    WINNING_PATTERNS_FILE, SCHEDULE_LOG_FILE,
)
from linkedin_agent.stop_slop_gate import score_post, recommendations, PASS_THRESHOLD
from linkedin_agent.engine.hook_library import frameworks_block
from linkedin_agent.engine.virality_grader import (
    grade as grade_virality, VIRALITY_TARGET, HOOK_RESCUE_BELOW,
)
from linkedin_agent.dedup import recent_post_texts, overlaps, avoid_list
from ai_client_factory import get_ai_client

# Voice rewritten Jun 2026 from live data: on this account, first-person personal
# narrative with specific numbers gets 100-300x the reach of abstract
# second-person advice. The old "HOOK/REFRAME/advice" structure WAS the losing
# format. This prompt forces the winning one.
LINKEDIN_SYSTEM_PROMPT = """You are Dr. Sahawat, an International Medical Graduate who traded the residency chase for a different path, writing your own LinkedIn posts. You are NOT a marketer. You are a person telling true stories from your life.

⚡ SINGLE DRAFT — what you write publishes as-is.

THE ONE RULE THAT MATTERS (proven by this account's own data):
Write in FIRST PERSON about a SPECIFIC MOMENT, with CONCRETE NUMBERS and SENSORY DETAIL.
Posts that do this get 4,000-14,000 views. Abstract second-person advice ("You're not afraid...", "Courage is a circuit") gets 15-50 views. Never write the second kind.

HOW YOUR BEST POSTS ARE BUILT:
1. Open mid-scene, first person: "I sat in my car for 47 minutes after the second CaRMS rejection." / "My parents flew 13 hours to visit me in Canada."
2. Concrete numbers and objects: dollars ($18,000), years (11 years), the stop sign, the yellow vest, the white coat, the WhatsApp from your mother.
3. A turn — the moment the meaning flips.
4. One earned reflection (NOT a lecture). What you learned, said plainly, from inside the story.
5. Close with a question that invites someone to share their own version.
6. 3-5 topic hashtags (#IMG #CaRMS #MedicalCareers). Never meta-hashtags like #Hook #LinkedIn.

HARD BANS:
- No second-person sermons ("You need to...", "You're not...", "Your fear is...").
- No section labels in the post (no "HOOK:", "REFRAME:", "CTA:").
- No AI slop: unleash, dive into, game-changer, supercharge, transformative, leverage, empower, unlock, cutting edge, innovative, paradigm shift, "here's what I learned", "at the end of the day", "honestly", "literally", "let's be real".
- No abstract openers. If your first line could be a fortune cookie, rewrite it as a scene.

LENGTH: 150-350 words. Tight. Hard cap 3,000 characters or LinkedIn rejects it.
VOICE: A real person who lived it. Vulnerable, specific, unhurried."""

class PostWriter:
    def __init__(self, voice_profile: dict = None, vertical=None):
        """vertical: an optional verticals.Vertical. When None the writer keeps
        its original Crosswalk-IMG behavior (system prompt + global data files),
        so the existing agent is unchanged. When set, the writer uses that
        vertical's persona prompt, theme framing, and per-vertical learning data.
        """
        self.provider, self.client = get_ai_client()
        self.voice_profile = voice_profile or self.load_voice_profile()
        self.vertical = vertical
        self.system_prompt = vertical.system_prompt if vertical else LINKEDIN_SYSTEM_PROMPT
        self.draft_subject = (
            vertical.draft_subject if vertical else "from your life as an IMG"
        )
        self.cta_fallback = (
            vertical.cta_fallback if vertical
            else "If this hit home, share it with one IMG who needs to hear it. "
                 "And follow Crosswalk Wisdom for more."
        )
        self.winning_patterns_file = (
            vertical.winning_patterns_file if vertical else WINNING_PATTERNS_FILE
        )
        self.schedule_log_file = (
            vertical.schedule_log_file if vertical else SCHEDULE_LOG_FILE
        )
        self.patterns = self.load_winning_patterns()

    def load_voice_profile(self) -> dict:
        """Load voice profile from file."""
        try:
            with open(VOICE_PROFILE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def load_winning_patterns(self) -> dict:
        """Load data-derived winning patterns (proven hooks + format lesson)."""
        try:
            with open(self.winning_patterns_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _proven_hooks_block(self) -> str:
        """Few-shot block of THIS account's highest-reach opening lines."""
        hooks = self.patterns.get("proven_hooks", [])
        if not hooks:
            return ""
        lines = [
            f'  - ({h.get("impressions", 0):,} views) "{h.get("hook", "")}"'
            for h in hooks[:6]
        ]
        rec = self.patterns.get("format_insight", {}).get("recommendation", "")
        return (
            "YOUR OWN HIGHEST-REACH OPENERS (match this energy — first person, "
            "specific, mid-scene):\n" + "\n".join(lines) +
            (f"\n\nDATA SAYS: {rec}" if rec else "")
        )

    def round_1_draft(self, hook: str, pain_point: str, avoid: str = "",
                      experiment_instruction: str = "") -> str:
        """Round 1: Write the draft post."""
        proven = self._proven_hooks_block()
        # Ground the opening in proven viral frameworks (Blotato hook library),
        # picked from this theme/wedge. The system prompt still owns the voice;
        # this only shapes the hook pattern.
        frameworks = frameworks_block(pain_point)
        fw_block = f"\n\n{frameworks}" if frameworks else ""
        avoid_block = f"\n\nFRESHNESS (important):\n{avoid}" if avoid else ""
        exp_block = f"\n\nENDING (follow exactly): {experiment_instruction}" if experiment_instruction else ""

        user_message = f"""Write a LinkedIn post — a true first-person story {self.draft_subject} — on this theme:

THEME: {pain_point}

STARTING IMAGE (rewrite into a vivid first-person opening scene if useful, or replace with a stronger real moment): {hook}

{proven}{fw_block}{avoid_block}{exp_block}

Tell ONE specific moment. Real numbers, real objects, a turn, one honest reflection. No advice-giving, no second person."""

        print("\n[ROUND 1] Writing draft...")
        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=2000,
                    system=self.system_prompt,
                    messages=[{"role": "user", "content": user_message}]
                )
            else:
                response = self.client.create(
                    messages=[{"role": "user", "content": user_message}],
                    system=self.system_prompt,
                    max_tokens=2000
                )
            draft = response.content[0].text
            print("✓ Draft complete")
            return draft
        except Exception as e:
            print(f"Error in round 1: {e}")
            return ""

    def round_2_critique(self, draft: str) -> str:
        """Round 2: Critique the draft and identify issues."""
        critique_prompt = """Critique this LinkedIn post against these 10 criteria:

1. NO AI SLOP - Does it avoid clichés like "unleash", "dive into", "game-changer"?
2. VOICE MATCH - Does it sound like the creator (conversational, vulnerable, direct)?
3. STRUCTURAL INTEGRITY - Does it follow hook → reframe → details → lessons → brand reveal → CTA → question → hashtags?
4. ICP RELEVANCE - Does it speak specifically to IMGs struggling with career pivots?
5. HOOK STRENGTH - Is the opening hook truly scroll-stopping?
6. BODY FLOW - Do the ideas flow logically? Is it easy to follow?
7. CTA CLARITY - Is the call-to-action clear and compelling?
8. HASHTAG QUALITY - Are the hashtags relevant and not overstuffed?
9. LENGTH - Is it 600-1200 words (appropriate for the topic)?
10. EMOTIONAL PUNCH - Does it tap into real fears/aspirations of the audience?

Return a JSON object with:
{
  "issues": [{"criterion": "string", "status": "pass" | "fail", "feedback": "string"}],
  "overall_score": number (out of 100),
  "critical_fixes": ["list of critical issues to fix"],
  "strengths": ["list of what's working well"]
}"""

        print("[ROUND 2] Critiquing draft...")
        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1500,
                    system=critique_prompt,
                    messages=[{"role": "user", "content": f"Post to critique:\n\n{draft}"}]
                )
            else:
                response = self.client.create(
                    messages=[{"role": "user", "content": f"Post to critique:\n\n{draft}"}],
                    system=critique_prompt,
                    max_tokens=1500
                )
            critique_text = response.content[0].text
            print("✓ Critique complete")
            return critique_text
        except Exception as e:
            print(f"Error in round 2: {e}")
            return ""

    def round_3_final(self, draft: str, critique: str) -> str:
        """Round 3: Revise the draft based on critique."""
        revision_prompt = f"""Your job is to revise this LinkedIn post to address the critique.

ORIGINAL POST:
{draft}

CRITIQUE:
{critique}

REVISION INSTRUCTIONS:
1. Fix every critical issue mentioned in the critique
2. Strengthen the weak areas
3. Keep the voice authentic and conversational
4. Maintain the required structure
5. Remove all banned AI phrases
6. Ensure length is 600-1200 words
7. Make sure the hook is genuinely scroll-stopping
8. Double-check the CTA is clear

Write the FINAL, REVISED post. This is the version that will be published."""

        print("[ROUND 3] Revising based on critique...")
        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=2000,
                    system=self.system_prompt,
                    messages=[{"role": "user", "content": revision_prompt}]
                )
            else:
                response = self.client.create(
                    messages=[{"role": "user", "content": revision_prompt}],
                    system=self.system_prompt,
                    max_tokens=2000
                )
            final_post = response.content[0].text
            print("✓ Final revision complete")
            return final_post
        except Exception as e:
            print(f"Error in round 3: {e}")
            return draft

    def fix_banned_phrases(self, post: str, issues: list) -> str:
        """One rewrite pass that removes flagged words/phrases, keeping everything else."""
        fix_prompt = f"""Rewrite this LinkedIn post, changing ONLY one thing: remove or replace these words/phrases: {issues}

Keep every other sentence, the structure, the line breaks, and the hashtags exactly as they are. Replace each flagged word with a plain, natural alternative or simply delete it if it's filler.

Return ONLY the rewritten post, nothing else.

POST:
{post}"""

        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": fix_prompt}]
                )
            else:
                response = self.client.create(
                    messages=[{"role": "user", "content": fix_prompt}],
                    max_tokens=2000
                )
            return response.content[0].text.strip()
        except Exception as e:
            print(f"Fix pass failed: {e}")
            return ""

    def fix_stop_slop(self, post: str, recs: list) -> str:
        """Targeted rewrite to clear stop-slop issues while keeping the story."""
        if not recs:
            return ""
        rec_text = "; ".join(recs)
        fix_prompt = f"""This is a first-person LinkedIn story. Keep the story, the specific numbers, the voice, and the structure exactly. Make ONLY these line-edits to remove AI-writing tells: {rec_text}.

Do not add advice. Do not switch to second person. Do not pad it. Return ONLY the edited post.

POST:
{post}"""
        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=2000,
                    system=self.system_prompt,
                    messages=[{"role": "user", "content": fix_prompt}],
                )
            else:
                response = self.client.create(
                    messages=[{"role": "user", "content": fix_prompt}],
                    system=self.system_prompt,
                    max_tokens=2000,
                )
            return response.content[0].text.strip()
        except Exception as e:
            print(f"Stop-slop fix pass failed: {e}")
            return ""

    def fix_hook(self, post: str, fixes: list) -> str:
        """Rewrite ONLY the opening line(s) into a stronger first-person scene.

        The hook is 50% of the virality score, so a weak opener caps the whole
        post. Keeps the body, numbers, voice, and hashtags intact.
        """
        if not fixes:
            return ""
        fix_text = "; ".join(fixes)
        fix_prompt = f"""This first-person LinkedIn story has a weak opening. Rewrite ONLY the first 1-2 lines so they open mid-scene in first person with a concrete number or object, and pass the first-3-words test. Apply: {fix_text}.

Keep the rest of the post, the specific numbers, the voice, the structure, and the hashtags exactly as they are. Do not switch to second person. Do not add advice. Return ONLY the edited post.

POST:
{post}"""
        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=2000,
                    system=self.system_prompt,
                    messages=[{"role": "user", "content": fix_prompt}],
                )
            else:
                response = self.client.create(
                    messages=[{"role": "user", "content": fix_prompt}],
                    system=self.system_prompt,
                    max_tokens=2000,
                )
            return response.content[0].text.strip()
        except Exception as e:
            print(f"Hook rescue pass failed: {e}")
            return ""

    def validate_post(self, post: str) -> dict:
        """Validate the final post against quality criteria."""
        word_count = len(post.split())
        char_count = len(post)

        # Check for banned phrases (strict enforcement)
        banned_found = []
        for phrase in BANNED_PHRASES:
            if phrase.lower() in post.lower():
                banned_found.append(phrase)

        # Check for AI slop patterns
        slop_patterns = [
            r"(?i)\bcheck out\b",
            r"(?i)\btap into\b",
            r"(?i)\bshould be doing\b",
            r"(?i)\bneed to be doing\b",
            r"(?i)\bdon't sleep on\b",
            r"(?i)\btrip\b.*\bwire\b",
            r"(?i)essential reading",
            r"(?i)game theory",
            r"(?i)food for thought",
        ]

        import re
        slop_found = []
        for pattern in slop_patterns:
            match = re.search(pattern, post)
            if match:
                slop_found.append(match.group(0))

        # Template artifacts: section labels and meta-hashtags that belong to
        # the prompt structure, never to a published post
        template_patterns = [
            r"(?im)^\**\s*(HOOK|REFRAME|LESSONS|INSIGHTS|BRAND REVEAL|CTA|CLOSING QUESTION|HASHTAGS|SENSORY[^:\n]*)\s*\**\s*:",
            r"#(LinkedIn|Hook|Reframe|CTA|BrandReveal|ClosingQuestion|Hashtags|Post)\b",
        ]
        for pattern in template_patterns:
            for match in re.finditer(pattern, post):
                slop_found.append(match.group(0))

        # Check structure — accept any CTA verb the system prompt allows
        cta_signals = ["www.", "click", "comment", "save this", "share this",
                       "share it", "repost", "follow", "calculator", "dm me",
                       "send this", "tag someone", "link in"]
        post_lower = post.lower()
        has_cta = any(signal in post_lower for signal in cta_signals)
        has_question = "?" in post

        all_issues = banned_found + slop_found

        length_ok = (POST_MIN_LENGTH <= word_count <= POST_MAX_LENGTH
                     and char_count <= POST_MAX_CHARS)

        # Stop-slop score (canonical 5-dimension, /50, pass >= 35)
        slop_score, slop_dims, slop_issue_counts = score_post(post)
        slop_pass = slop_score >= PASS_THRESHOLD

        # Virality scorecard (advisory — hook weighted 50%). Pure-function, no API.
        # Deliberately NOT part of `valid`, so it can never empty a live slot; it
        # only informs the hook-rescue pass and the logged summary.
        virality_score, virality_dims, virality_fixes = grade_virality(post)

        # First-person opening is the PROVEN reach driver (18.2x). Stop-slop
        # doesn't catch second-person advice (it's mechanically clean), so
        # enforce the format separately. Find the first real line.
        first_line = next((ln.strip().lstrip("*# ").lower()
                           for ln in post.split("\n") if ln.strip()), "")
        import re as _re
        first_person_open = bool(_re.match(
            r"^(i |i'|my |we |we'|the day i|the year i|the night i|the morning i)",
            first_line))
        second_person_open = bool(_re.match(r"^(you |you'|your )", first_line))

        validation = {
            "word_count": word_count,
            "char_count": char_count,
            "length_ok": length_ok,
            "banned_phrases_found": banned_found,
            "slop_patterns_found": slop_found,
            "all_issues": all_issues,
            "banned_phrases_ok": len(banned_found) == 0,
            "slop_ok": len(slop_found) == 0,
            "stop_slop_score": slop_score,
            "stop_slop_pass": slop_pass,
            "stop_slop_recommendations": recommendations(slop_issue_counts),
            "first_person_open": first_person_open,
            "second_person_open": second_person_open,
            "has_cta": has_cta,
            "has_closing_question": has_question,
            "virality_score": virality_score,
            "virality_dims": virality_dims,
            "virality_fixes": virality_fixes,
            "virality_pass": virality_score >= VIRALITY_TARGET,
            "valid": (
                length_ok and
                len(banned_found) == 0 and
                len(slop_found) == 0 and
                slop_pass and
                not second_person_open and
                has_cta and
                has_question
            )
        }

        return validation

    def write_with_3_qa_rounds(self, hook: str, pain_point: str,
                               experiment_instruction: str = "") -> dict:
        """Execute lean 1-round draft pipeline (cost-optimized)."""
        print(f"\n{'='*60}")
        print("POST WRITING PIPELINE - SINGLE DRAFT (COST-OPTIMIZED)")
        print(f"{'='*60}")

        # Single round: Draft only (no critique/revision)
        draft = self.round_1_draft(hook, pain_point,
                                   experiment_instruction=experiment_instruction)
        if not draft:
            return {"success": False, "post": "", "validation": {}}

        final_post = draft

        # Validate
        validation = self.validate_post(final_post)

        # One fix pass: if banned phrases / slop slipped through, rewrite
        # to remove them instead of discarding the whole generation
        if not validation["valid"] and validation["all_issues"]:
            print(f"⚠ Banned phrases detected {validation['all_issues']} — running fix pass")
            fixed = self.fix_banned_phrases(final_post, validation["all_issues"])
            if fixed:
                final_post = fixed
                validation = self.validate_post(final_post)

        # If the ONLY failure is a missing CTA, append the standard brand
        # CTA instead of discarding the whole generation
        if not validation["valid"] and not validation["has_cta"] and \
                validation["length_ok"] and validation["banned_phrases_ok"] and \
                validation["slop_ok"] and validation["has_closing_question"]:
            print("⚠ No CTA detected — appending standard brand CTA")
            # Insert CTA before hashtags if present, else append
            cta_line = self.cta_fallback
            lines = final_post.rstrip().split("\n")
            hashtag_index = next(
                (i for i, line in enumerate(lines) if line.strip().startswith("#")),
                None
            )
            if hashtag_index is not None:
                lines.insert(hashtag_index, cta_line + "\n")
                final_post = "\n".join(lines)
            else:
                final_post = final_post.rstrip() + "\n\n" + cta_line
            validation = self.validate_post(final_post)

        # Stop-slop gate: if it scores below 35/50, run one targeted rewrite
        # against the specific issues, then re-score. Applies to EVERY post.
        if not validation.get("stop_slop_pass", True):
            print(f"⚠ Stop-slop {validation['stop_slop_score']}/50 (<{PASS_THRESHOLD}) — running stop-slop rewrite")
            recs = validation.get("stop_slop_recommendations", [])
            fixed = self.fix_stop_slop(final_post, recs)
            if fixed:
                new_val = self.validate_post(fixed)
                # Only keep the rewrite if it actually improved the score
                if new_val["stop_slop_score"] >= validation["stop_slop_score"]:
                    final_post, validation = fixed, new_val

        # Hook rescue: the hook is 50% of virality. If the post is otherwise valid
        # but its hook scores below the rescue threshold, run ONE targeted opening
        # rewrite. Advisory-only — it never blocks publish, only upgrades a winner.
        v_dims = validation.get("virality_dims", {})
        if validation.get("valid") and v_dims.get("hook", 10) < HOOK_RESCUE_BELOW:
            print(f"⚠ Weak hook (virality {validation['virality_score']}/100, "
                  f"hook {v_dims['hook']}/10) — running hook rescue")
            rescued = self.fix_hook(final_post, validation.get("virality_fixes", []))
            if rescued:
                new_val = self.validate_post(rescued)
                if new_val["valid"] and \
                        new_val["virality_score"] >= validation["virality_score"]:
                    final_post, validation = rescued, new_val
                    print(f"  ✓ Hook upgraded → virality {validation['virality_score']}/100")

        # Repetition guard: the model recycles openings/details. If this post
        # overlaps recent ones IN THIS VERTICAL, regenerate ONCE with an
        # avoid-list. (Per-vertical log → fitness posts don't dedup against IMG.)
        recent = recent_post_texts(self.schedule_log_file, n=20)
        repeat_reasons = overlaps(final_post, recent)
        if repeat_reasons:
            print(f"⚠ Repetition detected: {repeat_reasons[0]} — regenerating with avoid-list")
            regen = self.round_1_draft(hook, pain_point, avoid=avoid_list(recent),
                                       experiment_instruction=experiment_instruction)
            if regen and not overlaps(regen, recent):
                regen_val = self.validate_post(regen)
                if regen_val["valid"]:
                    final_post, validation = regen, regen_val
                    print("  ✓ Fresh version accepted")

        print(f"\n{'='*60}")
        print("VALIDATION RESULT - STRICT ANTI-SLOP CHECK (1-ROUND DRAFT)")
        print(f"{'='*60}")
        print(f"Word count: {validation['word_count']} (target: {POST_MIN_LENGTH}-{POST_MAX_LENGTH})")
        print(f"Char count: {validation['char_count']} (LinkedIn max: {POST_MAX_CHARS})")
        print(f"Length OK: {'✓' if validation['length_ok'] else '✗'}")
        print(f"Banned phrases: {validation['banned_phrases_found'] or 'None ✓'}")
        print(f"AI slop patterns: {validation['slop_patterns_found'] or 'None ✓'}")
        print(f"Stop-slop score: {validation['stop_slop_score']}/50 {'✓' if validation['stop_slop_pass'] else '✗ <'+str(PASS_THRESHOLD)}")
        print(f"Virality score: {validation['virality_score']}/100 (hook {validation['virality_dims']['hook']}/10) {'✓' if validation['virality_pass'] else '~ advisory'}")
        print(f"First-person open: {'✓' if validation['first_person_open'] else ('✗ SECOND-PERSON' if validation['second_person_open'] else '~ neutral')}")
        print(f"Has CTA: {'✓' if validation['has_cta'] else '✗'}")
        print(f"Has closing question: {'✓' if validation['has_closing_question'] else '✗'}")
        print(f"READY TO PUBLISH: {'✓ YES' if validation['valid'] else '✗ NEEDS REWRITE'}")
        print(f"{'='*60}\n")

        return {
            "success": validation["valid"],
            "post": final_post,
            "validation": validation,
            "hook": hook,
            "pain_point": pain_point
        }
