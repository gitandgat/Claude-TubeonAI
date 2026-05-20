"""
Wave 3: Schedule 9 posts (Apr 13 – May 2) on LinkedIn + Instagram + Facebook.
Pillar progression: THE STORY → THE GRIEF → THE REBUILD
Images to be added later via PATCH once user generates them on Freepik.
"""

import requests
import json

ZERNIO_KEY = "***REMOVED-ZERNIO-KEY***"
BASE = "https://zernio.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {ZERNIO_KEY}",
    "Content-Type": "application/json",
}

LINKEDIN_ID = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID = "6909409a5f6fbb9ef8323074"

FEAR_AUDIT = "https://fear-audit.vercel.app/"

POSTS = [
    # ── WEEK 1: THE STORY (Apr 14-18) ──────────────────────────────────────────

    {
        "scheduledFor": "2026-04-14T09:00:00",
        "timezone": "America/New_York",
        "title": "The Psychiatrist",
        "linkedin": f"""I went to a psychiatrist during my last year in medicine.

I sat in his office and told him everything. The 96-hour shifts. The colleagues collapsing in hallways. The stairwells where I slept because there was no bed. The feeling that my body was giving up before my mind gave me permission.

He listened. He nodded. He wrote something on a pad.

Then he said: "There is nothing I can do for you. The system is the system."

I remember staring at him. Not angry. Not surprised. Just... clear.

Because in that sentence, I heard something he did not intend to say:

"Nobody is coming to save you."

And that was the day I stopped waiting for permission to leave.

Not because I was brave. Because I realized the alternative was waiting for someone to say it was okay — and no one ever would.

The system does not give you permission to leave the system.

You give yourself permission.

And if you need help figuring out what is actually holding the door closed — that is what the Fear Audit does.

Free. 5 minutes: {FEAR_AUDIT}""",
        "instagram": f"""I went to a psychiatrist during my last year in medicine.

I told him everything. The 96-hour shifts. The stairwells where I slept. The feeling that my body was giving up before my mind gave me permission.

He said: "There is nothing I can do for you. The system is the system."

In that sentence, I heard something he didn't intend:

"Nobody is coming to save you."

That was the day I stopped waiting for permission to leave.

The system does not give you permission to leave the system. You give yourself permission.

Free. 5 minutes. Link in bio.

#crosswalkwisdom #fearaudit #leavingmedicine #burnout #permission #careerchange #mentalhealth #courage""",
        "facebook": f"""I went to a psychiatrist during my last year in medicine.

I told him everything. The 96-hour shifts. The colleagues collapsing. The stairwells where I slept.

He said: "There is nothing I can do for you. The system is the system."

In that sentence, I heard something he didn't intend: "Nobody is coming to save you."

That was the day I stopped waiting for permission to leave. Not because I was brave. Because I realized no one was ever going to say it was okay.

The system does not give you permission to leave the system. You give yourself permission.

If you need help figuring out what is actually holding the door closed — that is what the Fear Audit does.

Free. 5 minutes: {FEAR_AUDIT}""",
    },
    {
        "scheduledFor": "2026-04-16T09:00:00",
        "timezone": "America/New_York",
        "title": "The Phone Call",
        "linkedin": f"""The fear I carried for three years lived inside a five-minute phone call I had been refusing to make.

I called my father on a Wednesday afternoon.

I told him I was leaving medicine. That I was a crossing guard now. That I stood at an intersection in a yellow vest with a stop sign and helped children cross the street.

I waited.

He said: "Are you sleeping better?"

I said yes.

He said: "Good."

That was the whole conversation.

Three years of dread. Three years of imagining his disappointment. Three years of "I am afraid that without the title of doctor, my parents will stop being proud of me."

And it took five minutes to find out I was wrong.

Here is what I want you to understand:

Your fear has a specific shape. It is not general dread. It is a specific scene. A specific conversation. A specific face.

And until you find the shape, the fear feels infinite.

Once you find it, you find out if the thing is actually as big as it felt.

Usually it is not.

The Fear Audit helps you find the shape.

Free. 5 minutes: {FEAR_AUDIT}""",
        "instagram": f"""The fear I carried for three years lived inside a five-minute phone call I refused to make.

I called my father. I told him I left medicine. I was a crossing guard now.

He said: "Are you sleeping better?"
I said yes.
He said: "Good."

That was the whole conversation.

Three years of dread. Answered in five minutes.

Your fear has a specific shape. It is not general dread. It is a specific scene. A specific face.

Once you find the shape, you find out if the thing is as big as it felt. Usually it is not.

Free. 5 minutes. Link in bio.

#crosswalkwisdom #fearaudit #careerchange #fatherson #nameyourfear #identity #vulnerability #healing""",
        "facebook": f"""The fear I carried for three years lived inside a five-minute phone call I had been refusing to make.

I called my father on a Wednesday afternoon. I told him I was leaving medicine. That I was a crossing guard now.

He said: "Are you sleeping better?" I said yes. He said: "Good."

That was the whole conversation.

Three years of dread. Three years of imagining his disappointment. Answered in five minutes.

Your fear has a specific shape. It is not general dread. It is a specific conversation. A specific face. Once you find the shape, you find out if the thing is actually as big as it felt.

Usually it is not.

The Fear Audit helps you find the shape.

Free. 5 minutes: {FEAR_AUDIT}""",
    },
    {
        "scheduledFor": "2026-04-18T09:00:00",
        "timezone": "America/New_York",
        "title": "The Yellow Vest",
        "linkedin": f"""I did not leave medicine to become a crossing guard.

I left to find out who I was without a title.

The vest just happened to be there when I did.

People ask me: "Of all things, why crossing guard?"

Because it was the first job I found that asked nothing of my ego.

No one calls me "doctor." No one is impressed. No one asks where I went to school.

Children wave at me every morning. They do not care what I used to be. They care that I am there. Every day. With the sign. In the rain.

And that is the point.

I spent 10 years building an identity around what I did. The title. The credentials. The prestige.

I spent 2 years as a crossing guard learning that none of it was me.

I was always the person under the title. I just never met him.

If you are afraid that leaving your career means losing yourself — I understand. I thought the same thing.

It turns out you do not lose yourself. You just meet yourself for the first time.

Fear Audit — free, 5 minutes: {FEAR_AUDIT}""",
        "instagram": f"""I did not leave medicine to become a crossing guard.

I left to find out who I was without a title. The vest just happened to be there when I did.

No one calls me "doctor." No one is impressed. Children wave at me every morning. They do not care what I used to be.

I spent 10 years building an identity around what I did. I spent 2 years as a crossing guard learning that none of it was me.

You do not lose yourself when you leave. You meet yourself for the first time.

Free. 5 minutes. Link in bio.

#crosswalkwisdom #fearaudit #yellowvest #crossingguard #identity #careerchange #whoareyou #courage""",
        "facebook": f"""I did not leave medicine to become a crossing guard. I left to find out who I was without a title. The vest just happened to be there when I did.

No one calls me "doctor." No one is impressed. Children wave at me every morning. They do not care what I used to be. They care that I am there.

I spent 10 years building an identity around what I did. I spent 2 years as a crossing guard learning that none of it was me.

If you are afraid that leaving your career means losing yourself — I thought the same thing. It turns out you do not lose yourself. You meet yourself for the first time.

Fear Audit — free, 5 minutes: {FEAR_AUDIT}""",
    },

    # ── WEEK 2: THE GRIEF (Apr 21-25) ─────────────────────────────────────────

    {
        "scheduledFor": "2026-04-21T09:00:00",
        "timezone": "America/New_York",
        "title": "The Loneliest Six Months",
        "linkedin": f"""The first six months after leaving are the loneliest.

Nobody talks about this part.

They talk about the courage it takes to leave. The logistics. The pivot. The reinvention.

Nobody talks about the silence.

You will have more time than you know what to do with. The calendar that used to own you will suddenly be empty. And the silence where the chaos used to be will feel wrong.

It is not wrong. It is withdrawal.

You spent years in a high-cortisol, high-identity, high-demand environment. Your nervous system adapted to that. Chaos became your normal.

When the chaos stops, your body does not celebrate. It panics.

"Something must be wrong. Why is nothing happening? Am I wasting my life?"

No. You are recovering.

And recovery is not comfortable. It is not exciting. It does not photograph well.

But it is the most important thing you will ever do.

Because until you learn what your life sounds like without the noise, you will keep filling it with someone else's noise.

If you are in the silence right now — the Fear Audit was built for exactly this moment.

Free. 5 minutes: {FEAR_AUDIT}""",
        "instagram": f"""The first six months after leaving are the loneliest.

Nobody talks about the silence. The empty calendar. The space where chaos used to be.

It is not wrong. It is withdrawal.

Your nervous system adapted to high-cortisol, high-demand. When the chaos stops, your body panics.

"Something must be wrong. Why is nothing happening?"

No. You are recovering. And recovery does not photograph well.

But until you learn what your life sounds like without the noise, you will keep filling it with someone else's noise.

Free. 5 minutes. Link in bio.

#crosswalkwisdom #fearaudit #burnoutrecovery #thesilence #grief #careerchange #healing #nervous""",
        "facebook": f"""The first six months after leaving are the loneliest. Nobody talks about this part.

You will have more time than you know what to do with. The silence where the chaos used to be will feel wrong. It is not wrong. It is withdrawal.

You spent years in a high-cortisol, high-demand environment. When the chaos stops, your body does not celebrate. It panics.

"Something must be wrong. Why is nothing happening? Am I wasting my life?"

No. You are recovering. Recovery is not comfortable. But it is the most important thing you will ever do.

If you are in the silence right now — the Fear Audit was built for exactly this moment.

Free. 5 minutes: {FEAR_AUDIT}""",
    },
    {
        "scheduledFor": "2026-04-23T09:00:00",
        "timezone": "America/New_York",
        "title": "The 3am Questions",
        "linkedin": f"""You will question everything.

Sometimes at 3am. Sometimes in the shower. Sometimes in the middle of a perfectly good Tuesday.

"Did I throw it all away?"
"Am I lazy?"
"What if I could have fixed it?"
"What if everyone was right and I was wrong?"

These are not signs you made a mistake.

They are signs you are grieving.

Leaving a career — even one that was destroying you — is a loss. You are mourning the version of yourself that believed in it. The version that worked 96-hour shifts and thought it would be worth it. The version that told everyone "this is what I am meant to do."

That version of you was real. And they deserve to be mourned.

But mourning is not the same as regretting.

You can grieve something and still know you were right to let it go.

That is the hardest lesson of leaving:

The grief does not mean you were wrong.

It means the thing was real.

And real things hurt when they end — even when they needed to.

If you are in the 3am questions right now — you are not broken. You are human.

The Fear Audit helps you separate the grief from the doubt.

Free. 5 minutes: {FEAR_AUDIT}""",
        "instagram": f"""You will question everything. Sometimes at 3am.

"Did I throw it all away?"
"Am I lazy?"
"What if everyone was right?"

These are not signs you made a mistake. They are signs you are grieving.

You are mourning the version of yourself that believed in it. That version was real. They deserve to be mourned.

But mourning is not the same as regretting.

The grief does not mean you were wrong. It means the thing was real. And real things hurt when they end — even when they needed to.

Free. 5 minutes. Link in bio.

#crosswalkwisdom #fearaudit #3amthoughts #grief #careerchange #mourning #healing #youarenotbroken""",
        "facebook": f"""You will question everything. Sometimes at 3am. Sometimes in the middle of a perfectly good Tuesday.

"Did I throw it all away?"
"Am I lazy?"
"What if I could have fixed it?"

These are not signs you made a mistake. They are signs you are grieving.

You are mourning the version of yourself that believed in it. That version was real. They deserve to be mourned.

But mourning is not the same as regretting. You can grieve something and still know you were right to let it go.

The grief does not mean you were wrong. It means the thing was real.

The Fear Audit helps you separate the grief from the doubt.

Free. 5 minutes: {FEAR_AUDIT}""",
    },
    {
        "scheduledFor": "2026-04-25T09:00:00",
        "timezone": "America/New_York",
        "title": "When They Take It Personally",
        "linkedin": f"""Some people will take your decision to leave personally.

They will not say it. But you will feel it.

The colleague who stops texting. The friend who suddenly has opinions about "stability." The family member who brings up your old job at every gathering.

Here is what is happening:

Your decision to leave is holding up a mirror to the people who stayed.

It is asking them — without you saying a word — "Why are you still there?"

And that question is uncomfortable. So they redirect the discomfort at you.

"You are being irresponsible."
"You are throwing away your education."
"Must be nice to just quit."

These are not about you. These are about them.

They are afraid that if you can leave, then their reasons for staying might not be as solid as they thought.

You are not responsible for their fear. You are only responsible for yours.

And the people who truly love you? They will ask the only question that matters:

"Are you okay?"

My father asked: "Are you sleeping better?"

Everyone else asked: "But what about your career?"

You will learn very quickly who is who.

Fear Audit — free, 5 minutes: {FEAR_AUDIT}""",
        "instagram": f"""Some people will take your decision to leave personally. They will not say it. But you will feel it.

Your decision to leave holds up a mirror to people who stayed. It asks them — without a word — "Why are you still there?"

So they redirect the discomfort at you.

"You are throwing away your education."
"Must be nice to just quit."

These are not about you. These are about them.

The people who truly love you will ask: "Are you okay?"

My father asked: "Are you sleeping better?" Everyone else asked: "But what about your career?"

You will learn very quickly who is who.

Free. 5 minutes. Link in bio.

#crosswalkwisdom #fearaudit #boundaries #careerchange #judgment #family #courage #lettinggo""",
        "facebook": f"""Some people will take your decision to leave personally. They will not say it. But you will feel it.

Your decision holds up a mirror to people who stayed. It asks them: "Why are you still there?" That is uncomfortable. So they redirect the discomfort at you.

"You are throwing away your education." "Must be nice to just quit."

These are not about you. These are about them.

The people who truly love you will ask the only question that matters: "Are you okay?"

My father asked: "Are you sleeping better?" Everyone else asked: "But what about your career?"

You will learn very quickly who is who.

Fear Audit — free, 5 minutes: {FEAR_AUDIT}""",
    },

    # ── WEEK 3: THE REBUILD (Apr 28 – May 2) ──────────────────────────────────

    {
        "scheduledFor": "2026-04-28T09:00:00",
        "timezone": "America/New_York",
        "title": "You Don't Need a Plan",
        "linkedin": f"""You do not need a plan. You need a first step.

I know that sounds reckless. It is not.

Here is the difference:

A plan is what we build when we are afraid to begin. We research. We outline. We create spreadsheets. We tell ourselves we are "preparing." But what we are really doing is waiting — for the fear to leave first.

The fear does not leave first. It leaves second. After you move.

A first step is what happens when you stop waiting.

My first step was walking into a temp agency and saying: "What do you have that starts tomorrow?"

That is not a career plan. That is a Tuesday decision.

But that Tuesday decision led to the crossing guard job. Which led to the first morning a child waved at me. Which led to the realization that I had been defining myself by other people's expectations for a decade.

None of that was in the plan. Because there was no plan.

There was just one step. And then the next one appeared.

If you are waiting for the whole staircase before you take the first step — you will wait forever.

The Fear Audit is a first step.

5 minutes. One piece of paper. Name the thing.

Free: {FEAR_AUDIT}""",
        "instagram": f"""You do not need a plan. You need a first step.

A plan is what we build when we are afraid to begin. "Preparing" is often just waiting — for the fear to leave first.

The fear does not leave first. It leaves second. After you move.

My first step was walking into a temp agency: "What do you have that starts tomorrow?"

That led to the crossing guard job. Which led to the first morning a child waved at me. Which led to everything.

None of that was in the plan. Because there was no plan.

There was just one step.

Free. 5 minutes. Link in bio.

#crosswalkwisdom #fearaudit #firststep #noplan #careerchange #juststart #courage #rebuild""",
        "facebook": f"""You do not need a plan. You need a first step.

A plan is what we build when we are afraid to begin. We research. We outline. We create spreadsheets. We tell ourselves we are "preparing."

But what we are really doing is waiting — for the fear to leave first. The fear does not leave first. It leaves second. After you move.

My first step was walking into a temp agency: "What do you have that starts tomorrow?"

That led to the crossing guard job. Which led to everything.

None of that was in the plan. Because there was no plan. There was just one step. And then the next one appeared.

The Fear Audit is a first step. 5 minutes. Name the thing.

Free: {FEAR_AUDIT}""",
    },
    {
        "scheduledFor": "2026-04-30T09:00:00",
        "timezone": "America/New_York",
        "title": "What Do You Do",
        "linkedin": f""""So, what do you do?"

That question used to make me panic.

Because for two years after leaving medicine, I did not have a good answer. I had an honest answer. But honest and good are different things at dinner parties.

"I am a crossing guard."

Silence. Then the tilt. Then: "Oh. Okay. That is... different."

I tried versions. I tried "I am in transition." I tried "I am exploring." I tried "I used to be a doctor."

None of them worked. Because they were all apologies.

Then one day, a child at my crosswalk asked me: "What is your job?"

I said: "I help you cross the street safely."

She said: "That is a good job."

And I thought — she is right. It is.

Here is what I say now:

"I help children cross the street. And I help adults cross a different kind of street."

Both are true.

You do not owe anyone a title. You owe yourself the truth.

And the truth is: you are more than what you do for money. You always were. You just forgot.

If you are afraid that leaving means becoming "nothing" — that is Identity Fear. It is the quietest of the five fears. And it is the one the Fear Audit was built for.

Free. 5 minutes: {FEAR_AUDIT}""",
        "instagram": f""""So, what do you do?"

For two years after leaving medicine, that question made me panic.

"I am a crossing guard." Silence. The tilt. "Oh. That is... different."

I tried "in transition." I tried "exploring." They were all apologies.

Then a child at my crosswalk asked me: "What is your job?"
I said: "I help you cross the street safely."
She said: "That is a good job."

She was right.

Now I say: "I help children cross the street. And I help adults cross a different kind of street."

You do not owe anyone a title. You owe yourself the truth.

Free. 5 minutes. Link in bio.

#crosswalkwisdom #fearaudit #whatdoyoudo #identity #careerchange #nolabels #rebuild #truth""",
        "facebook": f""""So, what do you do?" That question used to make me panic.

"I am a crossing guard." Silence. The tilt. "Oh. That is... different."

I tried "in transition." I tried "exploring." They were all apologies.

Then a child at my crosswalk asked: "What is your job?" I said: "I help you cross the street safely." She said: "That is a good job."

She was right.

Now I say: "I help children cross the street. And I help adults cross a different kind of street." Both are true.

You do not owe anyone a title. You owe yourself the truth.

If "what do you do?" terrifies you — that is Identity Fear. The Fear Audit was built for it.

Free. 5 minutes: {FEAR_AUDIT}""",
    },
    {
        "scheduledFor": "2026-05-02T09:00:00",
        "timezone": "America/New_York",
        "title": "The Courage to Choose",
        "linkedin": f"""I wrote everything I wish someone had told me when I was in the gap.

The gap between leaving and landing. The quiet place where the old identity is gone and the new one has not arrived yet.

Nobody writes about the gap. Because it is not inspiring. It is not "I quit my job and traveled the world." It is not "I found my passion and never looked back."

It is sitting in a kitchen. Wondering if you made a mistake. Trying to remember what you enjoy. Realizing you do not know.

That is the gap. And I lived in it for over a year.

During that time, I wrote. I wrote about fear — the five kinds I found inside myself. I wrote about grief — the mourning nobody warns you about. I wrote about rebuilding — the slow, unglamorous process of becoming someone new.

I turned it into a book.

It is called The Courage to Choose.

It is not a career guide. It is not a motivational book. It is not "10 steps to find your passion."

It is a companion for the gap.

7 chapters. 3 frameworks. 1 question that changed everything for me.

If you have already taken the Fear Audit and you are ready for the next conversation — this is it.

$27. Link in comments.

And if you have not taken the Fear Audit yet — start there. It is free:
{FEAR_AUDIT}""",
        "instagram": f"""I wrote everything I wish someone had told me when I was in the gap.

The gap between leaving and landing. Where the old identity is gone and the new one hasn't arrived.

Nobody writes about the gap. It is not inspiring. It is sitting in a kitchen. Wondering if you made a mistake. Realizing you do not know what you enjoy.

I lived there for over a year. During that time, I wrote about fear, grief, and rebuilding.

I turned it into The Courage to Choose.

Not a career guide. A companion for the gap.

7 chapters. 3 frameworks. 1 question that changed everything.

$27. Link in bio.

Start with the Fear Audit if you haven't yet — it's free.

#crosswalkwisdom #thecouragetoochoose #fearaudit #careerchange #thegap #book #rebuild #newidentity""",
        "facebook": f"""I wrote everything I wish someone had told me when I was in the gap.

The gap between leaving and landing. Where the old identity is gone and the new one has not arrived yet.

Nobody writes about the gap. It is not inspiring. It is sitting in a kitchen. Wondering if you made a mistake. Realizing you do not know what you enjoy.

I lived there for over a year. I wrote about fear, grief, and rebuilding. I turned it into The Courage to Choose.

Not a career guide. A companion for the gap. 7 chapters. 3 frameworks. 1 question that changed everything.

$27: https://sahawat.gumroad.com/l/courage-to-choose

Start with the Fear Audit if you haven't yet — it's free: {FEAR_AUDIT}""",
    },
]


