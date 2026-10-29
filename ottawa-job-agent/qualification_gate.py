"""Hard-requirement qualification gate: rules out postings with a real, stated
mandatory requirement Sahawat cannot honestly meet, before spending further LLM
calls (scoring, cover letter, resume tailoring) on them.

Two-step, LLM-assisted but Python-aggregated: one call extracts the posting's
mandatory requirements, one call per requirement classifies YES/NO/UNCERTAIN
against his real on-file facts, and the final verdict is decided in plain
Python -- never a single holistic LLM judgment. content_generator.score_fit
has shown that kind of holistic call is noisy (the same posting scored both
4/10 and 2/10 across two runs on identical input); a constrained per-item
classification is far less noisy for the local 8B model.

Per the "no need to match my background, any job I can do" standing
instruction, this gate only rules out HARD mandatory mismatches (a missing
licence, an unmet years-of-experience floor, a required degree field with no
equivalent-experience escape clause) -- never thematic fit with his medical/
health background.
"""
import os
import re
import time

from ollama_client import OllamaClient
from resume_data import PROFILE

# Belt-and-suspenders on top of the extraction prompt's own instruction to
# exclude asset/preferred language -- the local 8B model doesn't always
# follow that instruction (observed: it once included a "bilingual is an
# asset but not mandatory" clause as if it were a hard requirement). Any
# extracted line matching one of these markers is dropped in plain Python
# rather than trusted to the model's own filtering.
_ASSET_LANGUAGE = re.compile(
    r"\b(an asset|is an asset|nice[- ]to[- ]have|preferred|not mandatory|not required|"
    r"considered an asset|would be an asset)\b",
    re.I,
)

_client = OllamaClient(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
)


def _call(max_tokens: int, prompt: str, max_retries: int = 2) -> str:
    """Call the local Ollama model, retrying once if the server isn't up yet."""
    for attempt in range(max_retries):
        try:
            return _client.generate(prompt, max_tokens=max_tokens).strip()
        except RuntimeError as e:
            print(f"[qualification_gate] {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
    return ""


def _candidate_facts_block() -> str:
    """Render resume_data.PROFILE into a plain-text facts sheet, built fresh
    each call -- never a hardcoded copy -- so edits to PROFILE automatically
    propagate into every prompt this module sends."""
    lines = [
        f"Status: {PROFILE['status']}",
        f"Languages: {', '.join(PROFILE['languages'])}",
        "",
        "Education:",
    ]
    for edu in PROFILE["education"]:
        lines.append(f"- {edu['degree']}, {edu['school']} ({edu['dates']})")

    lines.append("")
    lines.append("Certifications:")
    for cert in PROFILE["certifications"]:
        lines.append(f"- {cert}")

    lines.append("")
    lines.append("Work experience:")
    for job in PROFILE["experience"]:
        lines.append(f"- {job['title']}, {job['company']}, {job['location']} ({job['dates']})")
        for bullet in job["bullets"]:
            lines.append(f"  - {bullet}")

    return "\n".join(lines)


def extract_hard_requirements(description: str) -> list:
    """Return only the mandatory/required qualifications stated in a job
    posting, excluding anything phrased as an asset/preferred/nice-to-have."""
    if not description or not description.strip():
        return []

    prompt = f"""Read this job posting and list ONLY the mandatory/required qualifications a candidate MUST meet to be considered: education, certifications/licences, years of experience, language level, security clearance eligibility, work authorization, etc.

Do NOT include anything described as "an asset", "preferred", "nice to have", or similar wording -- those are not mandatory.
If a requirement says something like "degree in X OR an equivalent combination of education and experience", keep that whole phrase together as one requirement -- the equivalency clause matters.

Job posting:
{description}

Reply with ONLY a plain list, one requirement per line, each starting with "- ". If there are no real mandatory requirements stated, reply with exactly: NONE"""

    text = _call(500, prompt)
    if not text or text.strip().upper() == "NONE":
        return []

    # Only keep actual bullet/numbered items -- local models routinely prefix
    # the list with a preamble line ("Here is the list of mandatory
    # qualifications:") that isn't itself a requirement and must not be
    # treated as one.
    requirements = []
    for line in text.splitlines():
        raw = line.strip()
        if not raw:
            continue
        m = re.match(r"^[-*•]\s*(.+)", raw) or re.match(r"^\d+[.)]\s*(.+)", raw)
        if not m:
            continue
        item = m.group(1).strip()
        if item and item.upper() != "NONE" and not _ASSET_LANGUAGE.search(item):
            requirements.append(item)
    return requirements


def _check_one_requirement(requirement: str, facts: str) -> dict:
    """Classify a single requirement against real, on-file facts only."""
    prompt = f"""Candidate's real, on-file facts:
{facts}

Job requirement to check: "{requirement}"

Does the candidate meet this requirement, based ONLY on the facts above? Do not assume anything not stated in the facts. If the requirement includes an "equivalent combination of education/experience" clause, consider whether his combination of postgraduate diplomas and work experience could plausibly count.

Reply in exactly this format on one line:
VERDICT - one sentence reason grounded only in the facts above

Where VERDICT is exactly one of: YES, NO, UNCERTAIN"""

    text = _call(150, prompt)
    m = re.match(r"^(YES|NO|UNCERTAIN)\s*[-:]?\s*(.*)", text.strip(), re.I | re.S)
    if not m:
        return {"requirement": requirement, "verdict": "UNCERTAIN", "reason": text or "No response from model."}
    return {
        "requirement": requirement,
        "verdict": m.group(1).upper(),
        "reason": m.group(2).strip() or "(no reason given)",
    }


def check_qualification_gate(description: str) -> dict:
    """Extract hard requirements, check each against real facts, and
    deterministically aggregate to a verdict:
      - "ruled_out" if any requirement is a clear NO
      - "uncertain" if none are NO but at least one is UNCERTAIN
      - "pass" if every requirement is YES (or none were stated)
    Never fabricates a pass or a fail -- the verdict follows only from the
    per-item checks, and every check is grounded only in real PROFILE facts."""
    requirements = extract_hard_requirements(description)
    if not requirements:
        return {"verdict": "pass", "requirements": []}

    facts = _candidate_facts_block()
    checked = [_check_one_requirement(req, facts) for req in requirements]

    if any(r["verdict"] == "NO" for r in checked):
        verdict = "ruled_out"
    elif any(r["verdict"] == "UNCERTAIN" for r in checked):
        verdict = "uncertain"
    else:
        verdict = "pass"

    return {"verdict": verdict, "requirements": checked}
