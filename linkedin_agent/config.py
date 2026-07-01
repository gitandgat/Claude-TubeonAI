import os
from datetime import datetime

# Environment variables
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ZERNIO_API_KEY = os.getenv("ZERNIO_API_KEY")
ENCHARGE_API_KEY = os.getenv("ENCHARGE_API_KEY")

# LinkedIn API credentials (optional - for direct LinkedIn posting without Zernio limit)
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_USER_URN = os.getenv("LINKEDIN_USER_URN")  # format: urn:li:person:{user_id}

# AI Model Configuration
# "auto" (default): Ollama local (free) with Claude Haiku fallback.
# Force one with AI_PROVIDER: "ollama", "claude", or "groq".
AI_PROVIDER = os.getenv("AI_PROVIDER", "auto").lower()

# Groq configuration (free tier; key currently invalid — not in auto chain)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"

# Ollama configuration (free, local, M1 Pro GPU-accelerated)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Claude configuration (paid)
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

# Zernio configuration
ZERNIO_BASE_URL = "https://zernio.com/api/v1"
LINKEDIN_ACCOUNT_ID = "690940455f6fbb9ef8323070"

# Video cross-post targets — one rendered video → all four video surfaces.
# (FB included but expected to underperform: it's audience-starved, not a
# format problem — see analysis Jun 2026.)
VIDEO_PLATFORM_ACCOUNTS = {
    "tiktok": "690941425f6fbb9ef8323078",
    "instagram": "690940655f6fbb9ef8323072",
    "facebook": "6909409a5f6fbb9ef8323074",
    "youtube": "690940d35f6fbb9ef8323077",
}

# LinkedIn post configuration
LINKEDIN_SCHEDULE_TIME = "08:00"  # 8am ET
LINKEDIN_SCHEDULE_TZ = "America/New_York"
# Auto-posted as the first comment on EVERY post (zero daily work). This is the
# always-on capture path — the Fear Audit link lives in the first comment so the
# post body stays link-free (LinkedIn suppresses body links, not comment links).
LINKEDIN_FIRST_COMMENT = (
    "The free 3-minute Fear Audit names which fear — money, judgment, or identity "
    "— is running your decisions: https://fear-audit.vercel.app"
)
LINKEDIN_DAILY_LIMIT = 5

# ── Frequency experiment: 5/day vs 2/day ────────────────────────────────────
# Alternates posting volume by ISO week (even=5/day, odd=2/day). Disabled by
# default — the user wants 5/day always. Set LINKEDIN_FREQ_EXPERIMENT=1 in .env
# to re-enable the experiment if you want to compare volume arms again.
FREQUENCY_EXPERIMENT = os.getenv("LINKEDIN_FREQ_EXPERIMENT", "0") == "1"
FREQUENCY_ARMS = {"high": 5, "low": 2}


def current_daily_limit() -> int:
    """Effective posts/day. Alternates 5 (even ISO week) / 2 (odd) when the
    frequency experiment is on; otherwise the fixed LINKEDIN_DAILY_LIMIT."""
    if not FREQUENCY_EXPERIMENT:
        return LINKEDIN_DAILY_LIMIT
    import datetime
    even_week = datetime.date.today().isocalendar()[1] % 2 == 0
    return FREQUENCY_ARMS["high"] if even_week else FREQUENCY_ARMS["low"]


def current_frequency_arm() -> str:
    """'high' (5/day) or 'low' (2/day) for tagging posts so the learning loop
    can attribute reach to the active frequency arm."""
    if not FREQUENCY_EXPERIMENT:
        return "high"
    return "high" if datetime_isoweek_even() else "low"


def datetime_isoweek_even() -> bool:
    import datetime
    return datetime.date.today().isocalendar()[1] % 2 == 0

# ── Comment-to-DM lead capture (Sendpilot) ──────────────────────────────────
# OFF by default: Sendpilot comment automations are per-post with no "all posts"
# option and no API, so a daily "Comment FEAR" CTA would require wiring every
# post by hand. Instead the always-on capture path is LINKEDIN_FIRST_COMMENT
# (above), plus ONE pinned "Comment FEAR" post wired once in Sendpilot.
# Set LINKEDIN_COMMENT_DM=1 only if you commit to wiring each day's post.
COMMENT_DM_ENABLED = os.getenv("LINKEDIN_COMMENT_DM", "0") == "1"
COMMENT_DM_KEYWORD = "FEAR"
COMMENT_DM_CTAS = [
    "Comment FEAR and I'll send you the free 3-minute Fear Audit — it names which of the three fears is actually running your decisions.",
    "If you want the map: comment FEAR and I'll DM you the free 3-minute Fear Audit. It tells you which fear — money, judgment, or identity — is keeping you at the curb.",
    "Want to know which fear is driving? Comment FEAR below and I'll send you the free 3-minute audit that scores all three.",
]

