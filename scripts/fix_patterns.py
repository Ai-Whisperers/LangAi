"""
Bulk Pattern Replacement Script for Codebase Standardization.

This script replaces:
1. datetime.now() and datetime.utcnow() → utc_now()
2. logging.getLogger(__name__) → get_logger(__name__)

And adds the appropriate imports from company_researcher.utils.
"""

import os
import re
from pathlib import Path
from typing import List, Set, Tuple

# Files to exclude from modification (use filename only for simplicity)
EXCLUDE_FILES = {
    "time.py",  # Defines utc_now() in utils/
    "logging.py",  # Defines get_logger() in utils/ (but we use logger.py)
    "fix_patterns.py",  # This script
}

# Specific paths to exclude (checked with endswith)
EXCLUDE_PATHS = {
    "utils/time.py",
    "utils\\time.py",
    "utils/logger.py",  # The actual file name
    "utils\\logger.py",
    "utils/__init__.py",
    "utils\\__init__.py",
}

# Directories to exclude
EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    "venv",
    ".venv",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    "External repos",
}


def should_process_file(filepath: Path) -> bool:
    """Check if file should be processed."""
    # Only Python files
    if not filepath.suffix == ".py":
        return False

    rel_path = str(filepath)

    # Check specific path exclusions
    for exclude_path in EXCLUDE_PATHS:
        if rel_path.endswith(exclude_path):
            return False

    # Check directory exclusions
    for exclude_dir in EXCLUDE_DIRS:
        if exclude_dir in rel_path:
            return False

    return True


def fix_datetime_patterns(content: str) -> Tuple[str, bool, Set[str]]:
    """
    Replace datetime.now() and datetime.utcnow() with utc_now().

    Returns:
        Tuple of (new_content, was_changed, imports_needed)
    """
    imports_needed = set()
    changed = False

    # Pattern for datetime.now() - but not datetime.now(tz=...)
    datetime_now_pattern = r"datetime\.now\(\)"
    if re.search(datetime_now_pattern, content):
        content = re.sub(datetime_now_pattern, "utc_now()", content)
        imports_needed.add("utc_now")
        changed = True

    # Pattern for datetime.utcnow()
    datetime_utcnow_pattern = r"datetime\.utcnow\(\)"
    if re.search(datetime_utcnow_pattern, content):
        content = re.sub(datetime_utcnow_pattern, "utc_now()", content)
        imports_needed.add("utc_now")
        changed = True

    # Pattern for default_factory=datetime.now
    factory_now_pattern = r"default_factory\s*=\s*datetime\.now(?!\()"
    if re.search(factory_now_pattern, content):
        content = re.sub(factory_now_pattern, "default_factory=utc_now", content)
        imports_needed.add("utc_now")
        changed = True

    # Pattern for default_factory=datetime.utcnow
    factory_utcnow_pattern = r"default_factory\s*=\s*datetime\.utcnow(?!\()"
    if re.search(factory_utcnow_pattern, content):
        content = re.sub(factory_utcnow_pattern, "default_factory=utc_now", content)
        imports_needed.add("utc_now")
        changed = True

    return content, changed, imports_needed


def fix_logging_patterns(content: str) -> Tuple[str, bool, Set[str]]:
    """
    Replace logging.getLogger(__name__) with get_logger(__name__).

    Returns:
        Tuple of (new_content, was_changed, imports_needed)
    """
    imports_needed = set()
    changed = False

    # Pattern for logging.getLogger(__name__)
    logging_pattern = r"logging\.getLogger\(__name__\)"
    if re.search(logging_pattern, content):
        content = re.sub(logging_pattern, "get_logger(__name__)", content)
        imports_needed.add("get_logger")
        changed = True

    return content, changed, imports_needed


