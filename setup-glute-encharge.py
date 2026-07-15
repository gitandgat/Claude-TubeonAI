#!/usr/bin/env python3
"""
Set up the Glute Longevity application nurture emails in Encharge.

Uses the sanctioned crosswalk-encharge-email helper for API-correctness
(richtext STRING state + populated `html` send field + subject + verify),
but OVERRIDES the branding to Glute Longevity (not Crosswalk Wisdom).

Creates 3 emails for the tag-triggered flow (trigger tag: glute-longevity-applicant):
  1. Application received + 2-min intro video  (immediate)
  2. Enrollment details / next steps           (~24h, reply-to CTA)
  3. Soft last-call + guarantee                 (~48-72h, reply-to CTA)

The flow itself is built in the Encharge UI (no flow API). See the printed recipe.
"""
import sys
from dotenv import load_dotenv
load_dotenv("/Users/toto/Claude TubeonAI/.env")
sys.path.insert(0, "/Users/toto/.claude/skills/crosswalk-encharge-email")
import encharge_email as ee

# ── Glute Longevity branding overrides (legible on light background) ──────────
ee.ACCENT = "#00A699"  # teal from the landing palette
ee._P_OPEN = ('<p style="font-family: Arial, Helvetica, sans-serif; font-size: 16px; '
              'line-height: 175%; color: #1A1917;">')

def _glute_header() -> str:
    return (
        '<p style="text-align:center;padding:8px 0 4px;font-family:Arial,Helvetica,sans-serif;'
        'font-size:20px;font-weight:800;letter-spacing:1.5px;color:#0d0d1a;">'
        'GLUTE <span style="color:#00A699;">LONGEVITY</span></p>'
        '<hr style="border:none;border-top:2px solid #00A699;width:60px;margin:0 auto 18px;">'
    )

def _glute_footer() -> str:
    return (
        '<hr style="border:none;border-top:1px solid #e5e7eb;margin:28px 0 18px;">'
        '<p style="font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#1A1917;">'
        '&mdash; Sahawat<br><span style="color:#6b7280;">Glute Longevity</span></p>'
        '<p style="text-align:center;font-size:13px;line-height:160%;color:#9ca3af;'
        'font-family:Arial,Helvetica,sans-serif;">'
        'glutelongevity.com<br><br>'
        'Glute Longevity<br>{{account.mailingAddress}}<br>'
        '{{person.unsubscribeLink}} &nbsp; {{person.managePreferencesLink}}</p>'
    )

def _glute_wrap(inner: str) -> str:
    return (
        '<!DOCTYPE html><html><body style="margin:0;padding:0;background:#f3f4f6;">'
        '<table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6;padding:32px 0;">'
        '<tr><td align="center">'
        '<table width="600" cellpadding="0" cellspacing="0" '
        'style="background:#ffffff;border-radius:12px;border:1px solid #e5e7eb;">'
        '<tr><td style="padding:28px 40px;">'
        f"{inner}"
        "</td></tr></table></td></tr></table></body></html>"
    )

ee._header = _glute_header
ee._footer = _glute_footer
ee.wrap_html = _glute_wrap

FROM_EMAIL = "sahawat@crosswalkwisdom.com"   # verified domain (SPF/DKIM) — deliverable immediately
FROM_NAME = "Sahawat, Glute Longevity"        # display name keeps the Glute brand

p, link, button = ee.p, ee.link, ee.button
HI = "Hi {{ person.firstName | default: 'there' }},"
VIDEO_LINK = "https://youtu.be/pvKWD6O2_mY"   # Glute Longevity intro v2 (AI b-roll + VoiSpark voice, YouTube, unlisted)

