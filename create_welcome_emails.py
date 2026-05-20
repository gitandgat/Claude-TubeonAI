"""
Create Crosswalk Community Welcome Email Sequence
==================================================
Creates 5 emails in Encharge for new members who join via /start.

Trigger: tag 'crosswalk-community' (applied by api/subscribe.ts)
Goal:    Welcome new members, build relationship, guide toward Fear Audit
         and The Courage to Choose ($27)
Timing:  Immediate → Day 2 → Day 4 → Day 7 → Day 10

Run:
  python create_welcome_emails.py
"""

import os, uuid, json, requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ENCHARGE_API_KEY")
BASE    = "https://api.encharge.io/v1"
HEADERS = {"X-Encharge-Token": API_KEY, "Content-Type": "application/json"}

ACCOUNT_ID            = 156229
COMMUNICATION_CAT_ID  = 289738
FROM_EMAIL            = "sahawat@crosswalkwisdom.com"
FROM_NAME             = "Sahawat at Crosswalk Wisdom"
GUMROAD_URL           = "https://sahawat.gumroad.com/l/courage-to-choose"
FEAR_AUDIT_URL        = "https://fear-audit.vercel.app"
FACEBOOK_GROUP_URL    = "https://www.facebook.com/groups/2073825613397240"
LOGO_URL              = "https://d231yrez0cpae9.cloudfront.net/1750037512272-Crosswalk%20wisdom%20logo%20white%20BG.png"

# ─────────────────────────────────────────────
# Unlayer building blocks (identical to create_quiz_emails.py)
# ─────────────────────────────────────────────

def uid():
    return str(uuid.uuid4())[:9]

def logo_row():
    return {
        "id": uid(), "cells": [1],
        "values": {
            "_meta": {"htmlID": f"u_row_{uid()}", "htmlClassNames": "u_row"},
            "anchor": "", "locked": False, "columns": False, "padding": "0px",
            "hideable": True, "deletable": True, "draggable": True,
            "hideMobile": False, "selectable": True, "_styleGuide": None,
            "hideDesktop": False, "duplicatable": True, "noStackMobile": False,
            "backgroundColor": "",
            "backgroundImage": {"url": "", "size": "custom", "repeat": "no-repeat",
                                "position": "top-center", "fullWidth": True,
                                "customPosition": ["50%", "0%"]},
            "displayCondition": None, "columnsBackgroundColor": "#ffffff"
        },
        "columns": [{
            "id": uid(),
            "values": {
                "_meta": {"htmlID": f"u_column_{uid()}", "htmlClassNames": "u_column"},
                "border": {}, "padding": "0px", "deletable": True, "backgroundColor": ""
            },
            "contents": [{
                "id": uid(), "type": "image",
                "values": {
                    "src": {
                        "id": uid(), "url": LOGO_URL,
                        "size": 1600285, "width": 1024, "height": 1024,
                        "dynamic": False, "filename": "Crosswalk wisdom logo white BG.png",
                        "maxWidth": "28%", "autoWidth": False, "contentType": "image/png"
                    },
                    "_meta": {"htmlID": f"u_content_image_{uid()}", "htmlClassNames": "u_content_image"},
                    "action": {"name": "web", "values": {"href": "", "target": "_blank"}},
                    "anchor": "", "locked": False, "altText": "Crosswalk Wisdom",
                    "pending": False, "hideable": True, "deletable": True,
                    "draggable": True, "textAlign": "center", "hideMobile": False,
                    "selectable": True, "_styleGuide": None, "hideDesktop": False,
                    "duplicatable": True, "containerPadding": "20px", "displayCondition": None
                }
            }]
        }]
    }

