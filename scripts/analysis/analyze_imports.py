#!/usr/bin/env python3
"""
Comprehensive Python codebase analyzer for syntax and import errors.
"""
import ast
import os
import sys
import importlib.util
from pathlib import Path
from collections import defaultdict
import json

class CodeAnalyzer:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.issues = []
        self.import_graph = defaultdict(set)
        self.all_modules = set()
        self.issue_count = 0

    def add_issue(self, file_path, line_number, error_type, description, severity):
        """Add an issue to the list"""
        self.issue_count += 1
        self.issues.append({
            'id': self.issue_count,
            'file': str(file_path),
            'line': line_number,
            'type': error_type,
            'description': description,
            'severity': severity
        })

    def check_syntax(self, file_path):
        """Check for syntax errors in a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    self.add_issue(
                        file_path,
                        e.lineno or 0,
                        'SYNTAX_ERROR',
                        f"Syntax error: {e.msg}",
                        'CRITICAL'
                    )
                    return False
        except Exception as e:
            self.add_issue(
                file_path,
                0,
                'FILE_READ_ERROR',
                f"Cannot read file: {str(e)}",
                'HIGH'
            )
            return False
        return True

    def extract_imports(self, file_path):
        """Extract all imports from a Python file"""
        imports = {
            'standard': [],
            'third_party': [],
            'local': [],
            'relative': []
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            import_info = {
                                'module': alias.name,
                                'line': node.lineno,
                                'type': 'import'
                            }
                            imports['standard'].append(import_info)

                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            import_info = {
                                'module': node.module,
                                'names': [alias.name for alias in node.names],
                                'line': node.lineno,
                                'level': node.level,
                                'type': 'from_import'
                            }

                            if node.level > 0:
                                imports['relative'].append(import_info)
                            elif node.module.startswith('.'):
                                imports['relative'].append(import_info)
                            else:
                                imports['local'].append(import_info)
        except SyntaxError:
            pass  # Already caught in check_syntax
        except Exception as e:
            self.add_issue(
                file_path,
                0,
                'IMPORT_EXTRACTION_ERROR',
                f"Cannot extract imports: {str(e)}",
                'MEDIUM'
            )

        return imports

    def check_import_exists(self, file_path, module_name, line_number):
        """Check if an imported module exists"""
        # Standard library modules (basic check)
        stdlib_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'collections', 're',
            'pathlib', 'typing', 'logging', 'unittest', 'asyncio', 'io',
            'copy', 'itertools', 'functools', 'operator', 'tempfile', 'shutil',
            'subprocess', 'threading', 'multiprocessing', 'hashlib', 'hmac',
            'base64', 'urllib', 'http', 'email', 'math', 'random', 'statistics',
            'dataclasses', 'enum', 'abc', 'contextlib', 'warnings', 'traceback',
            'inspect', 'ast', 'importlib', 'pkgutil', 'uuid', 'socket', 'ssl'
        }

        # Common third-party packages
        common_packages = {
            'langchain', 'langchain_core', 'langchain_community', 'langchain_openai',
            'langgraph', 'pydantic', 'fastapi', 'uvicorn', 'requests', 'httpx',
            'aiohttp', 'pytest', 'numpy', 'pandas', 'redis', 'sqlalchemy',
            'alembic', 'dotenv', 'anthropic', 'openai', 'tavily', 'exa_py',
            'firecrawl', 'tweepy', 'beautifulsoup4', 'lxml', 'yaml', 'toml',
            'click', 'rich', 'tqdm', 'pytest_asyncio', 'websockets', 'starlette'
        }

        # Extract base module
        base_module = module_name.split('.')[0]

        # Check if it's a standard library or common package
        if base_module in stdlib_modules or base_module in common_packages:
            return True

        # Check if it's a local module (starts with src or company_researcher)
        if base_module in ['src', 'company_researcher', 'tests', 'scripts']:
            # Check if the file exists in the project
            potential_paths = [
                self.root_path / 'src' / module_name.replace('.', '/') / '__init__.py',
                self.root_path / 'src' / f"{module_name.replace('.', '/')}.py",
                self.root_path / module_name.replace('.', '/') / '__init__.py',
                self.root_path / f"{module_name.replace('.', '/')}.py",
            ]

            for path in potential_paths:
                if path.exists():
                    return True

            return False

        # Unknown - assume it might exist (to reduce false positives)
        return True

    def check_circular_imports(self):
        """Detect circular import dependencies"""
        def has_cycle(node, visited, rec_stack, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.import_graph.get(node, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack, path):
                        return True
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    self.add_issue(
                        cycle[0],
                        0,
                        'CIRCULAR_IMPORT',
                        f"Circular import detected: {' -> '.join(cycle)}",
                        'HIGH'
                    )
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        visited = set()
        for node in self.import_graph:
            if node not in visited:
                has_cycle(node, visited, set(), [])

    def analyze_file(self, file_path):
        """Analyze a single Python file"""
        # Check syntax first
        if not self.check_syntax(file_path):
            return

        # Extract and analyze imports
        imports = self.extract_imports(file_path)

        # Check for missing imports
        all_imports = (
            imports['standard'] +
            imports['third_party'] +
            imports['local'] +
            imports['relative']
        )

        for imp in all_imports:
            module = imp.get('module', '')
            line = imp.get('line', 0)

            if module and not self.check_import_exists(file_path, module, line):
                self.add_issue(
                    file_path,
                    line,
                    'MISSING_MODULE',
                    f"Module '{module}' may not exist",
                    'HIGH'
                )

        # Build import graph for circular dependency detection
        file_module = self.get_module_name(file_path)
        if file_module:
            for imp in imports['local']:
                module = imp.get('module', '')
                if module:
                    self.import_graph[file_module].add(module)

    def get_module_name(self, file_path):
        """Convert file path to module name"""
        try:
            rel_path = file_path.relative_to(self.root_path / 'src')
            parts = rel_path.parts
            if parts[-1] == '__init__.py':
                return '.'.join(parts[:-1])
            else:
                return '.'.join(parts)[:-3]  # Remove .py
        except:
            return None

    def analyze_all(self):
        """Analyze all Python files in the codebase"""
        directories = ['src', 'tests', 'scripts']

        for directory in directories:
            dir_path = self.root_path / directory
            if not dir_path.exists():
                continue

            for file_path in dir_path.rglob('*.py'):
                self.analyze_file(file_path)

        # Check for circular imports
        self.check_circular_imports()

        return self.issues

    def print_report(self):
        """Print analysis report"""
        print(f"\n{'='*80}")
        print(f"PYTHON CODEBASE ANALYSIS REPORT")
        print(f"{'='*80}\n")

        # Group by severity
        by_severity = defaultdict(list)
        for issue in self.issues:
            by_severity[issue['severity']].append(issue)

        print(f"Total Issues Found: {len(self.issues)}\n")

        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            issues = by_severity[severity]
            if issues:
                print(f"\n{severity} SEVERITY ({len(issues)} issues)")
                print(f"{'-'*80}")
                for issue in issues[:50]:  # Limit output
                    print(f"\n#{issue['id']} - {issue['type']}")
                    print(f"  File: {issue['file']}")
                    print(f"  Line: {issue['line']}")
                    print(f"  Description: {issue['description']}")

                if len(issues) > 50:
                    print(f"\n... and {len(issues) - 50} more {severity} issues")

        # Save to JSON
        output_file = self.root_path / 'code_analysis_report.json'
        with open(output_file, 'w') as f:
            json.dump(self.issues, f, indent=2)
        print(f"\n\nFull report saved to: {output_file}")

if __name__ == '__main__':
    root = Path(__file__).parent
    analyzer = CodeAnalyzer(root)
    analyzer.analyze_all()
    analyzer.print_report()
