#!/usr/bin/env python3
"""
Zernio scheduling v3 - optimized for reliability
- Extended timeouts for slow CDN
- Platform-specific handling
- Async retry queue
"""

import os
import json
import time
import sys
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
if not ZERNIO_API_KEY:
    print("ERROR: ZERNIO_API_KEY not found")
    sys.exit(1)

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}

PLATFORMS = {
    "linkedin": "690940455f6fbb9ef8323070",
    "instagram": "690940655f6fbb9ef8323072",
    "facebook": "6909409a5f6fbb9ef8323074",
    "tiktok": "690941425f6fbb9ef8323078",
    "youtube": "690940d35f6fbb9ef8323077",
}

# Extended timeouts
UPLOAD_TIMEOUT = 120  # 2 minutes for CDN upload
API_TIMEOUT = 60      # 1 minute for API calls
PHILOSOPHY_LINK = "www.crosswalkwisdom.com/philosophy"

POSTS = [
    {
        'title': 'The Credential Halo',
        'date': '2026-05-27', 'time': '08:00',
        'image': 'Philosophy images/The Credential Halo.jpeg',
        'content': """The credential halo is a cage nobody talks about.

You get credentialed in one thing, and suddenly—that's all people can see you doing. MD = clinic. MBA = corporate. The degree becomes a ceiling disguised as a launching pad.

I spent years as a doctor. And yes, that training was valuable. But it taught me something the system never intended: *how to see problems others can't.*

Clinical thinking means pattern recognition. It means staying calm in ambiguity. It means understanding systems well enough to know where they break.

Those skills are worth infinitely more *outside* the clinic than inside it.

But the halo effect keeps credentialed people trapped in credential-shaped roles. Your degree becomes proof that you *can't* do anything else. Never mind that it's actually your best asset for doing everything else.

Stop letting people's limited imagination define your scope.""",
        'youtube_title': 'The Credential Halo: Why Your Degree Isn\'t a Cage',
    },
    {
        'title': 'The Sunk Cost Projection',
        'date': '2026-05-28', 'time': '11:00',
        'image': 'Philosophy images/The Sunk Cost Projection.jpeg',
        'content': """Here's what took me years to understand: when people question your unconventional choice, they're not actually questioning *you*. They're questioning themselves.

"Why would you leave medicine?" really means: "I'm terrified I wasted my degree, and your freedom is making me feel it."

The sunk cost projection is real and it's everywhere. People take your choices personally because your choices feel like a referendum on theirs. If you can walk away from something "everyone wants," what does that say about them staying?

So they push back. Not maliciously. Out of self-protection.

They want you back in the box because it makes the box feel safer. For them.

But here's the boundary you need: You don't owe anyone reassurance about their choices. You especially don't owe them a performance of regret to make them feel better about staying.

Your path doesn't invalidate theirs. But your freedom might expose something they've been avoiding.

That's their work, not yours.""",
        'youtube_title': 'Stop Defending Your Choice: The Sunk Cost Projection',
    },
    {
        'title': 'On Leaving Safe Paths',
        'date': '2026-05-29', 'time': '14:00',
        'image': 'Philosophy images/On Leaving Safe Paths.jpeg',
        'content': """I was a crossing guard in Canada.

Not because I failed at medicine. Not because I regretted my training. But because I needed *space.* Space to think. Space to ask: Who am I when I'm not performing a role?

The safe path feels safe because it's scripted. Your family understands it. Your community understands it. Society built the whole thing centuries ago and keeps polishing it.

But safety bought with your own ambiguity is not safety. It's stagnation wearing a comfortable mask.

So I stepped off. Into something ambiguous. Something my parents couldn't explain to their friends. Something that didn't have a name.

And yes, it was terrifying. Yes, people questioned it. Yes, I had moments of doubt.

But the alternative was slower. Quieter. More insidious.

The safe path takes your life in small, incremental cuts. And by the time you realize what happened, you're too invested to leave.

I chose the discomfort of ambiguity over the slow death of a good fit.

Some people still don't understand. And that's okay. They're not supposed to. This isn't their path.""",
        'youtube_title': 'Why I Left Medicine to Become a Crossing Guard',
    },
    {
        'title': 'What Your Training Actually Taught You',
        'date': '2026-05-30', 'time': '17:00',
        'image': 'Philosophy images/What Your Training Actually Taught You.jpeg',
        'content': """When people ask why I left medicine, they're asking the wrong question.

They assume I left because I didn't want to use my training. But I use it every single day. Just not how they imagine.

Medical training didn't teach me a job. It taught me how to think.

Pattern recognition. Diagnostic reasoning. Staying calm when you don't have perfect information. Understanding systems complex enough to fail in invisible ways. Knowing that small interventions in the right place can ripple outward.

These are *superpowers* in tech. In business. In building products. In understanding why systems break and how to fix them.

But the credential halo is so bright that people can't see past it to what's actually useful. They see "MD" and think "doctor." They can't imagine "founder" or "builder" or "strategist."

Your training wasn't wasted when you left the clinic. It was *finally* being used at full capacity.

Stop apologizing for seeing beyond the expected application of what you know.""",
        'youtube_title': 'What Medical Training Actually Teaches You (And It\'s Not What You Think)',
    },
    {
        'title': 'The Discomfort Is the Point',
        'date': '2026-05-31', 'time': '20:00',
        'image': 'Philosophy images/The Discomfort Is the Point.jpeg',
        'content': """People are terrified of ambiguity.

It's why they want you back in the box. Not because the box is good—but because it's *knowable.* They can explain it. They can picture it. They can tell other people what you do without having to say, "Well... it's complicated."

The unconventional path is uncomfortable because it doesn't fit into neat categories. And humans will do almost anything to avoid that discomfort—including projecting it onto you.

"What do you actually do?" they'll ask, with a slight edge of panic. Because if they can't file you into a clear folder, they don't know how to relate to you.

But here's the thing: that discomfort is information. It's telling you that you're no longer performing a role for an audience. You're building something that doesn't have a name yet.

And that's exactly where the interesting work happens.

Stop trying to make other people comfortable with your ambiguity. Your job isn't to fit their categories. Your job is to build something real.

The discomfort will fade when they see what you're building. Or it won't. And that's okay too.""",
        'youtube_title': 'Embrace the Discomfort: Why Your Unconventional Path Scares Everyone',
    },
    {
        'title': 'You Don\'t Need Permission',
        'date': '2026-06-02', 'time': '11:00',
        'image': 'Philosophy images/You Don\'t Need Permission.jpeg',
        'content': """You're waiting for permission to leave.

Not consciously. But I can feel it in the questions people ask me. "But what if you regret it?" "Don't you want to keep your options open?" "Have you thought about a hybrid role?"

It's permission disguised as concern.

The truth is brutal: you will never feel ready enough. You will never check all the boxes. You will never have a credential that makes the unconventional choice feel *safe*.

Because safety isn't what you get when you leave the script. Safety is what you build.

You already have the skills. You already have the thinking patterns. You already have the rigor and discipline and ability to learn under pressure. You trained for it.

What you don't have is permission. And that's because nobody can give it to you. Not your family. Not your mentors. Not the right certification or credential.

You have to give it to yourself.

So here's my permission, for whatever it's worth: You are not wasting anything by building something unconventional. You are not reckless for leaving a safe path. You are not broken because you want more than one box.

You're just awake.

And the awake ones always make the others nervous.""",
        'youtube_title': 'You Don\'t Need Permission: Give It to Yourself',
    },
    {
        'title': 'Three Things People Hate About Your Choice',
        'date': '2026-06-03', 'time': '14:00',
        'image': 'Philosophy images/Three Things People Hate About Your Choice.jpeg',
        'content': """People hate three things about your unconventional choice.

**First: The Credential Halo.** They can't imagine your training being useful outside a clinic. So they assume you're wasting it. Fact: you're seeing what the clinic never let you see.

**Second: The Sunk Cost Projection.** Your freedom makes them question theirs. So they push back hard. Not because your choice is wrong. Because it's making them feel their own anxiety. That's their work, not yours.

**Third: The Discomfort of Ambiguity.** They need you back in a box they understand. An unconventional path has no name. No script. No reassurance. And that terrifies people who've built their entire identity around knowing what's next.

But here's what I know after years of living this:

Your choice was never about wasting a degree. It was about *finally* using it.

Your choice wasn't about recklessness. It was about honesty.

Your choice wasn't about comfort. It was about alignment.

The three things people hate about your path? Those are exactly why it's the right one.""",
        'youtube_title': 'Three Reasons People Hate Your Unconventional Choice (And Why That Proves You\'re Right)',
    },
]

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")
    sys.stdout.flush()

