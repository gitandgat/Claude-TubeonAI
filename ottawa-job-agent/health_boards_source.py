"""Ottawa health employers' own job boards, polled directly.

Serper is out of credits and no Ottawa health employer is on Greenhouse/Lever,
so the health-informatics priority track was fed by CHEO's Workday board alone,
and by Sept 2026 every CHEO posting had been seen. A survey of the employers'
career pages that month found three more boards readable without an account:

  - CIHI (Canadian Institute for Health Information): Njoyn, behind a Radware
    bot check that plain requests never pass but headless Chromium does. This
    is the single best health-data employer in the city, so it earns a browser.
  - City of Ottawa (incl. Ottawa Public Health): SAP SuccessFactors career
    site, server-rendered, keyword search, 25 rows a page.
  - The Royal (mental health): Jobvite career site; needs the iframe params
    (nl=1&fr=false) plus a Referer or it redirects to the marketing page.

Dead ends checked the same day, recorded so nobody re-probes them: The Ottawa
Hospital (PeopleSoft, 403), QCH (DLGL e-recruiter, JS + login), EORLA (Njoyn
but needs a session token), Bruyère (UltiPro, no public board link), Ontario
Health / Montfort / CMA (403 to scripts), GC Jobs (JSF session app), Infoway.

Every board is a row in known_health_boards.json ({kind, company_name, ...})
and all three kinds produce the same pipeline job shape. Categories come from
the same is_health_informatics_text matcher Workday uses, so the +2 boost and
always_notify agree across sources. None of these ATSs can be applied to
without a candidate account, so apply_target is employer_site and the job's
url is the posting page: the web applier follows the Apply button itself and,
when it hits the login wall, produces the prefill package instead.
"""

import html
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests

from job_sources import _OTTAWA_AREA_TERMS
from workday_source import is_health_informatics_text, make_id

KNOWN_BOARDS_FILE = Path(__file__).parent / "known_health_boards.json"

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126 Safari/537.36"
)
HEADERS = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"}
TIMEOUT = 30
SLEEP_BETWEEN = 0.3
# Unseen postings whose detail page is fetched per board per run. Six runs a
# day means a board never falls more than a day behind even at this cap.
MAX_DETAILS_PER_BOARD = 12
SF_PAGE_SIZE = 25
SF_MAX_PAGES = 3
NJOYN_LOAD_TIMEOUT_MS = 45_000
NJOYN_SETTLE_MS = 6_000  # Radware's JS challenge needs a moment to resolve

KIND_LABELS = {"njoyn": "Njoyn", "successfactors": "SuccessFactors", "jobvite": "Jobvite"}


def load_known_boards() -> dict:
    try:
        data = json.loads(KNOWN_BOARDS_FILE.read_text())
    except (OSError, json.JSONDecodeError):
        return {"boards": []}
    data.setdefault("boards", [])
    return data


def _strip(fragment: Optional[str]) -> str:
    text = re.sub(r"<[^>]+>", " ", html.unescape(fragment or ""))
    return re.sub(r"\s+", " ", text).strip()


def _is_ottawa_or_remote(location: str) -> bool:
    low = (location or "").lower()
    if "remote" in low or "télétravail" in low:
        return True
    return any(term in low for term in _OTTAWA_AREA_TERMS)


def _iso_date(text: Optional[str], fmts: tuple) -> Optional[str]:
    text = (text or "").strip()
    for fmt in fmts:
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return None


# --- shared shape ---

# Data/informatics signal in a *title*. On a hospital board every clinical
# posting (nurse practitioner, pharmacist) mentions the EHR somewhere in its
# description, so the shared matcher run over title+description tagged them
# health_informatics and let them bypass MIN_SCORE — first live poll of The
# Royal, 2026-09-07. The description is still what score_fit reads; only the
# category (and with it always_notify and the +2 boost) is decided on the title.
_DATA_TITLE_RE = re.compile(
    r"\b(?:data|informatics|health information|medical records|health records|"
    r"digital health|epidemiolog\w*|biostatistic\w*|decision support|business intelligence|"
    r"reporting analyst|clinical analyst)\b",
    re.IGNORECASE,
)


