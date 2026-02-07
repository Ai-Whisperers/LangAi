"""Tests for ESG scorer."""

import pytest

from company_researcher.agents.esg.models import (
    Controversy,
    ControversySeverity,
    ESGCategory,
    ESGMetric,
    ESGRating,
    ESGScore,
)
from company_researcher.agents.esg.scorer import ESGScorer


class TestESGScorerInit:
    """Tests for ESGScorer initialization."""

    def test_default_base_score(self):
        """ESGScorer should default to base score of 50."""
        scorer = ESGScorer()
        assert scorer.base_score == 50.0

    def test_custom_base_score(self):
        """ESGScorer should accept custom base score."""
        scorer = ESGScorer(base_score=60.0)
        assert scorer.base_score == 60.0


class TestESGScorerCalculateScore:
    """Tests for ESGScorer.calculate_score method."""

    @pytest.fixture
    def scorer(self):
        """Create default ESG scorer."""
        return ESGScorer()

    def test_empty_inputs(self, scorer):
        """calculate_score with no inputs should return base scores."""
        score = scorer.calculate_score(metrics=[], controversies=[])

        assert score.overall_score == pytest.approx(50.0, rel=0.01)
        assert score.environmental_score == 50.0
        assert score.social_score == 50.0
        assert score.governance_score == 50.0

    def test_improving_metrics_increase_score(self, scorer):
        """Improving metrics should increase category scores."""
        metrics = [
            ESGMetric(
                name="Carbon Emissions",
                category=ESGCategory.ENVIRONMENTAL,
                value=1000,
                trend="improving",
            )
        ]
        score = scorer.calculate_score(metrics, [])

        assert score.environmental_score > 50.0

    def test_declining_metrics_decrease_score(self, scorer):
        """Declining metrics should decrease category scores."""
        metrics = [
            ESGMetric(
                name="Safety Incidents", category=ESGCategory.SOCIAL, value=10, trend="declining"
            )
        ]
        score = scorer.calculate_score(metrics, [])

        assert score.social_score < 50.0

    def test_above_benchmark_increases_score(self, scorer):
        """Metrics above benchmark should increase score."""
        metrics = [
            ESGMetric(
                name="Board Independence", category=ESGCategory.GOVERNANCE, value=80, benchmark=60.0
            )
        ]
        score = scorer.calculate_score(metrics, [])

        assert score.governance_score > 50.0

    def test_below_benchmark_decreases_score(self, scorer):
        """Metrics below benchmark should decrease score."""
        metrics = [
            ESGMetric(
                name="Renewable Energy",
                category=ESGCategory.ENVIRONMENTAL,
                value=20,
                benchmark=50.0,
            )
        ]
        score = scorer.calculate_score(metrics, [])

        assert score.environmental_score < 50.0

    def test_controversies_decrease_score(self, scorer):
        """Controversies should decrease category scores."""
        controversies = [
            Controversy(
                title="Environmental Incident",
                description="Major pollution event",
                category=ESGCategory.ENVIRONMENTAL,
                severity=ControversySeverity.HIGH,
            )
        ]
        score = scorer.calculate_score([], controversies)

        assert score.environmental_score < 50.0

    def test_severe_controversy_penalty(self, scorer):
        """Severe controversies should have larger penalty."""
        severe = [
            Controversy(
                title="Major Scandal",
                description="...",
                category=ESGCategory.GOVERNANCE,
                severity=ControversySeverity.SEVERE,
            )
        ]
        moderate = [
            Controversy(
                title="Minor Issue",
                description="...",
                category=ESGCategory.GOVERNANCE,
                severity=ControversySeverity.MODERATE,
            )
        ]
        score_severe = scorer.calculate_score([], severe)
        score_moderate = scorer.calculate_score([], moderate)

        assert score_severe.governance_score < score_moderate.governance_score

    def test_resolved_controversy_reduced_penalty(self, scorer):
        """Resolved controversies should have reduced penalty."""
        unresolved = [
            Controversy(
                title="Issue",
                description="...",
                category=ESGCategory.SOCIAL,
                severity=ControversySeverity.HIGH,
                resolved=False,
            )
        ]
        resolved = [
            Controversy(
                title="Issue",
                description="...",
                category=ESGCategory.SOCIAL,
                severity=ControversySeverity.HIGH,
                resolved=True,
            )
        ]
        score_unresolved = scorer.calculate_score([], unresolved)
        score_resolved = scorer.calculate_score([], resolved)

        assert score_resolved.social_score > score_unresolved.social_score

    def test_scores_clamped_to_range(self, scorer):
        """Scores should be clamped to 0-100 range."""
        # Many positive metrics
        metrics = [
            ESGMetric(
                name=f"Metric {i}",
                category=ESGCategory.ENVIRONMENTAL,
                value=100,
                trend="improving",
                benchmark=50.0,
            )
            for i in range(20)
        ]
        score = scorer.calculate_score(metrics, [])

        assert score.environmental_score <= 100.0

    def test_overall_score_weighted_average(self, scorer):
        """Overall score should be weighted average of categories."""
        # Create metrics that move each category differently
        metrics = [
            ESGMetric(name="E", category=ESGCategory.ENVIRONMENTAL, value=100, trend="improving"),
            ESGMetric(name="S", category=ESGCategory.SOCIAL, value=100, trend="improving"),
            ESGMetric(name="G", category=ESGCategory.GOVERNANCE, value=100, trend="improving"),
        ]
        score = scorer.calculate_score(metrics, [])

        # All categories should be elevated equally, so overall should match
        assert score.overall_score == pytest.approx(
            (
                score.environmental_score * 0.33
                + score.social_score * 0.33
                + score.governance_score * 0.34
            ),
            rel=0.01,
        )


