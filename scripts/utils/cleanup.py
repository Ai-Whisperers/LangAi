#!/usr/bin/env python
"""
Repository Cleanup Utility.

Consolidated tool for cleaning up the repository. Combines functionality from:
- analyze_obsolete_files.py
- analyze_root_cleanup.py
- clean_root_directory.py
- find_obsolete_docs.py
- move_obsolete_docs.py
- quick_cleanup_scan.py

Usage:
    python -m scripts.utils.cleanup scan          # Quick scan for cleanup items
    python -m scripts.utils.cleanup analyze       # Full analysis report
    python -m scripts.utils.cleanup clean         # Clean (dry run)
    python -m scripts.utils.cleanup clean --execute  # Actually clean
"""

import argparse
import hashlib
import os
import shutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set

# ============================================================================
# CONFIGURATION
# ============================================================================

# Directories to skip during scanning
SKIP_DIRS: Set[str] = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".git",
    "venv",
    ".venv",
    "node_modules",
    "htmlcov",
    "External repos",
}

# Temporary file patterns
TEMP_PATTERNS = ["*.tmp", "*.temp", "*~", "*.swp", "*.swo", "*.pyc", "*.pyo", "*.log"]

# Backup file patterns
BACKUP_PATTERNS = ["*.bak", "*.backup", "*.old", "*.orig", "*-old", "*_old"]

# Files that should be in root
ROOT_ESSENTIAL_FILES = {
    "README.md",
    "INSTALLATION.md",
    "QUICK_START.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "LICENSE",
    "LICENSE.md",
    ".gitignore",
    ".gitattributes",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "poetry.lock",
    "Pipfile",
    "Pipfile.lock",
    "env.example",
    ".env.example",
}

# Report files to archive
REPORT_FILE_PATTERNS = [
    "*_report.txt",
    "*_log.txt",
    "*_analysis.txt",
    "obsolete_*.txt",
    "quick_cleanup_*.txt",
    "import_validation_*.txt",
]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def format_size(size: int) -> str:
    """Format file size for display."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}TB"


def hash_file(filepath: Path) -> str:
    """Calculate MD5 hash of a file."""
    try:
        hasher = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def should_skip_dir(dirname: str) -> bool:
    """Check if directory should be skipped."""
    return dirname in SKIP_DIRS or dirname.startswith(".")


# ============================================================================
# SCANNER CLASS
# ============================================================================


class RepositoryScanner:
    """Scan repository for cleanup items."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results: Dict[str, List[Any]] = {
            "temp_files": [],
            "backup_files": [],
            "pycache_dirs": [],
            "empty_dirs": [],
            "large_files": [],
            "report_files": [],
            "duplicate_files": defaultdict(list),
            "obsolete_docs": [],
        }

    def scan_all(self, quick: bool = False) -> Dict[str, List[Any]]:
        """Run all scans."""
        print("[*] Scanning repository...")

        self._scan_temp_and_backup_files()
        self._scan_cache_dirs()
        self._scan_empty_dirs()
        self._scan_large_files()
        self._scan_root_reports()

        if not quick:
            self._scan_duplicates()
            self._scan_obsolete_docs()

        return self.results

    def _scan_temp_and_backup_files(self):
        """Find temporary and backup files."""
        print("  [*] Scanning for temp/backup files...")

        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not should_skip_dir(d)]

            for filename in files:
                filepath = Path(root) / filename

                for pattern in TEMP_PATTERNS:
                    if filepath.match(pattern):
                        self.results["temp_files"].append(filepath)
                        break

                for pattern in BACKUP_PATTERNS:
                    if filepath.match(pattern):
                        self.results["backup_files"].append(filepath)
                        break

    def _scan_cache_dirs(self):
        """Find __pycache__ directories."""
        print("  [*] Scanning for cache directories...")

        for root, dirs, _ in os.walk(self.project_root):
            if "__pycache__" in dirs:
                self.results["pycache_dirs"].append(Path(root) / "__pycache__")
            if ".pytest_cache" in dirs:
                self.results["pycache_dirs"].append(Path(root) / ".pytest_cache")

            dirs[:] = [d for d in dirs if not should_skip_dir(d)]

    def _scan_empty_dirs(self):
        """Find empty directories."""
        print("  [*] Scanning for empty directories...")

        for root, dirs, _ in os.walk(self.project_root, topdown=False):
            dirs[:] = [d for d in dirs if not should_skip_dir(d)]

            for dirname in dirs:
                dirpath = Path(root) / dirname
                try:
                    contents = list(dirpath.iterdir())
                    if not contents:
                        self.results["empty_dirs"].append(dirpath)
                    elif len(contents) == 1 and contents[0].name == "__init__.py":
                        if contents[0].stat().st_size == 0:
                            self.results["empty_dirs"].append(dirpath)
                except (PermissionError, OSError):
                    continue

    def _scan_large_files(self, threshold_mb: float = 1.0):
        """Find large files."""
        print("  [*] Scanning for large files...")
        threshold = int(threshold_mb * 1024 * 1024)

        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not should_skip_dir(d)]

            for filename in files:
                filepath = Path(root) / filename
                try:
                    size = filepath.stat().st_size
                    if size > threshold:
                        self.results["large_files"].append((filepath, size))
                except (PermissionError, OSError):
                    continue

    def _scan_root_reports(self):
        """Find report files in root that should be archived."""
        print("  [*] Scanning root for report files...")

        for item in self.project_root.iterdir():
            if item.is_file():
                for pattern in REPORT_FILE_PATTERNS:
                    if item.match(pattern):
                        self.results["report_files"].append(item)
                        break

    def _scan_duplicates(self):
        """Find duplicate files by content hash."""
        print("  [*] Scanning for duplicate files...")

        file_hashes: Dict[str, List[Path]] = defaultdict(list)

        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not should_skip_dir(d)]

            for filename in files:
                filepath = Path(root) / filename

                try:
                    # Skip large files and binaries
                    if filepath.stat().st_size > 10 * 1024 * 1024:
                        continue
                    if filepath.suffix in [".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".exe"]:
                        continue

                    file_hash = hash_file(filepath)
                    if file_hash:
                        file_hashes[file_hash].append(filepath)
                except (PermissionError, OSError):
                    continue

        # Keep only duplicates
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                self.results["duplicate_files"][file_hash] = files

    def _scan_obsolete_docs(self):
        """Find potentially obsolete markdown files."""
        print("  [*] Scanning for obsolete documentation...")

        doc_counts: Dict[str, List[Path]] = defaultdict(list)

        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not should_skip_dir(d)]

            for filename in files:
                if not filename.lower().endswith(".md"):
                    continue

                filepath = Path(root) / filename

                # Track multiple copies of same doc type
                doc_type = filename.lower()
                if doc_type in ["readme.md", "changelog.md", "contributing.md"]:
                    doc_counts[doc_type].append(filepath)

                # Flag planning/status docs
                keywords = ["planning", "roadmap", "todo", "status", "progress", "phase"]
                if any(kw in filename.lower() for kw in keywords):
                    self.results["obsolete_docs"].append(filepath)

        # Add duplicate docs
        for doc_type, files in doc_counts.items():
            if len(files) > 1:
                self.results["obsolete_docs"].extend(files[1:])  # Keep first, mark rest


