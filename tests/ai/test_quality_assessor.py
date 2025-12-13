"""Tests for AI quality assessor."""
import pytest
from unittest.mock import AsyncMock, patch
import json

from company_researcher.ai.quality import (
    AIQualityAssessor,
    get_quality_assessor,
    reset_quality_assessor,
    QualityLevel,
    SourceType,
    ContentQualityAssessment,
    SourceQualityAssessment,
    OverallQualityReport,
)


class TestQualityLevel:
    """Test QualityLevel enum."""

    def test_from_score_excellent(self):
        """Test excellent score mapping."""
        assert QualityLevel.from_score(95) == QualityLevel.EXCELLENT
        assert QualityLevel.from_score(90) == QualityLevel.EXCELLENT
        assert QualityLevel.from_score(100) == QualityLevel.EXCELLENT

    def test_from_score_good(self):
        """Test good score mapping."""
        assert QualityLevel.from_score(80) == QualityLevel.GOOD
        assert QualityLevel.from_score(75) == QualityLevel.GOOD
        assert QualityLevel.from_score(89) == QualityLevel.GOOD

    def test_from_score_acceptable(self):
        """Test acceptable score mapping."""
        assert QualityLevel.from_score(65) == QualityLevel.ACCEPTABLE
        assert QualityLevel.from_score(60) == QualityLevel.ACCEPTABLE
        assert QualityLevel.from_score(74) == QualityLevel.ACCEPTABLE

    def test_from_score_poor(self):
        """Test poor score mapping."""
        assert QualityLevel.from_score(50) == QualityLevel.POOR
        assert QualityLevel.from_score(40) == QualityLevel.POOR
        assert QualityLevel.from_score(59) == QualityLevel.POOR

    def test_from_score_insufficient(self):
        """Test insufficient score mapping."""
        assert QualityLevel.from_score(20) == QualityLevel.INSUFFICIENT
        assert QualityLevel.from_score(0) == QualityLevel.INSUFFICIENT
        assert QualityLevel.from_score(39) == QualityLevel.INSUFFICIENT

    def test_is_passing_with_default_threshold(self):
        """Test passing check with default 75% threshold."""
        assert QualityLevel.EXCELLENT.is_passing()
        assert QualityLevel.GOOD.is_passing()
        assert not QualityLevel.ACCEPTABLE.is_passing()
        assert not QualityLevel.POOR.is_passing()
        assert not QualityLevel.INSUFFICIENT.is_passing()

    def test_is_passing_with_custom_threshold(self):
        """Test passing check with custom threshold."""
        assert QualityLevel.EXCELLENT.is_passing(90)
        assert not QualityLevel.GOOD.is_passing(90)
        assert QualityLevel.ACCEPTABLE.is_passing(60)
        assert QualityLevel.POOR.is_passing(40)

    def test_to_score_range(self):
        """Test score range conversion."""
        assert QualityLevel.EXCELLENT.to_score_range() == (90, 100)
        assert QualityLevel.GOOD.to_score_range() == (75, 89)
        assert QualityLevel.ACCEPTABLE.to_score_range() == (60, 74)
        assert QualityLevel.POOR.to_score_range() == (40, 59)
        assert QualityLevel.INSUFFICIENT.to_score_range() == (0, 39)


class TestSourceType:
    """Test SourceType enum."""

    def test_all_source_types_exist(self):
        """Test all expected source types exist."""
        assert SourceType.OFFICIAL.value == "official"
        assert SourceType.REGULATORY.value == "regulatory"
        assert SourceType.NEWS_MAJOR.value == "news_major"
        assert SourceType.NEWS_TRADE.value == "news_trade"
        assert SourceType.NEWS_LOCAL.value == "news_local"
        assert SourceType.ACADEMIC.value == "academic"
        assert SourceType.ANALYST.value == "analyst"
        assert SourceType.BLOG.value == "blog"
        assert SourceType.SOCIAL.value == "social"
        assert SourceType.UNKNOWN.value == "unknown"


