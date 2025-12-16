"""
Natural Language Query Processor (UX-001).

Allows users to ask questions in natural language:
- Company identification from queries
- Intent classification
- Query parameter extraction
- Response formatting

Examples:
- "What is Apple's revenue?"
- "Compare Tesla and Ford's market share"
- "Show me recent news about Microsoft"
- "Who are Amazon's main competitors?"
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..utils import get_logger

logger = get_logger(__name__)


class QueryIntent(str, Enum):
    """Types of query intents."""

    COMPANY_OVERVIEW = "company_overview"
    FINANCIAL_INFO = "financial_info"
    MARKET_ANALYSIS = "market_analysis"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    NEWS_SEARCH = "news_search"
    PRODUCT_INFO = "product_info"
    LEADERSHIP_INFO = "leadership_info"
    COMPARISON = "comparison"
    TREND_ANALYSIS = "trend_analysis"
    UNKNOWN = "unknown"


class EntityType(str, Enum):
    """Types of entities in queries."""

    COMPANY = "company"
    METRIC = "metric"
    TIME_PERIOD = "time_period"
    INDUSTRY = "industry"
    LOCATION = "location"


@dataclass
class Entity:
    """An entity extracted from a query."""

    text: str
    entity_type: EntityType
    normalized: Optional[str] = None
    confidence: float = 1.0


@dataclass
class ParsedQuery:
    """Result of parsing a natural language query."""

    original_query: str
    intent: QueryIntent
    companies: List[str]
    metrics: List[str]
    time_period: Optional[str] = None
    entities: List[Entity] = field(default_factory=list)
    confidence: float = 1.0
    is_comparison: bool = False
    follow_up_questions: List[str] = field(default_factory=list)


@dataclass
class QueryResponse:
    """Formatted response to a natural language query."""

    query: ParsedQuery
    answer: str
    data: Dict[str, Any]
    sources: List[str] = field(default_factory=list)
    confidence: float = 1.0
    suggestions: List[str] = field(default_factory=list)


class NaturalLanguageQueryProcessor:
    """
    Process natural language queries about companies.

    Usage:
        processor = NaturalLanguageQueryProcessor()

        # Parse query
        parsed = processor.parse("What is Apple's revenue?")
        print(parsed.intent)  # QueryIntent.FINANCIAL_INFO
        print(parsed.companies)  # ["Apple"]
        print(parsed.metrics)  # ["revenue"]

        # Format response
        response = processor.format_response(parsed, research_data)
    """

    # Company name patterns
    KNOWN_COMPANIES = {
        # Tech giants
        "apple": ["apple", "aapl", "apple inc", "apple computer"],
        "microsoft": ["microsoft", "msft", "microsoft corp", "microsoft corporation"],
        "google": ["google", "googl", "goog", "alphabet", "alphabet inc"],
        "amazon": ["amazon", "amzn", "amazon.com", "amazon inc"],
        "meta": ["meta", "facebook", "fb", "meta platforms"],
        "tesla": ["tesla", "tsla", "tesla motors", "tesla inc"],
        "nvidia": ["nvidia", "nvda", "nvidia corp"],
        # Traditional
        "walmart": ["walmart", "wmt", "wal-mart"],
        "jpmorgan": ["jpmorgan", "jpm", "jp morgan", "chase"],
        "johnson & johnson": ["johnson & johnson", "j&j", "jnj"],
    }

    # Financial metric keywords
    FINANCIAL_KEYWORDS = {
        "revenue": ["revenue", "sales", "income", "earnings", "turnover"],
        "profit": ["profit", "net income", "earnings", "bottom line"],
        "market_cap": ["market cap", "market capitalization", "valuation", "worth"],
        "stock_price": ["stock price", "share price", "stock", "shares"],
        "growth": ["growth", "growth rate", "increase", "yoy"],
        "debt": ["debt", "liabilities", "debt ratio"],
        "cash": ["cash", "cash flow", "liquidity"],
    }

    # Intent patterns
    INTENT_PATTERNS = {
        QueryIntent.FINANCIAL_INFO: [
            r"(revenue|profit|earnings|market cap|stock|financial|money|worth)",
            r"how much.*earn|make",
            r"financial (performance|data|metrics)",
        ],
        QueryIntent.COMPETITOR_ANALYSIS: [
            r"competitor|competition|compete|rival",
            r"who.*compete|competing",
            r"market share.*vs|versus",
        ],
        QueryIntent.COMPARISON: [
            r"compare|comparison|versus|vs\.?|between",
            r"which is (better|bigger|larger)",
            r"difference between",
        ],
        QueryIntent.NEWS_SEARCH: [
            r"news|recent|latest|update|announce",
            r"what('s| is) (new|happening)",
        ],
        QueryIntent.PRODUCT_INFO: [
            r"product|service|offering|sell|make",
            r"what do(es)?.*(make|sell|offer)",
        ],
        QueryIntent.MARKET_ANALYSIS: [
            r"market (share|position|size)",
            r"industry|sector",
            r"market analysis",
        ],
        QueryIntent.LEADERSHIP_INFO: [
            r"(ceo|cfo|cto|founder|leader|executive|management)",
            r"who (runs|leads|founded)",
        ],
        QueryIntent.COMPANY_OVERVIEW: [
            r"(what is|who is|tell me about|describe)",
            r"overview|summary|information",
        ],
    }

    # Time period patterns
    TIME_PATTERNS = {
        "current": [r"current|now|today|latest"],
        "this_year": [r"this year|ytd|year to date|\d{4}"],
        "last_year": [r"last year|previous year"],
        "quarterly": [r"q[1-4]|quarter|quarterly"],
        "historical": [r"historical|history|trend|over time"],
    }

    def __init__(self):
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for efficiency."""
        self._intent_patterns = {
            intent: [re.compile(p, re.IGNORECASE) for p in patterns]
            for intent, patterns in self.INTENT_PATTERNS.items()
        }
        self._time_patterns = {
            period: [re.compile(p, re.IGNORECASE) for p in patterns]
            for period, patterns in self.TIME_PATTERNS.items()
        }

    def parse(self, query: str) -> ParsedQuery:
        """
        Parse a natural language query.

        Args:
            query: Natural language query string

        Returns:
            ParsedQuery with extracted information
        """
        query_lower = query.lower()

        # Extract companies
        companies = self._extract_companies(query_lower)

        # Determine intent
        intent, intent_confidence = self._classify_intent(query_lower)

        # Check if it's a comparison
        is_comparison = len(companies) > 1 or bool(
            re.search(r"compare|versus|vs\.?|between", query_lower)
        )
        if is_comparison:
            intent = QueryIntent.COMPARISON

        # Extract metrics
        metrics = self._extract_metrics(query_lower)

        # Extract time period
        time_period = self._extract_time_period(query_lower)

        # Extract all entities
        entities = self._extract_entities(query, companies, metrics)

        # Generate follow-up questions
        follow_ups = self._generate_follow_ups(intent, companies, metrics)

        return ParsedQuery(
            original_query=query,
            intent=intent,
            companies=companies,
            metrics=metrics,
            time_period=time_period,
            entities=entities,
            confidence=intent_confidence,
            is_comparison=is_comparison,
            follow_up_questions=follow_ups,
        )

    def _extract_companies(self, query: str) -> List[str]:
        """Extract company names from query."""
        companies = []

        for canonical, aliases in self.KNOWN_COMPANIES.items():
            for alias in aliases:
                if alias in query:
                    companies.append(canonical.title())
                    break

        # Also look for capitalized words that might be company names
        words = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", query)
        for word in words:
            word_lower = word.lower()
            if word_lower not in [c.lower() for c in companies]:
                # Check if it looks like a company name
                if len(word) > 2 and word_lower not in ["the", "and", "for", "with"]:
                    companies.append(word)

        return list(set(companies))

    def _classify_intent(self, query: str) -> Tuple[QueryIntent, float]:
        """Classify the intent of a query."""
        max_matches = 0
        best_intent = QueryIntent.UNKNOWN
        total_patterns = 0

        for intent, patterns in self._intent_patterns.items():
            matches = sum(1 for p in patterns if p.search(query))
            total_patterns += len(patterns)

            if matches > max_matches:
                max_matches = matches
                best_intent = intent

        # Calculate confidence
        if max_matches == 0:
            confidence = 0.3  # Low confidence for unknown
        else:
            confidence = min(0.5 + (max_matches * 0.2), 0.95)

        return best_intent, confidence

    def _extract_metrics(self, query: str) -> List[str]:
        """Extract financial metrics mentioned in query."""
        metrics = []

        for metric, keywords in self.FINANCIAL_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query:
                    metrics.append(metric)
                    break

        return list(set(metrics))

    def _extract_time_period(self, query: str) -> Optional[str]:
        """Extract time period from query."""
        for period, patterns in self._time_patterns.items():
            for pattern in patterns:
                if pattern.search(query):
                    return period
        return None

    def _extract_entities(
        self, query: str, companies: List[str], metrics: List[str]
    ) -> List[Entity]:
        """Extract all entities from query."""
        entities = []

        for company in companies:
            entities.append(
                Entity(
                    text=company,
                    entity_type=EntityType.COMPANY,
                    normalized=company.lower(),
                )
            )

        for metric in metrics:
            entities.append(
                Entity(
                    text=metric,
                    entity_type=EntityType.METRIC,
                    normalized=metric,
                )
            )

        return entities

    def _generate_follow_ups(
        self, intent: QueryIntent, companies: List[str], metrics: List[str]
    ) -> List[str]:
        """Generate follow-up question suggestions."""
        follow_ups = []

        if companies:
            company = companies[0]
            if intent != QueryIntent.COMPETITOR_ANALYSIS:
                follow_ups.append(f"Who are {company}'s main competitors?")
            if intent != QueryIntent.FINANCIAL_INFO:
                follow_ups.append(f"What is {company}'s revenue?")
            if intent != QueryIntent.NEWS_SEARCH:
                follow_ups.append(f"What's the latest news about {company}?")

        if len(companies) == 1:
            follow_ups.append(f"Compare {companies[0]} with a competitor")

        return follow_ups[:3]

    def format_response(self, parsed: ParsedQuery, research_data: Dict[str, Any]) -> QueryResponse:
        """
        Format research data as a response to the query.

        Args:
            parsed: Parsed query
            research_data: Research data from company researcher

        Returns:
            Formatted QueryResponse
        """
        answer = self._generate_answer(parsed, research_data)
        sources = self._extract_sources(research_data)
        suggestions = parsed.follow_up_questions

        return QueryResponse(
            query=parsed,
            answer=answer,
            data=research_data,
            sources=sources,
            confidence=parsed.confidence,
            suggestions=suggestions,
        )

    def _generate_answer(self, parsed: ParsedQuery, data: Dict[str, Any]) -> str:
        """Generate natural language answer from data."""
        if not parsed.companies:
            return "I couldn't identify which company you're asking about. Please specify a company name."

        company = parsed.companies[0]
        agent_outputs = data.get("agent_outputs", {})

        if parsed.intent == QueryIntent.FINANCIAL_INFO:
            financial = agent_outputs.get("financial", {})
            if isinstance(financial, dict) and financial.get("analysis"):
                return (
                    f"Here's what I found about {company}'s financials:\n\n{financial['analysis']}"
                )
            return f"I found some financial information about {company}, but detailed metrics aren't available."

        elif parsed.intent == QueryIntent.COMPETITOR_ANALYSIS:
            market = agent_outputs.get("market", {})
            if isinstance(market, dict) and market.get("analysis"):
                return f"Here's the competitive landscape for {company}:\n\n{market['analysis']}"
            return f"I found information about {company}'s market position."

        elif parsed.intent == QueryIntent.COMPANY_OVERVIEW:
            analyst = agent_outputs.get("analyst", {})
            if isinstance(analyst, dict) and analyst.get("analysis"):
                return f"Here's an overview of {company}:\n\n{analyst['analysis']}"
            return f"Here's what I know about {company}."

        elif parsed.intent == QueryIntent.COMPARISON:
            return f"Comparing {' and '.join(parsed.companies)}. Please use the comparison report feature for detailed analysis."

        return f"Here's what I found about {company} based on your query."

    def _extract_sources(self, data: Dict[str, Any]) -> List[str]:
        """Extract source URLs from research data."""
        sources = data.get("sources", [])
        return [s.get("url", "") for s in sources if isinstance(s, dict)][:5]


def create_query_processor() -> NaturalLanguageQueryProcessor:
    """Create a new natural language query processor."""
    return NaturalLanguageQueryProcessor()


async def process_natural_query(
    query: str, research_data: Optional[Dict[str, Any]] = None
) -> QueryResponse:
    """
    Process a natural language query.

    Args:
        query: Natural language query
        research_data: Optional existing research data

    Returns:
        QueryResponse with answer
    """
    processor = NaturalLanguageQueryProcessor()
    parsed = processor.parse(query)

    if research_data:
        return processor.format_response(parsed, research_data)

    # Return parsed query with placeholder response
    return QueryResponse(
        query=parsed,
        answer=f"Query understood. Intent: {parsed.intent.value}. Companies: {', '.join(parsed.companies) or 'none identified'}",
        data={},
        suggestions=parsed.follow_up_questions,
    )
