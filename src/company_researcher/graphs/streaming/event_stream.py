"""
Event Streaming - Phase 13

Provides real-time streaming of workflow events and LLM outputs.

Stream Types:
- Node events: When nodes start/complete
- State updates: When state changes
- Token events: LLM token-by-token output
- Error events: When errors occur

Usage:
    async for event in stream_research("Tesla"):
        if event.type == "node_complete":
            print(f"Completed: {event.node}")
        elif event.type == "token":
            print(event.content, end="")
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, Literal, Optional

from langgraph.graph import END, StateGraph

from ...state.workflow import InputState, OutputState, OverallState, create_initial_state
from ...utils import get_logger, utc_now
from ..subgraphs import (
    create_analysis_subgraph,
    create_data_collection_subgraph,
    create_output_subgraph,
    create_quality_subgraph,
)

logger = get_logger(__name__)


# Event type literals
EventType = Literal[
    "workflow_start",
    "workflow_complete",
    "workflow_error",
    "node_start",
    "node_complete",
    "node_error",
    "state_update",
    "token",
    "progress",
]


@dataclass
class StreamEvent:
    """Represents a streaming event."""

    type: EventType
    timestamp: datetime = field(default_factory=utc_now)
    node: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    content: Optional[str] = None  # For token events
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type,
            "timestamp": self.timestamp.isoformat(),
            "node": self.node,
            "data": self.data,
            "content": self.content,
            "error": self.error,
        }


@dataclass
class StreamConfig:
    """Configuration for streaming."""

    # Event filtering
    include_node_events: bool = True
    include_state_updates: bool = True
    include_tokens: bool = False
    include_progress: bool = True

    # Throttling
    min_event_interval_ms: int = 100

    # State update filtering
    state_fields_to_stream: Optional[list] = None  # None = all fields


async def stream_research(
    company_name: str,
    config: Optional[StreamConfig] = None,
) -> AsyncGenerator[StreamEvent, None]:
    """
    Stream research workflow events.

    Yields events as the workflow progresses:
    - workflow_start: When workflow begins
    - node_start: When each node starts
    - node_complete: When each node completes
    - progress: Periodic progress updates
    - workflow_complete: When workflow finishes
    - workflow_error: If an error occurs

    Args:
        company_name: Name of company to research
        config: Optional streaming configuration

    Yields:
        StreamEvent objects
    """
    if config is None:
        config = StreamConfig()

    logger.info(f"[STREAM] Starting streaming research: {company_name}")

    # Yield workflow start event
    yield StreamEvent(
        type="workflow_start",
        data={
            "company_name": company_name,
            "message": f"Starting research for {company_name}",
        },
    )

    # Build workflow
    graph = StateGraph(OverallState, input=InputState, output=OutputState)

    # Add subgraphs
    graph.add_node("data_collection", create_data_collection_subgraph())
    graph.add_node("analysis", create_analysis_subgraph())
    graph.add_node("quality", create_quality_subgraph())
    graph.add_node("output", create_output_subgraph())

    graph.set_entry_point("data_collection")
    graph.add_edge("data_collection", "analysis")
    graph.add_edge("analysis", "quality")
    graph.add_edge("quality", "output")
    graph.add_edge("output", END)

    compiled = graph.compile()

    # Initial state
    initial_state = create_initial_state(company_name)

    try:
        # Stream workflow execution
        async for event in compiled.astream(initial_state):
            # Each event is a dict with node name as key
            for node_name, node_output in event.items():
                if config.include_node_events:
                    yield StreamEvent(
                        type="node_complete",
                        node=node_name,
                        data={
                            "cost": node_output.get("total_cost", 0),
                            "sources": len(node_output.get("sources", [])),
                            "quality_score": node_output.get("quality_score"),
                        },
                    )

                if config.include_state_updates:
                    # Filter state fields if configured
                    state_data = {}
                    if config.state_fields_to_stream:
                        for field in config.state_fields_to_stream:
                            if field in node_output:
                                state_data[field] = node_output[field]
                    else:
                        # Include key fields
                        state_data = {
                            "company_name": node_output.get("company_name"),
                            "quality_score": node_output.get("quality_score"),
                            "total_cost": node_output.get("total_cost"),
                            "iteration_count": node_output.get("iteration_count"),
                        }

                    yield StreamEvent(
                        type="state_update",
                        node=node_name,
                        data=state_data,
                    )

        # Workflow complete
        yield StreamEvent(
            type="workflow_complete",
            data={
                "company_name": company_name,
                "message": "Research completed successfully",
            },
        )

    except Exception as e:
        logger.error(f"[STREAM] Error during streaming: {e}")
        yield StreamEvent(
            type="workflow_error",
            error=str(e),
            data={"company_name": company_name},
        )


async def stream_research_events(
    company_name: str,
    include_tokens: bool = False,
) -> AsyncGenerator[StreamEvent, None]:
    """
    Stream research with detailed event types.

    Uses LangGraph's astream_events for more detailed streaming.

    Args:
        company_name: Name of company to research
        include_tokens: Whether to stream LLM tokens

    Yields:
        StreamEvent objects
    """
    logger.info(f"[STREAM] Starting detailed event streaming: {company_name}")

    yield StreamEvent(type="workflow_start", data={"company_name": company_name})

    # Build workflow
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

    compiled = graph.compile()
    initial_state = create_initial_state(company_name)

    try:
        async for event in compiled.astream_events(initial_state, version="v2"):
            event_kind = event.get("event", "")
            event_name = event.get("name", "")

            if event_kind == "on_chain_start":
                yield StreamEvent(
                    type="node_start", node=event_name, data={"message": f"Starting {event_name}"}
                )

            elif event_kind == "on_chain_end":
                output = event.get("data", {}).get("output", {})
                yield StreamEvent(
                    type="node_complete",
                    node=event_name,
                    data={
                        "cost": output.get("total_cost", 0) if isinstance(output, dict) else 0,
                    },
                )

            elif event_kind == "on_chat_model_stream" and include_tokens:
                chunk = event.get("data", {}).get("chunk", {})
                content = getattr(chunk, "content", "") if hasattr(chunk, "content") else ""
                if content:
                    yield StreamEvent(
                        type="token",
                        content=content,
                    )

        yield StreamEvent(type="workflow_complete", data={"company_name": company_name})

    except Exception as e:
        logger.error(f"[STREAM] Error: {e}")
        yield StreamEvent(
            type="workflow_error",
            error=str(e),
        )


async def stream_to_callback(
    company_name: str,
    callback: callable,
    config: Optional[StreamConfig] = None,
) -> Dict[str, Any]:
    """
    Stream research and call callback for each event.

    Useful for integrating with existing callback-based systems.

    Args:
        company_name: Name of company to research
        callback: Async function to call with each event
        config: Optional streaming configuration

    Returns:
        Final workflow state
    """
    final_state = None

    async for event in stream_research(company_name, config):
        await callback(event)

        if event.type == "workflow_complete":
            final_state = event.data

    return final_state


# ============================================================================
# Synchronous Streaming (for non-async contexts)
# ============================================================================


def stream_research_sync(
    company_name: str,
) -> "Generator[StreamEvent, None, None]":
    """
    Synchronous streaming wrapper.

    Note: This runs the async stream in a new event loop.
    For production, prefer async streaming.

    Args:
        company_name: Name of company to research

    Yields:
        StreamEvent objects
    """
    import asyncio

    async def _collect_events():
        events = []
        async for event in stream_research(company_name):
            events.append(event)
        return events

    # Run in event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    events = loop.run_until_complete(_collect_events())

    for event in events:
        yield event


# ============================================================================
# Progress Tracking
# ============================================================================


class ProgressTracker:
    """
    Track workflow progress for UI display.

    Usage:
        tracker = ProgressTracker()

        async for event in stream_research("Tesla"):
            tracker.update(event)
            print(f"Progress: {tracker.percentage}%")
    """

    # Expected nodes in order
    NODES = [
        "data_collection",
        "analysis",
        "quality",
        "output",
    ]

    def __init__(self):
        self.completed_nodes: list = []
        self.current_node: Optional[str] = None
        self.total_cost: float = 0.0
        self.error: Optional[str] = None

    def update(self, event: StreamEvent) -> None:
        """Update progress with new event."""
        if event.type == "node_start":
            self.current_node = event.node
        elif event.type == "node_complete":
            if event.node and event.node not in self.completed_nodes:
                self.completed_nodes.append(event.node)
            self.total_cost += event.data.get("cost", 0)
            self.current_node = None
        elif event.type == "workflow_error":
            self.error = event.error

    @property
    def percentage(self) -> int:
        """Get completion percentage."""
        if not self.NODES:
            return 0
        return int(len(self.completed_nodes) / len(self.NODES) * 100)

    @property
    def status(self) -> str:
        """Get current status string."""
        if self.error:
            return f"Error: {self.error}"
        elif self.current_node:
            return f"Running: {self.current_node}"
        elif self.percentage >= 100:
            return "Complete"
        else:
            return "In Progress"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "percentage": self.percentage,
            "status": self.status,
            "current_node": self.current_node,
            "completed_nodes": self.completed_nodes,
            "total_cost": self.total_cost,
            "error": self.error,
        }
