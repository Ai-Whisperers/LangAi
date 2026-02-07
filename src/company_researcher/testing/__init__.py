"""
Testing Utilities Module for Company Researcher.

Provides comprehensive testing support:
- Evaluation datasets
- Evaluation runners
- Graph visualization
- Test fixtures
- Snapshot testing
- Property-based testing
"""

from .eval_dataset import (
    EvalCase,
    EvalDataset,
    EvalResult,
    create_research_dataset,
    load_dataset,
    save_dataset,
)
from .eval_runner import EvalConfig, EvalMetrics, EvalRunner, compare_evaluations, run_evaluation
from .fixtures import MockLLM, MockTool, mock_llm_response, mock_research_state, mock_tool_result
from .graph_visualizer import GraphVisualizer, export_to_json, export_to_mermaid, visualize_workflow
from .precommit import (
    CheckResult,
    CheckStatus,
    PrecommitResult,
    PrecommitRunner,
    check_bandit,
    check_black,
    check_docstring_coverage,
    check_isort,
    check_mypy,
    check_no_debug,
    check_pytest,
    check_ruff,
    create_fast_runner,
    create_standard_runner,
    install_precommit_hook,
)
from .property_testing import (
    Gen,
    PropertyTestResult,
    ResearchGen,
    check_property,
    given,
    is_associative,
    is_commutative,
    is_idempotent,
    preserves_invariant,
)
from .snapshot import SnapshotManager, snapshot_test, update_snapshots

__all__ = [
    # Eval Dataset
    "EvalDataset",
    "EvalCase",
    "EvalResult",
    "create_research_dataset",
    "load_dataset",
    "save_dataset",
    # Eval Runner
    "EvalRunner",
    "EvalConfig",
    "EvalMetrics",
    "run_evaluation",
    "compare_evaluations",
    # Graph Visualizer
    "GraphVisualizer",
    "visualize_workflow",
    "export_to_mermaid",
    "export_to_json",
    # Fixtures
    "mock_llm_response",
    "mock_tool_result",
    "mock_research_state",
    "MockLLM",
    "MockTool",
    # Snapshot
    "SnapshotManager",
    "snapshot_test",
    "update_snapshots",
    # Property Testing
    "Gen",
    "ResearchGen",
    "PropertyTestResult",
    "given",
    "check_property",
    "is_idempotent",
    "is_commutative",
    "is_associative",
    "preserves_invariant",
    # Pre-commit
    "PrecommitRunner",
    "PrecommitResult",
    "CheckResult",
    "CheckStatus",
    "check_ruff",
    "check_black",
    "check_mypy",
    "check_pytest",
    "check_bandit",
    "check_isort",
    "check_docstring_coverage",
    "check_no_debug",
    "create_standard_runner",
    "create_fast_runner",
    "install_precommit_hook",
]
