#!/usr/bin/env python3
"""
Schedule 5 philosophy LinkedIn posts to Zernio across all platforms.
Timing: Day 1 (Kintsugi), Day 4 (Ikigai), Day 8 (Shoshin), Day 11 (Ma), Day 15 (Philosophy)
Time: 8am-9am ET each day (varies by platform for optimal engagement)
"""

import os
import json
from datetime import datetime, timedelta
import requests

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
if not ZERNIO_API_KEY:
    raise ValueError("ZERNIO_API_KEY environment variable not set")

# Post definitions with timing
POSTS = [
    {
        'title': 'Kintsugi Hook - Broken Pottery',
        'day': 1,
        'time': '08:00',  # 8am ET
        'image': 'linkedin-post-01-kintsugi.png',
        'body': 'There\'s a Japanese art called Kintsugi.\n\nBroken pottery. Repaired with gold.\n\nAnd here\'s what\'s wild: the broken pieces aren\'t less beautiful after. They\'re *more* beautiful. The gold doesn\'t hide the cracks—it *honors* them. The damage becomes the masterpiece.\n\nI think about this when I see IMGs in low-level positions.\n\nA physician. A world-class education. Credentials that took everything. And somehow ending up in a role that feels... broken. Like the system took your masterpiece and cracked it.\n\nAnd here\'s the thing you\'re probably thinking: "I\'m broken. I failed. I wasted it all."\n\nWrong question.\n\nThe real question isn\'t: "How do I hide the cracks?"\n\nIt\'s: "How do I let the cracks become the gold?"\n\nYour burnout. Your sunk cost. Your identity crisis. These aren\'t failures.\n\nThey\'re the first signs of a deeper repair happening.\n\nWe\'ve just written a full philosophy on this—on what Japanese wisdom teaches about crossing from a broken career into a whole life.\n\nIt\'s free. It\'s real. It\'s probably the most honest thing you\'ll read about career transition.',
        'first_comment': 'Read the full Crosswalk Wisdom philosophy + Japanese wisdom integration here:\n→ www.crosswalkwisdom.com/philosophy\n\nTake the Fear Audit: www.crosswalkwisdom.com/fear-audit'
    },
    {
        'title': 'Ikigai Hook - Purpose Over Prestige',
        'day': 4,
        'time': '08:00',  # 8am ET
        'image': 'linkedin-post-02-ikigai.png',
        'body': 'You have credentials.\n\nYou have:\n- Debt from the education\n- Sunk cost from the years\n- Prestige on paper\n- Nothing in your body that feels alive\n\nThis is what happens when you choose a career based on what looks good instead of what feeds your soul.\n\nThe Japanese call it Ikigai.\n\nNot "career success." Not "prestigious title."\n\n*Reason for being.*\n\nThe intersection of:\n- What you love\n- What you\'re good at\n- What the world needs\n- What you can be paid for\n\nMost people pick one. Usually the last one. "I can be paid for this."\n\nThen they\'re 35, credentialed, broken, asking: "Is this all there is?"\n\nAnd the answer is: No. Not if you stop choosing from fear.\n\nThe question isn\'t: "How do I make this career work?"\n\nIt\'s: "What actually feeds my reason for being?"\n\nThat\'s Crossing Guard Philosophy. That\'s the Courage to Choose.\n\nWe just published a full breakdown of how Japanese wisdom (Ikigai, Shoshin, Ma, Kintsugi, Wabi-Sabi) maps to career crossing.',
        'first_comment': 'Read the full philosophy + five Japanese concepts:\n→ www.crosswalkwisdom.com/philosophy\n\nThen take the Fear Audit to see which fears are actually holding you back:\n→ www.crosswalkwisdom.com/fear-audit'
    },
    {
        'title': 'Shoshin Hook - Beginner\'s Mind',
        'day': 8,
        'time': '08:00',  # 8am ET
        'image': 'linkedin-post-03-shoshin.png',
        'body': 'You know too much.\n\nThat sounds like a compliment. It\'s not. It\'s why you\'re stuck.\n\nThere\'s a Zen concept called Shoshin: "beginner\'s mind."\n\nThe idea: an expert who clings to their expertise can\'t learn anything new. But a beginner—someone willing to not know—can learn *everything*.\n\nFor credentialed professionals (physicians, engineers, lawyers, IMGs), this is the cage.\n\nYou\'ve built an entire identity around expertise. You\'re *supposed* to know. You\'re *supposed* to be the expert in the room.\n\nSo when you consider starting over? Getting a job where you\'re *not* the expert? Where nobody recognizes your credentials?\n\nIt feels like death. Like you\'re going backwards.\n\nBut here\'s the thing the best practitioners know:\n\nYour greatest superpower isn\'t your expertise. It\'s your ability to *relearn*.\n\nThe MD who becomes an entrepreneur isn\'t valuable *because* they know medicine. They\'re valuable because they\'re willing to be a beginner in business, marketing, sales—and bring a beginner\'s mind to problems everyone else thinks they already understand.\n\nShoshin teaches: *The expert\'s secret weapon is the beginner\'s mind.*',
        'first_comment': 'Full Crosswalk Wisdom Philosophy (with Shoshin + 4 other Japanese concepts):\n→ www.crosswalkwisdom.com/philosophy\n\nFree IMG Pivot Challenge (7 days):\n→ www.crosswalkwisdom.com/img-pivot-challenge'
    },
    {
        'title': 'Ma Hook - The Meaningful Gap',
        'day': 11,
        'time': '08:00',  # 8am ET
        'image': 'linkedin-post-04-ma.png',
        'body': 'You\'re in the gap.\n\nYou left the career. No job title. No clear next move. No identity that fits anymore.\n\nAnd it feels like *nothing*.\n\nThere\'s a Japanese aesthetic called Ma.\n\nNot the absence of something. Not emptiness like "void."\n\nMa is the *presence* of space.\n\nThe silence between notes is part of the music. The empty space in a painting gives the whole work meaning. The pause in conversation is where understanding happens.\n\nMa teaches that emptiness is not void—it\'s *potential*.\n\nRight now, you\'re in the Ma of your career crossing.\n\nThat silence? That\'s not wasted time. That\'s where you\'re learning to listen to yourself instead of listening to everyone else.\n\nThat emptiness? That\'s not failure. That\'s the raw material of who you\'re becoming.\n\nMost people rush to fill the Ma. They get a job immediately just to feel solid again. They grab the first offer. They stop the silence.\n\nAnd they miss the whole point.\n\nThe real work happens in the gap.\n\nWe just wrote a philosophy that breaks down what the Ma teaches about career crossing—and the other four Japanese concepts that apply to every stage of your transition.',
        'first_comment': 'Full Crosswalk Wisdom Philosophy:\n→ www.crosswalkwisdom.com/philosophy\n\nTake the Fear Audit (reveals which of your 5 fears is strongest):\n→ www.crosswalkwisdom.com/fear-audit'
    },
    {
        'title': 'Philosophy Overview - East Meets West',
        'day': 15,
        'time': '08:00',  # 8am ET
        'image': 'linkedin-post-05-philosophy.png',
        'body': 'Western career coaching is broken.\n\n"Follow your passion."\n"Take the leap."\n"Hustle your way to success."\n\nIt\'s all momentum. All action. All go, go, go.\n\nAnd it doesn\'t work for professionals actually in crisis.\n\nYou can\'t "follow your passion" when you\'re $300k in debt. You can\'t "just pivot" when your entire identity is built on credentials. You can\'t "fake it till you make it" when you\'ve already given everything.\n\nEastern philosophy understands something Western self-help misses.\n\n**Sometimes the answer isn\'t forward. It\'s *inward*.**\n\nKintsugi teaches: your brokenness is where the gold lives.\nIkigai teaches: purpose beats prestige.\nShoshin teaches: not-knowing is a superpower.\nWabi-Sabi teaches: impermanence is beautiful.\nMa teaches: the gap is where you become whole.\n\nThese aren\'t motivational quotes. They\'re real frameworks for understanding what happens when a high-credential professional hits rock bottom and has to choose between the cage and the unknown.\n\nWe\'ve just published our most comprehensive philosophy on career crossing—bridging Western psychology with Eastern wisdom, specifically for IMGs and credentialed professionals stuck between careers.',
        'first_comment': 'Full Crosswalk Wisdom Philosophy (East meets West):\n→ www.crosswalkwisdom.com/philosophy\n\nDownload the free philosophy guide:\n→ www.crosswalkwisdom.com/download-philosophy-guide\n\nSubscribe to essays on identity, sunk cost, and crossing:\n→ www.crosswalkwisdom.com/subscribe'
    }
]

