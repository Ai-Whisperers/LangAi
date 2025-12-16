"""Tests for ESG models."""

from datetime import datetime, timezone

import pytest

from company_researcher.agents.esg.models import (
    ENVIRONMENTAL_INDICATORS,
    GOVERNANCE_INDICATORS,
    SOCIAL_INDICATORS,
    Controversy,
    ControversySeverity,
    ESGAnalysis,
    ESGCategory,
    ESGMetric,
    ESGRating,
    ESGScore,
)


class TestESGCategory:
    """Tests for ESGCategory enum."""

    def test_category_values(self):
        """ESGCategory should have correct values."""
        assert ESGCategory.ENVIRONMENTAL.value == "environmental"
        assert ESGCategory.SOCIAL.value == "social"
        assert ESGCategory.GOVERNANCE.value == "governance"

    def test_category_is_string_enum(self):
        """ESGCategory should be a string enum."""
        assert isinstance(ESGCategory.ENVIRONMENTAL.value, str)


class TestESGRating:
    """Tests for ESGRating enum."""

    def test_all_ratings(self):
        """ESGRating should have all standard ratings."""
        ratings = [r.value for r in ESGRating]
        assert "AAA" in ratings
        assert "AA" in ratings
        assert "A" in ratings
        assert "BBB" in ratings
        assert "BB" in ratings
        assert "B" in ratings
        assert "CCC" in ratings
        assert "CC" in ratings
        assert "C" in ratings

    def test_rating_count(self):
        """ESGRating should have 9 levels."""
        assert len(ESGRating) == 9


class TestControversySeverity:
    """Tests for ControversySeverity enum."""

    def test_severity_levels(self):
        """ControversySeverity should have correct levels."""
        assert ControversySeverity.SEVERE.value == "severe"
        assert ControversySeverity.HIGH.value == "high"
        assert ControversySeverity.MODERATE.value == "moderate"
        assert ControversySeverity.LOW.value == "low"
        assert ControversySeverity.NONE.value == "none"


class TestESGMetric:
    """Tests for ESGMetric dataclass."""

    def test_create_metric(self):
        """ESGMetric should store all fields."""
        metric = ESGMetric(
            name="Carbon Emissions",
            category=ESGCategory.ENVIRONMENTAL,
            value=1000,
            unit="tCO2e",
            year=2023,
            trend="improving",
            benchmark=1200,
            source="Annual Report",
        )
        assert metric.name == "Carbon Emissions"
        assert metric.category == ESGCategory.ENVIRONMENTAL
        assert metric.value == 1000
        assert metric.unit == "tCO2e"
        assert metric.trend == "improving"
        assert metric.benchmark == 1200

    def test_metric_defaults(self):
        """ESGMetric should have sensible defaults."""
        metric = ESGMetric(name="Test", category=ESGCategory.SOCIAL, value=50)
        assert metric.unit == ""
        assert metric.year == 0
        assert metric.trend == ""
        assert metric.benchmark is None
        assert metric.source == ""

    def test_metric_to_dict(self):
        """ESGMetric.to_dict should return correct dictionary."""
        metric = ESGMetric(
            name="Renewable Energy",
            category=ESGCategory.ENVIRONMENTAL,
            value=75,
            unit="%",
            year=2023,
            trend="stable",
        )
        result = metric.to_dict()

        assert result["name"] == "Renewable Energy"
        assert result["category"] == "environmental"
        assert result["value"] == 75
        assert result["unit"] == "%"
        assert result["trend"] == "stable"


