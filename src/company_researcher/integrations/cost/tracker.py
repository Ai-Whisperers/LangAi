"""
Cost Tracker - Main tracker class for monitoring API costs.

This module contains the CostTracker class that:
- Tracks real-time costs across all providers
- Manages budget alerts
- Provides usage analytics
- Generates cost optimization recommendations
"""

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Optional

from .models import (
    ProviderCategory,
    PROVIDER_CONFIGS,
    UsageRecord,
    CostAlert,
)
from ...utils import get_logger, utc_now

logger = get_logger(__name__)


class CostTracker:
    """
    Unified cost tracker for all API providers.

    Features:
    - Real-time cost tracking
    - Budget alerts
    - Usage analytics
    - Cost optimization recommendations
    """

    def __init__(
        self,
        daily_budget: float = 10.0,
        monthly_budget: float = 200.0,
        storage_path: Optional[Path] = None
    ):
        """
        Initialize cost tracker.

        Args:
            daily_budget: Daily spending limit in USD
            monthly_budget: Monthly spending limit in USD
            storage_path: Path to store usage data (optional)
        """
        self.daily_budget = daily_budget
        self.monthly_budget = monthly_budget
        self.storage_path = storage_path or Path(".cost_tracker")

        self._lock = Lock()
        self._usage: list[UsageRecord] = []
        self._alerts: list[CostAlert] = []
        self._session_start = utc_now()

        # Load historical data
        self._load_usage()

        # Set up default alerts
        self._setup_default_alerts()

        logger.info(
            f"CostTracker initialized: "
            f"daily_budget=${daily_budget}, monthly_budget=${monthly_budget}"
        )

    def _setup_default_alerts(self):
        """Set up default budget alerts."""
        # Daily budget alert at 80%
        self.add_alert(CostAlert(
            name="daily_80_percent",
            threshold=self.daily_budget * 0.8,
            period="daily"
        ))

        # Daily budget alert at 100%
        self.add_alert(CostAlert(
            name="daily_limit",
            threshold=self.daily_budget,
            period="daily"
        ))

        # Monthly budget alert at 50%
        self.add_alert(CostAlert(
            name="monthly_50_percent",
            threshold=self.monthly_budget * 0.5,
            period="monthly"
        ))

        # Monthly budget alert at 80%
        self.add_alert(CostAlert(
            name="monthly_80_percent",
            threshold=self.monthly_budget * 0.8,
            period="monthly"
        ))

    def _load_usage(self):
        """Load historical usage from storage."""
        if not self.storage_path.exists():
            self.storage_path.mkdir(parents=True, exist_ok=True)
            return

        usage_file = self.storage_path / "usage.json"
        if usage_file.exists():
            try:
                with open(usage_file, "r") as f:
                    data = json.load(f)
                    for record in data:
                        record["timestamp"] = datetime.fromisoformat(record["timestamp"])
                        self._usage.append(UsageRecord(**record))
                logger.info(f"Loaded {len(self._usage)} historical usage records")
            except Exception as e:
                logger.warning(f"Failed to load usage history: {e}")

    def _save_usage(self):
        """Save usage to storage."""
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            usage_file = self.storage_path / "usage.json"

            data = []
            for record in self._usage:
                r = asdict(record)
                r["timestamp"] = record.timestamp.isoformat()
                data.append(r)

            with open(usage_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save usage: {e}")

    def track(
        self,
        provider: str,
        units: float = 1.0,
        metadata: Optional[dict] = None
    ) -> float:
        """
        Track usage for a provider.

        Args:
            provider: Provider key (e.g., "tavily", "claude-3-5-sonnet")
            units: Number of units used (requests, tokens/1k, etc.)
            metadata: Optional metadata (query, response_tokens, etc.)

        Returns:
            Cost for this usage
        """
        config = PROVIDER_CONFIGS.get(provider)
        if not config:
            logger.warning(f"Unknown provider: {provider}")
            return 0.0

        cost = config.cost_per_unit * units

        record = UsageRecord(
            provider=provider,
            category=config.category.value,
            timestamp=utc_now(),
            units=units,
            cost=cost,
            metadata=metadata or {}
        )

        with self._lock:
            self._usage.append(record)
            self._save_usage()

        # Check alerts
        self._check_alerts()

        logger.debug(
            f"Tracked {units} {config.unit_type}s for {provider}: ${cost:.4f}"
        )

        return cost

    def track_llm(
        self,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        model: Optional[str] = None
    ) -> float:
        """
        Track LLM usage with token counts.

        Args:
            provider: LLM provider key
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model name (optional)

        Returns:
            Total cost
        """
        total_tokens = input_tokens + output_tokens
        units = total_tokens / 1000  # Convert to 1k token units

        return self.track(
            provider=provider,
            units=units,
            metadata={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "model": model
            }
        )

    def add_alert(self, alert: CostAlert):
        """Add a cost alert."""
        self._alerts.append(alert)
        logger.info(f"Added alert: {alert.name} (threshold: ${alert.threshold})")

    def _check_alerts(self):
        """Check and trigger alerts."""
        for alert in self._alerts:
            current = self._get_period_cost(alert.period, alert.category, alert.provider)

            if current >= alert.threshold:
                logger.warning(
                    f"ALERT [{alert.name}]: ${current:.2f} >= ${alert.threshold:.2f}"
                )
                if alert.callback:
                    alert.callback(current, alert.threshold)

    def _get_period_cost(
        self,
        period: str,
        category: Optional[ProviderCategory] = None,
        provider: Optional[str] = None
    ) -> float:
        """Get cost for a specific period."""
        now = utc_now()

        if period == "daily":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "monthly":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # total
            start = datetime.min

        total = 0.0
        for record in self._usage:
            if record.timestamp < start:
                continue
            if category and record.category != category.value:
                continue
            if provider and record.provider != provider:
                continue
            total += record.cost

        return total

    def get_daily_cost(self, category: Optional[ProviderCategory] = None) -> float:
        """Get today's total cost."""
        return self._get_period_cost("daily", category)

    def get_monthly_cost(self, category: Optional[ProviderCategory] = None) -> float:
        """Get this month's total cost."""
        return self._get_period_cost("monthly", category)

    def get_session_cost(self) -> float:
        """Get cost since session start."""
        total = 0.0
        for record in self._usage:
            if record.timestamp >= self._session_start:
                total += record.cost
        return total

    def get_summary(self) -> dict:
        """Get comprehensive cost summary."""
        now = utc_now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Calculate totals
        daily_total = 0.0
        monthly_total = 0.0
        session_total = 0.0

        daily_by_category: dict[str, float] = {}
        daily_by_provider: dict[str, float] = {}
        monthly_by_category: dict[str, float] = {}
        monthly_by_provider: dict[str, float] = {}

        for record in self._usage:
            if record.timestamp >= today_start:
                daily_total += record.cost
                daily_by_category[record.category] = (
                    daily_by_category.get(record.category, 0) + record.cost
                )
                daily_by_provider[record.provider] = (
                    daily_by_provider.get(record.provider, 0) + record.cost
                )

            if record.timestamp >= month_start:
                monthly_total += record.cost
                monthly_by_category[record.category] = (
                    monthly_by_category.get(record.category, 0) + record.cost
                )
                monthly_by_provider[record.provider] = (
                    monthly_by_provider.get(record.provider, 0) + record.cost
                )

            if record.timestamp >= self._session_start:
                session_total += record.cost

        return {
            "session": {
                "start": self._session_start.isoformat(),
                "cost": round(session_total, 4)
            },
            "daily": {
                "date": today_start.date().isoformat(),
                "cost": round(daily_total, 4),
                "budget": self.daily_budget,
                "remaining": round(self.daily_budget - daily_total, 4),
                "percent_used": round((daily_total / self.daily_budget) * 100, 1),
                "by_category": {k: round(v, 4) for k, v in daily_by_category.items()},
                "by_provider": {k: round(v, 4) for k, v in daily_by_provider.items()}
            },
            "monthly": {
                "month": month_start.strftime("%Y-%m"),
                "cost": round(monthly_total, 4),
                "budget": self.monthly_budget,
                "remaining": round(self.monthly_budget - monthly_total, 4),
                "percent_used": round((monthly_total / self.monthly_budget) * 100, 1),
                "by_category": {k: round(v, 4) for k, v in monthly_by_category.items()},
                "by_provider": {k: round(v, 4) for k, v in monthly_by_provider.items()}
            }
        }

    def get_recommendations(self) -> list[str]:
        """Get cost optimization recommendations based on usage patterns."""
        recommendations = []

        # Analyze usage patterns
        monthly_by_provider: dict[str, float] = {}
        for record in self._usage:
            monthly_by_provider[record.provider] = (
                monthly_by_provider.get(record.provider, 0) + record.cost
            )

        # Check for expensive providers with cheaper alternatives
        alternatives = {
            "tavily": ("serper", "10x cheaper search"),
            "firecrawl": ("crawl4ai", "free alternative"),
            "scrapegraph": ("crawl4ai", "free alternative"),
            "newsapi": ("google-news-rss", "free alternative"),
            "gnews": ("google-news-rss", "free alternative"),
            "mediastack": ("google-news-rss", "free alternative"),
            "claude-3-5-sonnet": ("deepseek-chat", "99% cheaper for non-critical tasks"),
            "gpt-4o": ("gpt-4o-mini", "100x cheaper for simple tasks"),
        }

        for provider, (alt, reason) in alternatives.items():
            if provider in monthly_by_provider and monthly_by_provider[provider] > 1.0:
                cost = monthly_by_provider[provider]
                recommendations.append(
                    f"Consider {alt} instead of {provider} ({reason}). "
                    f"Current spend: ${cost:.2f}/month"
                )

        # Check category spending
        monthly_by_category: dict[str, float] = {}
        for record in self._usage:
            monthly_by_category[record.category] = (
                monthly_by_category.get(record.category, 0) + record.cost
            )

        if monthly_by_category.get("search", 0) > 10:
            recommendations.append(
                "High search spending. Route bulk searches to DuckDuckGo (free) "
                "and use Serper for quality-critical queries."
            )

        if monthly_by_category.get("llm", 0) > 50:
            recommendations.append(
                "High LLM spending. Use DeepSeek/Groq for drafts and analysis, "
                "reserve Claude/GPT-4 for final outputs."
            )

        if monthly_by_category.get("scraping", 0) > 5:
            recommendations.append(
                "High scraping costs. Use Crawl4AI (free) for most pages, "
                "Jina Reader for quick markdown, Firecrawl only for complex JS sites."
            )

        if not recommendations:
            recommendations.append("Great job! Your cost optimization is on track.")

        return recommendations

    def export_to_csv(self, filepath: Path) -> None:
        """Export usage data to CSV."""
        import csv

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "provider", "category", "units", "cost", "metadata"
            ])

            for record in self._usage:
                writer.writerow([
                    record.timestamp.isoformat(),
                    record.provider,
                    record.category,
                    record.units,
                    record.cost,
                    json.dumps(record.metadata)
                ])

        logger.info(f"Exported {len(self._usage)} records to {filepath}")

    def print_summary(self) -> None:
        """Print a formatted cost summary."""
        summary = self.get_summary()

        print("\n" + "=" * 60)
        print("COST TRACKER SUMMARY")
        print("=" * 60)

        # Session
        print(f"\nSession (since {summary['session']['start'][:19]}):")
        print(f"  Total: ${summary['session']['cost']:.4f}")

        # Daily
        print(f"\nToday ({summary['daily']['date']}):")
        print(f"  Total: ${summary['daily']['cost']:.4f} / ${summary['daily']['budget']:.2f} "
              f"({summary['daily']['percent_used']:.1f}%)")
        print(f"  Remaining: ${summary['daily']['remaining']:.4f}")

        if summary['daily']['by_category']:
            print("  By Category:")
            for cat, cost in sorted(summary['daily']['by_category'].items(),
                                   key=lambda x: x[1], reverse=True):
                print(f"    {cat}: ${cost:.4f}")

        # Monthly
        print(f"\nThis Month ({summary['monthly']['month']}):")
        print(f"  Total: ${summary['monthly']['cost']:.4f} / ${summary['monthly']['budget']:.2f} "
              f"({summary['monthly']['percent_used']:.1f}%)")
        print(f"  Remaining: ${summary['monthly']['remaining']:.4f}")

        if summary['monthly']['by_category']:
            print("  By Category:")
            for cat, cost in sorted(summary['monthly']['by_category'].items(),
                                   key=lambda x: x[1], reverse=True):
                print(f"    {cat}: ${cost:.4f}")

        # Recommendations
        recommendations = self.get_recommendations()
        print("\nRecommendations:")
        for rec in recommendations:
            print(f"  - {rec}")

        print("\n" + "=" * 60)


# Singleton instance
_cost_tracker: Optional[CostTracker] = None
_tracker_lock = Lock()


def get_cost_tracker(
    daily_budget: float = 10.0,
    monthly_budget: float = 200.0,
    storage_path: Optional[Path] = None
) -> CostTracker:
    """
    Get or create the singleton cost tracker.

    Args:
        daily_budget: Daily budget in USD
        monthly_budget: Monthly budget in USD
        storage_path: Path to store usage data

    Returns:
        CostTracker instance
    """
    global _cost_tracker

    with _tracker_lock:
        if _cost_tracker is None:
            _cost_tracker = CostTracker(
                daily_budget=daily_budget,
                monthly_budget=monthly_budget,
                storage_path=storage_path
            )
        return _cost_tracker
