#!/usr/bin/env python3
"""
Comprehensive Link Verification for Crosswalk Wisdom Zernio Posts
Task: Verify all links in scheduled posts are working

Crosswalk Wisdom IMG Content Pipeline
"""

import os
import json
import requests
import time
import re
from datetime import datetime, timezone
from typing import Optional, Dict, List, Set
from collections import defaultdict
from urllib.parse import urlparse

# ── Configuration ──────────────────────────────────────────────────────────────
ZERNIO_KEY = os.getenv("ZERNIO_API_KEY") or os.getenv("ZERNIO_KEY")
ZERNIO_BASE = "https://zernio.com/api/v1"
ZERNIO_HDR = {
    "Authorization": f"Bearer {ZERNIO_KEY}",
    "Content-Type": "application/json"
}

# Link verification settings
TIMEOUT = 8  # seconds
MAX_LINKS_PER_POST = 20
REDIRECT_LIMIT = 5

# ── Utility Functions ──────────────────────────────────────────────────────────

def extract_links(text: str) -> List[str]:
    """Extract all URLs from text"""
    if not text:
        return []

    # Match both http(s):// and www. links
    url_pattern = r'https?://[^\s\]>)"`]+|www\.[^\s\]>)"`]+'
    matches = re.findall(url_pattern, text)

    # Clean up and deduplicate
    links = []
    for match in matches:
        # Remove trailing punctuation that's not part of URL
        match = match.rstrip('.,;:!?\'")')
        if match and len(match) > 4:  # Basic validity check
            links.append(match)

    return list(set(links))

def test_link(url: str, timeout: int = TIMEOUT) -> Dict:
    """Test if a link is working with detailed diagnostics"""
    # Ensure URL has protocol
    test_url = url if url.startswith("http") else f"https://{url}"

    # Parse domain for grouping
    try:
        domain = urlparse(test_url).netloc
    except:
        domain = "unknown"

    result = {
        "url": url,
        "test_url": test_url,
        "domain": domain,
        "status": None,
        "working": False,
        "redirects": False,
        "final_url": None,
        "error": None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    try:
        response = requests.head(
            test_url,
            timeout=timeout,
            allow_redirects=True,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; LinkChecker)'}
        )

        result["status"] = response.status_code
        result["working"] = response.status_code < 400
        result["redirects"] = len(response.history) > 0
        result["final_url"] = response.url if response.url != test_url else None

        # Additional info for HTTP errors
        if response.status_code >= 400:
            result["error"] = f"HTTP {response.status_code}"

    except requests.Timeout:
        result["error"] = "Connection timeout"
    except requests.ConnectionError:
        result["error"] = "Connection error"
    except requests.TooManyRedirects:
        result["error"] = "Too many redirects"
    except Exception as e:
        result["error"] = str(e)

    return result

def get_scheduled_posts(limit: int = 500, offset: int = 0) -> Optional[List]:
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

def extract_post_links(post: Dict) -> Dict:
    """Extract all links from a single post"""
    links = {
        "main_content": [],
        "platform_content": defaultdict(list),
        "first_comments": defaultdict(list),
        "all_unique": set()
    }

    # Main content
    main_links = extract_links(post.get("content", ""))
    links["main_content"] = main_links
    links["all_unique"].update(main_links)

    # Platform-specific content
    for platform in post.get("platforms", []):
        platform_name = platform.get("platform", "unknown")

        # Custom content
        custom_content = platform.get("customContent", "")
        custom_links = extract_links(custom_content)
        links["platform_content"][platform_name].extend(custom_links)
        links["all_unique"].update(custom_links)

        # First comments
        platform_data = platform.get("platformSpecificData", {})
        first_comment = platform_data.get("firstComment", "")
        comment_links = extract_links(first_comment)
        links["first_comments"][platform_name].extend(comment_links)
        links["all_unique"].update(comment_links)

    return links

# ── Main Workflow ──────────────────────────────────────────────────────────────

