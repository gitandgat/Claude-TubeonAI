"""
Lead Scraper for the Competitor Content Engine offer (Nick Saraev automation #2).

Discovers *challenger-tier* career-coach channels per sub-vertical, then filters
out the category kings by subscriber count. Output = expansion rows for
seed-prospects.csv, ready for the email-enrichment step.

Two phases, both yt-dlp only (no API keys):
  1. DISCOVER  - flat search across each sub-vertical's query set (fast).
  2. SIZE      - fetch each unique channel's follower count, keep only the
                 challenger band (default 3K-250K: big enough to have a course,
                 small enough to still feel the king's pressure).

Usage:
    python lead_scraper.py --vertical "tech sales" --per-query 15 --max-channels 25
    python lead_scraper.py --all --min-subs 3000 --max-subs 250000
"""
from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

OUT_DIR = Path(__file__).resolve().parent / "scraped"

# Each sub-vertical -> search queries that surface course-selling career coaches.
SUBVERTICAL_QUERIES: dict[str, list[str]] = {
    "tech sales": ["break into tech sales", "SDR cold calling tips", "tech sales AE career",
                   "how to get into tech sales", "SDR to AE promotion", "B2B sales prospecting tips",
                   "account executive day in the life", "tech sales interview prep",
                   "sales career advice software", "cold calling live examples"],
    "swe interview": ["system design interview", "coding interview prep faang", "leetcode explained"],
    "data science": ["break into data science", "data analyst portfolio", "data science career advice"],
    "product management": ["product manager interview", "break into product management", "PM career coach"],
    "job search": ["resume tips career coach", "job interview tips", "linkedin job search strategy"],
    "ux design": ["break into UX design", "UX portfolio review", "UX career coach"],
    "cybersecurity": ["break into cybersecurity", "cybersecurity career path", "soc analyst job"],
    "break into tech": ["break into tech no coding", "career change into tech", "tech job no experience"],
}

# Known kings to drop even if inside the band (they have content teams already).
KNOWN_KINGS = {
    "bytebytego", "neetcode", "linda raynier", "patrick dang", "self made millennial",
    "tina huang", "alex the analyst", "exponent", "mayuko", "dan lok", "jordan belfort",
}


@dataclass(frozen=True)
class Candidate:
    channel: str
    channel_url: str
    followers: Optional[int]
    sub_vertical: str
    example_video: str


def _ytdlp() -> str:
    return shutil.which("yt-dlp") or "/Library/Frameworks/Python.framework/Versions/3.14/bin/yt-dlp"


def discover(query: str, n: int) -> list[tuple[str, str, str]]:
    """Flat search -> (channel, channel_url, example_title) tuples."""
    cmd = [_ytdlp(), f"ytsearch{n}:{query}", "--flat-playlist",
           "--print", "%(channel)s|||%(channel_url)s|||%(title)s", "--no-warnings"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=90).stdout
    except subprocess.TimeoutExpired:
        return []
    rows = []
    for line in out.strip().splitlines():
        parts = line.split("|||")
        if len(parts) == 3 and parts[1].startswith("http"):
            rows.append((parts[0].strip(), parts[1].strip(), parts[2].strip()))
    return rows


def followers(channel_url: str) -> Optional[int]:
    """One non-flat video extraction yields the channel's follower count."""
    cmd = [_ytdlp(), channel_url, "-I", "1", "--print", "%(channel_follower_count)s", "--no-warnings"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout.strip()
    except subprocess.TimeoutExpired:
        return None
    first = out.splitlines()[0] if out else ""
    return int(first) if first.isdigit() else None


def scrape(vertical: str, per_query: int, max_channels: int,
           min_subs: int, max_subs: int) -> list[Candidate]:
    seen: dict[str, tuple[str, str]] = {}  # channel_url -> (channel, example)
    for q in SUBVERTICAL_QUERIES[vertical]:
        print(f"  discover: {q!r}")
        for channel, url, title in discover(q, per_query):
            if url not in seen and channel.lower() not in KNOWN_KINGS:
                seen[url] = (channel, title)
    print(f"  -> {len(seen)} unique channels; sizing (cap {max_channels})...")

    kept: list[Candidate] = []
    for url, (channel, title) in list(seen.items())[:max_channels]:
        subs = followers(url)
        if subs is not None and min_subs <= subs <= max_subs:
            kept.append(Candidate(channel, url, subs, vertical, title))
            print(f"    ✓ {channel} ({subs:,})")
        else:
            print(f"    · skip {channel} ({subs})")
    return kept


def write_csv(rows: list[Candidate], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["channel", "channel_url", "followers", "sub_vertical",
                    "example_video", "tier", "needs"])
        for c in sorted(rows, key=lambda x: -(x.followers or 0)):
            w.writerow([c.channel, c.channel_url, c.followers, c.sub_vertical,
                        c.example_video, "challenger",
                        "verify sells course/cohort; enrich email"])
    print(f"✓ wrote {len(rows)} rows -> {path}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--vertical", choices=sorted(SUBVERTICAL_QUERIES))
    p.add_argument("--all", action="store_true")
    p.add_argument("--per-query", type=int, default=15)
    p.add_argument("--max-channels", type=int, default=25)
    p.add_argument("--min-subs", type=int, default=3000)
    p.add_argument("--max-subs", type=int, default=250000)
    args = p.parse_args()

    verticals = sorted(SUBVERTICAL_QUERIES) if args.all else [args.vertical]
    if not verticals or verticals == [None]:
        p.error("pass --vertical <name> or --all")

    for v in verticals:
        print(f"\n=== {v} ===")
        rows = scrape(v, args.per_query, args.max_channels, args.min_subs, args.max_subs)
        write_csv(rows, OUT_DIR / f"{v.replace(' ', '-')}.csv")


if __name__ == "__main__":
    main()
