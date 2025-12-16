"""
End-to-End Integration Tests for Enhanced Research Workflow.

Tests the complete workflow including:
- Multilingual search query generation
- News sentiment analysis
- Competitive matrix generation
- Risk quantification
- Investment thesis generation
- Report generation
"""

from datetime import datetime
from unittest.mock import patch

import pytest

# Import analysis modules from consolidated package
from company_researcher.agents.research import (  # Multilingual search; Competitive matrix; Risk quantifier; Investment thesis; News sentiment (AI-powered)
    CompetitivePosition,
    InvestmentHorizon,
    InvestmentRecommendation,
    Language,
    MatrixDimension,
    NewsCategory,
    Region,
    RiskCategory,
    RiskLevel,
    SentimentLevel,
    create_competitive_matrix,
    create_multilingual_generator,
    create_risk_quantifier,
    create_sentiment_analyzer,
    create_thesis_generator,
)

# Import workflow components
from company_researcher.state import create_initial_state, create_output_state

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_company_name():
    """Sample company name for testing."""
    return "Petrobras S.A."


@pytest.fixture
def sample_latam_company():
    """Sample LATAM company for multilingual testing."""
    return "América Móvil"


@pytest.fixture
def sample_search_results():
    """Sample search results mimicking Tavily output."""
    return [
        {
            "title": "Petrobras Reports Strong Q3 Earnings Growth",
            "content": "Petrobras announced record revenue growth in Q3, beating analyst expectations with profit increase of 25%.",
            "url": "https://reuters.com/petrobras-q3",
            "source": "Reuters",
            "published_date": datetime.now().isoformat(),
        },
        {
            "title": "Petrobras Faces Regulatory Investigation",
            "content": "Brazilian authorities launched an investigation into Petrobras operations amid compliance concerns and potential fines.",
            "url": "https://bloomberg.com/petrobras-investigation",
            "source": "Bloomberg",
            "published_date": datetime.now().isoformat(),
        },
        {
            "title": "Petrobras Announces Strategic Partnership for Renewable Energy",
            "content": "Petrobras expands into renewable energy through strategic partnership, signaling expansion and growth.",
            "url": "https://oilgas.com/petrobras-partnership",
            "source": "Oil & Gas Journal",
            "published_date": datetime.now().isoformat(),
        },
        {
            "title": "Petrobras Stock Outlook: Market Analysis",
            "content": "Analysts maintain bullish outlook on Petrobras, citing strong market position and competitive advantage.",
            "url": "https://marketwatch.com/petrobras-outlook",
            "source": "MarketWatch",
            "published_date": datetime.now().isoformat(),
        },
        {
            "title": "Petrobras Faces Competition from Regional Rivals",
            "content": "Petrobras market share faces pressure from competitors as competition intensifies in the Brazilian market.",
            "url": "https://energy.com/petrobras-competition",
            "source": "Energy News",
            "published_date": datetime.now().isoformat(),
        },
    ]


@pytest.fixture
def sample_company_data():
    """Sample company data for analysis."""
    return {
        "name": "Petrobras S.A.",
        "overview": "Petrobras is a Brazilian multinational petroleum corporation.",
        "revenue": 120000000000,  # $120B
        "market_share": 35.0,
        "employees": 45000,
        "products_services": ["Oil & Gas", "Refining", "Petrochemicals"],
        "competitors": ["Shell", "Exxon", "Chevron", "BP", "Total"],
        "key_insights": [
            "Market leader in Brazilian oil sector",
            "Expanding renewable energy portfolio",
            "Facing regulatory challenges",
        ],
    }


@pytest.fixture
def sample_competitors_data():
    """Sample competitor data for competitive analysis."""
    return [
        {"name": "Shell", "revenue": 380000000000, "market_share": 8.0},
        {"name": "Exxon", "revenue": 400000000000, "market_share": 7.5},
        {"name": "Chevron", "revenue": 250000000000, "market_share": 5.0},
        {"name": "BP", "revenue": 280000000000, "market_share": 6.0},
        {"name": "Total", "revenue": 220000000000, "market_share": 5.5},
    ]


