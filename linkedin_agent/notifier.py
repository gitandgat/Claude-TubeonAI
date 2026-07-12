import json
import os
from datetime import datetime

# Add parent directories to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_agent.config import RUN_LOG_FILE, DATA_DIR, NOTIFY_EMAIL, NOTIFICATION_EMAIL

# Import EnchargeClient if email notification is enabled
if NOTIFY_EMAIL:
    from encharge_client import EnchargeClient

class Notifier:
    def __init__(self):
        self.notify_email = NOTIFY_EMAIL
        if self.notify_email:
            try:
                self.encharge = EnchargeClient()
            except:
                self.encharge = None

    def create_summary(self, result: dict) -> str:
        """Create human-readable summary of the run."""
        hook = result.get("hook", "N/A")
        pain_point = result.get("pain_point", "N/A")
        scheduled_for = result.get("scheduled_data", {}).get("scheduled_for", "N/A")
        post_id = result.get("scheduled_data", {}).get("post_id", "N/A")
        success = result.get("success", False)
        skipped = result.get("scheduled_data", {}).get("skipped", False)

        if success:
            status = "✓ SUCCESS"
        elif skipped:
            status = "⏭ SKIPPED (LinkedIn slots full today — post not wasted, will run next free slot)"
        else:
            status = "✗ FAILED"

        summary = f"""
{'='*60}
LINKEDIN AI AGENT - RUN SUMMARY
{'='*60}
Timestamp: {datetime.now().isoformat()}
Status: {status}

POST DETAILS:
Hook: {hook}
Pain Point: {pain_point}

SCHEDULING:
Scheduled for: {scheduled_for}
Post ID: {post_id}

COMPONENTS:
- Voice profile: {'✓ Loaded' if result.get('voice_profile_loaded') else '✗ Failed'}
- Research: {'✓ Complete' if result.get('research_done') else '✗ Skipped'}
- Post written: {'✓ Yes' if result.get('post_written') else '✗ Failed'}
- Validation: {'✓ Passed' if result.get('validation_passed') else '✗ Failed'}
- Image generated: {'✓ Yes' if result.get('image_generated') else '✗ Failed'}
- Scheduled: {'✓ Yes' if result.get('scheduled') else '✗ Not scheduled'}

{'='*60}
Next run: 24 hours
Dashboard: www.crosswalkwisdom.com
{'='*60}
"""
        return summary

    def print_summary(self, result: dict):
        """Print summary to stdout."""
        summary = self.create_summary(result)
        print(summary)

    def log_run(self, result: dict):
        """Log run details to run_log.jsonl."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "success": result.get("success", False),
            "hook": result.get("hook"),
            "pain_point": result.get("pain_point"),
            "post_id": result.get("scheduled_data", {}).get("post_id"),
            "validation_passed": result.get("validation_passed"),
            "components": {
                "voice_profile_loaded": result.get("voice_profile_loaded"),
                "research_done": result.get("research_done"),
                "post_written": result.get("post_written"),
                "image_generated": result.get("image_generated"),
                "scheduled": result.get("scheduled")
            }
        }

        os.makedirs(DATA_DIR, exist_ok=True)
        with open(RUN_LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def send_email_notification(self, result: dict):
        """Send notification email via Encharge."""
        if not self.notify_email or not self.encharge:
            return

        hook = result.get("hook", "N/A")
        post_id = result.get("scheduled_data", {}).get("post_id", "N/A")
        success = result.get("success", False)

        subject = f"LinkedIn Post {'✓ Scheduled' if success else '✗ Failed'} - {hook[:30]}"

        body = f"""
Your LinkedIn AI Agent just ran!

Hook: {hook}
Post ID: {post_id}
Status: {'Successfully scheduled' if success else 'Failed to schedule'}

Check your Zernio dashboard for the full post: www.zernio.com

— Crosswalk Wisdom AI Agent
"""

        try:
            self.encharge.send_broadcast_email(
                subject=subject,
                body=body,
                recipient_email=NOTIFICATION_EMAIL
            )
            print(f"✓ Notification email sent to {NOTIFICATION_EMAIL}")
        except Exception as e:
            print(f"Warning: Could not send email notification: {e}")

    def notify(self, result: dict):
        """Execute full notification pipeline."""
        self.print_summary(result)
        self.log_run(result)
        if self.notify_email:
            self.send_email_notification(result)
