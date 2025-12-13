"""
State Types Module - Pydantic Models for Type Safety

This module provides Pydantic models for type-safe state management
in LangGraph workflows.

Benefits:
- Runtime validation of state data
- Auto-completion and type hints in IDEs
- Clear documentation of state schema
- Serialization/deserialization support

Usage:
    from company_researcher.state.types import (
        NodeOutput,
        SearchNodeOutput,
        AnalysisNodeOutput,
        QualityMetrics,
    )

    # Validate node output
    output = SearchNodeOutput(
        search_results=[...],
        sources=[...],
        total_cost=0.05
    )
"""

from typing import Dict, Any, Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class NodeStatus(str, Enum):
    """Status of a node execution."""

    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"
    SKIPPED = "skipped"
    DEGRADED = "degraded"


class CompanyType(str, Enum):
    """Type of company being researched."""

    PUBLIC_US = "public_us"
    PUBLIC_INTL = "public_intl"
    PRIVATE = "private"
    STARTUP = "startup"
    SUBSIDIARY = "subsidiary"
    UNKNOWN = "unknown"


class ResearchDepth(str, Enum):
    """Depth of research."""

    QUICK = "quick"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


# ============================================================================
# Base Models
# ============================================================================

class TokenUsage(BaseModel):
    """Token usage tracking."""

    input: int = 0
    output: int = 0

    @property
    def total(self) -> int:
        return self.input + self.output


class CostMetrics(BaseModel):
    """Cost tracking metrics."""

    total_cost: float = 0.0
    tokens: TokenUsage = Field(default_factory=TokenUsage)

    def add(self, cost: float, input_tokens: int = 0, output_tokens: int = 0) -> None:
        """Add cost and tokens."""
        self.total_cost += cost
        self.tokens.input += input_tokens
        self.tokens.output += output_tokens


# ============================================================================
# Node Output Models
# ============================================================================

class NodeOutput(BaseModel):
    """Base class for all node outputs."""

    status: NodeStatus = NodeStatus.SUCCESS
    total_cost: float = 0.0
    total_tokens: TokenUsage = Field(default_factory=TokenUsage)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    # Metadata
    node_name: Optional[str] = None
    execution_time_ms: Optional[float] = None

    # Fallback tracking
    fallback_used: bool = False
    fallback_reason: Optional[str] = None


class SearchResult(BaseModel):
    """A single search result."""

    title: str = ""
    url: str = ""
    content: str = ""
    score: float = 0.0
    source: str = ""  # Which search provider


class Source(BaseModel):
    """A source reference."""

    title: str = ""
    url: str = ""
    relevance: float = 0.0
    accessed_at: Optional[datetime] = None


class SearchNodeOutput(NodeOutput):
    """Output from search-related nodes."""

    search_results: List[SearchResult] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)
    queries_executed: int = 0
    results_count: int = 0

    @field_validator("results_count", mode="before")
    def calculate_results_count(cls, v, info):
        if v == 0 and "search_results" in info.data:
            return len(info.data["search_results"])
        return v


class ClassificationOutput(NodeOutput):
    """Output from company classification."""

    company_type: CompanyType = CompanyType.UNKNOWN
    is_public_company: bool = False
    stock_ticker: Optional[str] = None
    exchange: Optional[str] = None
    available_data_sources: List[str] = Field(default_factory=list)
    detected_region: Optional[str] = None
    detected_language: Optional[str] = None


class AnalysisOutput(NodeOutput):
    """Output from analysis nodes."""

    analysis: str = ""
    data_extracted: bool = False
    confidence: float = 0.0
    key_findings: List[str] = Field(default_factory=list)


class FinancialAnalysisOutput(AnalysisOutput):
    """Output from financial analysis."""

    revenue: Optional[str] = None
    revenue_growth: Optional[str] = None
    profitability: Optional[str] = None
    market_cap: Optional[str] = None
    employees: Optional[str] = None
    financial_health: Optional[str] = None


class MarketAnalysisOutput(AnalysisOutput):
    """Output from market analysis."""

    market_share: Optional[str] = None
    market_position: Optional[str] = None
    competitors: List[str] = Field(default_factory=list)
    competitive_advantages: List[str] = Field(default_factory=list)
    market_trends: List[str] = Field(default_factory=list)


class CompetitorOutput(AnalysisOutput):
    """Output from competitor analysis."""

    competitors_found: int = 0
    competitive_intensity: str = ""
    competitor_details: List[Dict[str, Any]] = Field(default_factory=list)


