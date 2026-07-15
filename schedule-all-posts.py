#!/usr/bin/env python3
"""
Crosswalk Wisdom — Full Post Scheduling Script
Uploads images/videos to Zernio, re-schedules Wave 2 on all platforms,
schedules Wave 3 with media on LinkedIn + Instagram + Facebook.
"""

import requests
import json
import time
from pathlib import Path

from zernio_key import ZERNIO_API_KEY as API_KEY
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
BASE = "https://zernio.com/api/v1"

MAY = Path("/Users/toto/Downloads/Freepik May")
APR = Path("/Users/toto/Downloads/Freepik April")

ACCT = {
    "facebook":  "6909409a5f6fbb9ef8323074",
    "instagram": "690940655f6fbb9ef8323072",
    "linkedin":  "690940455f6fbb9ef8323070",
}
PLATFORMS = [
    {"platform": "linkedin",  "accountId": ACCT["linkedin"]},
    {"platform": "instagram", "accountId": ACCT["instagram"]},
    {"platform": "facebook",  "accountId": ACCT["facebook"]},
]
FEAR_AUDIT_LINK = "https://fear-audit.vercel.app/"

# ─── File helpers ─────────────────────────────────────────────────────────────

def find(folder: Path, keyword: str) -> Path | None:
    for f in folder.iterdir():
        if keyword in f.name and "(1)" not in f.name:
            return f
    return None

def upload(filepath: Path) -> str:
    """Upload file via Zernio presigned URL, return publicUrl."""
    ext = filepath.suffix.lower()
    ct = "video/mp4" if ext == ".mp4" else "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
    size = filepath.stat().st_size

    # Get presigned URL
    r = requests.post(f"{BASE}/media",
                      headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                      json={"filename": filepath.name, "contentType": ct})
    if r.status_code != 200:
        raise Exception(f"Presigned URL failed {r.status_code}: {r.text[:200]}")
    d = r.json()
    upload_url = d.get("uploadUrl") or d.get("data", {}).get("uploadUrl")
    public_url = d.get("publicUrl") or d.get("data", {}).get("publicUrl")

    # PUT file
    with open(filepath, "rb") as f:
        put = requests.put(upload_url, data=f.read(),
                           headers={"Content-Type": ct, "Content-Length": str(size)})
        if put.status_code not in (200, 201, 204):
            raise Exception(f"Upload failed {put.status_code}: {put.text[:200]}")

    print(f"  ✓ Uploaded {filepath.name[:60]}  →  {public_url[:60]}...")
    return public_url

def post(content: str, scheduled_for: str, media_url: str, is_video: bool = False) -> dict:
    """Create a scheduled post on all platforms."""
    media_type = "video" if is_video else "image"
    body = {
        "content": content,
        "scheduledFor": scheduled_for,
        "timezone": "America/New_York",
        "platforms": PLATFORMS,
        "mediaItems": [{"url": media_url, "type": media_type}],
        "firstComment": FEAR_AUDIT_LINK,
    }
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    if r.status_code not in (200, 201):
        err = r.json() if r.text else {}
        raise Exception(f"Post create failed {r.status_code}: {err.get('error','?')} — {err.get('details','')}")
    return r.json()

def delete_post(post_id: str):
    r = requests.delete(f"{BASE}/posts/{post_id}", headers=HEADERS)
    print(f"  Deleted {post_id}: {r.status_code}")

# ─── Delete old Wave 2 posts (will re-create with media + all platforms) ──────

OLD_WAVE2_IDS = [
    "69c1f8ad22500a8a92c5e465",  # Mar 24 Sunk Cost (may have published — delete anyway, harmless)
    "69c1f8b122500a8a92c5e4a5",  # Mar 26 What Will People Think
    "69c1f8b422500a8a92c5e50e",  # Mar 28 Quitting Is Not Failure
    "69c1f8b722500a8a92c5e546",  # Mar 31 Fear Audit Intro
    "69c1f8ba22500a8a92c5e5b8",  # Apr 2 I Named My Fear
    "69c1f8be2f9ba20fe63c093a",  # Apr 4 The 5 Fears
    "69c1f8c22f9ba20fe63c09c6",  # Apr 7 The 4 Stages
    "69c1f8c5cbc0c8903514f54e",  # Apr 9 Why I Built It
]

