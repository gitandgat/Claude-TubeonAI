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

import requests

from ollama_client import OllamaClient
from serper_client import SerperClient, SerperCreditsExhausted

# Small-employer ATS platforms (municipalities, nonprofits, SMBs) that the
# original `ats_query` fields never covered — those only targeted Greenhouse/
# Lever, the two boards web_applier.py has hand-built auto-submit logic for.
# Confirmed 2026-08-30: a manual search found an open Ottawa Safety Council
# crossing-guard posting hosted on ottawasafetycouncil.recruitee.com — a
# different domain than the stale `site:ottawasafetycouncil.ca` filter below —
# that the daily run had been missing entirely. web_applier.py's generic
# form-filler (_apply_generic) already handles these platforms best-effort,
# so this is purely a discovery gap, not an apply-side one.
#
# No `*.` wildcard before each domain: Serper's free tier rejects that syntax
# outright (HTTP 400 "Query pattern not allowed for free accounts", confirmed
# live 2026-08-30) even though it's valid raw Google syntax. Google's bare
# `site:domain.com` already matches subdomains like ottawasafetycouncil
# .recruitee.com, so this loses no coverage.
_SMALL_ATS_SITES = (
    "(site:recruitee.com OR site:bamboohr.com OR site:workable.com "
    "OR site:breezy.hr OR site:jobs.smartrecruiters.com OR site:applytojob.com)"
)