def _category_for(entry: dict, title: str, description: str) -> str:
    if is_health_informatics_text(title) or _DATA_TITLE_RE.search(title or ""):
        return "health_informatics"
    base = entry.get("category", "health")
    return "health_other" if base == "health" else base


def _possible_categories(entry: dict) -> set:
    """Every category _category_for can hand a posting from this board, so a
    scoped run knows whether to poll it. Mirrors _category_for's branches."""
    base = entry.get("category", "health")
    return {"health_informatics", "health_other" if base == "health" else base}


def _to_job(entry: dict, *, title: str, url: str, location: str, description: str,
            job_key: str, deadline: Optional[str] = None, posted_date: Optional[str] = None) -> dict:
    company = entry["company_name"]
    category = _category_for(entry, title, description)
    return {
        "id": make_id(title, company, job_key),
        "title": title,
        "company": company,
        "location": location or "Ottawa, ON",
        "url": url,
        "source": f"{company} ({KIND_LABELS.get(entry['kind'], entry['kind'])})",
        "category": category,
        "apply_email": None,
        "description": description,
        "deadline": deadline,
        "posted_date": posted_date,
        "status": "open",
        "always_notify": category == "health_informatics",
        "apply_target": "employer_site",
        "ats": entry["kind"],
    }


# --- SuccessFactors (City of Ottawa) ---

_SF_ANCHOR_RE = re.compile(r'<a\b([^>]*\bjobTitle-link\b[^>]*)>(.*?)</a>', re.S)
_HREF_RE = re.compile(r'href="([^"]+)"')


def parse_sf_rows(page_html: str) -> list:
    """Title/path pairs from a search page. Each posting renders two anchors
    (desktop + phone), so dedupe on the path while keeping page order."""
    rows, seen = [], set()
    for attrs, text in _SF_ANCHOR_RE.findall(page_html):
        m = _HREF_RE.search(attrs)
        if not m:
            continue
        path = html.unescape(m.group(1))
        if path in seen:
            continue
        seen.add(path)
        rows.append({"path": path, "title": _strip(text)})
    return rows


def parse_sf_detail(detail_html: str) -> dict:
    m = re.search(r'class="[^"]*\bjobdescription\b[^"]*"[^>]*>([\s\S]*?)(?:class="job-apply|id="jobs-related|$)',
                  detail_html)
    description = _strip(m.group(1)) if m else ""
    close = re.search(r"Application Close:\s*(\d{2}/\d{2}/\d{4})", description)
    return {
        "description": description,
        "deadline": _iso_date(close.group(1), ("%d/%m/%Y",)) if close else None,
    }


def fetch_successfactors(entry: dict, skip_ids: set, session: requests.Session) -> list:
    base = entry["base_url"].rstrip("/")
    host = "{0.scheme}://{0.netloc}".format(urlparse(base))
    jobs, seen_paths, details = [], set(), 0
    for query in entry.get("queries") or [""]:
        for page in range(SF_MAX_PAGES):
            resp = session.get(f"{base}/search/", headers=HEADERS, timeout=TIMEOUT,
                               params={"q": query, "locale": "en_GB", "startrow": page * SF_PAGE_SIZE})
            if resp.status_code != 200:
                print(f"[health_boards]   search '{query}' page {page + 1} HTTP {resp.status_code}")
                break
            rows = parse_sf_rows(resp.text)
            if not rows:
                break
            for row in rows:
                if row["path"] in seen_paths:
                    continue
                seen_paths.add(row["path"])
                if make_id(row["title"], entry["company_name"], row["path"]) in skip_ids:
                    continue
                if details >= MAX_DETAILS_PER_BOARD:
                    continue
                url = urljoin(host, row["path"])
                detail = session.get(url, headers=HEADERS, timeout=TIMEOUT)
                details += 1
                time.sleep(SLEEP_BETWEEN)
                parsed = parse_sf_detail(detail.text) if detail.status_code == 200 else {"description": "", "deadline": None}
                jobs.append(_to_job(entry, title=row["title"], url=url, location="Ottawa, ON",
                                    description=parsed["description"], job_key=row["path"],
                                    deadline=parsed["deadline"]))
            if len(rows) < SF_PAGE_SIZE:
                break
            time.sleep(SLEEP_BETWEEN)
    return jobs


