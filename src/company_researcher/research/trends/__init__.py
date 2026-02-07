"""
Historical Trends Package.

This package provides historical trend analysis for company metrics with:
- Multi-year trend analysis
- CAGR calculations
- Growth rate tracking
- Automated data extraction from text and tables

Modules:
    - models: Data models (TrendDirection, MetricCategory, DataPoint, TrendMetric, TrendAnalysis, TrendTable)
    - analyzer: HistoricalTrendAnalyzer class for trend analysis

Usage:
    from company_researcher.research.trends import (
        create_trend_analyzer,
        TrendDirection,
        MetricCategory,
        TrendMetric,
    )

    # Create analyzer
    analyzer = create_trend_analyzer(lookback_years=5)

    # Extract historical data
    metrics = analyzer.extract_historical_data(content, source_name="10-K")

    # Analyze trends
    for name, metric in metrics.items():
        analysis = analyzer.analyze_trend(metric)
        print(analysis.trend_description)

    # Generate trend table
    table = analyzer.generate_trend_table(list(metrics.values()))
    print(table.markdown)
"""

from .analyzer import HistoricalTrendAnalyzer
from .models import (
    DataPoint,
    MetricCategory,
    TrendAnalysis,
    TrendDirection,
    TrendMetric,
    TrendTable,
)

# Re-export all public APIs
__all__ = [
    # Models
    "TrendDirection",
    "MetricCategory",
    "DataPoint",
    "TrendMetric",
    "TrendAnalysis",
    "TrendTable",
    # Analyzer
    "HistoricalTrendAnalyzer",
    # Factory
    "create_trend_analyzer",
]


def create_trend_analyzer(lookback_years: int = 5) -> HistoricalTrendAnalyzer:
    """
    Factory function to create a HistoricalTrendAnalyzer.

    Args:
        lookback_years: Number of years to analyze (default 5)

    Returns:
        Configured HistoricalTrendAnalyzer instance

    Example:
        analyzer = create_trend_analyzer(lookback_years=5)
        metrics = analyzer.extract_historical_data(content, source_name="10-K")
    """
    return HistoricalTrendAnalyzer(lookback_years=lookback_years)
