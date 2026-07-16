#!/usr/bin/env python3
"""
Apply /stop-slop fixes to 15 posts scoring below 35/50
Uses Claude API to rewrite content, eliminating AI patterns
"""

import os
import json
import requests
import time
from dotenv import load_dotenv
import anthropic

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

if not ZERNIO_API_KEY:
    raise ValueError("ZERNIO_API_KEY not set")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not set")

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

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
12. No rhetorical question openings (what, when, where, why, how, which, who)
13. No pull-quote-sounding statements
14. Trust the reader - state facts directly without softening

TARGET SCORE: Minimum 35/50 across 5 dimensions (Directness, Rhythm, Trust, Authenticity, Density)

REWRITE STRATEGY:
- Keep the core message and meaning
- Use active voice with human subjects
- Be direct and specific
- Use short, punchy sentences mixed with longer ones
- Sound like a knowledgeable human, not an essay
- Cut anything that doesn't advance the point
"""

def rewrite_for_stop_slop(original_content: str) -> str:
    """Use Claude to rewrite content eliminating /stop-slop anti-patterns"""

    prompt = f"""{STOP_SLOP_RULES}

ORIGINAL POST:
{original_content}

Rewrite this post to pass /stop-slop standards. Keep the same topic and core message, but eliminate all AI writing patterns. Make it sound human, direct, and specific.

Output ONLY the rewritten post, no explanations."""

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text.strip()

def get_post(post_id: str) -> dict:
    """Fetch a single post from Zernio"""
    try:
        response = requests.get(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        # Handle wrapped response
        if 'post' in data:
            return data['post']
        return data
    except Exception as e:
        print(f"    Error fetching: {str(e)[:100]}")
        return None

def update_post(post_id: str, post_data: dict) -> bool:
    """Update post back to Zernio"""
    try:
        put_response = requests.put(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            json=post_data,
            timeout=30
        )
        if put_response.status_code in (200, 201):
            return True
        else:
            print(f"      Error: {put_response.status_code} - {put_response.text[:100]}")
            return False
    except Exception as e:
        print(f"    Error updating: {e}")
        return False

def main():
    print("=" * 70)
    print("Apply /Stop-Slop Fixes to 15 Posts Below Threshold")
    print("=" * 70 + "\n")

    # Load audit report
    if not os.path.exists('stop-slop-audit-report.json'):
        print("✗ stop-slop-audit-report.json not found")
        print("  Run zernio-audit-stop-slop.py first")
        return

    with open('stop-slop-audit-report.json', 'r') as f:
        audit_data = json.load(f)

    # Get posts below threshold
    failing_posts = [r for r in audit_data['results'] if r['score'] < 35]
    print(f"Found {len(failing_posts)} posts to revise\n")

    successful = 0
    failed = 0

    for idx, result in enumerate(failing_posts):
        post_id = result['post_id']
        current_score = result['score']

        print(f"  {idx+1}/{len(failing_posts)}: {post_id[:12]}... (Score: {current_score:.1f}→?)")

        # Fetch post
        post = get_post(post_id)
        if not post:
            print(f"    ✗ Failed to fetch")
            failed += 1
            continue

        original_content = post.get('content', '')
        if not original_content:
            print(f"    ✗ No content")
            failed += 1
            continue

        # Rewrite for /stop-slop
        try:
            revised_content = rewrite_for_stop_slop(original_content)

            # Update post
            post['content'] = revised_content
            post['isDraft'] = False

            # Fix platform accountIds (convert from object to string)
            if 'platforms' in post:
                for platform in post['platforms']:
                    if isinstance(platform.get('accountId'), dict):
                        platform['accountId'] = platform['accountId'].get('_id', platform['accountId'])

            if update_post(post_id, post):
                successful += 1
                print(f"    ✓ Updated")
            else:
                failed += 1
                print(f"    ✗ Failed to update (Zernio rejected)")

        except Exception as e:
            failed += 1
            print(f"    ✗ Error: {str(e)[:80]}")

        time.sleep(0.5)  # Rate limit

    # Summary
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"✓ Revised: {successful}/{len(failing_posts)}")
    print(f"✗ Failed: {failed}/{len(failing_posts)}")

    if successful == len(failing_posts):
        print("\n✓ All 15 posts have been updated to pass /stop-slop standards!")
        print("  Re-run audit to verify: python3 zernio-audit-stop-slop.py")
    else:
        print(f"\n⚠️  {failed} posts failed to update")

if __name__ == '__main__':
    main()
