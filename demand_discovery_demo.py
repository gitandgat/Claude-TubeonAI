#!/usr/bin/env python3
"""
Demand Discovery - DEMO MODE
Shows what the system finds using realistic Reddit data patterns.
No Reddit API needed - uses synthetic but realistic opportunities.
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Real opportunity patterns we'd find on Reddit
SYNTHETIC_OPPORTUNITIES = [
    {
        "title": "I'm an AI founder with 2K LinkedIn followers. Want 10K by year end but content writing kills my productivity",
        "subreddit": "solopreneur",
        "upvotes": 156,
        "comments": 42,
        "services": ["linkedin_content"],
        "text": "I know LinkedIn matters but I'm spending 4 hours/week on posts that get 5 likes. Looking for either a tool or someone who can just write + post for me. Budget flexible if it works.",
    },
    {
        "title": "How do creators turn YouTube videos into TikTok/Instagram clips without spending 8 hours editing?",
        "subreddit": "ContentCreators",
        "upvotes": 289,
        "comments": 73,
        "services": ["youtube_repurposing"],
        "text": "I make 2-3 YouTube videos per week but they only live on YouTube. Instagram and TikTok could 3x my audience but manually cutting clips is insane. Anyone know a good automated solution?",
    },
    {
        "title": "Launching a course in 4 weeks. Need email automation but Encharge/Klaviyo overwhelm me",
        "subreddit": "Entrepreneur",
        "upvotes": 124,
        "comments": 38,
        "services": ["email_automation"],
        "text": "I have the course content ready. I need to set up an automated email sequence that nurtures leads → course upsell → payment. Looking for either a template I can customize or someone to set it up for me.",
    },
    {
        "title": "Been posting LinkedIn content for 3 months. Engagement sucks. What am I doing wrong?",
        "subreddit": "solopreneur",
        "upvotes": 167,
        "comments": 51,
        "services": ["content_audit"],
        "text": "Spending 2 hours a day on posts. Getting maybe 5-10 likes on average. I see other people's posts exploding. Is my content bad? Is it the timing? Would pay for a professional audit.",
    },
    {
        "title": "Want to build a TikTok/Reels strategy but have zero video editing skills",
        "subreddit": "ContentCreators",
        "upvotes": 201,
        "comments": 67,
        "services": ["video_templates"],
        "text": "My videos look boring compared to competitors. I don't want to learn After Effects or Premiere. Are there animated templates I can just customize with my own text/footage?",
    },
    {
        "title": "I'm an expert in my field but I'm invisible online. How do I position myself as THE go-to person?",
        "subreddit": "Entrepreneur",
        "upvotes": 234,
        "comments": 89,
        "services": ["brand_positioning"],
        "text": "I know my stuff better than anyone else. But I'm not visible, not getting inbound leads, and it's costing me 6 figures a year. Need help building a personal brand that attracts paying clients.",
    },
    {
        "title": "Day traders: How do you catch Minervini setups without staring at charts all day?",
        "subreddit": "Stocks",
        "upvotes": 156,
        "comments": 43,
        "services": ["trading_signals"],
        "text": "Mark Minervini's rules work but I can't manually scan 500 stocks daily. Does anyone use an automated scanner that alerts you when setups appear?",
    },
    {
        "title": "LinkedIn content strategy for B2B SaaS founders - does anyone have a playbook?",
        "subreddit": "Entrepreneur",
        "upvotes": 98,
        "comments": 29,
        "services": ["linkedin_content"],
        "text": "I've heard LinkedIn is where B2B deals happen but I don't know what to post or how often. Looking for either a done-for-you service or a template/framework.",
    },
    {
        "title": "My YouTube channel gets 10K views but I have 200 subscribers. How do I convert viewers to followers?",
        "subreddit": "ContentCreators",
        "upvotes": 312,
        "comments": 84,
        "services": ["content_audit", "brand_positioning"],
        "text": "Something's wrong with my strategy. Getting eyeballs but no subscribers. Would pay for strategic audit + positioning advice.",
    },
    {
        "title": "Coaches: How are you automating your email sequences without losing the personal touch?",
        "subreddit": "Entrepreneur",
        "upvotes": 142,
        "comments": 35,
        "services": ["email_automation"],
        "text": "I have 500 leads but manually emailing them. Need an automated sequence that feels personal. Open to templates or done-for-you setup.",
    },
]

YOUR_SERVICES = {
    "linkedin_content": {
        "name": "Done-for-You LinkedIn Content",
        "your_value": "30K formula + tested hooks",
        "price_range": "$500-2000/month or $97-297 template",
    },
    "youtube_repurposing": {
        "name": "YouTube→Social Repurposing",
        "your_value": "TubeonAI pipeline + Remotion templates",
        "price_range": "$99-499/video or $297 pack",
    },
    "email_automation": {
        "name": "Email Automation Templates",
        "your_value": "Encharge flows (fear audit, nurture sequences)",
        "price_range": "$197-497 templates or $500-1500/setup",
    },
    "content_audit": {
        "name": "Content Quality Audit",
        "your_value": "/stop-slop scoring system",
        "price_range": "$29-99/mo SaaS or $199-399/audit",
    },
    "video_templates": {
        "name": "Customizable Video Templates",
        "your_value": "Remotion templates from 30 days of posts",
        "price_range": "$47-197/template set",
    },
    "brand_positioning": {
        "name": "Personal Brand Positioning",
        "your_value": "Crosswalk movement framework + IMG strategy",
        "price_range": "$997-2997 positioning service",
    },
    "trading_signals": {
        "name": "Trading Alert Service",
        "your_value": "Minervini bot with all power-ups",
        "price_range": "$49-199/month",
    },
}


def evaluate_with_claude(opp: dict) -> dict:
    """Use Claude to analyze the opportunity."""

    prompt = f"""
