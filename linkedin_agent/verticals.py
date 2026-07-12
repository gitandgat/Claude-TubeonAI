"""Content vertical registry for the multi-vertical LinkedIn + cross-post agent.

All five verticals publish to the ONE LinkedIn profile (Dr. Sahawat) — same
person, different subject lens — so the voice stays coherent across the brand's
"doctor who chose a new path" story. The 5/day LinkedIn cap is the design: one
day-part slot per vertical, exactly 5.

Each vertical owns:
  - its LinkedIn day-part slot (08:00 / 11:00 / 14:00 / 17:00 / 20:00 ET)
  - a persona/domain system prompt (shares the proven first-person FORMAT_SPINE)
  - a rotating theme list (no Reddit research needed off the Crosswalk vertical)
  - its first-comment CTA + a fallback CTA line
  - its cross-post account set (reuses the existing Crosswalk IG + FB accounts;
    TikTok/YouTube are video surfaces handled by the video agent, not image posts)
  - its own learning-loop data dir, so winning_patterns.json is independent
    per vertical (what wins for fitness ≠ what wins for IMG career content)
"""

import os
from dataclasses import dataclass, field

from linkedin_agent.config import (
    VIDEO_PLATFORM_ACCOUNTS,
    LINKEDIN_FIRST_COMMENT,
    DATA_DIR,
)
from linkedin_agent.verified_facts import VERIFIED_FACTS_BLOCK

# ── The proven format spine ──────────────────────────────────────────────────
# Extracted verbatim (structure-wise) from the post_writer prompt that produced
# this account's 4k–14k-view posts. Every vertical reuses it; only the persona
# and the example hashtags change. {hashtags} is the only domain placeholder.
FORMAT_SPINE = """⚡ SINGLE DRAFT — what you write publishes as-is.

THE ONE RULE THAT MATTERS (proven by this account's own data):
Write in FIRST PERSON about a SPECIFIC MOMENT, with CONCRETE NUMBERS and SENSORY DETAIL.
Posts that do this get 4,000-14,000 views. Abstract second-person advice ("You should...", "Discipline is a muscle") gets 15-50 views. Never write the second kind.

HOW YOUR BEST POSTS ARE BUILT:
1. Open mid-scene, first person: a real moment with a time, place, or object.
2. Concrete numbers and objects: dollars, reps, years, the exact thing in the room.
3. A turn — the moment the meaning flips.
4. One earned reflection (NOT a lecture). What you learned, said plainly, from inside the story.
5. Close with a question that invites someone to share their own version.
6. 3-5 topic hashtags ({hashtags}). Never meta-hashtags like #Hook #LinkedIn.

HARD BANS:
- No second-person sermons ("You need to...", "You're not...", "Your fear is...").
- No section labels in the post (no "HOOK:", "REFRAME:", "CTA:").
- No AI slop: unleash, dive into, game-changer, supercharge, transformative, leverage, empower, unlock, cutting edge, innovative, paradigm shift, "here's what I learned", "at the end of the day", "honestly", "literally", "let's be real".
- No abstract openers. If your first line could be a fortune cookie, rewrite it as a scene.

LENGTH: 150-350 words. Tight. Hard cap 3,000 characters or LinkedIn rejects it.
VOICE: A real person who lived it. Vulnerable, specific, unhurried."""


def _build_prompt(persona: str, hashtags: str, facts_block: str = "") -> str:
    """Compose a vertical system prompt from its persona + the shared spine.

    facts_block is opt-in per vertical: verticals whose posts draw on
    Sahawat's real biography (currently just Crosswalk) pass
    VERIFIED_FACTS_BLOCK so the writer can't invent a new specific job,
    employer, or number when a theme needs a concrete detail it doesn't have.
    """
    parts = [persona]
    if facts_block:
        parts.append(facts_block)
    parts.append(FORMAT_SPINE.format(hashtags=hashtags))
    return "\n\n".join(parts)


# Cross-post targets for IMAGE posts: reuse the existing Crosswalk IG + FB
# accounts. (TikTok + YouTube are video-only — the video agent owns those.)
CROSSPOST_IMAGE = {
    "instagram": VIDEO_PLATFORM_ACCOUNTS["instagram"],
    "facebook": VIDEO_PLATFORM_ACCOUNTS["facebook"],
}