class ESGAnalysisOutput(AnalysisOutput):
    """Output from ESG analysis."""

    environmental_score: Optional[float] = None
    social_score: Optional[float] = None
    governance_score: Optional[float] = None
    overall_esg_score: Optional[float] = None
    controversies: List[str] = Field(default_factory=list)


# ============================================================================
# Quality Models
# ============================================================================

class QualityMetrics(BaseModel):
    """Quality assessment metrics."""

    overall_score: float = 0.0
    completeness_score: float = 0.0
    consistency_score: float = 0.0
    coverage_score: float = 0.0
    accuracy_score: float = 0.0

    @property
    def is_passing(self) -> bool:
        return self.overall_score >= 85.0


class Contradiction(BaseModel):
    """A detected contradiction."""

    fact1: str
    fact2: str
    topic: str
    severity: Literal["low", "medium", "high", "critical"]
    source1: Optional[str] = None
    source2: Optional[str] = None


class Gap(BaseModel):
    """A detected information gap."""

    section: str
    field: str
    description: str
    severity: Literal["low", "medium", "high", "critical"]
    recommendation: Optional[str] = None


class QualityOutput(NodeOutput):
    """Output from quality check nodes."""

    quality_score: float = 0.0
    quality_metrics: QualityMetrics = Field(default_factory=QualityMetrics)
    contradictions: List[Contradiction] = Field(default_factory=list)
    gaps: List[Gap] = Field(default_factory=list)
    should_iterate: bool = False
    iteration_reason: Optional[str] = None


# ============================================================================
# Synthesis Output
# ============================================================================

class SynthesisOutput(NodeOutput):
    """Output from synthesizer node."""

    company_overview: str = ""
    key_metrics: Dict[str, Any] = Field(default_factory=dict)
    products_services: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)
    key_insights: List[str] = Field(default_factory=list)
    specialists_combined: int = 0


# ============================================================================
# Report Output
# ============================================================================

class ReportOutput(NodeOutput):
    """Output from report generation."""

    report_path: Optional[str] = None
    report_format: str = "markdown"
    report_size_bytes: int = 0
    output_files: Dict[str, str] = Field(default_factory=dict)


# ============================================================================
# Agent Output Tracking
# ============================================================================

class AgentMetrics(BaseModel):
    """Metrics for an individual agent."""

    agent_name: str
    status: NodeStatus = NodeStatus.SUCCESS
    cost: float = 0.0
    tokens: TokenUsage = Field(default_factory=TokenUsage)
    data_extracted: bool = False
    sources_used: int = 0
    execution_time_ms: Optional[float] = None


class WorkflowMetrics(BaseModel):
    """Overall workflow metrics."""

    company_name: str
    duration_seconds: float = 0.0
    total_cost: float = 0.0
    total_tokens: TokenUsage = Field(default_factory=TokenUsage)
    sources_count: int = 0
    quality_score: float = 0.0
    iterations: int = 0
    agents_used: List[str] = Field(default_factory=list)
    success: bool = False


# ============================================================================
# Full State Models (for validation)
# ============================================================================

class InputStateModel(BaseModel):
    """Validated input state."""

    company_name: str = Field(..., min_length=1)


class OutputStateModel(BaseModel):
    """Validated output state."""

    company_name: str
    report_path: Optional[str] = None
    metrics: WorkflowMetrics
    success: bool = False


# ============================================================================
# Helper Functions
# ============================================================================

def validate_node_output(output: Dict[str, Any], model: type) -> BaseModel:
    """
    Validate a node output dictionary against a Pydantic model.

    Args:
        output: Node output dictionary
        model: Pydantic model class

    Returns:
        Validated model instance

    Raises:
        ValidationError: If validation fails
    """
    return model(**output)


def merge_token_usage(usages: List[TokenUsage]) -> TokenUsage:
    """Merge multiple token usage records."""
    return TokenUsage(
        input=sum(u.input for u in usages),
        output=sum(u.output for u in usages),
    )


def create_node_output(
    status: NodeStatus = NodeStatus.SUCCESS,
    cost: float = 0.0,
    input_tokens: int = 0,
    output_tokens: int = 0,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a standard node output dictionary.

    Args:
        status: Node execution status
        cost: Cost in USD
        input_tokens: Input token count
        output_tokens: Output token count
        **kwargs: Additional fields

    Returns:
        Node output dictionary
    """
    return {
        "status": status.value,
        "total_cost": cost,
        "total_tokens": {"input": input_tokens, "output": output_tokens},
        **kwargs
    }