print("\n=== Deleting old Wave 2 posts ===")
for pid in OLD_WAVE2_IDS:
    delete_post(pid)
    time.sleep(0.3)

# ─── Wave 2 post content ──────────────────────────────────────────────────────

WAVE2 = [
    {
        "date": "2026-03-24T09:00:00.000Z",
        "file": find(MAY, "empty-hospital-corridor"),
        "content": """I stayed in medicine 2 years longer than I should have.

Not because I loved it. Because I had already given too much to leave.

6 years of medical school. Residency. The sleepless rotations. The money. The time. The youth I spent studying while everyone else was living.

"You've come too far to quit now."

That sentence almost killed me.

The investment becomes the cage. Every year you stay, the cage gets smaller.

Two years of 96-hour shifts. Two years of being screamed at. Two years of falling asleep in hospital stairwells.

The day I finally left, I did not feel like I was throwing anything away.

I felt like I had finally stopped throwing myself away.

The Fear Audit — free, 5 minutes. Link in comments.""",
    },
    {
        "date": "2026-03-26T09:00:00.000Z",
        "file": find(MAY, "person-silhouetted-at-expansive-window"),
        "content": """When I told my mother I was leaving medicine, she cried.

Not because she was sad. Because she was scared for me.

"My son is a doctor." Four words that carry the weight of generations.

My friends did not know what to say. Some stopped calling. Some gave me the look.

Here is what I have learned:

"What will people think" lasts five minutes.

The life you are not living? That stays with you every day.

I chose to disappoint some people so I could stop disappointing myself.

That is not selfish. That is survival.

The Fear Audit — separate real risk from social pressure. Link in comments.""",
    },
    {
        "date": "2026-03-28T09:00:00.000Z",
        "file": find(MAY, "slow-aerial-drift"),
        "content": """Quitting is not the opposite of success.

Staying in something that is destroying you is not strength. It is just endurance with no finish line.

I pushed through 96-hour shifts. I pushed through supervisors who threw instruments in the OR. I pushed through a system that treated sleep as a luxury.

And when I finally stopped pushing, people called it quitting.

I call it the single hardest decision I have ever made.

Staying was autopilot. Leaving was a choice.

And choice — real, terrifying, deliberate choice — is not weakness. It is the first honest thing I did in years.

The Fear Audit — the difference between commitment and captivity. Link in comments.""",
    },
    {
        "date": "2026-03-31T09:00:00.000Z",
        "file": find(MAY, "the-person-walks-slowly-forward"),
        "content": """Most people don't leave bad careers because of logistics.

They leave when they finally name what they're actually afraid of.

"I'm afraid my parents will think I wasted their sacrifice."
"I'm afraid I'm not good enough to do anything else."
"I'm afraid people will stop respecting me."

Those aren't logistics. Those are fears. And unnamed fears have all the power.

The Fear Audit. A 5-minute exercise.

Write "I'm afraid that..." 5 to 7 times. Don't filter.
Circle the one that hits hardest.
Then ask it: "Is this true, or is this a story I'm telling myself?"

Fog with a name is something you can walk through.

Free. Link in comments.""",
    },
    {
        "date": "2026-04-02T09:00:00.000Z",
        "file": find(MAY, "slow-pushin-toward-the-paper"),
        "content": """I named my fear out loud for the first time on a Tuesday morning.

No app. No therapist. Just a pen and a question: "What, specifically, am I afraid of?"

"I am afraid that without the title of doctor, my parents will stop being proud of me."

When fear is unnamed, it feels like the truth.
When it is named, it feels like a sentence you can examine.

Is that actually true? Has my father ever said his love was conditional on my job title?

No. He said it was conditional on my being kind.

Fear named is fear that can be questioned.
Fear unnamed is fear that cannot be beaten.

The Fear Audit. Free. 5 minutes. Link in comments.""",
    },
    {
        "date": "2026-04-04T09:00:00.000Z",
        "file": find(MAY, "five-closed-wooden-doors"),
        "content": """"I can't leave."

There are always 5 fears inside that sentence.

FINANCIAL FEAR — "I won't be able to pay my bills." Real. Deserves a real plan. Almost never the actual blocker. Most people have never run the actual numbers.

IDENTITY FEAR — "Who am I without this title?" The silent one. The fear the career is you.

JUDGMENT FEAR — "What will people think?" We make enormous life decisions to avoid conversations with people we barely like.

FAILURE FEAR — "What if I try and it doesn't work?" Disguised as realism. Realism would also ask: "What if it does?"

GRIEF FEAR — "What if I leave and feel like I wasted everything?" This kept me in medicine two extra years.

Each fear needs a different conversation. The Fear Audit separates them. Free. Link in comments.""",
    },
    {
        "date": "2026-04-07T09:00:00.000Z",
        "file": find(MAY, "camera-slowly-glides-forward"),
        "content": """Not everyone who's stuck looks the same.

4 stages. Different fears. Different next step.

START — You know something is wrong but can't name it yet. Fear feels like background noise. You keep saying: "I just need to push through."

STOP — You know exactly what's wrong. You've thought about leaving until it's its own exhausting thing. But you can't move.

ELDER — You've been here a long time. Fear has become habit. It doesn't feel like fear anymore. It just feels like "how work is."

HUMAN — Something broke recently. A moment. A loss. A conversation. You're not asking "Should I leave?" You're asking "How?"

Every stage has a path forward.

The Fear Audit meets you where you are. Free. 5 minutes. Link in comments.""",
    },
    {
        "date": "2026-04-09T09:00:00.000Z",
        "file": find(MAY, "the-hand-writes-slowly"),
        "content": """I did not build the Fear Audit because I am a coach.

I built it because I needed it and it didn't exist.

When I was trying to leave medicine, I searched for something that would help me figure out what I was actually afraid of.

I found: Career counselors who wanted to talk about skills assessments. Books that assumed I already knew what I wanted. Nobody who helped with my specific problem.

I knew what I wanted. I wanted out. I didn't know what was stopping me. That is a different problem.

Fear of career change is not one thing. It is a cluster of distinct fears that feel like one fog. Until you separate them, every move feels impossible.

I eventually built the separation exercise myself. On a piece of paper. At a kitchen table. With a pen.

That is all it does. That is all I needed. Free. 5 minutes. Link in comments.""",
    },
]

