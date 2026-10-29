import json
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from linkedin_agent.config import VOICE_PROFILE_FILE, VOICE_PROFILE_CACHE_DAYS, LINKEDIN_ACCOUNT_ID, DATA_DIR
from linkedin_agent.json_utils import extract_json
from ai_client_factory import get_ai_client
from zernio_client import ZernioClient

class VoiceEngine:
    def __init__(self):
        self.provider, self.client = get_ai_client()
        self.zernio = ZernioClient()

    def should_rebuild_voice_profile(self) -> bool:
        """Check if voice profile is stale (> 7 days old)."""
        if not os.path.exists(VOICE_PROFILE_FILE):
            return True

        mtime = os.path.getmtime(VOICE_PROFILE_FILE)
        age = datetime.now() - datetime.fromtimestamp(mtime)
        return age > timedelta(days=VOICE_PROFILE_CACHE_DAYS)

    def fetch_past_posts(self, limit: int = 100) -> list:
        """Fetch last 100 LinkedIn posts from Zernio."""
        print(f"  Fetching {limit} past LinkedIn posts from Zernio...")
        try:
            response = self.zernio.list_posts(
                account_id=LINKEDIN_ACCOUNT_ID,
                limit=limit
            )

            # Handle different response formats
            if isinstance(response, dict):
                posts = response.get("data", response.get("posts", []))
            elif isinstance(response, list):
                posts = response
            else:
                posts = []

            linkedin_posts = []
            if isinstance(posts, list):
                for post in posts:
                    if not isinstance(post, dict):
                        continue
                    # Extract LinkedIn content from platforms array
                    platforms = post.get("platforms", [])
                    for platform in platforms:
                        if isinstance(platform, dict) and platform.get("platform") == "linkedin":
                            content = platform.get("customContent", "")
                            linkedin_posts.append({
                                "post_id": post.get("_id") or post.get("id"),
                                "content": content,
                                "scheduled_at": post.get("scheduledFor")
                            })
                            break

            print(f"  Found {len(linkedin_posts)} past LinkedIn posts")
            return linkedin_posts
        except Exception as e:
            print(f"  Error fetching posts: {e}")
            import traceback
            traceback.print_exc()
            return []

    def analyze_voice_profile(self, posts: list) -> dict:
        """Use Claude Opus to analyze 100 posts and extract voice fingerprint."""
        if not posts:
            print("  No posts to analyze")
            return {}

        # Combine all post content
        combined_posts = "\n\n---\n\n".join([p["content"] for p in posts[:100]])

        system_prompt = """You are a linguistic and brand voice analyst.
Analyze the provided LinkedIn posts to extract the unique voice and style of this creator.
Focus on:
1. Tone and personality (formal, casual, inspirational, analytical, etc.)
2. Recurring sentence structures and patterns
3. Favorite vocabulary and phrases
4. Emotional appeals used most frequently
5. The 5 most common post structures (hook → body → CTA pattern)
6. Signature linguistic quirks

Return your analysis as a JSON object with these keys:
- tone: string (brief description)
- vocabulary_examples: list of 10-15 common words/phrases
- sentence_patterns: list of 3-5 structural patterns
- recurring_phrases: list of 5-10 phrases that appear frequently
- emotional_triggers: list of 3-5 emotions/appeals used
- structural_templates: list of 5 post structure templates (hook → body → cta)
- linguistic_quirks: list of unique speech patterns
- avg_sentence_length: number
- complexity_level: "simple" | "moderate" | "complex"
- hashtag_style: string describing how hashtags are used"""

        user_message = f"""Analyze this creator's LinkedIn post corpus and extract their voice fingerprint:

{combined_posts[:15000]}

Return ONLY valid JSON, no markdown formatting, no extra text."""

        print(f"  Analyzing voice profile with {self.provider.upper()}...")
        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=2000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}]
                )
            else:
                response = self.client.create(
                    messages=[{"role": "user", "content": user_message}],
                    system=system_prompt,
                    max_tokens=2000
                )

            # Extract JSON from response (tolerates markdown fences/preamble)
            response_text = response.content[0].text
            profile = extract_json(response_text)
            return profile
        except Exception as e:
            print(f"  Error analyzing voice: {e}")
            return {}

    def build_voice_profile(self) -> dict:
        """Build complete voice profile from scratch."""
        print("Building voice profile...")
        posts = self.fetch_past_posts()
        profile = self.analyze_voice_profile(posts)

        if profile:
            # Add metadata
            profile["generated_at"] = datetime.now().isoformat()
            profile["posts_analyzed"] = len(posts)

            # Save to file
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(VOICE_PROFILE_FILE, "w") as f:
                json.dump(profile, f, indent=2)

            print(f"✓ Voice profile saved to {VOICE_PROFILE_FILE}")
            return profile
        else:
            print("✗ Failed to build voice profile")
            return {}

    def load_voice_profile(self) -> dict:
        """Load voice profile from cache or rebuild if stale.

        If the rebuild fails (API error, parse error), fall back to the
        stale cached profile rather than failing the whole pipeline.
        """
        if os.path.exists(VOICE_PROFILE_FILE) and not self.should_rebuild_voice_profile():
            print(f"Loading voice profile from cache ({VOICE_PROFILE_FILE})...")
            with open(VOICE_PROFILE_FILE, "r") as f:
                return json.load(f)

        profile = self.build_voice_profile()
        if profile:
            return profile

        if os.path.exists(VOICE_PROFILE_FILE):
            print("⚠ Rebuild failed — falling back to stale cached voice profile")
            with open(VOICE_PROFILE_FILE, "r") as f:
                return json.load(f)

        return {}
