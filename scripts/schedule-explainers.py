"""
schedule-explainers.py
Upload and schedule the 4 Crosswalk Wisdom explainer videos on Zernio.
Schedule: Mar 26-29 at 1pm EST (18:00:00Z)
Platforms: LinkedIn, Instagram, Facebook, TikTok, YouTube
"""

import requests
import os

BASE    = "https://zernio.com/api/v1"
HEADERS = {"Authorization": "Bearer sk_d1c977cc304ec9685c24f22c7e3b868abd5a10b9db8f7648b2b74384ab1ca399"}
OUT_DIR = "/Users/toto/Claude TubeonAI/crosswalk-remotion/out/explainers"

ACCOUNT_IDS = {
    "linkedin":  "690940455f6fbb9ef8323070",
    "instagram": "690940655f6fbb9ef8323072",
    "facebook":  "6909409a5f6fbb9ef8323074",
    "tiktok":    "690941425f6fbb9ef8323078",
    "youtube":   "690940d35f6fbb9ef8323077",
}

VIDEOS = [
    {
        "file":  "fear-explainer.mp4",
        "date":  "2026-03-26",
        "yt_title": "Burnout Has 3 Fears Inside It. Most People Only Name One. | Crosswalk Wisdom",
        "li_copy": """Nobody tells you that burnout has three distinct fears hiding inside it.

The one everyone admits: I can't afford to quit.
The one nobody says out loud: What will people think?
The one that runs deepest: Who am I if I'm not this?

The third fear is the one that actually keeps you stuck.
It's not a financial problem. It's an identity problem.

I built the Fear Audit because I lived all three — and naming them was the first thing that moved me.

If you're in healthcare and something feels off, take it. It's free, 2 minutes, and surprisingly honest.

Link in bio.""",
        "ig_copy": """Burnout isn't one fear. It's three. And most people only ever name the first one.

The one that actually keeps you trapped might surprise you.

Fear Audit — link in bio.

#NurseBurnout #HealthcareWorkers #BurnoutRecovery #IdentityLoss #CrosswalkWisdom #PhysicianBurnout #NurseLife #HealthcareMentalHealth""",
        "fb_copy": """Nobody talks about this: burnout actually has three fears inside it.

Most people only admit the first one — "I can't afford to quit."

But the one that really keeps you stuck runs much deeper than money.

If you're in healthcare and something feels off, I made this for you. The Fear Audit is free, takes 2 minutes, and it's surprisingly honest about what's actually going on.

Link in bio 👆""",
    },
    {
        "file":  "crosswalk-method.mp4",
        "date":  "2026-03-27",
        "yt_title": "The 4 Stages of Getting Unstuck From Healthcare Burnout | Crosswalk Wisdom",
        "li_copy": """I didn't quit medicine. I moved through four stages.

START — I saw the problem but couldn't move. I kept picking up extra shifts.
STOP — I paused. I sat in parking lots. I stopped pretending I was fine.
ELDER — I found people who had crossed before me. Their honesty changed everything.
HUMAN — I chose myself. Not the career. Me.

Most burned-out healthcare workers are stuck in START. They can see the crossing. They just won't step off the curb.

Which stage are you in? (Serious question — drop it below.)""",
        "ig_copy": """There are 4 stages of getting unstuck from healthcare burnout.

Most people are stuck at Stage 1 — and don't even know it.

Which one are you? 👇

#HealthcareBurnout #NurseLife #CareerTransition #CrosswalkWisdom #BurnoutRecovery #NurseBurnout #PhysicianBurnout #HealthcareWorkers""",
        "fb_copy": """I didn't quit medicine all at once. I moved through four stages — and I've watched hundreds of healthcare workers do the same.

START → STOP → ELDER → HUMAN.

Most people are stuck at START. They can see the problem. They just can't move yet.

Which stage are you in right now? Drop it in the comments — no judgment, just honest conversation.""",
    },
    {
        "file":  "ai-bridge.mp4",
        "date":  "2026-03-28",
        "yt_title": "You Have 47 Transferable Skills. AI Can Find Them in 30 Minutes. | Crosswalk Wisdom",
        "li_copy": """I asked 100 burned-out nurses what skills they had outside of healthcare.

Most said: "None."

Every single one was wrong.

The problem isn't a lack of skills. It's a lack of visibility. You've been so deep inside one identity that you can't see what you actually bring.

AI can help you see it in 30 minutes. Not ChatGPT giving you generic career advice — structured prompts that surface what you already know.

That's what the Courage to Choose guide is. Prompts that do the work you've been putting off.

Link in bio.""",
        "ig_copy": """You have 47+ transferable skills that have nothing to do with your job title.

AI can find them in 30 minutes. Here's how. 🔗

Link in bio.

#AIForNurses #CareerChange #NurseBurnout #HealthcareWorkers #CrosswalkWisdom #AITools #NurseLife #CareerTransition""",
        "fb_copy": """Here's something I tell every burned-out nurse who says they have "no skills outside healthcare":

You're wrong. You just can't see them yet.

After years inside one identity, it's nearly impossible to see what you actually bring to the world. AI can help you map it — in 30 minutes, with the right prompts.

The Courage to Choose guide is exactly that. Link in bio 👆""",
    },
    {
        "file":  "grief-explainer.mp4",
        "date":  "2026-03-29",
        "yt_title": "Leaving Healthcare Feels Like a Death. Here's Why That's Normal. | Crosswalk Wisdom",
        "li_copy": """The thing nobody prepares you for when you leave healthcare:

It feels like grief.

Not metaphorically. Neurologically.

Your brain processes the loss of a professional identity the same way it processes losing someone you love.

The numbness. The anger. The bargaining. The morning you sit in the parking lot and can't go in.

I used to think that grief meant I was making a mistake.

I was wrong.

The grief meant something had mattered. And something new was beginning.

If you're in that parking lot right now — you're not broken. You're between.""",
        "ig_copy": """Nobody tells you that leaving your healthcare career feels like a death.

Not a metaphor. The grief is real — and it doesn't mean you made the wrong choice. 💙

#HealthcareBurnout #NurseLife #LeavingMedicine #GriefAndLoss #CrosswalkWisdom #NurseBurnout #PhysicianBurnout #HealthcareWorkers""",
        "fb_copy": """Can we talk about something nobody mentions?

When you leave healthcare — or even just seriously consider it — it feels like grief.

Not "I'm sad" grief. Deep, disorienting, neurological grief. The same kind your brain uses when you lose a person.

If you've felt numb, angry, stuck in a parking lot unable to walk in — that's not weakness. That's your nervous system processing a real loss.

You're not broken. You're between.

If this resonates, I'd love to hear your story in the comments. 💙""",
    },
]


