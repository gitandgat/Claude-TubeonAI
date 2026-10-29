"""
Full scheduling pipeline:
1. Upload 8 images to Zernio via presigned URLs
2. Delete old text-only LinkedIn posts
3. Re-schedule with images on LinkedIn + Instagram + Facebook
   with Fear Audit link in content
"""

import requests
import json
import os

from zernio_key import ZERNIO_API_KEY as ZERNIO_KEY
BASE = "https://zernio.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {ZERNIO_KEY}",
    "Content-Type": "application/json",
}

ASSETS = "/Users/toto/Claude TubeonAI/crosswalk-remotion/public/assets"

LINKEDIN_ID = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID = "6909409a5f6fbb9ef8323074"

# IDs of the 8 text-only LinkedIn posts to delete
OLD_POST_IDS = [
    "69c1f8ad22500a8a92c5e465",  # Mar 24
    "69c1f8b122500a8a92c5e4a5",  # Mar 26
    "69c1f8b422500a8a92c5e50e",  # Mar 28
    "69c1f8b722500a8a92c5e546",  # Mar 31
    "69c1f8ba22500a8a92c5e5b8",  # Apr 2
    "69c1f8be2f9ba20fe63c093a",  # Apr 4
    "69c1f8c22f9ba20fe63c09c6",  # Apr 7
    "69c1f8c5cbc0c8903514f54e",  # Apr 9
]

FEAR_AUDIT_LINK = "https://fear-audit.vercel.app/"

