"""
News Data Models and Enums.

This module contains all data models for the news routing system:
- NewsProvider enum
- NewsQuality enum
- NewsArticle dataclass
- NewsSearchResult dataclass
- ProviderQuota dataclass
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from ...utils import utc_now


class NewsProvider(str, Enum):
    """Available news providers."""
    GOOGLE_RSS = "google_rss"
    GNEWS = "gnews"
    NEWSAPI = "newsapi"
    MEDIASTACK = "mediastack"


class NewsQuality(str, Enum):
    """Quality tier for news search."""
    FREE = "free"           # Only use free providers
    STANDARD = "standard"   # Free first, fall back to paid
    PREMIUM = "premium"     # Use best provider regardless of cost


@dataclass
class NewsArticle:
    """Unified news article format."""
    title: str
    description: Optional[str]
    url: str
    source: str
    published_at: Optional[datetime]
    provider: NewsProvider
    image_url: Optional[str] = None
    author: Optional[str] = None
    content: Optional[str] = None
    sentiment: Optional[float] = None  # -1 to 1

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "source": self.source,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "provider": self.provider.value,
            "image_url": self.image_url,
            "author": self.author,
            "content": self.content,
            "sentiment": self.sentiment
        }


@dataclass
class NewsSearchResult:
    """Result from a news search."""
    query: str
    articles: list[NewsArticle]
    total_results: int
    provider: NewsProvider
    success: bool
    error: Optional[str] = None
    cached: bool = False
    cost: float = 0.0


@dataclass
class ProviderQuota:
    """Track provider quota usage."""
    provider: NewsProvider
    daily_limit: int
    monthly_limit: int
    daily_used: int = 0
    monthly_used: int = 0
    last_reset_daily: datetime = field(default_factory=utc_now)
    last_reset_monthly: datetime = field(default_factory=utc_now)

    def is_available(self) -> bool:
        """Check if provider has quota remaining."""
        self._check_reset()
        if self.daily_limit > 0 and self.daily_used >= self.daily_limit:
            return False
        if self.monthly_limit > 0 and self.monthly_used >= self.monthly_limit:
            return False
        return True

    def use(self):
        """Record a usage."""
        self._check_reset()
        self.daily_used += 1
        self.monthly_used += 1

    def _check_reset(self):
        """Reset counters if needed."""
        now = utc_now()

        # Daily reset
        if now.date() > self.last_reset_daily.date():
            self.daily_used = 0
            self.last_reset_daily = now

        # Monthly reset
        if now.month != self.last_reset_monthly.month or now.year != self.last_reset_monthly.year:
            self.monthly_used = 0
            self.last_reset_monthly = now
