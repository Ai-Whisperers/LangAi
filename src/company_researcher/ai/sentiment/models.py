"""Pydantic models for AI sentiment analysis."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


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
            self.VERY_NEGATIVE: -0.8
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
    is_target_company: bool = Field(default=False, description="Is this the company being researched?")

    model_config = {"use_enum_values": True}


class SentimentAnalysisResult(BaseModel):
    """Complete sentiment analysis result for an article."""

    # Overall sentiment
    overall_sentiment: SentimentLevel = Field(description="Overall sentiment of the article")
    overall_score: float = Field(ge=-1.0, le=1.0, description="Numeric sentiment score")
    overall_confidence: float = Field(ge=0.0, le=1.0, description="Confidence in overall assessment")

    # Entity-specific sentiments
    entity_sentiments: List[EntitySentiment] = Field(
        default_factory=list,
        description="Sentiment for each entity mentioned"
    )

    # Target company sentiment (convenience field)
    target_company_sentiment: Optional[SentimentLevel] = Field(
        default=None,
        description="Sentiment specifically about the target company"
    )
    target_company_confidence: float = Field(
        default=0.0,
        description="Confidence in target company sentiment"
    )

    # Analysis details
    key_factors: List[str] = Field(
        default_factory=list,
        description="Main factors driving the sentiment"
    )
    detected_language: str = Field(default="en", description="Detected language of the text")

    # Linguistic analysis
    has_negations: bool = Field(default=False, description="Whether negations were detected")
    has_uncertainty: bool = Field(default=False, description="Whether uncertainty language was detected")
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
        default_factory=list,
        description="Secondary categories"
    )
    relevance_to_company: float = Field(
        ge=0.0, le=1.0,
        description="How relevant this article is to the target company"
    )
    is_about_target_company: bool = Field(
        description="Whether the article is primarily about the target company"
    )
    mentioned_companies: List[str] = Field(
        default_factory=list,
        description="All companies mentioned in the article"
    )
    topic_keywords: List[str] = Field(
        default_factory=list,
        description="Key topics/themes in the article"
    )

    model_config = {"use_enum_values": True}


class SentimentAggregation(BaseModel):
    """Aggregated sentiment across multiple articles."""

    overall_sentiment: SentimentLevel
    overall_score: float = Field(ge=-1.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)

    article_count: int
    sentiment_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of articles per sentiment level"
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
