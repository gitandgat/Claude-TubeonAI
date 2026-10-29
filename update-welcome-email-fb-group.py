"""
Rebuild CW Welcome 1 (ID 437519) with proper richtext format
and add the Facebook community group invite.
"""
import sys
sys.path.insert(0, "/Users/toto/.claude/skills/crosswalk-encharge-email")

from encharge_email import update_email, p, link, button

EMAIL_ID = 437519
SUBJECT = "You made it. (And that already took something.)"
FB_GROUP = "https://www.facebook.com/groups/2073825613397240"

body = (
    p("Hey {{ person.firstName | default: 'there' }},")
    + p("You just took the first step — and that already took something.")
    + p("Most people in your position keep waiting. For the right moment. For more certainty. For someone to tell them it's okay to want more than this.")
    + p("You didn't wait. You're here.")
    + p("Over the next few days, I'm going to share the ideas that have actually helped me — and the IMGs I've worked with — move from stuck to clear.")
    + p("Not motivational content. Not career tips. The real stuff: the identity traps, the fears that don't have names yet, and what actually helps you cross over.")
    + p("But first — one invitation:")
    + p(
        "<strong>Join The Crosswalk Community on Facebook</strong> — a free space for IMGs in Canada who are done performing gratitude and ready to ask the real question: what do I actually want?"
    )
    + button(FB_GROUP, "Join The Crosswalk Community →")
    + p("Introduce yourself when you get in. Tell us where you're from, where you are now, and the one thing you wish someone had told you earlier.")
    + p("More from me in a couple of days.")
    + p("— Sahawat")
)

result = update_email(EMAIL_ID, SUBJECT, body)
print(result)
