#!/usr/bin/env python3
"""
Demand Discovery - Customized for Creator Services
Find opportunities for services YOU can actually build/sell:
- LinkedIn content creation
- YouTube→Social repurposing
- Email automation
- Content auditing
- Video templates
- Personal brand consulting
- Trading bot services
"""

import os
import json
import re
from datetime import datetime
from dataclasses import dataclass, asdict
import praw
from anthropic import Anthropic

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT", "DemandDiscoveryAgent/1.0"),
)

client = Anthropic()

# YOUR TARGET MARKETS
TARGET_SUBREDDITS = [
    "solopreneur",      # People building solo businesses
    "Entrepreneur",     # Want to grow on LinkedIn/socials
    "freelance",        # Service providers, content creators
    "ContentCreators",  # Video creators, YouTubers
    "EmailMarketing",   # Email sequence marketers
]

# Services YOU could provide
YOUR_SERVICES = {
    "linkedin_content": {
        "name": "Done-for-You LinkedIn Content",
        "keywords": ["linkedin", "post", "growth", "audience", "engagement", "viral"],
        "your_value": "You have the 30K formula + tested hooks",
        "model": "Done-for-you service or template",
        "price_range": "$500-2000/month or $97-297 template",
    },
    "youtube_repurposing": {
        "name": "YouTube→Social Repurposing",
        "keywords": ["youtube", "tiktok", "reels", "repurpose", "transcript", "clip"],
        "your_value": "You built TubeonAI pipeline, Remotion templates",
        "model": "Service: $99-499/video or Template library",
        "price_range": "$99-499/video or $297 template pack",
    },
    "email_automation": {
        "name": "Email Sequence Automation",
        "keywords": ["email", "automation", "nurture", "flow", "sequence", "drip"],
        "your_value": "You built Encharge flows for fear audit",
        "model": "Template library or done-for-you automation",
        "price_range": "$197-497 templates or $500-1500/setup",
    },
    "content_audit": {
        "name": "Content Quality Audit Service",
        "keywords": ["audit", "review", "quality", "feedback", "improve", "slop"],
        "your_value": "You built /stop-slop scoring system",
        "model": "SaaS tool or audit service",
        "price_range": "$29-99/mo or $199-399/audit",
    },
    "video_templates": {
        "name": "Customizable Video Templates",
        "keywords": ["video", "template", "remotion", "animation", "edit", "creator"],
        "your_value": "You have Remotion + 30 days of April/March templates",
        "model": "Template library (TikTok, Instagram, LinkedIn, YouTube)",
        "price_range": "$47-197/template set",
    },
    "brand_positioning": {
        "name": "Personal Brand Positioning Service",
        "keywords": ["personal brand", "positioning", "niche", "audience", "authority"],
        "your_value": "You built the Crosswalk movement + IMG pivot strategy",
        "model": "1-1 coaching or group workshop",
        "price_range": "$997-2997 for positioning + content plan",
    },
    "trading_signals": {
        "name": "Trading Alert Service (Minervini Rules)",
        "keywords": ["trading", "signals", "alert", "stock", "minervini", "scanner"],
        "your_value": "You built the Minervini bot with all power-ups",
        "model": "SaaS subscription or signal service",
        "price_range": "$49-199/month",
    },
}

@dataclass
class ServiceOpportunity:
    """Represents a service opportunity YOU could offer."""
    id: str
    subreddit: str
    title: str
    text: str
    upvotes: int
    comments: int
    url: str
    author: str
    created_utc: float

    # Analysis
    matches_your_services: list  # Which services match this need
    problem_description: str      # What do they actually need
    willingness_to_pay: str       # Estimated price they'd pay
    urgency: str                  # How badly they need it
    market_size_estimate: str     # Total addressable market
    your_edge: str               # Why you're better positioned
    score: int = 0


