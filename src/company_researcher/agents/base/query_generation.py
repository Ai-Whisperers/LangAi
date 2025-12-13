"""
Query Generation - Centralized utilities for generating search queries.

This module consolidates query generation logic used across:
- Researcher agent (initial queries)
- Deep Research agent (follow-up queries)
- Research graph (query generation node)
- LangFlow components

Provides:
- Fallback query templates for various research domains
- Query generation helpers
- Query validation and cleaning
- Domain-specific query builders

Usage:
    from company_researcher.agents.base import (
        get_fallback_queries,
        get_domain_queries,
        QueryDomain,
        clean_query,
    )

    # Get basic fallback queries
    queries = get_fallback_queries("Tesla")

    # Get domain-specific queries
    market_queries = get_domain_queries("Tesla", QueryDomain.MARKET)
    financial_queries = get_domain_queries("Tesla", QueryDomain.FINANCIAL)

    # Clean/validate a query
    cleaned = clean_query("  Tesla   revenue   ")
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
import re
from ...utils import (
    get_logger,
    get_current_year,
    get_relevant_years,
    get_freshness_indicator,
)


class QueryDomain(str, Enum):
    """Research domains for targeted query generation."""
    OVERVIEW = "overview"
    FINANCIAL = "financial"
    PRODUCTS = "products"
    COMPETITORS = "competitors"
    NEWS = "news"
    MARKET = "market"
    LEADERSHIP = "leadership"
    TECHNOLOGY = "technology"
    CUSTOMERS = "customers"
    BRAND = "brand"
    SOCIAL = "social"
    ESG = "esg"
    FUNDING = "funding"


# ==============================================================================
# Query Templates
# ==============================================================================

# Standard templates for basic research
OVERVIEW_TEMPLATES = [
    "{company} company overview",
    "{company} about company history founded",
    "{company} headquarters location employees",
]

FINANCIAL_TEMPLATES = [
    "{company} revenue financial performance",
    "{company} profit margin earnings",
    "{company} funding valuation investors",
    "{company} financial statements annual report",
]

PRODUCTS_TEMPLATES = [
    "{company} products services offerings",
    "{company} technology platform features",
    "{company} pricing plans tiers",
]

COMPETITORS_TEMPLATES = [
    "{company} competitors market position",
    "{company} vs alternatives comparison",
    "{company} competitive landscape rivals",
]

NEWS_TEMPLATES = [
    "{company} recent news developments",
    "{company} latest announcements updates",
    "{company} press releases",
]

MARKET_TEMPLATES = [
    "{company} market size TAM industry",
    "{company} market share growth trends",
    "{company} target market customers segments",
]

LEADERSHIP_TEMPLATES = [
    "{company} CEO leadership team executives",
    "{company} founders management team",
    "{company} board of directors",
]

TECHNOLOGY_TEMPLATES = [
    "{company} technology stack platform",
    "{company} patents innovations R&D",
    "{company} technical architecture",
]

CUSTOMERS_TEMPLATES = [
    "{company} customers case studies",
    "{company} client testimonials reviews",
    "{company} enterprise customers partnerships",
]

BRAND_TEMPLATES = [
    "{company} brand perception reputation",
    "{company} customer reviews ratings",
    "{company} brand awareness recognition",
]

SOCIAL_TEMPLATES = [
    "{company} social media presence",
    "{company} Twitter LinkedIn followers engagement",
    "{company} content marketing strategy",
]

ESG_TEMPLATES = [
    "{company} ESG sustainability environmental",
    "{company} corporate social responsibility",
    "{company} diversity inclusion initiatives",
]

FUNDING_TEMPLATES = [
    "{company} funding rounds investors",
    "{company} Series A B C funding",
    "{company} valuation unicorn",
]

# Map domains to templates
DOMAIN_TEMPLATES: Dict[QueryDomain, List[str]] = {
    QueryDomain.OVERVIEW: OVERVIEW_TEMPLATES,
    QueryDomain.FINANCIAL: FINANCIAL_TEMPLATES,
    QueryDomain.PRODUCTS: PRODUCTS_TEMPLATES,
    QueryDomain.COMPETITORS: COMPETITORS_TEMPLATES,
    QueryDomain.NEWS: NEWS_TEMPLATES,
    QueryDomain.MARKET: MARKET_TEMPLATES,
    QueryDomain.LEADERSHIP: LEADERSHIP_TEMPLATES,
    QueryDomain.TECHNOLOGY: TECHNOLOGY_TEMPLATES,
    QueryDomain.CUSTOMERS: CUSTOMERS_TEMPLATES,
    QueryDomain.BRAND: BRAND_TEMPLATES,
    QueryDomain.SOCIAL: SOCIAL_TEMPLATES,
    QueryDomain.ESG: ESG_TEMPLATES,
    QueryDomain.FUNDING: FUNDING_TEMPLATES,
}


# ==============================================================================
# Core Functions
# ==============================================================================

def get_fallback_queries(
    company_name: str,
    count: int = 5,
    domains: Optional[List[QueryDomain]] = None
) -> List[str]:
    """
    Generate fallback search queries for a company.

    These are used when LLM query generation fails or as a baseline.

    Args:
        company_name: Name of company to research
        count: Number of queries to generate
        domains: Specific domains to include. If None, uses default mix.

    Returns:
        List of search query strings
    """
    if domains is None:
        # Default balanced mix of domains
        domains = [
            QueryDomain.OVERVIEW,
            QueryDomain.FINANCIAL,
            QueryDomain.PRODUCTS,
            QueryDomain.COMPETITORS,
            QueryDomain.NEWS,
        ]

    queries = []
    for domain in domains:
        templates = DOMAIN_TEMPLATES.get(domain, [])
        if templates:
            # Use first template from each domain
            queries.append(templates[0].format(company=company_name))

    # Ensure we have at least the requested count
    while len(queries) < count:
        # Add more from existing domains
        for domain in domains:
            templates = DOMAIN_TEMPLATES.get(domain, [])
            for template in templates[1:]:
                if len(queries) >= count:
                    break
                query = template.format(company=company_name)
                if query not in queries:
                    queries.append(query)
            if len(queries) >= count:
                break

    return queries[:count]


def get_domain_queries(
    company_name: str,
    domain: QueryDomain,
    count: Optional[int] = None
) -> List[str]:
    """
    Generate queries for a specific research domain.

    Args:
        company_name: Name of company
        domain: Research domain
        count: Number of queries (None for all available)

    Returns:
        List of search queries for that domain
    """
    templates = DOMAIN_TEMPLATES.get(domain, [])
    queries = [t.format(company=company_name) for t in templates]

    if count is not None:
        return queries[:count]
    return queries


def get_gap_queries(
    company_name: str,
    missing_info: List[str],
    max_queries: int = 5
) -> List[str]:
    """
    Generate queries to fill identified research gaps.

    Args:
        company_name: Name of company
        missing_info: List of missing information descriptions
        max_queries: Maximum queries to generate

    Returns:
        List of targeted search queries
    """
    queries = []

    # Map common gap descriptions to domains
    gap_domain_map = {
        "revenue": QueryDomain.FINANCIAL,
        "financial": QueryDomain.FINANCIAL,
        "funding": QueryDomain.FUNDING,
        "valuation": QueryDomain.FUNDING,
        "product": QueryDomain.PRODUCTS,
        "service": QueryDomain.PRODUCTS,
        "competitor": QueryDomain.COMPETITORS,
        "market": QueryDomain.MARKET,
        "customer": QueryDomain.CUSTOMERS,
        "leadership": QueryDomain.LEADERSHIP,
        "team": QueryDomain.LEADERSHIP,
        "technology": QueryDomain.TECHNOLOGY,
        "brand": QueryDomain.BRAND,
        "social": QueryDomain.SOCIAL,
        "esg": QueryDomain.ESG,
        "sustainability": QueryDomain.ESG,
    }

    for gap in missing_info[:max_queries]:
        gap_lower = gap.lower()

        # Try to match gap to a domain
        matched_domain = None
        for keyword, domain in gap_domain_map.items():
            if keyword in gap_lower:
                matched_domain = domain
                break

        if matched_domain:
            domain_queries = get_domain_queries(company_name, matched_domain, 1)
            if domain_queries:
                queries.append(domain_queries[0])
        else:
            # Generic query from the gap description
            queries.append(f"{company_name} {gap}")

    return queries[:max_queries]


def get_comprehensive_queries(
    company_name: str,
    depth: str = "standard"
) -> List[str]:
    """
    Generate comprehensive research queries.

    Args:
        company_name: Name of company
        depth: Research depth - "basic", "standard", or "deep"

    Returns:
        List of comprehensive queries
    """
    if depth == "basic":
        domains = [QueryDomain.OVERVIEW, QueryDomain.NEWS]
        count = 3
    elif depth == "deep":
        domains = list(QueryDomain)  # All domains
        count = 15
    else:  # standard
        domains = [
            QueryDomain.OVERVIEW,
            QueryDomain.FINANCIAL,
            QueryDomain.PRODUCTS,
            QueryDomain.COMPETITORS,
            QueryDomain.NEWS,
            QueryDomain.MARKET,
        ]
        count = 8

    return get_fallback_queries(company_name, count=count, domains=domains)


# ==============================================================================
# Query Utilities
# ==============================================================================

def clean_query(query: str) -> str:
    """
    Clean and normalize a search query.

    Args:
        query: Raw query string

    Returns:
        Cleaned query string
    """
    if not query:
        return ""

    # Remove extra whitespace
    query = " ".join(query.split())

    # Remove quotes if they wrap the entire string
    if query.startswith('"') and query.endswith('"'):
        query = query[1:-1]
    if query.startswith("'") and query.endswith("'"):
        query = query[1:-1]

    # Remove common prefixes
    prefixes_to_remove = [
        "search for ",
        "find ",
        "look up ",
        "query: ",
    ]
    query_lower = query.lower()
    for prefix in prefixes_to_remove:
        if query_lower.startswith(prefix):
            query = query[len(prefix):]
            break

    return query.strip()


def validate_queries(queries: List[str]) -> List[str]:
    """
    Validate and filter a list of queries.

    Args:
        queries: List of query strings

    Returns:
        List of valid, cleaned queries
    """
    valid = []

    for query in queries:
        cleaned = clean_query(query)

        # Minimum length check
        if len(cleaned) < 3:
            continue

        # Maximum length check
        if len(cleaned) > 200:
            cleaned = cleaned[:200]

        # Skip duplicates
        if cleaned.lower() in [v.lower() for v in valid]:
            continue

        valid.append(cleaned)

    return valid


def parse_query_response(response_text: str) -> List[str]:
    """
    Parse queries from LLM response text.

    Handles various formats:
    - JSON array: ["query1", "query2"]
    - Numbered list: 1. query1\n2. query2
    - Bullet list: - query1\n- query2
    - Plain lines: query1\nquery2

    Args:
        response_text: Raw LLM response

    Returns:
        List of parsed queries
    """
    import json

    text = response_text.strip()

    # Try JSON array first
    try:
        # Find JSON array in text
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            queries = json.loads(json_match.group())
            if isinstance(queries, list):
                return validate_queries([str(q) for q in queries])
    except (json.JSONDecodeError, ValueError):
        pass

    # Try numbered/bullet lists
    queries = []
    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Remove numbering
        # "1. query" or "1) query"
        numbered = re.match(r'^\d+[\.\)]\s*(.+)$', line)
        if numbered:
            queries.append(numbered.group(1))
            continue

        # Remove bullets
        # "- query" or "* query" or "• query"
        bullet = re.match(r'^[-*•]\s*(.+)$', line)
        if bullet:
            queries.append(bullet.group(1))
            continue

        # Plain line (if it looks like a query)
        if len(line) > 5 and not line.startswith('#'):
            queries.append(line)

    return validate_queries(queries)


# ==============================================================================
# Query Configuration
# ==============================================================================

@dataclass
class QueryConfig:
    """Configuration for query generation."""
    company_name: str
    domains: List[QueryDomain] = field(default_factory=lambda: [
        QueryDomain.OVERVIEW,
        QueryDomain.FINANCIAL,
        QueryDomain.PRODUCTS,
        QueryDomain.COMPETITORS,
        QueryDomain.NEWS,
    ])
    count: int = 5
    include_year: bool = False
    year: Optional[int] = None

    def build_queries(self) -> List[str]:
        """Build queries based on configuration."""
        queries = get_fallback_queries(
            self.company_name,
            count=self.count,
            domains=self.domains
        )

        # Optionally add year to queries
        if self.include_year and self.year:
            queries = [f"{q} {self.year}" for q in queries]

        return queries


# ==============================================================================
# AI-Powered Query Generation
# ==============================================================================

def generate_research_queries(
    company_name: str,
    context: Optional[Dict[str, Any]] = None,
    num_queries: int = 10
) -> List[str]:
    """
    Generate research queries using AI or legacy templates.

    Args:
        company_name: Company to research
        context: Optional context dict with known information
        num_queries: Number of queries to generate

    Returns:
        List of query strings
    """
    from company_researcher.ai.config import get_ai_config

    config = get_ai_config()

    if config.query_generation.enabled:
        try:
            from company_researcher.ai.query import get_query_generator, CompanyContext

            # Build context
            ctx = CompanyContext(
                company_name=company_name,
                known_industry=context.get("industry") if context else None,
                known_region=context.get("region") if context else None,
                known_country=context.get("country") if context else None,
                is_public=context.get("is_public") if context else None,
                stock_ticker=context.get("ticker") if context else None,
            )

            generator = get_query_generator()
            result = generator.generate_queries(ctx, num_queries=num_queries)

            return result.to_query_list()

        except Exception as e:
            logger = get_logger(__name__)
            logger.warning(f"AI query generation failed, using legacy: {e}")

            if not config.query_generation.fallback_to_legacy:
                raise
            # Fall through to legacy

    # Legacy template-based generation
    return get_fallback_queries(company_name, count=num_queries)


# ==============================================================================
# Spanish Language Templates (LATAM Companies)
# ==============================================================================

SPANISH_OVERVIEW_TEMPLATES = [
    "{company} empresa información general",
    "{company} historia fundación origen",
    "{company} sede central ubicación empleados",
]

SPANISH_FINANCIAL_TEMPLATES = [
    "{company} ingresos resultados financieros",
    "{company} facturación ganancias",
    "{company} inversores valoración",
]

SPANISH_LEADERSHIP_TEMPLATES = [
    "{company} CEO director ejecutivo actual",
    "{company} equipo directivo gerencia",
    "{company} presidente junta directiva",
    "{company} nuevo CEO nombramiento",
]

SPANISH_MARKET_TEMPLATES = [
    "{company} participación de mercado cuota",
    "{company} clientes suscriptores usuarios",
    "{company} crecimiento tendencias mercado",
]

SPANISH_NEWS_TEMPLATES = [
    "{company} noticias recientes actualidad",
    "{company} últimas novedades anuncios",
    "{company} comunicados de prensa",
]

SPANISH_REGULATORY_TEMPLATES = [
    "{company} regulación CONATEL telecomunicaciones",
    "{company} licencia operador móvil",
    "{company} multas sanciones regulatorias",
]

# Map Spanish templates by domain
SPANISH_DOMAIN_TEMPLATES: Dict[QueryDomain, List[str]] = {
    QueryDomain.OVERVIEW: SPANISH_OVERVIEW_TEMPLATES,
    QueryDomain.FINANCIAL: SPANISH_FINANCIAL_TEMPLATES,
    QueryDomain.LEADERSHIP: SPANISH_LEADERSHIP_TEMPLATES,
    QueryDomain.MARKET: SPANISH_MARKET_TEMPLATES,
    QueryDomain.NEWS: SPANISH_NEWS_TEMPLATES,
}


# ==============================================================================
# Date-Aware Query Generation
# ==============================================================================

def get_date_filtered_queries(
    company_name: str,
    domain: QueryDomain,
    count: int = 3,
    include_year: bool = True,
) -> List[str]:
    """
    Generate queries with appropriate date filtering.

    Args:
        company_name: Name of company
        domain: Research domain
        count: Number of queries to generate
        include_year: Whether to append year to queries

    Returns:
        List of date-filtered queries
    """
    base_queries = get_domain_queries(company_name, domain, count)

    if not include_year:
        return base_queries

    current_year = get_current_year()

    # Determine year strategy based on domain
    if domain in [QueryDomain.LEADERSHIP, QueryDomain.NEWS]:
        # Need current year data
        years = [current_year]
    elif domain in [QueryDomain.FINANCIAL, QueryDomain.MARKET]:
        # Financial data may lag - include previous year
        years = [current_year, current_year - 1]
    else:
        # Default: current year
        years = [current_year]

    filtered_queries = []
    for query in base_queries:
        # Add most relevant year
        filtered_queries.append(f"{query} {years[0]}")

    return filtered_queries


def get_leadership_queries(
    company_name: str,
    include_spanish: bool = False,
) -> List[str]:
    """
    Generate comprehensive leadership queries.

    Designed to find current CEO and executive team info.

    Args:
        company_name: Name of company
        include_spanish: Include Spanish queries for LATAM companies

    Returns:
        List of leadership-focused queries
    """
    current_year = get_current_year()

    queries = [
        f"{company_name} CEO {current_year}",
        f"{company_name} current CEO chief executive",
        f"{company_name} new CEO appointed {current_year}",
        f"{company_name} CEO change {current_year - 1} {current_year}",
        f"{company_name} executive leadership team",
        f"{company_name} management team executives",
    ]

    if include_spanish:
        spanish_queries = [
            f"{company_name} CEO actual {current_year}",
            f"{company_name} director ejecutivo gerente general",
            f"{company_name} nuevo CEO nombramiento {current_year}",
            f"{company_name} cambio CEO {current_year - 1} {current_year}",
            f"{company_name} equipo directivo ejecutivos",
        ]
        queries.extend(spanish_queries)

    return queries


def get_market_data_queries(
    company_name: str,
    include_spanish: bool = False,
) -> List[str]:
    """
    Generate queries for current market data.

    Designed to find up-to-date market share, subscribers, revenue.

    Args:
        company_name: Name of company
        include_spanish: Include Spanish queries for LATAM companies

    Returns:
        List of market data queries
    """
    current_year = get_current_year()
    prev_year = current_year - 1

    queries = [
        f"{company_name} market share {current_year}",
        f"{company_name} subscribers users {current_year}",
        f"{company_name} revenue {prev_year} {current_year}",
        f"{company_name} quarterly results Q1 Q2 Q3 Q4 {current_year}",
        f"{company_name} annual report {prev_year}",
        f"{company_name} financial results {current_year}",
    ]

    if include_spanish:
        spanish_queries = [
            f"{company_name} participación mercado {current_year}",
            f"{company_name} suscriptores usuarios {current_year}",
            f"{company_name} ingresos facturación {prev_year} {current_year}",
            f"{company_name} resultados trimestrales {current_year}",
            f"{company_name} informe anual {prev_year}",
        ]
        queries.extend(spanish_queries)

    return queries


def get_bilingual_queries(
    company_name: str,
    domain: QueryDomain,
    count: int = 3,
) -> List[str]:
    """
    Generate queries in both English and Spanish.

    Args:
        company_name: Name of company
        domain: Research domain
        count: Number of queries per language

    Returns:
        List of bilingual queries
    """
    # Get English queries
    english_queries = get_domain_queries(company_name, domain, count)

    # Get Spanish queries if available
    spanish_templates = SPANISH_DOMAIN_TEMPLATES.get(domain, [])
    spanish_queries = [t.format(company=company_name) for t in spanish_templates[:count]]

    return english_queries + spanish_queries


def get_comprehensive_dated_queries(
    company_name: str,
    depth: str = "standard",
    region: Optional[str] = None,
) -> List[str]:
    """
    Generate comprehensive queries with date context.

    Args:
        company_name: Name of company
        depth: Research depth ("basic", "standard", "deep")
        region: Geographic region (e.g., "LATAM", "US", "EU")

    Returns:
        List of comprehensive date-aware queries
    """
    current_year = get_current_year()
    relevant_years = get_relevant_years(depth)
    include_spanish = region and region.upper() in ["LATAM", "SOUTH_AMERICA", "LATIN_AMERICA"]

    queries = []

    # Always include leadership queries with current year
    queries.extend(get_leadership_queries(company_name, include_spanish))

    # Market data queries
    queries.extend(get_market_data_queries(company_name, include_spanish))

    # Add year-filtered domain queries
    domains_by_depth = {
        "basic": [QueryDomain.OVERVIEW, QueryDomain.NEWS],
        "standard": [QueryDomain.OVERVIEW, QueryDomain.FINANCIAL, QueryDomain.NEWS, QueryDomain.MARKET],
        "deep": list(QueryDomain),
    }

    for domain in domains_by_depth.get(depth, domains_by_depth["standard"]):
        if include_spanish:
            queries.extend(get_bilingual_queries(company_name, domain, 2))
        else:
            queries.extend(get_date_filtered_queries(company_name, domain, 2))

    # Deduplicate while preserving order
    seen = set()
    unique_queries = []
    for q in queries:
        q_lower = q.lower()
        if q_lower not in seen:
            seen.add(q_lower)
            unique_queries.append(q)

    return unique_queries


def generate_targeted_queries(
    company_name: str,
    field_type: str,
    region: Optional[str] = None,
) -> List[str]:
    """
    Generate queries targeted at specific data fields.

    Uses freshness indicators to determine appropriate date filtering.

    Args:
        company_name: Company name
        field_type: Type of data needed (e.g., "ceo", "revenue", "subscribers")
        region: Geographic region

    Returns:
        List of targeted queries
    """
    freshness = get_freshness_indicator(field_type)
    include_spanish = region and region.upper() in ["LATAM", "SOUTH_AMERICA", "LATIN_AMERICA"]

    queries = []

    # Build targeted query
    base_query = f"{company_name} {field_type}"
    if freshness:
        queries.append(f"{base_query} {freshness}")
    else:
        queries.append(base_query)

    # Add variations
    if "ceo" in field_type.lower() or "leadership" in field_type.lower():
        queries.extend(get_leadership_queries(company_name, include_spanish))
    elif "revenue" in field_type.lower() or "financial" in field_type.lower():
        queries.extend(get_market_data_queries(company_name, include_spanish))
    elif "subscriber" in field_type.lower() or "user" in field_type.lower():
        current_year = get_current_year()
        queries.append(f"{company_name} subscribers count {current_year}")
        queries.append(f"{company_name} active users {current_year}")
        if include_spanish:
            queries.append(f"{company_name} número suscriptores {current_year}")
            queries.append(f"{company_name} usuarios activos {current_year}")

    return validate_queries(queries)
