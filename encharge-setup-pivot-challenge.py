"""
Encharge automation setup for the 7-Day IMG Pivot Challenge.

Creates sequence, emails, and automation routing to convert cold leads
into a warm email nurture audience for Fear Audit and Courage to Choose upsells.
"""
from __future__ import annotations
import os, requests, json
from datetime import datetime, timedelta

ENCHARGE_KEY = os.getenv("ENCHARGE_API_KEY")
ENCHARGE_BASE = "https://api.encharge.io/v1"
HDR = {"X-Encharge-Token": ENCHARGE_KEY, "Content-Type": "application/json"}

# Email bodies from 7day-pivot-challenge.md
EMAILS = [
    {
        "slug": "day-0",
        "subject": "Day 1: Your IMG Pivot Challenge Starts Now (The 1 Question That Changes Everything)",
        "body": """Hey there,

Welcome to the **7-Day IMG Pivot Challenge**.

You're reading this because you know something's wrong with the plan.

Failed CaRMS. Lab assistant salary. Family WhatsApp messages asking when you'll be "Dr." Finally, at 2am, you Googled something different.

Over the next 7 days, I'm going to walk you through the question that breaks the paralysis.

It's not "How do I pass CaRMS again?"

It's something better.

**Today's challenge** (takes 5 minutes):

Answer this one question honestly in your head:

*"If I knew for certain that CaRMS was never happening, what would I actually want to do?"*

Don't overthink it. Just feel the answer.

Tomorrow, I'll show you why that answer is the map you've been looking for.

You've got this.

—Sahawat
Crossing Guard, IMG Pivot Guide, Former Physician

P.S. — This challenge is free because I remember that panic. I became a crossing guard and found something better than residency. I want you to find your version of that too.""",
        "delay_minutes": 0,
    },
    {
        "slug": "day-1",
        "subject": "Day 2: The Question Isn't \"How Do I Stay?\" (It's \"Why Do I Feel Stuck?\")",
        "body": """Hey,

Yesterday I asked you: *"If CaRMS was never happening, what would I actually want to do?"*

Did you answer it?

Here's what I've learned from 200+ unmatched IMGs: **the real question isn't how to pass the next match.**

The real question is: **Why does staying in this limbo cost more than switching?**

Think about it:

- $48K salary (when you could earn $65K+ in non-clinical roles)
- 4+ years of "maybe next time" (when you could be building a career that pays now)
- Family pressure (when you could reframe what "success" actually means)
- Sunk cost shame (when you could turn it into a bridge to something better)

**The math nobody talks about:**

If you're unmatched and you stay in clinical purgatory for 2 more years:
- Lost income: ~$50K
- Emotional tax: immeasurable
- Delay in building a stable life: real

If you pivot to a non-clinical IMG role TODAY:
- $65K+ starting salary
- Stability in 30 days
- A career that actually values your MD/MBBS

**Your challenge today:**

Calculate your real cost of staying. Be honest:
- Lost salary vs. clinical roles
- Years waiting vs. certainty
- What you're sacrificing to stay in the loop

The answer isn't "switch immediately."

The answer is: **you deserve to know the real cost before you decide.**

Tomorrow, I'll show you the 4 paths that actually exist (that nobody tells you about).

—Sahawat""",
        "delay_minutes": 1440,
    },
    {
        "slug": "day-2",
        "subject": "Day 3: The 4 Paths Nobody Tells Unmatched IMGs Exist",
        "body": """Hey,

Here's what a recruiter told me after I left medicine:

"Sahawat, you didn't fail at residency. The system failed to value what you actually bring."

That stuck with me.

Today I'm showing you the 4 paths that actually exist for unmatched IMGs in Canada.

**PATH 1: Clinical Research Coordinator**
- Salary: $75K starting
- Your qualification: Your clinical background is GOLD here
- Timeline: Hire in 30-60 days
- Why IMG-friendly: They WANT MDs/MBBS who understand the science

**PATH 2: Lab Director or Senior Technician**
- Salary: $65K-$85K
- Your qualification: You understand pathology, microbiology, chemistry at a depth most techs don't
- Timeline: Hire in 60-90 days
- Why IMG-friendly: Leadership requires medical training; you have it

**PATH 3: Medical Education Coordinator**
- Salary: $68K starting, goes to $85K+
- Your qualification: You've navigated the medical system; universities need someone who understands IMG challenges
- Timeline: Hire in 45 days
- Why IMG-friendly: Your lived experience is exactly what they want

**PATH 4: Regulatory Affairs (Medical Boards)**
- Salary: $72K starting
- Your qualification: Your credential makes you credible reviewing credentials
- Timeline: Hire in 60 days
- Why IMG-friendly: You speak the language of medical licensing

**The pattern:**

All 4 paths:
- Pay $65K+
- Hire IMG doctors
- Don't require another exam
- Start within 90 days

**Your challenge today:**

Which path makes you think "wait, that could actually work"?

Just pick one. You don't have to commit. Just let yourself imagine it for 2 minutes.

Tomorrow, I'll show you the one thing that's actually stopping you from picking a path.

—Sahawat""",
        "delay_minutes": 2880,
    },
    {
        "slug": "day-3",
        "subject": "Day 4: Why You Haven't Switched Yet (And It's Not What You Think)",
        "body": """Hey,

I asked 47 unmatched IMGs: "Why haven't you pivoted to a clinical research or lab director role?"

The answers weren't "I can't get hired."

They were:

- "What if I regret it?"
- "My parents will think I gave up"
- "I feel like a failure if I'm not a doctor"
- "Everyone would know I didn't match"
- "I'm too far into this to switch"

**These aren't reasons. They're stories.**

And stories are powerful. They keep you in $48K limbo while better options exist.

Here's the truth nobody says out loud:

**Switching is not failing. Staying in a system that doesn't work is.**

I was a physician for 3 years. Top of my class. Then I became a crossing guard.

My parents didn't understand at first.

But you know what changed? When I stopped asking for permission.

When I said: "I get to choose what success looks like for me."

That's the real pivot.

Not the job change. The story change.

**Your challenge today:**

What story are you telling yourself about why you can't switch?

Write it down. Just one sentence.

"I haven't switched because _______________."

Tomorrow, I'm going to show you that story isn't true.

—Sahawat""",
        "delay_minutes": 4320,
    },
    {
        "slug": "day-4",
        "subject": "Day 5: Permission Doesn't Come From Your Board (It Comes From You)",
        "body": """Hey,

Here's what I learned on the corner in a yellow vest:

**Permission doesn't come from credentials.**

It comes from the moment you decide you're worth protecting.

I'm not a doctor anymore. I'm a crossing guard.

And I've never felt more legitimate in my life.

Because I made a choice that was right for me.

**Here's what I'm hearing from IMG pivots:**

- "When I stopped trying to be a doctor, I actually became valuable to employers"
- "The moment I said YES to lab director, everything changed"
- "Leaving residency hunt was the best decision I made"

**The pattern:**

Permission to pivot = permission to choose yourself.

And unmatched IMGs? You've already done the hardest part.

You've survived:
- Medical school in another country
- Licensing exams in a second language
- CaRMS rejection
- The shame of "failure"

And you're STILL standing.

That's not failure. That's resilience.

**Your challenge today:**

Say this out loud (seriously, actually say it):

"I give myself permission to choose a path that works for me."

Feel different? That's the moment everything shifts.

Tomorrow, I'm showing you the 30-day action plan to actually make this real.

—Sahawat""",
        "delay_minutes": 5760,
    },
    {
        "slug": "day-5",
        "subject": "Day 6: Your 30-Day IMG Pivot Playbook (The Exact Steps)",
        "body": """Hey,

You've made it to Day 6. That means you're actually considering this.

Here's the 30-day map to pivot:

**DAYS 1-7: Clarify**
- Pick ONE path from the 4 I showed you
- Talk to 2 people in that role (LinkedIn message them)
- Understand the actual day-to-day

**DAYS 8-14: Polish**
- Update your LinkedIn to highlight IMG credibility
- Rewrite your resume for that role (not residency, not clinical)
- Get 1 LinkedIn recommendation from someone in that field

**DAYS 15-21: Apply**
- Target 5-10 companies that hire for that role
- Customize your cover letter (show you understand their needs)
- Apply to all of them

**DAYS 22-30: Close**
- Follow up on applications
- Do interviews
- Get the offer

**The reality:**

Clinical research and lab director positions hire IMG doctors ALL THE TIME.

They're not gatekept by LMCC or CaRMS.

They're gatekept by "do you understand this role + can we trust you?"

Your IMG credential actually helps with both.

**Your challenge today:**

Which path are you actually going to pursue?

Write it down. Commit to it.

Tomorrow is the last email of this challenge. And it's the most important one.

—Sahawat""",
        "delay_minutes": 7200,
    },
    {
        "slug": "day-6",
        "subject": "Day 7: Here's What Happens Next (Your Real Next Step)",
        "body": """Hey,

You made it through the 7-Day IMG Pivot Challenge.

That means you've:
- ✓ Answered the real question
- ✓ Calculated your true cost
- ✓ Seen the 4 paths
- ✓ Identified the story stopping you
- ✓ Gave yourself permission
- ✓ Made a 30-day plan
- ✓ Picked your path

Now comes the part where most people stall.

They know what to do. But they don't know how to actually do it.

**That's what I built the Fear Audit for.**

It's a 5-minute assessment that shows you:
- Which of the 4 paths matches YOUR strengths (not just salary)
- The 3 hidden fears blocking your pivot (and how to break them)
- Your personalized 90-day action plan

→ **[Access Fear Audit - Free](https://fear-audit.vercel.app)**

But here's what happens after you take it:

You get a detailed report showing your IMG Pivot Path.

And if you want the deeper work (the one that actually gets you hired), there's **The Courage to Choose** — my complete playbook for IMG career transitions.

**The choice is yours.**

You can:
- A) Keep the 7 days of learning and go solo
- B) Take the Fear Audit and get your personalized path
- C) Go all-in with Courage to Choose and get hired in 90 days

**No judgment either way.**

But I know what changed my life: choosing to be guided instead of figuring it out alone.

See you on the other side.

—Sahawat

P.S. — You're not a failure for not matching. You're unmatched by a broken system. But you're not broken. You just needed permission and a path. You have both now. Use them.""",
        "delay_minutes": 8640,
    },
]


