"""
Autonomous Discovery Module - Makes research self-sufficient.

This module enables the researcher to discover all company information from the web
WITHOUT any hardcoded knowledge. The system learns about:
- Parent companies (discovered, not hardcoded)
- Industry context (discovered from searches)
- Regional regulators (discovered from searches)
- Key business segments (discovered from searches)

Key Improvements:
1. Discovery Phase - Runs FIRST to build context from web
2. Gap-Driven Queries - Generates targeted queries for missing fields
3. Semantic Extraction - Uses LLM to find fields even with indirect mentions
4. Date-Aware Searches - Adds date filters for recency

Usage:
    from company_researcher.research.autonomous_discovery import (
        discovery_phase,
        generate_gap_driven_queries,
        semantic_field_extraction,
    )

    # Phase 0: Discover context
    context = discovery_phase("Tigo Paraguay")
    # Returns: {"parent": "Millicom", "industry": "telecom", "country": "Paraguay", ...}

    # Generate targeted queries for missing fields
    queries = generate_gap_driven_queries("Tigo Paraguay", context, missing_fields=["ceo", "market_share"])
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..integrations.search_router import get_search_router
from ..llm.smart_client import TaskType, get_smart_client
from ..utils import get_logger

logger = get_logger(__name__)


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class DiscoveredContext:
    """Context discovered from web searches (not hardcoded)."""

    company_name: str
    parent_company: Optional[str] = None
    industry: Optional[str] = None
    sub_industries: List[str] = field(default_factory=list)
    country: Optional[str] = None
    region: Optional[str] = None
    founded_year: Optional[int] = None
    headquarters: Optional[str] = None
    stock_ticker: Optional[str] = None
    stock_exchange: Optional[str] = None
    regulator: Optional[str] = None
    competitors: List[str] = field(default_factory=list)
    key_products: List[str] = field(default_factory=list)
    business_segments: List[str] = field(default_factory=list)
    current_ceo: Optional[str] = None
    discovery_sources: List[str] = field(default_factory=list)
    discovery_confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "parent_company": self.parent_company,
            "industry": self.industry,
            "sub_industries": self.sub_industries,
            "country": self.country,
            "region": self.region,
            "founded_year": self.founded_year,
            "headquarters": self.headquarters,
            "stock_ticker": self.stock_ticker,
            "stock_exchange": self.stock_exchange,
            "regulator": self.regulator,
            "competitors": self.competitors,
            "key_products": self.key_products,
            "business_segments": self.business_segments,
            "current_ceo": self.current_ceo,
            "discovery_sources": self.discovery_sources,
            "discovery_confidence": self.discovery_confidence,
        }


class CriticalField(Enum):
    """Fields that are critical for research quality."""

    CEO = "ceo"
    REVENUE = "revenue"
    MARKET_SHARE = "market_share"
    SUBSCRIBERS = "subscribers"
    FOUNDED = "founded"
    HEADQUARTERS = "headquarters"
    EMPLOYEES = "employees"
    COMPETITORS = "competitors"


# =============================================================================
# Discovery Phase - Learn from Web Before Generating Queries
# =============================================================================

DISCOVERY_PROMPT = """You are a company research assistant. Analyze the search results and extract key company information.

Company being researched: {company_name}

Search Results:
{search_results}

Extract the following information in JSON format. Use null for unknown fields.
Be accurate - only extract information that is clearly stated in the search results.

{{
    "parent_company": "Name of parent/holding company if mentioned (e.g., 'Millicom International' for Tigo)",
    "industry": "Primary industry (e.g., 'telecommunications', 'banking', 'retail')",
    "sub_industries": ["List of specific business areas like 'mobile', 'broadband', 'mobile money'"],
    "country": "Country of primary operations",
    "region": "Geographic region (e.g., 'Latin America', 'Europe', 'Asia')",
    "headquarters": "City, Country of headquarters",
    "founded_year": 1990,
    "stock_ticker": "Ticker symbol if public",
    "stock_exchange": "Exchange name if public",
    "regulator": "Name of industry regulator (e.g., 'CONATEL' for Paraguay telecom)",
    "competitors": ["List of main competitors mentioned"],
    "key_products": ["List of main products/services"],
    "business_segments": ["List of business segments like 'Mobile', 'Home', 'B2B', 'Mobile Money'"],
    "current_ceo": "Name of current CEO/General Manager if mentioned",
    "confidence": 0.85
}}

