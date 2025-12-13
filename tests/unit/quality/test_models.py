"""Tests for quality models module."""

import pytest
from datetime import datetime, timezone

from company_researcher.quality.models import (
    SourceQuality,
    ConfidenceLevel,
    Source,
    ResearchFact,
    QualityReport,
)


class TestSourceQuality:
    """Tests for SourceQuality enum."""

    def test_all_levels_present(self):
        """SourceQuality should have 5 levels."""
        assert len(SourceQuality) == 5

    def test_level_values(self):
        """SourceQuality should have correct values."""
        assert SourceQuality.OFFICIAL.value == "OFFICIAL"
        assert SourceQuality.AUTHORITATIVE.value == "AUTHORITATIVE"
        assert SourceQuality.REPUTABLE.value == "REPUTABLE"
        assert SourceQuality.COMMUNITY.value == "COMMUNITY"
        assert SourceQuality.UNKNOWN.value == "UNKNOWN"


class TestConfidenceLevel:
    """Tests for ConfidenceLevel enum."""

    def test_all_levels_present(self):
        """ConfidenceLevel should have 3 levels."""
        assert len(ConfidenceLevel) == 3

    def test_level_values(self):
        """ConfidenceLevel should have correct values."""
        assert ConfidenceLevel.HIGH.value == "HIGH"
        assert ConfidenceLevel.MEDIUM.value == "MEDIUM"
        assert ConfidenceLevel.LOW.value == "LOW"


class TestSource:
    """Tests for Source model."""

    def test_create_source(self):
        """Source should store required fields."""
        source = Source(url="http://example.com", title="Test Article")
        assert source.url == "http://example.com"
        assert source.title == "Test Article"

    def test_default_quality(self):
        """Source should default to UNKNOWN quality."""
        source = Source(url="http://example.com", title="Test")
        assert source.quality == SourceQuality.UNKNOWN

    def test_default_quality_score(self):
        """Source should default to 30 quality score."""
        source = Source(url="http://example.com", title="Test")
        assert source.quality_score == 30

    def test_retrieved_at_auto_set(self):
        """Source should auto-set retrieved_at."""
        source = Source(url="http://example.com", title="Test")
        assert source.retrieved_at is not None
        assert isinstance(source.retrieved_at, datetime)

    def test_str_method(self):
        """Source __str__ should format correctly."""
        source = Source(
            url="http://example.com",
            title="Test Article",
            quality=SourceQuality.OFFICIAL,
            quality_score=85
        )
        result = str(source)
        assert "Test Article" in result
        assert "example.com" in result
        assert "OFFICIAL" in result

    def test_to_markdown(self):
        """Source to_markdown should format as markdown citation."""
        source = Source(
            url="http://example.com",
            title="Test Article",
            quality_score=75
        )
        result = source.to_markdown()
        assert "[Test Article]" in result
        assert "http://example.com" in result
        assert "75/100" in result


class TestResearchFact:
    """Tests for ResearchFact model."""

    @pytest.fixture
    def sample_source(self):
        """Create sample source for testing."""
        return Source(
            url="http://example.com",
            title="Test Source"
        )

    def test_create_fact(self, sample_source):
        """ResearchFact should store required fields."""
        fact = ResearchFact(
            content="Revenue is $1 billion",
            source=sample_source,
            extracted_by="financial"
        )
        assert fact.content == "Revenue is $1 billion"
        assert fact.extracted_by == "financial"

    def test_default_confidence(self, sample_source):
        """ResearchFact should default to MEDIUM confidence."""
        fact = ResearchFact(
            content="Test fact",
            source=sample_source,
            extracted_by="test"
        )
        assert fact.confidence == ConfidenceLevel.MEDIUM

    def test_default_verified(self, sample_source):
        """ResearchFact should default to unverified."""
        fact = ResearchFact(
            content="Test fact",
            source=sample_source,
            extracted_by="test"
        )
        assert fact.verified is False
        assert fact.verified_by is None

    def test_str_method(self, sample_source):
        """ResearchFact __str__ should format correctly."""
        fact = ResearchFact(
            content="Revenue is $1B",
            source=sample_source,
            extracted_by="financial",
            verified=True
        )
        result = str(fact)
        assert "Revenue is $1B" in result
        assert "✅" in result

    def test_str_unverified(self, sample_source):
        """ResearchFact __str__ should show unverified marker."""
        fact = ResearchFact(
            content="Test fact",
            source=sample_source,
            extracted_by="test",
            verified=False
        )
        result = str(fact)
        assert "❌" in result

    def test_to_markdown(self, sample_source):
        """ResearchFact to_markdown should format correctly."""
        fact = ResearchFact(
            content="Revenue is $1B",
            source=sample_source,
            extracted_by="financial",
            confidence=ConfidenceLevel.HIGH
        )
        result = fact.to_markdown()
        assert "Revenue is $1B" in result
        assert "HIGH" in result
        assert "financial" in result


