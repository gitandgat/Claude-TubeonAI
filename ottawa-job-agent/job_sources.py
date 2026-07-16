"""Job discovery via Serper.dev (Google Search API) + local Ollama structuring.

Searches multiple job categories in Ottawa, parses structured results, and
returns a deduplicated list of job dicts. Previously used Claude's hosted
web_search tool, which could fetch and read a full posting page in one step.
Serper only returns SERP snippets, so a separate free local-model pass
(Ollama) turns those snippets into the same job schema downstream code
already expects. Fields that used to come from reading the full page —
apply_email, deadline, posted_date — will be null/"unknown" more often now
since a snippet rarely contains them; that's an honest quality trade for a
$0 pipeline, not a bug.
"""

import hashlib
import json
import os
import re
from datetime import date
from typing import Optional

from ollama_client import OllamaClient
from serper_client import SerperClient, SerperCreditsExhausted

CATEGORIES = [
    {
        "category": "crossing_guard",
        "query": "crossing guard school crossing traffic safety jobs Ottawa Ontario Canada site:indeed.ca OR site:jobbank.gc.ca OR site:ottawasafetycouncil.ca OR site:jobs.ottawa.ca OR site:linkedin.com/jobs 2025 2026",
        "extra_query": "\"crossing guard\" OR \"school crossing guard\" Ottawa Ontario jobs hiring",
    },
    {
        "category": "thai_embassy",
        "query": "Royal Thai Embassy Ottawa jobs vacancy hiring position 2025 2026",
        "always_notify": True,
    },
    {
        "category": "healthcare_pt",
        "query": "personal trainer health coach wellness coordinator fitness instructor community health Ottawa Ontario jobs 2025 2026",
        "extra_query": "\"personal trainer\" OR \"health coach\" OR \"wellness\" Ottawa Ontario job posting",
        "ats_query": "\"personal trainer\" OR \"health coach\" OR \"wellness coordinator\" (site:boards.greenhouse.io OR site:jobs.lever.co)",
    },
    {
        "category": "health_promotion",
        "query": "health promotion specialist health educator public health educator community health promoter wellness program coordinator Ottawa Public Health CHEO community health centre Ottawa Ontario jobs 2025 2026",
        "extra_query": "\"health promotion\" OR \"health educator\" OR \"health promotion specialist\" Ottawa Ontario Canadian Cancer Society OR \"Heart and Stroke\" OR \"Diabetes Canada\" OR university jobs hiring",
        "ats_query": "\"health promotion\" OR \"health educator\" OR \"community health\" (site:boards.greenhouse.io OR site:jobs.lever.co)",
    },
    {
        "category": "outreach_sales",
        "query": "outreach coordinator community outreach health sales representative business development community liaison Ottawa Ontario jobs 2025 2026",
        "extra_query": "\"outreach\" OR \"sales representative\" Ottawa Ontario healthcare community job",
        "ats_query": "\"outreach coordinator\" OR \"business development\" OR \"sales representative\" (site:boards.greenhouse.io OR site:jobs.lever.co)",
    },
    {
        "category": "goodlife",
        "query": "GoodLife Fitness careers jobs Ottawa Ontario personal trainer membership advisor group fitness front desk 2025 2026 site:workatgoodlife.ca OR site:goodlifefitness.com OR site:indeed.ca",
        "extra_query": "GoodLife Fitness Ottawa hiring any position job opening",
        "always_notify": True,
    },
    {
        "category": "business_startup",
        "query": "business operations coordinator OR administrative coordinator OR junior business analyst OR entry-level business development OR startup operations associate jobs Ottawa Ontario Canada OR remote Canada 2025 2026",
        "extra_query": "\"operations coordinator\" OR \"business development\" OR \"startup\" jobs Ottawa OR remote Canada hiring",
        "ats_query": "\"operations coordinator\" OR \"business development\" OR \"startup\" (site:boards.greenhouse.io OR site:jobs.lever.co)",
    },
    {
        "category": "admin_office",
        "query": "administrative assistant OR executive assistant OR office administrator OR virtual assistant OR data entry clerk OR medical office assistant jobs Ottawa Ontario Canada OR remote Canada 2025 2026",
        "extra_query": "\"administrative assistant\" OR \"virtual assistant\" OR \"data entry\" Ottawa OR remote Canada job posting hiring",
        "ats_query": "\"administrative assistant\" OR \"executive assistant\" OR \"virtual assistant\" (site:boards.greenhouse.io OR site:jobs.lever.co)",
    },
    {
        "category": "customer_service",
        "query": "customer service representative OR client support specialist OR customer success associate OR call centre representative jobs Ottawa Ontario Canada OR remote Canada 2025 2026",
        "extra_query": "\"customer service\" OR \"customer support\" Ottawa OR remote Canada hiring day shift",
        "ats_query": "\"customer service representative\" OR \"customer support\" OR \"customer success\" (site:boards.greenhouse.io OR site:jobs.lever.co)",
    },
    {
        "category": "sustainability_nonprofit",
        "query": "sustainability coordinator OR environmental program coordinator OR nonprofit program coordinator OR community engagement coordinator OR volunteer coordinator jobs Ottawa Ontario Canada OR remote Canada 2025 2026",
        "extra_query": "\"sustainability\" OR \"environmental\" OR \"nonprofit\" OR \"community engagement\" Ottawa OR remote Canada hiring coordinator",
        "ats_query": "\"sustainability coordinator\" OR \"nonprofit program coordinator\" OR \"community engagement\" (site:boards.greenhouse.io OR site:jobs.lever.co)",
    },
    {
        "category": "general_labor",
        "query": "warehouse associate OR general labourer OR delivery driver OR retail associate OR landscaping labourer jobs Ottawa Ontario Canada 2025 2026 day shift",
        "extra_query": "\"warehouse\" OR \"general labour\" OR \"retail associate\" Ottawa Ontario day shift hiring",
        "ats_query": "\"warehouse associate\" OR \"general labourer\" OR \"retail associate\" (site:boards.greenhouse.io OR site:jobs.lever.co)",
    },
]

