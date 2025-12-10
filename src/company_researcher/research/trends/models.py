"""
Historical Trends Data Models.

This module contains all data models for historical trend analysis:
- TrendDirection enum
- MetricCategory enum
- DataPoint dataclass
- TrendMetric dataclass
- TrendAnalysis dataclass
- TrendTable dataclass
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TrendDirection(Enum):
    """Direction of trend movement."""
    STRONG_UP = "strong_up"
    UP = "up"
    STABLE = "stable"
    DOWN = "down"
    STRONG_DOWN = "strong_down"
    VOLATILE = "volatile"
    INSUFFICIENT_DATA = "insufficient_data"


class MetricCategory(Enum):
    """Categories of metrics for trend analysis."""
    REVENUE = "revenue"
    PROFITABILITY = "profitability"
    GROWTH = "growth"
    EFFICIENCY = "efficiency"
    MARKET = "market"
    OPERATIONAL = "operational"


@dataclass
class DataPoint:
    """Single data point in a time series."""
    year: int
    quarter: Optional[int] = None  # None for annual, 1-4 for quarterly
    value: float = 0.0
    currency: str = "USD"
    source: str = ""
    confidence: float = 1.0
    is_estimate: bool = False


@dataclass
class TrendMetric:
    """Metric with historical data points."""
    name: str
    display_name: str
    category: MetricCategory
    data_points: List[DataPoint] = field(default_factory=list)
    unit: str = ""  # e.g., "$", "%", "employees"
    is_percentage: bool = False

    def get_sorted_annual(self) -> List[DataPoint]:
        """Get annual data points sorted by year."""
        annual = [dp for dp in self.data_points if dp.quarter is None]
        return sorted(annual, key=lambda x: x.year)

    def get_sorted_quarterly(self) -> List[DataPoint]:
        """Get quarterly data points sorted by year and quarter."""
        quarterly = [dp for dp in self.data_points if dp.quarter is not None]
        return sorted(quarterly, key=lambda x: (x.year, x.quarter or 0))


@dataclass
class TrendAnalysis:
    """Analysis of a metric's trend."""
    metric_name: str
    direction: TrendDirection
    cagr: Optional[float] = None  # Compound Annual Growth Rate
    average_growth: Optional[float] = None
    volatility: Optional[float] = None  # Standard deviation of growth rates
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    latest_value: Optional[float] = None
    latest_year: Optional[int] = None
    trend_description: str = ""
    data_quality: str = "good"  # good, partial, poor
    years_of_data: int = 0


@dataclass
class TrendTable:
    """Formatted trend table for report output."""
    title: str
    headers: List[str]
    rows: List[Dict[str, Any]]
    footnotes: List[str] = field(default_factory=list)
    markdown: str = ""