def add_imports(content: str, imports_needed: Set[str]) -> str:
    """Add necessary imports to the file content."""
    if not imports_needed:
        return content

    # Check what's already imported from company_researcher.utils
    existing_utils_import = re.search(
        r"from\s+company_researcher\.utils\s+import\s+([^\n]+)", content
    )

    # Also check src.company_researcher.utils
    existing_src_utils_import = re.search(
        r"from\s+src\.company_researcher\.utils\s+import\s+([^\n]+)", content
    )

    if existing_utils_import:
        # Add to existing import
        current_imports = existing_utils_import.group(1)
        current_imports_list = [
            i.strip() for i in current_imports.replace("(", "").replace(")", "").split(",")
        ]

        # Filter out imports that already exist
        new_imports = [i for i in imports_needed if i not in current_imports_list]

        if new_imports:
            all_imports = current_imports_list + new_imports
            new_import_str = ", ".join(sorted(all_imports))
            content = re.sub(
                r"from\s+company_researcher\.utils\s+import\s+[^\n]+",
                f"from company_researcher.utils import {new_import_str}",
                content,
            )
    elif existing_src_utils_import:
        # Add to existing src.company_researcher.utils import
        current_imports = existing_src_utils_import.group(1)
        current_imports_list = [
            i.strip() for i in current_imports.replace("(", "").replace(")", "").split(",")
        ]

        new_imports = [i for i in imports_needed if i not in current_imports_list]

        if new_imports:
            all_imports = current_imports_list + new_imports
            new_import_str = ", ".join(sorted(all_imports))
            content = re.sub(
                r"from\s+src\.company_researcher\.utils\s+import\s+[^\n]+",
                f"from src.company_researcher.utils import {new_import_str}",
                content,
            )
    else:
        # Need to add new import line
        # Find the right place to insert (after other imports)
        imports_str = ", ".join(sorted(imports_needed))
        new_import_line = f"from company_researcher.utils import {imports_str}\n"

        # Try to find existing imports to insert after
        import_patterns = [
            r"(from\s+company_researcher\.[^\n]+\n)",
            r"(from\s+\.[^\n]+\n)",  # Relative imports
            r"(import\s+[^\n]+\n)",
        ]

        inserted = False
        for pattern in import_patterns:
            matches = list(re.finditer(pattern, content))
            if matches:
                # Insert after the last import
                last_match = matches[-1]
                insert_pos = last_match.end()
                content = content[:insert_pos] + new_import_line + content[insert_pos:]
                inserted = True
                break

        if not inserted:
            # Insert after docstring or at beginning
            docstring_match = re.match(r'("""[\s\S]*?"""\n|\'\'\'[\s\S]*?\'\'\'\n)', content)
            if docstring_match:
                insert_pos = docstring_match.end()
                content = content[:insert_pos] + "\n" + new_import_line + content[insert_pos:]
            else:
                content = new_import_line + content

    return content


def remove_unused_imports(content: str) -> str:
    """Remove import logging if no longer used."""
    # Check if 'logging' is still used anywhere (other than the import)
    import_line = re.search(r"^import logging\s*$", content, re.MULTILINE)
    if import_line:
        # Check if logging is still used (other than just the import)
        content_without_import = content[: import_line.start()] + content[import_line.end() :]
        if not re.search(r"\blogging\.", content_without_import):
            # Remove the import logging line
            content = re.sub(r"^import logging\s*\n", "", content, flags=re.MULTILINE)

    return content


def process_file(filepath: Path, dry_run: bool = False) -> dict:
    """
    Process a single file.

    Returns:
        Dict with processing results
    """
    result = {
        "file": str(filepath),
        "datetime_fixed": False,
        "logging_fixed": False,
        "imports_added": set(),
        "error": None,
    }

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            original_content = f.read()

        content = original_content
        all_imports_needed = set()

        # Fix datetime patterns
        content, datetime_changed, datetime_imports = fix_datetime_patterns(content)
        result["datetime_fixed"] = datetime_changed
        all_imports_needed.update(datetime_imports)

        # Fix logging patterns
        content, logging_changed, logging_imports = fix_logging_patterns(content)
        result["logging_fixed"] = logging_changed
        all_imports_needed.update(logging_imports)

        # Add imports if needed
        if all_imports_needed:
            content = add_imports(content, all_imports_needed)
            result["imports_added"] = all_imports_needed

        # Remove unused logging import
        if logging_changed:
            content = remove_unused_imports(content)

        # Write changes if not dry run and content changed
        if not dry_run and content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

    except Exception as e:
        result["error"] = str(e)

    return result


def find_python_files(root_dir: Path) -> List[Path]:
    """Find all Python files to process."""
    files = []
    for filepath in root_dir.rglob("*.py"):
        if should_process_file(filepath):
            files.append(filepath)
    return files


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fix datetime and logging patterns")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be changed without modifying files"
    )
    parser.add_argument("--path", default="src/company_researcher", help="Path to process")
    args = parser.parse_args()

    root_dir = Path(args.path)
    if not root_dir.exists():
        print(f"Error: Path {root_dir} does not exist")
        return

    print(f"Processing files in: {root_dir}")
    print(f"Dry run: {args.dry_run}")
    print("=" * 60)

    files = find_python_files(root_dir)
    print(f"Found {len(files)} Python files to process")
    print()

    stats = {"datetime_fixed": 0, "logging_fixed": 0, "files_modified": 0, "errors": 0}

    for filepath in files:
        result = process_file(filepath, dry_run=args.dry_run)

        if result["error"]:
            print(f"ERROR: {filepath}: {result['error']}")
            stats["errors"] += 1
            continue

        if result["datetime_fixed"] or result["logging_fixed"]:
            stats["files_modified"] += 1
            changes = []
            if result["datetime_fixed"]:
                changes.append("datetime")
                stats["datetime_fixed"] += 1
            if result["logging_fixed"]:
                changes.append("logging")
                stats["logging_fixed"] += 1

            rel_path = filepath.relative_to(root_dir) if root_dir in filepath.parents else filepath
            imports = ", ".join(result["imports_added"]) if result["imports_added"] else "none"
            print(f"FIXED: {rel_path} - {', '.join(changes)} (imports: {imports})")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files processed: {len(files)}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"Datetime patterns fixed: {stats['datetime_fixed']}")
    print(f"Logging patterns fixed: {stats['logging_fixed']}")
    print(f"Errors: {stats['errors']}")

    if args.dry_run:
        print()
        print("This was a dry run. Run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
