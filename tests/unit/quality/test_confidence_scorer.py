"""Tests for confidence scoring system."""

import pytest

from company_researcher.quality.confidence_scorer import (
    ConfidenceFactors,
    ConfidenceLevel,
    ConfidenceScorer,
    ScoredFact,
    SourceInfo,
    SourceType,
    create_confidence_scorer,
    score_facts,
)


class TestConfidenceLevelEnum:
    """Tests for ConfidenceLevel enum."""

    def test_very_high_value(self):
        """ConfidenceLevel.VERY_HIGH should have correct value."""
        assert ConfidenceLevel.VERY_HIGH.value == "very_high"

    def test_high_value(self):
        """ConfidenceLevel.HIGH should have correct value."""
        assert ConfidenceLevel.HIGH.value == "high"

    def test_medium_value(self):
        """ConfidenceLevel.MEDIUM should have correct value."""
        assert ConfidenceLevel.MEDIUM.value == "medium"

    def test_low_value(self):
        """ConfidenceLevel.LOW should have correct value."""
        assert ConfidenceLevel.LOW.value == "low"

    def test_very_low_value(self):
        """ConfidenceLevel.VERY_LOW should have correct value."""
        assert ConfidenceLevel.VERY_LOW.value == "very_low"


class TestSourceTypeEnum:
    """Tests for SourceType enum."""

    def test_official_value(self):
        """SourceType.OFFICIAL should have correct value."""
        assert SourceType.OFFICIAL.value == "official"

    def test_news_value(self):
        """SourceType.NEWS should have correct value."""
        assert SourceType.NEWS.value == "news"

    def test_research_value(self):
        """SourceType.RESEARCH should have correct value."""
        assert SourceType.RESEARCH.value == "research"

    def test_unknown_value(self):
        """SourceType.UNKNOWN should have correct value."""
        assert SourceType.UNKNOWN.value == "unknown"


class TestSourceInfo:
    """Tests for SourceInfo dataclass."""

    def test_required_url(self):
        """SourceInfo should require url."""
        info = SourceInfo(url="http://example.com")
        assert info.url == "http://example.com"

    def test_default_source_type(self):
        """SourceInfo should default to UNKNOWN type."""
        info = SourceInfo(url="http://example.com")
        assert info.source_type == SourceType.UNKNOWN

    def test_default_authority_score(self):
        """SourceInfo should default to 0.5 authority."""
        info = SourceInfo(url="http://example.com")
        assert info.authority_score == 0.5

    def test_custom_values(self):
        """SourceInfo should accept custom values."""
        info = SourceInfo(
            url="http://sec.gov/file.html", source_type=SourceType.OFFICIAL, authority_score=0.9
        )
        assert info.source_type == SourceType.OFFICIAL
        assert info.authority_score == 0.9


class TestConfidenceFactors:
    """Tests for ConfidenceFactors dataclass."""

    def test_default_values(self):
        """ConfidenceFactors should have sensible defaults."""
        factors = ConfidenceFactors()
        assert factors.source_count == 1
        assert factors.source_agreement == 1.0
        assert factors.source_authority == 0.5
        assert factors.recency == 1.0
        assert factors.specificity == 0.5
        assert factors.language_certainty == 0.5

    def test_custom_values(self):
        """ConfidenceFactors should accept custom values."""
        factors = ConfidenceFactors(
            source_count=5,
            source_agreement=0.8,
            source_authority=0.9,
            recency=0.7,
            specificity=0.6,
            language_certainty=0.4,
        )
        assert factors.source_count == 5
        assert factors.source_agreement == 0.8


class TestScoredFact:
    """Tests for ScoredFact dataclass."""

    @pytest.fixture
    def sample_factors(self):
        """Create sample factors for tests."""
        return ConfidenceFactors()

    def test_required_fields(self, sample_factors):
        """ScoredFact should require claim, confidence, level, factors."""
        fact = ScoredFact(
            claim="Test claim",
            confidence=0.75,
            confidence_level=ConfidenceLevel.HIGH,
            factors=sample_factors,
        )
        assert fact.claim == "Test claim"
        assert fact.confidence == 0.75
        assert fact.confidence_level == ConfidenceLevel.HIGH

    def test_default_sources(self, sample_factors):
        """ScoredFact should default to empty sources list."""
        fact = ScoredFact(
            claim="Test",
            confidence=0.5,
            confidence_level=ConfidenceLevel.MEDIUM,
            factors=sample_factors,
        )
        assert fact.sources == []

    def test_default_explanation(self, sample_factors):
        """ScoredFact should default to empty explanation."""
        fact = ScoredFact(
            claim="Test",
            confidence=0.5,
            confidence_level=ConfidenceLevel.MEDIUM,
            factors=sample_factors,
        )
        assert fact.explanation == ""

    def test_to_dict(self, sample_factors):
        """ScoredFact to_dict should return correct structure."""
        fact = ScoredFact(
            claim="Test claim",
            confidence=0.75,
            confidence_level=ConfidenceLevel.HIGH,
            factors=sample_factors,
        )
        result = fact.to_dict()
        assert result["claim"] == "Test claim"
        assert result["confidence"] == 0.75
        assert result["level"] == "high"


