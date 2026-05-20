"""
Bot Monitoring & Alerting System
=================================
Monitors bot health, tracks issues, and sends alerts.

Features:
  - Real-time health metrics
  - Alert thresholds for failures
  - Performance trend analysis
  - Webhook notifications (optional)
  - Slack integration (optional)
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
from urllib.request import Request, urlopen
from urllib.error import URLError


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Represents a bot alert."""
    timestamp: str
    level: AlertLevel
    title: str
    message: str
    details: Optional[Dict] = None
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        d = asdict(self)
        d["level"] = self.level.value
        return d


class HealthMetrics:
    """Aggregated health metrics."""

    def __init__(self):
        self.total_posts: int = 0
        self.successful_posts: int = 0
        self.failed_posts: int = 0
        self.avg_post_duration: float = 0.0
        self.success_rate: float = 1.0
        self.last_post_time: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.error_count_24h: int = 0
        self.retry_count_24h: int = 0
        self.estimated_roi: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_posts": self.total_posts,
            "successful_posts": self.successful_posts,
            "failed_posts": self.failed_posts,
            "success_rate": f"{self.success_rate:.1%}",
            "avg_post_duration_seconds": f"{self.avg_post_duration:.1f}",
            "last_post_time": self.last_post_time.isoformat() if self.last_post_time else None,
            "error_count_24h": self.error_count_24h,
            "retry_count_24h": self.retry_count_24h,
            "last_error": self.last_error,
        }


class AlertManager:
    """Manages alerts and notifications."""

    def __init__(self, log_dir: Path = Path("logs"), webhook_url: Optional[str] = None):
        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)
        self.webhook_url = webhook_url
        self.alerts_file = self.log_dir / "alerts.jsonl"
        self.alert_history: List[Alert] = []
        self.logger = logging.getLogger(__name__)
        self._load_recent_alerts()

    def _load_recent_alerts(self, hours: int = 24):
        """Load recent alerts from file."""
        if not self.alerts_file.exists():
            return

        cutoff = datetime.utcnow().timestamp() - (hours * 3600)
        with open(self.alerts_file, "r") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    ts = datetime.fromisoformat(data["timestamp"]).timestamp()
                    if ts > cutoff:
                        alert = Alert(
                            timestamp=data["timestamp"],
                            level=AlertLevel(data["level"]),
                            title=data["title"],
                            message=data["message"],
                            details=data.get("details"),
                            metadata=data.get("metadata"),
                        )
                        self.alert_history.append(alert)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue

    def add_alert(self, level: AlertLevel, title: str, message: str,
                  details: Optional[Dict] = None, metadata: Optional[Dict] = None) -> Alert:
        """Create and log an alert."""
        alert = Alert(
            timestamp=datetime.utcnow().isoformat(),
            level=level,
            title=title,
            message=message,
            details=details,
            metadata=metadata,
        )

        # Log to file
        with open(self.alerts_file, "a") as f:
            f.write(json.dumps(alert.to_dict()) + "\n")

        # Log to logger
        log_fn = {
            AlertLevel.INFO: self.logger.info,
            AlertLevel.WARNING: self.logger.warning,
            AlertLevel.ERROR: self.logger.error,
            AlertLevel.CRITICAL: self.logger.critical,
        }
        log_fn[level](f"[{level.value.upper()}] {title}: {message}")

        # Send webhook notification if configured
        if self.webhook_url and level in (AlertLevel.ERROR, AlertLevel.CRITICAL):
            self._send_webhook(alert)

        self.alert_history.append(alert)
        return alert

    def _send_webhook(self, alert: Alert):
        """Send alert to webhook (Slack, Discord, etc.)."""
        try:
            payload = json.dumps(alert.to_dict()).encode("utf-8")
            request = Request(
                self.webhook_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urlopen(request, timeout=10)
        except (URLError, Exception) as e:
            self.logger.warning(f"Failed to send webhook: {e}")

    def get_recent_alerts(self, level: Optional[AlertLevel] = None, hours: int = 24) -> List[Alert]:
        """Get recent alerts, optionally filtered by level."""
        cutoff = datetime.utcnow().timestamp() - (hours * 3600)
        alerts = []

        for alert in self.alert_history:
            ts = datetime.fromisoformat(alert.timestamp).timestamp()
            if ts > cutoff:
                if level is None or alert.level == level:
                    alerts.append(alert)

        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)

    def get_error_rate(self, hours: int = 24) -> float:
        """Get error rate as percentage."""
        cutoff = datetime.utcnow().timestamp() - (hours * 3600)
        total = 0
        errors = 0

        for alert in self.alert_history:
            ts = datetime.fromisoformat(alert.timestamp).timestamp()
            if ts > cutoff:
                if alert.level in (AlertLevel.ERROR, AlertLevel.CRITICAL):
                    errors += 1
                total += 1

        return (errors / total * 100) if total > 0 else 0.0


