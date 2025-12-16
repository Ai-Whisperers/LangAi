"""Pydantic models for AI sentiment analysis."""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SentimentLevel(str, Enum):
    """Sentiment level classification."""

    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

    @classmethod
    def from_score(cls, score: float) -> "SentimentLevel":
        """Convert a -1.0 to 1.0 score to sentiment level."""
        if score >= 0.6:
            return cls.VERY_POSITIVE
        elif score >= 0.2:
            return cls.POSITIVE
        elif score >= -0.2:
            return cls.NEUTRAL
        elif score >= -0.6:
            return cls.NEGATIVE
        else:
            return cls.VERY_NEGATIVE

    def to_score(self) -> float:
        """Convert sentiment level to approximate score."""
        mapping = {
            self.VERY_POSITIVE: 0.8,
            self.POSITIVE: 0.4,
            self.NEUTRAL: 0.0,
            self.NEGATIVE: -0.4,
            self.VERY_NEGATIVE: -0.8,
        }
        return mapping.get(self, 0.0)


class NewsCategory(str, Enum):
    """News article category."""

    FINANCIAL = "financial"
    PRODUCT = "product"
    LEGAL = "legal"
    PARTNERSHIP = "partnership"
    EXECUTIVE = "executive"
    MARKET = "market"
    REGULATORY = "regulatory"
    ESG = "esg"
    TECHNOLOGY = "technology"
    GENERAL = "general"


class EntitySentiment(BaseModel):
    """Sentiment for a specific entity mentioned in text."""

    entity_name: str = Field(description="Name of the entity (company, person, product)")
    entity_type: str = Field(description="Type: company, person, product, brand")
    sentiment: SentimentLevel = Field(description="Sentiment toward this entity")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in this assessment")
    reasoning: str = Field(description="Brief explanation of why this sentiment was assigned")
    context_snippet: str = Field(description="Relevant text excerpt supporting this sentiment")
    is_target_company: bool = Field(
        default=False, description="Is this the company being researched?"
    )

    model_config = {"use_enum_values": True}


class SentimentAnalysisResult(BaseModel):
    """Complete sentiment analysis result for an article."""

    # Overall sentiment
    overall_sentiment: SentimentLevel = Field(description="Overall sentiment of the article")
    overall_score: float = Field(ge=-1.0, le=1.0, description="Numeric sentiment score")
    overall_confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in overall assessment"
    )

    # Entity-specific sentiments
    entity_sentiments: List[EntitySentiment] = Field(
        default_factory=list, description="Sentiment for each entity mentioned"
    )

    # Target company sentiment (convenience field)
    target_company_sentiment: Optional[SentimentLevel] = Field(
        default=None, description="Sentiment specifically about the target company"
    )
    target_company_confidence: float = Field(
        default=0.0, description="Confidence in target company sentiment"
    )

    # Analysis details
    key_factors: List[str] = Field(
        default_factory=list, description="Main factors driving the sentiment"
    )
    detected_language: str = Field(default="en", description="Detected language of the text")

    # Linguistic analysis
    has_negations: bool = Field(default=False, description="Whether negations were detected")
    has_uncertainty: bool = Field(
        default=False, description="Whether uncertainty language was detected"
    )
    has_sarcasm: bool = Field(default=False, description="Whether sarcasm/irony was detected")

    # Categorization
    news_category: NewsCategory = Field(default=NewsCategory.GENERAL)
    secondary_categories: List[NewsCategory] = Field(default_factory=list)

    # Summary
    summary: str = Field(default="", description="One-sentence summary of the article")

    model_config = {"use_enum_values": True}

    def get_target_sentiment(self) -> SentimentLevel:
        """Get sentiment about the target company, falling back to overall."""
        if self.target_company_sentiment:
            return self.target_company_sentiment
        return self.overall_sentiment


