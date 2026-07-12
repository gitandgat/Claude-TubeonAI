#!/usr/bin/env python3
"""
Reddit Demand Discovery Agent
Scrapes targeted subreddits, identifies demand signals, validates Claude-solvable opportunities.
"""

import os
import json
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional
import praw
from anthropic import Anthropic

# PRAW setup (Reddit API)
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT", "DemandDiscoveryAgent/1.0"),
)

# Anthropic setup
client = Anthropic()

TARGET_SUBREDDITS = [
    "solopreneur",
    "Entrepreneur",
    "freelance",
    "HelpMeFind",
    "SideProject",
]

@dataclass
class RedditPost:
    """Represents a Reddit post with demand signals."""
    id: str
    subreddit: str
    title: str
    selftext: str
    upvotes: int
    num_comments: int
    created_utc: float
    url: str
    author: str
    score: int = 0
    is_demand_signal: bool = False
    claude_solvable: bool = False
    demand_level: str = "low"  # low, medium, high
    skill_required: str = ""
    explanation: str = ""


def scrape_subreddit_posts(subreddit_name: str, limit: int = 100) -> list[RedditPost]:
    """
    Scrape recent posts from a subreddit.
    Focuses on posts from the last 7 days with demand intent.
    """
    posts = []
    subreddit = reddit.subreddit(subreddit_name)

    seven_days_ago = datetime.now().timestamp() - (7 * 24 * 60 * 60)

    for submission in subreddit.new(limit=limit):
        if submission.created_utc < seven_days_ago:
            break

        post = RedditPost(
            id=submission.id,
            subreddit=subreddit_name,
            title=submission.title,
            selftext=submission.selftext[:500],  # First 500 chars
            upvotes=submission.ups,
            num_comments=submission.num_comments,
            created_utc=submission.created_utc,
            url=f"https://reddit.com{submission.permalink}",
            author=submission.author.name if submission.author else "[deleted]",
        )
        posts.append(post)

    return posts


def detect_demand_intent(post: RedditPost) -> tuple[bool, str]:
    """
    Use regex patterns to detect if a post signals demand.
    Returns (is_demand_signal, intent_type)
    """
    text = f"{post.title} {post.selftext}".lower()

    patterns = {
        "tool_request": r"(anyone know|does.*exist|is there a tool|looking for a.*tool|recommendations for)",
        "service_request": r"(looking for a.*service|need help with|anyone offer|done-for-you)",
        "ai_interest": r"(ai|chatgpt|claude|automation|scraping|data extraction|summariz)",
        "pain_point": r"(struggling with|difficult|time-consuming|manual|tedious|repetitive)",
        "problem_solving": r"(how do i|how can i|what's the best way|any tips|any advice|best practice)",
    }

    detected_intents = []
    for intent_type, pattern in patterns.items():
        if re.search(pattern, text):
            detected_intents.append(intent_type)

    is_demand = len(detected_intents) >= 2  # Need at least 2 patterns to count as demand
    intent_type = ", ".join(detected_intents) if detected_intents else "general"

    return is_demand, intent_type


