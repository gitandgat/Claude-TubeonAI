"""
Video Ranking System
====================
Intelligently scores and ranks videos for selection based on:
  - Content relevance to health/wellness topics
  - Video freshness and recency
  - Channel authority/credibility
  - Historical performance if available
  - Title quality and engagement potential

This replaces random selection with ML-like scoring for better content curation.
"""
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


# ── Health Topic Scoring ───────────────────────────────────────────────────────

HEALTH_TOPIC_KEYWORDS = {
    "mental_health": {
        "keywords": ["anxiety", "depression", "stress", "mindfulness", "therapy", "counseling", "mental"],
        "score": 9.0
    },
    "fitness": {
        "keywords": ["exercise", "fitness", "workout", "strength", "cardio", "training"],
        "score": 8.0
    },
    "nutrition": {
        "keywords": ["nutrition", "diet", "food", "protein", "carbs", "macro", "meal"],
        "score": 8.5
    },
    "sleep": {
        "keywords": ["sleep", "insomnia", "rest", "circadian", "recovery"],
        "score": 9.0
    },
    "longevity": {
        "keywords": ["longevity", "aging", "lifespan", "healthy aging", "anti-aging"],
        "score": 8.5
    },
    "burnout": {
        "keywords": ["burnout", "fatigue", "exhaustion", "recovery", "rest"],
        "score": 9.5
    },
    "neuroscience": {
        "keywords": ["brain", "neuroscience", "cognitive", "neuroplasticity", "focus"],
        "score": 8.0
    },
    "immunity": {
        "keywords": ["immune", "immunity", "gut health", "inflammation", "infection"],
        "score": 8.0
    },
}

# Channel authority heuristics
AUTHORITATIVE_CHANNELS = [
    "huberman", "andrew huberman",  # Huberman Lab
    "science based medicine",
    "mike israetel",  # Renaissance Periodization
    "peter attia",  # Longevity
    "tim ferriss",
    "wim hof",  # Breathing/cold exposure
    "david goggins",
    "jocko willink",
    "rhonda patrick",
]

# Keywords that signal low-quality content
SPAM_KEYWORDS = [
    "scam", "fake", "misleading", "hoax", "conspiracy",
    "clickbait", "viral", "shocking", "unbelievable",
    "do this one trick", "doctors hate",
]


# ── Data Structures ───────────────────────────────────────────────────────────

@dataclass
class VideoScore:
    """Breakdown of video quality score."""
    video_id: str
    title: str
    base_score: float = 5.0  # 0-10 scale
    topic_relevance: float = 5.0  # 0-10
    channel_authority: float = 5.0  # 0-10
    title_quality: float = 5.0  # 0-10
    freshness: float = 5.0  # 0-10 (placeholder, would need upload date)
    historical_performance: float = 5.0  # 0-10 (if tracking)
    spam_penalty: float = 0.0  # negative adjustment
    final_score: float = 0.0

    def calculate_final(self) -> float:
        """Calculate weighted final score."""
        weights = {
            "topic_relevance": 0.30,
            "channel_authority": 0.20,
            "title_quality": 0.20,
            "freshness": 0.15,
            "historical_performance": 0.15,
        }
        components = [
            self.topic_relevance * weights["topic_relevance"],
            self.channel_authority * weights["channel_authority"],
            self.title_quality * weights["title_quality"],
            self.freshness * weights["freshness"],
            self.historical_performance * weights["historical_performance"],
        ]
        self.final_score = (sum(components) - self.spam_penalty) / sum(weights.values())
        return self.final_score


# ── Scoring Functions ─────────────────────────────────────────────────────────

def score_topic_relevance(title: str) -> float:
    """Score how relevant the video is to health/wellness topics. 0-10."""
    title_lower = title.lower()
    max_score = 0.0

    for topic, info in HEALTH_TOPIC_KEYWORDS.items():
        if any(kw in title_lower for kw in info["keywords"]):
            max_score = max(max_score, info["score"])

    return max_score


def score_channel_authority(title: str) -> float:
    """Estimate channel authority from title mentions. 0-10."""
    title_lower = title.lower()

    # Direct channel name matches
    if any(channel in title_lower for channel in AUTHORITATIVE_CHANNELS):
        return 9.0

    # Keywords associated with credible channels
    credibility_indicators = [
        ("phd", 8.0),
        ("md", 8.0),
        ("science", 7.5),
        ("research", 7.0),
        ("evidence", 7.0),
        ("study", 6.5),
    ]

    for indicator, score in credibility_indicators:
        if indicator in title_lower:
            return score

    return 5.0


