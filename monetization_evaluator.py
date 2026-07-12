#!/usr/bin/env python3
"""
Monetization Evaluator Agent
Analyzes validated demand opportunities and recommends the best monetization model.
"""

import json
from dataclasses import dataclass
from anthropic import Anthropic

client = Anthropic()


@dataclass
class OpportunityMtM:
    """Monetization evaluation for an opportunity."""
    opportunity_title: str
    saas_viability: dict  # score, effort, market_size
    service_viability: dict  # score, effort, margin
    product_viability: dict  # score, effort, scalability
    recommended_model: str
    reasoning: str
    next_steps: list[str]


def evaluate_monetization(opportunity: dict) -> OpportunityMtM:
    """
    Use Claude to evaluate the best monetization model for an opportunity.
    Takes a demand discovery result and returns MtM recommendation.
    """

    prompt = f"""
You are evaluating the best monetization model for this market opportunity discovered on Reddit.

Opportunity Details:
- Title: {opportunity.get('title', 'Unknown')}
- Skill Required: {opportunity.get('skill_required', 'unknown')}
- Demand Level: {opportunity.get('demand_level', 'medium')}
- Why People Want It: {opportunity.get('explanation', '')}

Evaluate each monetization model (0-10 scale):

1. **SaaS (Subscription Tool)**
   - Could you build a web app Claude powers for this?
   - Score: (market size, recurring revenue potential, build effort)

2. **Consulting/Services (Done-For-You)**
   - Could you deliver this as a high-margin service using Claude?
   - Score: (pricing power, scalability, operational load)

3. **Digital Products (Templates/Frameworks/Courses)**
   - Could this work as a one-time purchase product?
   - Score: (market size, leverage, delivery effort)

For each model provide:
- viability_score (0-10)
- build_effort (low/medium/high)
- market_potential (small/medium/large)
- estimated_price_range

Then recommend ONE model with reasoning.

Respond in JSON:
{{
  "saas": {{"score": 8, "effort": "high", "market": "medium", "price": "$29-99/mo"}},
  "services": {{"score": 7, "effort": "medium", "market": "small", "price": "$500-2000/project"}},
  "products": {{"score": 5, "effort": "low", "market": "small", "price": "$27-97"}},
  "recommended": "saas",
  "reasoning": "...",
  "next_steps": ["step 1", "step 2", "step 3"]
}}
"""

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        result = json.loads(response.content[0].text)

        return OpportunityMtM(
            opportunity_title=opportunity.get('title', 'Unknown'),
            saas_viability={
                "score": result.get("saas", {}).get("score", 0),
                "effort": result.get("saas", {}).get("effort", "unknown"),
                "market": result.get("saas", {}).get("market", "unknown"),
                "price": result.get("saas", {}).get("price", "N/A"),
            },
            service_viability={
                "score": result.get("services", {}).get("score", 0),
                "effort": result.get("services", {}).get("effort", "unknown"),
                "market": result.get("services", {}).get("market", "unknown"),
                "price": result.get("services", {}).get("price", "N/A"),
            },
            product_viability={
                "score": result.get("products", {}).get("score", 0),
                "effort": result.get("products", {}).get("effort", "unknown"),
                "market": result.get("products", {}).get("market", "unknown"),
                "price": result.get("products", {}).get("price", "N/A"),
            },
            recommended_model=result.get("recommended", "unknown"),
            reasoning=result.get("reasoning", ""),
            next_steps=result.get("next_steps", []),
        )
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing monetization eval: {e}")
        return None


def evaluate_batch(opportunities: list[dict]) -> list[OpportunityMtM]:
    """Evaluate multiple opportunities."""
    results = []
    for opp in opportunities:
        print(f"Evaluating: {opp.get('title', 'Unknown')[:50]}...")
        mtm = evaluate_monetization(opp)
        if mtm:
            results.append(mtm)
    return results


def display_mtm_results(results: list[OpportunityMtM]):
    """Pretty-print monetization evaluation results."""
    print("\n" + "="*100)
    print("💰 MONETIZATION EVALUATION RESULTS".center(100))
    print("="*100 + "\n")

    for mtm in results:
        print(f"Opportunity: {mtm.opportunity_title}")
        print(f"{'─'*100}")

        print(f"\n  SaaS (Subscription):")
        print(f"    Viability: {mtm.saas_viability['score']}/10 | Effort: {mtm.saas_viability['effort']}")
        print(f"    Market: {mtm.saas_viability['market']} | Price: {mtm.saas_viability['price']}")

        print(f"\n  Services (Done-For-You):")
        print(f"    Viability: {mtm.service_viability['score']}/10 | Effort: {mtm.service_viability['effort']}")
        print(f"    Market: {mtm.service_viability['market']} | Price: {mtm.service_viability['price']}")

        print(f"\n  Products (Digital):")
        print(f"    Viability: {mtm.product_viability['score']}/10 | Effort: {mtm.product_viability['effort']}")
        print(f"    Market: {mtm.product_viability['market']} | Price: {mtm.product_viability['price']}")

        print(f"\n  🎯 RECOMMENDED: {mtm.recommended_model.upper()}")
        print(f"     {mtm.reasoning}")

        print(f"\n  📋 Next Steps:")
        for step in mtm.next_steps:
            print(f"     • {step}")

        print(f"\n{'─'*100}\n")


if __name__ == "__main__":
    # Example: Load discoveries and evaluate
    try:
        with open("demand_discoveries.json", "r") as f:
            data = json.load(f)

        opportunities = data.get("opportunities", [])[:5]  # Top 5

        if opportunities:
            results = evaluate_batch(opportunities)
            display_mtm_results(results)

            # Save results
            with open("monetization_evals.json", "w") as f:
                json.dump({
                    "timestamp": data.get("timestamp"),
                    "evaluations": [
                        {
                            "title": mtm.opportunity_title,
                            "recommended": mtm.recommended_model,
                            "reasoning": mtm.reasoning,
                            "next_steps": mtm.next_steps,
                            "viability": {
                                "saas": mtm.saas_viability["score"],
                                "services": mtm.service_viability["score"],
                                "products": mtm.product_viability["score"],
                            }
                        }
                        for mtm in results
                    ]
                }, f, indent=2)

            print(f"\n💾 Monetization evaluations saved to monetization_evals.json")
        else:
            print("No opportunities found. Run reddit_demand_scraper.py first.")

    except FileNotFoundError:
        print("demand_discoveries.json not found. Run reddit_demand_scraper.py first.")