# ============================================================================
# Multilingual Search Integration Tests
# ============================================================================


class TestMultilingualSearchIntegration:
    """Integration tests for multilingual search."""

    def test_detect_brazilian_company(self, sample_company_name):
        """Test detection of Brazilian company."""
        generator = create_multilingual_generator()
        region, language = generator.detect_region(sample_company_name)

        assert region == Region.LATAM_BRAZIL
        assert language == Language.PORTUGUESE

    def test_detect_mexican_company(self, sample_latam_company):
        """Test detection of Mexican company."""
        generator = create_multilingual_generator()
        region, language = generator.detect_region(sample_latam_company)

        # América Móvil is a known LATAM company
        assert region in [Region.LATAM_SPANISH, Region.LATAM_BRAZIL, Region.NORTH_AMERICA]

    def test_generate_multilingual_queries(self, sample_company_name):
        """Test multilingual query generation."""
        generator = create_multilingual_generator()
        queries = generator.generate_queries(sample_company_name, max_queries=10)

        assert len(queries) > 0
        assert len(queries) <= 10

        # Check that queries contain company name
        for query in queries:
            assert (
                sample_company_name.lower() in query.query.lower()
                or "petrobras" in query.query.lower()
            )

    def test_parent_company_lookup(self):
        """Test parent company lookup for subsidiaries."""
        generator = create_multilingual_generator()

        # Test known subsidiary
        parent = generator.get_parent_company("claro")
        assert parent == "América Móvil"

        # Test another subsidiary
        parent = generator.get_parent_company("oxxo")
        assert parent == "FEMSA"

    def test_new_latam_countries_detection(self):
        """Test detection of newly added LATAM countries."""
        generator = create_multilingual_generator()

        # Test Ecuador
        region, lang = generator.detect_region("Banco Guayaquil Ecuador")
        assert region == Region.LATAM_SPANISH
        assert lang == Language.SPANISH

        # Test Panama
        region, lang = generator.detect_region("Copa Airlines Panama")
        assert region == Region.LATAM_SPANISH

        # Test Venezuela
        region, lang = generator.detect_region("PDVSA Venezuela")
        assert region == Region.LATAM_SPANISH


# ============================================================================
# News Sentiment Integration Tests
# ============================================================================


class TestNewsSentimentIntegration:
    """Integration tests for news sentiment analysis."""

    @pytest.fixture
    def mock_sentiment_response(self):
        """Mock LLM response for sentiment analysis."""
        import json

        return json.dumps(
            {
                "overall_sentiment": "positive",
                "overall_score": 0.6,
                "overall_confidence": 0.85,
                "target_company_sentiment": "positive",
                "target_company_confidence": 0.8,
                "entity_sentiments": [
                    {
                        "entity_name": "Petrobras",
                        "entity_type": "company",
                        "sentiment": "positive",
                        "confidence": 0.85,
                        "reasoning": "Strong earnings reported",
                        "context_snippet": "record revenue growth",
                        "is_target_company": True,
                    }
                ],
                "key_factors": ["Strong Q3 earnings", "Strategic partnerships", "Market expansion"],
                "detected_language": "en",
                "has_negations": False,
                "has_uncertainty": False,
                "has_sarcasm": False,
                "news_category": "financial",
                "secondary_categories": ["partnership"],
                "summary": "Positive news about company performance",
            }
        )

    def test_analyze_search_results(self, sample_company_name, sample_search_results):
        """Test sentiment analysis from search results."""
        analyzer = create_sentiment_analyzer()
        profile = analyzer.analyze_from_search_results(sample_company_name, sample_search_results)

        assert profile.company_name == sample_company_name
        assert profile.total_articles > 0
        assert -1.0 <= profile.sentiment_score <= 1.0
        assert isinstance(profile.sentiment_level, SentimentLevel)
        assert profile.sentiment_trend in ["improving", "stable", "declining"]

    def test_extract_topics(self, sample_search_results, mock_sentiment_response):
        """Test topic extraction from news."""
        analyzer = create_sentiment_analyzer()

        # Mock the _call_llm method with lambda to ensure synchronous return
        with patch.object(analyzer, "_call_llm", lambda *args, **kwargs: mock_sentiment_response):
            profile = analyzer.analyze_from_search_results("Petrobras", sample_search_results)

        # Should detect relevant topics
        assert len(profile.key_topics) > 0

    def test_positive_and_negative_highlights(
        self, sample_company_name, sample_search_results, mock_sentiment_response
    ):
        """Test extraction of positive and negative highlights."""
        analyzer = create_sentiment_analyzer()

        # Mock the _call_llm method with lambda to ensure synchronous return
        with patch.object(analyzer, "_call_llm", lambda *args, **kwargs: mock_sentiment_response):
            profile = analyzer.analyze_from_search_results(
                sample_company_name, sample_search_results
            )

        # Should have some highlights (positive or negative)
        total_highlights = len(profile.positive_highlights) + len(profile.negative_highlights)
        assert total_highlights > 0

    def test_category_breakdown(self, sample_company_name, sample_search_results):
        """Test category breakdown of news."""
        analyzer = create_sentiment_analyzer()
        profile = analyzer.analyze_from_search_results(sample_company_name, sample_search_results)

        # Should have category breakdown
        assert len(profile.category_breakdown) > 0


