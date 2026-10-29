"""
Fix the 3 Viral Hooks launch emails (461900/461901/461902).

They were created with an Unlayer dict state, which doesn't persist via API
(shows an empty email, no subject). Per project memory
(feedback_encharge_editor_state): API emails must use editor type "richtext"
with a plain HTML string state. This PATCHes each with richtext + re-affirms
the subject.

Run: python3 fix_viral_hooks_emails_richtext.py
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["ENCHARGE_API_KEY"]
BASE = "https://api.encharge.io/v1"
HEADERS = {"X-Encharge-Token": API_KEY, "Content-Type": "application/json"}

LOGO_URL = "https://d231yrez0cpae9.cloudfront.net/1750037512272-Crosswalk%20wisdom%20logo%20white%20BG.png"
GUMROAD = "https://sahawat.gumroad.com/l/viral-hooks"

GREETING = 'Hey {{ person.firstName | default: "there" }},'
P = '<p style="font-family: Georgia, serif; font-size: 16px; line-height: 180%; color: #1A1917;">'
E = "</p>"


def link(url: str, text: str) -> str:
    return f'<a href="{url}" target="_blank" style="color: #2C5F4A;">{text}</a>'


def button(url: str, label: str) -> str:
    return (
        '<p style="text-align: center; margin: 28px 0;">'
        f'<a href="{url}" target="_blank" style="background: #2C5F4A; color: #ffffff; '
        'font-family: Georgia, serif; font-size: 16px; font-weight: bold; padding: 14px 30px; '
        f'border-radius: 6px; text-decoration: none; display: inline-block;">{label}</a></p>'
    )


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
    f"{P}I used to stare at a blank caption box for two hours.{E}"
    f"{P}Not because I had nothing to say. Because I had too much &mdash; and no idea "
    f"which opening line would make someone stop scrolling.{E}"
    f"{P}So I did what I always do when I'm stuck. I built a system.{E}"
    f"{P}It studies the hooks that actually work &mdash; the patterns behind creators like "
    f"Dan Koe and HealthyGamerGG &mdash; and rewrites them in my voice. Not robot voice. "
    f"Mine. The former-physician-in-a-yellow-vest voice.{E}"
    f"{P}Two hours became fifteen minutes. Five hooks, ready to post, every morning.{E}"
    f"{P}I've been using it quietly for my own content. A few people asked what changed. "
    f"This is what changed.{E}"
    f"{P}Later this week I'm opening it up to a small founding group. If you write content "
    f"for a living &mdash; or want to &mdash; keep an eye on your inbox.{E}"
)

EMAIL_2_BODY = (
    f"{P}{GREETING}{E}"
    f"{P}Last week I told you about the tool I built to fix my two-hour caption problem.{E}"
    f"{P}Here's how it works:{E}"
    f"{P}You type a topic &mdash; say, “leaving a career everyone admires.” It finds five "
    f"hook patterns proven to stop the scroll, then rewrites each one in your voice. "
    f"Warm. Specific. Human.{E}"
    f"{P}One it actually wrote for me:{E}"
    f"{P}<em>“Everyone tells you to follow your passion. Nobody tells you what to do "
    f"when that passion was your prison.”</em>{E}"
    f"{P}That's a usable hook. In seconds.{E}"
    f"{P}I'm opening 20 founding spots at <strong>$9/month &mdash; locked in for life</strong>. "
    f"Sign up and you'll get an access code by email within a minute.{E}"
    + button(GUMROAD, "Get Founding Access &mdash; $9/mo")
)

EMAIL_3_BODY = (
    f"{P}Quick one.{E}"
    f"{P}Founding access to the hook tool closes tonight at midnight.{E}"
    f"{P}After that, the price goes up &mdash; and the founding rate never comes back.{E}"
    f"{P}If you've been meaning to fix the blank-caption-box problem, this is the cheapest "
    f"it will ever be.{E}"
    + button(GUMROAD, "Grab the Last Founding Spot &mdash; $9/mo")
    + f"{P}If it's not for you, no hard feelings. The emails keep coming either way.{E}"
)

EMAILS = {
    461900: ("I built this for myself first", EMAIL_1_BODY),
    461901: ("Watch it write 5 hooks in 60 seconds", EMAIL_2_BODY),
    461902: ("Founding spots close tonight", EMAIL_3_BODY),
}


def wrap_html(inner: str) -> str:
    """Full send-ready HTML document — the `html` field is what Encharge SENDS."""
    return (
        '<!DOCTYPE html><html><body style="margin:0;padding:0;background:#f8f4ee;">'
        '<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f4ee;padding:32px 0;">'
        '<tr><td align="center">'
        '<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:10px;">'
        '<tr><td style="padding:24px 40px;">'
        f"{inner}"
        "</td></tr></table></td></tr></table></body></html>"
    )


def fix_email(email_id: int, subject: str, body_html: str) -> None:
    state = HEADER + body_html + FOOTER
    html = wrap_html(state)
    # Patch BOTH: editor.state (re-render path) AND html (the field Encharge
    # actually SENDS). Nested editor object + richtext string is the shape the
    # API honours; top-level editorType/state are silently ignored.
    payload = {
        "subject": subject,
        "type": "HTML",
        "html": html,
        "editor": {"type": "richtext", "state": state},
    }
    r = requests.patch(f"{BASE}/emails/{email_id}", headers=HEADERS, json=payload, timeout=30)
    if r.status_code not in (200, 201):
        r = requests.put(f"{BASE}/emails/{email_id}", headers=HEADERS, json=payload, timeout=30)
    ok = r.status_code in (200, 201)
    print(f"  {email_id}: HTTP {r.status_code}" + ("" if ok else f"  {r.text[:160]}"))


if __name__ == "__main__":
    print("Rebuilding Viral Hooks emails as richtext...\n")
    for eid, (subj, body) in EMAILS.items():
        fix_email(eid, subj, body)
    print("\nDone — refresh Encharge and re-open the emails.")
