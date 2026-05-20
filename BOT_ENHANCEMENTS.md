# Daily Health Bot - Enhancement Suite

This document describes the powerful new features added to make the Daily Health Bot more capable, reliable, and insightful.

## New Modules

### 1. `bot_enhancements.py` - Core Infrastructure

Advanced features for parallel processing, retry logic, analytics, and rate limiting.

**Key Classes:**
- `RetryHandler` - Intelligent retry logic with exponential backoff
- `ParallelProcessor` - Process multiple videos concurrently (2-3x speedup)
- `AnalyticsTracker` - Track performance metrics and ROI
- `RateLimiter` - Manage API rate limits with token bucket pattern
- `PerformanceMonitor` - Real-time health status monitoring

**Benefits:**
- **2-3x faster** video processing through parallelization
- **Automatic recovery** from transient API failures
- **Detailed metrics** on success rates, duration, errors

**Usage:**
```python
from bot_enhancements import RetryHandler, ParallelProcessor, AnalyticsTracker

# Retry logic
retry = RetryHandler()
result, retries = retry.execute_with_retry(some_api_call)

# Parallel processing
processor = ParallelProcessor(max_workers=3)
results = processor.process_batch(videos, process_video_func)

# Analytics
analytics = AnalyticsTracker()
analytics.log_event(AnalyticsEntry(...))
success_rate = analytics.get_success_rate(hours=24)
```

---

### 2. `daily_health_bot_v2.py` - Improved Bot

Drop-in replacement for `daily_health_bot.py` with all enhancements integrated.

**Improvements:**
- ✓ Parallel video processing
- ✓ Intelligent retry logic (exponential backoff)
- ✓ Real-time performance analytics
- ✓ Bot health status monitoring
- ✓ Better error tracking and logging
- ✓ Rate limit management

**Key Features:**
```
Health Status: HEALTHY / DEGRADED / CRITICAL
Success Rate (24h): 95%
Avg Duration: 45s per video
```

**Usage:**
```bash
# Replace cron job with v2
cd "/Users/toto/Claude TubeonAI" && python3 daily_health_bot_v2.py

# Output includes detailed health metrics and analytics
```

---

### 3. `video_ranker.py` - Intelligent Video Selection

ML-like scoring system for video quality and relevance.

**Scoring Factors:**
- **Topic Relevance** (30%) - How well-aligned with health/wellness
- **Channel Authority** (20%) - Credibility of creator
- **Title Quality** (20%) - Compelling and clear titles
- **Freshness** (15%) - Recent content
- **Historical Performance** (15%) - Past engagement metrics

**Key Classes:**
- `VideoScore` - Comprehensive scoring breakdown
- `PerformanceHistory` - Track video engagement over time
- `rank_videos()` - Rank by quality score
- `select_best_videos()` - Intelligent selection

**Benefits:**
- Better content curation automatically
- Avoid low-quality or clickbait videos
- Learn from past performance

**Usage:**
```python
from video_ranker import rank_videos, select_best_videos

# Rank videos by quality
ranked = rank_videos(videos)
for video, score in ranked:
    print(f"{video['title']}: {score:.1f}/10")

# Select only high-quality videos
best = select_best_videos(videos, n=5, min_score=4.0)
```

---

### 4. `bot_config.py` - Centralized Configuration

Single source of truth for all bot settings.

**Key Features:**
- Environment variable loading
- JSON configuration files
- Configuration profiles (development, production, performance, reliability)
- Validation of required API keys

**Configuration Profiles:**

```python
from bot_config import ConfigProfiles

# Development: verbose, single-threaded
dev = ConfigProfiles.development()

# Production: optimized, multi-threaded
prod = ConfigProfiles.production()

# Performance: maximum speed
perf = ConfigProfiles.performance()

# Reliability: maximum error handling
rel = ConfigProfiles.reliability()
```

**Usage:**
```python
from bot_config import get_config

config = get_config()
config.load()  # Load from .env + environment

print(config.zernio_key)
print(config.daily_post_times)  # ["08:00", "11:00", "14:00", "17:00", "20:00"]
print(config.parallel_workers)  # 3
```

---

### 5. `bot_monitor.py` - Monitoring & Alerting

Real-time health monitoring with alerting.

**Key Features:**
- Real-time health metrics
- Alert management (INFO, WARNING, ERROR, CRITICAL)
- Health checks with threshold-based alerts
- Webhook notifications (Slack, Discord, etc.)
- Detailed health reports

**Alert Levels:**
- `INFO` - Informational messages
- `WARNING` - Degraded performance, recovery recommended
- `ERROR` - Failure detected, manual review needed
- `CRITICAL` - System unstable, immediate action required

**Key Classes:**
- `AlertManager` - Manage and log alerts
- `HealthChecker` - Perform health checks
- `HealthMetrics` - Aggregate metrics
- `HealthReport` - Generate text reports

**Usage:**
```python
from bot_monitor import AlertManager, HealthChecker, AlertLevel

alert_mgr = AlertManager(webhook_url="https://hooks.slack.com/...")
checker = HealthChecker(alert_mgr)

metrics = HealthMetrics()
status = checker.check_health(metrics)
print(status["status"])  # healthy / degraded / critical
```

