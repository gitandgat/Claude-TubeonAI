"""
Schedule: April 2026 Gap Fill — 5 posts/day
Fills missing slots for April 5–30 to reach the 5-posts/day target.
73 posts total across LinkedIn, Instagram, Facebook, TikTok.
Slots: 07:00, 10:00, 13:00, 16:00, 19:00 ET
All image posts → 4 platforms (LI/IG/FB/TT). YouTube excluded (video only).
"""
import os
import time
import requests

BASE    = "https://zernio.com/api/v1"
from zernio_key import ZERNIO_API_KEY as API_KEY
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

LINKEDIN_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ID  = "6909409a5f6fbb9ef8323074"
TIKTOK_ID    = "690941425f6fbb9ef8323078"
TIMEZONE     = "America/New_York"

ASSETS = "/Users/toto/Claude TubeonAI/crosswalk-remotion/public/assets/april"

IMAGES = {
    "scrubs":    f"{ASSETS}/freepik__a-pair-of-folded-blue-hospital-scrubs-resting-neat__52543.jpeg",
    "hands_lap": f"{ASSETS}/freepik__closeup-of-a-persons-hands-resting-on-an-open-lapt__52544.jpeg",
    "hands_hosp":f"{ASSETS}/freepik__closeup-of-a-pair-of-hands-gently-placing-a-hospit__52545.jpeg",
    "phone":     f"{ASSETS}/freepik__a-smartphone-with-a-cracked-screen-showing-a-text-__52546.jpeg",
    "signal":    f"{ASSETS}/freepik__a-city-pedestrian-traffic-signal-light-changing-fr__52547.jpeg",
    "clipboard": f"{ASSETS}/freepik__a-clean-warm-flatlay-of-a-clipboard-with-a-white-n__52549.jpeg",
    "car":       f"{ASSETS}/freepik__interior-of-a-car-at-dusk-viewed-from-the-drivers-__52550.jpeg",
    "paper":     f"{ASSETS}/freepik__soft-cream-paper-texture-on-a-warm-white-backgroun__52551.jpeg",
    "hospital":  f"{ASSETS}/freepik__a-person-sitting-alone-in-a-softly-lit-hospital-co__52553.jpeg",
    "crosswalk": f"{ASSETS}/freepik__cinematic-shot-of-a-person-walking-across-a-wet-ci__52554.jpeg",
    "letter":    f"{ASSETS}/freepik__a-handwritten-letter-on-cream-textured-paper-lying__52555.jpeg",
    "id_badge":  f"{ASSETS}/freepik__closeup-of-two-hands-gently-cradling-a-hospital-id__52556.jpeg",
    "laptop":    f"{ASSETS}/freepik__a-persons-hands-typing-on-a-laptop-at-a-cozy-woode__52557.jpeg",
    "table":     f"{ASSETS}/freepik__overhead-flatlay-of-a-warm-wooden-table-with-an-op__52558.jpeg",
    "portrait":  f"{ASSETS}/freepik__cinematic-portrait-of-a-south-asian-man-in-his-40s__52542.jpeg",
}

# ─────────────────────────────────────────────
# CONTENT BANKS
# ─────────────────────────────────────────────

# MORNING (07:00) — short hooks for healthcare workers
MORNING = [
    {
        "img": "scrubs",
        "li": """The crosswalk doesn't ask if you're ready.

It just turns green.

That's the thing about transition — it doesn't wait for you to feel prepared. It doesn't wait for the right moment. It doesn't wait until your schedule clears up.

Most burned-out healthcare professionals I talk to are waiting for a sign that it's safe to change. Meanwhile, the light keeps changing.

The question isn't whether you're ready.

The question is: what will you do when the light turns?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #CareerTransition #HealthcareWorkers #CourageToChoose""",
        "ig": """The crosswalk doesn't ask if you're ready.

It just turns green.

Transition doesn't wait for the right moment. It doesn't wait until the schedule clears.

Most burned-out healthcare workers are waiting for a sign that it's safe to change.

Meanwhile, the light keeps changing.

What will you do when it turns?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #CareerTransition #HealthcareWorkers #CourageToChoose""",
        "fb": """The crosswalk doesn't ask if you're ready.

It just turns green.

That's the thing about transition — it doesn't wait for you to feel prepared. Most burned-out healthcare professionals are waiting for the perfect moment to change. Meanwhile, the light keeps turning.

The question isn't whether you're ready. The question is what you'll do when it does.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #CourageToChoose""",
        "tt": """The crosswalk doesn't ask if you're ready.

It just turns green.

Transition doesn't wait for perfect timing.

What will you do when your light turns?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #CourageToChoose""",
    },
    {
        "img": "id_badge",
        "li": """The version of you who started in healthcare — what would they think of you right now?

Not judge. Not criticize.

Just — look at you. The tired eyes. The clocked-out smile. The way you've learned to nod and keep moving.

I ask because that younger version didn't sign up for this. They signed up for something they believed in.

That belief doesn't disappear. It gets buried.

Recovery isn't about finding motivation. It's about excavating what was always there.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #PhysicianBurnout #IdentityLoss #BurnoutRecovery #HealthcareWorkers""",
        "ig": """The version of you who started in healthcare — what would they think of you right now?

Not judge. Not criticize.

Just look at the tired eyes. The clocked-out smile.

That younger version didn't sign up for this. They believed in something.

That belief doesn't disappear. It gets buried.

Recovery is excavation, not motivation.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #IdentityLoss #BurnoutRecovery #HealthcareWorkers""",
        "fb": """The version of you who started in healthcare — what would they think of you right now?

Not judge. Not criticize. Just look at you.

That person didn't sign up for this. They signed up for something they believed in. That belief doesn't disappear — it gets buried under years of overriding yourself.

Recovery isn't about finding motivation. It's about excavating what was always there.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #IdentityLoss""",
        "tt": """The version of you who started in healthcare — what would they think of you right now?

That belief didn't disappear.

It got buried.

Recovery isn't motivation. It's excavation.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #IdentityLoss #BurnoutRecovery""",
    },
    {
        "img": "hospital",
        "li": """Burnout doesn't happen to weak people.

It happens to the ones who gave everything.

The nurses who took the extra shift. The doctors who stayed late because the patient needed them. The NPs who answered messages on their days off.

Burnout is a bill that came due. And the people who get it are almost always the ones who cared the most.

If you're burned out, it means you were fully in it. That's not a flaw. That's the whole story.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #PhysicianBurnout #BurnoutRecovery #HealthcareWorkers #NurseLife""",
        "ig": """Burnout doesn't happen to weak people.

It happens to the ones who gave everything.

The nurses who took the extra shift. The doctors who stayed late. The NPs who answered messages on their days off.

Burnout is a bill that came due.

If you're burned out, it means you were fully in it. That's not a flaw. That's the whole story.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #HealthcareWorkers #NurseLife""",
        "fb": """Burnout doesn't happen to weak people.

It happens to the ones who gave everything. The nurses who took the extra shift. The doctors who stayed late because someone needed them.

Burnout is a bill that came due. And the people who get it are almost always the ones who cared most.

If that's you — it means you were fully in it. That's not a flaw. That's the whole story.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #HealthcareWorkers""",
        "tt": """Burnout doesn't happen to weak people.

It happens to the ones who gave everything.

If you're burned out, it means you were fully in it.

That's not a flaw. That's the whole story.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery""",
    },
    {
        "img": "car",
        "li": """Before the shift starts — one question.

How are you, really?

Not "fine." Not "tired but okay." Not "hanging in there."

How are you, really?

I ask because that question almost never gets asked in healthcare. You spend 12 hours asking it of patients. But no one is asking it of you.

And the honest answer matters. Not because you need to fix it right now. Because naming it is the beginning of everything else.

How are you, really?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #HealthcareWorkers #PhysicianBurnout #NurseLife""",
        "ig": """Before the shift starts — one question.

How are you, really?

Not "fine." Not "hanging in there."

You spend 12 hours asking it of patients. But no one is asking it of you.

Naming it honestly is the beginning of everything else.

So — how are you, really?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #HealthcareWorkers #NurseLife""",
        "fb": """Before the shift starts, I want to ask you something.

How are you, really?

Not "tired but okay." Not "managing." The honest answer.

That question almost never gets asked in healthcare. You spend your whole shift asking it of patients, but no one is asking it of you.

Naming how you're really doing is the beginning of everything else.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #HealthcareWorkers""",
        "tt": """Before the shift starts — one question.

How are you, really?

Not fine. Not hanging in there. Really.

You ask it of patients all day. Nobody asks it of you.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #HealthcareWorkers""",
    },
    {
        "img": "signal",
        "li": """There's a moment before the burnout breaks through.

Most people miss it.

It's the moment when helping starts to feel like draining. When you're doing everything right — showing up, being present, staying late — but something underneath is running on empty.

That's not weakness. That's a warning signal.

The light is yellow, not red. Which means you still have time to do something different.

The question is whether you're paying attention.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #HealthcareWorkers #CareerTransition #IdentityLoss""",
        "ig": """There's a moment before burnout breaks through.

Most people miss it.

It's when helping starts to feel like draining. When you're doing everything right — but something underneath is running on empty.

The light is yellow, not red.

You still have time to do something different.

Are you paying attention?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss""",
        "fb": """There's a moment before burnout fully breaks through. Most people miss it.

It's when helping starts to feel like draining. When you're showing up and staying late and doing everything right — but something underneath is running on empty.

That's not weakness. That's a warning signal. The light is yellow, not red.

Which means there's still time to do something different.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #HealthcareWorkers""",
        "tt": """There's a moment before burnout breaks through.

Most people miss it.

Helping starts to feel like draining.

The light is yellow, not red. You still have time.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery""",
    },
    {
        "img": "hands_hosp",
        "li": """If your body were a patient, what would you diagnose it with right now?

Chronic fatigue. Emotional numbness. Decreased motivation. Difficulty concentrating. Withdrawal from things that used to bring joy.

If a patient presented with this list, you'd know exactly what to say.

But when it's you — you call it a rough month. You call it part of the job.

The clinical eye you use for everyone else deserves to turn inward once in a while.

You know what you'd recommend. The question is whether you'll recommend it for yourself.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #PhysicianBurnout #BurnoutRecovery #HealthcareWorkers #IdentityLoss""",
        "ig": """If your body were a patient — what would you diagnose right now?

Chronic fatigue. Emotional numbness. Decreased motivation. Withdrawal from things that used to bring joy.

If a patient presented with that list, you'd know exactly what to say.

But when it's you — you call it a rough month.

You know what you'd recommend. The question is whether you'll recommend it for yourself.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #PhysicianBurnout #BurnoutRecovery #HealthcareWorkers""",
        "fb": """If your body were a patient, what would you diagnose it with right now?

Chronic fatigue. Emotional numbness. Decreased motivation. Difficulty concentrating. Withdrawal from things that used to bring joy.

You know what that chart looks like. You've seen it before.

The clinical eye you use for everyone else deserves to turn inward. And you already know what you'd recommend.

The question is whether you'll recommend it for yourself.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #HealthcareWorkers""",
        "tt": """If your body were a patient — what would you diagnose?

Chronic fatigue. Emotional numbness. Decreased motivation.

You know exactly what to say when it's someone else's chart.

Why is it different when it's yours?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #PhysicianBurnout #BurnoutRecovery""",
    },
    {
        "img": "crosswalk",
        "li": """The bravest thing a healthcare professional can do right now isn't show up stronger.

It's admit they're tired.

We've built an entire culture around endurance. The ones who don't complain. The ones who push through. The ones who are always available.

But that culture has a cost. And the people paying it are sitting in break rooms, in parking lots, in the quiet after a shift ends — alone with something they can't say out loud.

You don't have to say it to everyone. But you have to say it to someone.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #PhysicianBurnout #BurnoutRecovery #HealthcareWorkers #IdentityLoss""",
        "ig": """The bravest thing a healthcare professional can do right now?

Admit they're tired.

We've built an entire culture around endurance. Pushing through. Always available. Never complaining.

But that culture has a cost.

And the people paying it are sitting alone in parking lots after their shift — with something they can't say out loud.

You don't have to say it to everyone.

But you have to say it to someone.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #HealthcareWorkers #IdentityLoss""",
        "fb": """The bravest thing a healthcare professional can do right now isn't show up stronger.

It's admit they're tired.

We've built an entire culture around endurance. Never complaining. Always being the one who handles it. But that culture has a cost — and people are paying it quietly in break rooms and parking lots and in the space after the shift ends.

You don't have to say it to everyone. But you have to say it to someone.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #HealthcareWorkers""",
        "tt": """The bravest thing a healthcare professional can do right now?

Admit they're tired.

Not push harder. Not pretend it's fine.

Just — say it to someone.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss""",
    },
    {
        "img": "letter",
        "li": """You didn't lose yourself in one bad shift.

It was a slow erosion.

The missed lunch. The delayed vacation. The boundary you said you'd hold that slipped one more time. The version of yourself you promised you'd get back to — someday.

Someday keeps getting pushed.

Recovery isn't dramatic. It doesn't announce itself. It starts with one small thing you stop overriding.

What would that one thing be for you today?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #HealthcareWorkers #IdentityLoss #CareerTransition""",
        "ig": """You didn't lose yourself in one bad shift.

It was a slow erosion.

The missed lunch. The delayed vacation. The boundary that slipped one more time.

Recovery isn't dramatic. It doesn't announce itself. It starts with one small thing you stop overriding.

What would that one thing be for you today?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #CareerTransition""",
        "fb": """You didn't lose yourself in one bad shift. It was a slow erosion.

The missed lunch. The delayed vacation. The boundary you said you'd hold that slipped one more time. The version of yourself you kept promising you'd get back to — someday.

Recovery isn't dramatic. It starts with one small thing you stop overriding.

What would that be for you today?

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #IdentityLoss""",
        "tt": """You didn't lose yourself in one bad shift.

It was a slow erosion.

Recovery isn't dramatic either.

It starts with one small thing you stop overriding.

What's yours today?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss""",
    },
]

