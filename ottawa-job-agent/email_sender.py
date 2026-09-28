"""Email sender: application emails from Outlook + digest to Gmail."""

import html
import imaplib
import os
import re
import smtplib
import time
from datetime import date, datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from agent_config import has_sent_digest_today, mark_digest_sent

NOTIFY_TO = "totomakus@gmail.com"
NOTIFY_FROM = "totomakus@gmail.com"
APPLY_FROM = "Sahawat.nil@outlook.com"

# Crosswalk Wisdom brand palette — reused from crosswalk-remotion/src/theme.ts
BRAND_AMBER = "#D4A843"
BRAND_CHARCOAL = "#2C2C2C"
BRAND_TEAL = "#5B9A8B"
BRAND_WARM_WHITE = "#FAF7F2"


def _fmt_deadline(job: dict) -> str:
    """Format the deadline informatively. Never shows expired (already filtered)."""
    deadline = job.get("deadline")
    if not deadline:
        return "not stated on the posting"
    m = re.search(r"\d{4}-\d{2}-\d{2}", str(deadline))
    if not m:
        return str(deadline)
    try:
        dl = datetime.strptime(m.group(), "%Y-%m-%d").date()
        days = (dl - date.today()).days
        return f"{m.group()}  (closes in {days} day{'s' if days != 1 else ''})"
    except ValueError:
        return str(deadline)


SMTP_TIMEOUT_SEC = 30


def _gmail_smtp():
    s = smtplib.SMTP("smtp.gmail.com", 587, timeout=SMTP_TIMEOUT_SEC)
    s.starttls()
    s.login(NOTIFY_FROM, os.environ["GMAIL_APP_PASSWORD"])
    return s


def _safe_filename(name: str) -> str:
    """Strip characters that would break a Content-Disposition filename."""
    cleaned = re.sub(r'[\\/*?:"<>|\r\n]', "", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:150] or "file"


