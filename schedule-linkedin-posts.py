"""
Schedule all 8 Crosswalk Wisdom LinkedIn posts via Zernio API.
3x/week cadence — Mon/Wed/Fri at 9am ET starting March 24, 2026.
"""

import requests
import json
import os

API_KEY = "sk_d1c977cc304ec9685c24f22c7e3b868abd5a10b9db8f7648b2b74384ab1ca399"
BASE_URL = "https://zernio.com/api/v1"
LINKEDIN_ACCOUNT_ID = "690940455f6fbb9ef8323070"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

POSTS = [
    {
        "scheduledFor": "2026-03-24T09:00:00",
        "timezone": "America/New_York",
        "title": "Sunk Cost Trap",
        "content": """I stayed in medicine 2 years longer than I should have.

Not because I loved it.

Because I had already given too much to leave.

6 years of medical school. Residency. The sleepless rotations. The money. The time. The youth I spent studying while everyone else was living.

"You've come too far to quit now."

That sentence almost killed me.

The investment becomes the cage. Every year you stay, the cage gets smaller.

Two years of 96-hour shifts. Two years of being screamed at. Two years of falling asleep in hospital stairwells.

The day I finally left, I did not feel like I was throwing anything away.

I felt like I had finally stopped throwing myself away.

—

The Fear Audit helps you separate the real fears from the sunk cost fog.

Free. 5 minutes. Link in comments.""",
    },
    {
        "scheduledFor": "2026-03-26T09:00:00",
        "timezone": "America/New_York",
        "title": "What Will People Think",
        "content": """When I told my mother I was leaving medicine, she cried.

Not because she was sad.
Because she was scared for me.

"My son is a doctor." Four words that carry the weight of generations.

My friends did not know what to say. Some stopped calling. Some gave me the look.

Here is what I have learned:

"What will people think" lasts five minutes.

The life you are not living? That stays with you every day.

I chose to disappoint some people so I could stop disappointing myself.

That is not selfish. That is survival.

—

The Fear Audit helps you separate real risk from social pressure.

Free. 5 minutes. Link in comments.""",
    },
    {
        "scheduledFor": "2026-03-28T09:00:00",
        "timezone": "America/New_York",
        "title": "Quitting Is Not Failure",
        "content": """Quitting is not the opposite of success.

Staying in something that is destroying you is not strength.
It is just endurance with no finish line.

I pushed through 96-hour shifts.
I pushed through supervisors who threw instruments in the OR.
I pushed through a system that treated sleep as a luxury.

And when I finally stopped pushing, people called it quitting.

I call it the single hardest decision I have ever made.

Staying was autopilot.
Leaving was a choice.

And choice — real, terrifying, deliberate choice — is not weakness.

It is the first honest thing I did in years.

—

The Fear Audit: the difference between commitment and captivity.

Free. 5 minutes. Link in comments.""",
    },
    {
        "scheduledFor": "2026-03-31T09:00:00",
        "timezone": "America/New_York",
        "title": "Introducing the Fear Audit",
        "content": """Most people don't leave bad careers because of logistics.

They leave when they finally name what they're actually afraid of.

"I'm afraid my parents will think I wasted their sacrifice."
"I'm afraid I'm not good enough to do anything else."
"I'm afraid people will stop respecting me."

Those aren't logistics. Those are fears.

And unnamed fears have all the power.

The Fear Audit. A 5-minute exercise.

Write "I'm afraid that..." 5 to 7 times. Don't filter.

Circle the one that hits hardest.
Then ask it: "Is this true, or is this a story I'm telling myself?"

Fog with a name is something you can walk through.

—

Download the Fear Audit — free. Link in comments.""",
    },
    {
        "scheduledFor": "2026-04-02T09:00:00",
        "timezone": "America/New_York",
        "title": "I Named My Fear",
        "content": """I named my fear out loud for the first time on a Tuesday morning.

I was sitting at my kitchen table with a piece of paper.
No app. No therapist. Just a pen and a question:

What, specifically, am I afraid of?

Not "leaving medicine" or "making a mistake."
Specific. Granular. True.

And I wrote it.

"I am afraid that without the title of doctor, my parents will stop being proud of me."

I stared at it for a long time.

Because here is the thing about fear that nobody tells you:
When it is unnamed, it feels like the truth.
When it is named, it feels like a sentence you can examine.

My career anxiety didn't disappear that Tuesday.
I did not suddenly feel brave.

But for the first time, I was arguing with a specific thing instead of wrestling with a fog.

Is that actually true?
Has my father ever said his love was conditional on my job title?
No. He said it was conditional on my being kind.
I am still kind. In a yellow vest.

Fear named is fear that can be questioned.
Fear unnamed is fear that cannot be beaten.

—

The Fear Audit. Free. 5 minutes. Link in comments.""",
    },
    {
        "scheduledFor": "2026-04-04T09:00:00",
        "timezone": "America/New_York",
        "title": "The 5 Fears Inside I Can't Leave",
        "content": """"I can't leave."

I have heard this sentence from hundreds of people now.

And every single time, when we actually sit down and name what is inside it, we find the same five fears. In different proportions. In different disguises. But the same five.

Fear 1: Financial Fear
"I won't be able to pay my bills."
This one is real and it deserves a real plan — not dismissal.
But it almost always turns out to be smaller than assumed.
Nobody has run the actual numbers. They are just afraid to.

Fear 2: Identity Fear
"Who am I without this title?"
This is the silent one. The one people don't admit out loud.
It is the fear that the career is you.
That without it, you are nothing recognizable.

Fear 3: Judgment Fear
"What will people think?"
Not your closest friends. The peripheral people.
We make enormous life decisions to avoid conversations with people we barely like.

Fear 4: Failure Fear
"What if I try something new and it doesn't work?"
Disguised as realism.
But realism would ask: and what if it does work?

Fear 5: Grief Fear
"What if I leave and feel like I wasted everything?"
This is the deepest one.
It is not fear of the future.
It is fear of having to mourn the past.

I stayed in medicine two extra years because of Fear 5.
I couldn't bear to admit that I needed to let go of who I thought I was going to be.

The Fear Audit separates these five.
Because they require five different conversations — not one endless spiral.

Free. 5 minutes. Link in comments.""",
    },
    {
        "scheduledFor": "2026-04-07T09:00:00",
        "timezone": "America/New_York",
        "title": "The 4 Stages of Being Stuck",
        "content": """After building the Fear Audit and having thousands of people take it, I've noticed that stuck professionals don't all look the same.

They fall into four distinct stages.

Stage 1: START
You know something is wrong but you can't name it yet.
The fear feels like background noise — always present, never clear.
You keep saying "I just need to push through."
You are not burned out. You are pre-burnout.

Stage 2: STOP
You know exactly what is wrong.
You have thought about leaving so many times it has become its own exhausting thing.
But you can't move. Something has you frozen.
For most people in STOP, it is Identity Fear or Judgment Fear.

Stage 3: ELDER
You have been here a long time.
The fear has become habit.
You don't even experience it as fear anymore — it just feels like the way things are.
"This is just how work is."

Stage 4: HUMAN
Something broke recently — a conversation, a moment, a diagnosis, a loss.
And suddenly the calculation changed.
You are not asking "should I leave?"
You are asking "how?"
You already have the permission. You always did.

—

Which stage are you?

Take the 5-minute Fear Audit free. Link in comments.""",
    },
    {
        "scheduledFor": "2026-04-09T09:00:00",
        "timezone": "America/New_York",
        "title": "Why I Built the Fear Audit",
        "content": """I did not build the Fear Audit because I am a coach.
I built it because I needed it and it didn't exist.

When I was trying to leave medicine, I searched for something that would help me figure out what I was actually afraid of.

I found:
— Career counselors who wanted to talk about skills assessments
— Therapists who wanted to talk about childhood
— LinkedIn posts about "following your passion"
— Books that assumed I already knew what I wanted

None of them helped with the specific problem I had.

I knew what I wanted. I wanted out.
I didn't know what was stopping me.

That is a different problem.

Fear of career change is not one thing. It is a cluster of distinct fears that feel like one fog. And until you separate them, you are trying to solve all five problems with one move. Which is why every move feels impossible.

I eventually built the separation exercise myself. On a piece of paper, at a kitchen table, with a pen.

Later I turned it into the Fear Audit.

It is not therapy. It is not a career quiz. It is not a personality type.

It is five questions that separate five fears so you can actually look at them one at a time.

That is all it does.
That is all I needed.

Free. 5 minutes. Link in comments.""",
    },
]


def schedule_post(post):
    payload = {
        "content": post["content"],
        "scheduledFor": post["scheduledFor"],
        "timezone": post["timezone"],
        "platforms": [
            {"platform": "linkedin", "accountId": LINKEDIN_ACCOUNT_ID}
        ],
    }
    resp = requests.post(f"{BASE_URL}/posts", headers=HEADERS, json=payload)
    return resp.status_code, resp.json()


if __name__ == "__main__":
    print(f"Scheduling {len(POSTS)} LinkedIn posts...\n")
    for post in POSTS:
        status, result = schedule_post(post)
        post_id = result.get("_id") or result.get("id") or "?"
        print(f"[{status}] {post['scheduledFor']} — {post['title']}: {post_id}")
        if status not in (200, 201):
            print(f"  ERROR: {json.dumps(result, indent=2)}")
