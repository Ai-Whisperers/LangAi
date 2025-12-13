"""
Improved Bulk Pattern Replacement Script using AST for Safe Import Placement.

This script replaces:
1. datetime.now() and datetime.utcnow() → utc_now()
2. logging.getLogger(__name__) → get_logger(__name__)

Uses AST to properly determine where to insert imports (avoiding docstrings, classes).
Uses RELATIVE imports based on file depth within the package.

Usage:
    python scripts/fix_patterns_v2.py --dry-run  # Preview changes
    python scripts/fix_patterns_v2.py            # Apply changes
"""

import ast
import os
import re
from pathlib import Path
from typing import Set, Tuple, List, Optional


# Package root for calculating relative imports
PACKAGE_NAME = "company_researcher"

# Files to exclude from modification
EXCLUDE_FILES = {
    "time.py",
    "logger.py",
    "fix_patterns.py",
    "fix_patterns_v2.py",
}

# Specific paths to exclude (checked with endswith)
EXCLUDE_PATHS = {
    "utils/time.py",
    "utils\\time.py",
    "utils/logger.py",
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


def get_relative_import_prefix(filepath: Path, package_root: Path) -> str:
    """
    Calculate the relative import prefix based on file location within the package.

    Examples:
        - config.py (at package root) → '.'
        - agents/core/researcher.py (2 levels deep) → '...'
        - llm/client.py (1 level deep) → '..'

    Args:
        filepath: Full path to the file
        package_root: Path to the package root directory

    Returns:
        Relative import prefix (e.g., '.', '..', '...')
    """
    try:
        # Get path relative to package root
        relative_path = filepath.relative_to(package_root)

        # Count directory depth (number of parent directories)
        # -1 because we don't count the file itself
        depth = len(relative_path.parts) - 1

        if depth == 0:
            # File is at package root (e.g., config.py)
            return '.'
        else:
            # File is in a subdirectory
            # depth=1 (e.g., agents/base.py) → '..'
            # depth=2 (e.g., agents/core/researcher.py) → '...'
            return '.' * (depth + 1)
    except ValueError:
        # File is not under package root, use absolute import
        return None


def should_process_file(filepath: Path) -> bool:
    """Check if file should be processed."""
    if not filepath.suffix == ".py":
        return False

    rel_path = str(filepath)

    for exclude_path in EXCLUDE_PATHS:
        if rel_path.endswith(exclude_path):
            return False

    for exclude_dir in EXCLUDE_DIRS:
        if exclude_dir in rel_path:
            return False

    if filepath.name in EXCLUDE_FILES:
        return False

    return True


def get_import_insert_line(content: str) -> int:
    """
    Use AST to find the correct line to insert imports.

    Returns the line number (0-indexed) after the last import statement,
    or after the module docstring if no imports exist.
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        # If we can't parse, fall back to line 0
        return 0

    last_import_line = 0
    first_non_import_line = None

    for node in ast.iter_child_nodes(tree):
        # Skip module docstring (first Expr with Constant string)
        if isinstance(node, ast.Expr):
            if isinstance(node.value, (ast.Constant, ast.Str)):
                # This is likely the module docstring
                last_import_line = max(last_import_line, node.end_lineno or node.lineno)
                continue

        # Track import statements
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            last_import_line = max(last_import_line, node.end_lineno or node.lineno)
        else:
            # First non-import statement
            if first_non_import_line is None:
                first_non_import_line = node.lineno
            break

    return last_import_line


def check_existing_imports(content: str) -> Tuple[Set[str], Optional[int], Optional[str]]:
    """
    Check what's already imported from utils (relative or absolute).

    Returns:
        Tuple of:
        - set of already imported names
        - line number of import or None
        - existing import style ('relative', 'absolute', or None)
    """
    existing = set()
    import_line = None
    import_style = None

    # Match various import formats (relative and absolute)
    patterns = [
        # Relative imports (e.g., from .utils import, from ..utils import)
        (r'from\s+(\.+)utils\s+import\s+\(([^)]+)\)', 'relative'),  # Multi-line relative
        (r'from\s+(\.+)utils\s+import\s+([^\n]+)', 'relative'),     # Single line relative
        # Absolute imports
        (r'from\s+company_researcher\.utils\s+import\s+\(([^)]+)\)', 'absolute'),
        (r'from\s+company_researcher\.utils\s+import\s+([^\n]+)', 'absolute'),
        (r'from\s+src\.company_researcher\.utils\s+import\s+\(([^)]+)\)', 'absolute'),
        (r'from\s+src\.company_researcher\.utils\s+import\s+([^\n]+)', 'absolute'),
    ]

    lines = content.split('\n')
    for i, line in enumerate(lines):
        for pattern, style in patterns:
            match = re.search(pattern, line)
            if match:
                # For relative imports, group 1 is the dots, group 2 is imports
                # For absolute imports, group 1 is imports
                if style == 'relative':
                    imports_str = match.group(2)
                else:
                    imports_str = match.group(1)

                # Parse imported names
                for name in imports_str.split(','):
                    name = name.strip().strip('(').strip(')')
                    if name and not name.startswith('#'):
                        # Handle "as" aliases
                        name = name.split(' as ')[0].strip()
                        if name:
                            existing.add(name)
                if import_line is None:
                    import_line = i
                    import_style = style

    return existing, import_line, import_style


def fix_datetime_patterns(content: str, lines: List[str]) -> Tuple[List[str], bool, Set[str]]:
    """
    Replace datetime.now() and datetime.utcnow() with utc_now().

    Works on lines to preserve formatting.
    """
    imports_needed = set()
    changed = False

    for i, line in enumerate(lines):
        # Skip lines that are comments or in strings (basic check)
        stripped = line.lstrip()
        if stripped.startswith('#'):
            continue

        new_line = line

        # Pattern for datetime.now() - but not datetime.now(tz=...)
        if re.search(r'datetime\.now\(\)', new_line):
            new_line = re.sub(r'datetime\.now\(\)', 'utc_now()', new_line)
            imports_needed.add('utc_now')
            changed = True

        # Pattern for datetime.utcnow()
        if re.search(r'datetime\.utcnow\(\)', new_line):
            new_line = re.sub(r'datetime\.utcnow\(\)', 'utc_now()', new_line)
            imports_needed.add('utc_now')
            changed = True

        # Pattern for default_factory=datetime.now
        if re.search(r'default_factory\s*=\s*datetime\.now(?!\()', new_line):
            new_line = re.sub(r'default_factory\s*=\s*datetime\.now(?!\()', 'default_factory=utc_now', new_line)
            imports_needed.add('utc_now')
            changed = True

        # Pattern for default_factory=datetime.utcnow
        if re.search(r'default_factory\s*=\s*datetime\.utcnow(?!\()', new_line):
            new_line = re.sub(r'default_factory\s*=\s*datetime\.utcnow(?!\()', 'default_factory=utc_now', new_line)
            imports_needed.add('utc_now')
            changed = True

        lines[i] = new_line

    return lines, changed, imports_needed


def fix_logging_patterns(content: str, lines: List[str]) -> Tuple[List[str], bool, Set[str]]:
    """
    Replace logging.getLogger(__name__) with get_logger(__name__).
    """
    imports_needed = set()
    changed = False

    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith('#'):
            continue

        new_line = line

        if re.search(r'logging\.getLogger\(__name__\)', new_line):
            new_line = re.sub(r'logging\.getLogger\(__name__\)', 'get_logger(__name__)', new_line)
            imports_needed.add('get_logger')
            changed = True

        lines[i] = new_line

    return lines, changed, imports_needed


def add_imports_to_lines(
    lines: List[str],
    insert_line: int,
    imports_needed: Set[str],
    existing_imports: Set[str],
    relative_prefix: Optional[str] = None
) -> List[str]:
    """
    Add required imports at the correct position using relative imports.

    Args:
        lines: File lines
        insert_line: Line number to insert at
        imports_needed: Set of imports needed
        existing_imports: Set of already imported names
        relative_prefix: Relative import prefix (e.g., '.', '..', '...')
    """
    # Filter out imports that already exist
    new_imports = imports_needed - existing_imports

    if not new_imports:
        return lines

    # Create import line with relative prefix
    imports_str = ', '.join(sorted(new_imports))
    if relative_prefix:
        new_import_line = f'from {relative_prefix}utils import {imports_str}'
    else:
        # Fallback to absolute import if no relative prefix
        new_import_line = f'from company_researcher.utils import {imports_str}'

    # Insert at the correct position
    lines.insert(insert_line, new_import_line)

    return lines


def update_existing_import(
    lines: List[str],
    import_line: int,
    imports_needed: Set[str],
    existing_imports: Set[str],
    relative_prefix: Optional[str] = None,
    import_style: Optional[str] = None
) -> List[str]:
    """
    Update an existing import line to include new imports.

    Args:
        lines: File lines
        import_line: Line number of existing import
        imports_needed: Set of imports needed
        existing_imports: Set of already imported names
        relative_prefix: Relative import prefix for new imports
        import_style: Existing import style ('relative' or 'absolute')
    """
    new_imports = imports_needed - existing_imports
    if not new_imports:
        return lines

    all_imports = existing_imports | new_imports
    imports_str = ', '.join(sorted(all_imports))

    # Find and replace the import line
    line = lines[import_line]

    # Preserve existing import style
    if import_style == 'relative':
        # Extract existing relative prefix from the line
        match = re.search(r'from\s+(\.+)utils', line)
        if match:
            existing_prefix = match.group(1)
            new_line = f'from {existing_prefix}utils import {imports_str}'
        elif relative_prefix:
            new_line = f'from {relative_prefix}utils import {imports_str}'
        else:
            new_line = f'from .utils import {imports_str}'
    elif 'src.company_researcher.utils' in line:
        new_line = f'from src.company_researcher.utils import {imports_str}'
    else:
        # Default to relative import
        if relative_prefix:
            new_line = f'from {relative_prefix}utils import {imports_str}'
        else:
            new_line = f'from company_researcher.utils import {imports_str}'

    lines[import_line] = new_line
    return lines


def remove_unused_logging_import(lines: List[str]) -> List[str]:
    """
    Remove 'import logging' if logging is no longer used.
    """
    # Find the import logging line
    import_idx = None
    for i, line in enumerate(lines):
        if re.match(r'^\s*import\s+logging\s*$', line):
            import_idx = i
            break

    if import_idx is None:
        return lines

    # Check if 'logging.' is used anywhere else
    content_without_import = '\n'.join(lines[:import_idx] + lines[import_idx+1:])
    if not re.search(r'\blogging\.', content_without_import):
        # Remove the import line
        lines.pop(import_idx)

    return lines


def process_file(filepath: Path, package_root: Path, dry_run: bool = False) -> dict:
    """Process a single file.

    Args:
        filepath: Path to the file to process
        package_root: Path to the package root for relative import calculation
        dry_run: If True, don't write changes
    """
    result = {
        'file': str(filepath),
        'datetime_fixed': False,
        'logging_fixed': False,
        'imports_added': set(),
        'relative_prefix': None,
        'error': None
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        lines = content.split('\n')

        # Calculate relative import prefix for this file
        relative_prefix = get_relative_import_prefix(filepath, package_root)
        result['relative_prefix'] = relative_prefix

        # Check existing imports
        existing_imports, existing_import_line, import_style = check_existing_imports(content)

        all_imports_needed = set()

        # Fix datetime patterns
        lines, datetime_changed, datetime_imports = fix_datetime_patterns(content, lines)
        result['datetime_fixed'] = datetime_changed
        all_imports_needed.update(datetime_imports)

        # Fix logging patterns
        content_after_datetime = '\n'.join(lines)
        lines, logging_changed, logging_imports = fix_logging_patterns(content_after_datetime, lines)
        result['logging_fixed'] = logging_changed
        all_imports_needed.update(logging_imports)

        # Add/update imports if needed
        if all_imports_needed:
            if existing_import_line is not None:
                lines = update_existing_import(
                    lines, existing_import_line, all_imports_needed, existing_imports,
                    relative_prefix=relative_prefix, import_style=import_style
                )
            else:
                # Find correct insert position using AST
                insert_line = get_import_insert_line(original_content)
                lines = add_imports_to_lines(
                    lines, insert_line, all_imports_needed, existing_imports,
                    relative_prefix=relative_prefix
                )

            result['imports_added'] = all_imports_needed - existing_imports

        # Remove unused logging import
        if logging_changed:
            lines = remove_unused_logging_import(lines)

        new_content = '\n'.join(lines)

        # Write changes if not dry run and content changed
        if not dry_run and new_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

    except Exception as e:
        result['error'] = str(e)

    return result


def find_python_files(root_dir: Path) -> List[Path]:
    """Find all Python files to process."""
    files = []
    for filepath in root_dir.rglob('*.py'):
        if should_process_file(filepath):
            files.append(filepath)
    return files


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Fix datetime and logging patterns (v2 - AST-based)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    parser.add_argument('--path', default='src/company_researcher', help='Path to process')
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

    stats = {
        'datetime_fixed': 0,
        'logging_fixed': 0,
        'files_modified': 0,
        'errors': 0
    }

    for filepath in sorted(files):
        result = process_file(filepath, package_root=root_dir, dry_run=args.dry_run)

        if result['error']:
            print(f"ERROR: {filepath}: {result['error']}")
            stats['errors'] += 1
            continue

        if result['datetime_fixed'] or result['logging_fixed']:
            stats['files_modified'] += 1
            changes = []
            if result['datetime_fixed']:
                changes.append('datetime')
                stats['datetime_fixed'] += 1
            if result['logging_fixed']:
                changes.append('logging')
                stats['logging_fixed'] += 1

            try:
                rel_path = filepath.relative_to(root_dir)
            except ValueError:
                rel_path = filepath

            imports = ', '.join(result['imports_added']) if result['imports_added'] else 'none'
            prefix = result.get('relative_prefix', '?')
            print(f"FIXED: {rel_path} - {', '.join(changes)} (imports: {imports}, prefix: {prefix})")

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


if __name__ == '__main__':
    main()
