"""
News API Integration - Real-time news monitoring and sentiment tracking.

Provides:
- NewsAPI integration
- News search and filtering
- Sentiment analysis
- Topic clustering
- Alert triggers
"""

import asyncio
import hashlib
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class NewsSentiment(str, Enum):
    """News article sentiment."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class NewsCategory(str, Enum):
    """News categories."""
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    GENERAL = "general"
    SCIENCE = "science"
    HEALTH = "health"


@dataclass
class NewsArticle:
    """A news article."""
    title: str
    description: str
    url: str
    source_name: str
    published_at: datetime
    author: Optional[str] = None
    content: str = ""
    image_url: Optional[str] = None
    category: NewsCategory = NewsCategory.GENERAL
    sentiment: NewsSentiment = NewsSentiment.NEUTRAL
    sentiment_score: float = 0.0
    relevance_score: float = 0.0
    keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def age_hours(self) -> float:
        """Get article age in hours."""
        return (_utcnow() - self.published_at).total_seconds() / 3600

    @property
    def is_recent(self) -> bool:
        """Check if article is from last 24 hours."""
        return self.age_hours <= 24

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "source": self.source_name,
            "published_at": self.published_at.isoformat(),
            "author": self.author,
            "category": self.category.value,
            "sentiment": self.sentiment.value,
            "sentiment_score": self.sentiment_score,
            "relevance_score": self.relevance_score,
            "keywords": self.keywords,
            "age_hours": round(self.age_hours, 1)
        }


@dataclass
class NewsSearchResult:
    """Result of a news search."""
    query: str
    total_results: int
    articles: List[NewsArticle]
    searched_at: datetime = field(default_factory=_utcnow)
    sentiment_summary: Dict[str, int] = field(default_factory=dict)

    def get_positive_articles(self) -> List[NewsArticle]:
        """Get positive sentiment articles."""
        return [a for a in self.articles if a.sentiment == NewsSentiment.POSITIVE]

    def get_negative_articles(self) -> List[NewsArticle]:
        """Get negative sentiment articles."""
        return [a for a in self.articles if a.sentiment == NewsSentiment.NEGATIVE]

    def get_average_sentiment(self) -> float:
        """Get average sentiment score (-1 to 1)."""
        if not self.articles:
            return 0.0
        return sum(a.sentiment_score for a in self.articles) / len(self.articles)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "total_results": self.total_results,
            "searched_at": self.searched_at.isoformat(),
            "article_count": len(self.articles),
            "sentiment_summary": self.sentiment_summary,
            "average_sentiment": self.get_average_sentiment(),
            "articles": [a.to_dict() for a in self.articles]
        }


class SimpleSentimentAnalyzer:
    """Simple rule-based sentiment analyzer."""

    POSITIVE_WORDS = {
        "growth", "profit", "success", "gain", "rise", "surge", "boost",
        "beat", "exceed", "strong", "positive", "optimistic", "bullish",
        "innovation", "breakthrough", "milestone", "expand", "increase",
        "record", "high", "best", "leading", "outperform"
    }

    NEGATIVE_WORDS = {
        "loss", "decline", "fall", "drop", "miss", "weak", "negative",
        "pessimistic", "bearish", "layoff", "lawsuit", "fine", "penalty",
        "investigation", "scandal", "crisis", "recall", "fail", "concern",
        "warning", "risk", "threat", "downturn", "cut", "reduce"
    }

    def analyze(self, text: str) -> tuple:
        """
        Analyze sentiment of text.

        Returns:
            Tuple of (sentiment, score)
        """
        if not text:
            return NewsSentiment.NEUTRAL, 0.0

        text_lower = text.lower()
        words = set(re.findall(r'\w+', text_lower))

        positive_count = len(words & self.POSITIVE_WORDS)
        negative_count = len(words & self.NEGATIVE_WORDS)

        total = positive_count + negative_count
        if total == 0:
            return NewsSentiment.NEUTRAL, 0.0

        score = (positive_count - negative_count) / total

        if score > 0.3:
            return NewsSentiment.POSITIVE, score
        elif score < -0.3:
            return NewsSentiment.NEGATIVE, score
        elif positive_count > 0 and negative_count > 0:
            return NewsSentiment.MIXED, score
        else:
            return NewsSentiment.NEUTRAL, score


class NewsAPIClient:
    """
    Client for NewsAPI.org.

    Usage:
        client = NewsAPIClient(api_key="your_key")

        # Search for company news
        results = await client.search_company("Tesla")

        # Get top headlines
        headlines = await client.get_headlines(category="business")

        # Search with filters
        results = await client.search(
            query="Tesla earnings",
            from_date=datetime.now() - timedelta(days=7),
            language="en"
        )
    """

    BASE_URL = "https://newsapi.org/v2"

    def __init__(
        self,
        api_key: str = None,
        timeout: float = 30.0,
        enable_sentiment: bool = True
    ):
        self.api_key = api_key or os.environ.get("NEWS_API_KEY", "")
        self.timeout = timeout
        self.enable_sentiment = enable_sentiment
        self._sentiment_analyzer = SimpleSentimentAnalyzer() if enable_sentiment else None

    async def search(
        self,
        query: str,
        from_date: datetime = None,
        to_date: datetime = None,
        language: str = "en",
        sort_by: str = "relevancy",
        page_size: int = 20,
        page: int = 1
    ) -> NewsSearchResult:
        """
        Search for news articles.

        Args:
            query: Search query
            from_date: Start date filter
            to_date: End date filter
            language: Language code
            sort_by: Sort order (relevancy, popularity, publishedAt)
            page_size: Results per page
            page: Page number

        Returns:
            NewsSearchResult object
        """
        params = {
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "pageSize": min(page_size, 100),
            "page": page,
            "apiKey": self.api_key
        }

        if from_date:
            params["from"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            params["to"] = to_date.strftime("%Y-%m-%d")

        data = await self._request("everything", params)
        return self._parse_search_result(query, data)

    async def search_company(
        self,
        company_name: str,
        days_back: int = 7,
        page_size: int = 20
    ) -> NewsSearchResult:
        """
        Search for company-specific news.

        Args:
            company_name: Company name to search
            days_back: Number of days to look back
            page_size: Number of results

        Returns:
            NewsSearchResult object
        """
        from_date = _utcnow() - timedelta(days=days_back)
        return await self.search(
            query=company_name,
            from_date=from_date,
            sort_by="publishedAt",
            page_size=page_size
        )

    async def get_headlines(
        self,
        country: str = "us",
        category: str = None,
        query: str = None,
        page_size: int = 20
    ) -> NewsSearchResult:
        """
        Get top headlines.

        Args:
            country: Country code
            category: Category filter
            query: Search query
            page_size: Number of results

        Returns:
            NewsSearchResult object
        """
        params = {
            "country": country,
            "pageSize": min(page_size, 100),
            "apiKey": self.api_key
        }

        if category:
            params["category"] = category
        if query:
            params["q"] = query

        data = await self._request("top-headlines", params)
        return self._parse_search_result(query or "headlines", data)

    async def _request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request."""
        import urllib.request
        import urllib.parse

        url = f"{self.BASE_URL}/{endpoint}?{urllib.parse.urlencode(params)}"

        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "CompanyResearcher/1.0"}
            )

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: urllib.request.urlopen(request, timeout=self.timeout)
            )

            return json.loads(response.read().decode('utf-8'))

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "totalResults": 0,
                "articles": []
            }

    def _parse_search_result(self, query: str, data: Dict[str, Any]) -> NewsSearchResult:
        """Parse API response into NewsSearchResult."""
        articles = []
        sentiment_counts = {s.value: 0 for s in NewsSentiment}

        for item in data.get("articles", []):
            article = self._parse_article(item)
            articles.append(article)
            sentiment_counts[article.sentiment.value] += 1

        return NewsSearchResult(
            query=query,
            total_results=data.get("totalResults", 0),
            articles=articles,
            sentiment_summary=sentiment_counts
        )

    def _parse_article(self, data: Dict[str, Any]) -> NewsArticle:
        """Parse article data into NewsArticle."""
        # Parse published date
        published_str = data.get("publishedAt", "")
        try:
            published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
        except Exception:
            published_at = _utcnow()

        # Analyze sentiment if enabled
        text = f"{data.get('title', '')} {data.get('description', '')}"
        if self._sentiment_analyzer:
            sentiment, score = self._sentiment_analyzer.analyze(text)
        else:
            sentiment, score = NewsSentiment.NEUTRAL, 0.0

        # Extract keywords
        keywords = self._extract_keywords(text)

        return NewsArticle(
            title=data.get("title", ""),
            description=data.get("description", ""),
            url=data.get("url", ""),
            source_name=data.get("source", {}).get("name", ""),
            published_at=published_at,
            author=data.get("author"),
            content=data.get("content", ""),
            image_url=data.get("urlToImage"),
            sentiment=sentiment,
            sentiment_score=score,
            keywords=keywords
        )

    def _extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """Extract keywords from text."""
        if not text:
            return []

        # Simple keyword extraction
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        word_counts = {}
        for word in words:
            if len(word) > 3:
                word_counts[word] = word_counts.get(word, 0) + 1

        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:max_keywords]]


