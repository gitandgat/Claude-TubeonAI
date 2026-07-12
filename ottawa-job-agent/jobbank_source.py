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

BASE = "https://www.jobbank.gc.ca"
SEARCH_URL = BASE + "/jobsearch/jobsearch"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120 Safari/537.36"
)
HEADERS = {"User-Agent": UA}

# Job Bank searches take a single free-text string; keep these short and broad.
# category + always_notify mirror job_sources.CATEGORIES so downstream code is uniform.
QUERIES = [
    {"category": "crossing_guard", "q": "crossing guard"},
    {"category": "thai_embassy", "q": "consular embassy", "always_notify": True},
    {"category": "healthcare_pt", "q": "personal trainer"},
    {"category": "health_promotion", "q": "health promotion"},
    {"category": "outreach_sales", "q": "outreach coordinator"},
    {"category": "goodlife", "q": "fitness instructor", "always_notify": True},
    {"category": "business_startup", "q": "operations coordinator"},
    {"category": "admin_office", "q": "administrative assistant"},
    {"category": "customer_service", "q": "customer service"},
    {"category": "sustainability_nonprofit", "q": "community coordinator"},
    {"category": "general_labor", "q": "general labour"},
]

# Max postings resolved per category per run (bounds request volume + runtime).
MAX_PER_CATEGORY = 6
# Politeness delay between postings.
SLEEP_BETWEEN = 0.4

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
    low = location.lower()
    return "ottawa" in low or "remote" in low or "télétravail" in low or "teletravail" in low


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
    def fetch_all(self, skip_ids: Optional[set] = None) -> list:
        """Return Job Bank job dicts in the pipeline's shape. Pass `skip_ids` (already
        seen ids) to avoid spending reveal requests on jobs the pipeline will skip."""
        skip_ids = skip_ids or set()
        session = requests.Session()
        jobs = []
        seen_here = set()

        for spec in QUERIES:
            category = spec["category"]
            print(f"[jobbank] Searching: {category} ('{spec['q']}')...")
            try:
                params = {"searchstring": spec["q"], "locationstring": "Ottawa, ON", "sort": "D"}
                sr = session.get(SEARCH_URL, params=params, headers=HEADERS, timeout=30)
            except requests.RequestException as e:
                print(f"[jobbank]   search failed: {e}")
                continue
            if sr.status_code != 200:
                print(f"[jobbank]   search HTTP {sr.status_code}")
                continue

            resolved = 0
            for card in _parse_cards(sr.text):
                if resolved >= MAX_PER_CATEGORY:
                    break
                if not _is_ottawa_or_remote(card["location"]):
                    continue

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

                if route["mode"] == "email":
                    job["apply_email"] = route["email"]
                    job["source"] = "Job Bank (email)"
                elif route["mode"] == "external":
                    job["url"] = route["url"]
                    job["jobbank_url"] = posting_url
                    job["source"] = "Job Bank -> company site"
                else:
                    job["no_auto_apply"] = True
                    job["no_apply_reason"] = route["reason"]
                    job["jobbank_direct_apply"] = route.get("direct_apply", False)

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
