"""
Unit tests for competitive_matrix.py module.

Tests cover:
- MatrixDimension and CompetitivePosition enums
- CompetitorProfile dataclass
- CompetitiveMatrixGenerator methods
- Matrix generation and scoring
- Strategic group identification
- Market map generation
- Insight and recommendation generation
"""

import pytest
from src.company_researcher.agents.research.competitive_matrix import (
    MatrixDimension,
    CompetitivePosition,
    CompetitorProfile,
    CompetitiveMatrix,
    CompetitiveMatrixGenerator,
    create_competitive_matrix,
)


class TestEnums:
    """Tests for enum classes."""

    def test_matrix_dimension_values(self):
        """Test MatrixDimension enum has expected values."""
        assert MatrixDimension.MARKET_SHARE.value == "market_share"
        assert MatrixDimension.REVENUE.value == "revenue"
        assert MatrixDimension.PRICING.value == "pricing"
        assert MatrixDimension.PRODUCT_RANGE.value == "product_range"
        assert MatrixDimension.GEOGRAPHIC_REACH.value == "geographic_reach"
        assert MatrixDimension.TECHNOLOGY.value == "technology"
        assert MatrixDimension.BRAND_STRENGTH.value == "brand_strength"
        assert MatrixDimension.CUSTOMER_SERVICE.value == "customer_service"
        assert MatrixDimension.INNOVATION.value == "innovation"
        assert MatrixDimension.FINANCIAL_STRENGTH.value == "financial_strength"

    def test_matrix_dimension_count(self):
        """Test MatrixDimension has 10 dimensions."""
        assert len(MatrixDimension) == 10

    def test_competitive_position_values(self):
        """Test CompetitivePosition enum values."""
        assert CompetitivePosition.LEADER.value == "leader"
        assert CompetitivePosition.CHALLENGER.value == "challenger"
        assert CompetitivePosition.FOLLOWER.value == "follower"
        assert CompetitivePosition.NICHE.value == "niche"


class TestCompetitorProfile:
    """Tests for CompetitorProfile dataclass."""

    def test_create_basic_profile(self):
        """Test creating a basic competitor profile."""
        profile = CompetitorProfile(name="Competitor A")

        assert profile.name == "Competitor A"
        assert profile.market_share is None
        assert profile.revenue is None
        assert profile.employees is None
        assert profile.strengths == []
        assert profile.weaknesses == []
        assert profile.products == []
        assert profile.position is None
        assert profile.threat_level == "moderate"
        assert profile.scores == {}

    def test_create_full_profile(self):
        """Test creating a fully specified competitor profile."""
        profile = CompetitorProfile(
            name="Big Corp",
            market_share=35.5,
            revenue=150.0,
            employees=5000,
            strengths=["Strong brand", "Large distribution network"],
            weaknesses=["Slow innovation"],
            products=["Product A", "Product B"],
            position=CompetitivePosition.LEADER,
            threat_level="high",
            scores={"market_share": 8.5, "technology": 7.0}
        )

        assert profile.name == "Big Corp"
        assert profile.market_share == 35.5
        assert profile.revenue == 150.0
        assert profile.employees == 5000
        assert len(profile.strengths) == 2
        assert len(profile.weaknesses) == 1
        assert len(profile.products) == 2
        assert profile.position == CompetitivePosition.LEADER
        assert profile.threat_level == "high"
        assert profile.scores["market_share"] == 8.5


