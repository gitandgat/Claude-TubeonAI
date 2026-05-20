"""
Recover Apr 8 and Apr 17 — missing from Zernio.
Content sourced from schedule-april-calendar.py.
"""
import os
import requests
import time

BASE    = "https://zernio.com/api/v1"
API_KEY = "sk_d1c977cc304ec9685c24f22c7e3b868abd5a10b9db8f7648b2b74384ab1ca399"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

ASSETS = "/Users/toto/Claude TubeonAI/crosswalk-remotion/public/assets/april"

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
YOUTUBE_ID   = "690940d35f6fbb9ef8323077"
TIMEZONE     = "America/New_York"

HASHTAGS_8  = "#FearAudit #HealthcareIdentityCrisis #NurseBurnoutRecovery #LeavingNursing #IdentityCrisis #CareerChangeNurse #NurseBurnout #BurnoutRecovery #CrosswalkWisdom #TheCrosswalkMethod #HealingJourney #NurseTransition #CareerTransition"
HASHTAGS_17 = "#HealthcareBurnout #NurseBurnout #MentalHealth #MoralInjury #CrosswalkWisdom #BurnedOutNurse #NurseLife #HealthcareWorkerBurnout #NurseBurnoutRecovery #LeavingNursing #HealingFromBurnout #HealthcareBurnoutSupport #NurseAdvocate #MentalHealthMatters #NurseTransition"

POSTS = [
    {
        "date": "2026-04-08",
        "image": "freepik__closeup-of-two-hands-gently-cradling-a-hospital-id__52556.jpeg",
        "time": "2026-04-08T09:00:00",
        "yt_title": "Day 8 — Identity Loss Deep Dive",
        "linkedin": """The most dangerous sentence in healthcare:

"I am a nurse."

Not because nursing is dangerous (though it is). But because of two small words: "I am."

Not "I work as." Not "I practice." I AM.

When your job title comes after "I am," it's no longer a profession. It's an identity. And when an identity is threatened, the brain responds the same way it responds to physical danger: fight, flight, or freeze.

This is why so many healthcare professionals stay in careers that are destroying them. Leaving doesn't just feel like a career change. Neurologically, it feels like a threat to survival.

I call this Fear #1: Identity Loss. And in my experience, it's the primary reason talented, intelligent healthcare workers remain stuck in roles they've outgrown.

The antidote isn't finding a new title. It's learning to hold your identity more loosely. To shift from "I am a nurse" to "I am someone who has nursed — and who can now do so much more."

It sounds simple. It's the hardest psychological work most people will ever do.

But it's also the most liberating.

I've built a free tool called the Fear Audit that helps healthcare professionals identify which of the three transition fears is driving their decisions. If Identity Loss resonates with you, it's worth 3 minutes of your time: fear-audit.vercel.app""",
        "instagram": """"Who are you without the title?"

That question haunted me for two years after leaving medicine.

I'd wake up and reach for an identity that wasn't there anymore. Like a phantom limb. I could feel it, but it was gone.

Here's what I've learned since then: Identity Loss is the first fear — and the deepest one. It's the fear underneath all the other fears.

Because you didn't just choose a career. You chose a self. You chose "I am a nurse" the way some people choose "I am a mother" or "I am an artist." It became the lens through which you saw everything.

So when you think about leaving, it doesn't feel like a career change. It feels like dying. Like the person you've been for a decade is being erased.

But here's what the crosswalk taught me: You don't lose yourself when you cross. You find a bigger version of yourself on the other side.

The badge was never your identity. It was a placeholder. The real you has been waiting — on the other side of the street — this whole time.

If Identity Loss is your loudest fear, take the Fear Audit. 3 minutes. Completely free. It'll show you exactly where you are — and what to do next. Link in bio.""",
        "facebook": """Let me tell you about the hardest part of leaving medicine.

It wasn't the pay cut. It wasn't the confusion on people's faces. It wasn't even the self-doubt.

It was the silence.

When you're a doctor, you always know how to answer "what do you do?" When you leave, that question becomes a minefield.

"I'm... figuring things out."
"I'm in transition."
"I used to be a doctor."

Used to be. Past tense. Like a part of you died.

That silence — that gap between who you were and who you haven't become yet — is the most painful part of any career transition. And it's the part nobody prepares you for.

If you're in that silence right now, I want you to know two things:

1. It's temporary.
2. It's necessary.

The silence is the crosswalk. You're between two sides. And the only way through it is to keep walking.""",
        "hashtags": HASHTAGS_8,
    },
    {
        "date": "2026-04-17",
        "image": "freepik__interior-of-a-car-at-dusk-viewed-from-the-drivers-__52550.jpeg",
        "time": "2026-04-17T09:00:00",
        "yt_title": "Day 17 — Parking Lot Criers",
        "linkedin": """I want to talk about a phenomenon I've never seen addressed in any burnout research:

The parking lot cry.

If you've worked in healthcare, you know exactly what I'm talking about. That moment in your car — before or after a shift — when the mask comes off and the tears come.

It's not about one bad thing that happened. It's about the accumulation. The weight of performing wellness while feeling empty. The effort of caring for others while no one asks how you're doing.

I've spoken with hundreds of healthcare professionals. The parking lot cry is nearly universal. And yet nobody talks about it.

Why?

Because in healthcare culture, crying is weakness. Exhaustion is expected. And struggling means you're "not cut out for this."

I want to challenge that narrative directly:

If you're crying in your car, it doesn't mean you're too weak for healthcare. It means healthcare is too extractive for humans.

There's a difference. A crucial one.

The system is designed to take. Your compassion. Your energy. Your weekends. Your identity. And when you break under the weight of constant extraction, the system says the problem is you.

It's not you.

And recognizing that — truly recognizing it — is the first step off the curb.""",
        "instagram": """Parking lot criers, this one's for you.

Because we all know there are two types:

Before-shift criers: You're sitting in your car, staring at the building, trying to summon the energy to go in. The tears come because your body knows something your brain is still fighting: you don't want to be here anymore.

After-shift criers: You made it through. You held it together for 12 hours. You smiled at patients and joked with coworkers and documented everything perfectly. And now, in the safety of your car, you finally let yourself feel how heavy it all was.

Both are valid. Both are telling you something important.

The parking lot has always been healthcare's unofficial therapy office. And if you've spent more time crying in your car than you'd like to admit — you're not weak. You're human.

But here's my gentle question: How many more parking lot sessions before you listen to what the tears are trying to tell you?

Which one are you? Before or after? Or the rare and impressive "both"?

Comment below. No judgment. Just solidarity.""",
        "facebook": """Friday confessional:

Tell me your best/worst parking lot cry story. Or bathroom cry. Or supply closet cry. We all have one.

I'll start: Mine was after a 14-hour day. I got to my car, put the key in the ignition, and just... didn't turn it. I sat there for 45 minutes staring at the dashboard. No music. No phone. Just sitting with the realization that I couldn't remember the last time I felt like myself.

That was the day I started thinking about the crosswalk.

What was your moment?""",
        "hashtags": HASHTAGS_17,
    },
]


