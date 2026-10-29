"""
Accept-watcher: detects health-coach leads who accepted our LinkedIn connect
and sends ONE personalized first-touch DM (no links, no pitch), then stops.

How acceptance is detected: our connects go out via /inbox/connect (outside any
campaign), and SendPilot has no connect-status endpoint. So we enroll every
connect-sent lead into the dormant DRAFT campaign "AI Automation for Coaches"
purely as a status tracker: leads are PATCHed to CONNECTION_SENT, and
SendPilot's LinkedIn sync flips them to CONNECTION_ACCEPTED when the person
accepts (same mechanism that tracked the Ottawa campaign accepts). The draft
campaign has no active sequence, so nothing else is ever auto-sent.

FALLBACK if statuses never move off CONNECTION_SENT while accepts visibly
happen on LinkedIn (check after ~5 days): the sync doesn't cover
externally-sent connects; switch to probe-DMs (attempt send_message_to_lead
once per lead after a 3-day grace period; failure = not yet connected).

State lives in the leads JSON: sp_lead_id / dm_sent / dm_date / dm_text /
reply_flagged. Replies are NEVER auto-answered; they land in
replies-inbox.json for the morning briefing and the human.

    python3 freelance-leads/accept_watcher.py            # enroll + watch + DM
    python3 freelance-leads/accept_watcher.py --dry-run  # preview only
"""

import argparse
import json
import os
import re
import sys
import time

SKILL = "/Users/toto/.claude/skills/sendpilot-outreach"
sys.path.insert(0, SKILL)
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from dotenv import load_dotenv  # noqa: E402
load_dotenv(os.path.join(REPO_ROOT, ".env"))
from sendpilot import SP  # noqa: E402

from connect_drip import clean_first_name  # noqa: E402
from linkedin_agent.stop_slop_gate import score_post  # noqa: E402

LEADS_FILE = os.path.join(os.path.dirname(__file__), "health-coaches-2026-06-21.json")
REPLIES_FILE = os.path.join(os.path.dirname(__file__), "replies-inbox.json")

TRACKING_CAMPAIGN_ID = "cmr64vwoi037z0a01nvq9z4wt"  # "AI Automation for Coaches — Outreach" (draft)

MAX_DMS_PER_RUN = 15
SEND_SPACING_SEC = 10.0

GENERIC_COMPANIES = {"self-employed", "self employed", "freelance", "independent", ""}

# First-touch variants: peer tone, one genuine question, zero links/pitch.
# {thing} = their practice/company; {title} = their cleaned job title.
DM_VARIANTS_COMPANY = [
    ("Hi {fn}, thanks for connecting. Former physician here, now building on "
     "the coaching side of health. I noticed {thing} and wanted to ask: where "
     "do most of your new clients come from these days? I compare notes with "
     "other practitioners when I can."),
    ("Hi {fn}, good to be connected. I spent years in medicine before moving "
     "to the coaching side, so I pay attention to people who turned health "
     "expertise into a practice of their own. How long has {thing} been going?"),
]
DM_VARIANT_TITLE = (
    "Hi {fn}, thanks for accepting. I'm a former physician, now on the "
    "coaching side myself. Your work as {title} stood out. What part of "
    "finding new clients keeps you busiest lately?")


def norm_url(url: str) -> str:
    """Normalize a LinkedIn profile URL to its /in/ slug for matching."""
    m = re.search(r"linkedin\.com/in/([^/?#]+)", (url or "").lower())
    return m.group(1) if m else (url or "").lower().rstrip("/")


def clean_company(raw: str) -> str:
    name = re.sub(r",?\s*(LLC|Inc\.?|Ltd\.?|Corp\.?)$", "", (raw or "").strip(), flags=re.I)
    return name.strip()


def craft_dm(lead: dict, variant_idx: int) -> str:
    fn = clean_first_name(lead.get("first_name", ""))
    company = clean_company(lead.get("company", ""))
    if company and company.lower() not in GENERIC_COMPANIES:
        tpl = DM_VARIANTS_COMPANY[variant_idx % len(DM_VARIANTS_COMPANY)]
        return tpl.format(fn=fn, thing=company)
    title = (lead.get("job_title") or "a health coach").strip().rstrip(".")
    # Long credential-stuffed titles read like a mail merge; keep it short.
    if len(title) > 60:
        title = "a health coach"
    return DM_VARIANT_TITLE.format(fn=fn, title=title)


def gated_dm(lead: dict, idx: int) -> str | None:
    """Craft a DM that passes the stop-slop gate, or None (never send slop)."""
    for candidate in (craft_dm(lead, idx), craft_dm(lead, idx + 1)):
        total, _, _ = score_post(candidate)
        if total >= 35:
            return candidate
    return None