STRUCTURE_PROMPT = """Below are raw Google search results for the query: {query}

Extract ONLY real, currently open, individual job postings from these results and
return ONLY a JSON array. Each object must have exactly these keys:
  - title, company, location, url, description
  - apply_email: an email address ONLY if one appears explicitly in the text below, else null
  - deadline: the application closing date in YYYY-MM-DD format ONLY if explicitly stated below, else null
  - posted_date: YYYY-MM-DD ONLY if stated below, else null
  - status: "closed" if the text says the posting is expired/filled, otherwise "unknown"

Rules:
- Include only jobs that are either (a) in-person in Ottawa, Ontario, Canada, or (b) fully
  remote/work-from-home roles open to candidates anywhere in Canada. Skip anything in-person
  based in another city.
- Skip anything the text says is night-shift-only, overnight-only, or graveyard-shift-only.
- Today's date is {today}. Skip anything the text explicitly says is expired, closed, or filled.
- Skip results that aren't actual individual job postings (e.g. general careers pages with no
  specific role, news articles, review sites).
- Never invent facts that aren't in the text below — use null or "unknown" when something isn't stated.
Return [] if nothing qualifies. Output ONLY the JSON array — no commentary before or after.

Search results:
{results_text}
"""


def make_id(title: str, company: str, url: str) -> str:
    raw = f"{title}|{company}|{url}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()[:14]


def extract_email(text: str) -> Optional[str]:
    m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return m.group() if m else None


def _format_results(raw_results: list) -> str:
    lines = []
    for r in raw_results:
        lines.append(
            f"- Title: {r.get('title', '')}\n"
            f"  URL: {r.get('link', '')}\n"
            f"  Snippet: {r.get('snippet', '')}\n"
            f"  Date: {r.get('date', 'unknown')}"
        )
    return "\n".join(lines)