class TestCompetitiveMatrixGenerator:
    """Tests for CompetitiveMatrixGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create a generator instance for tests."""
        return CompetitiveMatrixGenerator()

    @pytest.fixture
    def sample_company_data(self):
        """Sample company data for testing."""
        return {
            "market_share": 25.0,
            "revenue": 100.0,
            "employees": 3000,
            "product_range_score": 7,
            "pricing_score": 6,
            "technology_score": 8,
        }

    @pytest.fixture
    def sample_competitors_data(self):
        """Sample competitors data for testing."""
        return [
            {
                "name": "Leader Corp",
                "market_share": 35.0,
                "revenue": 200.0,
                "employees": 8000,
                "strengths": ["Market dominance", "Brand recognition"],
                "weaknesses": ["Legacy systems"],
                "threat_level": "high",
                "scores": {"technology": 7, "innovation": 6}
            },
            {
                "name": "Challenger Inc",
                "market_share": 20.0,
                "revenue": 80.0,
                "employees": 2000,
                "strengths": ["Innovation", "Agility"],
                "weaknesses": ["Limited reach"],
                "threat_level": "moderate",
                "scores": {"technology": 9, "innovation": 9}
            },
            {
                "name": "Niche Player",
                "market_share": 3.0,
                "revenue": 15.0,
                "employees": 200,
                "strengths": ["Specialized expertise"],
                "weaknesses": ["Small scale"],
                "threat_level": "low",
                "scores": {"technology": 5, "innovation": 4}
            }
        ]

    def test_init_default_weights(self, generator):
        """Test generator initializes with empty custom weights."""
        assert generator.custom_weights == {}

    def test_init_custom_weights(self):
        """Test generator with custom weights."""
        custom = {"market_share": 0.25}
        gen = CompetitiveMatrixGenerator(custom_weights=custom)
        assert gen.custom_weights == {"market_share": 0.25}

    def test_scoring_criteria_exists(self, generator):
        """Test that scoring criteria exists for all dimensions."""
        for dim in MatrixDimension:
            assert dim in generator.SCORING_CRITERIA
            criteria = generator.SCORING_CRITERIA[dim]
            assert "weight" in criteria
            assert "scale" in criteria
            assert "higher_is_better" in criteria

    def test_weights_sum_to_one(self, generator):
        """Test that default weights sum to 1.0."""
        total_weight = sum(
            generator.SCORING_CRITERIA[dim]["weight"]
            for dim in MatrixDimension
        )
        assert abs(total_weight - 1.0) < 0.01


class TestDeterminePosition:
    """Tests for position determination logic."""

    @pytest.fixture
    def generator(self):
        return CompetitiveMatrixGenerator()

    def test_leader_position_high_market_share(self, generator):
        """Test leader position for high market share."""
        profile = CompetitorProfile(name="Big Corp", market_share=35.0)
        position = generator._determine_position(profile)
        assert position == CompetitivePosition.LEADER

    def test_leader_position_threshold(self, generator):
        """Test leader position at 30% threshold."""
        profile = CompetitorProfile(name="Corp", market_share=30.0)
        position = generator._determine_position(profile)
        assert position == CompetitivePosition.LEADER

    def test_challenger_position(self, generator):
        """Test challenger position for 15-30% market share."""
        profile = CompetitorProfile(name="Corp", market_share=22.0)
        position = generator._determine_position(profile)
        assert position == CompetitivePosition.CHALLENGER

    def test_challenger_position_threshold(self, generator):
        """Test challenger position at 15% threshold."""
        profile = CompetitorProfile(name="Corp", market_share=15.0)
        position = generator._determine_position(profile)
        assert position == CompetitivePosition.CHALLENGER

    def test_follower_position(self, generator):
        """Test follower position for 5-15% market share."""
        profile = CompetitorProfile(name="Corp", market_share=10.0)
        position = generator._determine_position(profile)
        assert position == CompetitivePosition.FOLLOWER

    def test_follower_position_threshold(self, generator):
        """Test follower position at 5% threshold."""
        profile = CompetitorProfile(name="Corp", market_share=5.0)
        position = generator._determine_position(profile)
        assert position == CompetitivePosition.FOLLOWER

    def test_niche_position(self, generator):
        """Test niche position for <5% market share."""
        profile = CompetitorProfile(name="Corp", market_share=3.0)
        position = generator._determine_position(profile)
        assert position == CompetitivePosition.NICHE

    def test_default_follower_no_market_share(self, generator):
        """Test default to follower when no market share data."""
        profile = CompetitorProfile(name="Corp")
        position = generator._determine_position(profile)
        assert position == CompetitivePosition.FOLLOWER


