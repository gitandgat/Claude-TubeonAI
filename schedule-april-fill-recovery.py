"""
Recovery: April 2026 Gap Fill — 12 failed posts
Posts IG + FB + TT only (LinkedIn already at 5/day cap for these dates).
Dates: Apr 7 19:00, Apr 9 07:00+13:00, Apr 13 13:00, Apr 14 19:00,
       Apr 16 19:00, Apr 18 19:00, Apr 21 19:00, Apr 23 19:00,
       Apr 25 19:00, Apr 28 19:00, Apr 30 19:00
"""
import os
import time
import requests

BASE    = "https://zernio.com/api/v1"
API_KEY = "sk_d1c977cc304ec9685c24f22c7e3b868abd5a10b9db8f7648b2b74384ab1ca399"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
TIMEZONE     = "America/New_York"

ASSETS = "/Users/toto/Claude TubeonAI/crosswalk-remotion/public/assets/april"

IMAGES = {
    "scrubs":    f"{ASSETS}/freepik__a-pair-of-folded-blue-hospital-scrubs-resting-neat__52543.jpeg",
    "hospital":  f"{ASSETS}/freepik__a-person-sitting-alone-in-a-softly-lit-hospital-co__52553.jpeg",
    "crosswalk": f"{ASSETS}/freepik__cinematic-shot-of-a-person-walking-across-a-wet-ci__52554.jpeg",
    "signal":    f"{ASSETS}/freepik__a-city-pedestrian-traffic-signal-light-changing-fr__52547.jpeg",
    "clipboard": f"{ASSETS}/freepik__a-clean-warm-flatlay-of-a-clipboard-with-a-white-n__52549.jpeg",
    "car":       f"{ASSETS}/freepik__interior-of-a-car-at-dusk-viewed-from-the-drivers-__52550.jpeg",
    "laptop":    f"{ASSETS}/freepik__a-persons-hands-typing-on-a-laptop-at-a-cozy-woode__52557.jpeg",
    "table":     f"{ASSETS}/freepik__overhead-flatlay-of-a-warm-wooden-table-with-an-op__52558.jpeg",
    "hands_lap": f"{ASSETS}/freepik__closeup-of-a-persons-hands-resting-on-an-open-lapt__52544.jpeg",
}

