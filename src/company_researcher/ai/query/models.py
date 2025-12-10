"""Pydantic models for AI query generation."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class QueryPurpose(str, Enum):
    """Purpose/category of a search query."""
    OVERVIEW = "overview"
    FINANCIAL = "financial"
    PRODUCTS = "products"
    COMPETITORS = "competitors"
    NEWS = "news"
    LEADERSHIP = "leadership"
    MARKET = "market"
    ESG = "esg"
    TECHNOLOGY = "technology"
    STRATEGY = "strategy"
    FUNDING = "funding"
    REGULATORY = "regulatory"
    HISTORY = "history"

    @classmethod
    def get_required_for_type(cls, company_type: str) -> List["QueryPurpose"]:
        """Get required query purposes for a company type."""
        base = [cls.OVERVIEW, cls.PRODUCTS, cls.COMPETITORS]

        if company_type == "public":
            return base + [cls.FINANCIAL, cls.NEWS, cls.MARKET]
        elif company_type == "startup":
            return base + [cls.FUNDING, cls.TECHNOLOGY, cls.LEADERSHIP]
        elif company_type == "private":
            return base + [cls.NEWS, cls.LEADERSHIP]
        elif company_type == "conglomerate":
            return base + [cls.FINANCIAL, cls.MARKET, cls.STRATEGY]
        else:
            return base + [cls.NEWS]


class CompanyContext(BaseModel):
    """
    Context about the company for query generation.

    Provide as much context as known to improve query quality.
    Unknown fields can be left as None/empty.
    """

    company_name: str = Field(description="Name of the company to research")

    # Known information (optional)
    known_industry: Optional[str] = Field(default=None, description="Industry if known")
    known_region: Optional[str] = Field(default=None, description="Region: LATAM, North America, Europe, etc.")
    known_country: Optional[str] = Field(default=None, description="Country if known")
    is_public: Optional[bool] = Field(default=None, description="Whether publicly traded")
    stock_ticker: Optional[str] = Field(default=None, description="Stock ticker if public")
    stock_exchange: Optional[str] = Field(default=None, description="Stock exchange if known")

    # Known entities
    known_products: List[str] = Field(default_factory=list, description="Known product names")
    known_competitors: List[str] = Field(default_factory=list, description="Known competitors")
    known_executives: List[str] = Field(default_factory=list, description="Known executives")
    known_subsidiaries: List[str] = Field(default_factory=list, description="Known subsidiaries")

    # Research focus
    research_focus: List[str] = Field(
        default_factory=list,
        description="Specific areas to focus on"
    )
    research_depth: str = Field(
        default="standard",
        description="Research depth: quick, standard, deep"
    )

    # Language preferences
    languages: List[str] = Field(
        default_factory=lambda: ["en"],
        description="Languages to search in"
    )

    # Previous research context
    previous_queries: List[str] = Field(
        default_factory=list,
        description="Queries already executed"
    )
    gaps_identified: List[str] = Field(
        default_factory=list,
        description="Information gaps from previous searches"
    )

    def get_inferred_languages(self) -> List[str]:
        """Get languages based on region."""
        region_languages = {
            "LATAM": ["en", "es", "pt"],
            "Latin America": ["en", "es", "pt"],
            "Brazil": ["en", "pt"],
            "Mexico": ["en", "es"],
            "Spain": ["en", "es"],
            "Germany": ["en", "de"],
            "France": ["en", "fr"],
            "China": ["en", "zh"],
            "Japan": ["en", "ja"],
            "Argentina": ["en", "es"],
            "Chile": ["en", "es"],
            "Colombia": ["en", "es"],
            "Peru": ["en", "es"],
            "Paraguay": ["en", "es"],
            "Central America": ["en", "es"],
        }

        for region, langs in region_languages.items():
            if self.known_region and region.lower() in self.known_region.lower():
                return langs
            if self.known_country and region.lower() in self.known_country.lower():
                return langs

        return self.languages or ["en"]


class GeneratedQuery(BaseModel):
    """A generated search query with metadata."""

    query: str = Field(description="The search query text")
    purpose: QueryPurpose = Field(description="What this query aims to find")
    expected_sources: List[str] = Field(
        default_factory=list,
        description="Types of sources expected (news, official, SEC, etc.)"
    )
    language: str = Field(default="en", description="Language of the query")
    priority: int = Field(
        ge=1, le=5,
        default=3,
        description="Priority: 1=highest, 5=lowest"
    )
    reasoning: str = Field(
        default="",
        description="Why this query was generated"
    )
    is_fallback: bool = Field(
        default=False,
        description="Whether this is a fallback/backup query"
    )

    class Config:
        use_enum_values = True


class QueryGenerationResult(BaseModel):
    """Result of AI query generation."""

    queries: List[GeneratedQuery] = Field(
        default_factory=list,
        description="Generated queries"
    )

    # Inferred context
    company_context_inferred: Dict[str, Any] = Field(
        default_factory=dict,
        description="What was inferred about the company"
    )

    # Follow-up suggestions
    suggested_follow_ups: List[str] = Field(
        default_factory=list,
        description="Additional queries if initial ones fail"
    )

    # Coverage estimation
    estimated_coverage: Dict[str, float] = Field(
        default_factory=dict,
        description="Expected coverage by category (0.0-1.0)"
    )

    # Metadata
    total_queries: int = Field(default=0)
    languages_used: List[str] = Field(default_factory=list)

    def get_queries_by_purpose(self, purpose: QueryPurpose) -> List[GeneratedQuery]:
        """Filter queries by purpose."""
        purpose_value = purpose.value if isinstance(purpose, QueryPurpose) else purpose
        return [q for q in self.queries if q.purpose == purpose_value]

    def get_queries_by_language(self, language: str) -> List[GeneratedQuery]:
        """Filter queries by language."""
        return [q for q in self.queries if q.language == language]

    def get_high_priority_queries(self, max_priority: int = 2) -> List[GeneratedQuery]:
        """Get high priority queries."""
        return [q for q in self.queries if q.priority <= max_priority]

    def to_query_list(self) -> List[str]:
        """Convert to simple list of query strings."""
        return [q.query for q in sorted(self.queries, key=lambda x: x.priority)]


class QueryRefinementResult(BaseModel):
    """Result of query refinement based on search results."""

    refined_queries: List[GeneratedQuery] = Field(
        default_factory=list,
        description="Refined/new queries to address gaps"
    )
    gaps_addressed: List[str] = Field(
        default_factory=list,
        description="Gaps these queries aim to fill"
    )
    dropped_purposes: List[str] = Field(
        default_factory=list,
        description="Purposes with sufficient coverage (no more queries needed)"
    )
    confidence_in_refinement: float = Field(
        default=0.5,
        ge=0.0, le=1.0,
        description="Confidence that refined queries will help"
    )

    class Config:
        use_enum_values = True