def create_sequence() -> dict:
    """Create the sequence in Encharge."""
    body = {
        "name": "7-Day IMG Pivot Challenge",
        "description": "Free 7-day email course for unmatched IMGs. Lead magnet funnel to Fear Audit and Courage to Choose.",
    }
    r = requests.post(f"{ENCHARGE_BASE}/sequences", headers=HDR, json=body)
    if r.status_code not in (200, 201):
        raise Exception(f"Failed to create sequence: {r.status_code} {r.text}")
    return r.json()


def create_email(sequence_id: str, email_data: dict) -> dict:
    """Create an email in the sequence."""
    body = {
        "subject": email_data["subject"],
        "body": email_data["body"],
        "type": "html",
        "automationDelay": email_data["delay_minutes"],
        "automationDelayUnit": "minutes",
    }
    r = requests.post(
        f"{ENCHARGE_BASE}/sequences/{sequence_id}/emails",
        headers=HDR,
        json=body,
    )
    if r.status_code not in (200, 201):
        raise Exception(f"Failed to create email: {r.status_code} {r.text}")
    return r.json()


def create_tag(tag_name: str) -> dict:
    """Create or fetch a tag."""
    body = {"name": tag_name}
    r = requests.post(f"{ENCHARGE_BASE}/tags", headers=HDR, json=body)
    if r.status_code not in (200, 201):
        # Tag might already exist, try fetching
        r = requests.get(
            f"{ENCHARGE_BASE}/tags",
            headers=HDR,
            params={"name": tag_name},
        )
        if r.status_code != 200:
            raise Exception(f"Failed to create/fetch tag: {r.status_code} {r.text}")
        tags = r.json().get("data", [])
        if not tags:
            raise Exception(f"Tag {tag_name} not found and could not be created")
        return tags[0]
    return r.json()