# Failed posts: (date, time, img_key, ig_copy, fb_copy, tt_copy)
FAILED = [
    # Apr 7 19:00 — eve/1 (Burnout Assessment stages)
    ("2026-04-07", "19:00", "crosswalk",
     """One of the questions on the Crosswalk Burnout Assessment reads:

"I've stopped imagining a future."

If that sentence landed — you already know which stage you're in.

Burnout isn't yes or no. It's a location. And the location determines what you actually need.

4 stages. 12 questions. 2 minutes. Free.

Built for healthcare workers.

Link in bio — or first comment.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #NurseBurnout #BurnoutRecovery #BurnoutStages""",
     """One of the questions on the Crosswalk Burnout Assessment reads: "I've stopped imagining a future."

If that sentence landed somewhere in you — you already know which stage you're in.

Burnout isn't a yes or no. It's a location. The location determines what you actually need right now.

Free 12-question assessment. Places you in one of four stages. Gives you the specific next step for where you are — not a generic list.

2 minutes. Free. Link in the comments.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery #BurnoutStages #HealthcareWorkers""",
     """One question on the Crosswalk Burnout Assessment:

"I've stopped imagining a future."

If that sentence landed — you already know which stage you're in.

4 stages. 12 questions. 2 minutes. Free.

Link in bio.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #BurnoutStages #BurnoutRecovery"""),

    # Apr 9 07:00 — morning/4 (signal light)
    ("2026-04-09", "07:00", "signal",
     """There's a moment before burnout breaks through.

Most people miss it.

It's when helping starts to feel like draining. When you're doing everything right — but something underneath is running on empty.

The light is yellow, not red.

You still have time to do something different.

Are you paying attention?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss""",
     """There's a moment before burnout fully breaks through. Most people miss it.

It's when helping starts to feel like draining. When you're showing up and staying late and doing everything right — but something underneath is running on empty.

That's not weakness. That's a warning signal. The light is yellow, not red.

Which means there's still time to do something different.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #HealthcareWorkers""",
     """There's a moment before burnout breaks through.

Most people miss it.

Helping starts to feel like draining.

The light is yellow, not red. You still have time.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery"""),

    # Apr 9 13:00 — main/0 (crosswalk metaphor)
    ("2026-04-09", "13:00", "crosswalk",
     """The crosswalk metaphor.

On one side: who you've been. The career. The identity. The certainty of who you are in scrubs.

On the other: something you can't fully see yet.

Most people never step off the curb. They wait for the light to already be green.

The light doesn't work that way.

The courage to cross comes from stepping forward — and watching it change as you move.

#CrosswalkWisdom #HealthcareBurnout #IdentityLoss #CourageToChoose #CareerTransition #BurnoutRecovery""",
     """The crosswalk metaphor.

You're standing on one side. The career, the identity, the certainty of who you are when you walk into a room in scrubs.

On the other side: something you can't fully see yet.

Most people never step off the curb. They wait for the light to already be green before they move.

The light doesn't work that way.

The courage to cross comes from stepping forward — and watching it change as you move.

That's all of it.

#CrosswalkWisdom #HealthcareBurnout #IdentityLoss #CourageToChoose #CareerTransition #BurnoutRecovery""",
     """The crosswalk metaphor.

One side: who you've been.
Other side: something you can't see yet.

Most people wait for the light to already be green.

The light doesn't work that way.

The courage to cross comes from stepping forward first.

#CrosswalkWisdom #HealthcareBurnout #IdentityLoss #CourageToChoose #BurnoutRecovery"""),

    # Apr 13 13:00 — main/1 (override yourself)
    ("2026-04-13", "13:00", "hospital",
     """Healthcare trains you to override yourself.

Hold it through the shift. Eat later. Be the one who doesn't complain.

You got so good at overriding the signal that you forgot it was a signal.

The fatigue. The numbness. The parking lot cry before a shift.

That wasn't weakness. That was your nervous system sending a message you'd learned to ignore.

The body always keeps the score.

Are you listening to yours?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #HealthcareWorkers #IdentityLoss""",
     """Healthcare trains you to override yourself.

Hold it through the shift. Eat later. Sleep when it's over. Be the one who doesn't complain.

You got so good at overriding the signal that you forgot it was a signal.

The fatigue. The numbness. The parking lot cry before the shift starts. That wasn't weakness — it was your nervous system sending a message you'd learned to ignore.

The body always keeps the score. Even when the mind has moved on.

Are you listening to it?

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
     """Healthcare trains you to override yourself.

Hold it. Eat later. Be the one who doesn't complain.

You got so good at ignoring the signal you forgot it was a signal.

The body always keeps the score.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery"""),

    # Apr 14 19:00 — eve/6 (burnout recovery starting point)
    ("2026-04-14", "19:00", "car",
     """Burnout recovery has a specific starting point.

Not a habit change. Not a career pivot. Not a meditation practice.

A name.

The name of what's been keeping you stuck.

Most burned-out healthcare workers have never had that name spoken to them.

Without it, every intervention is a guess.

Two free assessments. Two minutes each. Link in bio.

#CrosswalkWisdom #FearAudit #BurnoutAssessment #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss""",
     """Burnout recovery has a specific starting point.

Not a habit change. Not a career pivot. Not a meditation practice.

A name.

The name of the thing that has been keeping you stuck.

Most burned-out healthcare professionals have never had that name spoken to them. They know something is wrong. But without it, every intervention is a guess.

I built two free assessments to give you that name. Two minutes each. Link in the comments.

#CrosswalkWisdom #FearAudit #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery #IdentityLoss""",
     """Burnout recovery has a specific starting point.

Not a habit change. Not a career pivot.

A name.

The name of what's been keeping you stuck.

Two free assessments. Two minutes. Link in bio.

#CrosswalkWisdom #FearAudit #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery"""),

    # Apr 16 19:00 — eve/0 (Fear Audit intro)
    ("2026-04-16", "19:00", "clipboard",
     """Something I built for exactly this moment.

The Fear Audit. Free. 2 minutes.

It identifies which fear has been driving your decisions:

→ Financial Insecurity
→ Fear of Judgment
→ Identity Loss

Each sounds the same. They require completely different first steps.

Most burned-out healthcare workers have never had their specific fear named out loud.

That name is where recovery starts.

Link in bio — or first comment.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss""",
     """If any of this has been landing — I built something for exactly this moment.

The Fear Audit. Free. 2 minutes. 12 questions.

It tells you which of three fears has been driving your decisions: financial insecurity, fear of judgment, or identity loss.

Each one sounds the same on the surface. But they require completely different first steps. Most burned-out healthcare professionals have never had their specific fear named out loud.

That name is where recovery actually starts. Link in the comments.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
     """Something I built for exactly this moment.

The Fear Audit. Free. 2 minutes.

Names which fear has been making your decisions:

→ Financial insecurity
→ Fear of judgment
→ Identity loss

That name is where recovery starts.

Link in bio.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #BurnoutRecovery #IdentityLoss"""),

    # Apr 18 19:00 — eve/2 (Identity Loss most common)
    ("2026-04-18", "19:00", "laptop",
     """The Fear Audit has been taken by hundreds of healthcare workers.

The most common result? Identity Loss.

"If I'm not the person who handles everything — who am I?"

That fear looks like dedication from the outside. From the inside, it feels like a cage you can't find the door to.

The assessment names it. And naming it is the only first move that works.

Free. 2 minutes. Link in bio.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #NurseBurnout #IdentityLoss #BurnoutRecovery""",
     """The Fear Audit has been taken by hundreds of healthcare workers.

The most common result? Identity Loss.

"If I'm not the person who handles everything, who am I?"

That fear looks like dedication from the outside. From the inside, it feels like a cage you can't find the door to.

The assessment doesn't fix that. But it names it — and naming it is the first move that actually works.

Free. 2 minutes. Link in the comments.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #IdentityLoss #BurnoutRecovery #HealthcareWorkers""",
     """The Fear Audit's most common result?

Identity Loss.

"Who am I if I'm not the person who handles everything?"

Looks like dedication from the outside. Feels like a cage from the inside.

Naming it is the first move.

Free. 2 mins. Link in bio.

#CrosswalkWisdom #FearAudit #IdentityLoss #HealthcareBurnout #BurnoutRecovery"""),

    # Apr 21 19:00 — eve/4 (Two tools)
    ("2026-04-21", "19:00", "hands_lap",
     """Two free tools. Two minutes each.

Fear Audit — which fear has been making your decisions.
Burnout Assessment — which stage you're in and the specific next step.

Different tools. Both free. Both 2 minutes.

Most people who take both say: "I didn't realize that was what this was."

That's exactly the point.

Links in bio — or first comment.

#CrosswalkWisdom #FearAudit #BurnoutAssessment #HealthcareBurnout #NurseBurnout #BurnoutRecovery""",
     """Two free tools. Two minutes each.

The Fear Audit: tells you which fear has been making your decisions — financial insecurity, fear of judgment, or identity loss.

The Burnout Assessment: tells you which of 4 stages you're in and gives you the specific next step for exactly where you are.

Different tools. Both free. Both 2 minutes.

Most people who take both say the same thing: "I didn't realize that was what this was."

That's exactly the point. Links in the comments.

#CrosswalkWisdom #FearAudit #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery #IdentityLoss""",
     """Two free tools. Two minutes each.

Fear Audit: which fear has been making your decisions.

Burnout Assessment: which stage you're in + specific next step.

Most people: "I didn't realize that was what this was."

That's the point. Links in bio.

#CrosswalkWisdom #FearAudit #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery"""),

    # Apr 23 19:00 — eve/6 (tired of reading about burnout)
    ("2026-04-23", "19:00", "scrubs",
     """For the healthcare worker tired of reading about burnout without anything changing.

The problem isn't information. You have information.

The problem is it doesn't know what you're afraid of.

The Fear Audit names your specific fear:

→ Financial insecurity
→ Fear of judgment
→ Identity loss

That name tells you what first step works for you. Not everyone. You.

2 minutes. Free. Link in bio.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss""",
     """For the healthcare worker who is tired of reading about burnout without anything actually changing.

The problem isn't information. You have information. The problem is that information lands differently when it doesn't know what you're afraid of.

The Fear Audit gives you the specific name of your fear: financial insecurity, fear of judgment, or identity loss.

That name tells you what first step actually works for you — not for everyone, for you.

2 minutes. Free. Link in the comments.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
     """For the healthcare worker tired of reading about burnout without anything changing.

The problem isn't information.

It's that information doesn't know what you're afraid of.

The Fear Audit names your specific fear.

2 minutes. Free. Link in bio.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #NurseBurnout #BurnoutRecovery"""),

    # Apr 25 19:00 — eve/0 (Fear Audit intro)
    ("2026-04-25", "19:00", "clipboard",
     """Something I built for exactly this moment.

The Fear Audit. Free. 2 minutes.

Financial Insecurity. Fear of Judgment. Identity Loss.

Each one requires a completely different first step.

Most burned-out healthcare workers have never had their specific fear named out loud.

That name is where recovery starts.

Link in bio.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss""",
     """I built something for exactly this moment.

The Fear Audit. Free. 2 minutes. 12 questions.

Financial insecurity, fear of judgment, or identity loss — which fear has been driving your decisions?

Each one sounds similar on the surface. They require completely different first steps.

Most burned-out healthcare professionals have never had their specific fear named out loud. That name is where recovery actually starts. Link in the comments.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
     """Built for exactly this moment.

The Fear Audit. Free. 2 minutes.

Names which fear has been making your decisions.

That name is where recovery starts.

Link in bio.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #BurnoutRecovery #IdentityLoss"""),

    # Apr 28 19:00 — eve/2 (Identity Loss most common - variant)
    ("2026-04-28", "19:00", "table",
     """I want to ask you something before you end your day.

How long have you known something needed to change?

Not suspected. Known.

For most healthcare workers, the honest answer is months. Sometimes years.

The knowing doesn't feel like a decision point — it feels like background noise you push past every day.

You have the courage to act. It just needs a starting point.

Link in bio.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery #IdentityLoss #CourageToChoose""",
     """Before you end your day — how long have you known something needed to change?

Not suspected. Known.

For most healthcare workers, the honest answer is months. Sometimes years.

The knowing doesn't feel like a decision point — it feels like background noise you push past every day.

The fear isn't that you don't know what to do. It's that knowing requires acting. And acting requires courage you're not sure you have.

You have it. It just needs a starting point. Link in the comments.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery #IdentityLoss #CourageToChoose""",
     """Before you end your day — one question.

How long have you known something needed to change?

Not suspected. Known.

Most healthcare workers: months. Sometimes years.

You have the courage to act. It just needs a starting point.

Link in bio.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery #IdentityLoss"""),

    # Apr 30 19:00 — eve/4 (Two tools - variant)
    ("2026-04-30", "19:00", "laptop",
     """Before this month ends — one question.

What would it mean to give yourself permission to just start?

Not to have it figured out. Not to be recovered. Not to be ready.

Just to acknowledge where you are and take one honest step from there.

That's the crosswalk. Not the destination — the willingness to step off the curb.

Link in bio if you need a starting point.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #NurseBurnout #BurnoutRecovery #CourageToChoose #IdentityLoss""",
     """Before this month ends — one question.

What would it mean to give yourself permission to just start?

Not to have it figured out. Not to be recovered. Not to be ready.

Just to acknowledge where you are and take one honest step from there.

That's the whole crosswalk metaphor. Not the destination — the willingness to step off the curb.

If you're not sure where to start, I built something that can help. Free. 2 minutes. Link in the comments.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery #CourageToChoose #IdentityLoss""",
     """Before this month ends — one question.

What would it mean to give yourself permission to just start?

Not to be recovered. Not to be ready.

Just — acknowledge where you are and take one honest step.

That's the crosswalk.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery #CourageToChoose"""),
]


_url_cache = {}

def upload_image(img_key):
    filepath = IMAGES[img_key]
    if filepath in _url_cache:
        return _url_cache[filepath]
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    print(f"    Presigning {filename} ({filesize:,} bytes)...")
    r = requests.post(
        f"{BASE}/media/presign",
        headers=HEADERS,
        json={"filename": filename, "contentType": "image/jpeg", "fileSize": filesize},
    )
    r.raise_for_status()
    data = r.json()
    upload_url = data["uploadUrl"]
    public_url = data["publicUrl"]
    with open(filepath, "rb") as f:
        put_r = requests.put(upload_url, data=f, headers={"Content-Type": "image/jpeg"})
        put_r.raise_for_status()
    print(f"    Upload OK → {public_url[:70]}...")
    _url_cache[filepath] = public_url
    return public_url


def schedule_post(image_url, ig_copy, fb_copy, tt_copy, scheduled_for):
    platforms = [
        {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": ig_copy, "scheduledFor": scheduled_for},
        {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": fb_copy, "scheduledFor": scheduled_for},
        {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": tt_copy, "scheduledFor": scheduled_for},
    ]
    body = {
        "content": ig_copy,
        "mediaItems": [{"url": image_url, "type": "image"}],
        "platforms": platforms,
        "scheduledFor": scheduled_for,
        "timezone": TIMEZONE,
    }
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    return r.status_code, r.text[:200]


def main():
    print("=== April Recovery — 12 posts, IG+FB+TT only (LinkedIn at daily cap) ===\n")
    ok = 0
    fail = 0

    for idx, row in enumerate(FAILED, 1):
        date, time_slot, img_key, ig_copy, fb_copy, tt_copy = row
        scheduled_for = f"{date}T{time_slot}:00"
        print(f"[{idx:02d}/12] {date} {time_slot}")

        try:
            image_url = upload_image(img_key)
            status, resp = schedule_post(image_url, ig_copy, fb_copy, tt_copy, scheduled_for)
            if status in (200, 201):
                print(f"  ✓ Scheduled (IG+FB+TT)")
                ok += 1
            else:
                print(f"  ✗ Status {status}: {resp}")
                fail += 1
        except Exception as e:
            print(f"  ✗ Exception: {e}")
            fail += 1

        time.sleep(0.8)

    print(f"\n=== Done: {ok} scheduled, {fail} failed ===")


if __name__ == "__main__":
    main()
