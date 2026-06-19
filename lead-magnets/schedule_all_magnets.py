#!/usr/bin/env python3
"""
Schedule one promo cross-post per lead magnet (mind, fitness, health, trainer)
to LinkedIn + Facebook + Instagram via Zernio, spread one per day so they don't
cannibalize. Card + magnet link in the first comment (LinkedIn + FB).

    python schedule_all_magnets.py --dry-run
    python schedule_all_magnets.py
"""

import argparse
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv("/Users/toto/Claude TubeonAI/.env")
KEY = os.getenv("ZERNIO_API_KEY")
if not KEY:
    sys.exit("ZERNIO_API_KEY not set")

BASE = "https://zernio.com/api/v1"
HDR = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
TZ = "America/New_York"
LINKEDIN_ID = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID = "6909409a5f6fbb9ef8323074"
HERE = Path(__file__).resolve().parent

MAGNETS = [
    {
        "key": "mind", "card": "lm-inner-voices-social.png", "when": "2026-06-21T08:00:00",
        "link": "https://www.crosswalkwisdom.com/inner-voices",
        "linkedin": """There are five voices in your head. At least one of them is lying to you to keep you safe.

The Realist who calls quitting "being responsible." The Loyalist who says leaving would betray everyone who helped you. The Impostor who's sure you'll be found out. The Perfectionist who won't let you start until it's flawless. The Martyr who's quietly proud of how much you endure.

They don't sound like fear. They sound like wisdom. That's why capable people stay stuck for years in a life they've already outgrown.

You don't silence these voices. You learn to recognize each one and answer it.

Which voice runs loudest in your head?""",
        "short": "Five inner voices keep capable people stuck in lives they've outgrown. They don't sound like fear, they sound like wisdom. Learn to recognize and answer each one. Free guide, link in bio.",
        "first_comment": "I wrote a free guide on the five inner voices and how to answer each one: https://www.crosswalkwisdom.com/inner-voices",
    },
    {
        "key": "fitness", "card": "lm-train-like-a-clinician-social.png", "when": "2026-06-22T08:00:00",
        "link": "https://www.crosswalkwisdom.com/train-like-a-clinician",
        "linkedin": """Most fitness advice is sold to you. Almost none of it is studied.

I spent years reading scans and watching how real tissue handles load. Then I started coaching people through strength training. The gap between what the industry sells and what the research shows is enormous.

A few things that actually hold up:
- Progressive overload beats novelty. Muscle adapts to more load over time, not to being confused.
- Recovery is where strength is built, not the session itself.
- Most "bad" exercises are good exercises loaded badly.
- Soreness is not the goal, and it's a poor measure of a good session.

Train from physiology, not bro-science.

What training rule have you started to doubt?""",
        "short": "Most fitness advice is sold, not studied. Here's what the research actually shows about strength, recovery, and avoiding injury, from someone with clinical training. Free guide, link in bio.",
        "first_comment": "I put the evidence-based approach into a free guide, Train Like a Clinician: https://www.crosswalkwisdom.com/train-like-a-clinician",
    },
    {
        "key": "health", "card": "lm-marginal-decade-social.png", "when": "2026-06-23T08:00:00",
        "link": "https://www.crosswalkwisdom.com/marginal-decade",
        "linkedin": """Your last healthy decade is being decided by what you do in this one.

As a doctor I watched the bill come due, over and over. People arrived in their 60s and 70s and paid for thirty years of small choices nobody flagged in time.

The choices that protect that decade are unglamorous and few:
- Strength. Muscle is the organ of aging, and you can build it at any age.
- Walking after meals does more for your metabolism than most supplements.
- Sleep is not optional maintenance. It's the repair shift.
- The screening conversation you keep postponing.

Prevention is the work the system was too rushed to do. You can do it now.

What's one habit you've been postponing?""",
        "short": "Your last healthy decade is decided by what you do now. The habits that protect it are few and unglamorous: strength, walking, sleep, screening. A prevention-first guide, link in bio.",
        "first_comment": "I put the prevention essentials into a free guide, The Marginal Decade: https://www.crosswalkwisdom.com/marginal-decade",
    },
    {
        "key": "trainer", "card": "lm-clinic-to-coaching-social.png", "when": "2026-06-24T08:00:00",
        "link": "https://www.crosswalkwisdom.com/clinic-to-coaching",
        "linkedin": """If you trained in healthcare and quietly want out, coaching is the most underrated door you're not looking at.

You already have the thing most coaches spend years trying to fake: clinical credibility. You can read a body, explain hard things simply, and people trust you with their health by default.

What you're missing isn't knowledge. It's the translation: how to turn that credibility into a practice clients pay for, without the burnout that made you want to leave in the first place.

It isn't a step down from medicine. For a lot of us it's the part of medicine we actually wanted.

If you've thought about coaching, what's stopping you?""",
        "short": "Trained in healthcare and want out? Coaching is the most underrated exit. You already have what most coaches fake: clinical credibility. The missing piece is translation. Free guide, link in bio.",
        "first_comment": "I wrote a free guide for healthcare people who want to coach, From Clinic to Coaching: https://www.crosswalkwisdom.com/clinic-to-coaching",
    },
]


def upload(card: Path) -> str:
    r = requests.post(f"{BASE}/media/presign", headers=HDR,
                      json={"filename": card.name, "contentType": "image/png", "fileSize": card.stat().st_size}, timeout=30)
    r.raise_for_status()
    d = r.json()
    with open(card, "rb") as f:
        requests.put(d["uploadUrl"], data=f, headers={"Content-Type": "image/png"}, timeout=60).raise_for_status()
    return d["publicUrl"]


def schedule(m: dict) -> str:
    card = HERE / m["card"]
    image_url = upload(card)
    body = {
        "content": m["linkedin"], "mediaItems": [{"url": image_url, "type": "image"}],
        "isDraft": False, "scheduledFor": m["when"], "timezone": TZ,
        "platforms": [
            {"platform": "linkedin", "accountId": LINKEDIN_ID, "customContent": m["linkedin"],
             "scheduledFor": m["when"], "platformSpecificData": {"firstComment": m["first_comment"]}},
            {"platform": "facebook", "accountId": FACEBOOK_ID, "customContent": m["linkedin"],
             "scheduledFor": m["when"], "platformSpecificData": {"firstComment": m["first_comment"]}},
            {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": m["short"], "scheduledFor": m["when"]},
        ],
    }
    r = requests.post(f"{BASE}/posts", headers=HDR, json=body, timeout=60)
    p = r.json().get("post", {})
    return f"{r.status_code} id={p.get('_id','?')} status={p.get('status','?')}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    for m in MAGNETS:
        card = HERE / m["card"]
        if not card.exists():
            print(f"  ✗ {m['key']}: card missing {card.name}"); continue
        if args.dry_run:
            print(f"  [{m['key']}] {m['when']} ET | card {m['card']} | {m['link']}")
        else:
            print(f"  [{m['key']}] {schedule(m)}")


if __name__ == "__main__":
    main()