Return ONLY the JSON, no other text."""


def _call_llm(prompt: str, max_tokens: int = 2000) -> str:
    """
    Call LLM using SmartLLMClient with automatic provider fallback.

    Uses SmartLLMClient for automatic provider fallback:
    - Primary: Anthropic Claude
    - Fallback 1: Groq (llama-3.3-70b-versatile) on rate limit
    - Fallback 2: DeepSeek on rate limit

    Args:
        prompt: The prompt to send to the LLM
        max_tokens: Maximum tokens for the response

    Returns:
        The LLM response content as a string
    """
    smart_client = get_smart_client()

    result = smart_client.complete(
        prompt=prompt,
        task_type=TaskType.REASONING,
        complexity="medium",
        max_tokens=max_tokens,
        temperature=0.0,
    )

    logger.info(f"[LLM] Provider: {result.provider}/{result.model} ({result.routing_reason})")

    return result.content


def discovery_phase(company_name: str) -> DiscoveredContext:
    """
    Phase 0: Discover company context from web searches BEFORE generating research queries.

    This is the KEY improvement - instead of using hardcoded knowledge like:
        PARENT_COMPANY_MAP = {"tigo paraguay": "Millicom International"}

    We DISCOVER this from web searches:
        Search: "What is Tigo Paraguay parent company owner"
        Result: "Tigo Paraguay is a subsidiary of Millicom International..."

    Args:
        company_name: Name of the company to research

    Returns:
        DiscoveredContext with all learned information
    """
    logger.info(f"[DISCOVERY] Starting discovery phase for: {company_name}")

    # Discovery queries - designed to learn about the company from scratch
    discovery_queries = [
        f"What is {company_name}",  # Basic overview
        f"{company_name} parent company owner holding group subsidiary",  # Ownership
        f"{company_name} industry sector business",  # Industry
        f"{company_name} CEO chief executive officer general manager 2024",  # Leadership
        f"{company_name} headquarters location country",  # Geography
        f"{company_name} competitors rivals market",  # Competition
        f"{company_name} products services offerings",  # Products
        f"{company_name} regulatory authority regulator license",  # Regulatory
    ]

    # Execute discovery searches
    router = get_search_router()
    all_results = []
    sources = []

    for query in discovery_queries:
        try:
            response = router.search(
                query=query,
                quality="premium",
                max_results=3,  # Fewer results per query, more queries
            )
            if response.success and response.results:
                for item in response.results:
                    result_dict = item.to_dict()
                    all_results.append(
                        {
                            "query": query,
                            "title": result_dict.get("title", ""),
                            "content": result_dict.get("snippet", "")[:500],
                            "url": result_dict.get("url", ""),
                        }
                    )
                    sources.append(result_dict.get("url", ""))
                logger.debug(f"  [OK] '{query[:40]}...' - {len(response.results)} results")
        except (RuntimeError, ValueError, TypeError, AttributeError) as e:
            logger.warning(f"  [WARN] Discovery search failed: {query[:40]}... - {e}")

    if not all_results:
        logger.warning(f"[DISCOVERY] No results found for {company_name}")
        return DiscoveredContext(company_name=company_name)

    # Format results for LLM
    formatted_results = "\n\n".join(
        [
            f"Query: {r['query']}\nTitle: {r['title']}\nContent: {r['content']}"
            for r in all_results[:15]  # Limit to avoid context overflow
        ]
    )

    # Extract structured context using LLM
    prompt = DISCOVERY_PROMPT.format(company_name=company_name, search_results=formatted_results)

    try:
        content = _call_llm(prompt, max_tokens=1500)

        # Parse JSON response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        # Find JSON boundaries
        start_idx = content.find("{")
        end_idx = content.rfind("}")
        if start_idx >= 0 and end_idx >= 0:
            json_str = content[start_idx : end_idx + 1]
            data = json.loads(json_str)
        else:
            data = json.loads(content)

        # Build DiscoveredContext
        context = DiscoveredContext(
            company_name=company_name,
            parent_company=data.get("parent_company"),
            industry=data.get("industry"),
            sub_industries=data.get("sub_industries", []),
            country=data.get("country"),
            region=data.get("region"),
            founded_year=data.get("founded_year"),
            headquarters=data.get("headquarters"),
            stock_ticker=data.get("stock_ticker"),
            stock_exchange=data.get("stock_exchange"),
            regulator=data.get("regulator"),
            competitors=data.get("competitors", []),
            key_products=data.get("key_products", []),
            business_segments=data.get("business_segments", []),
            current_ceo=data.get("current_ceo"),
            discovery_sources=list(set(sources))[:10],
            discovery_confidence=data.get("confidence", 0.5),
        )

        logger.info(
            f"[DISCOVERY] Completed - Parent: {context.parent_company}, "
            f"Industry: {context.industry}, Country: {context.country}, "
            f"CEO: {context.current_ceo}"
        )

        return context

    except (json.JSONDecodeError, ValueError, TypeError, KeyError) as e:
        logger.error(f"[DISCOVERY] Failed to parse LLM response: {e}")
        return DiscoveredContext(company_name=company_name, discovery_sources=sources)


# =============================================================================
# Gap-Driven Query Generation
# =============================================================================


def generate_gap_driven_queries(
    company_name: str,
    context: DiscoveredContext,
    missing_fields: List[str],
    current_year: Optional[int] = None,
) -> List[str]:
    """
    Generate targeted search queries specifically for missing fields.

    Instead of generic queries like "Tigo Paraguay company information",
    this generates specific queries like:
    - "Tigo Paraguay CEO 2024" (if CEO is missing)
    - "Tigo Paraguay market share Paraguay 2024" (if market share is missing)
    - "CONATEL Tigo spectrum license" (uses discovered regulator)

    Args:
        company_name: Company being researched
        context: Discovered context from discovery phase
        missing_fields: List of missing field names
        current_year: Year for date-aware searches (defaults to current)

    Returns:
        List of targeted search queries
    """
    if current_year is None:
        current_year = datetime.now().year

    queries = []

    # Use discovered context to build better queries
    parent = context.parent_company or ""
    country = context.country or ""
    industry = context.industry or ""
    regulator = context.regulator or ""

    for field in missing_fields:
        field_lower = field.lower()

        if field_lower == "ceo" or field_lower == "leadership":
            # CEO-specific queries with multiple patterns
            queries.extend(
                [
                    f"{company_name} CEO {current_year}",
                    f"{company_name} chief executive officer {current_year}",
                    f"{company_name} general manager director {current_year}",
                    f"Who leads {company_name}",
                    f"{company_name} leadership appointment {current_year}",
                    f"{company_name} new CEO appointed",
                ]
            )
            if parent:
                queries.append(f"{parent} {company_name} CEO")

        elif field_lower == "market_share" or field_lower == "subscribers":
            # Market-specific queries
            queries.extend(
                [
                    f"{company_name} market share {country} {current_year}",
                    f"{company_name} subscribers customers {current_year}",
                    f"{industry} market {country} ranking {current_year}",
                    f"{company_name} market position {country}",
                ]
            )
            if context.competitors:
                competitor = context.competitors[0]
                queries.append(f"{company_name} vs {competitor} market share {country}")

        elif field_lower == "revenue" or field_lower == "financial":
            # Financial queries
            queries.extend(
                [
                    f"{company_name} revenue {current_year}",
                    f"{company_name} annual report {current_year - 1}",
                    f"{company_name} financial results {current_year}",
                ]
            )
            if parent:
                queries.append(f"{parent} {company_name} revenue financial")

        elif field_lower == "regulatory" or field_lower == "spectrum":
            # Regulatory queries using discovered regulator
            if regulator:
                queries.extend(
                    [
                        f"{regulator} {company_name}",
                        f"{company_name} {regulator} license",
                        f"{company_name} spectrum {country}",
                        f"{company_name} 5G license {country} {current_year}",
                    ]
                )
            else:
                queries.extend(
                    [
                        f"{company_name} telecom regulator {country}",
                        f"{company_name} spectrum license {country}",
                    ]
                )

        elif field_lower == "competitors":
            # Competitor discovery
            queries.extend(
                [
                    f"{company_name} competitors {country}",
                    f"{industry} companies {country}",
                    f"{company_name} vs market {country}",
                ]
            )

        elif field_lower == "products" or field_lower == "services":
            # Product/service discovery
            queries.extend(
                [
                    f"{company_name} products services",
                    f"{company_name} business segments",
                ]
            )
            if context.business_segments:
                for segment in context.business_segments[:2]:
                    queries.append(f"{company_name} {segment}")

        elif field_lower == "founded" or field_lower == "history":
            # Historical queries
            queries.extend(
                [
                    f"{company_name} founded established history",
                    f"{company_name} company history timeline",
                ]
            )

        elif field_lower == "employees":
            queries.extend(
                [
                    f"{company_name} employees workforce {current_year}",
                    f"{company_name} number of employees",
                ]
            )

        else:
            # Generic fallback
            queries.append(f"{company_name} {field} {current_year}")

    # Remove duplicates while preserving order
    seen = set()
    unique_queries = []
    for q in queries:
        if q.lower() not in seen:
            seen.add(q.lower())
            unique_queries.append(q)

    logger.info(
        f"[GAP-QUERIES] Generated {len(unique_queries)} targeted queries for {len(missing_fields)} missing fields"
    )

    return unique_queries


# =============================================================================
# Semantic Field Extraction
# =============================================================================

SEMANTIC_EXTRACTION_PROMPT = """Extract the {field_name} from the following text about {company_name}.

