"""
Definitive April fix: re-upload local videos + create one clean post per date.
- Hardcoded content from schedule-all-posts.py (no Zernio API lookups)
- Apr-03 and Apr-13 use new copy written from hook/sub
- Deletes any remaining duplicates for Apr-03 and Apr-13 before creating
"""
import os
import requests
import time

BASE    = "https://zernio.com/api/v1"
API_KEY = "***REMOVED-ZERNIO-KEY***"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
YOUTUBE_ID   = "690940d35f6fbb9ef8323077"
TIMEZONE     = "America/New_York"
VIDEOS_DIR   = "/Users/toto/Claude TubeonAI/crosswalk-remotion/out/april"
FEAR_AUDIT   = "https://fear-audit.vercel.app"

POSTS = [
    {
        "date": "2026-04-02",
        "slug": "apr-02",
        "time": "2026-04-02T13:00:00",
        "yt_title": "You didn't fail nursing. Nursing failed you.",
        "linkedin": """I named my fear out loud for the first time on a Tuesday morning.

No app. No therapist. Just a pen and a question: "What, specifically, am I afraid of?"

"I am afraid that without the title of doctor, my parents will stop being proud of me."

When fear is unnamed, it feels like the truth.
When it is named, it feels like a sentence you can examine.

Is that actually true? Has my father ever said his love was conditional on my job title?

No. He said it was conditional on my being kind.

Fear named is fear that can be questioned.
Fear unnamed is fear that cannot be beaten.

The Fear Audit. Free. 5 minutes. Link in first comment.

#HealthcareBurnout #PhysicianBurnout #NurseBurnout #CrosswalkWisdom #CareerTransition #IdentityShift""",
    },
    {
        "date": "2026-04-03",
        "slug": "apr-03",
        "time": "2026-04-03T13:00:00",
        "yt_title": "Healthcare burnout comes down to 3 fears. Here they are.",
        "linkedin": """It always comes down to three fears.

I've spoken with hundreds of burned-out healthcare professionals.

The story changes. The specialty changes. The geography changes.

The fear doesn't.

IDENTITY LOSS — "If I'm not a nurse, who am I?" This is the one nobody names. The most common. The most paralyzing. You've spent 15 years becoming something. The idea of un-becoming it feels like death.

FEAR OF JUDGMENT — "What will my colleagues think? What will my patients think? What will I tell my family?" We make enormous life decisions to avoid conversations with people we barely like.

FINANCIAL INSECURITY — "I can't afford to leave." The acceptable fear. The one we lead with because it sounds reasonable. Almost never the real blocker. Most people have never actually run the numbers.

Each fear needs a completely different conversation.

Naming yours is the first act of courage.

The Fear Audit identifies which fear is running your life. Free. 2 minutes. Link in first comment.

#HealthcareBurnout #NurseBurnout #PhysicianBurnout #CrosswalkWisdom #IdentityShift #CareerTransition""",
    },
    {
        "date": "2026-04-04",
        "slug": "apr-04",
        "time": "2026-04-04T13:00:00",
        "yt_title": "Every morning at the crosswalk, I watched people hesitate.",
        "linkedin": """"I can't leave."

There are always 5 fears inside that sentence.

FINANCIAL FEAR — "I won't be able to pay my bills." Real. Deserves a real plan. Almost never the actual blocker. Most people have never run the actual numbers.

IDENTITY FEAR — "Who am I without this title?" The silent one. The fear the career is you.

JUDGMENT FEAR — "What will people think?" We make enormous life decisions to avoid conversations with people we barely like.

FAILURE FEAR — "What if I try and it doesn't work?" Disguised as realism. Realism would also ask: "What if it does?"

GRIEF FEAR — "What if I leave and feel like I wasted everything?" This kept me in medicine two extra years.

Each fear needs a different conversation. The Fear Audit separates them. Free. Link in first comment.

#HealthcareBurnout #NurseBurnout #PhysicianBurnout #CrosswalkWisdom #CareerTransition #BurnoutRecovery""",
    },
    {
        "date": "2026-04-07",
        "slug": "apr-07",
        "time": "2026-04-07T13:00:00",
        "yt_title": "Fill in the blank: I became a healthcare worker because ___.",
        "linkedin": """Not everyone who's stuck looks the same.

4 stages. Different fears. Different next step.

START — You know something is wrong but can't name it yet. Fear feels like background noise. You keep saying: "I just need to push through."

STOP — You know exactly what's wrong. You've thought about leaving until it's its own exhausting thing. But you can't move.

ELDER — You've been here a long time. Fear has become habit. It doesn't feel like fear anymore. It just feels like "how work is."

HUMAN — Something broke recently. A moment. A loss. A conversation. You're not asking "Should I leave?" You're asking "How?"

Every stage has a path forward.

The Fear Audit meets you where you are. Free. 5 minutes. Link in first comment.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #PhysicianBurnout #CareerTransition #IdentityShift""",
    },
    {
        "date": "2026-04-09",
        "slug": "apr-09",
        "time": "2026-04-09T13:00:00",
        "yt_title": "5 things I'd tell the version of me in the hospital parking lot.",
        "linkedin": """I did not build the Fear Audit because I am a coach.

I built it because I needed it and it didn't exist.

When I was trying to leave medicine, I searched for something that would help me figure out what I was actually afraid of.

I found: Career counselors who wanted to talk about skills assessments. Books that assumed I already knew what I wanted. Nobody who helped with my specific problem.

I knew what I wanted. I wanted out. I didn't know what was stopping me. That is a different problem.

Fear of career change is not one thing. It is a cluster of distinct fears that feel like one fog. Until you separate them, every move feels impossible.

I eventually built the separation exercise myself. On a piece of paper. At a kitchen table. With a pen.

That is all it does. That is all I needed. Free. 5 minutes. Link in first comment.

#HealthcareBurnout #PhysicianBurnout #NurseBurnout #CrosswalkWisdom #CareerTransition #IdentityShift""",
    },
    {
        "date": "2026-04-13",
        "slug": "apr-13",
        "time": "2026-04-13T13:00:00",
        "yt_title": "'I have no skills outside nursing.' AI proves that wrong in 60s.",
        "linkedin": """"I don't have any skills outside of nursing."

I hear this every single week.

And every week, AI proves it wrong in about 60 seconds.

Here's what I actually do: I ask someone to paste their resume — or just describe their last five years — into Claude or ChatGPT. Then I ask: "What skills does this person have that would transfer outside of healthcare?"

The list is always longer than they expected.

Crisis communication. Team leadership under pressure. Patient advocacy. Systems thinking. Emotional intelligence. Triage and prioritization. Documentation and compliance. Teaching and mentorship.

These are not nursing skills. These are human skills that nurses happen to be exceptional at.

The cage is not your actual skill set. The cage is the story you tell yourself about your skill set.

You are not less qualified for life outside healthcare. You are differently qualified. Massively qualified.

The Fear Audit. What fear is hiding behind "I don't have the skills"? Link in first comment.

#NurseBurnout #HealthcareBurnout #CareerTransition #CrosswalkWisdom #PhysicianBurnout #IdentityShift""",
    },
    {
        "date": "2026-04-14",
        "slug": "apr-14",
        "time": "2026-04-14T13:00:00",
        "yt_title": "The real reason financial fear keeps healthcare workers stuck.",
        "linkedin": """A psychiatrist once told me I was making the biggest mistake of my life.

I was sitting in his office explaining that I was leaving medicine. He leaned back in his chair and said, slowly, "You have no idea what you're throwing away."

He was right about one thing: I had no idea.

I had no idea that I would sleep through the night for the first time in four years.
I had no idea that I would remember what it felt like to have a personality.
I had no idea that I would stop looking forward to getting sick because it was the only legitimate reason to stay home.

He was trying to protect me. I understand that now. What he didn't understand was what he was protecting me for.

A title. A salary. An identity built on other people's expectations.

I didn't need protection from leaving. I needed permission. And I gave it to myself.

The Fear Audit. What are you actually afraid of? Link in first comment.

#HealthcareBurnout #PhysicianBurnout #NurseBurnout #CrosswalkWisdom #LeavingMedicine #CareerTransition""",
    },
    {
        "date": "2026-04-16",
        "slug": "apr-16",
        "time": "2026-04-16T13:00:00",
        "yt_title": "Leaving isn't quitting. It's choosing. Let's reclaim that word.",
        "linkedin": """The phone call I remember most wasn't the one announcing my acceptance to medical school.

It was the one I made the day I decided to leave.

I called my father. I told him I was done. I was ready for him to be disappointed. I was ready for the silence, the careful words, the gentle redirection back to "what you've worked for."

Instead he said: "I wondered when you were going to figure that out."

I sat on the kitchen floor for ten minutes.

Not because I was sad. Because I realized I had spent years afraid of a conversation that my father had been waiting to have.

Here is the thing about the people who love you: they often know before you do.

They've seen the exhaustion. They've watched you dim. They've been holding their breath.

Your fear of their reaction is usually bigger than their actual reaction.

The Fear Audit. Face the fear before it faces you. Link in first comment.

#HealthcareBurnout #PhysicianBurnout #NurseBurnout #CrosswalkWisdom #CareerTransition #IdentityShift""",
    },
    {
        "date": "2026-04-18",
        "slug": "apr-18",
        "time": "2026-04-18T13:00:00",
        "yt_title": "Viktor Frankl was a physician first. What that means for burnout.",
        "linkedin": """I had a yellow vest.

That's what I wore as a crossing guard. Bright safety yellow. The kind of vest that says "I am here. See me. I am not hiding."

After years of a white coat — which, if I'm honest, was its own kind of armor — the yellow vest felt absurd.

And then it felt honest.

The white coat carried authority. Distance. A performance of competence that had nothing to do with how I actually felt inside.

The yellow vest just said: I am a person. Doing a job. In public. Unashamed.

I had more meaningful conversations in that yellow vest than in all my years of practice.

Because people didn't see a doctor. They saw a human being.

Sometimes you have to take off the armor to find out what's underneath it.

The Fear Audit. What identity are you wearing that isn't yours? Link in first comment.

#HealthcareBurnout #PhysicianBurnout #NurseBurnout #CrosswalkWisdom #IdentityShift #CareerTransition""",
    },
    {
        "date": "2026-04-21",
        "slug": "apr-21",
        "time": "2026-04-21T13:00:00",
        "yt_title": "Where are you right now? No wrong answers.",
        "linkedin": """The loneliest six months of my life were the six months after I left medicine.

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

The Fear Audit. Start naming what's underneath. Link in first comment.

#HealthcareBurnout #PhysicianBurnout #NurseBurnout #CrosswalkWisdom #IdentityShift #LeavingMedicine""",
    },
    {
        "date": "2026-04-23",
        "slug": "apr-23",
        "time": "2026-04-23T13:00:00",
        "yt_title": "How I'd use AI to plan a career transition from scratch.",
        "linkedin": """It's 3am. You're not asleep.

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

The Fear Audit. What are you actually afraid of? Link in first comment.

#HealthcareBurnout #NurseBurnout #PhysicianBurnout #CrosswalkWisdom #IdentityShift #CareerTransition""",
    },
    {
        "date": "2026-04-25",
        "slug": "apr-25",
        "time": "2026-04-25T13:00:00",
        "yt_title": "The 3 fears aren't separate. They feed each other.",
        "linkedin": """When I told my colleagues I was leaving medicine, some of them took it personally.

Not all of them. But some.

As if my leaving were a judgment on their staying.

I understand now what I didn't understand then: when you leave something others are trapped in, it can feel like an accusation.

You didn't say "I'm leaving." You said, without words, "Leaving is possible."

And that is terrifying if you've built an entire identity around the belief that staying is the only option.

The people who were angriest at my decision were not angry at me. They were angry at the door I had just proved was unlocked.

I am not telling you this so you'll feel righteous.

I'm telling you this so you'll be gentle. With them. And with yourself.

Their reaction is not about you. It's about what your courage reveals to them about their own fear.

The Fear Audit. What would your decision reveal to the people around you? Link in first comment.

#HealthcareBurnout #PhysicianBurnout #NurseBurnout #CrosswalkWisdom #CareerTransition #IdentityShift""",
    },
    {
        "date": "2026-04-28",
        "slug": "apr-28",
        "time": "2026-04-28T13:00:00",
        "yt_title": "If you've made it this far — you are closer than you think.",
        "linkedin": """You don't need a plan. You need a first step.

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

The Fear Audit. What's your first step? Link in first comment.

#HealthcareBurnout #NurseBurnout #PhysicianBurnout #CrosswalkWisdom #CareerTransition #IdentityShift""",
    },
    {
        "date": "2026-04-30",
        "slug": "apr-30",
        "time": "2026-04-30T13:00:00",
        "yt_title": "Not with a pitch. With a truth. How April ends.",
        "linkedin": """"What do you do?"

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

The Fear Audit. Find out what's actually stopping you. Link in first comment.

#HealthcareBurnout #PhysicianBurnout #NurseBurnout #CrosswalkWisdom #CareerTransition #IdentityShift""",
    },
]


