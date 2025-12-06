"""
Simple LangGraph example for testing LangGraph Studio

This is a minimal graph to verify Studio is working correctly.
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class SimpleState(TypedDict):
    """State for simple test graph"""
    input: str
    output: str
    step: int


def step1(state: SimpleState) -> dict:
    """First step: Process input"""
    return {
        "output": f"Processed: {state['input']}",
        "step": 1
    }


def step2(state: SimpleState) -> dict:
    """Second step: Add more processing"""
    return {
        "output": state["output"] + " | Enhanced",
        "step": 2
    }


def step3(state: SimpleState) -> dict:
    """Final step: Complete processing"""
    return {
        "output": state["output"] + " | Complete!",
        "step": 3
    }


# Build the graph
workflow = StateGraph(SimpleState)

# Add nodes
workflow.add_node("step1", step1)
workflow.add_node("step2", step2)
workflow.add_node("step3", step3)

# Add edges
workflow.add_edge(START, "step1")
workflow.add_edge("step1", "step2")
workflow.add_edge("step2", "step3")
workflow.add_edge("step3", END)

# Compile
graph = workflow.compile()


# Test function (optional - for CLI testing)
if __name__ == "__main__":
    result = graph.invoke({"input": "Hello LangGraph!", "step": 0})
    print("[OK] Graph executed successfully!")
    print(f"Output: {result['output']}")
    print(f"Steps completed: {result['step']}")
