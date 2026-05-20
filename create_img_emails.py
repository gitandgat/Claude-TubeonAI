"""
Create IMG Calculator Email Sequence
=====================================
7-email nurture sequence for people who opt into the MCCQE Reality Calculator.

Phase 1 — Digital products (Emails 1–5):
  Email 1 (Day 0):  "You ran the numbers. Most people never do."           → $17 guide (soft)
  Email 2 (Day 2):  "The 4 costs no one added up when you started."        → $17 Should You Keep Going?
  Email 3 (Day 4):  "You didn't fail medicine. The system failed you."     → $27 IMG Identity Reset
  Email 4 (Day 6):  "The immigration fear everyone ignores."               → $37 IMG Career Map
  Email 5 (Day 8):  "Income in 30 days. Without hiding your degree."       → $47 IMG Survival Playbook

Phase 2 — 1:1 coaching (Emails 6–7):
  Email 6 (Day 11): "What changes when you stop navigating this alone."    → Coaching bridge
  Email 7 (Day 14): "I have 3 spots open. Here's what we do together."    → Calendly discovery call

Trigger tag: img-calculator-optin

Run:
  python create_img_emails.py
"""

import os, uuid, json, requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ENCHARGE_API_KEY")
BASE    = "https://api.encharge.io/v1"
HEADERS = {"X-Encharge-Token": API_KEY, "Content-Type": "application/json"}

ACCOUNT_ID           = 156229
COMMUNICATION_CAT_ID = 289738
FROM_EMAIL           = "sahawat@crosswalkwisdom.com"
FROM_NAME            = "Sahawat at Crosswalk Wisdom"
LOGO_URL             = "https://d231yrez0cpae9.cloudfront.net/1750037512272-Crosswalk%20wisdom%20logo%20white%20BG.png"

GUIDE_URL    = "https://sahawat.gumroad.com/l/img-pivot"
IDENTITY_URL = "https://sahawat.gumroad.com/l/img-identity"
MAP_URL      = "https://sahawat.gumroad.com/l/img-map"
PLAYBOOK_URL = "https://sahawat.gumroad.com/l/img-playbook"
COACHING_URL = "https://calendly.com/sahawat/30min"

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

def button_block(label, url, bg_color="#2C5F4A"):
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
                "backgroundColor": bg_color, "hoverBackgroundColor": "#1a3d2b"
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

