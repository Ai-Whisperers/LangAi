"""
Canonical research runner.

Boundary rule:
- `workflows/` owns LangGraph graphs and their state transitions.
- `runner.py` owns "what to run" selection and provides stable entry points.
- `executors/` owns async/batch execution + persistence of artifacts.
- `api/` and CLI call `runner.py` (not raw workflows) to avoid duplicated logic.
"""

from __future__ import annotations

from typing import Any, Dict, Literal, Optional, Tuple

from .utils import get_logger

logger = get_logger(__name__)

ResearchType = Literal["company", "topic"]


def run_with_state(
    *,
    research_type: ResearchType,
    subject: str,
    force: bool = False,
    output_dir: Optional[str] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Run research and return (output, final_state) in a stable shape suitable for executors.
    """
    subject = (subject or "").strip()
    if not subject:
        raise ValueError("subject must be a non-empty string")

    if research_type == "topic":
        from .workflows.topic_workflow import run_topic_workflow_with_state

        output, state = run_topic_workflow_with_state(
            topic=subject, force=force, output_dir=output_dir
        )
        return output, state

    if research_type == "company":
        from .workflows.cache_aware_workflow import run_cache_aware_workflow_with_state

        # Company workflow currently derives report location from config; output_dir is reserved.
        output, state = run_cache_aware_workflow_with_state(company_name=subject, force=force)
        return output, state

    raise ValueError(f"Unsupported research_type: {research_type}")
