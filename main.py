"""
TubeonAI Content Pipeline
=========================
Repurposes a YouTube video into social media content for:
  - LinkedIn
  - Instagram Carousel
  - Instagram Reels
  - Facebook
  - TikTok
  - YouTube Shorts

Usage:
  python main.py <youtube_url>
  python main.py <tubeonai_summary_url_or_id>
  python main.py <youtube_url> --add-subscriber email@example.com
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

from tubeonai_client import TubeonAIClient
from encharge_client import EnchargeClient
from prompts import PLATFORMS

load_dotenv()

PROMPT_IDS_FILE = Path("prompt_ids.json")
TUBEONAI_SUMMARY_RE = re.compile(r"tubeonai\.com/summaries/([0-9a-f-]{36})", re.I)


def extract_summary_id(value: str):
    """Return a TubeonAI summary ID if value is a TubeonAI URL, else None."""
    m = TUBEONAI_SUMMARY_RE.search(value)
    return m.group(1) if m else None


def get_or_create_prompt_ids(client: TubeonAIClient) -> dict:
    """
    Load saved prompt IDs from disk, or create them in TubeonAI if missing.
    This runs once — IDs are reused on every subsequent video.
    """
    if PROMPT_IDS_FILE.exists():
        with open(PROMPT_IDS_FILE) as f:
            ids = json.load(f)
        # Verify all platforms are covered
        if all(k in ids for k in PLATFORMS):
            return ids

    print("\n[setup] Creating saved prompts in TubeonAI (one-time setup)...")

    # Fetch existing prompts to avoid duplicates
    existing = {p["title"]: p["id"] for p in client.list_prompts()}
    ids = {}

    for key, platform in PLATFORMS.items():
        title = f"[auto] {platform['label']}"
        if title in existing:
            ids[key] = existing[title]
            print(f"  ✓ Reusing: {title}")
        else:
            ids[key] = client.create_prompt(title, platform["prompt"])
            print(f"  + Created: {title}")

    with open(PROMPT_IDS_FILE, "w") as f:
        json.dump(ids, f, indent=2)

    print(f"  Prompt IDs saved to {PROMPT_IDS_FILE}\n")
    return ids


def save_output(title: str, results: dict) -> Path:
    """Save all generated content to a text file."""
    safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in title).strip()
    out_file = Path(f"{safe_title[:50]}.txt")

    with open(out_file, "w") as f:
        f.write(f"# {title}\n\n")
        for platform, content in results.items():
            label = PLATFORMS[platform]["label"]
            f.write(f"{'=' * 60}\n")
            f.write(f"## {label}\n")
            f.write(f"{'=' * 60}\n\n")
            f.write(content.strip())
            f.write("\n\n")

    return out_file


def run(url: str, subscriber_email: str = None):
    tubeonai_key = os.getenv("TUBEONAI_API_KEY")
    encharge_key = os.getenv("ENCHARGE_API_KEY")

    if not tubeonai_key:
        sys.exit("Error: TUBEONAI_API_KEY not set in .env")

    client = TubeonAIClient(tubeonai_key)
    prompt_ids = get_or_create_prompt_ids(client)

    # Step 1: Resolve summary
    existing_id = extract_summary_id(url)
    if existing_id:
        print(f"\n[1/3] Using existing TubeonAI summary: {existing_id}")
        summary = client.get_summary(existing_id)
        summary_id = existing_id
    else:
        print(f"\n[1/3] Summarising: {url}")
        response = client.create_summary(url)

        # Handle cached (200) vs accepted (202)
        if response.get("data", {}).get("status") == "ready":
            summary_id = response["data"]["id"]
            summary = response
        else:
            summary_id = response["data"]["id"]
            summary = client.wait_for_summary(summary_id)

    title = summary["data"].get("title", "Untitled")
    print(f"  Done: {title}")

    # Step 2: Repurpose into all platforms
    print(f"\n[2/3] Repurposing into {len(PLATFORMS)} platforms...")
    results = {}

    for key, platform in PLATFORMS.items():
        print(f"\n  → {platform['label']}")
        repurpose_resp = client.create_repurpose(
            summary_id=summary_id,
            prompt_id=prompt_ids[key],
            fmt=platform["format"],
        )

        data = repurpose_resp.get("data", {})

        # Cached result comes back immediately with content
        if data.get("status") == "completed" and data.get("content"):
            results[key] = data["content"]
        else:
            # Use the check_status link provided by the API
            check_status_url = repurpose_resp.get("_links", {}).get("check_status")
            if not check_status_url:
                raise RuntimeError(f"No check_status URL in repurpose response: {repurpose_resp}")
            results[key] = client.wait_for_repurpose(check_status_url)

    # Step 3: Save output
    print(f"\n[3/3] Saving content...")
    out_file = save_output(title, results)
    print(f"  Saved to: {out_file}")

    # Optional: add subscriber to Encharge
    if subscriber_email and encharge_key:
        print(f"\n  Adding {subscriber_email} to Encharge...")
        encharge = EnchargeClient(encharge_key)
        encharge.add_subscriber(
            email=subscriber_email,
            tags=["social-content", "youtube-repurpose"],
        )
        print("  Done.")

    # Print summary to terminal
    print(f"\n{'=' * 60}")
    print(f"Content ready for: {title}")
    print(f"{'=' * 60}")
    for key in results:
        print(f"  ✓ {PLATFORMS[key]['label']}")
    print(f"\nFull content saved to: {out_file}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Repurpose YouTube content for social media")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "--add-subscriber",
        metavar="EMAIL",
        help="Add this email to your Encharge list",
    )
    args = parser.parse_args()

    run(args.url, subscriber_email=args.add_subscriber)

