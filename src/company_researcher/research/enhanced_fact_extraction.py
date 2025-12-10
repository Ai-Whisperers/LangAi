"""
Enhanced Fact Extraction Module.

Addresses Issue #4: Better Fact Extraction from Sources.

Extracts structured facts from unstructured source content with:
1. Pattern-based extraction for common metrics
2. Table parsing for financial data
3. Currency normalization
4. Time period detection
5. Source attribution tracking
6. Confidence scoring based on extraction quality
"""

import re
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
import json

logger = logging.getLogger(__name__)


class FactType(Enum):
    """Types of extractable facts."""
    REVENUE = "revenue"
    NET_INCOME = "net_income"
    MARKET_CAP = "market_cap"
    EMPLOYEES = "employees"
    PROFIT_MARGIN = "profit_margin"
    REVENUE_GROWTH = "revenue_growth"
    EPS = "eps"
    PE_RATIO = "pe_ratio"
    STOCK_PRICE = "stock_price"
    HEADQUARTERS = "headquarters"
    CEO = "ceo"
    FOUNDED_YEAR = "founded_year"
    MARKET_SHARE = "market_share"
    COMPETITOR = "competitor"
    PRODUCT = "product"
    EBITDA = "ebitda"
    DIVIDEND_YIELD = "dividend_yield"
    DEBT_TO_EQUITY = "debt_to_equity"
    FREE_CASH_FLOW = "free_cash_flow"
    CUSTOM = "custom"


