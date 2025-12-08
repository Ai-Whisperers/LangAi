"""
Pre-commit Utilities - Code quality checks for CI/CD.

Provides:
- Code linting checks
- Type checking
- Test running
- Security scanning
- Documentation validation
"""

import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class CheckStatus(str, Enum):
    """Status of a check."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class CheckResult:
    """Result of a single check."""
    name: str
    status: CheckStatus
    message: str = ""
    duration_ms: float = 0
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "duration_ms": self.duration_ms,
            "details": self.details
        }


@dataclass
class PrecommitResult:
    """Result of all pre-commit checks."""
    checks: List[CheckResult] = field(default_factory=list)
    passed: bool = True
    total_duration_ms: float = 0

    def add_check(self, result: CheckResult) -> None:
        """Add a check result."""
        self.checks.append(result)
        if result.status == CheckStatus.FAILED:
            self.passed = False
        self.total_duration_ms += result.duration_ms

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "total_duration_ms": self.total_duration_ms,
            "checks": [c.to_dict() for c in self.checks],
            "failed_checks": [c.name for c in self.checks if c.status == CheckStatus.FAILED]
        }

    def summary(self) -> str:
        """Get summary string."""
        passed = sum(1 for c in self.checks if c.status == CheckStatus.PASSED)
        failed = sum(1 for c in self.checks if c.status == CheckStatus.FAILED)
        skipped = sum(1 for c in self.checks if c.status == CheckStatus.SKIPPED)

        status = "PASSED" if self.passed else "FAILED"
        return f"{status}: {passed} passed, {failed} failed, {skipped} skipped ({self.total_duration_ms:.0f}ms)"


class PrecommitRunner:
    """
    Runs pre-commit checks.

    Usage:
        runner = PrecommitRunner()

        # Add checks
        runner.add_check("lint", check_lint)
        runner.add_check("types", check_types)
        runner.add_check("tests", check_tests)

        # Run all checks
        result = runner.run()
        print(result.summary())
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self._checks: List[tuple] = []

    def add_check(
        self,
        name: str,
        check_fn: Callable[[], CheckResult],
        enabled: bool = True
    ) -> None:
        """Add a check."""
        self._checks.append((name, check_fn, enabled))

    def run(self, only: List[str] = None, exclude: List[str] = None) -> PrecommitResult:
        """
        Run all checks.

        Args:
            only: Only run these checks
            exclude: Exclude these checks

        Returns:
            PrecommitResult with all check results
        """
        import time

        result = PrecommitResult()

        for name, check_fn, enabled in self._checks:
            # Filter checks
            if only and name not in only:
                continue
            if exclude and name in exclude:
                continue
            if not enabled:
                result.add_check(CheckResult(
                    name=name,
                    status=CheckStatus.SKIPPED,
                    message="Check disabled"
                ))
                continue

            # Run check
            start = time.time()
            try:
                check_result = check_fn()
                check_result.duration_ms = (time.time() - start) * 1000
            except Exception as e:
                check_result = CheckResult(
                    name=name,
                    status=CheckStatus.ERROR,
                    message=str(e),
                    duration_ms=(time.time() - start) * 1000
                )

            result.add_check(check_result)

        return result


# Built-in checks