def main():
    print("=== 7-Day IMG Pivot Challenge: Encharge Automation Setup ===\n")

    try:
        # 1. Create sequence
        print("[1/4] Creating sequence...")
        seq = create_sequence()
        seq_id = seq.get("id")
        print(f"  ✓ Sequence created: {seq_id}\n")

        # 2. Create emails
        print("[2/4] Creating 7 email templates...")
        for i, email in enumerate(EMAILS):
            print(
                f"  [{i+1}/7] {email['slug']}: {email['subject'][:50]}..."
            )
            em = create_email(seq_id, email)
            email["id"] = em.get("id")

        print(f"  ✓ All 7 emails created\n")

        # 3. Create tags
        print("[3/4] Creating tags...")
        tag_entry = create_tag("challenge-joined")
        tag_exit = create_tag("challenge-complete")
        print(f"  ✓ Tags created: {tag_entry.get('name')}, {tag_exit.get('name')}\n")

        # 4. Save sequence ID for future reference
        print("[4/4] Saving configuration...")
        config = {
            "sequence_id": seq_id,
            "sequence_name": "7-Day IMG Pivot Challenge",
            "created_at": datetime.now().isoformat(),
            "emails": [
                {"slug": e["slug"], "id": e.get("id"), "delay_minutes": e["delay_minutes"]}
                for e in EMAILS
            ],
            "tags": {
                "entry": tag_entry.get("name"),
                "exit": tag_exit.get("name"),
            },
            "next_steps": [
                "1. Create landing page with email capture form at /pivotchallenge",
                "2. Set entry trigger: when user submits email form on landing page",
                "3. Add routing: tag 'challenge-joined' on entry, 'challenge-complete' on exit",
                "4. Promote via 100+ scheduled social posts (use provided snippets)",
                "5. Track: opens, clicks to Fear Audit, conversions to $27 PDF",
                "6. Route completers to Fear Audit sequence (IDs 436027-436031)",
            ],
        }

        with open("encharge-pivot-challenge-config.json", "w") as f:
            json.dump(config, f, indent=2)

        print(f"  ✓ Configuration saved to encharge-pivot-challenge-config.json\n")

        # Summary
        print("=" * 60)
        print("\n✓ Encharge automation setup complete\n")
        print("Sequence ID:", seq_id)
        print("7 emails created with the following delays:")
        for e in EMAILS:
            hours = e["delay_minutes"] // 60
            print(f"  • {e['slug']}: {hours}h after signup")

        print("\nNext actions:")
        for step in config["next_steps"]:
            print(f"  → {step}")

    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        raise


if __name__ == "__main__":
    main()
