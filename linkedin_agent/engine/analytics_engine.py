"""Analytics snapshot engine.

Zernio's /analytics endpoint (a) blends all platforms in its default response
and (b) stops refreshing a post's stats roughly a week after publishing. To run
a real learning loop we must pull the PLATFORM-FILTERED analytics (which return
the true per-platform numbers) and store our OWN daily snapshots, so we can:
  - keep a time series even after Zernio freezes the source
  - compare posts at matched ages (impressions@24h, @72h) instead of
    "3-week-old post vs 2-day-old post"
"""

import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import requests
from linkedin_agent.config import (
    ZERNIO_API_KEY, ZERNIO_BASE_URL, ANALYTICS_PLATFORM, ANALYTICS_PLATFORMS,
    ANALYTICS_HISTORY_FILE, DATA_DIR,
)


class AnalyticsEngine:
    def __init__(self, platform: str = ANALYTICS_PLATFORM):
        self.platform = platform
        self.headers = {"Authorization": f"Bearer {ZERNIO_API_KEY}"}

    def fetch_platform_analytics(self) -> list:
        """Pull platform-filtered analytics — the call that returns REAL numbers.

        The default /analytics call blends platforms and undercounts; passing
        ?platform=linkedin returns the true per-platform impressions.
        """
        try:
            resp = requests.get(
                f"{ZERNIO_BASE_URL}/analytics",
                headers=self.headers,
                params={"platform": self.platform, "period": "180d"},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json().get("posts", [])
        except Exception as e:
            print(f"  ✗ Analytics fetch failed: {e}")
            return []

    def snapshot(self) -> int:
        """Append today's analytics for every tracked post to the history file.

        Returns the number of posts snapshotted. History is append-only — each
        line is one post observed at one point in time.
        """
        posts = self.fetch_platform_analytics()
        if not posts:
            print("  No analytics returned — nothing to snapshot")
            return 0

        now = datetime.now(timezone.utc)
        os.makedirs(DATA_DIR, exist_ok=True)

        written = 0
        with open(ANALYTICS_HISTORY_FILE, "a") as f:
            for p in posts:
                a = p.get("analytics") or {}
                published_at = p.get("publishedAt") or p.get("scheduledFor") or ""
                age_hours = self._age_hours(published_at, now)
                entry = {
                    "snapshot_at": now.isoformat(),
                    "platform": self.platform,
                    "post_id": p.get("latePostId") or p.get("_id"),
                    "published_at": published_at,
                    "age_hours": age_hours,
                    "content_preview": (p.get("content") or "")[:200],
                    "impressions": a.get("impressions", 0) or 0,
                    "views": a.get("views", 0) or 0,
                    "reach": a.get("reach", 0) or 0,
                    "likes": a.get("likes", 0) or 0,
                    "comments": a.get("comments", 0) or 0,
                    "shares": a.get("shares", 0) or 0,
                    "saves": a.get("saves", 0) or 0,
                    "clicks": a.get("clicks", 0) or 0,
                    "engagement_rate": a.get("engagementRate", 0) or 0,
                    "zernio_last_updated": a.get("lastUpdated", ""),
                }
                f.write(json.dumps(entry) + "\n")
                written += 1

        print(f"  ✓ Snapshotted {written} {self.platform} posts to {ANALYTICS_HISTORY_FILE}")
        return written

    @staticmethod
    def _age_hours(published_at: str, now: datetime) -> float:
        """Hours between publish time and the snapshot. -1 if unparseable."""
        if not published_at:
            return -1.0
        try:
            pub = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            return round((now - pub).total_seconds() / 3600.0, 1)
        except Exception:
            return -1.0

    def load_history(self) -> list:
        """Read all snapshots back as a list of dicts."""
        if not os.path.exists(ANALYTICS_HISTORY_FILE):
            return []
        rows = []
        with open(ANALYTICS_HISTORY_FILE) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return rows


def snapshot_all_platforms() -> int:
    """Snapshot every platform we track (LinkedIn text + the video surfaces)."""
    total = 0
    for plat in ANALYTICS_PLATFORMS:
        total += AnalyticsEngine(platform=plat).snapshot()
    return total


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"))
    snapshot_all_platforms()