def match_your_services(title: str, text: str) -> dict:
    """
    Check which of YOUR services this problem matches.
    Returns matched services + relevance score.
    """
    full_text = f"{title} {text}".lower()
    matches = {}

    for service_id, service_info in YOUR_SERVICES.items():
        # Check keyword matches
        keyword_matches = sum(1 for kw in service_info["keywords"] if kw in full_text)

        if keyword_matches >= 2:  # Need at least 2 keywords to count
            matches[service_id] = {
                "service_name": service_info["name"],
                "relevance": min(keyword_matches / len(service_info["keywords"]), 1.0),
                "your_value": service_info["your_value"],
                "model": service_info["model"],
                "price_range": service_info["price_range"],
            }

    return matches


def evaluate_opportunity_for_you(opportunity: ServiceOpportunity) -> ServiceOpportunity:
    """
    Use Claude to evaluate how well this matches your capabilities + market.
    """

    prompt = f"""
A creator/business owner is asking this on Reddit:

Title: {opportunity.title}
Description: {opportunity.text[:500]}

I'm considering offering them one of these services:
{json.dumps({k: v['name'] for k, v in YOUR_SERVICES.items()}, indent=2)}

Evaluate:
1. Which service(s) match this need best?
2. What do they really need (core problem)?
3. How badly do they need this (1-10 urgency)?
4. What would they realistically pay?
5. Total market size (how many people have this problem)?
6. Why would I be better positioned than existing solutions?

Respond as JSON:
{{
  "matched_services": ["service_id1", "service_id2"],
  "core_problem": "what they really need in 1 sentence",
  "urgency": 7,
  "willingness_to_pay": "$500-2000/month or one-time $297",
  "market_size": "10,000-50,000 creators in this niche",
  "your_edge": "You understand creator pain points + have built solution before"
}}
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        result = json.loads(response.content[0].text)

        matched = result.get("matched_services", [])
        opportunity.matches_your_services = matched
        opportunity.problem_description = result.get("core_problem", "")
        opportunity.urgency = f"{result.get('urgency', 5)}/10"
        opportunity.willingness_to_pay = result.get("willingness_to_pay", "Unknown")
        opportunity.market_size_estimate = result.get("market_size", "Unknown")
        opportunity.your_edge = result.get("your_edge", "")

        # Score it
        if matched:
            base_score = opportunity.upvotes + (opportunity.comments * 2)
            urgency_mult = result.get("urgency", 5) / 5
            opportunity.score = int(base_score * urgency_mult)
        else:
            opportunity.score = 0

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error evaluating: {e}")
        opportunity.score = 0

    return opportunity


def scrape_for_your_market(limit: int = 100):
    """
    Scrape subreddits looking specifically for problems YOU can solve.
    """
    all_opportunities = []

    print(f"🔍 Searching for opportunities in {len(TARGET_SUBREDDITS)} subreddits...\n")

    for subreddit_name in TARGET_SUBREDDITS:
        print(f"  Scanning r/{subreddit_name}...")
        subreddit = reddit.subreddit(subreddit_name)

        try:
            for submission in subreddit.new(limit=limit):
                # Quick filter: only look at posts that might be asking for help/services
                text = f"{submission.title} {submission.selftext}".lower()
                if any(word in text for word in ["help", "need", "looking", "want", "how", "anyone", "struggling", "service", "tool"]):

                    opp = ServiceOpportunity(
                        id=submission.id,
                        subreddit=subreddit_name,
                        title=submission.title,
                        text=submission.selftext[:1000],
                        upvotes=submission.ups,
                        comments=submission.num_comments,
                        url=f"https://reddit.com{submission.permalink}",
                        author=submission.author.name if submission.author else "[deleted]",
                        created_utc=submission.created_utc,
                    )

                    # Check if it matches your services
                    matches = match_your_services(opp.title, opp.text)
                    if matches:
                        opp.matches_your_services = list(matches.keys())
                        # Quick eval before Claude call
                        opp.score = (opp.upvotes + opp.comments * 2) * (len(matches) / len(YOUR_SERVICES))
                        all_opportunities.append(opp)

        except Exception as e:
            print(f"  ⚠️  Error scanning r/{subreddit_name}: {e}")
            continue

    print(f"\n✅ Found {len(all_opportunities)} posts mentioning services you could offer\n")
    return all_opportunities


def deep_evaluate(opportunities: list) -> list:
    """
    Run Claude evaluation on each opportunity.
    """
    evaluated = []

    print("📊 Deep evaluating opportunities with Claude...\n")
    for i, opp in enumerate(opportunities, 1):
        print(f"  [{i}/{len(opportunities)}] {opp.title[:50]}...", end=" ")

        evaluated_opp = evaluate_opportunity_for_you(opp)

        if evaluated_opp.score > 0:
            print(f"✓ Score: {evaluated_opp.score}")
        else:
            print("✗")

        if evaluated_opp.matches_your_services:
            evaluated.append(evaluated_opp)

    # Sort by score
    evaluated.sort(key=lambda x: x.score, reverse=True)
    return evaluated


def display_winners(winners: list):
    """Show your actual revenue opportunities."""
    print("\n" + "="*120)
    print("🚀 SERVICE OPPORTUNITIES FOR YOU".center(120))
    print("="*120 + "\n")

    for i, opp in enumerate(winners[:10], 1):
        service_names = [YOUR_SERVICES[s]["name"] for s in opp.matches_your_services]

        print(f"{i}. {opp.title}")
        print(f"   {'─'*116}")
        print(f"   Services: {', '.join(service_names)}")
        print(f"   Market: {opp.market_size_estimate}")
        print(f"   They'd pay: {opp.willingness_to_pay}")
        print(f"   Urgency: {opp.urgency} | Your edge: {opp.your_edge}")
        print(f"   Problem: {opp.problem_description}")
        print(f"   Engagement: {opp.upvotes} 👍 {opp.comments} 💬")
        print(f"   → {opp.url}\n")


def create_action_plan(opp: ServiceOpportunity) -> str:
    """
    Generate a concrete action plan for turning this into revenue.
    """

    prompt = f"""
