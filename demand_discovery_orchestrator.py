#!/usr/bin/env python3
"""
Demand Discovery Orchestrator
Master agent that runs the full demand discovery pipeline:
1. Scrapes Reddit
2. Validates demand
3. Detects patterns
4. Evaluates monetization
"""

import json
import sys
from datetime import datetime
from reddit_demand_scraper import run_discovery_cycle, display_winners, save_results
from pattern_detector import run_pattern_analysis
from monetization_evaluator import evaluate_batch, display_mtm_results


def save_discovery_history(new_cycle: dict, history_file: str = "discovery_history.json"):
    """Add current cycle to historical record."""
    try:
        with open(history_file, "r") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []

    history.append(new_cycle)

    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

    print(f"📚 Added to discovery history ({len(history)} cycles total)")


def generate_executive_summary(discoveries: dict, patterns: dict, monetizations: dict) -> str:
    """Generate a text summary of the full analysis."""
    summary = f"""
╔════════════════════════════════════════════════════════════════════════════════════╗
║                    DEMAND DISCOVERY EXECUTIVE SUMMARY                            ║
║                          {datetime.now().strftime('%Y-%m-%d %H:%M')}                                  ║
╚════════════════════════════════════════════════════════════════════════════════════╝

📊 DISCOVERY CYCLE RESULTS
─────────────────────────────────────────────────────────────────────────────────────
Total Posts Analyzed: {len(discoveries.get('opportunities', []))}
High-Scoring Opportunities: {len([o for o in discoveries.get('opportunities', []) if o.get('score', 0) > 70])}
Top Opportunity Score: {max([o.get('score', 0) for o in discoveries.get('opportunities', [])], default=0)}/100

🎯 TOP 3 OPPORTUNITIES:
"""

    for i, opp in enumerate(discoveries.get("opportunities", [])[:3], 1):
        summary += f"""
{i}. {opp['title'][:60]}
   Score: {opp['score']}/100 | Demand: {opp['demand_level'].upper()}
   Skill: {opp['skill_required']} | Subreddit: r/{opp['subreddit']}
   Upvotes: {opp['upvotes']} | Comments: {opp['num_comments']}
"""

    summary += f"""

📈 PATTERN ANALYSIS
─────────────────────────────────────────────────────────────────────────────────────
Recurring Patterns Found: {len(patterns.get('patterns', []))}
Emerging Trends: {len(patterns.get('trends', []))}

"""

    if patterns.get("patterns"):
        summary += "Top Recurring Problems:\n"
        for pattern in patterns["patterns"][:3]:
            summary += f"  • {pattern['cluster']} (Confidence: {pattern['confidence']*100:.0f}%)\n"

    if patterns.get("trends"):
        summary += "\nEmerging Opportunities:\n"
        for trend in patterns["trends"][:3]:
            summary += f"  • {trend.get('trend')}\n"

    summary += f"""

💰 MONETIZATION RECOMMENDATIONS
─────────────────────────────────────────────────────────────────────────────────────
Ready for Monetization Evaluation: {len(monetizations.get('evaluations', []))} opportunities

Next Steps:
1. Review top opportunities in demand_discoveries.json
2. Check pattern_analysis.json for recurring themes
3. Review monetization recommendations in monetization_evals.json
4. Pick one high-confidence opportunity
5. Build MVP or validate market fit further
"""

    return summary


def run_full_pipeline(limit_per_sub: int = 50, evaluate_top_n: int = 5):
    """
    Run the complete demand discovery pipeline.
    """
    print("\n" + "╔" + "="*98 + "╗")
    print("║" + "DEMAND DISCOVERY PIPELINE".center(98) + "║")
    print("╚" + "="*98 + "╝\n")

    # PHASE 1: SCRAPE & VALIDATE
    print("PHASE 1️⃣  : Reddit Scraping & Demand Validation")
    print("─" * 100)
    winners = run_discovery_cycle(limit=limit_per_sub)

    if not winners:
        print("⚠️  No valid opportunities found. Exiting.")
        return

    # Save discoveries
    discoveries = save_results(winners)
    display_winners(winners)

    # Add to history
    save_discovery_history(discoveries)

    # PHASE 2: PATTERN DETECTION
    print("\n\nPHASE 2️⃣  : Pattern Detection & Trend Analysis")
    print("─" * 100)
    pattern_results = run_pattern_analysis()

    # PHASE 3: MONETIZATION EVALUATION
    print("\n\nPHASE 3️⃣  : Monetization Strategy Evaluation")
    print("─" * 100)

    top_opportunities = [
        {
            "title": w.title,
            "skill_required": w.skill_required,
            "demand_level": w.demand_level,
            "explanation": w.explanation,
            "score": w.score,
        }
        for w in winners[:evaluate_top_n]
    ]

    monetizations = evaluate_batch(top_opportunities)

    # Save monetization results
    mtm_output = {
        "timestamp": datetime.now().isoformat(),
        "total_evaluated": len(monetizations),
        "evaluations": [
            {
                "title": mtm.opportunity_title,
                "recommended_model": mtm.recommended_model,
                "reasoning": mtm.reasoning,
                "next_steps": mtm.next_steps,
                "viability_scores": {
                    "saas": mtm.saas_viability["score"],
                    "services": mtm.service_viability["score"],
                    "products": mtm.product_viability["score"],
                },
            }
            for mtm in monetizations
        ]
    }

    with open("monetization_evals.json", "w") as f:
        json.dump(mtm_output, f, indent=2)

    display_mtm_results(monetizations)

    # GENERATE SUMMARY
    print("\n\nPHASE 4️⃣  : Executive Summary")
    print("─" * 100)
    summary = generate_executive_summary(discoveries, pattern_results, mtm_output)
    print(summary)

    # Save summary
    with open("discovery_summary.txt", "w") as f:
        f.write(summary)

    print("\n✅ Pipeline Complete!")
    print(f"📁 Output files:")
    print(f"   • demand_discoveries.json (all opportunities with scores)")
    print(f"   • pattern_analysis.json (recurring themes)")
    print(f"   • monetization_evals.json (MtM recommendations)")
    print(f"   • discovery_summary.txt (executive summary)")
    print(f"   • discovery_history.json (historical cycles)")


if __name__ == "__main__":
    try:
        run_full_pipeline(limit_per_sub=50, evaluate_top_n=5)
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