class Currency(Enum):
    """Supported currencies."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    MXN = "MXN"
    BRL = "BRL"
    JPY = "JPY"
    CNY = "CNY"
    KRW = "KRW"
    INR = "INR"
    UNKNOWN = "UNKNOWN"


@dataclass
class ExtractedFact:
    """A fact extracted from source content."""
    fact_type: FactType
    value: Any
    raw_value: str  # Original string from source
    unit: Optional[str] = None
    currency: Optional[Currency] = None
    period: Optional[str] = None  # e.g., "FY2024", "Q4 2024"
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    confidence: float = 0.8  # 0-1
    context: str = ""  # Surrounding text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.fact_type.value,
            "value": self.value,
            "raw_value": self.raw_value,
            "unit": self.unit,
            "currency": self.currency.value if self.currency else None,
            "period": self.period,
            "source_url": self.source_url,
            "source_title": self.source_title,
            "confidence": round(self.confidence, 2),
        }

    @property
    def formatted_value(self) -> str:
        """Get a formatted display value."""
        if self.currency and isinstance(self.value, (int, float)):
            symbol = {"USD": "$", "EUR": "€", "GBP": "£", "MXN": "MX$", "BRL": "R$"}.get(
                self.currency.value, self.currency.value + " "
            )
            if self.value >= 1e12:
                return f"{symbol}{self.value/1e12:.2f}T"
            elif self.value >= 1e9:
                return f"{symbol}{self.value/1e9:.2f}B"
            elif self.value >= 1e6:
                return f"{symbol}{self.value/1e6:.2f}M"
            else:
                return f"{symbol}{self.value:,.2f}"
        elif self.unit == "percent":
            return f"{self.value}%"
        else:
            return str(self.value)


@dataclass
class ExtractionResult:
    """Result of fact extraction from a source."""
    source_url: str
    source_title: str
    facts: List[ExtractedFact]
    raw_text: str
    extraction_time: datetime = field(default_factory=datetime.now)

    @property
    def fact_count(self) -> int:
        return len(self.facts)

    @property
    def facts_by_type(self) -> Dict[FactType, List[ExtractedFact]]:
        result = {}
        for fact in self.facts:
            if fact.fact_type not in result:
                result[fact.fact_type] = []
            result[fact.fact_type].append(fact)
        return result


class EnhancedFactExtractor:
    """
    Extract structured facts from source content.

    Features:
    - Extracts financial metrics with currency normalization
    - Parses tables in markdown/HTML
    - Detects time periods
    - Tracks source attribution
    - Confidence scoring

    Usage:
        extractor = EnhancedFactExtractor()

        # Extract from a single source
        result = extractor.extract(
            text="Apple revenue was $383 billion in FY2024...",
            source_url="https://...",
            source_title="Apple Financials"
        )

        # Extract from multiple sources
        all_facts = extractor.extract_batch(sources)
    """

    # Currency patterns
    CURRENCY_PATTERNS = {
        Currency.USD: [r'\$', r'USD', r'US\s*dollars?'],
        Currency.EUR: [r'€', r'EUR', r'euros?'],
        Currency.GBP: [r'£', r'GBP', r'pounds?'],
        Currency.MXN: [r'MX\$', r'MXN', r'pesos?\s+mexicanos?'],
        Currency.BRL: [r'R\$', r'BRL', r'reais?', r'reales?'],
        Currency.JPY: [r'¥', r'JPY', r'yen'],
        Currency.CNY: [r'CNY', r'RMB', r'yuan'],
        Currency.KRW: [r'₩', r'KRW', r'won'],
        Currency.INR: [r'₹', r'INR', r'rupees?'],
    }

    # Multipliers
    MULTIPLIERS = {
        'trillion': 1e12, 't': 1e12,
        'billion': 1e9, 'b': 1e9, 'bn': 1e9,
        'million': 1e6, 'm': 1e6, 'mn': 1e6, 'mm': 1e6,
        'thousand': 1e3, 'k': 1e3,
    }

    # Extraction patterns for different fact types
    EXTRACTION_PATTERNS: Dict[FactType, List[Dict]] = {
        FactType.REVENUE: [
            {
                "pattern": r'(?:total\s+)?revenue\s+(?:of|was|is|:)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?',
                "value_group": 1,
                "multiplier_group": 2,
                "confidence": 0.9,
            },
            {
                "pattern": r'\$\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?\s+(?:in\s+)?(?:total\s+)?(?:revenue|sales)',
                "value_group": 1,
                "multiplier_group": 2,
                "confidence": 0.85,
            },
            {
                "pattern": r'(?:net\s+)?sales\s+(?:of|was|were|:)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?',
                "value_group": 1,
                "multiplier_group": 2,
                "confidence": 0.8,
            },
        ],
        FactType.NET_INCOME: [
            {
                "pattern": r'net\s+income\s+(?:of|was|is|:)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?',
                "value_group": 1,
                "multiplier_group": 2,
                "confidence": 0.9,
            },
            {
                "pattern": r'(?:net\s+)?(?:earnings|profit)\s+(?:of|was|is|:)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?',
                "value_group": 1,
                "multiplier_group": 2,
                "confidence": 0.85,
            },
        ],
        FactType.MARKET_CAP: [
            {
                "pattern": r'market\s+cap(?:italization)?\s+(?:of|is|was|:)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?',
                "value_group": 1,
                "multiplier_group": 2,
                "confidence": 0.9,
            },
            {
                "pattern": r'\$\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?\s+market\s+cap',
                "value_group": 1,
                "multiplier_group": 2,
                "confidence": 0.85,
            },
        ],
        FactType.EMPLOYEES: [
            {
                "pattern": r'([\d,]+)\s+employees',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.9,
            },
            {
                "pattern": r'employees?\s*:?\s*([\d,]+)',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.85,
            },
            {
                "pattern": r'(?:workforce|headcount|staff)\s+(?:of|:)?\s*([\d,]+)',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.8,
            },
        ],
        FactType.PROFIT_MARGIN: [
            {
                "pattern": r'(?:profit|net)\s+margin\s+(?:of|is|was|:)?\s*([\d,]+(?:\.\d+)?)\s*%',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.9,
                "unit": "percent",
            },
            {
                "pattern": r'([\d,]+(?:\.\d+)?)\s*%\s+(?:profit|net)\s+margin',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.85,
                "unit": "percent",
            },
        ],
        FactType.REVENUE_GROWTH: [
            {
                "pattern": r'(?:revenue|sales)\s+(?:grew|growth|increased)\s+(?:by\s+)?([\d,]+(?:\.\d+)?)\s*%',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.9,
                "unit": "percent",
            },
            {
                "pattern": r'([\d,]+(?:\.\d+)?)\s*%\s+(?:revenue|sales)\s+growth',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.85,
                "unit": "percent",
            },
        ],
        FactType.EPS: [
            {
                "pattern": r'(?:EPS|earnings\s+per\s+share)\s+(?:of|is|was|:)?\s*\$?\s*([\d,]+(?:\.\d+)?)',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.9,
            },
            {
                "pattern": r'\$\s*([\d]+(?:\.\d+)?)\s+(?:per\s+share|EPS)',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.85,
            },
        ],
        FactType.PE_RATIO: [
            {
                "pattern": r'(?:P/?E|price.to.earnings)\s+(?:ratio\s+)?(?:of|is|:)?\s*([\d,]+(?:\.\d+)?)',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.9,
            },
        ],
        FactType.STOCK_PRICE: [
            {
                "pattern": r'(?:stock|share)\s+price\s+(?:of|is|:)?\s*\$?\s*([\d,]+(?:\.\d+)?)',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.8,
            },
        ],
        FactType.HEADQUARTERS: [
            {
                "pattern": r'headquartered?\s+(?:in|at)\s+([A-Z][a-zA-Z\s,]+?)(?:\.|,|$|\n)',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.9,
                "is_text": True,
            },
            {
                "pattern": r'(?:based|located)\s+(?:in|at)\s+([A-Z][a-zA-Z\s,]+?)(?:\.|,|$|\n)',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.85,
                "is_text": True,
            },
        ],
        FactType.CEO: [
            {
                "pattern": r'(?:CEO|chief\s+executive(?:\s+officer)?)\s+(?:is|:)?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.9,
                "is_text": True,
            },
            {
                "pattern": r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:is|serves?\s+as)\s+(?:the\s+)?CEO',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.85,
                "is_text": True,
            },
        ],
        FactType.FOUNDED_YEAR: [
            {
                "pattern": r'founded\s+(?:in\s+)?(\d{4})',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.9,
            },
            {
                "pattern": r'(?:established|incorporated)\s+(?:in\s+)?(\d{4})',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.85,
            },
        ],
        FactType.MARKET_SHARE: [
            {
                "pattern": r'market\s+share\s+(?:of|is|:)?\s*([\d,]+(?:\.\d+)?)\s*%',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.85,
                "unit": "percent",
            },
        ],
        FactType.EBITDA: [
            {
                "pattern": r'EBITDA\s+(?:of|was|is|:)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?',
                "value_group": 1,
                "multiplier_group": 2,
                "confidence": 0.9,
            },
        ],
        FactType.DIVIDEND_YIELD: [
            {
                "pattern": r'dividend\s+yield\s+(?:of|is|:)?\s*([\d,]+(?:\.\d+)?)\s*%',
                "value_group": 1,
                "multiplier_group": None,
                "confidence": 0.9,
                "unit": "percent",
            },
        ],
    }

    # Period patterns
    PERIOD_PATTERNS = [
        (r'FY\s*(\d{4})', r'FY\1'),
        (r'fiscal\s+(?:year\s+)?(\d{4})', r'FY\1'),
        (r'Q([1-4])\s*(\d{4})', r'Q\1 \2'),
        (r'(?:full\s+year\s+)?(\d{4})', r'FY\1'),
        (r'(?:TTM|trailing\s+twelve\s+months)', 'TTM'),
    ]

    def __init__(self):
        # Compile patterns
        self._compiled_patterns = {}
        for fact_type, patterns in self.EXTRACTION_PATTERNS.items():
            self._compiled_patterns[fact_type] = [
                {**p, "compiled": re.compile(p["pattern"], re.IGNORECASE)}
                for p in patterns
            ]

    def extract(
        self,
        text: str,
        source_url: str = "",
        source_title: str = ""
    ) -> ExtractionResult:
        """
        Extract facts from text content.

        Args:
            text: The text to extract facts from
            source_url: URL of the source
            source_title: Title of the source

        Returns:
            ExtractionResult with extracted facts
        """
        facts = []

        # Detect currency context
        detected_currency = self._detect_currency(text)

        # Detect period context
        detected_period = self._detect_period(text)

        # Extract facts by type
        for fact_type, patterns in self._compiled_patterns.items():
            for pattern_def in patterns:
                matches = pattern_def["compiled"].finditer(text)

                for match in matches:
                    try:
                        fact = self._create_fact(
                            match,
                            pattern_def,
                            fact_type,
                            detected_currency,
                            detected_period,
                            source_url,
                            source_title,
                            text
                        )
                        if fact:
                            facts.append(fact)
                    except Exception as e:
                        logger.debug(f"Error extracting fact: {e}")

        # Parse tables if present
        table_facts = self._extract_from_tables(text, source_url, source_title)
        facts.extend(table_facts)

        # Deduplicate facts
        facts = self._deduplicate_facts(facts)

        return ExtractionResult(
            source_url=source_url,
            source_title=source_title,
            facts=facts,
            raw_text=text[:1000]  # Store first 1000 chars for reference
        )

    def extract_batch(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[ExtractionResult]:
        """
        Extract facts from multiple sources.

        Args:
            sources: List of dicts with 'content', 'url', 'title' keys

        Returns:
            List of ExtractionResult objects
        """
        results = []

        for source in sources:
            content = source.get("content") or source.get("snippet") or source.get("body", "")
            url = source.get("url", "")
            title = source.get("title", "")

            if content:
                result = self.extract(content, url, title)
                results.append(result)

        return results

    def _create_fact(
        self,
        match: re.Match,
        pattern_def: Dict,
        fact_type: FactType,
        detected_currency: Currency,
        detected_period: Optional[str],
        source_url: str,
        source_title: str,
        full_text: str
    ) -> Optional[ExtractedFact]:
        """Create a fact from a regex match."""
        value_group = pattern_def.get("value_group", 1)
        multiplier_group = pattern_def.get("multiplier_group")

        raw_value = match.group(value_group)

        # Parse numeric value
        if pattern_def.get("is_text"):
            value = raw_value.strip()
        else:
            value = self._parse_number(raw_value)
            if value is None:
                return None

            # Apply multiplier
            if multiplier_group:
                try:
                    mult_str = match.group(multiplier_group)
                    if mult_str:
                        mult = self.MULTIPLIERS.get(mult_str.lower().strip(), 1)
                        value *= mult
                except:
                    pass

        # Get context
        start = max(0, match.start() - 50)
        end = min(len(full_text), match.end() + 50)
        context = full_text[start:end]

        # Detect period from context if not found globally
        period = detected_period
        if not period:
            period = self._detect_period(context)

        return ExtractedFact(
            fact_type=fact_type,
            value=value,
            raw_value=match.group(0),
            unit=pattern_def.get("unit"),
            currency=detected_currency if not pattern_def.get("is_text") else None,
            period=period,
            source_url=source_url,
            source_title=source_title,
            confidence=pattern_def.get("confidence", 0.8),
            context=context
        )

    def _parse_number(self, text: str) -> Optional[float]:
        """Parse a number from text."""
        # Remove commas and whitespace
        cleaned = text.replace(",", "").strip()

        try:
            return float(cleaned)
        except ValueError:
            return None

    def _detect_currency(self, text: str) -> Currency:
        """Detect the primary currency in the text."""
        for currency, patterns in self.CURRENCY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return currency
        return Currency.USD  # Default to USD

    def _detect_period(self, text: str) -> Optional[str]:
        """Detect the time period mentioned in text."""
        for pattern, replacement in self.PERIOD_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return re.sub(pattern, replacement, match.group(0), flags=re.IGNORECASE)
        return None

    def _extract_from_tables(
        self,
        text: str,
        source_url: str,
        source_title: str
    ) -> List[ExtractedFact]:
        """Extract facts from markdown/HTML tables."""
        facts = []

        # Markdown table pattern
        table_pattern = r'\|[^\n]+\|(?:\n\|[^\n]+\|)+'

        tables = re.findall(table_pattern, text)

        for table in tables:
            rows = table.strip().split('\n')
            if len(rows) < 2:
                continue

            # Parse header
            header = [cell.strip() for cell in rows[0].split('|') if cell.strip()]

            # Parse data rows (skip separator row)
            for row in rows[2:]:
                cells = [cell.strip() for cell in row.split('|') if cell.strip()]
                if len(cells) != len(header):
                    continue

                # Try to map to known fact types
                for i, (h, c) in enumerate(zip(header, cells)):
                    fact_type = self._header_to_fact_type(h)
                    if fact_type:
                        # Try to extract value
                        value = self._parse_table_cell(c)
                        if value is not None:
                            facts.append(ExtractedFact(
                                fact_type=fact_type,
                                value=value,
                                raw_value=c,
                                source_url=source_url,
                                source_title=source_title,
                                confidence=0.85,
                                context=f"From table: {h}"
                            ))

        return facts

    def _header_to_fact_type(self, header: str) -> Optional[FactType]:
        """Map a table header to a fact type."""
        header_lower = header.lower()

        mappings = {
            "revenue": FactType.REVENUE,
            "sales": FactType.REVENUE,
            "net income": FactType.NET_INCOME,
            "profit": FactType.NET_INCOME,
            "earnings": FactType.NET_INCOME,
            "market cap": FactType.MARKET_CAP,
            "employees": FactType.EMPLOYEES,
            "eps": FactType.EPS,
            "p/e": FactType.PE_RATIO,
            "margin": FactType.PROFIT_MARGIN,
            "growth": FactType.REVENUE_GROWTH,
            "ebitda": FactType.EBITDA,
        }

        for keyword, fact_type in mappings.items():
            if keyword in header_lower:
                return fact_type

        return None

    def _parse_table_cell(self, cell: str) -> Optional[Any]:
        """Parse a value from a table cell."""
        # Remove currency symbols and common formatting
        cleaned = re.sub(r'[\$€£¥₹,]', '', cell).strip()

        # Try to parse as number
        try:
            # Check for multiplier
            mult_match = re.search(r'([\d.]+)\s*([TBMKtbmk])', cleaned)
            if mult_match:
                value = float(mult_match.group(1))
                mult = self.MULTIPLIERS.get(mult_match.group(2).lower(), 1)
                return value * mult

            # Check for percentage
            if '%' in cell:
                cleaned = cleaned.replace('%', '')
                return float(cleaned)

            return float(cleaned)
        except ValueError:
            return None

    def _deduplicate_facts(
        self,
        facts: List[ExtractedFact]
    ) -> List[ExtractedFact]:
        """Remove duplicate facts, keeping highest confidence."""
        # Group by type and approximate value
        grouped: Dict[Tuple, List[ExtractedFact]] = {}

        for fact in facts:
            # Create a key that groups similar facts
            if isinstance(fact.value, (int, float)):
                # Round to avoid floating point issues
                value_key = round(fact.value, -int(len(str(int(fact.value))) / 2))
            else:
                value_key = fact.value

            key = (fact.fact_type, value_key)

            if key not in grouped:
                grouped[key] = []
            grouped[key].append(fact)

        # Keep the highest confidence fact from each group
        result = []
        for facts_group in grouped.values():
            best = max(facts_group, key=lambda f: f.confidence)
            result.append(best)

        return result


# Convenience function
def extract_facts(
    text: str,
    source_url: str = "",
    source_title: str = ""
) -> List[ExtractedFact]:
    """
    Extract facts from text.

    Args:
        text: Text to extract from
        source_url: Source URL
        source_title: Source title

    Returns:
        List of extracted facts
    """
    extractor = EnhancedFactExtractor()
    result = extractor.extract(text, source_url, source_title)
    return result.facts


def extract_facts_from_sources(
    sources: List[Dict]
) -> Dict[str, List[ExtractedFact]]:
    """
    Extract facts from multiple sources, grouped by fact type.

    Args:
        sources: List of source dicts

    Returns:
        Dict mapping fact type to list of facts
    """
    extractor = EnhancedFactExtractor()
    results = extractor.extract_batch(sources)

    # Group all facts by type
    grouped: Dict[str, List[ExtractedFact]] = {}

    for result in results:
        for fact in result.facts:
            type_name = fact.fact_type.value
            if type_name not in grouped:
                grouped[type_name] = []
            grouped[type_name].append(fact)

    return grouped
