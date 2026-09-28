"""Job tracker — persistent record of every job's lifecycle, from first sight
to outcome.

Statuses: pending (couldn't auto-apply, needs you — recorded automatically)
                   -> applied -> interview_scheduled -> offer
                   -> rejected_after_application
                   -> rejected_after_interview
                   -> ghosted (auto-detected after GHOST_AFTER_DAYS of silence)
                   -> withdrawn
          not_interested (you decided to pass — set manually, any time)

CLI:
    python3 tracker.py list
    python3 tracker.py update "<company or title>" interview_scheduled "phone screen Jul 10"
    python3 tracker.py update "<company or title>" not_interested "not a fit"
    python3 tracker.py update "<company or title>" applied "applied manually via prefilled form"
    python3 tracker.py dashboard
"""

import json
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Optional

BASE = Path(__file__).resolve().parent
TRACKER_FILE = BASE / "applications.json"
DASHBOARD_FILE = BASE / "tracker_dashboard.html"

GHOST_AFTER_DAYS = 21

STATUS_LABELS = {
    "pending": "Needs you",
    "interested": "Interested (swiped)",
    "draft_ready": "Draft ready in Gmail",
    "applied": "Applied",
    "interview_scheduled": "Interview",
    "offer": "Offer",
    "rejected_after_application": "Rejected (application)",
    "rejected_after_interview": "Rejected (interview)",
    "ghosted": "Ghosted",
    "withdrawn": "Withdrawn",
    "not_interested": "Not interested",
}

COLUMN_ORDER = [
    "pending", "interested", "draft_ready", "interview_scheduled", "offer", "applied",
    "rejected_after_application", "rejected_after_interview",
    "ghosted", "withdrawn", "not_interested",
]


def _load() -> dict:
    if TRACKER_FILE.exists():
        try:
            data = json.loads(TRACKER_FILE.read_text())
        except Exception:
            return {}
        for entry in data.values():
            entry.setdefault("notes", "")
            entry.setdefault("location", "")
            entry.setdefault("source", "")
        return data
    return {}


def _save(data: dict) -> None:
    TRACKER_FILE.write_text(json.dumps(data, indent=2))


def record_application(job: dict, method: str) -> None:
    """Call the moment a real application actually goes out (email sent or web submitted)."""
    data = _load()
    today = str(date.today())
    entry = data.get(job["id"], {})
    entry.update({
        "title": job["title"],
        "company": job["company"],
        "url": job["url"],
        "category": job.get("category"),
        "score": job.get("score"),
        "location": job.get("location"),
        "source": job.get("source"),
        "applied_date": entry.get("applied_date", today),
        "applied_via": method,
        "status": "applied",
    })
    entry.setdefault("history", []).append({"status": "applied", "date": today, "note": f"Applied via {method}"})
    data[job["id"]] = entry
    _save(data)


def record_draft(job: dict, address: str) -> None:
    """Call when an application email was composed and left as a Gmail draft
    rather than sent (apply_email path never sends on its own — see memory
    feedback_no_autonomous_email_send). Kept as a distinct status from
    'applied' so the tracker/dashboard honestly show it as still needing
    Sahawat's own send, while still registering the address with
    already_emailed() below so a re-scraped duplicate posting doesn't queue
    a second draft to the same inbox."""
    data = _load()
    today = str(date.today())
    entry = data.get(job["id"], {})
    entry.update({
        "title": job["title"],
        "company": job["company"],
        "url": job["url"],
        "category": job.get("category"),
        "score": job.get("score"),
        "location": job.get("location"),
        "source": job.get("source"),
        "drafted_date": entry.get("drafted_date", today),
        "applied_via": address,
        "status": "draft_ready",
    })
    entry.setdefault("history", []).append({"status": "draft_ready", "date": today, "note": f"Draft created for {address}"})
    data[job["id"]] = entry
    _save(data)


def already_emailed(address: str) -> Optional[str]:
    """Return the job id of a prior 'applied' or 'draft_ready' entry that used this
    exact apply_email, or None. Job boards and small orgs sometimes list the same
    real posting under slightly different scraped titles/companies/URLs (typos,
    tracking params, re-published listings); make_id() then treats each as a "new"
    job and nothing upstream catches it. Since the one thing that stays constant
    across all those variants is the human inbox on the other end, this is the last
    line of defense against auto-emailing (or auto-drafting a second email to) the
    same real contact more than once — see the Aug 2026 incidents where this fired
    8x against cercottawa.ca and 12x against thaiembassy.ca for what was really 1-3
    actual openings each."""
    if not address:
        return None
    address = address.strip().lower()
    data = _load()
    for jid, entry in data.items():
        if entry.get("status") in ("applied", "draft_ready") and (entry.get("applied_via") or "").strip().lower() == address:
            return jid
    return None


