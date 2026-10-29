"""
Cold-lead sourcing pipeline (Phase 2).

Uses Perplexity to find WHERE the ICP gathers — LinkedIn creators whose
audiences are burned-out healthcare workers / IMGs, plus active communities —
then writes a weekly "cold target briefing" telling you exactly which accounts
to feed into Sendpilot's scraper and which communities to engage manually.

This SOURCES targets. It sends nothing. The actual connect+message runs in
Sendpilot once you load a list and connect your LinkedIn account.

Run: python3 cold_lead_sourcing.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

PPLX_KEY = os.environ["PERPLEXITY_API_KEY"]
PPLX_URL = "https://api.perplexity.ai/chat/completions"
OUT_DIR = Path(__file__).parent / "CROSSING-SESSION-LAUNCH" / "cold-targets"

ICP = (
    "burned-out healthcare professionals considering leaving clinical medicine — "
    "nurses, physicians, and especially International Medical Graduates (IMGs) in "
    "Canada who are unmatched or stuck in survival jobs. They feel trapped by "
    "identity, sunk cost, and fear (money / judgment / loss of identity)."
)

QUERY = f"""You are a B2B lead-research analyst. My ICP is: {ICP}

Find where these people actively gather and express this pain PUBLICLY right now.
Return STRICT JSON only, no prose, with this shape:
{{
  "linkedin_creators": [
    {{"name": "", "handle_or_url": "", "why": "audience fit in one line"}}
  ],
  "linkedin_hashtags": ["#..."],
  "reddit_communities": [{{"subreddit": "", "why": ""}}],
  "facebook_groups": [{{"name": "", "why": ""}}],
  "search_phrases": ["phrases these people literally write when venting/seeking help"]
}}

Rules: prioritize creators whose COMMENTERS are the ICP (not just the creator).
8-12 linkedin_creators, real and currently active. Be specific, not generic."""


def research_targets() -> dict:
    body = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You output only valid JSON. No markdown fences."},
            {"role": "user", "content": QUERY},
        ],
        "temperature": 0.2,
    }
    r = requests.post(
        PPLX_URL, headers={"Authorization": f"Bearer {PPLX_KEY}"}, json=body, timeout=90
    )
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"].strip()
    # strip accidental fences
    if content.startswith("```"):
        content = content.split("```")[1].replace("json", "", 1).strip()
    return json.loads(content)


def write_briefing(data: dict) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    out = OUT_DIR / f"{today}.md"

    lines = [
        f"# Cold target briefing — {today}",
        "",
        "Feed the LinkedIn creators into Sendpilot's audience scraper (scrape their",
        "**post commenters/engagers**, not followers — commenters show intent). Cap",
        "connects at ~15/day. Engage communities manually first, then DM.",
        "",
        "## LinkedIn creators to scrape (engagers = your ICP)",
    ]
    for c in data.get("linkedin_creators", []):
        lines.append(f"- **{c.get('name','?')}** — {c.get('handle_or_url','')}  \n  _{c.get('why','')}_")

    lines += ["", "## Hashtags to monitor", ""]
    lines.append(" ".join(data.get("linkedin_hashtags", [])) or "_none_")

    lines += ["", "## Reddit communities (engage, don't spam)", ""]
    for s in data.get("reddit_communities", []):
        sub = s.get("subreddit", "?").lstrip("r/").lstrip("/")
        lines.append(f"- r/{sub} — {s.get('why','')}")

    lines += ["", "## Facebook groups", ""]
    for g in data.get("facebook_groups", []):
        lines.append(f"- {g.get('name','?')} — {g.get('why','')}")

    lines += ["", "## What they say (search these to find live prospects)", ""]
    for p in data.get("search_phrases", []):
        lines.append(f'- "{p}"')

    lines += [
        "",
        "## Cold opener templates (soft — no link in msg 1)",
        "",
        "**On connect (note, <300 chars):**",
        "> Saw your activity around [topic/creator]. I write about the crossing out",
        "> of clinical medicine for healthcare folks who feel stuck. No pitch — just",
        "> connecting with people in the same crosswalk.",
        "",
        "**After they accept (msg 1, a question):**",
        "> Thanks for connecting. Out of curiosity — are you actively weighing a move",
        "> out of [their field], or more in the 'something has to change' stage?",
        "",
        "**If they engage → the Fear Audit (msg 2):**",
        "> What you're describing usually traces to one of three fears running the",
        "> show. I built a free 3-min audit that names which: https://fear-audit.vercel.app",
        "",
        "**Warm → the offer (only after real conversation):**",
        "> This is exactly what my Crossing Sessions are for — one hour, a written",
        "> plan after. First ten are $97: https://sahawat.gumroad.com/l/crossing-session",
    ]

    out.write_text("\n".join(lines))
    return out


if __name__ == "__main__":
    print("Researching cold targets via Perplexity...")
    data = research_targets()
    out = write_briefing(data)
    print(f"Briefing written: {out}")
    print(
        f"  {len(data.get('linkedin_creators', []))} creators, "
        f"{len(data.get('reddit_communities', []))} subreddits, "
        f"{len(data.get('facebook_groups', []))} FB groups"
    )