class TestBuildCompetitorProfiles:
    """Tests for competitor profile building."""

    @pytest.fixture
    def generator(self):
        return CompetitiveMatrixGenerator()

    def test_build_profiles_basic(self, generator):
        """Test building profiles from basic data."""
        data = [{"name": "Comp A"}, {"name": "Comp B"}]
        profiles = generator._build_competitor_profiles(data)

        assert len(profiles) == 2
        assert profiles[0].name == "Comp A"
        assert profiles[1].name == "Comp B"

    def test_build_profiles_with_market_share(self, generator):
        """Test building profiles with market share data."""
        data = [
            {"name": "Leader", "market_share": 40.0},
            {"name": "Niche", "market_share": 2.0}
        ]
        profiles = generator._build_competitor_profiles(data)

        assert profiles[0].position == CompetitivePosition.LEADER
        assert profiles[1].position == CompetitivePosition.NICHE

    def test_build_profiles_preserves_all_data(self, generator):
        """Test that all data is preserved in profiles."""
        data = [{
            "name": "Full Corp",
            "market_share": 25.0,
            "revenue": 100.0,
            "employees": 1000,
            "strengths": ["Strong R&D"],
            "weaknesses": ["High costs"],
            "products": ["Widget Pro"],
            "threat_level": "high",
            "scores": {"technology": 9}
        }]
        profiles = generator._build_competitor_profiles(data)

        p = profiles[0]
        assert p.name == "Full Corp"
        assert p.market_share == 25.0
        assert p.revenue == 100.0
        assert p.employees == 1000
        assert "Strong R&D" in p.strengths
        assert "High costs" in p.weaknesses
        assert "Widget Pro" in p.products
        assert p.threat_level == "high"
        assert p.scores["technology"] == 9

    def test_build_profiles_unknown_name_fallback(self, generator):
        """Test fallback to 'Unknown' when no name provided."""
        data = [{"market_share": 10.0}]
        profiles = generator._build_competitor_profiles(data)
        assert profiles[0].name == "Unknown"


class TestScoring:
    """Tests for scoring methods."""

    @pytest.fixture
    def generator(self):
        return CompetitiveMatrixGenerator()

    def test_score_company_with_explicit_scores(self, generator):
        """Test scoring company with explicit dimension scores."""
        data = {
            "market_share_score": 8.0,
            "revenue_score": 7.0,
            "technology_score": 9.0
        }
        dimensions = [MatrixDimension.MARKET_SHARE, MatrixDimension.REVENUE, MatrixDimension.TECHNOLOGY]
        scores = generator._score_company(data, dimensions)

        assert scores["market_share"] == 8.0
        assert scores["revenue"] == 7.0
        assert scores["technology"] == 9.0

    def test_score_company_default_mid_range(self, generator):
        """Test default to mid-range (5.0) when no score available."""
        data = {}
        dimensions = [MatrixDimension.INNOVATION]
        scores = generator._score_company(data, dimensions)
        assert scores["innovation"] == 5.0

    def test_score_competitor_from_stored_scores(self, generator):
        """Test scoring competitor from stored scores."""
        profile = CompetitorProfile(
            name="Comp",
            scores={"technology": 8.0, "innovation": 7.0}
        )
        dimensions = [MatrixDimension.TECHNOLOGY, MatrixDimension.INNOVATION]
        scores = generator._score_competitor(profile, dimensions)

        assert scores["technology"] == 8.0
        assert scores["innovation"] == 7.0

    def test_score_competitor_from_market_share(self, generator):
        """Test scoring competitor using market share field."""
        profile = CompetitorProfile(name="Comp", market_share=25.0)
        dimensions = [MatrixDimension.MARKET_SHARE]
        scores = generator._score_competitor(profile, dimensions)
        assert scores["market_share"] == 25.0

    def test_score_competitor_from_revenue(self, generator):
        """Test scoring competitor using revenue field."""
        profile = CompetitorProfile(name="Comp", revenue=50.0)
        dimensions = [MatrixDimension.REVENUE]
        scores = generator._score_competitor(profile, dimensions)
        assert scores["revenue"] == 5.0  # 50/10 = 5, capped at 10

    def test_score_competitor_revenue_cap(self, generator):
        """Test revenue scoring caps at 10."""
        profile = CompetitorProfile(name="Comp", revenue=150.0)
        dimensions = [MatrixDimension.REVENUE]
        scores = generator._score_competitor(profile, dimensions)
        assert scores["revenue"] == 10.0  # Capped at 10

    def test_score_competitor_default_by_position(self, generator):
        """Test default scoring based on competitive position."""
        positions_expected = {
            CompetitivePosition.LEADER: 8.0,
            CompetitivePosition.CHALLENGER: 6.5,
            CompetitivePosition.FOLLOWER: 5.0,
            CompetitivePosition.NICHE: 4.0
        }

        for position, expected_score in positions_expected.items():
            profile = CompetitorProfile(name="Comp", position=position)
            dimensions = [MatrixDimension.BRAND_STRENGTH]
            scores = generator._score_competitor(profile, dimensions)
            assert scores["brand_strength"] == expected_score