def _structure_jobs(ollama: OllamaClient, raw_results: list, query: str) -> list:
    """Turn raw Serper snippets into the job schema via the local model. Tolerant
    of bad/partial model output — returns [] rather than raising, matching the
    same honest-fallback behavior job_agent.py already expects from this source."""
    if not raw_results:
        return []

    prompt = STRUCTURE_PROMPT.format(
        query=query, today=date.today().isoformat(), results_text=_format_results(raw_results)
    )
    try:
        text = ollama.generate(prompt, max_tokens=2500)
    except RuntimeError as e:
        print(f"[job_sources] Ollama structuring error: {e}")
        return []

    json_match = re.search(r"\[[\s\S]*\]", text)
    if not json_match:
        return []
    try:
        return json.loads(json_match.group())
    except json.JSONDecodeError:
        return []


class JobSources:
    def __init__(self):
        # Set when Serper reports the account is out of credits, so job_agent.py
        # can surface a clear alert in the daily digest instead of the run just
        # quietly returning fewer jobs than usual.
        self.credits_exhausted = False

    def fetch_all(self) -> list:
        all_jobs = []
        serper = SerperClient(os.environ["SERPER_API_KEY"])
        ollama = OllamaClient(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        )

        for cat in CATEGORIES:
            category = cat["category"]

            if self.credits_exhausted:
                print(f"[job_sources] Skipping {category} — Serper credits exhausted this run")
                continue

            print(f"[job_sources] Searching: {category}...")

            try:
                raw_results = serper.search(cat["query"])
            except SerperCreditsExhausted as e:
                print(f"[job_sources] {e}")
                self.credits_exhausted = True
                continue

            structured = _structure_jobs(ollama, raw_results, cat["query"])

            # Secondary search if primary was thin or empty (search results are
            # non-deterministic — always retry empties to avoid missing a day)
            if cat.get("extra_query") and len(structured) < 3:
                try:
                    extra_raw = serper.search(cat["extra_query"])
                except SerperCreditsExhausted as e:
                    print(f"[job_sources] {e}")
                    self.credits_exhausted = True
                    extra_raw = []
                if extra_raw:
                    structured += _structure_jobs(ollama, extra_raw, cat["extra_query"])

            # ATS-biased search, run every time (not just on thin results): jobs
            # hosted on Greenhouse/Lever are the only ones web_applier.py can
            # reliably auto-submit (known field selectors), so deliberately
            # over-sample them to raise the auto-submit rate vs. generic sites.
            if cat.get("ats_query"):
                try:
                    ats_raw = serper.search(cat["ats_query"])
                except SerperCreditsExhausted as e:
                    print(f"[job_sources] {e}")
                    self.credits_exhausted = True
                    ats_raw = []
                if ats_raw:
                    structured += _structure_jobs(ollama, ats_raw, cat["ats_query"])

            for item in structured:
                title = str(item.get("title", "")).strip()
                company = str(item.get("company", "Unknown")).strip()
                url = str(item.get("url", "")).strip()
                location = str(item.get("location", "Ottawa, ON")).strip()
                description = str(item.get("description", f"{title} at {company}")).strip()

                if not title or not url:
                    continue

                all_jobs.append(
                    {
                        "id": make_id(title, company, url),
                        "title": title,
                        "company": company,
                        "location": location,
                        "url": url,
                        "source": "Web Search",
                        "category": category,
                        "apply_email": (
                            str(item.get("apply_email")).strip()
                            if item.get("apply_email") else extract_email(description)
                        ),
                        "description": description,
                        "deadline": (str(item.get("deadline")).strip() if item.get("deadline") else None),
                        "posted_date": (str(item.get("posted_date")).strip() if item.get("posted_date") else None),
                        "status": str(item.get("status", "unknown")).strip().lower(),
                        "always_notify": cat.get("always_notify", False),
                    }
                )

            print(f"  → {len(structured)} results")

        # Deduplicate by id
        seen_ids = set()
        unique = []
        for j in all_jobs:
            if j["id"] not in seen_ids:
                seen_ids.add(j["id"])
                unique.append(j)

        return unique
