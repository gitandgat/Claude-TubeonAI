"""
Free-Sample Generator for the Competitor Content Engine offer.

Given a prospect (a career-course creator) and their parasite-target "king"
(the category-leading YouTube channel), this:
  1. Mines the king's recent videos (yt-dlp, flat = fast).
  2. Mines the prospect's own recent videos (so we don't suggest what they cover).
  3. Asks the AI layer for a gap analysis + 5 ready-to-post pieces.
  4. Renders a 1-page teaser markdown = the cold-email deliverable.

Mining works with no API keys (yt-dlp only). The AI step reuses the repo's
ai_client_factory (Ollama -> Claude fallback); if that's unavailable it still
writes the raw mined data + the analysis prompt so nothing is lost.

Usage:
    python free_sample_generator.py \
        --prospect "Trent Dressel" \
        --prospect-channel "https://www.youtube.com/c/trentdressel/videos" \
        --king "Patrick Dang" \
        --king-channel "https://www.youtube.com/channel/UCLOzkJ9W9fntCGyYfUwMPew/videos" \
        --vertical "tech sales career" \
        --out out/trent-dressel.md
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
MINE_COUNT = 25  # videos to pull per channel


@dataclass(frozen=True)
class Video:
    title: str
    video_id: str
    view_count: Optional[int] = None


def _ytdlp_bin() -> str:
    return shutil.which("yt-dlp") or "/Library/Frameworks/Python.framework/Versions/3.14/bin/yt-dlp"


def mine_channel(channel_url: str, n: int = MINE_COUNT) -> list[Video]:
    """Pull the n most recent videos from a channel (flat = fast, view_count often NA)."""
    cmd = [
        _ytdlp_bin(), channel_url,
        "--flat-playlist",
        "--print", "%(view_count)s|||%(title)s|||%(id)s",
        "-I", f"1:{n}",
        "--no-warnings",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        print(f"  ! yt-dlp timed out on {channel_url}")
        return []
    videos: list[Video] = []
    for line in result.stdout.strip().splitlines():
        parts = line.split("|||")
        if len(parts) != 3:
            continue
        views, title, vid = parts
        videos.append(Video(title=title.strip(), video_id=vid.strip(),
                            view_count=int(views) if views.isdigit() else None))
    return videos


def build_prompt(prospect: str, king: str, vertical: str,
                 king_vids: list[Video], prospect_vids: list[Video]) -> str:
    king_list = "\n".join(f"- {v.title}" for v in king_vids) or "(none found)"
    own_list = "\n".join(f"- {v.title}" for v in prospect_vids) or "(none found)"
    return f"""You are a content strategist. {prospect} is a {vertical} coach who sells a \
course and runs a YouTube channel. Their biggest competitor ("the king") is {king}.

THE KING'S RECENT VIDEOS:
{king_list}

{prospect}'S OWN RECENT VIDEOS:
{own_list}

Produce a tight, specific "content gap report" with:
1. THE DRIFT: any topics the king has moved AWAY from (vacated audience = opportunity).
2. 3 TOPICS THE KING WINS ON that {prospect} barely covers.
3. 5 READY-TO-POST PIECES for {prospect}: each = a scroll-stopping TITLE + a 2-line \
angle on why it wins. Rebuild the king's best ideas BETTER for {prospect}'s audience, \
and ride any wave the king is riding but inside {prospect}'s lane.
Be concrete. No fluff. This is a free sample to earn a sales call."""


def run_ai(prompt: str) -> Optional[str]:
    """Best-effort call through the repo's AI factory. Returns None if unavailable."""
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from ai_client_factory import get_ai_client, call_ai
    except Exception as e:  # noqa: BLE001 - degrade gracefully, never hard-fail
        print(f"  ! AI factory unavailable ({e}); writing prompt for manual run.")
        return None
    try:
        _provider, client = get_ai_client()  # factory returns (provider, client)
        return call_ai(client, messages=[{"role": "user", "content": prompt}],
                       system="You write sharp, specific content strategy. No clichés.",
                       max_tokens=1800)
    except Exception as e:  # noqa: BLE001
        print(f"  ! AI call failed ({e}); writing prompt for manual run.")
        return None


def render(prospect: str, king: str, analysis: Optional[str], prompt: str,
           king_vids: list[Video]) -> str:
    body = analysis or (
        "_AI layer was unavailable when this ran — run the prompt below through "
        "Claude/Ollama to fill this section._\n\n```\n" + prompt + "\n```")
    mined = "\n".join(f"- {v.title}" for v in king_vids[:15]) or "(none)"
    return f"""# Content Gap Report — {prospect}
### vs. {king} (your category's biggest channel)

> Built free, before you've paid a cent. If this is useful, I have the other 25.

{body}

---
<details><summary>Raw material I mined from {king} (most recent 15)</summary>

{mined}
</details>

*Generated by the Competitor Content Engine.*
"""


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--prospect", required=True)
    p.add_argument("--prospect-channel", required=True)
    p.add_argument("--king", required=True)
    p.add_argument("--king-channel", required=True)
    p.add_argument("--vertical", default="career")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    print(f"Mining {args.king}...")
    king_vids = mine_channel(args.king_channel)
    print(f"  -> {len(king_vids)} videos")
    print(f"Mining {args.prospect}...")
    prospect_vids = mine_channel(args.prospect_channel)
    print(f"  -> {len(prospect_vids)} videos")

    prompt = build_prompt(args.prospect, args.king, args.vertical, king_vids, prospect_vids)
    print("Running gap analysis...")
    analysis = run_ai(prompt)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(args.prospect, args.king, analysis, prompt, king_vids))
    # Sidecar JSON of mined data for the scraper/CRM
    out.with_suffix(".json").write_text(json.dumps(
        {"prospect": args.prospect, "king": args.king,
         "king_videos": [asdict(v) for v in king_vids],
         "prospect_videos": [asdict(v) for v in prospect_vids]}, indent=2))
    print(f"✓ Wrote {out}  (AI section: {'filled' if analysis else 'prompt-only'})")


if __name__ == "__main__":
    main()