class HealthChecker:
    """Checks bot health and triggers alerts."""

    def __init__(self, alert_manager: Optional[AlertManager] = None):
        self.alert_manager = alert_manager or AlertManager()
        self.logger = logging.getLogger(__name__)

    def check_health(self, metrics: HealthMetrics) -> Dict[str, Any]:
        """Perform comprehensive health check and return status."""
        status = "healthy"
        checks = {
            "success_rate": {"passed": True, "value": metrics.success_rate},
            "error_count": {"passed": True, "value": metrics.error_count_24h},
            "last_error": {"passed": True, "value": metrics.last_error},
        }

        # Check success rate
        if metrics.success_rate < 0.8:
            status = "degraded"
            checks["success_rate"]["passed"] = False
            self.alert_manager.add_alert(
                AlertLevel.WARNING,
                "Low success rate",
                f"Bot success rate is {metrics.success_rate:.1%}, expected >80%",
                details={"current": metrics.success_rate, "threshold": 0.8},
            )

        if metrics.success_rate < 0.5:
            status = "critical"
            checks["success_rate"]["passed"] = False
            self.alert_manager.add_alert(
                AlertLevel.CRITICAL,
                "Critical success rate",
                f"Bot success rate is {metrics.success_rate:.1%}, immediate action required",
                details={"current": metrics.success_rate, "threshold": 0.5},
            )

        # Check error count
        if metrics.error_count_24h > 10:
            status = "degraded"
            checks["error_count"]["passed"] = False
            self.alert_manager.add_alert(
                AlertLevel.WARNING,
                "High error count",
                f"{metrics.error_count_24h} errors in last 24 hours",
                details={"errors": metrics.error_count_24h},
            )

        if metrics.error_count_24h > 20:
            status = "critical"
            checks["error_count"]["passed"] = False
            self.alert_manager.add_alert(
                AlertLevel.CRITICAL,
                "Critical error count",
                f"{metrics.error_count_24h} errors in last 24 hours, system unstable",
                details={"errors": metrics.error_count_24h},
            )

        return {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
            "metrics": metrics.to_dict(),
        }

    def check_service_dependencies(self, api_keys: Dict[str, str]) -> Dict[str, bool]:
        """Verify all required API keys are configured."""
        checks = {}
        required_keys = ["zernio_key", "tubeonai_key", "openai_key", "anthropic_key"]

        for key in required_keys:
            exists = bool(api_keys.get(key))
            checks[key] = exists
            if not exists:
                self.alert_manager.add_alert(
                    AlertLevel.CRITICAL,
                    f"Missing API key: {key}",
                    f"The {key} is not configured. Bot cannot run without it.",
                    details={"missing_key": key},
                )

        return checks


# ── Report Generator ──────────────────────────────────────────────────────────

class HealthReport:
    """Generates health reports."""

    @staticmethod
    def generate_summary(metrics: HealthMetrics, alert_manager: AlertManager) -> str:
        """Generate a text summary report."""
        report = []
        report.append("=" * 60)
        report.append("BOT HEALTH REPORT")
        report.append("=" * 60)
        report.append("")

        report.append("METRICS")
        report.append("-" * 60)
        report.append(f"Success Rate: {metrics.success_rate:.1%}")
        report.append(f"Total Posts: {metrics.total_posts}")
        report.append(f"Successful: {metrics.successful_posts}")
        report.append(f"Failed: {metrics.failed_posts}")
        report.append(f"Avg Duration: {metrics.avg_post_duration:.1f}s")
        report.append(f"Errors (24h): {metrics.error_count_24h}")
        report.append(f"Retries (24h): {metrics.retry_count_24h}")
        report.append("")

        errors = alert_manager.get_recent_alerts(level=AlertLevel.ERROR, hours=24)
        if errors:
            report.append("RECENT ERRORS")
            report.append("-" * 60)
            for alert in errors[:5]:
                report.append(f"  • {alert.timestamp}: {alert.title}")
                report.append(f"    {alert.message}")
            report.append("")

        error_rate = alert_manager.get_error_rate(hours=24)
        report.append("HEALTH STATUS")
        report.append("-" * 60)
        if error_rate < 5:
            status = "✓ HEALTHY"
        elif error_rate < 15:
            status = "⚠ DEGRADED"
        else:
            status = "✗ CRITICAL"
        report.append(f"{status} (Error rate: {error_rate:.1f}%)")
        report.append("=" * 60)
        report.append("")

        return "\n".join(report)
