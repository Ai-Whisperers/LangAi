"""
Human Review Workflow - Phase 15

Provides human-in-the-loop capabilities for research workflows.

Features:
- Interrupt at configurable points
- Human review UI data generation
- Approve/reject/modify decisions
- State modification before continuing

Usage:
    # CLI usage
    result = research_with_review("Tesla")
    # Workflow pauses at quality check for human review

    # API usage
    thread_id = await start_research_for_review("Tesla")
    # ... human reviews via UI ...
    result = await approve_and_continue(thread_id)
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Tuple

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from ...state.workflow import (
    InputState,
    OutputState,
    OverallState,
    create_initial_state,
    create_output_state,
)
from ...utils import get_logger, utc_now
from ..persistence import get_checkpointer
from ..subgraphs import (
    create_analysis_subgraph,
    create_data_collection_subgraph,
    create_output_subgraph,
    create_quality_subgraph,
)

logger = get_logger(__name__)


class ReviewDecision(str, Enum):
    """Human review decisions."""

    APPROVE = "approve"  # Continue to output
    REJECT = "reject"  # Stop workflow
    REVISE = "revise"  # Go back and research more
    MODIFY = "modify"  # Modify state and continue


@dataclass
class PendingReview:
    """Information about a pending human review."""

    thread_id: str
    company_name: str
    created_at: datetime
    current_node: str
    quality_score: Optional[float]
    iteration_count: int
    summary: str
    state_preview: Dict[str, Any]


@dataclass
class HumanReviewConfig:
    """Configuration for human review points."""

    # Where to interrupt
    interrupt_before_output: bool = True
    interrupt_on_low_quality: bool = True
    quality_threshold: float = 85.0

    # Review data
    include_summary: bool = True
    include_sources_preview: bool = True
    include_agent_outputs: bool = True
    max_preview_length: int = 1000

    # Timeouts
    review_timeout_hours: int = 24


# ============================================================================
# Review Nodes
# ============================================================================


def human_review_node(state: OverallState) -> Dict[str, Any]:
    """
    Node that prepares data for human review.

    This node:
    1. Generates a summary of current research
    2. Prepares preview data for UI
    3. Sets review_pending flag

    The workflow will interrupt AFTER this node for human input.

    Args:
        state: Current workflow state

    Returns:
        State update with review data
    """
    logger.info("[REVIEW] Preparing human review data...")

    company_name = state.get("company_name", "Unknown")
    quality_score = state.get("quality_score", 0)
    iteration_count = state.get("iteration_count", 0)
    company_overview = state.get("company_overview", "")
    agent_outputs = state.get("agent_outputs", {})

    # Generate summary
    summary_parts = [
        f"Research Summary for {company_name}",
        f"Quality Score: {quality_score:.1f}/100",
        f"Iterations: {iteration_count}",
        "",
    ]

    if company_overview:
        # First 500 chars of overview
        summary_parts.append("Overview Preview:")
        summary_parts.append(
            company_overview[:500] + "..." if len(company_overview) > 500 else company_overview
        )

    summary = "\n".join(summary_parts)

    # Prepare agent outputs summary
    agents_summary = {}
    for agent_name, output in agent_outputs.items():
        agents_summary[agent_name] = {
            "has_data": output.get("data_extracted", False),
            "cost": output.get("cost", 0),
            "status": output.get("status", "unknown"),
        }

    # Sources preview
    sources = state.get("sources", [])[:5]  # First 5 sources
    sources_preview = [{"title": s.get("title", ""), "url": s.get("url", "")} for s in sources]

    review_data = {
        "summary": summary,
        "agents_summary": agents_summary,
        "sources_preview": sources_preview,
        "key_metrics": state.get("key_metrics", {}),
        "competitors": state.get("competitors", []),
        "products": state.get("products_services", []),
    }

    logger.info(f"[REVIEW] Review prepared - awaiting human decision")

    return {
        "review_pending": True,
        "review_data": review_data,
        "review_created_at": utc_now().isoformat(),
    }


def apply_human_decision_node(state: OverallState) -> Dict[str, Any]:
    """
    Apply human decision to workflow state.

    Args:
        state: Current workflow state with human_decision

    Returns:
        State update based on decision
    """
    decision = state.get("human_decision", ReviewDecision.APPROVE.value)
    human_feedback = state.get("human_feedback", "")
    state_modifications = state.get("state_modifications", {})

    logger.info(f"[REVIEW] Applying human decision: {decision}")

    updates = {
        "review_pending": False,
        "human_decision_applied": True,
        "human_decision_at": utc_now().isoformat(),
    }

    if decision == ReviewDecision.MODIFY.value and state_modifications:
        # Apply any state modifications from human
        updates.update(state_modifications)
        logger.info(f"[REVIEW] Applied {len(state_modifications)} state modifications")

    if human_feedback:
        # Store feedback for audit
        updates["human_feedback_received"] = human_feedback

    return updates


# ============================================================================
# Routing Functions
# ============================================================================


def route_after_review(state: OverallState) -> str:
    """
    Route based on human decision.

    Args:
        state: Current workflow state

    Returns:
        Next node based on decision
    """
    decision = state.get("human_decision", ReviewDecision.APPROVE.value)

    if decision == ReviewDecision.APPROVE.value:
        logger.info("[ROUTE] Human approved - proceeding to output")
        return "output"
    elif decision == ReviewDecision.REVISE.value:
        logger.info("[ROUTE] Human requested revision - returning to data collection")
        return "revise"
    elif decision == ReviewDecision.REJECT.value:
        logger.info("[ROUTE] Human rejected - ending workflow")
        return "reject"
    else:  # MODIFY - continue with modifications
        logger.info("[ROUTE] Human modified - proceeding to output")
        return "output"


def should_require_review(state: OverallState) -> str:
    """
    Determine if human review is required.

    Args:
        state: Current workflow state

    Returns:
        "review" if review needed, "skip" otherwise
    """
    quality_score = state.get("quality_score", 0)
    iteration_count = state.get("iteration_count", 0)

    # Always review if quality is low after iterations
    if quality_score < 85 and iteration_count >= 2:
        logger.info("[ROUTE] Low quality after max iterations - requiring review")
        return "review"

    # Review if significant contradictions
    contradictions = state.get("contradictions", {})
    if contradictions.get("critical", 0) > 0:
        logger.info("[ROUTE] Critical contradictions - requiring review")
        return "review"

    # Default: proceed to output
    return "skip"


# ============================================================================
# Workflow Creation
# ============================================================================


def create_human_reviewed_workflow(
    config: Optional[HumanReviewConfig] = None,
    checkpointer=None,
) -> Tuple[StateGraph, Any]:
    """
    Create a workflow with human review capabilities.

    The workflow interrupts before the output node for human review.
    Use approve_and_continue() or reject_and_revise() to continue.

    Args:
        config: Optional review configuration
        checkpointer: Optional checkpointer (creates MemorySaver if None)

    Returns:
        Tuple of (compiled workflow, checkpointer)
    """
    if config is None:
        config = HumanReviewConfig()

    if checkpointer is None:
        checkpointer = MemorySaver()

    graph = StateGraph(OverallState, input=InputState, output=OutputState)

    # ========================================
    # Add Nodes
    # ========================================

    # Main workflow nodes
    graph.add_node("data_collection", create_data_collection_subgraph())
    graph.add_node("analysis", create_analysis_subgraph())
    graph.add_node("quality", create_quality_subgraph())

    # Human review nodes
    graph.add_node("human_review", human_review_node)
    graph.add_node("apply_decision", apply_human_decision_node)

    # Output node
    graph.add_node("output", create_output_subgraph())

    # Rejection end node
    def rejection_node(state: OverallState) -> Dict[str, Any]:
        return {
            "report_path": None,
            "rejection_reason": state.get("human_feedback", "Rejected by human reviewer"),
        }

    graph.add_node("rejection", rejection_node)

    # ========================================
    # Define Edges
    # ========================================

    graph.set_entry_point("data_collection")
    graph.add_edge("data_collection", "analysis")
    graph.add_edge("analysis", "quality")

    # After quality, decide if review is needed
    if config.interrupt_on_low_quality:
        graph.add_conditional_edges(
            "quality",
            should_require_review,
            {
                "review": "human_review",
                "skip": "output",
            },
        )
    else:
        graph.add_edge("quality", "human_review")

    # Human review flow
    graph.add_edge("human_review", "apply_decision")

    # After applying decision, route based on decision
    graph.add_conditional_edges(
        "apply_decision",
        route_after_review,
        {
            "output": "output",
            "revise": "data_collection",
            "reject": "rejection",
        },
    )

    # Endings
    graph.add_edge("output", END)
    graph.add_edge("rejection", END)

    # Compile with interrupt
    compiled = graph.compile(
        checkpointer=checkpointer,
        interrupt_after=["human_review"],  # Pause after review prep
    )

    return compiled, checkpointer


# ============================================================================
# Research Functions
# ============================================================================


def research_with_review(
    company_name: str,
    auto_approve_threshold: float = 90.0,
) -> OutputState:
    """
    Research a company with human review step (CLI version).

    For high-quality results (above threshold), auto-approves.
    Otherwise, prompts for human input.

    Args:
        company_name: Name of company to research
        auto_approve_threshold: Quality score for auto-approval

    Returns:
        OutputState with results
    """
    import uuid

    thread_id = f"review_{company_name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

    print(f"\n{'='*60}")
    print(f"[REVIEW] Human-Reviewed Research: {company_name}")
    print(f"[REVIEW] Thread ID: {thread_id}")
    print(f"{'='*60}")

    workflow, checkpointer = create_human_reviewed_workflow()

    config = {"configurable": {"thread_id": thread_id}}
    initial_state = create_initial_state(company_name)

    # Run until interrupt
    result = workflow.invoke(initial_state, config=config)

    # Check if interrupted
    state = workflow.get_state(config)

    if state.next and "apply_decision" in state.next:
        # Review is pending
        quality_score = state.values.get("quality_score", 0)
        review_data = state.values.get("review_data", {})

        print(f"\n{'='*60}")
        print("[REVIEW] Human Review Required")
        print(f"{'='*60}")
        print(f"Company: {company_name}")
        print(f"Quality Score: {quality_score:.1f}/100")
        print(f"\n{review_data.get('summary', 'No summary available')}")
        print(f"{'='*60}")

        # Auto-approve if quality is high
        if quality_score >= auto_approve_threshold:
            print(
                f"\n[AUTO] Quality {quality_score:.1f} >= {auto_approve_threshold}, auto-approving..."
            )
            decision = ReviewDecision.APPROVE.value
        else:
            # Prompt for decision
            print("\nOptions:")
            print("  1. approve  - Accept and generate report")
            print("  2. revise   - Research more (another iteration)")
            print("  3. reject   - Stop and discard")
            print()

            decision_input = input("Enter decision (approve/revise/reject): ").strip().lower()

            if decision_input in ("1", "approve", "a"):
                decision = ReviewDecision.APPROVE.value
            elif decision_input in ("2", "revise", "r"):
                decision = ReviewDecision.REVISE.value
            elif decision_input in ("3", "reject", "x"):
                decision = ReviewDecision.REJECT.value
            else:
                print("[REVIEW] Invalid input, defaulting to approve")
                decision = ReviewDecision.APPROVE.value

        # Update state with decision
        workflow.update_state(config, {"human_decision": decision}, as_node="human_review")

        # Continue execution
        result = workflow.invoke(None, config=config)

    return create_output_state(result)


async def start_research_for_review(company_name: str) -> str:
    """
    Start research and return thread_id for later review.

    Use this in API contexts where review happens asynchronously.

    Args:
        company_name: Name of company to research

    Returns:
        thread_id for later continuation
    """
    import uuid

    thread_id = f"review_{company_name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

    workflow, _ = create_human_reviewed_workflow()

    config = {"configurable": {"thread_id": thread_id}}
    initial_state = create_initial_state(company_name)

    # Run until interrupt
    await workflow.ainvoke(initial_state, config=config)

    logger.info(f"[REVIEW] Research started, pending review: {thread_id}")

    return thread_id


async def approve_and_continue(
    thread_id: str,
    feedback: Optional[str] = None,
) -> OutputState:
    """
    Approve pending review and continue workflow.

    Args:
        thread_id: Thread ID of pending research
        feedback: Optional human feedback

    Returns:
        OutputState with results
    """
    workflow, _ = create_human_reviewed_workflow()

    config = {"configurable": {"thread_id": thread_id}}

    # Update state with approval
    update = {"human_decision": ReviewDecision.APPROVE.value}
    if feedback:
        update["human_feedback"] = feedback

    workflow.update_state(config, update, as_node="human_review")

    # Continue execution
    result = await workflow.ainvoke(None, config=config)

    return create_output_state(result)


async def reject_and_revise(
    thread_id: str,
    feedback: Optional[str] = None,
) -> OutputState:
    """
    Reject current results and request revision.

    Args:
        thread_id: Thread ID of pending research
        feedback: Optional feedback for revision

    Returns:
        OutputState (after revision completes)
    """
    workflow, _ = create_human_reviewed_workflow()

    config = {"configurable": {"thread_id": thread_id}}

    update = {"human_decision": ReviewDecision.REVISE.value}
    if feedback:
        update["human_feedback"] = feedback

    workflow.update_state(config, update, as_node="human_review")

    # Continue - will loop back to data collection
    result = await workflow.ainvoke(None, config=config)

    return create_output_state(result)


async def modify_and_continue(
    thread_id: str,
    modifications: Dict[str, Any],
    feedback: Optional[str] = None,
) -> OutputState:
    """
    Modify state and continue workflow.

    Args:
        thread_id: Thread ID of pending research
        modifications: State fields to modify
        feedback: Optional feedback

    Returns:
        OutputState with results
    """
    workflow, _ = create_human_reviewed_workflow()

    config = {"configurable": {"thread_id": thread_id}}

    update = {
        "human_decision": ReviewDecision.MODIFY.value,
        "state_modifications": modifications,
    }
    if feedback:
        update["human_feedback"] = feedback

    workflow.update_state(config, update, as_node="human_review")

    result = await workflow.ainvoke(None, config=config)

    return create_output_state(result)


def get_pending_reviews() -> List[PendingReview]:
    """
    Get list of pending human reviews.

    Note: Requires persistent checkpointer with query support.

    Returns:
        List of PendingReview objects
    """
    # This would require database queries in production
    logger.warning(
        "[REVIEW] Listing pending reviews requires persistent storage. "
        "Use thread_id tracking in your application."
    )
    return []