IMPORTANT: Look for BOTH direct and indirect mentions:
- Direct: "The CEO is John Smith", "CEO: John Smith"
- Indirect: "John Smith leads the company", "under the leadership of John Smith",
  "John Smith was appointed to head", "John Smith took over as", "John Smith became"

For CEO extraction specifically, also look for:
- "General Manager", "Managing Director", "President", "Chief Executive"
- Recent appointments: "named as CEO", "appointed CEO", "new CEO"

Text:
{text}

Instructions:
1. If you find the {field_name}, return ONLY the extracted value
2. If not found, return exactly: NOT_FOUND
3. Do not explain or add context - just the value or NOT_FOUND

{field_name}:"""


def semantic_field_extraction(text: str, field_name: str, company_name: str) -> Optional[str]:
    """
    Use LLM to semantically extract a field from text.

    Unlike keyword matching which looks for "CEO", this understands:
    - "Roberto Laratro leads Tigo Paraguay" -> CEO: Roberto Laratro
    - "Under the leadership of John Smith" -> CEO: John Smith
    - "The company appointed Maria Garcia as head" -> CEO: Maria Garcia

    Args:
        text: Text to extract from
        field_name: Name of field to extract (e.g., "CEO", "Revenue", "Market Share")
        company_name: Company being researched

    Returns:
        Extracted value or None if not found
    """
    if not text or len(text.strip()) < 50:
        return None

    # Truncate text to avoid context overflow
    text = text[:4000]

    prompt = SEMANTIC_EXTRACTION_PROMPT.format(
        field_name=field_name, company_name=company_name, text=text
    )

    try:
        result = _call_llm(prompt, max_tokens=200)
        result = result.strip()

        if result.upper() == "NOT_FOUND" or not result:
            return None

        # Clean up common artifacts
        result = result.strip("\"'")
        if result.lower().startswith(f"{field_name.lower()}:"):
            result = result[len(field_name) + 1 :].strip()

        return result if result and result.upper() != "NOT_FOUND" else None

    except (RuntimeError, ValueError, TypeError) as e:
        logger.warning(f"Semantic extraction failed for {field_name}: {e}")
        return None


def extract_all_fields_semantically(
    text: str, company_name: str, fields: List[str] = None
) -> Dict[str, Optional[str]]:
    """
    Extract multiple fields from text using semantic understanding.

    Args:
        text: Text to extract from
        company_name: Company being researched
        fields: Fields to extract (defaults to critical fields)

    Returns:
        Dict mapping field names to extracted values (or None)
    """
    if fields is None:
        fields = ["CEO", "Revenue", "Market Share", "Subscribers", "Founded Year", "Headquarters"]

    results = {}
    for field in fields:
        results[field] = semantic_field_extraction(text, field, company_name)

    # Log what was found
    found = [f for f, v in results.items() if v is not None]
    if found:
        logger.info(f"[SEMANTIC] Found {len(found)} fields: {', '.join(found)}")

    return results


# =============================================================================
# Date-Aware Search Queries
# =============================================================================


def add_date_filters(queries: List[str], prefer_recent: bool = True) -> List[str]:
    """
    Add date filters to search queries for recency.

    Transforms:
        "Tigo Paraguay market share"
    Into:
        "Tigo Paraguay market share 2024"
        "Tigo Paraguay market share Q4 2023"

    Args:
        queries: List of search queries
        prefer_recent: Whether to prefer recent results

    Returns:
        Enhanced queries with date filters
    """
    current_year = datetime.now().year
    last_year = current_year - 1

    enhanced = []

    for query in queries:
        # Keep original
        enhanced.append(query)

        # Check if query already has a year
        has_year = any(str(y) in query for y in range(2020, current_year + 1))

        if not has_year and prefer_recent:
            # Add year-filtered versions
            enhanced.append(f"{query} {current_year}")
            enhanced.append(f"{query} Q4 {last_year}")

    return enhanced


# =============================================================================
# Multi-Source Fact Validation
# =============================================================================


def validate_fact_across_sources(
    fact: str, fact_type: str, sources: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Validate a fact by checking how many sources mention it.

    Args:
        fact: The fact to validate (e.g., "Roberto Laratro")
        fact_type: Type of fact (e.g., "CEO")
        sources: List of source dictionaries with 'content' key

    Returns:
        Dict with validation results
    """
    mention_count = 0
    mentioning_sources = []

    fact_lower = fact.lower()

    for source in sources:
        content = source.get("content", "").lower()
        if fact_lower in content:
            mention_count += 1
            mentioning_sources.append(source.get("url", "unknown"))

    confidence = "high" if mention_count >= 3 else "medium" if mention_count >= 2 else "low"

    return {
        "fact": fact,
        "fact_type": fact_type,
        "mention_count": mention_count,
        "confidence": confidence,
        "sources": mentioning_sources[:5],
        "validated": mention_count >= 2,
    }


