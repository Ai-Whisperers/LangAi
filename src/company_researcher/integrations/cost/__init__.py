"""
Cost Tracking Package - Unified cost tracking across all API providers.

This package provides:
- Models: ProviderCategory, CostTier, ProviderConfig, PROVIDER_CONFIGS, etc.
- CostTracker: Main tracker class with alerts and analytics
- Convenience functions: track_cost, get_daily_cost, get_monthly_cost, etc.

Usage:
    from company_researcher.integrations.cost import (
        CostTracker,
        track_cost,
        get_cost_tracker,
        get_daily_cost,
        print_cost_summary,
    )

    # Track usage
    track_cost("tavily", units=5)
    track_cost("claude-3-5-sonnet", units=7.5)  # 7.5k tokens

    # Get summaries
    daily_cost = get_daily_cost()
    print_cost_summary()
"""


from .models import (
    ProviderCategory,
    CostTier,
    ProviderConfig,
    PROVIDER_CONFIGS,
    UsageRecord,
    DailyUsage,
    CostAlert,
)

from .tracker import (
    CostTracker,
    get_cost_tracker,
)


# Convenience functions
def track_cost(provider: str, units: float = 1.0, **metadata) -> float:
    """
    Quick function to track cost.

    Args:
        provider: Provider key
        units: Number of units
        **metadata: Additional metadata

    Returns:
        Cost for this usage
    """
    tracker = get_cost_tracker()
    return tracker.track(provider, units, metadata)


def get_daily_cost() -> float:
    """Get today's total cost."""
    return get_cost_tracker().get_daily_cost()


def get_monthly_cost() -> float:
    """Get this month's total cost."""
    return get_cost_tracker().get_monthly_cost()


def print_cost_summary() -> None:
    """Print cost summary to console."""
    get_cost_tracker().print_summary()


__all__ = [
    # Models
    "ProviderCategory",
    "CostTier",
    "ProviderConfig",
    "PROVIDER_CONFIGS",
    "UsageRecord",
    "DailyUsage",
    "CostAlert",
    # Tracker
    "CostTracker",
    "get_cost_tracker",
    # Convenience functions
    "track_cost",
    "get_daily_cost",
    "get_monthly_cost",
    "print_cost_summary",
]
