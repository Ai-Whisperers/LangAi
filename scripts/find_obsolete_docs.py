#!/usr/bin/env python
"""
Find Obsolete Documentation Files

Analyzes markdown files to identify:
1. Duplicate documentation (multiple README, CHANGELOG, etc.)
2. Old/dated documentation (references to old phases, deprecated features)
3. Documentation in wrong locations
4. Redundant planning/status files
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def analyze_markdown_files(project_root: Path):
    """Analyze markdown files for obsolescence."""

    results = {
        'duplicate_docs': defaultdict(list),
        'planning_docs': [],
        'status_docs': [],
        'old_phase_docs': [],
        'validation_docs': [],
        'implementation_docs': [],
        'all_markdown': []
    }

    # Skip these directories
    skip_dirs = {
        '__pycache__', '.git', 'venv', '.venv', 'node_modules',
        '.pytest_cache', '.mypy_cache', 'External repos'
    }

    print("[*] Scanning for markdown files...")

    for root, dirs, files in os.walk(project_root):
        # Remove skip directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for filename in files:
            if not filename.lower().endswith('.md'):
                continue

            filepath = Path(root) / filename
            rel_path = filepath.relative_to(project_root)

            results['all_markdown'].append(filepath)

            # Check for duplicate doc types
            doc_type = filename.lower()
            if doc_type in ['readme.md', 'changelog.md', 'contributing.md',
                           'license.md', 'installation.md', 'quickstart.md']:
                results['duplicate_docs'][doc_type].append(filepath)

            # Check for planning documents
            if any(keyword in filename.lower() for keyword in
                   ['planning', 'roadmap', 'todo', 'todos', 'plan']):
                results['planning_docs'].append(filepath)

            # Check for status/progress documents
            if any(keyword in filename.lower() for keyword in
                   ['status', 'progress', 'checklist', 'validation']):
                results['status_docs'].append(filepath)

            # Check for old phase documents
            if 'phase' in filename.lower():
                results['old_phase_docs'].append(filepath)

            # Check for validation/verification documents
            if any(keyword in filename.lower() for keyword in
                   ['validation', 'verification', 'check']):
                results['validation_docs'].append(filepath)

            # Check for implementation summaries
            if any(keyword in filename.lower() for keyword in
                   ['implementation', 'summary', 'analysis']):
                results['implementation_docs'].append(filepath)

    return results


def check_file_content(filepath: Path, project_root: Path) -> dict:
    """Check file content for obsolescence indicators."""
    info = {
        'filepath': filepath,
        'rel_path': filepath.relative_to(project_root),
        'size': filepath.stat().st_size,
        'modified': datetime.fromtimestamp(filepath.stat().st_mtime),
        'indicators': []
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for date references
        if 'TODO' in content or 'FIXME' in content:
            info['indicators'].append('Contains TODO/FIXME')

        # Check for "old" or "deprecated" mentions
        if any(word in content.lower() for word in ['deprecated', 'obsolete', 'old system']):
            info['indicators'].append('References deprecated/obsolete content')

        # Check for specific old features
        if 'research-workflow-system' in content.lower():
            info['indicators'].append('References old research-workflow-system')

        # Check for completed status
        if 'completed' in content.lower() or '✅' in content or 'COMPLETED' in content:
            info['indicators'].append('Marked as completed')

        # Check if it's a short file (might be a stub)
        if len(content.strip()) < 200:
            info['indicators'].append(f'Short file ({len(content)} chars)')

    except Exception as e:
        info['indicators'].append(f'Error reading: {e}')

    return info


def generate_report(results: dict, project_root: Path) -> str:
    """Generate markdown obsolescence report."""
    lines = []
    lines.append("=" * 80)
    lines.append("OBSOLETE MARKDOWN DOCUMENTATION REPORT")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Summary
    total_md = len(results['all_markdown'])
    duplicate_count = sum(len(files) for files in results['duplicate_docs'].values() if len(files) > 1)

    lines.append("SUMMARY")
    lines.append("=" * 80)
    lines.append(f"Total Markdown Files: {total_md}")
    lines.append(f"Duplicate Documentation: {duplicate_count} files")
    lines.append(f"Planning Documents: {len(results['planning_docs'])}")
    lines.append(f"Status/Progress Documents: {len(results['status_docs'])}")
    lines.append(f"Phase Documents: {len(results['old_phase_docs'])}")
    lines.append(f"Validation Documents: {len(results['validation_docs'])}")
    lines.append(f"Implementation Summaries: {len(results['implementation_docs'])}")
    lines.append("")

    # Duplicate documentation
    duplicate_sets = {k: v for k, v in results['duplicate_docs'].items() if len(v) > 1}
    if duplicate_sets:
        lines.append("=" * 80)
        lines.append("DUPLICATE DOCUMENTATION (Keep 1, archive others)")
        lines.append("=" * 80)
        lines.append("")

        for doc_type, files in sorted(duplicate_sets.items()):
            lines.append(f"{doc_type.upper()} ({len(files)} copies):")
            for filepath in sorted(files):
                rel_path = filepath.relative_to(project_root)
                size = filepath.stat().st_size
                modified = datetime.fromtimestamp(filepath.stat().st_mtime).strftime('%Y-%m-%d')
                lines.append(f"  - {rel_path}")
                lines.append(f"    Modified: {modified}, Size: {size} bytes")
            lines.append("")

    # Phase documents
    if results['old_phase_docs']:
        lines.append("=" * 80)
        lines.append("PHASE DOCUMENTS (Archive completed phases)")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['old_phase_docs'])} phase documents")
        lines.append("")

        # Analyze each phase doc
        phase_docs_analyzed = []
        for filepath in sorted(results['old_phase_docs']):
            info = check_file_content(filepath, project_root)
            phase_docs_analyzed.append(info)

        for info in sorted(phase_docs_analyzed, key=lambda x: x['rel_path']):
            lines.append(f"- {info['rel_path']}")
            lines.append(f"  Modified: {info['modified'].strftime('%Y-%m-%d %H:%M')}")
            if info['indicators']:
                for indicator in info['indicators']:
                    lines.append(f"  ! {indicator}")
            lines.append("")

    # Status documents
    if results['status_docs']:
        lines.append("=" * 80)
        lines.append("STATUS/PROGRESS DOCUMENTS (Archive if completed)")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['status_docs'])} status documents")
        lines.append("")

        status_docs_analyzed = []
        for filepath in sorted(results['status_docs']):
            info = check_file_content(filepath, project_root)
            status_docs_analyzed.append(info)

        for info in sorted(status_docs_analyzed, key=lambda x: x['rel_path']):
            lines.append(f"- {info['rel_path']}")
            lines.append(f"  Modified: {info['modified'].strftime('%Y-%m-%d %H:%M')}")
            if info['indicators']:
                for indicator in info['indicators']:
                    lines.append(f"  ! {indicator}")
            lines.append("")

    # Planning documents
    if results['planning_docs']:
        lines.append("=" * 80)
        lines.append("PLANNING DOCUMENTS (Review and archive old plans)")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['planning_docs'])} planning documents")
        lines.append("")

        for filepath in sorted(results['planning_docs']):
            rel_path = filepath.relative_to(project_root)
            modified = datetime.fromtimestamp(filepath.stat().st_mtime).strftime('%Y-%m-%d')
            size = filepath.stat().st_size
            lines.append(f"  - {rel_path}")
            lines.append(f"    Modified: {modified}, Size: {size} bytes")
        lines.append("")

    # Implementation summaries
    if results['implementation_docs']:
        lines.append("=" * 80)
        lines.append("IMPLEMENTATION SUMMARIES (Archive after completion)")
        lines.append("=" * 80)
        lines.append(f"Found {len(results['implementation_docs'])} implementation documents")
        lines.append("")

        impl_docs_analyzed = []
        for filepath in sorted(results['implementation_docs']):
            info = check_file_content(filepath, project_root)
            impl_docs_analyzed.append(info)

        for info in sorted(impl_docs_analyzed, key=lambda x: x['rel_path']):
            lines.append(f"- {info['rel_path']}")
            lines.append(f"  Modified: {info['modified'].strftime('%Y-%m-%d %H:%M')}")
            if info['indicators']:
                for indicator in info['indicators']:
                    lines.append(f"  ! {indicator}")
            lines.append("")

    # Recommendations
    lines.append("=" * 80)
    lines.append("RECOMMENDATIONS")
    lines.append("=" * 80)
    lines.append("")

    lines.append("MOVE TO .archive/:")
    lines.append("")

    if duplicate_sets:
        lines.append("1. Duplicate Documentation:")
        lines.append("   - Keep the most recent/complete version in root or docs/")
        lines.append("   - Move older duplicates to .archive/documentation/")
        lines.append("")

    if results['old_phase_docs']:
        lines.append("2. Completed Phase Documents:")
        lines.append("   - Move PHASE_*_STATUS.md and PHASE_*_SUMMARY.md to .archive/phases/")
        lines.append("   - Keep current phase docs in root")
        lines.append("")

    if results['status_docs']:
        lines.append("3. Completed Status Documents:")
        lines.append("   - Move VALIDATION_REPORT.md, VALIDATION_CHECKLIST.md to .archive/validation/")
        lines.append("   - Keep only active status tracking in root")
        lines.append("")

    if results['planning_docs']:
        lines.append("4. Old Planning Documents:")
        lines.append("   - Move completed planning docs to .archive/planning/")
        lines.append("   - Keep active roadmap/planning in docs/planning/")
        lines.append("")

    if results['implementation_docs']:
        lines.append("5. Implementation Summaries:")
        lines.append("   - Move to .archive/implementation/")
        lines.append("   - These are historical records, not active documentation")
        lines.append("")

    # Suggested archive structure
    lines.append("=" * 80)
    lines.append("SUGGESTED ARCHIVE STRUCTURE")
    lines.append("=" * 80)
    lines.append("")
    lines.append(".archive/")
    lines.append("  documentation/     # Duplicate/old doc files")
    lines.append("  phases/           # Completed phase documents")
    lines.append("  validation/       # Validation reports and checklists")
    lines.append("  planning/         # Old planning documents")
    lines.append("  implementation/   # Implementation summaries")
    lines.append("  reference/        # Reference code (existing)")
    lines.append("")

    # Keep in active documentation
    lines.append("=" * 80)
    lines.append("KEEP IN ACTIVE DOCUMENTATION")
    lines.append("=" * 80)
    lines.append("")
    lines.append("Root level:")
    lines.append("  - README.md (main project overview)")
    lines.append("  - INSTALLATION.md")
    lines.append("  - QUICK_START.md")
    lines.append("  - CONTRIBUTING.md (if exists)")
    lines.append("")
    lines.append("docs/:")
    lines.append("  - Current architecture documentation")
    lines.append("  - Active user guides")
    lines.append("  - API documentation")
    lines.append("")
    lines.append("docs/planning/:")
    lines.append("  - Active roadmap")
    lines.append("  - Current sprint plans")
    lines.append("")

    return "\n".join(lines)


def main():
    """Main function."""
    # Set UTF-8 encoding for Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    project_root = Path(__file__).parent.parent

    results = analyze_markdown_files(project_root)

    report = generate_report(results, project_root)
    print("\n" + report)

    # Save report
    report_path = project_root / 'obsolete_docs_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print("=" * 80)
    print(f"[*] Report saved to: {report_path}")
    print("=" * 80)


if __name__ == '__main__':
    main()
