"""Direct-ATS job discovery via Workday's unauthenticated CXS JSON API.

Mirrors ats_boards.py's Greenhouse/Lever pattern but for Workday tenants: a
registry (known_workday.json) of `{tenant, wd_host, site}` triples, each polled
via `POST /wday/cxs/<tenant>/<site>/jobs`, with a per-job detail GET for the
full description and the public apply URL. Two tenants are seeded — GoodLife
Fitness (goodlifefitness.wd3/Careers, auto_apply=True, approved first) and CHEO
(cheo.wd10/External_Site, auto_apply=False until GoodLife proves the wizard
works in web_applier.py) — and the registry grows from any myworkdayjobs.com
URL seen elsewhere in the pipeline, same "never invent facts" rule as
known_boards.json: new tenants default to auto_apply=False until reviewed.
"""

import hashlib
import html
import json
import re
import time
from pathlib import Path
from typing import Optional

import requests

from job_sources import _is_ottawa_or_remote_location

KNOWN_WORKDAY_FILE = Path(__file__).parent / "known_workday.json"

WORKDAY_URL_RE = re.compile(r"https?://([a-z0-9\-]+)\.(wd\d+)\.myworkdayjobs\.com", re.IGNORECASE)

# Politeness delay between per-tenant/per-job API calls.
SLEEP_BETWEEN = 0.2
WORKDAY_TIMEOUT = 20
PAGE_SIZE = 20
MAX_PAGES = 5  # an Ottawa-scoped searchText rarely exceeds 100 results

DEFAULT_TENANTS = [
    {
        "tenant": "goodlifefitness",
        "wd_host": "wd3",
        "site": "Careers",
        "company_name": "GoodLife Fitness",
        "search_text": "Ottawa",
        "category": "goodlife",
        "auto_apply": True,
    },
    {
        "tenant": "cheo",
        "wd_host": "wd10",
        "site": "External_Site",
        "company_name": "CHEO",
        "search_text": "Ottawa",
        "category": "health",
        "auto_apply": False,
    },
]

# Health-informatics/health-data keywords for CHEO (and any newly discovered
# tenant) category tagging — same list job_agent.py's +2 priority boost uses,
# imported from here so the two stay in sync. "HIM" is checked case-sensitively
# and separately below since case-insensitive "him" is the English pronoun and
# would false-positive on nearly every job description.
_HEALTH_INFORMATICS_RE = re.compile(
    r"health information management|clinical informatics|health informatics|"
    r"\bemr\b|\behr\b|health data analyst|coding\s*(?:and|/)?\s*abstracting|"
    r"digital health|electronic (?:medical|health) record",
    re.IGNORECASE,
)
_HIM_CREDENTIAL_RE = re.compile(r"\bHIM\b")  # credential abbreviation, not the pronoun


def is_health_informatics_text(text: str) -> bool:
    text = text or ""
    return bool(_HEALTH_INFORMATICS_RE.search(text)) or bool(_HIM_CREDENTIAL_RE.search(text))


def make_id(title: str, company: str, url: str) -> str:
    raw = f"{title}|{company}|{url}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()[:14]