# ============================================================================
# Competitive Matrix Integration Tests
# ============================================================================


class TestCompetitiveMatrixIntegration:
    """Integration tests for competitive matrix generation."""

    def test_generate_competitive_matrix(self, sample_company_data, sample_competitors_data):
        """Test competitive matrix generation."""
        matrix = create_competitive_matrix(
            company_name=sample_company_data["name"],
            company_data=sample_company_data,
            competitors_data=sample_competitors_data,
        )

        assert matrix.company_name == sample_company_data["name"]
        assert len(matrix.competitors) == len(sample_competitors_data)
        assert len(matrix.dimensions) > 0

    def test_competitive_insights_generation(self, sample_company_data, sample_competitors_data):
        """Test generation of competitive insights."""
        matrix = create_competitive_matrix(
            company_name=sample_company_data["name"],
            company_data=sample_company_data,
            competitors_data=sample_competitors_data,
        )

        # Should generate insights
        assert len(matrix.insights) > 0

    def test_strategic_groups_identification(self, sample_company_data, sample_competitors_data):
        """Test identification of strategic groups."""
        matrix = create_competitive_matrix(
            company_name=sample_company_data["name"],
            company_data=sample_company_data,
            competitors_data=sample_competitors_data,
        )

        # Should identify strategic groups
        assert matrix.strategic_groups is not None


# ============================================================================
# Risk Quantifier Integration Tests
# ============================================================================


class TestRiskQuantifierIntegration:
    """Integration tests for risk quantification."""

    def test_assess_risks(self, sample_company_data):
        """Test risk assessment."""
        quantifier = create_risk_quantifier()
        risk_profile = quantifier.assess_risks(
            company_name=sample_company_data["name"], company_data=sample_company_data
        )

        assert risk_profile.company_name == sample_company_data["name"]
        assert 0 <= risk_profile.overall_risk_score <= 100
        assert risk_profile.risk_grade in ["A", "B", "C", "D", "F"]

    def test_risk_categories(self, sample_company_data):
        """Test risk categorization."""
        quantifier = create_risk_quantifier()

        # Provide content with risk indicators for analysis
        content = """
        The company faces intense competition in the market with declining market share.
        There are regulatory concerns and ongoing lawsuit investigations.
        The debt levels are high with restructuring needs.
        Leadership changes have led to executive departures.
        """

        risk_profile = quantifier.assess_risks(
            company_name=sample_company_data["name"],
            company_data=sample_company_data,
            content=content,
        )

        # Should have risks detected from content
        assert len(risk_profile.risks) > 0

        # Should have risk by category populated
        assert len(risk_profile.risk_by_category) > 0

        # Should have risk matrix populated
        assert len(risk_profile.risk_matrix) > 0

    def test_risk_tolerance_levels(self, sample_company_data):
        """Test different risk tolerance levels."""
        # Conservative
        conservative = create_risk_quantifier(risk_tolerance="conservative")
        profile_conservative = conservative.assess_risks(
            company_name=sample_company_data["name"], company_data=sample_company_data
        )

        # Aggressive
        aggressive = create_risk_quantifier(risk_tolerance="aggressive")
        profile_aggressive = aggressive.assess_risks(
            company_name=sample_company_data["name"], company_data=sample_company_data
        )

        # Both should produce valid results
        assert profile_conservative.risk_grade in ["A", "B", "C", "D", "F"]
        assert profile_aggressive.risk_grade in ["A", "B", "C", "D", "F"]


