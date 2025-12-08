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
    EvalDataset,
    EvalCase,
    EvalResult,
    create_research_dataset,
    load_dataset,
    save_dataset,
)

from .eval_runner import (
    EvalRunner,
    EvalConfig,
    EvalMetrics,
    run_evaluation,
    compare_evaluations,
)

from .graph_visualizer import (
    GraphVisualizer,
    visualize_workflow,
    export_to_mermaid,
    export_to_json,
)

from .fixtures import (
    mock_llm_response,
    mock_tool_result,
    mock_research_state,
    MockLLM,
    MockTool,
)

from .snapshot import (
    SnapshotManager,
    snapshot_test,
    update_snapshots,
)

from .property_testing import (
    Gen,
    ResearchGen,
    PropertyTestResult,
    given,
    check_property,
    is_idempotent,
    is_commutative,
    is_associative,
    preserves_invariant,
)

from .precommit import (
    PrecommitRunner,
    PrecommitResult,
    CheckResult,
    CheckStatus,
    check_ruff,
    check_black,
    check_mypy,
    check_pytest,
    check_bandit,
    check_isort,
    check_docstring_coverage,
    check_no_debug,
    create_standard_runner,
    create_fast_runner,
    install_precommit_hook,
)

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
