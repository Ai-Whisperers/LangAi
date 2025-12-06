"""
LangFlow Integration for Company Researcher.

This module provides:
- Custom LangFlow components for each research agent
- Flow export/import utilities
- Server configuration and management
- Pre-built flows for common research tasks

LangFlow is a visual workflow builder for LangChain applications.
It provides a drag-and-drop interface for building AI workflows.

Usage:
    # Start LangFlow server with custom components
    from company_researcher.langflow import start_langflow_server
    start_langflow_server()

    # Export a workflow to LangFlow format
    from company_researcher.langflow import export_workflow
    flow_json = export_workflow("parallel_research")

Components Available:
    - ResearcherAgentComponent: Initial company research
    - FinancialAgentComponent: Financial analysis
    - MarketAgentComponent: Market analysis
    - ProductAgentComponent: Product analysis
    - CompetitorScoutComponent: Competitive intelligence (Phase 9)
    - SynthesizerAgentComponent: Report synthesis
    - QualityCheckerComponent: Quality validation
"""

from .components import (
    ResearcherAgentComponent,
    FinancialAgentComponent,
    MarketAgentComponent,
    ProductAgentComponent,
    CompetitorScoutComponent,
    SynthesizerAgentComponent,
    QualityCheckerComponent,
)

from .server import (
    start_langflow_server,
    get_langflow_config,
    is_langflow_available,
)

from .flows import (
    export_workflow,
    import_workflow,
    get_available_flows,
    BASIC_RESEARCH_FLOW,
    PARALLEL_RESEARCH_FLOW,
)

__all__ = [
    # Components
    "ResearcherAgentComponent",
    "FinancialAgentComponent",
    "MarketAgentComponent",
    "ProductAgentComponent",
    "CompetitorScoutComponent",
    "SynthesizerAgentComponent",
    "QualityCheckerComponent",
    # Server
    "start_langflow_server",
    "get_langflow_config",
    "is_langflow_available",
    # Flows
    "export_workflow",
    "import_workflow",
    "get_available_flows",
    "BASIC_RESEARCH_FLOW",
    "PARALLEL_RESEARCH_FLOW",
]