class TestDeriveScore:
    """Tests for score derivation from raw data."""

    @pytest.fixture
    def generator(self):
        return CompetitiveMatrixGenerator()

    def test_derive_market_share(self, generator):
        """Test deriving market share score."""
        data = {"market_share": 25.0}
        score = generator._derive_score(data, MatrixDimension.MARKET_SHARE)
        assert score == 25.0

    def test_derive_revenue_log_scale(self, generator):
        """Test deriving revenue score with logarithmic scale."""
        data = {"revenue": 1000.0}  # log10(1000) * 2 = 6
        score = generator._derive_score(data, MatrixDimension.REVENUE)
        assert score == 6.0

    def test_derive_revenue_capped_at_10(self, generator):
        """Test revenue score caps at 10."""
        data = {"revenue": 1000000.0}
        score = generator._derive_score(data, MatrixDimension.REVENUE)
        assert score == 10.0

    def test_derive_returns_none_for_unknown(self, generator):
        """Test returns None for unknown dimensions."""
        data = {}
        score = generator._derive_score(data, MatrixDimension.BRAND_STRENGTH)
        assert score is None


class TestNormalizeScores:
    """Tests for score normalization."""

    @pytest.fixture
    def generator(self):
        return CompetitiveMatrixGenerator()

    def test_normalize_scores_range(self, generator):
        """Test normalization produces 0-100 range."""
        matrix = {
            "Company A": {"market_share": 10.0},
            "Company B": {"market_share": 50.0},
            "Company C": {"market_share": 30.0}
        }
        dimensions = [MatrixDimension.MARKET_SHARE]
        normalized = generator._normalize_scores(matrix, dimensions)

        # Min (10) should be 0, Max (50) should be 100
        assert normalized["Company A"]["market_share"] == 0.0
        assert normalized["Company B"]["market_share"] == 100.0
        assert normalized["Company C"]["market_share"] == 50.0  # (30-10)/(50-10) * 100 = 50

    def test_normalize_scores_single_value(self, generator):
        """Test normalization with single company."""
        matrix = {"Company A": {"market_share": 25.0}}
        dimensions = [MatrixDimension.MARKET_SHARE]
        normalized = generator._normalize_scores(matrix, dimensions)
        # With single value, it becomes 0 (min=max, range=1 by default)
        assert "market_share" in normalized["Company A"]


class TestStrategicGroups:
    """Tests for strategic group identification."""

    @pytest.fixture
    def generator(self):
        return CompetitiveMatrixGenerator()

    def test_identify_strategic_groups(self, generator):
        """Test strategic group identification."""
        company_data = {"market_share": 25, "product_range_score": 8}
        competitors = [
            CompetitorProfile(name="Leader", market_share=40, position=CompetitivePosition.LEADER),
            CompetitorProfile(name="Niche", market_share=3, position=CompetitivePosition.NICHE)
        ]

        groups = generator._identify_strategic_groups("MyCompany", company_data, competitors)

        assert "MyCompany" in groups.get("broad_market", [])
        assert "Leader" in groups.get("broad_market", [])
        assert "Niche" in groups.get("niche", [])

    def test_classify_strategic_group_broad_market(self, generator):
        """Test broad market classification."""
        data = {"market_share": 25, "product_range_score": 8}
        group = generator._classify_strategic_group(data)
        assert group == "broad_market"

    def test_classify_strategic_group_premium(self, generator):
        """Test premium classification."""
        data = {"market_share": 15, "product_range_score": 5}
        group = generator._classify_strategic_group(data)
        assert group == "premium"

    def test_classify_strategic_group_niche(self, generator):
        """Test niche classification."""
        data = {"market_share": 5, "product_range_score": 3}
        group = generator._classify_strategic_group(data)
        assert group == "niche"

    def test_classify_strategic_group_value(self, generator):
        """Test value classification."""
        data = {"market_share": 5, "product_range_score": 5}
        group = generator._classify_strategic_group(data)
        assert group == "value"