def record_pending(job: dict) -> None:
    """Call for every job that couldn't be auto-applied, so it's visible in the
    tracker as something needing action instead of only living in that day's
    digest email. Never overwrites a status already set on this job (e.g. once
    you've marked it applied or not_interested, re-runs leave it alone)."""
    data = _load()
    today = str(date.today())
    entry = data.get(job["id"], {})
    if entry.get("status") and entry["status"] != "pending":
        return
    entry.update({
        "title": job["title"],
        "company": job["company"],
        "url": job["url"],
        "category": job.get("category"),
        "score": job.get("score"),
        "location": job.get("location"),
        "source": job.get("source"),
        "no_apply_reason": job.get("no_apply_reason", ""),
        "next_step": job.get("next_step", ""),
        # The three things that turn a pending row back into a finishable task
        # weeks later, once the digest email is buried: where the form actually
        # is, the answers already written for it, and whether it's walkable.
        "apply_url": job.get("apply_url", ""),
        "prefill_path": job.get("prefill_path", ""),
        "commute": (job.get("commute") or {}).get("label", ""),
        "status": "pending",
    })
    if not entry.get("history"):
        entry["history"] = [{"status": "pending", "date": today, "note": job.get("no_apply_reason", "")}]
    data[job["id"]] = entry
    _save(data)


def update_status(match: str, new_status: str, note: str = "") -> dict:
    """Update by job id, or fuzzy match against company/title. Returns the updated entry or None."""
    if new_status not in STATUS_LABELS:
        raise ValueError(f"Unknown status '{new_status}'. Valid: {', '.join(STATUS_LABELS)}")

    data = _load()
    key = match if match in data else None
    if not key:
        match_lower = match.lower()
        for k, v in data.items():
            if match_lower in v.get("company", "").lower() or match_lower in v.get("title", "").lower():
                key = k
                break
    if not key:
        return None

    entry = data[key]
    entry["status"] = new_status
    entry.setdefault("history", []).append({"status": new_status, "date": str(date.today()), "note": note})
    data[key] = entry
    _save(data)
    return entry


def auto_mark_ghosted(days: int = GHOST_AFTER_DAYS) -> list:
    """Mark any 'applied'/'interview_scheduled' entry stale for `days` as ghosted. Returns newly-ghosted entries."""
    data = _load()
    newly = []
    for entry in data.values():
        if entry.get("status") not in ("applied", "interview_scheduled"):
            continue
        history = entry.get("history", [])
        last_date_str = history[-1]["date"] if history else entry.get("applied_date")
        if not last_date_str:
            continue
        try:
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        if (date.today() - last_date).days >= days:
            entry["status"] = "ghosted"
            entry.setdefault("history", []).append({
                "status": "ghosted", "date": str(date.today()),
                "note": f"No response after {days}+ days — auto-marked",
            })
            newly.append(entry)
    if newly:
        _save(data)
    return newly


def stats() -> dict:
    data = _load()
    return dict(Counter(v.get("status", "unknown") for v in data.values()))


def _fmt_date(d: str) -> str:
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%b %-d")
    except (ValueError, TypeError):
        return d or "?"


def _card(entry: dict) -> str:
    import html as _html
    latest_note = entry.get("history", [{}])[-1].get("note", "")
    if entry.get("status") == "pending":
        reason = entry.get("no_apply_reason", "")
        meta = f"score {entry.get('score', '?')}/10" + (f" · {reason}" if reason else "")
        note = entry.get("next_step", "") or latest_note
    elif entry.get("applied_date"):
        days_ago = ""
        try:
            d0 = datetime.strptime(entry["applied_date"], "%Y-%m-%d").date()
            days_ago = f"{(date.today() - d0).days}d ago"
        except (ValueError, TypeError):
            pass
        meta = f"Applied {_fmt_date(entry.get('applied_date', ''))} · {days_ago} · score {entry.get('score', '?')}/10"
        note = latest_note
    else:
        meta = f"score {entry.get('score', '?')}/10"
        note = latest_note
    commute = entry.get("commute", "")
    if commute:
        meta = f"{meta} · {commute}"

    # The apply link is what makes a pending card actionable months later — the
    # posting URL usually lands on a description page, several redirects short of
    # the form. Only rendered when it's genuinely different from the posting.
    apply_url = entry.get("apply_url", "")
    apply_link = ""
    if apply_url and apply_url != entry.get("url"):
        apply_link = (
            f'\n        <a class="card-apply" href="{_html.escape(apply_url)}" '
            f'target="_blank" rel="noopener">Apply →</a>'
        )

    return f"""      <div class="card">
        <a class="card-open" href="{_html.escape(entry.get('url', '#'))}" target="_blank" rel="noopener">
          <div class="card-title">{_html.escape(entry.get('title', ''))}</div>
          <div class="card-company">{_html.escape(entry.get('company', ''))}</div>
        </a>
        <div class="card-meta">{_html.escape(meta)}</div>
        <div class="card-note">{_html.escape(note)}</div>{apply_link}
      </div>"""


