"""
Schedule one rebel-campaign reel to all 5 Zernio platforms
(LinkedIn, Instagram, Facebook, TikTok, YouTube) with platform-specific
copy and a first-comment CTA.

Usage:
  python3 schedule_reel.py <reel_key>   # reel_key must be in REELS below
"""
import os
import sys
import requests

from zernio_key import ZERNIO_API_KEY as API_KEY

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID = "6909409a5f6fbb9ef8323074"
TIKTOK_ID = "690941425f6fbb9ef8323078"
YOUTUBE_ID = "690940d35f6fbb9ef8323077"
TIMEZONE = "America/New_York"

REBEL = os.path.dirname(os.path.abspath(__file__))
CALCULATOR_LINK = "www.crosswalkwisdom.com/img/calculator"
FIRST_COMMENT = f"If you're ready to actually run the math on staying vs. pivoting → {CALCULATOR_LINK}"

REELS = {
    "reel1": {
        "video": f"{REBEL}/reels/reel1-whose-dream/source.enhanced.mp4",
        "scheduled_for": "2026-06-25T15:00:00.000Z",  # 11am ET
        "linkedin": """Nobody tells you this part: the career that made your family proud was never actually about you.

It was about status. Access. Never paying for a consultation again.

That's not a moral failing. That's how survival cultures work. Your parents needed something solved. You became the answer.

The system ran exactly as designed:
→ You got in.
→ You got through.
→ You got licensed.

Mission accomplished — for them.

So here's the question that was never actually yours to answer: now that you're safe, what do YOU want?

Not what was realistic. Not what kept everyone proud.

What did you actually want?""",
        "instagram": """Nobody tells you this part: the career that made your family proud was never about you.

Status. Access. Never paying for a consultation again. That's what it bought THEM.

Now that you're safe — what do you want?

#doctorburnout #physicianburnout #careerchange #immigrantfamily #crosswalkwisdom""",
        "facebook": """Nobody tells you this part: the career that made your family proud was never actually about you. It was about status, access, never paying for a consultation again.

That's not a moral failing — that's how survival cultures work. The system ran exactly as designed. You got in, you got through, you got licensed.

So here's the question nobody asked: now that you're safe, what do YOU want?""",
        "tiktok": """The career that made your family proud was never about you. Status. Access. Security. Now that you're safe — what do YOU want? \U0001fa7a

#doctorburnout #careerchange #immigrantfamily #crosswalkwisdom""",
        "youtube_title": "Whose Dream Was It, Really? (Doctors, Watch This)",
        "youtube_desc": """Every family dinner, every "you should be a doctor" — it was never about you. Now that you're safe, what do you actually want?

#Shorts #CrosswalkWisdom #DoctorBurnout #CareerChange""",
    },
    "reel2": {
        "video": f"{REBEL}/reels/reel2-the-timeline/source.enhanced.mp4",
        "scheduled_for": "2026-06-27T15:00:00.000Z",  # 11am ET
        "linkedin": """Walk the timeline with me: high school sciences, MCAT, med school, residency, licensed.

Notice what's missing from every single step? You.

Each one had a job: get you to the next one. Nobody asked what YOU wanted at any of them — because the timeline wasn't built for that question.

Your framework: happiness, flourishing, your choices.
Their framework: stability, status, survival.

Stability ≠ flourishing. Those are different objectives. Nobody told you there was a difference — you just kept running the same checklist and assumed the feeling would catch up.

You're 35. You're licensed. You're not free.

That's not a contradiction. That's the timeline working exactly as designed — for a goal that was never about your flourishing.""",
        "instagram": """You're 35. You're licensed. You're not free.

Nobody warned you those were three different milestones.

Stability ≠ flourishing — nobody told you there was a difference.

#doctorburnout #physicianburnout #careerchange #crosswalkwisdom""",
        "facebook": """Walk the timeline with me: high school sciences, MCAT, med school, residency, licensed. Notice what's missing from every step? You.

Your framework: happiness, flourishing, your choices. Their framework: stability, status, survival.

Stability ≠ flourishing. Nobody told you there was a difference.

You're 35. You're licensed. You're not free. That's the timeline working exactly as designed — for a goal that was never about your flourishing.""",
        "tiktok": """High school sciences. MCAT. Med school. Residency. Licensed. Notice what's missing from every step? You. \U0001fa7a

#doctorburnout #careerchange #crosswalkwisdom""",
        "youtube_title": "You're 35. Licensed. Not Free. Here's Why.",
        "youtube_desc": """Walk the timeline: high school, MCAT, med school, residency, licensed. Notice what's missing from every step? You. Stability isn't flourishing.

#Shorts #CrosswalkWisdom #DoctorBurnout #CareerChange""",
    },
    "reel3": {
        "video": f"{REBEL}/reels/reel3-the-code/source.enhanced.mp4",
        "scheduled_for": "2026-06-29T15:00:00.000Z",  # 11am ET
        "linkedin": """You're running 1985 survival logic on a 2026 problem.

That's not a metaphor. That's literally what's installed in your head.

1985 — the year the code was written. Your parents needed safety, status, belonging. Medicine was the only program that delivered all three at once. So they installed it. In you.

Safety. Status. Belonging.

The code worked. You became a doctor.

There's just one problem: it was written for their threat environment. Not yours.

Wrong era. Right person.""",
        "instagram": """You're running 1985 survival logic on a 2026 problem.

Safety, status, belonging — the code worked, you became a doctor.

But it was written for their threat environment, not yours. Wrong era.

#doctorburnout #physicianburnout #careerchange #crosswalkwisdom""",
        "facebook": """You're running 1985 survival logic on a 2026 problem. Your parents needed safety, status, belonging — medicine was the only program that delivered all three. So they installed it. In you.

The code worked. You became a doctor.

There's just one problem: it was written for their threat environment. Not yours. Wrong era. Right person.""",
        "tiktok": """1985. The year the code was written. Safety. Status. Belonging. It worked — you became a doctor. Wrong era though. \U0001fa7a

#doctorburnout #careerchange #crosswalkwisdom""",
        "youtube_title": "You're Running 1985 Survival Code (Doctors, Watch This)",
        "youtube_desc": """1985 — the year the survival code was written: safety, status, belonging. It worked, you became a doctor. But it was written for their threat environment, not yours.

#Shorts #CrosswalkWisdom #DoctorBurnout #CareerChange""",
    },
    "reel4": {
        "video": f"{REBEL}/reels/reel4-the-sacrifice/source.enhanced.mp4",
        "scheduled_for": "2026-07-01T15:00:00.000Z",  # 11am ET
        "linkedin": """Here's the thing no one says out loud: your parents' sacrifice was supposed to buy you freedom.

Somewhere along the way, it became the reason you can't leave.

They came with nothing. A suitcase. A passport. They built something so you'd have choices they never had.

What it was supposed to be: freedom. Options. Permission to choose.
What it became: obligation. Guilt. Can't leave.

That inversion isn't your fault, and it isn't theirs either. Nobody planned for the gift to calcify into a debt.

But here's the part that changes everything: leaving isn't betraying the sacrifice.

Leaving IS the mission completing.""",
        "instagram": """Your parents' sacrifice was supposed to buy you freedom.

Somewhere along the way it became the reason you can't leave.

Options, not obligations — that was always the point.

#immigrantfamily #doctorburnout #careerchange #crosswalkwisdom""",
        "facebook": """Here's the thing no one says out loud: your parents' sacrifice was supposed to buy you freedom. Somewhere along the way, it became the reason you can't leave.

They came with nothing so you'd have choices they never had.

What it was supposed to be: freedom, options, permission to choose. What it became: obligation, guilt, can't leave.

Leaving isn't betraying the sacrifice. Leaving IS the mission completing.""",
        "tiktok": """They came with nothing so you'd have choices. Not so you'd feel trapped. Options, not obligations. \U0001fa7a

#immigrantfamily #careerchange #crosswalkwisdom""",
        "youtube_title": "Your Parents' Sacrifice Wasn't Supposed to Be a Cage",
        "youtube_desc": """They came with nothing so you'd have choices they never had. Somewhere along the way that gift became a cage. Leaving isn't betraying the sacrifice — leaving is completing it.

#Shorts #CrosswalkWisdom #DoctorBurnout #CareerChange""",
    },
    "reel5": {
        "video": f"{REBEL}/reels/reel5-different-question/source.enhanced.mp4",
        "scheduled_for": "2026-07-03T15:00:00.000Z",  # 11am ET
        "linkedin": """Most doctors ask: can I leave medicine?

Wrong question. The right one: what am I actually built for?

Your training gave you precision. Capacity for complexity. The ability to hold high stakes without falling apart.

The system said those skills are only for clinical work. The system was wrong.

Wrong question: Can I leave? Am I allowed? What will they think?
Right question: What am I built for? Where do my skills go? What do I choose?

What you can do with what you have — that's a much more interesting question than whether you're allowed to stop.""",
        "instagram": """Most doctors ask: can I leave medicine? Wrong question.

The right one: what am I actually built for?

Precision, complexity, high stakes — the system said those only count in a hospital. The system was wrong.

#doctorburnout #careerchange #physiciantransition #crosswalkwisdom""",
        "facebook": """Most doctors ask: can I leave medicine? Wrong question. The right one: what am I actually built for?

Your training gave you precision, capacity for complexity, the ability to hold high stakes without falling apart. The system said those skills are only for clinical work. The system was wrong.

What you can do with what you have — that's a much more interesting question than whether you're allowed to stop.""",
        "tiktok": """Wrong question: can I leave medicine? Right question: what am I actually built for? \U0001fa7a

#doctorburnout #careerchange #crosswalkwisdom""",
        "youtube_title": "Wrong Question vs. Right Question (Doctors Considering Leaving)",
        "youtube_desc": """Most doctors ask can I leave medicine. Wrong question. The right one: what am I actually built for? Precision, complexity, high stakes — the system said those only count in a hospital. The system was wrong.

#Shorts #CrosswalkWisdom #DoctorBurnout #CareerChange""",
    },
}


