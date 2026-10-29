"""
Schedule: Crosswalk Wisdom — May 8–21, 2026 — 5 Posts/Day
Times: 7am · 10am · 1pm · 4pm · 7pm ET
Platforms: LinkedIn, Instagram, Facebook, TikTok (image posts — YouTube excluded)

Week 2 (May 8–14): "The Crossing" — origin story + crossing guard philosophy
Week 3 (May 15–21): "The Three Fears" — Fear Audit framework + assessment CTAs

NOTE: May 11 & 18 already have a 7pm post in Zernio — those slots are skipped.
"""
import os, time, requests

BASE    = "https://zernio.com/api/v1"
from zernio_key import ZERNIO_API_KEY as API_KEY
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
TZ = "America/New_York"

ASSETS = "/Users/toto/Claude TubeonAI/crosswalk-remotion/public/assets"

IMG = {
    "morning":      f"{ASSETS}/post-naming-fear.jpg",
    "educational":  f"{ASSETS}/april/freepik__a-persons-hands-typing-on-a-laptop-at-a-cozy-woode__52557.jpeg",
    "engagement":   f"{ASSETS}/april/freepik__a-city-pedestrian-traffic-signal-light-changing-fr__52547.jpeg",
    "cta_fear":     f"{ASSETS}/post-fear-audit-intro.jpg",
    "cta_stages":   f"{ASSETS}/post-four-stages.jpg",
    "yellow_vest":  f"{ASSETS}/bg-tiktok-yellow-vest.jpg",
    "crosswalk":    f"{ASSETS}/april/freepik__cinematic-shot-of-a-person-walking-across-a-wet-ci__52554.jpeg",
    "nobody_tells": f"{ASSETS}/bg-carousel-nobody-tells-you.jpg",
    "badge":        f"{ASSETS}/april/freepik__closeup-of-two-hands-gently-cradling-a-hospital-id__52556.jpeg",
    "quitting":     f"{ASSETS}/post-quitting-is-not-failure.jpg",
    "sunk_cost":    f"{ASSETS}/bg-linkedin-sunk-cost.jpg",
    "laptop":       f"{ASSETS}/april/freepik__closeup-of-a-persons-hands-resting-on-an-open-lapt__52544.jpeg",
    "portrait":     f"{ASSETS}/april/freepik__cinematic-portrait-of-a-south-asian-man-in-his-40s__52542.jpeg",
    "scrubs":       f"{ASSETS}/april/freepik__a-pair-of-folded-blue-hospital-scrubs-resting-neat__52543.jpeg",
    "letter":       f"{ASSETS}/april/freepik__a-handwritten-letter-on-cream-textured-paper-lying__52555.jpeg",
    "five_fears":   f"{ASSETS}/post-five-fears.jpg",
}

# ─────────────────────────────────────────────
# SHARED SLOT CONTENT (rotates across days)
# ─────────────────────────────────────────────

# Morning hooks (7am) — 4 variants, cycle by day-of-week
MORNING = [
    {   # A
        "li": """The body knew before the brain did.

The fatigue. The numbness. The parking lot tears before a shift.

That wasn't weakness.

That was your nervous system sending a signal your mind had been trained to ignore.

Burnout isn't a warning to push through.

It's wisdom arriving in the only language that could get through.

What has your body been trying to tell you?

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery #IdentityLoss""",
        "ig": """The body knew before the brain did.

The fatigue. The numbness. The parking lot tears.

Not weakness.

Wisdom — arriving in the only language that could get through.

What has your body been trying to tell you?

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery""",
        "fb": """The body knew before the brain did.\n\nThe fatigue. The numbness. The parking lot tears before a shift.\n\nThat wasn't weakness. That was your nervous system sending a signal your mind had been trained to ignore.\n\nBurnout isn't a warning to push through. It's wisdom arriving in the only language that could get through.\n\nWhat has your body been trying to tell you? I'd love to hear in the comments.""",
        "tt": """The body knew before the brain did.\n\nThe fatigue. The numbness. The parking lot tears.\n\nNot weakness.\n\nWisdom — arriving in the only language that could get through.\n\nWhat has your body been trying to tell you?\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom""",
        "img": "morning",
    },
    {   # B
        "li": """You were a whole person before this career.

Not a degree. Not a title. Not a credential.

A whole person — with curiosity, with fear, with something to give that had nothing to do with patient ratios or shift lengths.

That person didn't disappear.

They got buried.

Burnout is often that person knocking from the inside.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #IdentityLoss #BurnoutRecovery #LeavingMedicine""",
        "ig": """You were a whole person before this career.

Not a degree. Not a title. Not a credential.

A whole person.

That person didn't disappear. They got buried.

Burnout is often that person knocking from the inside.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #IdentityLoss""",
        "fb": """You were a whole person before this career.\n\nNot a degree. Not a title. Not a credential.\n\nA whole person — with curiosity, with fear, with something to give that had nothing to do with patient ratios or shift lengths.\n\nThat person didn't disappear. They got buried.\n\nBurnout is often that person knocking from the inside.\n\nWhat part of yourself have you lost track of?""",
        "tt": """You were a whole person before this career.\n\nNot a degree. Not a title. Not a credential.\n\nThat person didn't disappear. They got buried.\n\nBurnout is often that person knocking from the inside.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #IdentityLoss""",
        "img": "morning",
    },
    {   # C
        "li": """Slowing down is not retreat.

It is reconnaissance.

The healthcare system rewards speed. Faster. More patients. More output. Keep moving.

But the people I've watched make real transitions — the ones who actually get from burned out to building something new — almost always describe a moment of full stop.

Not a vacation. Not a long weekend.

An actual pause.

Where they finally heard themselves think.

What would it mean to stop — just for this week?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #LeavingMedicine""",
        "ig": """Slowing down is not retreat.

It is reconnaissance.

You cannot navigate a crossing you haven't looked at.

What would it mean to stop — just for this week?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery""",
        "fb": """Slowing down is not retreat. It is reconnaissance.\n\nThe healthcare system rewards speed. More patients. More output. Keep moving.\n\nBut the people who make real transitions almost always describe one thing first: an actual pause. Not a vacation. A full stop. Where they finally heard themselves think.\n\nWhat would it mean to slow down — just for this week?""",
        "tt": """Slowing down is not retreat.\n\nIt is reconnaissance.\n\nYou cannot navigate a crossing you haven't looked at.\n\nWhat would it mean to stop — just this week?\n\n#CrosswalkWisdom #HealthcareBurnout #NurseBurnout""",
        "img": "morning",
    },
    {   # D
        "li": """Fear is a map, not a stop sign.

The three fears holding burned-out healthcare workers in place:

Financial Insecurity — "I can't afford to stop."
Fear of Judgment — "What will people think?"
Identity Loss — "I don't know who I am without this."

These fears don't mean you should stay.

They mean something specific about you is at stake — and something specific needs to be addressed first.

Fear is diagnostic. Navigate toward it, not away.

(Link in the first comment — 2-minute quiz that tells you which fear is dominant for you right now.)

#CrosswalkWisdom #HealthcareBurnout #FearAudit #NurseBurnout #IdentityLoss #BurnoutRecovery""",
        "ig": """Fear is a map, not a stop sign.

Three fears keep healthcare workers stuck:

→ Financial Insecurity
→ Fear of Judgment
→ Identity Loss

They don't mean stay. They mean something specific is at stake.

Navigate toward the fear, not away.

Link in bio — free 2-minute quiz.

#CrosswalkWisdom #HealthcareBurnout #FearAudit #NurseBurnout #IdentityLoss""",
        "fb": """Fear is a map, not a stop sign.\n\nThree fears hold burned-out healthcare workers in place:\n\nFinancial Insecurity — "I can't afford to stop."\nFear of Judgment — "What will people think?"\nIdentity Loss — "I don't know who I am without this."\n\nThese fears don't mean you should stay. They mean something specific about you is at stake — and something specific needs to be addressed first.\n\nFear is diagnostic data. Navigate toward it, not away.\n\n(Link in comments — 2-minute quiz to find your dominant fear.)""",
        "tt": """Fear is a map, not a stop sign.\n\nThree fears keep healthcare workers stuck:\n→ Financial Insecurity\n→ Fear of Judgment\n→ Identity Loss\n\nNavigate toward them, not away.\n\nFree 2-minute quiz — link in bio.\n\n#CrosswalkWisdom #HealthcareBurnout #FearAudit #NurseBurnout""",
        "img": "morning",
    },
]