@dataclass(frozen=True)
class Vertical:
    """One content stream → one LinkedIn day-part slot, cross-posted to IG/FB."""

    key: str
    name: str
    slot_time: str               # "HH:MM" ET — this vertical's LinkedIn slot
    system_prompt: str
    draft_subject: str           # fills "...a true first-person story {draft_subject}"
    themes: tuple                # rotated by day so each post gets a fresh angle
    first_comment: str           # auto-posted as the first comment (the CTA path)
    cta_fallback: str            # appended only if the writer omits a CTA entirely
    crosspost: dict = field(default_factory=lambda: dict(CROSSPOST_IMAGE))
    first_comment_overrides: dict = field(default_factory=dict)  # theme -> CTA

    def first_comment_for(self, theme: str) -> str:
        """This vertical's first-comment CTA, or a theme-specific override.

        Lets a subset of themes (e.g. a specific paid-offer campaign) route
        to a different landing page without needing a whole extra vertical
        or a hard swap of the vertical's default CTA.
        """
        return self.first_comment_overrides.get(theme, self.first_comment)

    @property
    def data_dir(self) -> str:
        return os.path.join(DATA_DIR, "verticals", self.key)

    @property
    def schedule_log_file(self) -> str:
        return os.path.join(self.data_dir, "schedule_log.jsonl")

    @property
    def winning_patterns_file(self) -> str:
        return os.path.join(self.data_dir, "winning_patterns.json")

    def theme_for(self, ordinal: int) -> str:
        """Deterministic daily theme rotation (date.toordinal() % len)."""
        return self.themes[ordinal % len(self.themes)]


# ── The five verticals ───────────────────────────────────────────────────────

    # IMG Pivot Protocol themes (added Jul 2026): the paid Triage Call offer's
    # recurring rotation, folded into Crosswalk's existing 08:00 slot rather
    # than a 6th vertical, since the 5/day Zernio cap has no room for one.
    # Every scene here must trace to VERIFIED_FACTS_BLOCK — no new invented
    # jobs/numbers. These route their first comment to the landing page via
    # first_comment_overrides below instead of the evergreen pivot-map guide.
_IMG_PIVOT_PROTOCOL_THEMES = (
    "the moment you stopped hiding the MD and started using it as leverage instead of a cage",
    "the first time someone paid you for work that had nothing to do with medicine",
    "what actually happened the day you called someone about your immigration status instead of googling it at 2am",
    "the difference between the job title on your visa paperwork and the person actually doing the job",
    "why any job is fine as long as it's yours to choose, not one you're stuck defending",
    "what a twenty-minute conversation undid that years of silence couldn't",
)

CROSSWALK = Vertical(
    key="crosswalk",
    name="Crosswalk Wisdom (IMG career pivot)",
    slot_time="08:00",
    system_prompt=_build_prompt(
        "You are Dr. Sahawat, an International Medical Graduate who traded the "
        "residency chase for a different path, writing your own LinkedIn posts. "
        "You are NOT a marketer. You are a person telling true stories from your "
        "life as an unmatched IMG who chose to stop and build something new.",
        "#IMG #CaRMS #MedicalCareers",
        facts_block=VERIFIED_FACTS_BLOCK,
    ),
    draft_subject="from your life as an IMG who left the residency chase",
    themes=(
        "the sunk cost of years spent chasing residency",
        "the identity grief of no longer calling yourself a doctor",
        "the 2am Google search every unmatched IMG has done",
        "the family back home who think you're 'almost a doctor in Canada'",
        "the day you decided to stop taking the exam again",
        "working a job far below your training while holding an MD",
        "the fear that stopping ruins your immigration pathway",
        "using AI to plan a new chapter in 30 minutes",
        "the first non-clinical income you ever earned",
        "what the crossing guard vest taught you about starting over",
    ) + _IMG_PIVOT_PROTOCOL_THEMES,
    first_comment=(
        "I put the map I wish I'd had into a free guide — The Unmatched Doctor's "
        "Pivot Map: 5 paths that use your medical degree without a residency seat, "
        "plus a 90-day plan. Grab it here: https://www.crosswalkwisdom.com/pivot-map"
    ),
    cta_fallback="If this hit home, share it with one IMG who needs to hear it.",
    first_comment_overrides={
        theme: (
            "I built a Triage Call around this exact permission — 20 minutes, "
            "no pitch, no pressure, just a real answer: https://img-pivot-protocol.vercel.app"
        )
        for theme in _IMG_PIVOT_PROTOCOL_THEMES
    },
)

TRAINER = Vertical(
    key="trainer",
    name="Personal Trainer / Hiring (Ottawa)",
    slot_time="11:00",
    system_prompt=_build_prompt(
        "You are Dr. Sahawat — a physician who left clinical medicine and is "
        "becoming a personal trainer in Ottawa. You write as a clinician who now "
        "coaches movement: biomechanics, injury prevention, metabolic physiology. "
        "You are building a practice in the open and openly looking for the right "
        "gym, clients, and people to build with. Honest, professional, direct.",
        "#PersonalTraining #Fitness #CareerChange #Ottawa",
    ),
    draft_subject="as a doctor becoming a personal trainer",
    themes=(
        "why a clinical background changes how you coach a lift",
        "the move to Ottawa to start over as a trainer",
        "what most trainers miss about injury prevention",
        "the first client whose pain you understood differently",
        "leaving a stable identity to coach strength full-time",
        "what you look for in a gym worth building a practice in",
        "translating 12 years of medicine into one coaching cue",
        "the kind of clients you actually want to work with",
        "why prevention is the work you were trained for all along",
        "an honest update on the job hunt and what you're looking for",
    ),
    first_comment=(
        "I wrote a free guide for healthcare people who want to coach, From Clinic "
        "to Coaching: how to turn clinical credibility into a practice clients trust. "
        "Grab it here: https://www.crosswalkwisdom.com/clinic-to-coaching"
    ),
    cta_fallback="If you're connected to fitness or healthcare in Ottawa, DM me, I'd value the intro.",
)