class TestControversy:
    """Tests for Controversy dataclass."""

    def test_create_controversy(self):
        """Controversy should store all fields."""
        date = datetime(2023, 6, 15, tzinfo=timezone.utc)
        controversy = Controversy(
            title="Environmental Incident",
            description="Oil spill reported",
            category=ESGCategory.ENVIRONMENTAL,
            severity=ControversySeverity.HIGH,
            date=date,
            resolved=False,
            impact="Significant environmental damage",
            sources=["https://news.com/article"],
        )
        assert controversy.title == "Environmental Incident"
        assert controversy.category == ESGCategory.ENVIRONMENTAL
        assert controversy.severity == ControversySeverity.HIGH
        assert controversy.resolved is False

    def test_controversy_defaults(self):
        """Controversy should have sensible defaults."""
        controversy = Controversy(
            title="Test",
            description="Test controversy",
            category=ESGCategory.GOVERNANCE,
            severity=ControversySeverity.LOW,
        )
        assert controversy.date is None
        assert controversy.resolved is False
        assert controversy.impact == ""
        assert controversy.sources == []

    def test_controversy_to_dict(self):
        """Controversy.to_dict should return correct dictionary."""
        date = datetime(2023, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        controversy = Controversy(
            title="Test Issue",
            description="Description",
            category=ESGCategory.SOCIAL,
            severity=ControversySeverity.MODERATE,
            date=date,
            resolved=True,
        )
        result = controversy.to_dict()

        assert result["title"] == "Test Issue"
        assert result["category"] == "social"
        assert result["severity"] == "moderate"
        assert result["resolved"] is True
        assert "2023-06-15" in result["date"]

    def test_controversy_to_dict_no_date(self):
        """Controversy.to_dict should handle None date."""
        controversy = Controversy(
            title="Test",
            description="Test",
            category=ESGCategory.GOVERNANCE,
            severity=ControversySeverity.LOW,
        )
        result = controversy.to_dict()
        assert result["date"] is None


class TestESGScore:
    """Tests for ESGScore dataclass."""

    def test_create_score(self):
        """ESGScore should store all scores."""
        score = ESGScore(
            overall_score=75.5,
            overall_rating=ESGRating.AA,
            environmental_score=80.0,
            social_score=70.0,
            governance_score=76.0,
            confidence=0.85,
        )
        assert score.overall_score == 75.5
        assert score.overall_rating == ESGRating.AA
        assert score.environmental_score == 80.0
        assert score.confidence == 0.85

    def test_score_default_confidence(self):
        """ESGScore should default confidence to 0."""
        score = ESGScore(
            overall_score=50,
            overall_rating=ESGRating.BBB,
            environmental_score=50,
            social_score=50,
            governance_score=50,
        )
        assert score.confidence == 0.0

    def test_score_to_dict(self):
        """ESGScore.to_dict should return correct dictionary."""
        score = ESGScore(
            overall_score=65.0,
            overall_rating=ESGRating.A,
            environmental_score=70.0,
            social_score=60.0,
            governance_score=65.0,
            confidence=0.75,
        )
        result = score.to_dict()

        assert result["overall_score"] == 65.0
        assert result["overall_rating"] == "A"
        assert result["environmental_score"] == 70.0
        assert result["confidence"] == 0.75


class TestESGAnalysis:
    """Tests for ESGAnalysis dataclass."""

    @pytest.fixture
    def sample_analysis(self):
        """Create sample ESG analysis."""
        return ESGAnalysis(
            company_name="TestCorp",
            score=ESGScore(
                overall_score=70.0,
                overall_rating=ESGRating.A,
                environmental_score=75.0,
                social_score=65.0,
                governance_score=70.0,
            ),
            metrics=[
                ESGMetric(name="Carbon Emissions", category=ESGCategory.ENVIRONMENTAL, value=1000)
            ],
            controversies=[],
            environmental_summary="Good environmental practices",
            social_summary="Average social performance",
            governance_summary="Strong governance",
            strengths=["Low emissions"],
            risks=["Regulatory risk"],
            recommendations=["Improve diversity"],
            data_sources=["Annual Report"],
        )

    def test_analysis_stores_all_fields(self, sample_analysis):
        """ESGAnalysis should store all fields."""
        assert sample_analysis.company_name == "TestCorp"
        assert sample_analysis.score.overall_score == 70.0
        assert len(sample_analysis.metrics) == 1
        assert sample_analysis.strengths == ["Low emissions"]

    def test_analysis_to_dict(self, sample_analysis):
        """ESGAnalysis.to_dict should return complete dictionary."""
        result = sample_analysis.to_dict()

        assert result["company_name"] == "TestCorp"
        assert "score" in result
        assert result["score"]["overall_score"] == 70.0
        assert len(result["metrics"]) == 1
        assert result["strengths"] == ["Low emissions"]
        assert "analysis_date" in result


class TestIndicatorFrameworks:
    """Tests for indicator framework dictionaries."""

    def test_environmental_indicators_exist(self):
        """ENVIRONMENTAL_INDICATORS should have standard indicators."""
        assert "carbon_emissions" in ENVIRONMENTAL_INDICATORS
        assert "renewable_energy" in ENVIRONMENTAL_INDICATORS
        assert "water_usage" in ENVIRONMENTAL_INDICATORS

    def test_indicator_structure(self):
        """Indicators should have name, unit, and description."""
        carbon = ENVIRONMENTAL_INDICATORS["carbon_emissions"]
        assert "name" in carbon
        assert "unit" in carbon
        assert "description" in carbon

    def test_social_indicators_exist(self):
        """SOCIAL_INDICATORS should have standard indicators."""
        assert "employee_turnover" in SOCIAL_INDICATORS
        assert "diversity_leadership" in SOCIAL_INDICATORS
        assert "safety_incidents" in SOCIAL_INDICATORS

    def test_governance_indicators_exist(self):
        """GOVERNANCE_INDICATORS should have standard indicators."""
        assert "board_independence" in GOVERNANCE_INDICATORS
        assert "board_diversity" in GOVERNANCE_INDICATORS
        assert "ceo_pay_ratio" in GOVERNANCE_INDICATORS