# EDUCATIONAL (10:00) — teach something valuable
EDUCATIONAL = [
    {
        "img": "clipboard",
        "li": """3 signs burnout is affecting your identity — not just your energy.

1. You can't picture yourself doing anything different. Not because you love what you do, but because you've forgotten who you are without it.

2. You feel guilty resting. Not just slightly uncomfortable — genuinely guilty, like rest is something you have to earn and haven't yet.

3. Your sense of worth is tied entirely to how much you produce. On slow days, you don't feel lighter. You feel worthless.

These aren't personality traits. They're symptoms.

And they require a different kind of intervention than a vacation or a self-care list.

They require naming the fear underneath them first.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #PhysicianBurnout #HealthcareWorkers""",
        "ig": """3 signs burnout is affecting your identity — not just your energy.

1. You can't picture yourself doing anything different — not because you love it, but because you've forgotten who you are without it.

2. You feel guilty resting. Not uncomfortable. Actually guilty, like rest has to be earned.

3. Your worth is tied entirely to how much you produce. On slow days, you don't feel lighter. You feel worthless.

These aren't personality traits. They're symptoms.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
        "fb": """3 signs burnout is affecting your identity — not just your energy.

1. You can't picture yourself doing anything different. Not because you love it, but because you've forgotten who you are without it.

2. You feel guilty resting. Genuinely guilty, like rest is something you have to earn and haven't yet.

3. Your sense of worth is tied entirely to how much you produce. Slow days don't feel like relief — they feel like failure.

These aren't personality traits. They're symptoms. And they require naming the fear underneath them first.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
        "tt": """3 signs burnout is affecting your identity — not just your energy.

1. You've forgotten who you are without the job.
2. You feel guilty resting.
3. Slow days feel worthless, not restful.

These aren't personality traits. They're symptoms.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #IdentityLoss #BurnoutRecovery""",
    },
    {
        "img": "table",
        "li": """Why self-care advice fails burned-out healthcare workers.

It's not that the advice is wrong. It's that it's answering the wrong question.

"Get more sleep. Exercise. Eat better. Set limits."

Healthcare workers know this. They teach it. They prescribe it.

The problem isn't knowledge. The problem is that something underneath is preventing them from acting on what they already know.

That something is almost always a fear. Specifically one of three:

— Fear of financial instability ("I can't afford to slow down")
— Fear of judgment ("What will people think if I'm the one who breaks?")
— Fear of losing identity ("Who am I if I'm not this?")

Self-care advice lands on top of those fears and slides right off.

The first step isn't adding a new habit. It's naming what's underneath.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers #FearAudit""",
        "ig": """Why self-care advice fails burned-out healthcare workers.

It's not that the advice is wrong. It's answering the wrong question.

"Get more sleep. Exercise. Set limits."

Healthcare workers know this. They prescribe it.

The problem isn't knowledge. Something underneath is preventing action.

Almost always: a fear.

→ "I can't afford to slow down."
→ "What will people think if I break?"
→ "Who am I if I'm not this?"

Self-care advice slides right off those fears.

The first step is naming what's underneath.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #FearAudit""",
        "fb": """Why self-care advice fails burned-out healthcare workers.

It's not that the advice is wrong. It's answering the wrong question. "Get more sleep. Exercise. Set limits." Healthcare workers know this — they prescribe it.

The problem isn't knowledge. Something underneath is preventing action. Almost always, it's a fear: financial insecurity, fear of judgment, or identity loss.

Self-care advice lands on top of those fears and slides right off. The first step is naming what's underneath.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
        "tt": """Why self-care advice fails healthcare workers.

It's answering the wrong question.

You already know what to do. Something underneath is preventing you from doing it.

That something is almost always a fear.

Name the fear first.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #FearAudit""",
    },
    {
        "img": "hands_lap",
        "li": """The hidden cost of being "the reliable one."

In every unit, every practice, every team — there's someone everyone calls.

They handle the difficult patients. They cover the extra shift. They're the ones who figure it out when no one else can.

That person pays a specific tax.

Because the more reliable you are, the more is asked of you. The more is asked of you, the less you say no. The less you say no, the more invisible your limits become — to others and eventually to yourself.

Being indispensable doesn't protect you. It consumes you.

The reliable one deserves to be someone other than the answer to everyone else's problems.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #HealthcareWorkers #IdentityLoss #PhysicianBurnout""",
        "ig": """The hidden cost of being "the reliable one."

Every team has one. They handle the hard patients. Cover the extra shift. Figure it out when no one else can.

That person pays a specific tax.

The more reliable you are, the more is asked. The more asked, the less you say no. The less you say no, the more invisible your limits become — to others and eventually to yourself.

Being indispensable doesn't protect you. It consumes you.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
        "fb": """The hidden cost of being "the reliable one."

In every unit, every practice, every team — there's someone everyone calls. They handle the difficult patients, cover the extra shift, figure it out.

That person pays a specific tax.

Because the more reliable you are, the more is asked. The more asked, the less you say no. The less you say no, the more invisible your limits become — to others and eventually to yourself.

Being indispensable doesn't protect you. It consumes you.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
        "tt": """The hidden cost of being "the reliable one."

Everyone calls you. You handle it. You cover it. You figure it out.

That person pays a specific tax.

The more reliable you are, the more invisible your limits become.

Being indispensable doesn't protect you. It consumes you.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery""",
    },
    {
        "img": "laptop",
        "li": """Burnout has 4 stages. Here's what changes at each one.

Stage 1 — START: You're noticing the cracks before they become canyons. Fatigue is there, but so is awareness. This is the most powerful place to be.

Stage 2 — STOP: Something has hit the brakes. The old coping mechanisms aren't working. This is the pause before the turn.

Stage 3 — ELDER: You're reaching outward — for books, for mentors, for answers. That reaching is wisdom, not weakness.

Stage 4 — HUMAN: The armor has come off. This feels like the end. It is actually the beginning.

What matters is that each stage has a different next step. Not a generic list. The one move that makes sense for exactly where you are.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #HealthcareWorkers #BurnoutStages #IdentityLoss""",
        "ig": """Burnout has 4 stages. Here's what changes at each one.

START — You notice the cracks before they become canyons. The most powerful place to be.

STOP — Something hit the brakes. Old coping isn't working. The pause before the turn.

ELDER — You're reaching outward for answers. That's wisdom, not weakness.

HUMAN — The armor has come off. Feels like the end. It's actually the beginning.

Each stage has a different next step. Not a generic list — the one move for exactly where you are.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #BurnoutStages #IdentityLoss""",
        "fb": """Burnout has 4 stages — and what you need is different at each one.

Stage 1 (START): You're noticing the cracks before they become canyons. The most powerful place to be.

Stage 2 (STOP): Something has hit the brakes. Old coping mechanisms have stopped working. This is the pause before the turn.

Stage 3 (ELDER): You're reaching outward — for books, mentors, answers. That's wisdom, not weakness.

Stage 4 (HUMAN): The armor has come off. This feels like the end. It's actually the beginning.

Each stage needs a different response. Not a generic self-care list — the specific move for exactly where you are.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #BurnoutStages #HealthcareWorkers""",
        "tt": """Burnout has 4 stages.

START — Cracks before canyons. Most powerful place to be.
STOP — Brakes hit. Old coping stopped working.
ELDER — Reaching outward for answers. That's wisdom.
HUMAN — Armor off. Feels like the end. It's the beginning.

Each one needs a different move.

#CrosswalkWisdom #HealthcareBurnout #BurnoutStages #BurnoutRecovery""",
    },
    {
        "img": "paper",
        "li": """Identity loss is the burnout symptom nobody talks about.

You can sleep and still be exhausted. You can take a vacation and come back just as depleted. You can remove every external stressor and still feel like something is deeply wrong.

That's because the problem isn't the schedule. It's that somewhere along the way, you stopped being a person who happens to work in healthcare — and became healthcare.

Your identity merged with your role. And the role is destroying you.

Separating those two things is the hardest part of burnout recovery. And the most necessary.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #PhysicianBurnout #IdentityLoss #BurnoutRecovery #HealthcareWorkers #CareerTransition""",
        "ig": """Identity loss is the burnout symptom nobody talks about.

You can sleep. Take a vacation. Remove every stressor. And still feel like something is deeply wrong.

Because the problem isn't the schedule.

Somewhere along the way, you stopped being a person who works in healthcare — and became healthcare.

Your identity merged with your role. And the role is destroying you.

Separating those two things is the hardest part of recovery. And the most necessary.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #IdentityLoss #BurnoutRecovery #CareerTransition""",
        "fb": """Identity loss is the burnout symptom nobody talks about.

You can sleep and still feel exhausted. You can take a vacation and come back just as depleted. You can remove every stressor and still feel like something is deeply wrong.

Because the problem isn't the schedule. Somewhere along the way, you stopped being a person who works in healthcare and became healthcare. Your identity merged with your role.

Separating those two things is the hardest — and most necessary — part of recovery.

#CrosswalkWisdom #HealthcareBurnout #IdentityLoss #BurnoutRecovery #HealthcareWorkers""",
        "tt": """Identity loss is the burnout symptom nobody talks about.

You can sleep, vacation, remove every stressor.

And still feel like something is deeply wrong.

Because you stopped being a person who works in healthcare.

You became healthcare.

#CrosswalkWisdom #HealthcareBurnout #IdentityLoss #NurseBurnout #BurnoutRecovery""",
    },
    {
        "img": "portrait",
        "li": """What healthcare workers get wrong about recovery.

Most think recovery means getting back to who you were before.

It doesn't.

The version of you that was running before burnout was already overextended. Going back to that isn't recovery — it's replay.

Real recovery builds something new. A version of you that knows the limits. That has named the fears. That doesn't need external validation to feel like enough.

That version isn't easier to build. But it lasts.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #CareerTransition #HealthcareWorkers #CourageToChoose""",
        "ig": """What healthcare workers get wrong about recovery.

Most think it means getting back to who they were before.

It doesn't.

The version of you running before burnout was already overextended. Going back isn't recovery — it's replay.

Real recovery builds something new. A version that knows the limits. Has named the fears. Doesn't need external validation to feel like enough.

That version lasts.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #CareerTransition""",
        "fb": """What healthcare workers get wrong about recovery.

Most think it means getting back to who they were before. It doesn't.

The version of you that was running before burnout was already overextended. Going back to that isn't recovery — it's replay.

Real recovery builds something new. A version that knows the limits. Has named the fears. Doesn't need external validation.

That version isn't easier to build. But it lasts.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
        "tt": """What healthcare workers get wrong about recovery.

Most think it means getting back to who they were before.

It doesn't.

That version was already overextended.

Recovery builds something new.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss""",
    },
    {
        "img": "phone",
        "li": """The moment burnout becomes undeniable.

It's not the shift from hell. It's not the difficult patient. It's not even the bad news delivered one too many times.

It's the morning you wake up and feel nothing.

Not dread. Not sadness. Nothing.

The thing that used to drive you — the reason you got into this — has gone quiet. And you can't remember the last time it was loud.

That silence is a signal. Not a sentence.

What you do with it is still up to you.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #PhysicianBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
        "ig": """The moment burnout becomes undeniable.

It's not the shift from hell or the difficult patient.

It's the morning you wake up and feel nothing.

Not dread. Not sadness. Nothing.

The thing that drove you — the reason you got into this — has gone quiet.

That silence is a signal. Not a sentence.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #PhysicianBurnout #BurnoutRecovery #IdentityLoss""",
        "fb": """The moment burnout becomes undeniable.

It's not the shift from hell or the difficult patient. It's the morning you wake up and feel nothing. Not dread. Not sadness. Nothing.

The thing that used to drive you — the reason you chose this — has gone quiet.

That silence is a signal. Not a sentence.

What you do with it is still up to you.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
        "tt": """The moment burnout becomes undeniable.

It's not the bad shift. It's the morning you wake up and feel nothing.

Not dread. Not sadness. Nothing.

That silence is a signal. Not a sentence.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss""",
    },
    {
        "img": "hands_hosp",
        "li": """The difference between compassion fatigue and burnout.

Compassion fatigue is emotional exhaustion from absorbing the pain of others. It's specific to caring professions. It's about the weight of what you witness.

Burnout is different. Burnout is a systemic collapse — of motivation, identity, and meaning. It's not about one thing you witnessed. It's about a sustained misalignment between who you are and what the system demands.

You can have both. Many healthcare workers do.

But they require different interventions.

Compassion fatigue needs space, discharge, and nervous system support.

Burnout needs something harder: a reckoning with who you are outside of what you do.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #CompassionFatigue #IdentityLoss #HealthcareWorkers""",
        "ig": """The difference between compassion fatigue and burnout.

Compassion fatigue: emotional exhaustion from absorbing others' pain. It's about the weight of what you witness.

Burnout: systemic collapse of motivation, identity, and meaning. Not one thing you witnessed — a sustained misalignment between who you are and what the system demands.

They need different interventions.

Compassion fatigue needs space and nervous system support.

Burnout needs a reckoning with who you are outside of what you do.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #CompassionFatigue #IdentityLoss""",
        "fb": """The difference between compassion fatigue and burnout.

Compassion fatigue is emotional exhaustion from absorbing others' pain — specific to caring professions. It's about the weight of what you witness.

Burnout is different. It's a systemic collapse of motivation, identity, and meaning. Not about one thing you witnessed — a sustained misalignment between who you are and what the system demands.

They need different interventions. Compassion fatigue needs space and nervous system support. Burnout needs a reckoning with who you are outside of what you do.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #CompassionFatigue #IdentityLoss""",
        "tt": """Compassion fatigue vs burnout — not the same thing.

Compassion fatigue: absorbing others' pain. The weight of what you witness.

Burnout: identity and meaning collapse. A mismatch between who you are and what the system demands.

They need different fixes.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #CompassionFatigue #BurnoutRecovery""",
    },
]

