#!/usr/bin/env python3
"""
Schedule 106 draft posts into 5-posts-per-day plan starting June 6, 2026
Times: 8am, 11am, 2pm, 5pm, 8pm ET
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
    raise ValueError("ZERNIO_API_KEY environment variable not set")

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

# Schedule times per day (ET)
SCHEDULE_TIMES = [8, 11, 14, 17, 20]  # 8am, 11am, 2pm, 5pm, 8pm
START_DATE = datetime(2026, 6, 6)  # June 6, 2026
TIMEZONE = "America/New_York"

def get_all_draft_posts():
    """Fetch all 106 draft posts with pagination"""
    print("Fetching all draft posts...")
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

            if isinstance(data, dict) and 'posts' in data:
                posts = data['posts']
            elif isinstance(data, dict) and 'data' in data:
                posts = data['data']
            else:
                break

            # Filter for draft posts only
            draft_posts = [p for p in posts if p.get('status') == 'draft']
            all_posts.extend(draft_posts)

            if len(posts) < per_page:
                break

            page += 1

        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    return all_posts

def generate_schedule(num_posts):
    """Generate list of (date, time_hour, time_string) tuples for all posts"""
    schedule = []
    current_date = START_DATE
    time_index = 0

    for _ in range(num_posts):
        hour = SCHEDULE_TIMES[time_index]
        time_str = f"{hour:02d}:00:00"

        # Format as ISO 8601: YYYY-MM-DDTHH:MM:SS
        scheduled_for = current_date.strftime(f"%Y-%m-%dT{hour:02d}:00:00")

        schedule.append({
            'date': current_date.strftime("%Y-%m-%d"),
            'hour': hour,
            'scheduled_for': scheduled_for
        })

        # Move to next time slot
        time_index += 1
        if time_index >= len(SCHEDULE_TIMES):
            time_index = 0
            current_date += timedelta(days=1)

    return schedule

def update_post(post_id, scheduled_for):
    """Update post with new scheduledFor time"""
    try:
        # Minimal update: just change scheduledFor
        update_body = {
            "scheduledFor": scheduled_for,
            "status": "scheduled"
        }

        response = requests.put(
            f"{BASE}/posts/{post_id}",
            headers=HEADERS,
            json=update_body,
            timeout=30
        )

        if response.status_code in (200, 201):
            return True, "OK"
        else:
            return False, f"{response.status_code}: {response.text[:100]}"

    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("Schedule Draft Posts → 5-Posts-Per-Day (June 6 forward)")
    print("=" * 70)

    # Fetch draft posts
    draft_posts = get_all_draft_posts()
    print(f"\nFound {len(draft_posts)} draft posts")

    if not draft_posts:
        print("No draft posts to schedule")
        return

    # Generate schedule
    print(f"\nGenerating schedule for {len(draft_posts)} posts...")
    schedule = generate_schedule(len(draft_posts))

    # Show schedule preview
    print("\nSchedule Preview (first 5 posts):")
    for i, slot in enumerate(schedule[:5]):
        print(f"  Post {i+1}: {slot['date']} at {slot['hour']:02d}:00 → {slot['scheduled_for']}")
    print(f"  ... ({len(schedule) - 5} more posts)")
    print(f"\nLast post: {schedule[-1]['date']} at {schedule[-1]['hour']:02d}:00")

    # Calculate duration
    start = datetime.strptime(schedule[0]['date'], "%Y-%m-%d")
    end = datetime.strptime(schedule[-1]['date'], "%Y-%m-%d")
    days = (end - start).days + 1
    print(f"Duration: {days} days ({start.strftime('%b %d')} - {end.strftime('%b %d')})")

    # Apply schedule
    print("\n" + "=" * 70)
    print("Applying Schedule to Posts")
    print("=" * 70)

    successful = 0
    failed = 0
    failed_posts = []

    for idx, (post, slot) in enumerate(zip(draft_posts, schedule)):
        post_id = post.get('id') or post.get('_id')
        scheduled_for = slot['scheduled_for']

        success, msg = update_post(post_id, scheduled_for)

        if success:
            successful += 1
            if (idx + 1) % 10 == 0:
                print(f"  ✓ {idx + 1}/{len(draft_posts)} posts scheduled")
        else:
            failed += 1
            failed_posts.append((post_id, msg))
            if failed <= 5:  # Show first 5 failures
                print(f"  ✗ {post_id}: {msg}")

        # Rate limiting
        if (idx + 1) % 5 == 0:
            time.sleep(1)

    # Summary
    print("\n" + "=" * 70)
    print("Results")
    print("=" * 70)
    print(f"✓ Successfully scheduled: {successful}/{len(draft_posts)}")
    print(f"✗ Failed to schedule: {failed}/{len(draft_posts)}")

    if failed > 0:
        print(f"\nFirst failures:")
        for post_id, msg in failed_posts[:5]:
            print(f"  {post_id}: {msg}")

    # Save schedule to file
    schedule_file = 'drafts-scheduled-5-per-day.json'
    with open(schedule_file, 'w') as f:
        json.dump({
            'start_date': START_DATE.isoformat(),
            'total_posts': len(draft_posts),
            'successful': successful,
            'failed': failed,
            'posts_per_day': len(SCHEDULE_TIMES),
            'times': SCHEDULE_TIMES,
            'schedule': schedule
        }, f, indent=2)

    print(f"\n✓ Schedule saved to {schedule_file}")

if __name__ == '__main__':
    main()