# =============================================================================
# Main Autonomous Research Function
# =============================================================================


def run_autonomous_discovery(
    company_name: str, required_fields: List[str] = None
) -> Dict[str, Any]:
    """
    Run the full autonomous discovery process.

    This is the main entry point that:
    1. Discovers company context from web (no hardcoded knowledge)
    2. Generates targeted queries for missing fields
    3. Extracts fields semantically
    4. Validates facts across sources

    Args:
        company_name: Company to research
        required_fields: Fields that must be found

    Returns:
        Dict with discovered context and extracted fields
    """
    if required_fields is None:
        required_fields = ["ceo", "revenue", "market_share", "competitors", "products"]

    logger.info(f"[AUTONOMOUS] Starting autonomous discovery for: {company_name}")

    # Phase 1: Discovery
    context = discovery_phase(company_name)

    # Phase 2: Identify gaps
    discovered_fields = set()
    if context.current_ceo:
        discovered_fields.add("ceo")
    if context.competitors:
        discovered_fields.add("competitors")
    if context.key_products:
        discovered_fields.add("products")
    if context.regulator:
        discovered_fields.add("regulatory")

    missing_fields = [f for f in required_fields if f.lower() not in discovered_fields]

    # Phase 3: Generate gap-driven queries
    if missing_fields:
        targeted_queries = generate_gap_driven_queries(
            company_name=company_name, context=context, missing_fields=missing_fields
        )

        # Phase 4: Execute targeted searches
        router = get_search_router()
        additional_results = []

        for query in targeted_queries[:10]:  # Limit to avoid excessive API calls
            try:
                response = router.search(query=query, quality="premium", max_results=3)
                if response.success and response.results:
                    for item in response.results:
                        result_dict = item.to_dict()
                        additional_results.append(
                            {
                                "query": query,
                                "content": result_dict.get("snippet", ""),
                                "url": result_dict.get("url", ""),
                            }
                        )
            except (RuntimeError, ValueError, TypeError, AttributeError) as e:
                logger.warning(f"Targeted search failed: {query[:40]}... - {e}")

        # Phase 5: Semantic extraction from additional results
        if additional_results:
            combined_text = "\n\n".join([r["content"] for r in additional_results])
            extracted = extract_all_fields_semantically(
                text=combined_text,
                company_name=company_name,
                fields=["CEO", "Market Share", "Revenue", "Subscribers"],
            )

            # Update context with extracted fields
            if extracted.get("CEO") and not context.current_ceo:
                context.current_ceo = extracted["CEO"]

    return {
        "company_name": company_name,
        "context": context.to_dict(),
        "discovery_sources": context.discovery_sources,
        "missing_fields": missing_fields,
        "confidence": context.discovery_confidence,
    }