def sign_off(ps=None):
    ps_html = f'<p style="line-height: 180%; font-size: 14px; color: #888888;">P.S. {ps}</p>' if ps else ""
    return text_block(
        '<p style="line-height: 180%; font-size: 16px;">— Sahawat</p>'
        '<p style="line-height: 180%; font-size: 16px;">'
        '<span style="color: #888888; font-size: 14px;">Crosswalk Wisdom</span></p>'
        + ps_html
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
# Email content definitions
# ─────────────────────────────────────────────

P = '<p style="line-height: 180%; font-size: 16px;">'
E = '</p>'

EMAILS = [

    # ── Email 1: Day 0 ───────────────────────────────────────────────────
    {
        "name": "IMG → Email 1: You Ran the Numbers",
        "subject": "You ran the numbers. Most people never do.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}The calculator you just used took maybe four minutes to complete.{E}'
                f'{P}Most IMGs I\'ve spoken with — people who\'ve been on the pathway for 3, 5, '
                f'even 8 years — have never done what you just did: stopped and ran the actual math.{E}'
                f'{P}Not the dream math. Not the "if everything goes perfectly" math. The real '
                f'numbers: what you\'ve spent, what you\'ve earned, what\'s still ahead.{E}'
                f'{P}That takes a kind of honesty most people avoid. Not because they\'re afraid '
                f'to leave — but because looking at the numbers too clearly makes the decision '
                f'harder to delay.{E}'
            ),
            text_block(
                f'{P}I\'m Sahawat. I was an IMG.{E}'
                f'{P}I spent years on the treadmill before I finally stepped off — and I remember '
                f'exactly what it felt like to keep rerunning the math to make staying look '
                f'reasonable. To adjust the inputs. To find the version of the calculation '
                f'that gave permission to continue.{E}'
                f'{P}The calculator you just used doesn\'t do that. It gives you the honest '
                f'version. And if those numbers made you uncomfortable, that\'s useful — it '
                f'means they\'re doing their job.{E}'
            ),
            text_block(
                f'{P}Over the next two weeks, I\'m going to share the thinking that helped me '
                f'understand what I was actually dealing with — and the frameworks I\'ve built '
                f'for IMGs who are exactly where you are right now.{E}'
                f'{P}If you want a head start, here\'s the first resource: a structured '
                f'30-page decision framework for IMGs who\'ve run the math and need to know '
                f'what to do next.{E}'
            ),
            button_block("Should You Keep Going? — $17", GUIDE_URL),
            divider_block(),
            sign_off(),
        ]
    },

    # ── Email 2: Day 2 ───────────────────────────────────────────────────
    {
        "name": "IMG → Email 2: The 4 Costs",
        "subject": "The 4 costs no one added up when you started the pathway.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}When you started the pathway, someone told you the costs.{E}'
                f'{P}Maybe not all of them. But the financial ones — the exam fees, the prep '
                f'courses, the application cycle — those are visible. You could count them.{E}'
                f'{P}Here\'s what almost nobody counts: the compound cost of staying one more year.{E}'
            ),
            text_block(
                f'{P}If you\'ve spent $15,000 and four years, and the match rate for IMGs is '
                f'10–22%, another year doesn\'t just add to that total. It compounds across '
                f'four layers:{E}'
                f'{P}<strong>Financial</strong> — Another $5,000–$10,000 in exam fees, prep, '
                f'and living costs while not earning at your credential level. That money follows '
                f'the money you\'ve already spent into the same system.{E}'
                f'{P}<strong>Time</strong> — Another year isn\'t just 12 months. It\'s 12 months '
                f'of not building in the direction you might actually go. Sunk time is gone. '
                f'Only the next year is a choice.{E}'
                f'{P}<strong>Identity</strong> — The longer the pathway defines you, the harder '
                f'it becomes to imagine yourself outside of it. "I\'m an IMG trying to match" '
                f'becomes an identity. And identities are harder to step out of than decisions.{E}'
                f'{P}<strong>Immigration</strong> — For many IMGs, the pathway is entangled '
                f'with Express Entry calculations, provincial nomination scores, or work permit '
                f'timelines. The fear of "if I stop, I lose Canada" is the fourth layer — '
                f'and the hardest to untangle. (We\'ll address this directly later this week.){E}'
            ),
            text_block(
                f'{P}None of this means the answer is obvious. It means the cost structure '
                f'is larger than most people realize — and that the decision to stay deserves '
                f'the same rigour as the decision to pivot.{E}'
                f'{P}"Should You Keep Going?" walks through each layer with a structured '
                f'framework built specifically for this moment. Not inspiration. A decision tool.{E}'
            ),
            button_block("Get Should You Keep Going? — $17", GUIDE_URL),
            divider_block(),
            sign_off(),
        ]
    },

    # ── Email 3: Day 4 ───────────────────────────────────────────────────
    {
        "name": "IMG → Email 3: The System Failed You",
        "subject": "You didn't fail medicine. The system failed you.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}Let me give you a statistic that most people on the pathway have heard — '
                f'but few have let fully land:{E}'
                f'{P}97% of Canadian medical graduates who apply to residency match.{E}'
                f'{P}For IMGs, the number is 10–22%. In competitive specialties, it can be lower.{E}'
                f'{P}That\'s not a performance gap. It\'s a structural one.{E}'
            ),
            text_block(
                f'{P}The system was designed for Canadian-trained physicians. IMGs are eligible '
                f'to apply — but the match rate reflects institutional preference, not '
                f'individual ability. You didn\'t fail the pathway. The pathway wasn\'t '
                f'built for you.{E}'
                f'{P}I want to name something that gets in the way of hearing that clearly: '
                f'the identity lock.{E}'
                f'{P}After years of training — and often more years on the pathway — the '
                f'credential becomes more than a degree. "I AM a doctor" stops being a '
                f'description and becomes a self-concept. When staying on the pathway feels '
                f'like protecting that identity, it\'s no longer a career calculation. '
                f'It\'s a psychological one.{E}'
            ),
            text_block(
                f'{P}Here\'s what I found to be true on the other side: your MD is an asset, '
                f'not a limitation.{E}'
                f'{P}It\'s recognized and valued in clinical research, health policy, medical '
                f'education, pharmaceutical consulting, regulatory affairs, and medical writing '
                f'— roles that pay well, respect your background, and don\'t require you to '
                f'start over.{E}'
                f'{P}The identity doesn\'t disappear when you step off the treadmill. '
                f'It gets redeployed.{E}'
                f'{P}The IMG Identity Reset is five AI-guided prompts designed to help you '
                f'separate who you are from the credential you hold — so your next decision '
                f'comes from clarity, not from fear of erasure.{E}'
            ),
            button_block("Get the IMG Identity Reset — $27", IDENTITY_URL),
            divider_block(),
            sign_off(),
        ]
    },

    # ── Email 4: Day 6 ───────────────────────────────────────────────────
    {
        "name": "IMG → Email 4: The Immigration Fear",
        "subject": "The immigration fear everyone ignores — and how to answer it.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}Of the four sunk cost layers I outlined earlier, one gets almost no '
                f'attention in the IMG community:{E}'
                f'{P}<em>The immigration fear.</em>{E}'
                f'{P}"If I stop pursuing residency, I might lose my status in Canada."{E}'
                f'{P}For IMGs on work permits, PGWP, or in the middle of Express Entry '
                f'calculations, this fear isn\'t abstract. It\'s a real constraint that shapes '
                f'every decision — often more than the financial and time costs combined.{E}'
            ),
            text_block(
                f'{P}Here\'s what most people don\'t know: the pathway isn\'t required to '
                f'maintain immigration eligibility.{E}'
                f'{P}Canada\'s Express Entry system assigns CRS points for job offer, education, '
                f'language, and work experience. An MD degree — regardless of whether it leads '
                f'to licensure — is evaluated at a high educational level. And many non-clinical '
                f'roles open to IMGs fall under NOC codes that directly build Express Entry '
                f'points: healthcare administration, health policy, research coordination, '
                f'pharmaceutical consulting.{E}'
                f'{P}The question isn\'t "do I stay on the treadmill or lose Canada." '
                f'The question is: what path builds the strongest immigration case and '
                f'the strongest life? Those are not always the same path.{E}'
            ),
            text_block(
                f'{P}The IMG Career Map lists 12 non-clinical roles with Canadian income data, '
                f'NOC codes, required credentials, and Express Entry implications. It was built '
                f'specifically to answer the immigration question — not with generic advice, '
                f'but with the specific numbers that matter for your file.{E}'
            ),
            button_block("Get the IMG Career Map — $37", MAP_URL),
            divider_block(),
            sign_off(),
        ]
    },

    # ── Email 5: Day 8 ───────────────────────────────────────────────────
    {
        "name": "IMG → Email 5: Income in 30 Days",
        "subject": "Income in 30 days. Without hiding your medical degree.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}Every decision on the pathway — stay, pivot, wait — eventually comes '
                f'back to money.{E}'
                f'{P}Not because money is the most important thing. But because financial '
                f'fear is the lock that holds every other fear in place.{E}'
                f'{P}When income is precarious, the identity questions feel academic. '
                f'The immigration calculations feel urgent. And another year on the treadmill, '
                f'with its familiar (if uncertain) financial logic, starts to look reasonable.{E}'
            ),
            text_block(
                f'{P}Here\'s what most IMGs don\'t see until they\'re through the crossing: '
                f'the income problem is solvable faster than the pathway problem.{E}'
                f'{P}The MCCQE cycle takes years. The CaRMS match happens once a year. But '
                f'non-clinical roles — consulting, research coordination, health policy, '
                f'medical writing, pharmaceutical liaison — these can be accessed in 30 days '
                f'with an MD and the right positioning.{E}'
                f'{P}Not at a physician\'s salary. Not at first. But enough to change the math. '
                f'Enough to make the next year a real choice instead of a financial necessity.{E}'
            ),
            text_block(
                f'{P}The IMG Survival Playbook is a 30-day income plan for IMGs stepping off '
                f'the pathway: which roles to target first, how to position your medical '
                f'background as an asset (not a liability), what to say when asked why you '
                f'left the pathway, and how to build toward sustainable non-clinical income.{E}'
            ),
            button_block("Get the IMG Survival Playbook — $47", PLAYBOOK_URL),
            divider_block(),
            sign_off(
                ps="If you\'ve been going through this week\'s emails and haven\'t picked up "
                   "any of the guides yet — start here. The income problem is the one that "
                   "makes every other decision possible."
            ),
        ]
    },

    # ── Email 6: Day 11 ──────────────────────────────────────────────────
    {
        "name": "IMG → Email 6: Stop Navigating Alone",
        "subject": "What changes when you stop navigating this alone.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}Over the last week, I\'ve shared the four cost layers, the identity lock, '
                f'the immigration math, and the income path.{E}'
                f'{P}Most of the IMGs I hear from have done some version of this thinking on '
                f'their own. They\'ve Googled the match rates. They\'ve read the NOC code lists. '
                f'They\'ve downloaded guides. They\'ve had late-night conversations in IMG '
                f'Facebook groups and Reddit threads.{E}'
                f'{P}And then they\'ve woken up the next morning and gone back to the prep '
                f'schedule.{E}'
            ),
            text_block(
                f'{P}Not because the information wasn\'t useful. But because information, on '
                f'its own, doesn\'t interrupt the momentum of a pathway you\'ve been on for '
                f'years.{E}'
                f'{P}What interrupts it is being seen clearly — by someone who\'s been through '
                f'it — and being walked through the specific version of this crossing that\'s '
                f'yours.{E}'
                f'{P}Your immigration status is different from someone else\'s. Your financial '
                f'picture is different. Your specialty background opens different doors. '
                f'The 4-layer trap looks different depending on how long you\'ve been on the '
                f'treadmill and what you\'ve already tried.{E}'
                f'{P}Generic frameworks can get you oriented. They can\'t get you to the '
                f'other side.{E}'
            ),
            text_block(
                f'{P}I work directly with a small number of IMGs at a time. Not to convince '
                f'anyone to leave the pathway. Not to add another voice to the pile of opinions.{E}'
                f'{P}But to build a clear picture of what your next chapter actually looks like '
                f'— the income structure, the identity bridge, the immigration calculus — so '
                f'the decision, whatever it is, comes from clarity rather than exhaustion.{E}'
                f'{P}Tomorrow I\'ll tell you exactly what that looks like.{E}'
            ),
            divider_block(),
            sign_off(),
        ]
    },

    # ── Email 7: Day 14 ──────────────────────────────────────────────────
    {
        "name": "IMG → Email 7: 3 Spots Open",
        "subject": "I have 3 spots open. Here's what we do together.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}Here\'s what 1:1 coaching with me looks like.{E}'
                f'{P}We meet over four sessions across four weeks. Before we start, you '
                f'complete a brief intake covering your pathway history, finances, immigration '
                f'status, and what\'s keeping you stuck.{E}'
            ),
            text_block(
                f'{P}<strong>Session 1 — The real picture.</strong><br>'
                f'We map your actual costs across all four layers. We look at what you\'ve '
                f'spent, what you\'ve earned, and what the next year realistically looks like '
                f'if nothing changes. No softening. No optimism bias. Just the numbers.{E}'
                f'{P}<strong>Session 2 — The identity question.</strong><br>'
                f'Who you are without the credential. What you\'re actually building toward. '
                f'What "success" looks like when you\'re no longer defining it by a '
                f'match rate.{E}'
                f'{P}<strong>Session 3 — The bridge.</strong><br>'
                f'The specific non-clinical roles that fit your background, your income needs, '
                f'and your immigration file. The 30-60-90 day plan. Concrete, not aspirational.{E}'
                f'{P}<strong>Session 4 — The friction.</strong><br>'
                f'The conversations you\'ll have to have. The moment you\'ll want to go back — '
                f'and how to not. The version of this story you\'ll tell, and to whom.{E}'
            ),
            text_block(
                f'{P}This is not a course, a group program, or an accountability check-in. '
                f'It\'s direct, focused work on your specific situation.{E}'
                f'{P}I work with 3 IMGs at a time. When those spots fill, the waitlist is '
                f'the only option.{E}'
                f'{P}If this is the right next step for you, book a 30-minute discovery call. '
                f'We\'ll talk through where you are and whether working together makes sense. '
                f'The call is free. It costs you nothing except the honesty of showing up to it.{E}'
            ),
            button_block("Book a 30-min discovery call", COACHING_URL, bg_color="#1A1917"),
            divider_block(),
            sign_off(),
        ]
    },
]