# ============================================================================
# Investment Thesis Integration Tests
# ============================================================================


class TestInvestmentThesisIntegration:
    """Integration tests for investment thesis generation."""

    def test_generate_thesis(self, sample_company_data):
        """Test thesis generation."""
        generator = create_thesis_generator()

        # First create risk profile
        quantifier = create_risk_quantifier()
        risk_profile = quantifier.assess_risks(
            company_name=sample_company_data["name"], company_data=sample_company_data
        )

        # Convert to dict format expected by thesis generator
        risk_dict = {
            "overall_risk_score": risk_profile.overall_risk_score,
            "risk_grade": risk_profile.risk_grade,
            "key_risks": risk_profile.key_risks,
        }

        thesis = generator.generate_thesis(
            company_name=sample_company_data["name"],
            company_data=sample_company_data,
            risk_assessment=risk_dict,
        )

        assert thesis.company_name == sample_company_data["name"]
        assert isinstance(thesis.recommendation, InvestmentRecommendation)
        assert 0 <= thesis.confidence <= 100

    def test_bull_and_bear_cases(self, sample_company_data):
        """Test bull and bear case generation."""
        generator = create_thesis_generator()
        thesis = generator.generate_thesis(
            company_name=sample_company_data["name"], company_data=sample_company_data
        )

        # Should have bull case
        assert thesis.bull_case is not None
        assert thesis.bull_case.headline

        # Should have bear case
        assert thesis.bear_case is not None
        assert thesis.bear_case.headline

    def test_suitable_investor_profiles(self, sample_company_data):
        """Test suitable investor profile identification."""
        generator = create_thesis_generator()
        thesis = generator.generate_thesis(
            company_name=sample_company_data["name"], company_data=sample_company_data
        )

        # Should identify suitable investor profiles
        assert len(thesis.suitable_for) > 0


# ============================================================================
# Full Pipeline Integration Tests
# ============================================================================