def schedule_post(post):
    payload = {
        "content": post["linkedin"],
        "scheduledFor": post["scheduledFor"],
        "timezone": post["timezone"],
        "platforms": [
            {
                "platform": "linkedin",
                "accountId": LINKEDIN_ID,
                "customContent": post["linkedin"],
            },
            {
                "platform": "instagram",
                "accountId": INSTAGRAM_ID,
                "customContent": post["instagram"],
            },
            {
                "platform": "facebook",
                "accountId": FACEBOOK_ID,
                "customContent": post["facebook"],
            },
        ],
    }
    resp = requests.post(f"{BASE}/posts", headers=HEADERS, json=payload)
    return resp.status_code, resp.json()


if __name__ == "__main__":
    print(f"Scheduling {len(POSTS)} Wave 3 posts...\n")
    scheduled_ids = []
    for post in POSTS:
        status, result = schedule_post(post)
        post_id = result.get("_id") or result.get("id") or "?"
        label = "OK" if status in (200, 201) else "FAIL"
        print(f"  [{label} {status}] {post['scheduledFor'][:10]} — {post['title']} (id: {post_id})")
        if status not in (200, 201):
            print(f"    {json.dumps(result, indent=2)[:200]}")
        scheduled_ids.append({"id": post_id, "date": post["scheduledFor"][:10], "title": post["title"]})

    print(f"\n--- Scheduled IDs (for image PATCH later) ---")
    for s in scheduled_ids:
        print(f"  {s['id']} — {s['date']} — {s['title']}")
