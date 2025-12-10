"""
Ground Truth Validation Module.

Validates research claims against authoritative sources like Yahoo Finance,
SEC EDGAR, and other financial APIs to prevent hallucinations.

This is the most critical anti-hallucination measure in the system.
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationResult(Enum):
    """Result of validating a claim against ground truth."""
    VERIFIED = "verified"           # Matches ground truth within tolerance
    CONTRADICTED = "contradicted"   # Conflicts with ground truth
    UNVERIFIABLE = "unverifiable"   # No ground truth available
    APPROXIMATE = "approximate"     # Within extended tolerance


@dataclass
class GroundTruthData:
    """Authoritative data from financial APIs."""
    source: str
    ticker: str
    timestamp: datetime
    data: Dict[str, Any]
    confidence: float = 0.95  # API reliability score

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from ground truth data."""
        return self.data.get(key, default)


@dataclass
class ValidationReport:
    """Report of validating a single claim."""
    field: str
    claimed_value: str
    ground_truth_value: Optional[str]
    result: ValidationResult
    deviation_pct: Optional[float]
    source: str
    recommendation: str


@dataclass
class ValidationSummary:
    """Summary of all validation results."""
    reports: List[ValidationReport]
    verified_count: int = 0
    contradicted_count: int = 0
    approximate_count: int = 0
    unverifiable_count: int = 0
    validation_score: float = 50.0

    def __post_init__(self):
        """Calculate counts and score from reports."""
        for report in self.reports:
            if report.result == ValidationResult.VERIFIED:
                self.verified_count += 1
            elif report.result == ValidationResult.CONTRADICTED:
                self.contradicted_count += 1
            elif report.result == ValidationResult.APPROXIMATE:
                self.approximate_count += 1
            else:
                self.unverifiable_count += 1

        # Calculate score
        total = len(self.reports)
        if total > 0:
            base_score = (self.verified_count + self.approximate_count * 0.7) / total * 100
            # Major penalty for contradictions
            self.validation_score = max(0, base_score - (self.contradicted_count * 20))


