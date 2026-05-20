"""
Create Crosswalk Wisdom Quiz → Courage to Choose Email Sequence
================================================================
Creates 5 emails in Encharge using the exact unlayer format
as the Fear Audit sequence (436027–436031).

Trigger: quiz-completed tag (applied by Encharge hook when quiz is submitted)
Goal: Convert quiz completers to purchase The Courage to Choose ($27 on Gumroad)
Timing: Immediate → Day 2 → Day 5 → Day 8 → Day 12

Run:
  python create_quiz_emails.py
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
LOGO_URL              = "https://d231yrez0cpae9.cloudfront.net/1750037512272-Crosswalk%20wisdom%20logo%20white%20BG.png"

# ─────────────────────────────────────────────
# Unlayer building blocks
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
                        "_meta": {"htmlID": "u_content_text_5", "htmlClassNames": "u_content_text"},
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
            "linkStyle": {"inherit": True, "linkColor": "#1a1a1a", "linkUnderline": True,
                          "linkHoverColor": "#1a1a1a", "linkHoverUnderline": True},
            "textAlign": "left",
            "fontFamily": {"label": "Georgia", "value": "georgia,serif"},
            "hideMobile": False, "lineHeight": "180%", "selectable": True,
            "_styleGuide": None, "hideDesktop": False, "duplicatable": True,
            "containerPadding": "10px 30px", "displayCondition": None
        }
    }

def button_block(label, url, style="primary"):
    bg = "#1a1a1a" if style == "primary" else "#555555"
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
                "backgroundColor": bg, "hoverBackgroundColor": "#333333"
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
                "linkStyle": {"body": True, "inherit": False, "linkColor": "#1a1a1a",
                              "linkUnderline": True, "linkHoverColor": "#1a1a1a",
                              "linkHoverUnderline": True},
                "textColor": "#000000",
                "fontFamily": {"label": "Georgia", "value": "georgia,serif"},
                "popupWidth": "600px", "_styleGuide": None, "popupHeight": "auto",
                "borderRadius": "10px", "contentAlign": "center", "contentWidth": "600px",
                "popupPosition": "center", "preheaderText": "",
                "backgroundColor": "#f9f9f9",
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
# Email content definitions
# ─────────────────────────────────────────────

P = '<p style="line-height: 180%; font-size: 16px;">'
E = '</p>'

EMAILS = [
    {
        "name": "Quiz → Email 1: You Crossed a Line",
        "subject": "You crossed a line most people don't.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}Most people who feel burned out in healthcare do one of two things.{E}'
                f'{P}They push through — adding more shifts, more coffee, more '
                f'convincing themselves it\'s just a hard season.{E}'
                f'{P}Or they fantasize about leaving without ever taking a single honest '
                f'look at what\'s actually stopping them.{E}'
                f'{P}You did something different. You sat down, answered twelve questions, '
                f'and looked clearly at where you are on this road.{E}'
                f'{P}That matters more than it sounds.{E}'
            ),
            text_block(
                f'{P}I built the Burnout Crosswalk Assessment because I\'ve been exactly '
                f'where you are. Trained physician. Over a decade of investment in a career '
                f'I was proud of — and quietly suffocating in.{E}'
                f'{P}The day I finally looked honestly at what was keeping me stuck wasn\'t '
                f'the day I left medicine. But it was the day the leaving became possible.{E}'
                f'{P}You\'ve just had that day.{E}'
            ),
            text_block(
                f'{P}Here\'s what I\'ve learned: naming the stage you\'re in is only the '
                f'first step. What most people don\'t have is a framework for what comes next — '
                f'a way to move through the fear rather than around it.{E}'
                f'{P}Over the next few days, I\'m going to share the ideas that shaped my '
                f'own transition. Not to sell you a story. To give you something useful.{E}'
                f'{P}For now: you\'re in the right place.{E}'
            ),
            divider_block(),
            sign_off(),
        ]
    },
    {
        "name": "Quiz → Email 2: It's Not Burnout. It's the Fear Under It.",
        "subject": "The burnout is real. But it's not what's keeping you stuck.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}When I ask healthcare professionals what\'s keeping them from making a '
                f'change, the answers almost always involve workload, the system, the hours, '
                f'the administration.{E}'
                f'{P}All real. All valid.{E}'
                f'{P}But here\'s what I\'ve noticed, both in my own transition and in the '
                f'hundreds of people I\'ve worked with since: the burnout is the reason you '
                f'want to leave. It\'s not the reason you haven\'t.{E}'
            ),
            text_block(
                f'{P}Alfred Adler — the psychologist whose thinking sits at the core of '
                f'everything I teach — was clear about this: almost every hesitation we feel '
                f'about changing our lives is, at its root, interpersonal.{E}'
                f'{P}We\'re not afraid of the career change itself. We\'re afraid of our '
                f'parents\' disappointment. Our colleagues\' raised eyebrows. The version of '
                f'us that exists in other people\'s minds, and what happens to that version '
                f'when we do something unexpected.{E}'
                f'{P}Ichiro Kishimi put it plainly: <em>freedom is being disliked.</em> Not '
                f'seeking it out, but accepting that if you live according to your own values, '
                f'some people will disapprove — and that\'s not a crisis. It\'s the price of '
                f'authenticity.{E}'
            ),
            text_block(
                f'{P}Here\'s the question I\'d sit with today:{E}'
                f'{P}If no one in your life would ever know you made this transition — if it '
                f'were entirely private — would you still hesitate?{E}'
                f'{P}If the answer is no, the obstacle isn\'t the job. It\'s relational.{E}'
                f'{P}<em>The Courage to Choose</em> has a full chapter on this — the Judgment '
                f'Detox — that goes deep into whose approval you\'ve been unconsciously living '
                f'for, and how to stop letting that run your decisions.{E}'
            ),
            button_block("Take a look at the guide", GUMROAD_URL, style="secondary"),
            divider_block(),
            sign_off(),
        ]
    },
    {
        "name": "Quiz → Email 3: You Are Not Your White Coat",
        "subject": "The costume and the person wearing it.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}Epictetus was a Stoic philosopher and a former slave. He had very few '
                f'possessions and almost no control over his circumstances.{E}'
                f'{P}What he had was a distinction that I\'ve returned to more times than I '
                f'can count:{E}'
                f'{P}There is what you are. And there is what you do.{E}'
                f'{P}Most of us in healthcare have spent years — sometimes decades — '
                f'collapsing those two things into one.{E}'
            ),
            text_block(
                f'{P}I call it the costume problem.{E}'
                f'{P}At some point, the white coat stopped being something you put on. It '
                f'became something you <em>were.</em> The title didn\'t describe your work — '
                f'it described your worth. Your identity. Your answer to the question '
                f'"who are you?"{E}'
                f'{P}The fear of leaving isn\'t just the fear of financial uncertainty or '
                f'professional judgment. It\'s the fear of what\'s left when you take the '
                f'costume off.{E}'
                f'{P}Who are you without the degree? The title? The role that everyone '
                f'recognizes?{E}'
            ),
            text_block(
                f'{P}Here\'s what I found on the other side of that question:{E}'
                f'{P}More than I expected.{E}'
                f'{P}The costume was covering someone who had never been allowed to just '
                f'exist — only to perform, to achieve, to be useful. Removing it wasn\'t '
                f'a loss. It was an introduction.{E}'
                f'{P}The second chapter of <em>The Courage to Choose</em> — The Identity '
                f'Bridge — is built entirely around this transition. It\'s a framework for '
                f'holding both who you\'ve been and who you\'re becoming, so the crossing '
                f'doesn\'t feel like erasure.{E}'
            ),
            button_block("Get The Courage to Choose — $27", GUMROAD_URL),
            divider_block(),
            sign_off(),
        ]
    },
    {
        "name": "Quiz → Email 4: I Left Medicine. I Became a Crossing Guard.",
        "subject": "The year I made 70% less — and what I actually lost.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}I want to tell you a story today. Not a polished one. The real one.{E}'
                f'{P}I left medicine after years of training and practice. I had the degree, '
                f'the title, the respect that comes with it. I also had a quiet dread every '
                f'morning that I\'d spent most of my adult life getting to a place I didn\'t '
                f'actually want to be.{E}'
                f'{P}I moved to Toronto. I became a crossing guard.{E}'
            ),
            text_block(
                f'{P}That\'s not a metaphor. That\'s what happened.{E}'
                f'{P}I stood at a crosswalk in a fluorescent vest, helping people across the '
                f'street. My income dropped by roughly 70%. People I\'d trained with didn\'t '
                f'understand. Some of them still don\'t.{E}'
                f'{P}And here\'s what I actually lost:{E}'
                f'{P}The performance of being fine.{E}'
                f'{P}The exhaustion of maintaining a version of myself that looked successful '
                f'from the outside while feeling hollow on the inside.{E}'
                f'{P}The identity I\'d borrowed from a system that never really fit.{E}'
            ),
            text_block(
                f'{P}What I found at that crosswalk — in the simplest, most grounded work '
                f'I\'d ever done — was that I was still someone. Without the title. Without '
                f'the salary. Without anyone\'s approval.{E}'
                f'{P}That\'s where Crosswalk Wisdom came from. Not from a branding exercise. '
                f'From standing at an actual crosswalk and understanding, for the first time, '
                f'what it means to cross one deliberately.{E}'
                f'{P}<em>The Courage to Choose</em> is the distillation of everything I '
                f'learned in that crossing — structured into a framework you can actually '
                f'walk through. Not inspiration. Tools.{E}'
            ),
            button_block("Get The Courage to Choose — $27", GUMROAD_URL),
            divider_block(),
            sign_off(),
        ]
    },
    {
        "name": "Quiz → Email 5: You're Not Waiting Until You're Ready",
        "subject": "You're not waiting until you're ready. You're waiting until it's safe.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}Viktor Frankl survived four Nazi concentration camps. He lost his wife, '
                f'his parents, his brother.{E}'
                f'{P}What he preserved — what no external force could touch — was his '
                f'ability to choose his response to his circumstances.{E}'
                f'{P}He wrote: <em>"Between stimulus and response there is a space. In that '
                f'space is our power to choose our response. In our response lies our growth '
                f'and our freedom."</em>{E}'
            ),
            text_block(
                f'{P}Most people reading this aren\'t waiting because they\'re not ready.{E}'
                f'{P}They\'re waiting because the risk isn\'t comfortable yet. Because the '
                f'financial picture isn\'t clean enough. Because they want one more year of '
                f'certainty before they step into uncertainty.{E}'
                f'{P}Brianna Wiest calls this the difference between <em>strategic delay</em> '
                f'and <em>fear-based avoidance.</em> Strategic delay has a clear condition: '
                f'"I\'m waiting until X." Fear-based avoidance moves the goalposts: every '
                f'time X arrives, a new condition appears.{E}'
                f'{P}The question worth asking honestly is: which one is this?{E}'
            ),
            text_block(
                f'{P}The Courage to Choose won\'t make the decision for you. No guide, no '
                f'coach, no framework can do that.{E}'
                f'{P}What it will do is give you the tools to know — clearly, practically, '
                f'without self-deception — what\'s actually in the way. And a structured '
                f'path through each of the three fears that keep most healthcare professionals '
                f'stuck longer than they need to be.{E}'
                f'{P}For $27, it\'s the most direct thing I know how to offer you.{E}'
            ),
            button_block("Get The Courage to Choose — $27", GUMROAD_URL),
            divider_block(),
            text_block(
                f'{P}— Sahawat{E}'
                f'{P}<span style="color: #888888; font-size: 14px;">Crosswalk Wisdom</span>{E}'
                f'{P}<span style="color: #888888; font-size: 14px;">P.S. The assessment you '
                f'completed told you where you are on the crosswalk. This guide tells you how '
                f'to cross it.</span>{E}'
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
        "name":                 email_def["name"],
        "subject":              email_def["subject"],
        "fromEmail":            FROM_EMAIL,
        "fromName":             FROM_NAME,
        "type":                 "HTML",
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
        raise RuntimeError(f"Failed to create '{email_def['name']}': {r.status_code} {r.text[:300]}")


def main():
    if not API_KEY:
        raise SystemExit("ENCHARGE_API_KEY not set in .env")

    print("Creating Courage to Choose email sequence...\n")
    created = []

    for i, email_def in enumerate(EMAILS, 1):
        print(f"  [{i}/5] {email_def['name']}...")
        eid = create_email(email_def)
        created.append({"index": i, "id": eid, "name": email_def["name"],
                         "subject": email_def["subject"]})
        print(f"         ✓ Created — ID: {eid}")

    print("\n✓ All 5 emails created.\n")
    print("Email IDs:")
    for e in created:
        print(f"  Email {e['index']}: ID {e['id']}  —  {e['subject']}")

    out_file = "quiz_email_ids.json"
    with open(out_file, "w") as f:
        json.dump(created, f, indent=2)
    print(f"\nIDs saved to {out_file}")

    print("\nNext step in Encharge UI:")
    print("  1. Flows → New Flow")
    print("  2. Trigger: Tag Added = 'quiz-completed'")
    print("  3. Add emails in order with delays:")
    for e in created:
        delays = ["Immediately", "Day 2", "Day 5", "Day 8", "Day 12"]
        print(f"     {delays[e['index']-1]}: Email ID {e['id']}")


if __name__ == "__main__":
    main()