# ─── Wave 3 post content + files ─────────────────────────────────────────────

WAVE3 = [
    {
        "date": "2026-04-14T09:00:00.000Z",
        "file": find(MAY, "slow-pan-across-the-empty-psychiatrist"),
        "content": """A psychiatrist once told me I was making the biggest mistake of my life.

I was sitting in his office explaining that I was leaving medicine. He leaned back in his chair and said, slowly, "You have no idea what you're throwing away."

He was right about one thing: I had no idea.

I had no idea that I would sleep through the night for the first time in four years.
I had no idea that I would remember what it felt like to have a personality.
I had no idea that I would stop looking forward to getting sick because it was the only legitimate reason to stay home.

He was trying to protect me. I understand that now. What he didn't understand was what he was protecting me for.

A title. A salary. A identity built on other people's expectations.

I didn't need protection from leaving. I needed permission. And I gave it to myself.

The Fear Audit. What are you actually afraid of? Link in comments.""",
    },
    {
        "date": "2026-04-16T09:00:00.000Z",
        "file": find(MAY, "the-man-holds-the-phone-to-his-ear"),
        "content": """The phone call I remember most wasn't the one announcing my acceptance to medical school.

It was the one I made the day I decided to leave.

I called my father. I told him I was done. I was ready for him to be disappointed. I was ready for the silence, the careful words, the gentle redirection back to "what you've worked for."

Instead he said: "I wondered when you were going to figure that out."

I sat on the kitchen floor for ten minutes.

Not because I was sad. Because I realized I had spent years afraid of a conversation that my father had been waiting to have.

Here is the thing about the people who love you: they often know before you do.

They've seen the exhaustion. They've watched you dim. They've been holding their breath.

Your fear of their reaction is usually bigger than their actual reaction.

The Fear Audit. Face the fear before it faces you. Link in comments.""",
    },
    {
        "date": "2026-04-18T09:00:00.000Z",
        "file": find(MAY, "morning-light-slowly-moves-across-the-yellow-vest"),
        "content": """I had a yellow vest.

That's what I wore as a crossing guard. Bright safety yellow. The kind of vest that says "I am here. See me. I am not hiding."

After years of a white coat — which, if I'm honest, was its own kind of armor — the yellow vest felt absurd.

And then it felt honest.

The white coat carried authority. Distance. A performance of competence that had nothing to do with how I actually felt inside.

The yellow vest just said: I am a person. Doing a job. In public. Unashamed.

I had more meaningful conversations in that yellow vest than in all my years of practice.

Because people didn't see a doctor. They saw a human being.

Sometimes you have to take off the armor to find out what's underneath it.

The Fear Audit. What identity are you wearing that isn't yours? Link in comments.""",
    },
    {
        "date": "2026-04-21T09:00:00.000Z",
        "file": find(MAY, "camera-holds-still-on-the-empty-kitchen"),
        "content": """The loneliest six months of my life were the six months after I left medicine.

Not because I had no one. I had people. But I had spent 15 years defining myself by a role, and suddenly the role was gone.

I would wake up and not know what to call myself.
I would run into former colleagues and change the subject.
I would fill out forms and freeze at "occupation."

Nobody tells you about the identity hangover.

You prepare for the grief of leaving. You don't prepare for the grief of not knowing who you are on the other side.

That emptiness was the most important thing that ever happened to me.

Because it forced me to answer a question I had been avoiding for 15 years:

Who am I when I'm not performing?

The answer took time. It still does.

But I am more sure of that answer today — in a yellow vest on a crosswalk — than I ever was in a white coat.

The Fear Audit. Start naming what's underneath. Link in comments.""",
    },
    {
        "date": "2026-04-23T09:00:00.000Z",
        "file": find(MAY, "camera-slowly-pushes-in-on-the-person-sitting-on-the-bed"),
        "content": """It's 3am. You're not asleep.

You're running the same questions you've run a hundred times.

"What if I leave and it doesn't work out?"
"What if I stay and nothing ever changes?"
"What if I'm wrong about all of it?"
"What if the version of me that could be happy doesn't actually exist?"

Those questions aren't problems to solve. They're fears wearing the costume of logic.

3am thinking isn't thinking. It's your nervous system trying to protect you from a threat it doesn't understand.

The threat isn't leaving. The threat is change. The threat is the unknown.

And your brain at 3am is very bad at distinguishing between "unfamiliar" and "dangerous."

Here is what I have learned: You cannot think your way out of a fear you haven't named.

Write it down. At noon. With coffee. On paper.

Not "I'm afraid to leave." That's too big. Too vague.

"I'm afraid that if I leave, I will have wasted everything I sacrificed to get here."

That's a fear you can examine. That's a fear you can talk back to.

The Fear Audit. What are you actually afraid of? Link in comments.""",
    },
    {
        "date": "2026-04-25T09:00:00.000Z",
        "file": find(MAY, "camera-slowly-dollies"),
        "content": """When I told my colleagues I was leaving medicine, some of them took it personally.

Not all of them. But some.

As if my leaving were a judgment on their staying.

I understand now what I didn't understand then: when you leave something others are trapped in, it can feel like an accusation.

You didn't say "I'm leaving." You said, without words, "Leaving is possible."

And that is terrifying if you've built an entire identity around the belief that staying is the only option.

The people who were angriest at my decision were not angry at me. They were angry at the door I had just proved was unlocked.

I am not telling you this so you'll feel righteous.

I'm telling you this so you'll be gentle. With them. And with yourself.

Their reaction is not about you. It's about what your courage reveals to them about their own fear.

The Fear Audit. What would your decision reveal to the people around you? Link in comments.""",
    },
    {
        "date": "2026-04-28T09:00:00.000Z",
        "file": find(MAY, "camera-holds-on-the-single-footprint"),
        "content": """You don't need a plan. You need a first step.

I spent two years waiting until I had a plan before I would let myself leave medicine. A detailed, airtight, everyone-is-taken-care-of, nothing-can-go-wrong plan.

That plan never came.

What came instead was a single moment of clarity: I cannot do one more shift like this.

That was not a plan. That was a first step.

And the first step was enough to get me to the second step.

Which got me to the third.

Which eventually got me to a crosswalk, in a yellow vest, watching the sun rise over a street I had never stood on before, feeling more like myself than I had in fifteen years.

You will not be able to see the whole crossing from where you're standing. That is not how crossings work.

You will only see the next stripe of paint. And then the one after that. And then the one after that.

You don't need the full view. You need to take one step off the curb.

The Fear Audit. What's your first step? Link in comments.""",
    },
    {
        "date": "2026-04-30T09:00:00.000Z",
        "file": find(MAY, "children-walk-across-the-crosswalk"),
        "content": """"What do you do?"

Four words that used to stop me cold.

When I was a doctor, the answer was easy. "I'm a physician." People nodded. They understood. They knew exactly where to file me.

When I left, the answer became impossible.

"I'm... between things." "I'm transitioning." "I used to be a doctor."

The past tense was the worst. "I used to be."

Here's what I've come to understand: "What do you do?" is a lazy question. And "I'm a doctor" is a lazy answer.

Because neither one touches what's actually true.

What I do is: I help people cross.

I help nurses who can't breathe figure out what's actually stopping them. I help physicians who've forgotten who they are start to remember. I stand at the intersection between who someone was told to be and who they actually are, and I hold up the stop sign long enough for them to decide to walk.

That is what I do. In the yellow vest and in this work.

The question was never about my job. It was about my purpose.

The Fear Audit. Find out what's actually stopping you. Link in comments.""",
    },
    {
        "date": "2026-05-02T09:00:00.000Z",
        "file": find(MAY, "camera-slowly-pushes-in-on-the-open-book"),
        "content": """I've been a physician. I've been a crossing guard. I've been lost.

I've learned that fear doesn't go away when you make the right choice. It goes away when you make AN honest one.

The Courage to Choose is the guide I wish I had when I was sitting at that kitchen table at 3am, paralyzed, convinced I was the only person who had ever felt this stuck.

It is three chapters:

Chapter 1: Naming the Fear. (The Fear Audit gives you the question. This chapter gives you the language.)

Chapter 2: Reframing the Story. Shifting from "I'm trapped" to "I'm choosing." Every word matters.

Chapter 3: Taking the First Step. Not the full plan. Not the five-year roadmap. The one honest thing you can do this week.

Rooted in Adlerian psychology, Stoic philosophy, and Viktor Frankl's logotherapy. Written by someone who has lived every page of it.

$27. Because transformation should not require a second mortgage.

Available now. Link in comments.""",
    },
]