def enroll(sp: SP, leads: list[dict], dry_run: bool) -> None:
    """Idempotently put every connect-sent lead into the tracking campaign."""
    existing = {norm_url(cl.get("linkedinUrl") or cl.get("linkedin_url")): cl
                for cl in sp.leads(TRACKING_CAMPAIGN_ID)}
    need = [l for l in leads if l.get("connect_sent") and not l.get("sp_lead_id")]
    if not need:
        return

    to_add = [l for l in need if norm_url(l["linkedin_url"]) not in existing]
    if to_add:
        payload = [{"linkedinUrl": l["linkedin_url"],
                    "firstName": l.get("first_name", ""),
                    "lastName": l.get("last_name", ""),
                    "company": l.get("company", ""),
                    "title": l.get("job_title", "")} for l in to_add]
        if dry_run:
            print(f"  · would enroll {len(payload)} leads into tracking campaign")
        else:
            sp.add_leads(TRACKING_CAMPAIGN_ID, payload)
            existing = {norm_url(cl.get("linkedinUrl") or cl.get("linkedin_url")): cl
                        for cl in sp.leads(TRACKING_CAMPAIGN_ID)}

    enrolled = 0
    for l in need:
        cl = existing.get(norm_url(l["linkedin_url"]))
        if not cl:
            continue
        l["sp_lead_id"] = cl["id"]
        # New campaign leads sit at PENDING, which would mean "send a connect"
        # if the campaign ever went live. Reflect reality: connect already sent.
        if not dry_run and cl.get("status") == "PENDING":
            sp.set_lead_status(cl["id"], "CONNECTION_SENT",
                               note="connect sent via direct API drip")
        enrolled += 1
    print(f"  enrolled {enrolled} leads into tracking campaign "
          f"({len(need) - enrolled} unmatched)")


def flag_reply(lead: dict) -> None:
    replies = []
    if os.path.exists(REPLIES_FILE):
        with open(REPLIES_FILE) as f:
            replies = json.load(f)
    if any(r.get("linkedin_url") == lead["linkedin_url"] for r in replies):
        return
    replies.append({"name": lead.get("full_name"),
                    "linkedin_url": lead.get("linkedin_url"),
                    "company": lead.get("company"),
                    "flagged": time.strftime("%Y-%m-%d"),
                    "handled": False})
    with open(REPLIES_FILE, "w") as f:
        json.dump(replies, f, indent=2)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-dms", type=int, default=MAX_DMS_PER_RUN)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with open(LEADS_FILE) as f:
        leads = json.load(f)

    sp = SP()
    enroll(sp, leads, args.dry_run)

    status_by_id = {cl["id"]: cl.get("status", "?")
                    for cl in sp.leads(TRACKING_CAMPAIGN_ID)}
    tally: dict[str, int] = {}
    for s in status_by_id.values():
        tally[s] = tally.get(s, 0) + 1
    print(f"  campaign status tally: {tally}")

    sender = sp.senders()[0]
    budget = min(args.max_dms, sender.get("remainingMessages", args.max_dms))
    sent = consecutive_errors = 0

    for idx, lead in enumerate(leads):
        lid = lead.get("sp_lead_id")
        if not lid or lead.get("dm_sent"):
            continue
        status = status_by_id.get(lid)
        if status == "REPLY_RECEIVED" and not lead.get("reply_flagged"):
            lead["reply_flagged"] = True
            flag_reply(lead)
            print(f"  ★ REPLY from {lead['full_name']} — flagged for the human, no auto-DM")
            continue
        if status != "CONNECTION_ACCEPTED":
            continue
        if sent >= budget:
            print("  DM budget reached; remaining accepts wait for the next run")
            break

        msg = gated_dm(lead, idx)
        who = f"{lead.get('full_name','?')} ({lead.get('company','—')})"
        if msg is None:
            print(f"  ✗ {who} — no variant passed the slop gate, skipped")
            continue
        if args.dry_run:
            print(f"  · would DM {who}:\n    {msg}")
            continue
        try:
            sp.send_message_to_lead(lid, msg)
            # Direct sends do NOT advance lead status (SendPilot gotcha #2);
            # mark it ourselves or a re-run would double-DM this person.
            sp.set_lead_status(lid, "MESSAGE_SENT", note="first-touch DM sent")
            lead["dm_sent"] = True
            lead["dm_date"] = time.strftime("%Y-%m-%d")
            lead["dm_text"] = msg
            sent += 1
            consecutive_errors = 0
            print(f"  ✓ DM → {who}")
            time.sleep(SEND_SPACING_SEC)
        except Exception as e:
            body = e.response.text[:120] if getattr(e, "response", None) is not None else str(e)
            consecutive_errors += 1
            print(f"  ✗ {who} — {body}")
            if consecutive_errors >= 3:
                print("  3 consecutive errors — backing off until next run")
                break

    if not args.dry_run:
        with open(LEADS_FILE, "w") as f:
            json.dump(leads, f, indent=2)
    accepted_waiting = sum(1 for l in leads
                           if l.get("sp_lead_id") and not l.get("dm_sent")
                           and status_by_id.get(l["sp_lead_id"]) == "CONNECTION_ACCEPTED")
    print(f"\nDONE: {sent} first-touch DMs sent, {accepted_waiting} accepted awaiting DM")


if __name__ == "__main__":
    main()
