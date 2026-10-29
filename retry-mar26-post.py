#!/usr/bin/env python3
"""
One-off retry: schedule the Mar 26 post that failed due to LinkedIn daily limit.
Date moved to Apr 1 (next available slot) since Mar 26 has already passed.
"""

import requests
import time
from pathlib import Path

from zernio_key import ZERNIO_API_KEY as API_KEY
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
BASE = "https://zernio.com/api/v1"
OVERLAYS_DIR = Path("/Users/toto/Claude TubeonAI/crosswalk-remotion/out/overlays")

ACCT = {
    "facebook":  "6909409a5f6fbb9ef8323074",
    "instagram": "690940655f6fbb9ef8323072",
    "linkedin":  "690940455f6fbb9ef8323070",
}
PLATFORMS = [
    {"platform": "linkedin",  "accountId": ACCT["linkedin"]},
    {"platform": "instagram", "accountId": ACCT["instagram"]},
    {"platform": "facebook",  "accountId": ACCT["facebook"]},
]

DM_CTA = "\n\nComment FEAR below and I will DM you the link."

CONTENT = """When I told my mother I was leaving medicine, she cried.

Not because she was sad. Because she was scared for me.

"My son is a doctor." Four words that carry the weight of generations.

My friends did not know what to say. Some stopped calling. Some gave me the look.

Here is what I have learned:

"What will people think" lasts five minutes.

The life you are not living? That stays with you every day.

I chose to disappoint some people so I could stop disappointing myself.

That is not selfish. That is survival.

Take the free Fear Audit — separate real risk from social pressure."""

FILE = "02-what-will-people-think.mp4"
SCHEDULED_FOR = "2026-04-01T13:00:00.000Z"  # Apr 1 1pm UTC = 9am ET

filepath = OVERLAYS_DIR / FILE
if not filepath.exists():
    print(f"ERROR: File not found: {filepath}")
    exit(1)

print(f"Uploading {FILE}...")
r = requests.post(f"{BASE}/media",
                  headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                  json={"filename": filepath.name, "contentType": "video/mp4"})
if r.status_code != 200:
    print(f"Upload presign failed {r.status_code}: {r.text[:300]}")
    exit(1)

d = r.json()
upload_url = d["uploadUrl"]
public_url = d["publicUrl"]

size = filepath.stat().st_size
with open(filepath, "rb") as f:
    put = requests.put(upload_url, data=f.read(),
                       headers={"Content-Type": "video/mp4", "Content-Length": str(size)})
    if put.status_code not in (200, 201, 204):
        print(f"PUT failed {put.status_code}: {put.text[:300]}")
        exit(1)

print(f"  ✓ Uploaded → {public_url[:60]}...")

body = {
    "content": CONTENT + DM_CTA,
    "scheduledFor": SCHEDULED_FOR,
    "timezone": "America/New_York",
    "platforms": PLATFORMS,
    "mediaItems": [{"url": public_url, "type": "video"}],
}
r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
if r.status_code not in (200, 201):
    print(f"Post create failed {r.status_code}: {r.text[:400]}")
    exit(1)

pid = r.json().get("post", {}).get("_id", "?")
print(f"  ✓ Scheduled → post {pid}")
print(f"     Date: {SCHEDULED_FOR}  (Apr 1 9am ET)")
print(f"     Platforms: LinkedIn + Instagram + Facebook")
print("\nDone.")