# Publishing route:
#   "zernio" — posts go through Zernio so their analytics are tracked and the
#              learning loop / experiments can read results. Zernio caps this at
#              5/day per account (Zernio's product limit, NOT LinkedIn's).
#   "direct" — direct LinkedIn API: no Zernio cap. LinkedIn publishes no fixed
#              daily post number — only a 429 rate limit — so it is NOT
#              "unlimited", just higher. UNMEASURABLE though (write-only token;
#              Zernio doesn't see these) so the learning loop goes blind.
# Chosen: zernio (measurable continuous learning).
PUBLISH_VIA = os.getenv("LINKEDIN_PUBLISH_VIA", "zernio").lower()

# Reddit configuration
REDDIT_BASE_URL = "https://www.reddit.com"
TARGET_SUBREDDITS = [
    "IMGreddit",
    "MCCQE",
    "CanadianPhysicians",
    "medicalschool",
    "residency"
]
REDDIT_FETCH_LIMIT = 25
REDDIT_TIME_FILTER = "week"

# Keywords for filtering Reddit posts (IMG pain points)
REDDIT_FILTER_KEYWORDS = [
    "IMG", "MCCQE", "career", "pivot", "stuck", "Canada",
    "sunk cost", "medical license", "burnout", "struggling",
    "fellowship", "residency", "international", "transition"
]

# Infographic configuration
INFOGRAPHIC_WIDTH = 1080
INFOGRAPHIC_HEIGHT = 1080
INFOGRAPHIC_TEMPLATE_FILE = "linkedin_agent/data/infographic_template.html"

# Voice profile configuration
VOICE_PROFILE_FILE = "linkedin_agent/data/voice_profile.json"
VOICE_PROFILE_CACHE_DAYS = 7

# Performance tracking configuration
SCHEDULE_LOG_FILE = "linkedin_agent/data/schedule_log.jsonl"
RUN_LOG_FILE = "linkedin_agent/data/run_log.jsonl"
PERFORMANCE_FILE = "linkedin_agent/data/performance.json"
RESEARCH_FILE = "linkedin_agent/data/daily_research.json"

# Analytics + learning loop (LinkedIn-first)
# Zernio's default /analytics blends platforms AND freezes a post's stats ~1wk
# after publish. We snapshot platform-filtered analytics daily into our own
# time series so we can compare posts at matched ages.
ANALYTICS_PLATFORM = "linkedin"          # focus platform for the learning loop
# All platforms the nightly snapshot measures (video loop learns from tiktok/youtube)
ANALYTICS_PLATFORMS = ["linkedin", "tiktok", "youtube", "instagram", "facebook"]
ANALYTICS_HISTORY_FILE = "linkedin_agent/data/analytics_history.jsonl"
WINNING_PATTERNS_FILE = "linkedin_agent/data/winning_patterns.json"
# How many top posts feed the proven-hook library
TOP_HOOKS_COUNT = 8
# Impression thresholds that define a "hit" vs a "dud" on this account
HIT_IMPRESSIONS = 1000
DUD_IMPRESSIONS = 100

# Post configuration
# LinkedIn hard limit is 3,000 CHARACTERS. Proven winners are tight first-person
# stories (150-350 words) — forcing 250+ pushes toward padding/advice, the
# losing format. Allow short, punchy stories.
POST_MIN_LENGTH = 120
POST_MAX_LENGTH = 350
POST_MAX_CHARS = 2900

# AI slop banned phrases - STRICT anti-slop enforcement
BANNED_PHRASES = [
    "unleash", "dive into", "game-changer", "supercharge",
    "I'm excited to share", "groundbreaking", "revolutionary",
    "paradigm shift", "game-changing", "disrupt", "synergy",
    "transformative", "leverage", "synergistic", "empower",
    "unlock your potential", "next level", "cutting edge",
    "state-of-the-art", "innovative", "game changing",
    "take action today", "don't miss out", "limited time",
    "here's what I learned", "here's the thing",
    "spoiler alert", "let's be real", "at the end of the day",
    "at scale", "moving the needle", "best practices",
    "it goes without saying", "needless to say",
    "imagine if", "picture this", "think about it",
    "not gonna lie", "lowkey", "honestly", "literally"
]

# Notification configuration
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "false").lower() == "true"
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "totomakus@gmail.com")

# Directories
LINKEDIN_AGENT_DIR = "linkedin_agent"
DATA_DIR = f"{LINKEDIN_AGENT_DIR}/data"

def ensure_directories():
    """Ensure all required directories exist."""
    os.makedirs(DATA_DIR, exist_ok=True)

def get_timestamp():
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat() + "Z"
