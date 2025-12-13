"""
Bulk Pattern Replacement Script for os.getenv() → get_config().

This script replaces:
- os.getenv("KEY") → get_config("KEY")
- os.getenv("KEY", "default") → get_config("KEY", default="default")
- os.environ.get("KEY") → get_config("KEY")
- os.environ.get("KEY", "default") → get_config("KEY", default="default")

Uses AST to properly determine where to insert imports.
Uses RELATIVE imports based on file depth within the package.

Files in config layer (utils/config.py, ai/config.py, production/config.py) are excluded
as they legitimately need direct os.getenv() access.

Usage:
    python scripts/fix_getenv_patterns.py --dry-run  # Preview changes
    python scripts/fix_getenv_patterns.py            # Apply changes
"""

import ast
import os
import re
from pathlib import Path
from typing import Set, Tuple, List, Optional
import argparse


# Package root for calculating relative imports
PACKAGE_NAME = "company_researcher"

# Files to exclude from modification (config layer files that need os.getenv)
EXCLUDE_FILES = {
    "fix_getenv_patterns.py",
    "fix_patterns.py",
    "fix_patterns_v2.py",
}

# Specific paths to exclude (config layer - these legitimately use os.getenv)
EXCLUDE_PATHS = {
    "utils/config.py",
    "utils\\config.py",
    "utils/__init__.py",
    "utils\\__init__.py",
    "ai/config.py",
    "ai\\config.py",
    "production/config.py",
    "production\\config.py",
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


def get_relative_import_prefix(filepath: Path, package_root: Path) -> Optional[str]:
    """
    Calculate the relative import prefix based on file location within the package.

    Examples:
        - config.py (at package root) → '.'
        - agents/core/researcher.py (2 levels deep) → '...'
        - llm/client.py (1 level deep) → '..'
    """
    try:
        relative_path = filepath.relative_to(package_root)
        depth = len(relative_path.parts) - 1

        if depth == 0:
            return '.'
        else:
            return '.' * (depth + 1)
    except ValueError:
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
    Returns the line number (0-indexed) after the last import.
    """
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return 0

    last_import_line = 0
    first_non_import_line = None

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if hasattr(node, 'lineno'):
                last_import_line = max(last_import_line, node.lineno)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
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

    patterns = [
        (r'from\s+(\.+)utils\s+import\s+\(([^)]+)\)', 'relative'),
        (r'from\s+(\.+)utils\s+import\s+([^\n]+)', 'relative'),
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
                if style == 'relative':
                    imports_str = match.group(2)
                else:
                    imports_str = match.group(1)

                for name in imports_str.split(','):
                    name = name.strip().strip('(').strip(')')
                    if name and not name.startswith('#'):
                        name = name.split(' as ')[0].strip()
                        if name:
                            existing.add(name)
                if import_line is None:
                    import_line = i
                    import_style = style

    return existing, import_line, import_style


def fix_getenv_patterns(content: str, lines: List[str]) -> Tuple[List[str], bool, Set[str]]:
    """
    Replace os.getenv() and os.environ.get() with get_config().

    Handles:
    - os.getenv("KEY") → get_config("KEY")
    - os.getenv("KEY", "default") → get_config("KEY", default="default")
    - os.getenv("KEY", default) → get_config("KEY", default=default)
    - os.environ.get("KEY") → get_config("KEY")
    - os.environ.get("KEY", "default") → get_config("KEY", default="default")
    """
    changed = False
    imports_needed = set()

    # Pattern for os.getenv with optional default
    # Matches: os.getenv("KEY") or os.getenv("KEY", "default") or os.getenv("KEY", some_var)
    getenv_pattern = r'os\.getenv\(\s*(["\'][^"\']+["\'])\s*(?:,\s*([^)]+))?\)'

    # Pattern for os.environ.get with optional default
    environ_get_pattern = r'os\.environ\.get\(\s*(["\'][^"\']+["\'])\s*(?:,\s*([^)]+))?\)'

    for i, line in enumerate(lines):
        new_line = line

        # Replace os.getenv patterns
        def replace_getenv(match):
            key = match.group(1)
            default = match.group(2)
            if default:
                default = default.strip()
                # If default is a string literal, keep it as is
                # If it's a variable or expression, wrap with default=
                return f'get_config({key}, default={default})'
            else:
                return f'get_config({key})'

        new_line = re.sub(getenv_pattern, replace_getenv, new_line)

        # Replace os.environ.get patterns
        new_line = re.sub(environ_get_pattern, replace_getenv, new_line)

        if new_line != line:
            imports_needed.add('get_config')
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
    """Add required imports at the correct position using relative imports."""
    new_imports = imports_needed - existing_imports

    if not new_imports:
        return lines

    imports_str = ', '.join(sorted(new_imports))
    if relative_prefix:
        new_import_line = f'from {relative_prefix}utils import {imports_str}'
    else:
        new_import_line = f'from company_researcher.utils import {imports_str}'

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
    """Update an existing import line to include new imports."""
    new_imports = imports_needed - existing_imports
    if not new_imports:
        return lines

    all_imports = existing_imports | new_imports
    imports_str = ', '.join(sorted(all_imports))

    line = lines[import_line]

    if import_style == 'relative':
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
        if relative_prefix:
            new_line = f'from {relative_prefix}utils import {imports_str}'
        else:
            new_line = f'from company_researcher.utils import {imports_str}'

    lines[import_line] = new_line
    return lines


def remove_unused_os_import(lines: List[str]) -> List[str]:
    """
    Remove 'import os' if os is no longer used after our replacements.
    """
    import_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == 'import os':
            import_idx = i
            break

    if import_idx is None:
        return lines

    # Check if 'os.' is still used elsewhere
    content_without_import = '\n'.join(lines[:import_idx] + lines[import_idx+1:])
    if not re.search(r'\bos\.', content_without_import):
        # 'os' is no longer used, remove the import
        lines.pop(import_idx)

    return lines


def process_file(filepath: Path, package_root: Path, dry_run: bool = False) -> dict:
    """Process a single file."""
    result = {
        'file': str(filepath),
        'getenv_fixed': False,
        'imports_added': set(),
        'relative_prefix': None,
        'error': None
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skip files without os.getenv or os.environ.get
        if 'os.getenv' not in content and 'os.environ.get' not in content:
            return result

        original_content = content
        lines = content.split('\n')

        relative_prefix = get_relative_import_prefix(filepath, package_root)
        result['relative_prefix'] = relative_prefix

        existing_imports, existing_import_line, import_style = check_existing_imports(content)

        # Fix getenv patterns
        lines, getenv_changed, getenv_imports = fix_getenv_patterns(content, lines)
        result['getenv_fixed'] = getenv_changed

        # Add/update imports if needed
        if getenv_imports:
            if existing_import_line is not None:
                lines = update_existing_import(
                    lines, existing_import_line, getenv_imports, existing_imports,
                    relative_prefix=relative_prefix, import_style=import_style
                )
            else:
                insert_line = get_import_insert_line(original_content)
                lines = add_imports_to_lines(
                    lines, insert_line, getenv_imports, existing_imports,
                    relative_prefix=relative_prefix
                )

            result['imports_added'] = getenv_imports - existing_imports

        # Remove unused os import
        if getenv_changed:
            lines = remove_unused_os_import(lines)

        new_content = '\n'.join(lines)

        if new_content != original_content and not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

    except Exception as e:
        result['error'] = str(e)

    return result


def main():
    parser = argparse.ArgumentParser(description='Fix os.getenv patterns')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    args = parser.parse_args()

    # Find package root
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent / "src" / PACKAGE_NAME

    if not root_dir.exists():
        print(f"ERROR: Package root not found: {root_dir}")
        return

    print(f"Package root: {root_dir}")
    print(f"Dry run: {args.dry_run}")
    print("=" * 60)

    # Find all Python files
    files = [f for f in root_dir.rglob("*.py") if should_process_file(f)]
    print(f"Found {len(files)} Python files to process")
    print("=" * 60)

    stats = {
        'getenv_fixed': 0,
        'files_modified': 0,
        'errors': 0
    }

    for filepath in sorted(files):
        result = process_file(filepath, package_root=root_dir, dry_run=args.dry_run)

        if result['error']:
            print(f"ERROR: {filepath}: {result['error']}")
            stats['errors'] += 1
            continue

        if result['getenv_fixed']:
            stats['files_modified'] += 1
            stats['getenv_fixed'] += 1

            try:
                rel_path = filepath.relative_to(root_dir)
            except ValueError:
                rel_path = filepath

            imports = ', '.join(result['imports_added']) if result['imports_added'] else 'none (already imported)'
            prefix = result.get('relative_prefix', '?')
            print(f"FIXED: {rel_path} (imports: {imports}, prefix: {prefix})")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files processed: {len(files)}")
    print(f"Files modified: {stats['files_modified']}")
    print(f"os.getenv patterns fixed: {stats['getenv_fixed']}")
    print(f"Errors: {stats['errors']}")

    if args.dry_run:
        print()
        print("This was a dry run. Run without --dry-run to apply changes.")


if __name__ == '__main__':
    main()
