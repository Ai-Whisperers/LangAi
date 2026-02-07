"""AI-powered sentiment analyzer using LLM."""

from typing import Any, Dict, List, Optional

from ...llm.response_parser import parse_json_response
from ..base import AIComponent
from ..fallback import FallbackHandler
from ..utils import get_logger, normalize_confidence, truncate_text
from .models import (
    EntitySentiment,
    NewsCategorization,
    NewsCategory,
    SearchResultSentimentProfile,
    SentimentAggregation,
    SentimentAnalysisResult,
    SentimentLevel,
)
from .prompts import (
    CATEGORIZATION_SYSTEM_PROMPT,
    NEWS_CATEGORIZATION_PROMPT,
    SENTIMENT_ANALYSIS_PROMPT,
    SENTIMENT_SYSTEM_PROMPT,
)

logger = get_logger(__name__)


class AISentimentAnalyzer(AIComponent[SentimentAnalysisResult]):
    """
    AI-driven sentiment analysis replacing keyword-based approach.

    Uses LLM to understand context, handle negations, and provide
    entity-aware sentiment analysis.

    Example:
        analyzer = get_sentiment_analyzer()
        result = analyzer.analyze_sentiment(
            article_text="Tesla reported record earnings...",
            company_name="Tesla"
        )
        print(result.overall_sentiment)  # SentimentLevel.POSITIVE
        print(result.target_company_sentiment)  # Sentiment specifically about Tesla
    """

    component_name = "sentiment"
    default_task_type = "classification"
    default_complexity = "medium"

    def __init__(self):
        super().__init__()
        self._fallback_handler = FallbackHandler("sentiment")

    def analyze_sentiment(
        self,
        article_text: str,
        company_name: str,
        include_entities: bool = True,
        max_text_length: int = 8000,
    ) -> SentimentAnalysisResult:
        """
        Analyze sentiment of an article using LLM.

        Args:
            article_text: The article text to analyze
            company_name: The target company name
            include_entities: Whether to include entity-level sentiment
            max_text_length: Maximum text length to send to LLM

        Returns:
            SentimentAnalysisResult with overall and entity sentiments
        """
        # Truncate text if needed
        text = truncate_text(article_text, max_text_length)

        prompt = SENTIMENT_ANALYSIS_PROMPT.format(company_name=company_name, article_text=text)

        try:
            result = self._call_llm(
                prompt=prompt,
                task_type="classification",
                complexity="medium",
                system=SENTIMENT_SYSTEM_PROMPT,
                json_mode=True,
            )

            parsed = parse_json_response(result, default={})
            return self._parse_sentiment_result(parsed, company_name)

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            # Return neutral sentiment on failure
            return SentimentAnalysisResult(
                overall_sentiment=SentimentLevel.NEUTRAL,
                overall_score=0.0,
                overall_confidence=0.0,
                summary=f"Analysis failed: {str(e)}",
            )

    def categorize_news(self, article_text: str, company_name: str) -> NewsCategorization:
        """
        Categorize a news article using LLM.

        Args:
            article_text: The article text
            company_name: The target company

        Returns:
            NewsCategorization with category and relevance
        """
        text = truncate_text(article_text, 4000)

        prompt = NEWS_CATEGORIZATION_PROMPT.format(company_name=company_name, article_text=text)

        try:
            result = self._call_llm(
                prompt=prompt,
                task_type="classification",
                complexity="low",
                system=CATEGORIZATION_SYSTEM_PROMPT,
                json_mode=True,
            )

            parsed = parse_json_response(result, default={})
            return self._parse_categorization_result(parsed)

        except Exception as e:
            logger.error(f"News categorization failed: {e}")
            return NewsCategorization(
                primary_category=NewsCategory.GENERAL,
                relevance_to_company=0.5,
                is_about_target_company=False,
            )

    def analyze_batch(
        self, articles: List[Dict[str, Any]], company_name: str, max_articles: int = 20
    ) -> List[SentimentAnalysisResult]:
        """
        Analyze multiple articles efficiently.

        Args:
            articles: List of article dicts with 'content' or 'snippet' keys
            company_name: The target company
            max_articles: Maximum articles to analyze

        Returns:
            List of SentimentAnalysisResult
        """
        results = []
        for article in articles[:max_articles]:
            text = article.get("content") or article.get("snippet") or ""
            if text:
                result = self.analyze_sentiment(text, company_name)
                results.append(result)

        return results

    def aggregate_sentiment(self, results: List[SentimentAnalysisResult]) -> SentimentAggregation:
        """
        Aggregate sentiment across multiple articles.

        Args:
            results: List of individual sentiment results

        Returns:
            SentimentAggregation with overall sentiment and distribution
        """
        if not results:
            return SentimentAggregation(
                overall_sentiment=SentimentLevel.NEUTRAL,
                overall_score=0.0,
                confidence=0.0,
                article_count=0,
                positive_ratio=0.0,
                negative_ratio=0.0,
                neutral_ratio=1.0,
            )

        # Calculate weighted average score
        total_weight = 0.0
        weighted_sum = 0.0
        sentiment_counts = {level.value: 0 for level in SentimentLevel}
        all_positive_factors = []
        all_negative_factors = []
        category_counts = {}

        for r in results:
            weight = r.overall_confidence
            weighted_sum += r.overall_score * weight
            total_weight += weight

            # Count sentiments
            sentiment_key = (
                r.overall_sentiment.value
                if isinstance(r.overall_sentiment, SentimentLevel)
                else r.overall_sentiment
            )
            sentiment_counts[sentiment_key] = sentiment_counts.get(sentiment_key, 0) + 1

            # Collect factors
            for factor in r.key_factors:
                if r.overall_score > 0:
                    all_positive_factors.append(factor)
                elif r.overall_score < 0:
                    all_negative_factors.append(factor)

            # Count categories
            cat = (
                r.news_category.value
                if isinstance(r.news_category, NewsCategory)
                else r.news_category
            )
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # Calculate overall
        avg_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        overall_sentiment = SentimentLevel.from_score(avg_score)

        # Calculate ratios
        n = len(results)
        positive_count = sentiment_counts.get("very_positive", 0) + sentiment_counts.get(
            "positive", 0
        )
        negative_count = sentiment_counts.get("very_negative", 0) + sentiment_counts.get(
            "negative", 0
        )
        neutral_count = sentiment_counts.get("neutral", 0)

        # Get top factors (deduplicated)
        top_positive = list(dict.fromkeys(all_positive_factors))[:5]
        top_negative = list(dict.fromkeys(all_negative_factors))[:5]

        # Get top categories
        sorted_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        top_categories = [NewsCategory(cat) for cat, _ in sorted_cats[:3]]

        return SentimentAggregation(
            overall_sentiment=overall_sentiment,
            overall_score=avg_score,
            confidence=total_weight / n if n > 0 else 0.0,
            article_count=n,
            sentiment_distribution=sentiment_counts,
            positive_ratio=positive_count / n if n > 0 else 0.0,
            negative_ratio=negative_count / n if n > 0 else 0.0,
            neutral_ratio=neutral_count / n if n > 0 else 0.0,
            top_positive_factors=top_positive,
            top_negative_factors=top_negative,
            top_categories=top_categories,
        )

    def analyze_from_search_results(
        self, company_name: str, search_results: List[Dict[str, Any]], max_articles: int = 20
    ) -> SearchResultSentimentProfile:
        """
        Analyze sentiment from search results and return a high-level profile.

        This is a convenience method that combines analyze_batch and aggregate_sentiment
        to produce a SearchResultSentimentProfile suitable for workflow integration.

        Args:
            company_name: The target company name
            search_results: List of search result dicts with 'content', 'snippet', or 'title' keys
            max_articles: Maximum articles to analyze

        Returns:
            SearchResultSentimentProfile with overall sentiment analysis
        """
        if not search_results:
            return SearchResultSentimentProfile.empty(company_name)

        # Analyze batch of articles
        results = self.analyze_batch(search_results, company_name, max_articles)

        if not results:
            return SearchResultSentimentProfile.empty(company_name)

        # Aggregate results
        aggregation = self.aggregate_sentiment(results)

        # Extract key topics from categorization
        key_topics = []
        for r in results:
            if r.news_category and r.news_category != NewsCategory.GENERAL:
                cat_name = (
                    r.news_category.value
                    if isinstance(r.news_category, NewsCategory)
                    else str(r.news_category)
                )
                if cat_name not in key_topics:
                    key_topics.append(cat_name)
            # Also extract from key factors
            for factor in r.key_factors[:2]:  # Limit to avoid too many
                if factor and factor not in key_topics:
                    key_topics.append(factor)
        key_topics = key_topics[:10]  # Limit total topics

        # Build category breakdown from aggregation
        category_breakdown = {}
        for cat in aggregation.top_categories:
            cat_name = cat.value if isinstance(cat, NewsCategory) else str(cat)
            category_breakdown[cat_name] = category_breakdown.get(cat_name, 0) + 1

        # Also count from individual results for more accurate breakdown
        for r in results:
            cat = r.news_category
            cat_name = cat.value if isinstance(cat, NewsCategory) else str(cat)
            category_breakdown[cat_name] = category_breakdown.get(cat_name, 0) + 1

        # Create profile from aggregation
        return SearchResultSentimentProfile(
            company_name=company_name,
            total_articles=aggregation.article_count,
            sentiment_score=aggregation.overall_score,
            sentiment_level=aggregation.overall_sentiment,
            sentiment_trend=(
                "improving"
                if aggregation.positive_ratio > aggregation.negative_ratio + 0.2
                else (
                    "declining"
                    if aggregation.negative_ratio > aggregation.positive_ratio + 0.2
                    else "stable"
                )
            ),
            key_topics=key_topics,
            positive_highlights=aggregation.top_positive_factors,
            negative_highlights=aggregation.top_negative_factors,
            category_breakdown=category_breakdown,
            confidence=aggregation.confidence,
        )

    def _parse_sentiment_result(
        self, data: Dict[str, Any], company_name: str
    ) -> SentimentAnalysisResult:
        """Parse LLM response into SentimentAnalysisResult."""
        # Parse overall sentiment
        overall_sentiment = data.get("overall_sentiment", "neutral")
        if isinstance(overall_sentiment, str):
            try:
                overall_sentiment = SentimentLevel(overall_sentiment)
            except ValueError:
                overall_sentiment = SentimentLevel.NEUTRAL

        # Parse entity sentiments
        entity_sentiments = []
        for entity_data in data.get("entity_sentiments", []):
            try:
                sentiment = entity_data.get("sentiment", "neutral")
                if isinstance(sentiment, str):
                    sentiment = SentimentLevel(sentiment)

                entity = EntitySentiment(
                    entity_name=entity_data.get("entity_name", "Unknown"),
                    entity_type=entity_data.get("entity_type", "company"),
                    sentiment=sentiment,
                    confidence=normalize_confidence(entity_data.get("confidence", 0.5)),
                    reasoning=entity_data.get("reasoning", ""),
                    context_snippet=entity_data.get("context_snippet", ""),
                    is_target_company=entity_data.get("is_target_company", False),
                )
                entity_sentiments.append(entity)
            except Exception as e:
                logger.warning(f"Failed to parse entity sentiment: {e}")

        # Parse target company sentiment
        target_sentiment = data.get("target_company_sentiment")
        if target_sentiment and isinstance(target_sentiment, str):
            try:
                target_sentiment = SentimentLevel(target_sentiment)
            except ValueError:
                target_sentiment = None

        # Parse news category
        news_category = data.get("news_category", "general")
        if isinstance(news_category, str):
            try:
                news_category = NewsCategory(news_category)
            except ValueError:
                news_category = NewsCategory.GENERAL

        # Parse secondary categories
        secondary = []
        for cat in data.get("secondary_categories", []):
            try:
                secondary.append(NewsCategory(cat))
            except ValueError:
                pass

        return SentimentAnalysisResult(
            overall_sentiment=overall_sentiment,
            overall_score=float(data.get("overall_score", 0.0)),
            overall_confidence=normalize_confidence(data.get("overall_confidence", 0.5)),
            entity_sentiments=entity_sentiments,
            target_company_sentiment=target_sentiment,
            target_company_confidence=normalize_confidence(
                data.get("target_company_confidence", 0.0)
            ),
            key_factors=data.get("key_factors", []),
            detected_language=data.get("detected_language", "en"),
            has_negations=data.get("has_negations", False),
            has_uncertainty=data.get("has_uncertainty", False),
            has_sarcasm=data.get("has_sarcasm", False),
            news_category=news_category,
            secondary_categories=secondary,
            summary=data.get("summary", ""),
        )

    def _parse_categorization_result(self, data: Dict[str, Any]) -> NewsCategorization:
        """Parse LLM response into NewsCategorization."""
        primary = data.get("primary_category", "general")
        try:
            primary = NewsCategory(primary)
        except ValueError:
            primary = NewsCategory.GENERAL

        secondary = []
        for cat in data.get("secondary_categories", []):
            try:
                secondary.append(NewsCategory(cat))
            except ValueError:
                pass

        return NewsCategorization(
            primary_category=primary,
            secondary_categories=secondary,
            relevance_to_company=normalize_confidence(data.get("relevance_to_company", 0.5)),
            is_about_target_company=data.get("is_about_target_company", False),
            mentioned_companies=data.get("mentioned_companies", []),
            topic_keywords=data.get("topic_keywords", []),
        )

    def process(self, article_text: str, company_name: str) -> SentimentAnalysisResult:
        """Main processing method (implements AIComponent interface)."""
        return self.analyze_sentiment(article_text, company_name)


# Singleton instance
_analyzer_instance: Optional[AISentimentAnalyzer] = None


def get_sentiment_analyzer() -> AISentimentAnalyzer:
    """Get singleton sentiment analyzer instance."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = AISentimentAnalyzer()
    return _analyzer_instance
