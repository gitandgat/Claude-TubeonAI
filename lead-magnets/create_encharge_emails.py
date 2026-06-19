#!/usr/bin/env python3
"""
Create the 5 lead-magnet nurture sequences (3 emails each = 15) in Encharge.

Follows project memory (feedback_encharge_editor_state) EXACTLY:
  - editor type "richtext" with a plain HTML string state (NOT unlayer dict)
  - set BOTH `html` (the field Encharge actually SENDS) and `editor.state`
  - compliance footer via Encharge merge tags ({{account.mailingAddress}},
    {{person.unsubscribeLink}}) so it's centrally managed + legally correct
  - CREATE only (POST). Never PATCH or touch existing emails.

After creation, prints the tag -> [email ids] map for wiring the flows in the
Encharge flow builder.

    python create_encharge_emails.py --dry-run   # preview names/subjects, no writes
    python create_encharge_emails.py             # create live + verify each
"""

import argparse
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv("/Users/toto/Claude TubeonAI/.env")
API_KEY = os.getenv("ENCHARGE_API_KEY")
if not API_KEY:
    sys.exit("ENCHARGE_API_KEY not set")

BASE = "https://api.encharge.io/v1"
HEADERS = {"X-Encharge-Token": API_KEY, "Content-Type": "application/json"}
COMMUNICATION_CAT_ID = 289738
FROM_EMAIL = "sahawat@crosswalkwisdom.com"
FROM_NAME = "Sahawat at Crosswalk Wisdom"
LOGO_URL = "https://d231yrez0cpae9.cloudfront.net/1750037512272-Crosswalk%20wisdom%20logo%20white%20BG.png"

GREETING = 'Hey {{ person.firstName | default: "there" }},'
P = '<p style="font-family: Georgia, serif; font-size: 16px; line-height: 180%; color: #1A1917;">'
E = "</p>"


def link(url, text):
    return f'<a href="{url}" target="_blank" style="color: #2C5F4A;">{text}</a>'


def button(url, label):
    return ('<p style="text-align: center; margin: 28px 0;">'
            f'<a href="{url}" target="_blank" style="background: #2C5F4A; color: #ffffff; '
            'font-family: Georgia, serif; font-size: 16px; font-weight: bold; padding: 14px 30px; '
            f'border-radius: 6px; text-decoration: none; display: inline-block;">{label}</a></p>')


HEADER = ('<p style="text-align: center; padding: 16px 0;">'
          f'<img src="{LOGO_URL}" alt="Crosswalk Wisdom" width="150" style="max-width: 150px;"></p>')

FOOTER = (
    '<hr style="border: none; border-top: 1px solid #ecf0f1; margin: 28px 0 20px;">'
    f"{P}From the Ward to the World,<br>Sahawat{E}"
    '<p style="text-align: center; font-size: 14px; line-height: 160%; color: #95a5a6; font-family: Georgia, serif;">'
    + link("https://www.facebook.com/profile.php?id=61580308547545", "Facebook") + " &middot; "
    + link("https://www.instagram.com/crosswalkwisdom/", "Instagram") + " &middot; "
    + link("https://www.linkedin.com/in/sahawat-nilwatcharamanee-a359b1143/", "LinkedIn")
    + "<br><br>Crosswalk Wisdom<br>{{account.mailingAddress}}<br>"
    "{{person.unsubscribeLink}} &nbsp; {{person.managePreferencesLink}}</p>"
)


def wrap_html(inner):
    return ('<!DOCTYPE html><html><body style="margin:0;padding:0;background:#f8f4ee;">'
            '<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f4ee;padding:32px 0;">'
            '<tr><td align="center">'
            '<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:10px;">'
            f'<tr><td style="padding:24px 40px;">{inner}</td></tr></table></td></tr></table></body></html>')


def para(*sentences):
    return "".join(f"{P}{s}{E}" for s in sentences)


PM = "https://www.crosswalkwisdom.com/pivot-map"
IV = "https://www.crosswalkwisdom.com/inner-voices"
TC = "https://www.crosswalkwisdom.com/train-like-a-clinician"
MD = "https://www.crosswalkwisdom.com/marginal-decade"
CC = "https://www.crosswalkwisdom.com/clinic-to-coaching"