class TestQualityReport:
    """Tests for QualityReport model."""

    def test_create_report(self):
        """QualityReport should store all scores."""
        report = QualityReport(
            overall_score=85.0,
            source_quality_score=90.0,
            verification_rate=80.0,
            recency_score=75.0,
            completeness_score=85.0
        )
        assert report.overall_score == 85.0
        assert report.source_quality_score == 90.0

    def test_default_counts(self):
        """QualityReport should default counts to 0."""
        report = QualityReport(
            overall_score=50,
            source_quality_score=50,
            verification_rate=50,
            recency_score=50,
            completeness_score=50
        )
        assert report.total_facts == 0
        assert report.verified_facts == 0
        assert report.high_quality_sources == 0

    def test_default_lists(self):
        """QualityReport should default lists to empty."""
        report = QualityReport(
            overall_score=50,
            source_quality_score=50,
            verification_rate=50,
            recency_score=50,
            completeness_score=50
        )
        assert report.missing_information == []
        assert report.strengths == []
        assert report.recommendations == []

    def test_is_passing_above_threshold(self):
        """is_passing should return True above threshold."""
        report = QualityReport(
            overall_score=90,
            source_quality_score=90,
            verification_rate=90,
            recency_score=90,
            completeness_score=90
        )
        assert report.is_passing() is True

    def test_is_passing_below_threshold(self):
        """is_passing should return False below threshold."""
        report = QualityReport(
            overall_score=70,
            source_quality_score=70,
            verification_rate=70,
            recency_score=70,
            completeness_score=70
        )
        assert report.is_passing() is False

    def test_is_passing_custom_threshold(self):
        """is_passing should accept custom threshold."""
        report = QualityReport(
            overall_score=75,
            source_quality_score=75,
            verification_rate=75,
            recency_score=75,
            completeness_score=75
        )
        assert report.is_passing(threshold=70) is True
        assert report.is_passing(threshold=80) is False


class TestQualityReportGrades:
    """Tests for QualityReport grade calculation."""

    def test_grade_a(self):
        """Score >= 90 should get A."""
        report = QualityReport(
            overall_score=95,
            source_quality_score=90,
            verification_rate=90,
            recency_score=90,
            completeness_score=90
        )
        assert report.get_grade() == "A"

    def test_grade_b(self):
        """Score >= 80 should get B."""
        report = QualityReport(
            overall_score=85,
            source_quality_score=85,
            verification_rate=85,
            recency_score=85,
            completeness_score=85
        )
        assert report.get_grade() == "B"

    def test_grade_c(self):
        """Score >= 70 should get C."""
        report = QualityReport(
            overall_score=75,
            source_quality_score=75,
            verification_rate=75,
            recency_score=75,
            completeness_score=75
        )
        assert report.get_grade() == "C"

    def test_grade_d(self):
        """Score >= 60 should get D."""
        report = QualityReport(
            overall_score=65,
            source_quality_score=65,
            verification_rate=65,
            recency_score=65,
            completeness_score=65
        )
        assert report.get_grade() == "D"

    def test_grade_f(self):
        """Score < 60 should get F."""
        report = QualityReport(
            overall_score=50,
            source_quality_score=50,
            verification_rate=50,
            recency_score=50,
            completeness_score=50
        )
        assert report.get_grade() == "F"

    def test_grade_boundaries(self):
        """Test exact boundary values."""
        report_90 = QualityReport(
            overall_score=90, source_quality_score=90,
            verification_rate=90, recency_score=90, completeness_score=90
        )
        report_80 = QualityReport(
            overall_score=80, source_quality_score=80,
            verification_rate=80, recency_score=80, completeness_score=80
        )
        report_70 = QualityReport(
            overall_score=70, source_quality_score=70,
            verification_rate=70, recency_score=70, completeness_score=70
        )
        report_60 = QualityReport(
            overall_score=60, source_quality_score=60,
            verification_rate=60, recency_score=60, completeness_score=60
        )

        assert report_90.get_grade() == "A"
        assert report_80.get_grade() == "B"
        assert report_70.get_grade() == "C"
        assert report_60.get_grade() == "D"


