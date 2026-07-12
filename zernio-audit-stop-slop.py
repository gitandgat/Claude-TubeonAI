#!/usr/bin/env python3
"""
Audit all 107 scheduled posts against /stop-slop criteria
Score each on 5 dimensions, update any below 35/50
"""

import os
import re
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
if not ZERNIO_API_KEY:
    raise ValueError("ZERNIO_API_KEY not set")

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

# Stop-slop anti-patterns
SLOP_PATTERNS = {
    'adverbs': r'\b(really|truly|literally|clearly|honestly|simply|basically|actually|definitely|certainly|obviously|absolutely|essentially|quite|rather|fairly|extremely|incredibly|remarkably|undoubtedly|notably|arguably|seemingly|arguably|perhaps|arguably)\b',
    'throat_clearing': r'\b(here\'s what|this is|that is|the fact is|the truth is|what we|the thing is|listen|so|well)\b',
    'passive_voice': r'\b(is|are|was|were|been|be)\s+(said|done|made|given|taken|put|set|kept|left|shown|seen|found|brought|told|asked|called|thought|felt|known|understood|meant|supposed|believed)\b',
    'vague_declaratives': r'\b(the reason|the issue|the problem|the solution|the answer|implications are|reasons are|causes are|effects are)\b',
    'inanimate_actions': r'\b(the [a-z]+ (emerges|becomes|develops|grows|shifts|transforms|evolves|changes|turns|becomes))\b',
    'extremes': r'\b(always|never|every|everyone|nobody|everything|nothing)\b',
    'em_dashes': r'—',
    'whquestion_starts': r'^(what|when|where|why|how|which|who)\s+',
    'meta_joiners': r'\b(the rest of|as mentioned|as noted|furthermore|additionally|moreover|in addition|the fact that)\b',
}

def score_post(content):
    """
    Score post on 5 dimensions (1-10 each, 50 max)
    Returns: (total_score, breakdown)
    """

    issues = {dim: 0 for dim in SLOP_PATTERNS}

    # Count pattern matches
    for dim, pattern in SLOP_PATTERNS.items():
        matches = len(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
        issues[dim] = matches

    # Scoring logic
    scores = {}

    # Directness: penalize vague declaratives and throat clearing
    directness = 10 - min(10, (issues['vague_declaratives'] + issues['throat_clearing']) * 2)
    scores['directness'] = max(1, directness)

    # Rhythm: penalize em-dashes and check sentence variety
    sentences = [s.strip() for s in content.split('.') if s.strip()]
    rhythm = 10 - min(10, issues['em_dashes'] * 3)
    if len(sentences) > 2:
        lengths = [len(s.split()) for s in sentences[:5]]
        if len(set(lengths)) < 2:  # All similar length
            rhythm -= 3
    scores['rhythm'] = max(1, rhythm)

    # Trust: penalize passive voice and extremes
    trust = 10 - min(10, (issues['passive_voice'] + issues['extremes']) * 1.5)
    scores['trust'] = max(1, trust)

    # Authenticity: penalize adverbs, inanimate actions
    authenticity = 10 - min(10, (issues['adverbs'] + issues['inanimate_actions']) * 2)
    scores['authenticity'] = max(1, authenticity)

    # Density: penalize whquestion starts and meta joiners
    density = 10 - min(10, (issues['whquestion_starts'] + issues['meta_joiners']) * 2)
    scores['density'] = max(1, density)

    total = sum(scores.values())

    return total, scores, issues

def get_all_scheduled_posts():
    """Fetch all scheduled posts"""
    all_posts = []
    page = 1
    per_page = 50

    while True:
        try:
            response = requests.get(
                f"{BASE}/posts?limit={per_page}&page={page}",
                headers=HEADERS,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            posts = data.get('posts', [])
            scheduled = [p for p in posts if p.get('status') == 'scheduled']
            all_posts.extend(scheduled)

            if len(posts) < per_page:
                break

            page += 1

        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break

    return all_posts

def main():
    print("=" * 70)
    print("Audit 107 Posts Against /Stop-Slop Criteria")
    print("=" * 70 + "\n")

    posts = get_all_scheduled_posts()
    print(f"Auditing {len(posts)} scheduled posts...\n")

    audit_results = []
    below_threshold = []

    for idx, post in enumerate(posts):
        post_id = post.get('id') or post.get('_id')
        content = post.get('content', '')

        if not content:
            print(f"  {idx+1}/{len(posts)}: {post_id[:12]}... - NO CONTENT (skip)")
            continue

        score, scores, issues = score_post(content)

        audit_results.append({
            'post_id': post_id,
            'score': score,
            'scores': scores,
            'issues': issues,
            'content_length': len(content)
        })

        status = "✓" if score >= 35 else "✗"
        print(f"  {idx+1}/{len(posts)}: {post_id[:12]}... {status} Score: {score}/50")

        if score < 35:
            below_threshold.append(post_id)

    # Summary
    print("\n" + "=" * 70)
    print("AUDIT RESULTS")
    print("=" * 70)

    passing = sum(1 for r in audit_results if r['score'] >= 35)
    failing = len(audit_results) - passing

    print(f"\nPassing (≥35/50): {passing}/{len(audit_results)}")
    print(f"Needs revision (<35/50): {failing}/{len(audit_results)}")

    if below_threshold:
        print(f"\nPost IDs needing revision:")
        for post_id in below_threshold[:10]:
            print(f"  - {post_id}")
        if len(below_threshold) > 10:
            print(f"  ... and {len(below_threshold) - 10} more")

    # Save audit report
    audit_report = {
        'total_posts': len(audit_results),
        'passing': passing,
        'failing': failing,
        'threshold': 35,
        'results': audit_results
    }

    with open('stop-slop-audit-report.json', 'w') as f:
        json.dump(audit_report, f, indent=2)

    print(f"\n✓ Audit report saved to stop-slop-audit-report.json")

    if failing > 0:
        print(f"\n⚠️  {failing} posts need revision for /stop-slop compliance")
        print("Next step: Run zernio-apply-stop-slop-fixes.py to update them")

if __name__ == '__main__':
    main()
