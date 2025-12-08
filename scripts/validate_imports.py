#!/usr/bin/env python
"""
Import Path Validation Script

Analyzes all Python files in the project and validates:
1. All import statements
2. Relative import paths
3. Module availability
4. Common import issues

Usage:
    python scripts/validate_imports.py
    python scripts/validate_imports.py --fix-dry-run
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import defaultdict


class ImportAnalyzer(ast.NodeVisitor):
    """AST visitor to extract import information."""

    def __init__(self, filepath: Path, project_root: Path):
        self.filepath = filepath
        self.project_root = project_root
        self.imports = []
        self.errors = []

    def visit_Import(self, node):
        """Visit regular import statements."""
        for alias in node.names:
            self.imports.append({
                'type': 'import',
                'module': alias.name,
                'asname': alias.asname,
                'line': node.lineno,
                'level': 0
            })
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Visit from...import statements."""
        self.imports.append({
            'type': 'from_import',
            'module': node.module,
            'names': [alias.name for alias in node.names],
            'line': node.lineno,
            'level': node.level  # Number of leading dots
        })
        self.generic_visit(node)


def analyze_file(filepath: Path, project_root: Path) -> Dict:
    """Analyze a single Python file for imports."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content, filename=str(filepath))
        analyzer = ImportAnalyzer(filepath, project_root)
        analyzer.visit(tree)

        return {
            'filepath': filepath,
            'relative_path': filepath.relative_to(project_root),
            'imports': analyzer.imports,
            'errors': analyzer.errors,
            'success': True
        }
    except SyntaxError as e:
        return {
            'filepath': filepath,
            'relative_path': filepath.relative_to(project_root),
            'imports': [],
            'errors': [f"Syntax error: {e}"],
            'success': False
        }
    except Exception as e:
        return {
            'filepath': filepath,
            'relative_path': filepath.relative_to(project_root),
            'imports': [],
            'errors': [f"Error: {e}"],
            'success': False
        }


def get_package_depth(filepath: Path, src_root: Path) -> int:
    """Calculate package depth (how many levels deep from src/)."""
    try:
        relative = filepath.relative_to(src_root)
        return len(relative.parts) - 1  # -1 for the file itself
    except ValueError:
        return 0


def validate_relative_import(import_info: Dict, filepath: Path, src_root: Path) -> List[str]:
    """Validate a relative import path."""
    issues = []

    if import_info['type'] != 'from_import':
        return issues

    level = import_info['level']
    if level == 0:
        return issues  # Absolute import

    # Calculate expected levels based on file location
    package_depth = get_package_depth(filepath, src_root)

    # Get the directory structure
    current_dir = filepath.parent
    module_parts = []

    # Try to determine the target module
    for _ in range(level):
        if current_dir == src_root:
            break
        current_dir = current_dir.parent

    module_name = import_info['module']

    # Check if we're in agents/core/ trying to import from company_researcher/
    file_str = str(filepath)
    if 'agents/core' in file_str or 'agents\\core' in file_str:
        # Files in agents/core/ need 3 dots to reach company_researcher/
        if module_name in ['config', 'state', 'prompts'] and level < 3:
            issues.append(
                f"Line {import_info['line']}: "
                f"Import '{module_name}' from agents/core/ needs 3 dots (...{module_name}), "
                f"found {level} dot(s)"
            )
    elif 'agents/' in file_str or 'agents\\' in file_str:
        # Files directly in agents/ need 2 dots to reach company_researcher/
        if module_name in ['config', 'state', 'prompts'] and level < 2:
            issues.append(
                f"Line {import_info['line']}: "
                f"Import '{module_name}' from agents/ needs 2 dots (..{module_name}), "
                f"found {level} dot(s)"
            )

    return issues


def find_python_files(root_dir: Path, exclude_dirs: Set[str] = None) -> List[Path]:
    """Find all Python files in directory."""
    if exclude_dirs is None:
        exclude_dirs = {'__pycache__', 'venv', '.venv', 'node_modules', '.git', 'htmlcov', '.pytest_cache'}

    python_files = []
    for path in root_dir.rglob('*.py'):
        # Check if any parent is in exclude_dirs
        if any(part in exclude_dirs for part in path.parts):
            continue
        python_files.append(path)

    return sorted(python_files)


def generate_report(results: List[Dict], project_root: Path) -> str:
    """Generate a formatted validation report."""
    lines = []
    lines.append("=" * 80)
    lines.append("IMPORT VALIDATION REPORT")
    lines.append("=" * 80)
    lines.append("")

    total_files = len(results)
    success_files = sum(1 for r in results if r['success'])
    error_files = total_files - success_files

    total_imports = sum(len(r['imports']) for r in results)
    total_issues = sum(len(r['errors']) for r in results)

    # Summary
    lines.append(f"Total Files Analyzed: {total_files}")
    lines.append(f"  ✓ Successful: {success_files}")
    lines.append(f"  ✗ Errors: {error_files}")
    lines.append(f"Total Imports: {total_imports}")
    lines.append(f"Total Issues Found: {total_issues}")
    lines.append("")

    # Files with issues
    files_with_issues = [r for r in results if r['errors'] or not r['success']]

    if files_with_issues:
        lines.append("=" * 80)
        lines.append("FILES WITH ISSUES")
        lines.append("=" * 80)
        lines.append("")

        for result in files_with_issues:
            lines.append(f"[FILE] {result['relative_path']}")
            lines.append(f"   Full path: {result['filepath']}")

            if result['errors']:
                for error in result['errors']:
                    lines.append(f"   [ERROR] {error}")

            lines.append("")
    else:
        lines.append("[OK] No import issues found!")
        lines.append("")

    # Import statistics by type
    lines.append("=" * 80)
    lines.append("IMPORT STATISTICS")
    lines.append("=" * 80)
    lines.append("")

    import_stats = defaultdict(int)
    relative_import_levels = defaultdict(int)

    for result in results:
        for imp in result['imports']:
            import_stats[imp['type']] += 1
            if imp['type'] == 'from_import' and imp['level'] > 0:
                relative_import_levels[imp['level']] += 1

    lines.append("Import Types:")
    for imp_type, count in sorted(import_stats.items()):
        lines.append(f"  - {imp_type}: {count}")
    lines.append("")

    if relative_import_levels:
        lines.append("Relative Import Levels:")
        for level, count in sorted(relative_import_levels.items()):
            dots = '.' * level
            lines.append(f"  - {dots} ({level} level): {count}")
        lines.append("")

    # Most common imports
    lines.append("=" * 80)
    lines.append("MOST COMMON IMPORTS (Top 15)")
    lines.append("=" * 80)
    lines.append("")

    module_counts = defaultdict(int)
    for result in results:
        for imp in result['imports']:
            if imp['type'] == 'import':
                module_counts[imp['module']] += 1
            elif imp['type'] == 'from_import' and imp['module']:
                module_counts[imp['module']] += 1

    for module, count in sorted(module_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
        lines.append(f"  {count:3d}  {module}")
    lines.append("")

    # Files by directory
    lines.append("=" * 80)
    lines.append("FILES BY DIRECTORY")
    lines.append("=" * 80)
    lines.append("")

    dir_counts = defaultdict(list)
    for result in results:
        dir_path = result['relative_path'].parent
        dir_counts[dir_path].append(result['relative_path'].name)

    for dir_path in sorted(dir_counts.keys()):
        files = dir_counts[dir_path]
        lines.append(f"[DIR] {dir_path}/ ({len(files)} files)")
        for filename in sorted(files):
            lines.append(f"   - {filename}")
        lines.append("")

    return "\n".join(lines)


def main():
    """Main validation function."""
    # Set UTF-8 encoding for Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    project_root = Path(__file__).parent.parent
    src_root = project_root / 'src'

    print("[*] Scanning for Python files...")
    python_files = find_python_files(src_root)

    print(f"[*] Found {len(python_files)} Python files")
    print("")

    results = []
    validation_issues = []

    for filepath in python_files:
        result = analyze_file(filepath, project_root)
        results.append(result)

        # Validate relative imports
        if result['success']:
            for imp in result['imports']:
                issues = validate_relative_import(imp, filepath, src_root)
                if issues:
                    result['errors'].extend(issues)
                    validation_issues.extend(issues)

        # Progress indicator
        if len(results) % 10 == 0:
            print(f"  Analyzed {len(results)}/{len(python_files)} files...")

    print(f"[+] Analysis complete!")
    print("")

    # Generate and print report
    report = generate_report(results, project_root)
    print(report)

    # Save report to file
    report_path = project_root / 'import_validation_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print("=" * 80)
    print(f"[*] Full report saved to: {report_path}")
    print("=" * 80)
    print("")

    # Exit with error code if issues found
    if validation_issues:
        print(f"[!] Found {len(validation_issues)} import validation issues")
        sys.exit(1)
    else:
        print("[+] All imports validated successfully!")
        sys.exit(0)


if __name__ == '__main__':
    main()
