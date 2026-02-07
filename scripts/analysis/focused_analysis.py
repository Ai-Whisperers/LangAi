#!/usr/bin/env python3
"""
Focused analysis on src/, tests/, scripts/ only
"""
import ast
import json
import os
import sys
from collections import defaultdict
from pathlib import Path


class FocusedAnalyzer:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.issues = []
        self.issue_count = 0
        self.all_modules = set()

    def add_issue(self, file_path, line_number, error_type, description, severity):
        """Add an issue to the list"""
        self.issue_count += 1
        rel_path = (
            str(file_path.relative_to(self.root_path))
            if isinstance(file_path, Path)
            else str(file_path)
        )
        self.issues.append(
            {
                "id": self.issue_count,
                "file": rel_path,
                "line": line_number,
                "type": error_type,
                "description": description,
                "severity": severity,
            }
        )

    def scan_all_modules(self):
        """Build a set of all available modules"""
        for dir_name in ["src", "tests", "scripts"]:
            dir_path = self.root_path / dir_name
            if not dir_path.exists():
                continue

            for py_file in dir_path.rglob("*.py"):
                # Skip external repos
                if "External repos" in str(py_file):
                    continue

                # Calculate module path
                try:
                    rel_parts = py_file.relative_to(dir_path).parts

                    if rel_parts[-1] == "__init__.py":
                        module_path = ".".join(rel_parts[:-1])
                    else:
                        module_path = ".".join(rel_parts[:-1] + (rel_parts[-1][:-3],))

                    if module_path:
                        self.all_modules.add(module_path)

                        # Also add parent modules
                        parts = module_path.split(".")
                        for i in range(1, len(parts)):
                            self.all_modules.add(".".join(parts[:i]))
                except:
                    pass

    def check_file(self, file_path):
        """Check a single file for issues"""
        # Check syntax
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)
        except SyntaxError as e:
            self.add_issue(
                file_path, e.lineno or 0, "SYNTAX_ERROR", f"Syntax error: {e.msg}", "CRITICAL"
            )
            return
        except Exception as e:
            self.add_issue(file_path, 0, "FILE_READ_ERROR", f"Cannot read file: {str(e)}", "HIGH")
            return

        # Check imports
        lines = content.split("\n")
        imports_seen = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name

                    # Check for duplicate
                    key = f"import {module}"
                    if key in imports_seen:
                        self.add_issue(
                            file_path,
                            node.lineno,
                            "DUPLICATE_IMPORT",
                            f"Duplicate import: {module} (first imported at line {imports_seen[key]})",
                            "LOW",
                        )
                    imports_seen[key] = node.lineno

                    # Check if module exists (for local modules)
                    base_module = module.split(".")[0]
                    if base_module in ["company_researcher", "src", "tests", "scripts"]:
                        # Check if this module exists
                        clean_module = module.replace("src.", "")
                        if clean_module not in self.all_modules:
                            # Check if any module ends with this
                            found = any(m.endswith(clean_module) for m in self.all_modules)
                            if not found:
                                self.add_issue(
                                    file_path,
                                    node.lineno,
                                    "MODULE_NOT_FOUND",
                                    f"Cannot find module: {module}",
                                    "HIGH",
                                )

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                level = node.level

                # Check for duplicate
                key = f"from {module} import ..."
                if key in imports_seen and level == 0:
                    self.add_issue(
                        file_path,
                        node.lineno,
                        "DUPLICATE_IMPORT",
                        f"Duplicate from import: {module} (first imported at line {imports_seen[key]})",
                        "LOW",
                    )
                imports_seen[key] = node.lineno

                # Check wildcard imports
                for alias in node.names:
                    if alias.name == "*":
                        self.add_issue(
                            file_path,
                            node.lineno,
                            "WILDCARD_IMPORT",
                            f"Wildcard import from {module} (avoid using *)",
                            "MEDIUM",
                        )

                # Check if module exists
                if level == 0 and module:
                    base_module = module.split(".")[0]
                    if base_module in ["company_researcher", "src", "tests", "scripts"]:
                        clean_module = module.replace("src.", "")
                        if clean_module not in self.all_modules:
                            found = any(m.endswith(clean_module) for m in self.all_modules)
                            if not found:
                                self.add_issue(
                                    file_path,
                                    node.lineno,
                                    "MODULE_NOT_FOUND",
                                    f"Cannot find module: {module}",
                                    "HIGH",
                                )

                # Check relative import level
                if level > 0:
                    try:
                        # Calculate current package depth
                        current_package = file_path.parent
                        depth = 0
                        for part in file_path.parts:
                            if part in ["src", "tests", "scripts"]:
                                break
                        else:
                            depth = 0

                        if level > 3:  # Arbitrary limit
                            self.add_issue(
                                file_path,
                                node.lineno,
                                "EXCESSIVE_RELATIVE_IMPORT",
                                f"Relative import level {level} may be excessive",
                                "MEDIUM",
                            )
                    except:
                        pass

    def check_missing_init(self):
        """Check for missing __init__.py files"""
        for dir_name in ["src", "tests", "scripts"]:
            dir_path = self.root_path / dir_name
            if not dir_path.exists():
                continue

            for subdir in dir_path.rglob("*"):
                if not subdir.is_dir():
                    continue

                # Skip certain directories
                if any(
                    skip in str(subdir)
                    for skip in ["__pycache__", ".git", "External repos", ".venv", "venv"]
                ):
                    continue

                # Check if contains Python files
                py_files = list(subdir.glob("*.py"))
                if py_files:
                    init_file = subdir / "__init__.py"
                    if not init_file.exists():
                        self.add_issue(
                            subdir,
                            0,
                            "MISSING_INIT_FILE",
                            f"Package directory missing __init__.py",
                            "MEDIUM",
                        )

    def analyze(self):
        """Run analysis"""
        print("Scanning for all modules...")
        self.scan_all_modules()
        print(f"Found {len(self.all_modules)} modules")

        print("\nChecking for missing __init__.py files...")
        self.check_missing_init()

        print("\nAnalyzing files...")
        count = 0
        for dir_name in ["src", "tests", "scripts"]:
            dir_path = self.root_path / dir_name
            if not dir_path.exists():
                continue

            for py_file in dir_path.rglob("*.py"):
                # Skip external repos
                if "External repos" in str(py_file):
                    continue

                count += 1
                if count % 20 == 0:
                    print(f"  Analyzed {count} files...")

                self.check_file(py_file)

        print(f"\nAnalyzed {count} files total")
        print(f"Found {len(self.issues)} issues\n")

    def generate_report(self):
        """Generate report"""
        by_severity = defaultdict(list)
        by_type = defaultdict(list)

        for issue in self.issues:
            by_severity[issue["severity"]].append(issue)
            by_type[issue["type"]].append(issue)

        print(f"{'='*80}")
        print(f"CODEBASE ANALYSIS REPORT")
        print(f"{'='*80}\n")
        print(f"Total Issues: {len(self.issues)}\n")

        print("BY SEVERITY:")
        print("-" * 40)
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            count = len(by_severity[severity])
            if count > 0:
                print(f"  {severity}: {count}")

        print(f"\nBY TYPE:")
        print("-" * 40)
        for error_type, issues in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True)[
            :15
        ]:
            print(f"  {error_type}: {len(issues)}")

        # Show all issues
        print(f"\n{'='*80}")
        print("ALL ISSUES")
        print(f"{'='*80}\n")

        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            issues = by_severity[severity]
            if issues:
                print(f"\n{severity} SEVERITY ({len(issues)} issues)")
                print(f"{'-'*80}")

                for issue in issues:
                    print(f"\n#{issue['id']} {issue['type']}")
                    print(f"  File: {issue['file']}")
                    print(f"  Line: {issue['line']}")
                    print(f"  Description: {issue['description']}")

        # Save JSON
        output_file = self.root_path / "focused_analysis_report.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "total_issues": len(self.issues),
                    "by_severity": {k: len(v) for k, v in by_severity.items()},
                    "by_type": {k: len(v) for k, v in by_type.items()},
                    "issues": self.issues,
                },
                f,
                indent=2,
            )

        print(f"\n\nJSON report saved to: {output_file}")


if __name__ == "__main__":
    root = Path(__file__).parent
    analyzer = FocusedAnalyzer(root)
    analyzer.analyze()
    analyzer.generate_report()
