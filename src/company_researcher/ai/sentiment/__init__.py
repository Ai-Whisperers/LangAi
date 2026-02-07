"""AI-powered sentiment analysis module."""

from .analyzer import AISentimentAnalyzer, get_sentiment_analyzer
from .models import (
    EntitySentiment,
    NewsCategorization,
    NewsCategory,
    SentimentAggregation,
    SentimentAnalysisResult,
    SentimentLevel,
)

__all__ = [
    # Main class
    "AISentimentAnalyzer",
    "get_sentiment_analyzer",
    # Models
    "SentimentLevel",
    "EntitySentiment",
    "SentimentAnalysisResult",
    "NewsCategorization",
    "NewsCategory",
    "SentimentAggregation",
]
