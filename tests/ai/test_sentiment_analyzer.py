"""Tests for AI sentiment analyzer."""
import pytest
from unittest.mock import MagicMock, patch
import json

from company_researcher.ai.sentiment import (
    AISentimentAnalyzer,
    get_sentiment_analyzer,
    SentimentLevel,
    SentimentAnalysisResult,
    NewsCategory,
)


class TestSentimentModels:
    """Test sentiment models."""

    def test_sentiment_level_from_score_very_positive(self):
        """Test converting very positive score to sentiment level."""
        assert SentimentLevel.from_score(0.8) == SentimentLevel.VERY_POSITIVE
        assert SentimentLevel.from_score(0.9) == SentimentLevel.VERY_POSITIVE
        assert SentimentLevel.from_score(1.0) == SentimentLevel.VERY_POSITIVE

    def test_sentiment_level_from_score_positive(self):
        """Test converting positive score to sentiment level."""
        assert SentimentLevel.from_score(0.4) == SentimentLevel.POSITIVE
        assert SentimentLevel.from_score(0.5) == SentimentLevel.POSITIVE
        assert SentimentLevel.from_score(0.2) == SentimentLevel.POSITIVE

    def test_sentiment_level_from_score_neutral(self):
        """Test converting neutral scores to sentiment level."""
        assert SentimentLevel.from_score(0.0) == SentimentLevel.NEUTRAL
        assert SentimentLevel.from_score(0.1) == SentimentLevel.NEUTRAL
        assert SentimentLevel.from_score(-0.1) == SentimentLevel.NEUTRAL

    def test_sentiment_level_from_score_negative(self):
        """Test converting negative scores to sentiment level."""
        assert SentimentLevel.from_score(-0.4) == SentimentLevel.NEGATIVE
        assert SentimentLevel.from_score(-0.5) == SentimentLevel.NEGATIVE

    def test_sentiment_level_from_score_very_negative(self):
        """Test converting very negative scores to sentiment level."""
        assert SentimentLevel.from_score(-0.8) == SentimentLevel.VERY_NEGATIVE
        assert SentimentLevel.from_score(-1.0) == SentimentLevel.VERY_NEGATIVE

    def test_sentiment_level_to_score(self):
        """Test converting sentiment levels to scores."""
        assert SentimentLevel.VERY_POSITIVE.to_score() == 0.8
        assert SentimentLevel.POSITIVE.to_score() == 0.4
        assert SentimentLevel.NEUTRAL.to_score() == 0.0
        assert SentimentLevel.NEGATIVE.to_score() == -0.4
        assert SentimentLevel.VERY_NEGATIVE.to_score() == -0.8

    def test_sentiment_analysis_result_get_target_sentiment(self):
        """Test getting target sentiment with fallback."""
        # With target sentiment set
        result = SentimentAnalysisResult(
            overall_sentiment=SentimentLevel.NEUTRAL,
            overall_score=0.0,
            overall_confidence=0.8,
            target_company_sentiment=SentimentLevel.POSITIVE
        )
        assert result.get_target_sentiment() == SentimentLevel.POSITIVE

        # Without target sentiment (fallback to overall)
        result2 = SentimentAnalysisResult(
            overall_sentiment=SentimentLevel.NEGATIVE,
            overall_score=-0.4,
            overall_confidence=0.8,
            target_company_sentiment=None
        )
        assert result2.get_target_sentiment() == SentimentLevel.NEGATIVE