POSTS = [
    {
        "scheduledFor": "2026-03-24T09:00:00",
        "timezone": "America/New_York",
        "title": "Sunk Cost Trap",
        "image": "post-sunk-cost.jpg",
        "linkedin_content": f"""I stayed in medicine 2 years longer than I should have.

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

Free. 5 minutes. Take it here: {FEAR_AUDIT_LINK}""",
        "instagram_content": f"""I stayed in medicine 2 years longer than I should have.

Not because I loved it. Because I had already given too much to leave.

"You've come too far to quit now." That sentence almost killed me.

The investment becomes the cage. Every year you stay, the cage gets smaller.

The day I finally left, I did not feel like I was throwing anything away. I felt like I had finally stopped throwing myself away.

The Fear Audit — free, 5 minutes. Link in bio.

#careerchange #burnout #fearaudit #crosswalkwisdom #leavingmedicine #identitycrisis #mentalhealth #selfworth""",
        "facebook_content": f"""I stayed in medicine 2 years longer than I should have.

Not because I loved it. Because I had already given too much to leave.

"You've come too far to quit now." That sentence almost killed me.

The investment becomes the cage. Every year you stay, the cage gets smaller.

The day I finally left, I did not feel like I was throwing anything away. I felt like I had finally stopped throwing myself away.

—

The Fear Audit helps you separate the real fears from the sunk cost fog.

Free. 5 minutes. Take it here: {FEAR_AUDIT_LINK}""",
    },
    {
        "scheduledFor": "2026-03-26T09:00:00",
        "timezone": "America/New_York",
        "title": "What Will People Think",
        "image": "post-what-will-people-think.jpg",
        "linkedin_content": f"""When I told my mother I was leaving medicine, she cried.

Not because she was sad. Because she was scared for me.

"My son is a doctor." Four words that carry the weight of generations.

My friends did not know what to say. Some stopped calling. Some gave me the look.

Here is what I have learned:

"What will people think" lasts five minutes.

The life you are not living? That stays with you every day.

I chose to disappoint some people so I could stop disappointing myself.

That is not selfish. That is survival.

—

The Fear Audit helps you separate real risk from social pressure.

Free. 5 minutes. Take it here: {FEAR_AUDIT_LINK}""",
        "instagram_content": f"""When I told my mother I was leaving medicine, she cried. Not because she was sad. Because she was scared for me.

"My son is a doctor." Four words that carry the weight of generations.

"What will people think" lasts five minutes. The life you are not living? That stays with you every day.

I chose to disappoint some people so I could stop disappointing myself. That is not selfish. That is survival.

The Fear Audit — free, 5 minutes. Link in bio.

#careerchange #fearaudit #crosswalkwisdom #whatwillpeoplethink #socialpressure #boundaries #authenticity #burnoutrecovery""",
        "facebook_content": f"""When I told my mother I was leaving medicine, she cried.

Not because she was sad. Because she was scared for me.

"My son is a doctor." Four words that carry the weight of generations.

"What will people think" lasts five minutes. The life you are not living? That stays with you every day.

I chose to disappoint some people so I could stop disappointing myself. That is not selfish. That is survival.

—

The Fear Audit: separate real risk from social pressure.

Free. 5 minutes. Take it here: {FEAR_AUDIT_LINK}""",
    },
    {
        "scheduledFor": "2026-03-28T09:00:00",
        "timezone": "America/New_York",
        "title": "Quitting Is Not Failure",
        "image": "post-quitting-is-not-failure.jpg",
        "linkedin_content": f"""Quitting is not the opposite of success.

Staying in something that is destroying you is not strength. It is just endurance with no finish line.

I pushed through 96-hour shifts. I pushed through supervisors who threw instruments in the OR. I pushed through a system that treated sleep as a luxury.

And when I finally stopped pushing, people called it quitting.

I call it the single hardest decision I have ever made.

Staying was autopilot. Leaving was a choice.

And choice — real, terrifying, deliberate choice — is not weakness.

It is the first honest thing I did in years.

—

The Fear Audit: the difference between commitment and captivity.

Free. 5 minutes. Take it here: {FEAR_AUDIT_LINK}""",
        "instagram_content": f"""Quitting is not the opposite of success.

Staying in something that is destroying you is not strength. It is just endurance with no finish line.

When I finally stopped pushing, people called it quitting. I call it the single hardest decision I have ever made.

Staying was autopilot. Leaving was a choice.

And choice — real, terrifying, deliberate choice — is not weakness. It is the first honest thing I did in years.

The Fear Audit — free, 5 minutes. Link in bio.

#quitting #careerchange #fearaudit #crosswalkwisdom #strength #courage #burnout #selflove""",
        "facebook_content": f"""Quitting is not the opposite of success.

Staying in something that is destroying you is not strength. It is just endurance with no finish line.

When I finally stopped pushing, people called it quitting. I call it the single hardest decision I have ever made.

Staying was autopilot. Leaving was a choice.

And choice — real, terrifying, deliberate choice — is not weakness. It is the first honest thing I did in years.

—

The Fear Audit: the difference between commitment and captivity.

Free. 5 minutes. Take it here: {FEAR_AUDIT_LINK}""",
    },
    {
        "scheduledFor": "2026-03-31T09:00:00",
        "timezone": "America/New_York",
        "title": "Introducing the Fear Audit",
        "image": "post-fear-audit-intro.jpg",
        "linkedin_content": f"""Most people don't leave bad careers because of logistics.

They leave when they finally name what they're actually afraid of.

"I'm afraid my parents will think I wasted their sacrifice."
"I'm afraid I'm not good enough to do anything else."
"I'm afraid people will stop respecting me."

Those aren't logistics. Those are fears. And unnamed fears have all the power.

The Fear Audit. A 5-minute exercise.

Write "I'm afraid that..." 5 to 7 times. Don't filter.

Circle the one that hits hardest. Then ask it: "Is this true, or is this a story I'm telling myself?"

Fog with a name is something you can walk through.

—

Download the Fear Audit — free. Take it here: {FEAR_AUDIT_LINK}""",
        "instagram_content": f"""Most people don't leave bad careers because of logistics.

They leave when they finally name what they're actually afraid of.

"I'm afraid my parents will think I wasted their sacrifice."
"I'm afraid I'm not good enough to do anything else."

Those aren't logistics. Those are fears. And unnamed fears have all the power.

The Fear Audit. Write "I'm afraid that..." 5 to 7 times. Don't filter. Circle the one that hits hardest.

Fog with a name is something you can walk through.

Free, 5 minutes. Link in bio.

#fearaudit #careerchange #crosswalkwisdom #nameyourfear #burnoutrecovery #lifechanges #courage #personalgrowth""",
        "facebook_content": f"""Most people don't leave bad careers because of logistics.

They leave when they finally name what they're actually afraid of.

"I'm afraid my parents will think I wasted their sacrifice."
"I'm afraid I'm not good enough to do anything else."
"I'm afraid people will stop respecting me."

Those aren't logistics. Those are fears. And unnamed fears have all the power.

The Fear Audit: write "I'm afraid that..." 5 to 7 times. Don't filter. Circle the one that hits hardest.

Fog with a name is something you can walk through.

Free. 5 minutes. Take it here: {FEAR_AUDIT_LINK}""",
    },
    {
        "scheduledFor": "2026-04-02T09:00:00",
        "timezone": "America/New_York",
        "title": "I Named My Fear",
        "image": "post-naming-fear.jpg",
        "linkedin_content": f"""I named my fear out loud for the first time on a Tuesday morning.

I was sitting at my kitchen table with a piece of paper. No app. No therapist. Just a pen and a question:

What, specifically, am I afraid of?

Not "leaving medicine" or "making a mistake." Specific. Granular. True.

And I wrote it.

"I am afraid that without the title of doctor, my parents will stop being proud of me."

I stared at it for a long time.

Because here is the thing about fear that nobody tells you:
When it is unnamed, it feels like the truth.
When it is named, it feels like a sentence you can examine.

Is that actually true?
Has my father ever said his love was conditional on my job title?
No. He said it was conditional on my being kind.
I am still kind. In a yellow vest.

Fear named is fear that can be questioned.
Fear unnamed is fear that cannot be beaten.

—

The Fear Audit. Free. 5 minutes. Take it here: {FEAR_AUDIT_LINK}""",
        "instagram_content": f"""I named my fear out loud for the first time on a Tuesday morning.

Just a pen and a question: What, specifically, am I afraid of?

"I am afraid that without the title of doctor, my parents will stop being proud of me."

When fear is unnamed, it feels like the truth.
When it is named, it feels like a sentence you can examine.

Has my father ever said his love was conditional on my job title? No. He said it was conditional on my being kind. I am still kind. In a yellow vest.

Fear named is fear that can be questioned. Fear unnamed is fear that cannot be beaten.

Free, 5 minutes. Link in bio.

#fearaudit #crosswalkwisdom #nameyourfear #careerchange #identity #vulnerability #healing #courage""",
        "facebook_content": f"""I named my fear out loud for the first time on a Tuesday morning.

Just a pen and a question: What, specifically, am I afraid of?

"I am afraid that without the title of doctor, my parents will stop being proud of me."

When fear is unnamed, it feels like the truth. When it is named, it feels like a sentence you can examine.

Has my father ever said his love was conditional on my job title? No. He said it was conditional on my being kind. I am still kind. In a yellow vest.

Fear named is fear that can be questioned. Fear unnamed is fear that cannot be beaten.

Free. 5 minutes. Take it here: {FEAR_AUDIT_LINK}""",
    },
    {
        "scheduledFor": "2026-04-04T09:00:00",
        "timezone": "America/New_York",
        "title": "The 5 Fears",
        "image": "post-five-fears.jpg",
        "linkedin_content": f""""I can't leave."

I have heard this sentence from hundreds of people now.

And every single time, when we actually sit down and name what is inside it, we find the same five fears. In different proportions. In different disguises. But the same five.

Fear 1: Financial Fear
"I won't be able to pay my bills."
Real. Deserves a real plan. But almost never the actual blocker. Nobody has run the numbers.

Fear 2: Identity Fear
"Who am I without this title?"
The silent one. The fear the career is you.

Fear 3: Judgment Fear
"What will people think?"
We make enormous life decisions to avoid conversations with people we barely like.

Fear 4: Failure Fear
"What if I try and it doesn't work?"
Disguised as realism. Realism would also ask: "What if it does?"

Fear 5: Grief Fear
"What if I leave and feel like I wasted everything?"
Not fear of the future. Fear of having to mourn the past. This kept me in medicine two extra years.

The Fear Audit separates these five. Because they require five different conversations — not one endless spiral.

Free. 5 minutes. Take it here: {FEAR_AUDIT_LINK}""",
        "instagram_content": f""""I can't leave." There are always 5 fears inside that sentence.

1. Financial Fear — "I won't be able to pay my bills."
2. Identity Fear — "Who am I without this title?"
3. Judgment Fear — "What will people think?"
4. Failure Fear — "What if I try and it doesn't work?"
5. Grief Fear — "What if leaving means I wasted everything?"

Each fear needs a different conversation — not one endless spiral.

The Fear Audit separates them. Free, 5 minutes. Link in bio.

#fearaudit #fivefears #crosswalkwisdom #careerchange #stuckprofessional #identitycrisis #burnout #courage""",
        "facebook_content": f""""I can't leave." There are always 5 fears inside that sentence.

1. Financial Fear — "I won't be able to pay my bills."
2. Identity Fear — "Who am I without this title?"
3. Judgment Fear — "What will people think?"
4. Failure Fear — "What if I try and it doesn't work?"
5. Grief Fear — "What if leaving means I wasted everything?"

Each fear needs a different conversation — not one endless spiral.

The Fear Audit separates them. Free. 5 minutes. Take it here: {FEAR_AUDIT_LINK}""",
    },
    {
        "scheduledFor": "2026-04-07T09:00:00",
        "timezone": "America/New_York",
        "title": "The 4 Stages of Stuck",
        "image": "post-four-stages.jpg",
        "linkedin_content": f"""After building the Fear Audit and having thousands of people take it, I've noticed that stuck professionals don't all look the same.

They fall into four distinct stages.

Stage 1: START
You know something is wrong but you can't name it yet.
The fear feels like background noise. You keep saying "I just need to push through."
You are not burned out. You are pre-burnout.

Stage 2: STOP
You know exactly what is wrong.
You have thought about leaving so many times it has become its own exhausting thing.
But you can't move. Something has you frozen.

Stage 3: ELDER
You have been here a long time.
The fear has become habit. It doesn't feel like fear anymore.
"This is just how work is."

Stage 4: HUMAN
Something broke recently — a conversation, a moment, a loss.
You are not asking "should I leave?" You are asking "how?"
You already have the permission. You always did.

—

Which stage are you?

Take the Fear Audit free. 5 minutes: {FEAR_AUDIT_LINK}""",
        "instagram_content": f"""Not everyone who's stuck looks the same. 4 stages:

START — You know something is wrong but can't name it yet.
STOP — You know exactly what's wrong but can't move.
ELDER — Fear has become habit. It just feels like "how work is."
HUMAN — Something broke. You're asking "how?" not "should I?"

Every stage has a path forward. The Fear Audit meets you where you are.

Free, 5 minutes. Link in bio.

#fearaudit #fourstages #crosswalkwisdom #careerchange #stuck #burnout #nextstep #courage""",
        "facebook_content": f"""Not everyone who's stuck looks the same. 4 stages:

START — You know something is wrong but can't name it yet.
STOP — You know exactly what's wrong but can't move.
ELDER — Fear has become habit. It just feels like "how work is."
HUMAN — Something broke. You're asking "how?" not "should I?"

Every stage has a path forward. The Fear Audit meets you where you are.

Which stage are you?

Free. 5 minutes. Take it here: {FEAR_AUDIT_LINK}""",
    },
    {
        "scheduledFor": "2026-04-09T09:00:00",
        "timezone": "America/New_York",
        "title": "Why I Built the Fear Audit",
        "image": "post-why-i-built-it.jpg",
        "linkedin_content": f"""I did not build the Fear Audit because I am a coach.
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

Fear of career change is not one thing. It is a cluster of distinct fears that feel like one fog. And until you separate them, every move feels impossible.

I eventually built the separation exercise myself. On a piece of paper, at a kitchen table, with a pen.

Later I turned it into the Fear Audit.

It is not therapy. It is not a career quiz. It is not a personality type.

It is five questions that separate five fears so you can actually look at them one at a time.

That is all it does. That is all I needed.

Free. 5 minutes. Take it here: {FEAR_AUDIT_LINK}""",
        "instagram_content": f"""I did not build the Fear Audit because I am a coach. I built it because I needed it and it didn't exist.

I knew what I wanted. I wanted out. I didn't know what was stopping me. That is a different problem.

Fear of career change is not one thing. It is a cluster of distinct fears that feel like one fog. Until you separate them, every move feels impossible.

Five questions. Five fears. One at a time.

That is all it does. That is all I needed.

Free, 5 minutes. Link in bio.

#fearaudit #crosswalkwisdom #whyibuiltit #careerchange #leavingmedicine #personalgrowth #courage #healing""",
        "facebook_content": f"""I did not build the Fear Audit because I am a coach. I built it because I needed it and it didn't exist.

I knew what I wanted. I wanted out. I didn't know what was stopping me. That is a different problem.

Fear of career change is not one thing. It is a cluster of distinct fears that feel like one fog. Until you separate them, every move feels impossible.

I eventually built the separation exercise myself. On a piece of paper, at a kitchen table, with a pen.

Five questions. Five fears. One at a time.

That is all it does. That is all I needed.

Free. 5 minutes. Take it here: {FEAR_AUDIT_LINK}""",
    },
]


