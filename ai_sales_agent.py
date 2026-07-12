#!/usr/bin/env python3
"""
AI Sales Agent - The Brain of the Autonomous System
Uses Claude Opus for deep reasoning during calls.
Handles discovery, objection handling, closing.

This is what answers the phone and closes deals automatically.
"""

import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Use Opus for maximum reasoning capability
client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


class AISalesAgent:
    """AI Sales Agent powered by Claude Opus"""

    def __init__(self):
        self.model = "claude-opus-4-8"  # Most capable model for sales conversations
        self.conversation_history = []
        self.prospect_profile = {
            "name": None,
            "service": None,
            "pain_points": [],
            "budget": None,
            "objections": [],
            "buying_signals": [],
            "engagement_level": "initial"
        }

    def system_prompt(self) -> str:
        """The agent's core instructions and personality."""

        return """You are a world-class sales agent. Your goal: Close a $1500/month deal.

YOUR PRODUCT:
- Demand Discovery Service
- We find 50-100 pre-qualified prospects per month for their service
- They close 3-5 customers per month from those leads
- ROI: 300-600% (we cost $1500, they make $6-15K)

YOUR TONE:
- Conversational, warm, empathetic
- NOT pushy or salesy
- Genuinely curious about their business
- Listen more than you talk
- Build rapport first

YOUR STRATEGY:
1. GREETING (10 sec) - Warm welcome, set context
2. DISCOVERY (2-3 min) - Understand their situation
   - What service do they sell?
   - How many customers do they want?
   - What's their current lead source?
   - How much time do they spend on lead gen?
3. PROBLEM DISCOVERY (1-2 min) - Uncover pain
   - Is lead generation their biggest blocker?
   - How much revenue are they leaving on table?
   - What have they tried before?
4. PRESENT SOLUTION (1 min) - Show how you solve it
   - "Here's what we do..."
   - Real example: "Client XYZ closed 3 customers, made $6K, paid us $1500"
5. HANDLE OBJECTIONS (30-60 sec) - Address concerns
   - "What if you only close 1 customer? That pays us back."
   - "Most people get results within 2 weeks"
6. CLOSE (30 sec) - Ask for commitment
   - "Sound good? Let's get you started."
   - Send contract + payment link

KEY BEHAVIORS:
- Ask open-ended questions (not yes/no)
- Listen for pain, not for objections
- When they hesitate, offer guarantee: "Try 1 month, if not working, we stop"
- Always tie value to THEIR revenue, not our features
- If they say "let me think about it", offer: "Quick call Monday to check in?"

OBJECTION SCRIPTS:
"That's expensive" → "What if you close just 1 customer at $2K? That pays us back. Most get 3+."
"Not interested" → "I get it. Most aren't looking. But when they need leads, this is fastest way."
"Need to think" → "Totally fair. How about: start this week, and if it's not working in 2 weeks, we stop."
"Already have solution" → "What's working well? What's not? Maybe we can do one thing better."

CLOSING LINE:
"So let's get you started. I'll send you a contract and payment link. Sound good?"

CRITICAL SUCCESS FACTORS:
- Build genuine rapport (they buy from people they like)
- Understand their real pain (listen deeply)
- Show specific proof (social proof + ROI math)
- Make it easy to say yes (remove friction)
- Create urgency (limited spots, offer guarantee)
- Track their buying signals (objection type reveals readiness)

Remember: You're not pushy. You're genuinely helping. If they're right fit, they'll feel relieved to say yes.
"""

    def start_call(self, prospect_name: str = "Friend") -> str:
        """Start the call with warm greeting."""

        greeting = f"""Hi {prospect_name}! Thanks so much for jumping on. I'm the founder of Demand Discovery, and I help service businesses find their next customers on autopilot. How are you doing today?"""

        self.conversation_history.append({
            "role": "assistant",
            "content": greeting
        })

        self.prospect_profile["name"] = prospect_name
        return greeting

    def process_response(self, user_message: str) -> str:
        """Process prospect's response using Opus for deep reasoning."""

        # Add their message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Analyze their response before replying
        analysis_prompt = f"""Analyze this response to extract:
1. Engagement level (interested/neutral/skeptical)
2. Pain points mentioned
3. Buying signals (if any)
4. Objections or hesitations
5. What to focus on next

Response: "{user_message}"

Be concise."""

        analysis = client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{"role": "user", "content": analysis_prompt}]
        )

        # Update profile based on analysis
        analysis_text = analysis.content[0].text
        if "interested" in analysis_text.lower():
            self.prospect_profile["engagement_level"] = "interested"
        elif "skeptical" in analysis_text.lower():
            self.prospect_profile["engagement_level"] = "skeptical"

        # Generate response using Opus
        response = client.messages.create(
            model=self.model,
            max_tokens=500,
            system=self.system_prompt(),
            messages=self.conversation_history
        )

        agent_response = response.content[0].text

        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": agent_response
        })

        return agent_response

    def should_close(self) -> bool:
        """Determine if it's time to close based on conversation."""

        if len(self.conversation_history) < 8:  # Need at least 4 exchanges
            return False

        # Check for closing indicators
        last_messages = " ".join([m["content"] for m in self.conversation_history[-4:]])

        close_indicators = [
            "sounds good",
            "let's try",
            "how do we start",
            "when can you",
            "send me",
            "what's next"
        ]

        return any(indicator in last_messages.lower() for indicator in close_indicators)

    def close_deal(self) -> dict:
        """Close the deal and return contract/payment details."""

        closing_message = """Awesome! Here's what happens next:

1. I'll send you a contract (just 1 page) - takes 2 min to sign via DocuSign
2. Then payment link ($1500 for the first month)
3. We start this week - begin finding your prospects Monday

You'll get:
- 50-100 pre-qualified prospects per month
- Personalized outreach sequences
- Pipeline tracking dashboard
- Monthly reporting

If you're not seeing results in 2 weeks, we stop - no long-term commitment.

Contract and payment link coming to your email in 2 minutes.

Sound good?"""

        self.conversation_history.append({
            "role": "assistant",
            "content": closing_message
        })

        # Generate deal record
        deal_record = {
            "status": "closed",
            "amount": 1500,
            "currency": "USD",
            "frequency": "monthly",
            "timestamp": datetime.now().isoformat(),
            "conversation_length": len(self.conversation_history),
            "prospect_name": self.prospect_profile["name"],
            "closing_message": closing_message
        }

        return deal_record

    def get_call_transcript(self) -> list:
        """Get formatted call transcript."""

        transcript = []
        for msg in self.conversation_history:
            role = "Agent" if msg["role"] == "assistant" else "Prospect"
            transcript.append({
                "speaker": role,
                "message": msg["content"]
            })
        return transcript

    def get_call_analytics(self) -> dict:
        """Analyze call performance."""

        analytics = {
            "total_messages": len(self.conversation_history),
            "agent_messages": len([m for m in self.conversation_history if m["role"] == "assistant"]),
            "prospect_messages": len([m for m in self.conversation_history if m["role"] == "user"]),
            "conversation_length_minutes": len(self.conversation_history) * 0.5,  # Rough estimate
            "prospect_engagement": self.prospect_profile["engagement_level"],
            "pain_points_identified": len(self.prospect_profile["pain_points"]),
            "objections_handled": len(self.prospect_profile["objections"]),
            "ready_to_close": self.should_close()
        }

        return analytics


