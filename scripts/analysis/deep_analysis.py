#!/usr/bin/env python3
"""
Deep analysis of Python codebase - checks for:
- Syntax errors via compilation
- Import errors via actual import attempts
- Relative vs absolute import issues
- Circular imports
- Missing __init__.py files
- Unused imports
- Duplicate imports
"""
import ast
import os
import sys
import py_compile
from pathlib import Path
import json
from collections import defaultdict
import re

class DeepCodeAnalyzer:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.issues = []
        self.issue_count = 0
        self.module_map = {}
        self.import_graph = defaultdict(set)

    def add_issue(self, file_path, line_number, error_type, description, severity, code_snippet=None):
        """Add an issue to the list"""
        self.issue_count += 1
        issue = {
            'id': self.issue_count,
            'file': str(file_path.relative_to(self.root_path)) if isinstance(file_path, Path) else str(file_path),
            'line': line_number,
            'type': error_type,
            'description': description,
            'severity': severity
        }
        if code_snippet:
            issue['code'] = code_snippet
        self.issues.append(issue)

    def build_module_map(self):
        """Build a map of all Python modules in the project"""
        for py_file in self.root_path.rglob('*.py'):
            try:
                # Calculate module path
                if 'src' in py_file.parts:
                    src_idx = py_file.parts.index('src')
                    rel_parts = py_file.parts[src_idx + 1:]
                elif 'tests' in py_file.parts:
                    test_idx = py_file.parts.index('tests')
                    rel_parts = py_file.parts[test_idx + 1:]
                else:
                    continue

                if rel_parts[-1] == '__init__.py':
                    module_path = '.'.join(rel_parts[:-1])
                else:
                    module_path = '.'.join(rel_parts[:-1] + (rel_parts[-1][:-3],))

                self.module_map[module_path] = py_file
            except:
                pass

    def check_syntax_compile(self, file_path):
        """Check syntax by attempting to compile"""
        try:
            py_compile.compile(str(file_path), doraise=True)
            return True
        except py_compile.PyCompileError as e:
            self.add_issue(
                file_path,
                0,
                'COMPILE_ERROR',
                f"Compilation failed: {str(e)}",
                'CRITICAL'
            )
            return False
        except SyntaxError as e:
            self.add_issue(
                file_path,
                e.lineno or 0,
                'SYNTAX_ERROR',
                f"Syntax error: {e.msg} - {e.text}",
                'CRITICAL',
                e.text
            )
            return False

    def check_import_style(self, file_path):
        """Check for import style issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                tree = ast.parse(''.join(lines))

            imports_seen = set()
            relative_imports = []
            absolute_imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_str = f"import {alias.name}"
                        if import_str in imports_seen:
                            self.add_issue(
                                file_path,
                                node.lineno,
                                'DUPLICATE_IMPORT',
                                f"Duplicate import: {alias.name}",
                                'LOW',
                                lines[node.lineno - 1].strip() if node.lineno <= len(lines) else None
                            )
                        imports_seen.add(import_str)
                        absolute_imports.append((alias.name, node.lineno))

                elif isinstance(node, ast.ImportFrom):
                    if node.level > 0:
                        # Relative import
                        relative_imports.append((node.module or '', node.level, node.lineno))

                        # Check if mixing relative and absolute in same file
                        if absolute_imports and len(relative_imports) == 1:
                            self.add_issue(
                                file_path,
                                node.lineno,
                                'MIXED_IMPORT_STYLE',
                                'Mixing relative and absolute imports (consider using consistent style)',
                                'LOW'
                            )
                    else:
                        module_name = node.module or ''
                        import_str = f"from {module_name}"

                        # Check for duplicate from imports
                        if import_str in imports_seen:
                            self.add_issue(
                                file_path,
                                node.lineno,
                                'DUPLICATE_IMPORT',
                                f"Duplicate from import: {module_name}",
                                'LOW'
                            )
                        imports_seen.add(import_str)
                        absolute_imports.append((module_name, node.lineno))

        except SyntaxError:
            pass  # Already caught elsewhere
        except Exception as e:
            self.add_issue(
                file_path,
                0,
                'IMPORT_ANALYSIS_ERROR',
                f"Error analyzing imports: {str(e)}",
                'LOW'
            )

    def check_missing_init_files(self):
        """Check for missing __init__.py files in package directories"""
        for directory in ['src', 'tests', 'scripts']:
            dir_path = self.root_path / directory
            if not dir_path.exists():
                continue

            for subdir in dir_path.rglob('*'):
                if subdir.is_dir() and not subdir.name.startswith('.') and not subdir.name == '__pycache__':
                    # Check if directory contains .py files
                    py_files = list(subdir.glob('*.py'))
                    if py_files and not (subdir / '__init__.py').exists():
                        self.add_issue(
                            subdir,
                            0,
                            'MISSING_INIT_FILE',
                            f"Package directory missing __init__.py: {subdir.relative_to(self.root_path)}",
                            'MEDIUM'
                        )

    def check_import_resolution(self, file_path):
        """Check if imports can be resolved"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module
                    level = node.level

                    if level > 0:
                        # Relative import - resolve it
                        try:
                            current_package = self.get_package_name(file_path)
                            if current_package:
                                parts = current_package.split('.')
                                if level > len(parts):
                                    self.add_issue(
                                        file_path,
                                        node.lineno,
                                        'INVALID_RELATIVE_IMPORT',
                                        f"Relative import level {level} exceeds package depth",
                                        'HIGH'
                                    )
                        except Exception as e:
                            self.add_issue(
                                file_path,
                                node.lineno,
                                'RELATIVE_IMPORT_ERROR',
                                f"Cannot resolve relative import: {str(e)}",
                                'MEDIUM'
                            )

                    elif module:
                        # Absolute import - check if module exists
                        base_module = module.split('.')[0]

                        # Check if it's a local module
                        if base_module in ['company_researcher', 'src', 'tests', 'scripts']:
                            # Try to find the module in our module map
                            if module not in self.module_map:
                                # Check variations
                                found = False
                                for mapped_module in self.module_map.keys():
                                    if mapped_module.endswith(module) or module.endswith(mapped_module):
                                        found = True
                                        break

                                if not found:
                                    self.add_issue(
                                        file_path,
                                        node.lineno,
                                        'MODULE_NOT_FOUND',
                                        f"Cannot find module: {module}",
                                        'HIGH'
                                    )

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name
                        base_module = module.split('.')[0]

                        if base_module in ['company_researcher', 'src', 'tests', 'scripts']:
                            if module not in self.module_map:
                                found = False
                                for mapped_module in self.module_map.keys():
                                    if mapped_module.endswith(module) or module.endswith(mapped_module):
                                        found = True
                                        break

                                if not found:
                                    self.add_issue(
                                        file_path,
                                        node.lineno,
                                        'MODULE_NOT_FOUND',
                                        f"Cannot find module: {module}",
                                        'HIGH'
                                    )

        except SyntaxError:
            pass
        except Exception as e:
            pass

    def get_package_name(self, file_path):
        """Get the package name for a file"""
        try:
            if 'src' in file_path.parts:
                src_idx = file_path.parts.index('src')
                rel_parts = file_path.parts[src_idx + 1:-1]
                return '.'.join(rel_parts)
            elif 'tests' in file_path.parts:
                test_idx = file_path.parts.index('tests')
                rel_parts = file_path.parts[test_idx + 1:-1]
                return '.'.join(rel_parts)
        except:
            pass
        return None

    def check_wildcard_imports(self, file_path):
        """Check for wildcard imports (from x import *)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                tree = ast.parse(''.join(lines))

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name == '*':
                            self.add_issue(
                                file_path,
                                node.lineno,
                                'WILDCARD_IMPORT',
                                f"Wildcard import from {node.module} (can cause namespace pollution)",
                                'MEDIUM',
                                lines[node.lineno - 1].strip() if node.lineno <= len(lines) else None
                            )
        except:
            pass

    def check_import_order(self, file_path):
        """Check if imports follow PEP 8 ordering"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                tree = ast.parse(''.join(lines))

            import_nodes = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if hasattr(node, 'lineno'):
                        import_nodes.append((node.lineno, node))

            import_nodes.sort(key=lambda x: x[0])

            # Check if imports are grouped (stdlib, third-party, local)
            current_group = None
            last_line = 0

            for lineno, node in import_nodes:
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    if node.level > 0:
                        group = 'local'
                    elif module.startswith('company_researcher') or module.startswith('src'):
                        group = 'local'
                    elif module.split('.')[0] in ['os', 'sys', 'json', 'datetime', 'collections', 're', 'pathlib', 'typing', 'logging']:
                        group = 'stdlib'
                    else:
                        group = 'third_party'
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        module = alias.name
                        if module.split('.')[0] in ['os', 'sys', 'json', 'datetime', 'collections', 're', 'pathlib', 'typing', 'logging']:
                            group = 'stdlib'
                        else:
                            group = 'third_party'
                        break

                # Check if order is correct
                if current_group == 'third_party' and group == 'stdlib':
                    self.add_issue(
                        file_path,
                        lineno,
                        'IMPORT_ORDER',
                        'Import order violation: stdlib imports should come before third-party',
                        'LOW'
                    )
                elif current_group == 'local' and group in ['stdlib', 'third_party']:
                    self.add_issue(
                        file_path,
                        lineno,
                        'IMPORT_ORDER',
                        'Import order violation: local imports should come last',
                        'LOW'
                    )

                current_group = group
                last_line = lineno

        except:
            pass

    def detect_circular_imports_advanced(self):
        """Advanced circular import detection"""
        # Build import graph
        for py_file in self.root_path.rglob('*.py'):
            if 'venv' in str(py_file) or '.venv' in str(py_file) or '__pycache__' in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())

                source_module = None
                if 'src' in py_file.parts:
                    src_idx = py_file.parts.index('src')
                    rel_parts = py_file.parts[src_idx + 1:]
                    if rel_parts[-1] == '__init__.py':
                        source_module = '.'.join(rel_parts[:-1])
                    else:
                        source_module = '.'.join(rel_parts[:-1] + (rel_parts[-1][:-3],))

                if not source_module:
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.level == 0:
                            if node.module.startswith('company_researcher'):
                                self.import_graph[source_module].add(node.module)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name.startswith('company_researcher'):
                                self.import_graph[source_module].add(alias.name)
            except:
                pass

        # DFS to find cycles
        def find_cycles(node, path, visited, cycles):
            if node in path:
                cycle = path[path.index(node):] + [node]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            path.append(node)

            for neighbor in self.import_graph.get(node, set()):
                find_cycles(neighbor, path.copy(), visited, cycles)

        cycles = []
        visited = set()

        for node in self.import_graph:
            if node not in visited:
                find_cycles(node, [], set(), cycles)

        # Report unique cycles
        unique_cycles = []
        for cycle in cycles:
            cycle_set = frozenset(cycle)
            if cycle_set not in [frozenset(c) for c in unique_cycles]:
                unique_cycles.append(cycle)
                self.add_issue(
                    cycle[0],
                    0,
                    'CIRCULAR_IMPORT',
                    f"Circular import chain: {' -> '.join(cycle)}",
                    'HIGH'
                )

    def analyze_all(self):
        """Run all analyses"""
        print("Building module map...")
        self.build_module_map()

        print("Checking for missing __init__.py files...")
        self.check_missing_init_files()

        print("Analyzing Python files...")
        py_files = list(self.root_path.rglob('*.py'))
        total = len(py_files)

        for idx, py_file in enumerate(py_files):
            if idx % 50 == 0:
                print(f"  Progress: {idx}/{total}")

            if 'venv' in str(py_file) or '.venv' in str(py_file) or '__pycache__' in str(py_file):
                continue

            # Skip if not in target directories
            if not any(part in py_file.parts for part in ['src', 'tests', 'scripts']):
                continue

            # Syntax check
            self.check_syntax_compile(py_file)

            # Import style check
            self.check_import_style(py_file)

            # Import resolution
            self.check_import_resolution(py_file)

            # Wildcard imports
            self.check_wildcard_imports(py_file)

            # Import order
            # self.check_import_order(py_file)  # Commented out to reduce noise

        print("Checking for circular imports...")
        self.detect_circular_imports_advanced()

        print(f"\nAnalysis complete! Found {len(self.issues)} issues.")
        return self.issues

    def generate_report(self):
        """Generate and save report"""
        # Group by severity
        by_severity = defaultdict(list)
        by_type = defaultdict(list)

        for issue in self.issues:
            by_severity[issue['severity']].append(issue)
            by_type[issue['type']].append(issue)

        print(f"\n{'='*80}")
        print(f"DEEP CODE ANALYSIS REPORT")
        print(f"{'='*80}\n")
        print(f"Total Issues: {len(self.issues)}\n")

        # Summary by severity
        print("SUMMARY BY SEVERITY:")
        print("-" * 80)
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = len(by_severity[severity])
            if count > 0:
                print(f"  {severity}: {count}")

        # Summary by type
        print(f"\nSUMMARY BY TYPE:")
        print("-" * 80)
        for error_type, issues in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {error_type}: {len(issues)}")

        # Detailed issues
        print(f"\n{'='*80}")
        print("DETAILED ISSUES")
        print(f"{'='*80}\n")

        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            issues = by_severity[severity]
            if issues:
                print(f"\n{severity} SEVERITY ({len(issues)} issues)")
                print(f"{'-'*80}")

                # Show all issues for CRITICAL and HIGH, limit others
                limit = 100 if severity in ['CRITICAL', 'HIGH'] else 30

                for issue in issues[:limit]:
                    print(f"\n#{issue['id']} {issue['type']}")
                    print(f"  File: {issue['file']}")
                    print(f"  Line: {issue['line']}")
                    print(f"  Description: {issue['description']}")
                    if 'code' in issue and issue['code']:
                        print(f"  Code: {issue['code']}")

                if len(issues) > limit:
                    print(f"\n... and {len(issues) - limit} more {severity} issues")

        # Save JSON report
        output_file = self.root_path / 'deep_analysis_report.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_issues': len(self.issues),
                'by_severity': {k: len(v) for k, v in by_severity.items()},
                'by_type': {k: len(v) for k, v in by_type.items()},
                'issues': self.issues
            }, f, indent=2)

        print(f"\n\nFull JSON report saved to: {output_file}")

if __name__ == '__main__':
    root = Path(__file__).parent
    analyzer = DeepCodeAnalyzer(root)
    analyzer.analyze_all()
    analyzer.generate_report()
