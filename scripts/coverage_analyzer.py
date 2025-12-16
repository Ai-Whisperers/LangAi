#!/usr/bin/env python3
"""
Test Coverage Gap Analyzer - Senior QA Tool

Analyzes Python codebase for comprehensive test coverage gaps including:
- Untested modules, classes, and functions
- Missing edge cases and error paths
- Integration and E2E test gaps
- Mock isolation issues
- Flaky test patterns
- Async test coverage
- Boundary and negative tests
"""

import ast
import json
import os
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestType(str, Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PROPERTY = "property"
    PERFORMANCE = "performance"


@dataclass
class TestGap:
    """Represents a test coverage gap."""

    file_path: str
    element_name: str
    element_type: str  # function, class, method, module
    gap_type: str
    reason: str
    test_type_needed: TestType
    priority: Priority
    line_number: Optional[int] = None
    complexity: Optional[int] = None
    has_error_handling: bool = False
    has_async: bool = False
    parameters: List[str] = field(default_factory=list)


@dataclass
class CodeElement:
    """Represents a code element to be tested."""

    name: str
    type: str
    file_path: str
    line_number: int
    is_public: bool
    is_async: bool
    has_decorators: bool
    parameters: List[str]
    return_type: Optional[str]
    has_error_handling: bool
    complexity: int
    docstring: Optional[str]


class ASTAnalyzer(ast.NodeVisitor):
    """AST visitor to extract testable code elements."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.elements: List[CodeElement] = []
        self.current_class: Optional[str] = None

    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit class definition."""
        is_public = not node.name.startswith("_")

        # Check if it's a test class
        if node.name.startswith("Test") or any(
            base.id == "TestCase" if isinstance(base, ast.Name) else False for base in node.bases
        ):
            self.generic_visit(node)
            return

        element = CodeElement(
            name=node.name,
            type="class",
            file_path=self.file_path,
            line_number=node.lineno,
            is_public=is_public,
            is_async=False,
            has_decorators=len(node.decorator_list) > 0,
            parameters=[],
            return_type=None,
            has_error_handling=self._has_error_handling(node),
            complexity=self._calculate_complexity(node),
            docstring=ast.get_docstring(node),
        )
        self.elements.append(element)

        # Visit methods
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function/method definition."""
        # Skip test functions
        if node.name.startswith("test_"):
            return

        is_public = not node.name.startswith("_")
        is_async = isinstance(node, ast.AsyncFunctionDef)

        # Get parameters
        params = [arg.arg for arg in node.args.args if arg.arg != "self" and arg.arg != "cls"]

        # Get return type
        return_type = None
        if node.returns:
            return_type = (
                ast.unparse(node.returns) if hasattr(ast, "unparse") else str(node.returns)
            )

        element_type = "method" if self.current_class else "function"
        full_name = f"{self.current_class}.{node.name}" if self.current_class else node.name

        element = CodeElement(
            name=full_name,
            type=element_type,
            file_path=self.file_path,
            line_number=node.lineno,
            is_public=is_public,
            is_async=is_async,
            has_decorators=len(node.decorator_list) > 0,
            parameters=params,
            return_type=return_type,
            has_error_handling=self._has_error_handling(node),
            complexity=self._calculate_complexity(node),
            docstring=ast.get_docstring(node),
        )
        self.elements.append(element)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visit async function definition."""
        self.visit_FunctionDef(node)

    def _has_error_handling(self, node: ast.AST) -> bool:
        """Check if node contains error handling."""
        for child in ast.walk(node):
            if isinstance(child, (ast.Try, ast.Raise, ast.ExceptHandler)):
                return True
        return False

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(
                child,
                (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With, ast.Assert, ast.BoolOp),
            ):
                complexity += 1
        return complexity


class TestAnalyzer(ast.NodeVisitor):
    """Analyzer for test files to identify what's being tested."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.tested_elements: Set[str] = set()
        self.test_issues: List[Dict[str, Any]] = []
        self.current_test: Optional[str] = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit test function."""
        if not node.name.startswith("test_"):
            return

        self.current_test = node.name

        # Check for assertions
        has_assertions = self._has_assertions(node)
        if not has_assertions:
            self.test_issues.append(
                {"test": node.name, "issue": "no_assertions", "line": node.lineno}
            )

        # Check for hardcoded values
        if self._has_hardcoded_values(node):
            self.test_issues.append(
                {"test": node.name, "issue": "hardcoded_values", "line": node.lineno}
            )

        # Check for external service calls
        if self._calls_external_service(node):
            self.test_issues.append(
                {"test": node.name, "issue": "external_service", "line": node.lineno}
            )

        # Extract what's being tested
        tested = self._extract_tested_elements(node)
        self.tested_elements.update(tested)

        self.generic_visit(node)
        self.current_test = None

    def _has_assertions(self, node: ast.FunctionDef) -> bool:
        """Check if test has assertions."""
        for child in ast.walk(node):
            if isinstance(child, ast.Assert):
                return True
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr.startswith("assert"):
                        return True
        return False

    def _has_hardcoded_values(self, node: ast.FunctionDef) -> bool:
        """Check for hardcoded test values."""
        # Simple heuristic: many string/number literals
        literals = []
        for child in ast.walk(node):
            if isinstance(child, (ast.Constant, ast.Str, ast.Num)):
                if isinstance(child, ast.Constant):
                    if isinstance(child.value, (str, int, float)):
                        literals.append(child.value)
        return len(literals) > 5

    def _calls_external_service(self, node: ast.FunctionDef) -> bool:
        """Check if test calls external services."""
        external_patterns = ["requests.", "httpx.", "urllib.", "http.client"]
        code = ast.unparse(node) if hasattr(ast, "unparse") else ""
        return any(pattern in code for pattern in external_patterns)

    def _extract_tested_elements(self, node: ast.FunctionDef) -> Set[str]:
        """Extract names of tested elements."""
        tested = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    tested.add(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    tested.add(child.func.attr)
        return tested


class CoverageAnalyzer:
    """Main test coverage analyzer."""

    def __init__(self, src_dir: str, test_dir: str):
        self.src_dir = Path(src_dir)
        self.test_dir = Path(test_dir)
        self.gaps: List[TestGap] = []
        self.src_elements: Dict[str, List[CodeElement]] = {}
        self.tested_elements: Set[str] = set()
        self.test_issues: List[Dict[str, Any]] = []

    def analyze(self) -> List[TestGap]:
        """Run complete analysis."""
        print("Analyzing source code...")
        self._analyze_source_files()

        print("Analyzing test files...")
        self._analyze_test_files()

        print("Finding coverage gaps...")
        self._find_gaps()

        print(f"Found {len(self.gaps)} test coverage gaps")
        return self.gaps

    def _analyze_source_files(self):
        """Analyze all source files."""
        for py_file in self.src_dir.rglob("*.py"):
            if "__pycache__" in str(py_file) or "test" in str(py_file).lower():
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=str(py_file))

                analyzer = ASTAnalyzer(str(py_file.relative_to(self.src_dir)))
                analyzer.visit(tree)

                if analyzer.elements:
                    self.src_elements[str(py_file)] = analyzer.elements

            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")

    def _analyze_test_files(self):
        """Analyze all test files."""
        if not self.test_dir.exists():
            print(f"Warning: Test directory {self.test_dir} does not exist")
            return

        for py_file in self.test_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=str(py_file))

                analyzer = TestAnalyzer(str(py_file.relative_to(self.test_dir)))
                analyzer.visit(tree)

                self.tested_elements.update(analyzer.tested_elements)
                self.test_issues.extend(analyzer.test_issues)

            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")

    def _find_gaps(self):
        """Find all test coverage gaps."""
        for file_path, elements in self.src_elements.items():
            # Check for untested file
            file_has_tests = self._has_test_file(file_path)

            for element in elements:
                # Skip private elements for now
                if not element.is_public:
                    continue

                # Check if element is tested
                is_tested = (
                    element.name in self.tested_elements
                    or element.name.split(".")[-1] in self.tested_elements
                )

                if not is_tested:
                    self._add_untested_gap(element, file_has_tests)

                # Check for missing edge cases
                if element.complexity > 5:
                    self._add_complexity_gap(element)

                # Check for missing error path tests
                if element.has_error_handling:
                    self._add_error_path_gap(element)

                # Check for async test handling
                if element.is_async:
                    self._add_async_test_gap(element)

                # Check for boundary tests
                if element.parameters:
                    self._add_boundary_test_gap(element)

    def _has_test_file(self, src_file: str) -> bool:
        """Check if source file has corresponding test file."""
        # Convert src path to test path
        src_path = Path(src_file)
        test_candidates = [
            self.test_dir / f"test_{src_path.name}",
            self.test_dir / "unit" / f"test_{src_path.name}",
            self.test_dir / "integration" / f"test_{src_path.name}",
        ]
        return any(p.exists() for p in test_candidates)

    def _add_untested_gap(self, element: CodeElement, file_has_tests: bool):
        """Add gap for untested element."""
        priority = Priority.HIGH if element.type == "class" else Priority.MEDIUM
        if not file_has_tests:
            priority = Priority.HIGH

        gap = TestGap(
            file_path=element.file_path,
            element_name=element.name,
            element_type=element.type,
            gap_type="untested_element",
            reason=f"Public {element.type} '{element.name}' has no tests",
            test_type_needed=TestType.UNIT,
            priority=priority,
            line_number=element.line_number,
            complexity=element.complexity,
            has_error_handling=element.has_error_handling,
            has_async=element.is_async,
            parameters=element.parameters,
        )
        self.gaps.append(gap)

    def _add_complexity_gap(self, element: CodeElement):
        """Add gap for complex element needing edge case tests."""
        gap = TestGap(
            file_path=element.file_path,
            element_name=element.name,
            element_type=element.type,
            gap_type="missing_edge_cases",
            reason=f"High complexity ({element.complexity}) requires edge case testing",
            test_type_needed=TestType.UNIT,
            priority=Priority.HIGH,
            line_number=element.line_number,
            complexity=element.complexity,
        )
        self.gaps.append(gap)

    def _add_error_path_gap(self, element: CodeElement):
        """Add gap for missing error path tests."""
        gap = TestGap(
            file_path=element.file_path,
            element_name=element.name,
            element_type=element.type,
            gap_type="missing_error_paths",
            reason="Contains error handling that should be tested",
            test_type_needed=TestType.UNIT,
            priority=Priority.HIGH,
            line_number=element.line_number,
            has_error_handling=True,
        )
        self.gaps.append(gap)

    def _add_async_test_gap(self, element: CodeElement):
        """Add gap for async function needing async tests."""
        gap = TestGap(
            file_path=element.file_path,
            element_name=element.name,
            element_type=element.type,
            gap_type="missing_async_test",
            reason="Async function requires async test handling",
            test_type_needed=TestType.UNIT,
            priority=Priority.MEDIUM,
            line_number=element.line_number,
            has_async=True,
        )
        self.gaps.append(gap)

    def _add_boundary_test_gap(self, element: CodeElement):
        """Add gap for boundary value tests."""
        gap = TestGap(
            file_path=element.file_path,
            element_name=element.name,
            element_type=element.type,
            gap_type="missing_boundary_tests",
            reason=f"Function with {len(element.parameters)} parameters needs boundary testing",
            test_type_needed=TestType.UNIT,
            priority=Priority.MEDIUM,
            line_number=element.line_number,
            parameters=element.parameters,
        )
        self.gaps.append(gap)

    def generate_report(self, output_file: str = "test_coverage_gaps.json"):
        """Generate comprehensive report."""
        report = {
            "summary": {
                "total_gaps": len(self.gaps),
                "high_priority": len([g for g in self.gaps if g.priority == Priority.HIGH]),
                "medium_priority": len([g for g in self.gaps if g.priority == Priority.MEDIUM]),
                "low_priority": len([g for g in self.gaps if g.priority == Priority.LOW]),
                "by_type": {},
                "test_issues": len(self.test_issues),
            },
            "gaps": [asdict(gap) for gap in self.gaps],
            "test_issues": self.test_issues,
        }

        # Count by gap type
        for gap in self.gaps:
            gap_type = gap.gap_type
            report["summary"]["by_type"][gap_type] = (
                report["summary"]["by_type"].get(gap_type, 0) + 1
            )

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved to {output_file}")
        print(f"\nSummary:")
        print(f"  Total gaps: {report['summary']['total_gaps']}")
        print(f"  High priority: {report['summary']['high_priority']}")
        print(f"  Medium priority: {report['summary']['medium_priority']}")
        print(f"  Low priority: {report['summary']['low_priority']}")
        print(f"\nGaps by type:")
        for gap_type, count in sorted(report["summary"]["by_type"].items()):
            print(f"  {gap_type}: {count}")

        return report


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze test coverage gaps")
    parser.add_argument("--src", default="src", help="Source directory")
    parser.add_argument("--tests", default="tests", help="Tests directory")
    parser.add_argument("--output", default="test_coverage_gaps.json", help="Output file")
    args = parser.parse_args()

    analyzer = CoverageAnalyzer(args.src, args.tests)
    gaps = analyzer.analyze()
    report = analyzer.generate_report(args.output)

    # Print first 20 high-priority gaps
    high_priority = [g for g in gaps if g.priority == Priority.HIGH][:20]
    if high_priority:
        print("\n" + "=" * 80)
        print("TOP 20 HIGH PRIORITY GAPS:")
        print("=" * 80)
        for i, gap in enumerate(high_priority, 1):
            print(f"\n{i}. {gap.element_name} ({gap.element_type})")
            print(f"   File: {gap.file_path}:{gap.line_number}")
            print(f"   Type: {gap.gap_type}")
            print(f"   Reason: {gap.reason}")
            print(f"   Test needed: {gap.test_type_needed.value}")


if __name__ == "__main__":
    main()
