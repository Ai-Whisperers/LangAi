#!/usr/bin/env python
"""
Analyze repository for obsolete files and directories.

Identifies:
1. Duplicate files
2. Old/backup files (.bak, .old, ~)
3. Temporary files
4. Unused documentation
5. Empty directories
6. Archive directories
7. Cache directories
8. Test artifacts
"""

import os
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
import json


class ObsoleteFileAnalyzer:
    """Analyze repository for obsolete files."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.duplicates = defaultdict(list)
        self.old_files = []
        self.temp_files = []
        self.backup_files = []
        self.empty_dirs = []
        self.archive_dirs = []
        self.cache_dirs = []
        self.large_files = []
        self.obsolete_docs = []

        # Patterns
        self.temp_patterns = [
            '*.tmp', '*.temp', '*~', '*.swp', '*.swo',
            '*.pyc', '*.pyo', '__pycache__', '*.log'
        ]
        self.backup_patterns = [
            '*.bak', '*.backup', '*.old', '*.orig',
            '*-old', '*_old', '*-backup', '*_backup'
        ]
        self.archive_dirs_names = [
            'archive', 'archived', 'old', 'backup',
            'backups', 'deprecated', 'legacy'
        ]
        self.cache_dirs_names = [
            '__pycache__', '.pytest_cache', 'htmlcov',
            '.mypy_cache', '.coverage', 'node_modules',
            '.git', '.venv', 'venv'
        ]

    def analyze(self):
        """Run all analysis."""
        print("[*] Analyzing repository structure...")

        self.find_duplicate_files()
        self.find_temp_files()
        self.find_backup_files()
        self.find_empty_directories()
        self.find_archive_directories()
        self.find_large_files()
        self.find_obsolete_documentation()

    def find_duplicate_files(self):
        """Find duplicate files by content hash."""
        print("\n[*] Scanning for duplicate files...")

        file_hashes = defaultdict(list)

        for root, dirs, files in os.walk(self.project_root):
            # Skip cache/venv directories
            dirs[:] = [d for d in dirs if d not in self.cache_dirs_names]

            for filename in files:
                filepath = Path(root) / filename

                # Skip very large files
                try:
                    if filepath.stat().st_size > 10 * 1024 * 1024:  # 10MB
                        continue

                    # Skip binary files we don't care about
                    if filepath.suffix in ['.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.exe']:
                        continue

                    # Calculate hash
                    file_hash = self._hash_file(filepath)
                    if file_hash:
                        file_hashes[file_hash].append(filepath)
                except (PermissionError, OSError):
                    continue

        # Find duplicates (hash appears more than once)
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                self.duplicates[file_hash] = files

    def find_temp_files(self):
        """Find temporary files."""
        print("[*] Scanning for temporary files...")

        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.cache_dirs_names]

            for filename in files:
                filepath = Path(root) / filename

                # Check patterns
                for pattern in self.temp_patterns:
                    if filepath.match(pattern):
                        self.temp_files.append(filepath)
                        break

    def find_backup_files(self):
        """Find backup files."""
        print("[*] Scanning for backup files...")

        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.cache_dirs_names]

            for filename in files:
                filepath = Path(root) / filename

                # Check patterns
                for pattern in self.backup_patterns:
                    if filepath.match(pattern):
                        self.backup_files.append(filepath)
                        break

    def find_empty_directories(self):
        """Find empty directories."""
        print("[*] Scanning for empty directories...")

        for root, dirs, files in os.walk(self.project_root, topdown=False):
            for dirname in dirs:
                dirpath = Path(root) / dirname

                # Skip cache directories
                if dirname in self.cache_dirs_names:
                    continue

                # Check if empty (no files, only maybe __init__.py)
                try:
                    contents = list(dirpath.iterdir())
                    if not contents:
                        self.empty_dirs.append(dirpath)
                    elif len(contents) == 1 and contents[0].name == '__init__.py':
                        # Only __init__.py, check if it's empty
                        if contents[0].stat().st_size == 0:
                            self.empty_dirs.append(dirpath)
                except (PermissionError, OSError):
                    continue

    def find_archive_directories(self):
        """Find archive/old directories."""
        print("[*] Scanning for archive directories...")

        for root, dirs, files in os.walk(self.project_root):
            for dirname in dirs:
                if dirname.lower() in self.archive_dirs_names:
                    dirpath = Path(root) / dirname
                    self.archive_dirs.append(dirpath)

    def find_large_files(self):
        """Find unusually large files."""
        print("[*] Scanning for large files...")

        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.cache_dirs_names]

            for filename in files:
                filepath = Path(root) / filename

                try:
                    size = filepath.stat().st_size
                    # Files larger than 1MB
                    if size > 1024 * 1024:
                        self.large_files.append((filepath, size))
                except (PermissionError, OSError):
                    continue

    def find_obsolete_documentation(self):
        """Find potentially obsolete documentation."""
        print("[*] Scanning for obsolete documentation...")

        # Look for old/duplicate READMEs, CHANGELOGs, etc.
        doc_files = defaultdict(list)

        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.cache_dirs_names]

            for filename in files:
                if filename.lower() in ['readme.md', 'changelog.md', 'contributing.md',
                                       'license.md', 'todo.md', 'notes.md']:
                    filepath = Path(root) / filename
                    doc_files[filename.lower()].append(filepath)

        # Multiple copies of the same doc type might be obsolete
        for doc_type, files in doc_files.items():
            if len(files) > 1:
                self.obsolete_docs.append((doc_type, files))

    def _hash_file(self, filepath: Path) -> str:
        """Calculate file hash."""
        try:
            hasher = hashlib.md5()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return None

    def generate_report(self) -> str:
        """Generate analysis report."""
        lines = []
        lines.append("=" * 80)
        lines.append("OBSOLETE FILES ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"Project Root: {self.project_root}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Summary
        total_issues = (
            len(self.duplicates) +
            len(self.temp_files) +
            len(self.backup_files) +
            len(self.empty_dirs) +
            len(self.archive_dirs) +
            len(self.obsolete_docs)
        )

        lines.append("SUMMARY")
        lines.append("=" * 80)
        lines.append(f"Duplicate File Sets: {len(self.duplicates)}")
        lines.append(f"Temporary Files: {len(self.temp_files)}")
        lines.append(f"Backup Files: {len(self.backup_files)}")
        lines.append(f"Empty Directories: {len(self.empty_dirs)}")
        lines.append(f"Archive Directories: {len(self.archive_dirs)}")
        lines.append(f"Large Files (>1MB): {len(self.large_files)}")
        lines.append(f"Obsolete Documentation: {len(self.obsolete_docs)}")
        lines.append(f"Total Issues: {total_issues}")
        lines.append("")

        # Duplicate files
        if self.duplicates:
            lines.append("=" * 80)
            lines.append("DUPLICATE FILES")
            lines.append("=" * 80)
            lines.append(f"Found {len(self.duplicates)} sets of duplicate files")
            lines.append("")

            for i, (file_hash, files) in enumerate(self.duplicates.items(), 1):
                lines.append(f"{i}. Duplicate Set ({len(files)} files):")
                for filepath in files:
                    rel_path = filepath.relative_to(self.project_root)
                    size = filepath.stat().st_size
                    lines.append(f"   - {rel_path} ({self._format_size(size)})")
                lines.append("")

        # Temporary files
        if self.temp_files:
            lines.append("=" * 80)
            lines.append("TEMPORARY FILES")
            lines.append("=" * 80)
            lines.append(f"Found {len(self.temp_files)} temporary files")
            lines.append("")

            for filepath in sorted(self.temp_files)[:50]:  # Limit to 50
                rel_path = filepath.relative_to(self.project_root)
                lines.append(f"  - {rel_path}")

            if len(self.temp_files) > 50:
                lines.append(f"  ... and {len(self.temp_files) - 50} more")
            lines.append("")

        # Backup files
        if self.backup_files:
            lines.append("=" * 80)
            lines.append("BACKUP FILES")
            lines.append("=" * 80)
            lines.append(f"Found {len(self.backup_files)} backup files")
            lines.append("")

            for filepath in sorted(self.backup_files):
                rel_path = filepath.relative_to(self.project_root)
                lines.append(f"  - {rel_path}")
            lines.append("")

        # Empty directories
        if self.empty_dirs:
            lines.append("=" * 80)
            lines.append("EMPTY DIRECTORIES")
            lines.append("=" * 80)
            lines.append(f"Found {len(self.empty_dirs)} empty directories")
            lines.append("")

            for dirpath in sorted(self.empty_dirs):
                rel_path = dirpath.relative_to(self.project_root)
                lines.append(f"  - {rel_path}/")
            lines.append("")

        # Archive directories
        if self.archive_dirs:
            lines.append("=" * 80)
            lines.append("ARCHIVE DIRECTORIES")
            lines.append("=" * 80)
            lines.append(f"Found {len(self.archive_dirs)} archive directories")
            lines.append("")

            for dirpath in sorted(self.archive_dirs):
                rel_path = dirpath.relative_to(self.project_root)
                # Count files in directory
                file_count = sum(1 for _ in dirpath.rglob('*') if _.is_file())
                dir_size = sum(f.stat().st_size for f in dirpath.rglob('*') if f.is_file())
                lines.append(f"  - {rel_path}/ ({file_count} files, {self._format_size(dir_size)})")
            lines.append("")

        # Large files
        if self.large_files:
            lines.append("=" * 80)
            lines.append("LARGE FILES (>1MB)")
            lines.append("=" * 80)
            lines.append(f"Found {len(self.large_files)} large files")
            lines.append("")

            # Sort by size
            for filepath, size in sorted(self.large_files, key=lambda x: x[1], reverse=True)[:20]:
                rel_path = filepath.relative_to(self.project_root)
                lines.append(f"  {self._format_size(size):>10s}  {rel_path}")

            if len(self.large_files) > 20:
                lines.append(f"  ... and {len(self.large_files) - 20} more")
            lines.append("")

        # Obsolete documentation
        if self.obsolete_docs:
            lines.append("=" * 80)
            lines.append("POTENTIALLY OBSOLETE DOCUMENTATION")
            lines.append("=" * 80)
            lines.append(f"Found {len(self.obsolete_docs)} potential issues")
            lines.append("")

            for doc_type, files in self.obsolete_docs:
                lines.append(f"Multiple {doc_type} files:")
                for filepath in files:
                    rel_path = filepath.relative_to(self.project_root)
                    lines.append(f"  - {rel_path}")
                lines.append("")

        # Cleanup recommendations
        lines.append("=" * 80)
        lines.append("CLEANUP RECOMMENDATIONS")
        lines.append("=" * 80)
        lines.append("")

        if self.temp_files:
            lines.append("[HIGH] Remove temporary files:")
            lines.append("  git clean -fdx  # Remove all untracked files")
            lines.append("")

        if self.backup_files:
            lines.append("[MEDIUM] Review and remove backup files:")
            lines.append("  These can usually be safely deleted if you have git history")
            lines.append("")

        if self.archive_dirs:
            lines.append("[MEDIUM] Review archive directories:")
            lines.append("  Consider moving to separate archive repo or deleting if not needed")
            lines.append("")

        if self.duplicates:
            lines.append("[MEDIUM] Review duplicate files:")
            lines.append("  Keep one copy and remove duplicates")
            lines.append("")

        if self.empty_dirs:
            lines.append("[LOW] Remove empty directories:")
            lines.append("  These serve no purpose and can be removed")
            lines.append("")

        return "\n".join(lines)

    def _format_size(self, size: int) -> str:
        """Format file size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"


def main():
    """Main analysis function."""
    project_root = Path(__file__).parent.parent

    analyzer = ObsoleteFileAnalyzer(project_root)
    analyzer.analyze()

    report = analyzer.generate_report()
    print("\n" + report)

    # Save report
    report_path = project_root / 'obsolete_files_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print("=" * 80)
    print(f"[*] Full report saved to: {report_path}")
    print("=" * 80)


if __name__ == '__main__':
    main()