class TestFullPipelineIntegration:
    """Integration tests for the complete analysis pipeline."""

    def test_complete_analysis_pipeline(
        self,
        sample_company_name,
        sample_company_data,
        sample_competitors_data,
        sample_search_results,
    ):
        """Test complete analysis pipeline from search to thesis."""
        # Step 1: Multilingual query generation
        ml_generator = create_multilingual_generator()
        region, language = ml_generator.detect_region(sample_company_name)
        queries = ml_generator.generate_queries(sample_company_name, max_queries=5)

        assert len(queries) > 0

        # Step 2: News sentiment analysis
        sentiment_analyzer = create_sentiment_analyzer()
        sentiment_profile = sentiment_analyzer.analyze_from_search_results(
            sample_company_name, sample_search_results
        )

        assert sentiment_profile.total_articles > 0

        # Step 3: Competitive matrix
        matrix = create_competitive_matrix(
            company_name=sample_company_data["name"],
            company_data=sample_company_data,
            competitors_data=sample_competitors_data,
        )

        assert matrix.company_name is not None

        # Step 4: Risk quantification
        risk_quantifier_inst = create_risk_quantifier()
        risk_profile = risk_quantifier_inst.assess_risks(
            company_name=sample_company_data["name"], company_data=sample_company_data
        )

        assert risk_profile.overall_risk_score >= 0

        # Step 5: Investment thesis
        thesis_generator = create_thesis_generator()
        risk_dict = {
            "overall_risk_score": risk_profile.overall_risk_score,
            "risk_grade": risk_profile.risk_grade,
        }
        thesis = thesis_generator.generate_thesis(
            company_name=sample_company_data["name"],
            company_data=sample_company_data,
            risk_assessment=risk_dict,
        )

        assert thesis.recommendation is not None

        # Verify all components produced valid output
        print("\n=== Full Pipeline Results ===")
        print(f"Company: {sample_company_name}")
        print(f"Region: {region.value}, Language: {language.value}")
        print(f"Queries Generated: {len(queries)}")
        print(
            f"News Sentiment: {sentiment_profile.sentiment_level.value} ({sentiment_profile.sentiment_score:.2f})"
        )
        print(f"Competitors analyzed: {len(matrix.competitors)}")
        print(f"Risk Grade: {risk_profile.risk_grade} ({risk_profile.overall_risk_score:.1f}/100)")
        print(
            f"Investment Recommendation: {thesis.recommendation.value} ({thesis.confidence:.0f}% confidence)"
        )

    def test_state_initialization(self, sample_company_name):
        """Test workflow state initialization."""
        state = create_initial_state(sample_company_name)

        assert state["company_name"] == sample_company_name
        assert state["search_queries"] == []
        assert state["search_results"] == []
        assert state["competitive_matrix"] is None
        assert state["risk_profile"] is None
        assert state["investment_thesis"] is None
        assert state["news_sentiment"] is None

    def test_state_output_conversion(self, sample_company_name):
        """Test conversion from overall state to output state."""
        state = create_initial_state(sample_company_name)
        state["report_path"] = "/tmp/test_report.md"
        state["quality_score"] = 85.0
        state["iteration_count"] = 1

        output = create_output_state(state)

        assert output["company_name"] == sample_company_name
        assert output["report_path"] == "/tmp/test_report.md"
        assert output["success"] is True
        assert output["metrics"]["quality_score"] == 85.0


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestEdgeCasesAndErrors:
    """Test edge cases and error handling."""

    def test_empty_search_results(self):
        """Test handling of empty search results."""
        analyzer = create_sentiment_analyzer()
        profile = analyzer.analyze_from_search_results("TestCorp", [])

        assert profile.total_articles == 0
        assert profile.sentiment_score == 0.0
        assert profile.sentiment_level == SentimentLevel.NEUTRAL

    def test_minimal_company_data(self):
        """Test with minimal company data."""
        minimal_data = {"name": "MinimalCorp"}

        # Risk assessment should still work
        quantifier = create_risk_quantifier()
        risk_profile = quantifier.assess_risks(
            company_name="MinimalCorp", company_data=minimal_data
        )
        assert risk_profile.company_name == "MinimalCorp"

        # Thesis generation should still work
        generator = create_thesis_generator()
        thesis = generator.generate_thesis(company_name="MinimalCorp", company_data=minimal_data)
        assert thesis.company_name == "MinimalCorp"

    def test_unknown_company_region(self):
        """Test region detection for unknown company."""
        generator = create_multilingual_generator()
        region, language = generator.detect_region("Unknown Random Company XYZ")

        # Should default to North America / English
        assert region == Region.NORTH_AMERICA
        assert language == Language.ENGLISH

    def test_empty_competitors(self):
        """Test competitive matrix with no competitors."""
        company_data = {"name": "SoloCorp", "revenue": 1000000}

        matrix = create_competitive_matrix(
            company_name="SoloCorp",
            company_data=company_data,
            competitors_data=[],
        )

        assert matrix.company_name == "SoloCorp"
        assert len(matrix.competitors) == 0
