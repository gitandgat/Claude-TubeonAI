#!/usr/bin/env python3
"""
Daily Health Bot
================
Runs at 7am ET each morning. For 5 fresh health/wellness YouTube videos:
  1. Summarises via TubeonAI
  2. Repurposes to LinkedIn copy
  3. Generates image via GPT-image-2
  4. Schedules to Zernio (LinkedIn primary + IG / FB / TikTok)

Cron: 0 11 * * * cd "/Users/toto/Claude TubeonAI" && python3 daily_health_bot.py >> logs/health_bot.log 2>&1
(11:00 UTC = 7:00 EDT)
"""
import json, os, sys, time, datetime, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import anthropic
from tubeonai_client import TubeonAIClient
from health_video_finder import get_fresh_videos
from image_gen_client import generate_health_image

_haiku = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── Zernio ────────────────────────────────────────────────────────────────────
ZERNIO_BASE = "https://zernio.com/api/v1"
ZERNIO_KEY  = os.getenv("ZERNIO_API_KEY")
Z_HEADERS   = {"Authorization": f"Bearer {ZERNIO_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"

# ── Daily post times (ET) ─────────────────────────────────────────────────────
TIMES_ET = ["08:00", "11:00", "14:00", "17:00", "20:00"]

PROMPT_IDS_FILE = Path("prompt_ids.json")
LOG_DIR = Path("logs")


# ── Helpers ───────────────────────────────────────────────────────────────────

def et_to_utc(time_str: str, date: datetime.date) -> str:
    """Convert HH:MM ET to UTC ISO string. EDT (UTC-4) May–Oct, EST (UTC-5) otherwise."""
    hour, minute = map(int, time_str.split(":"))
    offset = 4 if 4 <= date.month <= 10 else 5
    local = datetime.datetime(date.year, date.month, date.day, hour, minute)
    utc = local + datetime.timedelta(hours=offset)
    return utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def write_post_from_summary(summary: str) -> str:
    """Claude Haiku turns a TubeonAI summary into a hook-led LinkedIn post."""
    msg = _haiku.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": (
                "Write a LinkedIn post from these health insights.\n\n"
                f"INSIGHTS:\n{summary[:2500]}\n\n"
                "RULES:\n"
                "- Line 1: one bold hook — a claim, stat, or provocation. Never start with Here, Here's, Key, In this, Summary.\n"
                "- 2-3 short paragraphs, first-person voice, no bullet lists.\n"
                "- Closing line or question, then 3-5 hashtags.\n"
                "- Under 1300 characters. Never mention the video or source."
            ),
        }],
    )
    return msg.content[0].text.strip()


def adapt_copy(linkedin_copy: str, platform: str) -> str:
    """Shorten LinkedIn copy for other platforms."""
    if platform == "instagram":
        short = linkedin_copy[:900].rsplit("\n", 1)[0]
        return short + "\n\n#HealthWellness #Mindset #MentalHealth #Fitness #Wellness #HealthTips #SelfCare"
    if platform == "facebook":
        return linkedin_copy
    if platform == "tiktok":
        paras = [p for p in linkedin_copy.split("\n\n") if p.strip()]
        short = "\n\n".join(paras[:2])[:500]
        return short + "\n\n#health #wellness #fitness #mentalhealth #selfcare #healthtips"
    return linkedin_copy


def upload_image(filepath: str) -> str:
    """Upload image to Zernio, return public CDN URL."""
    filename  = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)
    data = requests.post(
        f"{ZERNIO_BASE}/media/presign",
        headers=Z_HEADERS,
        json={"filename": filename, "contentType": "image/png", "size": file_size},
    ).json()
    upload_url = data.get("uploadUrl") or data.get("data", {}).get("uploadUrl")
    public_url = data.get("publicUrl")  or data.get("data", {}).get("publicUrl")
    with open(filepath, "rb") as f:
        requests.put(upload_url, data=f, headers={"Content-Type": "image/png"}).raise_for_status()
    return public_url