def calculate_schedule_time(day_offset):
    """Calculate UTC time from day offset (8am ET)"""
    base_date = datetime.now()
    target_date = base_date + timedelta(days=day_offset - 1)
    # 8am ET = 1pm UTC (EDT) or 12pm UTC (EST)
    # Using 13:00 UTC for EDT (current)
    return target_date.replace(hour=13, minute=0, second=0).isoformat() + 'Z'

def schedule_post_to_zernio(post_data, platforms):
    """
    Schedule a single post to Zernio across all platforms.

    Args:
        post_data: Dict with title, body, first_comment, image, day, time
        platforms: List of platform codes ['linkedin', 'instagram', 'facebook', 'tiktok', 'youtube']
    """

    image_path = f"/Users/toto/Claude TubeonAI/{post_data['image']}"

    # Read image file
    with open(image_path, 'rb') as f:
        image_data = f.read()

    schedule_time = calculate_schedule_time(post_data['day'])

    print(f"\n📱 Scheduling: {post_data['title']}")
    print(f"   Time: {schedule_time}")
    print(f"   Platforms: {', '.join(platforms)}")

    # API request to Zernio
    headers = {
        'Authorization': f'Bearer {ZERNIO_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'title': post_data['title'],
        'content': post_data['body'],
        'first_comment': post_data['first_comment'],
        'scheduled_at': schedule_time,
        'platforms': platforms,
        'image_path': image_path,  # Zernio will handle upload
    }

    try:
        response = requests.post(
            'https://api.zernio.com/posts',
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        print(f"   ✓ Scheduled post ID: {result.get('id', 'N/A')}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Error scheduling: {str(e)}")
        return None

def main():
    print("=" * 60)
    print("Crosswalk Wisdom Philosophy Posts → Zernio Scheduling")
    print("=" * 60)

    platforms = ['linkedin', 'instagram', 'facebook', 'tiktok']  # YouTube typically video-only

    scheduled_posts = []

    for post in POSTS:
        result = schedule_post_to_zernio(post, platforms)
        if result:
            scheduled_posts.append({
                'title': post['title'],
                'scheduled_at': calculate_schedule_time(post['day']),
                'zernio_id': result.get('id')
            })

    print("\n" + "=" * 60)
    print(f"Total posts scheduled: {len(scheduled_posts)}/5")
    print("=" * 60)

    # Save schedule to file for reference
    with open('philosophy-posts-schedule.json', 'w') as f:
        json.dump({
            'scheduled_at': datetime.now().isoformat(),
            'posts': scheduled_posts,
            'timing_strategy': {
                'day_1': 'Kintsugi Hook',
                'day_4': 'Ikigai Hook',
                'day_8': 'Shoshin Hook',
                'day_11': 'Ma Hook',
                'day_15': 'Philosophy Overview'
            }
        }, f, indent=2)

    print("\n✓ Schedule saved to philosophy-posts-schedule.json")

if __name__ == '__main__':
    main()