def footer_row():
    return {
        "id": uid(), "cells": [1],
        "values": {
            "_meta": {"htmlID": f"u_row_{uid()}", "htmlClassNames": "u_row"},
            "anchor": "", "locked": False, "columns": False, "padding": "0px",
            "hideable": True, "deletable": True, "draggable": True,
            "hideMobile": False, "selectable": True, "_styleGuide": None,
            "hideDesktop": False, "duplicatable": True, "noStackMobile": False,
            "backgroundColor": "",
            "backgroundImage": {"url": "", "size": "custom", "repeat": "no-repeat",
                                "position": "top-center", "fullWidth": True,
                                "customPosition": ["50%", "0%"]},
            "displayCondition": None, "columnsBackgroundColor": ""
        },
        "columns": [{
            "id": uid(),
            "values": {
                "_meta": {"htmlID": f"u_column_{uid()}", "htmlClassNames": "u_column"},
                "border": {}, "padding": "0px", "deletable": True, "backgroundColor": ""
            },
            "contents": [
                {
                    "id": uid(), "type": "divider",
                    "values": {
                        "_meta": {"htmlID": f"u_content_divider_{uid()}", "htmlClassNames": "u_content_divider"},
                        "width": "100%", "anchor": "", "locked": False,
                        "border": {"borderTopColor": "#ecf0f1", "borderTopStyle": "solid", "borderTopWidth": "1px"},
                        "hideable": True, "deletable": True, "draggable": True,
                        "textAlign": "center", "hideMobile": False, "selectable": True,
                        "_styleGuide": None, "hideDesktop": False, "duplicatable": True,
                        "containerPadding": "10px", "displayCondition": None
                    }
                },
                {
                    "id": uid(), "type": "social",
                    "values": {
                        "_meta": {"htmlID": f"u_content_social_{uid()}", "htmlClassNames": "u_content_social"},
                        "align": "center",
                        "icons": {
                            "icons": [
                                {"url": "https://www.facebook.com/profile.php?id=61580308547545", "name": "Facebook"},
                                {"url": "https://www.instagram.com/crosswalkwisdom/", "name": "Instagram"},
                                {"url": "https://www.linkedin.com/in/sahawat-nilwatcharamanee-a359b1143/", "name": "LinkedIn"}
                            ],
                            "editor": {"data": {"customIcons": [], "customOptions": [],
                                                "showDefaultIcons": True, "showDefaultOptions": True}},
                            "iconType": "rounded"
                        },
                        "anchor": "", "locked": False, "spacing": 5,
                        "hideable": True, "iconSize": 32, "deletable": True,
                        "draggable": True, "selectable": True, "_styleGuide": None,
                        "hideDesktop": False, "duplicatable": True,
                        "containerPadding": "10px", "displayCondition": None
                    }
                },
                {
                    "id": uid(), "type": "text",
                    "values": {
                        "text": (
                            '<p style="font-size: 14px; line-height: 160%;">'
                            '<span style="color: rgb(149, 165, 166); font-size: 14px;">Crosswalk Wisdom</span></p>\n'
                            '<p style="font-size: 14px; line-height: 160%;">'
                            '<span style="color: rgb(149, 165, 166); font-size: 14px;">{{account.mailingAddress}}</span></p>\n'
                            '<p style="font-size: 14px; line-height: 160%;">'
                            '<span style="color: rgb(149, 165, 166); font-size: 14px;">{{person.unsubscribeLink}}</span> '
                            '<span style="color: rgb(149, 165, 166); font-size: 14px;">{{person.managePreferencesLink}}</span></p>'
                        ),
                        "_meta": {"htmlID": "u_content_text_footer", "htmlClassNames": "u_content_text"},
                        "color": "#003399", "anchor": "", "locked": False,
                        "fontSize": "14px", "hideable": True, "deletable": True,
                        "draggable": True,
                        "linkStyle": {"body": False, "inherit": False, "linkColor": "#95a5a6",
                                      "linkUnderline": True, "linkHoverColor": "#0000ee",
                                      "linkHoverUnderline": True},
                        "textAlign": "center", "hideMobile": False, "lineHeight": "160%",
                        "selectable": True, "_styleGuide": None, "hideDesktop": False,
                        "duplicatable": True, "containerPadding": "20px", "displayCondition": None
                    },
                    "hasDeprecatedFontControls": True
                }
            ]
        }]
    }