def _attach_file(msg: MIMEMultipart, file_path: str, filename: str = None):
    if not file_path or not Path(file_path).exists():
        return
    with open(file_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    name = _safe_filename(filename) if filename else Path(file_path).name
    part.add_header("Content-Disposition", f'attachment; filename="{name}"')
    msg.attach(part)


def draft_application(job: dict, cover_letter: str, resume_pdf: str, subject: str) -> bool:
    """Compose the application email and leave it as a draft in Sahawat's own
    Gmail — never sent automatically, regardless of what the posting's apply
    instructions say. A real employer address on the other end makes this
    irreversible once sent, so it always needs his own review and his own
    click to send (see memory feedback_no_autonomous_email_send — a prior
    'send it' doesn't carry forward, and neither does the request sounding
    routine). Uses IMAP APPEND to Gmail's own Drafts folder with the same
    app-password credential the digest SMTP send already uses."""
    apply_email = job.get("apply_email")
    if not apply_email:
        return False

    msg = MIMEMultipart()
    msg["To"] = apply_email
    msg["Subject"] = subject

    body = f"""{cover_letter}

---
Sahawat Nilwatcharamanee
Phone: 416-616-9589
Email: {APPLY_FROM}
LinkedIn: linkedin.com/in/sahawatcrosswalkwisdom
"""
    msg.attach(MIMEText(body, "plain"))
    _attach_file(msg, resume_pdf)

    try:
        with imaplib.IMAP4_SSL("imap.gmail.com") as imap:
            imap.login(NOTIFY_FROM, os.environ["GMAIL_APP_PASSWORD"])
            imap.append(
                "[Gmail]/Drafts",
                "(\\Draft)",
                imaplib.Time2Internaldate(time.time()),
                msg.as_bytes(),
            )
        return True
    except Exception as e:
        print(f"[email_sender] Failed to draft application to {apply_email}: {e}")
        return False


def _card_sort_key(j: dict):
    """Digest order: adjusted fit first (the health-informatics boost and the
    commute adjustment are already baked into `score` by job_agent), then the
    health track, then the target club — so an equal-scoring GoodLife posting
    never outranks a health-informatics one."""
    return (
        j.get("score", 0),
        1 if j.get("health_track") else 0,
        1 if j.get("target_club") else 0,
    )


def _digest_body(
    applied: list, notify: list, total_found: int,
    skipped: int = 0, newly_ghosted: list = None, alerts: list = None,
) -> tuple:
    """Build the (subject, body) of the daily summary. Pure function, no I/O.

    The agent is fully autonomous: everything here is a report of what already
    happened, never a to-do list. Jobs it couldn't apply to are listed FYI-only
    with the reason and the link, in case the reader ever wants to follow up."""
    newly_ghosted = newly_ghosted or []
    alerts = alerts or []

    if not applied and not notify:
        subject = "Job Agent — quiet day, nothing new"
    else:
        subject = f"Job Agent — {len(applied)} applied for you, {len(notify)} couldn't be auto-applied"
    if alerts:
        subject = "⚠ " + subject

    lines = [
        "=== OTTAWA JOB AGENT — DAILY SUMMARY ===",
        "",
        f"Scanned: {total_found} | Applied: {len(applied)} | "
        f"Couldn't auto-apply: {len(notify)} | Skipped (low fit): {skipped}",
        "",
        "Everything below is FYI only — applications go out automatically, "
        "nothing here needs action.",
        "",
    ]

    if alerts:
        lines.append("─── ⚠ ALERTS " + "─" * 40)
        for a in alerts:
            lines.append(f"  ! {a}")
        lines.append("")

    if not applied and not notify:
        lines += ["No new relevant jobs today.", ""]

    if applied:
        lines.append(f"─── APPLIED ({len(applied)}) " + "─" * 30)
        for j in sorted(applied, key=_card_sort_key, reverse=True):
            applied_via = (
                f"email → {j['apply_email']}" if j.get("apply_email")
                else f"company website ({j.get('web_apply_ats', 'unknown')} form)"
            )
            if j.get("target_club"):
                lines.append("\n★ TARGET CLUB — Queen and Bank, walking distance:")
            if j.get("rare_category"):
                lines.append("\n★ RARE POSTING — applied automatically:")
            lines += [
                f"\n✓ {j['title']} — {j['company']}  (fit {j.get('score', '?')}/10)",
                f"    via:      {applied_via}",
                f"    location: {j['location']}",
                f"    commute:  {(j.get('commute') or {}).get('label', 'unknown')}",
                f"    deadline: {_fmt_deadline(j)}",
                f"    posting:  {j['url']}",
            ]
            if j.get("qualification_note"):
                lines.append(f"    qualify:  uncertain — {j['qualification_note']}")
            if j.get("microsite_url"):
                lines.append(f"    pitch page sent along: {j['microsite_url']}")
        lines.append("")

    if notify:
        lines.append(f"─── COULDN'T AUTO-APPLY ({len(notify)}) — FYI " + "─" * 15)
        for j in sorted(notify, key=_card_sort_key, reverse=True):
            if j.get("target_club"):
                lines.append("\n★ TARGET CLUB — Queen and Bank, walking distance:")
            if j.get("rare_category"):
                lines.append("\n★ RARE POSTING:")
            lines += [
                f"\n✗ {j['title']} — {j['company']}  (fit {j.get('score', '?')}/10)",
                f"    why:      {j.get('no_apply_reason', 'unknown')}",
                f"    next:     {j.get('next_step', 'Open the posting and apply directly')}",
                f"    commute:  {(j.get('commute') or {}).get('label', 'unknown')}",
                f"    deadline: {_fmt_deadline(j)}",
            ]
            prefill = j.get("prefill") or {}
            if prefill:
                lines.append(
                    f"    prefilled:{prefill.get('n_ready', 0)} answers ready, "
                    f"{prefill.get('n_needs_input', 0)} need your input (attached)"
                )
            if j.get("apply_url") and j["apply_url"] != j["url"]:
                lines.append(f"    apply:    {j['apply_url']}")
            lines.append(f"    posting:  {j['url']}")
            if j.get("qualification_note"):
                lines.append(f"    qualify:  uncertain — {j['qualification_note']}")
        lines.append("")

    if newly_ghosted:
        lines.append(f"─── AUTO-MARKED GHOSTED ({len(newly_ghosted)}) — no response in 21+ days " + "─" * 5)
        for g in newly_ghosted:
            lines.append(f"  - {g['title']} @ {g['company']}")
        lines.append("")

    lines.append(
        "Full tracker, the application-autofill sheet, each tailored resume, and a "
        "prefilled application package per unfinished job are attached to this email. "
        "The dashboard picks up today's data automatically."
    )

    return subject, "\n".join(lines)


def _esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def _open_button_html(url: str, label: str = "Open posting →") -> str:
    return (
        f'<a href="{_esc(url)}" '
        f'style="display:inline-block;background:{BRAND_CHARCOAL};color:{BRAND_WARM_WHITE};'
        f'text-decoration:none;font-weight:600;font-size:13px;padding:9px 18px;'
        f'border-radius:999px;margin-top:10px;">{label}</a>'
    )


# How many prefilled questions to show inline before deferring to the attachment.
# Enough to finish a short form from the phone; past that the email gets unreadable
# and the attached package is the better surface.
MAX_INLINE_QA = 8


def _apply_button_html(j: dict) -> str:
    """The primary CTA on a card he has to finish himself: the page the form
    actually lives on, which is usually several redirects past the posting URL.
    Falls back to the plain posting button when no form was ever resolved."""
    apply_url = (j.get("apply_url") or "").strip()
    posting_url = j.get("url", "")
    if not apply_url or apply_url == posting_url:
        return _open_button_html(posting_url)

    return (
        f'<div style="margin-top:10px;">'
        f'<a href="{_esc(apply_url)}" '
        f'style="display:inline-block;background:{BRAND_AMBER};color:{BRAND_CHARCOAL};'
        f'text-decoration:none;font-weight:700;font-size:13px;padding:9px 18px;'
        f'border-radius:999px;">Apply here →</a>'
        f'<a href="{_esc(posting_url)}" '
        f'style="display:inline-block;color:#888;text-decoration:underline;font-size:12px;'
        f'margin-left:12px;">Open posting</a>'
        f'</div>'
    )


def _commute_tag_html(j: dict) -> str:
    """Commute from 335 Cooper St. Walk is the priority, so it's on every card —
    applied ones too, since it's the first thing he'll want to know if one lands."""
    label = (j.get("commute") or {}).get("label")
    if not label:
        return ""
    return f'<div style="font-size:13px;color:#555;">commute: {_esc(label)}</div>'


def _target_club_banner_html(j: dict) -> str:
    if not j.get("target_club"):
        return ""
    return (
        f'<div style="color:{BRAND_TEAL};font-weight:700;font-size:12px;margin-bottom:6px;">'
        f'★ TARGET CLUB — Queen and Bank, walking distance</div>'
    )


def _prefill_html(j: dict) -> str:
    """Counts plus the answers themselves, so a short form can be finished straight
    from the email without opening the attachment. Amber rows are the questions the
    engine refused to guess — those are the only ones that need him."""
    prefill = j.get("prefill") or {}
    answers = prefill.get("answers") or []
    if not answers:
        return ""

    n_ready = prefill.get("n_ready", 0)
    n_needs = prefill.get("n_needs_input", 0)
    typical_note = (
        ' <span style="color:#999;font-weight:400;">(typical questions for this '
        'portal — the real form wasn\'t reachable)</span>'
        if prefill.get("questions_are_typical") else ""
    )

    rows = []
    for a in answers[:MAX_INLINE_QA]:
        if a["needs_input"]:
            value = f'<span style="color:#B8860B;font-weight:600;">NEEDS YOUR INPUT</span>'
            if a.get("hint"):
                value += f' <span style="color:#888;">— {_esc(a["hint"])}</span>'
            background = "#FFF6E5"
        else:
            value = f'<span style="white-space:pre-wrap;">{_esc(a["answer"])}</span>'
            background = "#FAF9F6"
        rows.append(
            f'<div style="background:{background};border:1px solid #eee;border-radius:6px;'
            f'padding:8px 12px;margin-top:6px;font-size:13px;color:#333;">'
            f'<div style="color:#777;font-size:11px;text-transform:uppercase;'
            f'letter-spacing:0.06em;margin-bottom:3px;">{_esc(a["label"])}</div>{value}</div>'
        )

    remaining = len(answers) - len(rows)
    more = (
        f'<div style="font-size:12px;color:#999;margin-top:6px;">'
        f'+ {remaining} more in the attached package</div>'
        if remaining > 0 else ""
    )

    return (
        f'<div style="margin-top:12px;">'
        f'<div style="font-size:12px;font-weight:700;color:{BRAND_CHARCOAL};">'
        f'{n_ready} answer{"" if n_ready == 1 else "s"} ready · '
        f'{n_needs} need{"s" if n_needs == 1 else ""} your input{typical_note}</div>'
        f'{"".join(rows)}{more}</div>'
    )


def _applied_card_html(j: dict) -> str:
    applied_via = (
        f"email → {_esc(j['apply_email'])}" if j.get("apply_email")
        else f"company website ({_esc(j.get('web_apply_ats', 'unknown'))} form)"
    )
    rare_banner = (
        '<div style="color:#B8860B;font-weight:700;font-size:12px;margin-bottom:6px;">'
        '★ RARE POSTING — applied automatically</div>'
    ) if j.get("rare_category") else ""
    microsite = (
        f'<div style="margin-top:8px;font-size:13px;">Pitch page sent along: '
        f'<a href="{_esc(j["microsite_url"])}">{_esc(j["microsite_url"])}</a></div>'
    ) if j.get("microsite_url") else ""

    qualification_note_html = (
        f'<div style="background:#FFF6E5;border-left:3px solid {BRAND_AMBER};padding:8px 12px;'
        f'border-radius:6px;font-size:12px;margin-top:8px;color:#555;">'
        f'⚠ Qualification uncertain — {_esc(j["qualification_note"])}</div>'
    ) if j.get("qualification_note") else ""

    return f"""
    <div style="border:1px solid #e2ddd3;border-left:4px solid {BRAND_TEAL};border-radius:10px;
                padding:16px 20px;margin-bottom:14px;background:#ffffff;">
      {_target_club_banner_html(j)}
      {rare_banner}
      <div style="font-size:15px;font-weight:700;color:{BRAND_CHARCOAL};">
        ✓ {_esc(j['title'])} — {_esc(j['company'])}
        <span style="font-weight:400;color:#888;font-size:12px;">(fit {_esc(j.get('score', '?'))}/10)</span>
      </div>
      <div style="font-size:13px;color:#555;margin-top:6px;">via: {applied_via}</div>
      <div style="font-size:13px;color:#555;">location: {_esc(j.get('location', ''))}</div>
      {_commute_tag_html(j)}
      <div style="font-size:13px;color:#555;">deadline: {_esc(_fmt_deadline(j))}</div>
      {microsite}
      {qualification_note_html}
      {_open_button_html(j['url'])}
    </div>"""


def _notify_card_html(j: dict) -> str:
    rare_banner = (
        '<div style="color:#B8860B;font-weight:700;font-size:12px;margin-bottom:6px;">'
        '★ RARE POSTING</div>'
    ) if j.get("rare_category") else ""

    next_step = j.get("next_step")
    next_step_html = (
        f'<div style="background:#FFF6E5;border-left:3px solid {BRAND_AMBER};padding:10px 14px;'
        f'border-radius:6px;font-size:13px;margin-top:10px;"><b>Next step:</b> {_esc(next_step)}</div>'
    ) if next_step else ""

    cover_letter = (j.get("cover_letter") or "").strip()
    cover_letter_html = (
        f'<div style="margin-top:12px;">'
        f'<div style="font-size:11px;text-transform:uppercase;letter-spacing:0.08em;color:#999;'
        f'margin-bottom:4px;">Cover letter (copy-paste ready)</div>'
        f'<div style="white-space:pre-wrap;background:#FAF9F6;border:1px solid #eee;border-radius:8px;'
        f'padding:12px 14px;font-size:13px;color:#333;">{_esc(cover_letter)}</div></div>'
    ) if cover_letter else ""

    resume_note = (
        '<div style="font-size:12px;color:#888;margin-top:8px;">\U0001F4CE Tailored resume attached '
        'to this email</div>'
        if j.get("resume_pdf") and Path(j["resume_pdf"]).exists() else ""
    )

    prefill_note = (
        '<div style="font-size:12px;color:#888;margin-top:4px;">\U0001F4CE Prefilled application '
        'attached to this email</div>'
        if j.get("prefill_path") and Path(j["prefill_path"]).exists() else ""
    )

    qualification_note_html = (
        f'<div style="background:#FFF6E5;border-left:3px solid {BRAND_AMBER};padding:8px 12px;'
        f'border-radius:6px;font-size:12px;margin-top:8px;color:#555;">'
        f'⚠ Qualification uncertain — {_esc(j["qualification_note"])}</div>'
    ) if j.get("qualification_note") else ""

    return f"""
    <div style="border:1px solid #e2ddd3;border-left:4px solid {BRAND_AMBER};border-radius:10px;
                padding:16px 20px;margin-bottom:14px;background:#ffffff;">
      {_target_club_banner_html(j)}
      {rare_banner}
      <div style="font-size:15px;font-weight:700;color:{BRAND_CHARCOAL};">
        ✗ {_esc(j['title'])} — {_esc(j['company'])}
        <span style="font-weight:400;color:#888;font-size:12px;">(fit {_esc(j.get('score', '?'))}/10)</span>
      </div>
      <div style="font-size:13px;color:#555;margin-top:6px;">why: {_esc(j.get('no_apply_reason', 'unknown'))}</div>
      {_commute_tag_html(j)}
      <div style="font-size:13px;color:#555;">deadline: {_esc(_fmt_deadline(j))}</div>
      {next_step_html}
      {qualification_note_html}
      {_apply_button_html(j)}
      {_prefill_html(j)}
      {resume_note}
      {prefill_note}
      {cover_letter_html}
    </div>"""


def _digest_html(
    applied: list, notify: list, total_found: int,
    skipped: int = 0, newly_ghosted: list = None, alerts: list = None,
) -> str:
    """HTML counterpart to _digest_body — same data, richer rendering. Pure function, no I/O."""
    newly_ghosted = newly_ghosted or []
    alerts = alerts or []

    alerts_html = ""
    if alerts:
        items = "".join(f'<li style="margin-bottom:4px;">{_esc(a)}</li>' for a in alerts)
        alerts_html = f"""
        <div style="background:#FDEDED;border-left:4px solid #C0392B;border-radius:8px;
                    padding:14px 18px;margin-bottom:24px;">
          <div style="font-weight:700;color:#C0392B;margin-bottom:6px;">⚠ Alerts</div>
          <ul style="margin:0;padding-left:18px;font-size:13px;color:#555;">{items}</ul>
        </div>"""

    applied_html = ""
    if applied:
        cards = "".join(
            _applied_card_html(j) for j in sorted(applied, key=_card_sort_key, reverse=True)
        )
        applied_html = f"""
        <h2 style="font-size:13px;letter-spacing:0.1em;text-transform:uppercase;color:{BRAND_TEAL};
                   margin:28px 0 14px;">Applied ({len(applied)})</h2>
        {cards}"""

    notify_html = ""
    if notify:
        cards = "".join(
            _notify_card_html(j) for j in sorted(notify, key=_card_sort_key, reverse=True)
        )
        notify_html = f"""
        <h2 style="font-size:13px;letter-spacing:0.1em;text-transform:uppercase;color:{BRAND_AMBER};
                   margin:28px 0 14px;">Couldn't auto-apply — FYI ({len(notify)})</h2>
        {cards}"""

    ghosted_html = ""
    if newly_ghosted:
        items = "".join(
            f'<li style="margin-bottom:4px;">{_esc(g["title"])} @ {_esc(g["company"])}</li>'
            for g in newly_ghosted
        )
        ghosted_html = f"""
        <h2 style="font-size:13px;letter-spacing:0.1em;text-transform:uppercase;color:#888;
                   margin:28px 0 14px;">Auto-marked ghosted — no response in 21+ days
                   ({len(newly_ghosted)})</h2>
        <ul style="font-size:13px;color:#555;padding-left:18px;">{items}</ul>"""

    empty_html = (
        '<p style="color:#777;">No new relevant jobs today.</p>'
        if not applied and not notify else ""
    )

    return f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:{BRAND_WARM_WHITE};
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <div style="max-width:640px;margin:0 auto;padding:28px 20px;">
    <h1 style="font-size:22px;color:{BRAND_CHARCOAL};margin:0 0 4px;">Ottawa Job Agent — Daily Summary</h1>
    <p style="font-size:13px;color:#777;margin:0 0 22px;">
      Scanned {total_found} &middot; Applied {len(applied)} &middot;
      Couldn't auto-apply {len(notify)} &middot; Skipped {skipped}
    </p>
    {alerts_html}
    {empty_html}
    {applied_html}
    {notify_html}
    {ghosted_html}
    <p style="font-size:12px;color:#999;margin-top:32px;border-top:1px solid #e5e0d5;padding-top:16px;">
      Full tracker, the application-autofill sheet, each tailored resume, and a prefilled
      application package per unfinished job are attached to this email.
    </p>
  </div>
</body></html>"""


def _send_quiet_status(total_found: int, sources_checked: int) -> bool:
    """Sahawat asked (Sep18) for a daily email regardless of results, so a run
    that finds nothing no longer goes fully silent — it sends one short status
    note instead of the full digest. Throttled to once/day by has_sent_digest_today()
    in the caller, since the pipeline runs 6x/day and the other 5 quiet runs that
    day still shouldn't re-notify."""
    subject = "Ottawa Job Agent — daily check-in (nothing new today)"
    body = (
        f"Checked {sources_checked} job source(s) today, {total_found} posting(s) seen total — "
        "nothing new that cleared the fit bar, nothing pending your review, no alerts.\n\n"
        "The agent is running on schedule; this is just confirmation it's alive. "
        "You'll get the full digest (with attachments) the moment there's something to act on."
    )
    msg = MIMEMultipart("alternative")
    msg["From"] = NOTIFY_FROM
    msg["To"] = NOTIFY_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        with _gmail_smtp() as s:
            s.sendmail(NOTIFY_FROM, NOTIFY_TO, msg.as_string())
        print(f"[email_sender] Quiet-day status sent to {NOTIFY_TO}")
        return True
    except Exception as e:
        print(f"[email_sender] Failed to send quiet-day status: {e}")
        return False


def send_digest(
    applied: list, notify: list, total_found: int,
    tracker_html: str = None, newly_ghosted: list = None, skipped: int = 0,
    alerts: list = None, autofill_html: str = None, sources_checked: int = 5,
) -> bool:
    """Send the daily summary to Sahawat's Gmail. A run that applied to nothing,
    has nothing for him to review, ghosted nothing, and raised no alert sends a
    short "nothing new today" status instead of the full digest — throttled to
    once per calendar day via agent_config.has_sent_digest_today(), since the
    pipeline runs 6x/day and he only wants one email a day, not six identical
    "quiet" pings. A genuine alert (e.g. Serper credits exhausted) or any real
    result always sends the full digest. Returns whether an email was actually sent."""
    newly_ghosted = newly_ghosted or []
    alerts = alerts or []
    if not applied and not notify and not newly_ghosted and not alerts:
        if has_sent_digest_today():
            print("[email_sender] Quiet run (nothing applied, nothing to review, no alerts) — already sent today's status, skipping")
            return False
        sent = _send_quiet_status(total_found, sources_checked)
        if sent:
            mark_digest_sent()
        return sent

    subject, body = _digest_body(applied, notify, total_found, skipped, newly_ghosted, alerts)
    body_html = _digest_html(applied, notify, total_found, skipped, newly_ghosted, alerts)

    msg = MIMEMultipart("mixed")
    msg["From"] = NOTIFY_FROM
    msg["To"] = NOTIFY_TO
    msg["Subject"] = subject

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(body, "plain"))
    alt.attach(MIMEText(body_html, "html"))
    msg.attach(alt)

    if tracker_html and Path(tracker_html).exists():
        _attach_file(msg, tracker_html)

    if autofill_html and Path(autofill_html).exists():
        _attach_file(msg, autofill_html, filename="Application autofill sheet.html")

    # Attach each notify job's tailored resume once — several Job Bank Direct
    # Apply jobs share the same category-level PDF, so dedupe by path.
    attached_resumes = set()
    for j in notify:
        resume_pdf = j.get("resume_pdf")
        if not resume_pdf or resume_pdf in attached_resumes or not Path(resume_pdf).exists():
            continue
        attached_resumes.add(resume_pdf)
        filename = _safe_filename(f"Resume - {j['company']} - {j['title']}.pdf")
        _attach_file(msg, resume_pdf, filename=filename)

    # The prefilled application package — one per job he has to finish himself.
    # Named for the job rather than the job id so the attachment list reads like
    # a to-do list. Unique per job, so no dedupe needed beyond the path guard.
    attached_prefills = set()
    for j in notify:
        prefill_path = j.get("prefill_path")
        if not prefill_path or prefill_path in attached_prefills or not Path(prefill_path).exists():
            continue
        attached_prefills.add(prefill_path)
        filename = _safe_filename(f"Prefilled application - {j['company']} - {j['title']}.html")
        _attach_file(msg, prefill_path, filename=filename)

    try:
        with _gmail_smtp() as s:
            s.sendmail(NOTIFY_FROM, NOTIFY_TO, msg.as_string())
        print(f"[email_sender] Digest sent to {NOTIFY_TO}")
        mark_digest_sent()
        return True
    except Exception as e:
        print(f"[email_sender] Failed to send digest: {e}")
        return False