# =============================================================================
# Previous Run Loading - Build on Past Research
# =============================================================================


@dataclass
class PreviousResearchResult:
    """Extracted data from a previous research run."""

    company_name: str
    company_slug: str
    report_path: str
    timestamp: Optional[str] = None
    quality_score: float = 0.0
    extracted_fields: Dict[str, Any] = field(default_factory=dict)
    missing_fields: List[str] = field(default_factory=list)
    sources_count: int = 0
    raw_content: str = ""


def _normalize_company_slug(company_name: str) -> str:
    """Convert company name to folder slug format."""
    import re

    slug = company_name.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = slug.strip("_")
    return slug


def _get_outputs_dir() -> Path:
    """Get the outputs directory path."""
    # Try to get from config, fallback to default
    try:
        from ..config import get_config

        config = get_config()
        return Path(config.output_dir)
    except (ImportError, AttributeError, RuntimeError, ValueError, TypeError):
        # Fallback to outputs in project root
        return Path("outputs")


def load_previous_research(company_name: str) -> Optional[PreviousResearchResult]:
    """
    Load previous research results for a company.

    This enables incremental research - we don't re-research what we already know,
    we focus on filling gaps and validating existing data.

    Args:
        company_name: Name of the company

    Returns:
        PreviousResearchResult or None if no previous research exists
    """
    outputs_dir = _get_outputs_dir()
    slug = _normalize_company_slug(company_name)
    company_dir = outputs_dir / slug

    if not company_dir.exists():
        logger.info(f"[PREVIOUS] No previous research found for {company_name}")
        return None

    # Load the full report
    report_path = company_dir / "00_full_report.md"
    if not report_path.exists():
        # Try alternative names
        for alt in ["report.md", "full_report.md", "00_full_report_enhanced.md"]:
            alt_path = company_dir / alt
            if alt_path.exists():
                report_path = alt_path
                break
        else:
            logger.warning(f"[PREVIOUS] No report file found in {company_dir}")
            return None

    # Read report content
    try:
        raw_content = report_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as e:
        logger.error(f"[PREVIOUS] Failed to read report: {e}")
        return None

    # Load metrics if available
    metrics_path = company_dir / "metrics.json"
    quality_score = 0.0
    timestamp = None
    sources_count = 0

    if metrics_path.exists():
        try:
            import json

            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            quality_score = metrics.get("quality_score", 0.0)
            timestamp = metrics.get("timestamp")
            sources_count = metrics.get("sources_count", 0)
        except (OSError, json.JSONDecodeError, ValueError, TypeError) as e:
            logger.warning(f"[PREVIOUS] Failed to load metrics: {e}")

    # Extract fields from report using LLM
    extracted_fields = _extract_fields_from_report(raw_content, company_name)

    # Identify missing fields
    missing_fields = _identify_missing_fields(extracted_fields)

    result = PreviousResearchResult(
        company_name=company_name,
        company_slug=slug,
        report_path=str(report_path),
        timestamp=timestamp,
        quality_score=quality_score,
        extracted_fields=extracted_fields,
        missing_fields=missing_fields,
        sources_count=sources_count,
        raw_content=raw_content[:10000],  # Truncate for memory
    )

    logger.info(
        f"[PREVIOUS] Loaded research for {company_name}: "
        f"quality={quality_score:.1f}, sources={sources_count}, "
        f"missing={len(missing_fields)} fields"
    )

    return result


EXTRACT_FIELDS_PROMPT = """Analyze this research report and extract structured information.

Report for: {company_name}

Content:
{content}

Extract the following information. Return ONLY what is explicitly stated in the report.
Use "NOT_FOUND" for any field that is not mentioned or says "Not specified".

Return as JSON:
{{
    "ceo": "Name of CEO/General Manager or NOT_FOUND",
    "revenue": "Revenue figure with currency or NOT_FOUND",
    "revenue_growth": "Revenue growth percentage or NOT_FOUND",
    "market_share": "Market share percentage or NOT_FOUND",
    "subscribers": "Number of subscribers/customers or NOT_FOUND",
    "employees": "Number of employees or NOT_FOUND",
    "founded_year": "Year founded or NOT_FOUND",
    "headquarters": "Headquarters location or NOT_FOUND",
    "parent_company": "Parent/holding company or NOT_FOUND",
    "competitors": ["List of competitors mentioned"] or [],
    "products": ["List of products/services"] or [],
    "regulator": "Industry regulator name or NOT_FOUND",
    "stock_ticker": "Stock ticker symbol or NOT_FOUND",
    "ebitda": "EBITDA figure or NOT_FOUND",
    "net_income": "Net income figure or NOT_FOUND"
}}

Return ONLY the JSON, no other text."""