def upload_video(slug):
    filepath = os.path.join(VIDEOS_DIR, f"{slug}.mp4")
    filename = f"{slug}.mp4"
    filesize = os.path.getsize(filepath)
    r = requests.post(
        f"{BASE}/media/presign",
        headers=HEADERS,
        json={"filename": filename, "contentType": "video/mp4", "fileSize": filesize},
    )
    r.raise_for_status()
    data = r.json()
    with open(filepath, "rb") as f:
        requests.put(data["uploadUrl"], data=f, headers={"Content-Type": "video/mp4"}).raise_for_status()
    return data["publicUrl"]


def delete_remaining(date):
    """Delete any leftover posts for this date (handles apr-03 and apr-13 duplicates)."""
    r = requests.get(f"{BASE}/posts?limit=100", headers=HEADERS)
    posts = r.json().get("posts", [])
    count = 0
    for p in posts:
        if p.get("scheduledFor", "")[:10] == date:
            requests.delete(f"{BASE}/posts/{p['_id']}", headers=HEADERS)
            count += 1
    if count:
        print(f"    Deleted {count} leftover posts")


def create_post(post_data, video_url):
    li = post_data["linkedin"]
    ig = li  # Use LinkedIn copy for all platforms (can customize later)
    yt_desc = li + "\n\n#Shorts #CrosswalkWisdom #HealthcareBurnout #NurseBurnout #CareerTransition"

    platforms = [
        {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": li, "scheduledFor": post_data["time"]},
        {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": ig, "scheduledFor": post_data["time"]},
        {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": ig, "scheduledFor": post_data["time"]},
        {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": ig, "scheduledFor": post_data["time"]},
        {"platform": "youtube",   "accountId": YOUTUBE_ID,   "customContent": yt_desc, "title": post_data["yt_title"], "scheduledFor": post_data["time"]},
    ]
    body = {
        "content": li,
        "mediaItems": [{"url": video_url, "type": "video"}],
        "platforms": platforms,
        "scheduledFor": post_data["time"],
        "timezone": TIMEZONE,
        "firstComment": FEAR_AUDIT,
    }
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    return r.status_code, r.text[:200]


def main():
    print(f"Fixing {len(POSTS)} April posts...\n")
    success = 0

    for p in POSTS:
        date = p["date"]
        slug = p["slug"]
        print(f"  {date} ({slug})")

        # Delete any leftover posts (important for apr-03 and apr-13)
        delete_remaining(date)

        # Upload local video
        print(f"    Uploading {slug}.mp4...")
        video_url = upload_video(slug)
        print(f"    Uploaded → ...{video_url[-40:]}")

        # Create clean post
        status, resp = create_post(p, video_url)
        if status in (200, 201):
            print(f"    ✓ Scheduled at {p['time']}")
            success += 1
        else:
            print(f"    ✗ Failed {status}: {resp}")

        time.sleep(0.5)  # Small pause to avoid rate limits

    print(f"\nDone: {success}/{len(POSTS)} posts created.")


if __name__ == "__main__":
    main()