class TestAISentimentAnalyzer:
    """Test AI sentiment analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return AISentimentAnalyzer()

    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response for sentiment analysis."""
        return json.dumps({
            "overall_sentiment": "positive",
            "overall_score": 0.6,
            "overall_confidence": 0.85,
            "entity_sentiments": [
                {
                    "entity_name": "Tesla",
                    "entity_type": "company",
                    "sentiment": "positive",
                    "confidence": 0.9,
                    "reasoning": "Record earnings reported",
                    "context_snippet": "Tesla reported record earnings",
                    "is_target_company": True
                },
                {
                    "entity_name": "BYD",
                    "entity_type": "company",
                    "sentiment": "negative",
                    "confidence": 0.7,
                    "reasoning": "Sales declined",
                    "context_snippet": "BYD reported declining sales",
                    "is_target_company": False
                }
            ],
            "target_company_sentiment": "positive",
            "target_company_confidence": 0.9,
            "key_factors": ["record earnings", "market leadership"],
            "detected_language": "en",
            "has_negations": False,
            "has_uncertainty": False,
            "has_sarcasm": False,
            "news_category": "financial",
            "secondary_categories": ["market"],
            "summary": "Tesla reported record earnings, maintaining market leadership."
        })

    def test_analyze_sentiment_success(self, analyzer, mock_llm_response):
        """Test successful sentiment analysis."""
        # Use MagicMock explicitly to avoid AsyncMock auto-detection
        mock_call = MagicMock(return_value=mock_llm_response)
        with patch.object(analyzer, '_call_llm', mock_call):
            result = analyzer.analyze_sentiment(
                article_text="Tesla reported record earnings...",
                company_name="Tesla"
            )

            assert result.overall_sentiment == SentimentLevel.POSITIVE
            assert result.overall_score == 0.6
            assert result.overall_confidence == 0.85
            assert len(result.entity_sentiments) == 2
            assert result.target_company_sentiment == SentimentLevel.POSITIVE
            assert result.news_category == NewsCategory.FINANCIAL

    def test_analyze_sentiment_handles_failure(self, analyzer):
        """Test sentiment analysis handles LLM failure gracefully."""
        with patch.object(analyzer, '_call_llm') as mock_call:
            mock_call.side_effect = Exception("LLM error")

            result = analyzer.analyze_sentiment(
                article_text="Some article",
                company_name="Tesla"
            )

            # Should return neutral on failure
            assert result.overall_sentiment == SentimentLevel.NEUTRAL
            assert result.overall_confidence == 0.0

    def test_entity_sentiment_distinguishes_companies(self, analyzer, mock_llm_response):
        """Test that entity sentiment correctly distinguishes between companies."""
        # Use MagicMock explicitly to avoid AsyncMock auto-detection
        mock_call = MagicMock(return_value=mock_llm_response)
        with patch.object(analyzer, '_call_llm', mock_call):
            result = analyzer.analyze_sentiment(
                article_text="Tesla beat earnings while BYD sales declined",
                company_name="Tesla"
            )

            # Find Tesla and BYD sentiments
            tesla_sentiment = next(
                (e for e in result.entity_sentiments if e.entity_name == "Tesla"),
                None
            )
            byd_sentiment = next(
                (e for e in result.entity_sentiments if e.entity_name == "BYD"),
                None
            )

            assert tesla_sentiment is not None
            assert byd_sentiment is not None
            assert tesla_sentiment.sentiment == SentimentLevel.POSITIVE
            assert byd_sentiment.sentiment == SentimentLevel.NEGATIVE
            assert tesla_sentiment.is_target_company is True
            assert byd_sentiment.is_target_company is False

    def test_aggregate_sentiment(self, analyzer):
        """Test sentiment aggregation."""
        results = [
            SentimentAnalysisResult(
                overall_sentiment=SentimentLevel.POSITIVE,
                overall_score=0.6,
                overall_confidence=0.8,
                key_factors=["growth"],
                news_category=NewsCategory.FINANCIAL
            ),
            SentimentAnalysisResult(
                overall_sentiment=SentimentLevel.VERY_POSITIVE,
                overall_score=0.9,
                overall_confidence=0.9,
                key_factors=["record sales"],
                news_category=NewsCategory.FINANCIAL
            ),
            SentimentAnalysisResult(
                overall_sentiment=SentimentLevel.NEUTRAL,
                overall_score=0.0,
                overall_confidence=0.7,
                key_factors=[],
                news_category=NewsCategory.GENERAL
            )
        ]

        aggregation = analyzer.aggregate_sentiment(results)

        assert aggregation.article_count == 3
        assert aggregation.overall_score > 0  # Should be positive overall
        assert aggregation.positive_ratio > 0.5
        assert "growth" in aggregation.top_positive_factors or "record sales" in aggregation.top_positive_factors

    def test_aggregate_empty_results(self, analyzer):
        """Test aggregation with no results."""
        aggregation = analyzer.aggregate_sentiment([])

        assert aggregation.article_count == 0
        assert aggregation.overall_sentiment == SentimentLevel.NEUTRAL
        assert aggregation.confidence == 0.0

    def test_parse_sentiment_result_with_missing_fields(self, analyzer):
        """Test parsing handles missing fields gracefully."""
        minimal_data = {
            "overall_sentiment": "positive",
            "overall_score": 0.5,
            "overall_confidence": 0.7
        }

        result = analyzer._parse_sentiment_result(minimal_data, "TestCorp")

        assert result.overall_sentiment == SentimentLevel.POSITIVE
        assert result.overall_score == 0.5
        assert result.entity_sentiments == []
        assert result.key_factors == []
        assert result.news_category == NewsCategory.GENERAL

    def test_parse_sentiment_result_invalid_sentiment_level(self, analyzer):
        """Test parsing handles invalid sentiment level."""
        invalid_data = {
            "overall_sentiment": "super_duper_positive",  # Invalid
            "overall_score": 0.5,
            "overall_confidence": 0.7
        }

        result = analyzer._parse_sentiment_result(invalid_data, "TestCorp")

        # Should fall back to NEUTRAL
        assert result.overall_sentiment == SentimentLevel.NEUTRAL


