"""Viral hook framework library (the Blotato 100-hook pack, as data).

Ported from the installed `viral-hooks` Claude skill so the generator can GROUND
its opening lines in proven frameworks instead of free-forming them. Pure data +
pure functions — no API key, no network. The writer injects `frameworks_block()`
into the draft prompt; the grader (virality_grader.py) scores the result.

Categories are ordered by virality ceiling, highest first. For THIS account the
proven winners are first-person scenes with real numbers (Receipt / Confession /
Transformation), so `pick_categories` biases toward those when a theme is vague.
"""

from __future__ import annotations

# ── The 100 frameworks, by category (templates keep [brackets] to fill) ───────
HOOK_LIBRARY: dict[str, dict] = {
    "receipt": {
        "name": "The Receipt (proof, numbers, results)",
        "why": "Earned credibility + a specific number + an open loop.",
        "templates": [
            "I tested [N] [things]. Only [smaller N] worked.",
            "I [did specific thing] for [time period]. Here's what happened.",
            "[Big accomplishment] — here are [N] lessons.",
            "I audited [N] [things]. Here are [N] tips to [outcome].",
            "I asked [N] experts about [topic]. Here's what they said.",
            "How I went from [past situation] to [result] in [time].",
            "Here's how I [achieved result] in [time frame].",
            "Here's proof that [claim everyone doubts].",
        ],
    },
    "contrarian": {
        "name": "Contrarian / Myth-Buster",
        "why": "Forces the reader to pick a side. Polarity drives comments.",
        "templates": [
            "Most people think [common belief]. Here's why they're wrong.",
            "[Common practice] is dead. Stop doing it for [outcome].",
            "Everything you know about [subject] is wrong.",
            "Here's why [common advice] doesn't work.",
            "[Topic] is overrated.",
            "Unpopular opinion: [contrarian take].",
            "Here's why I disagree with [common belief].",
            "Here's why [popular product] isn't worth the hype.",
        ],
    },
    "negative_frame": {
        "name": "Negative Frame / Mistake Callout",
        "why": "Loss aversion. People click faster to avoid a mistake.",
        "templates": [
            "[N] mistakes you're making with [task].",
            "Stop doing [common action] right now.",
            "Do not [common action] unless you know these [N] secrets.",
            "Here's why you're failing at [task].",
            "As a [niche], please stop making this mistake.",
            "Here's why you've been doing [task] wrong all along.",
            "Don't make the same mistake I did with [thing].",
        ],
    },
    "stolen_lessons": {
        "name": "Stolen Lessons / Steal This",
        "why": "Borrowed credibility + a tactic the reader can copy.",
        "templates": [
            "I copied [specific thing]. Here's what happened.",
            "[Famous brand] does [specific thing]. I tried it. Result: [outcome].",
            "Here's a [industry] hack [experts] don't want you to know.",
            "Here's what [influencer] doesn't tell you about [topic].",
            "[Famous person] makes [money] a month. We're about to steal it.",
        ],
    },
    "curiosity_gap": {
        "name": "Curiosity Gap / Open Loop",
        "why": "Open a question in line 1 and withhold the answer.",
        "templates": [
            "Here's what nobody tells you about [topic].",
            "[N] things that feel illegal to know.",
            "Here's the hidden truth about [situation].",
            "Here's what I wish I knew before I started.",
            "Here's a secret I learned the hard way.",
            "Here's what happened when I tried [action].",
        ],
    },
    "listicle": {
        "name": "Listicle / Number Hook",
        "why": "A specific count promises a skimmable payoff.",
        "templates": [
            "[N] things about [niche] I wish I knew earlier.",
            "[N] surprising facts about [topic] that will [outcome].",
            "Here are [N] signs that you should [action].",
            "[N] ways to level up your [area].",
            "[N] things you need to stop doing right now.",
        ],
    },
    "secret": {
        "name": "Secret / Insider",
        "why": "Promises access to gated knowledge.",
        "templates": [
            "[Industry] does not want you to know this secret.",
            "Here's the secret to [outcome].",
            "Here's a secret I haven't shared before.",
            "The secret to [topic] is [secret most people skip].",
        ],
    },
    "audience_callout": {
        "name": "Audience Callout / Pattern Interrupt",
        "why": "Names the exact reader so the right person stops.",
        "templates": [
            "[Specific group], stop scrolling.",
            "Attention [group], you need to see this.",
            "99% of [audience] don't understand this.",
            "98% of [niche] gets this wrong. Maybe you do too.",
            "[Specific group], don't [action]. Here's why.",
        ],
    },
    "question": {
        "name": "Question Hook",
        "why": "A question the reader answers in their head.",
        "templates": [
            "Did you know [shocking statistic]?",
            "Are you still [common action]?",
            "Ever wonder why [pain point] keeps happening?",
            "Have you ever felt [specific emotion]?",
            "Are you making this mistake with [task]?",
        ],
    },
    "transformation": {
        "name": "Transformation / Before-After / Story",
        "why": "The gap between before and after is the hook.",
        "templates": [
            "How I [achieved result] without [common requirement].",
            "I challenged myself to [hard thing]. Here's what happened.",
            "I did [thing] for a week. Here's what happened.",
            "Here's the before and after of [project].",
            "A day in the life of a [profession] making [money] a month.",
        ],
    },
    "speed": {
        "name": "Speed / Effortless How-To",
        "why": "Low effort + fast result removes the reason to scroll past.",
        "templates": [
            "Here's how to [goal] in just [short time].",
            "Here's how to [goal] without [common obstacle].",
            "Here's how to [goal] with zero experience.",
            "Here's a shortcut to [goal].",
        ],
    },
    "urgency": {
        "name": "Urgency / FOMO / Stop-Scroll",
        "why": "A reason to act now. Use sparingly.",
        "templates": [
            "Don't scroll if you want to [achieve something].",
            "Here's your sign to try [activity].",
            "This changes everything about [topic].",
            "Save this for [the moment you'll need it].",
        ],
    },
    "confession": {
        "name": "Confession / Vulnerable",
        "why": "A real admission earns trust and 3-10x engagement.",
        "templates": [
            "I almost [near-disaster]. Here's what saved me.",
            "I can't believe I'm about to say this, but [admission].",
            "Don't hate me, but [hard truth].",
            "I have to confess something I've avoided saying.",
            "I used to [do thing wrong]. Now I swear by [the fix].",
        ],
    },
}

