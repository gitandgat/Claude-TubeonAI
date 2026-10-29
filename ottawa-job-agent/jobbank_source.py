"""Job discovery from Canada's Job Bank (jobbank.gc.ca).

Unlike LinkedIn/Indeed/Glassdoor (Cloudflare-defended, and their apply flows need
YOUR logged-in account — automating that risks getting the account banned), Job Bank
is a government site that serves real Ottawa listings with no bot-check and, for most
postings, tells you exactly how to apply. This module scrapes the search results and,
per posting, resolves the real apply method via Job Bank's own "Show how to apply"
reveal, then routes each job so the existing pipeline can act on it honestly:

  - a real application email  -> job["apply_email"] set  -> pipeline's email-apply path
  - an external employer/ATS  -> job["url"] = that link  -> pipeline's web-apply path
  - an aggregator repost (Indeed/ZipRecruiter/etc.), Job Bank "Direct Apply" (needs
    the applicant's sign-in), or in-person/mail/phone only -> flagged no_auto_apply so
    the pipeline surfaces it FYI with the link instead of faking an application.

The "Show how to apply" reveal is a stateless JSF ajax postback (ViewState is the
literal string "stateless", so there is no per-request token to scrape) — see
_reveal_apply_method for the exact call.
"""

import hashlib
import html
import re
import time
from datetime import date
from typing import Optional

import requests

from employer_site import is_job_board_url
from job_sources import _OTTAWA_AREA_TERMS
from workday_source import is_health_informatics_text

BASE = "https://www.jobbank.gc.ca"
SEARCH_URL = BASE + "/jobsearch/jobsearch"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120 Safari/537.36"
)
HEADERS = {"User-Agent": UA}

# Job Bank searches take a single free-text string over NOC titles, and the
# matching is quirky: probed 2026-09-07 with the real city filter, "health
# information", "medical records" and "fitness instructor" return zero Ottawa
# cards while "informatics", "data analyst" and "fitness" return real ones. A
# category that starved on one string therefore carries a list ("queries") that
# is run in turn and deduped under one per-category resolve cap; a single "q"
# is still fine for the broad ones. Keep every string short.
# category + always_notify mirror job_sources.CATEGORIES so downstream code is uniform.
QUERIES = [
    {"category": "crossing_guard", "q": "crossing guard"},
    {"category": "thai_embassy", "q": "consular embassy", "always_notify": True},
    {"category": "healthcare_pt", "queries": ["personal trainer", "kinesiologist"]},
    {"category": "health_promotion", "queries": ["health promotion", "health educator", "community health"]},
    {"category": "health_informatics", "always_notify": True,
     "queries": ["health informatics", "informatics", "data analyst", "clinical informatics", "database"]},
    {"category": "outreach_sales", "q": "outreach coordinator"},
    # "fitness advisor" is GoodLife's own title but Job Bank fuzzes "advisor" into
    # attorneys and corporate counsel (7 of 8 hits, 2026-09-07) — left out.
    {"category": "goodlife", "queries": ["fitness instructor", "fitness"], "always_notify": True},
    {"category": "business_startup", "q": "operations coordinator"},
    {"category": "admin_office", "q": "administrative assistant"},
    {"category": "customer_service", "q": "customer service"},
    {"category": "hospitality_hotel", "q": "hotel front desk", "always_notify": True},
    {"category": "sustainability_nonprofit", "q": "community coordinator"},
    {"category": "general_labor", "q": "general labour"},
]


def queries_for(spec: dict) -> list:
    """A category's search strings: `queries` when it has several, else `[q]`."""
    return list(spec.get("queries") or [spec["q"]])