# ── Email 1 — Application received + intro video (immediate) ──────────────────
body1 = (
    p(HI)
    + p("Got your application for the Glute Longevity 6-Week Protocol &mdash; thanks for raising your hand.")
    + p("Quick bit about me: I&rsquo;m a former physician. I built this protocol because I got tired of "
        "watching capable people accept decline as inevitable &mdash; and because the usual "
        "&ldquo;glute work&rdquo; never rebuilds the strength that actually matters as you age.")
    + p("Before anything else, watch the 2-minute intro. It shows exactly how the protocol rebuilds "
        "glute strength and posture, and why most &ldquo;glute work&rdquo; quietly fails.")
    + button(VIDEO_LINK, "Watch the 2-min intro")
    + p("<strong>What happens next:</strong> I personally review every application within 24 hours, "
        "then send your personalized next steps and enrollment details.")
    + p("One thing that helps me prep for you: just hit reply and tell me the single biggest frustration "
        "with your glutes or hips right now &mdash; weakness, posture, a nagging ache, a plateau, whatever "
        "it is. I read every reply.")
    + p("Talk soon,")
)

# ── Email 2 — Enrollment details / next steps (~24h, reply CTA) ───────────────
body2 = (
    p(HI)
    + p("I reviewed your application &mdash; you&rsquo;re a fit for the Founding Member group.")
    + p("Quick recap of what&rsquo;s inside the 6-Week Protocol:")
    + ('<ul style="font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:175%;color:#1A1917;">'
       "<li>6 video training modules, built to progress week by week</li>"
       "<li>A simple weekly plan you can actually keep up with</li>"
       "<li>Lifetime access &mdash; revisit it any time</li>"
       "<li>Money-back guarantee: complete the protocol as designed and if your glute strength, "
       "posture, or comfort don&rsquo;t improve, I refund you in full</li>"
       "</ul>")
    + p("<strong>Two ways in (one-time payment, lifetime access):</strong>")
    + ('<ul style="font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:175%;color:#1A1917;">'
       "<li><strong>Founding Member</strong> &mdash; $297</li>"
       "<li><strong>Founding Member + Longevity Lift App</strong> &mdash; $497</li>"
       "</ul>")
    + p("Founding spots are limited to keep the group small. To claim yours, just reply "
        "<strong>&ldquo;I&rsquo;m in&rdquo;</strong> (or with any questions) and I&rsquo;ll send your "
        "secure enrollment link and get you started.")
    + p("Talk soon,")
)

# ── Email 3 — Soft last call + guarantee (~48-72h, reply CTA) ─────────────────
body3 = (
    p(HI)
    + p("I didn&rsquo;t hear back, so I&rsquo;ll keep this short.")
    + p("Most people who apply and then stall aren&rsquo;t unsure about the program &mdash; they&rsquo;re "
        "unsure it&rsquo;ll work for <em>their</em> body. That&rsquo;s the whole reason there&rsquo;s a "
        "guarantee: do the six weeks as designed, and if your glute strength, posture, or comfort "
        "don&rsquo;t improve, I refund you in full. The risk is on me, not you.")
    + p("If there&rsquo;s a question holding you back, hit reply &mdash; I answer personally. "
        "If the timing&rsquo;s just not right, no problem; reply <strong>&ldquo;not now&rdquo;</strong> "
        "and I&rsquo;ll close your file so I stop emailing you.")
    + p("Either way, I appreciate you applying.")
)

EMAILS = [
    ("Glute Longevity — 1 Application Received + Intro",
     "Your Glute Longevity application — watch this first (2 min)", body1),
    ("Glute Longevity — 2 Enrollment Details",
     "Your Glute Longevity next steps (Founding Member)", body2),
    ("Glute Longevity — 3 Last Call + Guarantee",
     "A quick question about your glutes", body3),
]

# Existing email IDs (created Jun 21 2026) — update in place, do NOT create duplicates.
EMAIL_IDS = [464212, 464213, 464214]

if __name__ == "__main__":
    if not ee.API_KEY:
        raise SystemExit("ENCHARGE_API_KEY not loaded from .env")
    results = []
    for eid, (name, subject, body) in zip(EMAIL_IDS, EMAILS):
        summary = ee.update_email(eid, subject, body)
        results.append((name, summary))
        print(f"UPDATED #{eid}: {name}")
        print(f"   verify -> {summary}")
    print("\nALL UPDATED + VERIFIED:")
    for name, s in results:
        print(f"  #{s['id']}  {name}  (subject set, html {s['html_chars']} chars, editor={s['editor']})")