class TestQualityReportMarkdown:
    """Tests for QualityReport markdown generation."""

    def test_to_markdown_basic(self):
        """to_markdown should generate valid markdown."""
        report = QualityReport(
            overall_score=85,
            source_quality_score=90,
            verification_rate=80,
            recency_score=75,
            completeness_score=85,
            total_facts=10,
            verified_facts=8
        )
        result = report.to_markdown()

        assert "## Quality Report" in result
        assert "85" in result
        assert "PASS" in result or "Grade: B" in result

    def test_to_markdown_includes_scores(self):
        """to_markdown should include all scores."""
        report = QualityReport(
            overall_score=85,
            source_quality_score=90,
            verification_rate=80,
            recency_score=75,
            completeness_score=85
        )
        result = report.to_markdown()

        assert "85" in result  # overall
        assert "90" in result  # source quality
        assert "80" in result  # verification
        assert "75" in result  # recency

    def test_to_markdown_includes_facts(self):
        """to_markdown should include fact counts."""
        report = QualityReport(
            overall_score=85,
            source_quality_score=90,
            verification_rate=80,
            recency_score=75,
            completeness_score=85,
            total_facts=10,
            verified_facts=8
        )
        result = report.to_markdown()

        assert "10" in result  # total
        assert "8" in result   # verified

    def test_to_markdown_includes_lists(self):
        """to_markdown should include strengths and recommendations."""
        report = QualityReport(
            overall_score=85,
            source_quality_score=90,
            verification_rate=80,
            recency_score=75,
            completeness_score=85,
            strengths=["Good sources"],
            missing_information=["Leadership info"],
            recommendations=["Add more sources"]
        )
        result = report.to_markdown()

        assert "Good sources" in result
        assert "Leadership info" in result
        assert "Add more sources" in result


class TestSourceValidation:
    """Tests for Source model validation."""

    def test_quality_score_minimum(self):
        """Quality score should accept minimum value 0."""
        source = Source(
            url="http://example.com",
            title="Test",
            quality_score=0
        )
        assert source.quality_score == 0

    def test_quality_score_maximum(self):
        """Quality score should accept maximum value 100."""
        source = Source(
            url="http://example.com",
            title="Test",
            quality_score=100
        )
        assert source.quality_score == 100

    def test_quality_score_validation_error(self):
        """Quality score outside 0-100 should raise error."""
        with pytest.raises(ValueError):
            Source(
                url="http://example.com",
                title="Test",
                quality_score=150
            )


class TestQualityReportValidation:
    """Tests for QualityReport model validation."""

    def test_score_minimum(self):
        """Scores should accept minimum value 0."""
        report = QualityReport(
            overall_score=0,
            source_quality_score=0,
            verification_rate=0,
            recency_score=0,
            completeness_score=0
        )
        assert report.overall_score == 0

    def test_score_maximum(self):
        """Scores should accept maximum value 100."""
        report = QualityReport(
            overall_score=100,
            source_quality_score=100,
            verification_rate=100,
            recency_score=100,
            completeness_score=100
        )
        assert report.overall_score == 100

    def test_score_validation_error(self):
        """Scores outside 0-100 should raise error."""
        with pytest.raises(ValueError):
            QualityReport(
                overall_score=150,
                source_quality_score=100,
                verification_rate=100,
                recency_score=100,
                completeness_score=100
            )
