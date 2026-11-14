"""Peter's New Jobs — ingest the daily Ottawa jobs newsletter.

The first mail-reading source in the pipeline. Every other source fetches from a
board or an API, so there was no existing shape to copy; this module defines it.

The send is a Mailchimp campaign that lays the jobs out one table row per job,
four cells to a row: index, linked title, employer, location. Rows are grouped
under bold section headers (Private / Healthcare / Agencies / Public) and each
section restarts its numbering at 1 — so the index cell is not an identifier and
is dropped.

Two MIME parts matter, for different reasons:

  * The HTML carries title, employer and location, but wraps every link in a
    Mailchimp redirect whose "?e=" recipient token is regenerated on each send.
    Hashing that into an id would make every job look new every morning.
  * The plain-text part carries the real destination URLs (with mc_cid/mc_eid
    appended, which _clean_url strips).

They are joined by position *within a section*. A section whose row count and
URL count disagree keeps its redirect URLs instead of pairing by guesswork: a
mis-paired row would point an application at the wrong posting, which is worse
than a tracked link. Mismatches are reported, not swallowed.

VALIDATION STATUS: the HTML row/section extraction is tested against the
documented structure. The plain-text layout was described to us rather than
observed, so the URL join is NOT yet confirmed against a real send. Run
  python3 -m petersnewjobs_source <path to .eml>
on a real message and check the reported counts before trusting ids or dedup.
"""

import html
import re
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from job_sources import _OTTAWA_AREA_TERMS
from workday_source import is_health_informatics_text, make_id

SOURCE_NAME = "Peter's New Jobs"
SENDER = "jobs@petersnewjobs.com"

# Bold headers that open each table. Parsing is gated on finding at least one:
# the subscription also sends a weekly events digest with a different layout,
# and best-effort parsing of that would manufacture nonsense leads.
SECTIONS = ("Private", "Healthcare", "Agencies", "Public")

# Mailchimp's click-tracking wrapper. Its "?e=" token is per-recipient and
# per-send, so these are never hashed into an id.
_REDIRECT_HOSTS = ("list-manage.com", "list-manage1.com", "mailchi.mp")

# Campaign/recipient tracking appended to the real destinations in the text part.
_TRACKING_PARAMS = ("mc_cid", "mc_eid", "utm_source", "utm_medium",
                    "utm_campaign", "utm_term", "utm_content")

# Listings that name no actual vacancy. The live example is Peter's
# "Candidates Interested in Vice Principal..." row, which is a talent-pool
# notice rather than a posting to apply to.
_NOT_A_POSTING_RE = re.compile(
    r"candidates?\s+interested|talent\s+(pool|community)|expression\s+of\s+interest",
    re.I,
)

_TR_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.I | re.S)
_TD_RE = re.compile(r"<td\b[^>]*>(.*?)</td>", re.I | re.S)
_HREF_RE = re.compile(r"""<a\b[^>]*\bhref\s*=\s*["']([^"']+)["']""", re.I)
_URL_RE = re.compile(r"https?://[^\s<>\"')\]]+")


def _strip_tags(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html.unescape(fragment or ""))
    return re.sub(r"\s+", " ", text).strip()


def _is_ottawa_or_remote(location: str) -> bool:
    """Strict positive test, unlike job_sources._is_ottawa_or_remote_location.

    That one is a reject-list of named cities and deliberately lets anything
    unrecognised through, which is right for a web-search source where the
    location field is often blank. It is wrong here: this digest openly carries
    Kingston, Renfrew and Montebello rows, none of which are on that list, so
    the permissive version would wave all of them in. Peter always states a
    location, so requiring an Ottawa-area term costs nothing.
    """
    low = (location or "").lower()
    if "remote" in low or "télétravail" in low or "teletravail" in low:
        return True
    return any(term in low for term in _OTTAWA_AREA_TERMS)


def _is_redirect(url: str) -> bool:
    host = (urlsplit(url).hostname or "").lower()
    return any(host == h or host.endswith("." + h) for h in _REDIRECT_HOSTS)


