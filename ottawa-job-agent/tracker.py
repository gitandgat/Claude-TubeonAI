"""Job application tracker — persistent record of every application's lifecycle.

Statuses: applied -> interview_scheduled -> offer
                   -> rejected_after_application
                   -> rejected_after_interview
                   -> ghosted (auto-detected after GHOST_AFTER_DAYS of silence)
                   -> withdrawn

CLI:
    python3 tracker.py list
    python3 tracker.py update "<company or title>" interview_scheduled "phone screen Jul 10"
    python3 tracker.py dashboard
"""

import json
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
TRACKER_FILE = BASE / "applications.json"
DASHBOARD_FILE = BASE / "tracker_dashboard.html"

GHOST_AFTER_DAYS = 21

STATUS_LABELS = {
    "applied": "Applied",
    "interview_scheduled": "Interview",
    "offer": "Offer",
    "rejected_after_application": "Rejected (application)",
    "rejected_after_interview": "Rejected (interview)",
    "ghosted": "Ghosted",
    "withdrawn": "Withdrawn",
}

COLUMN_ORDER = [
    "interview_scheduled", "offer", "applied",
    "rejected_after_application", "rejected_after_interview",
    "ghosted", "withdrawn",
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
    days_ago = ""
    try:
        d0 = datetime.strptime(entry.get("applied_date", ""), "%Y-%m-%d").date()
        days_ago = f"{(date.today() - d0).days}d ago"
    except (ValueError, TypeError):
        pass
    latest_note = entry.get("history", [{}])[-1].get("note", "")
    return f"""      <a class="card" href="{_html.escape(entry.get('url', '#'))}" target="_blank" rel="noopener">
        <div class="card-title">{_html.escape(entry.get('title', ''))}</div>
        <div class="card-company">{_html.escape(entry.get('company', ''))}</div>
        <div class="card-meta">Applied {_fmt_date(entry.get('applied_date', ''))} · {days_ago} · score {entry.get('score', '?')}/10</div>
        <div class="card-note">{_html.escape(latest_note)}</div>
      </a>"""


def build_dashboard() -> str:
    data = _load()
    counts = stats()
    total = sum(counts.values())

    columns_html = []
    for status in COLUMN_ORDER:
        entries = [v for v in data.values() if v.get("status") == status]
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
  .card-title {{ font-weight:600; font-size:0.92rem; }}
  .card-company {{ color:#555; font-size:0.85rem; margin-top:0.15rem; }}
  .card-meta {{ color:#999; font-size:0.72rem; margin-top:0.5rem; }}
  .card-note {{ color:var(--charcoal); font-size:0.78rem; margin-top:0.4rem; font-style:italic; }}
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
        for entry in sorted(data.values(), key=lambda e: e.get("applied_date", ""), reverse=True):
            print(f"[{entry.get('status')}] {entry.get('title')} @ {entry.get('company')} "
                  f"(applied {entry.get('applied_date')})")
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
