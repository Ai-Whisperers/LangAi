"""
Evaluation Runner - Execute evaluations and collect metrics.

Provides:
- Evaluation execution
- Metrics collection
- Results comparison
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .eval_dataset import EvalCase, EvalDataset, EvalResult


@dataclass
class EvalConfig:
    """Configuration for evaluation runs."""
    timeout_seconds: float = 300.0
    max_concurrent: int = 5
    retry_on_failure: bool = False
    max_retries: int = 3
    collect_traces: bool = True
    verbose: bool = True
    fail_fast: bool = False


@dataclass
class EvalMetrics:
    """Aggregated evaluation metrics."""
    total_cases: int = 0
    passed_cases: int = 0
    failed_cases: int = 0
    error_cases: int = 0

    total_score: float = 0.0
    avg_score: float = 0.0

    total_duration_seconds: float = 0.0
    avg_duration_seconds: float = 0.0

    # Breakdown by difficulty
    by_difficulty: Dict[str, Dict[str, int]] = field(default_factory=dict)

    # Breakdown by tag
    by_tag: Dict[str, Dict[str, int]] = field(default_factory=dict)

    def calculate_aggregates(self) -> None:
        """Calculate aggregate metrics."""
        if self.total_cases > 0:
            self.avg_score = self.total_score / self.total_cases
            self.avg_duration_seconds = self.total_duration_seconds / self.total_cases

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate."""
        if self.total_cases == 0:
            return 0.0
        return self.passed_cases / self.total_cases

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "failed_cases": self.failed_cases,
            "error_cases": self.error_cases,
            "pass_rate": self.pass_rate,
            "avg_score": self.avg_score,
            "total_duration_seconds": self.total_duration_seconds,
            "avg_duration_seconds": self.avg_duration_seconds,
            "by_difficulty": self.by_difficulty,
            "by_tag": self.by_tag
        }


