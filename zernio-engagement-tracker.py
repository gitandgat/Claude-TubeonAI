#!/usr/bin/env python3
"""
Engagement Tracker - Monitor comment sentiment, flags brand risk, detects high engagement.
Tracks community interaction and sentiment patterns.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

RISK_KEYWORDS = [
    'scam', 'fraud', 'fake', 'misleading', 'lies', 'garbage', 'trash',
    'horrible', 'terrible', 'awful', 'hate', 'boycott', 'unfollow'
]

POSITIVE_KEYWORDS = [
    'love', 'amazing', 'great', 'excellent', 'helpful', 'inspiring',
    'thank', 'appreciate', 'perfect', 'beautiful', 'awesome'
]

def get_recent_posts(days_back=7):
    """Get recently published posts"""
    recent = []
    page = 1
    cutoff = datetime.utcnow() - timedelta(days=days_back)

    while True:
        try:
            response = requests.get(
                f"{BASE}/posts?limit=50&page={page}",
                headers=HEADERS,
                timeout=30
            )
            data = response.json()
            posts = data.get('posts', [])

            for p in posts:
                if p.get('status') == 'published':
                    pub_date = p.get('publishedAt')
                    if pub_date:
                        pub_dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                        if pub_dt >= cutoff:
                            recent.append(p)

            if len(posts) < 50:
                break
            page += 1
        except Exception as e:
            break

    return recent

def analyze_sentiment(text):
    """Simple sentiment analysis"""
    text_lower = text.lower()

    risk_count = sum(1 for keyword in RISK_KEYWORDS if keyword in text_lower)
    positive_count = sum(1 for keyword in POSITIVE_KEYWORDS if keyword in text_lower)

    if risk_count > 0:
        return 'RISK'
    elif positive_count >= 2:
        return 'POSITIVE'
    elif positive_count > 0:
        return 'NEUTRAL_POSITIVE'
    else:
        return 'NEUTRAL'

def track_engagement(posts):
    """Track engagement metrics"""
    tracking = {
        'total_posts': len(posts),
        'high_engagement': [],
        'brand_risks': [],
        'positive_posts': [],
        'sentiment_breakdown': {
            'RISK': 0,
            'POSITIVE': 0,
            'NEUTRAL_POSITIVE': 0,
            'NEUTRAL': 0
        }
    }

    for post in posts:
        content = post.get('content', '')
        post_id = post.get('_id')

        sentiment = analyze_sentiment(content)
        tracking['sentiment_breakdown'][sentiment] += 1

        # Flag risks
        if sentiment == 'RISK':
            tracking['brand_risks'].append({
                'post_id': post_id,
                'published': post.get('publishedAt'),
                'risk_keywords': [k for k in RISK_KEYWORDS if k in content.lower()]
            })

        # Flag positive posts
        if sentiment == 'POSITIVE':
            tracking['positive_posts'].append({
                'post_id': post_id,
                'published': post.get('publishedAt')
            })

        # High engagement estimate (comment count proxy)
        publish_attempts = sum(
            p.get('publishAttempts', 0)
            for p in post.get('platforms', [])
        )
        if publish_attempts > 2:
            tracking['high_engagement'].append({
                'post_id': post_id,
                'engagement_score': publish_attempts
            })

    return tracking

def main():
    print("=" * 70)
    print("ENGAGEMENT TRACKER")
    print("=" * 70)
    print(f"Time: {datetime.now().isoformat()}\n")

    posts = get_recent_posts(days_back=7)
    print(f"Tracking {len(posts)} posts from last 7 days\n")

    tracking = track_engagement(posts)

    print("=" * 70)
    print("ENGAGEMENT REPORT")
    print("=" * 70)

    print(f"\nSentiment breakdown:")
    for sentiment, count in tracking['sentiment_breakdown'].items():
        print(f"  {sentiment}: {count}")

    if tracking['brand_risks']:
        print(f"\n⚠️  Brand Risk Alerts: {len(tracking['brand_risks'])}")
        for risk in tracking['brand_risks'][:5]:
            print(f"  • {risk['post_id'][:12]}... - Risk keywords: {', '.join(risk['risk_keywords'])}")

    if tracking['positive_posts']:
        print(f"\n✓ Positive engagement: {len(tracking['positive_posts'])} posts")

    if tracking['high_engagement']:
        print(f"\n🔥 High engagement: {len(tracking['high_engagement'])} posts")
        for post in tracking['high_engagement'][:5]:
            print(f"  • {post['post_id'][:12]}... - Score: {post['engagement_score']}")

    report = {
        'timestamp': datetime.now().isoformat(),
        'days_tracked': 7,
        'tracking': tracking
    }

    with open('engagement-report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Report saved to engagement-report.json")

    if tracking['brand_risks']:
        print(f"\n🚨 ACTION REQUIRED: Review {len(tracking['brand_risks'])} flagged posts")

if __name__ == '__main__':
    main()