class TestESGScorerRatings:
    """Tests for score to rating conversion."""

    @pytest.fixture
    def scorer(self):
        return ESGScorer()

    def test_aaa_rating_threshold(self, scorer):
        """Score >= 85 should get AAA rating."""
        rating = scorer._score_to_rating(90)
        assert rating == ESGRating.AAA

    def test_aa_rating_threshold(self, scorer):
        """Score >= 75 should get AA rating."""
        rating = scorer._score_to_rating(80)
        assert rating == ESGRating.AA

    def test_a_rating_threshold(self, scorer):
        """Score >= 65 should get A rating."""
        rating = scorer._score_to_rating(70)
        assert rating == ESGRating.A

    def test_bbb_rating_threshold(self, scorer):
        """Score >= 55 should get BBB rating."""
        rating = scorer._score_to_rating(60)
        assert rating == ESGRating.BBB

    def test_c_rating_for_low_score(self, scorer):
        """Very low scores should get C rating."""
        rating = scorer._score_to_rating(5)
        assert rating == ESGRating.C

    def test_boundary_scores(self, scorer):
        """Test exact boundary scores."""
        assert scorer._score_to_rating(85) == ESGRating.AAA
        assert scorer._score_to_rating(84.9) == ESGRating.AA
        assert scorer._score_to_rating(75) == ESGRating.AA


