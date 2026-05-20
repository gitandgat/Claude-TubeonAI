"""
Discovers fresh health & wellness YouTube videos via yt-dlp search.
Tracks seen video IDs in seen_videos.json to avoid duplicates.
"""
import json, os, subprocess, datetime, random
from pathlib import Path
from typing import List, Dict

SEEN_FILE = Path("seen_videos.json")

# Rotated daily for content variety
SEARCH_QUERIES = [
    "health wellness science habits",
    "mental health burnout recovery psychology",
    "nutrition gut health diet science",
    "sleep optimization recovery performance",
    "stress nervous system regulation",
    "longevity healthy aging lifestyle",
    "mindset behavior change motivation",
    "fitness exercise movement science evidence",
    "immune system inflammation nutrition",
    "anxiety depression mental wellness tools",
]

HEALTH_KEYWORDS = [
    "health", "wellness", "fitness", "nutrition", "mental", "burnout",
    "anxiety", "sleep", "diet", "exercise", "mindset", "stress", "brain",
    "gut", "hormone", "immune", "therapy", "habit", "trauma", "psychology",
    "neuroscience", "longevity", "recovery", "inflammation", "biohack",
]


def load_seen() -> set:
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def save_seen(seen: set):
    SEEN_FILE.write_text(json.dumps(sorted(seen), indent=2))


def is_health_related(title: str) -> bool:
    t = title.lower()
    return any(kw in t for kw in HEALTH_KEYWORDS)


def search_youtube(query: str, n: int = 15) -> List[Dict]:
    """Run yt-dlp search and return video dicts."""
    import shutil
    ytdlp = shutil.which("yt-dlp") or "/Library/Frameworks/Python.framework/Versions/3.14/bin/yt-dlp"
    cmd = [
        ytdlp,
        f"ytsearch{n}:{query}",
        "--print", "%(title)s|||%(webpage_url)s|||%(id)s",
        "--no-download",
        "--quiet",
        "--no-warnings",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        videos = []
        for line in result.stdout.strip().split("\n"):
            if "|||" not in line:
                continue
            parts = line.split("|||")
            if len(parts) == 3:
                videos.append({"title": parts[0], "url": parts[1], "id": parts[2]})
        return videos
    except subprocess.TimeoutExpired:
        print("  Warning: yt-dlp search timed out")
        return []


def get_fresh_videos(n: int = 5) -> List[Dict]:
    """Return n unseen health/wellness videos, tracking what's been used."""
    seen = load_seen()

    # Pick 2 queries based on day of week for daily variety
    day = datetime.date.today().weekday()
    q1 = SEARCH_QUERIES[day % len(SEARCH_QUERIES)]
    q2 = SEARCH_QUERIES[(day + 1) % len(SEARCH_QUERIES)]

    candidates = []
    for query in [q1, q2]:
        print(f"  Searching: {query}")
        for v in search_youtube(query):
            if v["id"] not in seen and is_health_related(v["title"]):
                if not any(c["id"] == v["id"] for c in candidates):
                    candidates.append(v)

    if len(candidates) < n:
        # Fallback: broader search
        print("  Fallback search: health wellness 2026")
        for v in search_youtube("health wellness 2026", 20):
            if v["id"] not in seen and is_health_related(v["title"]):
                if not any(c["id"] == v["id"] for c in candidates):
                    candidates.append(v)

    random.shuffle(candidates)
    selected = candidates[:n]

    # Mark as seen
    for v in selected:
        seen.add(v["id"])
    save_seen(seen)

    return selected