I found this market opportunity:

**Person asking:** r/{opp.subreddit}
**Their problem:** {opp.problem_description}
**They'd pay:** {opp.willingness_to_pay}
**Market size:** {opp.market_size_estimate}

**Services I could offer:**
{json.dumps({s: YOUR_SERVICES[s]['name'] for s in opp.matches_your_services}, indent=2)}

Create a 2-week action plan to turn this into a revenue stream:

1. **Validation (Days 1-3):**
   - How to reach 10 people with this need
   - What to ask them
   - How to test willingness to pay

2. **MVP (Days 4-10):**
   - Minimum viable version of the service
   - What to build vs what to do manually
   - How to deliver it to first customer

3. **Launch (Days 11-14):**
   - How to find first customers
   - Pricing strategy
   - Go-to-market channel
   - What's your competitive advantage

Be specific and actionable.
"""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def run_your_discovery():
    """Run the full discovery optimized for YOUR services."""

    print("🎯 Demand Discovery for YOUR Services")
    print("="*120)
    print(f"Looking for: {', '.join([v['name'] for v in YOUR_SERVICES.values()])}\n")

    # Step 1: Scrape
    opportunities = scrape_for_your_market(limit=80)

    if not opportunities:
        print("No matching opportunities found in first pass.")
        return

    # Step 2: Deep evaluate
    winners = deep_evaluate(opportunities)

    if not winners:
        print("No high-confidence opportunities found.")
        return

    # Step 3: Display
    display_winners(winners)

    # Step 4: Create action plan for top opportunity
    if winners:
        print("\n" + "="*120)
        print(f"📋 ACTION PLAN FOR: {winners[0].title}".center(120))
        print("="*120 + "\n")

        action_plan = create_action_plan(winners[0])
        print(action_plan)

    # Step 5: Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_found": len(winners),
        "opportunities": [
            {
                **asdict(opp),
                "services": [YOUR_SERVICES[s]["name"] for s in opp.matches_your_services],
            }
            for opp in winners
        ]
    }

    with open("your_service_opportunities.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n💾 Results saved to your_service_opportunities.json")

    return winners


if __name__ == "__main__":
    print("\n")
    winners = run_your_discovery()