# ─── Step 1: Upload images ──────────────────────────────────────────────────────

def upload_image(filename):
    """Get presigned URL, upload file, return publicUrl."""
    filepath = os.path.join(ASSETS, filename)
    file_size = os.path.getsize(filepath)

    # Get presigned URL
    presign_resp = requests.post(
        f"{BASE}/media/presign",
        headers=HEADERS,
        json={
            "filename": filename,
            "contentType": "image/jpeg",
            "size": file_size,
        },
    )
    presign_resp.raise_for_status()
    presign_data = presign_resp.json()
    upload_url = presign_data.get("uploadUrl") or presign_data.get("data", {}).get("uploadUrl")
    public_url = presign_data.get("publicUrl") or presign_data.get("data", {}).get("publicUrl")

    if not upload_url or not public_url:
        raise ValueError(f"Missing URLs in presign response: {presign_data}")

    # Upload file via PUT
    with open(filepath, "rb") as f:
        put_resp = requests.put(
            upload_url,
            data=f,
            headers={"Content-Type": "image/jpeg"},
        )
        put_resp.raise_for_status()

    return public_url


# ─── Step 2: Delete old posts ────────────────────────────────────────────────────

def delete_old_posts():
    deleted = 0
    for post_id in OLD_POST_IDS:
        resp = requests.delete(f"{BASE}/posts/{post_id}", headers=HEADERS)
        if resp.status_code in (200, 204):
            deleted += 1
            print(f"  Deleted {post_id}")
        else:
            print(f"  Failed to delete {post_id}: {resp.status_code} {resp.text[:100]}")
    return deleted


