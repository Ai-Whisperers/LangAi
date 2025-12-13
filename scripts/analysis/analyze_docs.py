#!/usr/bin/env python3
"""Script to analyze Python files for documentation issues."""

import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import json

class DocAnalyzer(ast.NodeVisitor):
    """Analyzes Python AST for documentation issues."""

    def __init__(self, filepath: str, content: str):
        self.filepath = filepath
        self.content = content
        self.lines = content.split('\n')
        self.issues = []
        self.in_class = None

    def get_line_content(self, lineno: int) -> str:
        """Get content of a specific line."""
        if 0 < lineno <= len(self.lines):
            return self.lines[lineno - 1]
        return ""

    def check_type_hints(self, node):
        """Check if function has type hints."""
        missing_hints = []

        # Check arguments
        for arg in node.args.args:
            if arg.arg != 'self' and arg.arg != 'cls' and not arg.annotation:
                missing_hints.append(f"arg '{arg.arg}'")

        # Check return type
        if not node.returns and node.name not in ['__init__', '__str__', '__repr__']:
            missing_hints.append("return type")

        return missing_hints

    def has_docstring(self, node):
        """Check if node has docstring."""
        return (ast.get_docstring(node) is not None)

    def check_docstring_completeness(self, node, docstring):
        """Check if docstring is complete."""
        issues = []

        if not docstring:
            return issues

        # Check for Args section if function has parameters
        if isinstance(node, ast.FunctionDef):
            params = [arg.arg for arg in node.args.args if arg.arg not in ['self', 'cls']]
            if params and 'Args:' not in docstring and 'Parameters:' not in docstring and 'Arguments:' not in docstring:
                issues.append("Missing Args/Parameters section")

            # Check for Returns section
            if node.returns and 'Returns:' not in docstring and 'Return:' not in docstring:
                issues.append("Missing Returns section")

            # Check for Raises section (if raises exceptions)
            # This is hard to detect perfectly, but we can check for common patterns
            func_code = ast.get_source_segment(self.content, node)
            if func_code and 'raise ' in func_code and 'Raises:' not in docstring:
                issues.append("Missing Raises section (code contains 'raise')")

        return issues

    def is_public(self, name: str) -> bool:
        """Check if name is public (not starting with _)."""
        return not name.startswith('_') or name.startswith('__') and name.endswith('__')

    def check_magic_numbers(self, node):
        """Check for magic numbers in code."""
        class NumberVisitor(ast.NodeVisitor):
            def __init__(self):
                self.magic_numbers = []

            def visit_Num(self, node):
                # Skip common non-magic numbers
                if hasattr(node, 'n') and node.n not in [0, 1, -1, 2, 10, 100, 1000]:
                    self.magic_numbers.append((node.lineno, node.n))
                self.generic_visit(node)

            def visit_Constant(self, node):
                if isinstance(node.value, (int, float)) and node.value not in [0, 1, -1, 2, 10, 100, 1000]:
                    self.magic_numbers.append((node.lineno, node.value))
                self.generic_visit(node)

        visitor = NumberVisitor()
        visitor.visit(node)
        return visitor.magic_numbers

    def visit_Module(self, node):
        """Check module-level docstring."""
        if not self.has_docstring(node):
            self.issues.append({
                'file': self.filepath,
                'line': 1,
                'issue': 'Missing module docstring',
                'severity': 'high',
                'type': 'missing_module_docstring'
            })
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Check class documentation."""
        old_class = self.in_class
        self.in_class = node.name

        if self.is_public(node.name):
            if not self.has_docstring(node):
                self.issues.append({
                    'file': self.filepath,
                    'line': node.lineno,
                    'issue': f'Missing docstring on public class: {node.name}',
                    'severity': 'high',
                    'type': 'missing_class_docstring'
                })
            else:
                docstring = ast.get_docstring(node)
                completeness_issues = self.check_docstring_completeness(node, docstring)
                for issue in completeness_issues:
                    self.issues.append({
                        'file': self.filepath,
                        'line': node.lineno,
                        'issue': f'Class {node.name}: {issue}',
                        'severity': 'medium',
                        'type': 'incomplete_docstring'
                    })

        self.generic_visit(node)
        self.in_class = old_class

    def visit_FunctionDef(self, node):
        """Check function documentation."""
        if self.is_public(node.name) or self.in_class:
            # Check docstring
            if not self.has_docstring(node):
                context = f"method in class {self.in_class}" if self.in_class else "function"
                self.issues.append({
                    'file': self.filepath,
                    'line': node.lineno,
                    'issue': f'Missing docstring on public {context}: {node.name}',
                    'severity': 'high',
                    'type': 'missing_function_docstring'
                })
            else:
                # Check docstring completeness
                docstring = ast.get_docstring(node)
                completeness_issues = self.check_docstring_completeness(node, docstring)
                for issue in completeness_issues:
                    self.issues.append({
                        'file': self.filepath,
                        'line': node.lineno,
                        'issue': f'Function {node.name}: {issue}',
                        'severity': 'medium',
                        'type': 'incomplete_docstring'
                    })

            # Check type hints
            missing_hints = self.check_type_hints(node)
            if missing_hints:
                self.issues.append({
                    'file': self.filepath,
                    'line': node.lineno,
                    'issue': f'Function {node.name}: Missing type hints for {", ".join(missing_hints)}',
                    'severity': 'medium',
                    'type': 'missing_type_hints'
                })

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Check async function documentation."""
        self.visit_FunctionDef(node)

