"""Pydantic models for AI data extraction."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class CompanyType(str, Enum):
    """Company type classification."""
    PUBLIC = "public"
    PRIVATE = "private"
    STARTUP = "startup"
    CONGLOMERATE = "conglomerate"
    SUBSIDIARY = "subsidiary"
    NONPROFIT = "nonprofit"
    GOVERNMENT = "government"
    UNKNOWN = "unknown"


class FactCategory(str, Enum):
    """Category of extracted facts."""
    FINANCIAL = "financial"
    COMPANY_INFO = "company_info"
    PRODUCT = "product"
    MARKET = "market"
    LEADERSHIP = "leadership"
    TECHNOLOGY = "technology"
    ESG = "esg"
    LEGAL = "legal"
    NEWS = "news"


class FactType(str, Enum):
    """Specific type of fact."""
    # Financial
    REVENUE = "revenue"
    PROFIT = "profit"
    NET_INCOME = "net_income"
    MARKET_CAP = "market_cap"
    FUNDING_TOTAL = "funding_total"
    FUNDING_ROUND = "funding_round"
    VALUATION = "valuation"
    GROWTH_RATE = "growth_rate"
    EBITDA = "ebitda"

    # Company Info
    FOUNDING_DATE = "founding_date"
    HEADQUARTERS = "headquarters"
    EMPLOYEE_COUNT = "employee_count"
    BUSINESS_DESCRIPTION = "business_description"

    # Market
    MARKET_SHARE = "market_share"
    MARKET_POSITION = "market_position"

    # Leadership
    CEO = "ceo"
    FOUNDER = "founder"
    EXECUTIVE = "executive"

    # Other
    PRODUCT_NAME = "product_name"
    COMPETITOR = "competitor"
    TECHNOLOGY = "technology"
    OTHER = "other"


class ContradictionSeverity(str, Enum):
    """Severity of data contradiction."""
    CRITICAL = "critical"  # >50% difference
    HIGH = "high"  # 30-50% difference
    MEDIUM = "medium"  # 20-30% difference
    LOW = "low"  # <20% difference
    NONE = "none"  # Not a contradiction


class CompanyClassification(BaseModel):
    """AI-inferred company classification."""

    company_name: str = Field(description="Original company name")
    normalized_name: str = Field(description="Cleaned company name")
    company_type: CompanyType = Field(description="Type of company")

    # Industry
    industry: str = Field(description="Primary industry")
    sub_industry: Optional[str] = Field(default=None, description="Sub-industry")
    sector: Optional[str] = Field(default=None, description="Market sector")

    # Geography
    region: str = Field(description="Geographic region")
    country: str = Field(description="Country name")
    country_code: str = Field(description="ISO 2-letter code")
    headquarters_city: Optional[str] = Field(default=None)

    # Public company info
    stock_ticker: Optional[str] = Field(default=None)
    stock_exchange: Optional[str] = Field(default=None)
    is_listed: bool = Field(default=False)

    # Corporate structure
    parent_company: Optional[str] = Field(default=None)
    is_conglomerate: bool = Field(default=False)
    is_subsidiary: bool = Field(default=False)
    known_subsidiaries: List[str] = Field(default_factory=list)

    # Confidence
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(default="", description="Explanation")

    class Config:
        use_enum_values = True


class ExtractedFact(BaseModel):
    """A fact extracted from text."""

    category: FactCategory = Field(description="Fact category")
    fact_type: FactType = Field(description="Specific fact type")

    # Value
    value: Any = Field(description="Extracted value")
    value_normalized: Optional[float] = Field(
        default=None,
        description="Normalized numeric value"
    )
    unit: Optional[str] = Field(default=None, description="Unit of measurement")
    currency: Optional[str] = Field(default=None, description="Currency if monetary")

    # Time context
    time_period: Optional[str] = Field(default=None, description="Time period")
    as_of_date: Optional[str] = Field(default=None, description="Date of the data")
    is_estimate: bool = Field(default=False, description="Whether value is estimated")

    # Source
    source_text: str = Field(description="Original text excerpt")
    source_url: Optional[str] = Field(default=None)

    # Confidence
    confidence: float = Field(ge=0.0, le=1.0)

    class Config:
        use_enum_values = True


class FinancialData(BaseModel):
    """Consolidated financial data."""

    # Revenue
    revenue: Optional[float] = Field(default=None)
    revenue_currency: str = Field(default="USD")
    revenue_period: Optional[str] = Field(default=None)
    revenue_growth: Optional[float] = Field(default=None, description="YoY growth %")

    # Profitability
    profit: Optional[float] = Field(default=None)
    net_income: Optional[float] = Field(default=None)
    ebitda: Optional[float] = Field(default=None)
    gross_margin: Optional[float] = Field(default=None)
    operating_margin: Optional[float] = Field(default=None)

    # Valuation
    market_cap: Optional[float] = Field(default=None)
    enterprise_value: Optional[float] = Field(default=None)
    valuation: Optional[float] = Field(default=None, description="Private company valuation")

    # Funding (startups)
    funding_total: Optional[float] = Field(default=None)
    funding_stage: Optional[str] = Field(default=None)
    last_funding_amount: Optional[float] = Field(default=None)
    last_funding_date: Optional[str] = Field(default=None)

    # Size
    employee_count: Optional[int] = Field(default=None)

    # Raw facts for traceability
    raw_facts: List[ExtractedFact] = Field(default_factory=list)

    def get_best_size_indicator(self) -> Optional[str]:
        """Get best available size indicator."""
        if self.revenue:
            return f"${self.revenue:,.0f} revenue"
        if self.market_cap:
            return f"${self.market_cap:,.0f} market cap"
        if self.employee_count:
            return f"{self.employee_count:,} employees"
        return None


class ContradictionAnalysis(BaseModel):
    """Analysis of contradicting facts."""

    fact_type: str = Field(description="Type of fact with contradiction")
    values_found: List[Dict[str, Any]] = Field(
        description="All values found with sources"
    )

    # Analysis
    is_contradiction: bool = Field(description="Whether this is a true contradiction")
    severity: ContradictionSeverity = Field(description="How severe the contradiction is")
    difference_percentage: Optional[float] = Field(
        default=None,
        description="Percentage difference between values"
    )

    # Resolution
    can_be_resolved: bool = Field(default=False)
    resolution_explanation: Optional[str] = Field(default=None)
    most_likely_value: Optional[Any] = Field(default=None)
    most_likely_source: Optional[str] = Field(default=None)

    reasoning: str = Field(description="Detailed explanation")

    class Config:
        use_enum_values = True


class ExtractionResult(BaseModel):
    """Complete extraction result."""

    # Classification
    company_classification: CompanyClassification

    # Financial data
    financial_data: FinancialData

    # All extracted facts
    all_facts: List[ExtractedFact] = Field(default_factory=list)

    # Contradictions
    contradictions: List[ContradictionAnalysis] = Field(default_factory=list)
    has_critical_contradictions: bool = Field(default=False)

    # Coverage metrics
    data_coverage: Dict[str, float] = Field(
        default_factory=dict,
        description="Coverage score per category"
    )
    extraction_confidence: float = Field(
        ge=0.0, le=1.0,
        description="Overall extraction confidence"
    )

    # Metadata
    sources_processed: int = Field(default=0)
    facts_extracted: int = Field(default=0)
    languages_detected: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True

    def get_facts_by_category(self, category: FactCategory) -> List[ExtractedFact]:
        """Get facts filtered by category."""
        cat_value = category.value if isinstance(category, FactCategory) else category
        return [f for f in self.all_facts if f.category == cat_value]

    def get_facts_by_type(self, fact_type: FactType) -> List[ExtractedFact]:
        """Get facts filtered by type."""
        type_value = fact_type.value if isinstance(fact_type, FactType) else fact_type
        return [f for f in self.all_facts if f.fact_type == type_value]


class CountryDetectionResult(BaseModel):
    """Result of country detection."""

    country: str = Field(description="Full country name")
    country_code: str = Field(description="ISO 2-letter code")
    region: str = Field(description="Geographic region")
    confidence: float = Field(ge=0.0, le=1.0)
    indicators_found: List[str] = Field(default_factory=list)
    reasoning: str = Field(default="")