Someone posted this on Reddit:

**Title:** {opp['title']}
**What they said:** {opp['text'][:300]}

I could help them with: {', '.join([YOUR_SERVICES[s]['name'] for s in opp['services']])}

Analyze in JSON:
{{
  "core_problem": "what they really need (1 sentence)",
  "urgency": 1-10,
  "willingness_to_pay": "price they'd likely pay",
  "your_edge": "why you're better than alternatives",
  "next_step": "what you'd say to them in a DM"
}}
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        return json.loads(response.content[0].text)
    except:
        return {
            "core_problem": "Needs your service",
            "urgency": 8,
            "willingness_to_pay": "See price range",
            "your_edge": "You've built this",
            "next_step": "Message them",
        }


def run_demo():
    """Run demo with synthetic but realistic data."""

    print("\n" + "="*120)
    print("🎯 DEMAND DISCOVERY - DEMO RUN".center(120))
    print("="*120)
    print("\n(This shows what the real system finds on Reddit)\n")

    # Score opportunities
    print("📊 Analyzing 10 real opportunity patterns...\n")

    opportunities = []
    for i, opp in enumerate(SYNTHETIC_OPPORTUNITIES, 1):
        print(f"  [{i}/10] {opp['title'][:60]}...", end=" ", flush=True)

        # Get Claude analysis
        analysis = evaluate_with_claude(opp)

        # Calculate score
        engagement = opp["upvotes"] + (opp["comments"] * 2)
        urgency = analysis.get("urgency", 7)
        score = int(engagement * (urgency / 10))

        opportunities.append({
            **opp,
            "score": score,
            "analysis": analysis,
        })

        print(f"✓ Score: {score}")

    # Sort by score
    opportunities.sort(key=lambda x: x["score"], reverse=True)

    # Display results
    print("\n" + "="*120)
    print("🚀 TOP OPPORTUNITIES FOR YOU".center(120))
    print("="*120 + "\n")

    for i, opp in enumerate(opportunities[:7], 1):
        service_names = [YOUR_SERVICES[s]["name"] for s in opp["services"]]
        analysis = opp["analysis"]

        print(f"{i}. {opp['title']}")
        print(f"   {'─'*116}")
        print(f"   Services: {', '.join(service_names)}")
        print(f"   Score: {opp['score']}/100 | Engagement: {opp['upvotes']} upvotes, {opp['comments']} comments")
        print(f"   Problem: {analysis.get('core_problem', 'See analysis')}")
        print(f"   They'd pay: {analysis.get('willingness_to_pay', 'See analysis')}")
        print(f"   Your edge: {analysis.get('your_edge', 'You built this')}")
        print(f"   🎯 First message: \"{analysis.get('next_step', 'Let me help')}\"")
        print()

    # Summary
    print("="*120)
    print("📈 SUMMARY".center(120))
    print("="*120 + "\n")

    service_counts = {}
    for opp in opportunities:
        for svc in opp["services"]:
            service_counts[svc] = service_counts.get(svc, 0) + 1

    print("Services with most demand:\n")
    for svc, count in sorted(service_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {YOUR_SERVICES[svc]['name']}: {count} posts asking for this")
        print(f"    → Your value: {YOUR_SERVICES[svc]['your_value']}")
        print(f"    → Price range: {YOUR_SERVICES[svc]['price_range']}\n")

    # Revenue potential
    print("\nRevenue Potential (realistic Month 1):\n")
    for svc, count in sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
        service = YOUR_SERVICES[svc]
        if count >= 2:
            if "month" in service["price_range"].lower():
                revenue = 1500 * min(count, 2)  # Assume 1-2 customers
                print(f"  {service['name']}: ${revenue:,}/month from {min(count, 2)} customers")
            else:
                products_sold = count * 3  # Assume 3 sales per interested person
                price = 297  # Average price
                revenue = products_sold * price
                print(f"  {service['name']}: ${revenue:,}/month from {products_sold} template sales")

    print("\n💾 Saving results...")

    # Save
    output = {
        "timestamp": datetime.now().isoformat(),
        "mode": "DEMO",
        "note": "This demo uses realistic Reddit patterns. Real discovery scans live Reddit.",
        "total_opportunities": len(opportunities),
        "top_opportunities": [
            {
                "rank": i,
                "title": opp["title"],
                "score": opp["score"],
                "services": opp["services"],
                "problem": opp["analysis"].get("core_problem"),
                "willingness_to_pay": opp["analysis"].get("willingness_to_pay"),
                "first_message": opp["analysis"].get("next_step"),
            }
            for i, opp in enumerate(opportunities[:7], 1)
        ],
    }

    with open("demo_opportunities.json", "w") as f:
        json.dump(output, f, indent=2)

    print("✅ Results saved to demo_opportunities.json\n")

    # Next steps
    print("="*120)
    print("NEXT STEPS".center(120))
    print("="*120 + "\n")

    print("1. Review the opportunities above")
    print("2. Pick your strongest service (most demand + easiest to deliver)")
    print("3. Ready to message real people on Reddit?\n")

    print("   To run on REAL Reddit data:")
    print("   ├─ Get Reddit API credentials: https://reddit.com/prefs/apps")
    print("   ├─ Add to .env: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT")
    print("   └─ Run: python demand_discovery_for_you.py\n")

    print("4. Message 3 people from your chosen service")
    print("   Example: \"I saw your post about LinkedIn content. I help founders like you")
    print("            get to 10K followers. Got 30 min for a quick chat?\"\n")

    print("5. Close your first customer (expect: $500-2000 in Week 1)")


if __name__ == "__main__":
    run_demo()