# ============================================================================
# CLEANER CLASS
# ============================================================================


class RepositoryCleaner:
    """Clean up repository based on scan results."""

    def __init__(self, project_root: Path, dry_run: bool = True):
        self.project_root = project_root
        self.dry_run = dry_run
        self.stats = {"deleted": 0, "moved": 0, "skipped": 0, "errors": 0}

    def clean_temp_files(self, files: List[Path]):
        """Delete temporary files."""
        print("\n[*] Cleaning temporary files...")
        self._delete_files(files)

    def clean_pycache(self, dirs: List[Path]):
        """Delete __pycache__ directories."""
        print("\n[*] Cleaning cache directories...")
        self._delete_dirs(dirs)

    def clean_empty_dirs(self, dirs: List[Path]):
        """Delete empty directories."""
        print("\n[*] Cleaning empty directories...")
        for dirpath in sorted(dirs, reverse=True):  # Delete deepest first
            try:
                rel_path = dirpath.relative_to(self.project_root)
                if self.dry_run:
                    print(f"  [DRY] Would delete: {rel_path}/")
                else:
                    dirpath.rmdir()
                    print(f"  [OK] Deleted: {rel_path}/")
                self.stats["deleted"] += 1
            except Exception as e:
                print(f"  [ERR] {rel_path}: {e}")
                self.stats["errors"] += 1

    def archive_reports(self, files: List[Path]):
        """Move report files to archive."""
        print("\n[*] Archiving report files...")

        archive_dir = self.project_root / ".archive" / "reports"
        if not self.dry_run:
            archive_dir.mkdir(parents=True, exist_ok=True)

        for filepath in files:
            try:
                target = archive_dir / filepath.name
                if target.exists():
                    print(f"  [SKIP] Already archived: {filepath.name}")
                    self.stats["skipped"] += 1
                    continue

                if self.dry_run:
                    print(f"  [DRY] Would move: {filepath.name} -> .archive/reports/")
                else:
                    shutil.move(str(filepath), str(target))
                    print(f"  [OK] Moved: {filepath.name} -> .archive/reports/")
                self.stats["moved"] += 1
            except Exception as e:
                print(f"  [ERR] {filepath.name}: {e}")
                self.stats["errors"] += 1

    def _delete_files(self, files: List[Path]):
        """Delete a list of files."""
        for filepath in files:
            try:
                rel_path = filepath.relative_to(self.project_root)
                if self.dry_run:
                    print(f"  [DRY] Would delete: {rel_path}")
                else:
                    filepath.unlink()
                    print(f"  [OK] Deleted: {rel_path}")
                self.stats["deleted"] += 1
            except Exception as e:
                print(f"  [ERR] {rel_path}: {e}")
                self.stats["errors"] += 1

    def _delete_dirs(self, dirs: List[Path]):
        """Delete directories recursively."""
        for dirpath in dirs:
            try:
                rel_path = dirpath.relative_to(self.project_root)
                if self.dry_run:
                    print(f"  [DRY] Would delete: {rel_path}/")
                else:
                    shutil.rmtree(dirpath)
                    print(f"  [OK] Deleted: {rel_path}/")
                self.stats["deleted"] += 1
            except Exception as e:
                print(f"  [ERR] {rel_path}: {e}")
                self.stats["errors"] += 1

    def print_stats(self):
        """Print cleanup statistics."""
        print("\n" + "=" * 60)
        print("CLEANUP SUMMARY")
        print("=" * 60)
        print(f"  Deleted: {self.stats['deleted']}")
        print(f"  Moved: {self.stats['moved']}")
        print(f"  Skipped: {self.stats['skipped']}")
        print(f"  Errors: {self.stats['errors']}")

        if self.dry_run:
            print("\n  [INFO] This was a DRY RUN - no changes were made")
            print("  [INFO] Run with --execute to apply changes")