def upload_video(filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    r = requests.post(
        f"{BASE}/media/presign",
        headers=HEADERS,
        json={"filename": filename, "contentType": "video/mp4", "fileSize": filesize},
    )
    r.raise_for_status()
    data = r.json()
    upload_url = data["uploadUrl"]
    public_url = data["publicUrl"]
    with open(filepath, "rb") as f:
        put_r = requests.put(upload_url, data=f, headers={"Content-Type": "video/mp4"})
        put_r.raise_for_status()
    return public_url


def schedule(reel_key: str):
    reel = REELS[reel_key]
    video_path = reel["video"]
    if not os.path.exists(video_path):
        print(f"[FAIL] video not found: {video_path}")
        return

    print(f"Uploading {video_path}...")
    video_url = upload_video(video_path)
    print(f"  [UPLOAD OK] {video_url}")

    media_item = {"url": video_url, "type": "video"}
    scheduled_for = reel["scheduled_for"]

    platforms = [
        {
            "platform": "linkedin",
            "accountId": LINKEDIN_ID,
            "customContent": reel["linkedin"],
            "scheduledFor": scheduled_for,
            "platformSpecificData": {"firstComment": FIRST_COMMENT},
        },
        {
            "platform": "instagram",
            "accountId": INSTAGRAM_ID,
            "customContent": reel["instagram"],
            "scheduledFor": scheduled_for,
            "platformSpecificData": {"firstComment": FIRST_COMMENT},
        },
        {
            "platform": "facebook",
            "accountId": FACEBOOK_ID,
            "customContent": reel["facebook"],
            "scheduledFor": scheduled_for,
            "platformSpecificData": {"firstComment": FIRST_COMMENT},
        },
        {
            "platform": "tiktok",
            "accountId": TIKTOK_ID,
            "customContent": reel["tiktok"],
            "scheduledFor": scheduled_for,
        },
        {
            "platform": "youtube",
            "accountId": YOUTUBE_ID,
            "customContent": reel["youtube_desc"],
            "title": reel["youtube_title"],
            "scheduledFor": scheduled_for,
        },
    ]

    body = {
        "content": reel["linkedin"],
        "mediaItems": [media_item],
        "platforms": platforms,
        "scheduledFor": scheduled_for,
        "timezone": TIMEZONE,
        "isDraft": False,
    }

    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    print(f"[POST {r.status_code}] {r.text[:500]}")


if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "reel1"
    schedule(key)
