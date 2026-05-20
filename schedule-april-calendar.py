#!/usr/bin/env python3
"""
Crosswalk Wisdom — April 2026 Social Media Scheduler
Schedules all unscheduled April posts via the Zernio API.
Skipped dates (already in Zernio): Mar 26-28, 30-31, Apr 2-4, 7, 9, 13-14, 16, 18, 21, 23, 25, 28, 30, May 2
Dates to schedule: Apr 1, 5, 6, 8, 10, 11, 12, 15, 17, 19, 20, 22, 24, 26, 27, 29
"""

import json
import requests

# ─── API CONFIG ───────────────────────────────────────────────────────────────
BASE_URL = "https://zernio.com/api/v1"
API_KEY  = "sk_d1c977cc304ec9685c24f22c7e3b868abd5a10b9db8f7648b2b74384ab1ca399"

LINKEDIN_ACCOUNT_ID  = "690940455f6fbb9ef8323070"
INSTAGRAM_ACCOUNT_ID = "690940655f6fbb9ef8323072"
FACEBOOK_ACCOUNT_ID  = "6909409a5f6fbb9ef8323074"

TIMEZONE  = "America/New_York"
POST_TIME = "09:00:00"

# ─── POST DATA ────────────────────────────────────────────────────────────────
POSTS = [

    # ─────────────────────────────────────────────────────────────────────────
    # DAY 1 — Wednesday, April 1
    # ─────────────────────────────────────────────────────────────────────────
    {
        "date": "2026-04-01",
        "title": "Day 1 — Origin Story",
        "linkedin": """I left medicine.

Not because I burned out (though I did). Not because I couldn't cut it (I could). But because I woke up one morning and realized I had spent 15 years building an identity — and none of it was actually mine.

"Doctor" was my answer to every question. Who are you? Doctor. What do you do? Doctor. What's your purpose? Doctor.

When I finally left, people asked: "What happened?"

Nothing happened. Everything happened. I just stopped pretending the title was enough.

I became a crossing guard. Yes, really. And that crosswalk taught me more about healing than a decade of practice ever did.

Standing at that intersection every morning, helping people get from one side to the other — I realized that's what I'd always been doing. Just without the scrubs.

Now I run Crosswalk Wisdom, where I help healthcare professionals navigate the scariest crossing of their lives: the one from who they were told to be to who they actually are.

If you're in healthcare and you've ever whispered "I don't know how much longer I can do this" — you're not broken. You're ready.

The crosswalk is waiting.

I'm Sahawat. I'm a former physician, a former crossing guard, and now a guide for people brave enough to cross.

Welcome.""",
        "instagram": """I used to introduce myself as "Doctor."

It was the first word out of my mouth at parties, at parent meetings, at the grocery store when someone asked what I did. It wasn't a job title. It was my entire identity.

And then I left.

Not because I failed. Not because I couldn't handle it. But because I realized something that terrified me more than any diagnosis I'd ever given:

I had no idea who I was without the white coat.

So I did something no one understood. I became a crossing guard.

Every morning, I stood at a crosswalk — holding a stop sign, watching kids look both ways, helping people get from one side to the other.

And somewhere between the yellow lines, I started to heal.

Not the kind of healing I was trained for. Not the kind with charts and protocols. The kind that happens when you finally stop performing and start breathing.

That crosswalk became my classroom. The street became my teacher. And the lesson was simple:

You are allowed to cross.

You are allowed to leave one side and walk toward something new — even if you can't see what's on the other side yet.

That's why I built Crosswalk Wisdom. For the nurses crying in parking lots. For the doctors who feel trapped by a title. For the caregivers who gave everything and forgot to save anything for themselves.

If you're standing at that curb right now — afraid to step off — I want you to know: I've been there. And the other side is real.

Welcome to the crosswalk.""",
        "facebook": """I've been carrying this story for a while. Today I'm sharing it.

I was a physician. I left. I became a crossing guard.

People thought I lost my mind. My family worried. My colleagues were confused. "You went to medical school for THIS?"

But here's what they didn't understand:

I wasn't running away from medicine. I was running toward myself.

That crosswalk — the one I stood at every single morning with a stop sign in my hand — it taught me something no textbook ever could: Healing starts when you stop pretending you're fine.

I watched kids cross the street every day. They'd look both ways. They'd wait for the signal. And then they'd walk — trusting that someone was watching out for them.

I wanted someone to watch out for me like that. And when I couldn't find that person, I decided to become that person — for every healthcare worker standing at their own crosswalk, afraid to take the first step.

That's Crosswalk Wisdom.

If you're a nurse, a doctor, a caregiver, a pharmacist — and you've been standing at the curb wondering if it's safe to cross — pull up a chair. You're home.

Drop a crosswalk emoji in the comments if you've ever felt stuck between who you are and who you're supposed to be.""",
        "hashtags": "#CrosswalkWisdom #NurseBurnoutRecovery #LeavingMedicine #HealthcareBurnoutSupport #CareerTransition #HealingJourney #NurseBurnout #BurnoutRecovery #HealthcareIdentityCrisis #MidlifeCareerChange #NurseTransition #NewChapter #BurnedOutNurse",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DAY 5 — Sunday, April 5
    # ─────────────────────────────────────────────────────────────────────────
    {
        "date": "2026-04-05",
        "title": "Day 5 — Grief Post",
        "linkedin": """There's a grief nobody talks about in healthcare.

Not the grief of losing patients — we're trained for that (barely, but we're trained).

I'm talking about the grief of losing yourself.

The grief that shows up when you realize your career has become a costume. When "I'm a doctor" stops being a proud statement and starts being a cage. When the thing you sacrificed everything for starts taking everything from you.

I experienced this grief firsthand. And I want to name it clearly, because I think millions of healthcare professionals are feeling it right now and don't have a word for it:

It's occupational grief. The mourning of a professional identity that no longer fits.

It looks like crying in the car after a shift — not because something terrible happened, but because nothing happened and you still felt empty.

It looks like scrolling job boards at 2am, not applying to anything, just... wondering.

It looks like snapping at the people you love because you have nothing left to give after giving all day.

This grief is not a clinical term. You won't find it in the DSM. But it's as real as any loss I've ever witnessed.

And here's what I wish someone had told me when I was in the thick of it:

You're not falling apart. You're outgrowing a container that was never built to hold all of who you are.

If this resonates, I'd be honored if you shared it. Someone in your network needs to read this today.""",
        "instagram": """Nobody warns you about the grief.

They warn you about burnout. They warn you about compassion fatigue. They even warn you about the pay.

But nobody tells you that leaving healthcare feels like a death.

Because it is one.

It's the death of the person you built. The one who stayed late. The one who held hands during codes. The one who knew exactly who she was when someone asked "what do you do?"

When I left medicine, I didn't feel free. I felt hollow. Like I'd amputated something essential and was still reaching for it in the dark.

It took me months to understand that what I was feeling wasn't regret. It was grief.

Grief for the identity I'd worn like armor. Grief for the version of me that believed the title was the point. Grief for all the years I spent building a life that looked right but felt wrong.

If you're in that place right now — the place where you've left or you're about to leave and everything feels like loss — I want you to know:

Grief is not a sign you made the wrong choice. Grief is proof you cared. And caring deeply is not a flaw. It's the reason you'll build something extraordinary on the other side.

The crosswalk has room for your grief too. Bring it. We'll carry it together.""",
        "facebook": """Nobody warns you about the grief.

They warn you about burnout. They warn you about compassion fatigue. They even warn you about the pay.

But nobody tells you that leaving healthcare feels like a death.

Because it is one.

It's the death of the person you built. The one who stayed late. The one who held hands during codes. The one who knew exactly who she was when someone asked "what do you do?"

When I left medicine, I didn't feel free. I felt hollow. Like I'd amputated something essential and was still reaching for it in the dark.

It took me months to understand that what I was feeling wasn't regret. It was grief.

Grief is not a sign you made the wrong choice. Grief is proof you cared. And caring deeply is not a flaw. It's the reason you'll build something extraordinary on the other side.

The crosswalk has room for your grief too. Bring it. We'll carry it together.""",
        "hashtags": "#HealthcareIdentityCrisis #NurseBurnoutRecovery #LeavingNursing #HealingFromBurnout #BurnoutRecovery #GriefAndLoss #NurseBurnout #CareerTransition #HealingJourney #MentalHealthMatters #CrosswalkWisdom #NurseTransition #LeavingMedicine",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DAY 6 — Monday, April 6
    # ─────────────────────────────────────────────────────────────────────────
    {
        "date": "2026-04-06",
        "title": "Day 6 — AI as Bridge",
        "linkedin": """Hot take: AI is the most underutilized career transition tool in healthcare right now.

Not because it can write your resume (it can). Not because it can prep you for interviews (it can do that too). But because it can do something far more important:

It can help you see your own story from the outside.

When you've spent 10, 15, 20 years in healthcare, your entire professional identity is wrapped in clinical language. You describe yourself in terms of certifications, specialties, and patient loads.

But the skills that actually make you extraordinary? Emotional regulation under pressure. Complex decision-making with incomplete information. Communicating life-altering news with compassion. Managing teams in crisis.

Those skills don't show up on your nursing license. But they're exactly what the world outside healthcare is desperate for.

I've been using AI to help healthcare professionals reframe their career narratives. Not as "former nurses" but as leaders with rare, battle-tested skills that translate everywhere.

One prompt I use regularly:

"Take my clinical experience as a [role] and translate my top 5 skills into language that a non-healthcare employer or client would immediately understand and value."

The results consistently surprise people. Not because AI is magic — but because it holds up a mirror without the bias of your own exhaustion.

If you're in healthcare and thinking about what's next, AI isn't a luxury. It's a bridge.

Try the prompt above and let me know what comes back.""",
        "instagram": """When I left medicine, I had no idea how to describe what I'd done in a way that didn't start and end with "physician."

My resume was a list of clinical skills. My LinkedIn was a medical CV. My entire professional identity was built around one word.

So I did something unconventional. I opened ChatGPT and typed:

"I'm a former physician who left clinical practice. I now work as a crossing guard and I'm building a coaching business for healthcare professionals experiencing burnout. Help me rewrite my professional story in a way that centers my transferable skills, emotional intelligence, and unique perspective — not my clinical credentials."

What came back wasn't perfect. But it was the first time I'd ever seen my story reflected back to me as something valuable — not something broken.

That's what AI can do for career changers. It's not about replacing your thinking. It's about showing you a version of your story you've been too close to see.

Here's the prompt framework if you want to try it yourself:

"I'm a [current/former role] who is transitioning to [new direction]. Help me rewrite my professional narrative focusing on [transferable skills, values, unique perspective] rather than [specific credentials or titles]."

Try it. Screenshot your result. DM it to me. I'd love to see what comes up for you.""",
        "facebook": """Okay, I want to try something with you all.

If you're a healthcare professional — current or former — I want you to open ChatGPT (or any AI tool) and type this:

"I'm a [your role] with [X years] of experience. I'm considering a career change. What are 5 transferable skills I have that I might not recognize because they feel so normal to me?"

Then come back here and share what surprised you most.

I did this exercise myself when I left medicine. The AI told me I had "crisis leadership skills, advanced empathetic communication, and high-stakes decision-making capacity."

I had been describing myself as "a doctor who quit."

Same person. Completely different story.

Your skills are not trapped in healthcare. They're portable. Let's prove it together.

Try it and report back.""",
        "hashtags": "#AIinHealthcare #CareerTransition #HealthcareBurnout #ProfessionalDevelopment #CrosswalkWisdom #AIforCareerChange #NurseTransition #ChatGPT #ArtificialIntelligence #CareerChangeNurse #NurseBurnoutRecovery #HealthcareBurnoutSupport #NewChapter",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DAY 8 — Wednesday, April 8
    # ─────────────────────────────────────────────────────────────────────────
    {
        "date": "2026-04-08",
        "title": "Day 8 — Identity Loss Deep Dive",
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
        "hashtags": "#FearAudit #HealthcareIdentityCrisis #NurseBurnoutRecovery #LeavingNursing #IdentityCrisis #CareerChangeNurse #NurseBurnout #BurnoutRecovery #CrosswalkWisdom #TheCrosswalkMethod #HealingJourney #NurseTransition #CareerTransition",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DAY 10 — Friday, April 10
    # ─────────────────────────────────────────────────────────────────────────
    {
        "date": "2026-04-10",
        "title": "Day 10 — Fear of Judgment",
        "linkedin": """The second fear that keeps healthcare professionals stuck:

Fear of Judgment.

I want to break this one down because it's more layered than people think.

Layer 1: Family.
"My parents sacrificed so I could go to nursing school. How do I tell them I want to leave?"

Layer 2: Colleagues.
"If I leave, they'll think I couldn't handle it. They'll talk."

Layer 3: Society.
"Healthcare workers are heroes. Walking away makes me what — a quitter?"

Layer 4 — and this is the one nobody mentions: Yourself.
"The version of me who chose this career — am I betraying her?"

That last layer is where the real work happens. Because external judgment fades. Your mom adjusts. Your coworkers move on. Society forgets.

But your own internal jury? That one follows you.

The Stoics had a framework for this. Marcus Aurelius wrote: "It never ceases to amaze me: we all love ourselves more than other people, but care more about their opinion than our own."

Two thousand years later, and we're still doing it.

The antidote to Fear of Judgment isn't thick skin. It's self-trust. Learning to value your own assessment of your life more than anyone else's commentary on it.

That's what crossing looks like. Not fearlessness — but choosing your own opinion over the crowd's.

What judgment are you most afraid of? I'd love to hear honestly.""",
        "instagram": """"But you worked so hard to get here."

That one sentence has kept more healthcare workers trapped than any student loan.

Because it weaponizes your past against your future. It takes the sacrifice you made — the late nights studying, the clinicals, the boards, the years of training — and turns it into a chain.

But here's what I want you to consider:

The fact that you worked hard to get here doesn't mean you have to stay here.

A bridge is not a destination. You crossed it to get somewhere. And sometimes, where it brought you isn't where you need to be.

Fear of Judgment — the second of the three fears — isn't really about other people. It's about the version of yourself that still believes you need permission to change your mind.

You don't.

You are allowed to honor everything you've built and still choose to build something new.

The crosswalk goes both ways. But the light only stays green for so long.""",
        "facebook": """Friday question for the group:

What's the most unhelpful thing someone has said to you about your burnout or your desire to leave healthcare?

I'll start: "But you're so good at it."

As if being good at something means you owe it your entire life.

What's yours? Let's name them so they lose their power.""",
        "hashtags": "#FearOfJudgment #HealthcareBurnout #Stoicism #CareerTransition #CrosswalkWisdom #NurseBurnoutRecovery #LeavingNursing #HealthcareBurnoutSupport #CareerChangeNurse #NurseBurnout #BurnoutRecovery #FearAudit #NurseTransition #HealthcareIdentityCrisis #MentalHealthMatters",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DAY 11 — Saturday, April 11
    # ─────────────────────────────────────────────────────────────────────────
    {
        "date": "2026-04-11",
        "title": "Day 11 — The Crosswalk Method",
        "linkedin": """Alfred Adler believed that our deepest suffering comes not from what happens to us — but from the gap between who we are and who we feel we should be.

He called it the "inferiority gap." And I think it explains healthcare burnout better than any modern framework I've seen.

Think about it:

You entered healthcare with an ideal self — compassionate, competent, making a difference. That was the "should be."

Then reality happened. The system happened. The bureaucracy, the understaffing, the moral injury of knowing what your patients need and being unable to provide it.

And slowly, a gap opened. Between the healer you wanted to be and the worker you were forced to become.

That gap? That's where burnout lives. Not in the long hours. Not in the difficult patients. In the distance between your values and your daily reality.

Adler's solution wasn't to close the gap by trying harder. It was to redefine the ideal. To ask: "What if who I should be isn't who I was told to be — but who I actually am?"

That's the crossing. That's the work.

Not fixing yourself. Redefining what "fixed" even means.

If you're feeling that gap right now — between who you are at work and who you know yourself to be — it's not burnout telling you to rest. It's wisdom telling you to move.""",
        "instagram": """The Crosswalk Method.

I didn't plan this framework. It came to me one morning while I was standing at the intersection, watching the same pattern unfold for the hundredth time:

START — You stand on the curb. You see the other side. Something in you says "it's time." This is the awareness stage. You can't un-see it once you see it.

STOP — You pause. You check both ways. You assess the risks, the fears, the unknowns. This isn't hesitation — it's wisdom. Rushing into traffic helps no one.

ELDER — You look for guidance. A crossing guard. A mentor. Someone who's been to the other side and can tell you: yes, it's real. Yes, it's worth it. You don't have to cross alone.

HUMAN — You step into the crosswalk. Not as a doctor. Not as a nurse. Not as any title. Just as a human being choosing to move forward. This is where healing begins.

START. STOP. ELDER. HUMAN.

That's the crossing. That's the method. And it works whether you're leaving healthcare, leaving a relationship, or leaving any version of yourself that no longer fits.

Where are you in the crossing right now? START, STOP, ELDER, or HUMAN?""",
        "facebook": """I want to introduce you to something I call The Crosswalk Method.

It came to me during my time as a crossing guard — watching the same beautiful pattern unfold every morning:

START — You see the other side. You feel the pull. You know something has to change. This is awareness, and you can't go back to sleep once you've woken up.

STOP — You pause at the curb. You look both ways. You assess. What are the risks? What are the fears? What's the worst case? This isn't weakness — it's the smartest thing you can do before crossing any street.

ELDER — You look for a guide. Someone who's already crossed. Someone who can say "I know that curb. I stood there too. And the other side is real." You don't have to figure this out alone.

HUMAN — You step off the curb. Not as your title. Not as your role. As your whole, messy, beautiful human self. And you walk.

Every healthcare worker I've talked to is somewhere in this framework. Some have been at START for years. Some are mid-crossing, somewhere between STOP and ELDER.

Where are you? Tell me in the comments. And if you're looking for your ELDER — that's literally why I'm here.""",
        "hashtags": "#TheCrosswalkMethod #CrosswalkWisdom #NurseBurnoutRecovery #CareerTransition #HealingJourney #BurnoutRecovery #PersonalGrowth #NurseBurnout #HealthcareBurnoutSupport #LeavingMedicine #MidlifeCareerChange #NurseTransition",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DAY 12 — Sunday, April 12
    # ─────────────────────────────────────────────────────────────────────────
    {
        "date": "2026-04-12",
        "title": "Day 12 — Things They Don't Tell You",
        "linkedin": """A former ICU nurse told me something last month that I can't stop thinking about:

"I don't miss the job. I miss who I was when I believed in it."

Read that again.

She wasn't nostalgic for the 12-hour shifts or the mandatory overtime or the emotional weight of watching people die. She was nostalgic for the version of herself that walked into nursing school with fire in her eyes and believed she'd found her life's purpose.

That belief — that certainty — is what she lost. And no amount of self-care or PTO or "wellness initiatives" could bring it back.

Because the problem was never the workload. The problem was that the system broke the covenant. It promised her she'd be a healer. Then it turned her into a data entry clerk with a stethoscope.

This is what burnout really is. Not tiredness. Betrayal.

And the only cure for betrayal isn't rest. It's reclamation.

Reclaiming your story. Your identity. Your right to define what healing means — on your terms.

If you know a healthcare professional who has lost that fire — share this. Not as a fix. Just as a "you're not alone." """,
        "instagram": """Things they don't tell you about leaving healthcare:

You'll miss the adrenaline. The way your body knew exactly what to do in a code. The way time slowed down when it mattered. Nothing in your new life will feel that intense — and you'll grieve the rush even as you're grateful to be free of it.

You'll forget how to introduce yourself. "I'm a..." will trail off mid-sentence. You'll fumble. You'll overexplain. And one day, you'll say something new — and it will feel like putting on a coat that actually fits.

You'll cry over scrubs in your closet. Not because you want to go back. Because they represent a version of you that tried so hard. Honor that version. She deserves your tears.

You'll feel guilty on their birthdays. The patients. The regulars. The ones who trusted you with their worst days. You'll wonder who's taking care of them now. And you'll learn to trust that someone is.

You'll be free. And freedom will terrify you before it heals you. Because freedom means you have to choose — and choosing is the hardest thing you'll ever do when you've spent your whole career following orders.

But you will heal. Not despite the crossing. Because of it.

Share this with a healthcare worker who needs it today.""",
        "facebook": """A former ICU nurse told me something last month that I can't stop thinking about:

"I don't miss the job. I miss who I was when I believed in it."

She wasn't nostalgic for the 12-hour shifts or the mandatory overtime. She was nostalgic for the version of herself that walked into nursing school with fire in her eyes and believed she'd found her life's purpose.

This is what burnout really is. Not tiredness. Betrayal.

And the only cure for betrayal isn't rest. It's reclamation.

Reclaiming your story. Your identity. Your right to define what healing means — on your terms.

If you know a healthcare professional who has lost that fire — share this. Not as a fix. Just as a "you're not alone." """,
        "hashtags": "#LeavingNursing #NurseBurnoutRecovery #HealthcareIdentityCrisis #BurnoutRecovery #HealingJourney #NurseBurnout #CareerTransition #LeavingMedicine #MentalHealthMatters #CrosswalkWisdom #NurseTransition #HealthcareBurnoutSupport #GriefAndHealing",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DAY 15 — Wednesday, April 15
    # ─────────────────────────────────────────────────────────────────────────
    {
        "date": "2026-04-15",
        "title": "Day 15 — 5 AI Prompts",
        "linkedin": """I've been collecting AI prompts that specifically help healthcare professionals navigate career transitions. Here are the 5 that get the most dramatic results:

1. The Skill Translator
"Analyze my role as a [title] and create a skills matrix showing how each clinical responsibility maps to a non-healthcare competency. Format it as a table with columns: Clinical Task | Transferable Skill | Industries That Value This."

2. The Salary Research Agent
"I'm a [title] earning [salary] in [location]. I'm considering transitioning to [target field]. Research realistic salary ranges for entry-to-mid-level roles in this field, and identify which of my healthcare skills command a premium."

3. The Network Mapper
"I'm a [title] looking to transition to [field]. Identify 10 specific types of professionals I should connect with on LinkedIn, what to say in my connection request, and what to ask in a 15-minute informational interview."

4. The 90-Day Transition Plan
"Create a detailed 90-day career transition plan for a [title] moving into [target area]. Include weekly milestones for skills development, networking, personal branding, and financial preparation."

5. The Imposter Syndrome Coach
"I'm a healthcare professional entering [new field] and I feel like a fraud. Help me create a 'evidence file' — a list of concrete examples from my clinical career that prove I have the skills for this new direction. Use specific scenarios I might not have thought of."

These aren't generic prompts. They're built from real conversations with healthcare professionals who've used AI to cross from one career to another.

Save this. Share it with a colleague who's been googling "can nurses become consultants" at 2am.""",
        "instagram": """Save this post. You're going to need it.

5 AI prompts specifically designed for healthcare professionals in career transition:

Prompt 1 — The Resume Translator:
"Rewrite my healthcare resume for a [target industry] role. Translate my clinical experience into business language. Focus on leadership, crisis management, communication, and problem-solving rather than clinical terminology."

Prompt 2 — The Cover Letter That Tells Your Story:
"Write a cover letter for a [role] position. I'm a former [healthcare title] with [X years] experience. I'm career-changing because I want to [goal]. Make it authentic, not corporate. Show how my clinical background is an asset, not a gap."

Prompt 3 — The Business Idea Generator:
"Based on my experience as a [healthcare role], suggest 10 business ideas I could start that leverage my clinical knowledge, patient relationships, and industry insight. Include both online and local options."

Prompt 4 — The Reflection Journal:
"Ask me 5 deep questions about my career transition. One about identity, one about fear, one about grief, one about hope, and one about practical next steps. Wait for my answer before asking the next question."

Prompt 5 — The Interview Coach:
"I have an interview for [role] at [company]. I'm coming from healthcare. Prepare me for the 5 most likely questions they'll ask about my career change, and help me frame my clinical experience as a competitive advantage."

Screenshot these. Save this post. Use them this week.

And DM me what happens. I mean it — I want to hear your results.""",
        "facebook": """Prompt of the Week challenge:

I'm sharing 5 AI prompts designed specifically for healthcare career changers (full list in the comments).

Your challenge: Pick ONE. Use it this week. Come back and share what happened.

No pressure to act on the results. This is just about seeing your skills through a different lens.

I'll feature the most interesting results in a post this weekend (with your permission, of course).

Who's in? Drop a hand-raise emoji below and I'll post the full prompt list.""",
        "hashtags": "#AIPrompts #CareerTransition #HealthcareBurnout #ProfessionalDevelopment #CrosswalkWisdom #AIforCareerChange #CareerChangeNurse #NurseTransition #ChatGPTPrompts #NurseBurnoutRecovery #TransferableSkills #MidlifeCareerChange #HealthcareBurnoutSupport #ArtificialIntelligence #NewChapter",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DAY 17 — Friday, April 17
    # ─────────────────────────────────────────────────────────────────────────
    {
        "date": "2026-04-17",
        "title": "Day 17 — Parking Lot Criers",
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
        "hashtags": "#HealthcareBurnout #NurseBurnout #MentalHealth #MoralInjury #CrosswalkWisdom #BurnedOutNurse #NurseLife #HealthcareWorkerBurnout #NurseBurnoutRecovery #LeavingNursing #HealingFromBurnout #HealthcareBurnoutSupport #NurseAdvocate #MentalHealthMatters #NurseTransition",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DAY 19 — Sunday, April 19
    # ─────────────────────────────────────────────────────────────────────────
    {
        "date": "2026-04-19",
        "title": "Day 19 — Self-Care Hot Take",
        "linkedin": """Unpopular opinion:

The healthcare "wellness" industry is gaslighting burned-out workers.

Here's what I mean:

When a nurse works a 16-hour shift, goes home to a family, sleeps 4 hours, and comes back to do it again — the system's response is "Have you tried our wellness app?"

When a doctor speaks up about unsustainable patient loads, the response is "Here's a resilience workshop."

When a pharmacist reports that they're making errors due to exhaustion, the response is "Try our free meditation room."

This is not wellness. This is blame-shifting disguised as care. It takes a systemic problem and repackages it as an individual failure of self-management.

And it's working — because healthcare workers are trained to internalize. Trained to believe that if they're struggling, the problem is their coping, not the conditions.

I left medicine partly because I realized I was being asked to treat my own symptoms while the disease — the system itself — went unaddressed.

True wellness for healthcare workers isn't apps and aromatherapy. It's:
- Staffing ratios that respect human limits
- Compensation that reflects the actual risk and sacrifice
- Mental health support without stigma
- And for some — the genuine, supported option to leave

If we're going to talk about wellness, let's start telling the truth about what's making people sick.""",
        "instagram": """I said what I said.

The wellness industry has convinced healthcare workers that burnout is a self-care problem.

Take a bath. Do yoga. Journal. Meditate. Practice gratitude.

And look — I love all of those things. They help. They matter.

But they are band-aids on a bullet wound if the root cause of your suffering is a system that takes more than it gives.

Real self-care — the kind that actually heals — sometimes looks like the scariest decision you've ever made. It looks like updating your resume at midnight. It looks like whispering "I think I'm done" to someone you trust. It looks like stepping off the curb and walking toward a life where you don't need a bubble bath to survive the week.

I'm not saying everyone should leave. I'm saying no one should stay because they think essential oils are a substitute for a life that doesn't drain them.

Agree or disagree? I want to hear both sides. Drop your take below.""",
        "facebook": """I said what I said.

The wellness industry has convinced healthcare workers that burnout is a self-care problem.

Take a bath. Do yoga. Journal. Meditate. Practice gratitude.

And look — I love all of those things. They help. They matter.

But they are band-aids on a bullet wound if the root cause of your suffering is a system that takes more than it gives.

Real self-care — the kind that actually heals — sometimes looks like the scariest decision you've ever made. It looks like updating your resume at midnight. It looks like whispering "I think I'm done" to someone you trust. It looks like stepping off the curb and walking toward a life where you don't need a bubble bath to survive the week.

Agree or disagree? I want to hear both sides.""",
        "hashtags": "#HealthcareWellness #NurseBurnout #SystemicChange #HealthcareReform #CrosswalkWisdom #SelfCare #HealthcareWorkerBurnout #BurnedOutNurse #NurseBurnoutRecovery #BurnoutRecovery #LeavingNursing #HealingJourney #MentalHealthMatters #NurseLife #HealthcareBurnoutSupport",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DAY 20 — Monday, April 20
    # ─────────────────────────────────────────────────────────────────────────
    {
        "date": "2026-04-20",
        "title": "Day 20 — Burnout Assessment Tease",
        "linkedin": """I've been working on something I think the healthcare community desperately needs.

After hundreds of conversations with burned-out healthcare professionals, I've identified a pattern. There are levels to burnout — and most people can't tell which level they're at until they're in crisis.

Level 1: The Grind. You're tired but functional. You complain about work but still feel a sense of purpose. Recovery happens on days off.

Level 2: The Disconnect. You start going through the motions. Patients become tasks. Shifts become countdowns. Recovery takes longer — a weekend isn't enough anymore.

Level 3: The Crossroads. You're actively questioning whether you can continue. You're searching job boards, researching career changes, having conversations you never thought you'd have. Recovery doesn't happen — you just oscillate between exhaustion and anxiety.

Level 4: The Crisis. Physical symptoms. Mental health impact. Relationship strain. The question isn't "should I leave?" — it's "can I survive if I stay?"

Most burnout resources treat all four levels the same: "Try self-care." That's like giving Tylenol for a broken femur.

So I'm building something different: The Burnout Crosswalk Assessment. A free tool that tells you exactly where you are, what it means, and what your specific next step should be.

It's launching this month. If you're a healthcare professional — or you work with them — I'd love your input. What would you want an assessment like this to tell you?

Comment below or DM me. Your experience is shaping this tool.""",
        "instagram": """There's tired. And then there's this:

1. You dread your shift more than 48 hours before it starts. Not the normal "ugh, Monday" feeling. The pit-in-your-stomach, counting-the-hours, can't-enjoy-your-days-off dread.

2. You've stopped caring about the work — and the guilt of not caring is worse than the burnout itself. You used to cry for patients. Now you feel nothing. And the numbness terrifies you.

3. Your body is keeping score. Migraines before shifts. Chest tightness in the parking lot. GI issues that no GI doc can explain. Your body is screaming what your mouth won't say.

4. You've fantasized about getting into a minor car accident on the way to work. Not to hurt yourself. Just to have a reason not to go in. If this is you — please hear me: this is not normal tiredness. This is a warning sign.

5. You can't remember the last time you felt proud of your work. Not because you're not doing good work — but because the system has beaten the pride out of you.

6. You've Googled "can nurses become [literally anything else]" at 3am. More than once. In incognito mode.

If 3 or more of these resonated — you're not just burned out. You're standing at a crosswalk.

Something is coming that I think you need: The Burnout Crosswalk Assessment. A free tool designed specifically for healthcare workers to understand where they are — and what to do next.

It's launching soon. Link in bio to be first in line.""",
        "facebook": """Building something for this community and I need your help.

I'm creating a free Burnout Crosswalk Assessment — a tool designed specifically for healthcare workers to understand where they are on the burnout spectrum and what to do about it.

But I want it to be shaped by YOUR experience, not just my framework.

So tell me: If you could take a burnout assessment that actually felt relevant to healthcare workers, what would you want it to ask? What would you want it to tell you?

No wrong answers. Share anything that comes to mind. Your responses will directly influence how this tool is built.""",
        "hashtags": "#BurnoutAssessment #HealthcareBurnout #NurseBurnout #MentalHealth #CrosswalkWisdom #BurnedOutNurse #NurseBurnoutRecovery #HealthcareWorkerBurnout #HealthcareBurnoutSupport #BurnoutRecovery #LeavingNursing #HealingFromBurnout #MentalHealthMatters #NurseLife #NurseTransition #CareerChangeNurse",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DAY 22 — Wednesday, April 22
    # ─────────────────────────────────────────────────────────────────────────
    {
        "date": "2026-04-22",
        "title": "Day 22 — The Middle of the Crosswalk",
        "linkedin": """There's a phase in every major life transition that doesn't have a good name.

It sits between "I left" and "I've arrived." It's after the resignation and before the reinvention. It's the space where your old identity has been shed and your new one hasn't formed yet.

William Bridges called it the "neutral zone." I call it the middle of the crosswalk.

And it's where most career changers get stuck — not because they lack direction, but because the emptiness of the middle feels like proof they've made a mistake.

It's not proof. It's process.

The middle feels empty because it IS empty. Deliberately, necessarily empty. You can't fill a cup that's already full. You can't build a new identity on top of an old one that's still taking up all the space.

The middle is where you learn to tolerate ambiguity. Where you practice the terrifying discipline of not-knowing. Where you discover that you can exist — and even thrive — without a title, a badge, or a ready answer to "so, what do you do?"

If you're in the middle right now — between careers, between identities, between who you were and who you're becoming — I want you to know: this isn't a detour. This is the crossing.

And the crossing is where the real transformation happens.

Stay in motion. The other side is closer than you think.""",
        "instagram": """There's a moment in every crossing that nobody prepares you for.

It's not the first step. That's scary, but it has momentum.

It's not the other side. That's unknown, but it has hope.

It's the middle.

The middle of the crosswalk — where you've left the curb but haven't reached the other side. Where you can't go back and you can't see forward. Where you're just... in motion. In the open. Exposed.

That's the grief no one talks about.

It's not the grief of what you lost. It's the grief of who you are between identities. The grief of being no one for a while. Not a doctor. Not yet whatever you're becoming. Just a person, walking.

I spent eight months in the middle. Eight months of waking up without a purpose. Eight months of "I don't know" being my most honest answer to every question.

And I want you to know something about the middle: it's sacred.

Because the middle is where you stop performing and start discovering. It's where the crossing guard in you meets the healer in you meets the scared kid in you — and they all agree on one thing:

Keep walking.

The other side is one more step away. And it's been waiting for you longer than you know.""",
        "facebook": """Can I be honest about something?

The hardest part of my transition from medicine wasn't the leaving. It wasn't the financial uncertainty. It wasn't even the identity crisis.

It was the middle.

That strange, disorienting space between "I was a doctor" and "I am..." what, exactly?

For eight months, I didn't have an answer. And in a world that defines you by what you do — having no answer felt like having no self.

I'd go to the grocery store and dread running into someone who'd ask what I was up to. I'd scroll LinkedIn and feel physically sick watching my former colleagues post about their promotions. I'd wake up at 4am — the time I used to start rounds — and just lie there in the dark, wondering if I'd ruined everything.

But here's what I know now that I didn't know then:

The middle is not a mistake. The middle is the crossing.

And the only way to get to the other side is to keep walking through it. Even when it's dark. Even when it's disorienting. Even when you can't see where you're going.

The other side is there. I'm standing on it. And I promise you — it's worth every step through the middle.

If you're in the middle right now, drop a "walking" emoji below. I want to know you're here. And I want you to know you're not walking alone.""",
        "hashtags": "#CareerTransition #LifeTransition #HealthcareBurnout #ProfessionalGrowth #CrosswalkWisdom #HealingJourney #NurseBurnoutRecovery #LeavingMedicine #BurnoutRecovery #HealthcareIdentityCrisis #MentalHealthMatters #NurseBurnout #LeavingNursing #GriefAndHealing #TheCrosswalkMethod #NurseTransition",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DAY 24 — Friday, April 24
    # ─────────────────────────────────────────────────────────────────────────
    {
        "date": "2026-04-24",
        "title": "Day 24 — Letter to a Nurse",
        "linkedin": """To every healthcare professional in my network who is silently struggling:

I know you're there.

I know because my DMs are full of messages that start with "I haven't told anyone this, but..." and end with some version of "I don't know how much longer I can do this."

I know because every time I post about healthcare burnout, the engagement tells a story the industry doesn't want to acknowledge: this isn't a few disgruntled workers. This is a crisis of meaning affecting millions of talented, dedicated professionals.

I know because I was you. Sitting in my office, closing the door, putting my head in my hands, and wondering how a career I chose with such purpose could feel so purposeless.

So here's what I want to say to you, directly:

You are not failing. The system is failing you.

Your exhaustion is not a character flaw. It's a rational response to irrational demands.

Your desire to leave is not betrayal. It's self-preservation.

And your next chapter — whatever it looks like — will be built on a foundation of skills, empathy, and resilience that very few professionals on earth possess.

If you need someone to talk to — someone who's been where you are and can tell you honestly what the other side looks like — my DMs are open. Or book a free discovery call at crosswalkwisdom.com/start.

You don't have to cross alone.""",
        "instagram": """A letter to the nurse who's thinking about quitting:

I see you.

I see you holding it together during a 14-hour shift while your own heart is breaking. I see you charting at midnight because the system doesn't give you time during the day. I see you apologizing to patients for wait times that aren't your fault and absorbing anger that isn't yours to carry.

I see you googling "what else can nurses do" in incognito mode, as if researching your own freedom is something to hide.

I see you comparing yourself to the nurse who seems to handle it all — and I want you to know: she's probably googling the same thing.

You became a nurse because you care. And the system took that caring and wrung it out like a dishrag.

You're not ungrateful. You're not weak. You're not "not cut out for this." You're a human being who has given more than most people give in a lifetime, and you're asking the most courageous question a person can ask:

"Is there more?"

Yes. There is. And it's waiting for you on the other side of a crosswalk you haven't crossed yet.

When you're ready — not when the world says you should be, but when YOU'RE ready — I'll be at the crosswalk.

With love and respect,
Sahawat
Crosswalk Wisdom""",
        "facebook": """Friday love letter to this group:

I started Crosswalk Wisdom because I felt alone during the hardest transition of my life. No one in my circle understood why a doctor would leave medicine. No one could validate what I was feeling without trying to fix it or talk me out of it.

This group is becoming what I wished I'd had.

So today, I just want to say: I see every post. I read every comment. And every time one of you is brave enough to say "I'm struggling" or "I'm thinking about leaving" or even just "I'm here" — you make it safer for someone else to do the same.

That's the crosswalk. We don't cross alone.

If you joined this group recently and haven't introduced yourself yet — today's the day. Tell us:
1. Your role in healthcare (or former role)
2. Where you are in the crossing (START, STOP, ELDER, or HUMAN)
3. One thing you hope to get from being here

Welcome home.""",
        "hashtags": "#HealthcareBurnout #NurseBurnout #CareerTransition #Leadership #CrosswalkWisdom #BurnedOutNurse #NurseLife #HealthcareWorkerBurnout #NurseBurnoutRecovery #LeavingNursing #NurseTransition #CareerChangeNurse #HealingFromBurnout #NurseAdvocate #MentalHealthMatters #HealthcareBurnoutSupport",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DAY 26 — Sunday, April 26
    # ─────────────────────────────────────────────────────────────────────────
    {
        "date": "2026-04-26",
        "title": "Day 26 — Hold It Gently",
        "linkedin": """Sunday thought:

There's no rule that says career transitions have to be violent.

We've been conditioned by dramatic narratives — the "I quit" moment, the table flip, the mic drop. Movies love the decisive break. Social media loves the "I finally walked out" story.

But most real transitions look nothing like that.

They look like a nurse who picks up one fewer overtime shift. Then another. Then starts a side project on her days off. Then tells one trusted friend. Then takes a course. Then has a conversation. Then makes a plan. Then — quietly, with no audience and no applause — crosses.

Not with a bang. With a breath.

I think we need to normalize the slow crossing. The deliberate, thoughtful, undramatic transition that happens over months or years — not in a single cinematic moment.

Because the truth is: the best crossings I've witnessed weren't the fastest ones. They were the most intentional ones.

If you're in the slow crossing right now — please don't mistake your patience for cowardice. You're not stalling. You're preparing.

And when you're ready, you'll walk with a steadiness that the impulsive crossers will envy.

Take your time. The crosswalk isn't going anywhere.""",
        "instagram": """You can hold it gently.

You can hold the badge, the title, the years of training — and still set them down.

Holding something gently is not the same as gripping it tightly. And setting something down is not the same as throwing it away.

I think that's the part that trips us up. We think leaving has to be dramatic. A blowup. A burning of bridges. A decisive, clean break.

But most crossings aren't like that.

Most crossings are quiet. A slow exhale. A gentle loosening of the grip. A moment where you realize your hands have been clenched for so long that opening them feels foreign.

You don't have to drop everything all at once. You don't have to know what's next before you let go of what's now.

You just have to loosen your grip. One finger at a time.

And when you're ready to let go completely — the crosswalk will be there. Patient. Unhurried. Lit by a light that's been green for longer than you realize.""",
        "facebook": """You can hold it gently.

You can hold the badge, the title, the years of training — and still set them down.

Holding something gently is not the same as gripping it tightly. And setting something down is not the same as throwing it away.

Most crossings are quiet. A slow exhale. A gentle loosening of the grip. A moment where you realize your hands have been clenched for so long that opening them feels foreign.

You don't have to drop everything all at once. You don't have to know what's next before you let go of what's now.

You just have to loosen your grip. One finger at a time.

And when you're ready to let go completely — the crosswalk will be there. Patient. Unhurried. Lit by a light that's been green for longer than you realize.""",
        "hashtags": "#CareerTransition #SlowLiving #IntentionalLiving #HealthcareBurnout #CrosswalkWisdom #HealingJourney #NurseBurnoutRecovery #LeavingNursing #LeavingMedicine #BurnoutRecovery #HealthcareIdentityCrisis #MentalHealthMatters #NurseBurnout #SelfCare #NurseTransition #HealingFromBurnout",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DAY 27 — Monday, April 27
    # ─────────────────────────────────────────────────────────────────────────
    {
        "date": "2026-04-27",
        "title": "Day 27 — AI Journaling",
        "linkedin": """I want to share a use of AI that I haven't seen anyone talk about:

AI-assisted career transition journaling.

Here's the premise: Most healthcare professionals I work with know something is wrong. They feel the burnout, the dissonance, the pull toward something different. But they can't articulate it.

Why? Because they've never had a safe space to explore it without someone trying to fix it, talk them out of it, or project their own fears onto the conversation.

AI provides that space.

When you ask an AI to be your "career transition journal" — to ask you one reflective question at a time and just listen — something remarkable happens. You start saying things you didn't know you were thinking.

I've recommended this exercise to over 50 healthcare professionals. The results are consistently powerful:

"I realized I don't actually hate nursing. I hate who I've become inside a system that doesn't let me nurse."

"I discovered my fear isn't about money. It's about disappointing my mother."

"I finally admitted that I've been staying out of guilt, not love."

These aren't insights that come from a career quiz or a personality test. They come from being asked honest questions in a judgment-free space.

If you're in healthcare and feeling stuck, try this:

Prompt: "Act as my career reflection coach. I'm a healthcare professional in a period of questioning. Ask me one thoughtful, open-ended question at a time. Wait for my response before continuing. Don't offer advice unless I ask. Just help me think clearly."

15 minutes. That's all it takes.""",
        "instagram": """This is the most underrated use of AI I've ever discovered.

Not for resumes. Not for business plans. For journaling.

Here's why: Most of us can't be honest with ourselves in our own heads. We filter. We edit. We perform wellness even in our private thoughts.

But when you sit down with an AI and tell it to ask you questions — one at a time, slowly — something shifts.

The AI doesn't judge. It doesn't gasp. It doesn't try to fix you or talk you out of your feelings. It just... asks the next question.

And in that space — that non-judgmental, patient, curious space — you start telling the truth.

I've had healthcare workers tell me this exercise made them cry. Not sad crying. Relief crying. The kind that happens when you finally say out loud what you've been carrying in silence.

Try this tonight:

Open ChatGPT. Type: "Be my career transition journal. I'm a healthcare worker questioning my career. Ask me one deep, reflective question at a time. Wait for my answer before asking the next. Don't try to solve anything. Just help me explore."

Then answer honestly. For 15 minutes. See what comes up.

I'd love to hear what happens. DM me if you try it.""",
        "facebook": """This week's experiment (and I think this one might be the most powerful yet):

AI Journaling.

Here's what I want you to try:

Open any AI tool (ChatGPT, Claude, Gemini — any of them work). Type this:

"Be my career transition journal. I'm a healthcare worker thinking about my future. Ask me one question at a time. Make the questions deep but gentle. Wait for my answer before asking the next one."

Then just... answer. For 15 minutes. No filtering. No performing.

When you're done, come back here and share one insight that surprised you. Just one line. That's all.

You don't have to share the whole conversation. Just the one moment where you thought "oh... I didn't know I felt that."

Who's in?""",
        "hashtags": "#AICoaching #CareerReflection #HealthcareBurnout #ProfessionalDevelopment #CrosswalkWisdom #AIJournaling #CareerTransition #NurseTransition #ChatGPT #SelfReflection #NurseBurnoutRecovery #HealthcareBurnoutSupport #MentalHealthMatters #BurnoutRecovery #HealingJourney #CareerChangeNurse",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DAY 29 — Wednesday, April 29
    # ─────────────────────────────────────────────────────────────────────────
    {
        "date": "2026-04-29",
        "title": "Day 29 — Month-End Reflection",
        "linkedin": """One month into Crosswalk Wisdom's social presence. Here's what I've learned:

1. The need is bigger than I estimated.

I knew healthcare burnout was widespread. I didn't know how hungry people were for someone to simply say: "You're allowed to leave." The engagement on that message alone told me everything I needed to know about the state of the industry.

2. Psychology resonates more than tactics.

The posts about the three fears, identity loss, and grief outperformed every practical post by 3-5x. People don't need more LinkedIn tips or resume hacks. They need someone to name the emotional experience they're living through.

3. AI is a bridge, not a destination.

The most powerful AI content wasn't "here's how to use ChatGPT." It was "here's how to use AI to have a conversation with yourself that you've been avoiding." The tool matters less than the intention behind it.

4. Community is everything.

The comments on my posts have become more valuable than the posts themselves. Healthcare professionals finding each other, saying "me too," sharing resources — that's not engagement metrics. That's healing.

Thank you for following along this month. If you're in healthcare and you resonated with any of this — stay connected. May is going to go deeper.

And if you're standing at the curb: the light is green. I see you. And the other side is real.""",
        "instagram": """I want to end this month the way I started it — with honesty.

When I launched Crosswalk Wisdom, I didn't know if anyone would care. I didn't know if my story — doctor turned crossing guard turned whatever-I-am-now — would resonate with anyone beyond my own reflection in the mirror.

This month proved me wrong.

Your DMs broke me open. Your comments reminded me why I crossed. Your willingness to be vulnerable in a public space — to say "I'm struggling" or "I'm scared" or "I'm ready" — that's not small. That's revolutionary.

Here's what you taught me in April:

1. The healthcare burnout crisis isn't theoretical. It's personal. It has names and faces and 3am Google searches and parking lot tears.

2. People don't need more information. They need more permission. Permission to feel what they feel. Permission to want what they want. Permission to cross.

3. Community is the crossing guard. No one crosses alone. The people in this community — holding space, sharing stories, saying "me too" — you are the crossing guards for each other.

4. The crosswalk is bigger than I imagined. Nurses. Doctors. Pharmacists. Therapists. Paramedics. Techs. The whole spectrum. All standing at the same curb.

Thank you for trusting me with your stories. May is going to be extraordinary.

Stay close. The best is just beginning.""",
        "facebook": """End of Month 1 celebration post:

I want to hear from you. One sentence.

What shifted for you this month?

It doesn't have to be dramatic. Maybe you took the Fear Audit. Maybe you had a conversation with someone you trust. Maybe you just realized you're not alone. Maybe you joined this group and that, in itself, was a step.

One sentence. What shifted?

I'll compile these into a post (anonymized, of course) to kick off May. Your words will be the first thing a new member sees when they find this community.

You're not just sharing for yourself. You're lighting the path for someone behind you.""",
        "hashtags": "#HealthcareBurnout #ContentCreation #MonthlyReflection #CrosswalkWisdom #CareerTransition #TheCrosswalkMethod #NurseBurnoutRecovery #HealthcareBurnoutSupport #Community #HealingJourney #BurnoutRecovery #NurseBurnout #Gratitude #NurseTransition #NurseLife",
    },

]


# ─── SCHEDULER ────────────────────────────────────────────────────────────────

def schedule_post(post: dict) -> None:
    date_str = post["date"]
    title    = post["title"]

    # Build the Instagram content: caption + newline + hashtags
    instagram_content = post["instagram"] + "\n\n" + post["hashtags"]

    payload = {
        "content": post["linkedin"],          # main content = LinkedIn text
        "scheduledFor": f"{date_str}T{POST_TIME}",
        "timezone": TIMEZONE,
        "platforms": [
            {
                "platform": "linkedin",
                "accountId": LINKEDIN_ACCOUNT_ID,
                "customContent": post["linkedin"],
            },
            {
                "platform": "facebook",
                "accountId": FACEBOOK_ACCOUNT_ID,
                "customContent": post["facebook"],
            },
        ],
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    try:
        resp = requests.post(f"{BASE_URL}/posts", headers=headers, json=payload)
        if resp.status_code in (200, 201):
            print(f"[OK {resp.status_code}] {date_str} — {title}")
        else:
            print(f"[FAIL {resp.status_code}] {date_str} — {title} | {resp.text[:300]}")
    except requests.exceptions.RequestException as e:
        print(f"[FAIL NETWORK] {date_str} — {title} | {e}")


def main():
    print(f"Scheduling {len(POSTS)} posts to Zernio...\n")
    for post in POSTS:
        schedule_post(post)
    print("\nDone.")


if __name__ == "__main__":
    main()
