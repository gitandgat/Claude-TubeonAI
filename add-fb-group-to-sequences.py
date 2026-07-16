"""
Add Facebook community group invite to first email of 3 sequences:
- 436027: Fear Audit Email 1
- 436357: Quiz Email 1
- 444015: IMG Email 1
"""
import sys
sys.path.insert(0, "/Users/toto/.claude/skills/crosswalk-encharge-email")

from encharge_email import update_email, p, link, button

FB_GROUP = "https://www.facebook.com/groups/2073825613397240"
FB_INVITE = (
    p("One more thing before I go: I just opened <strong>The Crosswalk Community</strong> — "
      "a free Facebook group for IMGs in Canada who are done waiting and ready to cross over. "
      "If you want a space to think out loud with people who actually get it, come join us.")
    + button(FB_GROUP, "Join The Crosswalk Community →")
)

# ── Fear Audit Email 1 (436027) ──────────────────────────────────────────────
fear_audit_1 = (
    p('Hey {{ person.firstName | default: "there" }},')
    + p("You actually did it. Most people who find the Fear Audit bookmark it, intend to come back, and never do.")
    + p("You sat down and looked honestly at what's holding you back. That's not a small thing.")
    + p("So first — I mean this — thank you for trusting the process enough to see it through.")
    + p("Here's what I've noticed about the moment right after the audit: there's often a strange mix of relief and dread. Relief because you finally have language for what's been living in your chest. Dread because now you know, and knowing creates a kind of obligation.")
    + p("That gap — between knowing what's holding you back and actually moving — is exactly where people get stuck the longest. Not in the confusion stage. In the clarity stage.")
    + p("Because information doesn't change behavior. Insight doesn't either, not on its own. What changes behavior is having a structure to walk through when the fear is loudest and the reasons to stay are most convincing.")
    + p("That's what I built <strong>The Courage to Choose</strong> for — a guide written specifically for Fear Audit graduates, for people who've done the honest work of naming their fears and are ready for a practical framework to move through them. Not around them. Through them.")
    + p("Over the next few days, I'm going to share a few things that shaped the guide and shaped my own transition.")
    + FB_INVITE
    + p("For now, just know: what you discovered in the audit is real, and it's workable. You're in the right place.")
)

print("Updating Fear Audit Email 1...")
r1 = update_email(436027, "You finished the Fear Audit. That already took something.", fear_audit_1)
print(r1)

# ── Quiz Email 1 (436357) ────────────────────────────────────────────────────
quiz_1 = (
    p('Hey {{ person.firstName | default: "there" }},')
    + p("Most people who feel burned out in healthcare do one of two things.")
    + p("They push through — adding more shifts, more coffee, more convincing themselves it's just a hard season. Or they fantasize about leaving without ever taking a single honest look at what's actually stopping them.")
    + p("You did something different. You sat down, answered twelve questions, and looked clearly at where you are on this road. That matters more than it sounds.")
    + p("I built the Burnout Crosswalk Assessment because I've been exactly where you are. Trained physician. Over a decade of investment in a career I was proud of — and quietly suffocating in.")
    + p("The day I finally looked honestly at what was keeping me stuck wasn't the day I left medicine. But it was the day the leaving became possible.")
    + p("You've just had that day.")
    + p("Here's what I've learned: naming the stage you're in is only the first step. What most people don't have is a framework for what comes next — a way to move through the fear rather than around it.")
    + p("Over the next few days, I'm going to share the ideas that shaped my own transition. Not to sell you a story. To give you something useful.")
    + FB_INVITE
    + p("For now: you're in the right place.")
)

print("Updating Quiz Email 1...")
r2 = update_email(436357, "You crossed a line most people don't.", quiz_1)
print(r2)

# ── IMG Email 1 (444015) ─────────────────────────────────────────────────────
img_1 = (
    p('Hey {{ person.firstName | default: "there" }},')
    + p("You ran the numbers. Most people never do.")
    + p("They feel the weight of the investment — the years, the debt, the sacrifice — but they never actually sit down and calculate what staying is costing them. You did.")
    + p("That takes a different kind of honesty than most career advice asks for.")
    + p("Here's what I want you to hold onto from today: the sunk cost isn't the problem. The belief that the sunk cost defines what's possible next — that's the problem.")
    + p("You didn't waste a decade becoming a physician. You built a clinical brain, a systems mindset, and a level of resilience most people will never develop. The credential doesn't have to define what comes next.")
    + p("Over the next week, I'm going to walk you through the four costs that nobody calculated when you started this path — and what the pivot actually looks like for IMGs who've crossed over.")
    + FB_INVITE
    + p("More tomorrow.")
)

print("Updating IMG Email 1...")
r3 = update_email(444015, "You ran the numbers. Most people never do.", img_1)
print(r3)
