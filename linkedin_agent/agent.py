import json
import os

# Add parent directories to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_agent.config import RESEARCH_FILE, DATA_DIR

# Import all components
from linkedin_agent.engine.voice_engine import VoiceEngine
from linkedin_agent.engine.research_engine import ResearchEngine
from linkedin_agent.engine.hook_generator import HookGenerator
from linkedin_agent.engine.post_writer import PostWriter
from linkedin_agent.engine.infographic import InfographicEngine
from linkedin_agent.scheduler import Scheduler
from linkedin_agent.notifier import Notifier

class LinkedInAgent:
    def __init__(self):
        self.voice_engine = VoiceEngine()
        self.research_engine = ResearchEngine()
        self.hook_generator = HookGenerator()
        self.post_writer = PostWriter()
        self.infographic_engine = InfographicEngine()
        self.scheduler = Scheduler()
        self.notifier = Notifier()

    def run_voice_only(self) -> dict:
        """Run only the voice profile building."""
        print("\n[AGENT] Running voice profile rebuild...")
        voice_profile = self.voice_engine.build_voice_profile()
        return {"success": bool(voice_profile)}

    def run_research_only(self) -> dict:
        """Run only the daily research."""
        print("\n[AGENT] Running daily research scan...")
        research = self.research_engine.run_daily_research()
        self.research_engine.print_research_brief(research)
        return {"success": True, "research": research}

    def run_full_pipeline(self, dry_run: bool = False, pain_point: str = None,
                          scheduled_for: str = None, arm: str = None) -> dict:
        """Run the complete daily pipeline.

        pain_point / scheduled_for / arm: explicit overrides for batch mode
        (each post gets a distinct theme, day-part slot, and experiment arm).
        When None, falls back to per-run rotation / next-8am / hour-based arm.
        """
        print("\n" + "="*60)
        print("LINKEDIN AI AGENT - FULL PIPELINE")
        print("="*60)

        result = {
            "success": False,
            "voice_profile_loaded": False,
            "research_done": False,
            "post_written": False,
            "validation_passed": False,
            "image_generated": False,
            "scheduled": False,
            "hook": None,
            "pain_point": None,
            "scheduled_data": {}
        }

        try:
            # Step 1: Load voice profile
            print("\n[1/7] Loading voice profile...")
            voice_profile = self.voice_engine.load_voice_profile()
            if voice_profile:
                result["voice_profile_loaded"] = True
                print("✓ Voice profile loaded")
            else:
                print("✗ Failed to load voice profile")
                return result

            # Step 2: Run daily research
            print("\n[2/7] Running daily research...")
            research = self.research_engine.get_daily_research()
            result["research_done"] = True
            self.research_engine.print_research_brief(research)

            # Extract pain point — rotate per RUN (date + hour) so multiple
            # posts per day each get a different topic
            pain_points = research.get("synthesis", {}).get("top_pain_points", [])
            if not pain_points:
                print("✗ No pain points found in research")
                return result

            if not pain_point:
                from datetime import datetime
                now = datetime.now()
                rotation_index = (now.date().toordinal() * 24 + now.hour) % len(pain_points)
                pain_point = pain_points[rotation_index].get("pain_point", "IMG career challenges")
                print(f"  Pain point {rotation_index + 1}/{len(pain_points)} (per-run rotation)")
            else:
                print(f"  Pain point (batch): {pain_point}")
            result["pain_point"] = pain_point

            # Step 3: Generate hook
            print("\n[3/7] Generating hook...")
            self.hook_generator = HookGenerator(voice_profile, research)
            hook = self.hook_generator.generate_and_select_best_hook(pain_point)
            result["hook"] = hook

            # Step 4: Write post — assign an experiment arm so the loop can
            # DISCOVER what drives shares, not just confirm the known format
            print("\n[4/7] Writing post with 3 QA rounds...")
            from linkedin_agent.experiment import assign_arm, arm_instruction, ACTIVE_EXPERIMENT
            arm = arm or assign_arm()
            print(f"  Experiment '{ACTIVE_EXPERIMENT}' arm: {arm}")
            result["experiment"] = ACTIVE_EXPERIMENT
            result["arm"] = arm
            self.post_writer = PostWriter(voice_profile)
            post_result = self.post_writer.write_with_3_qa_rounds(
                hook, pain_point, experiment_instruction=arm_instruction(arm)
            )
            result["post_written"] = post_result.get("success", False)
            result["validation_passed"] = post_result.get("validation", {}).get("valid", False)

            if not result["post_written"]:
                print("✗ Post writing failed")
                return result

            post_content = post_result.get("post")

            # Append the comment-to-DM CTA AFTER the stop-slop scoring above, so
            # the opt-in line never affects the post's quality score. Sendpilot
            # watches comments for the keyword and auto-DMs the Fear Audit link.
            #
            # ONCE PER DAY ONLY: Sendpilot needs a manual per-post automation and
            # has no "all posts" option, so only the FIRST post each day carries
            # the FEAR CTA (you wire that single post). The other ~4 daily posts
            # stay clean engagement/reach posts.
            from linkedin_agent.config import COMMENT_DM_ENABLED, COMMENT_DM_CTAS
            from datetime import datetime as _dt
            from pathlib import Path as _Path

            _cta_state = _Path("linkedin_agent/data/last_comment_cta.txt")
            _today = _dt.now().strftime("%Y-%m-%d")
            _already_today = _cta_state.exists() and _cta_state.read_text().strip() == _today

            if (COMMENT_DM_ENABLED and post_content and COMMENT_DM_CTAS
                    and not _already_today and not dry_run):
                cta = COMMENT_DM_CTAS[_dt.now().toordinal() % len(COMMENT_DM_CTAS)]
                if "comment fear" not in post_content.lower():
                    post_content = f"{post_content.rstrip()}\n\n{cta}"
                    _cta_state.write_text(_today)
                    print("  + comment-to-DM CTA added (today's FEAR post — wire this one in Sendpilot)")

            # Step 5: Generate infographic
            print("\n[5/7] Generating infographic...")
            image_path = self.infographic_engine.generate_infographic(hook, pain_point)
            if image_path:
                result["image_generated"] = True
            else:
                print("⚠ Infographic generation skipped (shot-scraper not available)")

            # Step 6: Schedule post
            print("\n[6/7] Scheduling post...")
            if dry_run:
                print("(DRY RUN - not actually scheduling)")
                result["scheduled_data"] = {
                    "post_id": "dry-run-id",
                    "scheduled_for": "2026-05-29T08:00:00"
                }
                result["scheduled"] = False
            else:
                # Schedule post — backends handle their own image upload
                schedule_result = self.scheduler.schedule_post(
                    post_content,
                    image_path=image_path if result["image_generated"] else None,
                    scheduled_for=scheduled_for,
                )
                result["scheduled"] = schedule_result.get("success", False)
                result["scheduled_data"] = schedule_result

                if result["scheduled"]:
                    # Log the scheduled post (full text + experiment arm for the
                    # learning join)
                    self.scheduler.log_scheduled_post(
                        schedule_result, hook, pain_point, post_content,
                        experiment=result.get("experiment"), arm=result.get("arm")
                    )

            # Step 7: Notify
            print("\n[7/7] Sending notification...")
            result["success"] = result["scheduled"] or dry_run

        except Exception as e:
            print(f"\n✗ Agent error: {e}")
            import traceback
            traceback.print_exc()
            result["success"] = False

        return result

    def execute(self, voice_only: bool = False, research_only: bool = False, dry_run: bool = False) -> dict:
        """Main execution method with flexible modes."""
        try:
            if voice_only:
                return self.run_voice_only()
            elif research_only:
                return self.run_research_only()
            else:
                result = self.run_full_pipeline(dry_run=dry_run)
                # Always notify at the end
                self.notifier.notify(result)
                return result
        except Exception as e:
            print(f"✗ Fatal agent error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