class TestESGScorerConfidence:
    """Tests for confidence calculation."""

    @pytest.fixture
    def scorer(self):
        return ESGScorer()

    def test_base_confidence(self, scorer):
        """No metrics should give base confidence."""
        confidence = scorer._calculate_confidence([], [])
        assert confidence == pytest.approx(0.3)

    def test_more_metrics_higher_confidence(self, scorer):
        """More metrics should increase confidence."""
        few_metrics = [
            ESGMetric(name=f"M{i}", category=ESGCategory.ENVIRONMENTAL, value=i) for i in range(3)
        ]
        many_metrics = [
            ESGMetric(name=f"M{i}", category=ESGCategory.ENVIRONMENTAL, value=i) for i in range(15)
        ]
        conf_few = scorer._calculate_confidence(few_metrics, [])
        conf_many = scorer._calculate_confidence(many_metrics, [])

        assert conf_many > conf_few

    def test_category_coverage_increases_confidence(self, scorer):
        """Covering all categories should increase confidence."""
        single_category = [ESGMetric(name="E1", category=ESGCategory.ENVIRONMENTAL, value=1)]
        all_categories = [
            ESGMetric(name="E", category=ESGCategory.ENVIRONMENTAL, value=1),
            ESGMetric(name="S", category=ESGCategory.SOCIAL, value=1),
            ESGMetric(name="G", category=ESGCategory.GOVERNANCE, value=1),
        ]
        conf_single = scorer._calculate_confidence(single_category, [])
        conf_all = scorer._calculate_confidence(all_categories, [])

        assert conf_all > conf_single

    def test_sourced_metrics_increase_confidence(self, scorer):
        """Metrics with sources should increase confidence."""
        unsourced = [ESGMetric(name="M1", category=ESGCategory.ENVIRONMENTAL, value=1, source="")]
        sourced = [
            ESGMetric(
                name="M1", category=ESGCategory.ENVIRONMENTAL, value=1, source="Annual Report"
            )
        ]
        conf_unsourced = scorer._calculate_confidence(unsourced, [])
        conf_sourced = scorer._calculate_confidence(sourced, [])

        assert conf_sourced > conf_unsourced

    def test_confidence_capped_at_one(self, scorer):
        """Confidence should not exceed 1.0."""
        many_sourced = [
            ESGMetric(name=f"M{i}", category=list(ESGCategory)[i % 3], value=i, source="Source")
            for i in range(20)
        ]
        confidence = scorer._calculate_confidence(many_sourced, [])

        assert confidence <= 1.0


class TestESGScorerStrengthsRisks:
    """Tests for identifying strengths and risks."""

    @pytest.fixture
    def scorer(self):
        return ESGScorer()

    def test_improving_metrics_as_strengths(self, scorer):
        """Improving metrics should be identified as strengths."""
        metrics = [
            ESGMetric(
                name="Carbon Emissions",
                category=ESGCategory.ENVIRONMENTAL,
                value=1000,
                trend="improving",
            )
        ]
        strengths, risks = scorer.identify_strengths_risks(metrics, [])

        assert any("Improving" in s and "Carbon" in s for s in strengths)

    def test_declining_metrics_as_risks(self, scorer):
        """Declining metrics should be identified as risks."""
        metrics = [
            ESGMetric(
                name="Safety Incidents", category=ESGCategory.SOCIAL, value=10, trend="declining"
            )
        ]
        strengths, risks = scorer.identify_strengths_risks(metrics, [])

        assert any("Declining" in r and "Safety" in r for r in risks)

    def test_above_benchmark_as_strength(self, scorer):
        """Above benchmark metrics should be strengths."""
        metrics = [
            ESGMetric(
                name="Renewable Energy",
                category=ESGCategory.ENVIRONMENTAL,
                value=90,
                benchmark=50.0,
            )
        ]
        strengths, risks = scorer.identify_strengths_risks(metrics, [])

        assert any("Above benchmark" in s for s in strengths)

    def test_below_benchmark_as_risk(self, scorer):
        """Below benchmark metrics should be risks."""
        metrics = [
            ESGMetric(
                name="Board Diversity", category=ESGCategory.GOVERNANCE, value=20, benchmark=50.0
            )
        ]
        strengths, risks = scorer.identify_strengths_risks(metrics, [])

        assert any("Below benchmark" in r for r in risks)

    def test_severe_controversies_as_risks(self, scorer):
        """Severe and high controversies should be identified as risks."""
        controversies = [
            Controversy(
                title="Major Scandal",
                description="...",
                category=ESGCategory.GOVERNANCE,
                severity=ControversySeverity.SEVERE,
            )
        ]
        strengths, risks = scorer.identify_strengths_risks([], controversies)

        assert any("Major Scandal" in r for r in risks)

    def test_limited_to_five_each(self, scorer):
        """Strengths and risks should be limited to 5 each."""
        metrics = [
            ESGMetric(
                name=f"Metric {i}", category=ESGCategory.ENVIRONMENTAL, value=100, trend="improving"
            )
            for i in range(10)
        ]
        strengths, risks = scorer.identify_strengths_risks(metrics, [])

        assert len(strengths) <= 5
        assert len(risks) <= 5


