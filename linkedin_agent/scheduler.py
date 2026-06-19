import json
import os
from datetime import datetime, time
from pytz import timezone

# Add parent directories to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_agent.config import (
    ZERNIO_API_KEY, LINKEDIN_ACCOUNT_ID, LINKEDIN_SCHEDULE_TIME,
    LINKEDIN_SCHEDULE_TZ, LINKEDIN_FIRST_COMMENT, LINKEDIN_DAILY_LIMIT,
    SCHEDULE_LOG_FILE, DATA_DIR, PUBLISH_VIA
)
from linkedin_agent.engine.platform_cta import apply_crosspost_cta
from zernio_client import ZernioClient

try:
    from linkedin_full_automation import LinkedInFullAutomation
    LINKEDIN_API_AVAILABLE = True
except ImportError:
    LINKEDIN_API_AVAILABLE = False

class Scheduler:
    def __init__(self, linkedin_account_id: str = None):
        """linkedin_account_id: target Zernio account. Defaults to the in-house
        account (existing behavior). Pass a client's account id to post for a
        managed-service client instead."""
        self.zernio = ZernioClient()
        self.linkedin_account_id = linkedin_account_id or LINKEDIN_ACCOUNT_ID
        self.tz = timezone(LINKEDIN_SCHEDULE_TZ)

        # Direct LinkedIn publishing via the proven LinkedInFullAutomation
        # (fetches author URN from /userinfo at runtime). Built lazily so a
        # bad token doesn't break Scheduler construction.
        #
        # SAFETY: the direct token belongs to the IN-HOUSE account only. Never
        # enable it for a client account or a client's post would publish under
        # our identity. So gate it on the account being the in-house one.
        self.linkedin_api = None
        access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        if (LINKEDIN_API_AVAILABLE and access_token
                and self.linkedin_account_id == LINKEDIN_ACCOUNT_ID):
            try:
                automation = LinkedInFullAutomation(access_token)
                if automation.author_urn:
                    self.linkedin_api = automation
                else:
                    print("⚠ LinkedIn token can't resolve author URN. Falling back to Zernio.")
            except Exception as e:
                print(f"⚠ LinkedIn API unavailable ({e}). Falling back to Zernio.")

    def check_daily_limit(self) -> bool:
        """Check if we've already scheduled 5 posts today."""
        try:
            today = datetime.now(self.tz).date().isoformat()
            response = self.zernio.list_posts(account_id=self.linkedin_account_id)

            # Normalize response envelope ({"data": [...]} / {"posts": [...]} / bare list)
            if isinstance(response, dict):
                posts = response.get("data", response.get("posts", []))
            else:
                posts = response if isinstance(response, list) else []

            count_today = 0
            for post in posts:
                if not isinstance(post, dict):
                    continue
                scheduled_at = post.get("scheduledFor", "")
                if scheduled_at.startswith(today):
                    count_today += 1

            from linkedin_agent.config import current_daily_limit, current_frequency_arm
            limit = current_daily_limit()
            arm = current_frequency_arm()
            if count_today >= limit:
                print(f"✗ Daily limit reached: {count_today}/{limit} posts today (freq arm: {arm})")
                return False
            else:
                print(f"✓ Daily limit check: {count_today}/{limit} posts today (freq arm: {arm})")
                return True
        except Exception as e:
            print(f"Warning: Could not check daily limit: {e}")
            return True  # Proceed anyway

    def upload_image(self, image_path: str) -> str:
        """Upload image to Zernio CDN and return public URL."""
        if not os.path.exists(image_path):
            print(f"✗ Image file not found: {image_path}")
            return None

        try:
            print(f"Uploading image to Zernio CDN...")
            # ZernioClient.upload_image() returns the public URL
            public_url = self.zernio.upload_image(image_path)
            if public_url:
                print(f"✓ Image uploaded: {public_url}")
                return public_url
            else:
                print("✗ Failed to upload image")
                return None
        except Exception as e:
            print(f"✗ Error uploading image: {e}")
            return None

    def get_scheduled_time(self) -> str:
        """Get the next scheduled time (8am ET tomorrow if already posted today)."""
        now = datetime.now(self.tz)
        scheduled_time = now.replace(
            hour=int(LINKEDIN_SCHEDULE_TIME.split(":")[0]),
            minute=int(LINKEDIN_SCHEDULE_TIME.split(":")[1]),
            second=0,
            microsecond=0
        )

        # If it's past 8am today, schedule for tomorrow
        if now > scheduled_time:
            from datetime import timedelta
            scheduled_time += timedelta(days=1)

        return scheduled_time.isoformat()

    def schedule_post(self, post_content: str, image_path: str = None,
                      scheduled_for: str = None, vertical=None) -> dict:
        """Publish/schedule post to LinkedIn (+ cross-post to IG/FB).

        Route controlled by PUBLISH_VIA:
          - "zernio" (default): schedule through Zernio so analytics are tracked
            (measurable, 5/day cap). This is what the learning loop reads.
          - "direct": direct LinkedIn API (no cap) but unmeasurable.

        vertical: optional verticals.Vertical. When set, its first-comment CTA is
        used and the post is cross-posted to the vertical's IG/FB accounts (only
        when an image is present — IG requires media). When None, behavior is the
        original LinkedIn-only Crosswalk path.

        scheduled_for: explicit ISO slot (for batch spreading); defaults to the
        next 8am ET.
        """
        print(f"\nScheduling post to LinkedIn (route: {PUBLISH_VIA})...")

        if PUBLISH_VIA == "direct" and self.linkedin_api and image_path and os.path.exists(image_path):
            result = self._publish_via_linkedin_api(post_content, image_path)
            if result.get("success"):
                return result
            print("Falling back to Zernio for scheduled posting...")

        return self._schedule_via_zernio(post_content, image_path, scheduled_for, vertical)

    def _publish_via_linkedin_api(self, post_content: str, image_path: str) -> dict:
        """Publish immediately via LinkedIn API (upload image, then post)."""
        from pathlib import Path
        try:
            print("Publishing via LinkedIn API (direct, no daily cap)...")

            asset_urn = self.linkedin_api.upload_image(Path(image_path))
            if not asset_urn:
                return {"success": False, "post_id": None, "error": "Image upload failed"}

            post_urn = self.linkedin_api.create_post_with_image(post_content, asset_urn)
            if post_urn:
                print("✓ Post published via LinkedIn API!")
                # Add the resource link as the first comment (conversion path).
                # Direct API posts otherwise go out with NO link to the calculator.
                self.linkedin_api.add_comment(post_urn, LINKEDIN_FIRST_COMMENT)
                return {
                    "success": True,
                    "post_id": post_urn,
                    "asset_urn": asset_urn,
                    "published_at": datetime.now(self.tz).isoformat(),
                    "image_url": image_path,
                    "source": "linkedin_api"
                }
            return {"success": False, "post_id": None, "error": "ugcPosts call failed"}

        except Exception as e:
            print(f"⚠ LinkedIn API error: {e}")
            return {"success": False, "post_id": None, "error": str(e)}

    def _schedule_via_zernio(self, post_content: str, image_path: str = None,
                             scheduled_for: str = None, vertical=None) -> dict:
        """Schedule post via Zernio (LinkedIn 5/day limit) + cross-post to IG/FB.

        The 5/day cap is LinkedIn-only (server-side, per account). IG/FB are
        separate accounts and not bound by it, so cross-posting a vertical's
        image post to them is free of the cap. IG requires media, so cross-post
        entries are only added when an image is present.
        """
        print("Using Zernio API (LinkedIn daily limit: 5 posts)...")
        image_url = self.upload_image(image_path) if image_path else None
        # Check daily limit (LinkedIn account — shared across all 5 verticals)
        if not self.check_daily_limit():
            return {"success": False, "post_id": None, "error": "Daily limit reached"}

        # Explicit slot (batch spreading) or default next 8am
        scheduled_for = scheduled_for or self.get_scheduled_time()

        first_comment = vertical.first_comment if vertical else LINKEDIN_FIRST_COMMENT

        # LinkedIn always; it carries the first-comment CTA.
        platforms = [
            {
                "platform": "linkedin",
                "accountId": self.linkedin_account_id,
                "customContent": post_content,
                "scheduledFor": scheduled_for,
                "platformSpecificData": {
                    "firstComment": first_comment
                }
            }
        ]

        # Cross-post to the vertical's IG/FB accounts — but only with an image,
        # because Instagram rejects media-less posts. No image → LinkedIn only.
        crossposted = []
        if vertical and image_url:
            for plat, account_id in vertical.crosspost.items():
                # Adapt the CTA to what THIS platform's algorithm rewards
                # (IG = saves, FB = shares) instead of reusing LinkedIn's
                # comment-question. LinkedIn entry above is left as written.
                platforms.append({
                    "platform": plat,
                    "accountId": account_id,
                    "customContent": apply_crosspost_cta(post_content, plat, vertical),
                    "scheduledFor": scheduled_for,
                })
                crossposted.append(plat)
            if crossposted:
                print(f"  + cross-posting to: {', '.join(crossposted)}")
        elif vertical and not image_url:
            print("  (no image — LinkedIn only; IG/FB skipped, they need media)")

        # Build media items if image provided
        media_items = None
        if image_url:
            media_items = [{"url": image_url, "type": "image"}]

        try:
            print(f"Sending to Zernio API...")
            # Call schedule_post with proper parameters
            response = self.zernio.schedule_post(
                content=post_content,
                scheduled_for=scheduled_for,
                timezone=LINKEDIN_SCHEDULE_TZ,
                platforms=platforms,
                media_items=media_items
            )

            # Extract post ID from response
            post_id = response.get("_id") or response.get("id") or response.get("post", {}).get("_id")

            if post_id:
                print(f"✓ Post scheduled via Zernio!")
                print(f"  Post ID: {post_id}")
                print(f"  Scheduled for: {scheduled_for}")
                return {
                    "success": True,
                    "post_id": post_id,
                    "scheduled_for": scheduled_for,
                    "image_url": image_url,
                    "crossposted": crossposted,
                    "source": "zernio"
                }
            else:
                print("✗ Failed to schedule post (no ID returned)")
                return {"success": False, "post_id": None, "error": "No post ID returned"}

        except Exception as e:
            # Zernio enforces 5 LinkedIn posts/day/account server-side. When the
            # slots are already full (e.g. a pre-scheduled batch), this is an
            # EXPECTED skip, not a failure — don't dump a scary traceback.
            body = ""
            resp = getattr(e, "response", None)
            if resp is not None:
                body = resp.text or ""
            if "daily limit" in body.lower():
                print("⏭ LinkedIn account already at 5/5 posts today — skipping (slots full)")
                return {"success": False, "skipped": True,
                        "post_id": None, "error": "daily_limit_reached"}
            print(f"✗ Error scheduling post: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "post_id": None, "error": str(e)}

    def log_scheduled_post(self, post_data: dict, hook: str, pain_point: str,
                           post_content: str = None, experiment: str = None,
                           arm: str = None, vertical=None):
        """Log scheduled post to schedule_log.jsonl for tracking.

        With a vertical, the entry goes to that vertical's own schedule log
        (linkedin_agent/data/verticals/<key>/schedule_log.jsonl) so each
        vertical's learning loop only sees its own posts. Without one, it writes
        the original global log (existing Crosswalk agent behavior).
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "post_id": post_data.get("post_id"),
            "vertical": vertical.key if vertical else None,
            "hook": hook,
            "pain_point": pain_point,
            "scheduled_for": post_data.get("scheduled_for"),
            "image_url": post_data.get("image_url"),
            "crossposted": post_data.get("crossposted", []),
            "source": post_data.get("source"),
            "experiment": experiment,
            "arm": arm,
            "post_text": post_content,
            "success": post_data.get("success")
        }

        log_file = vertical.schedule_log_file if vertical else SCHEDULE_LOG_FILE
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        print(f"✓ Schedule logged to {log_file}")