def evaluate_claude_solvability(post: RedditPost) -> tuple[bool, str, str]:
    """
    Use Claude to evaluate if the post describes something Claude can solve.
    Returns (is_solvable, skill_type, explanation)
    """
    prompt = f"""
You are evaluating if Claude (an AI assistant) can help solve the problem described in this Reddit post.

Post Title: {post.title}
Post Text: {post.selftext}

Determine:
1. Can Claude solve this? (yes/no)
2. What skill/service type? (e.g., "content writing", "code review", "research", "analysis", "automation", "strategy")
3. Brief explanation (1 sentence)

Respond in JSON format:
{{"solvable": true/false, "skill": "...", "explanation": "..."}}
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        result = json.loads(response.content[0].text)
        return (
            result.get("solvable", False),
            result.get("skill", "unknown"),
            result.get("explanation", "")
        )
    except (json.JSONDecodeError, IndexError):
        return False, "error", "Could not parse response"


def score_demand_level(post: RedditPost) -> str:
    """
    Score post as low/medium/high demand based on engagement + recency + intent.
    """
    engagement_score = post.upvotes + (post.num_comments * 2)

    # Recency bonus (posts in last 24h get higher score)
    age_hours = (datetime.now().timestamp() - post.created_utc) / 3600
    recency_multiplier = 1.5 if age_hours < 24 else 1.0

    adjusted_score = engagement_score * recency_multiplier

    if adjusted_score > 100:
        return "high"
    elif adjusted_score > 30:
        return "medium"
    else:
        return "low"


def validate_post(post: RedditPost) -> RedditPost:
    """
    Run full validation pipeline on a post.
    """
    # Step 1: Detect demand intent
    is_demand, intent = detect_demand_intent(post)
    post.is_demand_signal = is_demand

    if not is_demand:
        post.demand_level = "low"
        return post

    # Step 2: Evaluate Claude solvability
    solvable, skill, explanation = evaluate_claude_solvability(post)
    post.claude_solvable = solvable
    post.skill_required = skill
    post.explanation = explanation

    # Step 3: Score demand level
    post.demand_level = score_demand_level(post)

    # Step 4: Composite score
    if post.claude_solvable and post.demand_level in ["medium", "high"]:
        post.score = 100 if post.demand_level == "high" else 75
    elif post.is_demand_signal and post.claude_solvable:
        post.score = 50
    else:
        post.score = 0

    return post


def run_discovery_cycle(subreddits: list[str] = TARGET_SUBREDDITS, limit: int = 50) -> list[RedditPost]:
    """
    Run one complete discovery cycle: scrape all subreddits, validate, return winners.
    """
    all_posts = []

    print(f"🔍 Scraping {len(subreddits)} subreddits...")
    for subreddit in subreddits:
        print(f"  └─ r/{subreddit}...")
        posts = scrape_subreddit_posts(subreddit, limit=limit)
        all_posts.extend(posts)

    print(f"\n✅ Found {len(all_posts)} posts. Validating demand signals...")

    validated = []
    for i, post in enumerate(all_posts, 1):
        print(f"  [{i}/{len(all_posts)}] {post.title[:50]}...", end=" ")
        validated_post = validate_post(post)
        validated.append(validated_post)

        if validated_post.score > 0:
            print(f"✓ Score: {validated_post.score}")
        else:
            print("✗")

    # Filter and sort by score
    winners = [p for p in validated if p.score > 0]
    winners.sort(key=lambda x: x.score, reverse=True)

    return winners


def save_results(winners: list[RedditPost], filename: str = "demand_discoveries.json"):
    """Save validated opportunities to JSON."""
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_discovered": len(winners),
        "opportunities": [
            {
                **asdict(p),
                "created_utc": datetime.fromtimestamp(p.created_utc).isoformat(),
            }
            for p in winners
        ]
    }

    with open(filename, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n💾 Results saved to {filename}")
    return output


def display_winners(winners: list[RedditPost]):
    """Pretty-print top opportunities."""
    print("\n" + "="*80)
    print("🎯 TOP CLAUDE-SOLVABLE OPPORTUNITIES".center(80))
    print("="*80 + "\n")

    for i, post in enumerate(winners[:10], 1):  # Top 10
        print(f"{i}. [{post.score}/100] r/{post.subreddit}")
        print(f"   Title: {post.title}")
        print(f"   Skill: {post.skill_required} | Demand: {post.demand_level.upper()}")
        print(f"   Engagement: {post.upvotes} upvotes, {post.num_comments} comments")
        print(f"   Why: {post.explanation}")
        print(f"   Link: {post.url}\n")


if __name__ == "__main__":
    # Example usage
    print("Reddit Demand Discovery Agent")
    print(f"Subreddits: {', '.join(TARGET_SUBREDDITS)}\n")

    # Run discovery
    winners = run_discovery_cycle()

    # Display results
    if winners:
        display_winners(winners)
        save_results(winners)
    else:
        print("\n⚠️  No high-demand Claude-solvable opportunities found in this cycle.")