class TestMarketMap:
    """Tests for market position map generation."""

    @pytest.fixture
    def generator(self):
        return CompetitiveMatrixGenerator()

    def test_generate_market_map(self, generator):
        """Test market map generation."""
        company_data = {"pricing_score": 7, "product_range_score": 8}
        competitors = [
            CompetitorProfile(name="Comp", scores={"pricing": 5, "product_range": 6})
        ]

        market_map = generator._generate_market_map("MyCompany", company_data, competitors)

        assert "MyCompany" in market_map
        assert "Comp" in market_map
        assert market_map["MyCompany"] == (70, 80)
        assert market_map["Comp"] == (50, 60)

    def test_generate_market_map_default_scores(self, generator):
        """Test market map with default scores when missing."""
        company_data = {}
        competitors = [CompetitorProfile(name="Comp")]

        market_map = generator._generate_market_map("MyCompany", company_data, competitors)

        # Default score is 5, multiplied by 10 = 50
        assert market_map["MyCompany"] == (50, 50)
        assert market_map["Comp"] == (50, 50)


class TestInsightsAndRecommendations:
    """Tests for insight and recommendation generation."""

    @pytest.fixture
    def generator(self):
        return CompetitiveMatrixGenerator()

    def test_generate_insights_with_strengths(self, generator):
        """Test insight generation identifies strengths."""
        matrix = {
            "MyCompany": {"technology": 85, "innovation": 75, "pricing": 25}
        }
        competitors = []

        insights = generator._generate_insights("MyCompany", {}, competitors, matrix)

        # Should identify technology and innovation as strengths (>70)
        assert any("technology" in insight.lower() or "innovation" in insight.lower()
                   for insight in insights)

    def test_generate_insights_with_weaknesses(self, generator):
        """Test insight generation identifies weaknesses."""
        matrix = {
            "MyCompany": {"technology": 20, "brand_strength": 15}
        }
        competitors = []

        insights = generator._generate_insights("MyCompany", {}, competitors, matrix)

        # Should identify weaknesses (<30)
        assert any("improvement" in insight.lower() for insight in insights)

    def test_generate_insights_with_leaders(self, generator):
        """Test insight generation notes market leaders."""
        competitors = [
            CompetitorProfile(name="Big Leader", position=CompetitivePosition.LEADER)
        ]
        matrix = {"MyCompany": {}}

        insights = generator._generate_insights("MyCompany", {}, competitors, matrix)

        assert any("leader" in insight.lower() for insight in insights)

    def test_generate_recommendations_limit(self, generator):
        """Test recommendations are limited to 5."""
        competitors = [
            CompetitorProfile(name=f"Comp{i}", position=CompetitivePosition.NICHE)
            for i in range(10)
        ]
        matrix = {
            "MyCompany": {"tech": 30, "brand": 30},
            **{f"Comp{i}": {"tech": 80, "brand": 80} for i in range(10)}
        }

        recommendations = generator._generate_recommendations(
            "MyCompany", {}, competitors, matrix
        )

        assert len(recommendations) <= 5


class TestSummary:
    """Tests for summary generation."""

    @pytest.fixture
    def generator(self):
        return CompetitiveMatrixGenerator()

    def test_generate_summary_basic(self, generator):
        """Test basic summary generation."""
        competitors = [
            CompetitorProfile(name="Comp A", position=CompetitivePosition.LEADER),
            CompetitorProfile(name="Comp B", position=CompetitivePosition.CHALLENGER)
        ]
        insights = ["Key insight about the market"]

        summary = generator._generate_summary("MyCompany", competitors, insights)

        assert "MyCompany" in summary
        assert "2 competitors" in summary
        assert "1 established leader" in summary
        assert "1 active challenger" in summary

    def test_generate_summary_includes_insight(self, generator):
        """Test summary includes first insight."""
        competitors = []
        insights = ["Technology leadership is strong"]

        summary = generator._generate_summary("MyCompany", competitors, insights)

        assert "Technology leadership" in summary


