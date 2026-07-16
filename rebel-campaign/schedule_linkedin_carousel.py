"""
LinkedIn document-carousel wave for the rebel campaign.

LinkedIn's native carousel format is a multi-page PDF ("document post").
This outperforms both video and plain text in reach because LinkedIn
prioritises documents in the feed — users swipe through slides without
leaving the app, which drives strong dwell-time signals.

Uses the same 4:5 (1080×1350) slides already generated for Instagram,
combined into a PDF per reel and uploaded as type "document".

Scheduled July 12–20 (same dates as the text-only wave) at 2pm ET so
they land 3 hours AFTER the text post — no same-hour collision.

Usage:
  PYTHONPATH="/Users/toto/Claude TubeonAI" python3 rebel-campaign/schedule_linkedin_carousel.py <reel_key>
  PYTHONPATH="/Users/toto/Claude TubeonAI" python3 rebel-campaign/schedule_linkedin_carousel.py all
"""
import os
import sys
import io
import requests
from PIL import Image

from zernio_key import ZERNIO_API_KEY as API_KEY

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID = "690940455f6fbb9ef8323070"
TIMEZONE = "America/New_York"
CALCULATOR_LINK = "www.crosswalkwisdom.com/img/calculator"
FIRST_COMMENT = f"If you're ready to actually run the math on staying vs. pivoting → {CALCULATOR_LINK}"

CAROUSEL_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carousels")

# 2pm ET = 18:00 UTC — 3h after the 11am text posts
SCHEDULE = {
    "reel1": {
        "scheduled_for": "2026-07-12T18:00:00.000Z",
        "content": """Nobody tells you this part: the career that made your family proud was never actually about you.

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
    },
    "reel2": {
        "scheduled_for": "2026-07-14T18:00:00.000Z",
        "content": """Walk the timeline with me: high school sciences, MCAT, med school, residency, licensed.

Notice what's missing from every single step? You.

Each one had a job: get you to the next one. Nobody asked what YOU wanted at any of them — because the timeline wasn't built for that question.

Your framework: happiness, flourishing, your choices.
Their framework: stability, status, survival.

Stability ≠ flourishing. Those are different objectives. Nobody told you there was a difference — you just kept running the same checklist and assumed the feeling would catch up.

You're 35. You're licensed. You're not free.

That's not a contradiction. That's the timeline working exactly as designed — for a goal that was never about your flourishing.""",
    },
    "reel3": {
        "scheduled_for": "2026-07-16T18:00:00.000Z",
        "content": """You're running 1985 survival logic on a 2026 problem.

That's not a metaphor. That's literally what's installed in your head.

1985 — the year the code was written. Your parents needed safety, status, belonging. Medicine was the only program that delivered all three at once. So they installed it. In you.

Safety. Status. Belonging.

The code worked. You became a doctor.

There's just one problem: it was written for their threat environment. Not yours.

Wrong era. Right person.""",
    },
    "reel4": {
        "scheduled_for": "2026-07-18T18:00:00.000Z",
        "content": """Here's the thing no one says out loud: your parents' sacrifice was supposed to buy you freedom.

Somewhere along the way, it became the reason you can't leave.

They came with nothing. A suitcase. A passport. They built something so you'd have choices they never had.

What it was supposed to be: freedom. Options. Permission to choose.
What it became: obligation. Guilt. Can't leave.

That inversion isn't your fault, and it isn't theirs either. Nobody planned for the gift to calcify into a debt.

But here's the part that changes everything: leaving isn't betraying the sacrifice.

Leaving IS the mission completing.""",
    },
    "reel5": {
        "scheduled_for": "2026-07-20T18:00:00.000Z",
        "content": """Most doctors ask: can I leave medicine?

Wrong question. The right one: what am I actually built for?

Your training gave you precision. Capacity for complexity. The ability to hold high stakes without falling apart.

The system said those skills are only for clinical work. The system was wrong.

Wrong question: Can I leave? Am I allowed? What will they think?
Right question: What am I built for? Where do my skills go? What do I choose?

What you can do with what you have — that's a much more interesting question than whether you're allowed to stop.""",
    },
}


def slides_to_pdf(reel_key: str) -> bytes:
    slide_dir = os.path.join(CAROUSEL_BASE, reel_key, "instagram")
    pngs = sorted([
        os.path.join(slide_dir, f)
        for f in os.listdir(slide_dir)
        if f.endswith(".png")
    ])
    imgs = []
    for path in pngs:
        img = Image.open(path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        imgs.append(img)
    buf = io.BytesIO()
    imgs[0].save(buf, format="PDF", save_all=True, append_images=imgs[1:])
    return buf.getvalue()


def upload_pdf(reel_key: str, pdf_bytes: bytes) -> str:
    filename = f"rebel-{reel_key}.pdf"
    r = requests.post(
        f"{BASE}/media/presign",
        headers=HEADERS,
        json={"filename": filename, "contentType": "application/pdf", "fileSize": len(pdf_bytes)},
    )
    r.raise_for_status()
    data = r.json()
    put_r = requests.put(
        data["uploadUrl"],
        data=pdf_bytes,
        headers={"Content-Type": "application/pdf"},
    )
    put_r.raise_for_status()
    return data["publicUrl"]


def schedule_carousel(reel_key: str) -> None:
    entry = SCHEDULE[reel_key]
    print(f"[{reel_key}] Building PDF from Instagram slides...")
    pdf_bytes = slides_to_pdf(reel_key)
    print(f"  PDF size: {len(pdf_bytes):,} bytes")

    print(f"[{reel_key}] Uploading PDF...")
    pdf_url = upload_pdf(reel_key, pdf_bytes)
    print(f"  URL: {pdf_url[:80]}...")

    body = {
        "content": entry["content"],
        "mediaItems": [{"url": pdf_url, "type": "document"}],
        "platforms": [
            {
                "platform": "linkedin",
                "accountId": LINKEDIN_ID,
                "customContent": entry["content"],
                "scheduledFor": entry["scheduled_for"],
                "platformSpecificData": {"firstComment": FIRST_COMMENT},
            }
        ],
        "scheduledFor": entry["scheduled_for"],
        "timezone": TIMEZONE,
        "isDraft": False,
    }

    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    print(f"[{reel_key}] POST {r.status_code} — {r.text[:250]}\n")


if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "reel1"
    if key == "all":
        for k in SCHEDULE:
            schedule_carousel(k)
    else:
        schedule_carousel(key)