def _extract_fields_from_report(content: str, company_name: str) -> Dict[str, Any]:
    """Extract structured fields from a report using LLM."""
    # Truncate content to avoid context overflow
    content = content[:8000]

    prompt = EXTRACT_FIELDS_PROMPT.format(company_name=company_name, content=content)

    try:
        result = _call_llm(prompt, max_tokens=1000)

        # Parse JSON
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]

        start_idx = result.find("{")
        end_idx = result.rfind("}")
        if start_idx >= 0 and end_idx >= 0:
            json_str = result[start_idx : end_idx + 1]
            return json.loads(json_str)

        return json.loads(result)

    except (json.JSONDecodeError, ValueError, TypeError, KeyError) as e:
        logger.error(f"[EXTRACT] Failed to extract fields: {e}")
        return {}


def _identify_missing_fields(extracted: Dict[str, Any]) -> List[str]:
    """Identify which critical fields are missing."""
    critical_fields = [
        "ceo",
        "revenue",
        "market_share",
        "subscribers",
        "employees",
        "founded_year",
        "headquarters",
        "parent_company",
        "competitors",
        "regulator",
    ]

    missing = []
    for field in critical_fields:
        value = extracted.get(field)
        if value is None or value == "NOT_FOUND" or value == [] or value == "":
            missing.append(field)

    return missing


def load_all_previous_research() -> Dict[str, PreviousResearchResult]:
    """
    Load all previous research results from outputs directory.

    Returns:
        Dict mapping company slug to PreviousResearchResult
    """
    outputs_dir = _get_outputs_dir()
    if not outputs_dir.exists():
        return {}

    results = {}

    for company_dir in outputs_dir.iterdir():
        if not company_dir.is_dir():
            continue

        # Skip non-company directories
        if company_dir.name in ["research", "visualizations", "telecom_research"]:
            continue

        # Convert slug back to company name
        company_name = company_dir.name.replace("_", " ").title()

        try:
            result = load_previous_research(company_name)
            if result:
                results[company_dir.name] = result
        except (OSError, UnicodeError, ValueError, TypeError) as e:
            logger.warning(f"[PREVIOUS] Failed to load {company_dir.name}: {e}")

    logger.info(f"[PREVIOUS] Loaded {len(results)} previous research results")
    return results


# =============================================================================
# Gap Analysis - Understand What's Missing
# =============================================================================


@dataclass
class GapAnalysis:
    """Analysis of gaps in previous research."""

    company_name: str
    quality_score: float
    total_fields: int
    found_fields: int
    missing_fields: List[str]
    priority_fields: List[str]  # Fields that should be re-researched first
    stale_fields: List[str]  # Fields that may need updating
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "quality_score": self.quality_score,
            "total_fields": self.total_fields,
            "found_fields": self.found_fields,
            "missing_fields": self.missing_fields,
            "priority_fields": self.priority_fields,
            "stale_fields": self.stale_fields,
            "recommendations": self.recommendations,
        }


def analyze_research_gaps(previous: PreviousResearchResult) -> GapAnalysis:
    """
    Analyze gaps in previous research to guide targeted re-research.

    Args:
        previous: Previous research result

    Returns:
        GapAnalysis with prioritized missing fields
    """
    critical_fields = [
        "ceo",
        "revenue",
        "market_share",
        "subscribers",
        "employees",
        "founded_year",
        "headquarters",
        "parent_company",
        "competitors",
        "regulator",
    ]

    # Count found vs missing
    found = []
    missing = []

    for field in critical_fields:
        value = previous.extracted_fields.get(field)
        if value and value != "NOT_FOUND" and value != []:
            found.append(field)
        else:
            missing.append(field)

    # Prioritize critical fields
    high_priority = ["ceo", "revenue", "market_share", "subscribers"]
    priority_fields = [f for f in missing if f in high_priority]

    # Identify stale fields (older than 6 months would need rechecking)
    stale_fields = []
    if previous.timestamp:
        try:
            from datetime import datetime

            ts = datetime.strptime(previous.timestamp, "%Y%m%d_%H%M%S")
            age_days = (datetime.now() - ts).days
            if age_days > 180:
                # Revenue, market share, subscribers can change frequently
                stale_fields = ["revenue", "market_share", "subscribers", "employees"]
        except (ValueError, TypeError):
            pass

    # Generate recommendations
    recommendations = []
    if "ceo" in missing:
        recommendations.append("Search for recent leadership announcements")
    if "market_share" in missing:
        recommendations.append("Search industry reports for market share data")
    if "revenue" in missing:
        recommendations.append("Search for annual reports or financial news")
    if "subscribers" in missing:
        recommendations.append("Search for subscriber/customer count announcements")
    if stale_fields:
        recommendations.append(f"Update stale data: {', '.join(stale_fields)}")

    return GapAnalysis(
        company_name=previous.company_name,
        quality_score=previous.quality_score,
        total_fields=len(critical_fields),
        found_fields=len(found),
        missing_fields=missing,
        priority_fields=priority_fields,
        stale_fields=stale_fields,
        recommendations=recommendations,
    )