class TestMarkdownFormatting:
    """Tests for markdown table formatting."""

    @pytest.fixture
    def generator(self):
        return CompetitiveMatrixGenerator()

    def test_format_as_markdown_table(self, generator):
        """Test markdown table formatting."""
        matrix = CompetitiveMatrix(
            company_name="MyCompany",
            competitors=[],
            dimensions=[MatrixDimension.MARKET_SHARE, MatrixDimension.TECHNOLOGY],
            matrix_data={
                "MyCompany": {"market_share": 75.0, "technology": 80.0},
                "Competitor": {"market_share": 60.0, "technology": 70.0}
            },
            strategic_groups={},
            market_map={},
            insights=[],
            recommendations=[],
            summary=""
        )

        table = generator.format_as_markdown_table(
            matrix,
            dimensions=["market_share", "technology"]
        )

        assert "| Company |" in table
        assert "| Market Share |" in table
        assert "| Technology |" in table
        assert "| MyCompany |" in table
        assert "| 75 |" in table
        assert "| 80 |" in table


class TestCreateCompetitiveMatrix:
    """Tests for the factory function."""

    def test_create_competitive_matrix_basic(self):
        """Test factory function creates valid matrix."""
        company_data = {"market_share": 25.0}
        competitors_data = [
            {"name": "Competitor A", "market_share": 30.0},
            {"name": "Competitor B", "market_share": 15.0}
        ]

        matrix = create_competitive_matrix(
            company_name="MyCompany",
            company_data=company_data,
            competitors_data=competitors_data
        )

        assert isinstance(matrix, CompetitiveMatrix)
        assert matrix.company_name == "MyCompany"
        assert len(matrix.competitors) == 2
        assert len(matrix.dimensions) == len(MatrixDimension)
        assert "MyCompany" in matrix.matrix_data
        assert matrix.summary != ""

    def test_create_competitive_matrix_custom_dimensions(self):
        """Test factory function with custom dimensions."""
        dimensions = [MatrixDimension.MARKET_SHARE, MatrixDimension.TECHNOLOGY]

        matrix = create_competitive_matrix(
            company_name="MyCompany",
            company_data={},
            competitors_data=[{"name": "Comp"}],
            dimensions=dimensions
        )

        assert matrix.dimensions == dimensions
        assert len(matrix.dimensions) == 2


class TestFullMatrixGeneration:
    """Integration tests for full matrix generation."""

    def test_full_matrix_generation(self):
        """Test complete matrix generation workflow."""
        company_data = {
            "market_share": 20.0,
            "revenue": 80.0,
            "product_range_score": 7,
            "pricing_score": 6,
            "technology_score": 8,
        }

        competitors_data = [
            {
                "name": "Market Leader",
                "market_share": 40.0,
                "revenue": 200.0,
                "threat_level": "high",
                "strengths": ["Brand recognition", "Scale"],
                "weaknesses": ["Slow innovation"]
            },
            {
                "name": "Fast Challenger",
                "market_share": 18.0,
                "revenue": 70.0,
                "threat_level": "moderate",
                "strengths": ["Innovation", "Agility"],
                "scores": {"technology": 9}
            },
            {
                "name": "Niche Specialist",
                "market_share": 4.0,
                "revenue": 15.0,
                "threat_level": "low",
                "strengths": ["Deep expertise"]
            }
        ]

        matrix = create_competitive_matrix(
            company_name="Our Company",
            company_data=company_data,
            competitors_data=competitors_data,
            dimensions=[
                MatrixDimension.MARKET_SHARE,
                MatrixDimension.REVENUE,
                MatrixDimension.TECHNOLOGY,
                MatrixDimension.BRAND_STRENGTH
            ]
        )

        # Verify structure
        assert matrix.company_name == "Our Company"
        assert len(matrix.competitors) == 3

        # Verify positions were determined
        positions = {c.name: c.position for c in matrix.competitors}
        assert positions["Market Leader"] == CompetitivePosition.LEADER
        assert positions["Fast Challenger"] == CompetitivePosition.CHALLENGER
        assert positions["Niche Specialist"] == CompetitivePosition.NICHE

        # Verify matrix data
        assert "Our Company" in matrix.matrix_data
        assert "Market Leader" in matrix.matrix_data

        # Verify scores are normalized (0-100)
        for company_scores in matrix.matrix_data.values():
            for score in company_scores.values():
                assert 0 <= score <= 100

        # Verify strategic groups exist
        assert len(matrix.strategic_groups) > 0

        # Verify market map has all companies
        assert len(matrix.market_map) == 4

        # Verify insights and recommendations generated
        assert len(matrix.insights) > 0
        assert matrix.summary != ""
