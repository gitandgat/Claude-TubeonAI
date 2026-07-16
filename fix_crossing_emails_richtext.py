"""
Fix the 3 Crossing Session launch emails (461554/461555/461556).

They were created with an Unlayer dict state, which doesn't persist via API
(shows the editor placeholder). Per project memory: API emails must use
editorType "richtext" with a plain HTML string state.

Run: python3 fix_crossing_emails_richtext.py
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["ENCHARGE_API_KEY"]
BASE = "https://api.encharge.io/v1"
HEADERS = {"X-Encharge-Token": API_KEY, "Content-Type": "application/json"}

LOGO_URL = "https://d231yrez0cpae9.cloudfront.net/1750037512272-Crosswalk%20wisdom%20logo%20white%20BG.png"
FEAR_AUDIT_URL = "https://fear-audit.vercel.app"
SESSION_URL = "https://sahawat.gumroad.com/l/crossing-session"

GREETING = 'Hi {{ person.firstName | default: "there" }},'
P = '<p style="font-family: Georgia, serif; font-size: 16px; line-height: 180%; color: #1A1917;">'
E = "</p>"


def link(url: str, text: str) -> str:
    return f'<a href="{url}" target="_blank" style="color: #2C5F4A;">{text}</a>'


HEADER = (
    f'<p style="text-align: center; padding: 16px 0;">'
    f'<img src="{LOGO_URL}" alt="Crosswalk Wisdom" width="150" style="max-width: 150px;"></p>'
)

FOOTER = (
    '<hr style="border: none; border-top: 1px solid #ecf0f1; margin: 28px 0 20px;">'
    f"{P}&mdash; Sahawat{E}"
    '<p style="font-family: Georgia, serif; font-size: 14px; color: #888888;">Crosswalk Wisdom</p>'
    '<p style="text-align: center; font-size: 14px; line-height: 160%; color: #95a5a6; font-family: Georgia, serif;">'
    + link("https://www.facebook.com/profile.php?id=61580308547545", "Facebook") + " &middot; "
    + link("https://www.instagram.com/crosswalkwisdom/", "Instagram") + " &middot; "
    + link("https://www.linkedin.com/in/sahawat-nilwatcharamanee-a359b1143/", "LinkedIn")
    + "<br><br>Crosswalk Wisdom<br>{{account.mailingAddress}}<br>"
    "{{person.unsubscribeLink}} &nbsp; {{person.managePreferencesLink}}</p>"
)


EMAIL_1_BODY = (
    f"{P}{GREETING}{E}"
    f"{P}I want to tell you about the worst part of my own crossing.{E}"
    f"{P}It wasn't the leaving. It wasn't the money, and it wasn't telling my family. "
    f"It was the two years <em>before</em> &mdash; the years I spent standing at the curb, "
    f"watching the traffic, waiting for a gap that never came.{E}"
    f"{P}I had a system, even. I'd tell myself: when the savings hit this number. "
    f"When this credential comes through. When things calm down at work. "
    f"The number moved. The credential came and I set a new one. Things never "
    f"calmed down, because they don't.{E}"
    f"{P}What finally moved me wasn't courage. It was arithmetic. I sat down one "
    f"evening and wrote out what staying was costing me &mdash; not in money, in "
    f"mornings. The dread before shifts. The version of myself I was becoming. "
    f"When I saw it on paper, waiting stopped looking safe. It was just slower.{E}"
    f"{P}I built a 3-minute audit around that exercise. It scores the three fears "
    f"that keep people at the curb &mdash; money, judgment, identity &mdash; and tells you "
    f"which one is actually running your decisions. Most people guess wrong about their own.{E}"
    f"{P}{link(FEAR_AUDIT_URL, 'Take the Fear Audit (free, 3 minutes)')}{E}"
    f"{P}Later this week I'll tell you about something I'm opening up for the first "
    f"time &mdash; for ten people only. But start with the audit. It's the map.{E}"
)

EMAIL_2_BODY = (
    f"{P}{GREETING}{E}"
    f"{P}For two years I've written about crossings &mdash; the identity cage, the cost "
    f"of staying, the fears that keep smart people at the curb. And the most "
    f'common reply I get is some version of: "This is exactly me. Now what?"{E}'
    f"{P}Fair question. Posts can name your situation. They can't sit with "
    f"<em>your</em> numbers, <em>your</em> license, <em>your</em> mortgage, "
    f"<em>your</em> particular fear. So I'm opening something I haven't offered before:{E}"
    f"{P}<strong>The Crossing Session.</strong> One hour, one-on-one, on your actual situation.{E}"
    f"{P}Here's the shape of it:{E}"
    f"{P}1. Before we talk, you take the 3-minute Fear Audit, so we start from a "
    f"map of which fear is really driving &mdash; money, judgment, or identity.<br>"
    f"2. On the call, we separate the real risks from the inherited ones, put a "
    f"price on staying, and work out your first concrete step.<br>"
    f"3. Within 48 hours you get a one-page Crossing Plan in writing: your "
    f"situation, your constraint, your next three moves.{E}"
    f"{P}A few honest caveats. I'm not going to tell you to quit your job &mdash; some "
    f"people leave this call with a plan to stay, on purpose, with the fear named "
    f"and priced. That's a real outcome too. And if you finish the hour with no "
    f"more clarity than you came with, tell me and I'll refund every dollar.{E}"
    f"{P}I'm taking <strong>ten people</strong> at the founding rate of "
    f"<strong>$97</strong>. After ten, it goes to $147 and I can't promise when "
    f"the next batch opens.{E}"
    f"{P}{link(SESSION_URL, 'Claim a founding spot — $97')}{E}"
)

EMAIL_3_BODY = (
    f"{P}{GREETING}{E}"
    f"{P}Quick one, and then I'll stop talking about this.{E}"
    f"{P}There's a number I ask people to calculate on every Crossing Session. "
    f"I call it the curb tax: what one more year of waiting actually costs you.{E}"
    f"{P}Not just salary you could be earning elsewhere. The shifts you dread. "
    f"The energy your family gets &mdash; the version of you they get. The compounding "
    f'of one more year of "I\'ll decide next year," which, as you may have '
    f"noticed, has a way of renewing itself automatically.{E}"
    f"{P}Nobody's curb tax has ever come out to less than $97.{E}"
    f"{P}That's the whole pitch. One hour on your actual situation, a written "
    f"plan within 48 hours, full refund if you leave without clarity. The "
    f"founding spots are nearly gone, and the price goes to $147 when they are.{E}"
    f"{P}{link(SESSION_URL, 'Take a spot — $97')}{E}"
    f"{P}And if it's a no &mdash; genuinely fine. The "
    + link(FEAR_AUDIT_URL, "Fear Audit stays free")
    + ", the posts keep coming, and I'll keep holding the sign at the crosswalk either way.{E}"
)

EMAILS = {
    461554: EMAIL_1_BODY,
    461555: EMAIL_2_BODY,
    461556: EMAIL_3_BODY,
}


def fix_email(email_id: int, body_html: str) -> None:
    state = HEADER + body_html + FOOTER
    # Nested editor object is the shape the API actually honours
    # (top-level editorType/state fields are silently ignored).
    payload = {"editor": {"type": "richtext", "state": state}}
    r = requests.patch(f"{BASE}/emails/{email_id}", headers=HEADERS, json=payload, timeout=30)
    if r.status_code not in (200, 201):
        r = requests.put(f"{BASE}/emails/{email_id}", headers=HEADERS, json=payload, timeout=30)
    print(f"  {email_id}: HTTP {r.status_code} {r.text[:120] if r.status_code not in (200, 201) else ''}")


if __name__ == "__main__":
    print("Rebuilding Crossing Session emails as richtext...\n")
    for email_id, body in EMAILS.items():
        fix_email(email_id, body)
    print("\nDone — refresh Encharge and re-open the emails.")
