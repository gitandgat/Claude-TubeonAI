"""
Recreate the 15 deleted overlay posts + 1 mar-28 video post
with all 5 platforms: LinkedIn, Instagram, Facebook, TikTok, YouTube.

Deleted posts had only LinkedIn/Instagram/Facebook (or LinkedIn/Instagram/Facebook/TikTok).
This re-uploads each video and creates a 5-platform post.
"""
import requests
import time
from pathlib import Path

BASE    = "https://zernio.com/api/v1"
API_KEY = "***REMOVED-ZERNIO-KEY***"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

OVERLAYS_DIR = Path("/Users/toto/Claude TubeonAI/crosswalk-remotion/out/overlays")
APRIL_DIR    = Path("/Users/toto/Claude TubeonAI/crosswalk-remotion/out/april")

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
YOUTUBE_ID   = "690940d35f6fbb9ef8323077"

DM_CTA = "\n\nComment FEAR below and I'll DM you the link."
YT_TAGS = "\n\n#Shorts #CrosswalkWisdom #HealthcareBurnout #NurseBurnout #CareerTransition"


def first_line(text, max_chars=97):
    for line in text.split("\n"):
        line = line.strip().strip('"')
        if line:
            return (line[:max_chars] + "...") if len(line) > max_chars else line
    return "Crosswalk Wisdom"


def upload(filepath: Path) -> str:
    r = requests.post(
        f"{BASE}/media",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"filename": filepath.name, "contentType": "video/mp4"},
    )
    r.raise_for_status()
    d = r.json()
    upload_url = d["uploadUrl"]
    public_url = d["publicUrl"]
    size = filepath.stat().st_size
    with open(filepath, "rb") as f:
        put = requests.put(
            upload_url, data=f.read(),
            headers={"Content-Type": "video/mp4", "Content-Length": str(size)},
        )
        if put.status_code not in (200, 201, 204):
            raise Exception(f"PUT failed {put.status_code}: {put.text[:200]}")
    print(f"  ✓ Uploaded {filepath.name}")
    return public_url