def presign_and_upload(filepath, filename):
    print(f"  → Presigning {filename}...")
    r = requests.post(f"{BASE}/media/presign", headers=HEADERS,
                      json={"filename": filename, "contentType": "video/mp4"})
    r.raise_for_status()
    upload_url = r.json()["uploadUrl"]
    public_url = r.json()["publicUrl"]

    print(f"  → Uploading {filename} ({os.path.getsize(filepath) // 1024 // 1024}MB)...")
    with open(filepath, "rb") as f:
        put = requests.put(upload_url, data=f, headers={"Content-Type": "video/mp4"})
        put.raise_for_status()

    print(f"  ✅ Uploaded → {public_url}")
    return public_url


def schedule_post(video, public_url):
    scheduled_for = f"{video['date']}T18:00:00.000Z"  # 1pm EST = 18:00 UTC
    li  = video["li_copy"]
    ig  = video["ig_copy"]
    fb  = video["fb_copy"]
    tt  = ig
    yt  = li + "\n\n#Shorts #CrosswalkWisdom #HealthcareBurnout #NurseBurnout #CareerTransition"

    body = {
        "content": li,
        "mediaItems": [{"url": public_url, "type": "video"}],
        "scheduledFor": scheduled_for,
        "timezone": "America/New_York",
        "platforms": [
            {"platform": "linkedin",  "accountId": ACCOUNT_IDS["linkedin"],
             "customContent": li, "scheduledFor": scheduled_for},
            {"platform": "instagram", "accountId": ACCOUNT_IDS["instagram"],
             "customContent": ig, "scheduledFor": scheduled_for},
            {"platform": "facebook",  "accountId": ACCOUNT_IDS["facebook"],
             "customContent": fb, "scheduledFor": scheduled_for},
            {"platform": "tiktok",    "accountId": ACCOUNT_IDS["tiktok"],
             "customContent": tt, "scheduledFor": scheduled_for},
            {"platform": "youtube",   "accountId": ACCOUNT_IDS["youtube"],
             "customContent": yt, "title": video["yt_title"],
             "scheduledFor": scheduled_for},
        ],
    }

    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    r.raise_for_status()
    post_id = r.json().get("_id", "?")
    print(f"  ✅ Scheduled → {scheduled_for} ET | Post ID: {post_id}")
    return post_id


if __name__ == "__main__":
    print("🗓️  Crosswalk Wisdom — Explainer Video Scheduler")
    print("─" * 52)

    for v in VIDEOS:
        filepath = os.path.join(OUT_DIR, v["file"])
        print(f"\n▶ {v['file']} — {v['date']} at 1pm ET")

        try:
            url = presign_and_upload(filepath, v["file"])
            schedule_post(v, url)
        except Exception as e:
            print(f"  ❌ Failed: {e}")

    print("\n✨ Done! All 4 videos scheduled across LinkedIn, Instagram, Facebook, TikTok, YouTube.")
