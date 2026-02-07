"""
Standard types for agent results.

Provides consistent typing across all agents using TypedDict.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from typing_extensions import NotRequired, TypedDict


class AgentStatus(Enum):
    """Status of an agent execution."""

    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"
    NO_DATA = "no_data"


class TokenUsage(TypedDict):
    """Token usage for an API call."""

    input: int
    output: int


class AgentOutput(TypedDict):
    """Standard output from an individual agent."""

    analysis: str
    data_extracted: bool
    cost: float
    tokens: TokenUsage
    status: NotRequired[str]
    error: NotRequired[str]
    sources_used: NotRequired[int]
    confidence: NotRequired[float]


class AgentResult(TypedDict):
    """Standardized result from an agent node function."""

    agent_outputs: Dict[str, AgentOutput]
    total_cost: float
    total_tokens: TokenUsage
    # Optional extensions for specific agents
    company_overview: NotRequired[str]
    notes: NotRequired[List[str]]
    sources: NotRequired[List[Dict[str, Any]]]
    quality_score: NotRequired[float]


class SearchResult(TypedDict):
    """Standard format for search results."""

    title: str
    url: str
    content: str
    score: NotRequired[float]


@dataclass
class AgentConfig:
    """Configuration for an individual agent."""

    max_tokens: int = 1000
    temperature: float = 0.0
    max_retries: int = 3
    timeout: float = 30.0
    # Agent-specific settings
    max_sources: int = 15
    content_truncate_length: int = 500


@dataclass
class AgentContext:
    """Context passed to agent execution."""

    company_name: str
    search_results: List[SearchResult] = field(default_factory=list)
    config: AgentConfig = field(default_factory=AgentConfig)
    metadata: Dict[str, Any] = field(default_factory=dict)


def create_empty_result(
    agent_name: str,
    message: str = "No search results available",
    status: AgentStatus = AgentStatus.NO_DATA,
) -> AgentResult:
    """Create an empty/error result for an agent."""
    return {
        "agent_outputs": {
            agent_name: {
                "analysis": message,
                "data_extracted": False,
                "cost": 0.0,
                "tokens": {"input": 0, "output": 0},
                "status": status.value,
            }
        },
        "total_cost": 0.0,
        "total_tokens": {"input": 0, "output": 0},
    }


def create_agent_result(
    agent_name: str,
    analysis: str,
    input_tokens: int,
    output_tokens: int,
    cost: float,
    status: AgentStatus = AgentStatus.SUCCESS,
    sources_used: int = 0,
    confidence: Optional[float] = None,
    **extra_fields,
) -> AgentResult:
    """Create a standardized agent result."""
    agent_output: AgentOutput = {
        "analysis": analysis,
        "data_extracted": status == AgentStatus.SUCCESS,
        "cost": cost,
        "tokens": {"input": input_tokens, "output": output_tokens},
        "status": status.value,
        "sources_used": sources_used,
    }

    if confidence is not None:
        agent_output["confidence"] = confidence

    result: AgentResult = {
        "agent_outputs": {agent_name: agent_output},
        "total_cost": cost,
        "total_tokens": {"input": input_tokens, "output": output_tokens},
    }

    # Add any extra fields (dynamic key access is valid at runtime for TypedDict)
    for key, value in extra_fields.items():
        if value is not None:
            result[key] = value  # type: ignore[literal-required]

    return result


def merge_agent_results(*results: AgentResult) -> AgentResult:
    """Merge multiple agent results into one."""
    merged: AgentResult = {
        "agent_outputs": {},
        "total_cost": 0.0,
        "total_tokens": {"input": 0, "output": 0},
    }

    for result in results:
        # Merge agent outputs
        merged["agent_outputs"].update(result.get("agent_outputs", {}))

        # Sum costs and tokens
        merged["total_cost"] += result.get("total_cost", 0.0)
        tokens = result.get("total_tokens", {"input": 0, "output": 0})
        merged["total_tokens"]["input"] += tokens.get("input", 0)
        merged["total_tokens"]["output"] += tokens.get("output", 0)

        # Carry forward optional fields from last result that has them
        # (dynamic key access is valid at runtime for TypedDict)
        for field in ["company_overview", "notes", "sources", "quality_score"]:
            if field in result and result[field] is not None:  # type: ignore[literal-required]
                merged[field] = result[field]  # type: ignore[literal-required]

    return merged
