#!/usr/bin/env python3
"""
Hashtag Optimizer - Suggest optimal hashtags, test performance, ensure consistency.
Improves discoverability and reach.
"""

import os
import json
import requests
from datetime import datetime
from collections import defaultdict, Counter
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

# Suggested hashtags by topic
HASHTAG_LIBRARY = {
    'career': ['#CareerTransition', '#PhysicianLife', '#MedicalCareers', '#HealthcareWorkers', '#ChangeYourPath'],
    'identity': ['#IdentityCrisis', '#ProfessionalIdentity', '#WhoAmI', '#PersonalGrowth', '#FindYourPath'],
    'medicine': ['#Medicine', '#PhysicianBurnout', '#HealthcareHeroes', '#DoctorLife', '#MedicalStudents'],
    'mental_health': ['#MentalHealth', '#BurnoutRecovery', '#WellnessMatters', '#MentalHealthAwareness', '#SelfCare'],
    'success': ['#Success', '#Motivation', '#Inspiration', '#LeadershipDevelopment', '#PersonalSuccess'],
}

def extract_hashtags_from_content(content):
    """Extract existing hashtags"""
    import re
    hashtags = re.findall(r'#\w+', content)
    return list(set(hashtags))

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

def analyze_hashtags(posts):
    """Analyze hashtag usage"""
    analysis = {
        'total_posts': len(posts),
        'hashtag_frequency': Counter(),
        'posts_without_hashtags': 0,
        'hashtag_coverage': 0,
        'most_used': [],
        'unused_recommended': []
    }

    for post in posts:
        content = post.get('content', '')
        hashtags = extract_hashtags_from_content(content)

        if hashtags:
            for tag in hashtags:
                analysis['hashtag_frequency'][tag] += 1
        else:
            analysis['posts_without_hashtags'] += 1

    # Calculate coverage
    posts_with_hashtags = len(posts) - analysis['posts_without_hashtags']
    analysis['hashtag_coverage'] = (posts_with_hashtags / len(posts) * 100) if posts else 0

    # Top hashtags
    analysis['most_used'] = analysis['hashtag_frequency'].most_common(10)

    # Unused from library
    all_library_tags = set()
    for tags in HASHTAG_LIBRARY.values():
        all_library_tags.update(tags)

    used_tags = set(analysis['hashtag_frequency'].keys())
    analysis['unused_recommended'] = list(all_library_tags - used_tags)

    return analysis

def generate_hashtag_suggestions(content):
    """Suggest hashtags for specific content"""
    suggestions = []

    keywords = {
        'transition': HASHTAG_LIBRARY['career'],
        'identity': HASHTAG_LIBRARY['identity'],
        'medicine': HASHTAG_LIBRARY['medicine'],
        'mental': HASHTAG_LIBRARY['mental_health'],
        'success': HASHTAG_LIBRARY['success']
    }

    content_lower = content.lower()
    suggested_tags = set()

    for keyword, tags in keywords.items():
        if keyword in content_lower:
            suggested_tags.update(tags)

    # Include general recommendations
    suggested_tags.update(['#Crosswalk', '#Wisdom', '#PersonalGrowth'])

    return list(suggested_tags)[:8]  # Limit to 8 hashtags

def main():
    print("=" * 70)
    print("HASHTAG OPTIMIZER")
    print("=" * 70)
    print(f"Time: {datetime.now().isoformat()}\n")

    posts = get_all_posts()
    print(f"Analyzing {len(posts)} posts...\n")

    analysis = analyze_hashtags(posts)

    print("=" * 70)
    print("HASHTAG ANALYSIS")
    print("=" * 70)

    print(f"\nHashtag coverage: {analysis['hashtag_coverage']:.1f}%")
    print(f"Posts without hashtags: {analysis['posts_without_hashtags']}")

    print(f"\nTop 10 hashtags used:")
    for tag, count in analysis['most_used']:
        print(f"  {tag}: {count} posts")

    print(f"\nRecommended hashtags not yet used:")
    if analysis['unused_recommended']:
        for tag in analysis['unused_recommended'][:10]:
            print(f"  {tag}")
    else:
        print("  ✓ All recommended hashtags in use!")

    # Improvement recommendations
    recommendations = []
    if analysis['hashtag_coverage'] < 80:
        recommendations.append(f"Add hashtags to {100-analysis['hashtag_coverage']:.0f}% more posts")
    if len(analysis['most_used']) < 5:
        recommendations.append("Diversify hashtag usage - try more variety")

    if recommendations:
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"  • {rec}")

    report = {
        'timestamp': datetime.now().isoformat(),
        'analysis': {
            'total_posts': analysis['total_posts'],
            'hashtag_coverage': analysis['hashtag_coverage'],
            'posts_without_hashtags': analysis['posts_without_hashtags'],
            'most_used': analysis['most_used'],
            'unused_recommended': analysis['unused_recommended'][:10]
        }
    }

    with open('hashtag-report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Report saved to hashtag-report.json")

if __name__ == '__main__':
    main()