def analyze_file(filepath: str) -> List[Dict]:
    """Analyze a single Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content, filename=filepath)
        analyzer = DocAnalyzer(filepath, content)
        analyzer.visit(tree)

        # Check for complex conditionals without comments
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Complex if statements
            if stripped.startswith('if ') and ' and ' in stripped and ' or ' in stripped:
                # Check if previous line has comment
                prev_line = lines[i-2].strip() if i > 1 else ''
                if not prev_line.startswith('#'):
                    analyzer.issues.append({
                        'file': filepath,
                        'line': i,
                        'issue': f'Complex conditional without comment: {stripped[:60]}...',
                        'severity': 'low',
                        'type': 'complex_conditional_no_comment'
                    })

        return analyzer.issues
    except Exception as e:
        return [{
            'file': filepath,
            'line': 0,
            'issue': f'Error analyzing file: {str(e)}',
            'severity': 'low',
            'type': 'parse_error'
        }]

def check_readme_files(src_dir: str) -> List[Dict]:
    """Check for missing README files in packages."""
    issues = []
    src_path = Path(src_dir)

    # Find all directories with __init__.py
    for init_file in src_path.rglob('__init__.py'):
        package_dir = init_file.parent
        readme_exists = any(package_dir.glob('README.md')) or any(package_dir.glob('README.rst'))

        # Check if this is a significant package (has multiple modules)
        py_files = list(package_dir.glob('*.py'))
        if len(py_files) > 2 and not readme_exists:  # More than just __init__.py
            issues.append({
                'file': str(package_dir / 'README.md'),
                'line': 0,
                'issue': f'Missing README.md in package: {package_dir.name}',
                'severity': 'medium',
                'type': 'missing_readme'
            })

    return issues

def main():
    """Main analysis function."""
    src_dir = r'c:\Users\Alejandro\Documents\Ivan\Work\Lang ai\src'
    all_issues = []

    # Analyze Python files
    for py_file in Path(src_dir).rglob('*.py'):
        issues = analyze_file(str(py_file))
        all_issues.extend(issues)

    # Check for missing READMEs
    readme_issues = check_readme_files(src_dir)
    all_issues.extend(readme_issues)

    # Sort by severity and file
    severity_order = {'high': 0, 'medium': 1, 'low': 2}
    all_issues.sort(key=lambda x: (severity_order[x['severity']], x['file'], x['line']))

    # Print results
    print(f"\n{'='*80}")
    print(f"DOCUMENTATION ANALYSIS RESULTS")
    print(f"{'='*80}\n")
    print(f"Total issues found: {len(all_issues)}\n")

    # Group by severity
    by_severity = {}
    for issue in all_issues:
        sev = issue['severity']
        by_severity.setdefault(sev, []).append(issue)

    for severity in ['high', 'medium', 'low']:
        if severity in by_severity:
            print(f"\n{severity.upper()} SEVERITY ({len(by_severity[severity])} issues)")
            print('-' * 80)
            for i, issue in enumerate(by_severity[severity][:200], 1):  # Limit output
                print(f"\n{i}. {issue['file']}:{issue['line']}")
                print(f"   Type: {issue['type']}")
                print(f"   Issue: {issue['issue']}")

    # Save to JSON
    output_file = r'c:\Users\Alejandro\Documents\Ivan\Work\Lang ai\documentation_issues.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_issues, f, indent=2)

    print(f"\n\nFull results saved to: {output_file}")

if __name__ == '__main__':
    main()
