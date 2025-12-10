"""Tests for AI data extractor."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from company_researcher.ai.extraction import (
    AIDataExtractor,
    get_data_extractor,
    reset_data_extractor,
    CompanyType,
    CompanyClassification,
    FactCategory,
    FactType,
    ContradictionSeverity,
    ExtractedFact,
    FinancialData,
    ExtractionResult,
    CountryDetectionResult,
)


class TestExtractionModels:
    """Test extraction models."""

    def test_company_type_enum(self):
        """Test company type enum values."""
        assert CompanyType.PUBLIC.value == "public"
        assert CompanyType.STARTUP.value == "startup"
        assert CompanyType.CONGLOMERATE.value == "conglomerate"
        assert CompanyType.PRIVATE.value == "private"
        assert CompanyType.SUBSIDIARY.value == "subsidiary"
        assert CompanyType.NONPROFIT.value == "nonprofit"
        assert CompanyType.GOVERNMENT.value == "government"
        assert CompanyType.UNKNOWN.value == "unknown"

    def test_fact_category_enum(self):
        """Test fact category enum."""
        assert FactCategory.FINANCIAL.value == "financial"
        assert FactCategory.COMPANY_INFO.value == "company_info"
        assert FactCategory.MARKET.value == "market"
        assert FactCategory.LEADERSHIP.value == "leadership"
        assert FactCategory.PRODUCT.value == "product"

    def test_fact_type_enum(self):
        """Test fact type enum."""
        assert FactType.REVENUE.value == "revenue"
        assert FactType.PROFIT.value == "profit"
        assert FactType.MARKET_CAP.value == "market_cap"
        assert FactType.EMPLOYEE_COUNT.value == "employee_count"
        assert FactType.CEO.value == "ceo"

    def test_contradiction_severity_enum(self):
        """Test contradiction severity enum."""
        assert ContradictionSeverity.CRITICAL.value == "critical"
        assert ContradictionSeverity.HIGH.value == "high"
        assert ContradictionSeverity.MEDIUM.value == "medium"
        assert ContradictionSeverity.LOW.value == "low"
        assert ContradictionSeverity.NONE.value == "none"

    def test_company_classification_model(self):
        """Test CompanyClassification model."""
        classification = CompanyClassification(
            company_name="Tesla Inc.",
            normalized_name="Tesla",
            company_type=CompanyType.PUBLIC,
            industry="Automotive",
            region="North America",
            country="United States",
            country_code="US",
            is_listed=True,
            stock_ticker="TSLA",
            stock_exchange="NASDAQ",
            confidence=0.95
        )

        assert classification.company_name == "Tesla Inc."
        assert classification.normalized_name == "Tesla"
        assert classification.company_type == CompanyType.PUBLIC
        assert classification.is_listed is True
        assert classification.stock_ticker == "TSLA"

    def test_extracted_fact_model(self):
        """Test ExtractedFact model."""
        fact = ExtractedFact(
            category=FactCategory.FINANCIAL,
            fact_type=FactType.REVENUE,
            value="$81.5 billion",
            value_normalized=81500000000,
            currency="USD",
            time_period="2023",
            source_text="Tesla revenue was $81.5 billion in 2023",
            confidence=0.9
        )

        assert fact.category == FactCategory.FINANCIAL
        assert fact.fact_type == FactType.REVENUE
        assert fact.value_normalized == 81500000000
        assert fact.currency == "USD"

    def test_financial_data_model(self):
        """Test FinancialData model."""
        financial = FinancialData(
            revenue=81500000000,
            revenue_currency="USD",
            revenue_period="FY2023",
            market_cap=500000000000,
            employee_count=140000
        )

        assert financial.revenue == 81500000000
        assert financial.get_best_size_indicator() == "$81,500,000,000 revenue"

    def test_financial_data_best_indicator_priority(self):
        """Test best size indicator priority."""
        # With only employee count
        financial = FinancialData(employee_count=1000)
        assert financial.get_best_size_indicator() == "1,000 employees"

        # With market cap
        financial = FinancialData(market_cap=1000000000, employee_count=1000)
        assert financial.get_best_size_indicator() == "$1,000,000,000 market cap"

        # With revenue (highest priority)
        financial = FinancialData(
            revenue=5000000000,
            market_cap=1000000000,
            employee_count=1000
        )
        assert financial.get_best_size_indicator() == "$5,000,000,000 revenue"

    def test_extraction_result_get_facts_methods(self):
        """Test ExtractionResult helper methods."""
        facts = [
            ExtractedFact(
                category=FactCategory.FINANCIAL,
                fact_type=FactType.REVENUE,
                value="$100M",
                source_text="Revenue",
                confidence=0.9
            ),
            ExtractedFact(
                category=FactCategory.FINANCIAL,
                fact_type=FactType.PROFIT,
                value="$10M",
                source_text="Profit",
                confidence=0.8
            ),
            ExtractedFact(
                category=FactCategory.COMPANY_INFO,
                fact_type=FactType.EMPLOYEE_COUNT,
                value="500",
                source_text="Employees",
                confidence=0.85
            ),
        ]

        classification = CompanyClassification(
            company_name="Test Co",
            normalized_name="Test Co",
            company_type=CompanyType.PRIVATE,
            industry="Technology",
            region="North America",
            country="United States",
            country_code="US",
            confidence=0.9
        )

        result = ExtractionResult(
            company_classification=classification,
            financial_data=FinancialData(),
            all_facts=facts,
            extraction_confidence=0.85
        )

        financial_facts = result.get_facts_by_category(FactCategory.FINANCIAL)
        assert len(financial_facts) == 2

        revenue_facts = result.get_facts_by_type(FactType.REVENUE)
        assert len(revenue_facts) == 1


class TestAIDataExtractor:
    """Test AI data extractor."""

    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        reset_data_extractor()
        return AIDataExtractor()

    @pytest.fixture
    def mock_classification_response(self):
        """Mock LLM response for classification."""
        return json.dumps({
            "company_name": "Grupo Bimbo",
            "normalized_name": "Grupo Bimbo",
            "company_type": "public",
            "industry": "Food & Beverage",
            "sub_industry": "Bakery Products",
            "region": "Latin America",
            "country": "Mexico",
            "country_code": "MX",
            "stock_ticker": "BIMBOA",
            "stock_exchange": "BMV",
            "is_listed": True,
            "is_conglomerate": True,
            "is_subsidiary": False,
            "confidence": 0.95,
            "reasoning": "Major Mexican public company on BMV"
        })

    @pytest.fixture
    def mock_facts_response(self):
        """Mock LLM response for fact extraction."""
        return json.dumps({
            "facts": [
                {
                    "category": "financial",
                    "fact_type": "revenue",
                    "value": "$20.1 billion",
                    "value_normalized": 20100000000,
                    "currency": "USD",
                    "time_period": "2023",
                    "source_text": "Revenue reached $20.1 billion in 2023",
                    "confidence": 0.9
                },
                {
                    "category": "company_info",
                    "fact_type": "employee_count",
                    "value": "136,000",
                    "value_normalized": 136000,
                    "source_text": "employs approximately 136,000 people",
                    "confidence": 0.85
                }
            ]
        })

    @pytest.mark.asyncio
    async def test_classify_company(self, extractor, mock_classification_response):
        """Test company classification."""
        with patch.object(extractor, '_async_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_classification_response

            result = await extractor.classify_company(
                company_name="Grupo Bimbo",
                context="Mexican multinational bakery company..."
            )

            assert result.company_type == CompanyType.PUBLIC
            assert result.country == "Mexico"
            assert result.country_code == "MX"
            assert result.stock_ticker == "BIMBOA"
            assert result.is_conglomerate is True

    @pytest.mark.asyncio
    async def test_extract_facts(self, extractor, mock_facts_response):
        """Test fact extraction."""
        with patch.object(extractor, '_async_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_facts_response

            # Text must be at least 50 characters for extraction to proceed
            facts = await extractor.extract_facts(
                text="Grupo Bimbo is a Mexican multinational bakery company. Its revenue reached $20.1 billion in 2023, making it one of the largest bakery companies in the world.",
                company_name="Grupo Bimbo"
            )

            assert len(facts) == 2
            revenue_fact = next(f for f in facts if f.fact_type == FactType.REVENUE)
            assert revenue_fact.value_normalized == 20100000000
            assert revenue_fact.currency == "USD"

    @pytest.mark.asyncio
    async def test_extract_facts_empty_text(self, extractor):
        """Test fact extraction with empty text."""
        facts = await extractor.extract_facts(
            text="",
            company_name="Test"
        )
        assert facts == []

    @pytest.mark.asyncio
    async def test_extract_facts_short_text(self, extractor):
        """Test fact extraction with very short text."""
        facts = await extractor.extract_facts(
            text="Hello",
            company_name="Test"
        )
        assert facts == []

    @pytest.mark.asyncio
    async def test_extract_all(self, extractor):
        """Test complete extraction pipeline."""
        mock_class = json.dumps({
            "company_name": "Tesla",
            "normalized_name": "Tesla",
            "company_type": "public",
            "industry": "Automotive",
            "region": "North America",
            "country": "United States",
            "country_code": "US",
            "stock_ticker": "TSLA",
            "is_listed": True,
            "confidence": 0.95
        })

        mock_facts = json.dumps({
            "facts": [
                {
                    "category": "financial",
                    "fact_type": "revenue",
                    "value": "$81.5B",
                    "value_normalized": 81500000000,
                    "currency": "USD",
                    "time_period": "2023",
                    "source_text": "Tesla revenue was $81.5B",
                    "confidence": 0.9
                }
            ]
        })

        with patch.object(extractor, '_async_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = [mock_class, mock_facts]

            # Content must be at least 50 characters for fact extraction to proceed
            result = await extractor.extract_all(
                company_name="Tesla",
                search_results=[
                    {"url": "https://example.com", "content": "Tesla Inc. reported record revenue of $81.5B for fiscal year 2023. The electric vehicle company continues to lead the EV market with strong growth."}
                ]
            )

            assert result.company_classification.company_type == CompanyType.PUBLIC
            assert result.financial_data.revenue == 81500000000
            assert len(result.all_facts) > 0

    @pytest.mark.asyncio
    async def test_contradiction_detection(self, extractor):
        """Test contradiction detection and resolution."""
        mock_response = json.dumps({
            "is_contradiction": True,
            "severity": "high",
            "difference_percentage": 35,
            "can_be_resolved": True,
            "resolution_explanation": "Different fiscal years",
            "most_likely_value": 81500000000,
            "reasoning": "One source uses 2023, other uses 2022 data"
        })

        with patch.object(extractor, '_async_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            values = [
                {"value": 81500000000, "source": "Reuters", "period": "2023"},
                {"value": 53800000000, "source": "Blog", "period": "2022"}
            ]

            result = await extractor.resolve_contradiction(
                fact_type="financial:revenue",
                values=values,
                company_name="Tesla"
            )

            assert result.is_contradiction is True
            assert result.severity == ContradictionSeverity.HIGH
            assert result.can_be_resolved is True

    @pytest.mark.asyncio
    async def test_detect_country(self, extractor):
        """Test country detection."""
        mock_response = json.dumps({
            "country": "Brazil",
            "country_code": "BR",
            "region": "Latin America",
            "confidence": 0.9,
            "indicators_found": [".com.br domain", "R$ currency"],
            "reasoning": "Brazilian domain and currency indicators"
        })

        with patch.object(extractor, '_async_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await extractor.detect_country(
                company_name="Petrobras",
                clues="Website: petrobras.com.br, Revenue: R$ 500 billion"
            )

            assert result.country == "Brazil"
            assert result.country_code == "BR"
            assert result.region == "Latin America"
            assert result.confidence == 0.9

    @pytest.mark.asyncio
    async def test_fallback_classification(self, extractor):
        """Test fallback classification when AI fails."""
        with patch.object(extractor, '_async_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = Exception("LLM Error")

            result = await extractor.classify_company(
                company_name="Unknown Company",
                context="Some context"
            )

            assert result.company_type == CompanyType.UNKNOWN
            assert result.confidence == 0.0
            assert "fallback" in result.reasoning.lower()


class TestDataExtractorHelpers:
    """Test helper methods."""

    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        reset_data_extractor()
        return AIDataExtractor()

    def test_to_number_with_float(self, extractor):
        """Test _to_number with float input."""
        assert extractor._to_number(123.45) == 123.45

    def test_to_number_with_int(self, extractor):
        """Test _to_number with int input."""
        assert extractor._to_number(100) == 100.0

    def test_to_number_with_string(self, extractor):
        """Test _to_number with string input."""
        assert extractor._to_number("1000") == 1000.0
        assert extractor._to_number("$1,000.50") == 1000.50

    def test_to_number_with_none(self, extractor):
        """Test _to_number with None input."""
        assert extractor._to_number(None) is None

    def test_to_number_with_invalid_string(self, extractor):
        """Test _to_number with invalid string."""
        assert extractor._to_number("not a number") is None

    def test_detect_languages_from_urls(self, extractor):
        """Test language detection from URLs."""
        results = [
            {"url": "https://example.com.br/article", "content": ""},
            {"url": "https://example.mx/noticias", "content": ""},
            {"url": "https://example.com/news", "content": ""}
        ]

        languages = extractor._detect_languages(results)

        assert "en" in languages
        assert "pt" in languages
        assert "es" in languages

    def test_calculate_confidence_empty(self, extractor):
        """Test confidence calculation with no facts."""
        assert extractor._calculate_confidence([]) == 0.0

    def test_calculate_confidence(self, extractor):
        """Test confidence calculation."""
        facts = [
            ExtractedFact(
                category=FactCategory.FINANCIAL,
                fact_type=FactType.REVENUE,
                value="$100M",
                source_text="Revenue",
                confidence=0.8
            ),
            ExtractedFact(
                category=FactCategory.FINANCIAL,
                fact_type=FactType.PROFIT,
                value="$10M",
                source_text="Profit",
                confidence=0.6
            ),
        ]

        confidence = extractor._calculate_confidence(facts)
        assert confidence == 0.7  # (0.8 + 0.6) / 2

    def test_calculate_coverage(self, extractor):
        """Test coverage calculation."""
        facts = [
            ExtractedFact(
                category=FactCategory.FINANCIAL,
                fact_type=FactType.REVENUE,
                value="$100M",
                source_text="Revenue",
                confidence=0.9
            ),
            ExtractedFact(
                category=FactCategory.FINANCIAL,
                fact_type=FactType.PROFIT,
                value="$10M",
                source_text="Profit",
                confidence=0.8
            ),
        ]

        coverage = extractor._calculate_coverage(facts)

        assert "financial" in coverage
        assert coverage["financial"] == 0.4  # 2/5 = 0.4
        assert coverage["company_info"] == 0.0

    def test_build_financial_data(self, extractor):
        """Test financial data building from facts."""
        facts = [
            ExtractedFact(
                category=FactCategory.FINANCIAL,
                fact_type=FactType.REVENUE,
                value="$81.5B",
                value_normalized=81500000000,
                currency="USD",
                time_period="2023",
                source_text="Revenue was $81.5B",
                confidence=0.9
            ),
            ExtractedFact(
                category=FactCategory.COMPANY_INFO,
                fact_type=FactType.EMPLOYEE_COUNT,
                value="140,000",
                value_normalized=140000,
                source_text="140,000 employees",
                confidence=0.85
            ),
        ]

        financial = extractor._build_financial_data(facts)

        assert financial.revenue == 81500000000
        assert financial.revenue_currency == "USD"
        assert financial.revenue_period == "2023"
        assert financial.employee_count == 140000


class TestDataExtractorSingleton:
    """Test singleton behavior."""

    def test_get_data_extractor_returns_same_instance(self):
        """Test singleton."""
        reset_data_extractor()
        ext1 = get_data_extractor()
        ext2 = get_data_extractor()
        assert ext1 is ext2

    def test_reset_data_extractor(self):
        """Test singleton reset."""
        ext1 = get_data_extractor()
        reset_data_extractor()
        ext2 = get_data_extractor()
        assert ext1 is not ext2


class TestDataExtractorParsingEdgeCases:
    """Test parsing edge cases."""

    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        reset_data_extractor()
        return AIDataExtractor()

    def test_parse_classification_with_invalid_company_type(self, extractor):
        """Test classification parsing with invalid company type."""
        data = {
            "company_name": "Test",
            "normalized_name": "Test",
            "company_type": "invalid_type",
            "industry": "Tech",
            "region": "NA",
            "country": "US",
            "country_code": "US"
        }

        result = extractor._parse_classification(data, "Test")
        assert result.company_type == CompanyType.UNKNOWN

    def test_parse_fact_with_invalid_category(self, extractor):
        """Test fact parsing with invalid category."""
        data = {
            "category": "invalid_category",
            "fact_type": "revenue",
            "value": "$100M",
            "source_text": "Revenue",
            "confidence": 0.8
        }

        result = extractor._parse_fact(data, None)
        assert result.category == FactCategory.COMPANY_INFO

    def test_parse_fact_with_invalid_fact_type(self, extractor):
        """Test fact parsing with invalid fact type."""
        data = {
            "category": "financial",
            "fact_type": "invalid_type",
            "value": "$100M",
            "source_text": "Some value",
            "confidence": 0.8
        }

        result = extractor._parse_fact(data, None)
        assert result.fact_type == FactType.OTHER

    def test_parse_contradiction_with_invalid_severity(self, extractor):
        """Test contradiction parsing with invalid severity."""
        data = {
            "is_contradiction": True,
            "severity": "invalid_severity",
            "reasoning": "Test"
        }

        result = extractor._parse_contradiction(data, "test_type", [])
        assert result.severity == ContradictionSeverity.MEDIUM
