#!/usr/bin/env python
"""
Analyze Root Directory Cleanup

Analyzes files in the project root directory to identify:
1. Report files that should be archived
2. Temporary files
3. Files that should be in docs/ or other directories
4. Old/obsolete configuration files
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def analyze_root_directory(project_root: Path):
    """Analyze root directory for cleanup."""

    results = {
        'reports': [],
        'temp_files': [],
        'documentation': [],
        'config_files': [],
        'keep_files': [],
        'other_files': [],
        'directories': []
    }

    # Files that should definitely be kept in root
    keep_in_root = {
        'README.md',
        'INSTALLATION.md',
        'QUICK_START.md',
        'CONTRIBUTING.md',
        'CHANGELOG.md',
        'LICENSE',
        'LICENSE.md',
        '.gitignore',
        '.gitattributes',
        'requirements.txt',
        'pyproject.toml',
        'setup.py',
        'setup.cfg',
        'poetry.lock',
        'Pipfile',
        'Pipfile.lock',
        'env.example',
        '.env.example',
    }

    print("[*] Analyzing root directory...")
    print()

    # Scan only root level
    for item in project_root.iterdir():
        if item.name.startswith('.') and item.is_dir():
            # Skip hidden directories
            continue

        if item.is_dir():
            results['directories'].append(item)
            continue

        # Categorize files
        if item.name in keep_in_root:
            results['keep_files'].append(item)
        elif item.name.endswith('_report.txt') or item.name.endswith('_log.txt'):
            results['reports'].append(item)
        elif item.name.endswith('.log'):
            results['temp_files'].append(item)
        elif item.name.endswith('.md') and item.name not in keep_in_root:
            results['documentation'].append(item)
        elif item.name.endswith(('.yml', '.yaml', '.json', '.toml', '.ini', '.cfg')):
            results['config_files'].append(item)
        elif item.name.endswith(('.tmp', '.bak', '.old', '.backup')):
            results['temp_files'].append(item)
        else:
            results['other_files'].append(item)

    return results


def get_file_info(filepath: Path) -> dict:
    """Get file information."""
    stat = filepath.stat()
    return {
        'name': filepath.name,
        'size': stat.st_size,
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'is_empty': stat.st_size == 0
    }


def generate_report(results: dict, project_root: Path) -> str:
    """Generate root cleanup report."""
    lines = []
    lines.append("=" * 80)
    lines.append("ROOT DIRECTORY CLEANUP ANALYSIS")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Summary
    total_files = (
        len(results['reports']) +
        len(results['temp_files']) +
        len(results['documentation']) +
        len(results['config_files']) +
        len(results['keep_files']) +
        len(results['other_files'])
    )

    lines.append("SUMMARY")
    lines.append("=" * 80)
    lines.append(f"Total files in root: {total_files}")
    lines.append(f"  Keep in root: {len(results['keep_files'])}")
    lines.append(f"  Reports to archive: {len(results['reports'])}")
    lines.append(f"  Documentation files: {len(results['documentation'])}")
    lines.append(f"  Configuration files: {len(results['config_files'])}")
    lines.append(f"  Temporary files: {len(results['temp_files'])}")
    lines.append(f"  Other files: {len(results['other_files'])}")
    lines.append(f"  Directories: {len(results['directories'])}")
    lines.append("")

    # Reports
    if results['reports']:
        lines.append("=" * 80)
        lines.append("REPORT FILES (Move to .archive/reports/)")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['reports'])} report files")
        lines.append("")

        for filepath in sorted(results['reports']):
            info = get_file_info(filepath)
            lines.append(f"  - {info['name']}")
            lines.append(f"    Size: {format_size(info['size'])}, Modified: {info['modified'].strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

    # Documentation
    if results['documentation']:
        lines.append("=" * 80)
        lines.append("DOCUMENTATION FILES (Review location)")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['documentation'])} markdown files")
        lines.append("")

        for filepath in sorted(results['documentation']):
            info = get_file_info(filepath)
            lines.append(f"  - {info['name']}")
            lines.append(f"    Size: {format_size(info['size'])}, Modified: {info['modified'].strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

    # Temporary files
    if results['temp_files']:
        lines.append("=" * 80)
        lines.append("TEMPORARY FILES (Safe to delete)")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['temp_files'])} temporary files")
        lines.append("")

        for filepath in sorted(results['temp_files']):
            info = get_file_info(filepath)
            lines.append(f"  - {info['name']}")
            lines.append(f"    Size: {format_size(info['size'])}, Modified: {info['modified'].strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

    # Configuration files
    if results['config_files']:
        lines.append("=" * 80)
        lines.append("CONFIGURATION FILES")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['config_files'])} configuration files")
        lines.append("")

        for filepath in sorted(results['config_files']):
            info = get_file_info(filepath)
            status = "(empty)" if info['is_empty'] else ""
            lines.append(f"  - {info['name']} {status}")
            lines.append(f"    Size: {format_size(info['size'])}, Modified: {info['modified'].strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

    # Other files
    if results['other_files']:
        lines.append("=" * 80)
        lines.append("OTHER FILES (Review)")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['other_files'])} other files")
        lines.append("")

        for filepath in sorted(results['other_files']):
            info = get_file_info(filepath)
            lines.append(f"  - {info['name']}")
            lines.append(f"    Size: {format_size(info['size'])}, Modified: {info['modified'].strftime('%Y-%m-%d %H:%M')}")
        lines.append("")

    # Keep files
    if results['keep_files']:
        lines.append("=" * 80)
        lines.append("FILES TO KEEP IN ROOT")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['keep_files'])} essential files")
        lines.append("")

        for filepath in sorted(results['keep_files']):
            info = get_file_info(filepath)
            lines.append(f"  ✓ {info['name']}")
        lines.append("")

    # Directories
    if results['directories']:
        lines.append("=" * 80)
        lines.append("ROOT DIRECTORIES")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['directories'])} directories")
        lines.append("")

        for dirpath in sorted(results['directories']):
            try:
                file_count = sum(1 for _ in dirpath.rglob('*') if _.is_file())
                lines.append(f"  - {dirpath.name}/ ({file_count} files)")
            except:
                lines.append(f"  - {dirpath.name}/")
        lines.append("")

    # Recommendations
    lines.append("=" * 80)
    lines.append("CLEANUP RECOMMENDATIONS")
    lines.append("=" * 80)
    lines.append("")

    if results['reports']:
        lines.append("[HIGH PRIORITY] Move report files to archive:")
        lines.append("  mkdir -p .archive/reports")
        for filepath in sorted(results['reports']):
            lines.append(f'  mv "{filepath.name}" .archive/reports/')
        lines.append("")

    if results['temp_files']:
        lines.append("[HIGH PRIORITY] Delete temporary files:")
        for filepath in sorted(results['temp_files']):
            lines.append(f'  rm "{filepath.name}"')
        lines.append("")

    if results['documentation']:
        lines.append("[MEDIUM PRIORITY] Review documentation files:")
        lines.append("  Consider moving to docs/ or .archive/ if obsolete")
        for filepath in sorted(results['documentation']):
            lines.append(f'  # Review: {filepath.name}')
        lines.append("")

    # Add to .gitignore
    lines.append("=" * 80)
    lines.append("RECOMMENDED .gitignore ADDITIONS")
    lines.append("=" * 80)
    lines.append("")
    lines.append("Add these patterns to .gitignore:")
    lines.append("  *_report.txt")
    lines.append("  *_log.txt")
    lines.append("  *.log")
    lines.append("  obsolete_*.txt")
    lines.append("  quick_cleanup_report.txt")
    lines.append("  import_validation_*.txt")
    lines.append("  docs_cleanup_log.txt")
    lines.append("")

    return "\n".join(lines)


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

    results = analyze_root_directory(project_root)

    report = generate_report(results, project_root)
    print("\n" + report)

    # Save report
    report_path = project_root / 'root_cleanup_analysis.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print("=" * 80)
    print(f"[*] Report saved to: {report_path}")
    print("=" * 80)


if __name__ == '__main__':
    main()