# Educational posts (10am) — 4 variants from 10-things video + assessment content
EDUCATIONAL = [
    {   # ED-A: Saying yes to everything
        "li": """One of the 10 habits that keep burnout in place: saying yes to everything.

Not just at work. To every request, every favor, every invitation.

The automatic yes is a survival strategy. In healthcare, you learned that saying no had consequences — for patients, for your team, for your reputation.

So you stopped asking whether you had the capacity. You just said yes, and figured it out.

Here's the check Dr. Sarah (a burnout coach) recommends before every yes:

Do I have the time for this?
Do I have the energy?
Do I have the attention?
Do I have the resources?
Do I actually want to do this?

If the answer to any of those is no — or even "I'm not sure" — it should probably be a no.

Recovery from burnout starts with recovering the right to say no.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery #Boundaries #HealthcareWorkers""",
        "ig": """Habit #1 that keeps burnout in place: the automatic yes.

Before every commitment, ask:

Do I have the time?
The energy?
The attention?
The resources?
Do I actually want to do this?

If any answer is no — it should be a no.

Recovery from burnout starts with recovering the right to say no.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery #Boundaries""",
        "fb": """One of the 10 habits that keeps burnout in place: saying yes to everything.\n\nNot just at work. To every request, every favor, every invitation.\n\nThe automatic yes is a survival strategy. In healthcare, you learned that saying no had consequences.\n\nHere's a simple check before every yes:\n• Do I have the time?\n• The energy?\n• The attention?\n• The resources?\n• Do I actually want to do this?\n\nIf any answer is no — it should probably be a no.\n\nRecovery from burnout starts with recovering the right to say no.\n\nWhich of these is hardest for you to protect?""",
        "tt": """Habit #1 that keeps burnout in place: the automatic yes.\n\nBefore every commitment, ask:\n\nDo I have the time? Energy? Attention? Resources? Do I actually want to?\n\nIf any answer is no — it should be a no.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery""",
        "img": "educational",
    },
    {   # ED-B: Pushing through exhaustion
        "li": """Another habit that keeps burnout alive: pushing through everything.

Running on 4 hours of sleep. Working while ill. Never taking breaks. Treating rest as a reward instead of a requirement.

This one is particularly insidious in healthcare because the system has trained you to celebrate it.

"She never calls in sick."
"He always covers the extra shift."
"She hasn't taken a vacation in three years."

These are treated as compliments. They're warning signs.

"Make time for your wellness or you'll have to make time for your illness."

Three questions worth sitting with:
Do I need time off right now?
Where can I clear space this week?
What am I overriding that my body is asking for?

You cannot pour from an empty cup. You know this. You say it to patients.

Now say it to yourself.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery #HealthcareWorkers #SelfCare""",
        "ig": """Habit keeping burnout alive: pushing through everything.

Running on no sleep. Working while ill. Treating rest as a reward.

In healthcare, this gets celebrated.
"She never calls in sick."
"He always covers extra shifts."

These are warning signs dressed as compliments.

Make time for your wellness — or you'll have to make time for your illness.

Where can you clear space this week?

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery""",
        "fb": """Another habit that keeps burnout alive: pushing through everything.\n\nRunning on 4 hours of sleep. Working while ill. Never taking breaks. Treating rest as a reward instead of a requirement.\n\nThis is particularly insidious in healthcare because the system celebrates it:\n\n"She never calls in sick." "He always covers the extra shift."\n\nThese are treated as compliments. They're warning signs.\n\n"Make time for your wellness or you'll have to make time for your illness."\n\nWhere can you clear space this week? Tell me in the comments.""",
        "tt": """Habit keeping burnout alive: pushing through everything.\n\nRunning on no sleep. Working while ill.\n\nIn healthcare, this gets celebrated.\n\nBut "she never calls in sick" is a warning sign dressed as a compliment.\n\nMake time for your wellness — or you'll have to make time for your illness.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom""",
        "img": "educational",
    },
    {   # ED-C: Living in constant urgency
        "li": """Sign you might be deeper in burnout than you realize: you've lost the ability to stop rushing.

Not just at work. At home. In the grocery store. Eating. Driving. Doing laundry.

Everything at high speed. Feeling guilty when you're not productive. Unable to actually relax even when you have time.

This is chronic fight-or-flight. Your nervous system has been in emergency mode for so long it's forgotten what normal feels like.

The practice: notice when you're rushing and ask one question.

"Do I really need to rush right now?"

Usually the answer is no. The urgency is internal — a system setting, not a real emergency.

Then — deliberately — slow down. Not dramatically. Just slightly. See what happens.

This tiny act, repeated, is how you start rewiring the nervous system out of emergency mode.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery #NervousSystem #HealthcareWorkers""",
        "ig": """Sign you might be deeper in burnout than you realize: you can't stop rushing.

Not just at work. Everywhere. All the time.

This is chronic fight-or-flight. Your nervous system has been in emergency mode so long it forgot what normal feels like.

The practice: when you notice yourself rushing, ask:

"Do I really need to rush right now?"

Usually no. Then deliberately — just slightly — slow down.

Repeated small acts rewire the nervous system.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery""",
        "fb": """Sign you might be deeper in burnout than you realize: you can't stop rushing.\n\nNot just at work. At home. In the grocery store. Eating. Everything at high speed. Feeling guilty when you're not productive.\n\nThis is chronic fight-or-flight. Your nervous system has been in emergency mode for so long it's forgotten what normal feels like.\n\nThe practice: notice when you're rushing and ask: "Do I really need to rush right now?"\n\nUsually the answer is no. Then deliberately, just slightly, slow down.\n\nThis tiny repeated act is how you start rewiring out of emergency mode. Have you noticed this in yourself?""",
        "tt": """Sign you're deeper in burnout than you realize: you can't stop rushing.\n\nNot just at work. Everywhere. Always.\n\nThis is chronic fight-or-flight.\n\nPractice: when you notice rushing, ask — "Do I really need to rush right now?"\n\nThen deliberately slow down. Just slightly.\n\nRepeat.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery""",
        "img": "educational",
    },
    {   # ED-D: START stage explained
        "li": """The START stage of burnout: what it looks like from the inside.

You're still functioning. Still showing up. Still capable of good days.

But you're noticing things.

A little more dread before some shifts. A little less recovery time between hard weeks. The work that used to fill you is starting to just drain you.

The cracks haven't become canyons yet — but you can see them forming.

This is the most powerful place to be, because awareness is where healing begins. Most people in healthcare ignore these early signals until it's too late.

If you're in the START stage, the move isn't dramatic. It's this:

Write down one thing after your next shift that drained you. And one thing that filled you up.

Awareness, practiced consistently, changes what you notice. And what you notice, you can begin to change.

(The free Burnout Assessment places you in one of 4 stages — link in first comment.)

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery #BurnoutStages #HealthcareWorkers""",
        "ig": """The START stage of burnout: you're still functioning. Still capable of good days.

But the cracks are forming.

A little more dread before some shifts.
A little less recovery between hard weeks.
The work that used to fill you starting to just drain you.

This is the most powerful place to be — because awareness is where healing begins.

After your next shift: write one thing that drained you. One thing that filled you up.

That practice changes everything.

Link in bio — free 2-min assessment.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery #BurnoutStages""",
        "fb": """The START stage of burnout: what it looks like from the inside.\n\nYou're still functioning. Still showing up. Still capable of good days.\n\nBut you're noticing things. A little more dread before some shifts. A little less recovery between hard weeks.\n\nThe cracks haven't become canyons yet — but you can see them forming.\n\nThis is the most powerful place to be, because awareness is where healing begins.\n\nThe move if you're here: write one thing after your next shift that drained you, and one thing that filled you up.\n\nAwareness practiced consistently changes what you notice. And what you notice, you can change.\n\nIs this where you are right now?""",
        "tt": """The START stage of burnout: still functioning, still capable of good days.\n\nBut the cracks are forming.\n\nMore dread. Less recovery. Work that used to fill you starting to drain.\n\nThis is the most powerful place to be — awareness is where healing begins.\n\nPractice: after your next shift, write one thing that drained you. One that filled you.\n\nLink in bio — free burnout assessment.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom""",
        "img": "cta_stages",
    },
]