# ─────────────────────────────────────────────
# Create emails via Encharge API
# ─────────────────────────────────────────────

def create_email(email_def):
    state = build_state(email_def["contents"])
    payload = {
        "name":    email_def["name"],
        "subject": email_def["subject"],
        "fromEmail": FROM_EMAIL,
        "fromName":  FROM_NAME,
        "type":    "HTML",
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

    print("Creating IMG Calculator email sequence...\n")
    created = []

    for i, email_def in enumerate(EMAILS, 1):
        print(f"  [{i}/7] {email_def['name']}...")
        eid = create_email(email_def)
        created.append({
            "index": i,
            "id": eid,
            "name": email_def["name"],
            "subject": email_def["subject"]
        })
        print(f"         ✓ Created — ID: {eid}")

    print("\n✓ All 7 emails created.\n")
    print("Email IDs:")
    delays = ["Immediately", "Day 2", "Day 4", "Day 6", "Day 8", "Day 11", "Day 14"]
    for e in created:
        print(f"  Email {e['index']} ({delays[e['index']-1]}): ID {e['id']}  —  {e['subject']}")

    out_file = "img_email_ids.json"
    with open(out_file, "w") as f:
        json.dump(created, f, indent=2)
    print(f"\nIDs saved to {out_file}")

    print("\n" + "="*60)
    print("NEXT STEP: Set up the Encharge flow manually")
    print("="*60)
    print("\n  1. Encharge → Flows → New Flow")
    print("  2. Trigger: Tag Added = 'img-calculator-optin'")
    print("  3. Add a Send Email step for each email with the delay below:")
    print()
    for e in created:
        print(f"     {delays[e['index']-1]:12s}  →  Email ID {e['id']}")
    print()
    print("  4. Activate the flow.")
    print()
    print("NOTE: The existing single-email flow (IDs 442604/442605) handles the")
    print("immediate result delivery split on immigrationStatus. This new sequence")
    print("runs in parallel — both flows fire from the same tag. No changes needed")
    print("to the existing flow.")


if __name__ == "__main__":
    main()