# Virality ceiling order (highest first).
CATEGORY_ORDER: tuple[str, ...] = (
    "receipt", "contrarian", "negative_frame", "stolen_lessons", "curiosity_gap",
    "listicle", "secret", "audience_callout", "question", "transformation",
    "speed", "urgency", "confession",
)

# Theme/wedge keyword → category. First match wins, in scan order.
_KEYWORD_MAP: tuple[tuple[tuple[str, ...], str], ...] = (
    (("tested", "results", "proof", "data", "dollars", "$", "numbers", "audited", "earned"), "receipt"),
    (("most people", "myth", "overrated", "wrong", "unpopular", "disagree", "everyone thinks"), "contrarian"),
    (("mistake", "stop ", "avoid", "failing", "don't ", "wrong all along"), "negative_frame"),
    (("copied", "stole", "steal", "famous", "hack"), "stolen_lessons"),
    (("almost", "confess", "ashamed", "grief", "burned out", "cried", "afraid", "fear", "identity"), "confession"),
    (("before", "after", "transformation", "went from", "day in the life", "challenge"), "transformation"),
    (("secret", "nobody tells", "hidden", "wish i knew"), "curiosity_gap"),
    (("how to", "shortcut", "fast", "in minutes", "without"), "speed"),
)

# For THIS account, first-person scene + real numbers wins. Bias vague themes here.
DEFAULT_CATEGORIES: tuple[str, ...] = ("confession", "receipt", "transformation")


def pick_categories(text: str, limit: int = 2) -> list[str]:
    """Suggest the best hook categories for a theme / wedge string."""
    text_l = (text or "").lower()
    hits: list[str] = []
    for needles, category in _KEYWORD_MAP:
        if any(n in text_l for n in needles) and category not in hits:
            hits.append(category)
        if len(hits) >= limit:
            return hits
    # Top up from the account's proven defaults without duplicating.
    for category in DEFAULT_CATEGORIES:
        if category not in hits:
            hits.append(category)
        if len(hits) >= limit:
            break
    return hits[:limit]


def frameworks_block(text: str, categories: int = 2, per_category: int = 4) -> str:
    """A compact prompt-injection block of proven frameworks for this theme.

    Grounds the draft's opening line in tested patterns. Returns "" defensively
    if something is off, so the caller can always concatenate it safely.
    """
    chosen = pick_categories(text, limit=categories)
    if not chosen:
        return ""
    lines = ["PROVEN HOOK FRAMEWORKS (shape your opening line like ONE of these — "
             "fill every [bracket] with a REAL number, name, or moment, never a placeholder):"]
    for key in chosen:
        cat = HOOK_LIBRARY.get(key)
        if not cat:
            continue
        lines.append(f"\n{cat['name']} — {cat['why']}")
        for tpl in cat["templates"][:per_category]:
            lines.append(f"  - {tpl}")
    lines.append("\nFirst-3-words test: the first 3 words alone must create curiosity, "
                 "surprise, or emotional pull. 'Here's what I' fails. 'I tested 47' passes.")
    return "\n".join(lines)


def all_templates() -> list[str]:
    """Flat list of every template (used by tests / inspection)."""
    return [t for cat in HOOK_LIBRARY.values() for t in cat["templates"]]
