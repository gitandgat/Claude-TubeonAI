#!/usr/bin/env python3
"""
Pre-publish quality gate - audits posts before Zernio scheduling.
Blocks failing posts, logs recommendations.
"""

import os
import re
import json
import sys
import anthropic
from dotenv import load_dotenv

# Reuse the shared deterministic virality scorecard (hook=50%, no API cost).
# Advisory only — stop-slop (35/50) stays the blocking gate.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from linkedin_agent.engine.virality_grader import (
        grade as grade_virality, VIRALITY_TARGET,
    )
except Exception:  # the gate must never crash on an import-path issue
    grade_virality, VIRALITY_TARGET = None, 70

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not set")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SLOP_PATTERNS = {
    'adverbs': r'\b(really|truly|literally|clearly|honestly|simply|basically|actually|definitely|certainly|obviously|absolutely|essentially|quite|rather|fairly|extremely|incredibly|remarkably|undoubtedly|notably|arguing|seemingly|perhaps)\b',
    'throat_clearing': r'\b(here\'s what|this is|that is|the fact is|the truth is|what we|the thing is|listen|so|well)\b',
    'passive_voice': r'\b(is|are|was|were|been|be)\s+(said|done|made|given|taken|put|set|kept|left|shown|seen|found|brought|told|asked|called|thought|felt|known|understood|meant|supposed|believed)\b',
    'vague_declaratives': r'\b(the reason|the issue|the problem|the solution|the answer|implications are|reasons are|causes are|effects are)\b',
    'inanimate_actions': r'\b(the [a-z]+ (emerges|becomes|develops|grows|shifts|transforms|evolves|changes|turns))\b',
    'extremes': r'\b(always|never|every|everyone|nobody|everything|nothing)\b',
    'em_dashes': r'—',
    'whquestion_starts': r'^(what|when|where|why|how|which|who)\s+',
    'meta_joiners': r'\b(the rest of|as mentioned|as noted|furthermore|additionally|moreover|in addition|the fact that)\b',
}