# Engagement posts (4pm) — 4 variants
ENGAGEMENT = [
    {   # ENG-A
        "li": """A question for healthcare workers:

If you had to describe your current career in three words — not what you wish it was, not what it used to be — what are the three words that actually fit right now?

I'll start with what I hear most often:

Exhausted. Trapped. Going through the motions.

But I've also heard: Reconnecting. Questioning. Waking up.

What are yours?

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #HealthcareWorkers""",
        "ig": """If you had to describe your current career in three words right now — the honest three, not the aspirational ones — what would they be?

Drop them below. 👇

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #NurseLife #HealthcareWorker""",
        "fb": """A question for healthcare workers:\n\nIf you had to describe your current career in three words — the honest three, not what you wish it was — what would they be?\n\nI'll start with what I hear most: "Exhausted. Trapped. Going through the motions."\n\nBut I've also heard: "Reconnecting. Questioning. Waking up."\n\nWhat are yours? No judgment here.""",
        "tt": """Three words. Your career, right now. Honest ones.\n\nDrop them below.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom""",
        "img": "engagement",
    },
    {   # ENG-B
        "li": """Finish this sentence — as honestly as you can:

"The thing I'm most afraid people will think if I change direction in my career is ____________."

(You don't have to answer publicly. But if you're willing — I'm reading every response.)

The fear of judgment is the second most common fear keeping healthcare professionals stuck in burnout. And most people have never said it out loud.

Saying it — even here, in a comment — makes it smaller.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery #FearAudit #HealthcareWorkers""",
        "ig": """Finish this sentence honestly:

"The thing I'm most afraid people will think if I change direction is ____________."

You don't have to answer publicly. But if you're willing — drop it below.

Saying it makes it smaller.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #FearAudit""",
        "fb": """Finish this sentence — as honestly as you can:\n\n"The thing I'm most afraid people will think if I change direction in my career is ____________."\n\nYou don't have to answer publicly. But if you're willing — I'm reading every response.\n\nThe fear of judgment keeps more healthcare professionals stuck than almost anything else. And most people have never said it out loud.\n\nSaying it makes it smaller.""",
        "tt": """Finish this sentence:\n\n"The thing I'm most afraid people will think if I change direction is ____________."\n\nDrop it below. Saying it makes it smaller.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #FearAudit""",
        "img": "engagement",
    },
    {   # ENG-C
        "li": """If you could go back and tell yourself one thing at the start of your healthcare career — what would it be?

Not career advice. Not practical tips.

Something about who you are. Who you'd become. What it would cost.

I'll tell you what mine would have been:

"The career will ask for everything. You don't have to give it."

What's yours?

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #HealthcareWorkers #BurnoutRecovery #LeavingMedicine""",
        "ig": """If you could go back and tell your first-week-in-healthcare self one thing — what would it be?

Not a career tip. Something deeper.

Mine would have been:
"The career will ask for everything. You don't have to give it."

What's yours? 👇

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #NurseLife""",
        "fb": """If you could go back and tell yourself one thing at the start of your healthcare career — what would it be?\n\nNot career advice. Not practical tips. Something about who you are. Who you'd become. What it would cost.\n\nMine would have been: "The career will ask for everything. You don't have to give it."\n\nWhat's yours? I'd genuinely love to hear.""",
        "tt": """What would you tell your first-week-in-healthcare self?\n\nNot a career tip. Something deeper.\n\nMine: "The career will ask for everything. You don't have to give it."\n\nWhat's yours?\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom""",
        "img": "engagement",
    },
    {   # ENG-D
        "li": """Where are you on the crosswalk today?

A) Standing at the curb — not ready to step off yet
B) One foot on the road — I've started but haven't committed
C) Halfway across — no going back, but the other side isn't clear
D) Almost there — I can see where I'm going, but my legs are tired

Drop your letter in the comments.

(If you want to understand your stage more precisely — the free Burnout Assessment is in the first comment. Takes 2 minutes.)

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery #CareerTransition""",
        "ig": """Where are you on the crosswalk today?

A) Still at the curb — watching 🟡
B) One foot on the road 🟠
C) Halfway across, no going back 🔴
D) Almost there, just tired 🟢

Drop your letter below. 👇

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery""",
        "fb": """Where are you on the crosswalk today?\n\nA) Standing at the curb — not ready to step off yet\nB) One foot on the road — I've started but haven't committed\nC) Halfway across — no going back, but the other side isn't clear\nD) Almost there — I can see where I'm going, but my legs are tired\n\nDrop your letter in the comments. I'll share what's most common — and what each stage actually needs.""",
        "tt": """Where are you on the crosswalk today?\n\nA) Still at the curb\nB) One foot on the road\nC) Halfway across\nD) Almost there, just tired\n\nDrop your letter.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom""",
        "img": "engagement",
    },
]

