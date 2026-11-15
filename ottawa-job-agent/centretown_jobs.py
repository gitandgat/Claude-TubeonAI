"""Centretown / Remote-Canada new jobs: our own Peter's-New-Jobs-style list.

Peter's digest covers all of Ottawa and beyond. This list is deliberately
narrower: it shows a posting only if its location is

  * walkable from 335 Cooper St (walkability.is_walkable), or
  * remote within Canada.

A bare "Ottawa, ON" is NOT listed. The address is unknown, and the point of
this list is that every row is one Sahawat can actually get to on foot or from
home. Those rows are counted and logged so the strictness stays visible.

There is no fetching here. job_agent.py hands over every lead its sources
already pulled this run (search, Job Bank, Workday, ATS, health boards), whether
or not the pipeline goes on to apply. Qualifying never-listed jobs go into a
pending queue. They ride on the next email the agent actually sends and are
marked listed only once that email has gone out, so a quiet run that sends
nothing never loses a row.

Dedup is on the cleaned destination URL, not job id, for the same reason as
petersnewjobs_source: one posting can show up under two employer labels.
"""

import html
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Iterable, List, Optional

from job_sources import _OTTAWA_AREA_TERMS
from petersnewjobs_source import _clean_url
from walkability import is_walkable

PENDING_FILENAME = "centretown_jobs_pending.json"
LISTED_FILENAME = "centretown_jobs_listed.json"
PREVIEW_FILENAME = "centretown_jobs.html"

SECTION_TITLES = {
    "walk": "🚶 Walkable from Centretown",
    "remote": "💻 Remote — Canada",
}
SECTION_ORDER = ("walk", "remote")

# Priority tracks first within a section, then everything else alphabetically.
_CATEGORY_PRIORITY = ("health_informatics", "healthcare_pt", "health_promotion", "goodlife")

_REMOTE_RE = re.compile(r"\bremote\b|work\s+from\s+home|\bwfh\b|t[ée]l[ée]travail", re.I)
_HYBRID_RE = re.compile(r"\bhybrid\b|hybride", re.I)

# Positive Canada markers. A remote posting must name one of these, or nothing
# at all besides "remote". Anything else ("US", "EMEA", "Cyprus") is treated as
# explicitly non-Canada rather than guessed at. Same reasoning as ats_boards.
_CANADA_WORDS = {
    "canada", "canadian", "ontario", "quebec", "québec", "alberta", "manitoba",
    "saskatchewan", "nova", "brunswick", "newfoundland", "labrador", "yukon",
    "nunavut", "columbia", "toronto", "montreal", "montréal", "vancouver",
    "calgary", "edmonton", "winnipeg", "halifax",
} | set(_OTTAWA_AREA_TERMS)
# Province codes only count as a whole comma/paren fragment, so the "on" in
# "based on US hours" is not read as Ontario.
_PROVINCE_CODES = {"on", "qc", "bc", "ab", "mb", "sk", "ns", "nb", "nl", "pe", "pei",
                   "yt", "nt", "nu"}
_FILLER_WORDS = {"remote", "work", "from", "home", "wfh", "teletravail", "télétravail",
                 "fully", "only", "in", "based", "anywhere", "first", "position", "the"}


def _is_remote_canada(location: str) -> bool:
    loc = location or ""
    if not _REMOTE_RE.search(loc) or _HYBRID_RE.search(loc):
        return False
    low = loc.lower()
    fragments = {f.strip() for f in re.split(r"[,()/|;\-–]+", low) if f.strip()}
    if fragments & _PROVINCE_CODES:
        return True
    words = set(re.findall(r"[a-zà-ÿ']+", low)) - _FILLER_WORDS
    return not words or bool(words & _CANADA_WORDS)


# Rows that are not a posting you could apply to: the local model's
# placeholder when it could not read a title, and aggregator search-result
# pages ("$13-$27/hr Remote Customer Service Rep Jobs" at ZipRecruiter).
_AGGREGATOR_COMPANIES = {"ziprecruiter", "indeed", "glassdoor", "linkedin", "talent.com",
                         "simplyhired", "jooble"}
_PLACEHOLDER_RE = re.compile(r"\bnot\s+specified\b|^\s*unknown\s*$", re.I)


def _is_junk(job: dict) -> bool:
    title = job.get("title") or ""
    company = (job.get("company") or "").strip().lower()
    return bool(not title.strip() or _PLACEHOLDER_RE.search(title)
                or company in _AGGREGATOR_COMPANIES)


def section_for(job: dict) -> Optional[str]:
    """'walk', 'remote', or None (not listed). Remote is judged from the
    location field only: a description mentioning "remote monitoring" must not
    turn a Kanata clinic job into a remote one."""
    if _is_junk(job):
        return None
    location = job.get("location") or ""
    if _is_remote_canada(location):
        return "remote"
    if is_walkable(f"{location} {job.get('title') or ''}"):
        return "walk"
    return None


def listing_key(job: dict) -> str:
    url = (job.get("url") or "").strip()
    if url:
        return "url:" + _clean_url(url)
    return f"id:{job.get('id', '')}"


def _is_unknown_ottawa(job: dict) -> bool:
    return "ottawa" in (job.get("location") or "").lower()


def _read_json(path: Path, expected_type: type):
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return expected_type()
    return data if isinstance(data, expected_type) else expected_type()


