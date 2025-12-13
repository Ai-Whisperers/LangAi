#!/usr/bin/env python3
"""
Bulk Refactoring Analyzer for company_researcher codebase.

This script analyzes the codebase for patterns that should use centralized utilities:
1. json.loads() with try/except -> safe_json_parse()
2. Generic except Exception handlers -> more specific exceptions
3. logging.getLogger(__name__) -> get_logger()
4. datetime.now()/datetime.utcnow() -> utc_now()

Usage:
    python bulk_refactoring_analyzer.py > refactoring_report.md
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict

# Base directory
BASE_DIR = Path(r"c:\Users\Alejandro\Documents\Ivan\Work\Lang ai\src\company_researcher")


@dataclass
class Finding:
    """Represents a refactoring finding."""
    file_path: Path
    line_number: int
    pattern_type: str
    current_code: str
    suggested_code: str
    context_before: str = ""
    context_after: str = ""
    priority: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    notes: str = ""


@dataclass
class RefactoringReport:
    """Complete refactoring analysis report."""
    findings: List[Finding] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def add_finding(self, finding: Finding):
        """Add a finding and update stats."""
        self.findings.append(finding)
        self.stats[finding.pattern_type] += 1
        self.stats["total"] += 1

    def generate_markdown(self) -> str:
        """Generate markdown report."""
        lines = [
            "# Company Researcher - Bulk Refactoring Report",
            "",
            "## Executive Summary",
            "",
            f"**Total Findings:** {self.stats['total']}",
            "",
            "### Breakdown by Pattern Type",
            ""
        ]

        # Summary table
        for pattern_type, count in sorted(self.stats.items()):
            if pattern_type != "total":
                lines.append(f"- **{pattern_type}:** {count} occurrences")

        lines.extend([
            "",
            "---",
            "",
            "## Detailed Findings",
            ""
        ])

        # Group findings by pattern type
        by_type = defaultdict(list)
        for finding in self.findings:
            by_type[finding.pattern_type].append(finding)

        # Generate sections for each pattern type
        for pattern_type in sorted(by_type.keys()):
            findings_list = by_type[pattern_type]
            lines.extend([
                f"## {pattern_type}",
                "",
                f"**Total occurrences:** {len(findings_list)}",
                ""
            ])

            for i, finding in enumerate(findings_list, 1):
                rel_path = finding.file_path.relative_to(BASE_DIR.parent.parent)
                lines.extend([
                    f"### {i}. `{rel_path}:{finding.line_number}`",
                    "",
                    f"**Priority:** {finding.priority}",
                    ""
                ])

                if finding.notes:
                    lines.extend([
                        f"**Notes:** {finding.notes}",
                        ""
                    ])

                lines.extend([
                    "**Current Code:**",
                    "```python",
                    finding.current_code.strip(),
                    "```",
                    "",
                    "**Suggested Refactoring:**",
                    "```python",
                    finding.suggested_code.strip(),
                    "```",
                    ""
                ])

                if finding.context_before or finding.context_after:
                    lines.extend([
                        "<details>",
                        "<summary>View context</summary>",
                        "",
                        "```python"
                    ])
                    if finding.context_before:
                        lines.append(finding.context_before.strip())
                    lines.append("# >>> CURRENT CODE >>>")
                    lines.append(finding.current_code.strip())
                    lines.append("# <<< END CURRENT CODE <<<")
                    if finding.context_after:
                        lines.append(finding.context_after.strip())
                    lines.extend([
                        "```",
                        "</details>",
                        ""
                    ])

        return "\n".join(lines)


class RefactoringAnalyzer:
    """Analyzes codebase for refactoring opportunities."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.report = RefactoringReport()

    def analyze(self):
        """Run all analyses."""
        print("Starting refactoring analysis...")

        # Get all Python files
        py_files = list(self.base_dir.rglob("*.py"))
        print(f"Found {len(py_files)} Python files")

        for py_file in py_files:
            # Skip __pycache__ and test files
            if "__pycache__" in str(py_file) or ".archive" in str(py_file):
                continue

            try:
                self.analyze_file(py_file)
            except Exception as e:
                print(f"WARNING: Error analyzing {py_file}: {e}")

        print(f"\nAnalysis complete! Found {self.report.stats['total']} refactoring opportunities")

    def analyze_file(self, file_path: Path):
        """Analyze a single file for all patterns."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return

        lines = content.split('\n')

        # Pattern 1: json.loads with try/except
        self._find_json_loads_patterns(file_path, lines)

        # Pattern 2: Generic exception handlers
        self._find_generic_exception_handlers(file_path, lines)

        # Pattern 3: logging.getLogger patterns
        self._find_logging_getlogger(file_path, lines)

        # Pattern 4: datetime.now()/utcnow()
        self._find_datetime_patterns(file_path, lines)

    def _find_json_loads_patterns(self, file_path: Path, lines: List[str]):
        """Find json.loads() patterns that could use safe_json_parse()."""
        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for json.loads(
            if 'json.loads(' in line and 'safe_json_parse' not in ''.join(lines[max(0, i-5):i+1]):
                # Check if within a try/except block (look ahead)
                has_try_except = False
                try_start = None

                # Look backwards for try:
                for j in range(max(0, i-10), i):
                    if re.match(r'\s*try:', lines[j]):
                        try_start = j
                        has_try_except = True
                        break

                # Look forward for except
                if has_try_except:
                    for j in range(i+1, min(len(lines), i+15)):
                        if re.match(r'\s*except\s+(json\.JSONDecodeError|Exception|ValueError)', lines[j]):
                            has_try_except = True
                            break

                if has_try_except:
                    # Extract the variable and default
                    match = re.search(r'(\w+)\s*=\s*json\.loads\(([^)]+)\)', line)
                    if match:
                        var_name = match.group(1)
                        json_arg = match.group(2)

                        # Try to find the default value in the except block
                        default_value = "None"
                        for j in range(i+1, min(len(lines), i+20)):
                            except_line = lines[j]
                            if f'{var_name} =' in except_line or f'return ' in except_line:
                                # Extract default
                                if 'return {}' in except_line or f'{var_name} = {{}}' in except_line:
                                    default_value = "{}"
                                elif 'return []' in except_line or f'{var_name} = []' in except_line:
                                    default_value = "[]"
                                break

                        # Get context
                        context_before = '\n'.join(lines[max(0, i-3):i])
                        context_after = '\n'.join(lines[i+1:min(len(lines), i+4)])

                        # Create finding
                        current = line
                        suggested = line.replace(
                            f'json.loads({json_arg})',
                            f'safe_json_parse({json_arg}, default={default_value})'
                        )

                        # Add import suggestion
                        import_line = "from company_researcher.utils import safe_json_parse"

                        self.report.add_finding(Finding(
                            file_path=file_path,
                            line_number=i + 1,
                            pattern_type="1. JSON Parsing (json.loads → safe_json_parse)",
                            current_code=current,
                            suggested_code=f"{import_line}\n\n{suggested}\n# Remove try/except block",
                            context_before=context_before,
                            context_after=context_after,
                            priority="HIGH",
                            notes="Replace try/except json.loads pattern with safe_json_parse utility"
                        ))

            i += 1

    def _find_generic_exception_handlers(self, file_path: Path, lines: List[str]):
        """Find generic 'except Exception as e:' handlers."""
        for i, line in enumerate(lines):
            # Match: except Exception as e:
            if re.match(r'\s*except Exception as \w+:', line):
                # Get context to determine if this should be more specific
                context_before = '\n'.join(lines[max(0, i-5):i])
                context_after = '\n'.join(lines[i+1:min(len(lines), i+8)])

                # Analyze the try block to suggest specific exceptions
                specific_exceptions = self._suggest_specific_exceptions(
                    lines[max(0, i-10):i],
                    context_after
                )

                if specific_exceptions:
                    suggested = line.replace(
                        "except Exception as",
                        f"except ({', '.join(specific_exceptions)}) as"
                    )

                    self.report.add_finding(Finding(
                        file_path=file_path,
                        line_number=i + 1,
                        pattern_type="2. Generic Exception Handlers",
                        current_code=line,
                        suggested_code=suggested,
                        context_before=context_before,
                        context_after=context_after,
                        priority="MEDIUM",
                        notes=f"Consider more specific exceptions: {', '.join(specific_exceptions)}"
                    ))

    def _suggest_specific_exceptions(self, try_block: List[str], except_block: str) -> List[str]:
        """Suggest specific exceptions based on code patterns."""
        exceptions = set()

        try_code = '\n'.join(try_block)

        # Common patterns
        if 'json.loads' in try_code or 'json.dumps' in try_code:
            exceptions.add('json.JSONDecodeError')
        if '.get(' in try_code or 'requests.' in try_code or 'urllib' in try_code:
            exceptions.add('requests.RequestException')
        if 'open(' in try_code or 'read(' in try_code or 'write(' in try_code:
            exceptions.add('IOError')
        if '[' in try_code or 'KeyError' in except_block:
            exceptions.add('KeyError')
        if 'int(' in try_code or 'float(' in try_code:
            exceptions.add('ValueError')
        if 'None' in try_code and '.' in try_code:
            exceptions.add('AttributeError')

        return sorted(list(exceptions))

    def _find_logging_getlogger(self, file_path: Path, lines: List[str]):
        """Find logging.getLogger(__name__) patterns."""
        for i, line in enumerate(lines):
            if re.search(r'logging\.getLogger\(__name__\)', line):
                # Skip if already importing get_logger
                file_content = '\n'.join(lines)
                if 'from company_researcher.utils import' in file_content and 'get_logger' in file_content:
                    continue

                context_before = '\n'.join(lines[max(0, i-2):i])
                context_after = '\n'.join(lines[i+1:min(len(lines), i+3)])

                # Current pattern
                current = line

                # Suggested pattern
                suggested = line.replace(
                    'logging.getLogger(__name__)',
                    'get_logger(__name__)'
                )

                # Add import
                import_line = "from company_researcher.utils import get_logger"

                self.report.add_finding(Finding(
                    file_path=file_path,
                    line_number=i + 1,
                    pattern_type="3. Logger Initialization (logging.getLogger → get_logger)",
                    current_code=current,
                    suggested_code=f"{import_line}\n\n{suggested}\n# Remove 'import logging' if no longer needed",
                    context_before=context_before,
                    context_after=context_after,
                    priority="LOW",
                    notes="Use centralized get_logger utility"
                ))

    def _find_datetime_patterns(self, file_path: Path, lines: List[str]):
        """Find datetime.now() and datetime.utcnow() patterns."""
        for i, line in enumerate(lines):
            # Match datetime.now(timezone.utc) or datetime.utcnow()
            if re.search(r'datetime\.(now\(timezone\.utc\)|utcnow\(\))', line):
                # Skip if in utils/time.py (that's the implementation file)
                if 'utils/time.py' in str(file_path) or 'utils\\time.py' in str(file_path):
                    continue

                # Skip if already importing utc_now
                file_content = '\n'.join(lines)
                if 'from company_researcher.utils import' in file_content and 'utc_now' in file_content:
                    # Check if this line already uses utc_now
                    if 'utc_now()' in line:
                        continue

                context_before = '\n'.join(lines[max(0, i-2):i])
                context_after = '\n'.join(lines[i+1:min(len(lines), i+3)])

                # Current pattern
                current = line

                # Suggested pattern
                suggested = re.sub(
                    r'datetime\.(?:now\(timezone\.utc\)|utcnow\(\))',
                    'utc_now()',
                    line
                )

                # Add import
                import_line = "from company_researcher.utils import utc_now"

                self.report.add_finding(Finding(
                    file_path=file_path,
                    line_number=i + 1,
                    pattern_type="4. Datetime Usage (datetime.now/utcnow → utc_now)",
                    current_code=current,
                    suggested_code=f"{import_line}\n\n{suggested}",
                    context_before=context_before,
                    context_after=context_after,
                    priority="MEDIUM",
                    notes="Use centralized utc_now() for consistent UTC timestamps"
                ))


def main():
    """Main entry point."""
    analyzer = RefactoringAnalyzer(BASE_DIR)
    analyzer.analyze()

    # Generate report
    print("\n" + "="*80)
    print("GENERATING MARKDOWN REPORT")
    print("="*80 + "\n")

    report_md = analyzer.report.generate_markdown()

    # Save to file
    output_file = Path(r"c:\Users\Alejandro\Documents\Ivan\Work\Lang ai\REFACTORING_REPORT.md")
    output_file.write_text(report_md, encoding='utf-8')
    print(f"Report saved to: {output_file}")

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total findings: {analyzer.report.stats['total']}")
    for pattern_type, count in sorted(analyzer.report.stats.items()):
        if pattern_type != "total":
            print(f"  - {pattern_type}: {count}")


if __name__ == "__main__":
    main()