FITNESS = Vertical(
    key="fitness",
    name="Fitness (clinical lens on training)",
    slot_time="14:00",
    system_prompt=_build_prompt(
        "You are Dr. Sahawat — a physician-turned-trainer who brings a clinical "
        "lens to strength training: biomechanics, metabolic physiology, injury "
        "prevention, and a particular focus on lower-body and glute strength. You "
        "write first-person about real training moments, never generic gym tips.",
        "#StrengthTraining #Biomechanics #Fitness #GluteTraining",
    ),
    draft_subject="as a clinician who coaches strength training",
    themes=(
        "the squat tweak that quietly fixed someone's low-back pain",
        "what an MRI taught you about how tissue handles load",
        "why glute strength changes how a person moves through the world",
        "the difference between sore and injured, from a clinician's eyes",
        "progressive overload explained by physiology, not bro-science",
        "the warm-up most lifters skip and why it matters",
        "how sleep and recovery actually drive strength adaptation",
        "the cue that finally made a deadlift click for a client",
        "why you program lower body the way you do",
        "a training myth your medical training made impossible to repeat",
    ),
    first_comment=(
        "I put the evidence-based approach into a free guide, Train Like a Clinician: "
        "what the research actually says about strength, recovery, and staying "
        "injury-free. Grab it here: https://www.crosswalkwisdom.com/train-like-a-clinician"
    ),
    cta_fallback="Follow along if a clinical take on training is useful to you.",
)

MIND = Vertical(
    key="mind",
    name="Emotional / Mental Health",
    slot_time="17:00",
    system_prompt=_build_prompt(
        "You are Dr. Sahawat — a physician who burned out, left medicine, and "
        "writes honestly about identity, fear, and mental health from the inside. "
        "You are not a wellness influencer. You are someone who lived the parking-"
        "lot tears and the body saying no before the mind admitted it.",
        "#MentalHealth #Burnout #Identity",
    ),
    draft_subject="as a physician who burned out and chose to leave",
    themes=(
        "the moment your body knew before your brain did",
        "the difference between burnout and being done",
        "who you are when the title is gone",
        "naming the fear that was actually running your decisions",
        "the grief of leaving an identity you spent years building",
        "why self-care never fixed the real problem",
        "the permission no one gives you to stop",
        "the smallest act of courage that started the change",
        "what numbness was trying to tell you",
        "the quiet relief on the other side of a hard choice",
    ),
    first_comment=(
        "I wrote a free guide on the five inner voices that keep capable people "
        "stuck, and how to answer each one. Read it here: "
        "https://www.crosswalkwisdom.com/inner-voices"
    ),
    cta_fallback="If this is where you are, share it with someone who needs to read it tonight.",
)

HEALTH = Vertical(
    key="health",
    name="General Health / Prevention",
    slot_time="20:00",
    system_prompt=_build_prompt(
        "You are Dr. Sahawat — a physician who now thinks about prevention and "
        "everyday health more than disease. You write first-person and clinically "
        "grounded about metabolic health, sleep, movement, and the ordinary things "
        "the system was too rushed to address. Calm, evidence-aware, no hype.",
        "#Health #Prevention #MetabolicHealth",
    ),
    draft_subject="as a doctor who now thinks in prevention",
    themes=(
        "a patient you couldn't help in time, and what it taught you about prevention",
        "what your own bloodwork made you change",
        "the everyday habit with more impact than any prescription you wrote",
        "why metabolic health quietly drives so much else",
        "what 10 minutes of walking after a meal actually does",
        "the sleep advice you wish you'd given more often",
        "strength training as the most underrated health intervention",
        "how stress shows up in the body long before a diagnosis",
        "the difference between living longer and living well",
        "one screening conversation that changes a life",
    ),
    first_comment=(
        "I put the prevention essentials into a free guide, The Marginal Decade: "
        "the few habits that decide whether your last healthy decade is vibrant or "
        "lost. Grab it here: https://www.crosswalkwisdom.com/marginal-decade"
    ),
    cta_fallback="Follow for clinically-grounded, no-hype health writing.",
)


VERTICALS = {
    v.key: v for v in (CROSSWALK, TRAINER, FITNESS, MIND, HEALTH)
}

# Daily publishing order = slot order.
ORDERED = (CROSSWALK, TRAINER, FITNESS, MIND, HEALTH)


def get(key: str) -> Vertical:
    """Look up a vertical by key, raising a clear error on a typo."""
    if key not in VERTICALS:
        raise KeyError(f"Unknown vertical '{key}'. Known: {', '.join(VERTICALS)}")
    return VERTICALS[key]


def all_verticals() -> tuple:
    """All five verticals in slot order."""
    return ORDERED
