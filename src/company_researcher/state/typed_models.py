"""
Typed State Models for Company Researcher.

Addresses Issue #8: State Schema Too Flexible.

Provides strongly-typed Pydantic models that:
1. Enforce data types at runtime
2. Provide clear documentation via field descriptions
3. Enable validation and serialization
4. Support IDE autocomplete
5. Catch errors early (not at report generation)

Usage:
    from company_researcher.state.typed_models import (
        FinancialMetrics,
        AgentOutput,
        TypedResearchState
    )

    # Create validated financial metrics
    metrics = FinancialMetrics(
        revenue=15_000_000_000,
        revenue_currency="USD",
        profit_margin=0.25,
        employees=50000
    )

    # Access with type safety
    print(metrics.revenue_formatted)  # "$15.0B"
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..utils import utc_now

# ============================================================================
# Enums for Categorical Fields
# ============================================================================


class CompanySize(str, Enum):
    """Company size categories."""

    STARTUP = "startup"  # < 50 employees
    SMALL = "small"  # 50-200
    MEDIUM = "medium"  # 200-1000
    LARGE = "large"  # 1000-10000
    ENTERPRISE = "enterprise"  # > 10000


class IndustryCategory(str, Enum):
    """Major industry categories."""

    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    ENERGY = "energy"
    TELECOMMUNICATIONS = "telecommunications"
    MEDIA = "media"
    TRANSPORTATION = "transportation"
    OTHER = "other"


class DataFreshness(str, Enum):
    """Data freshness indicators."""

    CURRENT = "current"  # < 7 days
    RECENT = "recent"  # < 30 days
    DATED = "dated"  # < 90 days
    STALE = "stale"  # < 1 year
    HISTORICAL = "historical"  # > 1 year


class ConfidenceLevel(str, Enum):
    """Confidence in data accuracy."""

    VERIFIED = "verified"  # Cross-validated from multiple sources
    HIGH = "high"  # From authoritative source
    MEDIUM = "medium"  # From reliable source
    LOW = "low"  # From single/unreliable source
    UNVERIFIED = "unverified"  # No validation


# ============================================================================
# Source Models
# ============================================================================


class SourceReference(BaseModel):
    """A reference to a source document."""

    model_config = ConfigDict(frozen=True)

    url: str = Field(..., description="Source URL")
    title: str = Field(default="", description="Source title")
    domain: str = Field(default="", description="Source domain")
    accessed_at: datetime = Field(default_factory=utc_now)
    relevance_score: float = Field(default=0.5, ge=0, le=1)
    authority_tier: int = Field(default=3, ge=1, le=4)

    @field_validator("domain", mode="before")
    @classmethod
    def extract_domain(cls, v, info):
        """Extract domain from URL if not provided."""
        if v:
            return v
        url = info.data.get("url", "")
        if url:
            from urllib.parse import urlparse

            try:
                return urlparse(url).netloc
            except:
                return ""
        return ""


class CitedClaim(BaseModel):
    """A claim with source attribution."""

    claim: str = Field(..., description="The factual claim")
    value: Optional[Any] = Field(default=None, description="Extracted value if applicable")
    sources: List[SourceReference] = Field(default_factory=list)
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM)
    verified: bool = Field(default=False)


# ============================================================================
# Financial Models
# ============================================================================


class FinancialMetrics(BaseModel):
    """Strongly-typed financial metrics."""

    model_config = ConfigDict(validate_assignment=True)

    # Revenue
    revenue: Optional[float] = Field(
        default=None, ge=0, description="Annual revenue in base currency units"
    )
    revenue_currency: str = Field(default="USD")
    revenue_year: Optional[int] = Field(default=None, ge=1900, le=2100)
    revenue_growth_yoy: Optional[float] = Field(
        default=None, description="Year-over-year revenue growth as decimal (0.15 = 15%)"
    )

    # Profitability
    net_income: Optional[float] = Field(default=None, description="Net income")
    profit_margin: Optional[float] = Field(
        default=None, ge=-10, le=1, description="Net profit margin as decimal"
    )
    gross_margin: Optional[float] = Field(default=None, ge=-10, le=1)
    operating_margin: Optional[float] = Field(default=None, ge=-10, le=1)
    ebitda: Optional[float] = Field(default=None)
    ebitda_margin: Optional[float] = Field(default=None)

    # Valuation
    market_cap: Optional[float] = Field(default=None, ge=0)
    enterprise_value: Optional[float] = Field(default=None, ge=0)
    pe_ratio: Optional[float] = Field(default=None)
    ps_ratio: Optional[float] = Field(default=None)
    pb_ratio: Optional[float] = Field(default=None)
    ev_ebitda: Optional[float] = Field(default=None)

    # Stock
    stock_price: Optional[float] = Field(default=None, ge=0)
    stock_currency: str = Field(default="USD")
    price_52w_high: Optional[float] = Field(default=None, ge=0)
    price_52w_low: Optional[float] = Field(default=None, ge=0)
    shares_outstanding: Optional[int] = Field(default=None, ge=0)
    dividend_yield: Optional[float] = Field(default=None, ge=0)

    # Operations
    employees: Optional[int] = Field(default=None, ge=0)
    revenue_per_employee: Optional[float] = Field(default=None, ge=0)

    # Debt
    total_debt: Optional[float] = Field(default=None, ge=0)
    cash_and_equivalents: Optional[float] = Field(default=None, ge=0)
    debt_to_equity: Optional[float] = Field(default=None)

    # Metadata
    fiscal_year_end: Optional[str] = Field(default=None)
    data_date: Optional[datetime] = Field(default=None)
    sources: List[SourceReference] = Field(default_factory=list)
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM)

    @property
    def revenue_formatted(self) -> str:
        """Format revenue for display."""
        if self.revenue is None:
            return "N/A"
        return self._format_currency(self.revenue, self.revenue_currency)

    @property
    def market_cap_formatted(self) -> str:
        """Format market cap for display."""
        if self.market_cap is None:
            return "N/A"
        return self._format_currency(self.market_cap, self.revenue_currency)

    @staticmethod
    def _format_currency(value: float, currency: str = "USD") -> str:
        """Format large numbers with appropriate suffix."""
        symbol = "$" if currency == "USD" else currency + " "
        if value >= 1e12:
            return f"{symbol}{value/1e12:.1f}T"
        elif value >= 1e9:
            return f"{symbol}{value/1e9:.1f}B"
        elif value >= 1e6:
            return f"{symbol}{value/1e6:.1f}M"
        elif value >= 1e3:
            return f"{symbol}{value/1e3:.1f}K"
        else:
            return f"{symbol}{value:.2f}"

    @model_validator(mode="after")
    def compute_derived_metrics(self):
        """Compute derived metrics if base data available."""
        # Revenue per employee
        if self.revenue and self.employees and self.employees > 0:
            self.revenue_per_employee = self.revenue / self.employees

        return self


class MarketMetrics(BaseModel):
    """Market positioning and competitive metrics."""

    model_config = ConfigDict(validate_assignment=True)

    # Market Position
    market_share: Optional[float] = Field(
        default=None, ge=0, le=1, description="Market share as decimal"
    )
    market_size: Optional[float] = Field(default=None, ge=0)
    market_growth_rate: Optional[float] = Field(default=None)
    tam: Optional[float] = Field(default=None, ge=0, description="Total Addressable Market")
    sam: Optional[float] = Field(default=None, ge=0, description="Serviceable Addressable Market")
    som: Optional[float] = Field(default=None, ge=0, description="Serviceable Obtainable Market")

    # Geographic
    regions_active: List[str] = Field(default_factory=list)
    primary_market: Optional[str] = Field(default=None)
    international_revenue_pct: Optional[float] = Field(default=None, ge=0, le=1)

    # Competitive
    competitors: List[str] = Field(default_factory=list)
    competitive_advantages: List[str] = Field(default_factory=list)
    competitive_threats: List[str] = Field(default_factory=list)
    market_position_rank: Optional[int] = Field(default=None, ge=1)

    # Metadata
    industry: Optional[IndustryCategory] = Field(default=None)
    sub_industry: Optional[str] = Field(default=None)
    data_date: Optional[datetime] = Field(default=None)
    sources: List[SourceReference] = Field(default_factory=list)
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM)


class ProductMetrics(BaseModel):
    """Product and service information."""

    model_config = ConfigDict(validate_assignment=True)

    # Products
    products: List[str] = Field(default_factory=list)
    services: List[str] = Field(default_factory=list)
    flagship_products: List[str] = Field(default_factory=list)

    # Revenue breakdown
    product_revenue_breakdown: Dict[str, float] = Field(
        default_factory=dict, description="Product name to revenue percentage"
    )
    segment_revenue_breakdown: Dict[str, float] = Field(
        default_factory=dict, description="Segment name to revenue percentage"
    )

    # Technology
    technologies_used: List[str] = Field(default_factory=list)
    patents_count: Optional[int] = Field(default=None, ge=0)
    r_and_d_spend: Optional[float] = Field(default=None, ge=0)
    r_and_d_pct_of_revenue: Optional[float] = Field(default=None, ge=0, le=1)

    # Pricing
    pricing_model: Optional[str] = Field(default=None)
    average_deal_size: Optional[float] = Field(default=None, ge=0)

    # Metadata
    data_date: Optional[datetime] = Field(default=None)
    sources: List[SourceReference] = Field(default_factory=list)
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM)


class CompanyProfile(BaseModel):
    """Basic company profile information."""

    model_config = ConfigDict(validate_assignment=True)

    # Identity
    name: str = Field(..., min_length=1)
    legal_name: Optional[str] = Field(default=None)
    ticker: Optional[str] = Field(default=None)
    stock_exchange: Optional[str] = Field(default=None)
    isin: Optional[str] = Field(default=None)
    cusip: Optional[str] = Field(default=None)

    # Location
    headquarters_city: Optional[str] = Field(default=None)
    headquarters_state: Optional[str] = Field(default=None)
    headquarters_country: Optional[str] = Field(default=None)
    headquarters_address: Optional[str] = Field(default=None)

    # Company Info
    founded_year: Optional[int] = Field(default=None, ge=1600, le=2100)
    website: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    company_type: Optional[str] = Field(default=None)  # public, private, subsidiary
    company_size: Optional[CompanySize] = Field(default=None)

    # Leadership
    ceo_name: Optional[str] = Field(default=None)
    ceo_since: Optional[int] = Field(default=None)
    key_executives: Dict[str, str] = Field(
        default_factory=dict, description="Title to name mapping"
    )

    # Classification
    industry: Optional[IndustryCategory] = Field(default=None)
    sub_industry: Optional[str] = Field(default=None)
    sic_code: Optional[str] = Field(default=None)
    naics_code: Optional[str] = Field(default=None)

    # Metadata
    data_date: Optional[datetime] = Field(default=None)
    sources: List[SourceReference] = Field(default_factory=list)
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM)

    @property
    def headquarters_full(self) -> str:
        """Get full headquarters string."""
        parts = [self.headquarters_city, self.headquarters_state, self.headquarters_country]
        return ", ".join(p for p in parts if p)


# ============================================================================
# Agent Output Models
# ============================================================================


class AgentOutput(BaseModel):
    """Output from a specialized research agent."""

    model_config = ConfigDict(validate_assignment=True)

    agent_name: str = Field(..., description="Name of the agent")
    agent_type: str = Field(..., description="Type: financial, market, product, competitor")

    # Content
    summary: str = Field(default="", description="Agent's analysis summary")
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    key_findings: List[str] = Field(default_factory=list)
    data_gaps: List[str] = Field(default_factory=list)

    # Sources
    sources_used: List[SourceReference] = Field(default_factory=list)
    sources_count: int = Field(default=0, ge=0)

    # Metrics
    execution_time_seconds: float = Field(default=0, ge=0)
    tokens_used: int = Field(default=0, ge=0)
    cost_usd: float = Field(default=0, ge=0)

    # Quality
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM)
    completeness_score: float = Field(default=0, ge=0, le=1)

    # Timestamp
    completed_at: datetime = Field(default_factory=utc_now)


class FinancialAgentOutput(AgentOutput):
    """Output from the Financial Agent."""

    agent_type: str = Field(default="financial", frozen=True)
    metrics: FinancialMetrics = Field(default_factory=FinancialMetrics)


class MarketAgentOutput(AgentOutput):
    """Output from the Market Agent."""

    agent_type: str = Field(default="market", frozen=True)
    metrics: MarketMetrics = Field(default_factory=MarketMetrics)


class ProductAgentOutput(AgentOutput):
    """Output from the Product Agent."""

    agent_type: str = Field(default="product", frozen=True)
    metrics: ProductMetrics = Field(default_factory=ProductMetrics)


class CompetitorAgentOutput(AgentOutput):
    """Output from the Competitor Agent."""

    agent_type: str = Field(default="competitor", frozen=True)
    competitors: List[CompanyProfile] = Field(default_factory=list)
    competitive_analysis: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Quality Models
# ============================================================================


class QualityAssessment(BaseModel):
    """Quality assessment of research output."""

    model_config = ConfigDict(validate_assignment=True)

    # Scores
    overall_score: float = Field(..., ge=0, le=100)
    source_authority_score: float = Field(default=0, ge=0, le=100)
    data_specificity_score: float = Field(default=0, ge=0, le=100)
    temporal_freshness_score: float = Field(default=0, ge=0, le=100)
    coverage_score: float = Field(default=0, ge=0, le=100)
    consistency_score: float = Field(default=0, ge=0, le=100)

    # Issues
    gaps: List[str] = Field(default_factory=list)
    contradictions: List[Dict[str, Any]] = Field(default_factory=list)
    unverified_claims: List[str] = Field(default_factory=list)

    # Metadata
    assessed_at: datetime = Field(default_factory=utc_now)
    assessor: str = Field(default="quality_system")


# ============================================================================
# Complete Research State
# ============================================================================


class TypedAgentOutputs(BaseModel):
    """Container for all agent outputs with type safety."""

    model_config = ConfigDict(validate_assignment=True)

    financial: Optional[FinancialAgentOutput] = Field(default=None)
    market: Optional[MarketAgentOutput] = Field(default=None)
    product: Optional[ProductAgentOutput] = Field(default=None)
    competitor: Optional[CompetitorAgentOutput] = Field(default=None)

    def get_all(self) -> List[AgentOutput]:
        """Get all non-None agent outputs."""
        outputs = [self.financial, self.market, self.product, self.competitor]
        return [o for o in outputs if o is not None]

    def get_by_type(self, agent_type: str) -> Optional[AgentOutput]:
        """Get agent output by type."""
        mapping = {
            "financial": self.financial,
            "market": self.market,
            "product": self.product,
            "competitor": self.competitor,
        }
        return mapping.get(agent_type)


class TypedResearchState(BaseModel):
    """
    Strongly-typed research state.

    This replaces the loose Dict[str, Any] approach with validated models.
    Can be used alongside existing TypedDict state during migration.
    """

    model_config = ConfigDict(validate_assignment=True)

    # Input
    company_name: str = Field(..., min_length=1)

    # Company Profile
    profile: CompanyProfile = Field(default=None)

    # Agent Outputs (typed)
    agent_outputs: TypedAgentOutputs = Field(default_factory=TypedAgentOutputs)

    # Aggregated Metrics
    financial_metrics: Optional[FinancialMetrics] = Field(default=None)
    market_metrics: Optional[MarketMetrics] = Field(default=None)
    product_metrics: Optional[ProductMetrics] = Field(default=None)

    # Quality
    quality_assessment: Optional[QualityAssessment] = Field(default=None)
    quality_score: Optional[float] = Field(default=None, ge=0, le=100)

    # Sources
    all_sources: List[SourceReference] = Field(default_factory=list)

    # Iteration tracking
    iteration_count: int = Field(default=0, ge=0)
    max_iterations: int = Field(default=3, ge=1)

    # Cost tracking
    total_cost_usd: float = Field(default=0, ge=0)
    total_tokens_input: int = Field(default=0, ge=0)
    total_tokens_output: int = Field(default=0, ge=0)

    # Timing
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: Optional[datetime] = Field(default=None)

    # Output
    report_path: Optional[str] = Field(default=None)
    report_generated: bool = Field(default=False)

    @property
    def duration_seconds(self) -> float:
        """Get research duration in seconds."""
        end = self.completed_at or utc_now()
        return (end - self.started_at).total_seconds()

    @property
    def total_tokens(self) -> int:
        """Get total tokens used."""
        return self.total_tokens_input + self.total_tokens_output

    def add_agent_output(self, output: AgentOutput) -> None:
        """Add an agent output to the state."""
        if isinstance(output, FinancialAgentOutput):
            self.agent_outputs.financial = output
        elif isinstance(output, MarketAgentOutput):
            self.agent_outputs.market = output
        elif isinstance(output, ProductAgentOutput):
            self.agent_outputs.product = output
        elif isinstance(output, CompetitorAgentOutput):
            self.agent_outputs.competitor = output

        # Update cost tracking
        self.total_cost_usd += output.cost_usd
        self.total_tokens_input += output.tokens_used // 2  # Approximate
        self.total_tokens_output += output.tokens_used // 2

        # Add sources
        self.all_sources.extend(output.sources_used)

    def to_legacy_dict(self) -> Dict[str, Any]:
        """Convert to legacy Dict[str, Any] format for compatibility."""
        return {
            "company_name": self.company_name,
            "agent_outputs": {
                k: v.model_dump() if v else None
                for k, v in {
                    "financial": self.agent_outputs.financial,
                    "market": self.agent_outputs.market,
                    "product": self.agent_outputs.product,
                    "competitor": self.agent_outputs.competitor,
                }.items()
            },
            "quality_score": self.quality_score,
            "iteration_count": self.iteration_count,
            "total_cost": self.total_cost_usd,
            "total_tokens": {"input": self.total_tokens_input, "output": self.total_tokens_output},
            "start_time": self.started_at,
            "report_path": self.report_path,
            "sources": [s.model_dump() for s in self.all_sources],
        }

    @classmethod
    def from_legacy_dict(cls, data: Dict[str, Any]) -> "TypedResearchState":
        """Create from legacy Dict[str, Any] format."""
        state = cls(
            company_name=data.get("company_name", "Unknown"),
            quality_score=data.get("quality_score"),
            iteration_count=data.get("iteration_count", 0),
            total_cost_usd=data.get("total_cost", 0),
            started_at=data.get("start_time", utc_now()),
            report_path=data.get("report_path"),
        )

        # Parse tokens
        tokens = data.get("total_tokens", {})
        state.total_tokens_input = tokens.get("input", 0)
        state.total_tokens_output = tokens.get("output", 0)

        return state
