"""
Company Research Graph for LangGraph Studio.

This module exports the comprehensive research workflow as a compiled graph
that can be visualized and executed in LangGraph Studio.
"""

from company_researcher.workflows.comprehensive_research import create_comprehensive_workflow

# Create and compile the workflow for LangGraph Studio
workflow = create_comprehensive_workflow()
graph = workflow.compile()

# Export for LangGraph Studio
__all__ = ["graph", "workflow"]