# =============================================================================
# Cross-Company Data Checking
# =============================================================================


@dataclass
class CrossCompanyData:
    """Data found in other company research that may be relevant."""

    source_company: str
    field_name: str
    value: Any
    context: str  # How this data relates to the target company
    confidence: str  # "high", "medium", "low"


def find_relevant_cross_company_data(
    target_company: str, all_research: Dict[str, PreviousResearchResult]
) -> List[CrossCompanyData]:
    """
    Search all previous research for data relevant to target company.

    For example, if researching "Tigo Paraguay" and we have research on "Millicom",
    we might find that Millicom is Tigo's parent company and extract relevant data.

    Args:
        target_company: Company being researched
        all_research: All previous research results

    Returns:
        List of relevant cross-company data points
    """
    target_lower = target_company.lower()
    relevant_data = []

    for slug, research in all_research.items():
        # Skip if this is the target company itself
        if _normalize_company_slug(target_company) == slug:
            continue

        # Check if target company is mentioned in this research
        if target_lower in research.raw_content.lower():
            # This company's research mentions our target - extract context
            context = _extract_mention_context(
                research.raw_content, target_company, research.company_name
            )

            if context:
                relevant_data.append(
                    CrossCompanyData(
                        source_company=research.company_name,
                        field_name="mention",
                        value=target_company,
                        context=context,
                        confidence="medium",
                    )
                )

        # Check if this company is the parent of target
        parent = research.extracted_fields.get("parent_company", "")
        if parent and parent != "NOT_FOUND":
            # Check if target mentions this parent
            pass  # Will be checked in the target's research

        # Check if target is a subsidiary mentioned in this research
        if target_lower in str(research.extracted_fields).lower():
            # Look for specific field mentions
            for field, value in research.extracted_fields.items():
                if isinstance(value, str) and target_lower in value.lower():
                    relevant_data.append(
                        CrossCompanyData(
                            source_company=research.company_name,
                            field_name=field,
                            value=value,
                            context=f"Found in {research.company_name}'s {field}",
                            confidence="high",
                        )
                    )

    logger.info(
        f"[CROSS-CHECK] Found {len(relevant_data)} relevant data points from other companies"
    )
    return relevant_data


def _extract_mention_context(content: str, target: str, source_company: str) -> Optional[str]:
    """Extract context around where target company is mentioned."""
    target_lower = target.lower()
    content_lower = content.lower()

    idx = content_lower.find(target_lower)
    if idx == -1:
        return None

    # Extract surrounding context (200 chars before and after)
    start = max(0, idx - 200)
    end = min(len(content), idx + len(target) + 200)

    context = content[start:end].strip()

    # Clean up
    context = context.replace("\n", " ").replace("  ", " ")

    return f"In {source_company}: ...{context}..."


# =============================================================================
# Inconsistency Detection
# =============================================================================


@dataclass
class DataInconsistency:
    """Detected inconsistency between data sources."""

    field_name: str
    company_a: str
    value_a: Any
    company_b: str
    value_b: Any
    severity: str  # "critical", "warning", "info"
    explanation: str


def detect_inconsistencies(
    target_company: str,
    target_data: Dict[str, Any],
    all_research: Dict[str, PreviousResearchResult],
) -> List[DataInconsistency]:
    """
    Detect inconsistencies between target company data and other sources.

    For example, if Tigo Paraguay says parent is "Millicom" but Millicom research
    doesn't mention Tigo Paraguay as a subsidiary, flag it.

    Args:
        target_company: Company being researched
        target_data: Extracted data for target company
        all_research: All previous research results

    Returns:
        List of detected inconsistencies
    """
    inconsistencies = []

    # Check parent company consistency
    target_parent = target_data.get("parent_company", "")
    if target_parent and target_parent != "NOT_FOUND":
        parent_slug = _normalize_company_slug(target_parent)

        if parent_slug in all_research:
            parent_research = all_research[parent_slug]
            # Check if parent research mentions target as subsidiary
            if target_company.lower() not in parent_research.raw_content.lower():
                inconsistencies.append(
                    DataInconsistency(
                        field_name="parent_company",
                        company_a=target_company,
                        value_a=f"Parent: {target_parent}",
                        company_b=target_parent,
                        value_b="Does not mention target as subsidiary",
                        severity="warning",
                        explanation=f"{target_company} claims {target_parent} as parent, but {target_parent}'s research doesn't mention it",
                    )
                )

    # Check competitor consistency
    target_competitors = target_data.get("competitors", [])
    if isinstance(target_competitors, list):
        for competitor in target_competitors:
            comp_slug = _normalize_company_slug(competitor)
            if comp_slug in all_research:
                comp_research = all_research[comp_slug]
                comp_competitors = comp_research.extracted_fields.get("competitors", [])

                # Check if relationship is bidirectional
                target_in_comp = (
                    any(target_company.lower() in str(c).lower() for c in comp_competitors)
                    if isinstance(comp_competitors, list)
                    else False
                )

                if not target_in_comp:
                    inconsistencies.append(
                        DataInconsistency(
                            field_name="competitors",
                            company_a=target_company,
                            value_a=f"Lists {competitor} as competitor",
                            company_b=competitor,
                            value_b="Does not list target as competitor",
                            severity="info",
                            explanation="Competitive relationship not confirmed bidirectionally",
                        )
                    )

    # Check for numerical inconsistencies in market share
    target_market_share = target_data.get("market_share", "")
    if target_market_share and target_market_share != "NOT_FOUND":
        # Sum market shares of all companies in same market
        market_shares = {target_company: _parse_percentage(target_market_share)}

        for slug, research in all_research.items():
            if _normalize_company_slug(target_company) == slug:
                continue

            ms = research.extracted_fields.get("market_share", "")
            if ms and ms != "NOT_FOUND":
                market_shares[research.company_name] = _parse_percentage(ms)

        total = sum(v for v in market_shares.values() if v is not None)
        if total > 100:
            inconsistencies.append(
                DataInconsistency(
                    field_name="market_share",
                    company_a="All companies",
                    value_a=f"Total: {total:.1f}%",
                    company_b="Expected",
                    value_b="<= 100%",
                    severity="critical",
                    explanation=f"Market shares sum to {total:.1f}%, exceeds 100%",
                )
            )

    logger.info(f"[INCONSISTENCY] Found {len(inconsistencies)} potential inconsistencies")
    return inconsistencies


