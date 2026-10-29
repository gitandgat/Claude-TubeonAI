#!/usr/bin/env python3
"""
Message Templates Generator
Creates platform-specific outreach messages for each opportunity
"""

import json
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

YOUR_SERVICES = {
    "linkedin_content": {
        "name": "LinkedIn Content Service",
        "pitch": "I help founders go from 0 to 10K followers with a proven formula (tested hooks + consistency)",
        "price": "$500-2000/month",
        "benefit": "4 posts/week that get engagement",
    },
    "youtube_repurposing": {
        "name": "YouTube→Social Conversion",
        "pitch": "Turn 1 YouTube video into 8 TikToks + 2 Instagram Reels in 24 hours",
        "price": "$99-499/video",
        "benefit": "Repurpose content across platforms automatically",
    },
    "email_automation": {
        "name": "Email Automation Setup",
        "pitch": "Complete Encharge sequences that nurture leads → course/product → payment",
        "price": "$197-497 template or $500-1500 done-for-you",
        "benefit": "Done-for-you or customizable templates",
    },
    "content_audit": {
        "name": "Content Quality Audit",
        "pitch": "I audit your content with a 5-dimension scoring system (tested on 100+ posts)",
        "price": "$199-399/audit",
        "benefit": "Detailed report + 3 specific improvements",
    },
    "video_templates": {
        "name": "Video Template Library",
        "pitch": "Plug-and-play Remotion templates for TikTok/Instagram/LinkedIn",
        "price": "$47-197/template set",
        "benefit": "No editing skills needed",
    },
    "brand_positioning": {
        "name": "Personal Brand Positioning",
        "pitch": "Position yourself as THE expert in your niche (I did this for Crosswalk Wisdom)",
        "price": "$997-2997",
        "benefit": "Positioning doc + 30-post content plan",
    },
    "trading_signals": {
        "name": "Trading Alert Service",
        "pitch": "Daily Minervini setup alerts (you built this with all power-ups)",
        "price": "$49-199/month",
        "benefit": "Never miss a setup again",
    },
}

PLATFORM_STYLES = {
    "Twitter": {
        "tone": "casual, direct, use @mention",
        "max_length": 280,
        "format": "short + link to DM",
        "example": "@user Exactly! I built this. DM?"
    },
    "Quora": {
        "tone": "helpful, detailed, expert-like",
        "max_length": 500,
        "format": "answer their question + offer help",
        "example": "I solved this exact problem. Here's how... Want to chat?"
    },
    "YouTube": {
        "tone": "friendly, helpful, reply to comment",
        "max_length": 500,
        "format": "acknowledge comment + offer help",
        "example": "Great question! I actually built this. Check my profile/DM"
    },
    "Indie Hackers": {
        "tone": "founder-to-founder, casual",
        "max_length": 300,
        "format": "brief but helpful",
        "example": "I solve this exact problem. Happy to chat. Reach out?"
    },
    "Product Hunt": {
        "tone": "concise, clear, direct",
        "max_length": 250,
        "format": "comment then link",
        "example": "I do exactly this. Want to chat?"
    }
}


def generate_message(opportunity: dict, platform: str) -> dict:
    """Generate customized message for each platform."""

    service = opportunity.get("best_service", "linkedin_content")
    service_info = YOUR_SERVICES.get(service, {})
    platform_style = PLATFORM_STYLES.get(platform, PLATFORM_STYLES["Twitter"])

    prompt = f"""
Generate a SHORT, NATURAL outreach message for this opportunity.

OPPORTUNITY:
Title: {opportunity.get('title', 'Unknown')}
Platform: {platform}
Problem: {opportunity.get('problem', 'See title')}

MY SERVICE:
Name: {service_info.get('name')}
Pitch: {service_info.get('pitch')}
Price: {service_info.get('price')}
Benefit: {service_info.get('benefit')}

PLATFORM REQUIREMENTS:
Tone: {platform_style['tone']}
Max length: {platform_style['max_length']} chars
Format: {platform_style['format']}

RULES:
1. Sound like a real person, not a bot
2. Reference their specific problem (not generic)
3. Be concise
4. Include call-to-action (DM, reply, chat, etc)
5. NO LINKS (just ask them to reach out)
6. NO EMOJIS (keep professional)

Return JSON:
{{
  "message": "the exact message to send",
  "cta": "specific call-to-action",
  "length": 123,
  "notes": "any tips for sending this"
}}
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        result = json.loads(response.content[0].text)
        return result
    except:
        return {
            "message": f"Hey, I help with {service_info.get('name', 'your needs')}. Want to chat?",
            "cta": "DM me",
            "length": 80,
            "notes": "Keep it simple"
        }


def create_message_pack(opportunities: list):
    """Create a pack of ready-to-send messages."""

    print("\n" + "="*120)
    print("✉️  MESSAGE TEMPLATES GENERATOR".center(120))
    print("="*120 + "\n")

    message_pack = {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "total_templates": len(opportunities),
        "messages": []
    }

    for i, opp in enumerate(opportunities[:10], 1):
        print(f"Generating message {i}/10...", end=" ", flush=True)

        platform = opp.get("platform", "Twitter")
        message_data = generate_message(opp, platform)

        msg_entry = {
            "rank": i,
            "platform": platform,
            "title": opp.get("title", "Unknown")[:60],
            "service": opp.get("best_service", "unknown"),
            "message": message_data.get("message", ""),
            "cta": message_data.get("cta", "DM"),
            "url": opp.get("url", ""),
            "notes": message_data.get("notes", ""),
            "status": "ready_to_send",
            "sent": False,
            "response": None,
        }

        message_pack["messages"].append(msg_entry)
        print(f"✓")

    # Save
    with open("message_templates.json", "w") as f:
        json.dump(message_pack, f, indent=2)

    # Display
    print("\n" + "="*120)
    print("📋 READY-TO-SEND MESSAGES".center(120))
    print("="*120 + "\n")

    for msg in message_pack["messages"]:
        print(f"{msg['rank']}. [{msg['platform']}] {msg['title']}")
        print(f"   {'─'*116}")
        print(f"   Message: \"{msg['message']}\"")
        print(f"   Action: {msg['cta']} • {msg['url']}")
        print(f"   Status: {msg['status']} • Sent: {msg['sent']}\n")

    print("="*120)
    print("💾 Saved to message_templates.json".center(120))
    print("="*120 + "\n")

    return message_pack


def display_single_message(opp: dict):
    """Display a single message for copy-paste."""

    print(f"\n📤 COPY & PASTE READY:\n")
    print(f"Platform: {opp.get('platform')}")
    print(f"Target: {opp.get('title')[:60]}")
    print(f"Link: {opp.get('url')}\n")

    msg = generate_message(opp, opp.get('platform', 'Twitter'))
    print(f"MESSAGE:\n")
    print(f">>> {msg['message']}\n")
    print(f"Then: {msg['cta']}\n")
    print(f"Tips: {msg['notes']}\n")


if __name__ == "__main__":
    # Load opportunities
    try:
        with open("multiplatform_opportunities.json") as f:
            data = json.load(f)
            opportunities = data.get("top_10", [])

        if opportunities:
            pack = create_message_pack(opportunities)
            print("\n✅ Message templates ready to use!")
            print("📋 Open message_templates.json to see all messages")
        else:
            print("No opportunities found. Run multiplatform_discovery.py first.")

    except FileNotFoundError:
        print("multiplatform_opportunities.json not found.")
        print("Run multiplatform_discovery.py first.")
