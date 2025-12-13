"""
Tests for quality validation modules.

Tests the metrics validator, data threshold checker, quality enforcer,
and multilingual search generator.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from consolidated research/ version
from src.company_researcher.research.metrics_validator import (
    MetricsValidator,
    create_metrics_validator,
    CompanyType,
)
from src.company_researcher.agents.research.data_threshold import (
    DataThresholdChecker,
    create_threshold_checker,
)
from src.company_researcher.agents.research.quality_enforcer import (
    QualityEnforcer,
    create_quality_enforcer,
    ReportStatus,
)
from src.company_researcher.agents.research.multilingual_search import (
    MultilingualSearchGenerator,
    create_multilingual_generator,
    Language,
    Region,
)


class TestMetricsValidator:
    """Tests for MetricsValidator."""

    def test_create_validator(self):
        """Test validator creation."""
        validator = create_metrics_validator()
        assert validator is not None
        # Validator is created with custom min_score (60.0 by default from create_metrics_validator)
        assert validator._custom_min_score == pytest.approx(60.0)

    def test_detect_public_company(self):
        """Test detection of public company."""
        validator = MetricsValidator()
        content = "Apple Inc. (NASDAQ: AAPL) has a market cap of $3 trillion"
        company_type = validator.detect_company_type(content, "Apple")
        assert company_type == CompanyType.PUBLIC_COMPANY

    def test_detect_startup(self):
        """Test detection of startup."""
        validator = MetricsValidator()
        content = "The startup raised $50M in Series B funding from venture capital firms"
        company_type = validator.detect_company_type(content, "TechStartup")
        assert company_type == CompanyType.STARTUP

    def test_validate_good_metrics(self):
        """Test validation of content with good metrics."""
        validator = MetricsValidator()
        # The validate method takes a dict research_output, not a string
        # Include all critical metrics for a PUBLIC company
        research_output = {
            "company_overview": """
            Apple Inc. founded in 1976, headquartered in Cupertino, California.
            Revenue of $400 billion in 2024.
            Net income of $100 billion in 2024 with strong profit margins.
            Market cap of $3 trillion as of December 2024.
            164,000 employees worldwide in 2024.
            EPS of $6.50 per share for fiscal 2024.
            P/E ratio of 28x based on current market valuation.
            Products include iPhone, Mac, iPad.
            Competes with Samsung, Google.
            CEO Tim Cook leads the company.
            """
        }
        result = validator.validate(research_output, "Apple", CompanyType.PUBLIC)

        assert result.score >= 50
        assert result.is_valid
        assert "revenue" in result.metrics_found
        assert len(result.critical_missing) == 0

    def test_validate_poor_metrics(self):
        """Test validation of content with poor metrics."""
        validator = MetricsValidator()
        # The validate method takes a dict research_output, not a string
        research_output = {
            "company_overview": """
            Company overview not available.
            Revenue: Not available in research.
            Employees: N/A
            Products: Unknown
            """
        }
        result = validator.validate(research_output, "UnknownCo", CompanyType.PUBLIC)

        assert result.score < 30
        assert not result.is_valid
        assert result.retry_recommended
        assert len(result.recommended_queries) > 0


class TestDataThresholdChecker:
    """Tests for DataThresholdChecker."""

    def test_create_checker(self):
        """Test checker creation."""
        checker = create_threshold_checker()
        assert checker is not None

    def test_check_threshold_good_data(self):
        """Test threshold check with good data."""
        checker = DataThresholdChecker()
        results = [
            {"url": "https://example1.com/company", "content": "Revenue of $10 billion in 2024. Founded in 1990."},
            {"url": "https://example2.com/about", "content": "Company overview with 5000 employees."},
            {"url": "https://example3.com/financials", "content": "Market cap of $50 billion. Products include..."},
            {"url": "https://news.com/article", "content": "Company announces new strategic initiative."},
            {"url": "https://market.com/analysis", "content": "Competitors include Company A, Company B."},
        ]

        result = checker.check_threshold(results, "TestCompany", "public")

        assert result.passes_threshold
        assert result.source_count == 5
        assert result.has_financial_data
        assert result.has_company_info

    def test_check_threshold_insufficient_data(self):
        """Test threshold check with insufficient data."""
        checker = DataThresholdChecker()
        results = [
            {"url": "https://example.com", "content": "Brief mention of the company."},
        ]

        result = checker.check_threshold(results, "UnknownCo", "public")

        assert not result.passes_threshold
        assert len(result.issues) > 0
        assert len(result.retry_strategies) > 0


class TestQualityEnforcer:
    """Tests for QualityEnforcer."""

    def test_create_enforcer(self):
        """Test enforcer creation."""
        enforcer = create_quality_enforcer()
        assert enforcer is not None

    def test_approve_good_report(self):
        """Test approval of good quality report."""
        enforcer = QualityEnforcer()
        # Need a longer report with proper markdown format (## headers at start of line)
        report = """## Company Overview