def run_command(cmd: List[str], cwd: str = ".") -> tuple:
    """Run a command and return (success, output)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def check_ruff(path: str = ".") -> CheckResult:
    """Run Ruff linter."""
    success, output = run_command(["ruff", "check", path])
    return CheckResult(
        name="ruff",
        status=CheckStatus.PASSED if success else CheckStatus.FAILED,
        message="Ruff linting passed" if success else "Ruff found issues",
        details={"output": output[:2000]}  # Truncate
    )


def check_black(path: str = ".", check_only: bool = True) -> CheckResult:
    """Run Black formatter check."""
    cmd = ["black", "--check", path] if check_only else ["black", path]
    success, output = run_command(cmd)
    return CheckResult(
        name="black",
        status=CheckStatus.PASSED if success else CheckStatus.FAILED,
        message="Black formatting passed" if success else "Black formatting issues",
        details={"output": output[:2000]}
    )


def check_mypy(path: str = ".") -> CheckResult:
    """Run MyPy type checker."""
    success, output = run_command(["mypy", path, "--ignore-missing-imports"])
    return CheckResult(
        name="mypy",
        status=CheckStatus.PASSED if success else CheckStatus.FAILED,
        message="Type checking passed" if success else "Type errors found",
        details={"output": output[:2000]}
    )


def check_pytest(path: str = "tests/", markers: str = None) -> CheckResult:
    """Run pytest."""
    cmd = ["pytest", path, "-v", "--tb=short"]
    if markers:
        cmd.extend(["-m", markers])

    success, output = run_command(cmd)
    return CheckResult(
        name="pytest",
        status=CheckStatus.PASSED if success else CheckStatus.FAILED,
        message="Tests passed" if success else "Tests failed",
        details={"output": output[-2000:]}  # Last part (results)
    )


def check_bandit(path: str = ".") -> CheckResult:
    """Run Bandit security scanner."""
    success, output = run_command(["bandit", "-r", path, "-ll"])
    return CheckResult(
        name="bandit",
        status=CheckStatus.PASSED if success else CheckStatus.FAILED,
        message="Security scan passed" if success else "Security issues found",
        details={"output": output[:2000]}
    )


def check_isort(path: str = ".", check_only: bool = True) -> CheckResult:
    """Run isort import checker."""
    cmd = ["isort", "--check-only", path] if check_only else ["isort", path]
    success, output = run_command(cmd)
    return CheckResult(
        name="isort",
        status=CheckStatus.PASSED if success else CheckStatus.FAILED,
        message="Import sorting passed" if success else "Import sorting issues",
        details={"output": output[:2000]}
    )


def check_docstring_coverage(path: str = "src/") -> CheckResult:
    """Check docstring coverage."""
    import ast

    total_items = 0
    documented_items = 0
    missing = []

    path_obj = Path(path)
    for py_file in path_obj.rglob("*.py"):
        try:
            with open(py_file, 'r') as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    total_items += 1
                    docstring = ast.get_docstring(node)
                    if docstring:
                        documented_items += 1
                    else:
                        missing.append(f"{py_file}:{node.lineno}:{node.name}")

        except Exception:
            continue

    if total_items == 0:
        coverage = 100.0
    else:
        coverage = (documented_items / total_items) * 100

    # Pass if > 80% coverage
    passed = coverage >= 80

    return CheckResult(
        name="docstrings",
        status=CheckStatus.PASSED if passed else CheckStatus.FAILED,
        message=f"Docstring coverage: {coverage:.1f}%",
        details={
            "coverage": coverage,
            "total": total_items,
            "documented": documented_items,
            "missing_sample": missing[:10]  # First 10 missing
        }
    )


def check_no_debug(path: str = "src/") -> CheckResult:
    """Check for debug statements."""
    import re

    debug_patterns = [
        r'\bprint\s*\(',
        r'\bbreakpoint\s*\(',
        r'\bpdb\.set_trace\s*\(',
        r'\bimport\s+pdb\b',
        r'\bdebugger\b',
    ]

    findings = []
    path_obj = Path(path)

    for py_file in path_obj.rglob("*.py"):
        try:
            with open(py_file, 'r') as f:
                for i, line in enumerate(f, 1):
                    for pattern in debug_patterns:
                        if re.search(pattern, line):
                            findings.append(f"{py_file}:{i}")
                            break
        except Exception:
            continue

    return CheckResult(
        name="no_debug",
        status=CheckStatus.PASSED if not findings else CheckStatus.FAILED,
        message="No debug statements" if not findings else f"Found {len(findings)} debug statements",
        details={"findings": findings[:20]}  # First 20
    )


def check_todo_fixme(path: str = "src/") -> CheckResult:
    """Check for TODO/FIXME comments."""
    import re

    patterns = [r'\bTODO\b', r'\bFIXME\b', r'\bHACK\b', r'\bXXX\b']
    findings = []
    path_obj = Path(path)

    for py_file in path_obj.rglob("*.py"):
        try:
            with open(py_file, 'r') as f:
                for i, line in enumerate(f, 1):
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            findings.append({
                                "file": str(py_file),
                                "line": i,
                                "content": line.strip()[:100]
                            })
                            break
        except Exception:
            continue

    # This is informational, not a failure
    return CheckResult(
        name="todo_fixme",
        status=CheckStatus.PASSED,
        message=f"Found {len(findings)} TODO/FIXME comments",
        details={"count": len(findings), "items": findings[:10]}
    )


# Pre-configured runner


def create_standard_runner(project_root: str = ".") -> PrecommitRunner:
    """
    Create a pre-configured pre-commit runner.

    Includes:
    - Ruff linting
    - Black formatting
    - MyPy type checking
    - isort import sorting
    - Bandit security
    - Docstring coverage
    - Debug statement check
    """
    runner = PrecommitRunner(project_root)

    runner.add_check("ruff", lambda: check_ruff(project_root))
    runner.add_check("black", lambda: check_black(project_root))
    runner.add_check("mypy", lambda: check_mypy(project_root))
    runner.add_check("isort", lambda: check_isort(project_root))
    runner.add_check("bandit", lambda: check_bandit(f"{project_root}/src"))
    runner.add_check("docstrings", lambda: check_docstring_coverage(f"{project_root}/src"))
    runner.add_check("no_debug", lambda: check_no_debug(f"{project_root}/src"))
    runner.add_check("todo_fixme", lambda: check_todo_fixme(f"{project_root}/src"))

    return runner


def create_fast_runner(project_root: str = ".") -> PrecommitRunner:
    """Create a fast pre-commit runner (no tests)."""
    runner = PrecommitRunner(project_root)

    runner.add_check("ruff", lambda: check_ruff(project_root))
    runner.add_check("black", lambda: check_black(project_root))
    runner.add_check("no_debug", lambda: check_no_debug(f"{project_root}/src"))

    return runner


# Pre-commit hook script generator


def generate_precommit_hook() -> str:
    """Generate a git pre-commit hook script."""
    return '''#!/usr/bin/env python3
"""Git pre-commit hook for code quality checks."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.company_researcher.testing.precommit import create_fast_runner

def main():
    runner = create_fast_runner(str(project_root))
    result = runner.run()

    print("\\n" + "="*60)
    print(result.summary())
    print("="*60 + "\\n")

    for check in result.checks:
        icon = "✓" if check.status.value == "passed" else "✗"
        print(f"  {icon} {check.name}: {check.message}")

    if not result.passed:
        print("\\n❌ Pre-commit checks failed. Please fix the issues above.")
        sys.exit(1)

    print("\\n✅ All pre-commit checks passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()
'''


def install_precommit_hook(project_root: str = ".") -> bool:
    """Install the pre-commit hook."""
    hooks_dir = Path(project_root) / ".git" / "hooks"
    if not hooks_dir.exists():
        return False

    hook_path = hooks_dir / "pre-commit"
    hook_content = generate_precommit_hook()

    with open(hook_path, 'w') as f:
        f.write(hook_content)

    # Make executable (Unix)
    try:
        hook_path.chmod(0o755)
    except Exception:
        pass

    return True
