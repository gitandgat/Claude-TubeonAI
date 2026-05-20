"""
Schedule: 6 LinkedIn Written Posts — May 11–16 2026
Images:   social-assets/linkedin-may/images/post-{f,g,h,i,j,k}.png
Times:    One per day at 8:00 AM ET (= 12:00 UTC)

Post 1 (per day): LinkedIn, Instagram, Facebook, TikTok — with image
Post 2 (per day): YouTube — text only (YouTube rejects image-only posts)
"""
import os
import time
import requests

BASE    = "https://zernio.com/api/v1"
API_KEY = "sk_d1c977cc304ec9685c24f22c7e3b868abd5a10b9db8f7648b2b74384ab1ca399"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
YOUTUBE_ID   = "690940d35f6fbb9ef8323077"
TIMEZONE     = "America/New_York"

IMAGES_DIR = "/Users/toto/Claude TubeonAI/social-assets/linkedin-may/images"

# ── Post definitions ────────────────────────────────────────────────────────────

POSTS = [
    {
        "id": "f",
        "image": "post-f.png",
        "scheduled_for": "2026-05-11T08:00:00",
        "youtube_title": "The most dangerous number in an IMG's life isn't the match rate. It's $18,000.",
        "linkedin": """\
The most dangerous number in an IMG's life isn't the match rate.
It's $18,000 — the average spent before the first CaRMS rejection.

The question isn't "was it worth it?"
It's "what does that number own of you right now?"

I've seen what $18,000 does to a decision.

✨ It makes you register for Part 2 when your gut says stop.
✨ It makes you apply to CaRMS a third time because stopping feels like losing the bet.
✨ It makes you stay on a path that stopped being yours two years ago.

The money isn't sunk because you spent it.
It's sunk because it now controls your next move.

👣 There's a difference between honoring your investment and being imprisoned by it.
👣 The debt doesn't disappear if you match. Neither does the cost if you don't.
👣 The wisest financial decision is usually the one your ego fights hardest.

I call this Crosswalk Wisdom — learning to look both ways before crossing.
Not just at the traffic. At the cost of waiting at the curb forever.

If you're doing the math at midnight and the numbers keep leading you in circles, I wrote something that might help. 5 minutes. 📬 Link in the comments.

Have you ever made a decision — or kept delaying one — because of money already spent? What did staying cost you?

#CrosswalkWisdom #IMGCanada #UnmatchedIMG #CareerTransition""",
        "short": """\
The most dangerous number in an IMG's life isn't the match rate.
It's $18,000 — the average spent before the first CaRMS rejection.

✨ It makes you register for Part 2 when your gut says stop.
✨ It makes you apply a third time because stopping feels like losing the bet.
✨ It makes you stay on a path that stopped being yours two years ago.

The money isn't sunk because you spent it.
It's sunk because it now controls your next move.

Have you ever delayed a decision because of money already spent?

#CrosswalkWisdom #IMGCanada #UnmatchedIMG #CareerTransition #BurnoutRecovery""",
    },
    {
        "id": "g",
        "image": "post-g.png",
        "scheduled_for": "2026-05-12T08:00:00",
        "youtube_title": "CaRMS didn't reject your application. It rejected your identity.",
        "linkedin": """\
For 10 years, "doctor" wasn't what you did.
It was who you were.

CaRMS didn't reject your application.
It rejected your identity. No wonder it hurt like that.

The question isn't "how do I get back in?"
It's "who am I when the credential isn't the answer?"

I know what it feels like when that question lands.

✨ Your name still has MD after it.
✨ Your knowledge didn't leave when the match result did.
✨ But you're walking around in a body that feels like it belongs to someone else.

The identity cage isn't the hospital.
It's the story you've been telling yourself about who you have to be to matter.

👣 You are not your match result.
👣 You are not your exam scores.
👣 You are a person who became a doctor — not a doctor who forgot to become a person.

I call it the Identity Cage — and it was the first thing Crosswalk Wisdom was built to address.

If you're sitting with this question and don't know where to start, there's a short framework that helped me and a lot of people like you. 5 minutes. 📬 Link in the comments.

When did you first realize that "doctor" had become your whole identity — not just your career?

#CrosswalkWisdom #IMGCanada #IdentityCrisis #BurnoutRecovery""",
        "short": """\
For 10 years, "doctor" wasn't what you did.
It was who you were.

CaRMS didn't reject your application.
It rejected your identity. No wonder it hurt like that.

✨ Your name still has MD after it.
✨ Your knowledge didn't leave when the match result did.
✨ But you're walking around in a body that feels like it belongs to someone else.

👣 You are not your match result.
👣 You are not your exam scores.
👣 You are a person who became a doctor — not a doctor who forgot to become a person.

When did "doctor" become your whole identity — not just your career?

#CrosswalkWisdom #IMGCanada #IdentityCrisis #BurnoutRecovery #CareerTransition""",
    },
    {
        "id": "h",
        "image": "post-h.png",
        "scheduled_for": "2026-05-13T08:00:00",
        "youtube_title": "Nobody in your family has done this before. That's not your fault.",
        "linkedin": """\
Nobody in your family has done this before.
Nobody in your community has language for what you're going through.

That's not your fault.
That's just how new territory feels.

The question isn't "why don't they understand?"
It's "who taught you that you needed their map?"

I've sat with IMGs who are completely alone in this.

✨ Their parents back home think they're "almost there."
✨ Their study group stopped texting after match results dropped.
✨ Their WhatsApp family chat has no category for "I'm choosing something different."

The loneliness isn't because you're doing something wrong.
It's because you're doing something first.

👣 You don't need permission from people who've never walked this road.
👣 You don't need language your community hasn't invented yet.
👣 You need one person who ran the same math and chose a different answer.

I left medicine. I became a crossing guard. Nobody in my world had a category for that either.
That's why I built Crosswalk Wisdom — for the people doing something their community doesn't have words for yet.

If you're standing at a crosswalk nobody around you can see, this might be worth 5 minutes. 📬 Link in the comments.

What decision are you sitting with that nobody in your life fully understands?

#CrosswalkWisdom #IMGCanada #ImmigrantExperience #UnmatchedIMG""",
        "short": """\
Nobody in your family has done this before.
Nobody in your community has language for what you're going through.

That's not your fault. That's just how new territory feels.

✨ Their parents think they're "almost there."
✨ Their study group stopped texting after match results.
✨ Their WhatsApp chat has no category for "I'm choosing something different."

The loneliness isn't because you're doing something wrong.
It's because you're doing something first.

What decision are you sitting with that nobody around you fully understands?

#CrosswalkWisdom #IMGCanada #ImmigrantExperience #UnmatchedIMG #BurnoutRecovery""",
    },
    {
        "id": "i",
        "image": "post-i.png",
        "scheduled_for": "2026-05-14T08:00:00",
        "youtube_title": "I spent 12 years becoming a physician. A crossing guard taught me more.",
        "linkedin": """\
I spent 12 years becoming a physician.
I spent 6 months becoming a crossing guard.

The crossing guard taught me more about starting over than medical school ever did.

The question isn't "how could you give that up?"
It's "what do you learn when you stop performing and start watching?"

Here's what I found on the crosswalk:

✨ Healing doesn't happen in conferences. It happens in parking lots.
✨ A first-grader grabbing your hand teaches more about trust than any textbook.
✨ Slowing down isn't failure. It's observation. And observation is where wisdom begins.

A crosswalk teaches things a hospital can't.

👣 How to be present without a protocol.
👣 How to slow traffic without a title.
👣 How to wave at strangers and mean it.

I call it Crosswalk Wisdom — the lessons that only show up when you're in a yellow vest instead of a white coat.

If this is landing, there's something I wrote that might give you language for what you're feeling. 5 minutes. 📬 Link in the comments.

Have you ever stepped into a role that looked like a step down — but taught you something you couldn't have learned any other way?

#CrosswalkWisdom #BurnoutRecovery #CareerTransition #IMGCanada""",
        "short": """\
I spent 12 years becoming a physician.
I spent 6 months becoming a crossing guard.

The crossing guard taught me more about starting over than medical school ever did.

✨ Healing doesn't happen in conferences. It happens in parking lots.
✨ Slowing down isn't failure. It's observation.
✨ A first-grader taught me more about trust than any textbook.

👣 How to be present without a protocol.
👣 How to slow traffic without a title.
👣 How to wave at strangers and mean it.

Have you ever stepped into a role that looked like a step down — but taught you something unexpected?

#CrosswalkWisdom #BurnoutRecovery #CareerTransition #IMGCanada #HealthcareBurnout""",
    },
    {
        "id": "j",
        "image": "post-j.png",
        "scheduled_for": "2026-05-15T08:00:00",
        "youtube_title": "Canada needs 44,000 more doctors. Canada rejects 88% of IMGs. Nobody says both.",
        "linkedin": """\
Canada needs 44,000 more doctors.
Canada also rejects 88% of IMGs from residency.

Nobody wants to say both of those things in the same sentence.

The question isn't "why didn't I match?"
It's "why is the system that needs you also designed to keep you out?"

Here's what that contradiction does to a person:

✨ You study harder because you believe performance is the variable.
✨ You apply again because the logic says "keep trying."
✨ You spend another $8,000 because no one tells you the math doesn't change.

And the whole time, the shortage gets worse and the match rate stays the same.

👣 Your application wasn't the problem.
👣 The structural cap on IMG residency spots is the problem.
👣 Knowing that doesn't fix the system — but it might free you from blaming yourself.

I left medicine. Not because I wasn't good enough.
Because I finally read the actual numbers.
That's what Crosswalk Wisdom was built on — making decisions from data, not from hope.

If you've never seen the real math laid out clearly, I put it together in something that takes 5 minutes to read. 📬 Link in the comments.

Did you know these numbers before you started the licensing pathway? What would have changed if you had?

#CrosswalkWisdom #IMGCanada #CaRMS #UnmatchedIMG""",
        "short": """\
Canada needs 44,000 more doctors.
Canada also rejects 88% of IMGs from residency.

Nobody wants to say both of those things in the same sentence.

✨ You study harder because you believe performance is the variable.
✨ You apply again because the logic says "keep trying."
✨ You spend another $8,000 because no one tells you the math doesn't change.

👣 Your application wasn't the problem.
👣 The structural cap on IMG residency spots is the problem.
👣 Knowing that doesn't fix the system — but it might free you from blaming yourself.

Did you know these numbers before you started the licensing pathway?

#CrosswalkWisdom #IMGCanada #CaRMS #UnmatchedIMG #BurnoutRecovery""",
    },
    {
        "id": "k",
        "image": "post-k.png",
        "scheduled_for": "2026-05-16T08:00:00",
        "youtube_title": "The hardest part isn't failing CaRMS. It's calling your parents afterward.",
        "linkedin": """\
The hardest part isn't failing CaRMS.
It's calling your parents afterward.

The question isn't "what do I say?"
It's "why does their disappointment feel like yours to carry too?"

I've heard this story so many times it has its own shape.

✨ You get the email. You read it twice.
✨ You sit with it alone for a few hours before you tell anyone.
✨ Then you call home — and you hear the silence before they find the words.

That silence isn't judgment.
But it feels like it — because you've spent years making your dream theirs too.

👣 The weight you're carrying isn't only your own.
👣 The sacrifice isn't only yours to measure.
👣 And none of that means you have to keep going in a direction that's already cost this much.

I left medicine. My family didn't have a category for it at first.
What we all eventually found — what Crosswalk Wisdom is built on — is that choosing differently isn't giving up. It's choosing yourself, maybe for the first time.

If you're sitting in the weight of this right now, I wrote something gentle for exactly this moment. 5 minutes. 📬 Link in the comments.

Have you ever had to deliver news to people you love that you hadn't finished processing yourself?

#CrosswalkWisdom #IMGCanada #UnmatchedIMG #ImmigrantExperience""",
        "short": """\
The hardest part isn't failing CaRMS.
It's calling your parents afterward.

✨ You get the email. You read it twice.
✨ You sit with it alone for hours before telling anyone.
✨ Then you call home — and hear the silence before they find the words.

That silence isn't judgment.
But it feels like it — because you've spent years making your dream theirs too.

👣 The weight you're carrying isn't only your own.
👣 And none of that means you have to keep going in a direction that's already cost this much.

Have you ever had to deliver news to people you love that you hadn't finished processing yourself?

#CrosswalkWisdom #IMGCanada #UnmatchedIMG #ImmigrantExperience #BurnoutRecovery""",
    },
]


