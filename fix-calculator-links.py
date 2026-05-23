#!/usr/bin/env python3
"""
Fix calculator link in all scheduled Zernio posts
Crosswalk Wisdom IMG Content Pipeline

Task: Update all scheduled posts on Zernio with the corrected calculator link
- Find posts containing calculator links
- Update them to use: www.crosswalkwisdom.com/img/calculator
- Verify all links are working
"""

import os
import json
import requests
import time
from datetime import datetime, timezone
from typing import Optional

# ── Configuration ──────────────────────────────────────────────────────────────
ZERNIO_KEY = os.getenv("ZERNIO_KEY")
ZERNIO_BASE = "https://zernio.com/api/v1"
ZERNIO_HDR = {
    "Authorization": f"Bearer {ZERNIO_KEY}",
    "Content-Type": "application/json"
}

# Link variants to search for and replace
OLD_LINKS = [
    "www.crosswalkwisdom.com/img/calculator",  # With https
    "http://www.crosswalkwisdom.com/img/calculator",   # With http
    "www.crosswalkwisdom.com/img/calculator",          # Without protocol
]
CORRECT_LINK = "www.crosswalkwisdom.com/img/calculator"

# ── Utility Functions ──────────────────────────────────────────────────────────

def test_link(url: str) -> dict:
    """Test if a link is working"""
    # Ensure URL has protocol
    test_url = url if url.startswith("http") else f"https://{url}"
    try:
        r = requests.head(test_url, timeout=5, allow_redirects=True)
        return {
            "url": url,
            "status": r.status_code,
            "working": r.status_code < 400,
            "redirects": len(r.history) > 0,
            "final_url": r.url
        }
    except Exception as e:
        return {
            "url": url,
            "status": None,
            "working": False,
            "error": str(e)
        }

def contains_calculator_link(content: str) -> bool:
    """Check if content contains any calculator link variant"""
    return any(link in content for link in OLD_LINKS)

def get_scheduled_posts(limit: int = 100, offset: int = 0) -> Optional[list]:
    """Fetch scheduled posts from Zernio"""
    try:
        url = f"{ZERNIO_BASE}/posts?limit={limit}&offset={offset}&status=scheduled"
        r = requests.get(url, headers=ZERNIO_HDR, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("posts", [])
    except Exception as e:
        print(f"❌ Error fetching posts: {e}")
        return None

def update_post(post_id: str, content: str, platforms_data: list) -> bool:
    """Update a post in Zernio"""
    try:
        body = {
            "content": content,
            "platforms": platforms_data,
        }
        url = f"{ZERNIO_BASE}/posts/{post_id}"
        r = requests.patch(url, headers=ZERNIO_HDR, json=body, timeout=10)
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"  ⚠️  Error updating post {post_id}: {e}")
        return False

def extract_links(text: str) -> list:
    """Extract all URLs from text"""
    import re
    url_pattern = r'https?://[^\s\]>]+|www\.[^\s\]>]+'
    return re.findall(url_pattern, text)

