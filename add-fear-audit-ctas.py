#!/usr/bin/env python3
"""
Add Fear Audit CTAs to all future scheduled Zernio posts.

Per-platform strategy:
- LinkedIn:  P.S. line in body (no URL) + link in first comment (platformSpecificData.firstComment)
- Facebook:  link appended to body (links fine on FB)
- Instagram: "link in bio" CTA (links not clickable)
- TikTok:    "link in bio" CTA (links not clickable)
- YouTube:   link appended to description

Idempotent: skips any platform copy that already mentions the Fear Audit.

Usage:
  python3 add-fear-audit-ctas.py --dry-run          # show what would change
  python3 add-fear-audit-ctas.py --test             # update only the latest-scheduled post, then verify
  python3 add-fear-audit-ctas.py                    # update all future posts
  python3 add-fear-audit-ctas.py --verify           # re-fetch and report CTA coverage
"""

import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

ZERNIO_KEY = os.environ["ZERNIO_API_KEY"]  # raises if missing
BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {ZERNIO_KEY}", "Content-Type": "application/json"}

TODAY = "2026-06-11"
QUIZ_URL = "https://fear-audit.vercel.app"
MARKER = "Fear Audit"  # idempotency check

LINKEDIN_PS = [
    "\n\nP.S. If you've read this far, the free 3-minute Fear Audit in the first comment will tell you which fear is actually keeping you at the curb.",
    "\n\nP.S. There's a free 3-minute Fear Audit in the first comment. It names the exact fear holding you at the curb — money, judgment, or identity.",
    "\n\nP.S. First comment has the free 3-minute Fear Audit. Three fears, one score, and a clearer picture of why you're still waiting.",
]

LINKEDIN_FIRST_COMMENT = (
    f"Take the free 3-minute Fear Audit → {QUIZ_URL}\n\n"
    "It scores the three fears that keep people at the curb — money, judgment, "
    "identity — and tells you which one is actually running your decisions."
)

FACEBOOK_CTA = (
    f"\n\n—\nFree 3-minute Fear Audit: {QUIZ_URL}\n"
    "Find out which fear — money, judgment, or identity — is actually running your decisions."
)

BIO_CTA = (
    "\n\nFree 3-minute Fear Audit — link in bio. It tells you which fear "
    "(money, judgment, or identity) is actually keeping you at the curb."
)

YOUTUBE_CTA = f"\n\nFree 3-minute Fear Audit: {QUIZ_URL}"


def fetch_future_posts() -> list:
    r = requests.get(f"{BASE}/posts?limit=200", headers=HEADERS, timeout=20)
    r.raise_for_status()
    posts = r.json().get("posts", [])
    future = [p for p in posts if p.get("scheduledFor", "") >= TODAY]
    future.sort(key=lambda p: p.get("scheduledFor", ""))
    return future


def normalize_account_id(plat: dict) -> dict:
    """accountId must be a string ID, not a nested object (May 29 fix)."""
    acc = plat.get("accountId")
    if isinstance(acc, dict):
        plat["accountId"] = acc.get("_id") or acc.get("id")
    return plat


def build_updated_platforms(post: dict, ps_index: int) -> tuple[list, bool]:
    """Return (updated platform list, changed flag)."""
    changed = False
    updated = []
    for plat in post.get("platforms", []):
        p = dict(plat)
        normalize_account_id(p)
        name = p.get("platform", "")
        copy = p.get("customContent") or post.get("content", "")

        if MARKER in copy:
            updated.append(p)
            continue

        if name == "linkedin":
            p["customContent"] = copy + LINKEDIN_PS[ps_index % len(LINKEDIN_PS)]
            psd = dict(p.get("platformSpecificData") or {})
            psd["firstComment"] = LINKEDIN_FIRST_COMMENT
            p["platformSpecificData"] = psd
            changed = True
        elif name == "facebook":
            p["customContent"] = copy + FACEBOOK_CTA
            changed = True
        elif name in ("instagram", "tiktok"):
            p["customContent"] = copy + BIO_CTA
            changed = True
        elif name == "youtube":
            p["customContent"] = copy + YOUTUBE_CTA
            changed = True

        updated.append(p)
    return updated, changed


def update_post(post: dict, platforms: list) -> bool:
    """PATCH with full body — minimal payloads silently fail (200 but no change)."""
    body = {
        "content": post.get("content", ""),
        "mediaItems": post.get("mediaItems", []),
        "scheduledFor": post.get("scheduledFor"),
        "timezone": post.get("timezone", "America/New_York"),
        "isDraft": False,
        "platforms": platforms,
    }
    r = requests.put(f"{BASE}/posts/{post['_id']}", headers=HEADERS, json=body, timeout=20)
    if r.status_code not in (200, 201):
        print(f"    -> {r.status_code}: {r.text[:150]}")
    return r.status_code in (200, 201)


def verify() -> None:
    posts = fetch_future_posts()
    full, partial, missing = 0, 0, 0
    for post in posts:
        plats = post.get("platforms", [])
        with_cta = sum(1 for p in plats if MARKER in (p.get("customContent") or ""))
        li = next((p for p in plats if p.get("platform") == "linkedin"), None)
        has_fc = bool(li and (li.get("platformSpecificData") or {}).get("firstComment"))
        if with_cta == len(plats) and has_fc:
            full += 1
        elif with_cta > 0:
            partial += 1
            print(f"  PARTIAL {post['scheduledFor'][:16]} {post['_id'][:8]} ({with_cta}/{len(plats)} plats, firstComment={has_fc})")
        else:
            missing += 1
            print(f"  MISSING {post['scheduledFor'][:16]} {post['_id'][:8]}")
    print(f"\nVerify: {len(posts)} future posts — {full} full CTA coverage, {partial} partial, {missing} missing")


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    test_one = "--test" in sys.argv
    if "--verify" in sys.argv:
        verify()
        return

    posts = fetch_future_posts()
    print(f"Future posts: {len(posts)}")
    if test_one:
        posts = posts[-1:]  # farthest-out post = lowest risk
        print(f"TEST MODE: only updating post scheduled {posts[0]['scheduledFor']}")

    ok, skipped, failed = 0, 0, 0
    for i, post in enumerate(posts):
        platforms, changed = build_updated_platforms(post, i)
        when = post.get("scheduledFor", "")[:16]
        if not changed:
            skipped += 1
            continue
        if dry_run:
            print(f"  WOULD UPDATE {when} {post['_id'][:8]} ({len(platforms)} platforms)")
            ok += 1
            continue
        if update_post(post, platforms):
            ok += 1
            print(f"  updated {when} {post['_id'][:8]}")
        else:
            failed += 1
            print(f"  FAILED  {when} {post['_id'][:8]}")
        time.sleep(1.0)

    print(f"\nDone: {ok} updated, {skipped} skipped (already had CTA), {failed} failed")
    if not dry_run:
        print("Run with --verify to confirm changes stuck.")


if __name__ == "__main__":
    main()
