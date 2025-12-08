#!/usr/bin/env python
"""
Quick Cleanup Scanner - Focused on src/ directory only

Analyzes src/ and root level for cleanup candidates.
Skips External repos/ to avoid long scanning times.
"""

import os
import sys
from pathlib import Path
from collections import defaultdict
import hashlib


def scan_for_cleanup(project_root: Path):
    """Quick scan for cleanup candidates."""

    # Directories to scan
    scan_dirs = [
        project_root / 'src',
        project_root / 'scripts',
        project_root / 'tests',
        project_root / 'docs',
        project_root / '.archive'
    ]

    # Patterns
    temp_patterns = ['*.tmp', '*.pyc', '*.pyo', '*.log', '*.swp', '*~']
    backup_patterns = ['*.bak', '*.backup', '*.old', '*.orig']

    results = {
        'temp_files': [],
        'backup_files': [],
        'empty_dirs': [],
        'large_files': [],
        'pycache_dirs': []
    }

    print("[*] Quick scanning for cleanup candidates...")
    print()

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue

        print(f"[*] Scanning {scan_dir.name}/...")

        for root, dirs, files in os.walk(scan_dir):
            # Find __pycache__ directories
            if '__pycache__' in dirs:
                pycache_path = Path(root) / '__pycache__'
                results['pycache_dirs'].append(pycache_path)

            # Remove cache dirs from further scanning
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.pytest_cache', '.mypy_cache', 'node_modules']]

            for filename in files:
                filepath = Path(root) / filename

                try:
                    # Check for temp files
                    for pattern in temp_patterns:
                        if filepath.match(pattern):
                            results['temp_files'].append(filepath)
                            break

                    # Check for backup files
                    for pattern in backup_patterns:
                        if filepath.match(pattern):
                            results['backup_files'].append(filepath)
                            break

                    # Check file size (>1MB)
                    size = filepath.stat().st_size
                    if size > 1024 * 1024:
                        results['large_files'].append((filepath, size))

                except (PermissionError, OSError):
                    continue

            # Check for empty directories
            for dirname in dirs:
                dirpath = Path(root) / dirname
                try:
                    contents = list(dirpath.iterdir())
                    if not contents:
                        results['empty_dirs'].append(dirpath)
                    elif len(contents) == 1 and contents[0].name == '__init__.py':
                        if contents[0].stat().st_size == 0:
                            results['empty_dirs'].append(dirpath)
                except (PermissionError, OSError):
                    continue

    # Check root level
    print("[*] Scanning root level...")
    root_items = [
        '.archive',
        'obsolete_files_report.txt',
        'import_validation_report.txt',
        'import_validation_output.txt'
    ]

    results['root_level'] = []
    for item in root_items:
        item_path = project_root / item
        if item_path.exists():
            results['root_level'].append(item_path)

    return results