def upload_image(filename):
    filepath = os.path.join(ASSETS, filename)
    filesize = os.path.getsize(filepath)
    ext = filename.rsplit(".", 1)[-1].lower()
    content_type = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    r = requests.post(f"{BASE}/media/presign", headers=HEADERS,
        json={"filename": filename, "contentType": content_type, "fileSize": filesize})
    r.raise_for_status()
    data = r.json()
    with open(filepath, "rb") as f:
        requests.put(data["uploadUrl"], data=f, headers={"Content-Type": content_type}).raise_for_status()
    return data["publicUrl"]


def create_post(p, image_url):
    ig_content = p["instagram"] + "\n\n" + p["hashtags"]
    yt_content = p["linkedin"] + "\n\n#Shorts #CrosswalkWisdom #HealthcareBurnout #NurseBurnout #CareerTransition"

    body = {
        "content": p["linkedin"],
        "mediaItems": [{"url": image_url, "type": "image"}],
        "scheduledFor": p["time"],
        "timezone": TIMEZONE,
        "platforms": [
            {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": p["linkedin"],  "scheduledFor": p["time"]},
            {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": ig_content,     "scheduledFor": p["time"]},
            {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": p["facebook"],  "scheduledFor": p["time"]},
            {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": ig_content,     "scheduledFor": p["time"]},
        ],
    }
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    return r.status_code, r.text[:200]


def main():
    print("Recovering Apr 8 and Apr 17...\n")
    for p in POSTS:
        print(f"  {p['date']} — {p['yt_title']}")
        print(f"    Uploading {p['image']}...")
        image_url = upload_image(p["image"])
        print(f"    Uploaded → ...{image_url[-40:]}")
        status, resp = create_post(p, image_url)
        if status in (200, 201):
            print(f"    ✓ Scheduled at {p['time']}")
        else:
            print(f"    ✗ Failed {status}: {resp}")
        time.sleep(1)
    print("\nDone.")


if __name__ == "__main__":
    main()