# ============================================================================
# REPORT GENERATOR
# ============================================================================


def generate_report(results: Dict[str, List[Any]], project_root: Path) -> str:
    """Generate cleanup analysis report."""
    lines = []
    lines.append("=" * 80)
    lines.append("REPOSITORY CLEANUP REPORT")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Project: {project_root}")
    lines.append("")

    # Summary
    total_issues = (
        len(results["temp_files"])
        + len(results["backup_files"])
        + len(results["pycache_dirs"])
        + len(results["empty_dirs"])
        + len(results["report_files"])
        + len(results["duplicate_files"])
        + len(results["obsolete_docs"])
    )

    lines.append("SUMMARY")
    lines.append("-" * 40)
    lines.append(f"  Cache directories: {len(results['pycache_dirs'])}")
    lines.append(f"  Temporary files: {len(results['temp_files'])}")
    lines.append(f"  Backup files: {len(results['backup_files'])}")
    lines.append(f"  Empty directories: {len(results['empty_dirs'])}")
    lines.append(f"  Report files: {len(results['report_files'])}")
    lines.append(f"  Large files (>1MB): {len(results['large_files'])}")
    lines.append(f"  Duplicate file sets: {len(results['duplicate_files'])}")
    lines.append(f"  Obsolete docs: {len(results['obsolete_docs'])}")
    lines.append(f"  Total cleanup items: {total_issues}")
    lines.append("")

    # Details sections
    if results["pycache_dirs"]:
        lines.append("=" * 80)
        lines.append("CACHE DIRECTORIES (safe to delete)")
        lines.append("=" * 80)
        for dirpath in sorted(results["pycache_dirs"])[:20]:
            rel_path = dirpath.relative_to(project_root)
            lines.append(f"  {rel_path}/")
        if len(results["pycache_dirs"]) > 20:
            lines.append(f"  ... and {len(results['pycache_dirs']) - 20} more")
        lines.append("")

    if results["temp_files"]:
        lines.append("=" * 80)
        lines.append("TEMPORARY FILES (safe to delete)")
        lines.append("=" * 80)
        for filepath in sorted(results["temp_files"])[:20]:
            rel_path = filepath.relative_to(project_root)
            lines.append(f"  {rel_path}")
        if len(results["temp_files"]) > 20:
            lines.append(f"  ... and {len(results['temp_files']) - 20} more")
        lines.append("")

    if results["backup_files"]:
        lines.append("=" * 80)
        lines.append("BACKUP FILES (review before deleting)")
        lines.append("=" * 80)
        for filepath in sorted(results["backup_files"]):
            rel_path = filepath.relative_to(project_root)
            lines.append(f"  {rel_path}")
        lines.append("")

    if results["report_files"]:
        lines.append("=" * 80)
        lines.append("REPORT FILES (should be archived)")
        lines.append("=" * 80)
        for filepath in sorted(results["report_files"]):
            lines.append(f"  {filepath.name}")
        lines.append("")

    if results["large_files"]:
        lines.append("=" * 80)
        lines.append("LARGE FILES (>1MB)")
        lines.append("=" * 80)
        for filepath, size in sorted(results["large_files"], key=lambda x: x[1], reverse=True)[:15]:
            rel_path = filepath.relative_to(project_root)
            lines.append(f"  {format_size(size):>10s}  {rel_path}")
        lines.append("")

    if results["duplicate_files"]:
        lines.append("=" * 80)
        lines.append("DUPLICATE FILES")
        lines.append("=" * 80)
        for i, (_, files) in enumerate(results["duplicate_files"].items(), 1):
            if i > 10:
                lines.append(f"  ... and {len(results['duplicate_files']) - 10} more sets")
                break
            lines.append(f"  Set {i} ({len(files)} files):")
            for filepath in files:
                rel_path = filepath.relative_to(project_root)
                lines.append(f"    - {rel_path}")
        lines.append("")

    # Cleanup commands
    lines.append("=" * 80)
    lines.append("CLEANUP COMMANDS")
    lines.append("=" * 80)
    lines.append("")
    lines.append("Quick cleanup (safe):")
    lines.append("  python -m scripts.utils.cleanup clean --execute")
    lines.append("")
    lines.append("Manual cleanup:")
    lines.append('  find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null')
    lines.append('  find . -type f -name "*.pyc" -delete')
    lines.append("")

    return "\n".join(lines)