Apple Inc. is a leading technology company founded in 1976 by Steve Jobs, Steve Wozniak, and Ronald Wayne.
They design, manufacture, and sell consumer electronics, computer software, and online services.
The company is headquartered in Cupertino, California and has become one of the most valuable companies in the world.
Apple's ecosystem of products and services has created a loyal customer base worldwide.
The company continues to innovate in areas like artificial intelligence, augmented reality, and health technology.

## Key Metrics
- Revenue: $400 billion (2024) - representing strong growth
- Employees: 164,000 full-time employees worldwide
- Market Cap: $3 trillion USD as of December 2024
- Founded: 1976 in Cupertino, California
- Headquarters: Apple Park, Cupertino, California
- Operating Income: $120 billion annually
- R&D Spending: $30 billion invested in research and development

## Products
- iPhone smartphones - flagship product generating over 50% of revenue
- Mac computers - laptops and desktops for professionals and consumers
- iPad tablets - leading tablet market share globally
- Apple Watch - best-selling smartwatch worldwide
- AirPods - dominant wireless earbuds market position
- Apple TV+ - streaming service with original content

## Competitors
- Samsung - primary smartphone competitor
- Google - Android operating system and Pixel phones
- Microsoft - Surface devices and Windows ecosystem
- Amazon - competing in services and smart home devices

## Key Insights
- Market leader in premium smartphones with over 50% profit share of the smartphone industry
- Strong services revenue growth reaching $24 billion per quarter
- Expanding into new markets including financial services with Apple Pay and Apple Card
- Significant investment in AR/VR technology with Vision Pro headset
"""

        result = enforcer.check_quality(report, "Apple")

        assert result.can_generate
        assert result.status in [ReportStatus.APPROVED, ReportStatus.WARNING]
        assert result.quality_score > 30

    def test_block_empty_report(self):
        """Test blocking of empty report."""
        enforcer = QualityEnforcer(block_on_empty_required=True)
        report = """
        ## Company Overview
        Not available in research.

        ## Key Metrics
        - Revenue: N/A
        - Employees: Not available
        - Founded: Unknown

        ## Products
        Data not found.

        ## Competitors
        No information available.
        """

        result = enforcer.check_quality(report, "UnknownCo")

        assert not result.can_generate
        assert result.status == ReportStatus.BLOCKED
        assert len(result.block_reasons) > 0


class TestMultilingualSearchGenerator:
    """Tests for MultilingualSearchGenerator."""

    def test_create_generator(self):
        """Test generator creation."""
        generator = create_multilingual_generator()
        assert generator is not None

    def test_detect_brazilian_company(self):
        """Test detection of Brazilian company."""
        generator = MultilingualSearchGenerator()
        region, language = generator.detect_region("Petrobras S.A.")

        assert region == Region.LATAM_BRAZIL
        assert language == Language.PORTUGUESE

    def test_detect_mexican_company(self):
        """Test detection of Mexican company."""
        generator = MultilingualSearchGenerator()
        # Use explicit Mexican indicator to avoid S.A. matching Brazil first
        region, language = generator.detect_region("Grupo Bimbo México S.A. de C.V.")

        assert region == Region.LATAM_SPANISH
        assert language == Language.SPANISH

    def test_generate_multilingual_queries(self):
        """Test generation of multilingual queries."""
        generator = MultilingualSearchGenerator()
        queries = generator.generate_queries(
            "Gerdau",
            region=Region.LATAM_BRAZIL,
            language=Language.PORTUGUESE,
            topics=["financial", "overview"],
            max_queries=10
        )

        assert len(queries) > 0
        assert any(q.language == Language.PORTUGUESE for q in queries)
        assert any(q.language == Language.ENGLISH for q in queries)

    def test_parent_company_lookup(self):
        """Test parent company lookup."""
        generator = MultilingualSearchGenerator()

        parent = generator.get_parent_company("Claro")
        assert parent == "América Móvil"

        parent = generator.get_parent_company("Telcel")
        assert parent == "América Móvil"

        parent = generator.get_parent_company("Unknown Corp")
        assert parent is None

    def test_parent_company_queries(self):
        """Test parent company query generation."""
        generator = MultilingualSearchGenerator()
        queries = generator.get_parent_company_queries("Claro Paraguay")

        assert len(queries) > 0
        assert any("América Móvil" in q for q in queries)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