# MAIN 1pm (thematic deep dives — one per day, 14 unique)
MAIN = [
    {
        "img": "crosswalk",
        "li": """The crosswalk is a metaphor I keep coming back to.

You're standing on one side. The life you built — the career, the identity, the certainty of who you are when you walk into a room in scrubs or a white coat.

On the other side: something you can't fully see yet. Possibility, yes. But also uncertainty. A version of yourself you haven't met.

Most people never step off the curb. Not because they don't want to. Because they're waiting for the light to already be green before they move.

The light doesn't work that way.

The courage to cross comes from stepping forward — and watching it change as you move.

That's the whole thing. That's all of it.

#CrosswalkWisdom #HealthcareBurnout #IdentityLoss #CourageToChoose #CareerTransition #BurnoutRecovery #HealthcareWorkers""",
        "ig": """The crosswalk metaphor.

On one side: who you've been. The career. The identity. The certainty of who you are in scrubs.

On the other: something you can't fully see yet.

Most people never step off the curb. They wait for the light to already be green.

The light doesn't work that way.

The courage to cross comes from stepping forward — and watching it change as you move.

#CrosswalkWisdom #HealthcareBurnout #IdentityLoss #CourageToChoose #CareerTransition #BurnoutRecovery""",
        "fb": """The crosswalk metaphor.

You're standing on one side. The career, the identity, the certainty of who you are when you walk into a room in scrubs.

On the other side: something you can't fully see yet.

Most people never step off the curb. They wait for the light to already be green before they move.

The light doesn't work that way.

The courage to cross comes from stepping forward — and watching it change as you move.

That's all of it.

#CrosswalkWisdom #HealthcareBurnout #IdentityLoss #CourageToChoose #CareerTransition #BurnoutRecovery""",
        "tt": """The crosswalk metaphor.

One side: who you've been.
Other side: something you can't see yet.

Most people wait for the light to already be green.

The light doesn't work that way.

The courage to cross comes from stepping forward first.

#CrosswalkWisdom #HealthcareBurnout #IdentityLoss #CourageToChoose #BurnoutRecovery""",
    },
    {
        "img": "hospital",
        "li": """Healthcare trains you to override yourself.

Hold it through the shift. Eat later. Sleep when it's over. Be the one who doesn't complain.

You got so good at overriding the signal that you forgot it was a signal.

The fatigue. The numbness. The crying in the parking lot before a shift. That wasn't weakness.

That was your nervous system sending a message you'd learned to ignore.

And here's what I've learned: the body always keeps the score. Even when the mind has moved on. Even when you've convinced yourself you're fine.

Your body knows the difference between fine and actually okay.

Are you listening to it?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #HealthcareWorkers #IdentityLoss #PhysicianBurnout""",
        "ig": """Healthcare trains you to override yourself.

Hold it through the shift. Eat later. Be the one who doesn't complain.

You got so good at overriding the signal that you forgot it was a signal.

The fatigue. The numbness. The parking lot cry before a shift.

That wasn't weakness. That was your nervous system sending a message you'd learned to ignore.

The body always keeps the score.

Are you listening to yours?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #HealthcareWorkers #IdentityLoss""",
        "fb": """Healthcare trains you to override yourself.

Hold it through the shift. Eat later. Sleep when it's over. Be the one who doesn't complain.

You got so good at overriding the signal that you forgot it was a signal.

The fatigue. The numbness. The parking lot cry before the shift starts. That wasn't weakness — it was your nervous system sending a message you'd learned to ignore.

The body always keeps the score. Even when the mind has moved on.

Are you listening to it?

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
        "tt": """Healthcare trains you to override yourself.

Hold it. Eat later. Be the one who doesn't complain.

You got so good at ignoring the signal you forgot it was a signal.

The body always keeps the score.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery""",
    },
    {
        "img": "car",
        "li": """There are three fears underneath most healthcare burnout.

The first: Financial Insecurity.
"I can't afford to slow down, even for a day." This one is often real. But it's also often an exaggeration — a worst-case story the mind tells to justify not changing.

The second: Fear of Judgment.
"What will people think if I'm the one who finally breaks?" This one keeps people performing wellness long after they've stopped feeling it.

The third: Identity Loss.
"If I'm not the person who handles everything, who am I?"

This is the most common one. And the hardest to see in yourself — because it's been wearing the costume of dedication for years.

Which one has been making your decisions?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #FearAudit #IdentityLoss #BurnoutRecovery #HealthcareWorkers""",
        "ig": """Three fears underneath most healthcare burnout.

Financial Insecurity:
"I can't afford to slow down, even for a day." Often real — but also often an exaggeration the mind uses to justify not changing.

Fear of Judgment:
"What will people think if I'm the one who breaks?" Keeps people performing wellness after they've stopped feeling it.

Identity Loss:
"If I'm not the person who handles everything, who am I?"

The most common. And the hardest to see — because it looks like dedication.

Which one has been making your decisions?

#CrosswalkWisdom #HealthcareBurnout #FearAudit #IdentityLoss #BurnoutRecovery #NurseBurnout""",
        "fb": """Three fears underneath most healthcare burnout.

1. Financial Insecurity: "I can't afford to slow down, even for a day." Often real — but also often the mind's story to justify not changing.

2. Fear of Judgment: "What will people think if I'm the one who finally breaks?" This one keeps people performing wellness long after they've stopped feeling it.

3. Identity Loss: "If I'm not the person who handles everything, who am I?" The most common. And the hardest to see in yourself — because it's been wearing the costume of dedication for years.

Which one has been making your decisions?

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #FearAudit #IdentityLoss #HealthcareWorkers""",
        "tt": """Three fears underneath most healthcare burnout.

Financial insecurity: "I can't afford to slow down."

Fear of judgment: "What if I'm the one who breaks?"

Identity loss: "Who am I if I'm not this?"

That last one is the most common.

Which one has been making your decisions?

#CrosswalkWisdom #HealthcareBurnout #FearAudit #IdentityLoss #BurnoutRecovery""",
    },
    {
        "img": "scrubs",
        "li": """What nobody tells you about leaving a healthcare career.

It's not the income you grieve first. It's not the colleagues, though you'll miss them.

It's the identity.

Because for most healthcare professionals, "nurse" or "doctor" or "NP" isn't a job title. It's the answer to "Who are you?" It's what you were on your wedding day, at your parents' dinner table, in the introduction at every party.

Walking away from the role means walking away from the clearest answer you've ever had to that question.

The work of rebuilding isn't finding a new career. It's finding out who you are when no job title is doing the heavy lifting.

That's the real crossing.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #IdentityLoss #CareerTransition #BurnoutRecovery #HealthcareWorkers #PhysicianBurnout""",
        "ig": """What nobody tells you about leaving a healthcare career.

It's not the income you grieve first. Not even the colleagues.

It's the identity.

"Nurse." "Doctor." "NP." That's not a job title — it's the answer to "Who are you?" at every dinner table and wedding and introduction.

Walking away from the role means walking away from the clearest answer you've ever had to that question.

The real work is finding out who you are when no title is doing the heavy lifting.

That's the real crossing.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #IdentityLoss #CareerTransition #BurnoutRecovery""",
        "fb": """What nobody tells you about leaving a healthcare career.

It's not the income you grieve first. It's not even the colleagues.

It's the identity. Because "nurse" or "doctor" or "NP" isn't a job title for most healthcare professionals — it's the answer to "Who are you?" It's what you were at every dinner table, every introduction, every conversation.

Walking away from the role means walking away from the clearest answer you've ever had to that question.

The real work of recovery is finding out who you are when no title is doing the heavy lifting. That's the real crossing.

#CrosswalkWisdom #HealthcareBurnout #IdentityLoss #CareerTransition #BurnoutRecovery #HealthcareWorkers""",
        "tt": """What nobody tells you about leaving a healthcare career.

It's not the income you grieve first.

It's the identity.

"Nurse." "Doctor." That's not a job title — it's the answer to "Who are you?"

The real crossing is finding out who you are when no title is doing the heavy lifting.

#CrosswalkWisdom #HealthcareBurnout #IdentityLoss #CareerTransition #NurseBurnout""",
    },
    {
        "img": "letter",
        "li": """I walked across the crosswalk in 2019.

I was a physician who had built a career that looked, from the outside, like everything was fine.

It wasn't.

What I didn't understand then — what took me years to see — is that I wasn't just burned out from the work. I was burned out from performing a version of myself that I'd outgrown.

The doctor identity had kept me safe for so long. It answered every question about my worth. It gave me a story to tell.

And then one morning it just... stopped being enough.

The crosswalk was terrifying. I crossed it anyway.

That's what Crosswalk Wisdom is about. Not the career pivot. The identity crossing.

#CrosswalkWisdom #HealthcareBurnout #IdentityLoss #CareerTransition #PhysicianBurnout #BurnoutRecovery #CourageToChoose""",
        "ig": """I walked across the crosswalk in 2019.

A physician. Career that looked, from the outside, like everything was fine.

It wasn't.

I wasn't just burned out from the work. I was burned out from performing a version of myself I'd outgrown.

The identity had kept me safe. Answered every question about my worth. Gave me a story.

Then one morning it stopped being enough.

The crosswalk was terrifying. I crossed it anyway.

That's what this is about. Not the career pivot. The identity crossing.

#CrosswalkWisdom #PhysicianBurnout #IdentityLoss #CareerTransition #BurnoutRecovery #CourageToChoose""",
        "fb": """I walked across the crosswalk in 2019.

I was a physician with a career that looked, from the outside, like everything was fine. It wasn't.

What took me years to see: I wasn't just burned out from the work. I was burned out from performing a version of myself I'd outgrown. The identity had kept me safe. Answered every question about my worth. Gave me a story to tell.

And then one morning it stopped being enough.

The crosswalk was terrifying. I crossed it anyway.

That's what Crosswalk Wisdom is about. Not the career pivot. The identity crossing.

#CrosswalkWisdom #PhysicianBurnout #IdentityLoss #CareerTransition #BurnoutRecovery #CourageToChoose""",
        "tt": """I walked across the crosswalk in 2019.

A physician. Career that looked fine from the outside.

I wasn't just burned out from the work.

I was burned out from performing a version of myself I'd outgrown.

The crosswalk was terrifying. I crossed it anyway.

#CrosswalkWisdom #PhysicianBurnout #IdentityLoss #CareerTransition #BurnoutRecovery""",
    },
    {
        "img": "signal",
        "li": """The system is not broken. It's working exactly as designed.

A system that produces burned-out healthcare workers didn't fail to prevent burnout. It succeeded at something else — extracting maximum output from people trained to prioritize others over themselves.

You're not broken. You're the predictable result of an unpredictable demand.

But here's what that means: recovery isn't about fixing yourself. You don't need to be fixed. You need to disentangle your worth from a system that has always told you your worth is conditional on how much you produce.

That's a different kind of work. And it starts with one question: who are you outside of what you give?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #PhysicianBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers #SystemicBurnout""",
        "ig": """The system is not broken. It's working exactly as designed.

A system that produces burned-out healthcare workers didn't fail to prevent burnout. It succeeded at something else — extracting maximum output from people trained to prioritize others.

You're not broken. You're the predictable result.

Recovery isn't about fixing yourself. It's about disentangling your worth from a system that made it conditional.

Who are you outside of what you give?

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #SystemicBurnout""",
        "fb": """The system is not broken. It's working exactly as designed.

A system that produces burned-out healthcare workers didn't fail to prevent burnout — it succeeded at something else. Extracting maximum output from people trained to prioritize others over themselves.

You're not broken. You're the predictable result of unsustainable demands.

Recovery isn't about fixing yourself. You don't need to be fixed. You need to disentangle your worth from a system that made it conditional on how much you produce.

That starts with one question: who are you outside of what you give?

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
        "tt": """The system is not broken. It's working exactly as designed.

You're not broken.

You're the predictable result of a system that extracts maximum output from people trained to put others first.

Recovery is disentangling your worth from that system.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss""",
    },
    {
        "img": "id_badge",
        "li": """What recovery actually looks like for a burned-out healthcare professional.

It doesn't look like a beach vacation. It doesn't look like finally getting enough sleep.

It looks quiet. Often boring. Sometimes disorienting.

It looks like saying no to something you would have said yes to six months ago — and sitting with the discomfort of people being slightly disappointed.

It looks like having a conversation you've been avoiding for two years.

It looks like doing less. And being surprised that less doesn't feel like failure.

Recovery isn't a destination. It's a reorientation. And it starts — always — with the willingness to name where you actually are.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #HealthcareWorkers #IdentityLoss #CourageToChoose""",
        "ig": """What recovery actually looks like.

Not a beach vacation. Not finally sleeping enough.

Quiet. Boring. Sometimes disorienting.

Saying no to something you'd have said yes to — and sitting with people being slightly disappointed.

Having a conversation you've avoided for two years.

Doing less. Being surprised that less doesn't feel like failure.

Recovery isn't a destination. It's a reorientation.

And it starts with naming where you actually are.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #CourageToChoose""",
        "fb": """What recovery actually looks like for a burned-out healthcare professional.

It doesn't look like a beach vacation or finally getting enough sleep.

It looks quiet. Often boring. Sometimes disorienting.

It looks like saying no to something you would have said yes to six months ago — and sitting with the discomfort of people being slightly disappointed. Like having a conversation you've been avoiding for two years. Like doing less and being surprised that less doesn't feel like failure.

Recovery isn't a destination. It's a reorientation. And it starts with naming where you actually are.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
        "tt": """What recovery actually looks like.

Not a vacation. Not more sleep.

Saying no to things. Sitting with people's disappointment.

Doing less. Being surprised it doesn't feel like failure.

Recovery is a reorientation. It starts with naming where you are.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss""",
    },
    {
        "img": "table",
        "li": """The moment I stopped asking "what should I do next" and started asking "who do I want to be" — everything changed.

That shift sounds simple. It's not.

Because we're trained to think in terms of action. The next career move. The next certification. The next thing that proves you're valuable.

But burnout is rarely a strategy problem. It's an identity problem.

When the strategy questions stop working, it's because they're asking the wrong question.

Who do you want to be? Not what title do you want to hold. Not what salary do you need. Who — the actual person behind all the credentials — do you want to become?

That question is harder. It's also the only one worth answering.

#CrosswalkWisdom #HealthcareBurnout #IdentityLoss #CareerTransition #BurnoutRecovery #CourageToChoose #HealthcareWorkers""",
        "ig": """The moment I stopped asking "what should I do next" and started asking "who do I want to be" — everything changed.

We're trained to think in action terms. Next career move. Next certification. Next thing that proves value.

But burnout is rarely a strategy problem. It's an identity problem.

When strategy stops working, you're asking the wrong question.

Who — the actual person behind the credentials — do you want to become?

Harder question. Only one worth answering.

#CrosswalkWisdom #HealthcareBurnout #IdentityLoss #CareerTransition #BurnoutRecovery #CourageToChoose""",
        "fb": """The moment I stopped asking "what should I do next" and started asking "who do I want to be" — everything changed.

That shift sounds simple. It's not.

We're trained to think in action terms. Next move. Next certification. Next thing that proves value. But burnout is rarely a strategy problem. It's an identity problem.

When the strategy questions stop working, it's because they're asking the wrong thing.

Who — the actual person behind all the credentials — do you want to become?

That question is harder. It's also the only one worth answering.

#CrosswalkWisdom #HealthcareBurnout #IdentityLoss #BurnoutRecovery #CareerTransition #CourageToChoose""",
        "tt": """The moment I stopped asking "what should I do next" and started asking "who do I want to be" — everything changed.

Burnout isn't a strategy problem.

It's an identity problem.

Who — the actual person behind the credentials — do you want to become?

#CrosswalkWisdom #HealthcareBurnout #IdentityLoss #CareerTransition #BurnoutRecovery""",
    },
]

