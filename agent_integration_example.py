#!/usr/bin/env python3
"""
Agent Integration Example
Shows how to feed demand discoveries to other agents for:
- Deeper market research
- PRD generation
- Competitor analysis
- Launch planning
"""

import json
from anthropic import Anthropic

client = Anthropic()
conversation_history = []


def load_discoveries(filename: str = "demand_discoveries.json") -> dict:
    """Load the latest discoveries."""
    try:
        with open(filename) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ {filename} not found. Run demand_discovery_orchestrator.py first.")
        return None


def create_market_research_agent(opportunity: dict) -> str:
    """
    Use Claude to deep-dive on market research for an opportunity.
    """
    prompt = f"""
You are a market research specialist. I've identified this market opportunity:

**Title:** {opportunity['title']}
**Why people want it:** {opportunity['explanation']}
**Demand Level:** {opportunity['demand_level']}
**Engagement:** {opportunity['upvotes']} upvotes, {opportunity['num_comments']} comments
**Source:** r/{opportunity['subreddit']}

Provide:
1. Market Size Estimate (TAM/SAM/SOM)
2. Competitor Landscape (3-5 existing solutions)
3. Customer Persona
4. Key Pain Points (ranked by severity)
5. Pricing Benchmarks
6. Distribution Channels

Be concise but specific. Use the Reddit post data to inform your research.
"""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def create_prd_generator_agent(opportunity: dict, market_research: str) -> str:
    """
    Use Claude to generate a PRD skeleton.
    """
    prompt = f"""
Create a Product Requirements Document skeleton for this opportunity:

**Opportunity:** {opportunity['title']}
**Skill Required:** {opportunity['skill_required']}

**Market Research Summary:**
{market_research[:1000]}...

Generate sections:
1. Problem Statement
2. Success Metrics
3. User Stories (3-5)
4. Feature List (MVP only)
5. Acceptance Criteria
6. Launch Roadmap (4 weeks)

Keep it actionable, not fluffy.
"""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def create_launch_plan_agent(opportunity: dict, prd: str) -> str:
    """
    Use Claude to create a 4-week launch plan.
    """
    prompt = f"""
Create a 4-week launch plan for:

**Product:** {opportunity['title']}
**Demand Source:** r/{opportunity['subreddit']}
**Target Customers:** People asking this on Reddit

**PRD Summary:**
{prd[:1000]}...

Provide:
**Week 1:** Foundation
- What to build
- What NOT to build
- Success criteria

**Week 2:** Build & Test
- Development milestones
- Testing strategy
- Fallback if stuck

**Week 3:** Polish
- Common issues to fix
- Performance optimization
- Copy/positioning

**Week 4:** Launch
- Launch channels (prioritized)
- Day-1 outreach strategy
- Success metrics

Be specific on actions, not generic advice.
"""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def create_positioning_agent(opportunity: dict) -> str:
    """
    Use Claude to refine positioning and messaging.
    """
    prompt = f"""
You are a positioning specialist. Help me craft the positioning for:

**Problem:** {opportunity['title']}
**Why it matters:** {opportunity['explanation']}
**Who has it:** r/{opportunity['subreddit']} users

Create:
1. **One-Liner:** The single sentence that captures it
2. **Value Prop:** 3-4 benefits (not features)
3. **Positioning Statement:** "For [target], [product] is [category] that [benefit]"
4. **Key Differentiators:** (vs. doing it manually / vs. existing tools)
5. **Elevator Pitch:** 30-second explanation

Make it sticky and memorable.
"""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def create_validation_plan_agent(opportunity: dict) -> str:
    """
    Use Claude to create a customer validation plan.
    """
    prompt = f"""
Create a 2-week customer validation plan for:

**Problem:** {opportunity['title']}
**Demand Signal:** {opportunity['upvotes']} upvotes on r/{opportunity['subreddit']}

The goal: Confirm 10+ people would actually pay for this.

Provide:
1. **Target Interview List** (how to find them)
2. **Interview Questions** (5-7 key questions)
3. **Willingness to Pay** (how to test pricing)
4. **Scoring Rubric** (what counts as validation)
5. **Stop/Go Decision Criteria** (go/no-go threshold)

Include concrete scripts you'd use in the actual interviews.
"""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def run_agent_pipeline(opportunity: dict, depth: str = "full"):
    """
    Run a sequence of agents to fully develop an opportunity.
    depth: "quick" (positioning only) or "full" (all agents)
    """
    print(f"\n{'='*100}")
    print(f"🤖 AGENT PIPELINE: {opportunity['title'][:60]}".center(100))
    print(f"{'='*100}\n")

    outputs = {}

    # Step 1: Market Research
    print("📊 Agent 1: Market Research Analysis...")
    market_research = create_market_research_agent(opportunity)
    outputs["market_research"] = market_research
    print(f"\n{market_research}\n")

    if depth == "quick":
        return outputs

    # Step 2: PRD Generation
    print("📋 Agent 2: PRD Generation...")
    prd = create_prd_generator_agent(opportunity, market_research)
    outputs["prd"] = prd
    print(f"\n{prd}\n")

    # Step 3: Launch Plan
    print("🚀 Agent 3: Launch Plan...")
    launch_plan = create_launch_plan_agent(opportunity, prd)
    outputs["launch_plan"] = launch_plan
    print(f"\n{launch_plan}\n")

    # Step 4: Positioning
    print("🎯 Agent 4: Positioning & Messaging...")
    positioning = create_positioning_agent(opportunity)
    outputs["positioning"] = positioning
    print(f"\n{positioning}\n")

    # Step 5: Validation
    print("✅ Agent 5: Validation Plan...")
    validation = create_validation_plan_agent(opportunity)
    outputs["validation"] = validation
    print(f"\n{validation}\n")

    return outputs


def save_agent_outputs(opportunity: dict, outputs: dict):
    """Save all agent outputs to a file."""
    filename = f"agent_analysis_{opportunity['id']}.json"

    output_data = {
        "opportunity": {
            "title": opportunity["title"],
            "score": opportunity["score"],
            "skill": opportunity["skill_required"],
        },
        "analysis": outputs,
    }

    with open(filename, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\n💾 Analysis saved to {filename}")
    return filename


if __name__ == "__main__":
    # Load discoveries
    data = load_discoveries()

    if not data or not data.get("opportunities"):
        print("No opportunities found.")
        exit(1)

    # Get top opportunity
    top_opp = data["opportunities"][0]

    print(f"\n🔍 Analyzing: {top_opp['title']}")
    print(f"Score: {top_opp['score']}/100 | Demand: {top_opp['demand_level']}\n")

    # Run agent pipeline
    outputs = run_agent_pipeline(top_opp, depth="full")

    # Save results
    save_agent_outputs(top_opp, outputs)

    print("\n✅ Full agent analysis complete!")
    print(f"\nNext steps:")
    print(f"1. Review the market research findings")
    print(f"2. Validate the PRD with 5-10 potential customers")
    print(f"3. Follow the launch plan week by week")
    print(f"4. Use the validation plan to confirm product-market fit")
