#!/usr/bin/env python3
"""
Performance Forecaster - Predict post performance based on patterns.
Uses historical data to estimate success of upcoming posts.
"""

import os
import json
import requests
from datetime import datetime
from statistics import mean, stdev
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

def get_all_posts():
    """Get all posts"""
    all_posts = []
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
            all_posts.extend(posts)

            if len(posts) < 50:
                break
            page += 1
        except Exception as e:
            break

    return all_posts

def calculate_baseline_metrics(posts):
    """Calculate baseline performance metrics"""
    metrics = {
        'total_posts': len(posts),
        'by_platform': {},
        'by_hour': {},
        'avg_engagement': 0,
        'engagement_std': 0
    }

    engagement_scores = []

    for post in posts:
        for platform in post.get('platforms', []):
            platform_name = platform.get('platform')
            attempts = platform.get('publishAttempts', 0)

            if platform_name not in metrics['by_platform']:
                metrics['by_platform'][platform_name] = {
                    'count': 0,
                    'avg_engagement': 0,
                    'engagements': []
                }

            metrics['by_platform'][platform_name]['count'] += 1
            metrics['by_platform'][platform_name]['engagements'].append(attempts)
            engagement_scores.append(attempts)

    # Calculate stats
    if engagement_scores:
        metrics['avg_engagement'] = mean(engagement_scores)
        if len(engagement_scores) > 1:
            metrics['engagement_std'] = stdev(engagement_scores)

        # Per-platform stats
        for platform, data in metrics['by_platform'].items():
            if data['engagements']:
                data['avg_engagement'] = mean(data['engagements'])

    return metrics

def forecast_post_performance(post, baseline_metrics):
    """Forecast performance of a post"""
    content = post.get('content', '')
    platforms = post.get('platforms', [])

    forecast = {
        'post_id': post.get('_id'),
        'scheduled': post.get('scheduledFor'),
        'forecasts': {}
    }

    # Calculate content features
    word_count = len(content.split())
    has_hashtags = '#' in content
    has_numbers = any(c.isdigit() for c in content)
    sentence_count = len([s for s in content.split('.') if s.strip()])

    for platform in platforms:
        platform_name = platform.get('platform')

        # Base forecast from platform average
        platform_baseline = baseline_metrics['by_platform'].get(platform_name, {})
        base_engagement = platform_baseline.get('avg_engagement', baseline_metrics['avg_engagement'])

        # Adjustments
        engagement_boost = 0

        # Boost for hashtags on social platforms
        if has_hashtags and platform_name in ['twitter', 'instagram', 'tiktok']:
            engagement_boost += 0.15

        # Boost for numbers
        if has_numbers:
            engagement_boost += 0.10

        # Adjust for content length
        if word_count > 200:
            engagement_boost -= 0.05  # Long posts slightly less performant
        elif word_count < 50:
            engagement_boost -= 0.10  # Too short

        predicted_engagement = base_engagement * (1 + engagement_boost)

        forecast['forecasts'][platform_name] = {
            'predicted_engagement': predicted_engagement,
            'confidence': 'MEDIUM',
            'factors': {
                'word_count': word_count,
                'has_hashtags': has_hashtags,
                'has_numbers': has_numbers,
                'sentence_count': sentence_count,
                'boost_applied': engagement_boost
            }
        }

    return forecast

def main():
    print("=" * 70)
    print("PERFORMANCE FORECASTER")
    print("=" * 70)
    print(f"Time: {datetime.now().isoformat()}\n")

    all_posts = get_all_posts()
    print(f"Analyzing {len(all_posts)} posts for patterns...\n")

    # Separate published and scheduled
    published = [p for p in all_posts if p.get('status') == 'published']
    scheduled = [p for p in all_posts if p.get('status') == 'scheduled']

    print(f"Published (for baseline): {len(published)}")
    print(f"Scheduled (to forecast): {len(scheduled)}\n")

    # Calculate baseline from published posts
    baseline = calculate_baseline_metrics(published)

    print("=" * 70)
    print("BASELINE METRICS (from published posts)")
    print("=" * 70)
    print(f"\nAverage engagement: {baseline['avg_engagement']:.2f}")
    print(f"Engagement std dev: {baseline['engagement_std']:.2f}")

    print(f"\nBy platform:")
    for platform, stats in baseline['by_platform'].items():
        print(f"  {platform}: avg {stats['avg_engagement']:.2f}")

    # Forecast upcoming
    print(f"\n\n{'='*70}")
    print("UPCOMING POST FORECASTS")
    print(f"{'='*70}\n")

    forecasts = []
    for post in scheduled[:5]:  # Forecast first 5 scheduled
        forecast = forecast_post_performance(post, baseline)
        forecasts.append(forecast)

        print(f"{forecast['post_id'][:12]}...")
        for platform, pred in forecast['forecasts'].items():
            print(f"  {platform}: {pred['predicted_engagement']:.2f} (confidence: {pred['confidence']})")

    if len(scheduled) > 5:
        print(f"\n... forecasting {len(scheduled) - 5} more posts")

    report = {
        'timestamp': datetime.now().isoformat(),
        'baseline_metrics': baseline,
        'total_forecasts': len(forecasts),
        'sample_forecasts': forecasts[:10]
    }

    with open('forecast-report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Report saved to forecast-report.json")

if __name__ == '__main__':
    main()
