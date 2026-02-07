"""
Unified Cost Tracker - Track costs across ALL providers.

Tracks spending across:
- LLM Providers (Claude, GPT-4, DeepSeek, Gemini, Groq)
- Search Providers (Tavily, Serper, DuckDuckGo)
- Scraping Providers (Firecrawl, ScrapeGraph, Crawl4AI, Jina)
- News Providers (NewsAPI, GNews, Mediastack, Google RSS)
- Financial APIs (FMP, Finnhub, Polygon)

Features:
- Real-time cost tracking per provider
- Daily/monthly budgets with alerts
- Cost optimization recommendations
- Usage analytics and trends
- Export to JSON/CSV

Cost Hierarchy (prefer cheaper options):
FREE → CHEAP → STANDARD → PREMIUM
"""

import logging

# Import from cost package
from .cost import (
    PROVIDER_CONFIGS,
    CostAlert,
    CostTier,
    CostTracker,
    DailyUsage,
    ProviderCategory,
    ProviderConfig,
    UsageRecord,
    get_cost_tracker,
    get_daily_cost,
    get_monthly_cost,
    print_cost_summary,
    track_cost,
)

# Re-export for backward compatibility
__all__ = [
    "ProviderCategory",
    "CostTier",
    "ProviderConfig",
    "PROVIDER_CONFIGS",
    "UsageRecord",
    "DailyUsage",
    "CostAlert",
    "CostTracker",
    "get_cost_tracker",
    "track_cost",
    "get_daily_cost",
    "get_monthly_cost",
    "print_cost_summary",
]


# Example usage and testing
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Create tracker
    tracker = get_cost_tracker(daily_budget=10.0, monthly_budget=200.0)

    # Simulate some usage
    tracker.track("tavily", 5)  # 5 searches
    tracker.track("serper", 10)  # 10 searches
    tracker.track("duckduckgo", 100)  # 100 free searches
    tracker.track("crawl4ai", 50)  # 50 scrapes
    tracker.track_llm("claude-3-5-sonnet", 5000, 2000)  # 7k tokens
    tracker.track_llm("deepseek-chat", 10000, 5000)  # 15k tokens
    tracker.track("google-news-rss", 20)  # 20 free news queries

    # Print summary
    tracker.print_summary()

    # Get recommendations
    print("\nDetailed Recommendations:")
    for rec in tracker.get_recommendations():
        print(f"  - {rec}")


# NOTE: Old implementation has been moved to the cost/ package
# This file now serves as a backward-compatible entry point
# The actual implementation is in:
# - cost/models.py: Data models and provider configurations
# - cost/tracker.py: CostTracker class with tracking logic
# - cost/__init__.py: Package exports and convenience functions
