"""
Round-2 rebel campaign: LinkedIn text-only posts (no video).

Videos averaged 7–20 views on LinkedIn. Text posts with first-person voice
get dramatically more organic reach. Same approved copy, text format only.

Spaced July 12–20, 11am ET (15:00 UTC), every other day.

Usage:
  PYTHONPATH="/Users/toto/Claude TubeonAI" python3 rebel-campaign/schedule_text_wave.py <reel_key>
  PYTHONPATH="/Users/toto/Claude TubeonAI" python3 rebel-campaign/schedule_text_wave.py all
"""
import sys
import requests

from zernio_key import ZERNIO_API_KEY as API_KEY

BASE = "https://zernio.com/api/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID = "690940455f6fbb9ef8323070"
TIMEZONE = "America/New_York"
CALCULATOR_LINK = "www.crosswalkwisdom.com/img/calculator"
FIRST_COMMENT = f"If you're ready to actually run the math on staying vs. pivoting → {CALCULATOR_LINK}"

TEXT_POSTS = {
    "reel1": {
        "scheduled_for": "2026-07-12T15:00:00.000Z",
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
        "scheduled_for": "2026-07-14T15:00:00.000Z",
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
        "scheduled_for": "2026-07-16T15:00:00.000Z",
        "content": """You're running 1985 survival logic on a 2026 problem.

That's not a metaphor. That's literally what's installed in your head.

1985 — the year the code was written. Your parents needed safety, status, belonging. Medicine was the only program that delivered all three at once. So they installed it. In you.

Safety. Status. Belonging.

The code worked. You became a doctor.

There's just one problem: it was written for their threat environment. Not yours.

Wrong era. Right person.""",
    },
    "reel4": {
        "scheduled_for": "2026-07-18T15:00:00.000Z",
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
        "scheduled_for": "2026-07-20T15:00:00.000Z",
        "content": """Most doctors ask: can I leave medicine?

Wrong question. The right one: what am I actually built for?

Your training gave you precision. Capacity for complexity. The ability to hold high stakes without falling apart.

The system said those skills are only for clinical work. The system was wrong.

Wrong question: Can I leave? Am I allowed? What will they think?
Right question: What am I built for? Where do my skills go? What do I choose?

What you can do with what you have — that's a much more interesting question than whether you're allowed to stop.""",
    },
}


def schedule_text(key: str) -> None:
    post = TEXT_POSTS[key]
    scheduled_for = post["scheduled_for"]
    content = post["content"]

    body = {
        "content": content,
        "platforms": [
            {
                "platform": "linkedin",
                "accountId": LINKEDIN_ID,
                "customContent": content,
                "scheduledFor": scheduled_for,
                "platformSpecificData": {"firstComment": FIRST_COMMENT},
            }
        ],
        "scheduledFor": scheduled_for,
        "timezone": TIMEZONE,
        "isDraft": False,
    }

    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    print(f"[{key}] POST {r.status_code} — {r.text[:200]}")


if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "reel1"
    if key == "all":
        for k in TEXT_POSTS:
            schedule_text(k)
    else:
        schedule_text(key)