# --- Jobvite (The Royal) ---

_JV_ROW_RE = re.compile(r"<tr[^>]*>([\s\S]*?)</tr>")
_JV_NAME_RE = re.compile(r'<a[^>]+href="(/[^"]+/job/[^"]+)"[^>]*>([\s\S]*?)</a>')
_JV_LOC_RE = re.compile(r'class="jv-job-list-location"[^>]*>([\s\S]*?)</td>')


def parse_jobvite_rows(page_html: str) -> list:
    rows = []
    for row in _JV_ROW_RE.findall(page_html):
        if "jv-job-list-name" not in row:
            continue
        name = _JV_NAME_RE.search(row)
        if not name:
            continue
        loc = _JV_LOC_RE.search(row)
        rows.append({"path": name.group(1), "title": _strip(name.group(2)),
                     "location": _strip(loc.group(1)) if loc else ""})
    return rows


def parse_jobvite_detail(detail_html: str) -> dict:
    m = re.search(r'class="jv-job-detail-description"[^>]*>([\s\S]*?)(?:class="jv-job-detail-bottom-actions|$)',
                  detail_html)
    meta = re.search(r'class="jv-job-detail-meta"[^>]*>([\s\S]*?)</p>', detail_html)
    return {"description": _strip(m.group(1)) if m else "", "meta": _strip(meta.group(1)) if meta else ""}


def fetch_jobvite(entry: dict, skip_ids: set, session: requests.Session) -> list:
    slug = entry["slug"]
    headers = dict(HEADERS, Referer=entry.get("referer", f"https://jobs.jobvite.com/{slug}/"))
    params = {"nl": "1", "fr": "false"}
    resp = session.get(f"https://jobs.jobvite.com/{slug}/jobs", headers=headers, params=params, timeout=TIMEOUT)
    if resp.status_code != 200:
        print(f"[health_boards]   listing HTTP {resp.status_code}")
        return []
    jobs, details = [], 0
    for row in parse_jobvite_rows(resp.text):
        if not _is_ottawa_or_remote(row["location"]):
            continue
        if make_id(row["title"], entry["company_name"], row["path"]) in skip_ids:
            continue
        if details >= MAX_DETAILS_PER_BOARD:
            continue
        url = f"https://jobs.jobvite.com{row['path']}"
        detail = session.get(url, headers=headers, params=params, timeout=TIMEOUT)
        details += 1
        time.sleep(SLEEP_BETWEEN)
        parsed = parse_jobvite_detail(detail.text) if detail.status_code == 200 else {"description": "", "meta": ""}
        jobs.append(_to_job(entry, title=row["title"], url=url, location=row["location"],
                            description=parsed["description"], job_key=row["path"]))
    return jobs


# --- Njoyn (CIHI), via headless Chromium ---

_NJ_ROW_RE = re.compile(r'<tr[^>]*class="[^"]*TableDataRow[^"]*"[^>]*>([\s\S]*?)</tr>')
_NJ_CELL_RE = re.compile(r"<td[^>]*>([\s\S]*?)</td>")
_NJ_LINK_RE = re.compile(r'<a[^>]+href="([^"]*Page=JobDetails[^"]*)"', re.I)
_NJ_DATE_FMTS = ("%B %d, %Y", "%b %d, %Y")


def parse_njoyn_rows(page_html: str) -> list:
    """Job number | title (link) | department | category | job type | city."""
    rows = []
    for row in _NJ_ROW_RE.findall(page_html):
        cells = _NJ_CELL_RE.findall(row)
        link = _NJ_LINK_RE.search(row)
        if len(cells) < 6 or not link:
            continue
        rows.append({
            "jobid": _strip(cells[0]), "title": _strip(cells[1]), "department": _strip(cells[2]),
            "job_type": _strip(cells[4]), "city": _strip(cells[5]), "href": html.unescape(link.group(1)),
        })
    return rows