def create_post(content: str, scheduled_for: str, video_url: str) -> str:
    full_content = content + DM_CTA
    yt_content   = full_content + YT_TAGS
    yt_title     = first_line(content)

    platforms = [
        {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": full_content, "scheduledFor": scheduled_for},
        {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": full_content, "scheduledFor": scheduled_for},
        {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": full_content, "scheduledFor": scheduled_for},
        {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": full_content, "scheduledFor": scheduled_for},
        {"platform": "youtube",   "accountId": YOUTUBE_ID,   "customContent": yt_content,   "scheduledFor": scheduled_for,
         "title": yt_title},
    ]
    body = {
        "content": full_content,
        "scheduledFor": scheduled_for,
        "timezone": "America/New_York",
        "platforms": platforms,
        "mediaItems": [{"url": video_url, "type": "video"}],
    }
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    if r.status_code not in (200, 201):
        raise Exception(f"Create failed {r.status_code}: {r.text[:400]}")
    return r.json().get("post", {}).get("_id", "?")


# ── Post definitions ──────────────────────────────────────────────────────────

POSTS = [
    {
        "date": "2026-03-28T09:00:00.000Z",
        "file": OVERLAYS_DIR / "03-quitting.mp4",
        "content": """Quitting is not the opposite of success.

Staying in something that is destroying you is not strength. It is just endurance with no finish line.

I pushed through 96-hour shifts. I pushed through supervisors who threw instruments in the OR. I pushed through a system that treated sleep as a luxury.

And when I finally stopped pushing, people called it quitting.

I call it the single hardest decision I have ever made.

Staying was autopilot. Leaving was a choice.

And choice — real, terrifying, deliberate choice — is not weakness. It is the first honest thing I did in years.

Take the free Fear Audit — understand the difference between commitment and captivity.""",
    },
    {
        "date": "2026-03-31T09:00:00.000Z",
        "file": OVERLAYS_DIR / "04-fear-audit-intro.mp4",
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

Take it free — 5 minutes.""",
    },
    {
        "date": "2026-04-02T09:00:00.000Z",
        "file": OVERLAYS_DIR / "05-named-fear.mp4",
        "content": """I named my fear out loud for the first time on a Tuesday morning.

No app. No therapist. Just a pen and a question: "What, specifically, am I afraid of?"

"I am afraid that without the title of doctor, my parents will stop being proud of me."

When fear is unnamed, it feels like the truth.
When it is named, it feels like a sentence you can examine.

Is that actually true? Has my father ever said his love was conditional on my job title?

No. He said it was conditional on my being kind.

Fear named is fear that can be questioned.
Fear unnamed is fear that cannot be beaten.

Take the free Fear Audit — 5 minutes.""",
    },
    {
        "date": "2026-04-04T09:00:00.000Z",
        "file": OVERLAYS_DIR / "06-five-fears.mp4",
        "content": """"I can't leave."

There are always 5 fears inside that sentence.

FINANCIAL FEAR — "I won't be able to pay my bills." Real. Deserves a real plan. Almost never the actual blocker.

IDENTITY FEAR — "Who am I without this title?" The silent one. The fear the career is you.

JUDGMENT FEAR — "What will people think?" We make enormous life decisions to avoid conversations with people we barely like.

FAILURE FEAR — "What if I try and it doesn't work?" Disguised as realism. Realism would also ask: "What if it does?"

GRIEF FEAR — "What if I leave and feel like I wasted everything?" This kept me in medicine two extra years.

Each fear needs a different conversation. Take the free Fear Audit — it separates them.""",
    },
    {
        "date": "2026-04-07T09:00:00.000Z",
        "file": OVERLAYS_DIR / "07-four-stages.mp4",
        "content": """Not everyone who's stuck looks the same.

4 stages. Different fears. Different next step.

START — You know something is wrong but can't name it yet. Fear feels like background noise. You keep saying: "I just need to push through."

STOP — You know exactly what's wrong. You've thought about leaving until it's its own exhausting thing. But you can't move.

ELDER — You've been here a long time. Fear has become habit. It doesn't feel like fear anymore. It just feels like "how work is."

HUMAN — Something broke recently. A moment. A loss. A conversation. You're asking "How?" not "Should I?"

Every stage has a path forward.

Take the free Fear Audit — it meets you where you are.""",
    },
    {
        "date": "2026-04-09T09:00:00.000Z",
        "file": OVERLAYS_DIR / "09-why-i-built-it.mp4",
        "content": """I did not build the Fear Audit because I am a coach.

I built it because I needed it and it didn't exist.

I knew what I wanted. I wanted out. I didn't know what was stopping me. That is a different problem.

Fear of career change is not one thing. It is a cluster of distinct fears that feel like one fog. Until you separate them, every move feels impossible.

I eventually built the separation exercise myself. On a piece of paper. At a kitchen table. With a pen.

That is all it does. That is all I needed.

Free. 5 minutes. Take it.""",
    },
    {
        "date": "2026-04-14T09:00:00.000Z",
        "file": OVERLAYS_DIR / "10-psychiatrist.mp4",
        "content": """A psychiatrist once told me I was making the biggest mistake of my life.

"You have no idea what you're throwing away."

He was right about one thing: I had no idea.

I had no idea that I would sleep through the night for the first time in four years.
I had no idea that I would remember what it felt like to have a personality.
I had no idea that I would stop looking forward to getting sick because it was the only legitimate reason to stay home.

He was protecting me. For a title. A salary. An identity built on expectations.

I didn't need protection from leaving. I needed permission.

And I gave it to myself.

Take the free Fear Audit — what are you actually afraid of?""",
    },
    {
        "date": "2026-04-16T09:00:00.000Z",
        "file": OVERLAYS_DIR / "11-phone-call.mp4",
        "content": """The phone call I remember most wasn't the one announcing my acceptance to medical school.

It was the one I made the day I decided to leave.

I called my father. I was ready for him to be disappointed.

Instead he said: "I wondered when you were going to figure that out."

I sat on the kitchen floor for ten minutes.

Not because I was sad. Because I realized I had spent years afraid of a conversation that my father had been waiting to have.

The people who love you often know before you do.

Your fear of their reaction is usually bigger than their actual reaction.

Take the free Fear Audit — face the fear before it faces you.""",
    },
    {
        "date": "2026-04-18T09:00:00.000Z",
        "file": OVERLAYS_DIR / "12-yellow-vest.mp4",
        "content": """I had a yellow vest.

After years of a white coat — which was its own kind of armor — the yellow vest felt absurd.

And then it felt honest.

The white coat carried authority. Distance. A performance of competence.

The yellow vest just said: I am a person. Doing a job. In public. Unashamed.

I had more meaningful conversations in that yellow vest than in all my years of practice.

Because people didn't see a doctor. They saw a human being.

Sometimes you have to take off the armor to find out what's underneath it.

Take the free Fear Audit — what identity are you wearing that isn't yours?""",
    },
    {
        "date": "2026-04-21T09:00:00.000Z",
        "file": OVERLAYS_DIR / "13-loneliest.mp4",
        "content": """The loneliest six months of my life were the six months after I left medicine.

I would wake up and not know what to call myself.
I would run into former colleagues and change the subject.
I would fill out forms and freeze at "occupation."

Nobody tells you about the identity hangover.

You prepare for the grief of leaving. You don't prepare for the grief of not knowing who you are on the other side.

That emptiness was the most important thing that ever happened to me.

Because it forced me to answer a question I had been avoiding for 15 years:

Who am I when I'm not performing?

Take the free Fear Audit — start naming what's underneath.""",
    },
    {
        "date": "2026-04-23T09:00:00.000Z",
        "file": OVERLAYS_DIR / "14-3am.mp4",
        "content": """It's 3am. You're not asleep.

You're running the same questions you've run a hundred times.

"What if I leave and it doesn't work out?"
"What if I stay and nothing ever changes?"
"What if the version of me that could be happy doesn't actually exist?"

Those questions aren't problems to solve. They're fears wearing the costume of logic.

3am thinking isn't thinking. It's your nervous system trying to protect you from a threat it doesn't understand.

You cannot think your way out of a fear you haven't named.

Write it down. At noon. With coffee. On paper.

"I'm afraid that if I leave, I will have wasted everything I sacrificed to get here."

That's a fear you can examine. That's a fear you can talk back to.

Take the free Fear Audit — what are you actually afraid of?""",
    },
    {
        "date": "2026-04-25T09:00:00.000Z",
        "file": OVERLAYS_DIR / "15-take-it-personally.mp4",
        "content": """When I told my colleagues I was leaving medicine, some of them took it personally.

As if my leaving were a judgment on their staying.

I understand now what I didn't understand then: when you leave something others are trapped in, it can feel like an accusation.

You didn't say "I'm leaving." You said, without words, "Leaving is possible."

And that is terrifying if you've built an entire identity around the belief that staying is the only option.

The people who were angriest at my decision were not angry at me. They were angry at the door I had just proved was unlocked.

Their reaction is not about you. It's about what your courage reveals to them about their own fear.

Take the free Fear Audit — what would your decision reveal?""",
    },
    {
        "date": "2026-04-28T09:00:00.000Z",
        "file": OVERLAYS_DIR / "16-first-step.mp4",
        "content": """You don't need a plan. You need a first step.

I spent two years waiting until I had a plan before I would let myself leave medicine. A detailed, airtight, nothing-can-go-wrong plan.

That plan never came.

What came instead was a single moment of clarity: I cannot do one more shift like this.

That was not a plan. That was a first step.

And the first step was enough to get me to the second step.

You will not be able to see the whole crossing from where you're standing. That is not how crossings work.

You will only see the next stripe of paint. And then the one after that.

You don't need the full view. You need to take one step off the curb.

Take the free Fear Audit — what's your first step?""",
    },
    {
        "date": "2026-04-30T09:00:00.000Z",
        "file": OVERLAYS_DIR / "17-what-do-you-do.mp4",
        "content": """"What do you do?"

When I was a doctor, the answer was easy. People nodded. They knew exactly where to file me.

When I left, the answer became impossible.

"I'm... between things." "I'm transitioning." "I used to be a doctor."

The past tense was the worst.

Here's what I've come to understand: "What do you do?" is a lazy question. And "I'm a doctor" is a lazy answer.

Because neither one touches what's actually true.

What I do is: I help people cross.

I help nurses who can't breathe figure out what's actually stopping them. I help physicians who've forgotten who they are start to remember.

The question was never about my job. It was about my purpose.

Take the free Fear Audit — find out what's actually stopping you.""",
    },
    {
        "date": "2026-05-02T09:00:00.000Z",
        "file": OVERLAYS_DIR / "18-courage.mp4",
        "content": """I've been a physician. I've been a crossing guard. I've been lost.

I've learned that fear doesn't go away when you make the right choice. It goes away when you make AN honest one.

The Courage to Choose is the guide I wish I had when I was sitting at that kitchen table at 3am, paralyzed.

Three chapters:

Chapter 1: Naming the Fear. (The Fear Audit gives you the question. This chapter gives you the language.)

Chapter 2: Reframing the Story. Shifting from "I'm trapped" to "I'm choosing."

Chapter 3: Taking the First Step. Not the full plan. The one honest thing you can do this week.

Rooted in Adlerian psychology, Stoic philosophy, and Viktor Frankl's logotherapy. Written by someone who has lived every page of it.

$27. Because transformation should not require a second mortgage.""",
    },
]


def main():
    total = len(POSTS)
    print(f"Recreating {total} posts across 5 platforms (LI / IG / FB / TT / YT)...\n")
    success = 0
    failed  = 0

    for i, p in enumerate(POSTS, 1):
        filepath = p["file"]
        date     = p["date"]
        content  = p["content"]
        print(f"[{i}/{total}] {date[:10]}  {filepath.name}")

        if not filepath.exists():
            print(f"  ✗ File not found: {filepath}\n")
            failed += 1
            continue

        try:
            video_url = upload(filepath)
            post_id   = create_post(content, date, video_url)
            print(f"  ✓ Created → {post_id}\n")
            success += 1
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
            failed += 1

        time.sleep(1.5)

    print(f"\nDone. Success: {success}  Failed: {failed}")


if __name__ == "__main__":
    main()