def build_dashboard() -> str:
    data = _load()
    counts = stats()
    total = sum(counts.values())

    columns_html = []
    for status in COLUMN_ORDER:
        entries = [v for v in data.values() if v.get("status") == status]
        if status == "pending":
            entries.sort(key=lambda e: e.get("score") or 0, reverse=True)
        else:
            entries.sort(key=lambda e: e.get("applied_date", ""), reverse=True)
        cards = "\n".join(_card(e) for e in entries) or '      <div class="empty">Nothing here yet</div>'
        columns_html.append(f"""    <div class="column">
      <div class="column-head">
        <span>{STATUS_LABELS[status]}</span>
        <span class="count">{len(entries)}</span>
      </div>
{cards}
    </div>""")

    summary_chips = " ".join(
        f'<span class="chip">{STATUS_LABELS.get(s, s)}: {n}</span>' for s, n in counts.items()
    )

    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="robots" content="noindex" />
<title>Job application tracker — Sahawat</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
<style>
  :root {{ --amber:#D4A843; --charcoal:#2C2C2C; --warm-white:#FAF7F2; --teal:#5B9A8B; --red:#C0604F; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:"Inter",sans-serif; background:var(--warm-white); color:var(--charcoal); padding:clamp(1.5rem,4vw,3rem); }}
  h1 {{ font-family:"Playfair Display",serif; font-size:clamp(1.6rem,1rem+2vw,2.4rem); }}
  .sub {{ color:#666; margin:0.4rem 0 1.25rem; }}
  .chips {{ display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:2rem; }}
  .chip {{ background:#fff; border:1px solid rgba(44,44,44,0.1); border-radius:999px; padding:0.35rem 0.9rem; font-size:0.8rem; font-weight:600; }}
  .board {{ display:grid; grid-auto-flow:column; grid-auto-columns:minmax(260px,1fr); gap:1.25rem; overflow-x:auto; padding-bottom:1rem; }}
  .column {{ background:rgba(44,44,44,0.03); border-radius:14px; padding:1rem; min-height:120px; }}
  .column-head {{ display:flex; justify-content:space-between; align-items:center; font-size:0.78rem;
    letter-spacing:0.1em; text-transform:uppercase; color:var(--teal); font-weight:600; margin-bottom:0.9rem; }}
  .count {{ background:var(--teal); color:#fff; border-radius:999px; padding:0.1rem 0.55rem; font-size:0.72rem; }}
  .card {{ display:block; background:#fff; border-radius:10px; padding:0.85rem 1rem; margin-bottom:0.7rem;
    text-decoration:none; color:inherit; border:1px solid rgba(44,44,44,0.08); box-shadow:0 2px 10px rgba(44,44,44,0.05);
    transition:transform 0.15s, box-shadow 0.15s; }}
  .card:hover {{ transform:translateY(-2px); box-shadow:0 6px 18px rgba(44,44,44,0.1); }}
  .card-open {{ display:block; text-decoration:none; color:inherit; }}
  .card-title {{ font-weight:600; font-size:0.92rem; }}
  .card-company {{ color:#555; font-size:0.85rem; margin-top:0.15rem; }}
  .card-meta {{ color:#999; font-size:0.72rem; margin-top:0.5rem; }}
  .card-note {{ color:var(--charcoal); font-size:0.78rem; margin-top:0.4rem; font-style:italic; }}
  .card-apply {{ display:inline-block; margin-top:0.6rem; background:var(--amber); color:var(--charcoal);
    text-decoration:none; font-weight:600; font-size:0.72rem; padding:0.3rem 0.75rem; border-radius:999px; }}
  .card-apply:hover {{ filter:brightness(0.95); }}
  .empty {{ color:#aaa; font-size:0.82rem; font-style:italic; }}
</style></head>
<body>
  <h1>Job application tracker</h1>
  <p class="sub">{total} total applications · auto-updated daily · click a card to reopen the posting</p>
  <div class="chips">{summary_chips}</div>
  <div class="board">
{chr(10).join(columns_html)}
  </div>
</body></html>"""

    DASHBOARD_FILE.write_text(page, encoding="utf-8")
    return str(DASHBOARD_FILE)


def _cli():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]
    if cmd == "list":
        data = _load()

        def _when(e: dict) -> str:
            return e.get("applied_date") or (e.get("history") or [{}])[-1].get("date", "")

        for entry in sorted(data.values(), key=_when, reverse=True):
            print(f"[{entry.get('status')}] {entry.get('title')} @ {entry.get('company')} "
                  f"({_when(entry) or 'no date'})")
    elif cmd == "update":
        if len(sys.argv) < 4:
            print("Usage: tracker.py update \"<company or title>\" <status> [\"note\"]")
            return
        match, new_status = sys.argv[2], sys.argv[3]
        note = sys.argv[4] if len(sys.argv) > 4 else ""
        entry = update_status(match, new_status, note)
        if entry:
            print(f"Updated: {entry['title']} @ {entry['company']} -> {new_status}")
        else:
            print(f"No application found matching '{match}'")
    elif cmd == "dashboard":
        print("Dashboard:", build_dashboard())
    elif cmd == "ghost-check":
        newly = auto_mark_ghosted()
        print(f"Marked {len(newly)} application(s) as ghosted")
    else:
        print(__doc__)


if __name__ == "__main__":
    _cli()