def score_title_quality(title: str) -> float:
    """Score how compelling and clear the title is. 0-10."""
    score = 5.0

    # Positive factors
    if len(title) > 30 and len(title) < 100:  # Good length
        score += 1.0
    if title.count("|") > 0 or title.count("-") > 0:  # Structured formatting
        score += 0.5
    if any(word in title.lower() for word in ["how to", "why", "what", "guide"]):  # Educational hooks
        score += 1.0
    if any(word in title for word in ["™", "®", "©"]):  # Official/branded
        score += 0.5

    # Negative factors
    if title.count("!") > 2:  # Over-excited punctuation
        score -= 1.0
    if len(title.upper()) > len(title) * 0.7:  # Too much caps
        score -= 1.0

    return min(10.0, max(0.0, score))


def detect_spam(title: str) -> float:
    """Detect spam/misleading content. Returns penalty 0-5."""
    title_lower = title.lower()
    penalties = 0.0

    for spam_kw in SPAM_KEYWORDS:
        if spam_kw in title_lower:
            penalties += 1.0

    return min(5.0, penalties)


def score_freshness(title: str, days_ago: int = 0) -> float:
    """Score based on freshness. Ideally we'd have upload dates. 0-10."""
    # Without upload date, use year indicators in title
    current_year = datetime.now().year
    current_month = datetime.now().month

    score = 5.0

    # Check for year mentions
    if str(current_year) in title:
        score = 9.0
    elif str(current_year - 1) in title:
        score = 7.0
    elif str(current_year - 2) in title:
        score = 5.0
    else:
        score = 4.0

    # Boost for timely topics
    if current_month in range(1, 3) and ("new year" in title.lower() or "resolution" in title.lower()):
        score += 1.0
    elif current_month in range(5, 8) and ("summer" in title.lower() or "vacation" in title.lower()):
        score += 0.5

    return min(10.0, max(0.0, score))


# ── Ranking Functions ─────────────────────────────────────────────────────────

def score_video(video: Dict, historical_perf: Optional[float] = None) -> VideoScore:
    """Calculate comprehensive score for a video."""
    title = video.get("title", "")
    video_id = video.get("id", "")

    score = VideoScore(
        video_id=video_id,
        title=title,
        topic_relevance=score_topic_relevance(title),
        channel_authority=score_channel_authority(title),
        title_quality=score_title_quality(title),
        freshness=score_freshness(title),
        historical_performance=historical_perf or 5.0,
        spam_penalty=detect_spam(title),
    )

    score.calculate_final()
    return score


def rank_videos(videos: List[Dict], performance_history: Optional[Dict] = None) -> List[Tuple[Dict, float]]:
    """
    Rank videos by quality score.
    Returns list of (video, score) tuples sorted by score descending.
    """
    perf_history = performance_history or {}
    scores = []

    for video in videos:
        video_id = video.get("id", "")
        hist_perf = perf_history.get(video_id, {}).get("avg_engagement", 5.0)
        video_score = score_video(video, hist_perf)
        scores.append((video, video_score.final_score))

    # Sort by score descending
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def select_best_videos(videos: List[Dict], n: int = 5, min_score: float = 4.0) -> List[Dict]:
    """
    Select the top N videos by quality score, filtering out low-quality content.
    """
    ranked = rank_videos(videos)
    selected = []

    for video, score in ranked:
        if len(selected) >= n:
            break
        if score >= min_score:
            selected.append(video)

    return selected


# ── Performance Tracking ───────────────────────────────────────────────────────

class PerformanceHistory:
    """Track historical performance of videos for better ranking."""

    def __init__(self, history_file: Path = Path("video_performance.json")):
        self.history_file = history_file
        self.data = self._load()

    def _load(self) -> Dict:
        """Load performance history from disk."""
        if self.history_file.exists():
            return json.loads(self.history_file.read_text())
        return {}

    def _save(self):
        """Save performance history to disk."""
        with open(self.history_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def record(self, video_id: str, engagement: float, reach: int = 0):
        """Record engagement metrics for a video."""
        if video_id not in self.data:
            self.data[video_id] = {
                "engagements": [],
                "total_reach": 0,
                "posts_count": 0,
            }

        self.data[video_id]["engagements"].append(engagement)
        self.data[video_id]["total_reach"] += reach
        self.data[video_id]["posts_count"] += 1
        self._save()

    def get_avg_engagement(self, video_id: str) -> float:
        """Get average engagement for a video. 0-10."""
        if video_id not in self.data:
            return 5.0
        engagements = self.data[video_id].get("engagements", [5.0])
        return sum(engagements) / len(engagements) if engagements else 5.0

    def get_stats(self, video_id: str) -> Dict:
        """Get full statistics for a video."""
        if video_id not in self.data:
            return {"avg_engagement": 5.0, "total_reach": 0, "posts_count": 0}
        data = self.data[video_id]
        return {
            "avg_engagement": sum(data["engagements"]) / len(data["engagements"]) if data["engagements"] else 5.0,
            "total_reach": data["total_reach"],
            "posts_count": data["posts_count"],
        }