class NewsMonitor:
    """
    Monitors news for specific companies with alerts.

    Usage:
        monitor = NewsMonitor(client)

        # Add companies to monitor
        monitor.add_company("Tesla", alert_on=["lawsuit", "recall"])
        monitor.add_company("Apple", alert_on=["earnings", "launch"])

        # Set alert callback
        monitor.on_alert(my_alert_handler)

        # Start monitoring
        await monitor.start()
    """

    def __init__(
        self,
        client: NewsAPIClient,
        check_interval: float = 300,  # 5 minutes
        max_seen_articles_per_company: int = 10000  # Prevent memory leaks
    ):
        self.client = client
        self.check_interval = check_interval
        self._max_seen_articles = max_seen_articles_per_company
        self._companies: Dict[str, Dict[str, Any]] = {}
        self._seen_articles: Dict[str, set] = {}
        self._alert_callbacks: List[Callable] = []
        self._running = False

    def add_company(
        self,
        company_name: str,
        alert_keywords: List[str] = None,
        sentiment_threshold: float = -0.5
    ) -> None:
        """
        Add company to monitor.

        Args:
            company_name: Company name
            alert_keywords: Keywords that trigger alerts
            sentiment_threshold: Sentiment below this triggers alert
        """
        self._companies[company_name] = {
            "keywords": alert_keywords or [],
            "sentiment_threshold": sentiment_threshold
        }
        self._seen_articles[company_name] = set()

    def remove_company(self, company_name: str) -> None:
        """Remove company from monitoring."""
        self._companies.pop(company_name, None)
        self._seen_articles.pop(company_name, None)

    def on_alert(self, callback: Callable) -> None:
        """Register alert callback."""
        self._alert_callbacks.append(callback)

    async def start(self) -> None:
        """Start monitoring."""
        self._running = True
        while self._running:
            await self._check_all_companies()
            await asyncio.sleep(self.check_interval)

    def stop(self) -> None:
        """Stop monitoring."""
        self._running = False

    async def _check_all_companies(self) -> None:
        """Check all monitored companies."""
        for company_name, config in self._companies.items():
            try:
                await self._check_company(company_name, config)
            except Exception as e:
                logger.warning(f"News monitor check failed for {company_name}: {e}")

    async def _check_company(self, company_name: str, config: Dict) -> None:
        """Check single company for news."""
        result = await self.client.search_company(company_name, days_back=1)

        for article in result.articles:
            # Skip if already seen
            article_id = self._get_article_id(article)
            if article_id in self._seen_articles[company_name]:
                continue

            self._seen_articles[company_name].add(article_id)

            # Prune seen articles to prevent memory leaks
            if len(self._seen_articles[company_name]) > self._max_seen_articles:
                # Keep only half when limit exceeded (FIFO approximation for sets)
                seen_list = list(self._seen_articles[company_name])
                self._seen_articles[company_name] = set(seen_list[len(seen_list) // 2:])

            # Check for alerts
            should_alert = False
            alert_reason = ""

            # Check keywords
            if config["keywords"]:
                text = f"{article.title} {article.description}".lower()
                for keyword in config["keywords"]:
                    if keyword.lower() in text:
                        should_alert = True
                        alert_reason = f"Keyword match: {keyword}"
                        break

            # Check sentiment
            if article.sentiment_score < config["sentiment_threshold"]:
                should_alert = True
                alert_reason = f"Negative sentiment: {article.sentiment_score:.2f}"

            if should_alert:
                await self._trigger_alert(company_name, article, alert_reason)

    async def _trigger_alert(
        self,
        company_name: str,
        article: NewsArticle,
        reason: str
    ) -> None:
        """Trigger alert callbacks."""
        alert_data = {
            "company": company_name,
            "article": article.to_dict(),
            "reason": reason,
            "timestamp": _utcnow().isoformat()
        }

        for callback in self._alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert_data)
                else:
                    callback(alert_data)
            except Exception as e:
                logger.warning(f"News alert callback failed: {e}")

    def _get_article_id(self, article: NewsArticle) -> str:
        """Generate unique article ID."""
        content = f"{article.url}{article.title}"
        return hashlib.md5(content.encode()).hexdigest()


class NewsSummarizer:
    """Summarizes news search results."""

    def summarize(self, result: NewsSearchResult) -> Dict[str, Any]:
        """
        Generate summary of news search results.

        Args:
            result: NewsSearchResult to summarize

        Returns:
            Summary dictionary
        """
        if not result.articles:
            return {
                "query": result.query,
                "total_articles": 0,
                "summary": "No articles found."
            }

        # Calculate metrics
        avg_sentiment = result.get_average_sentiment()
        positive_pct = (
            result.sentiment_summary.get("positive", 0) / len(result.articles) * 100
        )
        negative_pct = (
            result.sentiment_summary.get("negative", 0) / len(result.articles) * 100
        )

        # Get top sources
        sources = {}
        for article in result.articles:
            sources[article.source_name] = sources.get(article.source_name, 0) + 1
        top_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]

        # Get top keywords
        all_keywords = []
        for article in result.articles:
            all_keywords.extend(article.keywords)
        keyword_counts = {}
        for kw in all_keywords:
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # Generate text summary
        sentiment_label = "positive" if avg_sentiment > 0.2 else "negative" if avg_sentiment < -0.2 else "neutral"

        summary_text = (
            f"Found {result.total_results} articles about '{result.query}'. "
            f"Overall sentiment is {sentiment_label} ({avg_sentiment:.2f}). "
            f"{positive_pct:.0f}% positive, {negative_pct:.0f}% negative coverage. "
            f"Top sources: {', '.join(s[0] for s in top_sources[:3])}."
        )

        return {
            "query": result.query,
            "total_articles": result.total_results,
            "average_sentiment": avg_sentiment,
            "sentiment_label": sentiment_label,
            "positive_percentage": positive_pct,
            "negative_percentage": negative_pct,
            "top_sources": top_sources,
            "top_keywords": top_keywords,
            "summary": summary_text,
            "recent_headlines": [
                {"title": a.title, "source": a.source_name, "sentiment": a.sentiment.value}
                for a in result.articles[:5]
            ]
        }


# Convenience functions

def create_news_client(api_key: str = None) -> NewsAPIClient:
    """Create a NewsAPI client."""
    return NewsAPIClient(api_key=api_key)


async def search_company_news(
    company_name: str,
    api_key: str = None,
    days_back: int = 7
) -> NewsSearchResult:
    """Search for company news."""
    client = NewsAPIClient(api_key=api_key)
    return await client.search_company(company_name, days_back=days_back)


def create_news_monitor(
    api_key: str = None,
    check_interval: float = 300
) -> NewsMonitor:
    """Create a news monitor."""
    client = NewsAPIClient(api_key=api_key)
    return NewsMonitor(client, check_interval=check_interval)
