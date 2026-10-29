#!/usr/bin/env python3
"""Free TikTok / Instagram / Facebook daily slots for the video loop.

The carousel batch fills TikTok/IG/FB 5/5/day, blocking the autonomous video
cross-post. These posts now only target IG/FB/TikTok (LinkedIn + YouTube were
already removed), so stripping all three leaves nothing — the post is deleted.
That's intended: carousels are the losing format (2-3 views) being replaced by
video (240-594). Only FUTURE posts are touched; published ones are never removed.

  python3 zernio-free-video-slots.py --dry-run   # show what would change
  python3 zernio-free-video-slots.py             # apply
"""

import os
import sys
import time
import requests
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

ZERNIO_API_KEY = os.getenv("ZERNIO_API_KEY")
if not ZERNIO_API_KEY:
    raise ValueError("ZERNIO_API_KEY not set")

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}
STRIP = {"tiktok", "instagram", "facebook"}
THROTTLE = 1.0


def fetch_all_posts() -> list:
    posts, page, seen = [], 1, set()
    while True:
        r = requests.get(f"{BASE}/posts", headers=HEADERS,
                        params={"limit": 100, "page": page}, timeout=30)
        r.raise_for_status()
        data = r.json()
        batch = data.get("data", data.get("posts", [])) if isinstance(data, dict) else data
        new = [p for p in batch if isinstance(p, dict)
               and (p.get("_id") or p.get("id")) not in seen]
        if not new:
            break
        for p in new:
            seen.add(p.get("_id") or p.get("id"))
        posts.extend(new)
        if len(batch) < 100:
            break
        page += 1
    return posts


def get_full(post_id: str) -> dict:
    r = requests.get(f"{BASE}/posts/{post_id}", headers=HEADERS, timeout=30)
    r.raise_for_status()
    d = r.json()
    return d.get("data", d.get("post", d)) if isinstance(d, dict) else d


def strip_platforms(post: dict) -> tuple:
    pid = post.get("_id") or post.get("id")
    remaining = [pl for pl in post.get("platforms", [])
                 if not (isinstance(pl, dict) and pl.get("platform") in STRIP)]
    if not remaining:                              # nothing left → delete the post
        d = requests.delete(f"{BASE}/posts/{pid}", headers=HEADERS, timeout=30)
        if d.status_code == 429:
            return (None, "rate_limited")
        return (d.status_code in (200, 201, 204), f"deleted [{d.status_code}]")

    post["platforms"] = remaining
    for pl in post["platforms"]:
        if isinstance(pl.get("accountId"), dict):
            pl["accountId"] = pl["accountId"].get("_id", pl["accountId"])
    if isinstance(post.get("userId"), dict):
        post["userId"] = post["userId"].get("id", post["userId"].get("_id"))
    post["isDraft"] = False
    r = requests.put(f"{BASE}/posts/{pid}", headers=HEADERS, json=post, timeout=30)
    if r.status_code == 429:
        return (None, "rate_limited")
    return (r.status_code in (200, 201), f"stripped [{r.status_code}]")


def main():
    dry = "--dry-run" in sys.argv
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    print("Fetching posts...")
    posts = fetch_all_posts()

    targets, deletes = [], 0
    for p in posts:
        if not isinstance(p, dict):
            continue
        if (p.get("scheduledFor") or "") <= now_iso:
            continue
        plats = {pl.get("platform") for pl in p.get("platforms", []) if isinstance(pl, dict)}
        if plats & STRIP:
            keep = plats - STRIP
            if not keep:
                deletes += 1
            targets.append((p.get("_id") or p.get("id"), (p.get("scheduledFor") or "")[:10], keep))

    targets.sort(key=lambda t: t[1])
    print(f"Future posts to free on TikTok/IG/FB: {len(targets)} ({deletes} fully deleted, "
          f"{len(targets) - deletes} keep another platform)")
    for pid, day, keep in targets[:20]:
        print(f"  {day}  {'DELETE (no platform left)' if not keep else 'keep: ' + ', '.join(keep)}")

    if dry:
        print("\n(dry run — nothing changed)")
        return

    freed, failed = 0, []
    for i, (pid, _, _) in enumerate(targets):
        ok, msg = strip_platforms(get_full(pid))
        while ok is None:
            print("  429 — backing off 60s")
            time.sleep(60)
            ok, msg = strip_platforms(get_full(pid))
        if ok:
            freed += 1
        else:
            failed.append((pid, msg))
        if (i + 1) % 15 == 0:
            print(f"  {i+1}/{len(targets)} ({freed} done)")
        time.sleep(THROTTLE)

    print(f"\nDone. Freed: {freed}/{len(targets)}")
    if failed:
        for pid, msg in failed[:10]:
            print(f"  {pid}: {msg}")


if __name__ == "__main__":
    main()