class NewsCategorization(BaseModel):
    """News article categorization result."""

    primary_category: NewsCategory = Field(description="Primary category of the news")
    secondary_categories: List[NewsCategory] = Field(
        default_factory=list, description="Secondary categories"
    )
    relevance_to_company: float = Field(
        ge=0.0, le=1.0, description="How relevant this article is to the target company"
    )
    is_about_target_company: bool = Field(
        description="Whether the article is primarily about the target company"
    )
    mentioned_companies: List[str] = Field(
        default_factory=list, description="All companies mentioned in the article"
    )
    topic_keywords: List[str] = Field(
        default_factory=list, description="Key topics/themes in the article"
    )

    model_config = {"use_enum_values": True}


class SentimentAggregation(BaseModel):
    """Aggregated sentiment across multiple articles."""

    overall_sentiment: SentimentLevel
    overall_score: float = Field(ge=-1.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)

    article_count: int
    sentiment_distribution: Dict[str, int] = Field(
        default_factory=dict, description="Count of articles per sentiment level"
    )

    # Trend analysis
    positive_ratio: float = Field(ge=0.0, le=1.0)
    negative_ratio: float = Field(ge=0.0, le=1.0)
    neutral_ratio: float = Field(ge=0.0, le=1.0)

    # Key themes
    top_positive_factors: List[str] = Field(default_factory=list)
    top_negative_factors: List[str] = Field(default_factory=list)
    top_categories: List[NewsCategory] = Field(default_factory=list)

    model_config = {"use_enum_values": True}


class SearchResultSentimentProfile(BaseModel):
    """Sentiment profile from search results analysis.

    This model provides a high-level sentiment profile suitable for
    workflow integration tests and reporting.
    """

    company_name: str = Field(description="Company being analyzed")
    total_articles: int = Field(default=0, description="Number of articles analyzed")
    sentiment_score: float = Field(
        ge=-1.0, le=1.0, default=0.0, description="Overall sentiment score"
    )
    sentiment_level: SentimentLevel = Field(
        default=SentimentLevel.NEUTRAL, description="Overall sentiment level"
    )
    sentiment_trend: str = Field(
        default="stable", description="Trend direction: improving, stable, declining"
    )

    # Topics and highlights
    key_topics: List[str] = Field(default_factory=list, description="Key topics discussed")
    positive_highlights: List[str] = Field(default_factory=list, description="Positive factors")
    negative_highlights: List[str] = Field(
        default_factory=list, description="Negative factors/concerns"
    )

    # Category breakdown
    category_breakdown: Dict[str, int] = Field(
        default_factory=dict, description="Count of articles per category"
    )

    # Additional metadata
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    analysis_timestamp: Optional[str] = Field(default=None)

    # Note: use_enum_values is NOT set to True here because tests expect enum objects
    # for sentiment_level, not string values

    @classmethod
    def from_aggregation(
        cls,
        company_name: str,
        aggregation: "SentimentAggregation",
        key_topics: Optional[List[str]] = None,
    ) -> "SearchResultSentimentProfile":
        """Create profile from SentimentAggregation."""
        # Determine trend based on ratios
        if aggregation.positive_ratio > aggregation.negative_ratio + 0.2:
            trend = "improving"
        elif aggregation.negative_ratio > aggregation.positive_ratio + 0.2:
            trend = "declining"
        else:
            trend = "stable"

        # Convert categories to breakdown
        category_breakdown = {}
        for cat in aggregation.top_categories:
            cat_name = cat.value if hasattr(cat, "value") else str(cat)
            category_breakdown[cat_name] = category_breakdown.get(cat_name, 0) + 1

        return cls(
            company_name=company_name,
            total_articles=aggregation.article_count,
            sentiment_score=aggregation.overall_score,
            sentiment_level=aggregation.overall_sentiment,
            sentiment_trend=trend,
            key_topics=key_topics or [],
            positive_highlights=aggregation.top_positive_factors,
            negative_highlights=aggregation.top_negative_factors,
            category_breakdown=category_breakdown,
            confidence=aggregation.confidence,
        )

    @classmethod
    def empty(cls, company_name: str) -> "SearchResultSentimentProfile":
        """Create empty profile for no results."""
        return cls(
            company_name=company_name,
            total_articles=0,
            sentiment_score=0.0,
            sentiment_level=SentimentLevel.NEUTRAL,
            sentiment_trend="stable",
        )
