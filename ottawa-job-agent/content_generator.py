import os
import re
import time

from ollama_client import OllamaClient
from resume_data import PROFILE, SUMMARIES

_client = OllamaClient(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
)


def _call(max_tokens: int, prompt: str, max_retries: int = 2) -> str:
    """Call the local Ollama model, retrying once if the server isn't up yet
    (e.g. a cold-boot daily run racing Ollama's own startup). Returns the text
    response, or "" if Ollama is unreachable after retries — callers already
    have honest fallbacks for an empty result."""
    for attempt in range(max_retries):
        try:
            return _client.generate(prompt, max_tokens=max_tokens).strip()
        except RuntimeError as e:
            print(f"[content_generator] {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
    return ""


def _strip_meta_commentary(text: str) -> str:
    """Local models routinely wrap the actual content in a preamble ("Here is
    a cover letter that meets the requirements:") and/or a trailing meta-note
    about the tone/honesty of what they just wrote. This text gets pasted
    straight into emails and video scripts with no human review in between —
    any leaked commentary would be visible to a real employer — so strip both."""
    if not text:
        return text
    lines = text.split("\n")
    while lines and (
        lines[0].strip().startswith("#")
        or lines[0].strip().lower() in ("cover letter", "cover letter body", "cover letter:")
        or re.match(r"^(here('s| is)|the following is|below is)\b", lines[0].strip(), re.I)
    ):
        lines.pop(0)
        while lines and not lines[0].strip():
            lines.pop(0)
    while lines and (
        re.match(r"^[\(\[]?\s*note\s*:", lines[-1].strip(), re.I)
        or lines[-1].strip().lower().startswith("i've written this")
    ):
        lines.pop()
    return "\n".join(lines).strip()


def score_fit(job: dict) -> int:
    """Return a fit score 0–10 for this job. Runs on the local Ollama model — free, no API cost."""
    prompt = f"""You are evaluating job fit for this candidate:

Name: {PROFILE['name']}
Background: Former physician (MD), crossing guard (nearly 2 years), NASM CPT, health coach, postgraduate diplomas in Health Informatics and Health Care Administration & Management, Venture for Canada Entrepreneurship & Innovation Fellow, Canada Service Corps / Regenesis Eco Leader / LEAF community-environmental leadership programs, Canadian PR, bilingual Thai/English
Target roles: crossing guard, Thai embassy, personal trainer/health coach, health promotion/health educator, outreach/sales, business/startup operations & administrative support, customer service, sustainability/nonprofit/community coordination, general labour
Constraints: candidate does NOT want night-shift or overnight-only roles. If this posting is night-shift-only or overnight-only, score it no higher than 2 regardless of other fit.

Job posting:
Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Description: {job['description']}
Category matched: {job['category']}

Score this job from 0–10 for fit. Only reply with the integer score. No explanation."""

    text = _call(10, prompt)
    try:
        # Extract first integer found
        import re
        m = re.search(r"\d+", text)
        return int(m.group()) if m else 5
    except (ValueError, AttributeError):
        return 5


def write_cover_letter(job: dict) -> str:
    """Write a tailored, human-voice cover letter for this job."""
    category = job.get("category", "outreach_sales")
    summary = SUMMARIES.get(category, SUMMARIES["outreach_sales"])
    relevant_skills = PROFILE["skills"].get(category, PROFILE["skills"]["outreach_sales"])

    category_emphasis = ""
    if category == "sustainability_nonprofit":
        category_emphasis = (
            "\nFor this role specifically, lead with his Canada Service Corps, Regenesis Eco Leader "
            "Placement, and LEAF Young Urban Forest/Ravine Leaders experience as the primary hook — "
            "this is exactly the kind of community/environmental work this employer does.\n"
        )

    prompt = f"""Write a cover letter for this job application. The letter must sound like a real human wrote it — not corporate, not AI-polished. Sahawat's voice is honest, direct, and slightly story-driven (he left medicine to become a crossing guard and found purpose there — use this if relevant).

CANDIDATE PROFILE:
- Name: {PROFILE['name']}
- Location: Ottawa, ON (local candidate); available from October 13, 2026
- Background: {summary}
- Relevant skills: {', '.join(relevant_skills)}
- Languages: {', '.join(PROFILE['languages'])}
- Status: {PROFILE['status']}
{category_emphasis}
JOB:
- {_job_context(job)}
- Category: {category}
- Available start date: October 13, 2026

{GROUNDING}

RULES:
- 3–4 short paragraphs max
- Open with something specific to this job/company, not "I am writing to apply"
- Connect his real, relevant experience to what the posting actually asks for — do not pad or inflate
- It is fine to be honest that a role is a career change for him; lead with transferable strengths, not invented experience
- Close with a simple, sincere interview request (not a bold promise)
- Format: plain text, ready to paste into an email body
- Do NOT include date, address headers, or "Sincerely" block — just the letter body paragraphs
- Output ONLY the letter paragraphs. No preamble ("Here is a cover letter..."), no closing note or
  meta-commentary about the letter itself — the raw text you write is pasted directly into an email.

Write the letter now:"""

    letter = _strip_meta_commentary(_call(600, prompt))
    if not letter:
        # Fallback generic letter
        letter = (
            f"Dear Hiring Team,\n\nI am writing to express my interest in the {job['title']} "
            f"position at {job['company']}. As a Canadian Permanent Resident relocating to Ottawa "
            f"in October 2026, with a background spanning medicine, health coaching, and community "
            f"service, I believe I would be a strong fit for this role.\n\n"
            f"I would welcome the opportunity to discuss how my experience can contribute to your team. "
            f"Thank you for your consideration."
        )
    return letter


def tailor_resume(job: dict) -> dict:
    """Return a per-job resume emphasis: a re-emphasized summary paragraph and the
    category's skill list reordered by relevance to THIS posting. Never invents new
    facts or skills — the summary must stay within the base summary/skills/certifications
    already on file, and every returned skill must be one of the original strings.
    Falls back to the untailored category defaults on any failure."""
    category = job.get("category", "outreach_sales")
    base_summary = SUMMARIES.get(category, SUMMARIES["outreach_sales"])
    base_skills = PROFILE["skills"].get(category, PROFILE["skills"]["outreach_sales"])
    fallback = {"summary": base_summary, "skills": list(base_skills)}

    prompt = f"""Tailor this resume content to the specific job posting below — emphasis only, no new facts.

BASE PROFILE SUMMARY (for this candidate category, already accurate):
{base_summary}

BASE SKILLS LIST (already accurate, do not add/remove/reword any):
{chr(10).join(f'- {s}' for s in base_skills)}

CERTIFICATIONS ON FILE: {', '.join(PROFILE['certifications'])}

JOB POSTING:
{_job_context(job)}

{GROUNDING}

TASK:
1. Rewrite the base profile summary (2-4 sentences) to foreground whatever in it is MOST relevant
   to this specific posting's language and requirements. Use ONLY facts already present in the base
   summary, the skills list, or the certifications above — do not add anything new.
2. Reorder the base skills list (the exact same strings, verbatim, none added or removed) so the
   ones most relevant to this posting come first.

Return ONLY a JSON object, no explanation, no markdown fences:
{{"summary": "...", "skills": ["...", "..."]}}"""

    text = _call(500, prompt)
    if not text:
        return fallback

    import json
    import re

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return fallback

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        return fallback

    summary = str(data.get("summary") or "").strip() or base_summary

    returned_skills = data.get("skills") or []
    by_normalized = {s.strip().lower(): s for s in base_skills}
    ordered = []
    for s in returned_skills:
        key = str(s).strip().lower()
        if key in by_normalized and by_normalized[key] not in ordered:
            ordered.append(by_normalized[key])
    # Guarantee no skill is silently dropped, even if the model missed one
    for s in base_skills:
        if s not in ordered:
            ordered.append(s)

    return {"summary": summary, "skills": ordered}


def write_email_subject(job: dict) -> str:
    """Write a short email subject line for the application."""
    subject = _call(
        40,
        f"Write a concise email subject line for a job application. "
        f"Role: {job['title']}. Company: {job['company']}. "
        f"Applicant: Sahawat Nilwatcharamanee. "
        f"Keep it under 12 words. No quotes. Just the subject line text.",
    )
    return subject or f"Application for {job['title']} — Sahawat Nilwatcharamanee"


# ── Creative microsite content ──────────────────────────────────────────────

STORY = (
    "Sahawat spent a decade becoming a physician in Thailand, then walked away and moved "
    "to Canada with no plan. He took a job as a crossing guard — and at those intersections "
    "rediscovered who he was beyond his credentials. He went on to train as an IIN-certified "
    "health coach and NASM personal trainer. Former MD -> Crossing Guard -> Coach."
)

# Hard limits on what may be claimed. Every generator is bound by these.
GROUNDING = (
    "STRICT HONESTY RULES — follow exactly:\n"
    "- Only reference Sahawat's ACTUAL background: medical doctor in Thailand (2019-2021), "
    "crossing guard in Canada (2024-present), and hospital volunteer liaison (2022-2023). "
    "He holds an NASM personal-trainer certification, an IIN Integrative Nutrition Health Coach "
    "certification, a Bitelab (UK) health-technology diploma, an ECA credential assessment, and "
    "postgraduate diplomas in Health Informatics and Health Care Administration & Management from "
    "Sault College. As a physician he provided health education on preventive care and chronic "
    "disease management — reference this directly for health promotion/health educator roles.\n"
    "- He also completed a Venture for Canada Entrepreneurship & Innovation Fellowship (May 2024 – "
    "May 2025) — reference this for business/startup/operations roles. He does not have prior "
    "founder, ops, or corporate business experience beyond this fellowship — do not invent any.\n"
    "- Do NOT mention 'Crosswalk Wisdom' or describe him as a founder/business owner — he does not "
    "want that discussed in applications right now.\n"
    "- He is based in Ottawa now (local candidate). Do NOT say he is 'relocating' or 'moving to' Ottawa; "
    "his start-date availability is October 13, 2026.\n"
    "- He also took part in community/environmental leadership programs: Canada Service Corps, "
    "Regenesis Eco Leader Placement, and LEAF's Young Urban Forest Leaders & Young Ravine Leaders. "
    "Reference these where they add value (they show reliability, teamwork, and leadership), but only "
    "as participation — do not invent his specific duties or titles within them.\n"
    "- Do NOT invent or imply experience he lacks: he has NOT worked at a gym, has no prior "
    "personal-training clients, no sales/quota history, and no specific follower or revenue numbers.\n"
    "- Do NOT promise specific outcomes, client counts, timelines, or numbers he will deliver.\n"
    "- Do NOT overstate. If unsure whether he has done something, do not claim it.\n"
    "- Align everything to what THIS job posting actually asks for. Be modest, concrete, and honest.\n"
    "- No buzzwords (passionate, dynamic, excited to, leverage, synergy)."
)


def _job_context(job: dict) -> str:
    desc = (job.get("description") or "").strip()
    desc_line = f"\nWhat the posting says: {desc}" if desc else ""
    return f"Role: {job['title']} at {job['company']} ({job['location']}).{desc_line}"


def write_why_them(job: dict) -> str:
    """One short, specific paragraph on why Sahawat wants THIS employer/role."""
    text = _call(
        300,
        f"Write ONE short paragraph (3-4 sentences) explaining why Sahawat wants this role. "
        f"{_job_context(job)}\n"
        f"Context on Sahawat: {STORY}\n{GROUNDING}\n"
        f"Be specific and grounded in his real background and what the posting asks for. "
        f"Write in first person as Sahawat. Plain text only. Output ONLY the paragraph — no preamble, "
        f"no meta-commentary about what you wrote.",
    )
    text = _strip_meta_commentary(text)
    return text or (
        f"I'm drawn to this {job['title']} role at {job['company']} because it lets me put my "
        f"medical background and care for people to practical, everyday use."
    )


def write_30_day_plan(job: dict) -> list:
    """Return 3 modest, honest ways Sahawat would approach the role — no invented promises."""
    text = _call(
        400,
        f"List exactly 3 modest, honest things Sahawat would focus on when starting this role. "
        f"{_job_context(job)}\n"
        f"Context: {STORY}\n{GROUNDING}\n"
        f"These are intentions about how he'd approach the work, NOT promises of specific results, "
        f"client numbers, or revenue. Examples of the right tone: 'learn the team and how things run', "
        f"'show up reliably', 'ask good questions before suggesting changes'. "
        f"Keep each to one honest sentence, aligned to what this posting actually involves. "
        f"Format as 3 lines, each starting with '- '. No preamble, no buzzwords, no numbers.",
    )
    items = [line.lstrip("- ").strip() for line in text.split("\n") if line.strip().startswith("-")]
    if len(items) >= 3:
        return items[:3]
    return [
        "Learn how the team works and listen before suggesting anything.",
        "Show up reliably and bring a calm, people-first presence to every shift.",
        "Apply my clinical background carefully and within the limits of the role.",
    ]


def write_video_script(job: dict) -> str:
    """Write a 30-second spoken video script (first person, ~75 words)."""
    text = _call(
        300,
        f"Write a 30-second video pitch script (about 70-80 words, spoken first person) for "
        f"Sahawat applying to this role. {_job_context(job)}\n"
        f"Context: {STORY}\n{GROUNDING}\n"
        f"Open by addressing the team by name (e.g. 'Hi {job['company']} team'). "
        f"Tell the doctor-to-crossing-guard hook in one line, say honestly why this role fits, "
        f"then a warm, simple close. No promises of results. "
        f"Natural spoken rhythm, no stage directions, no buzzwords. Plain text only. Output ONLY the "
        f"spoken script — no preamble, no meta-commentary about what you wrote.",
    )
    text = _strip_meta_commentary(text)
    return text or (
        f"Hi {job['company']} team. I'm Sahawat. I trained as a doctor in Thailand, then moved "
        f"to Canada and became a crossing guard — and that's where I learned how much small, "
        f"consistent care matters. I'd like to bring that to this {job['title']} role. "
        f"I'd welcome the chance to talk."
    )