def text_block(html_content):
    return {
        "id": uid(), "type": "text",
        "values": {
            "text": html_content,
            "_meta": {"htmlID": f"u_content_text_{uid()}", "htmlClassNames": "u_content_text"},
            "anchor": "", "locked": False, "fontSize": "16px",
            "hideable": True, "deletable": True, "draggable": True,
            "linkStyle": {"inherit": True, "linkColor": "#2C5F4A", "linkUnderline": True,
                          "linkHoverColor": "#2C5F4A", "linkHoverUnderline": True},
            "textAlign": "left",
            "fontFamily": {"label": "Georgia", "value": "georgia,serif"},
            "hideMobile": False, "lineHeight": "180%", "selectable": True,
            "_styleGuide": None, "hideDesktop": False, "duplicatable": True,
            "containerPadding": "10px 30px", "displayCondition": None
        }
    }

def button_block(label, url, style="primary"):
    bg = "#2C5F4A" if style == "primary" else "#4A8A6E"
    return {
        "id": uid(), "type": "button",
        "values": {
            "href": {"name": "web", "values": {"href": url, "target": "_blank"}},
            "size": {"width": "100%", "autoWidth": False},
            "text": f'<span style="font-size: 16px; line-height: 32px;">{label}</span>',
            "_meta": {"htmlID": f"u_content_button_{uid()}", "htmlClassNames": "u_content_button"},
            "anchor": "", "border": {}, "locked": False, "padding": "14px 28px",
            "fontSize": "16px", "hideable": True, "deletable": True, "draggable": True,
            "textAlign": "center",
            "fontFamily": {"label": "Georgia", "value": "georgia,serif"},
            "hideMobile": False, "lineHeight": "120%", "selectable": True,
            "_styleGuide": None, "hideDesktop": False, "borderRadius": "4px",
            "buttonColors": {
                "color": "#ffffff", "hoverColor": "#ffffff",
                "backgroundColor": bg, "hoverBackgroundColor": "#4A8A6E"
            },
            "duplicatable": True, "calculatedWidth": 540, "calculatedHeight": 42,
            "containerPadding": "20px 30px", "displayCondition": None
        }
    }

def divider_block():
    return {
        "id": uid(), "type": "divider",
        "values": {
            "_meta": {"htmlID": f"u_content_divider_{uid()}", "htmlClassNames": "u_content_divider"},
            "width": "100%", "anchor": "", "locked": False,
            "border": {"borderTopColor": "#BBBBBB", "borderTopStyle": "solid", "borderTopWidth": "0px"},
            "hideable": True, "deletable": True, "draggable": True,
            "textAlign": "center", "hideMobile": False, "selectable": True,
            "_styleGuide": None, "hideDesktop": False, "duplicatable": True,
            "containerPadding": "5px 30px", "displayCondition": None
        }
    }

def sign_off():
    return text_block(
        '<p style="line-height: 180%; font-size: 16px;">— Sahawat</p>'
        '<p style="line-height: 180%; font-size: 16px;">'
        '<span style="color: #888888; font-size: 14px;">Crosswalk Wisdom</span></p>'
    )

def body_row(contents):
    return {
        "id": uid(), "cells": [1],
        "values": {
            "_meta": {"htmlID": f"u_row_{uid()}", "htmlClassNames": "u_row"},
            "anchor": "", "locked": False, "columns": False, "padding": "0px",
            "hideable": True, "deletable": True, "draggable": True,
            "hideMobile": False, "selectable": True, "_styleGuide": None,
            "hideDesktop": False, "duplicatable": True, "noStackMobile": False,
            "backgroundColor": "",
            "backgroundImage": {"url": "", "size": "custom", "repeat": "no-repeat",
                                "position": "top-center", "fullWidth": True,
                                "customPosition": ["50%", "0%"]},
            "displayCondition": None, "columnsBackgroundColor": "#ffffff"
        },
        "columns": [{
            "id": uid(),
            "values": {
                "_meta": {"htmlID": f"u_column_{uid()}", "htmlClassNames": "u_column"},
                "border": {}, "padding": "0px", "deletable": True, "backgroundColor": ""
            },
            "contents": contents
        }]
    }