class TestConfidenceScorer:
    """Tests for ConfidenceScorer class."""

    @pytest.fixture
    def scorer(self):
        """Create default scorer."""
        return ConfidenceScorer()

    def test_default_weights(self, scorer):
        """ConfidenceScorer should have default weights."""
        assert "source_count" in scorer.weights
        assert "source_agreement" in scorer.weights
        assert "source_authority" in scorer.weights
        assert "recency" in scorer.weights
        assert "specificity" in scorer.weights
        assert "language_certainty" in scorer.weights

    def test_custom_weights(self):
        """ConfidenceScorer should accept custom weights."""
        custom_weights = {
            "source_count": 0.5,
            "source_agreement": 0.5,
            "source_authority": 0,
            "recency": 0,
            "specificity": 0,
            "language_certainty": 0,
        }
        scorer = ConfidenceScorer(weights=custom_weights)
        assert scorer.weights["source_count"] == 0.5

    def test_score_fact_returns_scored_fact(self, scorer):
        """score_fact should return ScoredFact."""
        result = scorer.score_fact("Test claim")
        assert isinstance(result, ScoredFact)

    def test_score_fact_with_claim(self, scorer):
        """score_fact should store claim."""
        result = scorer.score_fact("Company reported $1B revenue in 2024")
        assert result.claim == "Company reported $1B revenue in 2024"

    def test_score_fact_confidence_bounded(self, scorer):
        """score_fact confidence should be 0-1."""
        result = scorer.score_fact("Test claim", [{"url": "http://sec.gov"}] * 10)
        assert 0 <= result.confidence <= 1

    def test_score_fact_with_official_source(self, scorer):
        """score_fact should give higher confidence for official sources."""
        official_result = scorer.score_fact("Test claim", [{"url": "http://sec.gov/filing"}])
        unknown_result = scorer.score_fact("Test claim", [{"url": "http://randomsite.com"}])
        assert official_result.confidence >= unknown_result.confidence

    def test_score_fact_with_news_source(self, scorer):
        """score_fact should recognize news sources."""
        news_result = scorer.score_fact("Test claim", [{"url": "http://reuters.com/article"}])
        assert news_result.confidence > 0

    def test_score_fact_multiple_sources_increase_confidence(self, scorer):
        """score_fact with more sources should have higher confidence."""
        single = scorer.score_fact("Test", [{"url": "http://test.com"}])
        multiple = scorer.score_fact(
            "Test",
            [{"url": "http://test1.com"}, {"url": "http://test2.com"}, {"url": "http://test3.com"}],
        )
        assert multiple.confidence >= single.confidence

    def test_score_fact_with_numbers_more_specific(self, scorer):
        """score_fact with numbers should be more specific."""
        with_numbers = scorer.score_fact("Revenue was $5.2 billion")
        without_numbers = scorer.score_fact("Revenue was significant")
        # Numbers increase specificity factor
        assert with_numbers.factors.specificity > without_numbers.factors.specificity

    def test_score_fact_with_dates_more_specific(self, scorer):
        """score_fact with dates should be more specific."""
        with_date = scorer.score_fact("Announced in 2024")
        without_date = scorer.score_fact("Announced recently")
        assert with_date.factors.specificity >= without_date.factors.specificity

    def test_score_fact_hedging_reduces_certainty(self, scorer):
        """score_fact with hedging words should have lower certainty."""
        confident = scorer.score_fact("The company confirmed new product")
        hedging = scorer.score_fact("The company might possibly release")
        assert confident.factors.language_certainty >= hedging.factors.language_certainty

    def test_score_fact_confident_words_increase_certainty(self, scorer):
        """score_fact with confident words should have higher certainty."""
        confident = scorer.score_fact("The company officially announced")
        neutral = scorer.score_fact("The company said something")
        assert confident.factors.language_certainty >= neutral.factors.language_certainty


class TestConfidenceClassification:
    """Tests for confidence level classification."""

    @pytest.fixture
    def scorer(self):
        """Create default scorer."""
        return ConfidenceScorer()

    def test_classify_very_high(self, scorer):
        """Scores >= 0.85 should be VERY_HIGH."""
        level = scorer._classify_confidence(0.90)
        assert level == ConfidenceLevel.VERY_HIGH

    def test_classify_high(self, scorer):
        """Scores 0.7-0.85 should be HIGH."""
        level = scorer._classify_confidence(0.75)
        assert level == ConfidenceLevel.HIGH

    def test_classify_medium(self, scorer):
        """Scores 0.5-0.7 should be MEDIUM."""
        level = scorer._classify_confidence(0.60)
        assert level == ConfidenceLevel.MEDIUM

    def test_classify_low(self, scorer):
        """Scores 0.3-0.5 should be LOW."""
        level = scorer._classify_confidence(0.40)
        assert level == ConfidenceLevel.LOW

    def test_classify_very_low(self, scorer):
        """Scores < 0.3 should be VERY_LOW."""
        level = scorer._classify_confidence(0.20)
        assert level == ConfidenceLevel.VERY_LOW

    def test_classify_boundary_085(self, scorer):
        """Score of exactly 0.85 should be VERY_HIGH."""
        level = scorer._classify_confidence(0.85)
        assert level == ConfidenceLevel.VERY_HIGH

    def test_classify_boundary_070(self, scorer):
        """Score of exactly 0.70 should be HIGH."""
        level = scorer._classify_confidence(0.70)
        assert level == ConfidenceLevel.HIGH

    def test_classify_boundary_050(self, scorer):
        """Score of exactly 0.50 should be MEDIUM."""
        level = scorer._classify_confidence(0.50)
        assert level == ConfidenceLevel.MEDIUM

    def test_classify_boundary_030(self, scorer):
        """Score of exactly 0.30 should be LOW."""
        level = scorer._classify_confidence(0.30)
        assert level == ConfidenceLevel.LOW


