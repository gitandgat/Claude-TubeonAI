#!/usr/bin/env python3
import os, json, time, sys, requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
ZERNIO_API_KEY = os.getenv('ZERNIO_API_KEY')
if not ZERNIO_API_KEY:
    print("ERROR: ZERNIO_API_KEY not found")
    sys.exit(1)

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}
FACEBOOK_ID = "6909409a5f6fbb9ef8323074"
PHILOSOPHY_LINK = "www.crosswalkwisdom.com/philosophy"

POSTS = [
    {
        'title': 'The Credential Halo',
        'date': '2026-05-29', 'time': '12:00',
        'image': 'Philosophy images/The Credential Halo.jpeg',
        'content': """The credential halo is a cage nobody talks about.

You get credentialed in one thing, and suddenly—that's all people can see you doing. MD = clinic. MBA = corporate. The degree becomes a ceiling disguised as a launching pad.

I spent years as a doctor. And yes, that training was valuable. But it taught me something the system never intended: *how to see problems others can't.*

Clinical thinking means pattern recognition. It means staying calm in ambiguity. It means understanding systems well enough to know where they break.

Those skills are worth infinitely more *outside* the clinic than inside it.

But the halo effect keeps credentialed people trapped in credential-shaped roles. Your degree becomes proof that you *can't* do anything else. Never mind that it's actually your best asset for doing everything else.

Stop letting people's limited imagination define your scope.""",
    },
    {
        'title': 'The Sunk Cost Projection',
        'date': '2026-05-30', 'time': '12:00',
        'image': 'Philosophy images/The Sunk Cost Projection.jpeg',
        'content': """Here's what took me years to understand: when people question your unconventional choice, they're not actually questioning *you*. They're questioning themselves.

"Why would you leave medicine?" really means: "I'm terrified I wasted my degree, and your freedom is making me feel it."

The sunk cost projection is real and it's everywhere. People take your choices personally because your choices feel like a referendum on theirs. If you can walk away from something "everyone wants," what does that say about them staying?

So they push back. Not maliciously. Out of self-protection.

They want you back in the box because it makes the box feel safer. For them.

But here's the boundary you need: You don't owe anyone reassurance about their choices. You especially don't owe them a performance of regret to make them feel better about staying.

Your path doesn't invalidate theirs. But your freedom might expose something they've been avoiding.

That's their work, not yours.""",
    },
]

def upload_image(path):
    filename = os.path.basename(path)
    filesize = os.path.getsize(path)
    ctype = "image/jpeg" if path.lower().endswith('.jpeg') else "image/png"

    r = requests.post(f"{BASE}/media/presign", headers=HEADERS, json={"filename": filename, "contentType": ctype, "fileSize": filesize}, timeout=60)
    r.raise_for_status()
    data = r.json()

    with open(path, "rb") as f:
        put_r = requests.put(data["uploadUrl"], data=f, headers={"Content-Type": ctype}, timeout=120)
        put_r.raise_for_status()

    return data['publicUrl']

def schedule_post(post, img_url):
    dt = f"{post['date']}T{post['time']}:00"
    body = {
        "content": post['content'],
        "mediaItems": [{"url": img_url, "type": "image"}],
        "platforms": [{"platform": "facebook", "accountId": FACEBOOK_ID}],
        "scheduledFor": dt,
        "timezone": "America/New_York",
        "firstComment": f"Read the full philosophy behind this insight:\n{PHILOSOPHY_LINK}",
    }

    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body, timeout=60)
    r.raise_for_status()
    result = r.json()
    post_id = result.get('id') or result.get('_id') or 'N/A'
    return {'title': post['title'], 'scheduled_at': dt, 'post_id': post_id, 'status': 'success'}

print("Scheduling remaining 2 posts to Facebook only...")
for idx, post in enumerate(POSTS, 1):
    try:
        print(f"[{idx}/2] {post['title']}")
        img = upload_image(post['image'])
        result = schedule_post(post, img)
        print(f"  ✓ Scheduled to Facebook")
    except Exception as e:
        print(f"  ✗ Failed: {str(e)[:100]}")
    if idx < len(POSTS):
        time.sleep(30)

print("\nDone! All 2 remaining posts scheduled to Facebook.")