# ─── Process Wave 2 ───────────────────────────────────────────────────────────

print("\n=== Processing Wave 2 (8 posts) ===")
for i, p in enumerate(WAVE2, 1):
    f = p["file"]
    if f is None:
        print(f"  ⚠️  Post {i}: no file found, skipping")
        continue
    print(f"\n[{i}/8] {f.name[:60]}...")
    try:
        url = upload(f)
        is_video = f.suffix.lower() == ".mp4"
        result = post(p["content"], p["date"], url, is_video)
        pid = result.get("post", {}).get("_id") or result.get("_id", "?")
        print(f"  ✓ Scheduled post ID: {pid}  ({p['date'][:10]})")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    time.sleep(1)

# ─── Process Wave 3 ───────────────────────────────────────────────────────────

print("\n=== Processing Wave 3 (9 posts) ===")
for i, p in enumerate(WAVE3, 1):
    f = p["file"]
    if f is None:
        print(f"  ⚠️  Post {i}: no file found, skipping")
        continue
    print(f"\n[{i}/9] {f.name[:60]}...")
    try:
        url = upload(f)
        is_video = f.suffix.lower() == ".mp4"
        result = post(p["content"], p["date"], url, is_video)
        pid = result.get("post", {}).get("_id") or result.get("_id", "?")
        print(f"  ✓ Scheduled post ID: {pid}  ({p['date'][:10]})")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    time.sleep(1)

print("\n✅ Done. Check zernio.com for all scheduled posts.")