# Evening CTAs (7pm) — 3 variants
EVENING_CTA = [
    {   # CTA-A: Fear Audit
        "li": """Three fears. One quiz. Two minutes.

If you've been reading this week and something landed — this is the practical next step.

The Fear Audit measures which of the three fears is most dominant for you right now:

Financial Insecurity — "I can't afford to stop."
Fear of Judgment — "What will people think?"
Identity Loss — "I don't know who I am without this."

Most people who take it say the same thing: "I've never had this named before."

Named fears are workable. Unnamed fears run your decisions.

Free. 12 questions. 2 minutes. Built for healthcare workers.

Link in the first comment.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #FearAudit #BurnoutRecovery #IdentityLoss #LeavingMedicine""",
        "ig": """Three fears keep healthcare workers stuck.

The Fear Audit tells you which one is running your life.

Financial Insecurity → Fear of Judgment → Identity Loss

Free. 2 minutes. Built for nurses, doctors, and healthcare workers.

Link in bio — or first comment.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #FearAudit #BurnoutRecovery #IdentityLoss""",
        "fb": """Three fears. One quiz. Two minutes.\n\nThe Fear Audit measures which of the three fears is most dominant for you right now:\n\nFinancial Insecurity — "I can't afford to stop."\nFear of Judgment — "What will people think?"\nIdentity Loss — "I don't know who I am without this."\n\nMost people who take it say: "I've never had this named before."\n\nNamed fears are workable. Unnamed fears run your decisions.\n\nFree. Link in comments.""",
        "tt": """Three fears keep healthcare workers stuck.\n\nThe Fear Audit tells you which one is running your life.\n\nFinancial Insecurity → Fear of Judgment → Identity Loss\n\nFree. 2 minutes. Link in bio.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #FearAudit""",
        "img": "cta_fear",
    },
    {   # CTA-B: Burnout Assessment
        "li": """There's a difference between being burned out and knowing what stage you're in.

Knowing the stage changes what you do next.

START: You're noticing the cracks. Awareness is the move.
STOP: You've hit the yellow light. One boundary is the move.
ELDER: You're seeking answers outside yourself. One honest conversation is the move.
HUMAN: The armor has come off. One step forward — with support — is the move.

The free Burnout Assessment places you in your stage and gives you exactly that: one specific next step.

Not a wellness checklist. The actual move for where you are.

Free. 12 questions. 2 minutes.

Link in the first comment.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery #BurnoutAssessment #HealthcareWorkers""",
        "ig": """Knowing your burnout stage changes what you do next.

START → Awareness is the move.
STOP → One boundary is the move.
ELDER → One honest conversation.
HUMAN → One step forward with support.

Free 12-question assessment. 2 minutes.

Link in bio.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery #BurnoutAssessment""",
        "fb": """There's a difference between being burned out and knowing what stage you're in.\n\nKnowing the stage changes what you do next.\n\nSTART: You're noticing the cracks. Awareness is the move.\nSTOP: You've hit the yellow light. One boundary is the move.\nELDER: You're seeking answers outside yourself. One honest conversation is the move.\nHUMAN: The armor has come off. One step forward — with support — is the move.\n\nThe free Burnout Assessment places you in your stage and gives you exactly that.\n\nFree. 12 questions. 2 minutes. Link in comments.""",
        "tt": """Knowing your burnout stage changes what you do next.\n\nSTART → Awareness\nSTOP → One boundary\nELDER → One honest conversation\nHUMAN → One step forward\n\nFree 12-question assessment. 2 minutes.\n\nLink in bio.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutAssessment""",
        "img": "cta_stages",
    },
    {   # CTA-C: Courage to Choose
        "li": """After the assessment — after you've named the fear or found your stage — there's a next question.

Now what?

The Courage to Choose is a $27 guide written for exactly that moment.

Three chapters:
1. Naming the Fear — specificity is the beginning of power
2. Reframing the Story — from "I'm trapped" to "I'm choosing"
3. Taking the First Step — concrete action despite fear

Rooted in Adlerian psychology, Stoic philosophy, and Viktor Frankl's logotherapy.

Written by someone who stood where you're standing and found a way through.

For healthcare professionals who are done with generic wellness advice and ready for a map.

Link in the first comment.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #CourageToChoose #BurnoutRecovery #LeavingMedicine #CareerTransition""",
        "ig": """After you've named the fear — then what?

The Courage to Choose ($27) is the map for that moment.

3 chapters:
Naming the Fear → Reframing the Story → Taking the First Step

Rooted in Adlerian psychology, Stoic philosophy, and Viktor Frankl.

Written by someone who actually made the crossing.

Link in bio.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #CourageToChoose #BurnoutRecovery""",
        "fb": """After the assessment — after you've named the fear or found your stage — there's a next question.\n\nNow what?\n\nThe Courage to Choose is a $27 guide for exactly that moment.\n\nThree chapters: Naming the Fear → Reframing the Story → Taking the First Step\n\nRooted in Adlerian psychology, Stoic philosophy, and Viktor Frankl's logotherapy.\n\nWritten by someone who stood where you're standing and found a way through.\n\nFor healthcare professionals ready for a map, not just a mirror.\n\nLink in comments.""",
        "tt": """Named the fear. Found your stage.\n\nNow what?\n\nThe Courage to Choose ($27) is the map.\n\nNaming → Reframing → First Step\n\nWritten by someone who made the crossing.\n\nLink in bio.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #CourageToChoose""",
        "img": "cta_fear",
    },
]

# ─────────────────────────────────────────────
# DAILY MAIN POSTS (1pm) — unique per day
# ─────────────────────────────────────────────