def build_state(body_contents):
    return {
        "body": {
            "id": uid(),
            "rows": [logo_row(), body_row(body_contents), footer_row()],
            "values": {
                "_meta": {"htmlID": "u_body", "htmlClassNames": "u_body"},
                "language": {},
                "linkStyle": {"body": True, "inherit": False, "linkColor": "#2C5F4A",
                              "linkUnderline": True, "linkHoverColor": "#2C5F4A",
                              "linkHoverUnderline": True},
                "textColor": "#1A1917",
                "fontFamily": {"label": "Georgia", "value": "georgia,serif"},
                "popupWidth": "600px", "_styleGuide": None, "popupHeight": "auto",
                "borderRadius": "10px", "contentAlign": "center", "contentWidth": "600px",
                "popupPosition": "center", "preheaderText": "",
                "backgroundColor": "#f8f4ee",
                "backgroundImage": {"url": "", "size": "custom", "repeat": "no-repeat",
                                    "position": "top-center", "fullWidth": True,
                                    "customPosition": ["50%", "0%"]},
                "contentVerticalAlign": "top",
                "popupBackgroundColor": "#FFFFFF",
                "popupBackgroundImage": {"url": "", "size": "cover", "repeat": "no-repeat",
                                         "position": "center", "fullWidth": True},
                "popupCloseButton_action": {
                    "name": "close_popup",
                    "attrs": {"onClick": "document.querySelector('.u-popup-container').style.display = 'none';"}
                },
                "popupCloseButton_margin": "0px",
                "popupCloseButton_position": "top-right",
                "popupCloseButton_iconColor": "#000000",
                "popupOverlay_backgroundColor": "rgba(0, 0, 0, 0.1)",
                "popupCloseButton_borderRadius": "0px",
                "popupCloseButton_backgroundColor": "#DDDDDD"
            },
            "footers": [], "headers": []
        },
        "counters": {
            "u_row": 3, "u_column": 3, "u_content_text": 8,
            "u_content_image": 1, "u_content_button": 2,
            "u_content_social": 1, "u_content_divider": 3
        },
        "schemaVersion": 21
    }

# ─────────────────────────────────────────────
# Email content
# ─────────────────────────────────────────────

P = '<p style="line-height: 180%; font-size: 16px;">'
E = '</p>'

