#!/usr/bin/env python3
"""
Autonomous self-auditing agent for Zernio posts.
Runs audit → identifies failures → auto-fixes → re-audits until 100% compliance.
"""

import os
import re
import sys
import json
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import anthropic

# Shared deterministic virality scorecard (hook=50%, no API). Advisory only —
# stop-slop (35/50) stays the sole auto-fix trigger; virality is reported, never
# rewritten, so the proven fix loop is unchanged.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from linkedin_agent.engine.virality_grader import (
        grade as grade_virality, VIRALITY_TARGET,
    )
except Exception:  # never crash the loop on an import-path issue
    grade_virality, VIRALITY_TARGET = None, 70

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

if not ZERNIO_API_KEY or not ANTHROPIC_API_KEY:
    raise ValueError("Missing ZERNIO_API_KEY or ANTHROPIC_API_KEY")

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}
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

STOP_SLOP_RULES = """
You are a prose editor specializing in eliminating AI writing patterns.

CRITICAL RULES:
1. Cut all adverbs (really, truly, literally, clearly, honestly, simply, basically, actually, definitely, certainly, obviously, absolutely, essentially, quite, rather, fairly, extremely)
2. Eliminate passive voice entirely - rewrite with active subjects
3. No inanimate objects performing human actions ("the decision emerges" → "I decided")
4. No vague declaratives - be specific ("the reasons are structural" → name the actual reason)
5. No throat-clearing ("here's what", "this is", "that is", "the fact is", "the truth is")
6. No "not X, it's Y" binary contrasts - state Y directly
7. Remove all em-dashes
8. Vary sentence length - no metronomic rhythm
9. Put reader in the room - "you" beats "people"; specifics beat abstractions
10. No lazy extremes ("always", "never", "every", "everyone", "nobody", "everything", "nothing")
11. No meta-joiners ("the rest of", "as mentioned", "furthermore", "additionally", "moreover", "in addition")
12. No rhetorical question openings
13. No pull-quote-sounding statements
14. Trust the reader - state facts directly without softening

TARGET: Minimum 35/50 across 5 dimensions (Directness, Rhythm, Trust, Authenticity, Density)
"""

def score_post(content):
    """Score post on 5 dimensions (1-10 each, 50 max)"""
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

def get_scheduled_posts():
    """Fetch all scheduled posts from Zernio"""
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

