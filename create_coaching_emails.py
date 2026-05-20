"""
Create Coaching Application Emails
=====================================
Creates 2 emails in Encharge:
  1. Applicant confirmation (tag: coaching-applicant) → sent to applicant
  2. Sahawat notification (tag: notify-new-application) → sent to sahawat@crosswalkwisdom.com

Trigger: Both tags applied by api/apply.ts on form submit.

Run:
  python create_coaching_emails.py
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
            "u_row": 3, "u_column": 3, "u_content_text": 6,
            "u_content_image": 1, "u_content_button": 1,
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
    # ── Email 1: Applicant confirmation ──────────────────────────────────
    {
        "name": "Coaching Application: Received.",
        "subject": "Your application is in my hands.",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}I have your application. Thank you for writing it — and for being honest.{E}'
                f'{P}I read every application personally. No assistant, no filter, no scoring system. '
                f'Just me, reading what you wrote, thinking about whether I can actually help you.{E}'
                f'{P}You\'ll hear back from me within 48 hours — from this email address, '
                f'sahawat@crosswalkwisdom.com. Either an invitation to a discovery call, '
                f'or honest feedback about fit if the timing isn\'t right.{E}'
            ),
            text_block(
                f'{P}<strong>What happens next:</strong>{E}'
                f'{P}<strong>01 — I review your application.</strong><br>'
                f'I read every word. I\'m looking for one thing: whether I can genuinely help '
                f'you move forward, not just validate that you\'re burned out.{E}'
                f'{P}<strong>02 — You get a personal reply within 48 hours.</strong><br>'
                f'Either a discovery call invitation or honest feedback on fit. '
                f'If it\'s not the right moment, I\'ll tell you what would make it the right moment.{E}'
                f'{P}<strong>03 — Discovery call — no pressure.</strong><br>'
                f'30 minutes to talk through your situation and see if The Crosswalk Program '
                f'is the right move. You ask questions. I ask questions. We decide together.{E}'
            ),
            text_block(
                f'{P}In the meantime: if you haven\'t taken the Fear Audit, do it now. '
                f'It will make our discovery call significantly more useful — we\'ll both '
                f'know exactly which fear is running your transition.{E}'
                f'{P}It takes 2 minutes and it\'s free.{E}'
            ),
            divider_block(),
            sign_off(),
        ]
    },

    # ── Email 2: Sahawat notification ────────────────────────────────────
    {
        "name": "INTERNAL: New Coaching Application",
        "subject": "New application: {{ person.notifyApplicantName }} ({{ person.notifyApplicantProfession }})",
        "contents": [
            text_block(
                f'{P}<strong>New coaching application received.</strong>{E}'
                f'{P}<strong>Name:</strong> {{{{ person.notifyApplicantName }}}}<br>'
                f'<strong>Email:</strong> {{{{ person.notifyApplicantEmail }}}}<br>'
                f'<strong>Profession:</strong> {{{{ person.notifyApplicantProfession }}}}<br>'
                f'<strong>Ready to invest:</strong> {{{{ person.notifyApplicantReadyToInvest }}}}{E}'
            ),
            text_block(
                f'{P}Reply within 48 hours — either a discovery call invite or honest feedback on fit.{E}'
                f'{P}Full application details are in Encharge under the applicant\'s profile.{E}'
            ),
            divider_block(),
            text_block(
                f'{P}<span style="color: #888888; font-size: 14px;">This is an internal notification. '
                f'Do not reply to the applicant from this email — use their email address above.</span>{E}'
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
        "name": email_def["name"],
        "subject": email_def["subject"],
        "fromEmail": FROM_EMAIL,
        "fromName": FROM_NAME,
        "replyTo": FROM_EMAIL,
        "accountId": ACCOUNT_ID,
        "communicationCategoryId": COMMUNICATION_CAT_ID,
        "editorType": "unlayer",
        "state": state,
    }
    r = requests.post(f"{BASE}/emails", headers=HEADERS, json=payload)
    if r.status_code in (200, 201):
        data = r.json()
        email_id = data.get("id") or data.get("email", {}).get("id") or "?"
        print(f"  ✓ Created: '{email_def['name']}' → ID {email_id}")
        return email_id
    else:
        print(f"  ✗ Failed: '{email_def['name']}' → {r.status_code}: {r.text[:200]}")
        return None

if __name__ == "__main__":
    print("Creating coaching application emails...\n")
    ids = []
    for email_def in EMAILS:
        email_id = create_email(email_def)
        ids.append(email_id)
    print(f"\nDone. Email IDs: {ids}")
    print("\nNext steps in Encharge:")
    print("  1. Create flow triggered by tag 'coaching-applicant'")
    print(f"     → Send email ID {ids[0]} immediately")
    print("  2. Create flow triggered by tag 'notify-new-application'")
    print(f"     → Send email ID {ids[1]} immediately to sahawat@crosswalkwisdom.com")