class TestSentimentAnalyzerSingleton:
    """Test singleton behavior."""

    def test_get_sentiment_analyzer_returns_same_instance(self):
        """Test that get_sentiment_analyzer returns singleton."""
        # Reset singleton for clean test
        import company_researcher.ai.sentiment.analyzer as analyzer_module
        analyzer_module._analyzer_instance = None

        analyzer1 = get_sentiment_analyzer()
        analyzer2 = get_sentiment_analyzer()

        assert analyzer1 is analyzer2


class TestNewsCategorization:
    """Test news categorization functionality."""

    @pytest.fixture
    def analyzer(self):
        return AISentimentAnalyzer()

    @pytest.fixture
    def mock_categorization_response(self):
        return json.dumps({
            "primary_category": "financial",
            "secondary_categories": ["market"],
            "relevance_to_company": 0.9,
            "is_about_target_company": True,
            "mentioned_companies": ["Tesla", "BYD", "Ford"],
            "topic_keywords": ["earnings", "revenue", "Q4"]
        })

    def test_categorize_news_success(self, analyzer, mock_categorization_response):
        """Test successful news categorization."""
        # Use MagicMock explicitly to avoid AsyncMock auto-detection
        mock_call = MagicMock(return_value=mock_categorization_response)
        with patch.object(analyzer, '_call_llm', mock_call):
            result = analyzer.categorize_news(
                article_text="Tesla Q4 earnings beat expectations...",
                company_name="Tesla"
            )

            assert result.primary_category == NewsCategory.FINANCIAL
            assert NewsCategory.MARKET in result.secondary_categories
            assert result.relevance_to_company == 0.9
            assert result.is_about_target_company is True
            assert "Tesla" in result.mentioned_companies

    def test_categorize_news_handles_failure(self, analyzer):
        """Test categorization handles LLM failure gracefully."""
        with patch.object(analyzer, '_call_llm') as mock_call:
            mock_call.side_effect = Exception("LLM error")

            result = analyzer.categorize_news(
                article_text="Some article",
                company_name="Tesla"
            )

            # Should return defaults on failure
            assert result.primary_category == NewsCategory.GENERAL
            assert result.relevance_to_company == 0.5
            assert result.is_about_target_company is False


class TestBatchAnalysis:
    """Test batch analysis functionality."""

    @pytest.fixture
    def analyzer(self):
        return AISentimentAnalyzer()

    def test_analyze_batch_multiple_articles(self, analyzer):
        """Test analyzing multiple articles."""
        mock_response = json.dumps({
            "overall_sentiment": "positive",
            "overall_score": 0.5,
            "overall_confidence": 0.8,
            "entity_sentiments": [],
            "key_factors": [],
            "news_category": "general",
            "summary": "Test summary"
        })

        articles = [
            {"content": "Article 1 content about company..."},
            {"snippet": "Article 2 snippet..."},
            {"content": "Article 3 content..."},
        ]

        with patch.object(analyzer, '_call_llm') as mock_call:
            mock_call.return_value = mock_response

            results = analyzer.analyze_batch(articles, "TestCorp")

            assert len(results) == 3
            assert all(isinstance(r, SentimentAnalysisResult) for r in results)

    def test_analyze_batch_respects_max_articles(self, analyzer):
        """Test batch analysis respects max_articles limit."""
        mock_response = json.dumps({
            "overall_sentiment": "neutral",
            "overall_score": 0.0,
            "overall_confidence": 0.5,
            "entity_sentiments": [],
            "key_factors": [],
            "news_category": "general",
            "summary": "Test"
        })

        articles = [{"content": f"Article {i}"} for i in range(50)]

        with patch.object(analyzer, '_call_llm') as mock_call:
            mock_call.return_value = mock_response

            results = analyzer.analyze_batch(articles, "TestCorp", max_articles=5)

            assert len(results) == 5

    def test_analyze_batch_skips_empty_content(self, analyzer):
        """Test batch analysis skips articles with no content."""
        mock_response = json.dumps({
            "overall_sentiment": "neutral",
            "overall_score": 0.0,
            "overall_confidence": 0.5,
            "entity_sentiments": [],
            "key_factors": [],
            "news_category": "general",
            "summary": "Test"
        })

        articles = [
            {"content": "Valid content"},
            {"content": ""},  # Empty
            {"snippet": ""},  # Empty
            {"other_field": "No content field"},
            {"content": "Another valid"},
        ]

        with patch.object(analyzer, '_call_llm') as mock_call:
            mock_call.return_value = mock_response

            results = analyzer.analyze_batch(articles, "TestCorp")

            # Should only process articles with actual content
            assert len(results) == 2
