"""
API Quota Checker - Main checker class for monitoring API quotas.

This module contains the APIQuotaChecker class that checks quotas
across all integrated APIs using async HTTP requests.
"""

import asyncio
from datetime import datetime

import httpx

from ...utils import get_config, get_logger
from .models import QuotaInfo, QuotaReport, QuotaStatus

logger = get_logger(__name__)


class APIQuotaChecker:
    """Check quotas across all integrated APIs."""

    def __init__(self):
        self.client = None
        self._load_env_keys()

    def _load_env_keys(self):
        """Load API keys from environment."""
        self.keys = {
            # Core
            "anthropic": get_config("ANTHROPIC_API_KEY"),
            "tavily": get_config("TAVILY_API_KEY"),
            # Financial
            "fmp": get_config("FMP_API_KEY"),
            "finnhub": get_config("FINNHUB_API_KEY"),
            "polygon": get_config("POLYGON_API_KEY"),
            "alpha_vantage": get_config("ALPHA_VANTAGE_API_KEY"),
            # News
            "newsapi": get_config("NEWSAPI_KEY"),
            "gnews": get_config("GNEWS_API_KEY"),
            "mediastack": get_config("MEDIASTACK_API_KEY"),
            # Contact/Company
            "hunter": get_config("HUNTER_API_KEY"),
            # Web Scraping
            "firecrawl": get_config("FIRECRAWL_API_KEY"),
            "scrapegraph": get_config("SCRAPEGRAPH_API_KEY"),
            # Other
            "github": get_config("GITHUB_TOKEN"),
            "reddit_client": get_config("REDDIT_CLIENT_ID"),
            "reddit_secret": get_config("REDDIT_CLIENT_SECRET"),
            "opencage": get_config("OPENCAGE_API_KEY"),
            "huggingface": get_config("HUGGINGFACE_API_KEY"),
            # Observability
            "agentops": get_config("AGENTOPS_API_KEY"),
            "langsmith": get_config("LANGSMITH_API_KEY"),
        }

    def _error_info(self, *, api_name: str, error: Exception) -> QuotaInfo:
        return QuotaInfo(
            api_name=api_name,
            status=QuotaStatus.ERROR,
            error_message=f"{type(error).__name__}: {error}",
        )

    async def check_all(self) -> QuotaReport:
        """Check quotas for all configured APIs."""
        report = QuotaReport()

        async with httpx.AsyncClient(timeout=30.0) as client:
            self.client = client

            # Run all checks concurrently
            checks = [
                self._check_anthropic(),
                self._check_tavily(),
                self._check_fmp(),
                self._check_finnhub(),
                self._check_polygon(),
                self._check_newsapi(),
                self._check_gnews(),
                self._check_mediastack(),
                self._check_hunter(),
                self._check_firecrawl(),
                self._check_github(),
                self._check_opencage(),
            ]

            results = await asyncio.gather(*checks, return_exceptions=True)

            for result in results:
                if isinstance(result, QuotaInfo):
                    report.add(result)
                elif isinstance(result, Exception):
                    logger.error(f"Check failed: {result}")

        return report

    # =========================================================================
    # Individual API Checks
    # =========================================================================

    async def _check_anthropic(self) -> QuotaInfo:
        """
        Check Anthropic API.

        Note: Anthropic doesn't have a public quota endpoint.
        Usage is tracked via the admin console at console.anthropic.com
        We can only verify the key works and check rate limit headers.
        """
        if not self.keys.get("anthropic"):
            return QuotaInfo(api_name="Anthropic (Claude)", status=QuotaStatus.NO_KEY)

        try:
            # Make a minimal request to check key validity
            # Using messages API with minimal tokens
            response = await self.client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.keys["anthropic"],
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "hi"}],
                },
            )

            # Extract rate limits from headers
            rate_limit = response.headers.get("anthropic-ratelimit-requests-limit")
            rate_remaining = response.headers.get("anthropic-ratelimit-requests-remaining")
            rate_reset = response.headers.get("anthropic-ratelimit-requests-reset")

            # Token limits
            tokens_limit = response.headers.get("anthropic-ratelimit-tokens-limit")
            tokens_remaining = response.headers.get("anthropic-ratelimit-tokens-remaining")

            if response.status_code == 200:
                info = QuotaInfo(
                    api_name="Anthropic (Claude)",
                    status=QuotaStatus.OK,
                    rate_limit=int(rate_limit) if rate_limit else None,
                    rate_remaining=int(rate_remaining) if rate_remaining else None,
                    raw_response={
                        "requests_limit": rate_limit,
                        "requests_remaining": rate_remaining,
                        "tokens_limit": tokens_limit,
                        "tokens_remaining": tokens_remaining,
                    },
                )

                # Check if rate is getting low
                if rate_remaining and rate_limit:
                    if int(rate_remaining) < int(rate_limit) * 0.2:
                        info.status = QuotaStatus.LOW

                return info
            else:
                return QuotaInfo(
                    api_name="Anthropic (Claude)",
                    status=QuotaStatus.ERROR,
                    error_message=f"HTTP {response.status_code}",
                )

        except (httpx.TimeoutException, httpx.RequestError, ValueError, KeyError, TypeError) as e:
            return self._error_info(api_name="Anthropic (Claude)", error=e)

    async def _check_tavily(self) -> QuotaInfo:
        """
        Check Tavily API.

        Tavily provides usage info in response headers and has an account endpoint.
        Free: 1,000 searches/month
        """
        if not self.keys.get("tavily"):
            return QuotaInfo(api_name="Tavily Search", status=QuotaStatus.NO_KEY)

        try:
            # Check account/usage endpoint if available
            # For now, make a minimal search to verify key and get headers
            response = await self.client.post(
                "https://api.tavily.com/search",
                headers={"Content-Type": "application/json"},
                json={
                    "api_key": self.keys["tavily"],
                    "query": "test",
                    "max_results": 1,
                    "search_depth": "basic",
                },
            )

            if response.status_code == 200:
                # Tavily includes usage in response
                data = response.json()

                return QuotaInfo(
                    api_name="Tavily Search",
                    status=QuotaStatus.OK,
                    plan_name="Check dashboard at tavily.com",
                    period="monthly",
                    raw_response={"status": "active"},
                )
            elif response.status_code == 401:
                return QuotaInfo(
                    api_name="Tavily Search",
                    status=QuotaStatus.ERROR,
                    error_message="Invalid API key",
                )
            elif response.status_code == 429:
                return QuotaInfo(
                    api_name="Tavily Search",
                    status=QuotaStatus.EXHAUSTED,
                    error_message="Rate limit exceeded",
                )
            else:
                return QuotaInfo(
                    api_name="Tavily Search",
                    status=QuotaStatus.ERROR,
                    error_message=f"HTTP {response.status_code}",
                )

        except (httpx.TimeoutException, httpx.RequestError, ValueError, KeyError, TypeError) as e:
            return self._error_info(api_name="Tavily Search", error=e)

    async def _check_fmp(self) -> QuotaInfo:
        """
        Check Financial Modeling Prep API.

        Free: 250 requests/day
        Has usage tracking endpoint.
        """
        if not self.keys.get("fmp"):
            return QuotaInfo(api_name="FMP (Financial Modeling Prep)", status=QuotaStatus.NO_KEY)

        try:
            # FMP has a usage endpoint
            response = await self.client.get(
                f"https://financialmodelingprep.com/api/v3/profile/AAPL",
                params={"apikey": self.keys["fmp"]},
            )

            # Check rate limit headers
            limit = response.headers.get("X-RateLimit-Limit")
            remaining = response.headers.get("X-RateLimit-Remaining")

            if response.status_code == 200:
                status = QuotaStatus.OK
                if remaining and limit:
                    remaining_int = int(remaining)
                    limit_int = int(limit)
                    if remaining_int == 0:
                        status = QuotaStatus.EXHAUSTED
                    elif remaining_int < limit_int * 0.2:
                        status = QuotaStatus.LOW

                return QuotaInfo(
                    api_name="FMP (Financial Modeling Prep)",
                    status=status,
                    limit=int(limit) if limit else 250,
                    remaining=int(remaining) if remaining else None,
                    period="daily",
                    plan_name="Free tier" if not limit or int(limit) <= 250 else "Paid",
                )
            elif response.status_code == 401:
                return QuotaInfo(
                    api_name="FMP (Financial Modeling Prep)",
                    status=QuotaStatus.ERROR,
                    error_message="Invalid API key",
                )
            elif response.status_code == 429:
                return QuotaInfo(
                    api_name="FMP (Financial Modeling Prep)",
                    status=QuotaStatus.EXHAUSTED,
                    error_message="Daily limit reached",
                    limit=250,
                    remaining=0,
                    period="daily",
                )
            else:
                return QuotaInfo(
                    api_name="FMP (Financial Modeling Prep)",
                    status=QuotaStatus.UNKNOWN,
                    error_message=f"HTTP {response.status_code}",
                )

        except (httpx.TimeoutException, httpx.RequestError, ValueError, KeyError, TypeError) as e:
            return self._error_info(api_name="FMP (Financial Modeling Prep)", error=e)

    async def _check_finnhub(self) -> QuotaInfo:
        """
        Check Finnhub API.

        Free: 60 API calls/minute
        Returns rate limit headers.
        """
        if not self.keys.get("finnhub"):
            return QuotaInfo(api_name="Finnhub", status=QuotaStatus.NO_KEY)

        try:
            response = await self.client.get(
                "https://finnhub.io/api/v1/quote",
                params={"symbol": "AAPL", "token": self.keys["finnhub"]},
            )

            # Finnhub returns rate limits in headers
            limit = response.headers.get("X-Ratelimit-Limit")
            remaining = response.headers.get("X-Ratelimit-Remaining")
            reset = response.headers.get("X-Ratelimit-Reset")

            if response.status_code == 200:
                status = QuotaStatus.OK
                if remaining:
                    remaining_int = int(remaining)
                    limit_int = int(limit) if limit else 60
                    if remaining_int == 0:
                        status = QuotaStatus.EXHAUSTED
                    elif remaining_int < limit_int * 0.2:
                        status = QuotaStatus.LOW

                return QuotaInfo(
                    api_name="Finnhub",
                    status=status,
                    rate_limit=int(limit) if limit else 60,
                    rate_remaining=int(remaining) if remaining else None,
                    rate_reset=int(reset) if reset else None,
                    period="per minute",
                    plan_name="Free" if (limit and int(limit) <= 60) else "Paid",
                )
            elif response.status_code == 429:
                return QuotaInfo(
                    api_name="Finnhub",
                    status=QuotaStatus.EXHAUSTED,
                    error_message="Rate limit exceeded",
                    rate_limit=60,
                    rate_remaining=0,
                )
            else:
                return QuotaInfo(
                    api_name="Finnhub",
                    status=QuotaStatus.ERROR,
                    error_message=f"HTTP {response.status_code}",
                )

        except (httpx.TimeoutException, httpx.RequestError, ValueError, KeyError, TypeError) as e:
            return self._error_info(api_name="Finnhub", error=e)

    async def _check_polygon(self) -> QuotaInfo:
        """
        Check Polygon.io API.

        Free: 5 API calls/minute (delayed data)
        """
        if not self.keys.get("polygon"):
            return QuotaInfo(api_name="Polygon.io", status=QuotaStatus.NO_KEY)

        try:
            response = await self.client.get(
                f"https://api.polygon.io/v3/reference/tickers/AAPL",
                params={"apiKey": self.keys["polygon"]},
            )

            if response.status_code == 200:
                return QuotaInfo(
                    api_name="Polygon.io",
                    status=QuotaStatus.OK,
                    rate_limit=5,
                    period="per minute",
                    plan_name="Free (delayed data)",
                )
            elif response.status_code == 429:
                return QuotaInfo(
                    api_name="Polygon.io",
                    status=QuotaStatus.EXHAUSTED,
                    error_message="Rate limit exceeded",
                    rate_limit=5,
                    rate_remaining=0,
                    period="per minute",
                )
            elif response.status_code == 403:
                return QuotaInfo(
                    api_name="Polygon.io",
                    status=QuotaStatus.ERROR,
                    error_message="Invalid API key or unauthorized",
                )
            else:
                return QuotaInfo(
                    api_name="Polygon.io",
                    status=QuotaStatus.ERROR,
                    error_message=f"HTTP {response.status_code}",
                )

        except (httpx.TimeoutException, httpx.RequestError, ValueError, KeyError, TypeError) as e:
            return self._error_info(api_name="Polygon.io", error=e)

    async def _check_newsapi(self) -> QuotaInfo:
        """
        Check NewsAPI.

        Developer: 100 requests/day (free)
        Business: 250,000 requests/month
        """
        if not self.keys.get("newsapi"):
            return QuotaInfo(api_name="NewsAPI", status=QuotaStatus.NO_KEY)

        try:
            response = await self.client.get(
                "https://newsapi.org/v2/top-headlines",
                params={"apiKey": self.keys["newsapi"], "country": "us", "pageSize": 1},
            )

            # Check headers for rate limit info
            limit = response.headers.get("X-RateLimit-Limit")
            remaining = response.headers.get("X-RateLimit-Remaining")

            if response.status_code == 200:
                status = QuotaStatus.OK

                limit_val = int(limit) if limit else 100
                remaining_val = int(remaining) if remaining else None

                if remaining_val is not None:
                    if remaining_val == 0:
                        status = QuotaStatus.EXHAUSTED
                    elif remaining_val < limit_val * 0.2:
                        status = QuotaStatus.LOW

                return QuotaInfo(
                    api_name="NewsAPI",
                    status=status,
                    limit=limit_val,
                    remaining=remaining_val,
                    period="daily",
                    plan_name="Developer (free)" if limit_val <= 100 else "Business",
                )
            elif response.status_code == 401:
                return QuotaInfo(
                    api_name="NewsAPI", status=QuotaStatus.ERROR, error_message="Invalid API key"
                )
            elif response.status_code == 429:
                return QuotaInfo(
                    api_name="NewsAPI",
                    status=QuotaStatus.EXHAUSTED,
                    error_message="Rate limit exceeded",
                    limit=100,
                    remaining=0,
                    period="daily",
                )
            else:
                return QuotaInfo(
                    api_name="NewsAPI",
                    status=QuotaStatus.ERROR,
                    error_message=f"HTTP {response.status_code}",
                )

        except (httpx.TimeoutException, httpx.RequestError, ValueError, KeyError, TypeError) as e:
            return self._error_info(api_name="NewsAPI", error=e)

    async def _check_gnews(self) -> QuotaInfo:
        """
        Check GNews API.

        Free: 100 requests/day
        """
        if not self.keys.get("gnews"):
            return QuotaInfo(api_name="GNews", status=QuotaStatus.NO_KEY)

        try:
            response = await self.client.get(
                "https://gnews.io/api/v4/top-headlines",
                params={"token": self.keys["gnews"], "lang": "en", "max": 1},
            )

            if response.status_code == 200:
                return QuotaInfo(
                    api_name="GNews",
                    status=QuotaStatus.OK,
                    limit=100,
                    period="daily",
                    plan_name="Free",
                )
            elif response.status_code == 403:
                data = response.json()
                if "limit" in str(data).lower():
                    return QuotaInfo(
                        api_name="GNews",
                        status=QuotaStatus.EXHAUSTED,
                        error_message="Daily limit reached",
                        limit=100,
                        remaining=0,
                        period="daily",
                    )
                return QuotaInfo(
                    api_name="GNews", status=QuotaStatus.ERROR, error_message="Invalid API key"
                )
            else:
                return QuotaInfo(
                    api_name="GNews",
                    status=QuotaStatus.ERROR,
                    error_message=f"HTTP {response.status_code}",
                )

        except (httpx.TimeoutException, httpx.RequestError, ValueError, KeyError, TypeError) as e:
            return self._error_info(api_name="GNews", error=e)

    async def _check_mediastack(self) -> QuotaInfo:
        """
        Check Mediastack API.

        Free: 500 requests/month
        """
        if not self.keys.get("mediastack"):
            return QuotaInfo(api_name="Mediastack", status=QuotaStatus.NO_KEY)

        try:
            # Mediastack uses HTTP for free tier
            response = await self.client.get(
                "http://api.mediastack.com/v1/news",
                params={"access_key": self.keys["mediastack"], "countries": "us", "limit": 1},
            )

            if response.status_code == 200:
                data = response.json()
                if "error" in data:
                    return QuotaInfo(
                        api_name="Mediastack",
                        status=QuotaStatus.ERROR,
                        error_message=data.get("error", {}).get("message", "Unknown error"),
                    )
                return QuotaInfo(
                    api_name="Mediastack",
                    status=QuotaStatus.OK,
                    limit=500,
                    period="monthly",
                    plan_name="Free",
                )
            else:
                return QuotaInfo(
                    api_name="Mediastack",
                    status=QuotaStatus.ERROR,
                    error_message=f"HTTP {response.status_code}",
                )

        except (httpx.TimeoutException, httpx.RequestError, ValueError, KeyError, TypeError) as e:
            return self._error_info(api_name="Mediastack", error=e)

    async def _check_hunter(self) -> QuotaInfo:
        """
        Check Hunter.io API.

        Free: 25 searches/month, 50 verifications/month
        Has account info endpoint.
        """
        if not self.keys.get("hunter"):
            return QuotaInfo(api_name="Hunter.io", status=QuotaStatus.NO_KEY)

        try:
            # Hunter has an account endpoint that shows quota
            response = await self.client.get(
                "https://api.hunter.io/v2/account", params={"api_key": self.keys["hunter"]}
            )

            if response.status_code == 200:
                data = response.json().get("data", {})

                # Extract quota info
                requests = data.get("requests", {})
                searches = requests.get("searches", {})
                verifications = requests.get("verifications", {})

                searches_used = searches.get("used", 0)
                searches_available = searches.get("available", 25)
                verif_used = verifications.get("used", 0)
                verif_available = verifications.get("available", 50)

                # Determine status based on searches (primary use)
                status = QuotaStatus.OK
                if searches_available == 0:
                    status = QuotaStatus.EXHAUSTED
                elif searches_available < 5:
                    status = QuotaStatus.LOW

                return QuotaInfo(
                    api_name="Hunter.io",
                    status=status,
                    used=searches_used,
                    limit=searches_used + searches_available,
                    remaining=searches_available,
                    period="monthly",
                    plan_name=data.get("plan_name", "Free"),
                    account_email=data.get("email"),
                    raw_response={
                        "searches": {"used": searches_used, "available": searches_available},
                        "verifications": {"used": verif_used, "available": verif_available},
                        "plan": data.get("plan_name"),
                    },
                )
            elif response.status_code == 401:
                return QuotaInfo(
                    api_name="Hunter.io", status=QuotaStatus.ERROR, error_message="Invalid API key"
                )
            else:
                return QuotaInfo(
                    api_name="Hunter.io",
                    status=QuotaStatus.ERROR,
                    error_message=f"HTTP {response.status_code}",
                )

        except (httpx.TimeoutException, httpx.RequestError, ValueError, KeyError, TypeError) as e:
            return self._error_info(api_name="Hunter.io", error=e)

    async def _check_firecrawl(self) -> QuotaInfo:
        """
        Check Firecrawl API.

        Free tier: 500 credits
        Has credits endpoint.
        """
        if not self.keys.get("firecrawl"):
            return QuotaInfo(api_name="Firecrawl", status=QuotaStatus.NO_KEY)

        try:
            # Check credits endpoint
            response = await self.client.get(
                "https://api.firecrawl.dev/v1/credits",
                headers={"Authorization": f"Bearer {self.keys['firecrawl']}"},
            )

            if response.status_code == 200:
                data = response.json()
                credits = data.get("credits", 0)

                status = QuotaStatus.OK
                if credits == 0:
                    status = QuotaStatus.EXHAUSTED
                elif credits < 50:
                    status = QuotaStatus.LOW

                return QuotaInfo(
                    api_name="Firecrawl",
                    status=status,
                    credits_remaining=credits,
                    plan_name=data.get("plan", "Free"),
                )
            elif response.status_code == 401:
                return QuotaInfo(
                    api_name="Firecrawl", status=QuotaStatus.ERROR, error_message="Invalid API key"
                )
            else:
                return QuotaInfo(
                    api_name="Firecrawl",
                    status=QuotaStatus.UNKNOWN,
                    error_message=f"HTTP {response.status_code}",
                )

        except (httpx.TimeoutException, httpx.RequestError, ValueError, KeyError, TypeError) as e:
            return self._error_info(api_name="Firecrawl", error=e)

    async def _check_github(self) -> QuotaInfo:
        """
        Check GitHub API.

        Unauthenticated: 60 requests/hour
        Authenticated: 5,000 requests/hour
        """
        if not self.keys.get("github"):
            return QuotaInfo(api_name="GitHub", status=QuotaStatus.NO_KEY)

        try:
            response = await self.client.get(
                "https://api.github.com/rate_limit",
                headers={
                    "Authorization": f"token {self.keys['github']}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )

            if response.status_code == 200:
                data = response.json()
                core = data.get("resources", {}).get("core", {})

                limit = core.get("limit", 5000)
                remaining = core.get("remaining", 0)
                reset_ts = core.get("reset", 0)

                status = QuotaStatus.OK
                if remaining == 0:
                    status = QuotaStatus.EXHAUSTED
                elif remaining < limit * 0.2:
                    status = QuotaStatus.LOW

                reset_at = datetime.fromtimestamp(reset_ts) if reset_ts else None

                return QuotaInfo(
                    api_name="GitHub",
                    status=status,
                    limit=limit,
                    remaining=remaining,
                    reset_at=reset_at,
                    period="hourly",
                    plan_name="Authenticated" if limit >= 5000 else "Unauthenticated",
                    raw_response=data.get("resources", {}),
                )
            else:
                return QuotaInfo(
                    api_name="GitHub",
                    status=QuotaStatus.ERROR,
                    error_message=f"HTTP {response.status_code}",
                )

        except (httpx.TimeoutException, httpx.RequestError, ValueError, KeyError, TypeError) as e:
            return self._error_info(api_name="GitHub", error=e)

    async def _check_opencage(self) -> QuotaInfo:
        """
        Check OpenCage Geocoding API.

        Free: 2,500 requests/day
        Has quota info in response.
        """
        if not self.keys.get("opencage"):
            return QuotaInfo(api_name="OpenCage Geocoding", status=QuotaStatus.NO_KEY)

        try:
            response = await self.client.get(
                "https://api.opencagedata.com/geocode/v1/json",
                params={"key": self.keys["opencage"], "q": "New York", "limit": 1},
            )

            if response.status_code == 200:
                data = response.json()
                rate = data.get("rate", {})

                limit = rate.get("limit", 2500)
                remaining = rate.get("remaining", 0)
                reset_ts = rate.get("reset")

                status = QuotaStatus.OK
                if remaining == 0:
                    status = QuotaStatus.EXHAUSTED
                elif remaining < limit * 0.2:
                    status = QuotaStatus.LOW

                reset_at = datetime.fromtimestamp(reset_ts) if reset_ts else None

                return QuotaInfo(
                    api_name="OpenCage Geocoding",
                    status=status,
                    limit=limit,
                    remaining=remaining,
                    reset_at=reset_at,
                    period="daily",
                    plan_name="Free" if limit <= 2500 else "Paid",
                )
            elif response.status_code == 403:
                return QuotaInfo(
                    api_name="OpenCage Geocoding",
                    status=QuotaStatus.ERROR,
                    error_message="Invalid API key",
                )
            elif response.status_code == 402:
                return QuotaInfo(
                    api_name="OpenCage Geocoding",
                    status=QuotaStatus.EXHAUSTED,
                    error_message="Quota exceeded",
                )
            else:
                return QuotaInfo(
                    api_name="OpenCage Geocoding",
                    status=QuotaStatus.ERROR,
                    error_message=f"HTTP {response.status_code}",
                )

        except (httpx.TimeoutException, httpx.RequestError, ValueError, KeyError, TypeError) as e:
            return self._error_info(api_name="OpenCage Geocoding", error=e)