# tag -> [(name, subject, body_html), ...]  (body excludes header/footer)
SEQUENCES = {
    "lead-magnet-pivot-map": [
        ("Pivot Map - 01 Deliver", "Your Pivot Map is here (read Section 2 twice)",
         para(GREETING, "Your guide is ready. One ask before you open it: read Section 2 twice. The reframe in it is the whole game. Everything else is just the map that follows.") + button(PM, "Open the Pivot Map")),
        ("Pivot Map - 02 Reframe", "The question that keeps unmatched doctors stuck",
         para(GREETING, "Most unmatched IMGs ask one question on repeat: how do I finally match? It feels responsible. It also hands your future to a lottery you don't control.", "The better question is what your medical training is worth right now, outside the match.", "Reply and tell me which of the four paths fits you best. I read every reply.")),
        ("Pivot Map - 03 Bridge", "Want help deciding?",
         para(GREETING, "The hard part isn't the plan. It's deciding, because deciding is exactly what sunk cost is built to stop.", "If you want a structured way through it, the Fear Audit names which layer of the trap is holding you, in two minutes.") + button("https://www.crosswalkwisdom.com", "Take the Fear Audit")),
    ],
    "lead-magnet-inner-voices": [
        ("Inner Voices - 01 Deliver", "Your guide to the 5 voices",
         para(GREETING, "It's here. Read it tonight with one question in mind: which voice is loudest for you right now? Naming it is most of the work.") + button(IV, "Open the guide")),
        ("Inner Voices - 02 The Realist", "The voice that sounds the most like wisdom",
         para(GREETING, "The Realist is the dangerous one, because it dresses fear up as being responsible.", "This week, when you catch yourself being realistic about not making a change, ask whether it's truth or just the Realist keeping you safe.", "Reply and tell me which voice you caught.")),
        ("Inner Voices - 03 Identity", "When the voices are about your whole identity",
         para(GREETING, "Sometimes the voices aren't about one decision. They're about who you are without the title.", "If that's where you are, this is the deeper work I write about most.") + button("https://www.crosswalkwisdom.com", "Read more")),
    ],
    "lead-magnet-train-like-a-clinician": [
        ("Train Like a Clinician - 01 Deliver", "Your training guide (read the recovery section first)",
         para(GREETING, "It's here. If you only read one part today, read the recovery section. It's where most people's progress quietly leaks.") + button(TC, "Open the guide")),
        ("Train Like a Clinician - 02 Soreness", "Soreness is not the scoreboard",
         para(GREETING, "The most common training mistake I see is chasing soreness as proof of a good session. It's a poor signal.", "Progressive overload and recovery build strength, not how wrecked you feel.", "Reply with your current split and I'll tell you the first thing I'd change.")),
        ("Train Like a Clinician - 03 Coaching", "Want a clinical eye on your training?",
         para(GREETING, "If you want training built from physiology instead of bro-science, that's what I coach.", "Reply with the word coaching and I'll send details.")),
    ],
    "lead-magnet-marginal-decade": [
        ("Marginal Decade - 01 Deliver", "Your prevention guide is here",
         para(GREETING, "It's here. The whole guide comes down to a few unglamorous habits. Pick one to start this week.") + button(MD, "Open the guide")),
        ("Marginal Decade - 02 Muscle", "Muscle is the organ of aging",
         para(GREETING, "If you do one thing for your last healthy decade, build and keep muscle. You can start at any age, and it protects nearly everything else.", "What's one strength habit you could add this week? Reply and tell me.")),
        ("Marginal Decade - 03 Screening", "The screening conversation you keep postponing",
         para(GREETING, "Prevention is the work the system was too rushed to do. The screening conversation you've been putting off is often the highest-leverage one.", "This week is a good week to book it.")),
    ],
    "lead-magnet-clinic-to-coaching": [
        ("Clinic to Coaching - 01 Deliver", "Your guide to the clinic-to-coaching move",
         para(GREETING, "It's here. The core idea: you already have the hard part, clinical credibility. What you need is the translation into a practice clients pay for.") + button(CC, "Open the guide")),
        ("Clinic to Coaching - 02 Not a step down", "It isn't a step down",
         para(GREETING, "A lot of healthcare people quietly think coaching is a demotion. For many of us it's the part of medicine we actually wanted: time, relationship, and visible change.", "What's the one thing stopping you? Reply and tell me.")),
        ("Clinic to Coaching - 03 Map", "Want to map your move?",
         para(GREETING, "If you're seriously considering the move, reply with the word map and I'll point you to the next step.", "Your clinical background is an advantage most coaches would pay for.")),
    ],
}


def create_email(name, subject, body_html):
    state = HEADER + body_html + FOOTER
    html = wrap_html(state)
    payload = {
        "name": name,
        "subject": subject,
        "fromEmail": FROM_EMAIL,
        "fromName": FROM_NAME,
        "type": "HTML",
        "communicationCategoryId": COMMUNICATION_CAT_ID,
        "html": html,
        "editor": {"type": "richtext", "state": state},
    }
    r = requests.post(f"{BASE}/emails", headers=HEADERS, json=payload, timeout=30)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"create failed {r.status_code}: {r.text[:200]}")
    data = r.json()
    eid = data.get("email", {}).get("id") or data.get("id")
    # Verify: GET returns the html field (per memory). Confirm it persisted.
    g = requests.get(f"{BASE}/emails/{eid}", headers=HEADERS, timeout=30)
    gj = g.json().get("email", g.json())
    has_html = bool(gj.get("html"))
    return eid, has_html


def _print_wiring(result):
    print("\n=== FLOW WIRING (build in Encharge flow builder) ===")
    for tag, ids in result.items():
        if ids:
            print(f"  Trigger 'Tag added: {tag}'  ->  emails {ids} (Day 0, +2d, +4d)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("Lead-magnet nurture emails (richtext, CREATE only)\n")
    result = {}
    for tag, emails in SEQUENCES.items():
        print(f"== {tag} ==")
        ids = []
        for name, subject, body in emails:
            if args.dry_run:
                print(f"   [dry] {name}  |  {subject}")
                continue
            eid, ok = create_email(name, subject, body)
            print(f"   created id={eid} verified_html={ok}  |  {subject}")
            ids.append(eid)
            if not ok:
                print("\n✗ ABORT: html did not persist on this email. Stopping before "
                      "creating the rest. Investigate the payload before continuing.")
                result[tag] = ids
                _print_wiring(result)
                return
        result[tag] = ids

    if not args.dry_run:
        _print_wiring(result)


if __name__ == "__main__":
    main()