# AFTERNOON (16:00) — engagement / questions
AFTERNOON = [
    {
        "img": "clipboard",
        "li": """Quick question for healthcare workers today.

If you could change one thing about your current situation — just one — what would it be?

I ask because the answer to that question is almost always a window into the fear underneath it.

Drop it in the comments. I read every response.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #HealthcareWorkers #BurnoutRecovery #IdentityLoss""",
        "ig": """Quick question for healthcare workers.

If you could change one thing about your current situation — what would it be?

The answer is almost always a window into the fear underneath it.

Drop it below. I read every response.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #HealthcareWorkers #BurnoutRecovery #IdentityLoss""",
        "fb": """Quick question for healthcare workers today.

If you could change one thing about your current situation — just one — what would it be?

The answer is almost always a window into the fear underneath it. Drop it in the comments — I read every response.

#CrosswalkWisdom #HealthcareBurnout #HealthcareWorkers #BurnoutRecovery""",
        "tt": """Quick question for healthcare workers.

If you could change one thing about your situation right now — what would it be?

The answer is usually a window into the fear underneath it.

Drop it below.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #HealthcareWorkers""",
    },
    {
        "img": "paper",
        "li": """Which of these resonates most with you right now?

A. "I'm tired but I can push through."
B. "I've been running on empty for months."
C. "I've stopped picturing a future."
D. "I'm looking for answers but nothing feels right."

There's no wrong answer. Each one maps to a different place in the burnout journey — and a different next step.

Drop your letter below. I'll share what it means.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #HealthcareWorkers #BurnoutStages""",
        "ig": """Which resonates most right now?

A. "I'm tired but I can push through."
B. "I've been running on empty for months."
C. "I've stopped picturing a future."
D. "I'm looking for answers but nothing feels right."

No wrong answer. Each maps to a different place in burnout — and a different next step.

Drop your letter below.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #HealthcareWorkers #BurnoutStages""",
        "fb": """Which of these resonates most with you right now?

A. "I'm tired but I can push through."
B. "I've been running on empty for months."
C. "I've stopped picturing a future."
D. "I'm looking for answers but nothing feels right."

No wrong answer. Each one maps to a different place in the burnout journey — and a different next step. Drop your letter below.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #BurnoutStages #HealthcareWorkers""",
        "tt": """Which resonates most right now?

A. Tired but pushing through.
B. Running on empty for months.
C. Stopped picturing a future.
D. Looking for answers, nothing feels right.

Drop your letter. I'll share what it means.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutStages""",
    },
    {
        "img": "portrait",
        "li": """What's the one thing you're most afraid to admit about where you are right now?

You don't have to answer out loud. But I'd invite you to answer it honestly — to yourself.

Because in my experience working with burned-out healthcare professionals, the thing they're most afraid to admit is usually the thing that, once named, unlocks everything else.

If you're willing to share: the comments are open. No judgment here.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #HealthcareWorkers #IdentityLoss #CourageToChoose""",
        "ig": """What's the one thing you're most afraid to admit about where you are right now?

You don't have to answer out loud. But answer it honestly — to yourself.

Because the thing healthcare professionals are most afraid to admit is usually what unlocks everything else once named.

If you're willing to share — comments are open. No judgment.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #CourageToChoose""",
        "fb": """What's the one thing you're most afraid to admit about where you are right now?

You don't have to answer out loud. But I'd invite you to answer it honestly — to yourself.

In my experience, the thing healthcare professionals are most afraid to admit is usually the thing that unlocks everything else once it's named.

If you're willing to share, the comments are open. No judgment here.

#CrosswalkWisdom #HealthcareBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
        "tt": """What's the one thing you're most afraid to admit about where you are right now?

You don't have to say it out loud.

But answer it honestly — to yourself.

That's usually the thing that unlocks everything else.

#CrosswalkWisdom #HealthcareBurnout #NurseBurnout #IdentityLoss #BurnoutRecovery""",
    },
]