# always_notify makes a posting bypass MIN_SCORE entirely, so it has to be earned.
# A Job Bank search is loose full text over NOC titles, not a classification: the
# "consular embassy" query returns a PSW at *Embassy West Senior Living*, "health
# informatics" returns a pathologists' assistant at a bakery, and Chipotle service
# leaders come back under the NOC title "manager, hotel front office". Same lesson
# as the Workday location filter — a search match is a hint, and the bucket label
# has to be confirmed against the posting before anything downstream trusts it.
#
# Only the four always_notify buckets need an entry; every other category is
# score-gated already. `fields` names what to confirm against, because for hotels
# the NOC *title* is exactly where the false match comes from (see above), so that
# one is judged on company + description alone.
_ALL_FIELDS = ("title", "company", "description")
_NOT_TITLE = ("company", "description")

_ALWAYS_NOTIFY_CONFIRM = {
    # The Serper query for this category names the Royal Thai Embassy outright;
    # Job Bank's "consular embassy" can't, so require diplomatic context.
    "thai_embassy": (re.compile(r"thai|consular|consulate|diplomatic|high commission",
                                re.IGNORECASE), _ALL_FIELDS),
    # One definition of the health-data track across every source.
    "health_informatics": (None, _ALL_FIELDS),
    "goodlife": (re.compile(r"fitness|trainer|instructor|gym|wellness|coach|yoga|pilates",
                            re.IGNORECASE), _ALL_FIELDS),
    "hospitality_hotel": (re.compile(r"hotel|motel|inn\b|resort|hospitality|front desk|"
                                     r"guest service|concierge", re.IGNORECASE), _NOT_TITLE),
}


def _confirms_always_notify(category: str, job: dict) -> bool:
    """Does the posting actually back up the always_notify claim its search bucket
    made? Unknown categories are trusted as-is — this only guards the loose ones."""
    rule = _ALWAYS_NOTIFY_CONFIRM.get(category)
    if rule is None:
        return True
    pattern, fields = rule
    text = " ".join(str(job.get(f) or "") for f in fields)
    if pattern is None:  # health track owns its own matcher
        return is_health_informatics_text(text)
    return bool(pattern.search(text))

# Max postings resolved per category per run (bounds request volume + runtime).
# Raised from 6 (2026-09-02): with Serper permanently off, Job Bank + ATS Direct
# are the only two sources left, so each category's Ottawa/remote-filtered results
# get pulled deeper before the per-category cap kicks in.
MAX_PER_CATEGORY = 10
# Politeness delay between postings.
SLEEP_BETWEEN = 0.4

# Job Bank's real city filter. `locationstring` is only the human-readable echo
# of what you typed — the actual server-side filter is `locationparam`, an
# internal numeric location id that the search page's typeahead fills in behind
# the scenes when you pick a suggestion. Captured 2026-09-04 with Playwright:
# loaded /jobsearch/, dismissed the on-load modal, typed "Ottawa", clicked the
# "Ottawa, ON" suggestion, and read the hidden field — locationparam=22409.
# Verified with plain requests the same day: results come back Ottawa/Orleans/
# Nepean/Gatineau/Kemptville instead of the nationwide Toronto/Kingston/
# Burlington mix that locationstring+fprov=ON returned. Re-capture with
# scripts/ or the same Playwright recipe if Job Bank ever renumbers its ids.
OTTAWA_LOCATION_PARAM = "22409"

# Job Bank pages 25 cards at a time and simply returns an empty result list past
# the end, so the loop stops on the first empty page rather than always burning
# five requests. Five is the ceiling, not the target.
MAX_SEARCH_PAGES = 5

# How many cards to collect per category relative to MAX_PER_CATEGORY, so the
# already-seen filter has headroom before the expensive resolve loop starts.
CARD_OVERSAMPLE = 3

# External destinations we can't honestly auto-apply to: aggregators that block bots,
# and social/auth hosts. A reveal pointing here is surfaced FYI, never web-applied.
BLOCKED_HOSTS = (
    "indeed.com", "ziprecruiter.com", "glassdoor.", "linkedin.com",
    "guichetemplois.gc.ca", "jobbank.gc.ca", "canada.ca", "facebook.com",
    "twitter.com", "x.com", "youtube.com", "instagram.com",
)


def make_id(title: str, company: str, url: str) -> str:
    raw = f"{title}|{company}|{url}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()[:14]