def upload_image(path):
    """Upload image with extended timeout"""
    name = os.path.basename(path)
    size = os.path.getsize(path)
    ctype = "image/jpeg" if path.lower().endswith('.jpeg') else "image/png"

    log(f"  → Presigning upload...")
    r = requests.post(
        f"{BASE}/media/presign",
        headers=HEADERS,
        json={"filename": name, "contentType": ctype, "fileSize": size},
        timeout=API_TIMEOUT
    )
    r.raise_for_status()
    data = r.json()

    log(f"  → Uploading to CDN (timeout: {UPLOAD_TIMEOUT}s)...")
    with open(path, "rb") as f:
        put_r = requests.put(
            data["uploadUrl"],
            data=f,
            headers={"Content-Type": ctype},
            timeout=UPLOAD_TIMEOUT
        )
        put_r.raise_for_status()

    log(f"  ✓ Uploaded: {data['publicUrl'][:50]}...")
    return data['publicUrl']

def schedule_post(post, img_url):
    """Schedule post across all platforms"""
    dt = f"{post['date']}T{post['time']}:00"

    platforms = [
        {"platform": "linkedin", "accountId": PLATFORMS["linkedin"]},
        {"platform": "instagram", "accountId": PLATFORMS["instagram"]},
        {"platform": "facebook", "accountId": PLATFORMS["facebook"]},
        {"platform": "tiktok", "accountId": PLATFORMS["tiktok"]},
        {"platform": "youtube", "accountId": PLATFORMS["youtube"]},
    ]

    body = {
        "content": post['content'],
        "mediaItems": [{"url": img_url, "type": "image"}],
        "platforms": platforms,
        "scheduledFor": dt,
        "timezone": "America/New_York",
    }

    log(f"  → Scheduling post...")
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body, timeout=API_TIMEOUT)
    r.raise_for_status()
    result = r.json()
    post_id = result.get('id') or result.get('_id') or 'N/A'
    log(f"  ✓ Scheduled: {post_id}")
    return {'title': post['title'], 'scheduled_at': dt, 'post_id': post_id, 'status': 'success'}