# EVENING CTA (19:00) — drive to assessments
EVENING_CTA = [
    {
        "img": "clipboard",
        "li": """If you've been reading along and something has been landing — I built something for exactly this moment.

It's called the Fear Audit. Free. 2 minutes. 12 questions.

It tells you which of three fears has been driving your decisions:

→ Financial Insecurity
→ Fear of Judgment
→ Identity Loss

Each one sounds the same on the surface. But they require completely different first steps.

Most burned-out healthcare professionals have never had someone name their specific fear out loud. That name is where recovery actually starts.

Link in the first comment.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers #CourageToChoose""",
        "ig": """Something I built for exactly this moment.

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
        "fb": """If any of this has been landing — I built something for exactly this moment.

The Fear Audit. Free. 2 minutes. 12 questions.

It tells you which of three fears has been driving your decisions: financial insecurity, fear of judgment, or identity loss.

Each one sounds the same on the surface. But they require completely different first steps. Most burned-out healthcare professionals have never had their specific fear named out loud.

That name is where recovery actually starts. Link in the comments.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
        "tt": """Something I built for exactly this moment.

The Fear Audit. Free. 2 minutes.

Names which fear has been making your decisions:

→ Financial insecurity
→ Fear of judgment
→ Identity loss

That name is where recovery starts.

Link in bio.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #BurnoutRecovery #IdentityLoss""",
    },
    {
        "img": "crosswalk",
        "li": """One of the questions on the Crosswalk Burnout Assessment reads:

"I've stopped imagining a future."

If that sentence just landed somewhere in you — you already know which stage you're in.

Burnout isn't a yes or no. It's a location. And the location determines everything about what you actually need right now.

I built a free 12-question assessment that places you in one of four stages — and gives you the specific next step for where you are, not a generic wellness list.

2 minutes. Free. Built for healthcare workers.

Link in the first comment.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #NurseBurnout #BurnoutRecovery #BurnoutStages #IdentityLoss""",
        "ig": """One of the questions on the Crosswalk Burnout Assessment reads:

"I've stopped imagining a future."

If that sentence landed — you already know which stage you're in.

Burnout isn't yes or no. It's a location. And the location determines what you actually need.

4 stages. 12 questions. 2 minutes. Free.

Built for healthcare workers.

Link in bio — or first comment.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #NurseBurnout #BurnoutRecovery #BurnoutStages""",
        "fb": """One of the questions on the Crosswalk Burnout Assessment reads: "I've stopped imagining a future."

If that sentence landed somewhere in you — you already know which stage you're in.

Burnout isn't a yes or no. It's a location. The location determines what you actually need right now.

Free 12-question assessment. Places you in one of four stages. Gives you the specific next step for where you are — not a generic list.

2 minutes. Free. Link in the comments.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery #BurnoutStages #HealthcareWorkers""",
        "tt": """One question on the Crosswalk Burnout Assessment:

"I've stopped imagining a future."

If that sentence landed — you already know which stage you're in.

4 stages. 12 questions. 2 minutes. Free.

Link in bio.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #BurnoutStages #BurnoutRecovery""",
    },
    {
        "img": "laptop",
        "li": """The Fear Audit has now been taken by hundreds of healthcare workers.

The most common result?

Identity Loss.

"If I'm not the person who handles everything, who am I?"

That fear looks like dedication from the outside. From the inside, it feels like a cage you can't find the door to.

The assessment doesn't fix that. But it names it. And naming it is the first move — the only first move that actually works.

Free. 2 minutes. Link in the first comment.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #NurseBurnout #IdentityLoss #BurnoutRecovery #HealthcareWorkers""",
        "ig": """The Fear Audit has been taken by hundreds of healthcare workers.

The most common result? Identity Loss.

"If I'm not the person who handles everything — who am I?"

That fear looks like dedication from the outside. From the inside, it feels like a cage you can't find the door to.

The assessment names it. And naming it is the only first move that works.

Free. 2 minutes. Link in bio.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #NurseBurnout #IdentityLoss #BurnoutRecovery""",
        "fb": """The Fear Audit has been taken by hundreds of healthcare workers.

The most common result? Identity Loss.

"If I'm not the person who handles everything, who am I?"

That fear looks like dedication from the outside. From the inside, it feels like a cage you can't find the door to.

The assessment doesn't fix that. But it names it — and naming it is the first move that actually works.

Free. 2 minutes. Link in the comments.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #IdentityLoss #BurnoutRecovery #HealthcareWorkers""",
        "tt": """The Fear Audit's most common result?

Identity Loss.

"Who am I if I'm not the person who handles everything?"

Looks like dedication from the outside. Feels like a cage from the inside.

Naming it is the first move.

Free. 2 mins. Link in bio.

#CrosswalkWisdom #FearAudit #IdentityLoss #HealthcareBurnout #BurnoutRecovery""",
    },
    {
        "img": "hospital",
        "li": """I want to ask you something before you end your day.

How long have you known something needed to change?

Not suspected. Known.

For most healthcare workers I talk to, the honest answer is months. Sometimes years.

The knowing doesn't feel like a decision point. It feels like background noise — always there, easy to push past.

The fear isn't that you don't know what to do. It's that knowing requires acting. And acting requires courage you're not sure you have.

You have it. It just needs a starting point.

The Burnout Assessment gives you a specific one. Free. 2 minutes. Link in the first comment.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #CourageToChoose""",
        "ig": """Before you end your day — one question.

How long have you known something needed to change?

Not suspected. Known.

For most healthcare workers, the honest answer is months. Sometimes years.

The knowing doesn't feel like a decision point. It feels like background noise — always there, easy to push past.

The fear isn't that you don't know what to do. It's that knowing requires acting.

You have that courage. It just needs a starting point.

Link in bio.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery #IdentityLoss #CourageToChoose""",
        "fb": """Before you end your day — how long have you known something needed to change?

Not suspected. Known.

For most healthcare workers, the honest answer is months. Sometimes years.

The knowing doesn't feel like a decision point — it feels like background noise you push past every day.

The fear isn't that you don't know what to do. It's that knowing requires acting. And acting requires courage you're not sure you have.

You have it. It just needs a starting point. Link in the comments.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery #IdentityLoss #CourageToChoose""",
        "tt": """Before you end your day — one question.

How long have you known something needed to change?

Not suspected. Known.

Most healthcare workers: months. Sometimes years.

You have the courage to act. It just needs a starting point.

Link in bio.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery #IdentityLoss""",
    },
    {
        "img": "hands_lap",
        "li": """Two free tools. Two minutes each.

If you don't know where to start — start here.

The Fear Audit (fear-audit.vercel.app) tells you which fear has been making your decisions. Financial insecurity, fear of judgment, or identity loss.

The Burnout Assessment (crosswalkwisdom.com/assessment) tells you which stage you're in — START, STOP, ELDER, or HUMAN — and gives you the specific next step for exactly where you are.

They're different tools. Both are free. Both take 2 minutes.

Most people who take both come back and say the same thing: "I didn't realize that was what this was."

That's exactly the point. Links in the first comment.

#CrosswalkWisdom #FearAudit #BurnoutAssessment #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss""",
        "ig": """Two free tools. Two minutes each.

Fear Audit — which fear has been making your decisions.
Burnout Assessment — which stage you're in and the specific next step.

Different tools. Both free. Both 2 minutes.

Most people who take both say: "I didn't realize that was what this was."

That's exactly the point.

Links in bio — or first comment.

#CrosswalkWisdom #FearAudit #BurnoutAssessment #HealthcareBurnout #NurseBurnout #BurnoutRecovery""",
        "fb": """Two free tools. Two minutes each.

The Fear Audit: tells you which fear has been making your decisions — financial insecurity, fear of judgment, or identity loss.

The Burnout Assessment: tells you which of 4 stages you're in and gives you the specific next step for exactly where you are.

Different tools. Both free. Both 2 minutes.

Most people who take both say the same thing: "I didn't realize that was what this was."

That's exactly the point. Links in the comments.

#CrosswalkWisdom #FearAudit #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery #IdentityLoss""",
        "tt": """Two free tools. Two minutes each.

Fear Audit: which fear has been making your decisions.

Burnout Assessment: which stage you're in + specific next step.

Most people: "I didn't realize that was what this was."

That's the point. Links in bio.

#CrosswalkWisdom #FearAudit #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery""",
    },
    {
        "img": "car",
        "li": """Burnout recovery has a specific starting point.

It's not a habit change. It's not a career pivot. It's not a meditation practice.

It's a name.

The name of the thing that has been keeping you stuck.

Most burned-out healthcare professionals have never had that name spoken to them. They know something is wrong. They know something needs to change. But without the name, every intervention is a guess.

I built two free assessments to give you that name. Two minutes each. No email required to start.

Link in the first comment.

#CrosswalkWisdom #FearAudit #BurnoutAssessment #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
        "ig": """Burnout recovery has a specific starting point.

Not a habit change. Not a career pivot. Not a meditation practice.

A name.

The name of what's been keeping you stuck.

Most burned-out healthcare workers have never had that name spoken to them.

Without it, every intervention is a guess.

Two free assessments. Two minutes each. Link in bio.

#CrosswalkWisdom #FearAudit #BurnoutAssessment #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss""",
        "fb": """Burnout recovery has a specific starting point.

Not a habit change. Not a career pivot. Not a meditation practice.

A name.

The name of the thing that has been keeping you stuck.

Most burned-out healthcare professionals have never had that name spoken to them. They know something is wrong. But without it, every intervention is a guess.

I built two free assessments to give you that name. Two minutes each. Link in the comments.

#CrosswalkWisdom #FearAudit #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery #IdentityLoss""",
        "tt": """Burnout recovery has a specific starting point.

Not a habit change. Not a career pivot.

A name.

The name of what's been keeping you stuck.

Two free assessments. Two minutes. Link in bio.

#CrosswalkWisdom #FearAudit #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery""",
    },
    {
        "img": "scrubs",
        "li": """For the healthcare worker who is tired of reading about burnout without anything actually changing.

The problem isn't information. You have information.

The problem is that information lands differently when it doesn't know what you're afraid of.

I built the Fear Audit for exactly this: to give you the specific name of the fear that's been keeping your decisions stuck.

Financial insecurity. Fear of judgment. Identity loss.

That name tells you what kind of first step actually works for you.

Not for everyone. For you.

2 minutes. Free. Link in the first comment.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers #CourageToChoose""",
        "ig": """For the healthcare worker tired of reading about burnout without anything changing.

The problem isn't information. You have information.

The problem is it doesn't know what you're afraid of.

The Fear Audit names your specific fear:

→ Financial insecurity
→ Fear of judgment
→ Identity loss

That name tells you what first step works for you. Not everyone. You.

2 minutes. Free. Link in bio.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #NurseBurnout #BurnoutRecovery #IdentityLoss""",
        "fb": """For the healthcare worker who is tired of reading about burnout without anything actually changing.

The problem isn't information. You have information. The problem is that information lands differently when it doesn't know what you're afraid of.

The Fear Audit gives you the specific name of your fear: financial insecurity, fear of judgment, or identity loss.

That name tells you what first step actually works for you — not for everyone, for you.

2 minutes. Free. Link in the comments.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #BurnoutRecovery #IdentityLoss #HealthcareWorkers""",
        "tt": """For the healthcare worker tired of reading about burnout without anything changing.

The problem isn't information.

It's that information doesn't know what you're afraid of.

The Fear Audit names your specific fear.

2 minutes. Free. Link in bio.

#CrosswalkWisdom #FearAudit #HealthcareBurnout #NurseBurnout #BurnoutRecovery""",
    },
    {
        "img": "table",
        "li": """I want to ask you something before this week ends.

What would it mean for you to give yourself permission — not to have it all figured out, not to be recovered, not to be ready — just to start?

Not a leap. Not a pivot. Just: to acknowledge where you are and take one honest step from there.

That's what the crosswalk is about. Not the destination. The willingness to step off the curb.

If you're not sure where to start, I built something that can help point you. Free. 2 minutes. Link in the first comment.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #NurseBurnout #BurnoutRecovery #CourageToChoose #IdentityLoss #HealthcareWorkers""",
        "ig": """Before this week ends — one question.

What would it mean to give yourself permission to start?

Not to have it figured out. Not to be recovered. Not to be ready.

Just to acknowledge where you are and take one honest step from there.

That's what the crosswalk is about.

Not the destination. The willingness to step off the curb.

Link in bio if you need a starting point.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #NurseBurnout #BurnoutRecovery #CourageToChoose #IdentityLoss""",
        "fb": """Before this week ends — one question.

What would it mean to give yourself permission to just start?

Not to have it figured out. Not to be recovered. Not to be ready.

Just to acknowledge where you are and take one honest step from there.

That's the whole crosswalk metaphor. Not the destination — the willingness to step off the curb.

If you're not sure where to start, I built something that can help. Free. 2 minutes. Link in the comments.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery #CourageToChoose #IdentityLoss""",
        "tt": """Before this week ends — one question.

What would it mean to give yourself permission to just start?

Not to be recovered. Not to be ready.

Just — to acknowledge where you are and take one honest step.

That's the crosswalk.

#CrosswalkWisdom #BurnoutAssessment #HealthcareBurnout #BurnoutRecovery #CourageToChoose""",
    },
]