def _clean(fragment: Optional[str]) -> str:
    if not fragment:
        return ""
    text = re.sub(r"<[^>]+>", " ", html.unescape(fragment))
    return re.sub(r"\s+", " ", text).strip()


def _is_ottawa_or_remote(location: str) -> bool:
    """Job Bank labels real Ottawa-area postings by their own municipality —
    "Orleans South (ON)", "Nepean (ON)", "Gatineau (QC)" — so matching only the
    literal "ottawa" dropped genuine walk/transit-range jobs. Share
    job_sources._OTTAWA_AREA_TERMS so both sources agree on what counts as the
    Ottawa area; the commute classifier de-ranks the far suburbs afterwards
    instead of this filter silently losing them."""
    low = location.lower()
    if "remote" in low or "télétravail" in low or "teletravail" in low:
        return True
    return any(term in low for term in _OTTAWA_AREA_TERMS)


def _parse_cards(search_html: str) -> list:
    """Pull the structured fields out of each result <article> on a search page."""
    cards = []
    for art in re.findall(r"<article[\s\S]*?</article>", search_html):
        pid_m = re.search(r"/jobsearch/jobposting/([0-9]+)", art)
        title_m = re.search(r'<span class="noctitle">(.*?)</span>', art, re.S)
        if not pid_m or not title_m:
            continue
        biz_m = re.search(r'<li class="business">(.*?)</li>', art, re.S)
        loc = re.search(r'<li class="location">(.*?)</li>', art, re.S)
        sal = re.search(r'<li class="salary">(.*?)</li>', art, re.S)
        biz = _clean(biz_m.group(1)) if biz_m else ""
        location = _clean(loc.group(1)).replace("Location", "").strip() if loc else ""
        salary = _clean(sal.group(1)).replace("Salary", "").strip() if sal else ""
        cards.append({
            "pid": pid_m.group(1),
            "title": _clean(title_m.group(1)),
            "company": biz or "Unknown",
            "location": location or "Ottawa, ON",
            "salary": salary,
        })
    return cards


def _search_ottawa_cards(session: requests.Session, query: str, want: int) -> list:
    """Paginate the search until `want` Ottawa-area cards are collected or the
    results run out.

    Page 1 alone is not enough even with the real city filter: a broad query
    spreads its Ottawa results across two or three pages, and Job Bank sorts by
    date, not distance. Stops early on the first empty page (Job Bank returns
    zero cards past the end rather than an error), so a narrow query still costs
    one request, not five.
    """
    cards = []
    for page in range(1, MAX_SEARCH_PAGES + 1):
        params = {
            "searchstring": query,
            "locationstring": "Ottawa, ON",
            "locationparam": OTTAWA_LOCATION_PARAM,
            "sort": "D",
            "page": page,
        }
        try:
            sr = session.get(SEARCH_URL, params=params, headers=HEADERS, timeout=30)
        except requests.RequestException as e:
            print(f"[jobbank]   search page {page} failed: {e}")
            break
        if sr.status_code != 200:
            print(f"[jobbank]   search page {page} HTTP {sr.status_code}")
            break

        page_cards = _parse_cards(sr.text)
        if not page_cards:
            break
        cards.extend(c for c in page_cards if _is_ottawa_or_remote(c["location"]))
        if len(cards) >= want:
            break
        time.sleep(SLEEP_BETWEEN)

    return cards[:want]


def _fetch_detail(session: requests.Session, pid: str) -> str:
    url = f"{BASE}/jobsearch/jobposting/{pid}"
    r = session.get(url, headers=HEADERS, timeout=30)
    return r.text if r.status_code == 200 else ""


def _extract_description(detail_html: str, fallback: str) -> str:
    m = re.search(r'property="description"[^>]*>([\s\S]*?)</div>', detail_html)
    text = _clean(m.group(1)) if m else ""
    return text[:1500] if text else fallback


def _extract_deadline(detail_html: str) -> Optional[str]:
    m = re.search(r'property="validThrough"[^>]*>\s*([0-9]{4}-[0-9]{2}-[0-9]{2})', detail_html)
    return m.group(1) if m else None


