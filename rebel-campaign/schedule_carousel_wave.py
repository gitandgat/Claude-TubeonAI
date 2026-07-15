"""
Schedule rebel carousel wave: TikTok + Instagram, July 13–21, 11am ET.
Each reel = 6 PNG slides uploaded as a carousel post.

Carousels are the top-performing format for this account on TikTok
(550–670 views vs 100–200 for video). Same approved copy, new format.

Usage:
  PYTHONPATH="/Users/toto/Claude TubeonAI" python3 rebel-campaign/schedule_carousel_wave.py <reel_key>
  PYTHONPATH="/Users/toto/Claude TubeonAI" python3 rebel-campaign/schedule_carousel_wave.py all
"""
import os
import sys
import requests

from zernio_key import ZERNIO_API_KEY as API_KEY

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

INSTAGRAM_ID = "690940655f6fbb9ef8323072"
TIKTOK_ID = "690941425f6fbb9ef8323078"
TIMEZONE = "America/New_York"
CALCULATOR_LINK = "www.crosswalkwisdom.com/img/calculator"
FIRST_COMMENT = f"If you're ready to actually run the math on staying vs. pivoting → {CALCULATOR_LINK}"

CAROUSEL_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carousels")

SCHEDULE = {
    "reel1": {"scheduled_for": "2026-07-13T15:00:00.000Z",
               "caption_tt": "Whose dream was it, really? 🩺 #doctorburnout #careerchange #crosswalkwisdom",
               "caption_ig": "Whose dream was it, really?\n\nNobody tells you this part: the career that made your family proud was never actually about you.\n\nStatus. Access. Never paying for a consultation again.\n\nNow that you're safe — what do YOU want?\n\n#doctorburnout #physicianburnout #careerchange #immigrantfamily #crosswalkwisdom"},
    "reel2": {"scheduled_for": "2026-07-15T15:00:00.000Z",
               "caption_tt": "35. Licensed. Not free. 🩺 #doctorburnout #careerchange #crosswalkwisdom",
               "caption_ig": "You're 35. You're licensed. You're not free.\n\nWalk the timeline: high school → MCAT → med school → residency → licensed.\n\nNotice what's missing from every step? You.\n\nStability ≠ flourishing. Nobody told you there was a difference.\n\n#doctorburnout #physicianburnout #careerchange #crosswalkwisdom"},
    "reel3": {"scheduled_for": "2026-07-17T15:00:00.000Z",
               "caption_tt": "1985. The year your code was written. 🩺 #doctorburnout #crosswalkwisdom",
               "caption_ig": "You're running 1985 survival logic on a 2026 problem.\n\nSafety. Status. Belonging. The code worked — you became a doctor.\n\nBut it was written for their threat environment. Not yours.\n\nWrong era. Right person.\n\n#doctorburnout #physicianburnout #careerchange #crosswalkwisdom"},
    "reel4": {"scheduled_for": "2026-07-19T15:00:00.000Z",
               "caption_tt": "Options, not obligations. 🩺 #immigrantfamily #careerchange #crosswalkwisdom",
               "caption_ig": "Your parents' sacrifice was supposed to buy you freedom.\n\nSomewhere along the way it became the reason you can't leave.\n\nLeaving isn't betraying the sacrifice. Leaving IS the mission completing.\n\n#immigrantfamily #doctorburnout #careerchange #crosswalkwisdom"},
    "reel5": {"scheduled_for": "2026-07-21T15:00:00.000Z",
               "caption_tt": "Wrong question vs right question. 🩺 #doctorburnout #crosswalkwisdom",
               "caption_ig": "Most doctors ask: can I leave medicine? Wrong question.\n\nThe right one: what am I actually built for?\n\nPrecision. Complexity. High stakes — the system said those only count in a hospital. The system was wrong.\n\n#doctorburnout #physicianburnout #careerchange #physiciantransition #crosswalkwisdom"},
}


def upload_image(filepath: str) -> str:
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    r = requests.post(
        f"{BASE}/media/presign",
        headers=HEADERS,
        json={"filename": filename, "contentType": "image/png", "fileSize": filesize},
    )
    r.raise_for_status()
    data = r.json()
    with open(filepath, "rb") as f:
        put_r = requests.put(data["uploadUrl"], data=f, headers={"Content-Type": "image/png"})
        put_r.raise_for_status()
    return data["publicUrl"]


def upload_slides(reel_key: str, fmt: str) -> list[dict]:
    slide_dir = os.path.join(CAROUSEL_BASE, reel_key, fmt)
    slides = sorted([
        os.path.join(slide_dir, f)
        for f in os.listdir(slide_dir)
        if f.endswith(".png")
    ])
    items = []
    for path in slides:
        url = upload_image(path)
        items.append({"url": url, "type": "image"})
        print(f"  [{fmt}] uploaded: {os.path.basename(path)}")
    return items


def schedule_carousel(reel_key: str) -> None:
    entry = SCHEDULE[reel_key]
    scheduled_for = entry["scheduled_for"]

    print(f"[{reel_key}] Uploading TikTok slides (9:16)...")
    tt_items = upload_slides(reel_key, "tiktok")

    print(f"[{reel_key}] Uploading Instagram slides (4:5)...")
    ig_items = upload_slides(reel_key, "instagram")

    # TikTok post (9:16 slides)
    tt_body = {
        "content": entry["caption_tt"],
        "mediaItems": tt_items,
        "platforms": [
            {
                "platform": "tiktok",
                "accountId": TIKTOK_ID,
                "customContent": entry["caption_tt"],
                "scheduledFor": scheduled_for,
            }
        ],
        "scheduledFor": scheduled_for,
        "timezone": TIMEZONE,
        "isDraft": False,
    }
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=tt_body)
    print(f"[{reel_key}] TikTok POST {r.status_code} — {r.text[:200]}")

    # Instagram post (4:5 slides)
    ig_body = {
        "content": entry["caption_ig"],
        "mediaItems": ig_items,
        "platforms": [
            {
                "platform": "instagram",
                "accountId": INSTAGRAM_ID,
                "customContent": entry["caption_ig"],
                "scheduledFor": scheduled_for,
                "platformSpecificData": {"firstComment": FIRST_COMMENT},
            }
        ],
        "scheduledFor": scheduled_for,
        "timezone": TIMEZONE,
        "isDraft": False,
    }
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=ig_body)
    print(f"[{reel_key}] Instagram POST {r.status_code} — {r.text[:200]}\n")


if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "reel1"
    if key == "all":
        for k in SCHEDULE:
            schedule_carousel(k)
    else:
        schedule_carousel(key)