class TestESGScorerRecommendations:
    """Tests for generating recommendations."""

    @pytest.fixture
    def scorer(self):
        return ESGScorer()

    def test_missing_category_recommendation(self, scorer):
        """Missing category should generate disclosure recommendation."""
        metrics = [ESGMetric(name="E", category=ESGCategory.ENVIRONMENTAL, value=1)]
        score = ESGScore(
            overall_score=50,
            overall_rating=ESGRating.BBB,
            environmental_score=50,
            social_score=50,
            governance_score=50,
        )
        recs = scorer.generate_recommendations(metrics, score, [])

        # Should recommend improving social and governance
        assert any("social" in r.lower() for r in recs)
        assert any("governance" in r.lower() for r in recs)

    def test_low_score_recommendation(self, scorer):
        """Low category score should generate improvement recommendation."""
        metrics = []
        score = ESGScore(
            overall_score=40,
            overall_rating=ESGRating.BB,
            environmental_score=30,
            social_score=50,
            governance_score=40,
        )
        recs = scorer.generate_recommendations(metrics, score, [])

        assert any("environmental" in r.lower() for r in recs)

    def test_risk_based_recommendations(self, scorer):
        """Risks should generate corresponding recommendations."""
        metrics = []
        score = ESGScore(
            overall_score=50,
            overall_rating=ESGRating.BBB,
            environmental_score=50,
            social_score=50,
            governance_score=50,
        )
        risks = ["Environmental: Major pollution issue"]
        recs = scorer.generate_recommendations(metrics, score, risks)

        assert any("environmental" in r.lower() for r in recs)

    def test_recommendations_limited_to_five(self, scorer):
        """Recommendations should be limited to 5."""
        metrics = []  # No metrics = all categories missing
        score = ESGScore(
            overall_score=20,
            overall_rating=ESGRating.CCC,
            environmental_score=20,
            social_score=20,
            governance_score=20,
        )
        risks = ["Environmental: Issue 1", "Social: Issue 2", "Governance: Issue 3"]
        recs = scorer.generate_recommendations(metrics, score, risks)

        assert len(recs) <= 5

    def test_no_duplicate_recommendations(self, scorer):
        """Recommendations should not have duplicates."""
        metrics = []
        score = ESGScore(
            overall_score=20,
            overall_rating=ESGRating.CCC,
            environmental_score=20,
            social_score=20,
            governance_score=20,
        )
        risks = [
            "Environmental: Issue 1",
            "Environmental: Issue 2",
        ]
        recs = scorer.generate_recommendations(metrics, score, risks)

        assert len(recs) == len(set(recs))


class TestESGScorerClampScore:
    """Tests for _clamp_score method."""

    @pytest.fixture
    def scorer(self):
        return ESGScorer()

    def test_clamp_negative_to_zero(self, scorer):
        """Negative scores should be clamped to 0."""
        assert scorer._clamp_score(-10) == 0

    def test_clamp_above_100_to_100(self, scorer):
        """Scores above 100 should be clamped to 100."""
        assert scorer._clamp_score(150) == 100

    def test_valid_scores_unchanged(self, scorer):
        """Valid scores should remain unchanged."""
        assert scorer._clamp_score(50) == 50
        assert scorer._clamp_score(0) == 0
        assert scorer._clamp_score(100) == 100