def parse_njoyn_detail(detail_html: str) -> dict:
    m = re.search(r'id="njnContentContainer"[^>]*>([\s\S]*)', detail_html)
    text = _strip(m.group(1)) if m else _strip(detail_html)
    start = text.find("Job number:")
    if start > 0:
        text = text[start:]
    closing = re.search(r"Closing date:\s*([A-Za-z]+ \d{1,2}, \d{4})", text)
    posted = re.search(r"Date posted:\s*([A-Za-z]+ \d{1,2}, \d{4})", text)
    location = re.search(r"Location:\s*(.*?)\s+(?:Number of positions|Contract Duration|Date posted|Closing date):", text)
    return {
        "description": text,
        "deadline": _iso_date(closing.group(1), _NJ_DATE_FMTS) if closing else None,
        "posted_date": _iso_date(posted.group(1), _NJ_DATE_FMTS) if posted else None,
        "location": location.group(1).strip() if location else "",
    }


def njoyn_listing_url(entry: dict) -> str:
    return f"https://clients.njoyn.com/{entry['cl']}/xweb/xweb.asp?CLID={entry['clid']}&page=joblisting&lang=1"


def fetch_njoyn(entry: dict, skip_ids: set, session: requests.Session = None) -> list:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[health_boards]   playwright not installed — Njoyn board skipped")
        return []
    listing = njoyn_listing_url(entry)
    jobs, details = [], 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            page = browser.new_context(user_agent=UA, locale="en-CA").new_page()
            page.goto(listing, wait_until="domcontentloaded", timeout=NJOYN_LOAD_TIMEOUT_MS)
            page.wait_for_timeout(NJOYN_SETTLE_MS)
            rows = parse_njoyn_rows(page.content())
            if not rows:
                print(f"[health_boards]   no rows on listing (title: {page.title()!r}) — bot check may have held")
                return []
            for row in rows:
                if not _is_ottawa_or_remote(row["city"]):
                    continue
                if make_id(row["title"], entry["company_name"], row["jobid"]) in skip_ids:
                    continue
                if details >= MAX_DETAILS_PER_BOARD:
                    continue
                url = urljoin(listing, row["href"])
                page.goto(url, wait_until="domcontentloaded", timeout=NJOYN_LOAD_TIMEOUT_MS)
                page.wait_for_timeout(NJOYN_SETTLE_MS // 2)
                details += 1
                parsed = parse_njoyn_detail(page.content())
                jobs.append(_to_job(entry, title=row["title"], url=url,
                                    location=parsed["location"] or row["city"],
                                    description=parsed["description"], job_key=row["jobid"],
                                    deadline=parsed["deadline"], posted_date=parsed["posted_date"]))
        finally:
            browser.close()
    return jobs


FETCHERS = {"successfactors": fetch_successfactors, "jobvite": fetch_jobvite, "njoyn": fetch_njoyn}


class HealthBoardsSource:
    def fetch_all(self, skip_ids: Optional[set] = None, categories: Optional[set] = None) -> list:
        """Poll every registered board and return unseen Ottawa postings in the
        pipeline's shape. skip_ids prevents a detail fetch (or a browser page
        load) for postings already in seen_jobs.json; categories scopes a run
        the same way WorkdaySource.fetch_all does. One board failing never
        takes the others down."""
        skip_ids = skip_ids or set()
        session = requests.Session()
        jobs = []
        for entry in load_known_boards()["boards"]:
            if categories and not (_possible_categories(entry) & categories):
                continue
            fetcher = FETCHERS.get(entry.get("kind"))
            if fetcher is None:
                print(f"[health_boards] unknown board kind {entry.get('kind')!r} — skipped")
                continue
            print(f"[health_boards] {entry['company_name']} ({KIND_LABELS.get(entry['kind'], entry['kind'])})...")
            try:
                found = fetcher(entry, skip_ids, session)
            except Exception as e:  # noqa: BLE001 — a board outage is not a run failure
                print(f"[health_boards]   {entry['company_name']} failed: {e}")
                continue
            print(f"[health_boards]   {len(found)} unseen Ottawa posting(s)")
            jobs.extend(found)
        return jobs


if __name__ == "__main__":
    from collections import Counter
    found = HealthBoardsSource().fetch_all(skip_ids=set())
    for j in found:
        print(f"- [{j['category']}] {j['title']} @ {j['company']} ({j['location']}) deadline={j['deadline']}")
        print(f"    {j['url']}")
    print("TALLY", dict(Counter(j["category"] for j in found)))
