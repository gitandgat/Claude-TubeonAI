"""Client tenant layer for the managed LinkedIn ghostwriting service.

The five verticals in `verticals.py` are five content lenses on ONE LinkedIn
account (Dr. Sahawat). A *client* is a different paying person: their own voice,
niche, LinkedIn/Zernio account, and isolated learning data.

A `Client` is intentionally duck-compatible with `verticals.Vertical` — it
exposes the same `.system_prompt`, `.draft_subject`, `.cta_fallback`,
`.winning_patterns_file`, and `.schedule_log_file` attributes — so it drops
straight into `PostWriter(vertical=client)` with zero changes to the proven
generator.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime

from linkedin_agent.config import DATA_DIR
from linkedin_agent.verticals import FORMAT_SPINE

CLIENTS_DIR = os.path.join(DATA_DIR, "clients")

DEFAULT_HASHTAGS = "#LinkedIn"
DEFAULT_CTA = "If this resonated, share it with someone who needs it today."


def slugify(name: str) -> str:
    """Filesystem-safe slug from a client name ('Jane Doe' -> 'jane-doe')."""
    slug = "".join(c.lower() if c.isalnum() else "-" for c in name.strip())
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "client"


@dataclass(frozen=True)
class Client:
    """One paying ghostwriting client — their own voice, niche, and data dir."""

    slug: str
    name: str
    niche: str
    system_prompt: str
    draft_subject: str
    themes: tuple
    first_comment: str
    cta_fallback: str
    hashtags: str = ""
    zernio_account_id: str | None = None  # set when they go live; None during demo
    created_at: str = ""
    # Their own IG/FB Zernio accounts for cross-posting (empty = LinkedIn only).
    # Present so Client is fully duck-compatible with verticals.Vertical.
    crosspost: dict = field(default_factory=dict)

    @property
    def key(self) -> str:
        """Alias for slug — keeps Client interchangeable with Vertical (which
        the Scheduler's logger reads as `.key`)."""
        return self.slug

    @property
    def data_dir(self) -> str:
        return os.path.join(CLIENTS_DIR, self.slug)

    @property
    def config_file(self) -> str:
        return os.path.join(self.data_dir, "config.json")

    @property
    def voice_profile_file(self) -> str:
        return os.path.join(self.data_dir, "voice_profile.json")

    @property
    def winning_patterns_file(self) -> str:
        return os.path.join(self.data_dir, "winning_patterns.json")

    @property
    def schedule_log_file(self) -> str:
        return os.path.join(self.data_dir, "schedule_log.jsonl")

    def theme_for(self, ordinal: int) -> str:
        """Deterministic daily theme rotation (mirrors Vertical.theme_for)."""
        return self.themes[ordinal % len(self.themes)]


def build_client(
    name: str,
    niche: str,
    *,
    hashtags: str = "",
    themes: tuple | list | None = None,
    subject: str | None = None,
    first_comment: str = "",
    cta_fallback: str = "",
    zernio_account_id: str | None = None,
    slug: str | None = None,
) -> Client:
    """Compose a Client, building its system prompt from the proven FORMAT_SPINE."""
    persona = (
        f"You are {name}, writing your own LinkedIn posts about {niche}. "
        "You are NOT a marketer. You write true first-person stories from your "
        "own life and work — specific moments, real numbers, honest reflection."
    )
    system_prompt = f"{persona}\n\n{FORMAT_SPINE.format(hashtags=hashtags or DEFAULT_HASHTAGS)}"
    cta = cta_fallback or DEFAULT_CTA
    return Client(
        slug=slug or slugify(name),
        name=name,
        niche=niche,
        system_prompt=system_prompt,
        draft_subject=subject or f"from your work in {niche}",
        themes=tuple(themes or ()),
        first_comment=first_comment or cta,
        cta_fallback=cta,
        hashtags=hashtags,
        zernio_account_id=zernio_account_id,
        created_at=datetime.now().isoformat(),
    )


def save_client(client: Client) -> str:
    """Persist the client config and guarantee its data files exist."""
    os.makedirs(client.data_dir, exist_ok=True)
    # Touch the schedule log so PostWriter's repetition guard never crashes on
    # a brand-new client (dedup reads this file).
    if not os.path.exists(client.schedule_log_file):
        open(client.schedule_log_file, "a").close()
    data = asdict(client)
    data["themes"] = list(client.themes)
    with open(client.config_file, "w") as f:
        json.dump(data, f, indent=2)
    return client.config_file


def load_client(slug: str) -> Client:
    """Load a saved client by slug."""
    path = os.path.join(CLIENTS_DIR, slug, "config.json")
    with open(path) as f:
        data = json.load(f)
    return Client(
        slug=data["slug"],
        name=data["name"],
        niche=data["niche"],
        system_prompt=data["system_prompt"],
        draft_subject=data["draft_subject"],
        themes=tuple(data.get("themes", ())),
        first_comment=data["first_comment"],
        cta_fallback=data["cta_fallback"],
        hashtags=data.get("hashtags", ""),
        zernio_account_id=data.get("zernio_account_id"),
        created_at=data.get("created_at", ""),
        crosspost=data.get("crosspost", {}),
    )


def list_clients() -> list[str]:
    """All saved client slugs."""
    if not os.path.isdir(CLIENTS_DIR):
        return []
    return sorted(
        d for d in os.listdir(CLIENTS_DIR)
        if os.path.exists(os.path.join(CLIENTS_DIR, d, "config.json"))
    )


def save_voice_profile(client: Client, profile: dict) -> None:
    os.makedirs(client.data_dir, exist_ok=True)
    with open(client.voice_profile_file, "w") as f:
        json.dump(profile, f, indent=2)


def load_voice_profile(client: Client) -> dict:
    try:
        with open(client.voice_profile_file) as f:
            return json.load(f)
    except Exception:
        return {}
