#!/usr/bin/env python
"""
Import Validation and Fix Utility.

Consolidated tool for managing Python imports. Combines functionality from:
- validate_imports.py
- fix_agent_imports.py

Usage:
    python -m scripts.utils.imports validate      # Validate all imports
    python -m scripts.utils.imports fix           # Fix relative imports (dry run)
    python -m scripts.utils.imports fix --execute # Actually fix imports
"""

import argparse
import ast
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set

# ============================================================================
# CONFIGURATION
# ============================================================================

SKIP_DIRS: Set[str] = {
    "__pycache__",
    "venv",
    ".venv",
    "node_modules",
    ".git",
    "htmlcov",
    ".pytest_cache",
    ".mypy_cache",
}

# Known modules that need specific import levels
IMPORT_LEVEL_RULES = {
    # Files in agents/core/ need 3 dots to reach company_researcher/
    "agents/core": {
        "modules": ["config", "state", "prompts", "quality", "tools", "memory"],
        "required_level": 3,
    },
    # Files in agents/<subdir>/ need 3 dots
    "agents/financial": {
        "modules": ["config", "state", "prompts", "quality", "tools", "memory"],
        "required_level": 3,
    },
    "agents/market": {
        "modules": ["config", "state", "prompts", "quality", "tools", "memory"],
        "required_level": 3,
    },
    "agents/specialized": {
        "modules": ["config", "state", "prompts", "quality", "tools", "memory"],
        "required_level": 3,
    },
    "agents/research": {
        "modules": ["config", "state", "prompts", "quality", "tools", "memory"],
        "required_level": 3,
    },
    # Files directly in agents/ need 2 dots
    "agents": {
        "modules": ["config", "state", "prompts", "quality", "tools", "memory"],
        "required_level": 2,
    },
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def should_skip(path: Path) -> bool:
    """Check if path should be skipped."""
    return any(part in SKIP_DIRS for part in path.parts)


def find_python_files(root_dir: Path) -> List[Path]:
    """Find all Python files in directory."""
    python_files = []
    for path in root_dir.rglob("*.py"):
        if not should_skip(path):
            python_files.append(path)
    return sorted(python_files)


# ============================================================================
# IMPORT ANALYZER
# ============================================================================


class ImportAnalyzer(ast.NodeVisitor):
    """AST visitor to extract import information."""

    def __init__(self, filepath: Path, project_root: Path):
        self.filepath = filepath
        self.project_root = project_root
        self.imports: List[Dict] = []
        self.errors: List[str] = []

    def visit_Import(self, node):
        """Visit regular import statements."""
        for alias in node.names:
            self.imports.append(
                {
                    "type": "import",
                    "module": alias.name,
                    "asname": alias.asname,
                    "line": node.lineno,
                    "level": 0,
                }
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Visit from...import statements."""
        self.imports.append(
            {
                "type": "from_import",
                "module": node.module,
                "names": [alias.name for alias in node.names],
                "line": node.lineno,
                "level": node.level,
            }
        )
        self.generic_visit(node)


def analyze_file(filepath: Path, project_root: Path) -> Dict:
    """Analyze a single Python file for imports."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(filepath))
        analyzer = ImportAnalyzer(filepath, project_root)
        analyzer.visit(tree)

        return {
            "filepath": filepath,
            "relative_path": filepath.relative_to(project_root),
            "imports": analyzer.imports,
            "errors": analyzer.errors,
            "success": True,
        }
    except SyntaxError as e:
        return {
            "filepath": filepath,
            "relative_path": filepath.relative_to(project_root),
            "imports": [],
            "errors": [f"Syntax error: {e}"],
            "success": False,
        }
    except Exception as e:
        return {
            "filepath": filepath,
            "relative_path": filepath.relative_to(project_root),
            "imports": [],
            "errors": [f"Error: {e}"],
            "success": False,
        }


def validate_import(import_info: Dict, filepath: Path, src_root: Path) -> List[str]:
    """Validate a relative import path."""
    issues = []

    if import_info["type"] != "from_import" or import_info["level"] == 0:
        return issues

    file_str = str(filepath).replace("\\", "/")
    module_name = import_info["module"]

    # Check against rules
    for path_pattern, rule in IMPORT_LEVEL_RULES.items():
        if path_pattern in file_str:
            if module_name in rule["modules"]:
                required = rule["required_level"]
                actual = import_info["level"]
                if actual < required:
                    issues.append(
                        f"Line {import_info['line']}: Import '{module_name}' needs "
                        f"{required} dots ({'.' * required}{module_name}), found {actual}"
                    )
            break

    return issues


# ============================================================================
# IMPORT FIXER
# ============================================================================


class ImportFixer:
    """Fix relative imports in Python files."""

    def __init__(self, project_root: Path, dry_run: bool = True):
        self.project_root = project_root
        self.dry_run = dry_run
        self.fixed_files: List[Path] = []

    def fix_file(self, filepath: Path) -> bool:
        """Fix relative imports in a single file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            original = content
            file_str = str(filepath).replace("\\", "/")

            # Determine required level based on file location
            for path_pattern, rule in IMPORT_LEVEL_RULES.items():
                if path_pattern in file_str:
                    required = rule["required_level"]
                    for module in rule["modules"]:
                        # Fix imports with insufficient dots
                        for level in range(1, required):
                            old_pattern = f"from {'.' * level}{module} import"
                            new_pattern = f"from {'.' * required}{module} import"
                            content = content.replace(old_pattern, new_pattern)
                    break

            if content != original:
                if not self.dry_run:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                self.fixed_files.append(filepath)
                return True

            return False

        except Exception as e:
            print(f"  [ERR] {filepath}: {e}")
            return False

    def fix_directory(self, target_dir: Path):
        """Fix all Python files in directory."""
        python_files = find_python_files(target_dir)

        for filepath in python_files:
            if self.fix_file(filepath):
                rel_path = filepath.relative_to(self.project_root)
                status = "[DRY]" if self.dry_run else "[FIXED]"
                print(f"  {status} {rel_path}")


# ============================================================================
# REPORT GENERATOR
# ============================================================================


def generate_validation_report(results: List[Dict], project_root: Path) -> str:
    """Generate import validation report."""
    lines = []
    lines.append("=" * 80)
    lines.append("IMPORT VALIDATION REPORT")
    lines.append("=" * 80)
    lines.append("")

    total_files = len(results)
    success_files = sum(1 for r in results if r["success"])
    total_imports = sum(len(r["imports"]) for r in results)
    total_issues = sum(len(r["errors"]) for r in results)

    lines.append(f"Total Files: {total_files}")
    lines.append(f"  Successful: {success_files}")
    lines.append(f"  With Errors: {total_files - success_files}")
    lines.append(f"Total Imports: {total_imports}")
    lines.append(f"Total Issues: {total_issues}")
    lines.append("")

    # Files with issues
    files_with_issues = [r for r in results if r["errors"]]
    if files_with_issues:
        lines.append("=" * 80)
        lines.append("FILES WITH ISSUES")
        lines.append("=" * 80)
        lines.append("")

        for result in files_with_issues:
            lines.append(f"[FILE] {result['relative_path']}")
            for error in result["errors"]:
                lines.append(f"  [!] {error}")
            lines.append("")
    else:
        lines.append("[OK] No import issues found!")
        lines.append("")

    # Import statistics
    lines.append("=" * 80)
    lines.append("IMPORT STATISTICS")
    lines.append("=" * 80)
    lines.append("")

    import_stats = defaultdict(int)
    relative_levels = defaultdict(int)

    for result in results:
        for imp in result["imports"]:
            import_stats[imp["type"]] += 1
            if imp["type"] == "from_import" and imp["level"] > 0:
                relative_levels[imp["level"]] += 1

    lines.append("Import Types:")
    for imp_type, count in sorted(import_stats.items()):
        lines.append(f"  {imp_type}: {count}")
    lines.append("")

    if relative_levels:
        lines.append("Relative Import Levels:")
        for level, count in sorted(relative_levels.items()):
            lines.append(f"  {'.' * level} ({level} level): {count}")
        lines.append("")

    # Top imports
    lines.append("=" * 80)
    lines.append("MOST COMMON IMPORTS (Top 15)")
    lines.append("=" * 80)
    lines.append("")

    module_counts = defaultdict(int)
    for result in results:
        for imp in result["imports"]:
            if imp["type"] == "import":
                module_counts[imp["module"]] += 1
            elif imp["type"] == "from_import" and imp["module"]:
                module_counts[imp["module"]] += 1

    for module, count in sorted(module_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
        lines.append(f"  {count:3d}  {module}")
    lines.append("")

    return "\n".join(lines)


# ============================================================================
# CLI COMMANDS
# ============================================================================


def cmd_validate(args):
    """Validate all Python imports."""
    project_root = get_project_root()
    src_root = project_root / "src"

    print("[*] Scanning for Python files...")
    python_files = find_python_files(src_root)
    print(f"[*] Found {len(python_files)} Python files")
    print("")

    results = []
    for i, filepath in enumerate(python_files, 1):
        result = analyze_file(filepath, project_root)

        # Validate relative imports
        if result["success"]:
            for imp in result["imports"]:
                issues = validate_import(imp, filepath, src_root)
                result["errors"].extend(issues)

        results.append(result)

        if i % 20 == 0:
            print(f"  Analyzed {i}/{len(python_files)} files...")

    print("[+] Analysis complete!")
    print("")

    report = generate_validation_report(results, project_root)
    print(report)

    # Save report
    report_path = project_root / "import_validation_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[*] Report saved to: {report_path}")

    # Exit code
    total_issues = sum(len(r["errors"]) for r in results)
    if total_issues:
        print(f"\n[!] Found {total_issues} import issues")
        sys.exit(1)
    else:
        print("\n[+] All imports validated successfully!")
        sys.exit(0)


def cmd_fix(args):
    """Fix relative imports."""
    project_root = get_project_root()
    dry_run = not args.execute

    print("[*] Fixing relative imports...")
    if dry_run:
        print("    (DRY RUN - no changes will be made)")
    print("")

    # Target the agents directory specifically
    src_root = project_root / "src"
    agents_dir = src_root / "company_researcher" / "agents"

    if not agents_dir.exists():
        print(f"[!] Agents directory not found: {agents_dir}")
        return

    fixer = ImportFixer(project_root, dry_run=dry_run)
    fixer.fix_directory(agents_dir)

    print("")
    print("=" * 60)
    if fixer.fixed_files:
        print(f"[+] {'Would fix' if dry_run else 'Fixed'} {len(fixer.fixed_files)} files")
    else:
        print("[*] No files needed fixing")

    if dry_run and fixer.fixed_files:
        print("\n[*] Run with --execute to apply fixes")


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Main entry point."""
    # UTF-8 for Windows
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Import Validation and Fix Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scripts.utils.imports validate         # Validate all imports
  python -m scripts.utils.imports fix              # Fix imports (dry run)
  python -m scripts.utils.imports fix --execute    # Actually fix imports
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate all Python imports")
    validate_parser.set_defaults(func=cmd_validate)

    # Fix command
    fix_parser = subparsers.add_parser("fix", help="Fix relative imports")
    fix_parser.add_argument(
        "--execute", action="store_true", help="Actually fix imports (default is dry run)"
    )
    fix_parser.set_defaults(func=cmd_fix)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