def _clean_url(url: str) -> str:
    """Drop campaign/recipient tracking so the same posting hashes identically
    tomorrow. Everything else about the URL is left alone."""
    parts = urlsplit((url or "").strip())
    kept = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
            if k.lower() not in _TRACKING_PARAMS]
    return urlunsplit((parts.scheme, parts.netloc, parts.path,
                       urlencode(kept), ""))


def _section_positions(html_body: str) -> list:
    """(offset, section) for each bold section header, in document order."""
    found = []
    for name in SECTIONS:
        for m in re.finditer(
            r"<(b|strong|h[1-4])\b[^>]*>\s*(?:<[^>]+>\s*)*" + re.escape(name)
            + r"\b.*?</\1>", html_body, re.I | re.S,
        ):
            found.append((m.start(), name))
    found.sort()
    # Keep the first sighting of each section; Mailchimp repeats names in the
    # table-of-contents links at the top.
    seen, ordered = set(), []
    for offset, name in found:
        if name not in seen:
            seen.add(name)
            ordered.append((offset, name))
    return ordered


def _section_for(offset: int, headers: list) -> str:
    current = ""
    for pos, name in headers:
        if pos <= offset:
            current = name
        else:
            break
    return current


def parse_html_rows(html_body: str) -> list:
    """Job rows in document order: section, title, employer, location, href.

    A row qualifies only with four cells and a link in the second, which is what
    separates job rows from the spacer and layout rows Mailchimp emits around
    them.
    """
    headers = _section_positions(html_body)
    rows = []
    for tr in _TR_RE.finditer(html_body):
        cells = _TD_RE.findall(tr.group(1))
        if len(cells) != 4:
            continue
        href = _HREF_RE.search(cells[1])
        if not href:
            continue
        title = _strip_tags(cells[1])
        if not title:
            continue
        rows.append({
            "section": _section_for(tr.start(), headers),
            "title": title,
            "employer": _strip_tags(cells[2]),
            "location": _strip_tags(cells[3]),
            "href": html.unescape(href.group(1)),
        })
    return rows


def parse_text_urls(text_body: str) -> dict:
    """Real destination URLs from the plain-text part, grouped by section.

    Only non-redirect links count: the success story, event links and footer in
    this part are Mailchimp redirects, while the job destinations are direct.
    """
    headers = []
    for name in SECTIONS:
        m = re.search(r"^\s*" + re.escape(name) + r"\s*$", text_body,
                      re.I | re.M)
        if m:
            headers.append((m.start(), name))
    headers.sort()

    by_section = {}
    for m in _URL_RE.finditer(text_body):
        url = m.group().rstrip(".,);")
        if _is_redirect(url):
            continue
        by_section.setdefault(_section_for(m.start(), headers), []).append(
            _clean_url(url))
    return by_section


