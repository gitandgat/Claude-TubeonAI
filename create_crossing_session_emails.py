"""
Create the 3 Crossing Session launch emails in Encharge.

Reuses the proven branded Unlayer builder from create_coaching_emails.py
(logo header, footer, Georgia serif, brand colors).

After running:
  1. Build ONE flow in Encharge UI: trigger "Tag added: crossing-launch"
     -> send Email 1 -> wait 2 days -> Email 2 -> wait 2 days -> Email 3
  2. Activate the flow
  3. Run tag-crossing-launch.py to enroll the Burnout Subscribers

IMPORTANT: the session link assumes the Gumroad product slug is
"crossing-session" -> https://sahawat.gumroad.com/l/crossing-session
Use exactly that slug when creating the product.

Run: python3 create_crossing_session_emails.py
"""

import requests

from create_coaching_emails import (
    BASE,
    HEADERS,
    ACCOUNT_ID,
    COMMUNICATION_CAT_ID,
    FROM_EMAIL,
    FROM_NAME,
    E,
    P,
    build_state,
    divider_block,
    sign_off,
    text_block,
)

FEAR_AUDIT_URL = "https://fear-audit.vercel.app"
SESSION_URL = "https://sahawat.gumroad.com/l/crossing-session"

GREETING = 'Hi {{ person.firstName | default: "there" }},'

LINK = '<a style="color: #2C5F4A;" href="{url}" target="_blank">{text}</a>'
quiz_link = LINK.format(url=FEAR_AUDIT_URL, text="Take the Fear Audit (free, 3 minutes)")
session_link = LINK.format(url=SESSION_URL, text="Claim a founding spot — $97")


