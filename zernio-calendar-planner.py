#!/usr/bin/env python3
"""
Content Calendar Planner - Optimize publish times and balance content distribution.
Analyzes scheduling patterns, identifies peak times, prevents conflicts.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

def get_scheduled_posts():
    """Fetch all scheduled posts"""
    scheduled = []
    page = 1

    while True:
        try:
            response = requests.get(
                f"{BASE}/posts?limit=50&page={page}",
                headers=HEADERS,
                timeout=30
            )
            data = response.json()
            posts = data.get('posts', [])

            scheduled.extend([p for p in posts if p.get('status') == 'scheduled'])

            if len(posts) < 50:
                break
            page += 1
        except Exception as e:
            print(f"Error: {e}")
            break

    return scheduled

def analyze_schedule(posts):
    """Analyze posting schedule"""
    analysis = {
        'total_posts': len(posts),
        'by_date': defaultdict(int),
        'by_hour': defaultdict(int),
        'by_day_of_week': defaultdict(int),
        'by_platform': defaultdict(int),
        'conflicts': [],
        'recommendations': []
    }

    for post in posts:
        scheduled_for = post.get('scheduledFor')
        if not scheduled_for:
            continue

        try:
            dt = datetime.fromisoformat(scheduled_for.replace('Z', '+00:00'))
            date_str = dt.strftime('%Y-%m-%d')
            hour = dt.hour
            day_of_week = dt.strftime('%A')

            analysis['by_date'][date_str] += 1
            analysis['by_hour'][hour] += 1
            analysis['by_day_of_week'][day_of_week] += 1

            for p in post.get('platforms', []):
                analysis['by_platform'][p.get('platform')] += 1

        except:
            pass

    # Find conflicts (>5 posts same hour)
    for hour, count in analysis['by_hour'].items():
        if count > 5:
            analysis['conflicts'].append(f"Hour {hour}: {count} posts (consider spreading)")

    # Generate recommendations
    if analysis['by_date']:
        avg_per_day = len(posts) / len(analysis['by_date'])
        max_day = max(analysis['by_date'], key=analysis['by_date'].get)
        if analysis['by_date'][max_day] > avg_per_day * 2:
            analysis['recommendations'].append(
                f"Day {max_day} has {analysis['by_date'][max_day]} posts (avg: {avg_per_day:.1f}). Consider spreading."
            )

    # Peak hours
    if analysis['by_hour']:
        peak_hours = sorted(analysis['by_hour'].items(), key=lambda x: x[1], reverse=True)[:3]
        analysis['peak_hours'] = peak_hours

    return analysis

def main():
    print("=" * 70)
    print("CONTENT CALENDAR PLANNER")
    print("=" * 70)
    print(f"Time: {datetime.now().isoformat()}\n")

    posts = get_scheduled_posts()
    print(f"Found {len(posts)} scheduled posts\n")

    analysis = analyze_schedule(posts)

    print("=" * 70)
    print("CALENDAR ANALYSIS")
    print("=" * 70)
    print(f"\nTotal scheduled: {analysis['total_posts']}")

    print(f"\nBy day of week:")
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        count = analysis['by_day_of_week'].get(day, 0)
        print(f"  {day}: {count}")

    print(f"\nBy platform:")
    for platform, count in sorted(analysis['by_platform'].items()):
        print(f"  {platform}: {count}")

    if analysis.get('peak_hours'):
        print(f"\nPeak publishing hours:")
        for hour, count in analysis['peak_hours']:
            print(f"  {hour:02d}:00 - {count} posts")

    if analysis['conflicts']:
        print(f"\n⚠️  Scheduling conflicts:")
        for conflict in analysis['conflicts']:
            print(f"  • {conflict}")

    if analysis['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in analysis['recommendations']:
            print(f"  • {rec}")

    report = {
        'timestamp': datetime.now().isoformat(),
        'analysis': {
            'total_posts': analysis['total_posts'],
            'by_day_of_week': dict(analysis['by_day_of_week']),
            'by_platform': dict(analysis['by_platform']),
            'peak_hours': analysis.get('peak_hours', []),
            'conflicts': analysis['conflicts'],
            'recommendations': analysis['recommendations']
        }
    }

    with open('calendar-analysis.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Report saved to calendar-analysis.json")

if __name__ == '__main__':
    main()