def schedule_post(linkedin_copy: str, media_url: str, scheduled_at: str) -> bool:
    """Schedule image post to 4 platforms. Returns True on success."""
    payload = {
        "content": linkedin_copy,
        "scheduledFor": scheduled_at,
        "timezone": "America/New_York",
        "mediaItems": [{"url": media_url, "type": "image"}],
        "platforms": [
            {
                "platform": "linkedin",
                "accountId": LINKEDIN_ID,
                "customContent": linkedin_copy,
                "scheduledFor": scheduled_at,
            },
            {
                "platform": "instagram",
                "accountId": INSTAGRAM_ID,
                "customContent": adapt_copy(linkedin_copy, "instagram"),
                "scheduledFor": scheduled_at,
            },
            {
                "platform": "facebook",
                "accountId": FACEBOOK_ID,
                "customContent": adapt_copy(linkedin_copy, "facebook"),
                "scheduledFor": scheduled_at,
            },
            {
                "platform": "tiktok",
                "accountId": TIKTOK_ID,
                "customContent": adapt_copy(linkedin_copy, "tiktok"),
                "scheduledFor": scheduled_at,
            },
        ],
    }
    resp = requests.post(f"{ZERNIO_BASE}/posts", headers=Z_HEADERS, json=payload)
    if resp.status_code not in (200, 201):
        print(f"  ! Zernio error {resp.status_code}: {resp.text[:300]}")
        return False
    return True


def process_video(client: TubeonAIClient, video: dict, slot_time: str,
                  today: datetime.date) -> dict:
    """Run the full pipeline for one video. Returns a result dict."""
    result = {"title": video["title"], "slot": slot_time, "success": False, "error": None}

    try:
        # 1. TubeonAI: summarise the video
        print(f"  [1/4] TubeonAI summary...")
        resp = client.create_summary(video["url"])
        data = resp.get("data", {})
        if data.get("status") in ("ready", "completed"):
            summary_id = data["id"]
        else:
            summary_id = data["id"]
            client.wait_for_summary(summary_id)
        summary_text = client.get_summary(summary_id)["data"].get("summary", "")

        # 2. Claude Haiku: write the LinkedIn post from the summary
        print(f"  [2/4] Writing post (Haiku)...")
        linkedin_copy = write_post_from_summary(summary_text)
        print(f"  ✓ Hook: {linkedin_copy.splitlines()[0][:80]}")

        # 3. Generate image
        print(f"  [3/4] Generating image (GPT-image-2)...")
        img_path = generate_health_image(video["title"])
        print(f"  ✓ Image saved: {img_path}")

        # 4. Upload + schedule
        print(f"  [4/4] Uploading & scheduling for {slot_time} ET...")
        media_url    = upload_image(img_path)
        scheduled_at = et_to_utc(slot_time, today)
        ok = schedule_post(linkedin_copy, media_url, scheduled_at)

        os.remove(img_path)

        if ok:
            print(f"  ✓ Scheduled → {scheduled_at} UTC")
            result["success"] = True
        else:
            result["error"] = "Zernio scheduling failed"

    except Exception as e:
        result["error"] = str(e)
        print(f"  ✗ Error: {e}")

    return result


def run():
    LOG_DIR.mkdir(exist_ok=True)
    today = datetime.date.today()

    print(f"\n{'='*60}")
    print(f"Daily Health Bot  —  {today}")
    print(f"{'='*60}")

    if not ZERNIO_KEY:
        sys.exit("Error: ZERNIO_API_KEY not set")
    if not os.getenv("TUBEONAI_API_KEY"):
        sys.exit("Error: TUBEONAI_API_KEY not set")
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("Error: OPENAI_API_KEY not set")

    client = TubeonAIClient(os.getenv("TUBEONAI_API_KEY"))

    print(f"\nSearching for 5 health/wellness videos...")
    videos = get_fresh_videos(5)

    if not videos:
        sys.exit("No new videos found. seen_videos.json may need to be cleared.")

    print(f"Found {len(videos)} video(s). Starting pipeline...\n")

    log = {"date": str(today), "results": []}

    for i, video in enumerate(videos[:5]):
        slot = TIMES_ET[i]
        print(f"\n[Post {i+1}/5]  →  {slot} ET")
        print(f"  {video['title'][:70]}")
        print(f"  {video['url']}")

        result = process_video(client, video, slot, today)
        log["results"].append(result)

        if i < len(videos) - 1:
            time.sleep(5)  # avoid hammering TubeonAI

    # Save log
    log_file = LOG_DIR / f"health_bot_{today}.json"
    log_file.write_text(json.dumps(log, indent=2))

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for r in log["results"]:
        icon = "✓" if r["success"] else "✗"
        print(f"  {icon}  [{r['slot']} ET]  {r['title'][:55]}")
        if r.get("error"):
            print(f"       ↳ {r['error']}")
    print(f"\nLog: {log_file}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run()
