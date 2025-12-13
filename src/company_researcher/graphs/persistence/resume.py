"""
Resume Functionality - Phase 12

Provides workflow resume capabilities for interrupted research:
- Resume from last checkpoint
- Inspect workflow state at any point
- List and manage checkpoints
- Delete old checkpoints

Usage:
    from company_researcher.graphs.persistence import (
        research_with_checkpoint,
        resume_research,
        get_workflow_state,
        list_checkpoints,
    )

    # Start research with checkpointing
    result, thread_id = research_with_checkpoint("Tesla")

    # If interrupted, resume later
    result = resume_research(thread_id)

    # Inspect state
    state = get_workflow_state(thread_id)
    print(f"Current node: {state.next}")
    print(f"Quality score: {state.values.get('quality_score')}")
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import uuid

from ..main_graph import create_research_workflow, WorkflowConfig
from .checkpointer import get_checkpointer, CheckpointerConfig
from ...state.workflow import (
    OverallState,
    InputState,
    OutputState,
    create_initial_state,
    create_output_state,
)
from ...utils import get_logger, utc_now

logger = get_logger(__name__)


@dataclass
class CheckpointInfo:
    """Information about a workflow checkpoint."""

    thread_id: str
    company_name: str
    checkpoint_id: str
    created_at: datetime
    current_node: Optional[str]
    quality_score: Optional[float]
    iteration_count: int
    status: str  # "in_progress", "completed", "interrupted"


def research_with_checkpoint(
    company_name: str,
    thread_id: Optional[str] = None,
    config: Optional[WorkflowConfig] = None,
    checkpointer_config: Optional[CheckpointerConfig] = None,
) -> Tuple[OutputState, str]:
    """
    Research a company with automatic checkpointing.

    Checkpoints are saved after each node, allowing resume if interrupted.

    Args:
        company_name: Name of company to research
        thread_id: Optional thread ID (generates new if not provided)
        config: Optional workflow configuration
        checkpointer_config: Optional checkpointer configuration

    Returns:
        Tuple of (OutputState, thread_id) for potential resume
    """
    # Generate thread ID if not provided
    if thread_id is None:
        thread_id = f"research_{company_name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

    print(f"\n{'='*60}")
    print(f"[CHECKPOINT] Research with persistence: {company_name}")
    print(f"[CHECKPOINT] Thread ID: {thread_id}")
    print(f"{'='*60}")

    # Get checkpointer
    checkpointer = get_checkpointer(
        config=checkpointer_config
    ) if checkpointer_config else get_checkpointer()

    # Create workflow with checkpointing
    if config is None:
        config = WorkflowConfig.standard()

    workflow_builder = create_research_workflow.__wrapped__ if hasattr(
        create_research_workflow, '__wrapped__'
    ) else None

    # We need to get uncompiled graph, compile with checkpointer
    from ..main_graph import create_research_workflow as _create_workflow
    from langgraph.graph import StateGraph

    # Create workflow config
    workflow = _create_workflow(config)

    # Recompile with checkpointer
    # Note: This is a workaround since workflow is already compiled
    # In production, you'd want to compile once with checkpointer
    from ..subgraphs import (
        create_data_collection_subgraph,
        create_analysis_subgraph,
        create_quality_subgraph,
        create_output_subgraph,
    )
    from langgraph.graph import END

    graph = StateGraph(OverallState, input=InputState, output=OutputState)

    data_collection = create_data_collection_subgraph()
    analysis = create_analysis_subgraph()
    quality = create_quality_subgraph()
    output = create_output_subgraph()

    graph.add_node("data_collection", data_collection)
    graph.add_node("analysis", analysis)
    graph.add_node("quality", quality)
    graph.add_node("output", output)

    graph.set_entry_point("data_collection")
    graph.add_edge("data_collection", "analysis")
    graph.add_edge("analysis", "quality")

    def should_iterate(state: OverallState) -> str:
        quality_score = state.get("quality_score", 0)
        iteration_count = state.get("iteration_count", 0)
        if quality_score >= 85 or iteration_count >= 2:
            return "complete"
        return "iterate"

    graph.add_conditional_edges(
        "quality",
        should_iterate,
        {"iterate": "data_collection", "complete": "output"}
    )
    graph.add_edge("output", END)

    compiled = graph.compile(checkpointer=checkpointer)

    # Configuration for this thread
    run_config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    # Create initial state
    initial_state = create_initial_state(company_name)

    try:
        # Run workflow
        final_state = compiled.invoke(initial_state, config=run_config)

        # Convert to output
        output = create_output_state(final_state)

        print(f"\n[CHECKPOINT] Research completed successfully")
        print(f"[CHECKPOINT] Thread ID for reference: {thread_id}")

        return output, thread_id

    except KeyboardInterrupt:
        print(f"\n[CHECKPOINT] Research interrupted!")
        print(f"[CHECKPOINT] Resume with: resume_research('{thread_id}')")
        raise

    except Exception as e:
        logger.error(f"[CHECKPOINT] Research failed: {e}")
        print(f"\n[CHECKPOINT] Research failed, can resume with: resume_research('{thread_id}')")
        raise


def resume_research(
    thread_id: str,
    checkpointer_config: Optional[CheckpointerConfig] = None,
) -> OutputState:
    """
    Resume an interrupted research workflow.

    Args:
        thread_id: Thread ID from previous research
        checkpointer_config: Optional checkpointer configuration

    Returns:
        OutputState with results

    Raises:
        ValueError: If thread_id not found or already completed
    """
    print(f"\n{'='*60}")
    print(f"[RESUME] Resuming research: {thread_id}")
    print(f"{'='*60}")

    # Get checkpointer
    checkpointer = get_checkpointer(
        config=checkpointer_config
    ) if checkpointer_config else get_checkpointer()

    # Rebuild workflow with same checkpointer
    from ..subgraphs import (
        create_data_collection_subgraph,
        create_analysis_subgraph,
        create_quality_subgraph,
        create_output_subgraph,
    )
    from langgraph.graph import StateGraph, END

    graph = StateGraph(OverallState, input=InputState, output=OutputState)

    graph.add_node("data_collection", create_data_collection_subgraph())
    graph.add_node("analysis", create_analysis_subgraph())
    graph.add_node("quality", create_quality_subgraph())
    graph.add_node("output", create_output_subgraph())

    graph.set_entry_point("data_collection")
    graph.add_edge("data_collection", "analysis")
    graph.add_edge("analysis", "quality")

    def should_iterate(state: OverallState) -> str:
        quality_score = state.get("quality_score", 0)
        iteration_count = state.get("iteration_count", 0)
        if quality_score >= 85 or iteration_count >= 2:
            return "complete"
        return "iterate"

    graph.add_conditional_edges(
        "quality",
        should_iterate,
        {"iterate": "data_collection", "complete": "output"}
    )
    graph.add_edge("output", END)

    compiled = graph.compile(checkpointer=checkpointer)

    # Configuration
    run_config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    # Get current state
    state = compiled.get_state(run_config)

    if state.values is None:
        raise ValueError(f"No checkpoint found for thread: {thread_id}")

    if state.next is None or len(state.next) == 0:
        print("[RESUME] Workflow already completed")
        return create_output_state(state.values)

    print(f"[RESUME] Found checkpoint at: {state.next}")
    print(f"[RESUME] Company: {state.values.get('company_name', 'Unknown')}")
    print(f"[RESUME] Quality: {state.values.get('quality_score', 'N/A')}")
    print(f"[RESUME] Iterations: {state.values.get('iteration_count', 0)}")

    # Resume execution
    final_state = compiled.invoke(None, config=run_config)

    output = create_output_state(final_state)

    print(f"\n[RESUME] Research resumed and completed!")

    return output


def get_workflow_state(
    thread_id: str,
    checkpointer_config: Optional[CheckpointerConfig] = None,
) -> Dict[str, Any]:
    """
    Get the current state of a workflow.

    Args:
        thread_id: Thread ID of the workflow
        checkpointer_config: Optional checkpointer configuration

    Returns:
        Dictionary with state information
    """
    checkpointer = get_checkpointer(
        config=checkpointer_config
    ) if checkpointer_config else get_checkpointer()

    # Rebuild minimal workflow just to get state
    from langgraph.graph import StateGraph, END

    graph = StateGraph(OverallState, input=InputState, output=OutputState)
    graph.add_node("placeholder", lambda x: x)
    graph.set_entry_point("placeholder")
    graph.add_edge("placeholder", END)

    compiled = graph.compile(checkpointer=checkpointer)

    run_config = {"configurable": {"thread_id": thread_id}}

    state = compiled.get_state(run_config)

    if state.values is None:
        return {"error": "No checkpoint found", "thread_id": thread_id}

    return {
        "thread_id": thread_id,
        "company_name": state.values.get("company_name", "Unknown"),
        "current_node": state.next[0] if state.next else None,
        "is_completed": state.next is None or len(state.next) == 0,
        "quality_score": state.values.get("quality_score"),
        "iteration_count": state.values.get("iteration_count", 0),
        "total_cost": state.values.get("total_cost", 0.0),
        "sources_count": len(state.values.get("sources", [])),
        "values": state.values,
    }


def list_checkpoints(
    company_name: Optional[str] = None,
    checkpointer_config: Optional[CheckpointerConfig] = None,
) -> List[CheckpointInfo]:
    """
    List available checkpoints.

    Note: This requires SQLite backend and direct database access.

    Args:
        company_name: Optional filter by company name
        checkpointer_config: Optional checkpointer configuration

    Returns:
        List of CheckpointInfo objects
    """
    # This is a simplified implementation
    # Full implementation would query the checkpoint database directly

    logger.info("[CHECKPOINT] Listing checkpoints...")

    # For now, return empty list with a note
    # Full implementation would iterate through SQLite database
    logger.warning(
        "[CHECKPOINT] Full checkpoint listing requires direct database access. "
        "Use get_workflow_state(thread_id) if you know the thread ID."
    )

    return []


def delete_checkpoint(
    thread_id: str,
    checkpointer_config: Optional[CheckpointerConfig] = None,
) -> bool:
    """
    Delete a checkpoint.

    Args:
        thread_id: Thread ID to delete
        checkpointer_config: Optional checkpointer configuration

    Returns:
        True if deleted, False if not found
    """
    logger.info(f"[CHECKPOINT] Deleting checkpoint: {thread_id}")

    # This would require direct database access
    # For now, log a warning
    logger.warning(
        "[CHECKPOINT] Checkpoint deletion requires direct database access. "
        "Delete the checkpoint database file to clear all checkpoints."
    )

    return False


# ============================================================================
# Async Support
# ============================================================================

async def async_research_with_checkpoint(
    company_name: str,
    thread_id: Optional[str] = None,
) -> Tuple[OutputState, str]:
    """
    Async version of research_with_checkpoint.

    Args:
        company_name: Name of company to research
        thread_id: Optional thread ID

    Returns:
        Tuple of (OutputState, thread_id)
    """
    from .checkpointer import get_async_checkpointer

    if thread_id is None:
        thread_id = f"research_{company_name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"

    logger.info(f"[ASYNC] Starting async research: {company_name}")

    checkpointer = await get_async_checkpointer()

    # Build workflow
    from ..subgraphs import (
        create_data_collection_subgraph,
        create_analysis_subgraph,
        create_quality_subgraph,
        create_output_subgraph,
    )
    from langgraph.graph import StateGraph, END

    graph = StateGraph(OverallState, input=InputState, output=OutputState)

    graph.add_node("data_collection", create_data_collection_subgraph())
    graph.add_node("analysis", create_analysis_subgraph())
    graph.add_node("quality", create_quality_subgraph())
    graph.add_node("output", create_output_subgraph())

    graph.set_entry_point("data_collection")
    graph.add_edge("data_collection", "analysis")
    graph.add_edge("analysis", "quality")
    graph.add_edge("quality", "output")
    graph.add_edge("output", END)

    compiled = graph.compile(checkpointer=checkpointer)

    run_config = {"configurable": {"thread_id": thread_id}}
    initial_state = create_initial_state(company_name)

    final_state = await compiled.ainvoke(initial_state, config=run_config)
    output = create_output_state(final_state)

    return output, thread_id


async def async_resume_research(thread_id: str) -> OutputState:
    """
    Async version of resume_research.

    Args:
        thread_id: Thread ID to resume

    Returns:
        OutputState with results
    """
    from .checkpointer import get_async_checkpointer

    logger.info(f"[ASYNC] Resuming research: {thread_id}")

    checkpointer = await get_async_checkpointer()

    # Build workflow (same as async_research_with_checkpoint)
    from ..subgraphs import (
        create_data_collection_subgraph,
        create_analysis_subgraph,
        create_quality_subgraph,
        create_output_subgraph,
    )
    from langgraph.graph import StateGraph, END

    graph = StateGraph(OverallState, input=InputState, output=OutputState)

    graph.add_node("data_collection", create_data_collection_subgraph())
    graph.add_node("analysis", create_analysis_subgraph())
    graph.add_node("quality", create_quality_subgraph())
    graph.add_node("output", create_output_subgraph())

    graph.set_entry_point("data_collection")
    graph.add_edge("data_collection", "analysis")
    graph.add_edge("analysis", "quality")
    graph.add_edge("quality", "output")
    graph.add_edge("output", END)

    compiled = graph.compile(checkpointer=checkpointer)

    run_config = {"configurable": {"thread_id": thread_id}}

    final_state = await compiled.ainvoke(None, config=run_config)
    output = create_output_state(final_state)

    return output
