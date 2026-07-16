"""
File Organizer — scans directories, classifies files, detects duplicates
"""
import os
import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_SCAN_DIRS = [
    "~/Desktop",
    "~/Downloads",
    "~/Documents",
    "~/Pictures",
    "~/Movies",
    "~/Music",
]

EXTENSION_CATEGORY = {
    # Documents
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".md": "Documents",
    ".rtf": "Documents",
    # Spreadsheets
    ".xlsx": "Finance",
    ".xls": "Finance",
    ".csv": "Finance",
    # Images
    ".jpg": "Media",
    ".jpeg": "Media",
    ".png": "Media",
    ".gif": "Media",
    ".svg": "Media",
    ".heic": "Media",
    ".webp": "Media",
    # Video
    ".mp4": "Media",
    ".mov": "Media",
    ".avi": "Media",
    ".mkv": "Media",
    ".flv": "Media",
    ".wmv": "Media",
    # Audio
    ".mp3": "Media",
    ".wav": "Media",
    ".m4a": "Media",
    ".flac": "Media",
    ".aac": "Media",
    # Code
    ".py": "Projects",
    ".js": "Projects",
    ".ts": "Projects",
    ".html": "Projects",
    ".css": "Projects",
    ".json": "Projects",
    ".sh": "Projects",
    ".yaml": "Projects",
    ".yml": "Projects",
    ".jsx": "Projects",
    ".tsx": "Projects",
    # Archives
    ".zip": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
    ".7z": "Archives",
    ".rar": "Archives",
    ".bz2": "Archives",
}

NAME_KEYWORD_SUBCATEGORY = {
    "invoice": "Finance",
    "receipt": "Finance",
    "tax": "Finance",
    "statement": "Finance",
    "payment": "Finance",
    "resume": "Work",
    "cv": "Work",
    "contract": "Work",
    "proposal": "Work",
    "report": "Work",
    "research": "Research",
    "paper": "Research",
    "study": "Research",
    "notes": "Personal",
    "journal": "Personal",
}

MAX_FILE_SIZE_FOR_HASH = 500 * 1024 * 1024  # 500 MB


@dataclass
class ScannedFile:
    path: str
    filename: str
    extension: str
    size_bytes: int
    modified_at: str
    category: str
    subcategory: str
    suggested_folder: str
    md5: Optional[str] = None
    duplicate_group: Optional[str] = None


@dataclass
class DuplicateGroup:
    group_key: str
    files: List[str] = field(default_factory=list)
    size_bytes: int = 0
    wasted_bytes: int = 0


@dataclass
class FileScanReport:
    run_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    scan_dirs: List[str] = field(default_factory=list)
    total_files: int = 0
    total_size_bytes: int = 0
    by_category: Dict[str, int] = field(default_factory=dict)
    duplicate_groups: List[Dict] = field(default_factory=list)
    total_duplicate_wasted_bytes: int = 0
    files: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    pending_approval: bool = True


