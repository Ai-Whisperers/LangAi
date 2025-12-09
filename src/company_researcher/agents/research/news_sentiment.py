"""
News Sentiment Analyzer - Analyzes news sentiment for companies.

This module provides:
- News article sentiment scoring
- Trend detection in news coverage
- Key topic extraction
- Sentiment aggregation over time periods
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SentimentLevel(Enum):
    """Sentiment classification levels."""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


class NewsCategory(Enum):
    """News article categories."""
    FINANCIAL = "financial"
    PRODUCT = "product"
    LEADERSHIP = "leadership"
    LEGAL = "legal"
    PARTNERSHIP = "partnership"
    EXPANSION = "expansion"
    WORKFORCE = "workforce"
    SUSTAINABILITY = "sustainability"
    COMPETITION = "competition"
    GENERAL = "general"


@dataclass
class NewsArticle:
    """Represents a news article with sentiment analysis."""
    title: str
    source: str
    published_date: datetime
    url: str
    snippet: str
    sentiment_score: float = 0.0  # -1.0 to 1.0
    sentiment_level: SentimentLevel = SentimentLevel.NEUTRAL
    category: NewsCategory = NewsCategory.GENERAL
    relevance_score: float = 0.5  # 0.0 to 1.0
    topics: List[str] = field(default_factory=list)


@dataclass
class NewsSentimentProfile:
    """Aggregated news sentiment profile for a company."""
    company_name: str
    analysis_date: datetime
    total_articles: int
    sentiment_score: float  # Weighted average -1.0 to 1.0
    sentiment_level: SentimentLevel
    articles: List[NewsArticle]
    category_breakdown: Dict[NewsCategory, int]
    sentiment_trend: str  # "improving", "stable", "declining"
    key_topics: List[str]
    positive_highlights: List[str]
    negative_highlights: List[str]
    confidence: float  # 0.0 to 1.0


# Sentiment keywords for basic analysis
POSITIVE_KEYWORDS = [
    # Growth & Performance
    "growth", "profit", "revenue increase", "beat expectations", "outperform",
    "record", "expansion", "success", "milestone", "breakthrough",
    # Innovation
    "innovation", "launch", "new product", "patent", "technology",
    # Leadership
    "strategic", "partnership", "acquisition", "merger", "synergy",
    # Market
    "market leader", "market share", "competitive advantage", "strong demand",
    # Financial
    "dividend", "buyback", "upgrade", "bullish", "opportunity",
    # Operations
    "efficiency", "cost reduction", "optimization", "improvement",
]

NEGATIVE_KEYWORDS = [
    # Financial issues
    "loss", "decline", "miss expectations", "downgrade", "restructuring",
    "layoffs", "job cuts", "bankruptcy", "default", "debt",
    # Legal/Regulatory
    "lawsuit", "investigation", "fine", "penalty", "violation",
    "recall", "scandal", "fraud", "compliance",
    # Market
    "competition", "market share loss", "bearish", "sell-off",
    # Operations
    "delay", "shortage", "supply chain", "disruption", "problem",
    # Leadership
    "resignation", "departure", "controversy", "criticism",
]

CATEGORY_KEYWORDS = {
    NewsCategory.FINANCIAL: [
        "revenue", "profit", "earnings", "financial", "quarterly",
        "annual report", "SEC", "investors", "stock", "shares",
    ],
    NewsCategory.PRODUCT: [
        "product", "launch", "release", "feature", "update",
        "technology", "innovation", "patent", "R&D",
    ],
    NewsCategory.LEADERSHIP: [
        "CEO", "CFO", "executive", "board", "appointment",
        "resignation", "leadership", "management",
    ],
    NewsCategory.LEGAL: [
        "lawsuit", "litigation", "court", "settlement", "investigation",
        "regulatory", "compliance", "fine", "penalty",
    ],
    NewsCategory.PARTNERSHIP: [
        "partnership", "collaboration", "agreement", "deal",
        "contract", "alliance", "joint venture",
    ],
    NewsCategory.EXPANSION: [
        "expansion", "growth", "new market", "acquisition",
        "merger", "facility", "office", "international",
    ],
    NewsCategory.WORKFORCE: [
        "hiring", "employees", "workforce", "layoffs", "jobs",
        "talent", "culture", "workplace",
    ],
    NewsCategory.SUSTAINABILITY: [
        "ESG", "sustainability", "environmental", "carbon",
        "renewable", "green", "climate", "social responsibility",
    ],
    NewsCategory.COMPETITION: [
        "competitor", "competition", "market share", "versus",
        "vs", "rival", "competing",
    ],
}


class NewsSentimentAnalyzer:
    """Analyzes news sentiment for companies."""

    def __init__(
        self,
        relevance_threshold: float = 0.3,
        lookback_days: int = 30
    ):
        """
        Initialize the news sentiment analyzer.

        Args:
            relevance_threshold: Minimum relevance score for articles
            lookback_days: Number of days to analyze
        """
        self.relevance_threshold = relevance_threshold
        self.lookback_days = lookback_days

    def analyze_text_sentiment(self, text: str) -> Tuple[float, SentimentLevel]:
        """
        Analyze sentiment of text using keyword matching.

        Args:
            text: Text to analyze

        Returns:
            Tuple of (sentiment_score, sentiment_level)
        """
        text_lower = text.lower()

        # Count positive and negative keywords
        positive_count = sum(
            1 for kw in POSITIVE_KEYWORDS if kw in text_lower
        )
        negative_count = sum(
            1 for kw in NEGATIVE_KEYWORDS if kw in text_lower
        )

        total_keywords = positive_count + negative_count
        if total_keywords == 0:
            return 0.0, SentimentLevel.NEUTRAL

        # Calculate score (-1.0 to 1.0)
        score = (positive_count - negative_count) / max(total_keywords, 1)

        # Determine level
        if score <= -0.6:
            level = SentimentLevel.VERY_NEGATIVE
        elif score <= -0.2:
            level = SentimentLevel.NEGATIVE
        elif score < 0.2:
            level = SentimentLevel.NEUTRAL
        elif score < 0.6:
            level = SentimentLevel.POSITIVE
        else:
            level = SentimentLevel.VERY_POSITIVE

        return score, level

    def categorize_article(self, text: str) -> NewsCategory:
        """
        Categorize an article based on content.

        Args:
            text: Article text

        Returns:
            NewsCategory
        """
        text_lower = text.lower()

        # Count keywords for each category
        category_scores = {}
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text_lower)
            category_scores[category] = score

        # Return category with highest score
        if max(category_scores.values()) > 0:
            return max(category_scores.items(), key=lambda x: x[1])[0]

        return NewsCategory.GENERAL

    def extract_topics(self, text: str, max_topics: int = 5) -> List[str]:
        """
        Extract key topics from text.

        Args:
            text: Text to analyze
            max_topics: Maximum number of topics

        Returns:
            List of topic strings
        """
        topics = []
        text_lower = text.lower()

        # Check for common business topics
        topic_patterns = [
            (r"\b(acquisition|merger)\b", "M&A Activity"),
            (r"\b(revenue|earnings|profit)\b", "Financial Performance"),
            (r"\b(product launch|new product)\b", "Product Launch"),
            (r"\b(partnership|collaboration)\b", "Strategic Partnership"),
            (r"\b(expansion|growth)\b", "Business Expansion"),
            (r"\b(layoff|restructuring)\b", "Restructuring"),
            (r"\b(lawsuit|litigation)\b", "Legal Issues"),
            (r"\b(ESG|sustainability)\b", "Sustainability"),
            (r"\b(CEO|executive)\b", "Leadership"),
            (r"\b(market share)\b", "Market Position"),
        ]

        for pattern, topic in topic_patterns:
            if re.search(pattern, text_lower):
                topics.append(topic)
                if len(topics) >= max_topics:
                    break

        return topics

    def calculate_relevance(
        self,
        text: str,
        company_name: str
    ) -> float:
        """
        Calculate how relevant an article is to a company.

        Args:
            text: Article text
            company_name: Company name to check relevance for

        Returns:
            Relevance score (0.0 to 1.0)
        """
        text_lower = text.lower()
        company_lower = company_name.lower()

        # Check for company name mentions
        name_parts = company_lower.split()

        # Full name match = high relevance
        if company_lower in text_lower:
            return 0.9

        # Partial name match
        matching_parts = sum(1 for part in name_parts if part in text_lower)
        if matching_parts > 0:
            return 0.5 + (0.3 * matching_parts / len(name_parts))

        return 0.2

    def analyze_article(
        self,
        title: str,
        snippet: str,
        source: str,
        url: str,
        published_date: datetime,
        company_name: str
    ) -> NewsArticle:
        """
        Analyze a single news article.

        Args:
            title: Article title
            snippet: Article snippet/summary
            source: News source
            url: Article URL
            published_date: Publication date
            company_name: Company to analyze relevance for

        Returns:
            NewsArticle with sentiment analysis
        """
        combined_text = f"{title} {snippet}"

        # Analyze sentiment
        sentiment_score, sentiment_level = self.analyze_text_sentiment(combined_text)

        # Categorize
        category = self.categorize_article(combined_text)

        # Extract topics
        topics = self.extract_topics(combined_text)

        # Calculate relevance
        relevance = self.calculate_relevance(combined_text, company_name)

        return NewsArticle(
            title=title,
            source=source,
            published_date=published_date,
            url=url,
            snippet=snippet,
            sentiment_score=sentiment_score,
            sentiment_level=sentiment_level,
            category=category,
            relevance_score=relevance,
            topics=topics
        )

    def determine_trend(self, articles: List[NewsArticle]) -> str:
        """
        Determine sentiment trend over time.

        Args:
            articles: List of analyzed articles (sorted by date)

        Returns:
            Trend description: "improving", "stable", or "declining"
        """
        if len(articles) < 3:
            return "stable"

        # Sort by date
        sorted_articles = sorted(articles, key=lambda a: a.published_date)

        # Split into halves
        mid = len(sorted_articles) // 2
        first_half = sorted_articles[:mid]
        second_half = sorted_articles[mid:]

        # Calculate average sentiment for each half
        avg_first = sum(a.sentiment_score for a in first_half) / len(first_half)
        avg_second = sum(a.sentiment_score for a in second_half) / len(second_half)

        # Determine trend
        diff = avg_second - avg_first
        if diff > 0.1:
            return "improving"
        elif diff < -0.1:
            return "declining"
        else:
            return "stable"

    def analyze_company_news(
        self,
        company_name: str,
        articles_data: List[Dict[str, Any]]
    ) -> NewsSentimentProfile:
        """
        Analyze news sentiment for a company.

        Args:
            company_name: Company name
            articles_data: List of article dictionaries with:
                - title: str
                - snippet: str
                - source: str
                - url: str
                - published_date: datetime or str

        Returns:
            NewsSentimentProfile with aggregated analysis
        """
        logger.info(f"Analyzing news sentiment for {company_name}")

        # Analyze each article
        analyzed_articles = []
        for article_data in articles_data:
            # Parse date if string
            pub_date = article_data.get("published_date", datetime.now())
            if isinstance(pub_date, str):
                try:
                    pub_date = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                except ValueError:
                    pub_date = datetime.now()

            article = self.analyze_article(
                title=article_data.get("title", ""),
                snippet=article_data.get("snippet", article_data.get("content", "")),
                source=article_data.get("source", "Unknown"),
                url=article_data.get("url", ""),
                published_date=pub_date,
                company_name=company_name
            )

            # Filter by relevance
            if article.relevance_score >= self.relevance_threshold:
                analyzed_articles.append(article)

        # Calculate aggregated sentiment
        if analyzed_articles:
            # Weighted average by relevance
            total_weight = sum(a.relevance_score for a in analyzed_articles)
            weighted_sentiment = sum(
                a.sentiment_score * a.relevance_score
                for a in analyzed_articles
            ) / total_weight if total_weight > 0 else 0.0
        else:
            weighted_sentiment = 0.0

        # Determine overall level
        if weighted_sentiment <= -0.6:
            overall_level = SentimentLevel.VERY_NEGATIVE
        elif weighted_sentiment <= -0.2:
            overall_level = SentimentLevel.NEGATIVE
        elif weighted_sentiment < 0.2:
            overall_level = SentimentLevel.NEUTRAL
        elif weighted_sentiment < 0.6:
            overall_level = SentimentLevel.POSITIVE
        else:
            overall_level = SentimentLevel.VERY_POSITIVE

        # Category breakdown
        category_breakdown = {}
        for article in analyzed_articles:
            category_breakdown[article.category] = category_breakdown.get(article.category, 0) + 1

        # Extract highlights
        positive_articles = sorted(
            [a for a in analyzed_articles if a.sentiment_score > 0.2],
            key=lambda a: a.sentiment_score,
            reverse=True
        )
        negative_articles = sorted(
            [a for a in analyzed_articles if a.sentiment_score < -0.2],
            key=lambda a: a.sentiment_score
        )

        positive_highlights = [a.title for a in positive_articles[:3]]
        negative_highlights = [a.title for a in negative_articles[:3]]

        # Extract key topics
        all_topics = []
        for article in analyzed_articles:
            all_topics.extend(article.topics)
        # Count topic frequency
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        key_topics = sorted(topic_counts.keys(), key=lambda t: topic_counts[t], reverse=True)[:5]

        # Determine trend
        trend = self.determine_trend(analyzed_articles)

        # Calculate confidence based on article count
        confidence = min(len(analyzed_articles) / 10, 1.0)

        return NewsSentimentProfile(
            company_name=company_name,
            analysis_date=datetime.now(),
            total_articles=len(analyzed_articles),
            sentiment_score=weighted_sentiment,
            sentiment_level=overall_level,
            articles=analyzed_articles,
            category_breakdown=category_breakdown,
            sentiment_trend=trend,
            key_topics=key_topics,
            positive_highlights=positive_highlights,
            negative_highlights=negative_highlights,
            confidence=confidence
        )

    def analyze_from_search_results(
        self,
        company_name: str,
        search_results: List[Dict[str, Any]]
    ) -> NewsSentimentProfile:
        """
        Analyze sentiment from search results (e.g., Tavily results).

        Args:
            company_name: Company name
            search_results: List of search result dictionaries

        Returns:
            NewsSentimentProfile
        """
        # Convert search results to article format
        articles_data = []
        for result in search_results:
            articles_data.append({
                "title": result.get("title", ""),
                "snippet": result.get("content", result.get("snippet", "")),
                "source": result.get("source", self._extract_source(result.get("url", ""))),
                "url": result.get("url", ""),
                "published_date": result.get("published_date", datetime.now())
            })

        return self.analyze_company_news(company_name, articles_data)

    def _extract_source(self, url: str) -> str:
        """Extract source name from URL."""
        if not url:
            return "Unknown"
        try:
            # Extract domain
            match = re.search(r"https?://(?:www\.)?([^/]+)", url)
            if match:
                domain = match.group(1)
                # Clean up domain
                return domain.replace(".com", "").replace(".org", "").title()
        except Exception:
            pass
        return "Unknown"


def create_sentiment_analyzer(
    relevance_threshold: float = 0.3,
    lookback_days: int = 30
) -> NewsSentimentAnalyzer:
    """Factory function to create NewsSentimentAnalyzer."""
    return NewsSentimentAnalyzer(
        relevance_threshold=relevance_threshold,
        lookback_days=lookback_days
    )