CATEGORIES = [
    {
        "category": "crossing_guard",
        "query": "crossing guard school crossing traffic safety jobs Ottawa Ontario Canada site:indeed.ca OR site:jobbank.gc.ca OR site:recruitee.com OR site:jobs.ottawa.ca OR site:linkedin.com/jobs 2025 2026",
        "extra_query": "\"crossing guard\" OR \"school crossing guard\" Ottawa Ontario jobs hiring",
        "small_ats_query": f"(\"crossing guard\" OR \"school crossing guard\" OR \"traffic safety\") Ottawa Ontario Canada {_SMALL_ATS_SITES}",
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
        "ats_query": "\"personal trainer\" OR \"health coach\" OR \"wellness coordinator\" Canada (site:boards.greenhouse.io OR site:jobs.lever.co)",
        "small_ats_query": f"(\"personal trainer\" OR \"health coach\" OR \"wellness coordinator\") Ottawa OR remote Canada {_SMALL_ATS_SITES}",
    },
    {
        "category": "health_promotion",
        "query": "health promotion specialist health educator public health educator community health promoter wellness program coordinator Ottawa Public Health CHEO community health centre Ottawa Ontario jobs 2025 2026",
        "extra_query": "\"health promotion\" OR \"health educator\" OR \"health promotion specialist\" Ottawa Ontario Canadian Cancer Society OR \"Heart and Stroke\" OR \"Diabetes Canada\" OR university jobs hiring",
        "ats_query": "\"health promotion\" OR \"health educator\" OR \"community health\" Canada (site:boards.greenhouse.io OR site:jobs.lever.co)",
        "small_ats_query": f"(\"health promotion\" OR \"health educator\" OR \"community health\") Ottawa Ontario Canada {_SMALL_ATS_SITES}",
    },
    {
        # Strategic priority: HIM/health-data roles start the ~5-year experiential
        # clock toward the CHIM designation (Sault College diplomas are not
        # CHIMA-accredited, per program coordinator Aug 2026 — experience is the
        # only certification pathway).
        "category": "health_informatics",
        "query": "health information management OR health records OR health data analyst OR clinical data coordinator OR decision support analyst OR health informatics jobs Ottawa Ontario Canada OR remote Canada 2025 2026 site:indeed.ca OR site:jobbank.gc.ca OR site:linkedin.com/jobs",
        "extra_query": "\"health information\" OR \"health records\" OR \"health data\" OR \"health informatics\" Ottawa Hospital OR CHEO OR \"Ontario Health\" OR CIHI OR \"Canada Health Infoway\" OR \"TELUS Health\" hiring analyst OR clerk OR coordinator OR specialist",
        "ats_query": "\"health information\" OR \"health data analyst\" OR \"clinical data\" OR \"health informatics\" Canada (site:boards.greenhouse.io OR site:jobs.lever.co)",
        "small_ats_query": f"(\"health information\" OR \"health data analyst\" OR \"clinical data\" OR \"health informatics\") Ottawa OR remote Canada {_SMALL_ATS_SITES}",
        "always_notify": True,
    },
    {
        "category": "outreach_sales",
        "query": "outreach coordinator community outreach health sales representative business development community liaison Ottawa Ontario jobs 2025 2026",
        "extra_query": "\"outreach\" OR \"sales representative\" Ottawa Ontario healthcare community job",
        "ats_query": "\"outreach coordinator\" OR \"business development\" OR \"sales representative\" Canada (site:boards.greenhouse.io OR site:jobs.lever.co)",
        "small_ats_query": f"(\"outreach coordinator\" OR \"business development\" OR \"sales representative\") Ottawa Ontario Canada {_SMALL_ATS_SITES}",
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
        "ats_query": "\"operations coordinator\" OR \"business development\" OR \"startup\" Canada (site:boards.greenhouse.io OR site:jobs.lever.co)",
        "small_ats_query": f"(\"operations coordinator\" OR \"business development\" OR \"startup\") Ottawa OR remote Canada {_SMALL_ATS_SITES}",
    },
    {
        "category": "admin_office",
        "query": "administrative assistant OR executive assistant OR office administrator OR virtual assistant OR data entry clerk OR medical office assistant jobs Ottawa Ontario Canada OR remote Canada 2025 2026",
        "extra_query": "\"administrative assistant\" OR \"virtual assistant\" OR \"data entry\" Ottawa OR remote Canada job posting hiring",
        "ats_query": "\"administrative assistant\" OR \"executive assistant\" OR \"virtual assistant\" Canada (site:boards.greenhouse.io OR site:jobs.lever.co)",
        "small_ats_query": f"(\"administrative assistant\" OR \"virtual assistant\" OR \"data entry\") Ottawa OR remote Canada {_SMALL_ATS_SITES}",
    },
    {
        "category": "customer_service",
        "query": "customer service representative OR client support specialist OR customer success associate OR call centre representative jobs Ottawa Ontario Canada OR remote Canada 2025 2026",
        "extra_query": "\"customer service\" OR \"customer support\" Ottawa OR remote Canada hiring day shift",
        "ats_query": "\"customer service representative\" OR \"customer support\" OR \"customer success\" Canada (site:boards.greenhouse.io OR site:jobs.lever.co)",
        "small_ats_query": f"(\"customer service\" OR \"customer support\") Ottawa OR remote Canada {_SMALL_ATS_SITES}",
    },
    {
        # Strategic priority (added 2026-09-01): front-desk/guest-services roles
        # biased toward the downtown/Centretown-walkable hotel cluster — real
        # front-desk-to-Front-Office-Manager promotion ladders exist there,
        # confirmed via a live Marriott Front Desk Supervisor posting. No
        # wildcard site: filters for chain ATS portals (unconfirmed exact
        # domains for Accor/Hyatt/Marriott career sites) — plain text search
        # lets Google resolve whatever domain actually hosts each listing.
        "category": "hospitality_hotel",
        "query": "hotel front desk agent OR guest services agent OR front office agent jobs Ottawa Ontario Fairmont Chateau Laurier OR Lord Elgin Hotel OR Novotel Ottawa OR Andaz Ottawa ByWard Market OR Westin Ottawa OR Delta Ottawa City Centre 2025 2026",
        "extra_query": "\"front desk agent\" OR \"guest services agent\" OR \"front office\" hotel Ottawa Ontario hiring now",
        "ats_query": "\"front desk agent\" OR \"guest services\" OR \"front office\" hotel Canada (site:boards.greenhouse.io OR site:jobs.lever.co)",
        "small_ats_query": f"(\"front desk agent\" OR \"guest services\" OR \"front office\") hotel Ottawa Ontario Canada {_SMALL_ATS_SITES}",
        "always_notify": True,
    },
    {
        "category": "sustainability_nonprofit",
        "query": "sustainability coordinator OR environmental program coordinator OR nonprofit program coordinator OR community engagement coordinator OR volunteer coordinator jobs Ottawa Ontario Canada OR remote Canada 2025 2026",
        "extra_query": "\"sustainability\" OR \"environmental\" OR \"nonprofit\" OR \"community engagement\" Ottawa OR remote Canada hiring coordinator",
        "ats_query": "\"sustainability coordinator\" OR \"nonprofit program coordinator\" OR \"community engagement\" Canada (site:boards.greenhouse.io OR site:jobs.lever.co)",
        "small_ats_query": f"(\"sustainability coordinator\" OR \"nonprofit program coordinator\" OR \"community engagement\") Ottawa OR remote Canada {_SMALL_ATS_SITES}",
    },
    {
        "category": "general_labor",
        "query": "warehouse associate OR general labourer OR delivery driver OR retail associate OR landscaping labourer jobs Ottawa Ontario Canada 2025 2026 day shift",
        "extra_query": "\"warehouse\" OR \"general labour\" OR \"retail associate\" Ottawa Ontario day shift hiring",
        "ats_query": "\"warehouse associate\" OR \"general labourer\" OR \"retail associate\" Canada (site:boards.greenhouse.io OR site:jobs.lever.co)",
        "small_ats_query": f"(\"warehouse\" OR \"general labour\" OR \"retail associate\") Ottawa Ontario Canada {_SMALL_ATS_SITES}",
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


# The structuring prompt asks the small local model for a real company name, but
# on a messy snippet it sometimes lifts the wrong field instead — a bare province
# code, a pay figure, a "no employer given" placeholder, or the job board's own
# name where the employer's name should be. Neither is an addressable lead
# (there's no one to write "Dear Hiring Team at ON" to), so drop them rather
# than surface a job the applicant can't actually act on.
_JUNK_COMPANY_PATTERN = re.compile(
    r"^(on|qc|bc|ab|mb|sk|ns|nb|nl|pe|nt|nu|yt|unknown|n/?a|none|null|not specified)$"
    r"|\b(none|null|various|multiple)\s+(companies|employers)\b"
    r"|\bnot specified\b|\bnot given\b|\bno company (listed|specified|given|mentioned)\b"
    r"|\b(ziprecruiter|indeed|linkedin|simplyhired|workopolis|glassdoor|monster|jooble|adzuna|flexjobs"
    r"|eluta|careerbeacon|jobillico|jobgether|talent\.com|neuvoo|theimpactjob)\b"
    # Page furniture the structuring model mistakes for an employer name: an
    # apply-button label, or its own hedge when the snippet named no company.
    # "unknown (SWCHC)" is unanchored-prefix because the model likes to append a
    # parenthetical guess, which the ^unknown$ alternative above never catches.
    r"|^easy apply$|^unknown\b|^\s*$"
    # Not anchored to the start: this text has shown up both alone ("$20 an
    # hour") and prefixed by a leaked province code ("ON $60,000-$65,000 a
    # year Full-Time") — the dollar figure is the reliable signal either way.
    r"|\$\s*[\d,]+(\.\d+)?k?\s*(?:(?:–|-|to)\s*\$?\s*[\d,]+(\.\d+)?k?)?"
    r"\s*(?:/|an?\s+|per\s+)?(hour|hr|hourly|year|yr|annum|annually)\b",
    re.I,
)

# Aggregator search-result and listing-page titles ("77 Remote ... jobs in
# Ottawa, ON", "23 Medical ... job openings in Ottawa, ON", raw boolean search
# queries with "OR") describe a category of postings, not one specific role —
# there's nothing concrete to write a cover letter or tailored resume for.
# Also catches the literal "None"/"null" placeholder the model sometimes
# emits for title itself, which a truthiness check alone won't catch since
# both are non-empty strings.
_JUNK_TITLE_PATTERN = re.compile(
    r"^(none|null|n/a)$"
    r"|^\d+\+?\s"
    r"|\d+\s+(active\s+)?job\s+posts?\b"
    r"|\bjob\s+openings?\s+in\s+\w"
    r"|\bjobs?\s+in\s+(ottawa|canada|ontario)\b"
    r"|\bOR\b.*\bOR\b"
    r"|^\$[\d,]+k?\s*[-–]\s*\$[\d,]+k?\b",
    re.I,
)

# Search-results/listing pages and social-media posts aren't individual job
# postings — there's no specific role to point the applicant at. Distinct from
# _BOT_CHECK_DOMAINS below: those ARE real postings, just ones headless browsers
# can't get past.
_NOT_A_POSTING_PATTERN = re.compile(
    r"indeed\.\w+/jobs\?|indeed\.\w+/q-.*-jobs\.html|linkedin\.com/jobs/search|/jobs/search|/search\?"
    # workopolis.com/jobsearch/<category-slug> is a listing page; distinct from
    # jobbank.gc.ca/jobsearch/jobposting/<id>, which IS a real single posting.
    r"|workopolis\.com/jobsearch/"
    # cercottawa.ca/<lang>/employer/job-postings.php is CERC's shared listing page
    # for many other employers' openings, not a posting itself — distinct from
    # .../employer/job-details.php?jid=<id>, a real single posting. Confirmed by
    # CERC staff after fabricated "postings" scraped off the listing page got
    # auto-applied to in Aug 2026 (see _BOARD_DOMAINS note in web_applier.py).
    r"|cercottawa\.ca/\w+/employer/job-postings\.php"
    # jobs.lever.co/<company> (optionally with a query string, no job-id path
    # segment) is the company's bare listing page, not a single posting — same
    # failure class as the cercottawa listing page above. A real Lever posting
    # always has a second path segment: jobs.lever.co/<company>/<job-id>.
    r"|jobs\.lever\.co/[^/?]+/?(?:\?|$)"
    r"|google\.\w+/search"
    # \b before twitter.com/x.com: unanchored "x\.com" also matches inside
    # legitimate company domains like arcteryx.com or concentrix.com.
    r"|flexjobs\.com/search|facebook\.com(?!/jobs/\d)|\btwitter\.com|\bx\.com|instagram\.com|reddit\.com"
    # Aggregator *search-result* pages. Each of these lists many roles, so the
    # structuring model pairs one title it saw with the query URL and invents a
    # posting that was never there (two distinct "jobs" sharing one Eluta URL is
    # the giveaway). Sep 2026 audit: 209 tracked entries, all from Web Search /
    # Job Bank scraping. Structured sources (Workday/Njoyn/SuccessFactors) had
    # zero. Each alternative below spares that site's real single-posting form:
    #   eluta      search "<Role>-jobs-in-<City>" / "jobs-at-<co>-in-<city>"
    #   glassdoor  search SRCH_IL...; real posting is /job-listing/...?jl=<id>
    #   ziprecruiter  /Jobs/<Role>/-in-<City>; real posting carries ?jid=<id>
    #   linkedin   /jobs/<slug>-jobs; real posting is /jobs/view/<id>
    #   indeed     /cmp/<Co>/jobs listing; real posting is /viewjob?jk=<id>
    r"|eluta\.\w+/[^?]*-jobs-in-|eluta\.\w+/jobs-at-"
    r"|glassdoor\.\w+/Job/[^?]*SRCH_IL"
    r"|ziprecruiter\.\w+/Jobs/(?![^?]*[?&]jid=)"
    r"|linkedin\.com/jobs/(?!view/)"
    r"|indeed\.\w+/cmp/[^/]+/(jobs|locations)\b"
    r"|flexjobs\.\w+/remote-jobs|jobgether\.\w+/remote-jobs|theimpactjob\.\w+/jobs/remote",
    re.I,
)

_GREENHOUSE_DOMAIN = re.compile(r"(?:boards|job-boards)\.greenhouse\.io", re.I)


def _greenhouse_board_is_live(url: str) -> bool:
    """The Web Search sourcing path over-samples Greenhouse/Lever links (they're
    the only ATSs web_applier.py can reliably auto-submit), which means the local
    model's occasional fabricated-but-plausible-looking job URL for an org that
    never had a Greenhouse board slips straight into the pipeline. Greenhouse
    redirects those to job-boards.greenhouse.io/<company>?error=true — sometimes
    with a 200 status, so the query marker matters as much as the status code.
    Fails open (assumes live) on any network error so a timeout never drops a
    real posting. Lever gets no equivalent check: its Cloudflare bot-protection
    returns a fake 404 to every plain HTTP request, live posting or not, so a
    status-code check there would wrongly discard genuine Lever jobs."""
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
    except requests.exceptions.RequestException:
        return True
    if r.status_code == 404:
        return False
    if "error=true" in r.url:
        return False
    return True


# Ottawa-area suburbs/neighbourhoods that sometimes show up as the bare place
# name in a scraped listing — never treat these as "a different city".
_OTTAWA_AREA_TERMS = (
    "ottawa", "nepean", "kanata", "orleans", "barrhaven", "stittsville",
    "gloucester", "vanier", "gatineau", "hull", "lansdowne", "manotick",
)

# Cities that have actually shown up on in-person postings the STRUCTURE_PROMPT
# should have excluded (the small local model doesn't always follow that rule).
# This is a deterministic backstop, not a replacement for the prompt rule.
_OTHER_CITY_TERMS = (
    "toronto", "mississauga", "calgary", "edmonton", "vancouver", "montreal",
    "montréal", "winnipeg", "hamilton", "brampton", "surrey", "delta,",
    "burnaby", "victoria", "halifax", "regina", "saskatoon", "kitchener",
    "waterloo", "windsor", "markham", "vaughan", "richmond hill", "burlington",
    "oakville", "st. john's", "quebec city", "québec,", "london, on",
)


def _is_ottawa_or_remote_location(location: str) -> bool:
    """Deterministic backstop for the STRUCTURE_PROMPT's location rule — the
    small local model doesn't always honor it, so real leads for other cities
    (Mississauga, Toronto, Calgary...) sometimes slip through. Only reject
    listings that name a different city; ambiguous/blank locations ("Canada",
    "ON", "") pass through since the prompt already tried to scope the source
    data to Ottawa/remote-Canada and there's nothing concrete here to reject."""
    low = (location or "").lower()
    if any(term in low for term in _OTTAWA_AREA_TERMS):
        return True
    if any(term in low for term in _OTHER_CITY_TERMS):
        return False
    return True


# Aggregators whose posting pages (not just search pages) reliably trip
# web_applier.py's BOT_BLOCK_PATTERN interstitial check. Real leads, but never
# worth spending a cover letter + tailored resume + Playwright attempt on when
# there's no scraped apply_email to route around the browser entirely — flag
# them here so job_agent.py's existing no_auto_apply short-circuit (the same
# one jobbank_source.py uses) skips straight to a manual-apply notification.
_BOT_CHECK_DOMAINS = re.compile(r"glassdoor\.\w+|ziprecruiter\.\w+|indeed\.\w+", re.I)


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

    def fetch_all(self, categories: Optional[set] = None) -> list:
        """Search every category in CATEGORIES, or only the ones named in
        `categories` (e.g. {"hospitality_hotel"}) for a scoped run — the daily
        production job passes nothing so it keeps covering every category."""
        all_jobs = []
        serper = SerperClient(os.environ["SERPER_API_KEY"])
        ollama = OllamaClient(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        )

        for cat in CATEGORIES:
            category = cat["category"]

            if categories and category not in categories:
                continue

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

            # Small-employer ATS search, also run every time: municipalities,
            # nonprofits, and SMBs (the crossing_guard/admin/outreach categories'
            # actual employer base) commonly use Recruitee/BambooHR/Workable/
            # Breezy/SmartRecruiters/JazzHR rather than Greenhouse/Lever, and the
            # `query`/`extra_query` site: filters above don't target them either.
            # web_applier.py's generic form-filler already handles these
            # best-effort, so this only needed to close the discovery gap.
            # Default num (10, 1 credit/query): Serper charges 2 credits for
            # any request asking for 11-100 results, confirmed 2026-08-30 while
            # pricing a top-up. Going deeper than 10 was unverified value for
            # certain 2x cost, so it isn't worth defaulting to here.
            if cat.get("small_ats_query"):
                try:
                    small_ats_raw = serper.search(cat["small_ats_query"])
                except SerperCreditsExhausted as e:
                    print(f"[job_sources] {e}")
                    self.credits_exhausted = True
                    small_ats_raw = []
                if small_ats_raw:
                    structured += _structure_jobs(ollama, small_ats_raw, cat["small_ats_query"])

            for item in structured:
                title = str(item.get("title", "")).strip()
                company = str(item.get("company", "Unknown")).strip()
                # item.get("url") can be JSON null -> Python None; str(None) is the
                # non-empty literal "None", which would otherwise slip past the
                # `not url` check below and get treated as a real link.
                url = str(item.get("url") or "").strip()
                location = str(item.get("location", "Ottawa, ON")).strip()
                description = str(item.get("description", f"{title} at {company}")).strip()

                if not title or not url:
                    continue
                if _JUNK_COMPANY_PATTERN.search(company):
                    continue
                if _JUNK_TITLE_PATTERN.search(title):
                    continue
                if _NOT_A_POSTING_PATTERN.search(url):
                    continue
                if not _is_ottawa_or_remote_location(location):
                    continue
                if _GREENHOUSE_DOMAIN.search(url) and not _greenhouse_board_is_live(url):
                    continue

                # The local model is told to emit null when no email is present, but
                # llama3.1:8b sometimes emits the literal string "unknown"/"n/a" instead —
                # a truthy value that used to slip straight through to smtplib as the
                # recipient and bounce with "501 5.1.3 Invalid address". Validate the
                # shape before trusting it; fall back to scraping the description.
                raw_apply_email = str(item.get("apply_email")).strip() if item.get("apply_email") else ""
                apply_email = raw_apply_email if extract_email(raw_apply_email) else extract_email(description)

                # Deliberately no `apply_target` here, unlike ats_boards.py /
                # workday_source.py / jobbank_source.py. Those three already know
                # the employer's own posting URL at fetch time; a web-search hit is
                # usually an Indeed/Jobs.ca *mirror* of a posting that also lives on
                # the company's real Greenhouse/Lever/Workday board. Leaving the tag
                # off is what lets employer_site.resolve_employer_apply_url() run its
                # registry lookup and swap the mirror for the real apply page —
                # pre-tagging would short-circuit exactly the case this pipeline
                # exists to fix.
                job = {
                    "id": make_id(title, company, url),
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": url,
                    "source": "Web Search",
                    "category": category,
                    "apply_email": apply_email,
                    "description": description,
                    "deadline": (str(item.get("deadline")).strip() if item.get("deadline") else None),
                    "posted_date": (str(item.get("posted_date")).strip() if item.get("posted_date") else None),
                    "status": str(item.get("status", "unknown")).strip().lower(),
                    "always_notify": cat.get("always_notify", False),
                }

                if not apply_email and _BOT_CHECK_DOMAINS.search(url):
                    job["no_auto_apply"] = True
                    job["no_apply_reason"] = (
                        "job board bot-check page (Glassdoor/ZipRecruiter/Indeed) — "
                        "open the link and apply directly"
                    )

                all_jobs.append(job)

            print(f"  → {len(structured)} results")

        # Deduplicate by id
        seen_ids = set()
        unique = []
        for j in all_jobs:
            if j["id"] not in seen_ids:
                seen_ids.add(j["id"])
                unique.append(j)

        return unique