class EvalRunner:
    """
    Evaluation runner for executing test datasets.

    Usage:
        runner = EvalRunner(research_workflow)

        # Run evaluation
        results = await runner.run(dataset)

        # Get metrics
        metrics = runner.get_metrics()
        print(f"Pass rate: {metrics.pass_rate:.2%}")
    """

    def __init__(
        self,
        workflow: Callable,
        evaluator: Optional[Callable] = None,
        config: Optional[EvalConfig] = None
    ):
        """
        Initialize runner.

        Args:
            workflow: The workflow/function to evaluate
            evaluator: Optional custom evaluator function
            config: Evaluation configuration
        """
        self.workflow = workflow
        self.evaluator = evaluator or self._default_evaluator
        self.config = config or EvalConfig()
        self.results: List[EvalResult] = []
        self._metrics = EvalMetrics()

    async def run(
        self,
        dataset: EvalDataset,
        filter_tags: Optional[List[str]] = None,
        filter_difficulty: Optional[str] = None
    ) -> List[EvalResult]:
        """
        Run evaluation on dataset.

        Args:
            dataset: Dataset to evaluate
            filter_tags: Only run cases with these tags
            filter_difficulty: Only run cases with this difficulty

        Returns:
            List of EvalResult
        """
        # Filter cases
        cases = list(dataset)
        if filter_tags:
            cases = [c for c in cases if any(t in c.tags for t in filter_tags)]
        if filter_difficulty:
            cases = [c for c in cases if c.difficulty == filter_difficulty]

        self.results = []
        self._metrics = EvalMetrics()

        # Run evaluations
        if self.config.max_concurrent > 1:
            # Concurrent execution
            semaphore = asyncio.Semaphore(self.config.max_concurrent)
            tasks = [self._run_case_with_semaphore(case, semaphore) for case in cases]
            self.results = await asyncio.gather(*tasks)
        else:
            # Sequential execution
            for case in cases:
                result = await self._run_case(case)
                self.results.append(result)

                if self.config.fail_fast and not result.passed:
                    break

        # Calculate metrics
        self._calculate_metrics(cases)

        return self.results

    async def _run_case_with_semaphore(
        self,
        case: EvalCase,
        semaphore: asyncio.Semaphore
    ) -> EvalResult:
        """Run single case with semaphore for concurrency control."""
        async with semaphore:
            return await self._run_case(case)

    async def _run_case(self, case: EvalCase) -> EvalResult:
        """Run single evaluation case."""
        start_time = time.time()
        errors = []
        actual_output = {}

        try:
            # Run workflow with timeout
            if asyncio.iscoroutinefunction(self.workflow):
                actual_output = await asyncio.wait_for(
                    self.workflow(case.input),
                    timeout=self.config.timeout_seconds
                )
            else:
                actual_output = self.workflow(case.input)

            # Evaluate result
            passed, score, eval_errors = self.evaluator(
                case.expected_output,
                actual_output
            )
            errors.extend(eval_errors)

        except asyncio.TimeoutError:
            passed = False
            score = 0.0
            errors.append(f"Timeout after {self.config.timeout_seconds}s")

        except Exception as e:
            passed = False
            score = 0.0
            errors.append(str(e))

        duration = time.time() - start_time

        if self.config.verbose:
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {case.name} (score: {score:.2f}, {duration:.2f}s)")

        return EvalResult(
            case_id=case.id,
            passed=passed,
            score=score,
            actual_output=actual_output,
            errors=errors,
            duration_seconds=duration
        )

    def _default_evaluator(
        self,
        expected: Dict[str, Any],
        actual: Dict[str, Any]
    ) -> tuple[bool, float, List[str]]:
        """
        Default evaluator - checks if expected keys exist and match.

        Returns:
            Tuple of (passed, score, errors)
        """
        errors = []
        matches = 0
        total = len(expected)

        for key, expected_value in expected.items():
            if key not in actual:
                errors.append(f"Missing key: {key}")
                continue

            actual_value = actual[key]

            if isinstance(expected_value, bool):
                if bool(actual_value) == expected_value:
                    matches += 1
                else:
                    errors.append(f"Mismatch for {key}: expected {expected_value}, got {actual_value}")
            elif isinstance(expected_value, (int, float)):
                if abs(float(actual_value) - float(expected_value)) < 0.01:
                    matches += 1
                else:
                    errors.append(f"Mismatch for {key}: expected {expected_value}, got {actual_value}")
            elif actual_value == expected_value:
                matches += 1
            else:
                errors.append(f"Mismatch for {key}: expected {expected_value}, got {actual_value}")

        score = matches / total if total > 0 else 1.0
        passed = len(errors) == 0

        return passed, score, errors

    def _calculate_metrics(self, cases: List[EvalCase]) -> None:
        """Calculate aggregate metrics."""
        self._metrics = EvalMetrics()
        self._metrics.total_cases = len(self.results)

        for result, case in zip(self.results, cases):
            # Overall counts
            if result.passed:
                self._metrics.passed_cases += 1
            elif result.errors:
                self._metrics.error_cases += 1
            else:
                self._metrics.failed_cases += 1

            self._metrics.total_score += result.score
            self._metrics.total_duration_seconds += result.duration_seconds

            # By difficulty
            if case.difficulty not in self._metrics.by_difficulty:
                self._metrics.by_difficulty[case.difficulty] = {"passed": 0, "failed": 0}
            if result.passed:
                self._metrics.by_difficulty[case.difficulty]["passed"] += 1
            else:
                self._metrics.by_difficulty[case.difficulty]["failed"] += 1

            # By tag
            for tag in case.tags:
                if tag not in self._metrics.by_tag:
                    self._metrics.by_tag[tag] = {"passed": 0, "failed": 0}
                if result.passed:
                    self._metrics.by_tag[tag]["passed"] += 1
                else:
                    self._metrics.by_tag[tag]["failed"] += 1

        self._metrics.calculate_aggregates()

    def get_metrics(self) -> EvalMetrics:
        """Get evaluation metrics."""
        return self._metrics

    def get_results(self) -> List[EvalResult]:
        """Get all results."""
        return self.results

    def get_failed_results(self) -> List[EvalResult]:
        """Get only failed results."""
        return [r for r in self.results if not r.passed]


async def run_evaluation(
    workflow: Callable,
    dataset: EvalDataset,
    config: Optional[EvalConfig] = None
) -> tuple[List[EvalResult], EvalMetrics]:
    """
    Convenience function to run evaluation.

    Args:
        workflow: Workflow to evaluate
        dataset: Dataset to use
        config: Optional configuration

    Returns:
        Tuple of (results, metrics)
    """
    runner = EvalRunner(workflow, config=config)
    results = await runner.run(dataset)
    metrics = runner.get_metrics()
    return results, metrics


def compare_evaluations(
    eval1_metrics: EvalMetrics,
    eval2_metrics: EvalMetrics,
    eval1_name: str = "Eval 1",
    eval2_name: str = "Eval 2"
) -> Dict[str, Any]:
    """
    Compare two evaluation runs.

    Args:
        eval1_metrics: First evaluation metrics
        eval2_metrics: Second evaluation metrics
        eval1_name: Name for first evaluation
        eval2_name: Name for second evaluation

    Returns:
        Comparison dictionary
    """
    return {
        "pass_rate_delta": eval2_metrics.pass_rate - eval1_metrics.pass_rate,
        "avg_score_delta": eval2_metrics.avg_score - eval1_metrics.avg_score,
        "avg_duration_delta": eval2_metrics.avg_duration_seconds - eval1_metrics.avg_duration_seconds,
        eval1_name: eval1_metrics.to_dict(),
        eval2_name: eval2_metrics.to_dict(),
        "improved": eval2_metrics.pass_rate > eval1_metrics.pass_rate
    }