def _parse_percentage(value: str) -> Optional[float]:
    """Parse a percentage string to float."""
    import re

    if not value or value == "NOT_FOUND":
        return None

    # Extract number from string like "45%", "45 percent", "45.5%"
    match = re.search(r"(\d+(?:\.\d+)?)\s*%?", str(value))
    if match:
        return float(match.group(1))
    return None


# =============================================================================
# Integrated Research with Historical Context
# =============================================================================


def run_research_with_history(
    company_name: str, required_fields: List[str] = None, use_cross_company: bool = True
) -> Dict[str, Any]:
    """
    Run research that builds on previous results.

    This is the MAIN entry point that:
    1. Loads previous research for context
    2. Identifies gaps in previous research
    3. Checks other companies for relevant data
    4. Detects inconsistencies
    5. Runs targeted discovery only for missing/stale fields

    Args:
        company_name: Company to research
        required_fields: Fields that must be found
        use_cross_company: Whether to check other company research

    Returns:
        Dict with research results and historical context
    """
    if required_fields is None:
        required_fields = ["ceo", "revenue", "market_share", "competitors", "subscribers"]

    logger.info(f"[RESEARCH] Starting research with history for: {company_name}")

    # Step 1: Load previous research
    previous = load_previous_research(company_name)

    # Step 2: Load all research for cross-checking
    all_research = {}
    cross_company_data = []
    inconsistencies = []

    if use_cross_company:
        all_research = load_all_previous_research()

        if previous:
            cross_company_data = find_relevant_cross_company_data(company_name, all_research)
            inconsistencies = detect_inconsistencies(
                company_name, previous.extracted_fields, all_research
            )

    # Step 3: Analyze gaps
    gap_analysis = None
    fields_to_research = required_fields  # Default to all fields

    if previous:
        gap_analysis = analyze_research_gaps(previous)

        # Only research missing and stale fields
        fields_to_research = list(set(gap_analysis.missing_fields + gap_analysis.stale_fields))

        logger.info(
            f"[RESEARCH] Previous research found. Focusing on {len(fields_to_research)} fields: {fields_to_research}"
        )
    else:
        logger.info(
            f"[RESEARCH] No previous research. Researching all {len(required_fields)} fields"
        )

    # Step 4: Run discovery (only if we have fields to research)
    discovery_result = None
    if fields_to_research:
        # Use previous context if available
        initial_context = None
        if previous:
            initial_context = DiscoveredContext(
                company_name=company_name,
                parent_company=(
                    previous.extracted_fields.get("parent_company")
                    if previous.extracted_fields.get("parent_company") != "NOT_FOUND"
                    else None
                ),
                industry=(
                    previous.extracted_fields.get("industry")
                    if previous.extracted_fields.get("industry") != "NOT_FOUND"
                    else None
                ),
                country=(
                    previous.extracted_fields.get("country")
                    if previous.extracted_fields.get("country") != "NOT_FOUND"
                    else None
                ),
            )

        discovery_result = run_autonomous_discovery(
            company_name=company_name, required_fields=fields_to_research
        )

    return {
        "company_name": company_name,
        "has_previous_research": previous is not None,
        "previous_quality_score": previous.quality_score if previous else None,
        "previous_timestamp": previous.timestamp if previous else None,
        "gap_analysis": gap_analysis.to_dict() if gap_analysis else None,
        "fields_researched": fields_to_research,
        "cross_company_data": [
            {
                "source": d.source_company,
                "field": d.field_name,
                "value": d.value,
                "context": d.context,
                "confidence": d.confidence,
            }
            for d in cross_company_data
        ],
        "inconsistencies": [
            {"field": i.field_name, "severity": i.severity, "explanation": i.explanation}
            for i in inconsistencies
        ],
        "discovery_result": discovery_result,
        "previous_extracted_fields": previous.extracted_fields if previous else {},
    }