# ─────────────────────────────────────────────
# SCHEDULE: (date, time) → (slot_type, variant_index)
# ─────────────────────────────────────────────
# slot_types: morning=MORNING, edu=EDUCATIONAL, main=MAIN, afternoon=AFTERNOON, eve=EVENING_CTA
SCHEDULE = [
    # April 5
    ("2026-04-05", "07:00", "morning", 0),
    ("2026-04-05", "19:00", "eve", 0),
    # April 6
    ("2026-04-06", "07:00", "morning", 1),
    # April 7
    ("2026-04-07", "07:00", "morning", 2),
    ("2026-04-07", "19:00", "eve", 1),
    # April 8
    ("2026-04-08", "07:00", "morning", 3),
    ("2026-04-08", "10:00", "edu", 0),
    ("2026-04-08", "16:00", "afternoon", 0),
    ("2026-04-08", "19:00", "eve", 2),
    # April 9
    ("2026-04-09", "07:00", "morning", 4),
    ("2026-04-09", "13:00", "main", 0),
    # April 10
    ("2026-04-10", "07:00", "morning", 5),
    ("2026-04-10", "10:00", "edu", 1),
    ("2026-04-10", "19:00", "eve", 3),
    # April 11
    ("2026-04-11", "07:00", "morning", 6),
    ("2026-04-11", "10:00", "edu", 2),
    ("2026-04-11", "19:00", "eve", 4),
    # April 12
    ("2026-04-12", "07:00", "morning", 7),
    ("2026-04-12", "10:00", "edu", 3),
    ("2026-04-12", "19:00", "eve", 5),
    # April 13
    ("2026-04-13", "07:00", "morning", 0),
    ("2026-04-13", "10:00", "edu", 4),
    ("2026-04-13", "13:00", "main", 1),
    # April 14
    ("2026-04-14", "07:00", "morning", 1),
    ("2026-04-14", "13:00", "main", 2),
    ("2026-04-14", "19:00", "eve", 6),
    # April 15
    ("2026-04-15", "07:00", "morning", 2),
    ("2026-04-15", "10:00", "edu", 5),
    ("2026-04-15", "19:00", "eve", 7),
    # April 16
    ("2026-04-16", "07:00", "morning", 3),
    ("2026-04-16", "13:00", "main", 3),
    ("2026-04-16", "19:00", "eve", 0),
    # April 17
    ("2026-04-17", "07:00", "morning", 4),
    ("2026-04-17", "10:00", "edu", 6),
    ("2026-04-17", "16:00", "afternoon", 1),
    ("2026-04-17", "19:00", "eve", 1),
    # April 18
    ("2026-04-18", "07:00", "morning", 5),
    ("2026-04-18", "13:00", "main", 4),
    ("2026-04-18", "19:00", "eve", 2),
    # April 19
    ("2026-04-19", "07:00", "morning", 6),
    ("2026-04-19", "10:00", "edu", 7),
    ("2026-04-19", "19:00", "eve", 3),
    # April 20
    ("2026-04-20", "07:00", "morning", 7),
    ("2026-04-20", "10:00", "edu", 0),
    # April 21
    ("2026-04-21", "07:00", "morning", 0),
    ("2026-04-21", "13:00", "main", 5),
    ("2026-04-21", "19:00", "eve", 4),
    # April 22
    ("2026-04-22", "07:00", "morning", 1),
    ("2026-04-22", "10:00", "edu", 1),
    ("2026-04-22", "19:00", "eve", 5),
    # April 23
    ("2026-04-23", "07:00", "morning", 2),
    ("2026-04-23", "13:00", "main", 6),
    ("2026-04-23", "19:00", "eve", 6),
    # April 24
    ("2026-04-24", "07:00", "morning", 3),
    ("2026-04-24", "10:00", "edu", 2),
    ("2026-04-24", "19:00", "eve", 7),
    # April 25
    ("2026-04-25", "07:00", "morning", 4),
    ("2026-04-25", "13:00", "main", 7),
    ("2026-04-25", "19:00", "eve", 0),
    # April 26
    ("2026-04-26", "07:00", "morning", 5),
    ("2026-04-26", "10:00", "edu", 3),
    ("2026-04-26", "19:00", "eve", 1),
    # April 27
    ("2026-04-27", "07:00", "morning", 6),
    ("2026-04-27", "10:00", "edu", 4),
    # April 28
    ("2026-04-28", "07:00", "morning", 7),
    ("2026-04-28", "13:00", "main", 0),
    ("2026-04-28", "19:00", "eve", 2),
    # April 29
    ("2026-04-29", "07:00", "morning", 0),
    ("2026-04-29", "10:00", "edu", 5),
    ("2026-04-29", "19:00", "eve", 3),
    # April 30
    ("2026-04-30", "07:00", "morning", 1),
    ("2026-04-30", "13:00", "main", 1),
    ("2026-04-30", "19:00", "eve", 4),
]

