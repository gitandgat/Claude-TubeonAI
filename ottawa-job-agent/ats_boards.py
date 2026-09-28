"""Direct-ATS job discovery via Greenhouse's and Lever's free public JSON board APIs.

job_sources.py already biases Serper searches toward boards.greenhouse.io / jobs.lever.co
URLs (its `ats_query` field) because those are the only two ATS platforms web_applier.py
can reliably auto-fill (known, stable field selectors). This module takes that one step
further: once a board *token* (the company slug in the board URL) has shown up in any
search result, it's remembered permanently in known_boards.json and polled directly on
every run via each platform's own public JSON API — the full, exact, structured listing
for that company, no LLM snippet-parsing, no per-run Serper cost, and no risk of missing
a posting that just didn't surface in a given day's top-10 search slice.

The registry starts empty and only grows from real search results
(discover_boards_from_jobs) — no guessed company tokens, consistent with this pipeline's
"never invent facts" rule.
"""

import hashlib
import html
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

KNOWN_BOARDS_FILE = Path(__file__).parent / "known_boards.json"

GREENHOUSE_URL_RE = re.compile(r"(?:boards|job-boards)\.greenhouse\.io/([a-zA-Z0-9][a-zA-Z0-9\-]*)")
LEVER_URL_RE = re.compile(r"jobs\.lever\.co/([a-zA-Z0-9][a-zA-Z0-9\-]*)")

# Politeness delay between per-board API calls.
SLEEP_BETWEEN = 0.2


def make_id(title: str, company: str, url: str) -> str:
    raw = f"{title}|{company}|{url}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()[:14]


# Greenhouse/Lever boards list roles from every country, unlike Job Bank (a Canadian
# government site, where "remote" always means remote-in-Canada). A denylist of
# non-Canada countries can never be exhaustive (missed one -> "Remote - Cyprus"
# silently passes), so this instead only accepts a "remote" tag whose qualifier is
# recognized as Canada-friendly, or has no qualifier at all — anything else is
# treated as an explicit non-Canada posting rather than guessed at.
_REMOTE_QUALIFIER_ALLOW = {"", "canada", "ontario", "north america", "americas", "global", "worldwide", "anywhere"}


def _is_ottawa_or_remote_canada(location: str) -> bool:
    low = (location or "").lower().strip()
    if "ottawa" in low:
        return True
    if "remote" not in low:
        return False

    fragments = [f.strip() for f in re.split(r"[-,/()]+", low) if f.strip() and f.strip() != "remote"]
    return all(f in _REMOTE_QUALIFIER_ALLOW for f in fragments)