class Store:
    """Pending queue + permanent listed set, both plain JSON in the agent dir."""

    def __init__(self, base_dir: Path):
        self.pending_path = Path(base_dir) / PENDING_FILENAME
        self.listed_path = Path(base_dir) / LISTED_FILENAME

    def pending(self) -> List[dict]:
        return _read_json(self.pending_path, list)

    def _listed(self) -> dict:
        return _read_json(self.listed_path, dict)

    def queue(self, jobs: Iterable[dict]) -> dict:
        """Add qualifying, never-listed, not-yet-pending jobs. Returns counts."""
        listed = self._listed()
        pending = self.pending()
        known = set(listed) | {p.get("key") for p in pending}
        additions = []
        unknown_ottawa = 0
        for job in jobs:
            section = section_for(job)
            if section is None:
                unknown_ottawa += _is_unknown_ottawa(job)
                continue
            key = listing_key(job)
            if key in known:
                continue
            known.add(key)
            additions.append({
                "key": key,
                "section": section,
                "title": job.get("title", ""),
                "company": job.get("company", ""),
                "location": job.get("location", ""),
                "url": job.get("url", ""),
                "source": job.get("source", ""),
                "category": job.get("category", ""),
                "found": str(date.today()),
            })
        if additions:
            self.pending_path.write_text(json.dumps(pending + additions, indent=2))
        return {"added": len(additions), "unknown_ottawa": unknown_ottawa}

    def mark_listed(self, items: Iterable[dict]) -> None:
        """Call only after the email carrying these items was actually sent."""
        items = list(items)
        sent_keys = {i.get("key") for i in items}
        today = str(date.today())
        listed = {
            **self._listed(),
            **{i["key"]: {"date": today, "title": i.get("title", ""),
                          "company": i.get("company", "")}
               for i in items if i.get("key")},
        }
        self.listed_path.write_text(json.dumps(listed, indent=2))
        remaining = [p for p in self.pending() if p.get("key") not in sent_keys]
        self.pending_path.write_text(json.dumps(remaining, indent=2))


# ── rendering ─────────────────────────────────────────────────────────────────

def _sort_key(item: dict) -> tuple:
    cat = item.get("category", "")
    rank = _CATEGORY_PRIORITY.index(cat) if cat in _CATEGORY_PRIORITY else len(_CATEGORY_PRIORITY)
    return (rank, cat, (item.get("title") or "").lower())


def _grouped(items: List[dict]) -> List[tuple]:
    return [
        (section, sorted((i for i in items if i.get("section") == section), key=_sort_key))
        for section in SECTION_ORDER
        if any(i.get("section") == section for i in items)
    ]


def _esc(value) -> str:
    return html.escape(str(value or ""), quote=True)


def _safe_url(url: str) -> str:
    return url if re.match(r"https?://", url or "", re.I) else ""


def _row_html(n: int, item: dict) -> str:
    url = _safe_url(item.get("url", ""))
    title = _esc(item.get("title"))
    title_cell = (f'<a href="{_esc(url)}" style="color:#2C2C2C;font-weight:600;">{title}</a>'
                  if url else f'<span style="font-weight:600;">{title}</span>')
    cell = 'style="padding:6px 8px;border-bottom:1px solid #eee;vertical-align:top;"'
    return (f"<tr><td {cell}>{n}.</td><td {cell}>{title_cell}</td>"
            f"<td {cell}>{_esc(item.get('company'))}</td>"
            f'<td {cell}><span style="color:#777;">{_esc(item.get("location"))}</span></td></tr>')


def render_html(items: List[dict]) -> str:
    """Email-safe HTML fragment: one numbered table per section, like Peter's."""
    if not items:
        return ""
    blocks = []
    for section, rows in _grouped(items):
        body = "".join(_row_html(n, item) for n, item in enumerate(rows, 1))
        blocks.append(
            f'<h3 style="font-size:15px;color:#2C2C2C;margin:20px 0 6px;">'
            f"{_esc(SECTION_TITLES[section])} ({len(rows)})</h3>"
            f'<table style="width:100%;border-collapse:collapse;font-size:13px;">{body}</table>'
        )
    return (
        '<div style="margin:0 0 28px;">'
        '<h2 style="font-size:13px;letter-spacing:0.1em;text-transform:uppercase;'
        f'color:#5B9A8B;margin:0 0 4px;">New jobs — Centretown &amp; Remote Canada ({len(items)})</h2>'
        '<p style="font-size:12px;color:#999;margin:0;">Every new posting our sources found, '
        "whether or not the agent applied. A plain “Ottawa, ON” without an address is left out.</p>"
        + "".join(blocks) + "</div>"
    )


def render_text(items: List[dict]) -> str:
    if not items:
        return ""
    lines = [f"NEW JOBS — CENTRETOWN & REMOTE CANADA ({len(items)})"]
    for section, rows in _grouped(items):
        lines += ["", f"{SECTION_TITLES[section]} ({len(rows)})"]
        for n, item in enumerate(rows, 1):
            lines.append(f"{n}. {item.get('title')} — {item.get('company')} ({item.get('location')})")
            if _safe_url(item.get("url", "")):
                lines.append(f"   {item['url']}")
    return "\n".join(lines)


def write_preview(items: List[dict], path: Path) -> Path:
    doc = ('<!doctype html><html><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1">'
           "<title>Centretown Jobs</title></head>"
           '<body style="font-family:-apple-system,Segoe UI,sans-serif;max-width:760px;'
           'margin:24px auto;padding:0 16px;background:#FAF7F2;color:#2C2C2C;">'
           + (render_html(items) or "<p>Nothing pending.</p>") + "</body></html>")
    path.write_text(doc)
    return path


if __name__ == "__main__":
    # python3 centretown_jobs.py  → writes centretown_jobs.html from the pending queue
    here = Path(__file__).parent
    pending = Store(here).pending()
    out = write_preview(pending, here / PREVIEW_FILENAME)
    print(f"{len(pending)} pending job(s) → {out}", file=sys.stderr)