MAIN_POSTS = {
    "2026-05-08": {
        "img": "yellow_vest",
        "li": """I used to introduce myself as "Dr. Sahawat."

For 20 years, that title was the answer to every question anyone could ask about me.

Then I left medicine.

A few months later, I was standing on a street corner in a fluorescent yellow vest, holding a stop sign, helping first-graders cross the street.

I remember my first morning in that vest. A former colleague drove past. Slowed down. Did not wave.

I felt the shame in my entire body.

But underneath it — something quieter. Something I hadn't felt in years.

Presence. Actual presence.

On day three, a seven-year-old named Marcus walked up and said: "Are you the new crossing guard?"

"Yes."

He nodded slowly, evaluating.

"Cool."

He didn't know I had a degree. He saw exactly what was in front of him.

I have thought about that conversation more than most conversations from my medical career.

The sidewalk taught me things medical school couldn't.

Slowing down is not a demotion. It's an observation post.

And observation is where wisdom begins.

#CrosswalkWisdom #LeavingMedicine #HealthcareBurnout #PhysicianTransition #BurnoutRecovery #IdentityLoss #CareerTransition""",
        "ig": """I went from "Dr. Sahawat" to a crossing guard in a yellow vest.

My first morning on that corner, a former colleague drove past. Slowed down. Did not wave.

I felt the shame in my whole body.

But underneath it — presence. Real presence, for the first time in years.

On day three, seven-year-old Marcus walked up:

"Are you the new crossing guard?"
"Yes."
He nodded. Evaluated.
"Cool."

He didn't know I had a degree. He saw exactly what was in front of him.

That conversation changed how I think about identity.

The sidewalk taught me what medical school couldn't:

Slowing down is not a demotion. It's an observation post.

#CrosswalkWisdom #LeavingMedicine #HealthcareBurnout #PhysicianTransition #IdentityLoss""",
        "fb": """I used to introduce myself as "Dr. Sahawat."\n\nFor 20 years, that title was the answer to every question.\n\nThen I left medicine. A few months later I was in a fluorescent yellow vest, helping first-graders cross the street.\n\nMy first morning, a former colleague drove past. Slowed down. Did not wave.\n\nI felt the shame in my entire body.\n\nBut underneath it — something quieter. Presence. Real presence, for the first time in years.\n\nOn day three, seven-year-old Marcus walked up: "Are you the new crossing guard?" "Yes." He nodded. "Cool."\n\nHe didn't know I had a degree. He saw exactly what was in front of him.\n\nThe sidewalk taught me things medical school couldn't: slowing down is not a demotion. It's an observation post.\n\nHas a small moment ever taught you something enormous? Tell me below.""",
        "tt": """I went from "Dr. Sahawat" to a crossing guard. Here's the one conversation that changed everything.\n\nA seven-year-old named Marcus. Day three. "Are you the new crossing guard?" "Yes." "Cool."\n\nHe didn't know I had a degree. He saw exactly what was in front of him.\n\nSlowing down is not a demotion. It's an observation post.\n\n#CrosswalkWisdom #LeavingMedicine #HealthcareBurnout #IdentityLoss""",
    },
    "2026-05-09": {
        "img": "crosswalk",
        "li": """Three types of people I watch on the crosswalk.

The first type pauses too long at the curb. They see the danger in every crossing, and so they never leave. They make the same risk calculation every morning — stay in the job that's depleting them because the crossing feels more dangerous than the corner.

The second type steps off without looking. They quit fast, move fast, tell themselves the momentum is protection. They find themselves in the middle of the road with no plan and no safety.

The third type crosses with their head down, mid-sentence, too busy surviving the current moment to look at where they're going.

I've recognized all three in healthcare professionals I've talked to.

The crossing guard — standing in the middle of all this — knows one thing the others don't:

The light will change. It always does.

You don't have to sprint. You don't have to freeze. You just have to look up — and cross when it's your time.

Which type are you right now?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #LeavingMedicine #CareerTransition #IdentityLoss""",
        "ig": """Three types of people on the crosswalk:

1. Frozen at the curb — the crossing feels more dangerous than staying
2. Sprinting off without looking — momentum as a substitute for a plan
3. Head down mid-sentence — too busy surviving to see where they're going

I've recognized all three in burned-out healthcare workers.

What the crossing guard knows: the light will change. It always does.

You don't have to sprint or freeze.

Just look up — and cross when it's your time.

Which type are you right now?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #LeavingMedicine""",
        "fb": """Three types of people I watch on the crosswalk.\n\nThe first type pauses too long at the curb. The crossing feels more dangerous than staying — so they stay.\n\nThe second type steps off without looking. They quit fast, move fast, and find themselves in the middle of the road with no plan.\n\nThe third type crosses with their head down, too busy surviving to look at where they're going.\n\nI've recognized all three in healthcare professionals.\n\nWhat the crossing guard knows: the light will change. It always does.\n\nYou don't have to sprint. You don't have to freeze. You just have to look up — and cross when it's your time.\n\nWhich type are you right now? Tell me below.""",
        "tt": """Three types of burned-out healthcare workers — and which one you are changes what you actually need.\n\nThe Freezer. The Sprinter. The Head-Down.\n\nWhat the crossing guard knows: the light will change.\n\nYou don't have to sprint or freeze. Just look up and cross when it's your time.\n\n#CrosswalkWisdom #HealthcareBurnout #NurseBurnout""",
    },
    "2026-05-10": {
        "img": "nobody_tells",
        "li": """Something nobody tells you about leaving a career you've outgrown:

The grief comes before the relief.

You imagine leaving and expect to feel lighter. Instead, you feel the weight of everything you'd be giving up — the title, the identity, the way people look at you when you tell them what you do.

The grief is real. It's not irrational. You are mourning a version of yourself that has carried you for years.

And that version deserves to be mourned.

But grief is not a stop sign. It's a signal.

It means something mattered. It means you built something real. It means you are capable of caring deeply — which is exactly the quality that will serve you in whatever comes next.

What nobody tells you: you can grieve and still go.

What has been the hardest thing to grieve about where you are right now?

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #LeavingMedicine #IdentityLoss #BurnoutRecovery #CareerTransition""",
        "ig": """Nobody tells you the grief comes before the relief.

You imagine leaving and expect to feel lighter.

Instead, you feel everything you'd be giving up.

The title. The identity. The way people look at you.

That grief is real. And it deserves to be felt.

But grief is not a stop sign.

You can grieve and still go.

What's been the hardest thing to grieve about where you are?

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #LeavingMedicine #IdentityLoss #BurnoutRecovery""",
        "fb": """Nobody tells you the grief comes before the relief.\n\nYou imagine leaving and expect to feel lighter. Instead, you feel everything you'd be giving up — the title, the identity, the way people look at you when you tell them what you do.\n\nThe grief is real. And it deserves to be felt.\n\nBut grief is not a stop sign. It's a signal. It means something mattered. It means you're capable of caring deeply.\n\nYou can grieve and still go.\n\nWhat has been the hardest thing to grieve about where you are right now? I'm reading every response.""",
        "tt": """Nobody tells you the grief comes before the relief.\n\nYou imagine leaving. You expect to feel lighter.\n\nInstead — the weight of everything you'd give up.\n\nThat grief is real. It deserves to be felt.\n\nBut grief is not a stop sign.\n\nYou can grieve and still go.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #IdentityLoss""",
    },
    "2026-05-11": {
        "img": "badge",
        "li": """The day I handed in my badge, I expected relief.

I had been planning the moment for months. Rehearsing it. Telling myself I would feel free.

I walked out of the building. The sun was out. A completely ordinary Tuesday.

And what I felt first wasn't relief. It was grief so unexpected and so complete that I had to sit in my car for twenty minutes before I could drive.

I had not understood, until that moment, how much of my identity I had stored inside that building. Inside that badge. Inside the title that had answered every version of "who are you" for two decades.

When I handed it in, I handed in a version of myself.

Here's what I know now, years later:

That grief was appropriate. That version of me deserved to be mourned.

And what came after — the crossing, the uncertainty, the slowly-rebuilt sense of self — was only possible because I let the grief be real.

You don't have to skip the grief to move forward.

The grief you're anticipating is not a sign you're making the wrong choice. It might be the clearest sign you're finally making the right one.

#CrosswalkWisdom #LeavingMedicine #BurnoutRecovery #IdentityLoss #HealthcareBurnout #PhysicianTransition #CourageToChoose""",
        "ig": """I thought handing in my badge would feel like freedom.

It felt like a funeral. I sat in my car for twenty minutes and couldn't drive.

I had stored so much of my identity inside that building. Inside that title.

Walking out — even by choice — felt like leaving part of myself on the desk.

Here's what I know now:

That grief was appropriate.

And it was not a sign I was making the wrong choice.

It was the clearest sign I was finally making the right one.

#CrosswalkWisdom #LeavingMedicine #BurnoutRecovery #IdentityLoss #HealthcareBurnout""",
        "fb": """The day I handed in my badge, I expected relief.\n\nI had rehearsed it for months. I walked out. The sun was out. An ordinary Tuesday.\n\nWhat came first wasn't relief. It was grief so unexpected and complete I had to sit in my car for twenty minutes before I could drive.\n\nI had stored so much of my identity inside that building. Inside that badge.\n\nWalking out without it — even by choice — felt like leaving part of myself on the desk.\n\nHere's what I know now: that grief was appropriate. And it was not a sign I was making the wrong choice.\n\nIt was the clearest sign I was finally making the right one.\n\nHas anyone here had a moment where a transition felt harder than expected — even one you chose?""",
        "tt": """I thought handing in my badge would feel like freedom.\n\nIt felt like a funeral.\n\nI sat in my car for twenty minutes and couldn't drive.\n\nHere's what I know now: that grief was not a sign I was making the wrong choice.\n\nIt was the clearest sign I was finally making the right one.\n\n#CrosswalkWisdom #LeavingMedicine #BurnoutRecovery #IdentityLoss""",
    },
    "2026-05-12": {
        "img": "quitting",
        "li": """The healthcare system will tell you that leaving is failure.

It has a vested interest in telling you that.

Because if you believe leaving is failure — you stay. And if you stay, the system keeps working. Understaffed units get covered. Impossible ratios get managed. The machine keeps moving.

"Resilience" is the word they use when they mean "endurance."
"Wellness programs" are what they offer when they mean "please don't leave."

I want to say this clearly:

Choosing to leave is not a betrayal of your patients.
Choosing to leave is not a character flaw.
Choosing to leave is not giving up.

In many cases, it is the single most honest decision you have made in years.

The healthcare system does not own your life. Your degree does not own your identity. Your title does not define your worth.

You are allowed to outgrow what you built. You are allowed to choose yourself.

Especially when the system calls it selfish.

Especially then.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #LeavingMedicine #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
        "ig": """The healthcare system calls it quitting.

I call it clarity.

You are not obligated to keep giving what the system refuses to protect.

Leaving is not betrayal.

Staying to disappear is.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #LeavingMedicine #BurnoutRecovery #IdentityLoss""",
        "fb": """The healthcare system will tell you that leaving is failure.\n\nIt has a vested interest in telling you that.\n\n"Resilience" is what they call endurance. "Wellness programs" are what they offer when they mean "please don't leave."\n\nChoosing to leave is not a betrayal of your patients. It is not a character flaw. In many cases, it is the single most honest decision you have made in years.\n\nYou are allowed to outgrow what you built.\n\nEspecially when the system calls it selfish.\n\nEspecially then.\n\nWhat does your gut tell you about this?""",
        "tt": """The healthcare system calls it quitting.\n\nI call it clarity.\n\nYou are not obligated to keep giving what the system refuses to protect.\n\nLeaving is not betrayal.\n\nStaying to disappear is.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #LeavingMedicine""",
    },
    "2026-05-13": {
        "img": "engagement",
        "li": """I want to try something today.

Tell me — in one sentence — what your ideal day looks like.

Not your current day. The day you're working toward. The one that exists somewhere on the other side of this.

It doesn't have to be a grand vision. It can be simple.

"Wake up without dread."
"Do work that feels like mine."
"Be home in time for dinner."
"Have energy left at the end of the day."

One sentence. Yours.

Because the people I've watched make real transitions could all describe — sometimes vaguely, sometimes precisely — what they were moving toward.

The direction matters. Even if the path isn't clear yet.

What's your one sentence?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #CareerTransition #IdentityLoss""",
        "ig": """Tell me in one sentence: what does your ideal day look like?

Not your current day. The one on the other side of this.

"Wake up without dread."
"Do work that feels like mine."
"Have energy left at the end of the day."

One sentence. Yours.

Drop it below. 👇

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery""",
        "fb": """I want to try something today.\n\nTell me — in one sentence — what your ideal day looks like.\n\nNot your current day. The one you're working toward.\n\nIt can be simple:\n"Wake up without dread."\n"Do work that feels like mine."\n"Be home in time for dinner."\n"Have energy left at the end of the day."\n\nOne sentence. Yours.\n\nThe people I've watched make real transitions could all describe — at least vaguely — what they were moving toward. The direction matters even if the path isn't clear yet.""",
        "tt": """Tell me in one sentence what your ideal day looks like.\n\nNot today. The one on the other side of this.\n\n"Wake up without dread."\n"Do work that feels like mine."\n"Have energy left."\n\nOne sentence. Drop it below.\n\n#CrosswalkWisdom #HealthcareBurnout #NurseBurnout""",
    },
    "2026-05-14": {
        "img": "sunk_cost",
        "li": """Unpopular opinion: slowing down is the advanced move.

High achievers in healthcare are trained to treat speed as virtue. Faster diagnosis. More patients. More output. Keep moving.

Burnout is, in part, what happens when you've been moving so fast for so long that you can't tell the difference between momentum and inertia.

You're not going anywhere. You're just moving.

The most sophisticated thing I did in my recovery was stop. Fully stop. Not take a vacation. Actually stop, stand still, and ask: what do I actually want?

It felt like failure. It looked like stillness.

It was the first intelligent choice I had made in years.

Slowing down is not retreat. It is reconnaissance.

You cannot navigate a crossing you haven't looked at.

What would full stop look like for you — even for one week?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #LeavingMedicine""",
        "ig": """Unpopular opinion: slowing down is the most advanced thing a burned-out healthcare worker can do.

Burnout is what happens when you've been moving so fast for so long you can't tell the difference between momentum and inertia.

You're not going anywhere. You're just moving.

Slowing down is not retreat.

It is reconnaissance.

You cannot navigate a crossing you haven't looked at.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery""",
        "fb": """Unpopular opinion: slowing down is the most advanced move.\n\nHigh achievers treat speed as virtue. More output. Keep moving.\n\nBurnout is what happens when you've been moving so fast you can't tell the difference between momentum and inertia. You're not going anywhere. You're just moving.\n\nThe most sophisticated thing I did in recovery: fully stop. Not a vacation. An actual stop.\n\nIt felt like failure. It was the first intelligent choice I'd made in years.\n\nSlowing down is not retreat. It is reconnaissance.\n\nWhat would full stop look like for you — even for one week?""",
        "tt": """Unpopular opinion: slowing down is the advanced move.\n\nBurnout is when you've been moving so fast you can't tell momentum from inertia.\n\nYou're not going anywhere. You're just moving.\n\nSlowing down is not retreat. It is reconnaissance.\n\nYou cannot navigate a crossing you haven't looked at.\n\n#CrosswalkWisdom #HealthcareBurnout #NurseBurnout""",
    },
    "2026-05-15": {
        "img": "educational",
        "li": """The first fear keeping burned-out healthcare professionals stuck: Financial Insecurity.

"I can't afford to leave."
"I have student loans."
"My family depends on my income."
"There's nothing else I could do that pays this well."

This fear is real. I won't tell you to ignore it.

But here's what Financial Insecurity does that people don't notice: it doesn't just prevent leaving. It prevents thinking.

The fear shuts down the entire exploration before it starts. You don't research other options because the fear tells you there are none. You don't talk to people who've transitioned because the fear says their situations don't apply.

You stay, burn out more, and the fear gets louder. Because exhausted people make worse decisions, which makes the fear feel more justified.

It's a loop.

The way out: separate the fear from the fact. Not to dismiss it — to examine it.

What do you actually know about your options? What would you need to know?

(The Fear Audit identifies which of the 3 fears is dominant for you — link in first comment.)

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #FearAudit #BurnoutRecovery #LeavingMedicine #CareerTransition""",
        "ig": """Fear #1 keeping healthcare workers stuck in burnout:

"I can't afford to leave."

This fear doesn't just stop you from leaving.

It stops you from thinking.

It shuts down the whole exploration before it starts.

The way out: separate the fear from the fact.

What do you actually know about your options? What would you need to know?

Link in bio — free Fear Audit.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #FearAudit #BurnoutRecovery #LeavingMedicine""",
        "fb": """The first fear keeping burned-out healthcare professionals stuck: Financial Insecurity.\n\n"I can't afford to leave."\n\nThis fear is real. I won't dismiss it.\n\nBut here's what it does that people don't notice: it doesn't just prevent leaving. It prevents thinking. The fear shuts down the exploration before it starts.\n\nYou stay. Burn out more. The fear gets louder. Because exhausted people make worse decisions, which makes the fear feel more justified.\n\nIt's a loop.\n\nThe way out: separate the fear from the fact. What do you actually know about your options?\n\nHas financial fear ever stopped you from even exploring? Tell me below.""",
        "tt": """Fear #1 keeping healthcare workers stuck:\n\n"I can't afford to leave."\n\nThis fear doesn't just stop leaving. It stops thinking.\n\nThe way out: separate the fear from the fact.\n\nWhat do you actually know about your options?\n\nFree Fear Audit — link in bio.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #FearAudit""",
    },
    "2026-05-16": {
        "img": "portrait",
        "li": """The second fear: Fear of Judgment.

"What will my family think?"
"My colleagues will think I couldn't handle it."
"What do I say at dinner parties now?"

This one hides better than financial insecurity. It presents as practicality.

"I'm not afraid of what people think. I'm just being realistic."

But underneath that framing — quietly, persistently — is a specific face. A parent. A mentor. A colleague. Someone whose opinion has become the measuring stick for every decision.

Fear of Judgment is powerful because it's social. We are wired to care what our tribe thinks.

The problem is that your tribe — family, training cohort, current colleagues — often has a vested interest in you staying. Not because they don't care about you. Because they've built an identity around you being who you are.

Their fear of your change is not your responsibility.

Their narrative about your choice is not your reality.

What would you do if you knew no one whose opinion you cared about would ever find out?

Start there.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #FearAudit #BurnoutRecovery #IdentityLoss #LeavingMedicine""",
        "ig": """Fear #2 keeping healthcare workers stuck:

Fear of Judgment.

It hides as practicality: "I'm just being realistic."

But underneath it is a face — a parent, a mentor, someone whose opinion has become the measuring stick.

Your tribe often has a vested interest in you staying. Not because they don't love you. Because they've built an identity around you being who you are.

Their fear of your change is not your responsibility.

What would you do if no one whose opinion you cared about would ever find out?

Start there.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #FearAudit #BurnoutRecovery #LeavingMedicine""",
        "fb": """The second fear holding healthcare workers in burnout: Fear of Judgment.\n\nIt hides well. It presents as "I'm being realistic."\n\nBut underneath that framing — quietly — is a specific face. A parent. A mentor. A colleague whose opinion has become the measuring stick.\n\nYour tribe often has a vested interest in you staying. Not because they don't care. Because they've built an identity around you being who you are.\n\nTheir fear of your change is not your responsibility.\n\nWhat would you do if you knew no one whose opinion you cared about would ever find out? Start there.\n\nDoes this resonate?""",
        "tt": """Fear #2 keeping healthcare workers stuck:\n\nFear of Judgment.\n\nIt hides as "I'm just being realistic."\n\nBut underneath it is a face. A parent. A mentor. Someone whose opinion has become the measuring stick.\n\nTheir fear of your change is not your responsibility.\n\nWhat would you do if no one would ever find out?\n\nStart there.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #FearAudit""",
    },
    "2026-05-17": {
        "img": "scrubs",
        "li": """The third fear. The one most people have never heard named.

Identity Loss.

Not "I'll lose money." Not "people will judge me."

"I don't know who I am without this."

When a job title becomes an identity answer — not "I work as a nurse" but "I am a nurse" — the whole career becomes load-bearing.

Leaving doesn't just mean changing jobs. It means answering the question "who are you?" from scratch. And for someone who's spent 10, 15, 20 years building a self inside a particular identity — that question is terrifying.

Here's what I want you to hear:

The fear is appropriate. A version of you would die in that transition. The version defined by the title, the ward, the credentials.

That grief is real.

But there is a self underneath the title. There always was.

It was there before nursing school. Before medical school. Before the first shift, the first patient, the first time someone called you by your title and you felt the weight of it settle into you.

That self is still there.

Burnout — the fatigue, the numbness, the hollowness — is often that self trying to get your attention.

Identity Loss isn't a warning not to go. It's a compass.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #IdentityLoss #FearAudit #BurnoutRecovery #LeavingMedicine""",
        "ig": """The fear most people have never heard named:

Identity Loss.

Not "I'll lose money."
Not "people will judge me."

"I don't know who I am without this."

When "nurse" or "doctor" becomes the answer to "who are you" — the whole career becomes load-bearing.

But the self underneath that title was there before the degree.

Before the first shift.

It's still there.

Burnout is often that self, knocking from the inside.

Identity Loss isn't a warning not to go.

It's a compass.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #IdentityLoss #FearAudit #BurnoutRecovery""",
        "fb": """The third fear. The one most people have never heard named: Identity Loss.\n\nNot "I'll lose money." Not "people will judge me."\n\n"I don't know who I am without this."\n\nWhen a job title becomes an identity answer — not "I work as a nurse" but "I am a nurse" — the whole career becomes load-bearing.\n\nLeaving doesn't just mean changing jobs. It means answering "who are you?" from scratch.\n\nBut here's what I know: the self underneath that title was there before the degree. Before the first shift.\n\nIt's still there.\n\nBurnout is often that self, knocking from the inside.\n\nIdentity Loss isn't a warning not to go. It's a compass.\n\nDoes this land for you?""",
        "tt": """The fear most people have never heard named:\n\nIdentity Loss.\n\n"I don't know who I am without this."\n\nWhen the job title becomes the answer to "who are you" — everything becomes load-bearing.\n\nBut the self underneath that title was there before the degree.\n\nIt's still there.\n\nBurnout is often that self, knocking from the inside.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #IdentityLoss #FearAudit""",
    },
    "2026-05-18": {
        "img": "five_fears",
        "li": """Three fears. One quiz. Everything changes when you name it.

After a week of naming these fears — Financial Insecurity, Fear of Judgment, Identity Loss — here's the practical tool that goes with all of it.

The Fear Audit identifies which of the three is most dominant for you right now.

Not to put you in a box. To give you language for the thing that's been making your decisions without your permission.

Because here's what I've learned: the people who stay stuck don't stay stuck because they lack information. They stay stuck because the fear running their decisions is unnamed.

And unnamed fear doesn't respond to logic. It doesn't respond to job listings or career coaches. It responds to being seen.

Name it. See it. Then decide what to do with it.

That's the whole model.

Free. 12 questions. 2 minutes.

Link in the first comment.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #FearAudit #BurnoutRecovery #IdentityLoss #LeavingMedicine #HealthcareWorkers""",
        "ig": """Three fears. One quiz. Two minutes.

Financial Insecurity → Fear of Judgment → Identity Loss

The Fear Audit tells you which one is running your life right now.

Not to label you — to give you language for the thing that's been making your decisions without your permission.

Named fears are workable. Unnamed fears run the show.

Free. Link in bio.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #FearAudit #BurnoutRecovery #IdentityLoss""",
        "fb": """Three fears. One quiz. Everything changes when you name it.\n\nAfter a week of naming Financial Insecurity, Fear of Judgment, and Identity Loss — here's the practical tool.\n\nThe Fear Audit identifies which of the three is most dominant for you right now.\n\nThe people who stay stuck don't lack information. They stay stuck because the fear running their decisions is unnamed. And unnamed fear doesn't respond to logic.\n\nIt responds to being seen.\n\nName it. See it. Then decide what to do.\n\nFree. 12 questions. 2 minutes. Link in comments.""",
        "tt": """Three fears. One quiz.\n\nThe Fear Audit tells you which one is running your decisions right now.\n\nFinancial → Judgment → Identity Loss\n\nNamed fears are workable. Unnamed fears run the show.\n\nFree. Link in bio.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #FearAudit""",
    },
    "2026-05-19": {
        "img": "laptop",
        "li": """30 minutes with Claude can do what 6 months of overthinking cannot.

I've watched this happen dozens of times.

A burned-out nurse practitioner. 14 years in. Hasn't let herself think about what else might be possible because the moment she starts, the fear shuts it down.

So we try something different. She opens Claude. Three prompts:

"What transferable skills do I have that I've never listed on a resume?"

"If I had to leave healthcare tomorrow and couldn't use any clinical credentials, what would I do with what I know?"

"What does a version of my life look like in 3 years if I choose myself instead of the system?"

The AI doesn't know her fears. It just responds to what she puts in.

Watching her read the output — watching her see, in plain text, options she had convinced herself didn't exist — I have seen that shift happen in 30 minutes that six months of internal debate couldn't produce.

If you're stuck in your head — get it out of your head. Onto a screen. Into a prompt.

What would you ask if you knew an honest answer was possible?

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery #CareerTransition #LeavingMedicine #AITools""",
        "ig": """30 minutes with Claude can do what 6 months of overthinking can't.

Three prompts that change things:

→ "What transferable skills do I have that I've never listed on a resume?"
→ "If I couldn't use clinical credentials, what would I do with what I know?"
→ "What does my life look like in 3 years if I choose myself?"

If you're stuck in your head — get it out of your head.

What would you ask if you knew an honest answer was possible?

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery #CareerTransition #AITools""",
        "fb": """30 minutes with Claude can do what 6 months of overthinking cannot.\n\nA burned-out NP. 14 years in. Every time she starts to think about options, the fear shuts it down.\n\nSo we try something different. Three prompts:\n\n"What transferable skills do I have that I've never listed on a resume?"\n"If I couldn't use clinical credentials, what would I do with what I know?"\n"What does my life look like in 3 years if I choose myself?"\n\nWatching her read the output — seeing options she'd convinced herself didn't exist — I've watched that shift happen in 30 minutes that months of debate couldn't produce.\n\nIf you're stuck in your head — get it out. Into a prompt.\n\nWhat would you ask if you knew an honest answer was possible?""",
        "tt": """30 minutes with Claude can do what 6 months of overthinking can't.\n\nThree prompts:\n→ What transferable skills have I never listed?\n→ If I couldn't use credentials, what would I do with what I know?\n→ What does my life look like in 3 years if I choose myself?\n\nGet it out of your head. Into a prompt.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #AITools""",
    },
    "2026-05-20": {
        "img": "letter",
        "li": """The Courage to Choose was written for one specific person.

The one who's done the self-reflection. Who knows they're burned out. Who has named the fear — or suspects what it is.

Who is stuck at the hardest question: what do I actually do next?

Three chapters:

Chapter 1: Naming the Fear — because the fear keeping you stuck is specific, and specificity is the beginning of power. Rooted in Adlerian psychology.

Chapter 2: Reframing the Story — the shift from "I'm trapped" to "I'm choosing." Stoic philosophy applied to the particular bind of healthcare identity.

Chapter 3: Taking the First Step — a concrete action framework for moving forward despite fear. Viktor Frankl's logotherapy meets career transition.

$27. PDF. Yours immediately.

Built for the moment after the assessment. The moment after you've looked honestly at where you are — and realized you need a path, not just a diagnosis.

Link in the first comment.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery #CourageToChoose #LeavingMedicine #IdentityLoss""",
        "ig": """The Courage to Choose is a $27 guide for the moment after you've looked honestly at where you are.

Not "self-care tips."

A map.

Three chapters:
Naming the Fear → Reframing the Story → Taking the First Step

Rooted in Adlerian psychology, Stoic philosophy, Viktor Frankl.

For the healthcare professional who needs a path, not just a diagnosis.

Link in bio.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #CourageToChoose #BurnoutRecovery""",
        "fb": """The Courage to Choose was written for one specific person.\n\nThe one who knows they're burned out, has started to name the fear — and is stuck at the hardest question: what do I actually do next?\n\nThree chapters: Naming the Fear → Reframing the Story → Taking the First Step\n\nRooted in Adlerian psychology, Stoic philosophy, and Viktor Frankl's logotherapy.\n\n$27. PDF. Yours immediately.\n\nFor healthcare professionals who are done with generic wellness advice and ready for a map.\n\nLink in comments.""",
        "tt": """The Courage to Choose — $27 guide for when you've named the fear and need to know what's next.\n\nNaming → Reframing → First Step\n\nRooted in Adlerian psychology, Stoic philosophy, Viktor Frankl.\n\nFor healthcare workers ready for a map, not a mirror.\n\nLink in bio.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #CourageToChoose""",
    },
    "2026-05-21": {
        "img": "cta_stages",
        "li": """There's a version of burnout where you still show up.

Still smile at patients. Still write the notes. Still clock the shifts.

But something is missing — and you haven't been able to name it.

It's not the job, exactly. It's not your colleagues. It's that you've lost the thread between who you are and what you're doing.

The work continues. The meaning doesn't.

This is the ELDER stage of burnout. The seeking phase.

Where you know something is wrong but haven't found language for it yet.

It's also the phase where the right intervention makes the most difference — not meditation, not resilience training, but a specific next step, matched to where you actually are.

The free 12-question Burnout Assessment places you in one of 4 stages and gives you exactly that.

Two minutes. Free. Built for nurses, doctors, and healthcare workers.

Link in the first comment.

Which stage resonates with where you are right now?

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery #IdentityLoss #BurnoutAssessment #HealthcareWorkers""",
        "ig": """There's a version of burnout where you still show up.

Still smile. Still write the notes. Still clock the shifts.

But the thread between who you are and what you're doing — that's gone.

The work continues. The meaning doesn't.

This is the ELDER stage. The seeking phase.

Where the right intervention makes the most difference — and most people don't know what it is.

Free 12-question assessment. 2 minutes.

Link in bio.

#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutRecovery #BurnoutAssessment #IdentityLoss""",
        "fb": """There's a version of burnout where you still show up every day.\n\nStill smile. Still write the notes. Still clock the shifts.\n\nBut the thread between who you are and what you're doing — that's gone.\n\nThe work continues. The meaning doesn't.\n\nThis is the ELDER stage of burnout. The seeking phase. Where you know something is wrong but haven't found language for it yet.\n\nIt's also the phase where the right intervention makes the most difference.\n\nFree 12-question Burnout Assessment. Tells you your stage. Gives you one specific next step.\n\n2 minutes. Link in comments.\n\nDoes this resonate with where you are?""",
        "tt": """There's a version of burnout where you still show up every day — and it's the hardest one to see from the inside.\n\nThe work continues. The meaning doesn't.\n\nThis is the ELDER stage. The seeking phase.\n\nFree Burnout Assessment tells you your stage and gives you one specific next step.\n\n2 minutes. Link in bio.\n\n#HealthcareBurnout #NurseBurnout #CrosswalkWisdom #BurnoutAssessment""",
    },
}