def parse_digest(html_body: str, text_body: str = "") -> dict:
    """Jobs plus a report of what did and did not line up.

    Returns {"jobs": [...], "sections": {...}, "mismatched": [...],
    "skipped": {...}}. Callers want the report: a silent count change is how a
    layout change would otherwise slip past unnoticed.
    """
    rows = parse_html_rows(html_body)
    if not _section_positions(html_body) or not rows:
        # Almost certainly the weekly events send, not the jobs digest.
        return {"jobs": [], "sections": {}, "mismatched": [],
                "skipped": {"not_a_jobs_digest": 1}}

    text_urls = parse_text_urls(text_body)
    mismatched = []

    grouped = {}
    for row in rows:
        grouped.setdefault(row["section"], []).append(row)

    for section, section_rows in grouped.items():
        urls = text_urls.get(section, [])
        if len(urls) == len(section_rows):
            for row, url in zip(section_rows, urls):
                row["url"] = url
        else:
            # Counts disagree, so position says nothing reliable. Keep the
            # redirect: a tracked link that works beats a direct link to the
            # wrong posting.
            mismatched.append({"section": section, "rows": len(section_rows),
                               "urls": len(urls)})
            for row in section_rows:
                row["url"] = row["href"]

    jobs, seen_urls = [], set()
    skipped = {"out_of_area": 0, "not_a_posting": 0, "duplicate": 0}

    for row in rows:
        if _NOT_A_POSTING_RE.search(row["title"]):
            skipped["not_a_posting"] += 1
            continue
        if not _is_ottawa_or_remote(row["location"]):
            skipped["out_of_area"] += 1
            continue

        url = row["url"]
        # The same posting is listed under more than one employer label — the
        # live case is Bilingual Care Coordinator under both CCAC and Champlain.
        # make_id() hashes the employer, so those would survive id-based dedup
        # as two jobs; the destination is what actually identifies the posting.
        key = url if not _is_redirect(url) else None
        if key and key in seen_urls:
            skipped["duplicate"] += 1
            continue
        if key:
            seen_urls.add(key)

        title, employer = row["title"], row["employer"]
        category = ("health_informatics" if is_health_informatics_text(title)
                    else "health_other" if row["section"] == "Healthcare"
                    else "general")
        # A redirect URL is unhashable for ids (its ?e= token rotates), so fall
        # back to title+employer, which is stable across sends.
        id_key = url if not _is_redirect(url) else "petersnewjobs"
        jobs.append({
            "id": make_id(title, employer, id_key),
            "title": title,
            "company": employer or SOURCE_NAME,
            "location": row["location"] or "Ottawa, ON",
            "url": url,
            "source": SOURCE_NAME,
            "category": category,
            "apply_email": None,
            "description": "",
            "deadline": None,
            "posted_date": None,
            "status": "open",
            "always_notify": category == "health_informatics",
            "apply_target": "employer_site",
            "ats": None,
        })

    return {"jobs": jobs,
            "sections": {s: len(r) for s, r in grouped.items()},
            "mismatched": mismatched,
            "skipped": skipped}


def parse_eml(path) -> dict:
    """Parse a saved .eml (Gmail: Show original -> Download Original)."""
    with open(path, "rb") as fh:
        msg = BytesParser(policy=policy.default).parse(fh)
    html_body, text_body = "", ""
    for part in msg.walk():
        if part.get_content_maintype() != "text":
            continue
        try:
            payload = part.get_content()
        except Exception:
            continue
        if part.get_content_subtype() == "html" and not html_body:
            html_body = payload
        elif part.get_content_subtype() == "plain" and not text_body:
            text_body = payload
    return parse_digest(html_body, text_body)


def fetch_petersnewjobs(skip_ids: set = None, eml_path=None) -> list:
    """Jobs from a saved .eml. Mailbox polling is deliberately not wired yet —
    the Gmail account is read by agents/email_organizer_agent through an OAuth
    token, and this source should reuse that rather than open a second path to
    the same inbox."""
    skip_ids = skip_ids or set()
    if not eml_path:
        print("[petersnewjobs] no .eml given — nothing to ingest")
        return []
    result = parse_eml(eml_path)
    for note in result["mismatched"]:
        print("[petersnewjobs] section %r: %d rows vs %d text URLs — kept "
              "redirect links" % (note["section"], note["rows"], note["urls"]))
    kept = [j for j in result["jobs"] if j["id"] not in skip_ids]
    print("[petersnewjobs] %d rows -> %d jobs (%d new); skipped %s"
          % (sum(result["sections"].values()), len(result["jobs"]),
             len(kept), result["skipped"]))
    return kept


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        raise SystemExit("usage: python3 -m petersnewjobs_source <file.eml>")
    report = parse_eml(sys.argv[1])
    print("sections:  ", report["sections"])
    print("mismatched:", report["mismatched"] or "none — URL join clean")
    print("skipped:   ", report["skipped"])
    print("jobs:      ", len(report["jobs"]))
    for job in report["jobs"][:10]:
        print("  [%s] %s — %s (%s)\n      %s"
              % (job["category"], job["title"], job["company"],
                 job["location"], job["url"]))