BANK_MAP = {
    "morning":   MORNING,
    "edu":       EDUCATIONAL,
    "main":      MAIN,
    "afternoon": AFTERNOON,
    "eve":       EVENING_CTA,
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
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
    print(f"    Uploading...")
    with open(filepath, "rb") as f:
        put_r = requests.put(upload_url, data=f, headers={"Content-Type": "image/jpeg"})
        put_r.raise_for_status()
    print(f"    Upload OK → {public_url[:70]}...")
    _url_cache[filepath] = public_url
    return public_url


def schedule_post(image_url, li_copy, ig_copy, fb_copy, tt_copy, scheduled_for):
    platforms = [
        {"platform": "linkedin",  "accountId": LINKEDIN_ID,  "customContent": li_copy, "scheduledFor": scheduled_for},
        {"platform": "instagram", "accountId": INSTAGRAM_ID, "customContent": ig_copy, "scheduledFor": scheduled_for},
        {"platform": "facebook",  "accountId": FACEBOOK_ID,  "customContent": fb_copy, "scheduledFor": scheduled_for},
        {"platform": "tiktok",    "accountId": TIKTOK_ID,    "customContent": tt_copy, "scheduledFor": scheduled_for},
    ]
    body = {
        "content": li_copy,
        "mediaItems": [{"url": image_url, "type": "image"}],
        "platforms": platforms,
        "scheduledFor": scheduled_for,
        "timezone": TIMEZONE,
    }
    r = requests.post(f"{BASE}/posts", headers=HEADERS, json=body)
    return r.status_code, r.text[:200]


def main():
    print("=== April 2026 Gap Fill — 5 posts/day ===")
    print(f"Total posts to schedule: {len(SCHEDULE)}\n")

    ok = 0
    fail = 0

    for idx, (date, time_slot, bank_key, variant_idx) in enumerate(SCHEDULE, 1):
        scheduled_for = f"{date}T{time_slot}:00"
        bank = BANK_MAP[bank_key]
        content = bank[variant_idx % len(bank)]
        img_key = content["img"]

        label = f"[{idx:02d}/{len(SCHEDULE)}] {date} {time_slot} ({bank_key}/{variant_idx})"
        print(f"{label}")

        if not os.path.exists(IMAGES[img_key]):
            print(f"  ERROR: image not found: {IMAGES[img_key]}")
            fail += 1
            continue

        try:
            image_url = upload_image(img_key)
            status, resp = schedule_post(
                image_url,
                content["li"],
                content["ig"],
                content["fb"],
                content["tt"],
                scheduled_for,
            )
            if status in (200, 201):
                print(f"  ✓ Scheduled")
                ok += 1
            else:
                print(f"  ✗ Status {status}: {resp}")
                fail += 1
        except Exception as e:
            print(f"  ✗ Exception: {e}")
            fail += 1

        time.sleep(0.8)

    print(f"\n=== Done: {ok} scheduled, {fail} failed ===")
    print("Reminder: add first comments with assessment links on posts after they publish.")
    print("  → Fear Audit posts: fear-audit.vercel.app")
    print("  → Burnout Assessment posts: crosswalkwisdom.com/assessment")


if __name__ == "__main__":
    main()
