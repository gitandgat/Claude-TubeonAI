"""
Read the 5/day vs 2/day frequency experiment.

Groups posts by day, sums impressions per day, then buckets days by ISO-week
parity (even week = 5/day "high" arm, odd week = 2/day "low" arm) and reports
which arm produced more TOTAL daily reach. Run after ~3-4 weeks of data.

Run: python3 freq_experiment_results.py
"""

import datetime
from collections import defaultdict

from linkedin_agent.engine.learning_engine import LearningEngine


def post_date(p: dict) -> str:
    for k in ("scheduledFor", "scheduled_for", "date", "createdAt"):
        v = p.get(k)
        if v:
            return str(v)[:10]
    return ""


def arm_for_date(iso_date: str) -> str:
    y, m, d = (int(x) for x in iso_date.split("-"))
    week = datetime.date(y, m, d).isocalendar()[1]
    return "high (5/day)" if week % 2 == 0 else "low (2/day)"


def main() -> None:
    posts = LearningEngine().latest_state_per_post()
    per_day = defaultdict(lambda: {"impressions": 0, "count": 0})
    for p in posts:
        d = post_date(p)
        if not d:
            continue
        per_day[d]["impressions"] += p.get("impressions", 0)
        per_day[d]["count"] += 1

    arms = defaultdict(lambda: {"days": 0, "impressions": 0, "posts": 0})
    for d, stats in per_day.items():
        arm = arm_for_date(d)
        arms[arm]["days"] += 1
        arms[arm]["impressions"] += stats["impressions"]
        arms[arm]["posts"] += stats["count"]

    print(f"Frequency experiment — {len(per_day)} days of data\n")
    if not per_day:
        print("No data yet. Re-run after a few weeks of posting.")
        return

    for arm in ("high (5/day)", "low (2/day)"):
        a = arms.get(arm)
        if not a or a["days"] == 0:
            print(f"{arm}: no days yet")
            continue
        per_day_reach = a["impressions"] / a["days"]
        per_post = a["impressions"] / a["posts"] if a["posts"] else 0
        print(
            f"{arm}: {a['days']} days | {per_day_reach:,.0f} impressions/day "
            f"| {per_post:,.0f} per post | {a['posts'] / a['days']:.1f} posts/day"
        )

    hi = arms.get("high (5/day)", {})
    lo = arms.get("low (2/day)", {})
    if hi.get("days") and lo.get("days"):
        hi_reach = hi["impressions"] / hi["days"]
        lo_reach = lo["impressions"] / lo["days"]
        winner = "5/day" if hi_reach >= lo_reach else "2/day"
        print(f"\nVERDICT: {winner} wins on total daily reach "
              f"({hi_reach:,.0f} vs {lo_reach:,.0f}). Lock it via LINKEDIN_FREQ_EXPERIMENT=0 + set LINKEDIN_DAILY_LIMIT.")
    else:
        print("\nNeed at least one full high-week AND one low-week before a verdict.")


if __name__ == "__main__":
    main()
