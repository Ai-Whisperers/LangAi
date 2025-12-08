#!/usr/bin/env python
"""
Move Obsolete Documentation to Archive

Moves completed phase documents, validation reports, and old planning files
from docs/ to .archive/ with proper organization.
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime


def move_obsolete_docs(project_root: Path, dry_run: bool = True):
    """Move obsolete documentation to archive."""

    # Archive structure
    archive_root = project_root / '.archive'

    # Define file movements
    movements = {
        # Completed Phase Documents
        'phases/completed': [
            'docs/PHASE_10_IMPLEMENTATION_SUMMARY.md',
            'PHASE_10_STATUS.md',
        ],

        # Phase Validation Documents
        'phases/validation': [
            'docs/VALIDATION_CHECKLIST.md',
            'docs/internal/VALIDATION_REPORT.md',
            'outputs/logs/PHASE0_VALIDATION_SUMMARY.md',
            'outputs/logs/PHASE1_VALIDATION_SUMMARY.md',
            'outputs/logs/PHASE2_VALIDATION_SUMMARY.md',
            'outputs/logs/PHASE3_VALIDATION_SUMMARY.md',
            'outputs/logs/PHASE4_VALIDATION_SUMMARY.md',
            'outputs/logs/PHASES_1-9_PROGRESS_SUMMARY.md',
        ],

        # Phase Implementation Reports
        'phases/implementation': [
            'outputs/logs/PHASE3_QUALITY_FIX_REPORT.md',
            'outputs/logs/PHASE4_OBSERVABILITY_COMPLETE.md',
            'outputs/logs/PHASE5_QUALITY_COMPLETE.md',
            'outputs/logs/PHASE6_ADVANCED_DOCS_COMPLETE.md',
            'outputs/logs/PHASE7_FINANCIAL_AGENT_COMPLETE.md',
            'outputs/logs/PHASE8_MARKET_ANALYST_COMPLETE.md',
            'outputs/logs/microsoft_phase2_report.md',
            'outputs/logs/openai_phase2_report.md',
            'outputs/logs/stripe_phase2_report.md',
            'outputs/logs/tesla_phase2_report.md',
        ],

        # Phase Foundation Documents
        'phases/foundation': [
            'docs/company-researcher/PHASE_EVOLUTION.md',
            'docs/planning/phases/PHASE_1_FOUNDATION.md',
            'docs/planning/phases/PHASE_2_SPECIALISTS.md',
        ],

        # Master Planning Documents
        'planning/master-plans': [
            'docs/planning/MASTER_20_PHASE_PLAN.md',
            'docs/planning/DOCUMENTATION_PHASES_PLAN.md',
            'docs/planning/DOCUMENTATION_COMPREHENSIVE_PLAN.md',
            'docs/planning/MASTER_PLAN_EXECUTIVE_SUMMARY.md',
            'docs/planning/MASTER_ROADMAP.md',
            'docs/planning/PLANNING_INTEGRATION_MAP.md',
            'docs/internal/IMPROVEMENT_PLAN.md',
            'docs/internal/MASTER_REPO_PLAN.md',
        ],

        # Old Documentation Analysis
        'documentation/analysis': [
            'docs/DOCUMENTATION_ANALYSIS_AND_NEXT_STEPS.md',
            'docs/COMPANY_RESEARCHER_INTEGRATION_IDEAS.md',
        ],
    }

    # Stats
    stats = {
        'moved': 0,
        'skipped': 0,
        'errors': 0,
        'directories_created': 0
    }

    print("=" * 80)
    if dry_run:
        print("DRY RUN - No files will be moved")
    else:
        print("MOVING OBSOLETE DOCUMENTATION TO ARCHIVE")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Process movements
    for archive_subdir, files in movements.items():
        archive_path = archive_root / archive_subdir

        print(f"\n[*] Category: {archive_subdir}")
        print(f"    Target: .archive/{archive_subdir}/")
        print()

        # Create archive directory
        if not dry_run:
            archive_path.mkdir(parents=True, exist_ok=True)
            if not archive_path.exists():
                stats['directories_created'] += 1

        for file_rel_path in files:
            source = project_root / file_rel_path

            # Get filename
            filename = Path(file_rel_path).name
            target = archive_path / filename

            # Check if source exists
            if not source.exists():
                print(f"  [ ] SKIP: {file_rel_path}")
                print(f"      (File not found)")
                stats['skipped'] += 1
                continue

            # Check if target already exists
            if target.exists():
                print(f"  [ ] SKIP: {file_rel_path}")
                print(f"      (Already exists in archive)")
                stats['skipped'] += 1
                continue

            # Move file
            try:
                if dry_run:
                    print(f"  [√] WOULD MOVE: {file_rel_path}")
                    print(f"      → .archive/{archive_subdir}/{filename}")
                else:
                    shutil.move(str(source), str(target))
                    print(f"  [√] MOVED: {file_rel_path}")
                    print(f"      → .archive/{archive_subdir}/{filename}")
                stats['moved'] += 1
            except Exception as e:
                print(f"  [X] ERROR: {file_rel_path}")
                print(f"      {e}")
                stats['errors'] += 1

    # Additional cleanup - empty directories
    print()
    print("=" * 80)
    print("CLEANUP EMPTY DIRECTORIES")
    print("=" * 80)
    print()

    empty_dirs_to_check = [
        'docs/planning/phases',
        'docs/internal',
        'outputs/logs',
    ]

    for dir_path in empty_dirs_to_check:
        full_path = project_root / dir_path
        if full_path.exists():
            try:
                contents = list(full_path.iterdir())
                if not contents:
                    if dry_run:
                        print(f"  [√] WOULD REMOVE: {dir_path}/ (empty)")
                    else:
                        full_path.rmdir()
                        print(f"  [√] REMOVED: {dir_path}/ (empty)")
                else:
                    print(f"  [ ] KEEP: {dir_path}/ ({len(contents)} items)")
            except Exception as e:
                print(f"  [X] ERROR checking {dir_path}: {e}")

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files moved: {stats['moved']}")
    print(f"Files skipped: {stats['skipped']}")
    print(f"Errors: {stats['errors']}")
    print(f"Directories created: {stats['directories_created']}")
    print()

    if dry_run:
        print("=" * 80)
        print("This was a DRY RUN - no changes were made")
        print("Run with --execute to actually move files")
        print("=" * 80)

    return stats


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
        print("EXECUTING - Files will be moved to .archive/")
        print("!" * 80)
        print()

        # Confirm
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            sys.exit(0)
        print()

    stats = move_obsolete_docs(project_root, dry_run=dry_run)

    # Save log
    log_path = project_root / 'docs_cleanup_log.txt'
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"Documentation Cleanup Log\n")
        f.write(f"========================\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}\n")
        f.write(f"\n")
        f.write(f"Files moved: {stats['moved']}\n")
        f.write(f"Files skipped: {stats['skipped']}\n")
        f.write(f"Errors: {stats['errors']}\n")

    print()
    print(f"[*] Log saved to: {log_path}")
    print()


if __name__ == '__main__':
    main()