# ─────────────────────────────────────────────
# SCHEDULE TABLE
# ─────────────────────────────────────────────
# Format: (date, slot_time, content_type, variant_index)
# Variant index cycles: morning A/B/C/D, edu A/B/C/D, eng A/B/C/D, cta A/B/C
# May 11 & 18 skip 7pm (already have a post there)

SCHEDULE = []
week2_days = ["2026-05-08","2026-05-09","2026-05-10","2026-05-11","2026-05-12","2026-05-13","2026-05-14"]
week3_days = ["2026-05-15","2026-05-16","2026-05-17","2026-05-18","2026-05-19","2026-05-20","2026-05-21"]

for i, date in enumerate(week2_days + week3_days):
    SCHEDULE.append((date, "07:00:00", "morning",    i % 4))
    SCHEDULE.append((date, "10:00:00", "educational", i % 4))
    SCHEDULE.append((date, "13:00:00", "main",        0))
    SCHEDULE.append((date, "16:00:00", "engagement",  i % 4))
    if date not in ("2026-05-11", "2026-05-18"):  # already have 7pm post
        SCHEDULE.append((date, "19:00:00", "evening_cta", i % 3))


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

_url_cache: dict[str, str] = {}

def upload_image(path: str) -> str:
    if path in _url_cache:
        return _url_cache[path]
    filename = os.path.basename(path)
    filesize = os.path.getsize(path)
    r = requests.post(f"{BASE}/media/presign", headers=HEADERS,
                      json={"filename": filename, "contentType": "image/jpeg", "fileSize": filesize})
    r.raise_for_status()
    data = r.json()
    with open(path, "rb") as f:
        requests.put(data["uploadUrl"], data=f, headers={"Content-Type": "image/jpeg"}).raise_for_status()
    _url_cache[path] = data["publicUrl"]
    print(f"    ↑ uploaded {filename[:50]}")
    return data["publicUrl"]


