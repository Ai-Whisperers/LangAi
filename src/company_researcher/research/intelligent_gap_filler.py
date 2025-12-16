"""
Intelligent Gap Filler - AI-driven gap detection and targeted query generation.

This module:
1. Analyzes research output to identify specific data gaps
2. Generates targeted queries using AI to fill those gaps
3. Executes searches and extracts data
4. Validates extracted data against sources

Enhanced with:
- Parent company traversal: Auto-queries parent company SEC/investor relations
- Founded date fallback: Wikipedia-specific queries for establishment dates
- Brand disambiguation: Uses legal names for ambiguous brands

The key insight: Generic queries produce generic results.
Targeted queries for specific missing data points yield precise information.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..agents.research.multilingual_search import BRAND_DISAMBIGUATION_MAP, PARENT_COMPANY_MAP
from ..integrations.search_router import get_search_router
from ..llm.smart_client import SmartLLMClient
from ..utils import get_logger

logger = get_logger(__name__)


# Parent company details for SEC/investor relations lookups
PARENT_COMPANY_DETAILS = {
    "Telecom Argentina": {
        "ticker": "TEO",
        "sec_cik": "0001058290",
        "investor_relations": "https://inversores.telecom.com.ar/",
        "subsidiaries": ["Personal Argentina", "Personal Paraguay", "Núcleo S.A."],
        "holding_company": "Grupo Clarín",
    },
    "Millicom International": {
        "ticker": "TIGO",
        "sec_cik": None,  # Not SEC-registered
        "investor_relations": "https://www.millicom.com/investors/",
        "subsidiaries": [
            "Tigo Paraguay",
            "Tigo Guatemala",
            "Tigo Honduras",
            "Tigo Colombia",
            "Tigo Bolivia",
        ],
        "exchange": "NASDAQ",
    },
    "América Móvil": {
        "ticker": "AMX",
        "sec_cik": "0001129137",
        "investor_relations": "https://www.americamovil.com/investors/",
        "subsidiaries": ["Claro", "Telcel", "Telmex", "TracFone"],
    },
    "Telefónica": {
        "ticker": "TEF",
        "sec_cik": "0000814052",
        "investor_relations": "https://www.telefonica.com/en/shareholders-investors/",
        "subsidiaries": ["Movistar", "Vivo", "O2"],
    },
}


class GapPriority(Enum):
    """Priority levels for data gaps."""

    CRITICAL = "critical"  # CEO, revenue, market share
    HIGH = "high"  # Subscribers, competitors, products
    MEDIUM = "medium"  # ESG, regulatory, history
    LOW = "low"  # Nice-to-have details


@dataclass
class DataGap:
    """Represents a specific gap in research data."""

    field_name: str
    category: str
    priority: GapPriority
    current_value: Optional[str] = None  # What we have (might be outdated/wrong)
    expected_format: str = ""  # "number", "name", "percentage", "date", "text"
    context_hint: str = ""  # Additional context for query generation
    generated_queries: List[str] = field(default_factory=list)
    found_value: Optional[str] = None
    found_source: Optional[str] = None
    confidence: float = 0.0


@dataclass
class GapAnalysisResult:
    """Result of gap analysis."""

    company_name: str
    gaps: List[DataGap]
    total_gaps: int
    critical_gaps: int
    analysis_timestamp: str
    quality_before: float = 0.0


class IntelligentGapFiller:
    """
    AI-driven gap detection and filling system.

    Workflow:
    1. Analyze existing research to identify gaps
    2. Prioritize gaps by business importance
    3. Generate targeted queries for each gap
    4. Execute searches with appropriate providers
    5. Extract and validate data from results
    6. Update research with validated data
    """

    # Standard fields we expect in comprehensive research
    EXPECTED_FIELDS = {
        "leadership": {
            "fields": ["ceo_name", "ceo_appointed_date", "cfo_name", "other_executives"],
            "priority": GapPriority.CRITICAL,
            "query_templates": [
                "{company} CEO director general {year}",
                "{company} nuevo gerente general nombrado {year}",
                "{company} executive leadership team {year}",
                "who is the CEO of {company} {year}",
            ],
        },
        "financial": {
            "fields": ["revenue", "revenue_year", "ebitda", "profit_margin", "assets"],
            "priority": GapPriority.CRITICAL,
            "query_templates": [
                "{company} revenue ingresos {year}",
                "{company} financial results Q{quarter} {year}",
                "{parent_company} {country} earnings report {year}",
            ],
        },
        "market_position": {
            "fields": ["market_share", "market_share_year", "market_rank", "subscriber_count"],
            "priority": GapPriority.CRITICAL,
            "query_templates": [
                "{company} market share cuota mercado {year}",
                "{company} subscribers usuarios {year}",
                "{regulator} {country} telecommunications statistics {year}",
            ],
        },
        "regulatory": {
            "fields": ["regulator_name", "licenses", "spectrum_bands", "5g_status"],
            "priority": GapPriority.HIGH,
            "query_templates": [
                "{regulator} {company} license spectrum",
                "{company} 5G licitacion espectro {year}",
                "{country} telecommunications regulatory {year}",
            ],
        },
        "business_segments": {
            "fields": ["main_products", "segment_revenue", "digital_services"],
            "priority": GapPriority.HIGH,
            "query_templates": [
                "{company} productos servicios offerings",
                "{company} {segment} revenue users {year}",
            ],
        },
        "competitors": {
            "fields": ["main_competitors", "competitive_position"],
            "priority": GapPriority.HIGH,
            "query_templates": [
                "{company} vs {competitor} comparison {country}",
                "{country} {industry} market competition {year}",
            ],
        },
    }

    def __init__(self, preferred_provider: Optional[str] = None):
        """
        Initialize the gap filler.

        Args:
            preferred_provider: Force a specific search provider (e.g., "tavily", "serper")
                              to avoid timeout issues with default providers.
        """
        self.llm = SmartLLMClient()
        self.search_router = get_search_router()
        self.preferred_provider = preferred_provider
        self.parent_company_map = PARENT_COMPANY_MAP
        self.parent_company_details = PARENT_COMPANY_DETAILS

    # =========================================================================
    # Parent Company Traversal
    # =========================================================================

    def get_parent_company_info(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Look up parent company and get detailed investor relations info.

        For subsidiaries like "Personal Paraguay", returns parent company
        details including SEC CIK, ticker, and investor relations URLs.

        Args:
            company_name: Name of the subsidiary company

        Returns:
            Dict with parent company details or None if not found
        """
        name_lower = company_name.lower().strip()

        # Find parent company name
        parent_name = None
        for key, parent in self.parent_company_map.items():
            if key in name_lower or name_lower in key:
                parent_name = parent
                break

        if not parent_name:
            return None

        # Get detailed parent info
        parent_details = self.parent_company_details.get(parent_name)
        if parent_details:
            return {"parent_name": parent_name, **parent_details}

        return {"parent_name": parent_name}

    def generate_parent_company_queries(
        self, company_name: str, gap_type: str, year: int
    ) -> List[str]:
        """
        Generate queries targeting parent company SEC/investor relations.

        Args:
            company_name: Subsidiary company name
            gap_type: Type of data gap (e.g., "revenue", "ceo")
            year: Year for the data

        Returns:
            List of parent company queries
        """
        parent_info = self.get_parent_company_info(company_name)
        if not parent_info:
            return []

        parent_name = parent_info.get("parent_name", "")
        ticker = parent_info.get("ticker", "")
        sec_cik = parent_info.get("sec_cik")

        queries = []

        if gap_type in ["revenue", "financial", "ebitda", "profit"]:
            # Financial queries targeting investor relations
            queries.append(f"{parent_name} {company_name} revenue {year} annual report")
            if ticker:
                queries.append(f"{ticker} subsidiary {company_name} financial results {year}")
            if sec_cik:
                queries.append(f"SEC EDGAR {parent_name} 20-F {year} {company_name}")
            queries.append(f"{parent_name} investor relations {company_name} segment revenue")

        elif gap_type in ["ceo", "leadership", "executive"]:
            queries.append(f"{parent_name} {company_name} management team executives")
            queries.append(f"{company_name} director general CEO appointed {year}")

        elif gap_type in ["market_share", "subscribers"]:
            queries.append(f"{parent_name} earnings call {company_name} subscribers {year}")
            queries.append(f"{parent_name} quarterly report {company_name} market share")

        return queries

    # =========================================================================
    # Founded Date Fallback
    # =========================================================================

    def generate_founded_date_queries(
        self, company_name: str, legal_name: Optional[str] = None, country: Optional[str] = None
    ) -> List[str]:
        """
        Generate targeted queries to find company founding date.

        Uses Wikipedia and official sources as primary targets.

        Args:
            company_name: Company name
            legal_name: Legal/registered name if different
            country: Country of incorporation

        Returns:
            List of founded date queries
        """
        queries = []

        # Wikipedia is often the best source for founding dates
        queries.append(f'site:wikipedia.org "{company_name}" founded established')
        if legal_name and legal_name != company_name:
            queries.append(f'site:wikipedia.org "{legal_name}" founded established')

        # Company profile sites
        queries.append(f'"{company_name}" "founded in" OR "established in" OR "incorporated"')
        queries.append(f'"{company_name}" company history founding year')

        # Country-specific queries
        if country:
            queries.append(f'"{company_name}" {country} company founded history')

        # Spanish queries for LATAM
        queries.append(f'"{company_name}" fundada fundación año historia')
        if legal_name:
            queries.append(f'"{legal_name}" constituida fundación')

        # Official sources
        queries.append(f'"{company_name}" "about us" history founded')

        return queries

    def extract_founded_date(self, text: str, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Extract founding date from text using pattern matching.

        Args:
            text: Text to search
            company_name: Company name for context

        Returns:
            Dict with year and context, or None
        """
        # Patterns for founding dates
        patterns = [
            # "founded in 1998" / "established in 1998"
            r"(?:founded|established|incorporated|created|launched)\s+(?:in\s+)?(\d{4})",
            # "fundada en 1998" / "constituida en 1998"
            r"(?:fundad[ao]|establecid[ao]|constituid[ao]|cread[ao])\s+(?:en\s+)?(\d{4})",
            # "since 1998" / "desde 1998"
            r"(?:since|desde)\s+(\d{4})",
            # "(1998)" in context of founding
            r"(?:founding|foundation|fundación|inicio)\s*[\(\[]?(\d{4})[\)\]]?",
        ]

        text_lower = text.lower()
        company_lower = company_name.lower()

        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                year = int(match)
                # Sanity check: year should be between 1800 and current year
                if 1800 <= year <= datetime.now().year:
                    # Check if company name is nearby in text
                    if company_lower in text_lower:
                        return {"year": year, "pattern_matched": pattern, "confidence": 0.8}

        return None

    def analyze_gaps(
        self, company_name: str, research_data: Dict[str, Any], report_text: str = ""
    ) -> GapAnalysisResult:
        """
        Use AI to analyze research output and identify specific gaps.

        Args:
            company_name: Name of the company
            research_data: Structured data from research (dict)
            report_text: Full text of the research report

        Returns:
            GapAnalysisResult with prioritized list of gaps
        """
        logger.info(f"[GAP-ANALYSIS] Analyzing gaps for: {company_name}")

        # Prepare context for AI analysis
        data_summary = json.dumps(research_data, indent=2, default=str)[:5000]
        report_excerpt = report_text[:3000] if report_text else ""

        analysis_prompt = f"""Analyze this research output for {company_name} and identify specific data gaps.

RESEARCH DATA:
{data_summary}

REPORT EXCERPT:
{report_excerpt}

IDENTIFY GAPS IN THESE CATEGORIES:
1. Leadership (CEO name, appointment date, other executives)
2. Financial (revenue, EBITDA, profit margin, assets - must be current year data)
3. Market Position (market share %, subscriber count, market rank)
4. Regulatory (regulator interactions, licenses, spectrum, 5G status)
5. Business Segments (product details, segment revenue, digital services)
6. Competitors (specific competitor data, competitive analysis)

For each gap found, provide:
- field_name: specific data point missing (e.g., "ceo_name", "2024_revenue")
- category: one of leadership/financial/market_position/regulatory/business_segments/competitors
- priority: critical/high/medium/low
- current_value: what the report says (if anything, might be wrong/outdated)
- expected_format: number/name/percentage/date/text
- context_hint: specific context to help search (e.g., "parent company is Millicom")

IMPORTANT:
- Flag data that is outdated (>1 year old) as a gap
- Flag data marked "Not Available" or "Not specified" as gaps
- Flag fabricated-looking data (round numbers, generic statements) as gaps
- Prioritize data that affects investment/business decisions

Return JSON array of gaps:
[
  {{
    "field_name": "ceo_name",
    "category": "leadership",
    "priority": "critical",
    "current_value": "Not specified",
    "expected_format": "name",
    "context_hint": "May be called Director General in Spanish"
  }},
  ...
]"""

        try:
            result = self.llm.complete(
                prompt=analysis_prompt,
                system="You are a research quality analyst. Identify specific data gaps in company research. Return valid JSON only.",
                task_type="extraction",
                max_tokens=2000,
                json_mode=True,
            )

            # Handle various result types
            logger.debug(f"[GAP-ANALYSIS] Result type: {type(result)}")
            if isinstance(result, str):
                content = result
            elif hasattr(result, "content"):
                content = result.content
            elif isinstance(result, dict):
                content = result.get("content", "[]")
            else:
                content = "[]"

            logger.debug(
                f"[GAP-ANALYSIS] Content (first 500 chars): {content[:500] if content else 'empty'}"
            )
            parsed = json.loads(content)

            # Handle both direct array and wrapped {"gaps": [...]} formats
            if isinstance(parsed, dict) and "gaps" in parsed:
                gaps_data = parsed["gaps"]
            elif isinstance(parsed, list):
                gaps_data = parsed
            else:
                logger.warning(f"[GAP-ANALYSIS] Unexpected JSON structure: {type(parsed)}")
                gaps_data = []

            logger.debug(
                f"[GAP-ANALYSIS] Parsed {len(gaps_data)} items, first item type: {type(gaps_data[0]) if gaps_data else 'N/A'}"
            )

            # Convert to DataGap objects
            gaps = []
            for g in gaps_data:
                if not isinstance(g, dict):
                    logger.warning(f"[GAP-ANALYSIS] Skipping non-dict item: {type(g)}")
                    continue
                priority = GapPriority(g.get("priority", "medium"))
                gap = DataGap(
                    field_name=g.get("field_name", ""),
                    category=g.get("category", ""),
                    priority=priority,
                    current_value=g.get("current_value"),
                    expected_format=g.get("expected_format", "text"),
                    context_hint=g.get("context_hint", ""),
                )
                gaps.append(gap)

            # Sort by priority
            priority_order = {
                GapPriority.CRITICAL: 0,
                GapPriority.HIGH: 1,
                GapPriority.MEDIUM: 2,
                GapPriority.LOW: 3,
            }
            gaps.sort(key=lambda x: priority_order[x.priority])

            critical_count = sum(1 for g in gaps if g.priority == GapPriority.CRITICAL)

            logger.info(f"[GAP-ANALYSIS] Found {len(gaps)} gaps ({critical_count} critical)")

            return GapAnalysisResult(
                company_name=company_name,
                gaps=gaps,
                total_gaps=len(gaps),
                critical_gaps=critical_count,
                analysis_timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"[GAP-ANALYSIS] Error: {e}")
            return GapAnalysisResult(
                company_name=company_name,
                gaps=[],
                total_gaps=0,
                critical_gaps=0,
                analysis_timestamp=datetime.now().isoformat(),
            )

    def generate_targeted_queries(
        self, company_name: str, gaps: List[DataGap], company_context: Dict[str, Any]
    ) -> List[DataGap]:
        """
        Use AI to generate targeted search queries for each gap.

        Enhanced with:
        - Parent company traversal for financial/leadership gaps
        - Founded date specific queries
        - Brand disambiguation for generic names

        Args:
            company_name: Name of the company
            gaps: List of identified gaps
            company_context: Additional context (country, industry, parent company, etc.)

        Returns:
            Gaps with generated_queries populated
        """
        logger.info(f"[QUERY-GEN] Generating queries for {len(gaps)} gaps")

        current_year = datetime.now().year

        # Check for parent company info
        parent_info = self.get_parent_company_info(company_name)
        if parent_info:
            logger.info(f"[QUERY-GEN] Found parent company: {parent_info.get('parent_name')}")

        # Check for brand disambiguation
        legal_name = company_context.get("legal_name")
        if not legal_name:
            name_lower = company_name.lower()
            if name_lower in BRAND_DISAMBIGUATION_MAP:
                legal_name = BRAND_DISAMBIGUATION_MAP[name_lower][0]
                logger.info(f"[QUERY-GEN] Brand disambiguation: {company_name} -> {legal_name}")

        # Pre-generate specialized queries for specific gap types
        for gap in gaps:
            specialized_queries = []

            # Parent company queries for financial gaps
            if gap.category in ["financial", "market_position"] and parent_info:
                parent_queries = self.generate_parent_company_queries(
                    company_name, gap.field_name, current_year
                )
                specialized_queries.extend(parent_queries)
                logger.debug(
                    f"[QUERY-GEN] Added {len(parent_queries)} parent company queries for {gap.field_name}"
                )

            # Founded date queries
            if "founded" in gap.field_name.lower() or gap.field_name in [
                "founding_year",
                "established_date",
            ]:
                founded_queries = self.generate_founded_date_queries(
                    company_name, legal_name=legal_name, country=company_context.get("country")
                )
                specialized_queries.extend(founded_queries)
                logger.debug(f"[QUERY-GEN] Added {len(founded_queries)} founded date queries")

            # Store specialized queries to be merged later
            gap.generated_queries = specialized_queries

        # Prepare gap descriptions for AI
        gap_descriptions = []
        for i, gap in enumerate(gaps):
            gap_descriptions.append(
                f"{i+1}. {gap.field_name} ({gap.category}, {gap.priority.value})"
            )
            gap_descriptions.append(f"   Current: {gap.current_value or 'missing'}")
            gap_descriptions.append(f"   Format: {gap.expected_format}")
            gap_descriptions.append(f"   Hint: {gap.context_hint}")

        gaps_text = "\n".join(gap_descriptions)

        # Add parent company and legal name to context
        enhanced_context = {**company_context}
        if parent_info:
            enhanced_context["parent_company"] = parent_info.get("parent_name")
            enhanced_context["parent_ticker"] = parent_info.get("ticker")
        if legal_name:
            enhanced_context["legal_name"] = legal_name

        context_text = json.dumps(enhanced_context, indent=2)

        query_prompt = f"""Generate targeted search queries to find specific missing data for {company_name}.

COMPANY CONTEXT:
{context_text}

DATA GAPS TO FILL:
{gaps_text}

GENERATE SEARCH QUERIES:
For each gap, generate 2-3 highly specific search queries that would find that exact data point.

QUERY GUIDELINES:
1. Include company name and year ({current_year} or {current_year-1})
2. Use both English AND Spanish queries for LATAM companies
3. Include parent company name ({enhanced_context.get('parent_company', 'if known')}) for financial data
4. Include legal name ({enhanced_context.get('legal_name', 'if different')}) for official sources
5. Include regulator name for regulatory data
6. Use specific terms like "CEO appointed", "revenue Q3", "market share %"
7. Reference official sources: SEC filings, regulator reports, earnings calls
8. For founded dates, target Wikipedia and company "about us" pages

AVOID:
- Generic queries like "company profile"
- Queries without year/date context
- Queries that would return only Wikipedia summaries (except for founded date)

Return JSON mapping gap field names to query arrays:
{{
  "ceo_name": [
    "{company_name} CEO director general {current_year}",
    "{enhanced_context.get('legal_name', company_name)} nuevo CEO nombrado {current_year}",
    "{enhanced_context.get('parent_company', 'Parent')} {company_name} executive appointment {current_year}"
  ],
  "2024_revenue": [
    "{enhanced_context.get('parent_company', 'Parent')} {company_name} revenue Q3 {current_year} earnings",
    "{company_name} ingresos {current_year} resultados financieros"
  ],
  ...
}}"""

        try:
            result = self.llm.complete(
                prompt=query_prompt,
                system="You are a search query specialist. Generate precise, targeted queries to find specific data. Return valid JSON only.",
                task_type="extraction",
                max_tokens=2000,
                json_mode=True,
            )

            # Handle various result types
            if isinstance(result, str):
                content = result
            elif hasattr(result, "content"):
                content = result.content
            elif isinstance(result, dict):
                content = result.get("content", "{}")
            else:
                content = "{}"

            queries_map = json.loads(content)

            # Merge AI-generated queries with specialized queries
            for gap in gaps:
                ai_queries = queries_map.get(gap.field_name, [])

                # Combine specialized + AI queries, removing duplicates
                all_queries = gap.generated_queries + ai_queries
                seen = set()
                unique_queries = []
                for q in all_queries:
                    q_lower = q.lower()
                    if q_lower not in seen:
                        seen.add(q_lower)
                        unique_queries.append(q)

                gap.generated_queries = unique_queries
                logger.debug(
                    f"[QUERY-GEN] {gap.field_name}: {len(gap.generated_queries)} total queries"
                )

            total_queries = sum(len(g.generated_queries) for g in gaps)
            logger.info(f"[QUERY-GEN] Generated {total_queries} total queries for {len(gaps)} gaps")

            return gaps

        except Exception as e:
            logger.error(f"[QUERY-GEN] Error: {e}")
            # Still return gaps with specialized queries if AI fails
            return gaps

    def execute_gap_searches(
        self, gaps: List[DataGap], max_results_per_query: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Execute searches for all generated queries.

        Args:
            gaps: Gaps with generated queries
            max_results_per_query: Max results per query

        Returns:
            Dict mapping field names to search results
        """
        logger.info(f"[SEARCH] Executing searches for {len(gaps)} gaps")

        all_results = {}

        for gap in gaps:
            if not gap.generated_queries:
                continue

            field_results = []

            for query in gap.generated_queries:
                try:
                    response = self.search_router.search(
                        query=query,
                        quality="premium",
                        provider=self.preferred_provider,  # Use preferred provider if set
                        max_results=max_results_per_query,
                        min_results=3,
                    )

                    if response.success and response.results:
                        for r in response.results:
                            result_dict = r.to_dict()
                            result_dict["query"] = query
                            result_dict["gap_field"] = gap.field_name
                            field_results.append(result_dict)

                        logger.debug(
                            f"[SEARCH] '{query[:40]}...' -> {len(response.results)} results via {response.provider}"
                        )

                except Exception as e:
                    logger.warning(f"[SEARCH] Query failed: {e}")

            # Deduplicate by URL
            seen_urls = set()
            unique_results = []
            for r in field_results:
                url = r.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(r)

            all_results[gap.field_name] = unique_results
            logger.info(f"[SEARCH] {gap.field_name}: {len(unique_results)} unique results")

        return all_results

    def extract_gap_data(
        self,
        gaps: List[DataGap],
        search_results: Dict[str, List[Dict[str, Any]]],
        company_name: str,
    ) -> List[DataGap]:
        """
        Use AI to extract specific data points from search results.

        Args:
            gaps: List of gaps to fill
            search_results: Search results by field name
            company_name: Company name for context

        Returns:
            Gaps with found_value and found_source populated
        """
        logger.info(f"[EXTRACT] Extracting data for {len(gaps)} gaps")

        for gap in gaps:
            results = search_results.get(gap.field_name, [])
            if not results:
                continue

            # Prepare context from search results
            context_parts = []
            for r in results[:10]:  # Limit context size
                context_parts.append(f"URL: {r.get('url', '')}")
                context_parts.append(f"Title: {r.get('title', '')}")
                content = r.get("content", r.get("snippet", ""))[:500]
                context_parts.append(f"Content: {content}")
                context_parts.append("---")

            context = "\n".join(context_parts)

            extract_prompt = f"""Extract the specific data point "{gap.field_name}" for {company_name}.

SEARCH RESULTS:
{context}

DATA POINT DETAILS:
- Field: {gap.field_name}
- Category: {gap.category}
- Expected format: {gap.expected_format}
- Context hint: {gap.context_hint}
- Current (possibly wrong) value: {gap.current_value}

EXTRACTION RULES:
1. ONLY extract if the data is explicitly stated in the sources
2. Include the source URL where you found the data
3. If multiple values found, prefer the most recent/authoritative
4. If data is not found or ambiguous, set value to null
5. Rate your confidence: high (exact match), medium (inferred), low (uncertain)

Return JSON:
{{
  "value": "the extracted value or null",
  "source_url": "URL where found or null",
  "confidence": "high/medium/low",
  "notes": "any relevant notes about the data"
}}"""

            try:
                result = self.llm.complete(
                    prompt=extract_prompt,
                    system="You are a precise data extractor. Only extract explicitly stated facts with sources.",
                    task_type="extraction",
                    max_tokens=500,
                    json_mode=True,
                )

                # Handle various result types
                if isinstance(result, str):
                    content = result
                elif hasattr(result, "content"):
                    content = result.content
                elif isinstance(result, dict):
                    content = result.get("content", "{}")
                else:
                    content = "{}"

                extracted = json.loads(content)

                if extracted.get("value"):
                    gap.found_value = extracted["value"]
                    gap.found_source = extracted.get("source_url")
                    confidence_map = {"high": 0.9, "medium": 0.7, "low": 0.4}
                    gap.confidence = confidence_map.get(extracted.get("confidence", "low"), 0.5)

                    logger.info(
                        f"[EXTRACT] {gap.field_name}: '{gap.found_value}' (confidence: {gap.confidence})"
                    )

            except Exception as e:
                logger.warning(f"[EXTRACT] Error extracting {gap.field_name}: {e}")

        return gaps

    def fill_gaps(
        self,
        company_name: str,
        research_data: Dict[str, Any],
        report_text: str = "",
        company_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Complete gap-filling workflow.

        Args:
            company_name: Name of the company
            research_data: Existing research data
            report_text: Full report text
            company_context: Additional context

        Returns:
            Dict with filled gaps and updated data
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"[GAP-FILLER] Starting intelligent gap filling for: {company_name}")
        logger.info(f"{'='*60}")

        # Default context
        if company_context is None:
            company_context = {"company_name": company_name, "year": datetime.now().year}

        # Phase 1: Analyze gaps
        logger.info("\n[PHASE 1] Analyzing research gaps...")
        gap_analysis = self.analyze_gaps(company_name, research_data, report_text)

        if not gap_analysis.gaps:
            logger.info("[GAP-FILLER] No gaps identified")
            return {"gaps_found": 0, "gaps_filled": 0}

        # Phase 2: Generate targeted queries
        logger.info(f"\n[PHASE 2] Generating queries for {len(gap_analysis.gaps)} gaps...")
        gaps_with_queries = self.generate_targeted_queries(
            company_name, gap_analysis.gaps, company_context
        )

        # Phase 3: Execute searches
        logger.info("\n[PHASE 3] Executing targeted searches...")
        search_results = self.execute_gap_searches(gaps_with_queries)

        # Phase 4: Extract data
        logger.info("\n[PHASE 4] Extracting data from results...")
        filled_gaps = self.extract_gap_data(gaps_with_queries, search_results, company_name)

        # Compile results
        filled_count = sum(1 for g in filled_gaps if g.found_value)
        high_confidence = sum(1 for g in filled_gaps if g.confidence >= 0.7)

        result = {
            "company_name": company_name,
            "gaps_found": len(filled_gaps),
            "gaps_filled": filled_count,
            "high_confidence_fills": high_confidence,
            "filled_data": {
                g.field_name: {
                    "value": g.found_value,
                    "source": g.found_source,
                    "confidence": g.confidence,
                    "category": g.category,
                    "priority": g.priority.value,
                }
                for g in filled_gaps
                if g.found_value
            },
            "unfilled_gaps": [
                {
                    "field": g.field_name,
                    "category": g.category,
                    "priority": g.priority.value,
                    "queries_tried": g.generated_queries,
                }
                for g in filled_gaps
                if not g.found_value
            ],
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"\n{'='*60}")
        logger.info(f"[GAP-FILLER] Complete: {filled_count}/{len(filled_gaps)} gaps filled")
        logger.info(f"[GAP-FILLER] High confidence: {high_confidence}")
        logger.info(f"{'='*60}\n")

        return result


def fill_research_gaps(
    company_name: str,
    research_data: Dict[str, Any],
    report_text: str = "",
    company_context: Optional[Dict[str, Any]] = None,
    preferred_provider: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to fill gaps in research data.

    Args:
        company_name: Name of the company
        research_data: Existing research data dict
        report_text: Full report text (optional)
        company_context: Additional context like country, industry, parent company
        preferred_provider: Force a specific search provider (e.g., "tavily")

    Returns:
        Dict with filled gap data
    """
    filler = IntelligentGapFiller(preferred_provider=preferred_provider)
    return filler.fill_gaps(company_name, research_data, report_text, company_context)