class FileOrganizer:
    def __init__(
        self,
        scan_dirs: Optional[List[str]] = None,
        report_dir: Path = Path("reports"),
        skip_hidden: bool = True,
        max_depth: int = 5,
    ) -> None:
        self.scan_dirs = [
            Path(d).expanduser()
            for d in (scan_dirs or DEFAULT_SCAN_DIRS)
        ]
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.skip_hidden = skip_hidden
        self.max_depth = max_depth

    def _classify_file(self, path: Path) -> ScannedFile:
        """
        Determine category and subcategory for a single file.
        Priority order:
          1. Extension → EXTENSION_CATEGORY (sets top-level category)
          2. Filename keywords → NAME_KEYWORD_SUBCATEGORY (refines)
          3. Build suggested_folder as "{category}/{subcategory}"
        Returns: ScannedFile (md5=None, duplicate_group=None at this stage)
        """
        extension = path.suffix.lower()
        filename = path.name.lower()

        category = EXTENSION_CATEGORY.get(extension, "Personal")
        subcategory = category

        for keyword, sub_cat in NAME_KEYWORD_SUBCATEGORY.items():
            if keyword in filename:
                subcategory = sub_cat
                break

        suggested_folder = f"{category}/{subcategory}"

        try:
            stat = path.stat()
            size_bytes = stat.st_size
            modified_at = datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.utc
            ).isoformat()
        except Exception as e:
            logger.warning(f"Failed to stat {path}: {str(e)}")
            size_bytes = 0
            modified_at = datetime.now(timezone.utc).isoformat()

        return ScannedFile(
            path=str(path),
            filename=path.name,
            extension=extension,
            size_bytes=size_bytes,
            modified_at=modified_at,
            category=category,
            subcategory=subcategory,
            suggested_folder=suggested_folder,
        )

    def _compute_md5(self, path: Path) -> Optional[str]:
        """
        Stream-read file and return MD5 hex digest.
        Returns None for files > MAX_FILE_SIZE_FOR_HASH or on any read error.
        """
        try:
            if path.stat().st_size > MAX_FILE_SIZE_FOR_HASH:
                logger.debug(
                    f"Skipping hash for {path.name} (too large > 500MB)"
                )
                return None

            md5_hash = hashlib.md5()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    md5_hash.update(chunk)
            return md5_hash.hexdigest()

        except Exception as e:
            logger.warning(f"Failed to compute MD5 for {path}: {str(e)}")
            return None

    def _scan_directory(
        self, root: Path, current_depth: int = 0
    ) -> List[ScannedFile]:
        """
        Recursively walk root up to max_depth.
        Skips hidden files/dirs if skip_hidden=True.
        Returns list of ScannedFile (md5 not yet set).
        """
        files = []

        if current_depth > self.max_depth:
            return files

        if not root.exists():
            logger.warning(f"Directory does not exist: {root}")
            return files

        try:
            for entry in root.iterdir():
                if self.skip_hidden and entry.name.startswith("."):
                    continue

                if entry.is_file():
                    try:
                        scanned = self._classify_file(entry)
                        files.append(scanned)
                    except Exception as e:
                        logger.warning(
                            f"Failed to classify {entry}: {str(e)}"
                        )

                elif entry.is_dir():
                    try:
                        subfiles = self._scan_directory(
                            entry, current_depth + 1
                        )
                        files.extend(subfiles)
                    except Exception as e:
                        logger.warning(
                            f"Failed to scan directory {entry}: {str(e)}"
                        )

        except Exception as e:
            logger.error(f"Error scanning directory {root}: {str(e)}")

        return files

    def _detect_duplicates(
        self, files: List[ScannedFile]
    ) -> List[DuplicateGroup]:
        """
        Two-pass dedup:
          Pass 1: group by (filename, size_bytes) — fast pre-filter
          Pass 2: for each candidate group, compute MD5 and group by hash
        Sets duplicate_group on each ScannedFile in a duplicate set.
        Returns list of DuplicateGroup (only groups with 2+ members).
        """
        pass1_candidates = defaultdict(list)
        for f in files:
            key = (f.filename, f.size_bytes)
            pass1_candidates[key].append(f)

        hash_groups = defaultdict(list)
        for (filename, size_bytes), group in pass1_candidates.items():
            if len(group) < 2:
                continue

            for scanned in group:
                md5 = self._compute_md5(Path(scanned.path))
                scanned.md5 = md5
                if md5:
                    hash_groups[md5].append(scanned)

        duplicate_groups = []
        group_id_counter = 0
        for md5, scanned_list in hash_groups.items():
            if len(scanned_list) >= 2:
                group_id = md5
                for scanned in scanned_list:
                    scanned.duplicate_group = group_id

                wasted = (len(scanned_list) - 1) * scanned_list[0].size_bytes
                dup_group = DuplicateGroup(
                    group_key=md5,
                    files=[s.path for s in scanned_list],
                    size_bytes=scanned_list[0].size_bytes,
                    wasted_bytes=wasted,
                )
                duplicate_groups.append(dup_group)

                group_id_counter += 1

        return duplicate_groups

    def scan(self) -> FileScanReport:
        """
        Entry point: scan all dirs, classify, detect duplicates, build report.
        Does NOT move or delete anything.
        Returns: FileScanReport
        """
        logger.info(f"Scanning {len(self.scan_dirs)} directories...")
        report = FileScanReport(scan_dirs=[str(d) for d in self.scan_dirs])

        all_files = []
        for scan_dir in self.scan_dirs:
            logger.info(f"  Scanning {scan_dir}...")
            files = self._scan_directory(scan_dir)
            all_files.extend(files)

        logger.info(f"Found {len(all_files)} files. Detecting duplicates...")
        duplicate_groups = self._detect_duplicates(all_files)

        report.total_files = len(all_files)
        report.total_size_bytes = sum(f.size_bytes for f in all_files)
        report.duplicate_groups = [asdict(dg) for dg in duplicate_groups]
        report.total_duplicate_wasted_bytes = sum(
            dg.wasted_bytes for dg in duplicate_groups
        )

        by_category = defaultdict(int)
        for f in all_files:
            by_category[f.category] += 1
        report.by_category = dict(by_category)

        report.files = [asdict(f) for f in all_files]

        logger.info(
            f"Scan complete: {report.total_files} files, {len(duplicate_groups)} duplicate groups, {report.total_duplicate_wasted_bytes} bytes wasted"
        )

        return report

    def _save_report(self, report: FileScanReport) -> Path:
        """
        Write report as JSON to reports/file_organizer_YYYY-MM-DD.json.
        Returns: path to written file
        """
        now = datetime.now(timezone.utc).isoformat().split("T")[0]
        filename = f"file_organizer_{now}.json"
        output_path = self.report_dir / filename

        try:
            with open(output_path, "w") as f:
                json.dump(asdict(report), f, indent=2)
            logger.info(f"Report saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to save report: {str(e)}")
            report.errors.append(f"Failed to save report: {str(e)}")
            raise
