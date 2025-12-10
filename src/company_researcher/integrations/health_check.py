"""
Integration Health Check Utility.

Provides comprehensive health checking for all API integrations.
Use this to verify which integrations are available and functioning.

Usage:
    from company_researcher.integrations import check_integration_health

    health = check_integration_health()
    print(health)

    # Or check specific category
    health = check_integration_health(categories=["financial", "news"])
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status for an integration."""
    HEALTHY = "healthy"           # Working properly
    DEGRADED = "degraded"         # Working but with issues
    UNAVAILABLE = "unavailable"   # Not responding
    UNCONFIGURED = "unconfigured" # API key not set
    ERROR = "error"               # Error during check


@dataclass
class IntegrationHealth:
    """Health status for a single integration."""
    name: str
    status: HealthStatus
    latency_ms: Optional[float] = None
    message: str = ""
    last_checked: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "latency_ms": self.latency_ms,
            "message": self.message,
            "last_checked": self.last_checked.isoformat(),
            "details": self.details
        }


@dataclass
class HealthReport:
    """Overall health report for all integrations."""
    overall_status: HealthStatus
    healthy_count: int
    degraded_count: int
    unavailable_count: int
    unconfigured_count: int
    error_count: int
    integrations: List[IntegrationHealth] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status.value,
            "summary": {
                "healthy": self.healthy_count,
                "degraded": self.degraded_count,
                "unavailable": self.unavailable_count,
                "unconfigured": self.unconfigured_count,
                "error": self.error_count,
                "total": len(self.integrations)
            },
            "integrations": [i.to_dict() for i in self.integrations],
            "generated_at": self.generated_at.isoformat()
        }

    def print_report(self):
        """Print a formatted health report."""
        print("\n" + "=" * 60)
        print("INTEGRATION HEALTH REPORT")
        print("=" * 60)
        print(f"Overall Status: {self.overall_status.value.upper()}")
        print(f"Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)

        # Group by category
        categories = {}
        for integration in self.integrations:
            cat = integration.details.get("category", "other")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(integration)

        for category, integrations in categories.items():
            print(f"\n{category.upper()}")
            print("-" * 40)
            for i in integrations:
                status_icon = {
                    HealthStatus.HEALTHY: "[OK]",
                    HealthStatus.DEGRADED: "[!!]",
                    HealthStatus.UNAVAILABLE: "[XX]",
                    HealthStatus.UNCONFIGURED: "[--]",
                    HealthStatus.ERROR: "[ER]"
                }.get(i.status, "[??]")

                latency = f"{i.latency_ms:.0f}ms" if i.latency_ms else "N/A"
                print(f"  {status_icon} {i.name:<25} {latency:<10} {i.message}")

        print("\n" + "=" * 60)
        print(f"Summary: {self.healthy_count} healthy, "
              f"{self.degraded_count} degraded, "
              f"{self.unavailable_count} unavailable, "
              f"{self.unconfigured_count} unconfigured, "
              f"{self.error_count} errors")
        print("=" * 60 + "\n")


class IntegrationHealthChecker:
    """
    Checks health of all integrations.

    Usage:
        checker = IntegrationHealthChecker(config)
        report = checker.check_all()
        report.print_report()
    """

    def __init__(self, config: Any):
        """Initialize with configuration."""
        self.config = config

    def check_all(
        self,
        categories: Optional[List[str]] = None,
        parallel: bool = True,
        timeout: float = 10.0
    ) -> HealthReport:
        """
        Check health of all integrations.

        Args:
            categories: Optional list of categories to check
            parallel: Whether to check in parallel
            timeout: Timeout for each check

        Returns:
            HealthReport with all results
        """
        checks = self._get_checks(categories)

        if parallel:
            results = self._check_parallel(checks, timeout)
        else:
            results = self._check_sequential(checks, timeout)

        return self._create_report(results)

    def _get_checks(self, categories: Optional[List[str]] = None) -> List[Dict]:
        """Get list of checks to perform."""
        all_checks = [
            # Financial
            {"name": "yfinance", "category": "financial", "check": self._check_yfinance, "requires_key": False},
            {"name": "FMP", "category": "financial", "check": self._check_fmp, "requires_key": True, "key_attr": "fmp_api_key"},
            {"name": "Finnhub", "category": "financial", "check": self._check_finnhub, "requires_key": True, "key_attr": "finnhub_api_key"},
            {"name": "Polygon", "category": "financial", "check": self._check_polygon, "requires_key": True, "key_attr": "polygon_api_key"},

            # News
            {"name": "NewsAPI", "category": "news", "check": self._check_newsapi, "requires_key": True, "key_attr": "newsapi_key"},
            {"name": "GNews", "category": "news", "check": self._check_gnews, "requires_key": True, "key_attr": "gnews_api_key"},
            {"name": "Mediastack", "category": "news", "check": self._check_mediastack, "requires_key": True, "key_attr": "mediastack_api_key"},

            # Search
            {"name": "Tavily", "category": "search", "check": self._check_tavily, "requires_key": True, "key_attr": "tavily_api_key"},

            # Company Data
            {"name": "Hunter.io", "category": "company", "check": self._check_hunter, "requires_key": True, "key_attr": "hunter_api_key"},
            {"name": "DomainsDB", "category": "company", "check": self._check_domainsdb, "requires_key": False},
            {"name": "GitHub", "category": "company", "check": self._check_github, "requires_key": True, "key_attr": "github_token"},

            # Geocoding
            {"name": "OpenCage", "category": "geocoding", "check": self._check_opencage, "requires_key": True, "key_attr": "opencage_api_key"},
            {"name": "Nominatim", "category": "geocoding", "check": self._check_nominatim, "requires_key": False},

            # LLM
            {"name": "Anthropic", "category": "llm", "check": self._check_anthropic, "requires_key": True, "key_attr": "anthropic_api_key"},
        ]

        if categories:
            all_checks = [c for c in all_checks if c["category"] in categories]

        return all_checks

    def _check_parallel(self, checks: List[Dict], timeout: float) -> List[IntegrationHealth]:
        """Run checks in parallel."""
        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {}
            for check in checks:
                future = executor.submit(self._run_check, check, timeout)
                futures[future] = check

            for future in as_completed(futures, timeout=timeout * 2):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    check = futures[future]
                    results.append(IntegrationHealth(
                        name=check["name"],
                        status=HealthStatus.ERROR,
                        message=str(e),
                        details={"category": check["category"]}
                    ))

        return results

    def _check_sequential(self, checks: List[Dict], timeout: float) -> List[IntegrationHealth]:
        """Run checks sequentially."""
        return [self._run_check(check, timeout) for check in checks]

    def _run_check(self, check: Dict, timeout: float) -> IntegrationHealth:
        """Run a single health check."""
        name = check["name"]
        category = check["category"]

        # Check if API key is required but not configured
        if check.get("requires_key"):
            key_attr = check.get("key_attr")
            if key_attr:
                key_value = getattr(self.config, key_attr, None)
                if not key_value:
                    return IntegrationHealth(
                        name=name,
                        status=HealthStatus.UNCONFIGURED,
                        message=f"{key_attr} not set",
                        details={"category": category}
                    )

        # Run the check
        start_time = time.time()
        try:
            check_func = check["check"]
            success, message, details = check_func()
            latency = (time.time() - start_time) * 1000

            status = HealthStatus.HEALTHY if success else HealthStatus.UNAVAILABLE
            if success and latency > 5000:  # > 5s is degraded
                status = HealthStatus.DEGRADED
                message = f"Slow response ({latency:.0f}ms)"

            return IntegrationHealth(
                name=name,
                status=status,
                latency_ms=latency,
                message=message,
                details={"category": category, **details}
            )

        except Exception as e:
            return IntegrationHealth(
                name=name,
                status=HealthStatus.ERROR,
                latency_ms=(time.time() - start_time) * 1000,
                message=str(e),
                details={"category": category}
            )

    def _create_report(self, results: List[IntegrationHealth]) -> HealthReport:
        """Create health report from results."""
        healthy = sum(1 for r in results if r.status == HealthStatus.HEALTHY)
        degraded = sum(1 for r in results if r.status == HealthStatus.DEGRADED)
        unavailable = sum(1 for r in results if r.status == HealthStatus.UNAVAILABLE)
        unconfigured = sum(1 for r in results if r.status == HealthStatus.UNCONFIGURED)
        errors = sum(1 for r in results if r.status == HealthStatus.ERROR)

        # Determine overall status
        if healthy == len(results):
            overall = HealthStatus.HEALTHY
        elif healthy > 0:
            overall = HealthStatus.DEGRADED
        elif unconfigured == len(results):
            overall = HealthStatus.UNCONFIGURED
        else:
            overall = HealthStatus.UNAVAILABLE

        return HealthReport(
            overall_status=overall,
            healthy_count=healthy,
            degraded_count=degraded,
            unavailable_count=unavailable,
            unconfigured_count=unconfigured,
            error_count=errors,
            integrations=results
        )

    # =========================================================================
    # Individual Check Methods
    # =========================================================================

    def _check_yfinance(self) -> tuple:
        """Check yfinance availability."""
        try:
            import yfinance as yf
            stock = yf.Ticker("AAPL")
            info = stock.info
            if info and info.get("regularMarketPrice"):
                return True, "OK", {"price": info.get("regularMarketPrice")}
            return False, "No data returned", {}
        except ImportError:
            return False, "yfinance not installed", {}
        except Exception as e:
            return False, str(e), {}

    def _check_fmp(self) -> tuple:
        """Check Financial Modeling Prep."""
        try:
            from .financial_modeling_prep import FMPClient
            client = FMPClient(self.config.fmp_api_key)
            profile = client.get_company_profile("AAPL")
            if profile:
                return True, "OK", {"company": "Apple Inc."}
            return False, "No data returned", {}
        except Exception as e:
            return False, str(e), {}

    def _check_finnhub(self) -> tuple:
        """Check Finnhub."""
        try:
            from .finnhub import FinnhubClient
            client = FinnhubClient(self.config.finnhub_api_key)
            quote = client.get_quote("AAPL")
            if quote and quote.get("c"):
                return True, "OK", {"price": quote.get("c")}
            return False, "No data returned", {}
        except Exception as e:
            return False, str(e), {}

    def _check_polygon(self) -> tuple:
        """Check Polygon."""
        try:
            from .polygon import PolygonClient
            client = PolygonClient(self.config.polygon_api_key)
            details = client.get_ticker_details("AAPL")
            if details:
                return True, "OK", {"name": details.get("name")}
            return False, "No data returned", {}
        except Exception as e:
            return False, str(e), {}

    def _check_newsapi(self) -> tuple:
        """Check NewsAPI."""
        try:
            from .news_api import NewsAPIClient
            client = NewsAPIClient(self.config.newsapi_key)
            articles = client.search_everything("technology", page_size=1)
            if articles:
                return True, "OK", {"articles": len(articles)}
            return False, "No articles returned", {}
        except Exception as e:
            return False, str(e), {}

    def _check_gnews(self) -> tuple:
        """Check GNews."""
        try:
            from .gnews import GNewsClient
            client = GNewsClient(self.config.gnews_api_key)
            articles = client.search("technology", max_results=1)
            if articles:
                return True, "OK", {"articles": len(articles)}
            return False, "No articles returned", {}
        except Exception as e:
            return False, str(e), {}

    def _check_mediastack(self) -> tuple:
        """Check Mediastack."""
        try:
            from .mediastack import MediastackClient
            client = MediastackClient(self.config.mediastack_api_key)
            articles = client.search(keywords="technology", limit=1)
            if articles:
                return True, "OK", {"articles": len(articles)}
            return False, "No articles returned", {}
        except Exception as e:
            return False, str(e), {}

    def _check_tavily(self) -> tuple:
        """Check Tavily."""
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=self.config.tavily_api_key)
            results = client.search("test query", max_results=1)
            if results.get("results"):
                return True, "OK", {"results": len(results.get("results", []))}
            return False, "No results returned", {}
        except Exception as e:
            return False, str(e), {}

    def _check_hunter(self) -> tuple:
        """Check Hunter.io."""
        try:
            from .hunter_io import HunterClient
            client = HunterClient(self.config.hunter_api_key)
            # Use account info check instead of domain search to save quota
            result = client.get_account()
            if result:
                return True, "OK", {}
            return False, "No response", {}
        except Exception as e:
            return False, str(e), {}

    def _check_domainsdb(self) -> tuple:
        """Check DomainsDB (free, no key)."""
        try:
            from .domainsdb import DomainsDBClient
            client = DomainsDBClient()
            result = client.search("google.com")
            if result:
                return True, "OK", {}
            return False, "No results", {}
        except Exception as e:
            return False, str(e), {}

    def _check_github(self) -> tuple:
        """Check GitHub API."""
        try:
            from .github_client import GitHubClient
            client = GitHubClient(self.config.github_token)
            result = client.get_rate_limit()
            if result:
                return True, "OK", {"remaining": result.get("remaining", 0)}
            return False, "No response", {}
        except Exception as e:
            return False, str(e), {}

    def _check_opencage(self) -> tuple:
        """Check OpenCage Geocoding."""
        try:
            from .opencage import OpenCageClient
            client = OpenCageClient(self.config.opencage_api_key)
            result = client.geocode("New York, USA")
            if result:
                return True, "OK", {}
            return False, "No results", {}
        except Exception as e:
            return False, str(e), {}

    def _check_nominatim(self) -> tuple:
        """Check Nominatim (free, no key)."""
        try:
            from .nominatim import NominatimClient
            client = NominatimClient()
            result = client.geocode("New York, USA")
            if result:
                return True, "OK", {}
            return False, "No results", {}
        except Exception as e:
            return False, str(e), {}

    def _check_anthropic(self) -> tuple:
        """Check Anthropic API."""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.config.anthropic_api_key)
            # Just verify the key format - don't make actual API call
            if self.config.anthropic_api_key.startswith("sk-ant-"):
                return True, "Key format valid", {}
            return False, "Invalid key format", {}
        except Exception as e:
            return False, str(e), {}


def check_integration_health(
    config: Any = None,
    categories: Optional[List[str]] = None,
    print_report: bool = False
) -> HealthReport:
    """
    Check health of all integrations.

    Args:
        config: Configuration object (uses get_config() if not provided)
        categories: Optional list of categories to check
        print_report: Whether to print the report

    Returns:
        HealthReport with all results
    """
    if config is None:
        from ..config import get_config
        config = get_config()

    checker = IntegrationHealthChecker(config)
    report = checker.check_all(categories=categories)

    if print_report:
        report.print_report()

    return report