EMAILS = [
    {
        "name": "Crossing Session Launch 1 — Story",
        "subject": "The day I stopped waiting for the traffic to clear",
        "contents": [
            text_block(
                f"{P}{GREETING}{E}"
                f"{P}I want to tell you about the worst part of my own crossing.{E}"
                f"{P}It wasn't the leaving. It wasn't the money, and it wasn't telling my family. "
                f"It was the two years <em>before</em> — the years I spent standing at the curb, "
                f"watching the traffic, waiting for a gap that never came.{E}"
                f"{P}I had a system, even. I'd tell myself: when the savings hit this number. "
                f"When this credential comes through. When things calm down at work. "
                f"The number moved. The credential came and I set a new one. Things never "
                f"calmed down, because they don't.{E}"
            ),
            text_block(
                f"{P}What finally moved me wasn't courage. It was arithmetic. I sat down one "
                f"evening and wrote out what staying was costing me — not in money, in "
                f"mornings. The dread before shifts. The version of myself I was becoming. "
                f"When I saw it on paper, waiting stopped looking safe. It was just slower.{E}"
                f"{P}I built a 3-minute audit around that exercise. It scores the three fears "
                f"that keep people at the curb — money, judgment, identity — and tells you "
                f"which one is actually running your decisions. Most people guess wrong "
                f"about their own.{E}"
                f"{P}{quiz_link}{E}"
                f"{P}Later this week I'll tell you about something I'm opening up for the "
                f"first time — for ten people only. But start with the audit. It's the map.{E}"
            ),
            divider_block(),
            sign_off(),
        ],
    },
    {
        "name": "Crossing Session Launch 2 — Offer",
        "subject": "I'm opening 10 one-on-one sessions (first time)",
        "contents": [
            text_block(
                f"{P}{GREETING}{E}"
                f"{P}For two years I've written about crossings — the identity cage, the cost "
                f"of staying, the fears that keep smart people at the curb. And the most "
                f'common reply I get is some version of: "This is exactly me. Now what?"{E}'
                f"{P}Fair question. Posts can name your situation. They can't sit with "
                f"<em>your</em> numbers, <em>your</em> license, <em>your</em> mortgage, "
                f"<em>your</em> particular fear. So I'm opening something I haven't offered "
                f"before:{E}"
                f"{P}<strong>The Crossing Session.</strong> One hour, one-on-one, on your "
                f"actual situation.{E}"
            ),
            text_block(
                f"{P}Here's the shape of it:{E}"
                f"{P}1. Before we talk, you take the 3-minute Fear Audit, so we start from a "
                f"map of which fear is really driving — money, judgment, or identity.<br>"
                f"2. On the call, we separate the real risks from the inherited ones, put a "
                f"price on staying, and work out your first concrete step.<br>"
                f"3. Within 48 hours you get a one-page Crossing Plan in writing: your "
                f"situation, your constraint, your next three moves.{E}"
                f"{P}A few honest caveats. I'm not going to tell you to quit your job — some "
                f"people leave this call with a plan to stay, on purpose, with the fear named "
                f"and priced. That's a real outcome too. And if you finish the hour with no "
                f"more clarity than you came with, tell me and I'll refund every dollar.{E}"
                f"{P}I'm taking <strong>ten people</strong> at the founding rate of "
                f"<strong>$97</strong>. After ten, it goes to $147 and I can't promise when "
                f"the next batch opens.{E}"
                f"{P}{session_link}{E}"
            ),
            divider_block(),
            sign_off(),
        ],
    },
    {
        "name": "Crossing Session Launch 3 — Last Call",
        "subject": "What's your curb tax?",
        "contents": [
            text_block(
                f"{P}{GREETING}{E}"
                f"{P}Quick one, and then I'll stop talking about this.{E}"
                f"{P}There's a number I ask people to calculate on every Crossing Session. "
                f"I call it the curb tax: what one more year of waiting actually costs you.{E}"
                f"{P}Not just salary you could be earning elsewhere. The shifts you dread. "
                f"The energy your family gets — the version of you they get. The compounding "
                f'of one more year of "I\'ll decide next year," which, as you may have '
                f"noticed, has a way of renewing itself automatically.{E}"
                f"{P}Nobody's curb tax has ever come out to less than $97.{E}"
            ),
            text_block(
                f"{P}That's the whole pitch. One hour on your actual situation, a written "
                f"plan within 48 hours, full refund if you leave without clarity. The "
                f"founding spots are nearly gone, and the price goes to $147 when they are.{E}"
                f"{P}{session_link}{E}"
                f"{P}And if it's a no — genuinely fine. The "
                + LINK.format(url=FEAR_AUDIT_URL, text="Fear Audit stays free")
                + ", the posts keep coming, and I'll keep holding the sign at the crosswalk "
                f"either way.{E}"
            ),
            divider_block(),
            sign_off(),
        ],
    },
]


def create_email(email_def: dict) -> int | None:
    payload = {
        "name": email_def["name"],
        "subject": email_def["subject"],
        "fromEmail": FROM_EMAIL,
        "fromName": FROM_NAME,
        "replyTo": FROM_EMAIL,
        "accountId": ACCOUNT_ID,
        "communicationCategoryId": COMMUNICATION_CAT_ID,
        "editorType": "unlayer",
        "state": build_state(email_def["contents"]),
    }
    r = requests.post(f"{BASE}/emails", headers=HEADERS, json=payload, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        email_id = data.get("id") or data.get("email", {}).get("id")
        print(f"  created: {email_def['name']} -> ID {email_id}")
        return email_id
    print(f"  FAILED: {email_def['name']} -> {r.status_code}: {r.text[:200]}")
    return None


if __name__ == "__main__":
    print("Creating Crossing Session launch emails...\n")
    ids = [create_email(e) for e in EMAILS]
    print(f"\nEmail IDs: {ids}")
    print("\nNext steps (Encharge UI):")
    print("  1. Flows -> new flow, trigger: Tag added 'crossing-launch'")
    print(f"     Send {ids[0]} -> wait 2 days -> send {ids[1]} -> wait 2 days -> send {ids[2]}")
    print("  2. Activate the flow")
    print("  3. Then run: python3 tag-crossing-launch.py")
