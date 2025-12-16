"""
Simple Test Graph for LangGraph Studio.

A minimal graph for testing LangGraph Studio connectivity.
"""

from typing import TypedDict

from langgraph.graph import END, StateGraph


class SimpleState(TypedDict):
    """Simple state for testing."""

    company_name: str
    result: str
    step_count: int


def start_node(state: SimpleState) -> dict:
    """Initial node."""
    return {"result": f"Starting research for: {state['company_name']}", "step_count": 1}


def process_node(state: SimpleState) -> dict:
    """Processing node."""
    return {"result": f"Processing: {state['company_name']}", "step_count": state["step_count"] + 1}


def finish_node(state: SimpleState) -> dict:
    """Final node."""
    return {
        "result": f"Completed research for: {state['company_name']} in {state['step_count']} steps",
        "step_count": state["step_count"] + 1,
    }


def create_simple_graph() -> StateGraph:
    """Create a simple test graph."""
    workflow = StateGraph(SimpleState)

    # Add nodes
    workflow.add_node("start", start_node)
    workflow.add_node("process", process_node)
    workflow.add_node("finish", finish_node)

    # Add edges
    workflow.set_entry_point("start")
    workflow.add_edge("start", "process")
    workflow.add_edge("process", "finish")
    workflow.add_edge("finish", END)

    return workflow


# Create and compile for LangGraph Studio
workflow = create_simple_graph()
graph = workflow.compile()

__all__ = ["graph", "workflow"]
