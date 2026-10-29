"""
File Organizer Agent — daily runner CLI
Usage:
  python -m agents.file_organizer_agent                         # scan default dirs
  python -m agents.file_organizer_agent --dirs ~/Desktop ~/Downloads
  python -m agents.file_organizer_agent --no-email              # report only
  python -m agents.file_organizer_agent --prune-duplicates      # interactive delete
"""
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _fmt_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def _pick_keeper(paths: List[str]) -> str:
    """
    Keep the copy that is NOT in Downloads (preferred permanent location).
    If tied, keep the oldest (earliest mtime = more likely the original).
    """
    def score(p: str) -> tuple:
        in_downloads = "downloads" in p.lower()
        mtime = Path(p).stat().st_mtime if Path(p).exists() else float("inf")
        return (int(in_downloads), mtime)

    return min(paths, key=score)


def prune_duplicates(groups: List[Dict]) -> Dict:
    """
    Interactively walk duplicate groups, show keep/delete choices, and delete on approval.
    Returns a summary dict.
    """
    if not groups:
        print("No duplicate files found.")
        return {"groups_shown": 0, "groups_deleted": 0, "files_deleted": 0, "bytes_freed": 0}

    total = len(groups)
    deleted_files = 0
    bytes_freed = 0
    groups_deleted = 0

    print(f"\nFound {total} duplicate group(s). Press Enter or 'n' to skip, 'y' to delete, 'a' to delete all remaining, 'q' to quit.\n")

    delete_all = False

    for i, group in enumerate(groups, 1):
        paths = group["files"]
        size = group["size_bytes"]
        wasted = group["wasted_bytes"]
        keeper = _pick_keeper(paths)
        to_delete = [p for p in paths if p != keeper]

        print(f"--- Group {i}/{total}  ({len(paths)} copies · {_fmt_size(wasted)} wasted) ---")
        print(f"  KEEP   → {keeper}")
        for p in to_delete:
            print(f"  DELETE → {p}")

        if delete_all:
            answer = "y"
        else:
            try:
                answer = input("  Delete duplicate(s)? [y/N/a=all/q=quit]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nAborted.")
                break

        if answer == "q":
            print("Quit — no further deletions.")
            break
        elif answer == "a":
            delete_all = True
            answer = "y"

        if answer == "y":
            for p in to_delete:
                try:
                    os.remove(p)
                    print(f"  Deleted: {p}")
                    deleted_files += 1
                    bytes_freed += size
                except Exception as e:
                    print(f"  ERROR deleting {p}: {e}")
            groups_deleted += 1
        else:
            print("  Skipped.")

        print()

    print(f"Done. {deleted_files} file(s) deleted, {_fmt_size(bytes_freed)} freed.")
    return {
        "groups_shown": total,
        "groups_deleted": groups_deleted,
        "files_deleted": deleted_files,
        "bytes_freed": bytes_freed,
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="File Organizer Agent")
    parser.add_argument(
        "--dirs",
        nargs="+",
        default=None,
        help="Directories to scan (default: ~/Desktop ~/Downloads ~/Documents ~/Pictures ~/Movies ~/Music)",
    )
    parser.add_argument(
        "--no-email",
        action="store_true",
        help="Generate report only, do not send email",
    )
    parser.add_argument(
        "--prune-duplicates",
        action="store_true",
        help="After scanning, interactively prompt to delete duplicate files",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    try:
        from file_organizer import FileOrganizer
        from file_report_generator import build_json_summary
        from report_mailer import ReportMailer

        logger.info("Starting File Organizer Agent...")

        organizer = FileOrganizer(scan_dirs=args.dirs)
        report = organizer.scan()
        saved_path = organizer._save_report(report)
        logger.info(f"Report saved to {saved_path}")

        if getattr(args, "prune_duplicates", False):
            prune_duplicates(report.duplicate_groups)

        if not args.no_email:
            logger.info("Sending digest email...")
            summary = build_json_summary(report.__dict__)
            mailer = ReportMailer()
            success = mailer.send_file_organizer_digest(summary)
            if not success:
                logger.warning("Failed to send email, but report was saved")

        logger.info("File Organizer Agent completed successfully")
        return 0

    except Exception as e:
        logger.error(f"File Organizer Agent failed: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = build_arg_parser()
    args = parser.parse_args()
    sys.exit(run(args))
