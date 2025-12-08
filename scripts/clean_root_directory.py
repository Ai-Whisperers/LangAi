#!/usr/bin/env python
"""
Clean Root Directory

Moves report files and analysis outputs to .archive/reports/
Optionally moves example scripts to examples/
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime


def clean_root_directory(project_root: Path, dry_run: bool = True):
    """Clean root directory by moving reports and organizing files."""

    # Files to move to .archive/reports/
    report_files = [
        'docs_cleanup_log.txt',
        'import_validation_output.txt',
        'import_validation_report.txt',
        'obsolete_docs_report.txt',
        'obsolete_files_report.txt',
        'quick_cleanup_report.txt',
        'root_cleanup_analysis.txt',
    ]

    # Example scripts to move to examples/
    example_scripts = [
        'hello_research.py',
    ]

    # Stats
    stats = {
        'reports_moved': 0,
        'examples_moved': 0,
        'skipped': 0,
        'errors': 0
    }

    print("=" * 80)
    if dry_run:
        print("DRY RUN - No files will be moved")
    else:
        print("CLEANING ROOT DIRECTORY")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Move report files
    print("[*] Moving report files to .archive/reports/")
    print()

    archive_reports = project_root / '.archive' / 'reports'
    if not dry_run:
        archive_reports.mkdir(parents=True, exist_ok=True)

    for filename in report_files:
        source = project_root / filename
        target = archive_reports / filename

        if not source.exists():
            print(f"  [ ] SKIP: {filename} (not found)")
            stats['skipped'] += 1
            continue

        if target.exists():
            print(f"  [ ] SKIP: {filename} (already exists in archive)")
            stats['skipped'] += 1
            continue

        try:
            size = source.stat().st_size
            if dry_run:
                print(f"  [√] WOULD MOVE: {filename} ({format_size(size)})")
                print(f"      → .archive/reports/{filename}")
            else:
                shutil.move(str(source), str(target))
                print(f"  [√] MOVED: {filename} ({format_size(size)})")
                print(f"      → .archive/reports/{filename}")
            stats['reports_moved'] += 1
        except Exception as e:
            print(f"  [X] ERROR: {filename}")
            print(f"      {e}")
            stats['errors'] += 1

    # Move example scripts
    print()
    print("[*] Moving example scripts to examples/")
    print()

    examples_dir = project_root / 'examples'
    if not dry_run:
        examples_dir.mkdir(parents=True, exist_ok=True)

    for filename in example_scripts:
        source = project_root / filename
        target = examples_dir / filename

        if not source.exists():
            print(f"  [ ] SKIP: {filename} (not found)")
            stats['skipped'] += 1
            continue

        if target.exists():
            print(f"  [ ] SKIP: {filename} (already exists in examples/)")
            stats['skipped'] += 1
            continue

        try:
            size = source.stat().st_size
            if dry_run:
                print(f"  [√] WOULD MOVE: {filename} ({format_size(size)})")
                print(f"      → examples/{filename}")
            else:
                shutil.move(str(source), str(target))
                print(f"  [√] MOVED: {filename} ({format_size(size)})")
                print(f"      → examples/{filename}")
            stats['examples_moved'] += 1
        except Exception as e:
            print(f"  [X] ERROR: {filename}")
            print(f"      {e}")
            stats['errors'] += 1

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Report files moved: {stats['reports_moved']}")
    print(f"Example scripts moved: {stats['examples_moved']}")
    print(f"Files skipped: {stats['skipped']}")
    print(f"Errors: {stats['errors']}")
    print()

    if dry_run:
        print("=" * 80)
        print("This was a DRY RUN - no changes were made")
        print("Run with --execute to actually move files")
        print("=" * 80)
    else:
        print("=" * 80)
        print("Root directory cleaned successfully!")
        print("=" * 80)

    return stats


def format_size(size: int) -> str:
    """Format file size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}TB"


def main():
    """Main function."""
    # Set UTF-8 encoding for Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    project_root = Path(__file__).parent.parent

    # Check for --execute flag
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        dry_run = False
        print()
        print("!" * 80)
        print("EXECUTING - Files will be moved")
        print("!" * 80)
        print()

        # Confirm
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            sys.exit(0)
        print()

    stats = clean_root_directory(project_root, dry_run=dry_run)

    # Save log
    log_path = project_root / 'root_cleanup_log.txt'
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"Root Directory Cleanup Log\n")
        f.write(f"==========================\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}\n")
        f.write(f"\n")
        f.write(f"Report files moved: {stats['reports_moved']}\n")
        f.write(f"Example scripts moved: {stats['examples_moved']}\n")
        f.write(f"Files skipped: {stats['skipped']}\n")
        f.write(f"Errors: {stats['errors']}\n")

    print()
    if not dry_run:
        print(f"[*] Log saved to: {log_path}")
        print()


if __name__ == '__main__':
    main()