EMAILS = [
    # ── Email 1 — Immediate ──────────────────────────────────────────────
    {
        "name": "CW Welcome 1: You made it.",
        "subject": "You made it. (And that already took something.)",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}You just joined The Crosswalk Community.{E}'
                f'{P}That might feel like a small thing. I want to tell you it isn\'t.{E}'
                f'{P}Most healthcare professionals who feel burned out do one of two things: '
                f'they push through, or they scroll. They add more shifts, more coffee, more '
                f'convincing themselves it\'s just a hard season. Or they lose themselves in '
                f'burnout memes on Instagram at midnight, feeling briefly understood, and '
                f'then going right back to bed to do it again tomorrow.{E}'
                f'{P}Joining here is neither of those things. It\'s the first honest move.{E}'
            ),
            text_block(
                f'{P}Here\'s what The Crosswalk is:{E}'
                f'{P}It\'s a community for healthcare professionals who are done pretending '
                f'they\'re fine — and are ready to figure out what\'s next. Nurses. '
                f'Physicians. Pharmacists. Therapists. People who gave everything to a '
                f'system that never gave back.{E}'
                f'{P}Some of us are still walking. Some of us have crossed. Some of us are '
                f'standing at the curb, waiting for the signal.{E}'
                f'{P}All of us are choosing.{E}'
            ),
            text_block(
                f'{P}<strong>Two things to do right now:</strong>{E}'
                f'{P}1. Join the Facebook group — that\'s where the real conversations happen. '
                f'Introduce yourself. Tell us your profession and one thing you\'re afraid to '
                f'say out loud at work. You\'ll be surprised how many people have been waiting '
                f'to hear exactly that.{E}'
                f'{P}2. If you haven\'t taken the Fear Audit yet, do it. It takes 2 minutes '
                f'and names the exact fear that\'s been running your life. It\'s free and it\'s '
                f'the most useful 2 minutes you\'ll spend this week.{E}'
            ),
            button_block("Join the Facebook group", FACEBOOK_GROUP_URL, style="secondary"),
            button_block("Take the Fear Audit (free, 2 min)", FEAR_AUDIT_URL),
            divider_block(),
            sign_off(),
        ]
    },

    # ── Email 2 — Day 2 ──────────────────────────────────────────────────
    {
        "name": "CW Welcome 2: What we actually believe here.",
        "subject": "What we actually believe here.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}Most wellness communities will tell you that burnout is a workload problem.{E}'
                f'{P}Take more breaks. Set better boundaries. Practice self-care.{E}'
                f'{P}That\'s not wrong, exactly. It\'s just not the whole truth.{E}'
            ),
            text_block(
                f'{P}Here\'s what we believe at Crosswalk Wisdom:{E}'
                f'{P}<strong>Burnout is primarily an identity crisis.</strong>{E}'
                f'{P}The cage isn\'t the hospital. It\'s the story you\'ve been telling '
                f'yourself about who you have to be. "I am a doctor." "I am a nurse." '
                f'These aren\'t descriptions — they\'re load-bearing walls. And dismantling '
                f'them feels like dying because a version of you actually is.{E}'
                f'{P}That grief is real. And it\'s also the beginning.{E}'
            ),
            text_block(
                f'{P}A few more things we believe — things you won\'t hear in most '
                f'healthcare burnout spaces:{E}'
                f'{P}<em>Your body knew before your brain did.</em> The fatigue, the '
                f'numbness, the parking lot tears — not weakness. Intelligence. Burnout '
                f'is wisdom in the body before it becomes decision in the mind.{E}'
                f'{P}<em>Leaving is not betrayal. Staying to disappear is.</em> Nobody '
                f'says it out loud: you need you. Choosing yourself is not abandonment. '
                f'Erasing yourself to stay is.{E}'
                f'{P}<em>Fear is a map, not a stop sign.</em> Financial insecurity, fear '
                f'of judgment, identity loss — these are diagnostic data. Navigate toward '
                f'them, not away.{E}'
            ),
            text_block(
                f'{P}More on that last one tomorrow.{E}'
            ),
            divider_block(),
            sign_off(),
        ]
    },

    # ── Email 3 — Day 4 ──────────────────────────────────────────────────
    {
        "name": "CW Welcome 3: The Yellow Vest",
        "subject": "I left medicine. I became a crossing guard. Here's what happened.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}I want to tell you a story today. Not the polished version. The real one.{E}'
            ),
            text_block(
                f'{P}The morning I showed up to my first shift as a crossing guard, I parked '
                f'around the corner. Not because I was ashamed — I told myself that.{E}'
                f'{P}I put on the yellow vest in my car. I checked my mirrors. I walked to '
                f'the corner. And for the next two hours, I held a stop sign and waved '
                f'kindergartners across the street.{E}'
                f'{P}Two former colleagues drove past. I saw them slow down. I smiled. I waved.{E}'
            ),
            text_block(
                f'{P}And then a first-grader — maybe six years old, missing a front tooth — '
                f'grabbed my hand before crossing and looked up at me and said:{E}'
                f'{P}<em>"You\'re the helper."</em>{E}'
                f'{P}I had been a doctor for twelve years. Nobody had ever called me the helper.{E}'
            ),
            text_block(
                f'{P}I\'m not telling you to become a crossing guard.{E}'
                f'{P}I\'m telling you that the sidewalk taught me what the hospital never could: '
                f'that healing starts when you slow down enough to see what\'s actually there.{E}'
                f'{P}The classroom is everywhere. You don\'t need a $3,000 retreat. You need '
                f'to stop moving long enough to ask the question you\'ve been avoiding.{E}'
                f'{P}Most people in this community are avoiding one of three questions. The '
                f'Fear Audit identifies which one is yours. If you haven\'t taken it yet, '
                f'this is a good moment.{E}'
            ),
            button_block("Take the Fear Audit (free)", FEAR_AUDIT_URL),
            divider_block(),
            sign_off(),
        ]
    },

    # ── Email 4 — Day 7 ──────────────────────────────────────────────────
    {
        "name": "CW Welcome 4: The three fears",
        "subject": "There are only three fears. You probably have one dominant one.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}When I ask burned-out healthcare professionals what they\'re afraid of, '
                f'they almost always say the same thing:{E}'
                f'{P}<em>"Everything."</em>{E}'
                f'{P}That\'s not an answer. That\'s a defense mechanism.{E}'
            ),
            text_block(
                f'{P}After years of working with people in career transition — and going '
                f'through my own — I\'ve found that it almost always comes down to one of '
                f'three fears:{E}'
                f'{P}<strong>Financial Insecurity.</strong> "I can\'t afford to leave." '
                f'"I have student loans." "My family depends on this income." The fear that '
                f'if you step away from healthcare, you step away from financial safety forever.{E}'
                f'{P}<strong>Fear of Judgment.</strong> "What will people think?" '
                f'"My parents sacrificed for this." "My colleagues will think I gave up." '
                f'The invisible audience that you\'ve been performing for your entire career.{E}'
                f'{P}<strong>Identity Loss.</strong> "Who am I without this?" This is the '
                f'deepest one. Not financial, not social — existential. The white coat stopped '
                f'being something you wore. It became something you were.{E}'
            ),
            text_block(
                f'{P}Most people think their dominant fear is financial. When they actually '
                f'sit with it, it\'s identity loss.{E}'
                f'{P}The Fear Audit is a 2-minute quiz that scores all three and tells you '
                f'which one is running your life. Over 10,000 healthcare professionals have '
                f'taken it. It\'s free. And the results will clarify something you\'ve probably '
                f'been carrying as fog.{E}'
            ),
            button_block("Find out which fear is yours", FEAR_AUDIT_URL),
            divider_block(),
            sign_off(),
        ]
    },

    # ── Email 5 — Day 10 ──────────────────────────────────────────────────
    {
        "name": "CW Welcome 5: The first act of courage",
        "subject": "You don't need more awareness. You need one act of courage.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}You\'ve been in The Crosswalk for ten days now.{E}'
                f'{P}I want to ask you something directly:{E}'
                f'{P}<em>What\'s changed?</em>{E}'
                f'{P}If the answer is "nothing yet" — that\'s honest. And it\'s also the '
                f'most common answer I hear. Awareness without a bridge to action is just '
                f'more fog with better lighting.{E}'
            ),
            text_block(
                f'{P}Here\'s what I\'ve learned: the gap between knowing you\'re burned out '
                f'and actually doing something about it isn\'t information. You have enough '
                f'information. It\'s one thing:{E}'
                f'{P}<strong>The courage to choose yourself.</strong>{E}'
                f'{P}Not leaving tomorrow. Not blowing up your life. Just one honest act — '
                f'naming the fear, making one plan, taking one step — that says: I matter '
                f'enough to do this.{E}'
            ),
            text_block(
                f'{P}I wrote <em>The Courage to Choose</em> for exactly this moment.{E}'
                f'{P}It\'s a practical guide — built on Adlerian psychology, Stoic philosophy, '
                f'and Viktor Frankl\'s logotherapy — for moving from awareness to action. '
                f'Three chapters: naming the fear, reframing the story, taking the first step.{E}'
                f'{P}It\'s $27. It\'s the most direct thing I know how to offer you.{E}'
                f'{P}Not inspiration. Not more awareness. A framework you can actually walk through.{E}'
            ),
            button_block("Get The Courage to Choose — $27", GUMROAD_URL),
            text_block(
                f'{P}And if you\'re not ready for that yet — that\'s okay. Keep showing up '
                f'in the community. Keep reading. The crossing happens at your pace, not mine.{E}'
                f'{P}The sidewalk is the classroom. You are the student. Healing is the lesson.{E}'
            ),
            divider_block(),
            text_block(
                f'{P}— Sahawat{E}'
                f'{P}<span style="color: #888888; font-size: 14px;">Crosswalk Wisdom</span>{E}'
                f'{P}<span style="color: #888888; font-size: 14px;">P.S. If you\'ve taken the '
                f'Fear Audit but haven\'t read your results closely yet — go back to it. '
                f'The dominant fear it identifies is the exact chapter in the guide you need '
                f'most.</span>{E}'
            ),
        ]
    },
]