def simulate_call():
    """Simulate a complete sales call."""

    print("\n" + "="*100)
    print("📞 AI SALES AGENT - LIVE CALL SIMULATION".center(100))
    print("="*100 + "\n")

    agent = AISalesAgent()

    # Start call
    print("🤖 AGENT:")
    greeting = agent.start_call("Sarah")
    print(f"{greeting}\n")

    # Simulate prospect responses
    prospect_responses = [
        "Hey! I'm doing good. So I'm actually a digital marketing agency - we help B2B companies with LinkedIn strategy.",

        "Yeah, we do all the strategy but lead generation is what kills us. We're always scrambling to find actual prospects. Right now we do cold outreach but it's so time-consuming.",

        "We charge like $3-5K per month per client, so if we could land 2-3 more clients we'd be making an extra $8-15K per month.",

        "Cold email mostly. But the response rates are terrible, like 2-3%. Takes us hours every week.",

        "A system that just finds leads for us? Like how would that even work?",

        "And you're telling me I could get 50 leads that are actually interested in LinkedIn strategy services? That seems hard to believe honestly.",

        "OK wait, so you're saying most people close 3 of those leads? Because if that's true... that would actually solve our biggest problem.",

        "Yeah that sounds... actually really good. What's the next step here?"
    ]

    for i, response in enumerate(prospect_responses, 1):
        print(f"👤 PROSPECT:")
        print(f"{response}\n")

        agent_response = agent.process_response(response)
        print(f"🤖 AGENT:")
        print(f"{agent_response}\n")

        if agent.should_close():
            print("✅ CLOSING SIGNALS DETECTED - Time to close\n")
            break

    # Try to close
    if agent.should_close():
        print("🤖 AGENT:")
        deal = agent.close_deal()
        print(deal["closing_message"])
        print(f"\n✅ DEAL CLOSED: ${deal['amount']}/month\n")

    # Analytics
    print("\n" + "="*100)
    print("📊 CALL ANALYTICS".center(100))
    print("="*100 + "\n")

    analytics = agent.get_call_analytics()
    print(f"Call Duration: ~{analytics['conversation_length_minutes']:.0f} minutes")
    print(f"Agent Messages: {analytics['agent_messages']}")
    print(f"Prospect Messages: {analytics['prospect_messages']}")
    print(f"Engagement Level: {analytics['prospect_engagement']}")
    print(f"Ready to Close: {analytics['ready_to_close']}")

    # Save transcript
    with open("call_transcript.json", "w") as f:
        json.dump({
            "transcript": agent.get_call_transcript(),
            "analytics": analytics,
            "deal": deal if agent.should_close() else None
        }, f, indent=2)

    print("\n✅ Transcript saved to call_transcript.json")


if __name__ == "__main__":
    simulate_call()