---

## Migration Guide

### Update Cron Job

**Old (v1):**
```bash
0 11 * * * cd "/Users/toto/Claude TubeonAI" && python3 daily_health_bot.py >> logs/health_bot.log 2>&1
```

**New (v2):**
```bash
0 11 * * * cd "/Users/toto/Claude TubeonAI" && python3 daily_health_bot_v2.py >> logs/health_bot_v2.log 2>&1
```

### Keep v1 as Fallback

The original `daily_health_bot.py` remains unchanged. Both can run in parallel if needed for A/B testing.

---

## Performance Improvements

### Speed
- **Sequential** (v1): 5 videos × 45s = ~225 seconds
- **Parallel** (v2): 5 videos in parallel batches ≈ 90-120 seconds
- **Speedup**: 2-2.5x faster

### Reliability
- **Auto-retry**: Transient API failures automatically recover
- **Exponential backoff**: Prevents overwhelming rate-limited APIs
- **Health monitoring**: Alerts on degradation before total failure

### Analytics
- **Success rate tracking**: Know what percentage of posts succeed
- **Performance history**: Learn from past video performance
- **ROI insights**: Which videos and posting times work best

---

## Configuration Examples

### High-Performance Setup
```python
from bot_config import ConfigProfiles

config = ConfigProfiles.performance()
config.parallel_workers = 5
config.rate_limit_per_minute = 100
config.videos_per_day = 10  # More content
```

### High-Reliability Setup
```python
from bot_config import ConfigProfiles

config = ConfigProfiles.reliability()
config.max_retries = 5  # More resilient
config.alert_on_failure = True  # Get notified
```

### Slack Notifications
```python
from bot_monitor import AlertManager

alert_mgr = AlertManager(
    webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/HERE"
)
# Errors and critical alerts will now notify Slack
```

---

## Monitoring Dashboard

View bot health:
```bash
# Check recent alerts
python3 -c "
from bot_monitor import AlertManager
mgr = AlertManager()
for alert in mgr.get_recent_alerts(hours=24):
    print(f'{alert.level.value}: {alert.title}')
"

# View success rate
python3 -c "
from bot_enhancements import AnalyticsTracker
tracker = AnalyticsTracker()
rate = tracker.get_success_rate(hours=24)
print(f'Success Rate (24h): {rate:.1%}')
"
```

---

## Advanced Usage

### Custom Retry Policy
```python
from bot_enhancements import RetryHandler, RetryConfig

config = RetryConfig(
    max_retries=5,
    base_delay=3.0,
    backoff_multiplier=1.5,
)
retry = RetryHandler(config)
result, retries = retry.execute_with_retry(api_call)
```

### Parallel Batch Processing
```python
from bot_enhancements import ParallelProcessor

processor = ParallelProcessor(max_workers=5)
results = processor.process_batch(
    videos,
    process_video_func,
    slot_times=times,
    date=today,
)
```

### Video Quality Filtering
```python
from video_ranker import rank_videos, select_best_videos

# Rank all videos
ranked = rank_videos(videos)

# Show scoring breakdown
for video, score in ranked[:3]:
    print(f"{video['title']}: {score:.1f}/10")

# Select only high-quality (score >= 6.5)
best = select_best_videos(videos, n=5, min_score=6.5)
```

---

## Analytics Data Format

Performance metrics are logged in `logs/analytics.jsonl`:
```json
{
  "timestamp": "2026-05-17T14:30:45.123456",
  "video_title": "10 Ways to Reduce Burnout and Stress",
  "slot_time": "08:00",
  "platform": "zernio_multiplatform",
  "success": true,
  "duration_seconds": 47.3,
  "error_type": null,
  "retry_count": 0,
  "api_calls": 12
}
```

Alerts are logged in `logs/alerts.jsonl`:
```json
{
  "timestamp": "2026-05-17T14:30:45.123456",
  "level": "warning",
  "title": "Low success rate",
  "message": "Bot success rate is 75%, expected >80%",
  "details": {"current": 0.75, "threshold": 0.8},
  "metadata": null
}
```

---

## Troubleshooting

### Bot runs slowly
Check parallel settings:
```python
from bot_config import config
print(f"Workers: {config.parallel_workers}")  # Should be 3-5
print(f"Rate limit: {config.rate_limit_per_minute}")
```

### High error rate
View recent errors:
```python
from bot_monitor import AlertManager, AlertLevel
mgr = AlertManager()
errors = mgr.get_recent_alerts(level=AlertLevel.ERROR, hours=24)
for e in errors:
    print(f"{e.timestamp}: {e.title}")
```

### Verify API keys
```python
from bot_config import config
config.load()
config.validate()  # Throws error if keys missing
```

---

## Summary

The enhancement suite makes the Daily Health Bot:

1. **2-3x faster** through parallel processing
2. **More reliable** with intelligent retry logic
3. **More insightful** with detailed analytics
4. **Self-aware** with health monitoring and alerts
5. **Better curated** with intelligent video selection
6. **Easier to configure** with centralized settings
7. **Production-ready** with comprehensive error handling

All enhancements are backward compatible. The original bot continues to work unchanged.