def _strip_html(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def load_known_boards() -> dict:
    if not KNOWN_BOARDS_FILE.exists():
        return {"greenhouse": [], "lever": []}
    try:
        data = json.loads(KNOWN_BOARDS_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {"greenhouse": [], "lever": []}
    data.setdefault("greenhouse", [])
    data.setdefault("lever", [])
    return data


def save_known_boards(boards: dict):
    KNOWN_BOARDS_FILE.write_text(json.dumps(boards, indent=2, sort_keys=True))


def board_exists(platform: str, token: str) -> bool:
    """Whether this board token resolves to a real board on the platform's API.

    Registration used to trust any token a URL happened to contain. The retired
    web-search source invented job URLs, so 26 of the 38 Greenhouse tokens in the
    registry were fabricated company names that have never returned anything but
    a 404 — including every Ottawa employer the pipeline believed it covered.
    Each one also costs a guaranteed-dead fetch on every run, forever.

    A 200 with zero open jobs still counts: a real employer between postings must
    not be dropped from the registry.
    """
    if platform == "greenhouse":
        url = "https://boards-api.greenhouse.io/v1/boards/{}/jobs".format(token)
    elif platform == "lever":
        url = "https://api.lever.co/v0/postings/{}?mode=json&limit=1".format(token)
    else:
        return False
    try:
        return requests.get(url, timeout=15).status_code == 200
    except requests.RequestException:
        # A network blip is not evidence the board is fake. Refuse to register it
        # now; a later run will see the same URL again and can confirm it then.
        return False


def discover_boards_from_jobs(jobs: list) -> int:
    """Scan already-fetched job URLs for Greenhouse/Lever board tokens and add any
    new ones to the registry. Returns the number of newly discovered tokens."""
    boards = load_known_boards()
    known_gh = set(boards["greenhouse"])
    known_lv = set(boards["lever"])
    added = 0

    for job in jobs:
        url = job.get("url", "") or ""
        gh_match = GREENHOUSE_URL_RE.search(url)
        if (gh_match and gh_match.group(1) not in known_gh
                and board_exists("greenhouse", gh_match.group(1))):
            known_gh.add(gh_match.group(1))
            added += 1
        lv_match = LEVER_URL_RE.search(url)
        if (lv_match and lv_match.group(1) not in known_lv
                and board_exists("lever", lv_match.group(1))):
            known_lv.add(lv_match.group(1))
            added += 1

    if added:
        boards["greenhouse"] = sorted(known_gh)
        boards["lever"] = sorted(known_lv)
        save_known_boards(boards)

    return added


def _fetch_greenhouse_board(token: str) -> list:
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    try:
        r = requests.get(url, timeout=20)
    except requests.RequestException:
        return []
    if r.status_code != 200:
        return []
    try:
        return r.json().get("jobs", [])
    except ValueError:
        return []


def _fetch_lever_board(token: str) -> list:
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    try:
        r = requests.get(url, timeout=20)
    except requests.RequestException:
        return []
    if r.status_code != 200:
        return []
    try:
        return r.json()
    except ValueError:
        return []


def _greenhouse_to_job(token: str, gjob: dict) -> Optional[dict]:
    # .get(key, default) only covers a *missing* key — Greenhouse sometimes
    # returns the key present with a JSON null value, and str(None) is the
    # non-empty literal "None", which would slip past the `not url` check
    # below and get handed to Playwright as a real link (see job_sources.py).
    title = str(gjob.get("title") or "").strip()
    location = str((gjob.get("location") or {}).get("name") or "").strip()
    url = str(gjob.get("absolute_url") or "").strip()
    if not title or not url or not _is_ottawa_or_remote_canada(location):
        return None

    company = token.replace("-", " ").replace("_", " ").title()
    posted = str(gjob.get("updated_at") or "")[:10] or None

    return {
        "id": make_id(title, company, url),
        "title": title,
        "company": company,
        "location": location or "Remote / Canada",
        "url": url,
        "source": "ATS Direct",
        # The Greenhouse absolute_url IS the employer's own hosted posting, so
        # there is nothing for employer_site.resolve_employer_apply_url() to look
        # up — tagging it here stops that resolver re-fetching the very board this
        # function just finished parsing.
        "apply_target": "employer_site",
        "category": "ats_direct",
        "apply_email": None,
        "description": _strip_html(gjob.get("content", ""))[:4000],
        "deadline": None,
        "posted_date": posted,
        "status": "open",
        "always_notify": False,
    }


def _lever_to_job(token: str, posting: dict) -> Optional[dict]:
    # Same null-vs-missing-key trap as _greenhouse_to_job above.
    title = str(posting.get("text") or "").strip()
    location = str((posting.get("categories") or {}).get("location") or "").strip()
    url = str(posting.get("hostedUrl") or "").strip()
    if not title or not url or not _is_ottawa_or_remote_canada(location):
        return None

    company = token.replace("-", " ").replace("_", " ").title()
    description = posting.get("descriptionPlain") or _strip_html(posting.get("description", ""))

    posted = None
    created_ms = posting.get("createdAt")
    if isinstance(created_ms, (int, float)):
        try:
            posted = datetime.utcfromtimestamp(created_ms / 1000).date().isoformat()
        except (OverflowError, OSError, ValueError):
            posted = None

    return {
        "id": make_id(title, company, url),
        "title": title,
        "company": company,
        "location": location or "Remote / Canada",
        "url": url,
        "source": "ATS Direct",
        # Same as the Greenhouse branch above: hostedUrl is already the employer's
        # own Lever posting.
        "apply_target": "employer_site",
        "category": "ats_direct",
        "apply_email": None,
        "description": str(description).strip()[:4000],
        "deadline": None,
        "posted_date": posted,
        "status": "open",
        "always_notify": False,
    }


class AtsBoardsSource:
    def fetch_all(self, skip_ids: Optional[set] = None) -> list:
        """Poll every known Greenhouse/Lever board token directly and return jobs in
        the pipeline's shape. `skip_ids` mirrors JobBankSource's interface — it trims
        the returned list but doesn't save any requests, since each board's full job
        list is fetched in one call regardless."""
        skip_ids = skip_ids or set()
        boards = load_known_boards()
        jobs = []

        for token in boards.get("greenhouse", []):
            print(f"[ats_boards] Greenhouse: {token}...")
            for gjob in _fetch_greenhouse_board(token):
                job = _greenhouse_to_job(token, gjob)
                if job and job["id"] not in skip_ids:
                    jobs.append(job)
            time.sleep(SLEEP_BETWEEN)

        for token in boards.get("lever", []):
            print(f"[ats_boards] Lever: {token}...")
            for posting in _fetch_lever_board(token):
                job = _lever_to_job(token, posting)
                if job and job["id"] not in skip_ids:
                    jobs.append(job)
            time.sleep(SLEEP_BETWEEN)

        # Dedup by id (a company could theoretically double-list a role)
        seen_ids = set()
        unique = []
        for j in jobs:
            if j["id"] not in seen_ids:
                seen_ids.add(j["id"])
                unique.append(j)

        return unique
