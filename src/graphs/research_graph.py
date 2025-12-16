"""
Company Research Graph for LangGraph Studio.

This module exports the comprehensive research workflow as a compiled graph
that can be visualized and executed in LangGraph Studio.
"""

from company_researcher.workflows.comprehensive_research import create_comprehensive_workflow

# `create_comprehensive_workflow()` already returns a compiled LangGraph runnable.
# LangGraph Studio expects an exported variable (by default `graph`) that is runnable.
graph = create_comprehensive_workflow()

__all__ = ["graph"]
