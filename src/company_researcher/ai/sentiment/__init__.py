"""AI-powered sentiment analysis module."""
from .analyzer import AISentimentAnalyzer, get_sentiment_analyzer
from .models import (
    SentimentLevel,
    EntitySentiment,
    SentimentAnalysisResult,
    NewsCategorization,
    NewsCategory,
    SentimentAggregation
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
