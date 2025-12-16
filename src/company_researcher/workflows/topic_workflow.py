"""
Topic research workflow.

This is a LangGraph StateGraph workflow that researches *general topics* (not just companies),
collects:
- web sources (SearchRouter)
- latest news sources (NewsProvider)
- related GitHub repositories (GitHubClient)
and synthesizes a beginner → state-of-the-art report with citations.
"""

from __future__ import annotations

from typing import Optional, Tuple

from langgraph.graph import END, StateGraph

from ..cache import get_cache
from ..state.workflow import (
    InputState,
    OutputState,
    OverallState,
    create_initial_state,
    create_output_state,
)
from ..utils import get_logger
from .nodes.topic_nodes import (
    discover_github_repos_node,
    fetch_topic_news_node,
    generate_topic_plan_node,
    refine_topic_report_node,
    synthesize_topic_report_node,
    topic_quality_check_node,
    topic_search_node,
)
from .nodes.topic_output_nodes import make_save_topic_report_node

logger = get_logger(__name__)


def _route_after_quality(state: OverallState) -> str:
    passed = bool(state.get("topic_quality_passed"))
    iterations = int(state.get("iteration_count") or 0)
    if passed:
        return "node_save_topic_report"
    if iterations >= 1:
        # Avoid infinite loops; save best-effort.
        return "node_save_topic_report"
    return "node_topic_refine"


def _bump_iteration(state: OverallState) -> dict:
    return {"iteration_count": int(state.get("iteration_count") or 0) + 1}


def run_topic_workflow_with_state(
    topic: str,
    *,
    force: bool = False,  # reserved for future caching parity
    output_dir: Optional[str] = None,
) -> Tuple[OutputState, OverallState]:
    """
    Run topic research workflow and return (output, final_state).

    Args:
        topic: Topic string to research
        force: Reserved (topic caching not yet implemented)
        output_dir: Optional override for where to save the report (defaults to config.output_dir)
    """
    cache = get_cache()
    decision = cache.should_research_topic(topic, force=force)
    if not decision.get("needs_research", True):
        cached = cache.get_topic_data(topic) or {}
        report_path = str(cached.get("report_path") or "")
        state = create_initial_state(
            company_name=topic,
            research_type="topic",
            subject=topic,
        )
        state["report_path"] = report_path
        state["sources"] = cached.get("sources") or []
        state["github_repos"] = cached.get("github_repos") or []
        state["topic_news"] = cached.get("topic_news")
        state["topic_plan"] = cached.get("topic_plan")
        output = create_output_state(state)
        output["metrics"]["from_cache"] = True
        logger.info("[TOPIC] Cache hit for '%s' report=%s", topic, report_path)
        return output, state

    # IMPORTANT: We want the full final OverallState for validation/caching/CLI output.
    # Using output=OutputState makes compiled.invoke() return only the output projection.
    workflow = StateGraph(OverallState)

    # Prefix node IDs to avoid collisions with OverallState keys (LangGraph restriction).
    workflow.add_node("node_topic_plan", generate_topic_plan_node)
    workflow.add_node("node_topic_search", topic_search_node)
    workflow.add_node("node_topic_news", fetch_topic_news_node)
    workflow.add_node("node_topic_github", discover_github_repos_node)
    workflow.add_node("node_topic_synthesize", synthesize_topic_report_node)
    workflow.add_node("node_topic_quality", topic_quality_check_node)
    workflow.add_node("node_topic_refine", refine_topic_report_node)
    workflow.add_node("node_bump_iteration", _bump_iteration)
    workflow.add_node("node_save_topic_report", make_save_topic_report_node(output_dir))

    workflow.set_entry_point("node_topic_plan")
    workflow.add_edge("node_topic_plan", "node_topic_search")
    workflow.add_edge("node_topic_search", "node_topic_news")
    workflow.add_edge("node_topic_news", "node_topic_github")
    workflow.add_edge("node_topic_github", "node_topic_synthesize")
    workflow.add_edge("node_topic_synthesize", "node_topic_quality")

    workflow.add_conditional_edges(
        "node_topic_quality",
        _route_after_quality,
        {
            "node_topic_refine": "node_bump_iteration",
            "node_save_topic_report": "node_save_topic_report",
        },
    )
    workflow.add_edge("node_bump_iteration", "node_topic_refine")
    workflow.add_edge("node_topic_refine", "node_topic_quality")

    workflow.add_edge("node_save_topic_report", END)

    compiled = workflow.compile()

    initial_state = create_initial_state(
        company_name=topic,  # keep backward-compatible key populated
        research_type="topic",
        subject=topic,
    )
    final_state = compiled.invoke(initial_state)
    output = create_output_state(final_state)

    # Persist topic cache (best-effort)
    try:
        cache.store_topic_run(
            topic,
            report_path=output.get("report_path") or "",
            sources=final_state.get("sources") or [],
            github_repos=final_state.get("github_repos") or [],
            topic_news=final_state.get("topic_news"),
            topic_plan=final_state.get("topic_plan"),
        )
    except Exception:
        pass

    logger.info(
        "[TOPIC] Completed topic research for '%s' report=%s", topic, output.get("report_path")
    )
    return output, final_state