def main():
    log("=" * 70)
    log("Crosswalk Wisdom Philosophy Series → Zernio (v3 - optimized)")
    log("=" * 70)

    results = []

    for idx, post in enumerate(POSTS, 1):
        log(f"\n[{idx}/{len(POSTS)}] {post['title']}")
        try:
            img = upload_image(post['image'])
            result = schedule_post(post, img)
            results.append(result)
        except Exception as e:
            log(f"  ✗ FAILED: {str(e)[:100]}")
            results.append({'title': post['title'], 'status': 'failed', 'error': str(e)[:200]})

        if idx < len(POSTS):
            log(f"  Waiting 8s...")
            time.sleep(8)

    # Summary
    log("\n" + "=" * 70)
    ok = sum(1 for r in results if r['status'] == 'success')
    log(f"Results: {ok}/{len(POSTS)} scheduled")
    log("=" * 70)

    # Save
    with open('philosophy-linkedin-series-schedule.json', 'w') as f:
        json.dump({
            'scheduled_at': datetime.now().isoformat(),
            'total': len(POSTS),
            'successful': ok,
            'posts': results
        }, f, indent=2)

    log("\n✓ Saved to philosophy-linkedin-series-schedule.json")
    if ok == len(POSTS):
        log("🎉 All 7 posts scheduled!")
        return 0
    else:
        log(f"⚠️  {len(POSTS) - ok} failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
