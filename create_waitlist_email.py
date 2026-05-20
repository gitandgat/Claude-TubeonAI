"""
Create Workshop Waitlist Confirmation Email
============================================
Creates 1 email in Encharge for people who join the workshop waitlist via /waitlist.

Trigger: tag 'workshop-waitlist' (applied by api/waitlist.ts)
Goal:    Confirm their spot on the waitlist + guide toward Fear Audit & $27 guide
Timing:  Immediate

Run:
  python create_waitlist_email.py
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
            "u_row": 3, "u_column": 3, "u_content_text": 6,
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

EMAIL = {
    "name": "Workshop Waitlist: You're on the list.",
    "subject": "You're on the waitlist. (Here's what happens next.)",
    "contents": [
        text_block(
            f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
            f'{P}You\'re on the waitlist for <strong>Use AI to Plan Your Next Chapter</strong> — '
            f'the 90-minute live workshop where we build your personalized career transition '
            f'plan using AI.{E}'
            f'{P}When the next session opens, you\'ll be the first to know — and the first '
            f'to get early access pricing ($97 vs. $197 at the door).{E}'
            f'{P}Sessions run monthly. I\'ll reach out personally when the next date is set.{E}'
        ),
        text_block(
            f'{P}<strong>While you wait, two things that will make the workshop more valuable:</strong>{E}'
            f'{P}<strong>1. Take the Fear Audit (free, 2 min).</strong><br>'
            f'The workshop works best when you already know which fear is running your '
            f'transition — Financial Insecurity, Fear of Judgment, or Identity Loss. '
            f'Most people guess wrong. The quiz tells you the truth.{E}'
            f'{P}<strong>2. Get The Courage to Choose ($27).</strong><br>'
            f'The PDF guide + AI prompt pack that walks you from naming your fear to '
            f'building a concrete plan. It\'s the pre-work that makes 90 minutes feel '
            f'like 6 months of clarity.{E}'
        ),
        button_block("Take the Fear Audit (free)", FEAR_AUDIT_URL),
        button_block("Get The Courage to Choose ($27)", GUMROAD_URL, style="secondary"),
        text_block(
            f'{P}If you have questions about the workshop — what we cover, whether it\'s '
            f'right for you, whether it works for your specific situation — just reply '
            f'to this email. I read every reply.{E}'
        ),
        divider_block(),
        sign_off(),
    ]
}

# ─────────────────────────────────────────────
# Create email via Encharge API
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
    print("Creating workshop waitlist confirmation email...\n")
    create_email(EMAIL)
    print("\nDone.")
