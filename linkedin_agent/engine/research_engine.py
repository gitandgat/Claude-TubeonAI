import json
import os
from datetime import datetime

# Add parent directories to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from linkedin_agent.config import RESEARCH_FILE, DATA_DIR
from linkedin_agent.json_utils import extract_json
from ai_client_factory import get_ai_client
from linkedin_agent.clients.reddit_client import RedditClient
from linkedin_agent.clients.linkedin_scraper import LinkedInScraper

class ResearchEngine:
    def __init__(self):
        self.provider, self.client = get_ai_client()
        self.reddit = RedditClient()
        self.linkedin = LinkedInScraper()

    def fetch_research_data(self) -> dict:
        """Fetch raw data from Reddit and LinkedIn."""
        print("Fetching research data...")
        print("  Scanning Reddit...")
        reddit_posts = self.reddit.fetch_all_target_subreddits()
        filtered_reddit = self.reddit.filter_by_keywords(reddit_posts)
        pain_points = self.reddit.extract_pain_points(filtered_reddit)

        print("  Scanning LinkedIn viral posts...")
        linkedin_templates = self.linkedin.fetch_viral_post_templates()

        return {
            "reddit_posts": filtered_reddit[:20],
            "reddit_pain_points": pain_points,
            "linkedin_templates": linkedin_templates,
            "fetched_at": datetime.now().isoformat()
        }

    def synthesize_research(self, data: dict) -> dict:
        """Use Claude Haiku to synthesize research into actionable brief."""
        reddit_pain_points = data.get("reddit_pain_points", [])
        linkedin_templates = data.get("linkedin_templates", [])

        # If no data collected, use fallback pain points based on Crosswalk Wisdom ICP
        # (10 topics so multiple daily posts rotate without repeating)
        if not reddit_pain_points and not linkedin_templates:
            default_pain_points = [
                ("Stuck in low-level medical work with no career progression",
                 "Trapped and underutilized", "The credential ceiling nobody explains"),
                ("Sunk cost paralysis after years of investment",
                 "Fear of losing what you've already invested", "Sunk costs aren't real costs"),
                ("Burnout from cultural and workplace isolation",
                 "Exhaustion from fighting invisible barriers", "The exhaustion nobody sees"),
                ("Identity crisis: who am I if not a doctor?",
                 "Losing the self built around the white coat", "The identity cage"),
                ("Family pressure to keep trying for residency",
                 "Shame and obligation toward parents who sacrificed", "Whose dream are you living?"),
                ("Another CaRMS/match rejection cycle looming",
                 "Dread of re-applying with worsening odds", "The match lottery nobody audits"),
                ("Watching former classmates advance while you stand still",
                 "Comparison grief and falling behind", "Their residency isn't your timeline"),
                ("The endless exam treadmill (MCCQE, NAC, English tests)",
                 "Paying and studying with no guaranteed payoff", "When preparation becomes procrastination"),
                ("Financial strain of low-wage survival jobs while credentialed",
                 "Two degrees, minimum wage, mounting debt", "The economics nobody shows you"),
                ("Fear of starting over in a new field at 30+",
                 "Feeling too old and too invested to pivot", "Starting over isn't starting from zero"),
            ]
            return {
                "top_pain_points": [
                    {
                        "pain_point": pain,
                        "emotional_core": core,
                        "hook_angle": angle,
                        "interest_level": "high",
                        "source": "default"
                    }
                    for pain, core, angle in default_pain_points
                ],
                "trending_now": "IMG career transitions and overcoming the 4-layer sunk cost trap",
                "content_opportunity": "Position the pivot as an investment in the right direction, not a loss of the past"
            }

        reddit_summary = json.dumps(reddit_pain_points, indent=2)
        linkedin_summary = json.dumps(linkedin_templates, indent=2)

        system_prompt = """You are a research synthesis expert for a LinkedIn content creator targeting international medical graduates (IMGs).
Your job is to identify the TOP pain points your ICP (ideal customer profile) cares about RIGHT NOW.

The ICP is: Canadian IMGs, stuck in low-level jobs, dealing with sunk cost fallacy, 4-layer career trap, wanting to pivot.

From the provided Reddit and LinkedIn data, extract:
1. Top 3-5 pain points your ICP is discussing
2. The emotional core of each pain point
3. A strong hook/angle for each (how to approach it)
4. Estimated audience size/interest level

Return ONLY valid JSON with this structure:
{
  "top_pain_points": [
    {
      "pain_point": "string",
      "emotional_core": "string",
      "hook_angle": "string",
      "interest_level": "high" | "medium" | "low",
      "source": "reddit or linkedin"
    }
  ],
  "trending_now": "string - the single biggest trend right now",
  "content_opportunity": "string - specific angle to attack"
}"""

        user_message = f"""Reddit pain points extracted from this week's top posts:
{reddit_summary}

LinkedIn viral post templates (hooks that are working):
{linkedin_summary}

Synthesize this into the TOP 3-5 pain points and content angles for our IMG audience."""

        print(f"Synthesizing research with {self.provider.upper()}...")
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
            research = extract_json(response_text)
            return research
        except Exception as e:
            print(f"Error synthesizing research: {e}")
            # Return fallback pain points
            return {
                "top_pain_points": [
                    {
                        "pain_point": "Sunk cost trap in medical career",
                        "emotional_core": "Fear of wasted investment",
                        "hook_angle": "The trap nobody talks about",
                        "interest_level": "high",
                        "source": "fallback"
                    }
                ],
                "trending_now": "IMG career pivots",
                "content_opportunity": "Break the sunk cost narrative"
            }

    def run_daily_research(self) -> dict:
        """Run full daily research pipeline."""
        print("Starting daily research scan...")
        raw_data = self.fetch_research_data()
        synthesis = self.synthesize_research(raw_data)

        # Save results
        research_output = {
            "generated_at": datetime.now().isoformat(),
            "synthesis": synthesis,
            "raw_data_summary": {
                "reddit_posts_found": len(raw_data.get("reddit_posts", [])),
                "linkedin_templates_found": len(raw_data.get("linkedin_templates", []))
            }
        }

        os.makedirs(DATA_DIR, exist_ok=True)
        with open(RESEARCH_FILE, "w") as f:
            json.dump(research_output, f, indent=2)

        print(f"✓ Research saved to {RESEARCH_FILE}")
        return research_output

    def get_daily_research(self) -> dict:
        """Get today's research (run fresh daily)."""
        return self.run_daily_research()

    def print_research_brief(self, research: dict):
        """Print human-readable research brief."""
        synthesis = research.get("synthesis", {})
        print("\n" + "="*60)
        print("DAILY RESEARCH BRIEF")
        print("="*60)

        trending = synthesis.get("trending_now")
        if trending:
            print(f"\n🔥 Trending now: {trending}\n")

        opportunity = synthesis.get("content_opportunity")
        if opportunity:
            print(f"💡 Content opportunity: {opportunity}\n")

        pain_points = synthesis.get("top_pain_points", [])
        if pain_points:
            print("Top pain points:\n")
            for i, point in enumerate(pain_points, 1):
                print(f"{i}. {point.get('pain_point')}")
                print(f"   Hook: {point.get('hook_angle')}")
                print(f"   Interest level: {point.get('interest_level')}\n")

        print("="*60)