class TestContentQualityAssessment:
    """Test ContentQualityAssessment model."""

    def test_create_assessment(self):
        """Test creating a content quality assessment."""
        assessment = ContentQualityAssessment(
            section_name="financial",
            quality_level=QualityLevel.GOOD,
            score=82.0,
            factual_density=0.75,
            specificity=0.8,
            completeness=0.7,
            issues=["Some figures lack sources"],
            strengths=["Recent data included"]
        )

        assert assessment.section_name == "financial"
        assert assessment.quality_level == QualityLevel.GOOD
        assert assessment.score == 82.0
        assert assessment.factual_density == 0.75
        assert len(assessment.issues) == 1
        assert len(assessment.strengths) == 1

    def test_default_values(self):
        """Test default values are set correctly."""
        assessment = ContentQualityAssessment(
            section_name="test",
            quality_level=QualityLevel.ACCEPTABLE,
            score=65.0,
            factual_density=0.5,
            specificity=0.5,
            completeness=0.5
        )

        assert assessment.accuracy_indicators == 0.5
        assert assessment.recency == 0.5
        assert assessment.issues == []
        assert assessment.strengths == []
        assert assessment.improvement_suggestions == []
        assert assessment.missing_topics == []


class TestSourceQualityAssessment:
    """Test SourceQualityAssessment model."""

    def test_create_source_assessment(self):
        """Test creating a source quality assessment."""
        assessment = SourceQualityAssessment(
            url="https://reuters.com/article/tesla",
            domain="reuters.com",
            title="Tesla Reports Record Revenue",
            quality_level=QualityLevel.EXCELLENT,
            source_type=SourceType.NEWS_MAJOR,
            authority_score=0.9,
            recency_score=0.95,
            relevance_score=0.85,
            is_primary_source=False
        )

        assert assessment.domain == "reuters.com"
        assert assessment.authority_score == 0.9
        assert assessment.is_primary_source is False
        assert assessment.source_type == SourceType.NEWS_MAJOR


class TestOverallQualityReport:
    """Test OverallQualityReport model."""

    def test_create_report(self):
        """Test creating an overall quality report."""
        section = ContentQualityAssessment(
            section_name="financial",
            quality_level=QualityLevel.GOOD,
            score=80.0,
            factual_density=0.7,
            specificity=0.8,
            completeness=0.75
        )

        report = OverallQualityReport(
            overall_score=78.0,
            overall_level=QualityLevel.GOOD,
            section_assessments=[section],
            section_scores={"financial": 80.0},
            ready_for_delivery=True,
            iteration_needed=False
        )

        assert report.overall_score == 78.0
        assert report.ready_for_delivery is True
        assert len(report.section_assessments) == 1

    def test_get_failing_sections(self):
        """Test identifying failing sections."""
        sections = [
            ContentQualityAssessment(
                section_name="financial",
                quality_level=QualityLevel.GOOD,
                score=80.0,
                factual_density=0.7,
                specificity=0.8,
                completeness=0.75
            ),
            ContentQualityAssessment(
                section_name="competitors",
                quality_level=QualityLevel.POOR,
                score=45.0,
                factual_density=0.3,
                specificity=0.4,
                completeness=0.3
            ),
        ]

        report = OverallQualityReport(
            overall_score=62.5,
            overall_level=QualityLevel.ACCEPTABLE,
            section_assessments=sections,
            ready_for_delivery=False,
            iteration_needed=True
        )

        failing = report.get_failing_sections()
        assert "competitors" in failing
        assert "financial" not in failing

    def test_get_section_score(self):
        """Test getting score for specific section."""
        section = ContentQualityAssessment(
            section_name="financial",
            quality_level=QualityLevel.GOOD,
            score=80.0,
            factual_density=0.7,
            specificity=0.8,
            completeness=0.75
        )

        report = OverallQualityReport(
            overall_score=80.0,
            overall_level=QualityLevel.GOOD,
            section_assessments=[section],
            ready_for_delivery=True,
            iteration_needed=False
        )

        assert report.get_section_score("financial") == 80.0
        assert report.get_section_score("nonexistent") is None