class TestSourceParsing:
    """Tests for source parsing."""

    @pytest.fixture
    def scorer(self):
        """Create default scorer."""
        return ConfidenceScorer()

    def test_parse_official_gov(self, scorer):
        """_parse_source should identify .gov as official."""
        info = scorer._parse_source({"url": "http://sec.gov/filing"})
        assert info.source_type == SourceType.OFFICIAL
        assert info.authority_score == 0.8

    def test_parse_news_reuters(self, scorer):
        """_parse_source should identify reuters as news."""
        info = scorer._parse_source({"url": "http://reuters.com/article"})
        assert info.source_type == SourceType.NEWS
        assert info.authority_score == 0.6

    def test_parse_news_bloomberg(self, scorer):
        """_parse_source should identify bloomberg as news."""
        info = scorer._parse_source({"url": "http://bloomberg.com/news"})
        assert info.source_type == SourceType.NEWS

    def test_parse_unknown(self, scorer):
        """_parse_source should default to unknown."""
        info = scorer._parse_source({"url": "http://randomsite.com"})
        assert info.source_type == SourceType.UNKNOWN
        assert info.authority_score == 0.4

    def test_parse_empty_url(self, scorer):
        """_parse_source should handle empty url."""
        info = scorer._parse_source({})
        assert info.url == ""
        assert info.source_type == SourceType.UNKNOWN


class TestCalculateAuthority:
    """Tests for authority calculation."""

    @pytest.fixture
    def scorer(self):
        """Create default scorer."""
        return ConfidenceScorer()

    def test_empty_sources(self, scorer):
        """_calculate_authority with no sources returns 0.3."""
        authority = scorer._calculate_authority([])
        assert authority == 0.3

    def test_single_source(self, scorer):
        """_calculate_authority with single source returns its score."""
        sources = [SourceInfo(url="http://test.com", authority_score=0.8)]
        authority = scorer._calculate_authority(sources)
        assert authority == 0.8

    def test_multiple_sources_average(self, scorer):
        """_calculate_authority averages multiple sources."""
        sources = [
            SourceInfo(url="http://test1.com", authority_score=0.8),
            SourceInfo(url="http://test2.com", authority_score=0.4),
        ]
        authority = scorer._calculate_authority(sources)
        assert authority == pytest.approx(0.6)


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_score_facts(self):
        """score_facts should score list of facts."""
        facts = [{"claim": "First claim", "sources": []}, {"claim": "Second claim", "sources": []}]
        results = score_facts(facts)
        assert len(results) == 2
        assert all(isinstance(r, ScoredFact) for r in results)

    def test_score_facts_empty(self):
        """score_facts with empty list returns empty."""
        results = score_facts([])
        assert results == []

    def test_create_confidence_scorer(self):
        """create_confidence_scorer should create scorer."""
        scorer = create_confidence_scorer()
        assert isinstance(scorer, ConfidenceScorer)

    def test_create_confidence_scorer_with_weights(self):
        """create_confidence_scorer should accept custom weights."""
        custom_weights = {
            "source_count": 1.0,
            "source_agreement": 0,
            "source_authority": 0,
            "recency": 0,
            "specificity": 0,
            "language_certainty": 0,
        }
        scorer = create_confidence_scorer(weights=custom_weights)
        assert scorer.weights["source_count"] == 1.0


class TestSpecificityCalculation:
    """Tests for specificity calculation."""

    @pytest.fixture
    def scorer(self):
        """Create default scorer."""
        return ConfidenceScorer()

    def test_no_numbers_base_specificity(self, scorer):
        """Claim without numbers has base specificity."""
        specificity = scorer._calculate_specificity("Generic claim about company")
        assert specificity == 0.3

    def test_with_numbers_increased_specificity(self, scorer):
        """Claim with numbers has increased specificity."""
        specificity = scorer._calculate_specificity("Revenue was 5 billion")
        assert specificity == pytest.approx(0.6)  # 0.3 + 0.3 for numbers

    def test_with_year_highest_specificity(self, scorer):
        """Claim with year has highest specificity."""
        specificity = scorer._calculate_specificity("Announced in 2024")
        assert specificity == pytest.approx(1.0)  # 0.3 + 0.3 + 0.4