def _strip_html(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def load_known_workday() -> dict:
    if not KNOWN_WORKDAY_FILE.exists():
        return {"tenants": [dict(t) for t in DEFAULT_TENANTS]}
    try:
        data = json.loads(KNOWN_WORKDAY_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {"tenants": [dict(t) for t in DEFAULT_TENANTS]}
    data.setdefault("tenants", [])
    return data


def save_known_workday(data: dict):
    KNOWN_WORKDAY_FILE.write_text(json.dumps(data, indent=2, sort_keys=True))


def discover_workday_tenants_from_jobs(jobs: list) -> int:
    """Scan already-fetched job URLs for new *.myworkdayjobs.com tenants and add
    them to the registry with auto_apply=False. Mirrors
    ats_boards.discover_boards_from_jobs. The site segment ("Careers",
    "External_Site", ...) can't be recovered from a bare host match, so a new
    entry defaults to "Careers" and a human corrects it in known_workday.json
    if that tenant turns out to use a different site name."""
    data = load_known_workday()
    known = {(t["tenant"], t["wd_host"]) for t in data["tenants"]}
    added = 0

    for job in jobs:
        url = job.get("url", "") or ""
        m = WORKDAY_URL_RE.search(url)
        if not m:
            continue
        tenant, wd_host = m.group(1).lower(), m.group(2).lower()
        if (tenant, wd_host) in known:
            continue
        data["tenants"].append({
            "tenant": tenant,
            "wd_host": wd_host,
            "site": "Careers",
            "company_name": tenant,
            "search_text": "Ottawa",
            "category": "workday_direct",
            "auto_apply": False,
        })
        known.add((tenant, wd_host))
        added += 1

    if added:
        save_known_workday(data)

    return added


def _fetch_workday_jobs(tenant: str, wd_host: str, site: str, search_text: str) -> list:
    base = f"https://{tenant}.{wd_host}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
    postings = []
    offset = 0

    for _ in range(MAX_PAGES):
        try:
            resp = requests.post(
                base,
                json={"appliedFacets": {}, "limit": PAGE_SIZE, "offset": offset, "searchText": search_text},
                headers={"Content-Type": "application/json"},
                timeout=WORKDAY_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError):
            break

        batch = data.get("jobPostings") or []
        postings.extend(batch)
        total = data.get("total", len(postings))
        offset += PAGE_SIZE
        time.sleep(SLEEP_BETWEEN)
        if offset >= total or not batch:
            break

    return postings


def _fetch_workday_detail(tenant: str, wd_host: str, site: str, external_path: str) -> Optional[dict]:
    url = f"https://{tenant}.{wd_host}.myworkdayjobs.com/wday/cxs/{tenant}/{site}{external_path}"
    try:
        resp = requests.get(url, timeout=WORKDAY_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except (requests.RequestException, ValueError):
        return None


def _category_for(entry: dict, title: str, description: str) -> str:
    base_category = entry.get("category", "workday_direct")
    if base_category == "goodlife":
        return "goodlife"
    if is_health_informatics_text(f"{title} {description}"):
        return "health_informatics"
    if base_category == "health":
        return "health_other"
    return "workday_direct"


def _possible_categories(entry: dict) -> set:
    """Every category _category_for could return for this tenant. A scoped run
    filters tenants on this, because which category a posting actually lands in
    isn't known until its description has been fetched — and that fetch is the
    expensive part. Mirrors _category_for's branches; change both together."""
    base_category = entry.get("category", "workday_direct")
    if base_category == "goodlife":
        return {"goodlife"}
    if base_category == "health":
        return {"health_informatics", "health_other"}
    return {"health_informatics", "workday_direct"}


def _workday_to_job(entry: dict, wjob: dict, detail: Optional[dict]) -> Optional[dict]:
    title = str(wjob.get("title") or "").strip()
    external_path = str(wjob.get("externalPath") or "").strip()
    if not title or not external_path:
        return None

    locations_text = str(wjob.get("locationsText") or "").strip()

    # Workday's searchText is a full-text match, not a location filter, so
    # "Ottawa" also returns GoodLife's Hamilton club on Upper Ottawa St. Judge
    # this on locationsText alone — the title is exactly where the false match
    # comes from. Ambiguous internal labels ("Research 2") pass through, since
    # every posting from an Ottawa tenant is in Ottawa unless it says otherwise.
    if locations_text and not _is_ottawa_or_remote_location(locations_text):
        return None

    posted_on = str(wjob.get("postedOn") or "").strip()
    bullet_fields = wjob.get("bulletFields") or []

    detail_info = (detail or {}).get("jobPostingInfo") or {}
    description = _strip_html(detail_info.get("jobDescription") or "")[:4000]
    external_url = str(detail_info.get("externalUrl") or "").strip()
    job_req_id = str(detail_info.get("jobReqId") or (bullet_fields[0] if bullet_fields else "") or "")

    # Without externalUrl there is no real apply link to hand him — skip rather
    # than guess one from the search-result path.
    if not external_url:
        return None
    apply_url = f"{external_url}/apply"

    company_name = entry["company_name"]
    category = _category_for(entry, title, description)
    always_notify = category in ("goodlife", "health_informatics")
    target_club = category == "goodlife" and "queen and bank" in title.lower()

    job = {
        "id": make_id(title, company_name, job_req_id or external_path),
        "title": title,
        "company": company_name,
        "location": locations_text or "Ottawa, ON",
        "url": apply_url,
        "source": f"{company_name} (Workday)",
        "category": category,
        "apply_email": None,
        "description": description,
        "deadline": None,
        "posted_date": posted_on or None,
        "status": "open",
        "always_notify": always_notify,
        "apply_target": "employer_site",
        "ats": "workday",
        "workday_tenant": entry["tenant"],
        "workday_wd_host": entry["wd_host"],
        "workday_site": entry["site"],
        "workday_external_path": external_path,
    }
    if target_club:
        job["target_club"] = True
    return job


class WorkdaySource:
    def fetch_all(self, skip_ids: Optional[set] = None,
                  categories: Optional[set] = None) -> list:
        """Poll every registered Workday tenant directly and return jobs in the
        pipeline's shape. Unlike AtsBoardsSource, skip_ids IS used to skip the
        per-job detail fetch for postings already in seen_jobs.json — Workday
        needs one extra request per job for the description/apply URL, so
        skipping early on repeat runs meaningfully cuts request volume.
        Pass `categories` (e.g. {"goodlife"}) to scope a run, same as
        JobBankSource.fetch_all — tenants that can't produce one of them are
        skipped without a request."""
        skip_ids = skip_ids or set()
        tenants = load_known_workday().get("tenants", [])
        jobs = []

        for entry in tenants:
            if categories and not (_possible_categories(entry) & categories):
                continue
            tenant, wd_host, site = entry["tenant"], entry["wd_host"], entry["site"]
            print(f"[workday_source] {entry.get('company_name', tenant)} ({tenant}.{wd_host}/{site})...")
            try:
                postings = _fetch_workday_jobs(tenant, wd_host, site, entry.get("search_text", "Ottawa"))
            except requests.RequestException:
                continue

            for wjob in postings:
                title = str(wjob.get("title") or "").strip()
                external_path = str(wjob.get("externalPath") or "").strip()
                bullet_fields = wjob.get("bulletFields") or []
                job_req_id = str(bullet_fields[0]) if bullet_fields else ""
                if not title or not external_path:
                    continue

                prelim_id = make_id(title, entry["company_name"], job_req_id or external_path)
                if prelim_id in skip_ids:
                    continue

                time.sleep(SLEEP_BETWEEN)
                detail = _fetch_workday_detail(tenant, wd_host, site, external_path)
                job = _workday_to_job(entry, wjob, detail)
                if job:
                    jobs.append(job)

        # Dedup by id (defensive — pagination overlap or a company double-listing a role)
        seen_ids = set()
        unique = []
        for j in jobs:
            if j["id"] not in seen_ids:
                seen_ids.add(j["id"])
                unique.append(j)

        return unique


if __name__ == "__main__":
    for j in WorkdaySource().fetch_all():
        flag = " ★ TARGET CLUB" if j.get("target_club") else ""
        print(f"[{j['category']}] {j['title']} — {j['company']} ({j['location']}){flag}")
        print(f"    {j['url']}")
