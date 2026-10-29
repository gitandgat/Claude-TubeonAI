"""Resolve each job's real, employer-hosted apply URL before any Playwright attempt.

Job boards and ATS aggregators are discovery surfaces, not application targets —
Indeed/ZipRecruiter/CareerBeacon/etc bot-wall their forms, and a listing scraped
from one of those is never the employer's own page. Before job_agent.py spends a
Playwright attempt on a URL, this module checks whether the job's company is
already a known Greenhouse/Lever board (known_boards.json) or Workday tenant
(known_workday.json) and, if so, finds the SAME posting through that platform's
own API and hands back its real, employer-hosted URL instead of whatever
job-board mirror the job was originally discovered on.

Jobs already sourced directly from ats_boards.py or workday_source.py carry their
true employer URL from the moment they're fetched (their `url` IS the Greenhouse
absolute_url / Lever hostedUrl / Workday externalUrl) — this resolver short-
circuits for those instead of re-fetching a board it already just polled.

Everything else (Serper/job_sources.py results, Job Bank listings) gets the
registry lookup. A job whose company doesn't match any known board/tenant keeps
its original URL, tagged "employer_site" unless the host is a known aggregator
(web_applier._BOARD_DOMAINS), in which case it's tagged "job_board" so
job_agent.py can skip the Playwright attempt entirely instead of running it
against a page that almost always bot-walls. Job Bank listings that don't match
a known employer board fall back to "jobbank_direct" — Job Bank's own Direct
Apply flow stays the last resort, per the plan, not the first choice.
"""

import re
from typing import Optional
from urllib.parse import urlparse

from ats_boards import _fetch_greenhouse_board, _fetch_lever_board, load_known_boards
from workday_source import _fetch_workday_jobs, load_known_workday

# Sources that already resolve to the employer's own hosted posting at fetch time —
# re-running the registry lookup for these would just re-fetch the same board for
# the same answer.
_ALREADY_RESOLVED_SOURCES = {"ATS Direct"}

# Discovery-only aggregators — never an apply target, per the plan's design
# principles. Deliberately narrower than web_applier._BOARD_DOMAINS: that regex
# also matches greenhouse/lever.co/myworkdayjobs/icims because those hosted pages
# should never receive a scraped *contact email* either, but those four ARE
# real, fillable ATS platforms (web_applier.detect_ats already knows how to fill
# them) — tagging a first-seen Greenhouse/Lever/Workday posting "job_board" here
# would wrongly skip a Playwright attempt the pipeline is fully capable of
# completing. Job Bank is excluded too: it gets its own "jobbank_direct" tag
# below, since Job Bank's Direct Apply flow is a last resort, not a dead end.
_AGGREGATOR_DOMAINS = re.compile(
    r"charityvillage|indeed|glassdoor|ziprecruiter|linkedin|workopolis"
    r"|jobillico|careerbeacon|simplyhired|monster|talent\.com|jobgether"
    r"|jobs\.ca|eluta|cercottawa"
    # Quebec-side aggregators, added 2026-09-04 after a live Job Bank run
    # surfaced Gatineau postings whose "apply here" reveal pointed at these
    # rather than at the employer's own site.
    r"|lavente\.ca|emploisadmin|quebecemploi"
    # Found in the Sep 29 2026 backlog sweep: both republish other employers'
    # postings under their own URL, so several tracked entries shared one link
    # (bebee carried a "Tea & Toast Inc" role, remoterocketship three variants of
    # one operations-coordinator listing). Staffing firms that post their own
    # mandates -- Robert Half, Randstad -- are deliberately NOT here: their
    # job-details pages are real, applyable postings.
    r"|bebee|remoterocketship",
    re.I,
)


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


def _title_matches(a: str, b: str) -> bool:
    norm = lambda s: re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()
    return norm(a) == norm(b)


def _company_matches(company: str, candidate: str) -> bool:
    return bool(company) and bool(candidate) and _normalize(company) == _normalize(candidate)


