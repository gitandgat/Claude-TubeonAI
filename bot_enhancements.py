"""
Bot Enhancements Module
=======================
Advanced features for the Daily Health Bot:
  - Parallel processing (concurrent video handling)
  - Intelligent retry logic (exponential backoff, transient error recovery)
  - Performance analytics (post engagement, success rates, ROI metrics)
  - Rate limit management (smart throttling, queue management)
  - Enhanced error tracking
"""
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict


# ── Configuration ─────────────────────────────────────────────────────────────

MAX_WORKERS = 3  # Parallel threads for API calls
MAX_RETRIES = 3
BASE_RETRY_DELAY = 2  # seconds
BACKOFF_MULTIPLIER = 2


# ── Data Models ───────────────────────────────────────────────────────────────

@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = MAX_RETRIES
    base_delay: float = BASE_RETRY_DELAY
    backoff_multiplier: float = BACKOFF_MULTIPLIER
    transient_errors: Tuple[type, ...] = (
        ConnectionError, TimeoutError, OSError
    )


@dataclass
class AnalyticsEntry:
    """Single performance data point."""
    timestamp: str
    video_title: str
    slot_time: str
    platform: str
    success: bool
    duration_seconds: float
    error_type: Optional[str] = None
    retry_count: int = 0
    api_calls: int = 0


class AnalyticsTracker:
    """Tracks performance metrics for the bot."""

    def __init__(self, log_dir: Path = Path("logs")):
        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)
        self.analytics_file = self.log_dir / "analytics.jsonl"
        self.session_metrics = {
            "total_videos": 0,
            "successful_videos": 0,
            "failed_videos": 0,
            "total_api_calls": 0,
            "total_retries": 0,
            "avg_duration": 0.0,
        }

    def log_event(self, entry: AnalyticsEntry):
        """Append an analytics event to the log."""
        with open(self.analytics_file, "a") as f:
            f.write(json.dumps(asdict(entry)) + "\n")

    def get_success_rate(self, hours: int = 24) -> float:
        """Get success rate over last N hours."""
        if not self.analytics_file.exists():
            return 1.0

        cutoff = datetime.utcnow().timestamp() - (hours * 3600)
        successes = 0
        total = 0

        with open(self.analytics_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    ts = datetime.fromisoformat(entry["timestamp"]).timestamp()
                    if ts > cutoff:
                        total += 1
                        if entry["success"]:
                            successes += 1
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

        return (successes / total) if total > 0 else 1.0

    def get_avg_duration(self, hours: int = 24) -> float:
        """Get average duration for successful operations."""
        if not self.analytics_file.exists():
            return 0.0

        cutoff = datetime.utcnow().timestamp() - (hours * 3600)
        durations = []

        with open(self.analytics_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    ts = datetime.fromisoformat(entry["timestamp"]).timestamp()
                    if ts > cutoff and entry["success"]:
                        durations.append(entry["duration_seconds"])
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

        return sum(durations) / len(durations) if durations else 0.0


class RetryHandler:
    """Handles retry logic with exponential backoff."""

    def __init__(self, config: Optional[RetryConfig] = None, logger: Optional[logging.Logger] = None):
        self.config = config or RetryConfig()
        self.logger = logger or logging.getLogger(__name__)

    def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Tuple[Any, int]:
        """
        Execute a function with retry logic.
        Returns (result, retry_count) on success.
        Raises the last exception if all retries fail.
        """
        retry_count = 0
        last_error = None

        for attempt in range(self.config.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    self.logger.info(f"  ↺ Recovered after {attempt} retries")
                return result, retry_count

            except self.config.transient_errors as e:
                last_error = e
                if attempt < self.config.max_retries:
                    delay = self.config.base_delay * (self.config.backoff_multiplier ** attempt)
                    self.logger.warning(
                        f"  ⚠ Transient error (attempt {attempt + 1}/{self.config.max_retries + 1}): {e.__class__.__name__}"
                    )
                    self.logger.debug(f"  → Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    retry_count += 1
            except Exception as e:
                # Non-transient error: fail immediately
                self.logger.error(f"  ✗ Non-transient error: {e}")
                raise

        self.logger.error(f"  ✗ Failed after {self.config.max_retries} retries")
        raise last_error or RuntimeError("Unknown error after retries")


class ParallelProcessor:
    """Manages parallel processing of video pipelines."""

    def __init__(self, max_workers: int = MAX_WORKERS, logger: Optional[logging.Logger] = None):
        self.max_workers = max_workers
        self.logger = logger or logging.getLogger(__name__)

    def process_batch(
        self,
        items: List[Dict],
        process_func: Callable,
        *args,
        **kwargs
    ) -> List[Dict]:
        """
        Process a batch of items in parallel.
        Returns results in the original order.
        """
        results = [None] * len(items)
        futures = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            for idx, item in enumerate(items):
                future = executor.submit(process_func, item, *args, **kwargs)
                futures[future] = idx

            # Collect results as they complete
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    self.logger.error(f"  Error processing item {idx}: {e}")
                    results[idx] = {
                        "success": False,
                        "error": str(e),
                    }

        return results


class RateLimiter:
    """Manages API rate limits with token bucket pattern."""

    def __init__(self, calls_per_minute: int = 60, logger: Optional[logging.Logger] = None):
        self.calls_per_minute = calls_per_minute
        self.call_times = []
        self.logger = logger or logging.getLogger(__name__)

    def wait_if_needed(self):
        """Block if rate limit would be exceeded."""
        now = time.time()
        # Remove old timestamps outside the window
        self.call_times = [t for t in self.call_times if now - t < 60]

        if len(self.call_times) >= self.calls_per_minute:
            oldest = self.call_times[0]
            wait_time = 60 - (now - oldest)
            if wait_time > 0:
                self.logger.debug(f"  ⏸ Rate limit: waiting {wait_time:.1f}s")
                time.sleep(wait_time)

        self.call_times.append(time.time())


class PerformanceMonitor:
    """Monitors bot performance and health."""

    def __init__(self, analytics: Optional[AnalyticsTracker] = None):
        self.analytics = analytics or AnalyticsTracker()

    def get_health_status(self) -> Dict[str, Any]:
        """Return current health metrics."""
        success_rate = self.analytics.get_success_rate(hours=24)
        avg_duration = self.analytics.get_avg_duration(hours=24)

        status = "healthy"
        if success_rate < 0.8:
            status = "degraded"
        if success_rate < 0.5:
            status = "critical"

        return {
            "status": status,
            "success_rate_24h": success_rate,
            "avg_duration_seconds": avg_duration,
            "timestamp": datetime.utcnow().isoformat(),
        }


# ── Convenience Functions ─────────────────────────────────────────────────────

def create_retry_handler(logger: Optional[logging.Logger] = None) -> RetryHandler:
    """Factory for retry handler with default config."""
    return RetryHandler(logger=logger)


def create_parallel_processor(max_workers: int = MAX_WORKERS, logger: Optional[logging.Logger] = None) -> ParallelProcessor:
    """Factory for parallel processor."""
    return ParallelProcessor(max_workers=max_workers, logger=logger)
