"""
Research Agents - Deep research and reasoning.

Agents for comprehensive research:
- DeepResearchAgent: Multi-iteration deep research
- ReasoningAgent: Strategic reasoning and hypothesis testing
- TrendAnalystAgent: Trend analysis and forecasting
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
from .trend_analyst import (
    TrendAnalystAgent,
    trend_analyst_agent_node,
    create_trend_analyst,
    TrendDirection,
    TrendStrength,
    Trend,
    Forecast,
    TrendAnalysis,
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
    # Trend Analysis
    "TrendAnalystAgent",
    "trend_analyst_agent_node",
    "create_trend_analyst",
    "TrendDirection",
    "TrendStrength",
    "Trend",
    "Forecast",
    "TrendAnalysis",
]