def schedule_post(date, slot_time, li, ig, fb, tt, img_path):
    sched = f"{date}T{slot_time}"
    image_url = upload_image(img_path)
    platforms = [
        {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": li, "scheduledFor": sched},
        {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": ig, "scheduledFor": sched},
        {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": fb, "scheduledFor": sched},
        {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": tt, "scheduledFor": sched},
    ]
    body = {
        "content": li,
        "mediaItems": [{"url": image_url, "type": "image"}],
        "platforms": platforms,
        "scheduledFor": sched,
        "timezone": TZ,
    }
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    return r.status_code


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("=== Crosswalk Wisdom — May 8–21 — 5 Posts/Day ===")
    print(f"    Total slots to schedule: {len(SCHEDULE)}\n")

    ok = fail = 0
    for entry in SCHEDULE:
        date, slot_time, content_type, idx = entry
        label = f"{date} {slot_time[:5]}"

        if content_type == "morning":
            c = MORNING[idx]
        elif content_type == "educational":
            c = EDUCATIONAL[idx]
        elif content_type == "engagement":
            c = ENGAGEMENT[idx]
        elif content_type == "evening_cta":
            c = EVENING_CTA[idx]
        elif content_type == "main":
            c = MAIN_POSTS[date]
        else:
            continue

        img_key = c.get("img", "morning")
        img_path = IMG[img_key]

        print(f"  [{label}] {content_type} → ", end="", flush=True)
        status = schedule_post(date, slot_time, c["li"], c["ig"], c["fb"], c["tt"], img_path)
        if status in (200, 201):
            print("✓")
            ok += 1
        else:
            print(f"✗ ({status})")
            fail += 1

        time.sleep(0.8)  # avoid rate limiting

    print(f"\n{'='*50}")
    print(f"✓ Scheduled: {ok}   ✗ Failed: {fail}")
    print("Reminder: post first comments with assessment URLs on publish dates.")
    print("  Fear Audit posts → fear-audit.vercel.app")
    print("  Stage posts      → crosswalkwisdom.com/assessment")


if __name__ == "__main__":
    main()