def score_post(content):
    """Score post on 5 dimensions"""
    issues = {dim: 0 for dim in SLOP_PATTERNS}

    for dim, pattern in SLOP_PATTERNS.items():
        matches = len(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
        issues[dim] = matches

    scores = {}
    directness = 10 - min(10, (issues['vague_declaratives'] + issues['throat_clearing']) * 2)
    scores['directness'] = max(1, directness)

    sentences = [s.strip() for s in content.split('.') if s.strip()]
    rhythm = 10 - min(10, issues['em_dashes'] * 3)
    if len(sentences) > 2:
        lengths = [len(s.split()) for s in sentences[:5]]
        if len(set(lengths)) < 2:
            rhythm -= 3
    scores['rhythm'] = max(1, rhythm)

    trust = 10 - min(10, (issues['passive_voice'] + issues['extremes']) * 1.5)
    scores['trust'] = max(1, trust)

    authenticity = 10 - min(10, (issues['adverbs'] + issues['inanimate_actions']) * 2)
    scores['authenticity'] = max(1, authenticity)

    density = 10 - min(10, (issues['whquestion_starts'] + issues['meta_joiners']) * 2)
    scores['density'] = max(1, density)

    total = sum(scores.values())
    return total, scores, issues

def generate_recommendations(content, issues):
    """Generate fix recommendations based on detected issues"""
    recommendations = []

    if issues['adverbs'] > 0:
        recommendations.append(f"Remove {issues['adverbs']} adverbs (really, truly, literally, etc.)")
    if issues['throat_clearing'] > 0:
        recommendations.append(f"Cut {issues['throat_clearing']} throat-clearing phrases (here's what, this is, etc.)")
    if issues['passive_voice'] > 0:
        recommendations.append(f"Rewrite {issues['passive_voice']} passive voice constructions with active subjects")
    if issues['vague_declaratives'] > 0:
        recommendations.append(f"Replace {issues['vague_declaratives']} vague declaratives with specifics")
    if issues['inanimate_actions'] > 0:
        recommendations.append(f"Rewrite {issues['inanimate_actions']} inanimate objects performing actions")
    if issues['extremes'] > 0:
        recommendations.append(f"Replace {issues['extremes']} lazy extremes (always, never, every)")
    if issues['em_dashes'] > 0:
        recommendations.append(f"Remove all {issues['em_dashes']} em-dashes")
    if issues['meta_joiners'] > 0:
        recommendations.append(f"Cut {issues['meta_joiners']} meta-joiners (furthermore, moreover, etc.)")

    return recommendations

def audit_post(content, post_id="unknown", auto_fix=False):
    """
    Audit single post before publishing.
    Returns: (passes, score, report)
    """
    score, scores, issues = score_post(content)
    passing = score >= 35   # stop-slop remains the ONLY blocking gate

    # Virality scorecard (advisory): hook=50%, curiosity, emotion, share, polarity,
    # platform fit. Surfaces engagement weaknesses stop-slop can't see.
    virality = None
    if grade_virality:
        v_score, v_dims, v_fixes = grade_virality(content)
        virality = {
            'score': v_score,
            'pass': v_score >= VIRALITY_TARGET,
            'dims': v_dims,
            'fixes': v_fixes,
        }

    report = {
        'post_id': post_id,
        'score': score,
        'passing': passing,
        'scores': scores,
        'issues': issues,
        'recommendations': generate_recommendations(content, issues)
    }
    if virality:
        report['virality'] = virality

    print("\n" + "=" * 70)
    print(f"PRE-PUBLISH QUALITY GATE: {post_id[:12]}...")
    print("=" * 70)
    print(f"Score: {score}/50")
    if virality:
        vt = '✓' if virality['pass'] else '~ advisory'
        print(f"Virality: {virality['score']}/100 (hook {virality['dims']['hook']}/10) {vt}")

    if passing:
        print("✅ POST PASSES - Ready to publish")
        # Stop-slop clean but engagement-weak? Surface fixes without blocking.
        if virality and not virality['pass'] and virality['fixes']:
            print(f"\n💡 Virality suggestions (advisory, {virality['score']}/100):")
            for fix in virality['fixes']:
                print(f"  • {fix}")
    else:
        print(f"❌ POST FAILS - Below 35/50 threshold")
        print(f"\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")

        if auto_fix:
            print("\n🔄 Auto-fixing post...")
            fixed = auto_fix_post(content)
            if fixed:
                score2, _, _ = score_post(fixed)
                print(f"Fixed score: {score2}/50")
                report['auto_fixed'] = True
                report['fixed_content'] = fixed
                report['fixed_score'] = score2
                passing = score2 >= 35
            else:
                report['auto_fixed'] = False

    return passing, report

def auto_fix_post(content):
    """Use Claude to auto-fix post"""
    prompt = f"""You are a prose editor specializing in eliminating AI writing patterns.

CRITICAL RULES:
1. Cut all adverbs (really, truly, literally, clearly, honestly, simply, basically, actually, definitely, certainly, obviously, absolutely, essentially, quite, rather, fairly, extremely)
2. Eliminate passive voice entirely - rewrite with active subjects
3. No inanimate objects performing human actions ("the decision emerges" → "I decided")
4. No vague declaratives - be specific
5. No throat-clearing ("here's what", "this is", "that is")
6. No "not X, it's Y" binary contrasts - state Y directly
7. Remove all em-dashes
8. Vary sentence length
9. No lazy extremes ("always", "never", "every", "everyone", "nobody", "everything", "nothing")

ORIGINAL POST:
{content}

Rewrite this post to pass /stop-slop standards. Keep the same topic and core message, but eliminate all AI writing patterns. Make it sound human, direct, and specific.

Output ONLY the rewritten post, no explanations."""

    try:
        message = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    except Exception as e:
        print(f"Auto-fix failed: {e}")
        return None

def process_post_file(filepath, auto_fix=False):
    """Process a single post file (markdown or text)"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"✗ Could not read {filepath}: {e}")
        return False, None

    post_id = os.path.splitext(os.path.basename(filepath))[0]
    passing, report = audit_post(content, post_id, auto_fix=auto_fix)

    # Save report
    report_path = f"{post_id}-audit.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    if auto_fix and report.get('auto_fixed'):
        # Save fixed content
        fixed_path = f"{post_id}-fixed.md"
        with open(fixed_path, 'w') as f:
            f.write(report['fixed_content'])
        print(f"\n✓ Fixed content saved to {fixed_path}")

    return passing, report

def main():
    import sys

    print("=" * 70)
    print("PRE-PUBLISH QUALITY GATE")
    print("=" * 70)

    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python3 zernio-prepublish-gate.py <post_file> [--auto-fix]")
        print("\nExamples:")
        print("  python3 zernio-prepublish-gate.py my-post.md")
        print("  python3 zernio-prepublish-gate.py my-post.md --auto-fix")
        return

    post_file = sys.argv[1]
    auto_fix = '--auto-fix' in sys.argv

    if not os.path.exists(post_file):
        print(f"✗ File not found: {post_file}")
        return

    passing, report = process_post_file(post_file, auto_fix=auto_fix)

    # Summary
    print("\n" + "=" * 70)
    if passing:
        print("✅ APPROVED FOR PUBLICATION")
        exit_code = 0
    else:
        print("❌ BLOCKED - NEEDS REVISION")
        if not auto_fix:
            print("\n💡 Tip: Run with --auto-fix to automatically fix issues")
        exit_code = 1

    print("=" * 70)
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