def _find_on_greenhouse(token: str, title: str) -> Optional[str]:
    for gjob in _fetch_greenhouse_board(token):
        if _title_matches(str(gjob.get("title") or ""), title):
            url = str(gjob.get("absolute_url") or "").strip()
            if url:
                return url
    return None


def _find_on_lever(token: str, title: str) -> Optional[str]:
    for posting in _fetch_lever_board(token):
        if _title_matches(str(posting.get("text") or ""), title):
            url = str(posting.get("hostedUrl") or "").strip()
            if url:
                return url
    return None


def _find_on_workday(entry: dict, title: str) -> Optional[str]:
    postings = _fetch_workday_jobs(
        entry["tenant"], entry["wd_host"], entry["site"], entry.get("search_text", "Ottawa")
    )
    for wjob in postings:
        if _title_matches(str(wjob.get("title") or ""), title):
            external_path = str(wjob.get("externalPath") or "").strip()
            if external_path:
                return (
                    f"https://{entry['tenant']}.{entry['wd_host']}.myworkdayjobs.com"
                    f"/{entry['site']}{external_path}"
                )
    return None


def _match_known_registries(company: str, title: str) -> Optional[str]:
    boards = load_known_boards()
    for token in boards.get("greenhouse", []):
        if _company_matches(company, token.replace("-", " ").replace("_", " ")):
            match = _find_on_greenhouse(token, title)
            if match:
                return match

    for token in boards.get("lever", []):
        if _company_matches(company, token.replace("-", " ").replace("_", " ")):
            match = _find_on_lever(token, title)
            if match:
                return match

    for entry in load_known_workday().get("tenants", []):
        if _company_matches(company, entry.get("company_name", "")) or _company_matches(company, entry["tenant"]):
            match = _find_on_workday(entry, title)
            if match:
                return match

    return None


def is_job_board_url(url: str) -> bool:
    """True when the URL's host is a discovery aggregator rather than a real
    apply target. Public because discovery modules tag `apply_target` at fetch
    time and must use the same rule this resolver does — a job routed one way
    here and another way there is how a Playwright attempt ends up pointed at a
    bot-check page."""
    return bool(_AGGREGATOR_DOMAINS.search(urlparse(url).netloc.lower()))


def resolve_employer_apply_url(job: dict) -> dict:
    """Returns {apply_url, apply_target}. Never mutates `job` — the caller merges
    the result in. apply_url is always a string: the resolved employer posting
    when a registry match is found, otherwise the job's original url unchanged."""
    original_url = job.get("url", "") or ""

    if job.get("apply_target"):
        return {"apply_url": original_url, "apply_target": job["apply_target"]}

    if job.get("source") in _ALREADY_RESOLVED_SOURCES:
        return {"apply_url": original_url, "apply_target": "employer_site"}

    company = job.get("company", "") or ""
    title = job.get("title", "") or ""
    is_jobbank = job.get("source") == "Job Bank"

    match = _match_known_registries(company, title)
    if match:
        return {"apply_url": match, "apply_target": "employer_site"}

    if is_jobbank:
        return {"apply_url": original_url, "apply_target": "jobbank_direct"}

    if not original_url or is_job_board_url(original_url):
        return {"apply_url": original_url, "apply_target": "job_board"}

    return {"apply_url": original_url, "apply_target": "employer_site"}


if __name__ == "__main__":
    samples = [
        {"company": "GoodLife Fitness", "title": "Personal Trainer - Ottawa Queen and Bank",
         "url": "https://www.indeed.com/some-mirror", "source": "Web Search"},
        {"company": "City of Ottawa", "title": "Some Role That Wont Match", "url": "https://jobs.ca/foo",
         "source": "Web Search"},
        {"company": "Random Local Cafe", "title": "Barista", "url": "https://randomcafe.example.com/careers/1",
         "source": "Web Search"},
        {"company": "Random Co", "title": "Admin Assistant", "url": "https://www.jobbank.gc.ca/some-posting",
         "source": "Job Bank"},
    ]
    for j in samples:
        result = resolve_employer_apply_url(j)
        print(f"[{result['apply_target']:>13}] {j['company']} — {j['title']}\n    {result['apply_url']}")
