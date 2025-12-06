"""
LangGraph Workflow Graphs for Company Researcher.

This module contains LangGraph-based workflows for company research:
- research_graph: Complete company research pipeline
- simple_graph: Simple test graph for LangGraph Studio

Usage:
    from company_researcher.graphs import research_graph, simple_graph

    # Run research graph
    result = research_graph.invoke({"company_name": "Tesla"})

    # Run simple test graph
    result = simple_graph.invoke({"input": "test"})
"""

from .research_graph import (
    graph as research_graph,
    ResearchState,
    node_generate_queries,
    node_search_web,
    node_extract_data,
    node_generate_report,
)

from .simple_graph import (
    graph as simple_graph,
    SimpleState,
)

__all__ = [
    # Research graph
    "research_graph",
    "ResearchState",
    "node_generate_queries",
    "node_search_web",
    "node_extract_data",
    "node_generate_report",
    # Simple graph
    "simple_graph",
    "SimpleState",
]