# ─────────────────────────────────────────────
# Create emails via Encharge API
# ─────────────────────────────────────────────

def create_email(email_def):
    state = build_state(email_def["contents"])
    payload = {
        "name":                    email_def["name"],
        "subject":                 email_def["subject"],
        "fromEmail":               FROM_EMAIL,
        "fromName":                FROM_NAME,
        "type":                    "HTML",
        "communicationCategoryId": COMMUNICATION_CAT_ID,
        "editor": {
            "type":  "unlayer",
            "state": state
        }
    }
    r = requests.post(f"{BASE}/emails", headers=HEADERS, json=payload)
    if r.status_code in (200, 201):
        data = r.json()
        eid = data.get("email", {}).get("id") or data.get("id")
        return eid
    else:
        raise RuntimeError(
            f"Failed to create '{email_def['name']}': {r.status_code} {r.text[:300]}"
        )


def main():
    if not API_KEY:
        raise SystemExit("ENCHARGE_API_KEY not set in .env")

    print("Creating Crosswalk Community Welcome email sequence...\n")
    created = []

    for i, email_def in enumerate(EMAILS, 1):
        print(f"  [{i}/5] {email_def['name']}...")
        eid = create_email(email_def)
        created.append({
            "index": i, "id": eid,
            "name": email_def["name"],
            "subject": email_def["subject"]
        })
        print(f"         ✓ Created — ID: {eid}")

    print("\n✓ All 5 emails created.\n")
    print("Email IDs:")
    for e in created:
        print(f"  Email {e['index']}: ID {e['id']}  —  {e['subject']}")

    out_file = "welcome_email_ids.json"
    with open(out_file, "w") as f:
        json.dump(created, f, indent=2)
    print(f"\nIDs saved to {out_file}")

    print("\n" + "="*60)
    print("NEXT STEP — Set up the flow in Encharge UI:")
    print("="*60)
    timings = ["Immediately", "Day 2", "Day 4", "Day 7", "Day 10"]
    print("  1. Go to Encharge → Flows → New Flow")
    print("  2. Set trigger: Tag Added = 'crosswalk-community'")
    print("  3. Add each email with the following delays:\n")
    for e in created:
        print(f"     {timings[e['index']-1]:12s}  →  Email ID {e['id']}")
    print("\n  4. Activate the flow.")
    print("  5. Done — new /start signups will receive this sequence automatically.\n")


if __name__ == "__main__":
    main()
