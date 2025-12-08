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
