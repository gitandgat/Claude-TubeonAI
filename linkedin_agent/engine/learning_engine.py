"""Learning engine.

Reads the analytics snapshot history, figures out what actually wins on this
account, and writes winning_patterns.json — which the post writer reads to bias
generation toward proven patterns. No human in the loop.

Grounded in the Jun 2026 finding: on this LinkedIn account, first-person
personal narrative with specific numbers does 100-300x the reach of abstract
second-person advice. This engine re-derives that from live data each run, so
the lesson updates itself as new posts land.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from linkedin_agent.config import (
    ANALYTICS_HISTORY_FILE, WINNING_PATTERNS_FILE, DATA_DIR,
    TOP_HOOKS_COUNT, HIT_IMPRESSIONS, DUD_IMPRESSIONS, SCHEDULE_LOG_FILE,
)
from linkedin_agent.engine.analytics_engine import AnalyticsEngine


def _fingerprint(text: str) -> str:
    """Normalized opening — stable join key between schedule log and analytics."""
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())[:60]


def _first_line(text: str) -> str:
    """The opening line — the hook — trimmed."""
    for line in (text or "").split("\n"):
        line = line.strip()
        if line:
            return line[:160]
    return ""


def _opening_voice(text: str) -> str:
    """Classify the opening as first_person / second_person / other."""
    head = _first_line(text).lower()
    if re.match(r"^(i |i'|my |we |we'|me |here's how i|the day i)", head):
        return "first_person"
    if re.match(r"^(you |you'|your )", head):
        return "second_person"
    return "other"


class LearningEngine:
    def __init__(self, vertical=None):
        """vertical: optional verticals.Vertical. When set, this engine reads
        that vertical's schedule log, filters the (shared) analytics feed down to
        that vertical's own posts by content fingerprint, and writes that
        vertical's own winning_patterns.json. When None, original global behavior.
        """
        self.analytics = AnalyticsEngine()
        self.vertical = vertical
        self.schedule_log_file = (
            vertical.schedule_log_file if vertical else SCHEDULE_LOG_FILE
        )
        self.winning_patterns_file = (
            vertical.winning_patterns_file if vertical else WINNING_PATTERNS_FILE
        )

    def _vertical_fingerprints(self) -> set:
        """Fingerprints of every post in THIS vertical's schedule log.

        Used to slice the shared analytics feed down to this vertical's posts —
        the same fingerprint join the experiment summary already relies on.
        Returns None when no vertical is set (→ no filtering, global behavior).
        """
        if not self.vertical or not os.path.exists(self.schedule_log_file):
            return None
        fps = set()
        with open(self.schedule_log_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if d.get("post_text"):
                    fps.add(_fingerprint(d["post_text"]))
        return fps

    def latest_state_per_post(self) -> list:
        """Collapse the time series to one row per post = its best-known stats.

        Impressions only grow, but Zernio freezes them ~1wk in, so the max
        observed value is the most complete figure we have.
        """
        history = self.analytics.load_history()
        vertical_fps = self._vertical_fingerprints()
        best: dict = {}
        for row in history:
            pid = row.get("post_id")
            if not pid:
                continue
            # Vertical scope: keep only posts that belong to this vertical.
            if vertical_fps is not None and \
                    _fingerprint(row.get("content_preview", "")) not in vertical_fps:
                continue
            if pid not in best or row.get("impressions", 0) > best[pid].get("impressions", 0):
                best[pid] = row
        return list(best.values())

    def age_matched(self, target_hours: float, tol: float = 18.0) -> list:
        """For each post, the impressions at the snapshot closest to target_hours.

        Enables apples-to-apples comparison (e.g. impressions@24h) once the
        nightly snapshots have built up history. Returns rows with 'impressions'
        observed near that age.
        """
        history = self.analytics.load_history()
        by_post: dict = {}
        for row in history:
            pid = row.get("post_id")
            age = row.get("age_hours", -1)
            if not pid or age < 0:
                continue
            if abs(age - target_hours) > tol:
                continue
            cur = by_post.get(pid)
            if cur is None or abs(age - target_hours) < abs(cur["age_hours"] - target_hours):
                by_post[pid] = row
        return list(by_post.values())

    def experiment_results(self, posts: list) -> dict:
        """Join scheduled posts (which carry the experiment arm) to their live
        analytics by content fingerprint, then summarize performance per arm.

        Returns {experiment_name: {arm: {n, avg_impressions, avg_shares,
        avg_engagement}}}. Empty until experiment-tagged posts accumulate stats.
        """
        if not os.path.exists(self.schedule_log_file):
            return {}

        # analytics by fingerprint
        by_fp = {}
        for p in posts:
            by_fp[_fingerprint(p.get("content_preview", ""))] = p

        grouped: dict = {}
        with open(self.schedule_log_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                arm, exp = d.get("arm"), d.get("experiment")
                if not arm or not d.get("post_text"):
                    continue
                stats = by_fp.get(_fingerprint(d["post_text"]))
                if not stats:
                    continue  # no analytics for this post yet
                bucket = grouped.setdefault(exp, {}).setdefault(arm, [])
                bucket.append(stats)

        summary: dict = {}
        for exp, arms in grouped.items():
            summary[exp] = {}
            for arm, rows in arms.items():
                n = len(rows)
                summary[exp][arm] = {
                    "n": n,
                    "avg_impressions": round(sum(r.get("impressions", 0) for r in rows) / n, 1),
                    "avg_shares": round(sum(r.get("shares", 0) for r in rows) / n, 2),
                    "avg_engagement": round(
                        sum(r.get("likes", 0) + r.get("comments", 0) + r.get("shares", 0)
                            for r in rows) / n, 2),
                }
        return summary

    def build_patterns(self) -> dict:
        """Analyze the data and write winning_patterns.json."""
        posts = self.latest_state_per_post()
        if not posts:
            print("  No analytics history yet — run a snapshot first")
            return {}

        ranked = sorted(posts, key=lambda r: r.get("impressions", 0), reverse=True)

        # Format insight: average impressions by opening voice
        buckets: dict = {"first_person": [], "second_person": [], "other": []}
        for p in posts:
            buckets[_opening_voice(p.get("content_preview", ""))].append(p.get("impressions", 0))

        def avg(xs):
            return round(sum(xs) / len(xs), 1) if xs else 0.0

        fp_avg, sp_avg = avg(buckets["first_person"]), avg(buckets["second_person"])
        if fp_avg and sp_avg:
            ratio = round(fp_avg / sp_avg, 1) if sp_avg else None
            recommendation = (
                f"First-person narrative averages {fp_avg} impressions vs "
                f"{sp_avg} for second-person advice "
                f"({ratio}x). Write in first person."
            )
        else:
            recommendation = (
                "Lead with first-person personal narrative ('I...', 'My...') "
                "and concrete numbers. Avoid abstract second-person advice."
            )

        # Proven hooks = opening lines of the top posts that cleared the dud line
        proven_hooks = [
            {"hook": _first_line(p.get("content_preview", "")),
             "impressions": p.get("impressions", 0)}
            for p in ranked[:TOP_HOOKS_COUNT]
            if p.get("impressions", 0) >= DUD_IMPRESSIONS
        ]

        total_shares = sum(p.get("shares", 0) for p in posts)
        hits = [p for p in posts if p.get("impressions", 0) >= HIT_IMPRESSIONS]

        patterns = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sample_size": len(posts),
            "hit_count": len(hits),
            "format_insight": {
                "first_person_avg_impressions": fp_avg,
                "second_person_avg_impressions": sp_avg,
                "recommendation": recommendation,
            },
            "engagement_note": (
                f"Total shares across {len(posts)} posts: {total_shares}. "
                "Shares are the viral lever — engineer share/tag mechanics and "
                "track whether they move."
            ),
            "experiment_results": self.experiment_results(posts),
            "proven_hooks": proven_hooks,
            "top_posts": [
                {"impressions": p.get("impressions", 0),
                 "likes": p.get("likes", 0),
                 "comments": p.get("comments", 0),
                 "shares": p.get("shares", 0),
                 "preview": p.get("content_preview", "")[:140]}
                for p in ranked[:10]
            ],
        }

        os.makedirs(os.path.dirname(self.winning_patterns_file) or DATA_DIR, exist_ok=True)
        with open(self.winning_patterns_file, "w") as f:
            json.dump(patterns, f, indent=2)

        label = f"[{self.vertical.key}] " if self.vertical else ""
        print(f"  ✓ {label}Learned from {len(posts)} posts → {self.winning_patterns_file}")
        print(f"    {recommendation}")
        print(f"    Proven hooks captured: {len(proven_hooks)} | hits (>{HIT_IMPRESSIONS} imp): {len(hits)}")
        return patterns


def build_all_verticals() -> dict:
    """Rebuild winning_patterns.json for every vertical from the shared analytics.

    Run after a snapshot. Each vertical learns only from its own posts, so
    fitness patterns never get contaminated by IMG-career patterns.
    """
    from linkedin_agent.verticals import all_verticals
    out = {}
    for v in all_verticals():
        print(f"\n🧠 Learning patterns for [{v.key}] {v.name}...")
        out[v.key] = LearningEngine(vertical=v).build_patterns()
    return out


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"))
    LearningEngine().build_patterns()