def format_size(size: int) -> str:
    """Format file size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}TB"


def generate_report(results: dict, project_root: Path):
    """Generate cleanup report."""
    lines = []
    lines.append("=" * 80)
    lines.append("QUICK CLEANUP SCAN REPORT")
    lines.append("=" * 80)
    lines.append(f"Scanned: src/, scripts/, tests/, docs/, .archive/")
    lines.append("")

    # Summary
    total_cleanup = (
        len(results['temp_files']) +
        len(results['backup_files']) +
        len(results['empty_dirs']) +
        len(results['pycache_dirs'])
    )

    lines.append("SUMMARY")
    lines.append("=" * 80)
    lines.append(f"__pycache__ directories: {len(results['pycache_dirs'])}")
    lines.append(f"Temporary files: {len(results['temp_files'])}")
    lines.append(f"Backup files: {len(results['backup_files'])}")
    lines.append(f"Empty directories: {len(results['empty_dirs'])}")
    lines.append(f"Large files (>1MB): {len(results['large_files'])}")
    lines.append(f"Root level items: {len(results['root_level'])}")
    lines.append(f"Total cleanup candidates: {total_cleanup}")
    lines.append("")

    # __pycache__ directories
    if results['pycache_dirs']:
        lines.append("=" * 80)
        lines.append("__PYCACHE__ DIRECTORIES (Safe to delete)")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['pycache_dirs'])} __pycache__ directories")
        lines.append("")

        for dirpath in sorted(results['pycache_dirs'])[:20]:
            rel_path = dirpath.relative_to(project_root)
            lines.append(f"  - {rel_path}/")

        if len(results['pycache_dirs']) > 20:
            lines.append(f"  ... and {len(results['pycache_dirs']) - 20} more")
        lines.append("")

    # Temporary files
    if results['temp_files']:
        lines.append("=" * 80)
        lines.append("TEMPORARY FILES (Safe to delete)")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['temp_files'])} temporary files")
        lines.append("")

        for filepath in sorted(results['temp_files'])[:20]:
            rel_path = filepath.relative_to(project_root)
            lines.append(f"  - {rel_path}")

        if len(results['temp_files']) > 20:
            lines.append(f"  ... and {len(results['temp_files']) - 20} more")
        lines.append("")

    # Backup files
    if results['backup_files']:
        lines.append("=" * 80)
        lines.append("BACKUP FILES")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['backup_files'])} backup files")
        lines.append("")

        for filepath in sorted(results['backup_files']):
            rel_path = filepath.relative_to(project_root)
            lines.append(f"  - {rel_path}")
        lines.append("")

    # Empty directories
    if results['empty_dirs']:
        lines.append("=" * 80)
        lines.append("EMPTY DIRECTORIES")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['empty_dirs'])} empty directories")
        lines.append("")

        for dirpath in sorted(results['empty_dirs']):
            rel_path = dirpath.relative_to(project_root)
            lines.append(f"  - {rel_path}/")
        lines.append("")

    # Large files
    if results['large_files']:
        lines.append("=" * 80)
        lines.append("LARGE FILES (>1MB)")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['large_files'])} large files")
        lines.append("")

        for filepath, size in sorted(results['large_files'], key=lambda x: x[1], reverse=True)[:15]:
            rel_path = filepath.relative_to(project_root)
            lines.append(f"  {format_size(size):>10s}  {rel_path}")

        if len(results['large_files']) > 15:
            lines.append(f"  ... and {len(results['large_files']) - 15} more")
        lines.append("")

    # Root level
    if results['root_level']:
        lines.append("=" * 80)
        lines.append("ROOT LEVEL ITEMS")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['root_level'])} items")
        lines.append("")

        for item_path in sorted(results['root_level']):
            if item_path.is_dir():
                # Count files
                file_count = sum(1 for _ in item_path.rglob('*') if _.is_file())
                lines.append(f"  - {item_path.name}/ ({file_count} files)")
            else:
                size = item_path.stat().st_size
                lines.append(f"  - {item_path.name} ({format_size(size)})")
        lines.append("")

    # Cleanup commands
    lines.append("=" * 80)
    lines.append("CLEANUP COMMANDS")
    lines.append("=" * 80)
    lines.append("")

    if results['pycache_dirs'] or results['temp_files']:
        lines.append("[HIGH] Clean Python cache and temp files:")
        lines.append('  find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null')
        lines.append('  find . -type f -name "*.pyc" -delete')
        lines.append('  find . -type f -name "*.pyo" -delete')
        lines.append("")

    if results['backup_files']:
        lines.append("[MEDIUM] Remove backup files:")
        lines.append("  # Review each file first, then delete if not needed")
        for filepath in sorted(results['backup_files'])[:5]:
            rel_path = filepath.relative_to(project_root)
            lines.append(f'  rm "{rel_path}"')
        if len(results['backup_files']) > 5:
            lines.append(f"  # ... and {len(results['backup_files']) - 5} more")
        lines.append("")

    if results['empty_dirs']:
        lines.append("[LOW] Remove empty directories:")
        lines.append("  find . -type d -empty -delete")
        lines.append("")

    # Additional recommendations
    lines.append("=" * 80)
    lines.append("ADDITIONAL RECOMMENDATIONS")
    lines.append("=" * 80)
    lines.append("")
    lines.append("1. Consider moving 'External repos/' to a separate location")
    lines.append("   - These are git submodules or reference repositories")
    lines.append("   - Keep them outside the main project directory")
    lines.append("")
    lines.append("2. Complete staged deletions:")
    lines.append('   git commit -m "chore: Remove obsolete files"')
    lines.append("")
    lines.append("3. Add to .gitignore:")
    lines.append("   __pycache__/")
    lines.append("   *.pyc")
    lines.append("   *.pyo")
    lines.append("   *.log")
    lines.append("   *_report.txt")
    lines.append("")

    return "\n".join(lines)


def main():
    """Main function."""
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    project_root = Path(__file__).parent.parent

    results = scan_for_cleanup(project_root)

    report = generate_report(results, project_root)
    print("\n" + report)

    # Save report
    report_path = project_root / 'quick_cleanup_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print("=" * 80)
    print(f"[*] Report saved to: {report_path}")
    print("=" * 80)


if __name__ == '__main__':
    main()