# ── Helpers ─────────────────────────────────────────────────────────────────────

def upload_image(filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    print(f"  Presigning {filename} ({filesize:,} bytes)...")
    r = requests.post(
        f"{BASE}/media/presign",
        headers=HEADERS,
        json={"filename": filename, "contentType": "image/png", "fileSize": filesize},
    )
    r.raise_for_status()
    data = r.json()
    upload_url = data["uploadUrl"]
    public_url = data["publicUrl"]
    print(f"  Uploading to CDN...")
    with open(filepath, "rb") as f:
        put_r = requests.put(upload_url, data=f, headers={"Content-Type": "image/png"})
        put_r.raise_for_status()
    print(f"  Upload OK -> {public_url[:80]}")
    return public_url


def schedule_image_post(post, image_url):
    platforms = [
        {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": post["linkedin"],  "scheduledFor": post["scheduled_for"]},
        {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": post["short"],     "scheduledFor": post["scheduled_for"]},
        {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": post["linkedin"],  "scheduledFor": post["scheduled_for"]},
        {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": post["short"],     "scheduledFor": post["scheduled_for"]},
    ]
    body = {
        "content": post["linkedin"],
        "mediaItems": [{"url": image_url, "type": "image"}],
        "platforms": platforms,
        "scheduledFor": post["scheduled_for"],
        "timezone": TIMEZONE,
    }
    print(f"  Scheduling LI/IG/FB/TT for {post['scheduled_for']} ET...")
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    print(f"  Response {r.status_code}: {r.text[:200]}")
    if r.status_code not in (200, 201):
        return None
    return r.json()


def schedule_youtube_post(post):
    platforms = [
        {
            "platform": "youtube",
            "accountId": YOUTUBE_ID,
            "customContent": post["linkedin"],
            "title": post["youtube_title"],
            "scheduledFor": post["scheduled_for"],
        },
    ]
    body = {
        "content": post["linkedin"],
        "platforms": platforms,
        "scheduledFor": post["scheduled_for"],
        "timezone": TIMEZONE,
    }
    print(f"  Scheduling YouTube text post...")
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    print(f"  Response {r.status_code}: {r.text[:200]}")
    if r.status_code not in (200, 201):
        return None
    return r.json()


def extract_id(resp):
    if not resp:
        return "FAILED"
    return resp.get("id") or resp.get("_id") or str(resp)[:80]


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    print("=== 6 LinkedIn Posts — Schedule May 11–16 2026 ===\n")

    results = []

    for post in POSTS:
        print(f"\n{'='*60}")
        print(f"POST {post['id'].upper()} — {post['scheduled_for']} ET")
        print(f"{'='*60}")

        image_path = os.path.join(IMAGES_DIR, post["image"])
        if not os.path.exists(image_path):
            print(f"  ERROR: Image not found: {image_path}")
            results.append({"id": post["id"], "error": "image not found"})
            continue

        # Upload image
        print("  Step 1: Upload image")
        image_url = upload_image(image_path)

        # Schedule LI/IG/FB/TT
        print("  Step 2: Schedule image post (LI/IG/FB/TT)")
        p1 = schedule_image_post(post, image_url)
        p1_id = extract_id(p1)
        time.sleep(1.5)

        # Schedule YouTube
        print("  Step 3: Schedule YouTube text post")
        p2 = schedule_youtube_post(post)
        p2_id = extract_id(p2)
        time.sleep(1.5)

        results.append({
            "id": post["id"],
            "date": post["scheduled_for"],
            "image_url": image_url,
            "li_ig_fb_tt_id": p1_id,
            "youtube_id": p2_id,
        })

        print(f"  Done. LI/IG/FB/TT: {p1_id} | YT: {p2_id}")

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Post':<6} {'Date':<22} {'LI/IG/FB/TT ID':<28} {'YouTube ID'}")
    print("-" * 90)
    for r in results:
        if "error" in r:
            print(f"  {r['id'].upper():<6} ERROR: {r['error']}")
        else:
            print(f"  {r['id'].upper():<6} {r['date']:<22} {r['li_ig_fb_tt_id']:<28} {r['youtube_id']}")

    print("\nACTION REQUIRED after each post goes live:")
    print("  Post the first comment on LinkedIn with the Fear Audit / Calculator link.")


if __name__ == "__main__":
    main()
