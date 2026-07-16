#!/usr/bin/env python3
"""
Detect failed posts and recover with retry → repost → reschedule strategy.
Monitors Zernio for failed posts, attempts recovery, logs outcomes.
"""

import os
import json
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
if not ZERNIO_API_KEY:
    raise ValueError("ZERNIO_API_KEY not set")

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

def get_failed_posts():
    """Fetch all failed posts from Zernio"""
    failed = []
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

            # Collect failed posts
            for p in posts:
                # Check for failed status in platforms
                platforms = p.get('platforms', [])
                for platform in platforms:
                    if platform.get('status') == 'failed':
                        failed.append({
                            'post_id': p.get('_id'),
                            'platform': platform.get('platform'),
                            'content': p.get('content'),
                            'scheduled_for': p.get('scheduledFor'),
                            'full_post': p
                        })

            if len(posts) < per_page:
                break
            page += 1

        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break

    return failed

def retry_publish(post_id, platform_name):
    """Attempt to retry publishing a failed post"""
    try:
        # Fetch post
        response = requests.get(f"{BASE}/posts/{post_id}", headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        post = data.get('post', data)

        # Find the failed platform config
        platforms = post.get('platforms', [])
        target_platform = None
        for p in platforms:
            if p.get('platform') == platform_name:
                target_platform = p
                break

        if not target_platform:
            return False, "Platform not found in post config"

        # Update status to 'pending' to retry
        target_platform['status'] = 'pending'
        target_platform['publishAttempts'] = target_platform.get('publishAttempts', 0) + 1

        # Fix accountId if needed
        if isinstance(target_platform.get('accountId'), dict):
            target_platform['accountId'] = target_platform['accountId'].get('_id')

        # Update post
        put_response = requests.put(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            json=post,
            timeout=30
        )

        if put_response.status_code in (200, 201):
            return True, "Retry triggered"
        else:
            return False, f"API rejected: {put_response.status_code}"

    except Exception as e:
        return False, str(e)

def repost(post_id):
    """Create a new post with same content (repost strategy)"""
    try:
        # Fetch original post
        response = requests.get(f"{BASE}/posts/{post_id}", headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        post = data.get('post', data)

        # Extract key fields
        content = post.get('content', '')
        platforms_config = post.get('platforms', [])
        media_items = post.get('mediaItems', [])

        # Create new post with same content (reschedule for 1 hour later)
        original_time = post.get('scheduledFor')
        if original_time:
            try:
                original_dt = datetime.fromisoformat(original_time.replace('Z', '+00:00'))
                new_dt = original_dt + timedelta(hours=1)
                new_scheduled = new_dt.isoformat()
            except:
                new_scheduled = (datetime.utcnow() + timedelta(hours=1)).isoformat() + 'Z'
        else:
            new_scheduled = (datetime.utcnow() + timedelta(hours=1)).isoformat() + 'Z'

        # Clean platforms for new post
        new_platforms = []
        for p in platforms_config:
            new_p = {
                'platform': p.get('platform'),
                'accountId': p.get('accountId'),
                'customContent': p.get('customContent'),
                'scheduledFor': new_scheduled
            }
            if p.get('title'):
                new_p['title'] = p['title']
            new_platforms.append(new_p)

        # Create new post
        new_post_data = {
            'content': content,
            'platforms': new_platforms,
            'isDraft': False
        }

        if media_items:
            new_post_data['mediaItems'] = media_items

        post_response = requests.post(
            f"{BASE}/posts",
            headers=HEADERS,
            json=new_post_data,
            timeout=30
        )

        if post_response.status_code in (200, 201):
            new_id = post_response.json().get('id') or post_response.json().get('_id')
            return True, f"Reposted as {new_id[:12]}..."
        else:
            return False, f"Create failed: {post_response.status_code}"

    except Exception as e:
        return False, str(e)

def reschedule(post_id, days_ahead=7):
    """Reschedule post for X days in the future"""
    try:
        # Fetch post
        response = requests.get(f"{BASE}/posts/{post_id}", headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        post = data.get('post', data)

        # Calculate new time
        new_dt = datetime.utcnow() + timedelta(days=days_ahead)
        new_scheduled = new_dt.isoformat() + 'Z'

        # Update all platforms with new scheduled time
        platforms = post.get('platforms', [])
        for p in platforms:
            p['scheduledFor'] = new_scheduled
            p['status'] = 'pending'  # Reset to pending
            if isinstance(p.get('accountId'), dict):
                p['accountId'] = p['accountId'].get('_id')

        # Update post
        put_response = requests.put(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            json=post,
            timeout=30
        )

        if put_response.status_code in (200, 201):
            return True, f"Rescheduled to {new_scheduled}"
        else:
            return False, f"Reschedule failed: {put_response.status_code}"

    except Exception as e:
        return False, str(e)

def recover_failed_post(failed):
    """Attempt recovery with escalating strategies"""
    post_id = failed['post_id']
    platform = failed['platform']

    recovery = {
        'post_id': post_id,
        'platform': platform,
        'timestamp': datetime.now().isoformat(),
        'attempts': []
    }

    print(f"\n  Recovering {post_id[:12]}... ({platform})")

    # Step 1: Retry
    print(f"    [1/3] Retry publish...", end=" ")
    success, msg = retry_publish(post_id, platform)
    recovery['attempts'].append({
        'step': 'retry',
        'success': success,
        'message': msg
    })
    if success:
        print(f"✓ {msg}")
        recovery['final_status'] = 'RECOVERED_RETRY'
        return recovery

    print(f"✗ {msg}")

    # Step 2: Repost (create new post)
    print(f"    [2/3] Repost (create new)...", end=" ")
    success, msg = repost(post_id)
    recovery['attempts'].append({
        'step': 'repost',
        'success': success,
        'message': msg
    })
    if success:
        print(f"✓ {msg}")
        recovery['final_status'] = 'RECOVERED_REPOST'
        return recovery

    print(f"✗ {msg}")

    # Step 3: Reschedule
    print(f"    [3/3] Reschedule (7 days out)...", end=" ")
    success, msg = reschedule(post_id, days_ahead=7)
    recovery['attempts'].append({
        'step': 'reschedule',
        'success': success,
        'message': msg
    })
    if success:
        print(f"✓ {msg}")
        recovery['final_status'] = 'RECOVERED_RESCHEDULE'
        return recovery

    print(f"✗ {msg}")
    recovery['final_status'] = 'UNRECOVERABLE'
    return recovery

def main():
    print("=" * 70)
    print("FAILED POST DETECTION & RECOVERY")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Get failed posts
    print("Scanning for failed posts...")
    failed_posts = get_failed_posts()

    if not failed_posts:
        print(f"✓ No failed posts found. All clear!\n")
        return

    print(f"Found {len(failed_posts)} failed platform(s)\n")

    # Recover each
    recoveries = []
    recovered = 0
    unrecoverable = 0

    for idx, failed in enumerate(failed_posts):
        print(f"[{idx+1}/{len(failed_posts)}]")
        result = recover_failed_post(failed)
        recoveries.append(result)

        if result['final_status'].startswith('RECOVERED'):
            recovered += 1
        elif result['final_status'] == 'UNRECOVERABLE':
            unrecoverable += 1

        time.sleep(0.5)

    # Summary
    print(f"\n\n{'='*70}")
    print("RECOVERY SUMMARY")
    print(f"{'='*70}")
    print(f"\nTotal failed: {len(failed_posts)}")
    print(f"✓ Recovered: {recovered}")
    print(f"✗ Unrecoverable: {unrecoverable}")

    # Breakdown by strategy
    strategies = {}
    for r in recoveries:
        if r['final_status'].startswith('RECOVERED'):
            strategy = r['final_status'].replace('RECOVERED_', '')
            strategies[strategy] = strategies.get(strategy, 0) + 1

    if strategies:
        print(f"\nRecovery breakdown:")
        for strategy, count in strategies.items():
            print(f"  • {strategy}: {count}")

    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_failed': len(failed_posts),
        'recovered': recovered,
        'unrecoverable': unrecoverable,
        'recoveries': recoveries
    }

    with open('failed-post-recovery-report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Report saved to failed-post-recovery-report.json")

    # Alert if unrecoverable
    if unrecoverable > 0:
        print(f"\n⚠️  {unrecoverable} posts require manual intervention")
        print("   Review failed-post-recovery-report.json for details")

if __name__ == '__main__':
    main()