def get_post(post_id: str):
    """Fetch single post"""
    try:
        response = requests.get(f"{BASE}/posts/{post_id}", headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        if 'post' in data:
            return data['post']
        return data
    except Exception as e:
        return None

def update_post(post_id: str, post_data: dict) -> bool:
    """Update post to Zernio"""
    try:
        # Fix accountIds
        if 'platforms' in post_data:
            for platform in post_data['platforms']:
                if isinstance(platform.get('accountId'), dict):
                    platform['accountId'] = platform['accountId'].get('_id', platform['accountId'])

        put_response = requests.put(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            json=post_data,
            timeout=30
        )
        return put_response.status_code in (200, 201)
    except Exception as e:
        return False

def rewrite_for_stop_slop(original_content: str) -> str:
    """Rewrite using Claude"""
    prompt = f"""{STOP_SLOP_RULES}

ORIGINAL POST:
{original_content}

Rewrite this post to pass /stop-slop standards. Keep the same topic and core message, but eliminate all AI writing patterns. Make it sound human, direct, and specific.

Output ONLY the rewritten post, no explanations."""

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()

def audit_posts(posts):
    """Audit all posts, return results"""
    results = []
    failing_posts = []

    for idx, post in enumerate(posts):
        post_id = post.get('_id') or post.get('id')
        content = post.get('content', '')

        if not content:
            continue

        score, scores, issues = score_post(content)
        result = {
            'post_id': post_id,
            'score': score,
            'scores': scores,
            'passing': score >= 35
        }
        # Advisory virality grade — does NOT gate or trigger a fix.
        if grade_virality:
            v_score, v_dims, _ = grade_virality(content)
            result['virality_score'] = v_score
            result['virality_pass'] = v_score >= VIRALITY_TARGET
            result['virality_hook'] = v_dims['hook']
        results.append(result)

        if score < 35:
            failing_posts.append({
                'post_id': post_id,
                'score': score,
                'content': content
            })

    return results, failing_posts

def main():
    print("=" * 70)
    print("AUTONOMOUS AUDIT-FIX LOOP")
    print("=" * 70)
    print(f"Started: {datetime.now().isoformat()}\n")

    loop_num = 0
    max_loops = 5
    all_results = []

    while loop_num < max_loops:
        loop_num += 1
        print(f"\n{'='*70}")
        print(f"LOOP {loop_num}")
        print(f"{'='*70}")

        # Fetch posts
        posts = get_scheduled_posts()
        print(f"\nAuditing {len(posts)} posts...")

        # Score all posts
        results, failing_posts = audit_posts(posts)
        passing = sum(1 for r in results if r['passing'])
        failing = len(failing_posts)

        print(f"Results: {passing} passing, {failing} failing")
        all_results.append({
            'loop': loop_num,
            'timestamp': datetime.now().isoformat(),
            'total': len(results),
            'passing': passing,
            'failing': failing,
            'results': results
        })

        # Check if done
        if failing == 0:
            print(f"\n✓ ALL POSTS PASSING (Loop {loop_num})")
            break

        # Fix failing posts
        print(f"\nFixing {failing} posts...")
        fixed_count = 0

        for idx, fail in enumerate(failing_posts):
            post_id = fail['post_id']
            print(f"  {idx+1}/{failing}: {post_id[:12]}...", end=" ")

            # Rewrite
            try:
                revised = rewrite_for_stop_slop(fail['content'])

                # Fetch current post data
                post = get_post(post_id)
                if not post:
                    print("✗ Fetch failed")
                    continue

                # Update
                post['content'] = revised
                post['isDraft'] = False

                if update_post(post_id, post):
                    fixed_count += 1
                    print("✓")
                else:
                    print("✗")

            except Exception as e:
                print(f"✗ Error")

            time.sleep(0.3)

        print(f"\nFixed: {fixed_count}/{failing}")

        if loop_num >= max_loops:
            print(f"\n⚠️  Max loops ({max_loops}) reached")
            break

    # Final report
    print(f"\n\n{'='*70}")
    print("FINAL REPORT")
    print(f"{'='*70}")

    final_posts = get_scheduled_posts()
    final_results, final_failing = audit_posts(final_posts)
    final_passing = sum(1 for r in final_results if r['passing'])

    print(f"\nTotal loops: {loop_num}")
    print(f"Final status: {final_passing}/{len(final_results)} passing")

    # Advisory virality rollup (engagement signal stop-slop can't see).
    graded = [r for r in final_results if r.get('virality_score') is not None]
    weak_virality = [r for r in graded if not r['virality_pass']]
    if graded:
        avg_v = round(sum(r['virality_score'] for r in graded) / len(graded), 1)
        print(f"Virality (advisory): {len(graded) - len(weak_virality)}/{len(graded)} "
              f"≥{VIRALITY_TARGET}/100, avg {avg_v} — {len(weak_virality)} engagement-weak")

    if final_failing == 0:
        print("\n✓✓✓ AUDIT COMPLETE - ALL POSTS COMPLIANT ✓✓✓")
        status = "SUCCESS"
    else:
        print(f"\n⚠️  {len(final_failing)} posts still failing")
        status = "INCOMPLETE"

    # Save report
    report = {
        'status': status,
        'timestamp': datetime.now().isoformat(),
        'loops': loop_num,
        'total_posts': len(final_results),
        'passing': final_passing,
        'failing': len(final_failing),
        'threshold': 35,
        'virality_target': VIRALITY_TARGET,
        'virality_below_target': len(weak_virality),
        'virality_weak_posts': [
            {'post_id': r['post_id'],
             'virality_score': r['virality_score'],
             'hook': r.get('virality_hook')}
            for r in weak_virality
        ],
        'loop_history': all_results,
        'final_results': final_results,
        'failing_posts': [
            {'post_id': f['post_id'], 'score': f['score']}
            for f in final_failing
        ]
    }

    with open('auto-audit-report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Report saved to auto-audit-report.json")
    print(f"Completed: {datetime.now().isoformat()}")

if __name__ == '__main__':
    main()
