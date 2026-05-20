"""
Batch Content Repurposer
========================
Add YouTube URLs to the URLS list below, then run:

    python batch_repurpose.py

Each video is summarised and repurposed into all 7 platforms.
Output is saved to output/YYYY-MM-DD/<safe-title>.txt — one file per video.
Failed videos are skipped and reported at the end.
"""

import os
import re
import json
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

from tubeonai_client import TubeonAIClient
from prompts import PLATFORMS

load_dotenv()

# ── Add your URLs here ─────────────────────────────────────────────────────────
# Retry: 4 connection failures from previous batch run
URLS = [
    "https://tubeonai.com/summaries/019c5bab-839b-72a1-b375-0f77ec482a32",  # 10 signs you might be BURNT OUT
    "https://tubeonai.com/summaries/a04ade38-6088-4ef1-8c57-08aca31700ea",  # Erasing Fears & Traumas | Huberman Lab
    "https://tubeonai.com/summaries/019c6428-2062-7236-b88c-468588e58b11",  # We Not The Same - Fearless Motivation
    "https://tubeonai.com/summaries/019c5227-2a90-7073-b968-a834a762b984",  # Learn French - The Mistaken Identity Story
]
# ──────────────────────────────────────────────────────────────────────────────

PROMPT_IDS_FILE = Path("prompt_ids.json")
TUBEONAI_SUMMARY_RE = re.compile(r"tubeonai\.com/summaries/([0-9a-f-]{36})", re.I)
OUTPUT_DIR = Path("output") / date.today().isoformat()


def get_or_create_prompt_ids(client: TubeonAIClient) -> dict:
    if PROMPT_IDS_FILE.exists():
        with open(PROMPT_IDS_FILE) as f:
            ids = json.load(f)
        if all(k in ids for k in PLATFORMS):
            return ids

    print("[setup] Creating saved prompts in TubeonAI (one-time)...")
    existing = {p["title"]: p["id"] for p in client.list_prompts()}
    ids = {}
    for key, platform in PLATFORMS.items():
        title = f"[auto] {platform['label']}"
        if title in existing:
            ids[key] = existing[title]
        else:
            ids[key] = client.create_prompt(title, platform["prompt"])
            print(f"  + Created: {title}")

    with open(PROMPT_IDS_FILE, "w") as f:
        json.dump(ids, f, indent=2)
    return ids


def safe_filename(title: str) -> str:
    return "".join(c if c.isalnum() or c in " -_" else "" for c in title).strip()[:60]


def save_output(title: str, results: dict) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / f"{safe_filename(title)}.txt"

    with open(out_file, "w") as f:
        f.write(f"# {title}\n\n")
        for platform, content in results.items():
            label = PLATFORMS[platform]["label"]
            f.write(f"{'=' * 60}\n## {label}\n{'=' * 60}\n\n")
            f.write(content.strip())
            f.write("\n\n")

    return out_file


def process(url: str, client: TubeonAIClient, prompt_ids: dict):
    """Summarise and repurpose one URL. Returns (title, output_path)."""
    m = TUBEONAI_SUMMARY_RE.search(url)
    if m:
        summary_id = m.group(1)
        summary = client.get_summary(summary_id)
    else:
        resp = client.create_summary(url)
        summary_id = resp["data"]["id"]
        if resp["data"].get("status") not in ("ready", "completed"):
            summary = client.wait_for_summary(summary_id)
        else:
            summary = resp

    title = summary["data"].get("title", "Untitled")

    results = {}
    for key, platform in PLATFORMS.items():
        repurpose_resp = client.create_repurpose(
            summary_id=summary_id,
            prompt_id=prompt_ids[key],
            fmt=platform["format"],
        )
        data = repurpose_resp.get("data", {})
        if data.get("status") == "completed" and data.get("content"):
            results[key] = data["content"]
        else:
            check_url = repurpose_resp.get("_links", {}).get("check_status")
            if not check_url:
                raise RuntimeError(f"No check_status URL: {repurpose_resp}")
            results[key] = client.wait_for_repurpose(check_url)

    out_file = save_output(title, results)
    return title, out_file


def main():
    api_key = os.getenv("TUBEONAI_API_KEY")
    if not api_key:
        raise SystemExit("Error: TUBEONAI_API_KEY not set in .env")

    client = TubeonAIClient(api_key)
    prompt_ids = get_or_create_prompt_ids(client)

    total = len(URLS)
    done, failed = [], []

    print(f"\nBatch repurpose: {total} video{'s' if total != 1 else ''}\n")

    for i, url in enumerate(URLS, 1):
        print(f"[{i}/{total}] {url}")
        try:
            title, out_file = process(url, client, prompt_ids)
            done.append((title, out_file))
            print(f"  ✓ Saved: {out_file}\n")
        except Exception as e:
            failed.append((url, str(e)))
            print(f"  ✗ Failed: {e}\n")

    print("=" * 60)
    print(f"Done: {len(done)} succeeded, {len(failed)} failed")
    print(f"Output folder: {OUTPUT_DIR.resolve()}")
    if failed:
        print("\nFailed URLs:")
        for url, err in failed:
            print(f"  {url}\n    {err}")


if __name__ == "__main__":
    main()