def _reveal_apply_method(session: requests.Session, pid: str) -> str:
    """Fire Job Bank's stateless-JSF "Show how to apply" reveal and return the HTML
    fragment describing how to apply (email / external link / sign-in / in-person)."""
    posturl = f"{BASE}/jobsearch/jobposting/{pid}"
    data = {
        "seekeractivity": "seekeractivity",
        "seekeractivity:jobid": pid,
        "jakarta.faces.ViewState": "stateless",
        "jakarta.faces.source": "applynowbutton",
        "jakarta.faces.partial.ajax": "true",
        "jakarta.faces.partial.execute": "jobid",
        "jakarta.faces.partial.render": "applynow markappliedgroup",
        "applynowbutton": "applynowbutton",
    }
    headers = dict(HEADERS)
    headers.update({
        "Faces-Request": "partial/ajax",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": posturl,
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    })
    try:
        r = session.post(posturl, headers=headers, data=data, timeout=30)
        return html.unescape(r.text) if r.status_code == 200 else ""
    except requests.RequestException:
        return ""


def _classify_apply(reveal_html: str) -> dict:
    """Turn the reveal fragment into a routing decision.

    Returns one of:
      {"mode": "email", "email": "..."}                      -> email-apply path
      {"mode": "external", "url": "https://..."}             -> web-apply path
      {"mode": "manual", "reason": "..."}                    -> FYI only
    """
    low = reveal_html.lower()

    mailto = re.search(r"mailto:([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})", reveal_html)
    if mailto:
        return {"mode": "email", "email": mailto.group(1)}
    plain_email = re.search(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", reveal_html)
    if plain_email and ("by email" in low or "par courriel" in low):
        return {"mode": "email", "email": plain_email.group(0)}

    for href in re.findall(r'href=["\']?(https?://[^"\'>\s]+)', reveal_html):
        host = href.split("/")[2].lower() if "://" in href else ""
        if any(b in host for b in BLOCKED_HOSTS):
            continue
        return {"mode": "external", "url": href}

    if "sign in" in low or "direct apply" in low:
        return {"mode": "manual", "reason": "Job Bank Direct Apply — requires your Job Bank sign-in",
                "direct_apply": True}
    if "indeed" in low or "ziprecruiter" in low or "glassdoor" in low:
        return {"mode": "manual", "reason": "reposted from a bot-blocked aggregator — apply on the posting directly"}
    for label, phrase in (("in person", "in person"), ("by mail", "by mail"),
                          ("by fax", "by fax"), ("by phone", "by phone")):
        if phrase in low:
            return {"mode": "manual", "reason": f"posting accepts applications {label} only"}
    return {"mode": "manual", "reason": "no automatable apply method on the posting"}


class JobBankSource:
    def fetch_all(self, skip_ids: Optional[set] = None, categories: Optional[set] = None) -> list:
        """Return Job Bank job dicts in the pipeline's shape. Pass `skip_ids` (already
        seen ids) to avoid spending reveal requests on jobs the pipeline will skip.
        Pass `categories` (e.g. {"hospitality_hotel"}) to scope a run to specific
        categories instead of every entry in QUERIES."""
        skip_ids = skip_ids or set()
        session = requests.Session()
        jobs = []
        seen_here = set()

        for spec in QUERIES:
            category = spec["category"]
            if categories and category not in categories:
                continue
            queries = queries_for(spec)
            print(f"[jobbank] Searching: {category} ({', '.join(repr(q) for q in queries)})...")
            # Oversample the card list: already-seen postings are cheap to skip
            # but still consume supply, so collecting only MAX_PER_CATEGORY
            # cards would leave a category short of new jobs on the second run
            # of the day. The expensive per-posting work below is still capped.
            # Several queries for one category share that cap and dedupe on
            # posting id, so a card that two queries both return is resolved once.
            search_cards, seen_pids = [], set()
            for query in queries:
                for card in _search_ottawa_cards(session, query, MAX_PER_CATEGORY * CARD_OVERSAMPLE):
                    if card["pid"] not in seen_pids:
                        seen_pids.add(card["pid"])
                        search_cards.append(card)

            resolved = 0
            for card in search_cards:
                if resolved >= MAX_PER_CATEGORY:
                    break

                posting_url = f"{BASE}/jobsearch/jobposting/{card['pid']}"
                job_id = make_id(card["title"], card["company"], posting_url)
                if job_id in skip_ids or job_id in seen_here:
                    continue
                seen_here.add(job_id)

                detail = _fetch_detail(session, card["pid"])
                fallback_desc = f"{card['title']} at {card['company']}. {card['salary']}".strip()
                reveal = _reveal_apply_method(session, card["pid"])
                route = _classify_apply(reveal)
                # The reveal for a Direct Apply posting doesn't expand for logged-out
                # users; the sign-in prompt lives in the detail page. Give it an
                # accurate FYI reason instead of the generic fallback.
                if route["mode"] == "manual" and "sign in to apply directly" in detail.lower():
                    route = {"mode": "manual",
                             "reason": "Job Bank Direct Apply — requires your Job Bank sign-in",
                             "direct_apply": True}
                resolved += 1
                time.sleep(SLEEP_BETWEEN)

                job = {
                    "id": job_id,
                    "title": card["title"],
                    "company": card["company"],
                    "location": card["location"],
                    "url": posting_url,
                    "source": "Job Bank",
                    "category": category,
                    "apply_email": None,
                    "description": _extract_description(detail, fallback_desc),
                    "deadline": _extract_deadline(detail),
                    "posted_date": None,
                    "status": "open",
                    "always_notify": spec.get("always_notify", False),
                    "salary": card["salary"],
                }

                # The search bucket claimed always_notify; the posting itself has
                # to back that up before it gets to skip MIN_SCORE.
                if job["always_notify"] and not _confirms_always_notify(category, job):
                    job["always_notify"] = False

                # apply_target tells job_agent.py where the application actually
                # has to happen, so employer_site.resolve_employer_apply_url()
                # doesn't have to re-derive it from the mutated `source` string.
                # Only the third branch is a genuine Job Bank Direct Apply — the
                # reveal handed us an employer email or an employer site in the
                # other two, which is exactly the "employer first" route.
                if route["mode"] == "email":
                    job["apply_email"] = route["email"]
                    job["source"] = "Job Bank (email)"
                    job["apply_target"] = "employer_site"
                elif route["mode"] == "external":
                    job["url"] = route["url"]
                    job["jobbank_url"] = posting_url
                    job["source"] = "Job Bank -> company site"
                    # The reveal sometimes points at *another* aggregator
                    # (Jobillico, lavente.ca) instead of the employer's own
                    # site — confirmed in a live run. Same host rule as the
                    # resolver so both agree on what is worth a real attempt.
                    job["apply_target"] = (
                        "job_board" if is_job_board_url(route["url"]) else "employer_site"
                    )
                else:
                    job["no_auto_apply"] = True
                    job["no_apply_reason"] = route["reason"]
                    job["jobbank_direct_apply"] = route.get("direct_apply", False)
                    job["apply_target"] = "jobbank_direct"

                jobs.append(job)

            print(f"  -> {resolved} resolved")

        return jobs


if __name__ == "__main__":
    # Read-only smoke test: prints what it finds, never applies to anything.
    sample = JobBankSource().fetch_all()
    from collections import Counter
    tally = Counter(j["source"] for j in sample)
    print(f"\n=== {len(sample)} Job Bank jobs ===")
    for j in sample:
        route = (f"email:{j['apply_email']}" if j.get("apply_email")
                 else (f"site:{j['url']}" if j["source"].endswith("company site")
                       else f"FYI:{j.get('no_apply_reason', '')}"))
        print(f"- [{j['category']}] {j['title']} @ {j['company']} ({j['location']}) -> {route}")
    print("TALLY", dict(tally))
