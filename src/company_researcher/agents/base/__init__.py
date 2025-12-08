"""
Base Agent Infrastructure.

Provides common functionality for all agents:
- Standardized types (AgentResult, AgentOutput, etc.)
- Centralized logging (AgentLogger)
- Base node class and decorator (BaseAgentNode, @agent_node)
- Utility functions for common operations

This module eliminates code duplication across 19+ agent files.

Usage:
    from company_researcher.agents.base import (
        # Types
        AgentResult,
        AgentOutput,
        AgentConfig,
        AgentStatus,
        create_agent_result,
        create_empty_result,
        merge_agent_results,

        # Logging
        AgentLogger,
        get_agent_logger,
        configure_agent_logging,

        # Node infrastructure
        BaseAgentNode,
        agent_node,
        format_search_results,
    )

Example - Using decorator:
    @agent_node("financial", max_tokens=800)
    def financial_agent_node(state, logger, client, config, node_config, formatted_results, company_name):
        prompt = PROMPT.format(company_name=company_name, results=formatted_results)
        return client.messages.create(
            model=config.llm_model,
            max_tokens=node_config.max_tokens,
            temperature=node_config.temperature,
            messages=[{"role": "user", "content": prompt}]
        )

Example - Using class:
    class FinancialAgentNode(BaseAgentNode):
        agent_name = "financial"
        max_tokens = 800

        def get_prompt(self, company_name, formatted_results, **kwargs):
            return PROMPT.format(...)
"""

# Types
from .types import (
    # Enums
    AgentStatus,
    # TypedDicts
    TokenUsage,
    AgentOutput,
    AgentResult,
    SearchResult,
    # Dataclasses
    AgentConfig,
    AgentContext,
    # Factory functions
    create_empty_result,
    create_agent_result,
    merge_agent_results,
)

# Logger
from .logger import (
    AgentLogger,
    AgentLogContext,
    get_agent_logger,
    configure_agent_logging,
)

# Node infrastructure
from .node import (
    BaseAgentNode,
    NodeConfig,
    agent_node,
    format_search_results,
)

__all__ = [
    # Types - Enums
    "AgentStatus",
    # Types - TypedDicts
    "TokenUsage",
    "AgentOutput",
    "AgentResult",
    "SearchResult",
    # Types - Dataclasses
    "AgentConfig",
    "AgentContext",
    # Types - Factory functions
    "create_empty_result",
    "create_agent_result",
    "merge_agent_results",
    # Logger
    "AgentLogger",
    "AgentLogContext",
    "get_agent_logger",
    "configure_agent_logging",
    # Node
    "BaseAgentNode",
    "NodeConfig",
    "agent_node",
    "format_search_results",
]
