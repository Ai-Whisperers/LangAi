#!/usr/bin/env python3
"""
Automated Refactoring Script - Datetime Pattern

This script automatically refactors datetime.now(timezone.utc) to utc_now()
across the codebase. It's safe to run because this is a simple mechanical
replacement.

Usage:
    # Dry run (preview changes)
    python automated_refactor_datetime.py --dry-run

    # Apply changes
    python automated_refactor_datetime.py --apply

    # Apply to specific file
    python automated_refactor_datetime.py --apply --file path/to/file.py
"""

import argparse
import re
from pathlib import Path
from typing import List, Set, Tuple

BASE_DIR = Path(r"c:\Users\Alejandro\Documents\Ivan\Work\Lang ai\src\company_researcher")


class DatetimeRefactorer:
    """Automatically refactor datetime patterns to use utc_now()."""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.files_modified = 0
        self.lines_modified = 0

    def refactor_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """
        Refactor a single file.

        Returns:
            (was_modified, changes_made)
        """
        # Skip utils/time.py (that's the implementation)
        if "utils/time.py" in str(file_path) or "utils\\time.py" in str(file_path):
            return False, []

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return False, []

        original_content = content
        changes = []

        # Check if file already uses datetime.now(timezone.utc)
        if "datetime.now(timezone.utc)" not in content:
            return False, []

        # Check if already importing utc_now
        has_utc_now_import = bool(
            re.search(r"from company_researcher\.utils import.*\butc_now\b", content)
        )

        # Step 1: Replace datetime.now(timezone.utc) with utc_now()
        new_content, count = re.subn(r"\bdatetime\.now\(timezone\.utc\)", "utc_now()", content)

        if count > 0:
            changes.append(
                f"Replaced {count} occurrences of datetime.now(timezone.utc) with utc_now()"
            )
            self.lines_modified += count

        # Step 2: Add import if not present
        if not has_utc_now_import and count > 0:
            new_content = self._add_utc_now_import(new_content)
            changes.append("Added 'from company_researcher.utils import utc_now'")

        # Step 3: Clean up datetime imports if no longer needed
        if count > 0:
            new_content = self._cleanup_datetime_imports(new_content)
            if new_content != content:
                changes.append("Cleaned up unused datetime imports")

        # Save if modified and not dry run
        if new_content != original_content:
            if not self.dry_run:
                file_path.write_text(new_content, encoding="utf-8")
            self.files_modified += 1
            return True, changes

        return False, []

    def _add_utc_now_import(self, content: str) -> str:
        """Add utc_now to existing utils import or create new one."""

        # Check if there's already a utils import we can extend
        utils_import_match = re.search(r"from company_researcher\.utils import ([^\n]+)", content)

        if utils_import_match:
            # Extend existing import
            existing_imports = utils_import_match.group(1)

            # Handle multi-line imports
            if "(" in existing_imports:
                # Multi-line import
                new_imports = existing_imports.rstrip()
                if not new_imports.endswith(","):
                    new_imports = new_imports.rstrip(")").rstrip() + ","
                new_imports += "\n    utc_now,"
                if ")" in existing_imports:
                    new_imports += "\n)"

                content = content.replace(
                    f"from company_researcher.utils import {existing_imports}",
                    f"from company_researcher.utils import {new_imports}",
                )
            else:
                # Single-line import - convert to multi-line if multiple items
                imports = [i.strip() for i in existing_imports.split(",")]
                if "utc_now" not in imports:
                    imports.append("utc_now")

                if len(imports) > 3:
                    # Convert to multi-line
                    new_import = "from company_researcher.utils import (\n"
                    new_import += ",\n".join(f"    {imp}" for imp in sorted(imports))
                    new_import += "\n)"
                else:
                    # Keep single line
                    new_import = f'from company_researcher.utils import {", ".join(imports)}'

                content = re.sub(
                    r"from company_researcher\.utils import [^\n]+", new_import, content, count=1
                )
        else:
            # No utils import exists, add new one after other imports
            # Find the last import line
            import_lines = []
            lines = content.split("\n")
            last_import_idx = -1

            for i, line in enumerate(lines):
                if line.strip().startswith("import ") or line.strip().startswith("from "):
                    last_import_idx = i

            if last_import_idx >= 0:
                # Insert after last import
                lines.insert(last_import_idx + 1, "from company_researcher.utils import utc_now")
                content = "\n".join(lines)
            else:
                # No imports, add at top after docstring
                # Find end of module docstring
                docstring_match = re.search(r'^"""[\s\S]*?"""', content)
                if docstring_match:
                    insert_pos = docstring_match.end()
                    content = (
                        content[:insert_pos]
                        + "\n\nfrom company_researcher.utils import utc_now\n"
                        + content[insert_pos:]
                    )
                else:
                    content = "from company_researcher.utils import utc_now\n\n" + content

        return content

    def _cleanup_datetime_imports(self, content: str) -> str:
        """Remove datetime imports if no longer needed."""

        # Check if datetime or timezone are still used
        has_datetime_usage = bool(
            re.search(r"\bdatetime\.(datetime|timedelta|date|time)\b", content)
        )
        has_timezone_usage = bool(re.search(r"\btimezone\.\w+", content))

        # If datetime.now(timezone.utc) was the only usage, clean up
        if not has_datetime_usage and not has_timezone_usage:
            # Remove entire import line
            content = re.sub(
                r"^from datetime import datetime, timezone\n", "", content, flags=re.MULTILINE
            )
            content = re.sub(
                r"^from datetime import timezone, datetime\n", "", content, flags=re.MULTILINE
            )
        elif not has_timezone_usage:
            # Remove just timezone
            content = re.sub(
                r"from datetime import (.*?)timezone,?\s*", r"from datetime import \1", content
            )
            content = re.sub(
                r"from datetime import (.*?),\s*timezone", r"from datetime import \1", content
            )
            # Clean up double commas
            content = re.sub(r",\s*,", ",", content)

        return content

    def refactor_all(self):
        """Refactor all Python files in the codebase."""
        py_files = list(BASE_DIR.rglob("*.py"))

        print(f"{'[DRY RUN] ' if self.dry_run else ''}Scanning {len(py_files)} Python files...")
        print()

        for py_file in py_files:
            # Skip __pycache__
            if "__pycache__" in str(py_file):
                continue

            modified, changes = self.refactor_file(py_file)

            if modified:
                rel_path = py_file.relative_to(BASE_DIR.parent.parent)
                print(f"{'[WOULD MODIFY]' if self.dry_run else '[MODIFIED]'} {rel_path}")
                for change in changes:
                    print(f"  - {change}")
                print()

        print("=" * 80)
        print(f"{'DRY RUN ' if self.dry_run else ''}SUMMARY")
        print("=" * 80)
        print(f"Files modified: {self.files_modified}")
        print(f"Lines modified: {self.lines_modified}")

        if self.dry_run:
            print("\nThis was a dry run. Use --apply to make actual changes.")
        else:
            print("\nRefactoring complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Automatically refactor datetime.now(timezone.utc) to utc_now()"
    )
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    parser.add_argument("--file", type=str, help="Refactor specific file only")

    args = parser.parse_args()

    refactorer = DatetimeRefactorer(dry_run=not args.apply)

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            return 1

        modified, changes = refactorer.refactor_file(file_path)
        if modified:
            print(f"{'[WOULD MODIFY]' if refactorer.dry_run else '[MODIFIED]'} {file_path}")
            for change in changes:
                print(f"  - {change}")
        else:
            print(f"No changes needed for {file_path}")
    else:
        refactorer.refactor_all()

    return 0


if __name__ == "__main__":
    exit(main())
