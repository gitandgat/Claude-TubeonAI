import json
import os

# Add parent directories to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from linkedin_agent.config import VOICE_PROFILE_FILE, RESEARCH_FILE
from linkedin_agent.json_utils import extract_json
from ai_client_factory import get_ai_client

class HookGenerator:
    def __init__(self, voice_profile: dict = None, research: dict = None):
        self.provider, self.client = get_ai_client()
        self.voice_profile = voice_profile or self.load_voice_profile()
        self.research = research or self.load_research()

    def load_voice_profile(self) -> dict:
        """Load voice profile from file."""
        try:
            with open(VOICE_PROFILE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}

    def load_research(self) -> dict:
        """Load research from file."""
        try:
            with open(RESEARCH_FILE, "r") as f:
                return json.load(f)
        except:
            return {}

    def generate_10_hooks(self, pain_point: str) -> list:
        """Generate 10 scroll-stopping hooks for a given pain point."""
        voice_info = json.dumps(self.voice_profile, indent=2)

        system_prompt = """You are a LinkedIn hook writing expert.
Your job is to generate SCROLL-STOPPING hooks that make people stop mid-scroll and read the post.

Key criteria for great LinkedIn hooks:
- Pattern interrupt (unexpected, contrarian, surprising)
- Specificity (not generic)
- Emotional resonance (taps into real fear or aspiration)
- Brevity (1-2 sentences max, under 20 words ideally)
- Question or bold statement (not "here's what I learned")
- Specificity to the IMG/career-pivot audience

Return ONLY a JSON array of 10 hook strings. NO markdown, NO explanations, NO numbering."""

        user_message = f"""Pain point: {pain_point}

Creator's voice fingerprint (use this to match tone):
{voice_info}

Generate 10 unique, scroll-stopping LinkedIn hooks for this pain point.
Return only the JSON array of strings."""

        print(f"Generating 10 hooks with {self.provider.upper()}...")
        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}]
                )
            else:
                response = self.client.create(
                    messages=[{"role": "user", "content": user_message}],
                    system=system_prompt,
                    max_tokens=1000
                )

            response_text = response.content[0].text
            hooks = extract_json(response_text)
            return hooks if isinstance(hooks, list) else []
        except Exception as e:
            print(f"Error generating hooks: {e}")
            return []

    def score_hooks(self, hooks: list) -> list:
        """Score each hook against 5 criteria using Claude Haiku."""
        hooks_json = json.dumps(hooks)

        system_prompt = """You are a LinkedIn engagement expert.
Score each hook on these 5 criteria (1-10 scale):
1. Pattern interrupt (does it stop scrolling?)
2. Emotional resonance (does it tap into real pain?)
3. Specificity (is it specific, not generic?)
4. Brevity (is it short and punchy?)
5. IMG-audience fit (does it speak to international med grads?)

Return ONLY a JSON array of objects. Each object MUST have: hook, scores (with pattern_interrupt, emotional, specificity, brevity, audience_fit as integers), and total (sum of scores). NO OTHER TEXT."""

        user_message = f"""Score these hooks:
{hooks_json}

Return only the JSON array. No markdown, no explanation."""

        print(f"Scoring hooks with {self.provider.upper()}...")
        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1500,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}]
                )
            else:
                response = self.client.create(
                    messages=[{"role": "user", "content": user_message}],
                    system=system_prompt,
                    max_tokens=1500
                )

            response_text = response.content[0].text
            scored = extract_json(response_text)
            return scored if isinstance(scored, list) else []
        except ValueError as e:
            print(f"Warning: Hook scoring JSON parse failed, using first hook: {e}")
            # Return dummy scores for all hooks - just use the first one
            return [{"hook": hooks[0], "scores": {"pattern_interrupt": 10, "emotional": 10, "specificity": 10, "brevity": 10, "audience_fit": 10}, "total": 50}]
        except Exception as e:
            print(f"Error scoring hooks: {e}")
            return []

    def generate_and_select_best_hook(self, pain_point: str) -> str:
        """Generate 10 hooks and auto-select the best one."""
        print(f"\nGenerating hooks for: {pain_point}")
        hooks = self.generate_10_hooks(pain_point)

        if not hooks:
            return f"Exploring: {pain_point}"

        scored_hooks = self.score_hooks(hooks)

        if scored_hooks:
            # Find highest scoring hook
            best_hook = max(scored_hooks, key=lambda h: h.get("total", 0))
            selected = best_hook.get("hook", hooks[0])
            print(f"✓ Selected hook: {selected}")
            return selected
        else:
            # Fallback to first hook if scoring fails
            print(f"✓ Selected hook: {hooks[0]}")
            return hooks[0]