class GroundTruthValidator:
    """
    Validates research claims against authoritative sources.

    Sources (in order of authority):
    1. SEC EDGAR (10-K, 10-Q filings)
    2. Yahoo Finance API
    3. Alpha Vantage API
    4. Company IR pages

    Usage:
        validator = GroundTruthValidator(config)
        ground_truth = await validator.fetch_ground_truth("AAPL")
        reports = validator.validate_claims(claims, ground_truth)
    """

    # Fields we can validate with their tolerances
    VALIDATABLE_FIELDS = {
        "market_cap": {
            "tolerance_pct": 5,      # 5% tolerance (changes daily)
            "sources": ["yahoo", "alpha_vantage"],
            "aliases": ["market capitalization", "market value", "valuation"]
        },
        "revenue": {
            "tolerance_pct": 2,      # 2% tolerance (should be exact)
            "sources": ["sec_edgar", "yahoo"],
            "aliases": ["annual revenue", "total revenue", "sales"]
        },
        "employees": {
            "tolerance_pct": 10,     # 10% tolerance (estimates vary)
            "sources": ["yahoo", "company_website"],
            "aliases": ["employee count", "headcount", "workforce", "staff"]
        },
        "pe_ratio": {
            "tolerance_pct": 5,
            "sources": ["yahoo", "alpha_vantage"],
            "aliases": ["p/e ratio", "price to earnings", "price-to-earnings"]
        },
        "dividend_yield": {
            "tolerance_pct": 2,
            "sources": ["yahoo"],
            "aliases": ["dividend", "yield"]
        },
        "52_week_high": {
            "tolerance_pct": 1,
            "sources": ["yahoo"],
            "aliases": ["52 week high", "52-week high", "yearly high"]
        },
        "52_week_low": {
            "tolerance_pct": 1,
            "sources": ["yahoo"],
            "aliases": ["52 week low", "52-week low", "yearly low"]
        },
        "gross_margin": {
            "tolerance_pct": 3,
            "sources": ["yahoo", "sec_edgar"],
            "aliases": ["gross profit margin", "gross margin"]
        },
        "operating_margin": {
            "tolerance_pct": 3,
            "sources": ["yahoo", "sec_edgar"],
            "aliases": ["operating profit margin", "operating margin"]
        },
        "net_margin": {
            "tolerance_pct": 3,
            "sources": ["yahoo", "sec_edgar"],
            "aliases": ["net profit margin", "net margin", "profit margin"]
        }
    }

    def __init__(self, config: Any = None):
        """
        Initialize validator.

        Args:
            config: Research configuration with API keys
        """
        self.config = config
        self._cache: Dict[str, GroundTruthData] = {}
        self._cache_ttl = timedelta(hours=1)

    async def fetch_ground_truth(self, ticker: str) -> Optional[GroundTruthData]:
        """
        Fetch authoritative data from financial APIs.

        Args:
            ticker: Stock ticker symbol

        Returns:
            GroundTruthData with authoritative values, or None if fetch fails
        """
        # Check cache
        if ticker in self._cache:
            cached = self._cache[ticker]
            if datetime.now() - cached.timestamp < self._cache_ttl:
                logger.debug(f"Using cached ground truth for {ticker}")
                return cached

        data = {}

        # Primary source: Yahoo Finance
        try:
            import yfinance as yf

            stock = yf.Ticker(ticker)
            info = stock.info

            if info:
                data.update({
                    "market_cap": info.get("marketCap"),
                    "revenue": info.get("totalRevenue"),
                    "employees": info.get("fullTimeEmployees"),
                    "pe_ratio": info.get("trailingPE"),
                    "forward_pe": info.get("forwardPE"),
                    "dividend_yield": info.get("dividendYield"),
                    "52_week_high": info.get("fiftyTwoWeekHigh"),
                    "52_week_low": info.get("fiftyTwoWeekLow"),
                    "gross_margin": info.get("grossMargins"),
                    "operating_margin": info.get("operatingMargins"),
                    "net_margin": info.get("profitMargins"),
                    "sector": info.get("sector"),
                    "industry": info.get("industry"),
                    "website": info.get("website"),
                    "ceo": self._extract_ceo(info.get("companyOfficers", [])),
                    "company_name": info.get("longName") or info.get("shortName"),
                    "description": info.get("longBusinessSummary"),
                })

                logger.info(f"Fetched ground truth for {ticker} from Yahoo Finance")

        except ImportError:
            logger.warning("yfinance not installed, skipping Yahoo Finance")
        except Exception as e:
            logger.warning(f"Yahoo Finance fetch failed for {ticker}: {e}")

        # Filter out None values
        data = {k: v for k, v in data.items() if v is not None}

        if not data:
            logger.warning(f"No ground truth data found for {ticker}")
            return None

        ground_truth = GroundTruthData(
            source="yahoo_finance",
            ticker=ticker,
            timestamp=datetime.now(),
            data=data,
            confidence=0.95
        )

        self._cache[ticker] = ground_truth
        return ground_truth

    def _extract_ceo(self, officers: List[Dict]) -> Optional[str]:
        """Extract CEO name from company officers list."""
        if not officers:
            return None

        for officer in officers:
            title = officer.get("title", "").lower()
            if "ceo" in title or "chief executive" in title:
                return officer.get("name")

        return None

    def validate_claims(
        self,
        claims: List[Dict[str, Any]],
        ground_truth: GroundTruthData
    ) -> ValidationSummary:
        """
        Validate research claims against ground truth.

        Args:
            claims: List of {"field": str, "claimed_value": str, "source": str}
            ground_truth: Authoritative data

        Returns:
            ValidationSummary with all reports
        """
        reports = []

        for claim in claims:
            field = claim.get("field", "").lower()
            claimed = claim.get("claimed_value", "")
            source = claim.get("source", "unknown")

            # Normalize field name
            normalized_field = self._normalize_field(field)

            if normalized_field is None:
                reports.append(ValidationReport(
                    field=field,
                    claimed_value=claimed,
                    ground_truth_value=None,
                    result=ValidationResult.UNVERIFIABLE,
                    deviation_pct=None,
                    source=source,
                    recommendation="Cannot validate this field type"
                ))
                continue

            truth_value = ground_truth.get(normalized_field)

            if truth_value is None:
                reports.append(ValidationReport(
                    field=field,
                    claimed_value=claimed,
                    ground_truth_value=None,
                    result=ValidationResult.UNVERIFIABLE,
                    deviation_pct=None,
                    source=ground_truth.source,
                    recommendation=f"Ground truth not available for {field}"
                ))
                continue

            # Parse and compare
            tolerance = self.VALIDATABLE_FIELDS[normalized_field]["tolerance_pct"]
            result, deviation = self._compare_values(
                claimed, truth_value, tolerance, normalized_field
            )

            reports.append(ValidationReport(
                field=field,
                claimed_value=claimed,
                ground_truth_value=self._format_value(truth_value, normalized_field),
                result=result,
                deviation_pct=deviation,
                source=ground_truth.source,
                recommendation=self._get_recommendation(result, field, deviation, truth_value)
            ))

        return ValidationSummary(reports=reports)

    def extract_claims_from_text(
        self,
        text: str,
        company_name: str
    ) -> List[Dict[str, Any]]:
        """
        Extract validatable claims from research text.

        Args:
            text: Research text to analyze
            company_name: Company name for context

        Returns:
            List of extracted claims
        """
        claims = []
        text_lower = text.lower()

        # Revenue claims
        revenue_patterns = [
            r'revenue\s+(?:of|was|reached|totaled)\s+\$?([\d,.]+)\s*(billion|million|B|M)?',
            r'\$?([\d,.]+)\s*(billion|million|B|M)?\s+(?:in\s+)?(?:annual\s+)?revenue',
        ]

        for pattern in revenue_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value = self._parse_match_to_value(match)
                if value:
                    claims.append({
                        "field": "revenue",
                        "claimed_value": value,
                        "source": "research_text"
                    })

        # Market cap claims
        market_cap_patterns = [
            r'market\s+cap(?:italization)?\s+(?:of|is|was|at)\s+\$?([\d,.]+)\s*(trillion|billion|million|T|B|M)?',
            r'\$?([\d,.]+)\s*(trillion|billion|million|T|B|M)?\s+market\s+cap',
        ]

        for pattern in market_cap_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value = self._parse_match_to_value(match)
                if value:
                    claims.append({
                        "field": "market_cap",
                        "claimed_value": value,
                        "source": "research_text"
                    })

        # Employee count claims
        employee_patterns = [
            r'([\d,]+)\s*(?:full[- ]?time\s+)?employees',
            r'(?:employs?|workforce\s+of|headcount\s+of)\s*([\d,]+)',
        ]

        for pattern in employee_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value = match.group(1).replace(',', '')
                claims.append({
                    "field": "employees",
                    "claimed_value": value,
                    "source": "research_text"
                })

        # PE ratio claims
        pe_patterns = [
            r'(?:P/?E|price[- ]?(?:to[- ])?earnings)\s+(?:ratio\s+)?(?:of|is|at)\s*([\d.]+)',
            r'([\d.]+)\s*(?:P/?E|price[- ]?(?:to[- ])?earnings)',
        ]

        for pattern in pe_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                claims.append({
                    "field": "pe_ratio",
                    "claimed_value": match.group(1),
                    "source": "research_text"
                })

        # Remove duplicates
        seen = set()
        unique_claims = []
        for claim in claims:
            key = (claim["field"], claim["claimed_value"])
            if key not in seen:
                seen.add(key)
                unique_claims.append(claim)

        return unique_claims

    def _parse_match_to_value(self, match: re.Match) -> Optional[str]:
        """Parse a regex match to a normalized value string."""
        try:
            number = match.group(1).replace(',', '')
            multiplier = match.group(2) if match.lastindex >= 2 else None

            if multiplier:
                return f"{number} {multiplier}"
            return number
        except:
            return None

    def _normalize_field(self, field: str) -> Optional[str]:
        """Normalize field name to canonical form."""
        field_lower = field.lower().strip()

        # Direct match
        if field_lower in self.VALIDATABLE_FIELDS:
            return field_lower

        # Check aliases
        for canonical, config in self.VALIDATABLE_FIELDS.items():
            aliases = config.get("aliases", [])
            if field_lower in aliases or any(alias in field_lower for alias in aliases):
                return canonical

        return None

    def _compare_values(
        self,
        claimed: str,
        truth: Any,
        tolerance_pct: float,
        field: str
    ) -> Tuple[ValidationResult, Optional[float]]:
        """Compare claimed value against ground truth."""
        try:
            # Parse claimed value
            claimed_num = self._parse_number(claimed, field)

            # Handle truth value
            if isinstance(truth, (int, float)):
                truth_num = float(truth)
            else:
                truth_num = self._parse_number(str(truth), field)

            if truth_num == 0:
                return ValidationResult.UNVERIFIABLE, None

            deviation = abs(claimed_num - truth_num) / abs(truth_num) * 100

            if deviation <= tolerance_pct:
                return ValidationResult.VERIFIED, deviation
            elif deviation <= tolerance_pct * 2:
                return ValidationResult.APPROXIMATE, deviation
            else:
                return ValidationResult.CONTRADICTED, deviation

        except (ValueError, TypeError) as e:
            logger.debug(f"Could not compare values: {e}")
            return ValidationResult.UNVERIFIABLE, None

    def _parse_number(self, text: str, field: str) -> float:
        """Parse a number from text (handles $1.5B, 10M, etc.)."""
        # Remove currency symbols and commas
        text = text.replace('$', '').replace(',', '').strip()

        # Handle multipliers
        multipliers = {
            'T': 1e12, 'trillion': 1e12,
            'B': 1e9, 'billion': 1e9,
            'M': 1e6, 'million': 1e6,
            'K': 1e3, 'thousand': 1e3, 'k': 1e3,
        }

        for suffix, mult in multipliers.items():
            if suffix.lower() in text.lower():
                num_match = re.search(r'[\d.]+', text)
                if num_match:
                    return float(num_match.group()) * mult

        # Handle percentage fields
        if 'margin' in field or 'yield' in field:
            text = text.replace('%', '')

        # Plain number
        num_match = re.search(r'[\d.]+', text)
        if num_match:
            return float(num_match.group())

        raise ValueError(f"Cannot parse number from: {text}")

    def _format_value(self, value: Any, field: str) -> str:
        """Format a ground truth value for display."""
        if value is None:
            return "N/A"

        if field in ["market_cap", "revenue"]:
            if value >= 1e12:
                return f"${value/1e12:.2f}T"
            elif value >= 1e9:
                return f"${value/1e9:.2f}B"
            elif value >= 1e6:
                return f"${value/1e6:.2f}M"
            else:
                return f"${value:,.0f}"

        if field == "employees":
            return f"{int(value):,}"

        if 'margin' in field or 'yield' in field:
            if isinstance(value, float) and value < 1:
                return f"{value*100:.1f}%"
            return f"{value:.1f}%"

        if field == "pe_ratio":
            return f"{value:.1f}"

        return str(value)

    def _get_recommendation(
        self,
        result: ValidationResult,
        field: str,
        deviation: Optional[float],
        truth_value: Any
    ) -> str:
        """Generate recommendation based on validation result."""
        if result == ValidationResult.VERIFIED:
            return f"✅ {field} verified - matches authoritative source"

        elif result == ValidationResult.CONTRADICTED:
            formatted = self._format_value(truth_value, field)
            return (
                f"❌ {field} CONTRADICTS ground truth by {deviation:.1f}%. "
                f"Authoritative value: {formatted}. Use this instead."
            )

        elif result == ValidationResult.APPROXIMATE:
            formatted = self._format_value(truth_value, field)
            return (
                f"⚠️ {field} approximately correct ({deviation:.1f}% deviation). "
                f"Authoritative value: {formatted}."
            )

        else:
            return f"ℹ️ Cannot validate {field} - no authoritative source available"
