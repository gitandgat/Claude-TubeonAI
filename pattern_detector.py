#!/usr/bin/env python3
"""
Pattern Detector Agent
Identifies recurring demand patterns across multiple discovery cycles.
Detects when the same problem is asked repeatedly across subreddits/time.
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict
from anthropic import Anthropic

client = Anthropic()


def load_discovery_history(history_file: str = "discovery_history.json") -> list[dict]:
    """Load historical discovery cycles."""
    try:
        with open(history_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def detect_topic_clustering(opportunities: list[dict]) -> dict:
    """
    Group opportunities by topic/skill using Claude to find semantic similarity.
    Returns clusters of related problems.
    """

    titles = [opp.get("title", "Unknown") for opp in opportunities]
    skills = list(set([opp.get("skill_required", "unknown") for opp in opportunities]))

    prompt = f"""
Group these Reddit posts into semantic clusters (problems that are essentially the same or very related):

Posts:
{json.dumps(titles, indent=2)}

Available Skills: {', '.join(skills)}

Respond with a JSON object:
{{
  "clusters": [
    {{
      "name": "Cluster name (the core problem)",
      "skill": "primary skill needed",
      "posts": [list of indices from the titles array],
      "pattern_strength": "weak/medium/strong (how consistently requested)"
    }}
  ]
}}
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        result = json.loads(response.content[0].text)
        return result.get("clusters", [])
    except json.JSONDecodeError:
        return []


def calculate_pattern_frequency(cluster: dict, history: list[dict]) -> dict:
    """
    Calculate how often a problem appears across multiple discovery cycles.
    """
    cluster_name = cluster.get("name", "unknown")
    post_indices = cluster.get("posts", [])

    total_occurrences = 0
    avg_engagement = 0
    first_seen = None
    last_seen = None

    for cycle in history:
        for opp in cycle.get("opportunities", []):
            # Simplified: check if title contains cluster keywords
            if cluster_name.lower() in opp.get("title", "").lower():
                total_occurrences += 1
                avg_engagement += opp.get("upvotes", 0) + (opp.get("num_comments", 0) * 2)

                if first_seen is None:
                    first_seen = opp.get("created_utc", None)
                last_seen = opp.get("created_utc", None)

    if total_occurrences > 0:
        avg_engagement = avg_engagement / total_occurrences

    return {
        "cluster": cluster_name,
        "total_occurrences": total_occurrences,
        "avg_engagement": avg_engagement,
        "first_seen": first_seen,
        "last_seen": last_seen,
        "pattern_strength": cluster.get("pattern_strength", "medium"),
        "confidence": min(total_occurrences / 5, 1.0),  # Confidence grows with repetitions
    }


def identify_emerging_trends(current_cycle: list[dict]) -> list[dict]:
    """
    Identify problems that just started appearing (emerging demand).
    """
    prompt = f"""
Identify EMERGING trends from these Reddit posts (problems that are just starting to gain traction):

Posts:
{json.dumps([p.get('title') for p in current_cycle[:15]], indent=2)}

Return JSON:
{{
  "emerging_trends": [
    {{
      "trend": "description",
      "why_emerging": "why this is just starting to appear",
      "demand_velocity": "accelerating/stable/declining",
      "early_adopter_indicators": ["indicator 1", "indicator 2"]
    }}
  ]
}}
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        result = json.loads(response.content[0].text)
        return result.get("emerging_trends", [])
    except json.JSONDecodeError:
        return []


def run_pattern_analysis(current_cycle_file: str = "demand_discoveries.json", save_output: bool = True):
    """Run full pattern detection analysis."""

    # Load current cycle
    try:
        with open(current_cycle_file, "r") as f:
            current_data = json.load(f)
            current_opportunities = current_data.get("opportunities", [])
    except FileNotFoundError:
        print(f"❌ {current_cycle_file} not found. Run reddit_demand_scraper.py first.")
        return

    # Load history
    history = load_discovery_history()

    print("📊 Running Pattern Detection Analysis...\n")

    # Step 1: Cluster by topic
    print("1️⃣  Clustering opportunities by topic...")
    clusters = detect_topic_clustering(current_opportunities)

    # Step 2: Calculate frequency
    print("2️⃣  Calculating pattern frequency across cycles...")
    frequency_analysis = [calculate_pattern_frequency(c, history) for c in clusters]
    frequency_analysis.sort(key=lambda x: x["confidence"], reverse=True)

    # Step 3: Identify emerging trends
    print("3️⃣  Identifying emerging trends...")
    emerging = identify_emerging_trends(current_opportunities)

    # Display results
    print("\n" + "="*100)
    print("📈 PATTERN ANALYSIS RESULTS".center(100))
    print("="*100)

    print("\n🎯 TOP RECURRING PATTERNS (High Confidence):")
    for i, pattern in enumerate(frequency_analysis[:5], 1):
        if pattern["total_occurrences"] > 1:
            print(f"\n{i}. {pattern['cluster']}")
            print(f"   Occurrences: {pattern['total_occurrences']} | Avg Engagement: {pattern['avg_engagement']:.0f}")
            print(f"   Confidence: {pattern['confidence']*100:.0f}% | Strength: {pattern['pattern_strength']}")

    print("\n\n🚀 EMERGING TRENDS (Just Starting):")
    for i, trend in enumerate(emerging, 1):
        print(f"\n{i}. {trend.get('trend')}")
        print(f"   Why: {trend.get('why_emerging')}")
        print(f"   Velocity: {trend.get('demand_velocity')}")
        print(f"   Early Signals: {', '.join(trend.get('early_adopter_indicators', []))}")

    if save_output:
        output = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "pattern_detection",
            "recurring_patterns": frequency_analysis,
            "emerging_trends": emerging,
        }

        with open("pattern_analysis.json", "w") as f:
            json.dump(output, f, indent=2)

        print(f"\n💾 Pattern analysis saved to pattern_analysis.json")

    return {
        "patterns": frequency_analysis,
        "trends": emerging,
    }


if __name__ == "__main__":
    run_pattern_analysis()
