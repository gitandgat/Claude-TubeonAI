#!/usr/bin/env python3
"""
Remove the YouTube platform entry from future image-only Zernio posts.

Root cause (Jun 12 audit): the June batch scheduled 5-platform packages,
but YouTube rejects image posts ("YouTube posts require video content").
Every such post publishes on LI/IG/FB/TT then flips to 'partial' and
retries YouTube forever.

Only touches FUTURE posts (scheduledFor > now UTC). Past partials are left
alone — their working platforms already published; re-PUTting them risks
duplicate publishes.

Usage:
  python3 zernio-remove-youtube-image-posts.py --dry-run   # report only
  python3 zernio-remove-youtube-image-posts.py             # apply fixes
"""

import os
import sys
import time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

ZERNIO_API_KEY = os.getenv("ZERNIO_API_KEY")
if not ZERNIO_API_KEY:
    raise ValueError("ZERNIO_API_KEY not set")

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_API_KEY}", "Content-Type": "application/json"}
THROTTLE_SECONDS = 1.0
RATE_LIMIT_BACKOFF = 60


def fetch_all_posts() -> list:
    """Page with ?page=N — Zernio ignores 'offset' and repeats page 1."""
    posts, page = [], 1
    seen_ids = set()
    while True:
        resp = requests.get(f"{BASE}/posts", headers=HEADERS,
                            params={"limit": 100, "page": page}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("data", data.get("posts", [])) if isinstance(data, dict) else data
        if not batch:
            break
        new = [p for p in batch if isinstance(p, dict)
               and (p.get("_id") or p.get("id")) not in seen_ids]
        if not new:  # API repeating itself — stop
            break
        for p in new:
            seen_ids.add(p.get("_id") or p.get("id"))
        posts.extend(new)
        if len(batch) < 100:
            break
        page += 1
    return posts


def get_full_post(post_id: str) -> dict:
    resp = requests.get(f"{BASE}/posts/{post_id}", headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", data.get("post", data)) if isinstance(data, dict) else data


def is_image_only(post: dict) -> bool:
    media = post.get("mediaItems", [])
    return bool(media) and all(m.get("type") == "image" for m in media if isinstance(m, dict))


def put_post_without_youtube(post: dict) -> tuple:
    """PUT full post body back with youtube removed. Returns (ok, message)."""
    post_id = post.get("_id") or post.get("id")
    post["platforms"] = [
        p for p in post.get("platforms", [])
        if not (isinstance(p, dict) and p.get("platform") == "youtube")
    ]
    # accountId must be a string ID, not the populated object (May 29 fix)
    for plat in post["platforms"]:
        if isinstance(plat.get("accountId"), dict):
            plat["accountId"] = plat["accountId"].get("_id", plat["accountId"])
    if isinstance(post.get("userId"), dict):
        post["userId"] = post["userId"].get("id", post["userId"].get("_id"))
    # keep the post scheduled (isDraft governs status)
    post["isDraft"] = False

    resp = requests.put(f"{BASE}/posts/{post_id}", headers=HEADERS, json=post, timeout=30)
    if resp.status_code == 429:
        return None, "rate_limited"
    if resp.status_code in (200, 201):
        return True, "OK"
    return False, f"{resp.status_code}: {resp.text[:120]}"


def main():
    dry_run = "--dry-run" in sys.argv
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    print("Fetching all posts...")
    posts = fetch_all_posts()
    print(f"Total posts: {len(posts)}")

    targets = []
    for p in posts:
        if not isinstance(p, dict):
            continue
        sched = p.get("scheduledFor") or ""
        has_youtube = any(
            isinstance(pl, dict) and pl.get("platform") == "youtube"
            for pl in p.get("platforms", [])
        )
        if has_youtube and sched > now_iso and is_image_only(p):
            targets.append((p.get("_id") or p.get("id"), sched))

    # de-dup, keep chronological order
    targets = sorted(set(targets), key=lambda t: t[1])
    print(f"Future image-only posts with YouTube to fix: {len(targets)}")

    if dry_run:
        for pid, sched in targets[:20]:
            print(f"  would fix {pid} @ {sched}")
        print("(dry run — nothing changed)")
        return

    fixed, failed = 0, []
    for i, (pid, sched) in enumerate(targets):
        full = get_full_post(pid)
        if not full:
            failed.append((pid, "fetch failed"))
            continue

        ok, msg = put_post_without_youtube(full)
        while ok is None:  # rate limited — back off and retry
            print(f"  429 — backing off {RATE_LIMIT_BACKOFF}s")
            time.sleep(RATE_LIMIT_BACKOFF)
            ok, msg = put_post_without_youtube(get_full_post(pid))

        if ok:
            fixed += 1
        else:
            failed.append((pid, msg))

        if (i + 1) % 20 == 0:
            print(f"  {i + 1}/{len(targets)} processed ({fixed} fixed, {len(failed)} failed)")
        time.sleep(THROTTLE_SECONDS)

    print(f"\nDone. Fixed: {fixed}/{len(targets)}")
    if failed:
        print("Failures:")
        for pid, msg in failed[:10]:
            print(f"  {pid}: {msg}")


if __name__ == "__main__":
    main()
