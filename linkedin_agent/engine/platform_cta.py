"""Per-platform CTA mapping (Blotato post-writer Step 4.5).

Each platform's algorithm rewards a different metric, so the same post should
close with the CTA that drives THAT metric:

    LinkedIn  -> comments   (its closing question already does this)
    Instagram -> saves      ("Save this...", "Send this to...")
    Facebook  -> shares     ("Tag someone who...")
    Twitter/X -> replies
    Threads   -> replies
    TikTok    -> completion / follows
    YouTube   -> watch-time / subscribes

The verticals pipeline writes ONE LinkedIn-shaped post and cross-posts it to
IG/FB via Zernio per-platform `customContent`. This module adapts the cross-post
copy so IG/FB get a save/share cue instead of a LinkedIn comment-question.

Pure functions, no API. CTA lines are written to pass stop-slop: plain words, no
em dashes, no filler, contractions where natural.
"""

from __future__ import annotations

REWARDED_METRIC: dict[str, str] = {
    "linkedin": "comments",
    "instagram": "saves",
    "facebook": "shares",
    "twitter": "replies",
    "threads": "replies",
    "bluesky": "replies",
    "tiktok": "completion",
    "youtube": "watch-time",
}

# Algorithm-aligned CTA line per platform. LinkedIn is intentionally empty — its
# proven format already closes with a comment-driving universal question, so we
# don't bolt a second CTA onto the measured channel.
_PLATFORM_CTA: dict[str, str] = {
    "linkedin": "",
    "instagram": "Save this for the next hard day, and send it to one person who needs it.",
    "facebook": "Tag someone who needs to read this today.",
    "twitter": "What's your version? Reply and tell me.",
    "threads": "What's your version? Reply and tell me.",
    "bluesky": "What's your version? Reply and tell me.",
    "tiktok": "Follow for more, and save this one for later.",
    "youtube": "Subscribe for more stories like this one.",
}


def rewarded_metric(platform: str) -> str:
    """The engagement metric a platform's algorithm rewards most."""
    return REWARDED_METRIC.get((platform or "").lower(), "comments")


def cta_for(platform: str, vertical=None) -> str:
    """The algorithm-aligned CTA line for a platform ("" for LinkedIn).

    `vertical` may carry a `crosspost_cta` override; fall back to the platform
    default otherwise. Kept duck-typed so any object with that attr works.
    """
    platform = (platform or "").lower()
    override = getattr(vertical, "crosspost_cta", None)
    if override and platform != "linkedin":
        return override
    return _PLATFORM_CTA.get(platform, "")


def apply_crosspost_cta(post_content: str, platform: str, vertical=None) -> str:
    """Return `post_content` adapted for `platform`'s rewarded metric.

    LinkedIn (and unknown platforms with no CTA) is returned unchanged. For
    IG/FB/etc the platform CTA is inserted just before the trailing hashtag block
    (or appended if there are none). Idempotent: if the cue is already present,
    the content is left as-is so re-runs don't stack CTAs.
    """
    cta = cta_for(platform, vertical)
    if not cta:
        return post_content

    # Don't double up if the post already carries this cue.
    probe = cta.split(",")[0].strip().lower()
    if probe and probe in post_content.lower():
        return post_content

    lines = post_content.rstrip().split("\n")
    hashtag_index = next(
        (i for i, line in enumerate(lines) if line.strip().startswith("#")),
        None,
    )
    if hashtag_index is not None:
        lines.insert(hashtag_index, cta + "\n")
        return "\n".join(lines)
    return post_content.rstrip() + "\n\n" + cta