class TestAIQualityAssessor:
    """Test AIQualityAssessor class."""

    @pytest.fixture
    def assessor(self):
        """Create assessor instance."""
        reset_quality_assessor()
        return AIQualityAssessor()

    @pytest.fixture
    def mock_content_response(self):
        """Mock LLM response for content assessment."""
        return json.dumps({
            "section_name": "financial",
            "quality_level": "good",
            "score": 82,
            "factual_density": 0.75,
            "specificity": 0.8,
            "completeness": 0.85,
            "accuracy_indicators": 0.7,
            "recency": 0.9,
            "issues": ["Some figures lack sources"],
            "strengths": ["Specific revenue numbers", "Recent data"],
            "improvement_suggestions": ["Add source citations"],
            "missing_topics": ["Profit margins"]
        })

    @pytest.fixture
    def mock_source_response(self):
        """Mock LLM response for source assessment."""
        return json.dumps({
            "url": "https://reuters.com/article/tesla",
            "domain": "reuters.com",
            "title": "Tesla Reports Record Revenue",
            "quality_level": "excellent",
            "source_type": "news_major",
            "authority_score": 0.9,
            "recency_score": 0.95,
            "relevance_score": 0.85,
            "depth_score": 0.7,
            "is_primary_source": False,
            "is_paywalled": False,
            "reasoning": "Major financial news outlet with recent coverage"
        })

    @pytest.mark.asyncio
    async def test_assess_content_quality(self, assessor, mock_content_response):
        """Test content quality assessment."""
        with patch.object(assessor, '_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_content_response

            result = await assessor.assess_content_quality(
                content="Tesla reported $81.5B revenue in 2023, a 19% increase from the previous year. The company maintains 20% market share in the global EV market.",
                section_name="financial",
                company_name="Tesla"
            )

            assert result.quality_level == QualityLevel.GOOD
            assert result.score == 82
            assert result.factual_density == 0.75
            assert len(result.issues) == 1
            assert len(result.strengths) == 2

    @pytest.mark.asyncio
    async def test_assess_empty_content(self, assessor):
        """Test assessment of empty content."""
        result = await assessor.assess_content_quality(
            content="",
            section_name="financial",
            company_name="Tesla"
        )

        assert result.quality_level == QualityLevel.INSUFFICIENT
        assert result.score == 0.0
        assert "empty or too short" in result.issues[0].lower()

    @pytest.mark.asyncio
    async def test_assess_very_short_content(self, assessor):
        """Test assessment of very short content."""
        result = await assessor.assess_content_quality(
            content="Tesla is a company.",  # Less than 50 chars
            section_name="financial",
            company_name="Tesla"
        )

        assert result.quality_level == QualityLevel.INSUFFICIENT
        assert result.score == 0.0

    @pytest.mark.asyncio
    async def test_assess_source_quality(self, assessor, mock_source_response):
        """Test source quality assessment."""
        with patch.object(assessor, '_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_source_response

            result = await assessor.assess_source_quality(
                url="https://reuters.com/article/tesla",
                title="Tesla Reports Record Revenue",
                snippet="Tesla Inc reported record revenue...",
                company_name="Tesla"
            )

            assert result.quality_level == QualityLevel.EXCELLENT
            assert result.authority_score == 0.9
            assert result.is_primary_source is False
            assert result.source_type == SourceType.NEWS_MAJOR

    @pytest.mark.asyncio
    async def test_generate_overall_report(self, assessor):
        """Test overall report generation."""
        mock_response = json.dumps({
            "overall_score": 78,
            "overall_level": "good",
            "key_gaps": ["ESG information missing"],
            "critical_issues": [],
            "recommendations": ["Add more recent data"],
            "ready_for_delivery": True,
            "iteration_needed": False,
            "focus_areas_for_iteration": []
        })

        with patch.object(assessor, '_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            section_assessments = [
                ContentQualityAssessment(
                    section_name="financial",
                    quality_level=QualityLevel.GOOD,
                    score=80,
                    factual_density=0.7,
                    specificity=0.8,
                    completeness=0.75
                )
            ]

            source_assessments = [
                SourceQualityAssessment(
                    url="https://example.com",
                    domain="example.com",
                    quality_level=QualityLevel.GOOD,
                    source_type=SourceType.NEWS_MAJOR,
                    authority_score=0.8,
                    recency_score=0.9,
                    relevance_score=0.85,
                    is_primary_source=False
                )
            ]

            report = await assessor.generate_overall_report(
                company_name="Tesla",
                section_assessments=section_assessments,
                source_assessments=source_assessments,
                threshold=75.0
            )

            assert report.overall_score == 78
            assert report.ready_for_delivery is True
            assert report.iteration_needed is False
            assert len(report.key_gaps) == 1

    @pytest.mark.asyncio
    async def test_assess_confidence(self, assessor):
        """Test confidence assessment."""
        mock_response = json.dumps({
            "claim": "Tesla revenue is $81.5B",
            "confidence_level": "good",
            "confidence_score": 0.85,
            "supporting_sources": 3,
            "contradicting_sources": 0,
            "source_quality_avg": 0.8,
            "uncertainty_indicators": [],
            "verification_status": "verified",
            "reasoning": "Multiple high-quality sources confirm this figure"
        })

        with patch.object(assessor, '_call_llm', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await assessor.assess_confidence(
                claim="Tesla revenue is $81.5B",
                evidence=[
                    {"source": "Reuters", "supports": True, "quote": "Tesla reported $81.5B"},
                    {"source": "Bloomberg", "supports": True, "quote": "Revenue of $81.5 billion"},
                ],
                company_name="Tesla"
            )

            assert result.confidence_level == QualityLevel.GOOD
            assert result.confidence_score == 0.85
            assert result.supporting_sources == 3
            assert result.verification_status == "verified"



class TestQualityAssessorSingleton:
    """Test singleton behavior."""

    def test_get_quality_assessor_returns_same_instance(self):
        """Test that get_quality_assessor returns singleton."""
        reset_quality_assessor()
        assessor1 = get_quality_assessor()
        assessor2 = get_quality_assessor()
        assert assessor1 is assessor2

    def test_reset_quality_assessor(self):
        """Test that reset creates new instance."""
        assessor1 = get_quality_assessor()
        reset_quality_assessor()
        assessor2 = get_quality_assessor()
        assert assessor1 is not assessor2


class TestAIQualityAssessorIntegration:
    """Integration tests for AIQualityAssessor."""

    @pytest.fixture
    def assessor(self):
        """Create assessor instance."""
        reset_quality_assessor()
        return AIQualityAssessor()

    @pytest.mark.asyncio
    async def test_full_process_workflow(self, assessor):
        """Test the full process method."""
        mock_content_response = json.dumps({
            "section_name": "financial",
            "quality_level": "good",
            "score": 80,
            "factual_density": 0.7,
            "specificity": 0.8,
            "completeness": 0.75,
            "issues": [],
            "strengths": ["Good data"],
            "improvement_suggestions": [],
            "missing_topics": []
        })

        mock_source_response = json.dumps({
            "url": "https://example.com",
            "domain": "example.com",
            "title": "Test",
            "quality_level": "good",
            "source_type": "news_major",
            "authority_score": 0.8,
            "recency_score": 0.9,
            "relevance_score": 0.85,
            "depth_score": 0.7,
            "is_primary_source": False,
            "is_paywalled": False,
            "reasoning": "Good source"
        })

        mock_overall_response = json.dumps({
            "overall_score": 78,
            "overall_level": "good",
            "key_gaps": [],
            "critical_issues": [],
            "recommendations": [],
            "ready_for_delivery": True,
            "iteration_needed": False,
            "focus_areas_for_iteration": []
        })

        call_count = [0]
        responses = [mock_content_response, mock_source_response, mock_overall_response]

        async def mock_llm(*args, **kwargs):
            idx = min(call_count[0], len(responses) - 1)
            call_count[0] += 1
            return responses[idx]

        with patch.object(assessor, '_call_llm', side_effect=mock_llm):
            result = await assessor.process(
                company_name="Tesla",
                sections={"financial": "Tesla reported $81.5B in revenue for 2023, a 19% increase from the previous year. The company maintains a strong market position in the EV industry."},
                sources=[{"url": "https://example.com", "title": "Test", "snippet": "Tesla reported strong quarterly results..."}]
            )

            assert isinstance(result, OverallQualityReport)
            assert result.ready_for_delivery is True

    @pytest.mark.asyncio
    async def test_graceful_degradation_on_llm_failure(self, assessor):
        """Test that LLM failures result in graceful degradation with fallback response.

        The implementation uses graceful degradation pattern - when LLM fails,
        it returns a fallback assessment rather than raising an exception.
        This ensures the research workflow can continue even with LLM issues.
        """
        from company_researcher.ai.quality.models import ContentQualityAssessment

        async def mock_failing_llm(*args, **kwargs):
            raise Exception("LLM service unavailable")

        with patch.object(assessor, '_call_llm', side_effect=mock_failing_llm):
            # Should NOT raise - graceful degradation returns fallback
            result = await assessor.assess_content_quality(
                content="Tesla reported significant revenue growth in 2023 with strong market position.",
                section_name="financial",
                company_name="Tesla"
            )

            # Verify fallback result is returned
            assert isinstance(result, ContentQualityAssessment)
            # Fallback typically returns moderate/default scores
            assert 0 <= result.score <= 100