# ============================================================================
# CLI COMMANDS
# ============================================================================


def cmd_scan(args):
    """Quick scan for cleanup items."""
    project_root = get_project_root()
    scanner = RepositoryScanner(project_root)
    results = scanner.scan_all(quick=True)

    # Print summary
    print("\n" + "=" * 60)
    print("QUICK SCAN RESULTS")
    print("=" * 60)
    print(f"  Cache directories: {len(results['pycache_dirs'])}")
    print(f"  Temporary files: {len(results['temp_files'])}")
    print(f"  Backup files: {len(results['backup_files'])}")
    print(f"  Empty directories: {len(results['empty_dirs'])}")
    print(f"  Report files: {len(results['report_files'])}")
    print(f"  Large files (>1MB): {len(results['large_files'])}")
    print("")
    print("Run 'python -m scripts.utils.cleanup analyze' for full report")
    print("Run 'python -m scripts.utils.cleanup clean' to clean up")


def cmd_analyze(args):
    """Full analysis with report."""
    project_root = get_project_root()
    scanner = RepositoryScanner(project_root)
    results = scanner.scan_all(quick=False)

    report = generate_report(results, project_root)
    print("\n" + report)

    # Save report
    report_path = project_root / "cleanup_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[*] Report saved to: {report_path}")


def cmd_clean(args):
    """Clean up repository."""
    project_root = get_project_root()
    dry_run = not args.execute

    # Scan first
    scanner = RepositoryScanner(project_root)
    results = scanner.scan_all(quick=True)

    # Clean
    cleaner = RepositoryCleaner(project_root, dry_run=dry_run)

    if results["pycache_dirs"]:
        cleaner.clean_pycache(results["pycache_dirs"])

    if results["temp_files"]:
        cleaner.clean_temp_files(results["temp_files"])

    if results["empty_dirs"]:
        cleaner.clean_empty_dirs(results["empty_dirs"])

    if results["report_files"]:
        cleaner.archive_reports(results["report_files"])

    cleaner.print_stats()


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Main entry point."""
    # UTF-8 for Windows
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Repository Cleanup Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scripts.utils.cleanup scan           # Quick scan
  python -m scripts.utils.cleanup analyze        # Full analysis report
  python -m scripts.utils.cleanup clean          # Clean (dry run)
  python -m scripts.utils.cleanup clean --execute  # Actually clean
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Quick scan for cleanup items")
    scan_parser.set_defaults(func=cmd_scan)

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Full analysis with report")
    analyze_parser.set_defaults(func=cmd_analyze)

    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean up repository")
    clean_parser.add_argument(
        "--execute", action="store_true", help="Actually perform cleanup (default is dry run)"
    )
    clean_parser.set_defaults(func=cmd_clean)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
