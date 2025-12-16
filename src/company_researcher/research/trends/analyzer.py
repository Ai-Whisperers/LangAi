"""
Historical Trend Analyzer.

This module contains the HistoricalTrendAnalyzer class for analyzing
historical trends from extracted facts and source content.
"""

import re
from typing import Any, Dict, List, Optional

from ...utils import utc_now
from .models import (
    DataPoint,
    MetricCategory,
    TrendAnalysis,
    TrendDirection,
    TrendMetric,
    TrendTable,
)


class HistoricalTrendAnalyzer:
    """
    Analyzes historical trends from extracted facts and source content.

    Generates multi-year trend tables, calculates growth rates,
    and identifies significant patterns.
    """

    # Patterns for extracting historical data from text
    YEAR_VALUE_PATTERNS = [
        # "revenue was $X in 2023"
        r"(?:revenue|sales|income|earnings|profit)\s+(?:was|were|of|:)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?\s+(?:in\s+)?(\d{4})",
        # "2023 revenue: $X"
        r"(\d{4})\s+(?:revenue|sales)(?:\s*:)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?",
        # "FY2023: $X revenue"
        r"FY\s*(\d{4})(?:\s*:)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?",
        # "$X billion (2023)"
        r"\$\s*([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBM])?\s*\((\d{4})\)",
    ]

    GROWTH_PATTERNS = [
        # "grew X% in 2023"
        r"(?:grew|increased|rose|up)\s+([\d.]+)%\s+(?:in\s+)?(\d{4})",
        # "2023 growth of X%"
        r"(\d{4})\s+growth\s+(?:of\s+)?([\d.]+)%",
        # "YoY growth: X%"
        r"(?:YoY|year-over-year)\s+growth(?:\s*:)?\s+([\d.]+)%",
        # "X% increase from previous year"
        r"([\d.]+)%\s+(?:increase|growth)\s+(?:from|over)\s+(?:the\s+)?previous\s+year",
    ]

    MARGIN_PATTERNS = [
        # "gross margin of X% in 2023"
        r"(gross|operating|net|profit|ebitda)\s+margin\s+(?:of\s+)?([\d.]+)%\s+(?:in\s+)?(\d{4})",
        # "2023 gross margin: X%"
        r"(\d{4})\s+(gross|operating|net|profit|ebitda)\s+margin(?:\s*:)?\s*([\d.]+)%",
    ]

    MULTIPLIERS = {
        "trillion": 1e12,
        "t": 1e12,
        "billion": 1e9,
        "b": 1e9,
        "million": 1e6,
        "m": 1e6,
        "thousand": 1e3,
        "k": 1e3,
    }

    def __init__(self, lookback_years: int = 5):
        """
        Initialize the analyzer.

        Args:
            lookback_years: Number of years to analyze (default 5)
        """
        self.lookback_years = lookback_years
        self.current_year = utc_now().year
        self.metrics: Dict[str, TrendMetric] = {}

    def extract_historical_data(
        self, content: str, source_name: str = ""
    ) -> Dict[str, TrendMetric]:
        """
        Extract historical data points from source content.

        Args:
            content: Text content from sources
            source_name: Name of the source for attribution

        Returns:
            Dictionary of metric name to TrendMetric with extracted data
        """
        metrics = {}

        # Extract revenue trends
        revenue_metric = self._extract_revenue_history(content, source_name)
        if revenue_metric.data_points:
            metrics["revenue"] = revenue_metric

        # Extract growth rates
        growth_metric = self._extract_growth_history(content, source_name)
        if growth_metric.data_points:
            metrics["revenue_growth"] = growth_metric

        # Extract margin trends
        margin_metrics = self._extract_margin_history(content, source_name)
        metrics.update(margin_metrics)

        # Extract from tables if present
        table_metrics = self._extract_from_tables(content, source_name)
        for name, metric in table_metrics.items():
            if name in metrics:
                # Merge data points
                existing_years = {dp.year for dp in metrics[name].data_points}
                for dp in metric.data_points:
                    if dp.year not in existing_years:
                        metrics[name].data_points.append(dp)
            else:
                metrics[name] = metric

        return metrics

    def _extract_revenue_history(self, content: str, source_name: str) -> TrendMetric:
        """Extract historical revenue data."""
        metric = TrendMetric(
            name="revenue", display_name="Annual Revenue", category=MetricCategory.REVENUE, unit="$"
        )

        for pattern in self.YEAR_VALUE_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                groups = match.groups()

                # Parse based on pattern structure
                try:
                    if len(groups) >= 3:
                        # Different patterns have year in different positions
                        if groups[0].isdigit() and len(groups[0]) == 4:
                            # Year first pattern
                            year = int(groups[0])
                            value = float(groups[1].replace(",", ""))
                            multiplier = groups[2] if len(groups) > 2 else None
                        else:
                            # Value first pattern
                            value = float(groups[0].replace(",", ""))
                            multiplier = groups[1]
                            year = int(groups[2])

                        # Apply multiplier
                        if multiplier:
                            mult_key = multiplier.lower().strip()
                            if mult_key in self.MULTIPLIERS:
                                value *= self.MULTIPLIERS[mult_key]

                        # Only include reasonable years
                        if self.current_year - self.lookback_years <= year <= self.current_year:
                            dp = DataPoint(
                                year=year, value=value, source=source_name, confidence=0.8
                            )
                            # Avoid duplicates
                            if not any(d.year == year for d in metric.data_points):
                                metric.data_points.append(dp)
                except (ValueError, IndexError):
                    continue

        return metric

    def _extract_growth_history(self, content: str, source_name: str) -> TrendMetric:
        """Extract historical growth rate data."""
        metric = TrendMetric(
            name="revenue_growth",
            display_name="Revenue Growth (YoY)",
            category=MetricCategory.GROWTH,
            unit="%",
            is_percentage=True,
        )

        for pattern in self.GROWTH_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                try:
                    # Handle different group orders
                    if groups[0].replace(".", "").isdigit():
                        growth = float(groups[0])
                        year = int(groups[1]) if len(groups) > 1 else self.current_year
                    else:
                        year = int(groups[0])
                        growth = float(groups[1])

                    if self.current_year - self.lookback_years <= year <= self.current_year:
                        dp = DataPoint(year=year, value=growth, source=source_name, confidence=0.7)
                        if not any(d.year == year for d in metric.data_points):
                            metric.data_points.append(dp)
                except (ValueError, IndexError):
                    continue

        return metric

    def _extract_margin_history(self, content: str, source_name: str) -> Dict[str, TrendMetric]:
        """Extract historical margin data."""
        metrics = {}

        margin_types = {
            "gross": ("gross_margin", "Gross Margin"),
            "operating": ("operating_margin", "Operating Margin"),
            "net": ("net_margin", "Net Profit Margin"),
            "profit": ("profit_margin", "Profit Margin"),
            "ebitda": ("ebitda_margin", "EBITDA Margin"),
        }

        for pattern in self.MARGIN_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                try:
                    if groups[0].isdigit():
                        year = int(groups[0])
                        margin_type = groups[1].lower()
                        value = float(groups[2])
                    else:
                        margin_type = groups[0].lower()
                        value = float(groups[1])
                        year = int(groups[2])

                    if margin_type in margin_types:
                        name, display_name = margin_types[margin_type]

                        if name not in metrics:
                            metrics[name] = TrendMetric(
                                name=name,
                                display_name=display_name,
                                category=MetricCategory.PROFITABILITY,
                                unit="%",
                                is_percentage=True,
                            )

                        if self.current_year - self.lookback_years <= year <= self.current_year:
                            dp = DataPoint(
                                year=year, value=value, source=source_name, confidence=0.75
                            )
                            if not any(d.year == year for d in metrics[name].data_points):
                                metrics[name].data_points.append(dp)
                except (ValueError, IndexError):
                    continue

        return metrics

    def _extract_from_tables(self, content: str, source_name: str) -> Dict[str, TrendMetric]:
        """Extract historical data from markdown tables."""
        metrics = {}

        # Find markdown tables
        table_pattern = r"\|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|[^\n]+\|\n?)+"
        tables = re.findall(table_pattern, content)

        for table in tables:
            lines = table.strip().split("\n")
            if len(lines) < 3:
                continue

            # Parse header
            header = [cell.strip() for cell in lines[0].split("|") if cell.strip()]

            # Look for year columns
            year_columns = {}
            for i, h in enumerate(header):
                year_match = re.search(r"(20\d{2})", h)
                if year_match:
                    year_columns[i] = int(year_match.group(1))

            if not year_columns:
                continue

            # Parse data rows
            for line in lines[2:]:
                cells = [cell.strip() for cell in line.split("|") if cell.strip()]
                if not cells:
                    continue

                metric_name = cells[0].lower()

                # Map common names
                name_mapping = {
                    "revenue": ("revenue", "Annual Revenue", MetricCategory.REVENUE),
                    "sales": ("revenue", "Annual Revenue", MetricCategory.REVENUE),
                    "net income": ("net_income", "Net Income", MetricCategory.PROFITABILITY),
                    "profit": ("net_income", "Net Income", MetricCategory.PROFITABILITY),
                    "ebitda": ("ebitda", "EBITDA", MetricCategory.PROFITABILITY),
                    "employees": ("employees", "Employee Count", MetricCategory.OPERATIONAL),
                }

                matched_name = None
                for key, (name, display, cat) in name_mapping.items():
                    if key in metric_name:
                        matched_name = (name, display, cat)
                        break

                if not matched_name:
                    continue

                name, display_name, category = matched_name

                if name not in metrics:
                    metrics[name] = TrendMetric(
                        name=name,
                        display_name=display_name,
                        category=category,
                        unit=(
                            "$"
                            if category in [MetricCategory.REVENUE, MetricCategory.PROFITABILITY]
                            else ""
                        ),
                    )

                for col_idx, year in year_columns.items():
                    if col_idx < len(cells):
                        value_str = cells[col_idx]
                        value = self._parse_value(value_str)
                        if value is not None:
                            dp = DataPoint(
                                year=year, value=value, source=source_name, confidence=0.85
                            )
                            if not any(d.year == year for d in metrics[name].data_points):
                                metrics[name].data_points.append(dp)

        return metrics

    def _parse_value(self, value_str: str) -> Optional[float]:
        """Parse a value string into a float."""
        if not value_str or value_str.lower() in ["n/a", "-", "data not available"]:
            return None

        # Remove currency symbols and whitespace
        clean = re.sub(r"[$€£¥₹]", "", value_str).strip()

        # Extract number and multiplier
        match = re.match(
            r"([\d,]+(?:\.\d+)?)\s*(trillion|billion|million|[TBMKtbmk])?", clean, re.IGNORECASE
        )
        if not match:
            return None

        try:
            value = float(match.group(1).replace(",", ""))
            if match.group(2):
                mult_key = match.group(2).lower().strip()
                if mult_key in self.MULTIPLIERS:
                    value *= self.MULTIPLIERS[mult_key]
            return value
        except ValueError:
            return None

    def analyze_trend(self, metric: TrendMetric) -> TrendAnalysis:
        """
        Analyze the trend of a metric.

        Args:
            metric: TrendMetric with data points

        Returns:
            TrendAnalysis with computed statistics
        """
        data_points = metric.get_sorted_annual()

        analysis = TrendAnalysis(
            metric_name=metric.name,
            direction=TrendDirection.INSUFFICIENT_DATA,
            years_of_data=len(data_points),
        )

        if len(data_points) < 2:
            analysis.trend_description = "Insufficient historical data for trend analysis"
            analysis.data_quality = "poor"
            if data_points:
                analysis.latest_value = data_points[-1].value
                analysis.latest_year = data_points[-1].year
            return analysis

        values = [dp.value for dp in data_points]
        years = [dp.year for dp in data_points]

        analysis.min_value = min(values)
        analysis.max_value = max(values)
        analysis.latest_value = values[-1]
        analysis.latest_year = years[-1]

        # Calculate growth rates
        growth_rates = []
        for i in range(1, len(values)):
            if values[i - 1] != 0:
                growth = (values[i] - values[i - 1]) / values[i - 1] * 100
                growth_rates.append(growth)

        if growth_rates:
            analysis.average_growth = sum(growth_rates) / len(growth_rates)

            # Calculate volatility (standard deviation)
            if len(growth_rates) > 1:
                mean = analysis.average_growth
                variance = sum((g - mean) ** 2 for g in growth_rates) / len(growth_rates)
                analysis.volatility = variance**0.5

        # Calculate CAGR if we have enough years
        if len(data_points) >= 2 and values[0] > 0 and values[-1] > 0:
            n_years = years[-1] - years[0]
            if n_years > 0:
                analysis.cagr = ((values[-1] / values[0]) ** (1 / n_years) - 1) * 100

        # Determine trend direction
        analysis.direction = self._determine_direction(growth_rates, analysis.volatility)

        # Generate description
        analysis.trend_description = self._generate_trend_description(
            metric, analysis, growth_rates
        )

        # Assess data quality
        if len(data_points) >= 4:
            analysis.data_quality = "good"
        elif len(data_points) >= 2:
            analysis.data_quality = "partial"
        else:
            analysis.data_quality = "poor"

        return analysis

    def _determine_direction(
        self, growth_rates: List[float], volatility: Optional[float]
    ) -> TrendDirection:
        """Determine the overall trend direction."""
        if not growth_rates:
            return TrendDirection.INSUFFICIENT_DATA

        avg_growth = sum(growth_rates) / len(growth_rates)

        # Check for high volatility
        if volatility and volatility > 15:
            return TrendDirection.VOLATILE

        # Categorize based on average growth
        if avg_growth >= 15:
            return TrendDirection.STRONG_UP
        elif avg_growth >= 3:
            return TrendDirection.UP
        elif avg_growth >= -3:
            return TrendDirection.STABLE
        elif avg_growth >= -15:
            return TrendDirection.DOWN
        else:
            return TrendDirection.STRONG_DOWN

    def _generate_trend_description(
        self, metric: TrendMetric, analysis: TrendAnalysis, growth_rates: List[float]
    ) -> str:
        """Generate a human-readable trend description."""
        parts = []

        # Direction description
        direction_text = {
            TrendDirection.STRONG_UP: "showing strong growth",
            TrendDirection.UP: "on an upward trend",
            TrendDirection.STABLE: "relatively stable",
            TrendDirection.DOWN: "on a downward trend",
            TrendDirection.STRONG_DOWN: "declining significantly",
            TrendDirection.VOLATILE: "showing high volatility",
            TrendDirection.INSUFFICIENT_DATA: "insufficient data for analysis",
        }
        parts.append(f"{metric.display_name} is {direction_text[analysis.direction]}")

        # CAGR
        if analysis.cagr is not None:
            parts.append(f"with a {analysis.years_of_data}-year CAGR of {analysis.cagr:.1f}%")

        # Recent momentum
        if len(growth_rates) >= 2:
            recent = growth_rates[-1]
            prior = sum(growth_rates[:-1]) / len(growth_rates[:-1])
            if recent > prior + 5:
                parts.append("(accelerating)")
            elif recent < prior - 5:
                parts.append("(decelerating)")

        return " ".join(parts) + "."

    def generate_trend_table(
        self, metrics: List[TrendMetric], title: str = "Historical Financial Trends"
    ) -> TrendTable:
        """
        Generate a formatted trend table for multiple metrics.

        Args:
            metrics: List of TrendMetrics to include
            title: Table title

        Returns:
            TrendTable with formatted data
        """
        # Determine year range
        all_years = set()
        for metric in metrics:
            for dp in metric.data_points:
                if dp.quarter is None:  # Annual only
                    all_years.add(dp.year)

        if not all_years:
            return TrendTable(
                title=title, headers=["Metric"], rows=[], markdown="*No historical data available*"
            )

        years = sorted(all_years)[-self.lookback_years :]  # Last N years

        # Build headers
        headers = ["Metric"] + [str(y) for y in years] + ["CAGR"]

        # Build rows
        rows = []
        footnotes = []

        for metric in metrics:
            analysis = self.analyze_trend(metric)

            row = {"Metric": metric.display_name}

            # Get values by year
            year_values = {dp.year: dp for dp in metric.data_points if dp.quarter is None}

            for year in years:
                if year in year_values:
                    dp = year_values[year]
                    value = dp.value

                    # Format value
                    if metric.is_percentage:
                        formatted = f"{value:.1f}%"
                    elif value >= 1e9:
                        formatted = f"${value/1e9:.1f}B"
                    elif value >= 1e6:
                        formatted = f"${value/1e6:.1f}M"
                    else:
                        formatted = f"${value:,.0f}"

                    row[str(year)] = formatted
                else:
                    row[str(year)] = "—"

            # Add CAGR
            if analysis.cagr is not None:
                row["CAGR"] = f"{analysis.cagr:+.1f}%"
            else:
                row["CAGR"] = "—"

            rows.append(row)

            # Add footnote for data quality if needed
            if analysis.data_quality == "partial":
                footnotes.append(f"*{metric.display_name}: Limited historical data")

        # Generate markdown
        markdown = self._generate_markdown_table(title, headers, rows, footnotes)

        return TrendTable(
            title=title, headers=headers, rows=rows, footnotes=footnotes, markdown=markdown
        )

    def _generate_markdown_table(
        self, title: str, headers: List[str], rows: List[Dict[str, Any]], footnotes: List[str]
    ) -> str:
        """Generate markdown table string."""
        lines = [f"### {title}", ""]

        if not rows:
            lines.append("*No historical data available*")
            return "\n".join(lines)

        # Header row
        lines.append("| " + " | ".join(headers) + " |")

        # Separator
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        # Data rows
        for row in rows:
            cells = [str(row.get(h, "—")) for h in headers]
            lines.append("| " + " | ".join(cells) + " |")

        # Footnotes
        if footnotes:
            lines.append("")
            for fn in footnotes:
                lines.append(fn)

        return "\n".join(lines)

    def generate_growth_analysis(self, metrics: Dict[str, TrendMetric]) -> str:
        """
        Generate a narrative growth analysis section.

        Args:
            metrics: Dictionary of metric name to TrendMetric

        Returns:
            Markdown formatted growth analysis
        """
        lines = ["### Growth Analysis", ""]

        analyses = {}
        for name, metric in metrics.items():
            analyses[name] = self.analyze_trend(metric)

        # Revenue analysis
        if "revenue" in analyses:
            analysis = analyses["revenue"]
            lines.append("**Revenue Growth:**")
            lines.append(analysis.trend_description)
            if analysis.cagr is not None and analysis.latest_value:
                lines.append(
                    f"- Latest annual revenue: ${analysis.latest_value/1e9:.2f}B ({analysis.latest_year})"
                )
                lines.append(f"- {analysis.years_of_data}-year CAGR: {analysis.cagr:.1f}%")
            lines.append("")

        # Profitability analysis
        profit_metrics = ["net_income", "ebitda", "operating_margin", "net_margin"]
        profit_analyses = [(k, analyses[k]) for k in profit_metrics if k in analyses]

        if profit_analyses:
            lines.append("**Profitability Trends:**")
            for name, analysis in profit_analyses:
                lines.append(f"- {analysis.trend_description}")
            lines.append("")

        # Overall assessment
        if analyses:
            lines.append("**Overall Assessment:**")

            growth_count = sum(
                1
                for a in analyses.values()
                if a.direction in [TrendDirection.STRONG_UP, TrendDirection.UP]
            )
            decline_count = sum(
                1
                for a in analyses.values()
                if a.direction in [TrendDirection.STRONG_DOWN, TrendDirection.DOWN]
            )

            if growth_count > decline_count:
                lines.append(
                    "The company shows positive momentum with most metrics trending upward."
                )
            elif decline_count > growth_count:
                lines.append("The company faces headwinds with several metrics showing decline.")
            else:
                lines.append("The company shows mixed performance across different metrics.")

        return "\n".join(lines)
