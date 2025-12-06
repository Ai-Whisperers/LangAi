"""
Research Agents - Deep research and reasoning.

Agents for comprehensive research:
- DeepResearchAgent: Multi-iteration deep research
- ReasoningAgent: Strategic reasoning and hypothesis testing
"""

from .deep_research import (
    DeepResearchAgent,
    deep_research_agent_node,
    create_deep_research_agent,
    ResearchDepth,
    ResearchIteration,
)
from .reasoning import (
    ReasoningAgent,
    reasoning_agent_node,
    create_reasoning_agent,
    ReasoningType,
    Hypothesis,
)

__all__ = [
    # Deep Research
    "DeepResearchAgent",
    "deep_research_agent_node",
    "create_deep_research_agent",
    "ResearchDepth",
    "ResearchIteration",
    # Reasoning
    "ReasoningAgent",
    "reasoning_agent_node",
    "create_reasoning_agent",
    "ReasoningType",
    "Hypothesis",
]