# ─── Step 3: Schedule new posts ──────────────────────────────────────────────────

def schedule_post(post, public_url):
    payload = {
        "content": post["linkedin_content"],
        "scheduledFor": post["scheduledFor"],
        "timezone": post["timezone"],
        "mediaItems": [
            {
                "url": public_url,
                "type": "image",
            }
        ],
        "platforms": [
            {
                "platform": "linkedin",
                "accountId": LINKEDIN_ID,
                "customContent": post["linkedin_content"],
            },
            {
                "platform": "instagram",
                "accountId": INSTAGRAM_ID,
                "customContent": post["instagram_content"],
            },
            {
                "platform": "facebook",
                "accountId": FACEBOOK_ID,
                "customContent": post["facebook_content"],
            },
        ],
    }
    resp = requests.post(f"{BASE}/posts", headers=HEADERS, json=payload)
    return resp.status_code, resp.json()


# ─── Main ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Step 1: Upload images
    print("=== Uploading images ===")
    image_urls = {}
    for post in POSTS:
        fname = post["image"]
        print(f"  Uploading {fname}...")
        try:
            url = upload_image(fname)
            image_urls[fname] = url
            print(f"    OK: {url[:80]}...")
        except Exception as e:
            print(f"    FAILED: {e}")

    # Step 2: Delete old text-only posts
    print("\n=== Deleting old text-only posts ===")
    deleted = delete_old_posts()
    print(f"  Deleted {deleted}/{len(OLD_POST_IDS)}")

    # Step 3: Schedule new posts with images on all platforms
    print("\n=== Scheduling posts on LinkedIn + Instagram + Facebook ===")
    for post in POSTS:
        public_url = image_urls.get(post["image"])
        if not public_url:
            print(f"  SKIP {post['title']} — no image uploaded")
            continue
        status, result = schedule_post(post, public_url)
        label = "OK" if status in (200, 201) else "FAIL"
        print(f"  [{label} {status}] {post['scheduledFor'][:10]} — {post['title']}")
        if status not in (200, 201):
            print(f"    {json.dumps(result, indent=2)[:200]}")

    print("\nDone.")
