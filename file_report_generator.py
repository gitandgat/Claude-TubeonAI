"""
File Report Generator — formats FileScanReport into JSON and email HTML
"""
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def format_bytes(n: int) -> str:
    """Convert byte count to human-readable string (B / KB / MB / GB / TB)."""
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def save_json_report(report_dict: dict, output_path: Path) -> Path:
    """Write JSON report to output_path. Returns path."""
    try:
        with open(output_path, "w") as f:
            json.dump(report_dict, f, indent=2)
        logger.info(f"Report saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to save report: {str(e)}")
        raise


def build_json_summary(report_dict: dict) -> dict:
    """
    Strip the full `files` list from the report dict and return a
    compact summary suitable for a daily digest (stats + top duplicates only).
    Returns: dict
    """
    summary = {
        "run_at": report_dict.get("run_at"),
        "scan_dirs": report_dict.get("scan_dirs", []),
        "total_files": report_dict.get("total_files", 0),
        "total_size_bytes": report_dict.get("total_size_bytes", 0),
        "by_category": report_dict.get("by_category", {}),
        "duplicate_groups": report_dict.get("duplicate_groups", []),
        "total_duplicate_wasted_bytes": report_dict.get(
            "total_duplicate_wasted_bytes", 0
        ),
        "pending_approval": True,
        "errors": report_dict.get("errors", []),
    }
    return summary
