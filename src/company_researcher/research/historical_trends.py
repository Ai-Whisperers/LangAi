"""
Historical Trend Analysis Module

This module provides multi-year trend analysis for company metrics with:
- Revenue and growth trends
- Profitability trends (margins, earnings)
- Market performance trends
- Operational metrics over time

The module addresses the issue of "single-point-in-time data" in reports
by extracting and visualizing historical patterns.

Modules:
    - trends.models: Data models (TrendDirection, MetricCategory, DataPoint, TrendMetric, TrendAnalysis, TrendTable)
    - trends.analyzer: HistoricalTrendAnalyzer class for trend analysis

Usage:
    from company_researcher.research.historical_trends import (
        create_trend_analyzer,
        TrendDirection,
        MetricCategory,
        HistoricalTrendAnalyzer,
    )

    # Create analyzer
    analyzer = create_trend_analyzer(lookback_years=5)

    # Extract historical data
    metrics = analyzer.extract_historical_data(content, source_name="10-K")

    # Analyze trends
    for name, metric in metrics.items():
        analysis = analyzer.analyze_trend(metric)
        print(analysis.trend_description)
"""

# Import from trends package
from .trends import (
    # Models
    TrendDirection,
    MetricCategory,
    DataPoint,
    TrendMetric,
    TrendAnalysis,
    TrendTable,
    # Analyzer
    HistoricalTrendAnalyzer,
    # Factory
    create_trend_analyzer,
)

# Re-export all public APIs for backward compatibility
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


# Example usage and testing
if __name__ == "__main__":
    # Sample content with historical data
    sample_content = """
    Tesla's Annual Performance:

    In 2023, revenue was $96.8 billion, up from $81.5 billion in 2022.
    2021 revenue: $53.8 billion
    FY2020: $31.5 billion revenue

    The company grew 19% in 2023, following 51% growth in 2022.
    2021 growth of 71%

    Gross margin of 18.2% in 2023
    2022 gross margin: 25.6%
    Operating margin of 9.2% in 2023

    | Metric | 2020 | 2021 | 2022 | 2023 |
    |--------|------|------|------|------|
    | Revenue | $31.5B | $53.8B | $81.5B | $96.8B |
    | Net Income | $0.7B | $5.5B | $12.6B | $15.0B |
    | Employees | 70,757 | 99,290 | 127,855 | 140,473 |
    """

    print("Historical Trend Analysis Demo")
    print("=" * 50)

    # Create analyzer
    analyzer = create_trend_analyzer(lookback_years=5)
    print("\n1. Extracting historical data...")

    # Extract historical data
    metrics = analyzer.extract_historical_data(sample_content, source_name="Sample Report")
    print(f"   Found {len(metrics)} metrics with historical data")

    # Analyze each metric
    print("\n2. Analyzing trends...")
    for name, metric in metrics.items():
        analysis = analyzer.analyze_trend(metric)
        print(f"\n   {metric.display_name}:")
        print(f"   - {analysis.trend_description}")
        print(f"   - Direction: {analysis.direction.value}")
        print(f"   - Data points: {len(metric.data_points)}")
        print(f"   - Data quality: {analysis.data_quality}")

    # Generate trend table
    print("\n3. Generating trend table...")
    if metrics:
        table = analyzer.generate_trend_table(
            list(metrics.values()),
            title="Multi-Year Financial Trends"
        )
        print("\n" + table.markdown)

    # Generate growth analysis
    print("\n4. Generating growth analysis...")
    if metrics:
        growth_analysis = analyzer.generate_growth_analysis(metrics)
        print("\n" + growth_analysis)

    print("\n" + "=" * 50)
    print("Demo completed. Key Features Demonstrated:")
    print("  ✓ Historical data extraction from text")
    print("  ✓ Historical data extraction from markdown tables")
    print("  ✓ Revenue trend analysis with CAGR")
    print("  ✓ Growth rate tracking")
    print("  ✓ Margin trend analysis")
    print("  ✓ Multi-metric trend tables")
    print("  ✓ Narrative growth analysis")
    print("  ✓ Trend direction classification")
    print("  ✓ Data quality assessment")


# NOTE: Old implementation has been moved to the trends/ package
# This file now serves as a backward-compatible entry point
# The actual implementation is in:
# - trends/models.py: Data models and enums (TrendDirection, MetricCategory, DataPoint, etc.)
# - trends/analyzer.py: HistoricalTrendAnalyzer class with analysis methods
# - trends/__init__.py: Package exports and factory function