# ── Main Workflow ──────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("🔧 Crosswalk Wisdom — Fix Calculator Links on Zernio")
    print("=" * 70)

    if not ZERNIO_KEY:
        print("❌ Error: ZERNIO_KEY environment variable not set")
        return

    print(f"\n📋 Fetching scheduled posts from Zernio...")
    posts = get_scheduled_posts()

    if not posts:
        print("⚠️  No scheduled posts found or error fetching posts")
        return

    print(f"✅ Found {len(posts)} scheduled posts\n")

    posts_with_calc = []
    posts_to_update = []
    all_links = set()

    # Step 1: Find posts with calculator links
    print("Step 1: Scanning for calculator links...")
    print("-" * 70)

    for i, post in enumerate(posts, 1):
        post_id = post.get("_id", "unknown")
        content = post.get("content", "")
        platforms = post.get("platforms", [])
        scheduled_for = post.get("scheduledFor", "")

        # Check main content
        has_calc_main = contains_calculator_link(content)

        # Check platform-specific content and first comments
        has_calc_platform = False
        updated_platforms = []

        for plat in platforms:
            plat_copy = plat.copy()
            plat_name = plat.get("platform", "unknown")
            custom_content = plat.get("customContent", "")
            first_comment = plat.get("platformSpecificData", {}).get("firstComment", "")

            has_calc = contains_calculator_link(custom_content) or contains_calculator_link(first_comment)

            if has_calc:
                has_calc_platform = True
                print(f"  [{i}] Post {post_id[:8]}... ({plat_name})")
                print(f"      Scheduled: {scheduled_for}")

                # Update content
                new_custom = custom_content
                for old_link in OLD_LINKS:
                    if old_link in new_custom:
                        new_custom = new_custom.replace(old_link, CORRECT_LINK)

                new_first_comment = first_comment
                for old_link in OLD_LINKS:
                    if old_link in new_first_comment:
                        new_first_comment = new_first_comment.replace(old_link, CORRECT_LINK)

                if new_custom != custom_content or new_first_comment != first_comment:
                    plat_copy["customContent"] = new_custom
                    if "platformSpecificData" not in plat_copy:
                        plat_copy["platformSpecificData"] = {}
                    plat_copy["platformSpecificData"]["firstComment"] = new_first_comment

                    posts_to_update.append({
                        "post_id": post_id,
                        "platform": plat_name,
                        "scheduled_for": scheduled_for,
                        "content": new_custom,
                        "platforms": updated_platforms + [plat_copy] + platforms[platforms.index(plat)+1:]
                    })

            updated_platforms.append(plat_copy)

        if has_calc_main or has_calc_platform:
            posts_with_calc.append(post_id)

        # Extract all links for verification
        all_links.update(extract_links(content))
        for plat in platforms:
            all_links.update(extract_links(plat.get("customContent", "")))
            all_links.update(extract_links(plat.get("platformSpecificData", {}).get("firstComment", "")))

    if posts_with_calc:
        print(f"\n✅ Found {len(posts_with_calc)} posts with calculator links")
    else:
        print(f"\n✅ No posts with calculator links found")

    # Step 2: Update posts
    if posts_to_update:
        print(f"\nStep 2: Updating {len(posts_to_update)} post(s)...")
        print("-" * 70)

        for update in posts_to_update:
            post_id = update["post_id"]
            platform = update["platform"]
            print(f"  Updating {post_id[:8]}... ({platform})")

            success = update_post(post_id, update["content"], update["platforms"])
            if success:
                print(f"    ✅ Updated successfully")
            else:
                print(f"    ❌ Failed to update")

    # Step 3: Test all links
    print(f"\nStep 3: Testing {len(all_links)} unique links...")
    print("-" * 70)

    link_results = []
    for link in sorted(all_links):
        result = test_link(link)
        link_results.append(result)

        status_icon = "✅" if result["working"] else "❌"
        status_code = f"[{result.get('status', 'ERROR')}]"
        print(f"  {status_icon} {status_code} {link}")

        if result.get("redirects"):
            print(f"      └→ Redirects to: {result.get('final_url', 'unknown')}")
        if not result["working"] and result.get("error"):
            print(f"      └→ Error: {result['error']}")

    # Summary
    print("\n" + "=" * 70)
    print("📊 Summary")
    print("=" * 70)
    working_links = sum(1 for r in link_results if r["working"])
    failing_links = sum(1 for r in link_results if not r["working"])

    print(f"  Posts scanned: {len(posts)}")
    print(f"  Posts with calculator links: {len(posts_with_calc)}")
    print(f"  Posts updated: {len([u for u in posts_to_update if 'post_id' in u])}")
    print(f"  Unique links tested: {len(link_results)}")
    print(f"  Links working: {working_links} ✅")
    print(f"  Links failing: {failing_links} ❌")

    if failing_links > 0:
        print(f"\n⚠️  {failing_links} link(s) need attention:")
        for result in link_results:
            if not result["working"]:
                print(f"    - {result['url']}")
    else:
        print(f"\n✅ All links are working!")

if __name__ == "__main__":
    main()
