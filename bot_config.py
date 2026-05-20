"""
Bot Configuration Manager
=========================
Centralized configuration for the Daily Health Bot.
Load from .env, environment variables, or override via config file.

Usage:
    from bot_config import config
    config.load()
    print(config.zernio_key)
    print(config.daily_post_times)
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class BotConfig:
    """Centralized configuration for the bot."""

    # ── API Keys ──────────────────────────────────────────────────────────────
    zernio_key: str = ""
    tubeonai_key: str = ""
    openai_key: str = ""
    anthropic_key: str = ""

    # ── Platform IDs ──────────────────────────────────────────────────────────
    linkedin_id: str = "690940455f6fbb9ef8323070"
    instagram_id: str = "690940655f6fbb9ef8323072"
    facebook_id: str = "6909409a5f6fbb9ef8323074"
    tiktok_id: str = "690941425f6fbb9ef8323078"

    # ── Daily posting schedule (ET) ───────────────────────────────────────────
    daily_post_times: List[str] = field(default_factory=lambda: [
        "08:00", "11:00", "14:00", "17:00", "20:00"
    ])
    videos_per_day: int = 5
    timezone: str = "America/New_York"

    # ── Processing settings ───────────────────────────────────────────────────
    parallel_workers: int = 3
    max_retries: int = 3
    retry_base_delay: float = 2.0
    rate_limit_per_minute: int = 60
    min_video_quality_score: float = 4.0

    # ── Video finder settings ─────────────────────────────────────────────────
    search_queries_per_run: int = 2
    videos_per_query: int = 15
    fallback_search: str = "health wellness 2026"

    # ── Image generation ──────────────────────────────────────────────────────
    image_model: str = "dall-e-3"
    image_size: str = "1024x1024"
    image_quality: str = "standard"

    # ── Claude model settings ─────────────────────────────────────────────────
    claude_model: str = "claude-haiku-4-5-20251001"
    claude_max_tokens: int = 500

    # ── Logging and monitoring ────────────────────────────────────────────────
    log_dir: str = "logs"
    analytics_enabled: bool = True
    health_checks_enabled: bool = True
    alert_on_failure: bool = True

    # ── Feature flags ─────────────────────────────────────────────────────────
    enable_parallel_processing: bool = True
    enable_video_ranking: bool = True
    enable_analytics: bool = True
    use_v2_bot: bool = True  # Use improved bot version

    def load(self, config_file: Optional[str] = None) -> None:
        """Load configuration from environment variables or JSON file."""
        # Load from .env first
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        # Load from environment variables
        self.zernio_key = os.getenv("ZERNIO_API_KEY", self.zernio_key)
        self.tubeonai_key = os.getenv("TUBEONAI_API_KEY", self.tubeonai_key)
        self.openai_key = os.getenv("OPENAI_API_KEY", self.openai_key)
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", self.anthropic_key)

        # Load from config file if provided
        if config_file and Path(config_file).exists():
            with open(config_file) as f:
                overrides = json.load(f)
            for key, value in overrides.items():
                if hasattr(self, key):
                    setattr(self, key, value)

    def validate(self) -> bool:
        """Validate that required API keys are configured."""
        required = {
            "zernio_key": "ZERNIO_API_KEY",
            "tubeonai_key": "TUBEONAI_API_KEY",
            "openai_key": "OPENAI_API_KEY",
            "anthropic_key": "ANTHROPIC_API_KEY",
        }

        missing = [key for key, env_var in required.items() if not getattr(self, key)]
        if missing:
            raise ValueError(f"Missing required API keys: {', '.join(missing)}")
        return True

    def get_platform_ids(self) -> Dict[str, str]:
        """Get all platform IDs as a dict."""
        return {
            "linkedin": self.linkedin_id,
            "instagram": self.instagram_id,
            "facebook": self.facebook_id,
            "tiktok": self.tiktok_id,
        }

    def to_dict(self) -> Dict:
        """Convert config to dictionary (excluding sensitive keys)."""
        d = self.__dict__.copy()
        # Redact API keys
        for key in ["zernio_key", "tubeonai_key", "openai_key", "anthropic_key"]:
            if key in d:
                d[key] = "***" if d[key] else ""
        return d

    def save(self, filename: str = "bot_config.json") -> None:
        """Save current config to JSON file."""
        d = self.__dict__.copy()
        # Don't save API keys to file for security
        for key in ["zernio_key", "tubeonai_key", "openai_key", "anthropic_key"]:
            d.pop(key, None)
        with open(filename, "w") as f:
            json.dump(d, f, indent=2)


# Global config instance
config = BotConfig()


# ── Convenience Functions ─────────────────────────────────────────────────────

def get_config(config_file: Optional[str] = None) -> BotConfig:
    """Get and load global config."""
    config.load(config_file)
    return config


def validate_config() -> bool:
    """Validate global config."""
    return config.validate()


# ── Profile Presets ──────────────────────────────────────────────────────────

class ConfigProfiles:
    """Pre-configured profiles for different use cases."""

    @staticmethod
    def development() -> BotConfig:
        """Development profile: slower, more verbose, all features."""
        cfg = BotConfig()
        cfg.parallel_workers = 1
        cfg.enable_parallel_processing = False
        cfg.enable_video_ranking = False
        cfg.use_v2_bot = False
        cfg.analytics_enabled = True
        cfg.health_checks_enabled = False
        return cfg

    @staticmethod
    def production() -> BotConfig:
        """Production profile: fast, reliable, optimized."""
        cfg = BotConfig()
        cfg.parallel_workers = 3
        cfg.enable_parallel_processing = True
        cfg.enable_video_ranking = True
        cfg.use_v2_bot = True
        cfg.analytics_enabled = True
        cfg.health_checks_enabled = True
        cfg.alert_on_failure = True
        return cfg

    @staticmethod
    def performance() -> BotConfig:
        """Performance profile: maximum speed."""
        cfg = ConfigProfiles.production()
        cfg.parallel_workers = 5
        cfg.rate_limit_per_minute = 100
        return cfg

    @staticmethod
    def reliability() -> BotConfig:
        """Reliability profile: maximum retry and error handling."""
        cfg = ConfigProfiles.production()
        cfg.max_retries = 5
        cfg.retry_base_delay = 3.0
        cfg.health_checks_enabled = True
        cfg.alert_on_failure = True
        return cfg