def main():
    print("=" * 80)
    print("🔍 Crosswalk Wisdom — Comprehensive Link Verification")
    print("=" * 80)
    print(f"Started: {datetime.now(timezone.utc).isoformat()}\n")

    if not ZERNIO_KEY:
        print("❌ Error: ZERNIO_KEY environment variable not set")
        return

    # Step 1: Fetch posts
    print("📋 Step 1: Fetching scheduled posts from Zernio...")
    print("-" * 80)

    posts = get_scheduled_posts()
    if not posts:
        print("⚠️  No scheduled posts found or error fetching posts")
        return

    print(f"✅ Found {len(posts)} scheduled posts\n")

    # Step 2: Extract all links
    print("📍 Step 2: Extracting links from all posts...")
    print("-" * 80)

    all_links = {}  # url -> [post_ids that contain it]
    posts_with_links = 0
    total_link_mentions = 0

    for i, post in enumerate(posts, 1):
        post_id = post.get("_id", "unknown")
        title = post.get("content", "")[:50].replace("\n", " ")

        links_data = extract_post_links(post)
        unique_links = list(links_data["all_unique"])

        if unique_links:
            posts_with_links += 1
            total_link_mentions += len(unique_links)

            for link in unique_links:
                if link not in all_links:
                    all_links[link] = []
                all_links[link].append(post_id)

            print(f"  [{i:3d}] {post_id[:8]}... ({len(unique_links):2d} links)")

    print(f"\n✅ Processed {posts_with_links} posts with {total_link_mentions} total link mentions")
    print(f"✅ Found {len(all_links)} unique links\n")

    # Step 3: Test all links
    print("🧪 Step 3: Testing links...")
    print("-" * 80)

    link_results = []
    working_count = 0
    broken_count = 0

    for i, link in enumerate(sorted(all_links.keys()), 1):
        print(f"  [{i:3d}/{len(all_links)}] Testing: {link[:60]}", end="\r")
        result = test_link(link)
        link_results.append(result)

        if result["working"]:
            working_count += 1
        else:
            broken_count += 1

        # Be nice to servers - add small delay between requests
        time.sleep(0.2)

    print(" " * 100 + "\r", end="")  # Clear the line

    # Step 4: Generate Report
    print("\n" + "=" * 80)
    print("📊 LINK VERIFICATION REPORT")
    print("=" * 80)

    print(f"\n📈 Summary Statistics:")
    print(f"  • Total posts scanned: {len(posts)}")
    print(f"  • Posts with links: {posts_with_links}")
    print(f"  • Unique links tested: {len(link_results)}")
    print(f"  • Links working: {working_count} ✅")
    print(f"  • Links broken: {broken_count} ❌")
    print(f"  • Success rate: {(working_count / len(link_results) * 100):.1f}%" if link_results else "N/A")

    # Group results by domain
    by_domain = defaultdict(list)
    for result in link_results:
        by_domain[result["domain"]].append(result)

    print(f"\n🌐 Links by Domain:")
    for domain in sorted(by_domain.keys()):
        domain_results = by_domain[domain]
        domain_working = sum(1 for r in domain_results if r["working"])
        domain_total = len(domain_results)
        status = "✅" if domain_working == domain_total else "⚠️ "
        print(f"  {status} {domain:40s} {domain_working}/{domain_total}")

    # Detailed breakdown of broken links
    broken_links = [r for r in link_results if not r["working"]]
    if broken_links:
        print(f"\n❌ BROKEN LINKS ({len(broken_links)}):")
        print("-" * 80)

        for result in sorted(broken_links, key=lambda x: x["url"]):
            link = result["url"]
            error = result.get("error", "Unknown error")
            status = result.get("status", "N/A")
            post_ids = all_links.get(link, [])

            print(f"\n  📌 {link}")
            print(f"     └─ Status: {error} [{status}]")
            print(f"     └─ Found in {len(post_ids)} post(s):")

            for post_id in post_ids[:3]:  # Show first 3 posts
                for post in posts:
                    if post.get("_id") == post_id:
                        scheduled = post.get("scheduledFor", "N/A")
                        print(f"        • {post_id[:8]}... (scheduled: {scheduled})")
                        break

            if len(post_ids) > 3:
                print(f"        • ... and {len(post_ids) - 3} more")

    # Links with redirects
    redirect_links = [r for r in link_results if r["redirects"]]
    if redirect_links:
        print(f"\n🔄 Links with Redirects ({len(redirect_links)}):")
        print("-" * 80)

        for result in sorted(redirect_links, key=lambda x: x["url"])[:10]:  # Show first 10
            print(f"  📌 {result['url']}")
            print(f"     └─ Redirects to: {result.get('final_url', 'unknown')}")

    # Summary recommendations
    print(f"\n" + "=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80)

    if broken_count > 0:
        print(f"\n🚨 ACTION REQUIRED: {broken_count} broken link(s) found")
        print("\nBroken links by domain:")
        broken_by_domain = defaultdict(int)
        for result in broken_links:
            broken_by_domain[result["domain"]] += 1

        for domain, count in sorted(broken_by_domain.items(), key=lambda x: -x[1]):
            print(f"  • {domain}: {count} broken link(s)")

        print("\nNext steps:")
        print("  1. Review the broken links above")
        print("  2. Update the links in the affected posts")
        print("  3. Re-run this script to verify fixes")
    else:
        print(f"\n✅ All {len(all_links)} links are working correctly!")
        print("   No action needed.")

    # Save detailed report to file
    report_file = f"link-verification-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    report_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_posts": len(posts),
            "posts_with_links": posts_with_links,
            "unique_links": len(link_results),
            "working": working_count,
            "broken": broken_count,
            "success_rate": (working_count / len(link_results) * 100) if link_results else 0
        },
        "broken_links": [
            {
                "url": r["url"],
                "error": r.get("error"),
                "status": r.get("status"),
                "posts_affected": all_links.get(r["url"], [])
            }
            for r in broken_links
        ],
        "all_results": [
            {
                "url": r["url"],
                "working": r["working"],
                "status": r.get("status"),
                "domain": r.get("domain"),
                "error": r.get("error"),
                "final_url": r.get("final_url")
            }
            for r in link_results
        ]
    }

    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_file}")
    print(f"\n✅ Verification complete at {datetime.now(timezone.utc).isoformat()}\n")

if __name__ == "__main__":
    main()
