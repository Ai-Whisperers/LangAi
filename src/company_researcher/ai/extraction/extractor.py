"""AI-powered data extraction using LLM."""
from typing import List, Optional, Dict, Any
import logging
import re
import asyncio

from ..base import AIComponent
from ..fallback import FallbackHandler
from ..utils import truncate_text, normalize_confidence
from ...llm.response_parser import parse_json_response

from .models import (
    CompanyType,
    CompanyClassification,
    ExtractedFact,
    FinancialData,
    ContradictionAnalysis,
    ContradictionSeverity,
    ExtractionResult,
    FactCategory,
    FactType,
    CountryDetectionResult
)
from .prompts import (
    COMPANY_CLASSIFICATION_PROMPT,
    FACT_EXTRACTION_PROMPT,
    CONTRADICTION_RESOLUTION_PROMPT,
    COUNTRY_DETECTION_PROMPT
)

logger = logging.getLogger(__name__)


class AIDataExtractor(AIComponent[ExtractionResult]):
    """
    AI-driven data extraction replacing regex-based approach.

    Provides semantic extraction that understands context,
    handles multiple languages, and resolves contradictions.

    Example:
        extractor = get_data_extractor()

        # Classify company
        classification = await extractor.classify_company(
            company_name="Grupo Bimbo",
            context="Mexican multinational..."
        )

        # Extract all data
        result = await extractor.extract_all(
            company_name="Grupo Bimbo",
            search_results=[...]
        )
    """

    component_name = "data_extraction"
    default_task_type = "extraction"
    default_complexity = "medium"

    def __init__(self):
        super().__init__()
        self._fallback_handler = FallbackHandler("data_extraction")

    async def classify_company(
        self,
        company_name: str,
        context: str
    ) -> CompanyClassification:
        """
        Classify company using LLM.

        Args:
            company_name: Company name
            context: Available context/text about the company

        Returns:
            CompanyClassification with inferred details
        """
        prompt = COMPANY_CLASSIFICATION_PROMPT.format(
            company_name=company_name,
            context=truncate_text(context, 6000)
        )

        try:
            result = await self._async_call_llm(
                prompt=prompt,
                task_type="classification",
                complexity="medium"
            )

            parsed = parse_json_response(result, default={})
            return self._parse_classification(parsed, company_name)

        except Exception as e:
            logger.error(f"Company classification failed: {e}")
            return self._fallback_classification(company_name)

    async def extract_facts(
        self,
        text: str,
        company_name: str,
        source_url: Optional[str] = None
    ) -> List[ExtractedFact]:
        """
        Extract structured facts from text.

        Args:
            text: Text to extract from
            company_name: Target company
            source_url: Source URL for attribution

        Returns:
            List of ExtractedFact
        """
        if not text or len(text.strip()) < 50:
            return []

        prompt = FACT_EXTRACTION_PROMPT.format(
            company_name=company_name,
            text=truncate_text(text, 8000)
        )

        try:
            result = await self._async_call_llm(
                prompt=prompt,
                task_type="extraction",
                complexity="medium"
            )

            parsed = parse_json_response(result, default={"facts": []})
            facts = []
            for f_data in parsed.get("facts", []):
                fact = self._parse_fact(f_data, source_url)
                if fact:
                    facts.append(fact)
            return facts

        except Exception as e:
            logger.error(f"Fact extraction failed: {e}")
            return []

    async def resolve_contradiction(
        self,
        fact_type: str,
        values: List[Dict[str, Any]],
        company_name: str
    ) -> ContradictionAnalysis:
        """
        Analyze and resolve contradicting facts.

        Args:
            fact_type: Type of fact with contradiction
            values: List of value dicts with source info
            company_name: Target company

        Returns:
            ContradictionAnalysis with resolution
        """
        values_str = "\n".join([
            f"- Value: {v.get('value')}"
            f", Source: {v.get('source', 'Unknown')}"
            f", Period: {v.get('period', 'Unknown')}"
            f", Confidence: {v.get('confidence', 0.5)}"
            for v in values
        ])

        prompt = CONTRADICTION_RESOLUTION_PROMPT.format(
            company_name=company_name,
            fact_type=fact_type,
            values=values_str
        )

        try:
            result = await self._async_call_llm(
                prompt=prompt,
                task_type="reasoning",
                complexity="medium"
            )

            parsed = parse_json_response(result, default={})
            return self._parse_contradiction(parsed, fact_type, values)

        except Exception as e:
            logger.error(f"Contradiction resolution failed: {e}")
            return ContradictionAnalysis(
                fact_type=fact_type,
                values_found=values,
                is_contradiction=True,
                severity=ContradictionSeverity.MEDIUM,
                reasoning=f"Resolution failed: {str(e)}"
            )

    async def detect_country(
        self,
        company_name: str,
        clues: str
    ) -> CountryDetectionResult:
        """
        Detect company's country from clues.

        Args:
            company_name: Company name
            clues: Text with country indicators

        Returns:
            CountryDetectionResult with country, country_code, region, confidence
        """
        prompt = COUNTRY_DETECTION_PROMPT.format(
            company_name=company_name,
            clues=truncate_text(clues, 2000)
        )

        try:
            result = await self._async_call_llm(
                prompt=prompt,
                task_type="classification",
                complexity="low"
            )

            parsed = parse_json_response(result, default={
                "country": "Unknown",
                "country_code": "XX",
                "region": "Unknown",
                "confidence": 0.0
            })

            return CountryDetectionResult(
                country=parsed.get("country", "Unknown"),
                country_code=parsed.get("country_code", "XX"),
                region=parsed.get("region", "Unknown"),
                confidence=normalize_confidence(parsed.get("confidence", 0.0)),
                indicators_found=parsed.get("indicators_found", []),
                reasoning=parsed.get("reasoning", "")
            )

        except Exception as e:
            logger.error(f"Country detection failed: {e}")
            return CountryDetectionResult(
                country="Unknown",
                country_code="XX",
                region="Unknown",
                confidence=0.0,
                reasoning=f"Detection failed: {str(e)}"
            )

    async def extract_all(
        self,
        company_name: str,
        search_results: List[Dict[str, Any]]
    ) -> ExtractionResult:
        """
        Complete extraction pipeline.

        Args:
            company_name: Company to research
            search_results: List of search result dicts

        Returns:
            ExtractionResult with all extracted data
        """
        # Combine text for classification context
        all_text = "\n\n".join([
            f"Source: {r.get('url', 'Unknown')}\n"
            f"{r.get('content', r.get('snippet', ''))}"
            for r in search_results[:10]
        ])

        # Classify company
        classification = await self.classify_company(company_name, all_text)

        # Extract facts from each source
        all_facts = []
        for result in search_results:
            text = result.get('content') or result.get('snippet', '')
            url = result.get('url')
            if text:
                facts = await self.extract_facts(text, company_name, url)
                all_facts.extend(facts)

        # Find and resolve contradictions
        contradictions = await self._find_contradictions(all_facts, company_name)

        # Build financial data
        financial_data = self._build_financial_data(all_facts)

        # Calculate coverage
        coverage = self._calculate_coverage(all_facts)

        # Detect languages
        languages = self._detect_languages(search_results)

        return ExtractionResult(
            company_classification=classification,
            financial_data=financial_data,
            all_facts=all_facts,
            contradictions=contradictions,
            has_critical_contradictions=any(
                c.severity == ContradictionSeverity.CRITICAL
                for c in contradictions
            ),
            data_coverage=coverage,
            extraction_confidence=self._calculate_confidence(all_facts),
            sources_processed=len(search_results),
            facts_extracted=len(all_facts),
            languages_detected=languages
        )

    async def _async_call_llm(
        self,
        prompt: str,
        task_type: Optional[str] = None,
        complexity: Optional[str] = None
    ) -> str:
        """Async wrapper for LLM call."""
        # The base class _call_llm is synchronous, wrap it
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._call_llm(
                prompt=prompt,
                task_type=task_type or self.default_task_type,
                complexity=complexity or self.default_complexity
            )
        )

    def _parse_classification(
        self,
        data: Dict[str, Any],
        company_name: str
    ) -> CompanyClassification:
        """Parse LLM response into CompanyClassification."""
        company_type = data.get("company_type", "unknown")
        try:
            company_type = CompanyType(company_type)
        except ValueError:
            company_type = CompanyType.UNKNOWN

        return CompanyClassification(
            company_name=company_name,
            normalized_name=data.get("normalized_name", company_name),
            company_type=company_type,
            industry=data.get("industry", "Unknown"),
            sub_industry=data.get("sub_industry"),
            sector=data.get("sector"),
            region=data.get("region", "Unknown"),
            country=data.get("country", "Unknown"),
            country_code=data.get("country_code", "XX"),
            headquarters_city=data.get("headquarters_city"),
            stock_ticker=data.get("stock_ticker"),
            stock_exchange=data.get("stock_exchange"),
            is_listed=data.get("is_listed", False),
            parent_company=data.get("parent_company"),
            is_conglomerate=data.get("is_conglomerate", False),
            is_subsidiary=data.get("is_subsidiary", False),
            known_subsidiaries=data.get("known_subsidiaries", []),
            confidence=normalize_confidence(data.get("confidence", 0.5)),
            reasoning=data.get("reasoning", "")
        )

    def _parse_fact(
        self,
        data: Dict[str, Any],
        source_url: Optional[str]
    ) -> Optional[ExtractedFact]:
        """Parse a single fact from LLM response."""
        try:
            category = data.get("category", "company_info")
            try:
                category = FactCategory(category)
            except ValueError:
                category = FactCategory.COMPANY_INFO

            fact_type = data.get("fact_type", "other")
            try:
                fact_type = FactType(fact_type)
            except ValueError:
                fact_type = FactType.OTHER

            return ExtractedFact(
                category=category,
                fact_type=fact_type,
                value=data.get("value"),
                value_normalized=self._to_number(data.get("value_normalized")),
                unit=data.get("unit"),
                currency=data.get("currency"),
                time_period=data.get("time_period"),
                as_of_date=data.get("as_of_date"),
                is_estimate=data.get("is_estimate", False),
                source_text=data.get("source_text", "")[:500],
                source_url=source_url,
                confidence=normalize_confidence(data.get("confidence", 0.5))
            )
        except Exception as e:
            logger.warning(f"Failed to parse fact: {e}")
            return None

    def _parse_contradiction(
        self,
        data: Dict[str, Any],
        fact_type: str,
        values: List[Dict]
    ) -> ContradictionAnalysis:
        """Parse contradiction analysis from LLM response."""
        severity = data.get("severity", "medium")
        try:
            severity = ContradictionSeverity(severity)
        except ValueError:
            severity = ContradictionSeverity.MEDIUM

        return ContradictionAnalysis(
            fact_type=fact_type,
            values_found=values,
            is_contradiction=data.get("is_contradiction", True),
            severity=severity,
            difference_percentage=data.get("difference_percentage"),
            can_be_resolved=data.get("can_be_resolved", False),
            resolution_explanation=data.get("resolution_explanation"),
            most_likely_value=data.get("most_likely_value"),
            most_likely_source=data.get("most_likely_source"),
            reasoning=data.get("reasoning", "")
        )

    async def _find_contradictions(
        self,
        facts: List[ExtractedFact],
        company_name: str
    ) -> List[ContradictionAnalysis]:
        """Find and analyze contradictions in facts."""
        # Group facts by type
        by_type: Dict[str, List[ExtractedFact]] = {}
        for fact in facts:
            key = f"{fact.category}:{fact.fact_type}"
            if key not in by_type:
                by_type[key] = []
            by_type[key].append(fact)

        contradictions = []
        for fact_type, type_facts in by_type.items():
            if len(type_facts) > 1:
                # Check for significant value differences
                numeric_facts = [f for f in type_facts if f.value_normalized is not None]
                if len(numeric_facts) > 1:
                    values = [
                        {
                            "value": f.value,
                            "numeric": f.value_normalized,
                            "source": f.source_url or "Unknown",
                            "period": f.time_period,
                            "confidence": f.confidence
                        }
                        for f in numeric_facts
                    ]

                    # Quick check for significant difference
                    nums = [v["numeric"] for v in values if v["numeric"]]
                    if nums and max(nums) > 0:
                        diff_pct = (max(nums) - min(nums)) / max(nums) * 100
                        if diff_pct > 15:  # Potentially significant
                            analysis = await self.resolve_contradiction(
                                fact_type, values, company_name
                            )
                            if analysis.is_contradiction:
                                contradictions.append(analysis)

        return contradictions

    def _build_financial_data(self, facts: List[ExtractedFact]) -> FinancialData:
        """Build consolidated financial data from facts."""
        financial_facts = [
            f for f in facts
            if f.category == FactCategory.FINANCIAL or f.category == "financial"
        ]

        financial = FinancialData(raw_facts=financial_facts)

        # Map fact types to financial data fields
        type_map = {
            FactType.REVENUE: "revenue",
            FactType.PROFIT: "profit",
            FactType.NET_INCOME: "net_income",
            FactType.MARKET_CAP: "market_cap",
            FactType.FUNDING_TOTAL: "funding_total",
            FactType.VALUATION: "valuation",
            FactType.EBITDA: "ebitda",
            FactType.EMPLOYEE_COUNT: "employee_count",
            # String versions
            "revenue": "revenue",
            "profit": "profit",
            "net_income": "net_income",
            "market_cap": "market_cap",
            "funding_total": "funding_total",
            "valuation": "valuation",
            "ebitda": "ebitda",
            "employee_count": "employee_count",
        }

        for fact in facts:
            fact_type_key = fact.fact_type
            if fact_type_key in type_map:
                field = type_map[fact_type_key]
                current = getattr(financial, field, None)
                if current is None and fact.value_normalized:
                    if field == "employee_count":
                        setattr(financial, field, int(fact.value_normalized))
                    else:
                        setattr(financial, field, fact.value_normalized)

                    # Set currency for revenue
                    if field == "revenue" and fact.currency:
                        financial.revenue_currency = fact.currency
                    if field == "revenue" and fact.time_period:
                        financial.revenue_period = fact.time_period

        return financial

    def _calculate_coverage(self, facts: List[ExtractedFact]) -> Dict[str, float]:
        """Calculate data coverage by category."""
        coverage = {}
        for category in FactCategory:
            cat_value = category.value
            cat_facts = [f for f in facts if f.category == cat_value]
            # Heuristic: more facts = higher coverage, capped at 1.0
            coverage[cat_value] = min(1.0, len(cat_facts) / 5.0)
        return coverage

    def _calculate_confidence(self, facts: List[ExtractedFact]) -> float:
        """Calculate overall extraction confidence."""
        if not facts:
            return 0.0
        return sum(f.confidence for f in facts) / len(facts)

    def _detect_languages(self, results: List[Dict]) -> List[str]:
        """Detect languages from search results."""
        languages = set()

        # Simple heuristics
        for r in results:
            text = r.get('content', '') + r.get('snippet', '')
            url = r.get('url', '')

            # URL-based detection
            if '.br' in url or 'brasil' in url.lower():
                languages.add('pt')
            elif '.mx' in url or 'mexico' in url.lower():
                languages.add('es')
            elif '.es' in url:
                languages.add('es')
            elif '.ar' in url or 'argentina' in url.lower():
                languages.add('es')
            elif '.cl' in url or 'chile' in url.lower():
                languages.add('es')
            elif '.co' in url or 'colombia' in url.lower():
                languages.add('es')

            # Content-based (simple)
            text_lower = text.lower()
            if any(w in text_lower for w in ['empresa', 'negocio', 'mercado', 'ano']):
                # Could be Spanish or Portuguese
                if any(w in text_lower for w in ['nao', 'sao', 'nao', 'tambem']):
                    languages.add('pt')
                else:
                    languages.add('es')

        languages.add('en')  # Always include English
        return list(languages)

    def _to_number(self, value: Any) -> Optional[float]:
        """Convert value to number."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Remove currency and formatting
            cleaned = re.sub(r'[$\u20ac\xa3R\$,\s]', '', value)
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    def _fallback_classification(self, company_name: str) -> CompanyClassification:
        """Fallback classification when AI fails."""
        return CompanyClassification(
            company_name=company_name,
            normalized_name=company_name,
            company_type=CompanyType.UNKNOWN,
            industry="Unknown",
            region="Unknown",
            country="Unknown",
            country_code="XX",
            confidence=0.0,
            reasoning="AI classification failed, using fallback"
        )

    async def process(
        self,
        company_name: str,
        search_results: List[Dict]
    ) -> ExtractionResult:
        """Main processing method (implements AIComponent interface)."""
        return await self.extract_all(company_name, search_results)


# Singleton instance
_extractor_instance: Optional[AIDataExtractor] = None


def get_data_extractor() -> AIDataExtractor:
    """Get singleton data extractor instance."""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = AIDataExtractor()
    return _extractor_instance


def reset_data_extractor() -> None:
    """Reset the singleton instance (useful for testing)."""
    global _extractor_instance
    _extractor_instance = None
