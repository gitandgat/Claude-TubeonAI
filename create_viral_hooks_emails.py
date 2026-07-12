"""
Create Viral Hooks Launch Email Sequence
=========================================
Creates 3 emails in Encharge for the Viral Hooks founding-member launch.

Trigger: manual send / one-off campaign to the full list
Goal:    Drive sign-ups to the $9/mo Viral Hooks Gumroad membership
Timing:  Day 1 -> Day 4 -> Day 7

Run:
  python create_viral_hooks_emails.py
"""

import os, uuid, json, requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ENCHARGE_API_KEY")
BASE    = "https://api.encharge.io/v1"
HEADERS = {"X-Encharge-Token": API_KEY, "Content-Type": "application/json"}

COMMUNICATION_CAT_ID = 289738
FROM_EMAIL = "sahawat@crosswalkwisdom.com"
FROM_NAME  = "Sahawat at Crosswalk Wisdom"
GUMROAD_URL = "https://sahawat.gumroad.com/l/viral-hooks"
LOGO_URL = "https://d231yrez0cpae9.cloudfront.net/1750037512272-Crosswalk%20wisdom%20logo%20white%20BG.png"

# ─────────────────────────────────────────────
# Unlayer building blocks (same as create_welcome_emails.py)
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
    # ── Email 1 — Day 1: The Story ──────────────────────────────────────
    {
        "name": "Viral Hooks 1: I built this for myself first",
        "subject": "I built this for myself first",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}I used to stare at a blank caption box for two hours.{E}'
                f'{P}Not because I had nothing to say. Because I had too much — and no '
                f'idea which opening line would make someone stop scrolling.{E}'
                f'{P}So I did what I always do when I\'m stuck. I built a system.{E}'
            ),
            text_block(
                f'{P}It studies the hooks that actually work — the patterns behind '
                f'creators like Dan Koe and HealthyGamerGG — and rewrites them in my '
                f'voice. Not robot voice. Mine. The former-physician-in-a-yellow-vest voice.{E}'
                f'{P}Two hours became fifteen minutes. Five hooks, ready to post, every '
                f'morning.{E}'
            ),
            text_block(
                f'{P}I\'ve been using it quietly for my own content. A few people asked '
                f'what changed. This is what changed.{E}'
                f'{P}Next week I\'m opening it up to a small founding group. If you write '
                f'content for a living — or want to — keep an eye on your inbox.{E}'
            ),
            divider_block(),
            sign_off(),
        ]
    },

    # ── Email 2 — Day 4: The Demo + Offer ───────────────────────────────
    {
        "name": "Viral Hooks 2: Watch it write 5 hooks in 60 seconds",
        "subject": "Watch it write 5 hooks in 60 seconds",
        "contents": [
            text_block(
                f'{P}Hey {{{{ person.firstName | default: "there" }}}},{E}'
                f'{P}Last week I told you about the tool I built to fix my two-hour '
                f'caption problem.{E}'
                f'{P}Here\'s how it works:{E}'
                f'{P}You type a topic. "Leaving a career everyone admires." It finds '
                f'five hook patterns proven to work in the wellness and career space — '
                f'then rewrites each one in your voice. Warm. Specific. Human.{E}'
            ),
            text_block(
                f'{P}One real example it wrote for me:{E}'
                f'{P}<em>"Everyone tells you to follow your passion. Nobody tells you '
                f'what to do when that passion was your prison."</em>{E}'
                f'{P}That\'s a usable hook. In seconds.{E}'
            ),
            text_block(
                f'{P}I\'m opening 20 founding spots at $9/month — locked in for life. '
                f'Sign up, and you\'ll get an access code by email within a minute.{E}'
            ),
            button_block("Get Founding Access — $9/mo", GUMROAD_URL),
            divider_block(),
            sign_off(),
        ]
    },

    # ── Email 3 — Day 7: Last Call ───────────────────────────────────────
    {
        "name": "Viral Hooks 3: Founding spots close tonight",
        "subject": "Founding spots close tonight",
        "contents": [
            text_block(
                f'{P}Quick one.{E}'
                f'{P}Founding access to the hook tool closes tonight at midnight.{E}'
                f'{P}After that, the price goes up — and the founding rate never '
                f'comes back.{E}'
                f'{P}If you\'ve been meaning to fix the blank-caption-box problem, this '
                f'is the cheapest it will ever be.{E}'
            ),
            button_block("Grab the Last Founding Spot — $9/mo", GUMROAD_URL),
            text_block(
                f'{P}If it\'s not for you, no hard feelings. The Tuesday emails keep '
                f'coming either way.{E}'
            ),
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

    print("Creating Viral Hooks launch email sequence...\n")
    created = []

    for i, email_def in enumerate(EMAILS, 1):
        print(f"  [{i}/3] {email_def['name']}...")
        eid = create_email(email_def)
        created.append({
            "index": i, "id": eid,
            "name": email_def["name"],
            "subject": email_def["subject"]
        })
        print(f"         Created - ID: {eid}")

    print("\nAll 3 emails created as drafts.\n")
    print("Email IDs:")
    for e in created:
        print(f"  Email {e['index']}: ID {e['id']}  -  {e['subject']}")

    out_file = "viral_hooks_email_ids.json"
    with open(out_file, "w") as f:
        json.dump(created, f, indent=2)
    print(f"\nIDs saved to {out_file}")

    print("\n" + "="*60)
    print("NEXT STEP - Review and send manually in Encharge:")
    print("="*60)
    timings = ["Day 1", "Day 4", "Day 7"]
    for e in created:
        print(f"  {timings[e['index']-1]:6s} -> Email ID {e['id']}  -  {e['subject']}")
    print("\n  Go to Encharge -> Emails, review each draft, then send")
    print("  as a one-off campaign to your full list on the days above.\n")


if __name__ == "__main__":
    main()
