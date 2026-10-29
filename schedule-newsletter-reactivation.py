"""
Schedule LinkedIn newsletter reactivation teaser post.
June 22, 2026 at 8am ET — LinkedIn only.
"""

import requests
import json

from zernio_key import ZERNIO_API_KEY as API_KEY

BASE_URL = "https://zernio.com/api/v1"
LINKEDIN_ID = "690940455f6fbb9ef8323070"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

CONTENT = """I went quiet for a while.

Not because I had nothing to say — but because I was trying to say everything perfectly, and that made me say nothing.

Here's what I've been figuring out:

IMGs in Canada aren't stuck because they lack options.

They're stuck because they've been trained to see leaving medicine as failure.

That's not a career problem. That's an identity problem.

And identity problems don't get solved by job boards or resume tips.

They get solved when someone shows you a different way to see yourself.

My newsletter is back — one idea a week that reframes what a "wasted" medical career actually means, and what's possible on the other side of that story.

If you're an IMG who feels like your training was a trap, subscribe via the link in my profile.

And if you know someone who needs to hear this — share this post with them."""

payload = {
    "content": CONTENT,
    "platforms": [
        {"platform": "linkedin", "accountId": LINKEDIN_ID, "scheduledFor": "2026-06-22T08:00:00"},
    ],
    "scheduledFor": "2026-06-22T08:00:00",
    "timezone": "America/New_York",
    "isDraft": False,
}

resp = requests.post(f"{BASE_URL}/posts", headers=HEADERS, json=payload)
print(f"Status: {resp.status_code}")
print(json.dumps(resp.json(), indent=2))
