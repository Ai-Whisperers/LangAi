"""
Reddit API Client (async implementation).

Free tier: 100 requests/minute (OAuth), 10/minute (unauthenticated)
Provides: Subreddit posts, comments, sentiment analysis

Documentation: https://www.reddit.com/dev/api/
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_client import BaseAPIClient

logger = logging.getLogger(__name__)


@dataclass
class RedditPost:
    """Reddit post/submission data."""
    id: str
    title: str
    selftext: str
    author: str
    subreddit: str
    score: int
    upvote_ratio: float
    num_comments: int
    created_utc: float
    url: str
    permalink: str
    is_self: bool

    @classmethod
    def from_dict(cls, data: Dict) -> "RedditPost":
        # Handle both raw API and processed formats
        post_data = data.get("data", data)
        return cls(
            id=post_data.get("id", ""),
            title=post_data.get("title", ""),
            selftext=post_data.get("selftext", ""),
            author=post_data.get("author", "[deleted]"),
            subreddit=post_data.get("subreddit", ""),
            score=post_data.get("score", 0),
            upvote_ratio=post_data.get("upvote_ratio", 0),
            num_comments=post_data.get("num_comments", 0),
            created_utc=post_data.get("created_utc", 0),
            url=post_data.get("url", ""),
            permalink=f"https://reddit.com{post_data.get('permalink', '')}",
            is_self=post_data.get("is_self", False)
        )

    @property
    def created_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.created_utc)


@dataclass
class SubredditInfo:
    """Subreddit information."""
    name: str
    display_name: str
    title: str
    description: str
    subscribers: int
    active_users: int
    created_utc: float
    url: str

    @classmethod
    def from_dict(cls, data: Dict) -> "SubredditInfo":
        sub_data = data.get("data", data)
        return cls(
            name=sub_data.get("name", ""),
            display_name=sub_data.get("display_name", ""),
            title=sub_data.get("title", ""),
            description=sub_data.get("public_description", ""),
            subscribers=sub_data.get("subscribers", 0),
            active_users=sub_data.get("accounts_active", 0),
            created_utc=sub_data.get("created_utc", 0),
            url=f"https://reddit.com{sub_data.get('url', '')}"
        )


class RedditClient(BaseAPIClient):
    """
    Reddit API Client (async HTTP-based).

    Free tier: 100 requests/minute with OAuth
    Note: Requires OAuth app credentials from https://www.reddit.com/prefs/apps

    Features:
    - Search posts across subreddits
    - Get subreddit info and posts
    - Company sentiment analysis
    - Market sentiment tracking
    """

    BASE_URL = "https://oauth.reddit.com"
    AUTH_URL = "https://www.reddit.com/api/v1/access_token"

    # Relevant subreddits for company/market research
    FINANCE_SUBREDDITS = [
        "stocks", "investing", "wallstreetbets", "stockmarket",
        "finance", "options", "SecurityAnalysis"
    ]

    TECH_SUBREDDITS = [
        "technology", "programming", "startups", "entrepreneur",
        "business", "SaaS", "artificial"
    ]

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: str = "CompanyResearcher/1.0"
    ):
        import os
        self.client_id = client_id or os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = user_agent
        self._access_token: Optional[str] = None
        self._token_expires: float = 0

        super().__init__(
            api_key=self.client_id,  # Use client_id as API key placeholder
            cache_ttl=300,  # 5 min cache
            rate_limit_calls=100,
            rate_limit_period=60.0
        )

    def is_available(self) -> bool:
        """Check if Reddit credentials are configured."""
        return bool(self.client_id and self.client_secret)

    async def _get_access_token(self) -> Optional[str]:
        """Get OAuth access token."""
        import time
        import base64
        import aiohttp

        # Return cached token if valid
        if self._access_token and time.time() < self._token_expires:
            return self._access_token

        if not self.is_available():
            return None

        # Request new token
        auth = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        headers = {
            "Authorization": f"Basic {auth}",
            "User-Agent": self.user_agent,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "client_credentials"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.AUTH_URL,
                headers=headers,
                data=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self._access_token = result.get("access_token")
                    # Token expires in 1 hour, refresh at 50 minutes
                    self._token_expires = time.time() + 3000
                    return self._access_token

        return None

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with auth token."""
        headers = {
            "User-Agent": self.user_agent
        }
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        **kwargs
    ) -> Any:
        """Make authenticated request."""
        # Ensure we have a token
        token = await self._get_access_token()
        if not token:
            logger.warning("Reddit: No access token available")
            return None

        return await super()._request(endpoint, params, **kwargs)

    # =========================================================================
    # Search
    # =========================================================================

    async def search_posts(
        self,
        query: str,
        subreddit: Optional[str] = None,
        sort: str = "relevance",
        time_filter: str = "month",
        limit: int = 25
    ) -> List[RedditPost]:
        """
        Search for posts.

        Args:
            query: Search query
            subreddit: Specific subreddit or None for all
            sort: Sort order (relevance, hot, top, new, comments)
            time_filter: Time range (hour, day, week, month, year, all)
            limit: Max results (up to 100)

        Returns:
            List of RedditPost objects
        """
        if subreddit:
            endpoint = f"r/{subreddit}/search"
        else:
            endpoint = "search"

        params = {
            "q": query,
            "sort": sort,
            "t": time_filter,
            "limit": min(limit, 100),
            "restrict_sr": "true" if subreddit else "false"
        }

        data = await self._request(endpoint, params)
        if not data:
            return []

        posts = data.get("data", {}).get("children", [])
        return [RedditPost.from_dict(post) for post in posts]

    # =========================================================================
    # Subreddits
    # =========================================================================

    async def get_subreddit(self, name: str) -> Optional[SubredditInfo]:
        """
        Get subreddit information.

        Args:
            name: Subreddit name (without r/)

        Returns:
            SubredditInfo or None
        """
        data = await self._request(f"r/{name}/about")
        if data:
            return SubredditInfo.from_dict(data)
        return None

    async def get_subreddit_posts(
        self,
        subreddit: str,
        sort: str = "hot",
        time_filter: str = "week",
        limit: int = 25
    ) -> List[RedditPost]:
        """
        Get posts from a subreddit.

        Args:
            subreddit: Subreddit name
            sort: Sort order (hot, new, top, rising)
            time_filter: Time range for top posts
            limit: Max results

        Returns:
            List of RedditPost objects
        """
        endpoint = f"r/{subreddit}/{sort}"
        params = {"limit": min(limit, 100)}

        if sort == "top":
            params["t"] = time_filter

        data = await self._request(endpoint, params)
        if not data:
            return []

        posts = data.get("data", {}).get("children", [])
        return [RedditPost.from_dict(post) for post in posts]

    # =========================================================================
    # Company Analysis
    # =========================================================================

    async def analyze_company_sentiment(
        self,
        company_name: str,
        ticker: Optional[str] = None,
        subreddits: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze Reddit sentiment about a company.

        Args:
            company_name: Company name to search
            ticker: Stock ticker symbol (optional)
            subreddits: Specific subreddits to search

        Returns:
            Dict with sentiment analysis and top posts
        """
        subreddits = subreddits or self.FINANCE_SUBREDDITS + self.TECH_SUBREDDITS

        # Build search queries
        queries = [company_name]
        if ticker:
            queries.append(f"${ticker}")
            queries.append(ticker)

        all_posts = []
        seen_ids = set()

        # Search across subreddits
        for subreddit in subreddits[:5]:  # Limit to avoid rate limits
            for query in queries:
                posts = await self.search_posts(
                    query=query,
                    subreddit=subreddit,
                    time_filter="month",
                    limit=20
                )
                for post in posts:
                    if post.id not in seen_ids:
                        seen_ids.add(post.id)
                        all_posts.append(post)

        if not all_posts:
            return {
                "company": company_name,
                "ticker": ticker,
                "total_posts": 0,
                "error": "No posts found"
            }

        # Calculate metrics
        avg_score = sum(p.score for p in all_posts) / len(all_posts)
        avg_ratio = sum(p.upvote_ratio for p in all_posts) / len(all_posts)
        total_comments = sum(p.num_comments for p in all_posts)

        # Sentiment based on upvote ratios
        positive = len([p for p in all_posts if p.upvote_ratio > 0.65])
        negative = len([p for p in all_posts if p.upvote_ratio < 0.45])
        neutral = len(all_posts) - positive - negative

        # Top subreddits
        subreddit_counts = {}
        for post in all_posts:
            subreddit_counts[post.subreddit] = subreddit_counts.get(post.subreddit, 0) + 1

        # Top posts
        top_posts = sorted(all_posts, key=lambda x: x.score, reverse=True)[:10]

        return {
            "company": company_name,
            "ticker": ticker,
            "total_posts": len(all_posts),
            "metrics": {
                "average_score": round(avg_score, 1),
                "average_upvote_ratio": round(avg_ratio, 2),
                "total_comments": total_comments
            },
            "sentiment": {
                "positive": positive,
                "negative": negative,
                "neutral": neutral,
                "positive_ratio": round(positive / len(all_posts), 2) if all_posts else 0
            },
            "top_subreddits": dict(
                sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            ),
            "top_posts": [
                {
                    "title": p.title[:100],
                    "score": p.score,
                    "comments": p.num_comments,
                    "subreddit": p.subreddit,
                    "url": p.permalink
                }
                for p in top_posts
            ]
        }

    async def get_market_sentiment(
        self,
        limit_per_sub: int = 10
    ) -> Dict[str, Any]:
        """
        Get overall market sentiment from finance subreddits.

        Args:
            limit_per_sub: Posts to fetch per subreddit

        Returns:
            Dict with market sentiment overview
        """
        all_posts = []

        for subreddit in self.FINANCE_SUBREDDITS[:4]:
            posts = await self.get_subreddit_posts(
                subreddit,
                sort="hot",
                limit=limit_per_sub
            )
            all_posts.extend(posts)

        if not all_posts:
            return {"error": "Could not fetch market posts"}

        avg_ratio = sum(p.upvote_ratio for p in all_posts) / len(all_posts)

        return {
            "total_posts": len(all_posts),
            "average_upvote_ratio": round(avg_ratio, 2),
            "sentiment": "bullish" if avg_ratio > 0.6 else "bearish" if avg_ratio < 0.4 else "neutral",
            "top_discussions": [
                {
                    "title": p.title[:80],
                    "subreddit": p.subreddit,
                    "score": p.score,
                    "comments": p.num_comments
                }
                for p in sorted(all_posts, key=lambda x: x.score, reverse=True)[:5]
            ]
        }
